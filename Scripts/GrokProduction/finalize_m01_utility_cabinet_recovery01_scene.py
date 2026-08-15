from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT = Path(r"D:\Skyguard52")
OUTPUT = PROJECT / "Production" / "Attempts" / "m01-utility-cabinet-grok-mcp-recovery01" / "attempt_20260811T091500000000Z" / "output"
CHECKPOINT = OUTPUT / "checkpoint"
RENDERS = OUTPUT / "renders"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
FINAL_BLEND = OUTPUT / "M01_Promenade_UtilityCabinet_Recovery01.blend"
FINAL_GLB = EXPORTS / "M01_Promenade_UtilityCabinet_Recovery01.glb"
MESH_NAME = "SM_M01_Promenade_UtilityCabinet_A"
SOCKET_NAME = "SOCKET_UtilityCabinet_Origin"
COLLISION_PREFIX = "UCX_SM_M01_Promenade_UtilityCabinet_A_"
SOURCE_NAMES = [
    "SRC_UtilityCabinet_BodyShell",
    "SRC_UtilityCabinet_Door_Left",
    "SRC_UtilityCabinet_Door_Right",
    "SRC_UtilityCabinet_Plinth",
    "SRC_UtilityCabinet_WeatherHood",
    "SRC_UtilityCabinet_Latch",
    "SRC_UtilityCabinet_Vent_Left",
    "SRC_UtilityCabinet_Vent_Right",
]
CHECKPOINT_FILES = [
    "01_front_full_daylight.png",
    "02_front_threequarter_daylight.png",
    "03_rear_threequarter_overcast.png",
    "04_left_side_vents.png",
    "05_right_side_vents.png",
    "06_door_latch_hinges_close.png",
    "07_plinth_and_door_gap_wet.png",
    "08_eye_level_context.png",
]


def fail(message: str) -> None:
    raise RuntimeError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def ensure_collection(name: str):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def clear_collection(collection) -> None:
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    minimum = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
    maximum = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
    return minimum, maximum


def look_at(obj, target) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def make_camera(direction, occupancy, lens, target_offset):
    obj = bpy.data.objects[MESH_NAME]
    minimum, maximum = bounds(obj)
    center = (minimum + maximum) * 0.5 + Vector(target_offset)
    extent = maximum - minimum
    radius = max(extent.x, extent.y, extent.z) * 0.5
    data = bpy.data.cameras.new("REVIEW_Camera_Data")
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.025
    data.clip_end = 200.0
    camera = bpy.data.objects.new("REVIEW_Camera", data)
    ensure_collection("REVIEW_ONLY").objects.link(camera)
    half_fov = math.atan((data.sensor_width * 0.5) / data.lens)
    distance = max(radius, 0.45) / max(math.sin(half_fov) * occupancy, 0.05)
    camera.location = center + Vector(direction).normalized() * distance
    look_at(camera, center)
    return camera


def make_area(name, location, energy, size, color, target) -> None:
    data = bpy.data.lights.new(name + "_Data", "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    light = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(light)
    light.location = location
    look_at(light, target)


def make_sun(name, rotation, energy, color) -> None:
    data = bpy.data.lights.new(name + "_Data", "SUN")
    data.energy = energy
    data.angle = math.radians(3.0)
    data.color = color
    light = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(light)
    light.rotation_euler = rotation


def create_ground(center) -> None:
    bpy.ops.mesh.primitive_plane_add(size=20.0, location=(center.x, center.y, -0.012))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    for collection in list(ground.users_collection):
        collection.objects.unlink(ground)
    ensure_collection("REVIEW_ONLY").objects.link(ground)
    material = bpy.data.materials.get("REVIEW_Ground_Mat") or bpy.data.materials.new("REVIEW_Ground_Mat")
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.045, 0.055, 0.065, 1.0)
    principled.inputs["Roughness"].default_value = 0.78
    ground.data.materials.append(material)


