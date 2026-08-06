from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


SDK_VERSION = "1.0.0"


class WorkerError(RuntimeError):
    pass


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def blender_module():
    try:
        import bpy  # type: ignore
    except ImportError as exc:
        raise WorkerError("This module must execute inside Blender.") from exc
    return bpy


def parse_worker_args(argv: list[str] | None = None) -> argparse.Namespace:
    source = list(sys.argv if argv is None else argv)
    if "--" in source:
        source = source[source.index("--") + 1 :]
    parser = argparse.ArgumentParser(description="Skyguard Blender production worker.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", required=True)
    return parser.parse_args(source)


def configure_scene() -> Any:
    bpy = blender_module()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"
    # Blender 5.2 exposes Eevee Next under the stable BLENDER_EEVEE enum.
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    if scene.world is None:
        scene.world = bpy.data.worlds.new("SkyguardReviewWorld")
    scene.world.color = (0.025, 0.035, 0.05)
    return scene


def create_collection(name: str) -> Any:
    bpy = blender_module()
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj: Any, collection: Any) -> None:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def create_socket(name: str, location: tuple[float, float, float], collection: Any) -> Any:
    if not name.startswith("SOCKET_"):
        raise WorkerError(f"Socket must use SOCKET_ prefix: {name}")
    bpy = blender_module()
    socket = bpy.data.objects.new(name, None)
    socket.empty_display_type = "PLAIN_AXES"
    socket.empty_display_size = 0.025
    socket.location = location
    collection.objects.link(socket)
    return socket


def pbr_material(
    name: str,
    base_color: tuple[float, float, float, float],
    metallic: float,
    roughness: float,
) -> Any:
    bpy = blender_module()
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled is None:
        raise WorkerError(f"Principled BSDF is missing from {name}.")
    principled.inputs["Base Color"].default_value = base_color
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    return material


def asset_bounds(collection: Any) -> tuple[tuple[float, float, float], float]:
    from mathutils import Vector  # type: ignore

    corners = []
    for obj in collection.all_objects:
        if obj.type != "MESH":
            continue
        corners.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not corners:
        raise WorkerError("Asset collection contains no mesh bounds.")
    minimum = Vector(
        (
            min(point.x for point in corners),
            min(point.y for point in corners),
            min(point.z for point in corners),
        )
    )
    maximum = Vector(
        (
            max(point.x for point in corners),
            max(point.y for point in corners),
            max(point.z for point in corners),
        )
    )
    center = (minimum + maximum) / 2
    radius = max((maximum - minimum).length / 2, 0.1)
    return (center.x, center.y, center.z), radius


def add_review_stage(asset_collection: Any) -> tuple[Any, Any]:
    bpy = blender_module()
    from mathutils import Vector  # type: ignore

    review = create_collection("REVIEW_ONLY")
    center, radius = asset_bounds(asset_collection)

    bpy.ops.mesh.primitive_plane_add(size=max(radius * 8, 4.0), location=(center[0], center[1], center[2] - radius))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    ground.data.materials.append(pbr_material("MAT_REVIEW_Ground", (0.08, 0.09, 0.11, 1), 0.0, 0.8))
    move_to_collection(ground, review)

    bpy.ops.object.light_add(type="AREA", location=(center[0] + radius * 2, center[1] - radius * 2, center[2] + radius * 3))
    key = bpy.context.object
    key.name = "REVIEW_Key"
    key.data.energy = 1400
    key.data.shape = "DISK"
    key.data.size = radius * 2.5
    move_to_collection(key, review)

    direction = Vector(center) - key.location
    key.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    bpy.ops.object.light_add(type="AREA", location=(center[0] - radius * 2, center[1] + radius, center[2] + radius))
    fill = bpy.context.object
    fill.name = "REVIEW_Fill"
    fill.data.energy = 650
    fill.data.size = radius * 2
    move_to_collection(fill, review)
    direction = Vector(center) - fill.location
    fill.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    camera_data = bpy.data.cameras.new("REVIEW_Camera")
    camera = bpy.data.objects.new("REVIEW_Camera", camera_data)
    review.objects.link(camera)
    bpy.context.scene.camera = camera
    return review, camera


