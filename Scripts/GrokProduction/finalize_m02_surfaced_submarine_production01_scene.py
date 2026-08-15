from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
OUTPUT = ROOT / r"Production\Attempts\m02-surfaced-submarine-grok-mcp-production01\attempt_20260811T1137000000000Z\output"
CHECKPOINT = OUTPUT / "checkpoint"
RENDERS = OUTPUT / "renders"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
FINAL_BLEND = OUTPUT / "M02_Harbor_SurfacedSubmarine_Production01.blend"
FINAL_GLB = EXPORTS / "M02_Harbor_SurfacedSubmarine_Production01.glb"

MESH_NAME = "SM_M02_Harbor_SurfacedSubmarine_A"
SOCKET_NAMES = {
    "SOCKET_Submarine_Waterline",
    "SOCKET_Submarine_Wake_Bow",
    "SOCKET_Submarine_Wake_Stern",
    "SOCKET_Submarine_Propeller",
}
COLLISION_NAMES = {
    "UCX_SM_M02_Harbor_SurfacedSubmarine_A_00",
    "UCX_SM_M02_Harbor_SurfacedSubmarine_A_01",
}
SOURCE_NAMES = {
    "SRC_Submarine_MainHull",
    "SRC_Submarine_BowSection",
    "SRC_Submarine_SternSection",
    "SRC_Submarine_DeckCasing",
    "SRC_Submarine_Sail",
    "SRC_Submarine_ControlSurfaces",
    "SRC_Submarine_Propulsor",
    "SRC_Submarine_DeckDetails",
}
MATERIAL_NAMES = {
    "M_M02_Submarine_HullCoating",
    "M_M02_Submarine_DeckCasing",
    "M_M02_Submarine_Sail",
    "M_M02_Submarine_Hardware",
    "M_M02_Submarine_Propulsor",
}
CHECK_KEYS = {
    "full_submarine_visible",
    "hull_is_hydrodynamic_not_capsule_or_block",
    "bow_and_stern_tapers_are_controlled",
    "sail_and_deck_casing_are_faired_and_connected",
    "control_surfaces_and_propulsor_are_connected",
    "waterline_reads_continuously",
    "mesh_is_centered_on_world_origin",
    "no_floating_or_clipped_parts",
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


def area(name, location, energy, size, color, target=(0.0, 0.0, 0.5)):
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


def review_surface(use_water):
    bpy.ops.mesh.primitive_plane_add(size=260.0, location=(0.0, 0.0, 0.0 if use_water else -4.9))
    obj = bpy.context.object
    obj.name = "REVIEW_Water" if use_water else "REVIEW_DryFloor"
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    ensure_collection("REVIEW_ONLY").objects.link(obj)
    name = "REVIEW_Water_Mat" if use_water else "REVIEW_DryFloor_Mat"
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.012, 0.055, 0.085, 1.0) if use_water else (0.055, 0.065, 0.075, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.05
    bsdf.inputs["Roughness"].default_value = 0.18 if use_water else 0.78
    obj.data.materials.append(material)


def stage(mode, use_water):
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
        background.inputs["Color"].default_value = (0.006, 0.012, 0.022, 1.0)
        background.inputs["Strength"].default_value = 0.10
        area("REVIEW_Moon", (-28.0, -34.0, 32.0), 1700.0, 24.0, (0.30, 0.48, 0.86))
        area("REVIEW_HarborRim", (30.0, 24.0, 16.0), 1200.0, 18.0, (1.0, 0.42, 0.16))
        scene.view_settings.exposure = 0.75
    elif mode == "overcast":
        background.inputs["Color"].default_value = (0.16, 0.21, 0.28, 1.0)
        background.inputs["Strength"].default_value = 0.52
        area("REVIEW_CloudKey", (-28.0, -38.0, 36.0), 2000.0, 30.0, (0.68, 0.80, 1.0))
        area("REVIEW_CloudFill", (30.0, 24.0, 18.0), 950.0, 24.0, (0.55, 0.66, 0.78))
        scene.view_settings.exposure = 0.20
    elif mode == "wet":
        background.inputs["Color"].default_value = (0.045, 0.065, 0.095, 1.0)
        background.inputs["Strength"].default_value = 0.30
        area("REVIEW_WetKey", (-30.0, -36.0, 30.0), 2050.0, 28.0, (0.45, 0.65, 1.0))
        area("REVIEW_WetRim", (32.0, 22.0, 16.0), 1150.0, 20.0, (1.0, 0.46, 0.22))
        scene.view_settings.exposure = 0.38
    else:
        background.inputs["Color"].default_value = (0.28, 0.43, 0.64, 1.0)
        background.inputs["Strength"].default_value = 0.48
        sun("REVIEW_Sun", (math.radians(32), math.radians(-18), math.radians(-38)), 2.2, (1.0, 0.80, 0.58))
        area("REVIEW_Sky", (36.0, -42.0, 38.0), 1550.0, 30.0, (0.50, 0.68, 1.0))
        area("REVIEW_Bounce", (-32.0, 24.0, 18.0), 800.0, 24.0, (1.0, 0.48, 0.24))
    review_surface(use_water)


def camera(location, target, lens):
    data = bpy.data.cameras.new("REVIEW_Camera_Data")
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.1
    data.clip_end = 1000.0
    obj = bpy.data.objects.new("REVIEW_Camera", data)
    ensure_collection("REVIEW_ONLY").objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj


def render_view(filename, location, target, lens, mode, use_water):
    stage(mode, use_water)
    scene = bpy.context.scene
    scene.camera = camera(location, target, lens)
    scene.render.filepath = str(RENDERS / filename)
    bpy.ops.render.render(write_still=True)
    return {"path": str(RENDERS / filename), "mode": mode, "water_surface": use_water}


def normalize(name, color, metallic, roughness):
    material = bpy.data.materials.get(name)
    require(material is not None, f"Missing material: {name}")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    require(bsdf is not None, f"Missing Principled BSDF: {name}")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness


def glb_summary(path):
    with path.open("rb") as stream:
        require(stream.read(4) == b"glTF", "Export is not GLB")
        version, _length = struct.unpack("<II", stream.read(8))
        require(version == 2, f"Unsupported GLB version: {version}")
        chunk_length, chunk_type = struct.unpack("<II", stream.read(8))
        require(chunk_type == 0x4E4F534A, "GLB JSON chunk missing")
        payload = json.loads(stream.read(chunk_length).decode("utf-8").rstrip("\x00 \t\r\n"))
    return {
        "nodes": [node.get("name") for node in payload.get("nodes", [])],
        "mesh_count": len(payload.get("meshes", [])),
        "material_count": len(payload.get("materials", [])),
    }


def export_selected(path):
    bpy.ops.object.select_all(action="DESELECT")
    names = {MESH_NAME} | SOCKET_NAMES | COLLISION_NAMES
    for name in names:
        obj = bpy.data.objects[name]
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = name != MESH_NAME
        obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[MESH_NAME]
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
require(CHECK_KEYS.issubset(checks), f"Checkpoint checks incomplete: {sorted(CHECK_KEYS - set(checks))}")
if review.get("classification") == "PASSED_CHECKPOINT_VISUAL_REVIEW":
    require(all(checks[key] is True for key in CHECK_KEYS), "Passed checkpoint contains false checks")
checkpoint_renders = sorted(CHECKPOINT.glob("*.png"))
require(len(checkpoint_renders) >= 6, f"Expected at least six checkpoint renders, found {len(checkpoint_renders)}")

for name in sorted({MESH_NAME} | SOCKET_NAMES | COLLISION_NAMES | SOURCE_NAMES):
    require(bpy.data.objects.get(name) is not None, f"Missing required object: {name}")
mesh = bpy.data.objects[MESH_NAME]
require(mesh.type == "MESH", "Governed submarine is not a mesh")
require(all(abs(value) <= 0.001 for value in mesh.location), f"Mesh is not at world origin: {tuple(mesh.location)}")
require(all(abs(value) <= 0.001 for value in mesh.rotation_euler), "Mesh rotation is not applied")
require(all(abs(value - 1.0) <= 0.001 for value in mesh.scale), "Mesh scale is not applied")
require(mesh.data.uv_layers.get("UVMap") is not None, "Governed mesh lacks UVMap")
vertices = len(mesh.data.vertices)
polygons = len(mesh.data.polygons)
require(vertices >= 8000, f"Vertex count too low: {vertices}")
require(6000 <= polygons <= 90000, f"Polygon count outside contract: {polygons}")

minimum, maximum = object_bounds(mesh)
dimensions = maximum - minimum
center = (minimum + maximum) * 0.5
require(68.0 <= dimensions.x <= 74.0, f"Length outside contract: {dimensions.x}")
require(6.8 <= dimensions.y <= 8.2, f"Beam outside contract: {dimensions.y}")
require(-4.8 <= minimum.z <= -3.4, f"Hull bottom outside contract: {minimum.z}")
require(7.0 <= maximum.z <= 9.0, f"Mast/sail maximum outside contract: {maximum.z}")
require(abs(center.x) <= 0.10 and abs(center.y) <= 0.10, f"Mesh is not centered in X/Y: {tuple(center)}")
require(minimum.z < 0.0 < maximum.z, "Mesh does not straddle the designed waterline")

for socket_name in SOCKET_NAMES:
    socket = bpy.data.objects[socket_name]
    require(socket.type == "EMPTY", f"Socket is not Empty: {socket_name}")
    socket.empty_display_type = "PLAIN_AXES"
waterline_socket = bpy.data.objects["SOCKET_Submarine_Waterline"]
require(waterline_socket.location.length <= 0.001, "Waterline socket is not at world origin")
bow_socket = bpy.data.objects["SOCKET_Submarine_Wake_Bow"]
stern_socket = bpy.data.objects["SOCKET_Submarine_Wake_Stern"]
prop_socket = bpy.data.objects["SOCKET_Submarine_Propeller"]
require(bow_socket.location.x >= maximum.x - 4.0 and abs(bow_socket.location.z) <= 0.5, "Bow wake socket is misplaced")
require(stern_socket.location.x <= minimum.x + 5.0 and abs(stern_socket.location.z) <= 0.5, "Stern wake socket is misplaced")
require(prop_socket.location.x <= minimum.x + 6.0 and prop_socket.location.z < 0.0, "Propeller socket is misplaced")

hull_min, hull_max = object_bounds(bpy.data.objects["SRC_Submarine_MainHull"])
sail_min, sail_max = object_bounds(bpy.data.objects["SRC_Submarine_Sail"])
control_min, control_max = object_bounds(bpy.data.objects["SRC_Submarine_ControlSurfaces"])
require(hull_max.x - hull_min.x >= 52.0, "Main hull is too short")
require(sail_min.z <= 2.6 and sail_max.z >= 5.8, "Sail is not faired into deck or tall enough")
require(control_min.x <= minimum.x + 10.0, "Stern control surfaces are not near the stern")

slot_materials = {slot.material.name for slot in mesh.material_slots if slot.material is not None}
require(MATERIAL_NAMES.issubset(slot_materials), f"Missing materials: {sorted(MATERIAL_NAMES - slot_materials)}")
normalize("M_M02_Submarine_HullCoating", (0.016, 0.026, 0.035), 0.55, 0.46)
normalize("M_M02_Submarine_DeckCasing", (0.028, 0.042, 0.052), 0.62, 0.54)
normalize("M_M02_Submarine_Sail", (0.020, 0.032, 0.042), 0.58, 0.48)
normalize("M_M02_Submarine_Hardware", (0.14, 0.17, 0.19), 0.88, 0.34)
normalize("M_M02_Submarine_Propulsor", (0.20, 0.15, 0.075), 0.92, 0.30)

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
    ("01_daylight_starboard_front_surfaced.png", (68.0, -78.0, 22.0), (0.0, 0.0, 1.2), 58.0, "daylight", True),
    ("02_daylight_port_rear_surfaced.png", (-72.0, 76.0, 21.0), (0.0, 0.0, 1.0), 58.0, "daylight", True),
    ("03_dry_elevated_planform.png", (0.0, -18.0, 92.0), (0.0, 0.0, 0.0), 58.0, "overcast", False),
    ("04_sail_deck_casing_detail.png", (12.0, -30.0, 14.0), (4.0, 0.0, 3.2), 68.0, "overcast", False),
    ("05_dry_stern_propulsor_detail.png", (-47.0, -23.0, 5.0), (-31.0, 0.0, -1.5), 66.0, "wet", False),
    ("06_overcast_waterline_profile.png", (0.0, -105.0, 9.0), (0.0, 0.0, 1.0), 62.0, "overcast", True),
    ("07_night_harbor_surfaced.png", (70.0, -82.0, 20.0), (0.0, 0.0, 1.2), 58.0, "night", True),
    ("08_wet_port_front_surfaced.png", (65.0, 82.0, 18.0), (0.0, 0.0, 1.0), 58.0, "wet", True),
]
render_receipts = [render_view(*view) for view in views]
clear_review()
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
export_selected(FINAL_GLB)
glb = glb_summary(FINAL_GLB)
for required_name in sorted({MESH_NAME} | SOCKET_NAMES | COLLISION_NAMES):
    require(required_name in glb["nodes"], f"GLB missing governed node: {required_name}")

