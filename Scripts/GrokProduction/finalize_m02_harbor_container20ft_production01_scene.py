from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
OUTPUT = ROOT / r"Production\Attempts\m02-harbor-container20ft-grok-mcp-production01\attempt_20260811T1230000000000Z\output"
CHECKPOINT = OUTPUT / "checkpoint"
RENDERS = OUTPUT / "renders"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
FINAL_BLEND = OUTPUT / "M02_Harbor_Container20ft_Production01.blend"
FINAL_GLB = EXPORTS / "M02_Harbor_Container20ft_Production01.glb"

MESH_NAME = "SM_M02_Harbor_Container20ft_A"
SOCKET_NAME = "SOCKET_Container_Origin"
COLLISION_NAME = "UCX_SM_M02_Harbor_Container20ft_A_00"
SOURCE_NAMES = {
    "SRC_Container_Shell",
    "SRC_Container_Corrugation",
    "SRC_Container_EndFrames",
    "SRC_Container_Doors",
    "SRC_Container_Hardware",
    "SRC_Container_Underframe",
}
MATERIAL_NAMES = {
    "M_M02_Container_WeatheredPaint",
    "M_M02_Container_GalvanizedHardware",
    "M_M02_Container_RubberGasket",
}
CHECK_KEYS = {
    "complete_container_visible",
    "corrugation_consistent",
    "door_hardware_complete",
    "corner_castings_integrated",
    "underframe_connected",
    "no_floating_or_intersecting_parts",
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def object_bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    minimum = Vector(tuple(min(point[index] for point in points) for index in range(3)))
    maximum = Vector(tuple(max(point[index] for point in points) for index in range(3)))
    return minimum, maximum


def ensure_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def clear_review():
    collection = ensure_collection("REVIEW_ONLY")
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area(name, location, energy, size, color, target=(0.0, 0.0, 1.25)):
    data = bpy.data.lights.new(name + "_Data", "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(obj)
    obj.location = location
    look_at(obj, target)


def sun(name, rotation, energy, color):
    data = bpy.data.lights.new(name + "_Data", "SUN")
    data.energy = energy
    data.angle = math.radians(3.0)
    data.color = color
    obj = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(obj)
    obj.rotation_euler = rotation


def ground():
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0.0, 0.0, -0.012))
    obj = bpy.context.object
    obj.name = "REVIEW_Ground"
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    ensure_collection("REVIEW_ONLY").objects.link(obj)
    material = bpy.data.materials.get("REVIEW_Quay_Mat") or bpy.data.materials.new("REVIEW_Quay_Mat")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.075, 0.085, 0.095, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.78
    obj.data.materials.append(material)


