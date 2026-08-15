"""Read-only Blender 5.2 comparison of project-owned Mission 1 lighthouse sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def authority(entry: dict[str, object]) -> dict[str, object]:
    path = Path(str(entry["path"]))
    require(path.is_file(), f"Authority missing: {path}")
    actual = record(path)
    require(actual["bytes"] == int(entry["bytes"]), f"Authority byte mismatch: {path}")
    require(actual["sha256"] == str(entry["sha256"]), f"Authority hash mismatch: {path}")
    return actual


def collection_names(obj: bpy.types.Object) -> list[str]:
    return [collection.name for collection in obj.users_collection]


def is_lighthouse(obj: bpy.types.Object) -> bool:
    if obj.type != "MESH":
        return False
    searchable = [obj.name, obj.data.name, *collection_names(obj)]
    if any("lighthouse" in value.lower() for value in searchable):
        return True
    return False


def is_helper(obj: bpy.types.Object) -> bool:
    upper = obj.name.upper()
    return any(token in upper for token in ("HIGH_", "CAGE_", "AOCC_", "UCX_", "COLLISION", "SOCKET_"))


def mesh_metrics(obj: bpy.types.Object) -> dict[str, object]:
    mesh = obj.data
    mesh.calc_loop_triangles()
    materials = []
    image_paths: set[str] = set()
    node_materials = 0
    for slot in obj.material_slots:
        material = slot.material
        if material is None:
            continue
        row = {"name": material.name, "use_nodes": bool(material.use_nodes)}
        if material.use_nodes and material.node_tree:
            node_materials += 1
            for node in material.node_tree.nodes:
                image = getattr(node, "image", None)
                if image is not None and image.filepath:
                    image_paths.add(str(Path(bpy.path.abspath(image.filepath))))
        materials.append(row)
    dimensions = obj.dimensions
    return {
        "object": obj.name,
        "mesh": mesh.name,
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "polygons": len(mesh.polygons),
        "triangles": len(mesh.loop_triangles),
        "uv_layer_count": len(mesh.uv_layers),
        "uv_coordinate_count": sum(len(layer.data) for layer in mesh.uv_layers),
        "material_slot_count": len(obj.material_slots),
        "node_material_count": node_materials,
        "materials": materials,
        "image_paths": sorted(image_paths),
        "dimensions_m": [float(dimensions.x), float(dimensions.y), float(dimensions.z)],
        "scale": [float(obj.scale.x), float(obj.scale.y), float(obj.scale.z)],
        "rotation_euler_degrees": [math.degrees(float(value)) for value in obj.rotation_euler],
        "modifier_count": len(obj.modifiers),
        "collections": collection_names(obj),
    }


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    require(points, "No bound points were found")
    minimum = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
    maximum = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
    return minimum, maximum


def make_material(name: str, color: tuple[float, float, float, float], metallic: float, roughness: float) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Metallic IOR Level"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    return material


def replace_with_clay(objects: list[bpy.types.Object]) -> None:
    tower = make_material("__EVAL_TOWER", (0.68, 0.70, 0.72, 1.0), 0.0, 0.58)
    metal = make_material("__EVAL_METAL", (0.16, 0.18, 0.21, 1.0), 0.72, 0.32)
    red = make_material("__EVAL_RED", (0.46, 0.055, 0.035, 1.0), 0.1, 0.4)
    glass = make_material("__EVAL_GLASS", (0.19, 0.34, 0.43, 1.0), 0.05, 0.18)
    for obj in objects:
        upper = obj.name.upper()
        selected = glass if "GLASS" in upper or "GLAZ" in upper else red if "RED" in upper or "ROOF" in upper else metal if "STEEL" in upper or "GALLERY" in upper or "DETAIL" in upper else tower
        obj.data.materials.clear()
        obj.data.materials.append(selected)


def set_look_at(camera: bpy.types.Object, target: Vector) -> None:
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


def add_area(name: str, location: Vector, energy: float, size: float, target: Vector) -> None:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    set_look_at(obj, target)


def prepare_review_scene(objects: list[bpy.types.Object], minimum: Vector, maximum: Vector) -> bpy.types.Object:
    for obj in bpy.context.scene.objects:
        obj.hide_render = obj not in objects
    replace_with_clay(objects)
    center = (minimum + maximum) * 0.5
    size = maximum - minimum
    ground_material = make_material("__EVAL_GROUND", (0.11, 0.12, 0.13, 1.0), 0.0, 0.82)
    bpy.ops.mesh.primitive_plane_add(size=max(size.x, size.y, 1.0) * 4.0, location=(center.x, center.y, minimum.z - 0.015))
    ground = bpy.context.object
    ground.name = "__EVAL_GROUND"
    ground.data.materials.append(ground_material)
    camera_data = bpy.data.cameras.new("__EVAL_CAMERA")
    camera_data.type = "ORTHO"
    camera_data.lens = 55.0
    camera = bpy.data.objects.new("__EVAL_CAMERA", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    bpy.context.scene.camera = camera
    span = max(size.x, size.y, size.z, 1.0)
    add_area("__EVAL_KEY", center + Vector((-span * 0.9, -span * 1.1, span * 1.25)), 1450.0, span * 0.85, center)
    add_area("__EVAL_FILL", center + Vector((span * 1.0, -span * 0.4, span * 0.55)), 850.0, span * 0.7, center)
    world = bpy.context.scene.world or bpy.data.worlds.new("__EVAL_WORLD")
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.045, 0.055, 0.075, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.42
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.look = "AgX - Medium High Contrast"
    camera.data.ortho_scale = max(size.z * 1.22, max(size.x, size.y) * 1.22 / (1600.0 / 900.0), 2.0)
    return camera


def render_views(source_id: str, objects: list[bpy.types.Object], output: Path) -> list[dict[str, object]]:
    minimum, maximum = world_bounds(objects)
    center = (minimum + maximum) * 0.5
    size = maximum - minimum
    camera = prepare_review_scene(objects, minimum, maximum)
    distance = max(size.x, size.y, size.z, 1.0) * 2.4
    views = [
        ("front", Vector((center.x, center.y - distance, center.z + size.z * 0.05))),
        ("oblique", Vector((center.x + distance * 0.72, center.y - distance, center.z + size.z * 0.22))),
    ]
    rows = []
    for suffix, location in views:
        camera.location = location
        set_look_at(camera, center)
        path = output / f"{source_id}_{suffix}.png"
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        require(path.is_file(), f"Render missing: {path}")
        rows.append(record(path))
    return rows


def evaluate_source(entry: dict[str, object], renders: Path) -> dict[str, object]:
    source_path = Path(str(entry["path"]))
    before = authority(entry)
    bpy.ops.wm.open_mainfile(filepath=str(source_path), load_ui=False)
    matches = [obj for obj in bpy.data.objects if is_lighthouse(obj)]
    require(matches, f"No lighthouse mesh objects found: {source_path}")
    visible = [obj for obj in matches if not is_helper(obj)]
    low = [obj for obj in visible if obj.name.upper().startswith("LOW_")]
    render_objects = low if low else visible
    require(render_objects, f"No renderable lighthouse source found: {source_path}")
    metrics = [mesh_metrics(obj) for obj in matches]
    render_metrics = [row for row in metrics if row["object"] in {obj.name for obj in render_objects}]
    minimum, maximum = world_bounds(render_objects)
    total_triangles = sum(int(row["triangles"]) for row in render_metrics)
    total_vertices = sum(int(row["vertices"]) for row in render_metrics)
    uv_ready = sum(1 for row in render_metrics if int(row["uv_layer_count"]) > 0)
    material_ready = sum(1 for row in render_metrics if int(row["material_slot_count"]) > 0)
    images = sorted({image for row in render_metrics for image in row["image_paths"]})
    result = {
        "source_id": str(entry["id"]),
        "source_before": before,
        "matched_object_count": len(matches),
        "render_object_count": len(render_objects),
        "render_objects": [obj.name for obj in render_objects],
        "helper_object_count": len([obj for obj in matches if is_helper(obj)]),
        "render_vertices": total_vertices,
        "render_triangles": total_triangles,
        "objects_with_uvs": uv_ready,
        "objects_with_materials": material_ready,
        "texture_dependency_count": len(images),
        "texture_dependencies": images,
        "bounds_min_m": [float(value) for value in minimum],
        "bounds_max_m": [float(value) for value in maximum],
        "bounds_size_m": [float(value) for value in maximum - minimum],
        "mesh_metrics": metrics,
        "renders": render_views(str(entry["id"]), render_objects, renders),
    }
    after = record(source_path)
    require(after == before, f"Source mutated during read-only evaluation: {source_path}")
    result["source_after"] = after
    result["source_unchanged"] = True
    return result


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args(argv)
    contract_path = Path(args.contract)
    attempt = Path(args.attempt)
    renders = attempt / "renders"
    renders.mkdir(parents=True, exist_ok=False)
    report_path = attempt / "source_evaluation_receipt.json"
    report: dict[str, object] = {
        "schema": "skyguard.m01-lighthouse-source-evaluation01.receipt.v1",
        "created_at_utc": utc_now(),
        "classification": "FAILED_WITH_EVIDENCE",
        "read_only": True,
        "sources": [],
        "render_count": 0,
        "error": None,
        "traceback": None,
    }
    exit_code = 3
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        require(contract["classification"] == "PASSED_READY_FOR_STANDING_AUTHORIZED_SINGLE_READ_ONLY_BLENDER_SOURCE_EVALUATION", "Contract classification changed")
        for entry in contract["authorities"]:
            authority(entry)
        for entry in contract["sources"]:
            report["sources"].append(evaluate_source(entry, renders))
        report["render_count"] = sum(len(row["renders"]) for row in report["sources"])
        require(report["render_count"] == 8, f"Expected eight renders; found {report['render_count']}")
        report["classification"] = "PASSED_SOURCE_EVALUATION_AWAITING_DIRECT_VISUAL_REVIEW"
        exit_code = 0
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        report["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(report_path, report)
        inventory = []
        for path in sorted(attempt.rglob("*")):
            if path.is_file() and path.name != "artifact_inventory.json":
                inventory.append(record(path))
        write_json_atomic(attempt / "artifact_inventory.json", {
            "schema": "skyguard.m01-lighthouse-source-evaluation01.artifact-inventory.v1",
            "created_at_utc": utc_now(),
            "classification": report["classification"],
            "artifacts": inventory,
        })
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