report = {
    "schema": "skyguard.m02-surfaced-submarine.grok-mcp.production01.implementation.v1",
    "classification": "PASSED_AWAITING_DIRECT_VISUAL_REVIEW",
    "asset": "M02 fictional non-branded surfaced diesel-electric patrol submarine",
    "identity_boundary": "Project-provisional fictional conventional submarine; no real class or nation claimed",
    "mesh": MESH_NAME,
    "sockets": sorted(SOCKET_NAMES),
    "collisions": sorted(COLLISION_NAMES),
    "dimensions_m": list(dimensions),
    "minimum_m": list(minimum),
    "maximum_m": list(maximum),
    "center_m": list(center),
    "vertices": vertices,
    "polygons": polygons,
    "materials": sorted(slot_materials),
    "uv_layers": [layer.name for layer in mesh.data.uv_layers],
    "glb": glb,
    "checkpoint_classification": review.get("classification"),
    "checkpoint_render_count": len(checkpoint_renders),
    "renders": render_receipts,
    "blend": str(FINAL_BLEND),
    "glb_path": str(FINAL_GLB),
    "limitations": [
        "Fictional project-provisional identity",
        "Direct full-resolution visual review remains mandatory",
        "Unreal water, wake, material replacement and D3D12 proof remain required",
        "No runtime proxy replacement or promotion is authorized",
    ],
}
write_json(OUTPUT / "grok_implementation_report.json", report)
write_json(RECEIPTS / "structure_dimensions_waterline.json", report)
inventory = []
for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file() and item.name != "artifact_inventory.json"):
    inventory.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
write_json(RECEIPTS / "artifact_inventory.json", {"schema": "skyguard.artifact-inventory.v1", "artifacts": inventory})
print("PASSED_AWAITING_DIRECT_VISUAL_REVIEW")