def stage(mode):
    clear_review()
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    scene = bpy.context.scene
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.45
    if mode == "night":
        background.inputs["Color"].default_value = (0.018, 0.030, 0.055, 1.0)
        background.inputs["Strength"].default_value = 0.28
        area("REVIEW_Moon", (-7.0, -8.0, 8.0), 2600.0, 5.0, (0.34, 0.54, 1.0))
        area("REVIEW_HarborRim", (6.0, 4.0, 4.5), 1900.0, 4.0, (1.0, 0.42, 0.16))
        scene.view_settings.exposure = 1.35
    elif mode == "wet":
        background.inputs["Color"].default_value = (0.10, 0.15, 0.22, 1.0)
        background.inputs["Strength"].default_value = 0.60
        area("REVIEW_WetKey", (-6.0, -7.5, 7.0), 3200.0, 6.0, (0.55, 0.72, 1.0))
        area("REVIEW_WetRim", (6.5, 4.5, 4.0), 1800.0, 4.0, (1.0, 0.52, 0.24))
        scene.view_settings.exposure = 0.90
    elif mode == "overcast":
        background.inputs["Color"].default_value = (0.27, 0.34, 0.43, 1.0)
        background.inputs["Strength"].default_value = 0.90
        area("REVIEW_CloudKey", (-6.0, -7.0, 8.0), 3000.0, 7.0, (0.76, 0.86, 1.0))
        area("REVIEW_CloudFill", (6.0, 4.5, 5.0), 1500.0, 5.0, (0.62, 0.70, 0.82))
        scene.view_settings.exposure = 0.65
    elif mode == "cockpit":
        background.inputs["Color"].default_value = (0.025, 0.035, 0.055, 1.0)
        background.inputs["Strength"].default_value = 0.32
        area("REVIEW_Worklight", (6.0, -7.0, 5.5), 3000.0, 5.0, (0.50, 0.76, 1.0))
        area("REVIEW_Amber", (-5.0, 4.0, 3.5), 1800.0, 4.0, (1.0, 0.44, 0.16))
        scene.view_settings.exposure = 1.15
    else:
        background.inputs["Color"].default_value = (0.38, 0.55, 0.76, 1.0)
        background.inputs["Strength"].default_value = 0.82
        sun("REVIEW_Sun", (math.radians(30), math.radians(-18), math.radians(-34)), 2.4, (1.0, 0.82, 0.62))
        area("REVIEW_Sky", (6.0, -8.0, 8.0), 2300.0, 6.0, (0.55, 0.72, 1.0))
        area("REVIEW_Bounce", (-6.0, 5.0, 4.0), 1100.0, 4.0, (1.0, 0.50, 0.25))
        scene.view_settings.exposure = 0.55
    ground()


def camera(location, target, lens):
    data = bpy.data.cameras.new("REVIEW_Camera_Data")
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.05
    data.clip_end = 200.0
    obj = bpy.data.objects.new("REVIEW_Camera", data)
    ensure_collection("REVIEW_ONLY").objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def luminance():
    image = bpy.data.images.get("Render Result")
    if image is None or not image.has_data:
        return None
    pixels = image.pixels[:]
    count = len(pixels) // 4
    stride = max(count // 8192, 1)
    values = []
    for index in range(0, count, stride):
        r, g, b = pixels[index * 4:index * 4 + 3]
        values.append(0.2126 * r + 0.7152 * g + 0.0722 * b)
    return sum(values) / len(values)


def render_view(filename, location, target, lens, mode):
    stage(mode)
    scene = bpy.context.scene
    scene.camera = camera(location, target, lens)
    scene.render.filepath = str(RENDERS / filename)
    bpy.ops.render.render(write_still=True)
    mean = luminance()
    rerenders = 0
    while mean is not None and mean < 0.10 and rerenders < 2:
        scene.view_settings.exposure += 1.0
        bpy.ops.render.render(write_still=True)
        mean = luminance()
        rerenders += 1
    if mean is not None and mean > 0.76:
        scene.view_settings.exposure -= 0.8
        bpy.ops.render.render(write_still=True)
        mean = luminance()
    return {"path": str(RENDERS / filename), "mode": mode, "mean_luminance": mean, "exposure_rerenders": rerenders}


def normalize(name, color, metallic, roughness):
    material = bpy.data.materials.get(name)
    require(material is not None, f"Missing material: {name}")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    require(bsdf is not None, f"Missing Principled BSDF: {name}")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness


def export_selected(path):
    bpy.ops.object.select_all(action="DESELECT")
    for name in (MESH_NAME, SOCKET_NAME, COLLISION_NAME):
        bpy.data.objects[name].select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(path), export_format="GLB", use_selection=True,
        export_yup=True, export_apply=True, export_extras=True,
        export_materials="EXPORT", export_cameras=False, export_lights=False,
    )


def read_glb_json(path):
    with path.open("rb") as stream:
        magic, version, total_length = struct.unpack("<4sII", stream.read(12))
        require(magic == b"glTF" and version == 2, "Invalid GLB header")
        chunk_length, chunk_type = struct.unpack("<II", stream.read(8))
        require(chunk_type == 0x4E4F534A, "GLB JSON chunk is missing")
        payload = stream.read(chunk_length).decode("utf-8").rstrip(" \t\r\n\x00")
    require(total_length == path.stat().st_size, "GLB declared length mismatch")
    return json.loads(payload)


