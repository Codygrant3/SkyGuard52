"""Create semantically consolidated Unreal-ready Mission 1 environment exports.

This bounded production step opens the visually accepted Checkpoint02 blend,
bakes evaluated geometry, groups it into a small number of cullable meshes, and
exports fresh GLBs. Blender-only water, foam, wet-contact, and vegetation are
intentionally excluded because Unreal owns those systems.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ROOT = Path(r"D:\Skyguard52")
SOURCE_BLEND = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint02\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02.blend"
OUTPUT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_UnrealReady01"
EXPORTS = OUTPUT / "exports"
RENDERS = OUTPUT / "renders"
BLEND_PATH = OUTPUT / "M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_UNREAL_READY01.blend"
RECEIPT_PATH = OUTPUT / "unreal_ready_export_receipt.json"
INVENTORY_PATH = OUTPUT / "artifact_inventory.json"

EXPECTED_SOURCE_SHA256 = "0ef89cd08cb224f1d21015cfb1c968c1b66d8916c29c4702e129766a215093eb"

ASSETS = (
    "SM_M01_Apartment_Production_A",
    "SM_M01_Midrise_Production_B",
    "SM_M01_CornerResidence_Production_C",
    "SM_M01_CoastalDistrict_Production_A",
    "SM_M01_Lighthouse_Production_A",
)

EXPECTED_GROUPS = {
    "SM_M01_Apartment_Production_A": {"STRUCTURAL", "GLAZING", "DETAILS"},
    "SM_M01_Midrise_Production_B": {"STRUCTURAL", "GLAZING", "DETAILS"},
    "SM_M01_CornerResidence_Production_C": {"STRUCTURAL", "GLAZING", "DETAILS"},
    "SM_M01_CoastalDistrict_Production_A": {"TERRAIN", "HARDSCAPE"},
    "SM_M01_Lighthouse_Production_A": {"STRUCTURAL", "GLAZING", "DETAILS"},
}

EXCLUDED_TOKENS = (
    "_WATER",
    "_FOAM_",
    "_WET_CONTACT",
    "_LEAF_",
    "_PLANT_",
    "_TRUNK",
    "_BRANCH_",
    "_TREE_",
    "_SHRUB_",
    "_FOLIAGE_",
)

STRUCTURAL_TOKENS = (
    "_STRUCTURE",
    "_FOUNDATION",
    "_PIER_",
    "_SPANDREL",
    "_SIDE_RETURN",
    "_CORNICE",
    "_ROOF",
    "_PARAPET",
    "_TOWER_",
    "_BAND_",
)

GLAZING_TOKENS = ("_GLASS_", "_CURTAIN_", "_VOID_", "_LANTERN_BASE")
HARDSCAPE_TOKENS = (
    "_SEAWALL_",
    "_PROMENADE",
    "_CURB_",
    "_ROAD",
    "_CITY_SIDEWALK",
    "_LANE_",
    "_DRAIN_",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record_file(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def classify_object(asset: str, name: str) -> str | None:
    upper = name.upper()
    if upper.startswith("UCX_") or upper.startswith("SOCKET_"):
        return None
    if any(token in upper for token in EXCLUDED_TOKENS):
        return "EXCLUDED_RUNTIME_SYSTEM"
    if asset == "SM_M01_COASTALDISTRICT_PRODUCTION_A":
        if "_BEACH_DUNE" in upper:
            return "TERRAIN"
        if any(token in upper for token in HARDSCAPE_TOKENS):
            return "HARDSCAPE"
        return "HARDSCAPE"
    if any(token in upper for token in GLAZING_TOKENS):
        return "GLAZING"
    if any(token in upper for token in STRUCTURAL_TOKENS):
        return "STRUCTURAL"
    return "DETAILS"


def asset_origin(collection: bpy.types.Collection) -> Vector:
    sockets = [obj for obj in collection.objects if obj.name.startswith("SOCKET_")]
    require(len(sockets) >= 1, f"Missing origin socket in {collection.name}")
    preferred = next((obj for obj in sockets if obj.name.endswith("Origin")), sockets[0])
    return preferred.matrix_world.translation.copy()


def triangle_count(mesh: bpy.types.Mesh) -> int:
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)


def evaluated_mesh_copy(source: bpy.types.Object, origin: Vector, name: str) -> bpy.types.Object:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = source.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
    require(mesh is not None, f"Could not evaluate mesh {source.name}")
    mesh.name = name + "_MESH"
    mesh.transform(Matrix.Translation(-origin) @ source.matrix_world)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.matrix_world = Matrix.Identity(4)
    return obj


def deduplicate_material_slots(obj: bpy.types.Object) -> None:
    old = list(obj.data.materials)
    unique: list[bpy.types.Material | None] = []
    remap: list[int] = []
    lookup: dict[int, int] = {}
    for material in old:
        key = material.as_pointer() if material is not None else 0
        if key not in lookup:
            lookup[key] = len(unique)
            unique.append(material)
        remap.append(lookup[key])
    for polygon in obj.data.polygons:
        if polygon.material_index < len(remap):
            polygon.material_index = remap[polygon.material_index]
    obj.data.materials.clear()
    for material in unique:
        if material is not None:
            obj.data.materials.append(material)


def join_group(asset: str, group: str, sources: list[bpy.types.Object], origin: Vector, target: bpy.types.Collection) -> tuple[bpy.types.Object, dict[str, object]]:
    require(sources, f"No sources for required group {asset}:{group}")
    expected_triangles = 0
    copies: list[bpy.types.Object] = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for index, source in enumerate(sources):
        evaluated = source.evaluated_get(depsgraph)
        probe = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
        require(probe is not None, f"Could not evaluate triangle authority {source.name}")
        expected_triangles += triangle_count(probe)
        bpy.data.meshes.remove(probe)
        copy = evaluated_mesh_copy(source, origin, f"TMP_{asset}_{group}_{index:04d}")
        target.objects.link(copy)
        copies.append(copy)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in copies:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    require(joined is not None, f"Join failed for {asset}:{group}")
    joined.name = f"{asset}_{group}"
    joined.data.name = joined.name + "_MESH"
    joined["skyguard_asset_family"] = asset
    joined["skyguard_semantic_group"] = group
    joined["skyguard_source_object_count"] = len(sources)
    deduplicate_material_slots(joined)
    joined.data.validate(verbose=False, clean_customdata=False)
    joined.data.update()
    actual_triangles = triangle_count(joined.data)
    require(actual_triangles == expected_triangles, f"Triangle mismatch {asset}:{group} expected={expected_triangles} actual={actual_triangles}")
    require(len(joined.data.materials) <= 16, f"Material-slot budget exceeded {asset}:{group}: {len(joined.data.materials)}")
    return joined, {
        "group": group,
        "source_object_count": len(sources),
        "triangle_count_before": expected_triangles,
        "triangle_count_after": actual_triangles,
        "material_slot_count": len(joined.data.materials),
        "uv_layer_count": len(joined.data.uv_layers),
        "vertex_count": len(joined.data.vertices),
        "polygon_count": len(joined.data.polygons),
    }


def copy_collision(asset: str, source: bpy.types.Object, origin: Vector, target: bpy.types.Collection) -> bpy.types.Object:
    association = "HARDSCAPE" if asset == "SM_M01_CoastalDistrict_Production_A" else "STRUCTURAL"
    collision = evaluated_mesh_copy(source, origin, f"UCX_{asset}_{association}_00")
    collision.display_type = "WIRE"
    collision.hide_render = True
    collision["skyguard_collision"] = True
    target.objects.link(collision)
    return collision


def create_socket(asset: str, target: bpy.types.Collection) -> bpy.types.Object:
    socket = bpy.data.objects.new(f"SOCKET_{asset}_Origin", None)
    socket.empty_display_type = "PLAIN_AXES"
    socket.empty_display_size = 0.5
    socket.location = (0.0, 0.0, 0.0)
    socket["skyguard_socket"] = True
    target.objects.link(socket)
    return socket


def remove_source_scene(keep: set[bpy.types.Object]) -> None:
    for obj in list(bpy.data.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj, do_unlink=True)
    for collection in list(bpy.data.collections):
        if collection.name.startswith("UNREAL_READY_"):
            continue
        if collection.users == 0 or len(collection.objects) == 0:
            bpy.data.collections.remove(collection)


def configure_review_scene() -> tuple[bpy.types.Object, list[bpy.types.Object]]:
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass
    world = bpy.data.worlds.new("World_UnrealReadyReview") if bpy.data.worlds.get("World_UnrealReadyReview") is None else bpy.data.worlds["World_UnrealReadyReview"]
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.035, 0.045, 0.06, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.32
    scene.world = world

    camera_data = bpy.data.cameras.new("CAM_UnrealReadyReview")
    camera = bpy.data.objects.new("CAM_UnrealReadyReview", camera_data)
    scene.collection.objects.link(camera)
    camera_data.lens = 52.0
    camera_data.clip_start = 0.05
    camera_data.clip_end = 2000.0
    scene.camera = camera

    lights: list[bpy.types.Object] = []
    sun_data = bpy.data.lights.new("SUN_UnrealReadyReview", "SUN")
    sun_data.energy = 2.2
    sun_data.angle = math.radians(4.0)
    sun = bpy.data.objects.new("SUN_UnrealReadyReview", sun_data)
    sun.rotation_euler = (math.radians(42), math.radians(-18), math.radians(-34))
    scene.collection.objects.link(sun)
    lights.append(sun)
    area_data = bpy.data.lights.new("AREA_UnrealReadyFill", "AREA")
    area_data.energy = 850.0
    area_data.shape = "DISK"
    area_data.size = 18.0
    area = bpy.data.objects.new("AREA_UnrealReadyFill", area_data)
    area.location = (-20.0, -30.0, 35.0)
    scene.collection.objects.link(area)
    lights.append(area)
    return camera, lights


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def bounds_for(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    require(points, "No bounds points")
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return minimum, maximum


def render_asset(asset: str, render_objects: dict[str, list[bpy.types.Object]], camera: bpy.types.Object) -> Path:
    for family, objects in render_objects.items():
        for obj in objects:
            obj.hide_render = family != asset
    visible = render_objects[asset]
    minimum, maximum = bounds_for(visible)
    center = (minimum + maximum) * 0.5
    extent = maximum - minimum
    span = max(extent.x, extent.y, extent.z, 1.0)
    direction = Vector((1.05, -1.45, 0.78)).normalized()
    camera.location = center + direction * span * 1.55
    look_at(camera, center + Vector((0.0, 0.0, extent.z * 0.04)))
    path = RENDERS / f"{asset}_UNREAL_READY_REVIEW.png"
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    require(path.is_file(), f"Review render missing: {path}")
    return path


def export_asset(asset: str, objects: list[bpy.types.Object], path: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = next(obj for obj in objects if obj.type == "MESH" and not obj.name.startswith("UCX_"))
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_extras=True,
        export_materials="EXPORT",
    )
    require(path.is_file(), f"GLB export missing: {path}")


def main() -> None:
    require(bpy.app.version[:2] == (5, 2), f"Blender 5.2 required, found {bpy.app.version_string}")
    require(Path(bpy.data.filepath).resolve() == SOURCE_BLEND.resolve(), f"Wrong source blend open: {bpy.data.filepath}")
    require(SOURCE_BLEND.stat().st_size == 84541315, "Accepted source blend byte count mismatch")
    require(sha256(SOURCE_BLEND) == EXPECTED_SOURCE_SHA256, "Accepted source blend hash mismatch")
    require(not OUTPUT.exists(), f"Fresh output namespace already exists: {OUTPUT}")
    OUTPUT.mkdir(parents=True)
    EXPORTS.mkdir()
    RENDERS.mkdir()

    records: dict[str, object] = {}
    export_objects: dict[str, list[bpy.types.Object]] = {}
    render_objects: dict[str, list[bpy.types.Object]] = {}
    keep: set[bpy.types.Object] = set()

    for asset in ASSETS:
        collection = bpy.data.collections.get(asset)
        require(collection is not None, f"Accepted source collection missing: {asset}")
        origin = asset_origin(collection)
        target = bpy.data.collections.new(f"UNREAL_READY_{asset}")
        bpy.context.scene.collection.children.link(target)
        sources = [obj for obj in collection.objects if obj.type == "MESH" and not obj.name.startswith("UCX_")]
        collisions = [obj for obj in collection.objects if obj.type == "MESH" and obj.name.startswith("UCX_")]
        require(len(collisions) == 1, f"Expected exactly one source collision object for {asset}; found {len(collisions)}")
        grouped: dict[str, list[bpy.types.Object]] = {}
        excluded: list[str] = []
        for source in sources:
            group = classify_object(asset.upper(), source.name)
            if group == "EXCLUDED_RUNTIME_SYSTEM":
                excluded.append(source.name)
            elif group is not None:
                grouped.setdefault(group, []).append(source)
        require(set(grouped) == EXPECTED_GROUPS[asset], f"Unexpected groups for {asset}: {sorted(grouped)}")

        consolidated: list[bpy.types.Object] = []
        group_records: list[dict[str, object]] = []
        for group in sorted(grouped):
            joined, group_record = join_group(asset, group, grouped[group], origin, target)
            consolidated.append(joined)
            group_records.append(group_record)
            keep.add(joined)
        collision = copy_collision(asset, collisions[0], origin, target)
        socket = create_socket(asset, target)
        keep.update((collision, socket))
        export_objects[asset] = consolidated + [collision, socket]
        render_objects[asset] = consolidated
        records[asset] = {
            "source_collection_object_count": len(collection.objects),
            "source_render_mesh_count": len(sources),
            "excluded_object_count": len(excluded),
            "excluded_objects": sorted(excluded),
            "placement_origin_m": [round(float(value), 6) for value in origin],
            "render_group_count": len(consolidated),
            "groups": group_records,
            "collision": collision.name,
            "socket": socket.name,
        }

    remove_source_scene(keep)
    camera, lights = configure_review_scene()
    keep.add(camera)
    keep.update(lights)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), compress=True)
    require(BLEND_PATH.is_file(), "Governed consolidated blend not saved")

    export_paths: list[Path] = []
    for asset in ASSETS:
        path = EXPORTS / f"{asset}_CONSOLIDATED.glb"
        export_asset(asset, export_objects[asset], path)
        export_paths.append(path)

    render_paths = [render_asset(asset, render_objects, camera) for asset in ASSETS]
    total_groups = sum(int(records[asset]["render_group_count"]) for asset in ASSETS)
    require(total_groups == 14, f"Expected exactly fourteen render groups; found {total_groups}")

    receipt = {
        "schema": "skyguard.m01-visible-environment-unreal-ready01-receipt.v1",
        "created_utc": utc_now(),
        "classification": "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_AND_UNREAL_IMPORT_REPROBE",
        "blender_version": bpy.app.version_string,
        "source": record_file(SOURCE_BLEND),
        "source_policy": {
            "accepted_checkpoint02_only": True,
            "failed_geometry_read": False,
            "external_models_imported": False,
            "unreal_owns_water_foliage_lighting_atmosphere": True,
        },
        "coordinate_contract": {"units": "meters", "forward": "+X", "up": "+Z"},
        "assets": records,
        "total_render_group_count": total_groups,
        "outputs": {
            "blend": record_file(BLEND_PATH),
            "exports": [record_file(path) for path in export_paths],
            "renders": [record_file(path) for path in render_paths],
        },
        "acceptance_boundary": "DIRECT_RENDER_REVIEW_AND_FRESH_UNREAL_IMPORT_REPROBE_REQUIRED_BEFORE_MAP_INTEGRATION",
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    files = sorted(path for path in OUTPUT.rglob("*") if path.is_file() and path != INVENTORY_PATH)
    inventory = {
        "schema": "skyguard.m01-visible-environment-unreal-ready01-inventory.v1",
        "created_utc": utc_now(),
        "files": [record_file(path) for path in files],
    }
    INVENTORY_PATH.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
