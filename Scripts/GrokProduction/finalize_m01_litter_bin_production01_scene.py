from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
OUTPUT = ROOT / r"Production\Attempts\m01-litter-bin-grok-mcp-production01\attempt_20260811T113000000000Z\output"
CHECKPOINT = OUTPUT / "checkpoint"
RENDERS = OUTPUT / "renders"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
FINAL_BLEND = OUTPUT / "M01_Promenade_LitterBin_Production01.blend"
FINAL_GLB = EXPORTS / "M01_Promenade_LitterBin_Production01.glb"

MESH_NAME = "SM_M01_Promenade_LitterBin_A"
SOCKET_NAME = "SOCKET_LitterBin_Origin"
COLLISION_NAME = "UCX_SM_M01_Promenade_LitterBin_A_00"
SOURCE_NAMES = {
    "SRC_LitterBin_Body",
    "SRC_LitterBin_Hood",
    "SRC_LitterBin_Aperture",
    "SRC_LitterBin_ServiceDoor",
    "SRC_LitterBin_Base",
}
MATERIAL_NAMES = {
    "M_M01_LitterBin_PowderCoat",
    "M_M01_LitterBin_DarkAperture",
    "M_M01_LitterBin_StainlessTrim",
}
CHECK_KEYS = {
    "complete_bin_visible",
    "waste_aperture_unmistakable",
    "aperture_recess_depth_visible",
    "service_door_not_on_front",
    "base_grounded",
    "no_floating_parts",
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


def area(name, location, energy, size, color, target=(0.0, 0.0, 0.55)):
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
    data.angle = math.radians(4.0)
    data.color = color
    obj = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(obj)
    obj.rotation_euler = rotation


def ground():
    bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, -0.008))
    obj = bpy.context.object
    obj.name = "REVIEW_Ground"
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    ensure_collection("REVIEW_ONLY").objects.link(obj)
    material = bpy.data.materials.get("REVIEW_Ground_Mat") or bpy.data.materials.new("REVIEW_Ground_Mat")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.055, 0.065, 0.075, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.76
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
    scene.view_settings.exposure = 0.0
    if mode == "night":
        background.inputs["Color"].default_value = (0.008, 0.014, 0.026, 1.0)
        background.inputs["Strength"].default_value = 0.11
        area("REVIEW_Moon", (-2.5, -3.5, 4.5), 900.0, 3.0, (0.30, 0.48, 0.86))
        area("REVIEW_WarmRim", (2.0, 2.0, 2.5), 520.0, 2.0, (1.0, 0.46, 0.20))
        scene.view_settings.exposure = 0.75
    elif mode == "wet":
        background.inputs["Color"].default_value = (0.06, 0.08, 0.11, 1.0)
        background.inputs["Strength"].default_value = 0.32
        area("REVIEW_WetKey", (-2.2, -3.2, 4.0), 1150.0, 3.2, (0.48, 0.68, 1.0))
        area("REVIEW_WetRim", (2.4, 1.8, 2.3), 700.0, 2.2, (1.0, 0.48, 0.24))
        scene.view_settings.exposure = 0.35
    elif mode == "overcast":
        background.inputs["Color"].default_value = (0.19, 0.24, 0.31, 1.0)
        background.inputs["Strength"].default_value = 0.56
        area("REVIEW_CloudKey", (-2.6, -3.2, 4.5), 1150.0, 4.0, (0.72, 0.84, 1.0))
        area("REVIEW_CloudFill", (2.5, 2.0, 2.8), 540.0, 3.0, (0.58, 0.67, 0.78))
        scene.view_settings.exposure = 0.15
    elif mode == "cockpit":
        background.inputs["Color"].default_value = (0.014, 0.019, 0.026, 1.0)
        background.inputs["Strength"].default_value = 0.15
        area("REVIEW_Worklight", (1.8, -2.4, 2.6), 980.0, 2.5, (0.48, 0.72, 1.0))
        area("REVIEW_Amber", (-1.8, 1.6, 1.8), 580.0, 1.8, (1.0, 0.42, 0.16))
        scene.view_settings.exposure = 0.55
    else:
        background.inputs["Color"].default_value = (0.30, 0.45, 0.66, 1.0)
        background.inputs["Strength"].default_value = 0.48
        sun("REVIEW_Sun", (math.radians(28), math.radians(-18), math.radians(-32)), 2.0, (1.0, 0.80, 0.58))
        area("REVIEW_Sky", (2.8, -3.6, 4.6), 850.0, 3.6, (0.50, 0.68, 1.0))
        area("REVIEW_Bounce", (-2.5, 2.0, 2.0), 390.0, 2.5, (1.0, 0.48, 0.24))
    ground()