def configure_stage(mode: str) -> None:
    review = ensure_collection("REVIEW_ONLY")
    clear_collection(review)
    obj = bpy.data.objects[MESH_NAME]
    minimum, maximum = bounds(obj)
    center = (minimum + maximum) * 0.5
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if mode == "wet":
        background.inputs["Color"].default_value = (0.06, 0.08, 0.11, 1.0)
        background.inputs["Strength"].default_value = 0.42
        make_area("REVIEW_WetKey", center + Vector((-3.0, -4.5, 5.0)), 1150.0, 4.5, (0.54, 0.72, 1.0), center)
        make_area("REVIEW_WetRim", center + Vector((3.5, 2.0, 2.8)), 620.0, 3.0, (1.0, 0.62, 0.38), center)
        bpy.context.scene.view_settings.exposure = 0.30
    elif mode == "overcast":
        background.inputs["Color"].default_value = (0.18, 0.23, 0.30, 1.0)
        background.inputs["Strength"].default_value = 0.58
        make_area("REVIEW_CloudKey", center + Vector((-3.5, -4.0, 6.0)), 1000.0, 6.0, (0.78, 0.88, 1.0), center)
        make_area("REVIEW_CloudFill", center + Vector((3.0, 1.5, 3.5)), 420.0, 4.0, (0.56, 0.68, 0.85), center)
        bpy.context.scene.view_settings.exposure = 0.05
    else:
        background.inputs["Color"].default_value = (0.25, 0.39, 0.58, 1.0)
        background.inputs["Strength"].default_value = 0.50
        make_sun("REVIEW_Sun", (math.radians(28), math.radians(-18), math.radians(-32)), 1.6, (1.0, 0.82, 0.65))
        make_area("REVIEW_SkyFill", center + Vector((3.0, -4.0, 5.0)), 620.0, 5.0, (0.55, 0.73, 1.0), center)
        bpy.context.scene.view_settings.exposure = -0.10
    bpy.context.scene.view_settings.view_transform = "AgX"
    bpy.context.scene.view_settings.look = "AgX - Medium High Contrast"
    create_ground(center)