for directory in (OUTPUT, CHECKPOINT, RENDERS, EXPORTS, RECEIPTS):
    directory.mkdir(parents=True, exist_ok=True)

review_path = CHECKPOINT / "checkpoint_visual_review.json"
require(review_path.is_file(), "Missing checkpoint visual review")
review = json.loads(review_path.read_text(encoding="utf-8"))
require(review.get("classification") in {"PASSED_CHECKPOINT_VISUAL_REVIEW", "PENDING_IMAGE_INSPECTION"}, "Invalid checkpoint classification")
checks = review.get("checks")
require(isinstance(checks, dict), "Checkpoint checks object is absent")
require(CHECK_KEYS.issubset(checks), f"Checkpoint checks are incomplete: {sorted(CHECK_KEYS - set(checks))}")
if review.get("classification") == "PASSED_CHECKPOINT_VISUAL_REVIEW":
    require(all(checks[key] is True for key in CHECK_KEYS), "A passed checkpoint contains false checks")
checkpoint_renders = sorted(CHECKPOINT.glob("*.png"))
require(len(checkpoint_renders) >= 5, f"Expected at least five checkpoint renders, found {len(checkpoint_renders)}")

for name in sorted({MESH_NAME, SOCKET_NAME, COLLISION_NAME} | SOURCE_NAMES):
    require(bpy.data.objects.get(name) is not None, f"Missing required object: {name}")
mesh = bpy.data.objects[MESH_NAME]
socket = bpy.data.objects[SOCKET_NAME]
collision = bpy.data.objects[COLLISION_NAME]
require(mesh.type == "MESH" and collision.type == "MESH" and socket.type == "EMPTY", "Governed object type mismatch")
require(all(abs(value) <= 0.001 for value in mesh.location), f"Mesh is not at origin: {tuple(mesh.location)}")
require(all(abs(value) <= 0.001 for value in mesh.rotation_euler), "Mesh rotation is not applied")
require(all(abs(value - 1.0) <= 0.001 for value in mesh.scale), "Mesh scale is not applied")
require(all(abs(value) <= 0.001 for value in socket.location), "Socket is not at world origin")
socket.empty_display_type = "PLAIN_AXES"
require(mesh.data.uv_layers.get("UVMap") is not None, "Governed mesh lacks UVMap")
vertices = len(mesh.data.vertices)
polygons = len(mesh.data.polygons)
require(vertices >= 3500, f"Vertex count too low: {vertices}")
require(polygons >= 2800, f"Polygon count too low: {polygons}")

minimum, maximum = object_bounds(mesh)
dimensions = maximum - minimum
require(abs(dimensions.x - 6.058) <= 0.030, f"Length outside contract: {dimensions.x}")
require(abs(dimensions.y - 2.438) <= 0.030, f"Width outside contract: {dimensions.y}")
require(abs(dimensions.z - 2.591) <= 0.030, f"Height outside contract: {dimensions.z}")
require(abs(minimum.z) <= 0.020, f"Bottom is not grounded: {minimum.z}")
require(abs((minimum.x + maximum.x) * 0.5) <= 0.020, "Container is not centered on X")
require(abs((minimum.y + maximum.y) * 0.5) <= 0.020, "Container is not centered on Y")

slot_materials = {slot.material.name for slot in mesh.material_slots if slot.material is not None}
require(MATERIAL_NAMES.issubset(slot_materials), f"Missing materials: {sorted(MATERIAL_NAMES - slot_materials)}")
normalize("M_M02_Container_WeatheredPaint", (0.055, 0.16, 0.24), 0.62, 0.52)
normalize("M_M02_Container_GalvanizedHardware", (0.24, 0.29, 0.33), 0.90, 0.30)
normalize("M_M02_Container_RubberGasket", (0.010, 0.012, 0.014), 0.05, 0.76)

for obj in bpy.data.objects:
    obj.hide_render = obj.name != MESH_NAME
mesh.hide_render = False

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False