def render_review_views(asset_collection: Any, output: Path) -> list[Path]:
    bpy = blender_module()
    from mathutils import Vector  # type: ignore

    _review, camera = add_review_stage(asset_collection)
    center, radius = asset_bounds(asset_collection)
    target = Vector(center)
    views = [
        ("front", (0.0, -3.2, 0.3)),
        ("rear", (0.0, 3.2, 0.3)),
        ("left", (-3.2, 0.0, 0.3)),
        ("right", (3.2, 0.0, 0.3)),
        ("top", (0.0, -0.3, 3.6)),
        ("three_quarter", (2.6, -2.6, 1.8)),
    ]
    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, direction in views:
        camera.location = target + Vector(direction) * radius
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.lens = 55
        path = render_dir / f"{name}.png"
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        paths.append(path)
    return paths


def validate_asset(collection: Any, required_sockets: list[str]) -> dict[str, Any]:
    meshes = [obj for obj in collection.all_objects if obj.type == "MESH"]
    if not meshes:
        raise WorkerError("Asset collection contains no mesh objects.")
    duplicate_names = [
        name
        for name in {obj.name for obj in collection.all_objects}
        if sum(obj.name == name for obj in collection.all_objects) > 1
    ]
    if duplicate_names:
        raise WorkerError(f"Duplicate object names: {duplicate_names}")

    missing_uv = [obj.name for obj in meshes if not obj.data.uv_layers]
    missing_sockets = [
        name
        for name in required_sockets
        if not any(obj.name == name and obj.type == "EMPTY" for obj in collection.all_objects)
    ]
    invalid_scale = [
        obj.name
        for obj in meshes
        if any(abs(value - 1.0) > 1e-4 for value in obj.scale)
    ]
    if missing_uv:
        raise WorkerError(f"Mesh objects without UVs: {missing_uv}")
    if missing_sockets:
        raise WorkerError(f"Required sockets are missing: {missing_sockets}")
    if invalid_scale:
        raise WorkerError(f"Mesh transforms were not applied: {invalid_scale}")

    triangles = 0
    vertices = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        triangles += len(obj.data.loop_triangles)
        vertices += len(obj.data.vertices)
    return {
        "mesh_objects": len(meshes),
        "vertices": vertices,
        "triangles": triangles,
        "materials": len({slot.material.name for obj in meshes for slot in obj.material_slots if slot.material}),
        "required_sockets": required_sockets,
    }


def export_asset(asset_id: str, collection: Any, output: Path) -> tuple[Path, Path]:
    bpy = blender_module()
    blend_path = output / f"{asset_id}.blend"
    glb_path = output / f"{asset_id}.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in collection.all_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = next(
        (obj for obj in collection.all_objects if obj.type == "MESH"),
        None,
    )
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
    )
    return blend_path, glb_path


def run_worker(
    asset_id: str,
    build: Callable[[Any], None],
    required_sockets: list[str],
    argv: list[str] | None = None,
) -> int:
    args = parse_worker_args(argv)
    if args.asset_id != asset_id:
        raise WorkerError(f"Worker asset id {asset_id} does not match {args.asset_id}.")
    output = Path(args.output)
    if output.exists() and any(output.iterdir()):
        raise WorkerError(f"Output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    scene = configure_scene()
    asset_collection = create_collection("ASSET")
    build(asset_collection)
    validation = validate_asset(asset_collection, required_sockets)
    renders = render_review_views(asset_collection, output)
    blend_path, glb_path = export_asset(asset_id, asset_collection, output)
    receipt = {
        "schema": "skyguard.blender-worker-receipt.v1",
        "sdk_version": SDK_VERSION,
        "asset_id": asset_id,
        "created_at_utc": now_utc(),
        "blender_version": blender_module().app.version_string,
        "unit_system": scene.unit_settings.system,
        "scale_length": scene.unit_settings.scale_length,
        "validation": validation,
        "artifacts": [
            {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in [blend_path, glb_path, *renders]
        ],
    }
    receipt_path = output / "artifact_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"asset_id": asset_id, "status": "awaiting_review"}))
    return 0
