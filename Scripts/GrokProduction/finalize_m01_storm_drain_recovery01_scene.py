from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
OUTPUT = ROOT / r"Production\Attempts\m01-storm-drain-grok-mcp-recovery01\attempt_20260811T101500000000Z\output"
CHECKPOINT = OUTPUT / "checkpoint"
RENDERS = OUTPUT / "renders"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
BLEND = OUTPUT / "M01_Promenade_StormDrain_Recovery01.blend"
GLB = EXPORTS / "M01_Promenade_StormDrain_Recovery01.glb"
REPORT = OUTPUT / "grok_implementation_report.json"

MESH_NAME = "SM_M01_Promenade_StormDrain_A"
SOCKET_NAME = "SOCKET_StormDrain_Origin"
COLLISION_NAME = "UCX_SM_M01_Promenade_StormDrain_A_00"
SOURCE_NAMES = {
    "SRC_StormDrain_Frame",
    "SRC_StormDrain_Grate",
    "SRC_StormDrain_DarkTray",
    "SRC_StormDrain_LiftingRecess_Left",
    "SRC_StormDrain_LiftingRecess_Right",
}
SLOT_NAMES = [f"SRC_StormDrain_Slot_{index:02d}" for index in range(1, 13)]
MATERIAL_NAMES = {
    "M_M01_StormDrain_CastIron",
    "M_M01_StormDrain_DarkRecess",
    "M_M01_StormDrain_EdgeWear",
}


