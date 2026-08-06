"""Render read-only mapped-mesh previews for Build 008.

The script must be launched with the already-authored Build 008 master open.
It assigns attempt-local review materials in memory, reads the governed normal
and AO maps, renders three views per asset, and exits without saving the blend
or writing any canonical source/map path. It contains no bake operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import bpy
from mathutils import Vector


BUILD_ID = "BLD_M01_HERO_GROUPED_TOPOLOGY_008"
REQUIRED_ASSETS = {"Pathfinder", "Lighthouse", "RadarPost"}
VIEWS = {
    "three_quarter": Vector((1.0, -1.0, 0.55)),
    "grazing_port": Vector((1.0, -0.10, 0.12)),
    "grazing_starboard": Vector((-1.0, 0.10, 0.12)),
}
BASE_COLORS = {
    "Pathfinder": (0.22, 0.30, 0.20, 1.0),
    "Lighthouse": (0.62, 0.62, 0.58, 1.0),
    "RadarPost": (0.26, 0.29, 0.31, 1.0),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--attempt", type=Path, required=True)
    parser.add_argument(
        "--review-attempt",
        default="mapped_mesh_review_attempt_02",
    )
    return parser.parse_args(values)


def manifest_groups(
    manifest: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for asset in manifest.get("assets", []):
        asset_id = asset.get("id")
        if asset_id not in REQUIRED_ASSETS:
            continue
        groups: list[dict[str, Any]] = []
        for group in asset.get("groups", []):
            maps = {
                item.get("type"): item
                for item in group.get("maps", [])
                if isinstance(item, dict)
            }
            if set(maps) != {"Normal", "AO"}:
                raise RuntimeError(
                    f"{asset_id}/{group.get('id')}: missing Normal or AO map"
                )
            groups.append(
                {
                    "id": group["id"],
                    "object": group["low"]["object"],
                    "normal": maps["Normal"],
                    "ao": maps["AO"],
                }
            )
        if len(groups) != 4:
            raise RuntimeError(f"{asset_id}: expected four mapped groups")
        result[asset_id] = groups
    if set(result) != REQUIRED_ASSETS:
        raise RuntimeError("Build 008 mapped-review asset scope mismatch")
    return result


def verify_map_evidence(group: dict[str, Any]) -> None:
    for map_type in ("normal", "ao"):
        item = group[map_type]
        path = Path(item["path"])
        if not path.is_file() or sha256_file(path) != item["sha256"]:
            raise RuntimeError(
                f"{group['object']}/{map_type}: governed map hash mismatch"
            )


def new_review_material(
    asset_id: str,
    group: dict[str, Any],
):
    normal_path = Path(group["normal"]["path"])
    ao_path = Path(group["ao"]["path"])
    material = bpy.data.materials.new(
        f"REVIEW_{asset_id}_{group['id']}_008"
    )
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Roughness"].default_value = 0.42
    shader.inputs["Metallic"].default_value = 0.08

    normal_image = bpy.data.images.load(
        str(normal_path),
        check_existing=True,
    )
    normal_image.colorspace_settings.name = "Non-Color"
    normal_texture = nodes.new("ShaderNodeTexImage")
    normal_texture.image = normal_image
    normal_texture.interpolation = "Linear"
    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.space = "TANGENT"
    normal_map.inputs["Strength"].default_value = 1.0
    links.new(normal_texture.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], shader.inputs["Normal"])

    ao_image = bpy.data.images.load(str(ao_path), check_existing=True)
    ao_image.colorspace_settings.name = "Non-Color"
    ao_texture = nodes.new("ShaderNodeTexImage")
    ao_texture.image = ao_image
    ao_texture.interpolation = "Linear"
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.inputs["Fac"].default_value = 1.0
    multiply.inputs["Color1"].default_value = BASE_COLORS[asset_id]
    links.new(ao_texture.outputs["Color"], multiply.inputs["Color2"])
    links.new(multiply.outputs["Color"], shader.inputs["Base Color"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return material


def assign_review_material(obj, material) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.material_index = 0


def world_bounds(objects) -> tuple[Vector, Vector]:
    corners = [
        obj.matrix_world @ Vector(corner)
        for obj in objects
        for corner in obj.bound_box
    ]
    minimum = Vector(
        (
            min(item.x for item in corners),
            min(item.y for item in corners),
            min(item.z for item in corners),
        )
    )
    maximum = Vector(
        (
            max(item.x for item in corners),
            max(item.y for item in corners),
            max(item.z for item in corners),
        )
    )
    return minimum, maximum


def point_camera(camera, center: Vector, direction: Vector, extent: Vector) -> None:
    direction = direction.normalized()
    radius = max(extent.length * 0.5, 0.5)
    camera.location = center + direction * (radius * 4.0 + 2.0)
    camera.rotation_euler = (
        center - camera.location
    ).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = max(extent.x, extent.y, extent.z) * 1.35
    camera.data.lens = 70.0


def place_light(light, center: Vector, offset: Vector) -> None:
    light.location = center + offset
    light.rotation_euler = (
        center - light.location
    ).to_track_quat("-Z", "Y").to_euler()


def configure_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.world.color = (0.018, 0.022, 0.028)
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass

    camera_data = bpy.data.cameras.new("CAM_M01_MAPPED_REVIEW_008")
    camera = bpy.data.objects.new(
        "CAM_M01_MAPPED_REVIEW_008",
        camera_data,
    )
    scene.collection.objects.link(camera)
    scene.camera = camera

    key_data = bpy.data.lights.new(
        "KEY_M01_MAPPED_REVIEW_008",
        type="AREA",
    )
    key_data.energy = 1150.0
    key_data.shape = "DISK"
    key_data.size = 8.0
    key = bpy.data.objects.new("KEY_M01_MAPPED_REVIEW_008", key_data)
    scene.collection.objects.link(key)

    fill_data = bpy.data.lights.new(
        "FILL_M01_MAPPED_REVIEW_008",
        type="AREA",
    )
    fill_data.energy = 700.0
    fill_data.size = 6.0
    fill = bpy.data.objects.new("FILL_M01_MAPPED_REVIEW_008", fill_data)
    scene.collection.objects.link(fill)

    rim_data = bpy.data.lights.new(
        "RIM_M01_MAPPED_REVIEW_008",
        type="AREA",
    )
    rim_data.energy = 1000.0
    rim_data.size = 5.0
    rim = bpy.data.objects.new("RIM_M01_MAPPED_REVIEW_008", rim_data)
    scene.collection.objects.link(rim)
    return scene, camera, key, fill, rim


def main() -> None:
    started = time.perf_counter()
    args = parse_args()
    manifest_path = args.manifest.resolve()
    attempt = args.attempt.resolve()
    if (
        Path(args.review_attempt).name != args.review_attempt
        or not args.review_attempt.startswith("mapped_mesh_review_attempt_")
    ):
        raise RuntimeError("Invalid attempt-local mapped-review namespace")
    output_root = attempt / args.review_attempt
    preview_root = output_root / "previews"
    if output_root.exists():
        raise RuntimeError(
            "Mapped-review output already exists; refusing overwrite"
        )
    preview_root.mkdir(parents=True)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("build_id") != BUILD_ID:
        raise RuntimeError("Mapped review requires Build 008 manifest")
    groups_by_asset = manifest_groups(manifest)
    canonical_master = Path(manifest["outputs"]["master_blend"]["path"])
    if Path(bpy.data.filepath).resolve() != canonical_master.resolve():
        raise RuntimeError("Blender did not open the governed Build 008 master")
    if sha256_file(canonical_master) != manifest["outputs"]["master_blend"][
        "sha256"
    ]:
        raise RuntimeError("Build 008 master hash mismatch")

    low_objects = {
        group["object"]: bpy.data.objects.get(group["object"])
        for groups in groups_by_asset.values()
        for group in groups
    }
    if any(obj is None for obj in low_objects.values()):
        missing = [
            name for name, obj in low_objects.items() if obj is None
        ]
        raise RuntimeError(f"Missing mapped-review low objects: {missing}")

    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.hide_render = True
    for asset_id, groups in groups_by_asset.items():
        for group in groups:
            verify_map_evidence(group)
            obj = low_objects[group["object"]]
            assign_review_material(
                obj,
                new_review_material(asset_id, group),
            )

    scene, camera, key, fill, rim = configure_scene()
    preview_records: list[dict[str, Any]] = []
    for asset_id in sorted(groups_by_asset):
        objects = [
            low_objects[group["object"]]
            for group in groups_by_asset[asset_id]
        ]
        for obj in low_objects.values():
            obj.hide_render = obj not in objects
        minimum, maximum = world_bounds(objects)
        center = (minimum + maximum) * 0.5
        extent = maximum - minimum
        radius = max(extent.length * 0.5, 1.0)
        place_light(key, center, Vector((radius, -radius, radius * 1.4)))
        place_light(
            fill,
            center,
            Vector((-radius * 0.8, -radius * 0.5, radius * 0.7)),
        )
        place_light(
            rim,
            center,
            Vector((0.0, radius * 1.2, radius * 1.1)),
        )

        for view_name, direction in VIEWS.items():
            point_camera(camera, center, direction, extent)
            output = preview_root / f"{asset_id}_{view_name}_008.png"
            scene.render.filepath = str(output)
            bpy.ops.render.render(write_still=True)
            preview_records.append(
                {
                    "asset": asset_id,
                    "view": view_name,
                    "path": str(output),
                    "bytes": output.stat().st_size,
                    "sha256": sha256_file(output),
                    "width": 1024,
                    "height": 1024,
                }
            )

    report = {
        "schema": (
            "skyguard.m01.hero-grouped-topology-bake."
            "mapped-mesh-preview.v1"
        ),
        "build_id": BUILD_ID,
        "gate": "PASS",
        "terminal_state": "MAPPED_PREVIEWS_RENDERED_AWAITING_DIRECT_REVIEW",
        "analysis_mode": "read_only_master_and_maps_attempt_local_previews",
        "manifest": {
            "path": str(manifest_path),
            "sha256": sha256_file(manifest_path),
        },
        "master": {
            "path": str(canonical_master),
            "sha256": sha256_file(canonical_master),
        },
        "asset_count": len(groups_by_asset),
        "mapped_group_count": sum(
            len(groups) for groups in groups_by_asset.values()
        ),
        "preview_count": len(preview_records),
        "previews": preview_records,
        "canonical_map_write_count": 0,
        "bake_operation_count": 0,
        "master_save_count": 0,
        "unreal_process_count": 0,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "mapped_mesh_grazing_angle_review": "NOT_RUN",
        "unreal_acceptance": "NOT_RUN",
        "promotion_authorized": False,
        "p3_4_closed": False,
    }
    report_path = output_root / "mapped_mesh_preview_report.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