def camera(location, target, lens):
    data = bpy.data.cameras.new("REVIEW_Camera_Data")
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.03
    data.clip_end = 100.0
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
    if mean is not None and mean < 0.045:
        scene.view_settings.exposure += 1.0
        bpy.ops.render.render(write_still=True)
        mean = luminance()
    elif mean is not None and mean > 0.72:
        scene.view_settings.exposure -= 0.8
        bpy.ops.render.render(write_still=True)
        mean = luminance()
    return {"path": str(RENDERS / filename), "mode": mode, "mean_luminance": mean}


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
require(len(checkpoint_renders) >= 4, f"Expected at least four checkpoint renders, found {len(checkpoint_renders)}")

for name in sorted({MESH_NAME, SOCKET_NAME, COLLISION_NAME} | SOURCE_NAMES):
    require(bpy.data.objects.get(name) is not None, f"Missing required object: {name}")
mesh = bpy.data.objects[MESH_NAME]
socket = bpy.data.objects[SOCKET_NAME]
collision = bpy.data.objects[COLLISION_NAME]
aperture = bpy.data.objects["SRC_LitterBin_Aperture"]
service_door = bpy.data.objects["SRC_LitterBin_ServiceDoor"]
require(mesh.type == "MESH" and collision.type == "MESH" and socket.type == "EMPTY", "Governed object type mismatch")
require(all(abs(value) <= 0.001 for value in mesh.location), f"Mesh is not at origin: {tuple(mesh.location)}")
require(all(abs(value) <= 0.001 for value in mesh.rotation_euler), "Mesh rotation is not applied")
require(all(abs(value - 1.0) <= 0.001 for value in mesh.scale), "Mesh scale is not applied")
require(all(abs(value) <= 0.001 for value in socket.location), "Socket is not at world origin")
socket.empty_display_type = "PLAIN_AXES"
require(mesh.data.uv_layers.get("UVMap") is not None, "Governed mesh lacks UVMap")
vertices = len(mesh.data.vertices)
polygons = len(mesh.data.polygons)
require(vertices >= 700, f"Vertex count too low: {vertices}")
require(polygons >= 550, f"Polygon count too low: {polygons}")

minimum, maximum = object_bounds(mesh)
dimensions = maximum - minimum
require(0.48 <= dimensions.x <= 0.62, f"Width outside contract: {dimensions.x}")
require(0.42 <= dimensions.y <= 0.55, f"Depth outside contract: {dimensions.y}")
require(0.90 <= dimensions.z <= 1.10, f"Height outside contract: {dimensions.z}")
require(-0.025 <= minimum.z <= 0.025, f"Bottom is not grounded: {minimum.z}")

ap_min, ap_max = object_bounds(aperture)
ap_dims = ap_max - ap_min
require(0.28 <= ap_dims.x <= 0.40, f"Aperture width outside contract: {ap_dims.x}")
require(ap_dims.y >= 0.045, f"Aperture recess depth too shallow: {ap_dims.y}")
require(0.14 <= ap_dims.z <= 0.24, f"Aperture height outside contract: {ap_dims.z}")
ap_center = (ap_min + ap_max) * 0.5
door_min, door_max = object_bounds(service_door)
door_center = (door_min + door_max) * 0.5
require(ap_center.y < 0.0, "Aperture is not on the governed -Y front")
require(door_center.y > 0.0, "Service door is not on the governed +Y rear")