views = [
    ("01_daylight_door_end_three_quarter.png", (8.8, -8.5, 5.1), (0.6, 0.0, 1.25), 54.0, "daylight"),
    ("02_daylight_front_opposite_three_quarter.png", (-8.8, 8.2, 4.8), (-0.5, 0.0, 1.22), 54.0, "daylight"),
    ("03_door_hardware_detail.png", (5.7, -3.2, 2.8), (3.02, 0.0, 1.28), 62.0, "overcast"),
    ("04_side_corrugation_corner_detail.png", (1.6, -4.8, 2.8), (1.4, -1.18, 1.25), 64.0, "overcast"),
    ("05_low_underframe_detail.png", (6.8, -5.6, 0.82), (1.2, 0.0, 0.35), 58.0, "wet"),
    ("06_overcast_whole_asset.png", (-8.5, -8.3, 4.7), (-0.4, 0.0, 1.22), 54.0, "overcast"),
    ("07_night_harbor_whole_asset.png", (8.5, 8.1, 4.8), (0.4, 0.0, 1.22), 54.0, "night"),
    ("08_cockpit_worklight_whole_asset.png", (8.7, -8.1, 4.8), (0.5, 0.0, 1.22), 54.0, "cockpit"),
]
render_receipts = [render_view(*view) for view in views]
require(all(item["mean_luminance"] is None or item["mean_luminance"] >= 0.08 for item in render_receipts), "One or more final renders remain underexposed")

clear_review()
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
export_selected(FINAL_GLB)
glb = read_glb_json(FINAL_GLB)
node_names = {node.get("name") for node in glb.get("nodes", [])}
require({MESH_NAME, SOCKET_NAME, COLLISION_NAME}.issubset(node_names), f"GLB nodes missing: {sorted({MESH_NAME, SOCKET_NAME, COLLISION_NAME} - node_names)}")
glb_materials = {material.get("name") for material in glb.get("materials", [])}
require(MATERIAL_NAMES.issubset(glb_materials), f"GLB materials missing: {sorted(MATERIAL_NAMES - glb_materials)}")

report = {
    "schema": "skyguard.m02-harbor-container20ft.grok-mcp.production01.implementation.v1",
    "classification": "PASSED_AWAITING_DIRECT_VISUAL_REVIEW",
    "asset": "M02 generic non-branded 20-foot dry freight container",
    "identity_boundary": "Project-provisional generic envelope; no certification, manufacturer, operator, serial, payload, or nation claimed",
    "mesh": MESH_NAME,
    "socket": SOCKET_NAME,
    "collision": COLLISION_NAME,
    "dimensions_m": list(dimensions),
    "minimum_m": list(minimum),
    "maximum_m": list(maximum),
    "vertices": vertices,
    "polygons": polygons,
    "materials": sorted(slot_materials),
    "uv_layers": [layer.name for layer in mesh.data.uv_layers],
    "glb": {
        "nodes": sorted(name for name in node_names if name),
        "mesh_count": len(glb.get("meshes", [])),
        "material_count": len(glb.get("materials", [])),
    },
    "checkpoint_classification": review.get("classification"),
    "checkpoint_render_count": len(checkpoint_renders),
    "renders": render_receipts,
    "blend": str(FINAL_BLEND),
    "glb_path": str(FINAL_GLB),
    "limitations": [
        "Generic project-provisional identity",
        "Direct full-resolution visual review remains mandatory",
        "Unreal material replacement and D3D12 proof remain required",
        "No runtime proxy replacement or promotion is authorized",
    ],
}
write_json(OUTPUT / "grok_implementation_report.json", report)
write_json(RECEIPTS / "structure_dimensions_glb.json", report)
inventory = []
for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file() and item.name != "artifact_inventory.json"):
    inventory.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
write_json(RECEIPTS / "artifact_inventory.json", {"schema": "skyguard.artifact-inventory.v1", "artifacts": inventory})
print("PASSED_AWAITING_DIRECT_VISUAL_REVIEW")