def mean_luminance():
    image = bpy.data.images.get("Render Result")
    if image is None or not image.has_data:
        return None
    pixels = image.pixels[:]
    count = len(pixels) // 4
    stride = max(count // 4096, 1)
    values = []
    for index in range(0, count, stride):
        red, green, blue = pixels[index * 4:index * 4 + 3]
        values.append(0.2126 * red + 0.7152 * green + 0.0722 * blue)
    return sum(values) / len(values)


def render_shot(filename, direction, mode, occupancy, lens, target_offset=(0.0, 0.0, 0.0)):
    configure_stage(mode)
    camera = make_camera(direction, occupancy, lens, target_offset)
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.filepath = str(RENDERS / filename)
    bpy.ops.render.render(write_still=True)
    luminance = mean_luminance()
    if luminance is not None and luminance < 0.065:
        scene.view_settings.exposure += 0.8
        bpy.ops.render.render(write_still=True)
        luminance = mean_luminance()
    elif luminance is not None and luminance > 0.72:
        scene.view_settings.exposure -= 0.7
        bpy.ops.render.render(write_still=True)
        luminance = mean_luminance()
    return {"file": filename, "mode": mode, "mean_luminance": luminance}


for directory in (OUTPUT, CHECKPOINT, RENDERS, EXPORTS, RECEIPTS):
    directory.mkdir(parents=True, exist_ok=True)

checkpoint_review = CHECKPOINT / "checkpoint_visual_review.json"
require(checkpoint_review.is_file(), "Missing checkpoint visual review")
for filename in CHECKPOINT_FILES:
    path = CHECKPOINT / filename
    require(path.is_file(), f"Missing checkpoint render: {filename}")

obj = bpy.data.objects.get(MESH_NAME)
require(obj is not None and obj.type == "MESH", f"Missing required mesh: {MESH_NAME}")
require(all(abs(value - 1.0) <= 0.001 for value in obj.scale), f"Unapplied scale: {tuple(obj.scale)}")
require(all(abs(value) <= 0.001 for value in obj.rotation_euler), f"Unapplied rotation: {tuple(obj.rotation_euler)}")
require(len(obj.data.uv_layers) > 0, "Missing UV map")
require(len(obj.material_slots) >= 4, "Expected at least four material slots")
require(all(slot.material is not None for slot in obj.material_slots), "Null material slot")
require(len(obj.data.vertices) >= 1000, f"Vertex count too low: {len(obj.data.vertices)}")
require(len(obj.data.polygons) <= 60000, f"Polygon count too high: {len(obj.data.polygons)}")

source_collection = bpy.data.collections.get("SOURCE_CONSTRUCTION")
require(source_collection is not None, "Missing SOURCE_CONSTRUCTION collection")
source_records = []
for name in SOURCE_NAMES:
    source = bpy.data.objects.get(name)
    require(source is not None, f"Missing retained construction object: {name}")
    require(source.hide_render, f"Construction object must be hidden from renders: {name}")
    require(source in source_collection.objects[:], f"Construction object not linked to SOURCE_CONSTRUCTION: {name}")
    require(all(abs(value - 1.0) <= 0.001 for value in source.scale), f"Construction scale not applied: {name}")
    require(all(abs(value) <= 0.001 for value in source.rotation_euler), f"Construction rotation not applied: {name}")
    source_records.append(name)

socket = bpy.data.objects.get(SOCKET_NAME)
require(socket is not None and socket.type == "EMPTY", f"Missing socket empty: {SOCKET_NAME}")
require(socket.location.length <= 0.002, f"Socket is not at world origin: {tuple(socket.location)}")
collisions = sorted(item.name for item in bpy.data.objects if item.name.startswith(COLLISION_PREFIX))
require(1 <= len(collisions) <= 3, f"Expected one to three UCX collisions, found {len(collisions)}")

minimum, maximum = bounds(obj)
dimensions = maximum - minimum
dimension_limits = ((0.82, 1.02), (0.38, 0.54), (1.25, 1.50))
for axis, value, limits in zip("XYZ", dimensions, dimension_limits):
    require(limits[0] <= value <= limits[1], f"{axis} dimension {value:.6f} outside [{limits[0]:.6f}, {limits[1]:.6f}]")
require(-0.025 <= minimum.z <= 0.025, f"Cabinet is not grounded: min Z {minimum.z:.6f}")

for item in bpy.data.objects:
    item.hide_render = True
obj.hide_render = False

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.render.use_file_extension = True

shots = [
    ("01_front_full_daylight.png", (1.15, -2.5, 1.05), "daylight", 0.67, 58.0, (0.0, 0.0, 0.02)),
    ("02_front_threequarter_daylight.png", (-1.3, -2.2, 1.0), "daylight", 0.70, 62.0, (0.0, 0.0, 0.03)),
    ("03_rear_threequarter_overcast.png", (1.3, 2.1, 0.95), "overcast", 0.68, 60.0, (0.0, 0.0, 0.02)),
    ("04_left_side_vents.png", (-2.2, -0.25, 0.9), "overcast", 0.77, 72.0, (0.0, 0.0, 0.02)),
    ("05_right_side_vents.png", (2.2, -0.25, 0.9), "overcast", 0.77, 72.0, (0.0, 0.0, 0.02)),
    ("06_door_latch_hinges_close.png", (0.65, -2.0, 0.85), "daylight", 0.86, 82.0, (0.05, -0.02, 0.10)),
    ("07_plinth_and_door_gap_wet.png", (-0.5, -1.7, 0.35), "wet", 0.83, 76.0, (0.0, -0.02, -0.34)),
    ("08_eye_level_context.png", (1.8, -3.4, 1.15), "daylight", 0.58, 52.0, (0.0, 0.0, 0.03)),
]
render_receipts = [render_shot(*shot) for shot in shots]

review = bpy.data.collections.get("REVIEW_ONLY")
if review is not None:
    clear_collection(review)
for item in bpy.data.objects:
    if item.name == MESH_NAME:
        item.hide_render = False
    elif item.name in SOURCE_NAMES or item.name.startswith("UCX_") or item.name.startswith("SOCKET_"):
        item.hide_render = True

bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

bpy.ops.object.select_all(action="DESELECT")
for name in [MESH_NAME, SOCKET_NAME] + collisions:
    item = bpy.data.objects.get(name)
    if item is not None:
        item.hide_set(False)
        item.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.export_scene.gltf(
    filepath=str(FINAL_GLB),
    export_format="GLB",
    use_selection=True,
    export_yup=True,
    export_apply=True,
    export_extras=True,
    export_materials="EXPORT",
    export_cameras=False,
    export_lights=False,
)

report = {
    "schema": "skyguard.m01-utility-cabinet.grok-mcp.recovery01.report.v1",
    "classification": "PASSED_AWAITING_DIRECT_VISUAL_REVIEW",
    "mesh": MESH_NAME,
    "socket": SOCKET_NAME,
    "collision": collisions,
    "source_construction": source_records,
    "vertices": len(obj.data.vertices),
    "polygons": len(obj.data.polygons),
    "dimensions_m": [dimensions.x, dimensions.y, dimensions.z],
    "bounds_min_m": list(minimum),
    "bounds_max_m": list(maximum),
    "materials": [slot.material.name for slot in obj.material_slots],
    "uv_layers": [layer.name for layer in obj.data.uv_layers],
    "renders": render_receipts,
    "glb": str(FINAL_GLB),
    "limitations": [
        "Direct full-resolution visual review remains required",
        "Candidate is scoped to mid-distance Mission 1 environment use",
        "Unreal import and mapped D3D12 review remain separate gates",
    ],
}
write_json(OUTPUT / "grok_implementation_report.json", report)
write_json(RECEIPTS / "structure_and_dimensions.json", report)

artifacts = []
for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file() and item.name != "artifact_inventory.json"):
    artifacts.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
write_json(RECEIPTS / "artifact_inventory.json", {"schema": "skyguard.artifact-inventory.v1", "artifacts": artifacts})

print("PASSED_AWAITING_DIRECT_VISUAL_REVIEW")