slot_materials = {slot.material.name for slot in mesh.material_slots if slot.material is not None}
require(MATERIAL_NAMES.issubset(slot_materials), f"Missing materials: {sorted(MATERIAL_NAMES - slot_materials)}")
normalize("M_M01_LitterBin_PowderCoat", (0.055, 0.075, 0.090), 0.70, 0.50)
normalize("M_M01_LitterBin_DarkAperture", (0.004, 0.006, 0.008), 0.10, 0.82)
normalize("M_M01_LitterBin_StainlessTrim", (0.34, 0.38, 0.42), 0.90, 0.30)

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
    ("01_daylight_front_three_quarter.png", (1.65, -2.35, 1.35), (0.0, 0.0, 0.53), 58.0, "daylight"),
    ("02_daylight_opposite_three_quarter.png", (-1.65, 2.35, 1.30), (0.0, 0.0, 0.52), 58.0, "daylight"),
    ("03_front_aperture_detail.png", (0.0, -1.55, 0.90), (0.0, -0.18, 0.72), 68.0, "overcast"),
    ("04_rear_service_detail.png", (0.90, 1.55, 0.90), (0.0, 0.18, 0.52), 62.0, "overcast"),
    ("05_grounded_base_detail.png", (1.15, -1.45, 0.55), (0.0, 0.0, 0.20), 62.0, "wet"),
    ("06_overcast_whole_asset.png", (-1.75, -2.45, 1.40), (0.0, 0.0, 0.53), 56.0, "overcast"),
    ("07_night_whole_asset.png", (1.75, -2.45, 1.40), (0.0, 0.0, 0.53), 56.0, "night"),
    ("08_cockpit_worklight_whole_asset.png", (-1.65, -2.35, 1.32), (0.0, 0.0, 0.52), 56.0, "cockpit"),
]
render_receipts = [render_view(*view) for view in views]
clear_review()
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
export_selected(FINAL_GLB)

report = {
    "schema": "skyguard.m01-litter-bin.grok-mcp.production01.implementation.v1",
    "classification": "PASSED_AWAITING_DIRECT_VISUAL_REVIEW",
    "asset": "M01 generic non-branded coastal promenade litter bin",
    "mesh": MESH_NAME,
    "socket": SOCKET_NAME,
    "collision": COLLISION_NAME,
    "dimensions_m": list(dimensions),
    "minimum_m": list(minimum),
    "maximum_m": list(maximum),
    "aperture_dimensions_m": list(ap_dims),
    "aperture_center_m": list(ap_center),
    "service_door_center_m": list(door_center),
    "vertices": vertices,
    "polygons": polygons,
    "materials": sorted(slot_materials),
    "uv_layers": [layer.name for layer in mesh.data.uv_layers],
    "checkpoint_classification": review.get("classification"),
    "checkpoint_render_count": len(checkpoint_renders),
    "renders": render_receipts,
    "blend": str(FINAL_BLEND),
    "glb": str(FINAL_GLB),
    "limitations": [
        "Generic project-provisional identity",
        "Direct visual review remains mandatory",
        "Unreal material replacement and D3D12 proof remain required",
        "No runtime promotion is authorized",
    ],
}
write_json(OUTPUT / "grok_implementation_report.json", report)
write_json(RECEIPTS / "structure_and_dimensions.json", report)
inventory = []
for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file() and item.name != "artifact_inventory.json"):
    inventory.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
write_json(RECEIPTS / "artifact_inventory.json", {"schema": "skyguard.artifact-inventory.v1", "artifacts": inventory})
print("PASSED_AWAITING_DIRECT_VISUAL_REVIEW")