def require(condition: object, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def look_at(camera: bpy.types.Object, target: Vector) -> None:
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()


def add_review_plane() -> bpy.types.Object:
    plane = bpy.data.objects.get("REVIEW_Ground")
    if plane is None:
        bpy.ops.mesh.primitive_plane_add(size=6.0, location=(0.0, 0.0, -0.004))
        plane = bpy.context.object
        plane.name = "REVIEW_Ground"
    material = bpy.data.materials.get("REVIEW_Ground_Material") or bpy.data.materials.new("REVIEW_Ground_Material")
    material.diffuse_color = (0.055, 0.06, 0.065, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.035, 0.04, 0.045, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.78
    if not plane.data.materials:
        plane.data.materials.append(material)
    plane.hide_render = False
    return plane


def ensure_review_rig() -> tuple[bpy.types.Object, bpy.types.Object, bpy.types.Object]:
    for name in ["REVIEW_Camera", "REVIEW_Key", "REVIEW_Fill"]:
        existing = bpy.data.objects.get(name)
        if existing:
            bpy.data.objects.remove(existing, do_unlink=True)
    camera_data = bpy.data.cameras.new("REVIEW_Camera_Data")
    camera = bpy.data.objects.new("REVIEW_Camera", camera_data)
    bpy.context.scene.collection.objects.link(camera)
    camera_data.lens = 56.0
    bpy.context.scene.camera = camera
    key_data = bpy.data.lights.new("REVIEW_Key_Data", type="AREA")
    key_data.energy = 850.0
    key_data.shape = "DISK"
    key_data.size = 2.2
    key = bpy.data.objects.new("REVIEW_Key", key_data)
    bpy.context.scene.collection.objects.link(key)
    fill_data = bpy.data.lights.new("REVIEW_Fill_Data", type="AREA")
    fill_data.energy = 360.0
    fill_data.size = 2.5
    fill = bpy.data.objects.new("REVIEW_Fill", fill_data)
    bpy.context.scene.collection.objects.link(fill)
    return camera, key, fill


def render_view(index: int, slug: str, camera: bpy.types.Object, key: bpy.types.Object, fill: bpy.types.Object, location: tuple[float, float, float], target: tuple[float, float, float], world_strength: float, key_energy: float, fill_energy: float) -> Path:
    camera.location = location
    look_at(camera, Vector(target))
    key.location = (1.4, -1.4, 2.0)
    look_at(key, Vector((0.0, 0.0, 0.0)))
    fill.location = (-1.2, 1.0, 1.0)
    look_at(fill, Vector((0.0, 0.0, 0.02)))
    key.data.energy = key_energy
    fill.data.energy = fill_energy
    world = bpy.context.scene.world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.075, 0.085, 0.105, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = world_strength
    path = RENDERS / f"{index:02d}_{slug}.png"
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return path


for directory in (OUTPUT, CHECKPOINT, RENDERS, EXPORTS, RECEIPTS):
    directory.mkdir(parents=True, exist_ok=True)

checkpoint_review_path = CHECKPOINT / "checkpoint_visual_review.json"
require(checkpoint_review_path.is_file(), "Missing checkpoint_visual_review.json")
checkpoint_review = json.loads(checkpoint_review_path.read_text(encoding="utf-8"))
require(checkpoint_review.get("classification") == "PASSED_CHECKPOINT_VISUAL_REVIEW", "Grok checkpoint review did not pass")
checkpoint_pngs = sorted(CHECKPOINT.glob("*.png"))
require(len(checkpoint_pngs) >= 3, f"Expected at least three checkpoint renders, found {len(checkpoint_pngs)}")
require(checkpoint_review.get("readable_slot_count") == 12, "Checkpoint review did not verify twelve readable slots")
require(checkpoint_review.get("lifting_recess_count") == 2, "Checkpoint review did not verify two lifting recesses")

required_names = {MESH_NAME, SOCKET_NAME, COLLISION_NAME, *SOURCE_NAMES, *SLOT_NAMES}
missing = sorted(required_names - set(bpy.data.objects.keys()))
require(not missing, f"Missing governed storm-drain objects: {missing}")
for scene_object in list(bpy.context.scene.objects):
    if scene_object.name not in required_names:
        scene_object.hide_render = True
mesh = bpy.data.objects[MESH_NAME]
socket = bpy.data.objects[SOCKET_NAME]
collision = bpy.data.objects[COLLISION_NAME]
require(mesh.type == "MESH", "Governed render object is not a mesh")
require(socket.type == "EMPTY", "Governed socket is not an Empty")
require(collision.type == "MESH", "Governed collision object is not a mesh")
require(mesh.parent is None and socket.parent is None and collision.parent is None, "Governed export objects must be world-root objects")
require(mesh.location.length <= 1e-5, f"Render mesh origin changed: {tuple(mesh.location)}")
require(max(abs(value - 1.0) for value in mesh.scale) <= 1e-5, f"Render mesh scale is unapplied: {tuple(mesh.scale)}")

dims = tuple(float(value) for value in mesh.dimensions)
require(abs(dims[0] - 0.68) <= 0.015, f"Storm-drain X dimension changed: {dims[0]}")
require(abs(dims[1] - 0.48) <= 0.015, f"Storm-drain Y dimension changed: {dims[1]}")
require(abs(dims[2] - 0.10) <= 0.012, f"Storm-drain Z dimension changed: {dims[2]}")
world_corners = [mesh.matrix_world @ Vector(corner) for corner in mesh.bound_box]
min_z = min(corner.z for corner in world_corners)
require(abs(min_z) <= 0.004, f"Storm-drain bottom is not grounded at Z=0: {min_z}")

slot_rows = []
for index, name in enumerate(SLOT_NAMES, start=1):
    marker = bpy.data.objects[name]
    require(marker.type in {"MESH", "EMPTY"}, f"Slot marker has invalid type: {name} {marker.type}")
    footprint = sorted([abs(float(marker.dimensions.x)), abs(float(marker.dimensions.y))])
    require(abs(footprint[0] - 0.035) <= 0.006 and abs(footprint[1] - 0.32) <= 0.02, f"Slot footprint changed: {name} {tuple(marker.dimensions)}")
    local_origin = mesh.matrix_world.inverted() @ Vector((marker.matrix_world.translation.x, marker.matrix_world.translation.y, 0.30))
    local_direction = (mesh.matrix_world.inverted().to_3x3() @ Vector((0.0, 0.0, -1.0))).normalized()
    hit, hit_location, _normal, _face = mesh.ray_cast(local_origin, local_direction, distance=1.0)
    require(hit, f"No recessed tray hit below slot: {name}")
    world_hit = mesh.matrix_world @ hit_location
    require(world_hit.z <= 0.042, f"Slot is blocked by top geometry: {name} hit Z={world_hit.z}")
    slot_rows.append({"name": name, "center": [float(marker.matrix_world.translation.x), float(marker.matrix_world.translation.y)], "tray_hit_z": float(world_hit.z)})

material_names = {slot.material.name for slot in mesh.material_slots if slot.material}
require(MATERIAL_NAMES.issubset(material_names), f"Required storm-drain materials are not assigned: {sorted(material_names)}")
require(len(mesh.data.vertices) >= 150, f"Render mesh is too simple for the governed detail contract: {len(mesh.data.vertices)} vertices")
require(len(mesh.data.polygons) >= 120, f"Render mesh is too simple for the governed detail contract: {len(mesh.data.polygons)} polygons")

for name in SOURCE_NAMES | set(SLOT_NAMES):
    source = bpy.data.objects[name]
    source.hide_render = True
    source.hide_set(True)
collision.hide_render = True
collision.display_type = "WIRE"
socket.empty_display_type = "PLAIN_AXES"
socket.empty_display_size = 0.08

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.use_file_extension = True
scene.world = scene.world or bpy.data.worlds.new("World")
add_review_plane()
camera, key, fill = ensure_review_rig()

views = [
    (1, "day_front_left", (1.18, -1.05, 0.72), (0.0, 0.0, 0.04), 0.40, 980.0, 320.0),
    (2, "day_front_right", (-1.15, -1.0, 0.68), (0.0, 0.0, 0.04), 0.40, 930.0, 360.0),
    (3, "top_orthographic_like", (0.0, 0.0, 1.55), (0.0, 0.0, 0.02), 0.52, 760.0, 300.0),
    (4, "grazing_slot_read", (1.1, -1.6, 0.23), (0.0, 0.0, 0.055), 0.28, 1150.0, 260.0),
    (5, "overcast", (1.0, 1.15, 0.64), (0.0, 0.0, 0.035), 0.20, 520.0, 430.0),
    (6, "wet_highlight", (-0.95, 1.05, 0.42), (0.0, 0.0, 0.045), 0.16, 1350.0, 160.0),
    (7, "night", (1.25, -1.25, 0.48), (0.0, 0.0, 0.04), 0.025, 520.0, 55.0),
    (8, "cockpit_worklight", (-1.15, -1.3, 0.55), (0.0, 0.0, 0.04), 0.05, 760.0, 90.0),
]
render_paths = [render_view(*view, camera, key, fill) for view in views]

bpy.ops.object.select_all(action="DESELECT")
for export_object in (mesh, socket, collision):
    export_object.hide_set(False)
    export_object.select_set(True)
bpy.context.view_layer.objects.active = mesh
bpy.ops.export_scene.gltf(
    filepath=str(GLB),
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_yup=True,
    export_cameras=False,
    export_lights=False,
)
collision.hide_set(True)
socket.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

report = {
    "schema": "skyguard.m01-storm-drain.grok-mcp.recovery01.implementation.v1",
    "classification": "PASSED_AWAITING_DIRECT_VISUAL_REVIEW",
    "asset": "M01 promenade storm drain",
    "bounds_m": list(dims),
    "min_z_m": min_z,
    "slot_count": len(slot_rows),
    "slots": slot_rows,
    "lifting_recess_count": 2,
    "materials": sorted(material_names),
    "render_mesh": {"name": MESH_NAME, "vertices": len(mesh.data.vertices), "polygons": len(mesh.data.polygons)},
    "socket": SOCKET_NAME,
    "collision": COLLISION_NAME,
    "checkpoint_review": record(checkpoint_review_path),
    "checkpoint_renders": [record(path) for path in checkpoint_pngs],
    "final_renders": [record(path) for path in render_paths],
    "blend": record(BLEND),
    "glb": record(GLB),
    "unreal_import_performed": False,
}
write_json(REPORT, report)
write_json(RECEIPTS / "storm_drain_geometry_receipt.json", report)
print("SKYGUARD_M01_STORM_DRAIN_RECOVERY01_FINALIZER_PASS")
