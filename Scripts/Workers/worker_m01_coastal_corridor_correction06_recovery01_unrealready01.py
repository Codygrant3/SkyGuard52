from __future__ import annotations

"""Consolidate the accepted Mission 1 corridor into Unreal-ready semantic meshes.

This worker never regenerates the accepted geometry. It opens the frozen
Correction06 Recovery01 source, evaluates its visible meshes, bakes world
transforms, and joins them into four independently controllable semantic meshes.
The review ocean remains Blender-only and is never exported.
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
ASSET_ID = "m01-coastal-corridor-correction06-recovery01-unrealready01"
SOURCE_BLEND = ROOT / r"Production\Attempts\m01-coastal-corridor-correction06-recovery01\attempt_20260810T202054858832Z\output\M01_CoastalCorridor_Correction06_Recovery01.blend"
SOURCE_BLEND_SHA256 = "08d6eec9dfd289a63634e3f12ac203a40d58d6c7a4f547be9210465e3052dec4"
SOURCE_TERMINAL = SOURCE_BLEND.parents[1] / "terminal.json"
SOURCE_TERMINAL_SHA256 = "768c427ead6d34ec5e7d0f5433deecd3859db4b5328c858f02a92e769f5689d9"
SOURCE_POSTFLIGHT = SOURCE_BLEND.parents[1] / "postflight.json"
SOURCE_POSTFLIGHT_SHA256 = "c640036d82242b7fc6608eaaf3af550c0d010dc92c3018131a9c95602f8b5c33"
SOURCE_REVIEW = SOURCE_BLEND.parents[1] / "visual_review.json"
SOURCE_REVIEW_SHA256 = "9210180b28577e1048470e3bcfc1b48a1ea7db7b260e8fa6e816b6a2423b8f20"

SOURCE_COLLECTION = "M01_C06_VISIBLE"
REVIEW_COLLECTION = "M01_C06_REVIEW_ONLY"
SEMANTIC_COLLECTION = "M01_C06R01_UNREAL_READY"
ARCHIVE_COLLECTION = "M01_C06R01_ACCEPTED_SOURCE_ARCHIVE"
COLLISION_SOURCE = "UCX_SM_M01_CoastalCorridor_C06_00"
SOCKET_SOURCE = "SOCKET_M01_CoastalCorridor_C06_Origin"

SEMANTIC_NAMES = {
    "terrain": "SM_M01_CoastalCorridor_C06R01_TERRAIN",
    "hardscape": "SM_M01_CoastalCorridor_C06R01_HARDSCAPE",
    "details": "SM_M01_CoastalCorridor_C06R01_DETAILS",
    "contact": "SM_M01_CoastalCorridor_C06R01_CONTACT",
}
COLLISION_NAME = "UCX_SM_M01_CoastalCorridor_C06R01_TERRAIN_00"
SOCKET_NAME = "SOCKET_M01_CoastalCorridor_C06R01_Origin"

CAMERAS = {
    "route_aerial": ((-5.0, -32.0, 25.0), (170.0, 91.0, 1.0), 58.0),
    "shoreline_oblique": ((56.0, 7.0, 5.8), (138.0, 54.0, 0.15), 62.0),
    "promenade_furniture": ((170.0, 67.0, 3.2), (245.0, 83.0, 1.05), 66.0),
    "integrated_intersection": ((236.0, 88.0, 8.5), (260.0, 126.0, 0.65), 61.0),
    "urban_service_detail": ((396.0, 97.0, 7.0), (445.0, 116.0, 0.8), 64.0),
    "wet_contact_close": ((330.0, 14.0, 4.6), (380.0, 44.0, -0.15), 66.0),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    raw = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", required=True)
    return parser.parse_args(raw)


def verify_authority() -> list[dict[str, Any]]:
    authorities = (
        (SOURCE_BLEND, SOURCE_BLEND_SHA256),
        (SOURCE_TERMINAL, SOURCE_TERMINAL_SHA256),
        (SOURCE_POSTFLIGHT, SOURCE_POSTFLIGHT_SHA256),
        (SOURCE_REVIEW, SOURCE_REVIEW_SHA256),
    )
    inventory = []
    for path, expected in authorities:
        require(path.is_file(), f"Frozen authority missing: {path}")
        actual = sha256(path)
        require(actual == expected, f"Frozen authority mismatch: {path}")
        inventory.append({"path": str(path), "bytes": path.stat().st_size, "sha256": actual})
    review = json.loads(SOURCE_REVIEW.read_text(encoding="utf-8"))
    require(review.get("decision") == "accept", "Source visual review is not accepted")
    return inventory


def collection(name: str) -> bpy.types.Collection:
    value = bpy.data.collections.get(name)
    require(value is not None, f"Required collection missing: {name}")
    return value


def move_collection(child: bpy.types.Collection, new_name: str) -> None:
    child.name = new_name
    child.hide_render = True
    child.hide_viewport = True


def classify(name: str) -> str:
    require(name.startswith("SM_M01_C06"), f"Unexpected accepted render mesh: {name}")
    if any(token in name for token in ("WetSand", "DrySand", "DuneTransition", "UrbanParcel")):
        return "terrain"
    if any(token in name for token in ("FoamPatch", "WetContactRibbon", "FoamContactGuide")):
        return "contact"
    if any(
        token in name
        for token in (
            "StormDrain",
            "Bollard",
            "Bench",
            "Lamp",
            "TreePit",
            "UtilityCabinet",
            "DuneFence",
        )
    ):
        return "details"
    if any(
        token in name
        for token in (
            "Promenade",
            "MainRoad",
            "InlandSidewalk",
            "IntegratedCrossStreet",
            "BeachAccessRamp",
            "CenterDash",
            "RoadCurb",
            "CrossStreetCurb",
            "Crosswalk",
            "TactilePad",
        )
    ):
        return "hardscape"
    raise RuntimeError(f"Accepted mesh has no semantic routing rule: {name}")


def evaluated_copy(source: bpy.types.Object, target: bpy.types.Collection) -> bpy.types.Object:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = source.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(
        evaluated,
        preserve_all_data_layers=True,
        depsgraph=depsgraph,
    )
    mesh.transform(source.matrix_world)
    mesh.update()
    duplicate = bpy.data.objects.new(f"BAKED_{source.name}", mesh)
    duplicate.matrix_world.identity()
    target.objects.link(duplicate)
    require(len(mesh.uv_layers) >= 1, f"Baked render mesh lost UV0: {source.name}")
    return duplicate


def join_group(objects: list[bpy.types.Object], final_name: str) -> bpy.types.Object:
    require(objects, f"Semantic group is empty: {final_name}")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    result = objects[0]
    result.name = final_name
    result.data.name = f"{final_name}_MESH"
    result.matrix_world.identity()
    bpy.context.view_layer.objects.active = result
    bpy.ops.object.material_slot_remove_unused()
    require(len(result.data.uv_layers) >= 1, f"Consolidated mesh lost UV0: {final_name}")
    require(len(result.material_slots) <= 16, f"Consolidated material slots unexpectedly expanded: {final_name}")
    return result


def duplicate_collision(source: bpy.types.Object, target: bpy.types.Collection) -> bpy.types.Object:
    duplicate = evaluated_copy(source, target)
    duplicate.name = COLLISION_NAME
    duplicate.data.name = f"{COLLISION_NAME}_MESH"
    duplicate.hide_render = True
    duplicate.display_type = "WIRE"
    return duplicate


def duplicate_socket(source: bpy.types.Object, target: bpy.types.Collection) -> bpy.types.Object:
    duplicate = bpy.data.objects.new(SOCKET_NAME, None)
    duplicate.matrix_world = source.matrix_world.copy()
    duplicate.empty_display_type = "PLAIN_AXES"
    duplicate.empty_display_size = 2.5
    target.objects.link(duplicate)
    return duplicate


def point_camera(camera: bpy.types.Object, location: tuple[float, float, float], target: tuple[float, float, float], lens: float) -> None:
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = lens


def configure_condition(scene: bpy.types.Scene, condition: str) -> None:
    background = scene.world.node_tree.nodes.get("Background")
    sun = bpy.data.objects.get("M01_C06_Sun")
    area = bpy.data.objects.get("M01_C06_SkyFill")
    require(background is not None and sun is not None and area is not None, "Review lighting authority missing")
    if condition == "daylight":
        background.inputs["Color"].default_value = (0.31, 0.47, 0.68, 1.0)
        background.inputs["Strength"].default_value = 0.42
        sun.data.energy = 3.1
        sun.data.color = (1.0, 0.78, 0.57)
        area.data.energy = 1550.0
        scene.view_settings.exposure = 0.12
    else:
        background.inputs["Color"].default_value = (0.24, 0.31, 0.37, 1.0)
        background.inputs["Strength"].default_value = 0.32
        sun.data.energy = 1.45
        sun.data.color = (0.74, 0.83, 0.90)
        area.data.energy = 1150.0
        scene.view_settings.exposure = 0.34


def render_reviews(output: Path) -> list[dict[str, Any]]:
    scene = bpy.context.scene
    camera = bpy.data.objects.get("M01_C06_ReviewCamera")
    require(camera is not None and camera.type == "CAMERA", "Review camera authority missing")
    scene.camera = camera
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    render_dir = output / "renders"
    render_dir.mkdir()
    results = []
    for camera_name, (location, target, lens) in CAMERAS.items():
        condition = "overcast" if camera_name in {"integrated_intersection", "wet_contact_close"} else "daylight"
        configure_condition(scene, condition)
        point_camera(camera, location, target, lens)
        path = render_dir / f"{condition}_{camera_name}.png"
        scene.render.filepath = str(path)
        print(json.dumps({"event": "render_start", "camera": camera_name}), flush=True)
        bpy.ops.render.render(write_still=True)
        require(path.is_file() and path.stat().st_size > 0, f"Render missing: {path}")
        results.append({"camera": camera_name, "condition": condition, "path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
    return results


def export_glb(path: Path, objects: list[bpy.types.Object]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.select_set(True)
    bpy.context.view_layer.objects.active = next(obj for obj in objects if obj.type == "MESH")
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_animations=False,
        export_lights=False,
        export_cameras=False,
    )
    require(path.is_file() and path.stat().st_size > 0, "GLB export was not created")


def main() -> int:
    args = parse_args()
    require(args.asset_id == ASSET_ID, f"Unexpected asset id: {args.asset_id}")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    require(not any(output.iterdir()), f"Controller output directory is not empty: {output}")
    authorities = verify_authority()

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    source_collection = collection(SOURCE_COLLECTION)
    source_meshes = sorted((obj for obj in source_collection.all_objects if obj.type == "MESH"), key=lambda obj: obj.name)
    require(len(source_meshes) >= 300, f"Accepted source mesh count unexpectedly low: {len(source_meshes)}")

    semantic_collection = bpy.data.collections.new(SEMANTIC_COLLECTION)
    bpy.context.scene.collection.children.link(semantic_collection)
    grouped: dict[str, list[bpy.types.Object]] = {key: [] for key in SEMANTIC_NAMES}
    source_mapping: dict[str, list[str]] = {key: [] for key in SEMANTIC_NAMES}
    source_polygon_count = 0
    for source in source_meshes:
        group = classify(source.name)
        source_mapping[group].append(source.name)
        source_polygon_count += len(source.data.polygons)
        grouped[group].append(evaluated_copy(source, semantic_collection))

    semantic_objects = [join_group(grouped[key], SEMANTIC_NAMES[key]) for key in ("terrain", "hardscape", "details", "contact")]
    move_collection(source_collection, ARCHIVE_COLLECTION)

    collision_source = bpy.data.objects.get(COLLISION_SOURCE)
    socket_source = bpy.data.objects.get(SOCKET_SOURCE)
    require(collision_source is not None and collision_source.type == "MESH", "Accepted collision source missing")
    require(socket_source is not None and socket_source.type == "EMPTY", "Accepted socket source missing")
    collision_object = duplicate_collision(collision_source, semantic_collection)
    socket_object = duplicate_socket(socket_source, semantic_collection)

    require(not any(obj.name.startswith("REVIEW_ONLY") for obj in semantic_collection.all_objects), "Review-only object entered semantic collection")
    require(len([obj for obj in semantic_collection.all_objects if obj.type == "MESH"]) == 5, "Semantic mesh count is not exactly five")
    require(len([obj for obj in semantic_collection.all_objects if obj.type == "EMPTY"]) == 1, "Semantic socket count is not exactly one")

    consolidated_polygon_count = sum(len(obj.data.polygons) for obj in semantic_objects)
    require(consolidated_polygon_count >= source_polygon_count, "Evaluated consolidation lost source surface topology")
    require(all(len(obj.data.uv_layers) >= 1 for obj in semantic_objects), "A semantic render mesh lacks UV0")
    material_names = sorted({slot.material.name for obj in semantic_objects for slot in obj.material_slots if slot.material is not None})
    require(len(material_names) >= 10, f"Material diversity was lost: {material_names}")

    renders = render_reviews(output)
    require(len(renders) == 6, "Governed render count mismatch")

    blend_path = output / "M01_CoastalCorridor_Correction06_Recovery01_UnrealReady01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    glb_path = output / "M01_CoastalCorridor_Correction06_Recovery01_UnrealReady01.glb"
    export_glb(glb_path, [*semantic_objects, collision_object, socket_object])

    write_json(
        output / "source_authority_receipt.json",
        {
            "schema": "skyguard.m01-c06r01-unrealready01.source-authority.v1",
            "asset_id": ASSET_ID,
            "accepted_source_regenerated": False,
            "accepted_source_modified": False,
            "authorities": authorities,
            "passed": True,
        },
    )
    write_json(
        output / "semantic_consolidation_receipt.json",
        {
            "schema": "skyguard.m01-c06r01-unrealready01.semantic-consolidation.v1",
            "asset_id": ASSET_ID,
            "coordinate_contract": {"units": "meters", "forward": "+X", "up": "+Z"},
            "source_render_mesh_count": len(source_meshes),
            "source_polygon_count": source_polygon_count,
            "semantic_render_mesh_count": len(semantic_objects),
            "export_mesh_count_including_collision": 5,
            "consolidated_polygon_count": consolidated_polygon_count,
            "semantic_names": SEMANTIC_NAMES,
            "source_mapping": source_mapping,
            "collision": COLLISION_NAME,
            "socket": SOCKET_NAME,
            "uv0_complete": True,
            "material_names": material_names,
            "review_ocean_exported": False,
            "accepted_source_archive_in_blend": ARCHIVE_COLLECTION,
            "passed": True,
        },
    )
    write_json(
        output / "render_receipt.json",
        {
            "schema": "skyguard.m01-c06r01-unrealready01.renders.v1",
            "asset_id": ASSET_ID,
            "resolution": [1920, 1080],
            "render_count": len(renders),
            "renders": renders,
            "direct_full_resolution_review_required": True,
            "passed": True,
        },
    )
    print(json.dumps({"classification": "PASSED_BLENDER_AWAITING_POSTFLIGHT", "blend": str(blend_path), "glb": str(glb_path), "semantic_meshes": SEMANTIC_NAMES}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
