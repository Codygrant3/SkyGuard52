from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
OUTPUT = ROOT / r"Production\Attempts\m02-quay-escape-ladder-grok-mcp-production01\attempt_20260812T1215000000000Z\output"
CHECKPOINT = OUTPUT / "checkpoint"
RENDERS = OUTPUT / "renders"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
FINAL_BLEND = OUTPUT / "M02_Quay_EscapeLadder_Production01.blend"
FINAL_GLB = EXPORTS / "M02_Quay_EscapeLadder_Production01.glb"

MESH_NAME = "SM_M02_Quay_EscapeLadder_A"
SOCKET_NAME = "SOCKET_QuayLadder_Origin"
COLLISION_NAME = "UCX_SM_M02_Quay_EscapeLadder_A_00"
SOURCE_NAMES = {
    "SRC_QuayLadder_Rails",
    "SRC_QuayLadder_Rungs",
    "SRC_QuayLadder_Mounts",
    "SRC_QuayLadder_Fasteners",
}
MATERIAL_NAMES = {
    "M_M02_QuayLadder_GalvanizedSteel",
    "M_M02_QuayLadder_WornExposedMetal",
}
CHECK_KEYS = {
    "complete_ladder_visible",
    "rails_continuous_and_parallel",
    "rungs_even_and_connected",
    "mounts_and_wall_clearance_readable",
    "fasteners_grounded",
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
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    points = [evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box]
    minimum = Vector(tuple(min(point[index] for point in points) for index in range(3)))
    maximum = Vector(tuple(max(point[index] for point in points) for index in range(3)))
    return minimum, maximum


def apply_object_transforms(obj):
    if obj is None:
        return
    bpy.ops.object.select_all(action="DESELECT")
    obj.hide_set(False)
    obj.hide_viewport = False
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


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


def area(name, location, energy, size, color, target=(0.0, 0.0, 0.45)):
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


def glb_nodes(path):
    with path.open("rb") as stream:
        magic, version, total_length = struct.unpack("<4sII", stream.read(12))
        require(magic == b"glTF", f"Invalid GLB magic: {magic!r}")
        require(version == 2, f"Unsupported GLB version: {version}")
        chunk_length, chunk_type = struct.unpack("<II", stream.read(8))
        require(chunk_type == 0x4E4F534A, "GLB JSON chunk missing")
        payload = json.loads(stream.read(chunk_length).decode("utf-8").rstrip("\x00 \t\r\n"))
    return [node.get("name") for node in payload.get("nodes", [])], len(payload.get("meshes", [])), len(payload.get("materials", []))


def export_selected(path):
    bpy.ops.object.select_all(action="DESELECT")
    for name in (MESH_NAME, SOCKET_NAME, COLLISION_NAME):
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
require(CHECK_KEYS.issubset(checks), f"Checkpoint checks are incomplete: {sorted(CHECK_KEYS - set(checks))}")
if review.get("classification") == "PASSED_CHECKPOINT_VISUAL_REVIEW":
    require(all(checks[key] is True for key in CHECK_KEYS), "A passed checkpoint contains false checks")
checkpoint_renders = sorted(CHECKPOINT.glob("*.png"))
require(len(checkpoint_renders) >= 4, f"Expected at least four checkpoint renders, found {len(checkpoint_renders)}")

for name in sorted({MESH_NAME, SOCKET_NAME, COLLISION_NAME} | SOURCE_NAMES):
    require(bpy.data.objects.get(name) is not None, f"Missing required object: {name}")
for name in sorted({MESH_NAME, COLLISION_NAME} | SOURCE_NAMES):
    apply_object_transforms(bpy.data.objects[name])
mesh = bpy.data.objects[MESH_NAME]
socket = bpy.data.objects[SOCKET_NAME]
collision = bpy.data.objects[COLLISION_NAME]
rails = bpy.data.objects["SRC_QuayLadder_Rails"]
rungs = bpy.data.objects["SRC_QuayLadder_Rungs"]
mounts = bpy.data.objects["SRC_QuayLadder_Mounts"]
fasteners = bpy.data.objects["SRC_QuayLadder_Fasteners"]
require(mesh.type == "MESH" and collision.type == "MESH" and socket.type == "EMPTY", "Governed object type mismatch")
require(all(abs(value) <= 0.001 for value in mesh.location), f"Mesh is not at origin: {tuple(mesh.location)}")
require(all(abs(value) <= 0.001 for value in mesh.rotation_euler), "Mesh rotation is not applied")
require(all(abs(value - 1.0) <= 0.001 for value in mesh.scale), "Mesh scale is not applied")
require(all(abs(value) <= 0.001 for value in socket.location), "Socket is not at world origin")
socket.empty_display_type = "PLAIN_AXES"
require(mesh.data.uv_layers.get("UVMap") is not None, "Governed mesh lacks UVMap")
vertices = len(mesh.data.vertices)
polygons = len(mesh.data.polygons)
require(vertices >= 2400, f"Vertex count too low: {vertices}")
require(polygons >= 1800, f"Polygon count too low: {polygons}")

minimum, maximum = object_bounds(mesh)
dimensions = maximum - minimum
require(0.48 <= dimensions.x <= 0.62, f"Width outside contract: {dimensions.x}")
require(0.20 <= dimensions.y <= 0.34, f"Projection outside contract: {dimensions.y}")
require(2.80 <= dimensions.z <= 3.20, f"Height outside contract: {dimensions.z}")
require(-0.025 <= minimum.z <= 0.025, f"Bottom is not grounded: {minimum.z}")
require(abs((minimum.x + maximum.x) * 0.5) <= 0.040, "Asset is not centered on X")
rails_min, rails_max = object_bounds(rails)
rungs_min, rungs_max = object_bounds(rungs)
mounts_min, mounts_max = object_bounds(mounts)
fast_min, fast_max = object_bounds(fasteners)
require(rails_max.z - rails_min.z >= 2.70, "Rails do not span the governed height")
require(0.45 <= rails_max.x - rails_min.x <= 0.62, "Rail spacing is outside contract")
require(rungs_max.z - rungs_min.z >= 2.20, "Rungs do not cover the climbable height")
require(rungs_max.x - rungs_min.x >= 0.36, "Clear rung width is too narrow")
require(mounts_max.y - mounts_min.y >= 0.12, "Mounts do not demonstrate wall stand-off")
require(mounts_max.z - mounts_min.z >= 1.80, "Mount pairs do not span enough of the ladder")
require(fast_max.y >= mounts_max.y - 0.08, "Fasteners do not reach the wall-side anchor plates")
require(fast_max.z - fast_min.z >= 1.80, "Fasteners do not cover multiple mount elevations")

slot_materials = {slot.material.name for slot in mesh.material_slots if slot.material is not None}
require(MATERIAL_NAMES.issubset(slot_materials), f"Missing materials: {sorted(MATERIAL_NAMES - slot_materials)}")
normalize("M_M02_QuayLadder_GalvanizedSteel", (0.31, 0.34, 0.36), 0.84, 0.34)
normalize("M_M02_QuayLadder_WornExposedMetal", (0.16, 0.18, 0.20), 0.92, 0.25)

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
    ("01_daylight_front_three_quarter.png", (2.45, -3.10, 1.65), (0.0, 0.08, 1.48), 62.0, "daylight"),
    ("02_daylight_wall_side_three_quarter.png", (-2.20, 2.85, 1.55), (0.0, 0.08, 1.45), 60.0, "daylight"),
    ("03_rung_weld_and_mount_detail.png", (1.25, -1.45, 1.30), (0.0, 0.05, 1.30), 72.0, "overcast"),
    ("04_elevated_top_returns.png", (0.0, -2.35, 3.30), (0.0, 0.05, 2.55), 62.0, "overcast"),
    ("05_anchor_plate_fastener_detail.png", (1.30, 1.35, 0.92), (0.0, 0.15, 0.92), 72.0, "wet"),
    ("06_overcast_whole_asset.png", (-2.40, -3.10, 1.60), (0.0, 0.08, 1.48), 60.0, "overcast"),
    ("07_night_whole_asset.png", (2.40, -3.10, 1.62), (0.0, 0.08, 1.48), 60.0, "night"),
    ("08_cockpit_worklight_whole_asset.png", (-2.25, -2.95, 1.56), (0.0, 0.08, 1.48), 60.0, "cockpit"),
]
render_receipts = [render_view(*view) for view in views]
clear_review()
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
export_selected(FINAL_GLB)
node_names, glb_mesh_count, glb_material_count = glb_nodes(FINAL_GLB)
for required_name in (MESH_NAME, SOCKET_NAME, COLLISION_NAME):
    require(required_name in node_names, f"GLB missing governed node: {required_name}")

report = {
    "schema": "skyguard.m02-quay-escape-ladder.grok-mcp.production01.implementation.v1",
    "classification": "PASSED_AWAITING_DIRECT_VISUAL_REVIEW",
    "asset": "M02 generic non-branded galvanized quay escape ladder",
    "identity_boundary": "Project-provisional marine safety fitting; no manufacturer, load rating, port authority, country, certification or regulatory compliance claimed",
    "mesh": MESH_NAME,
    "socket": SOCKET_NAME,
    "collision": COLLISION_NAME,
    "dimensions_m": list(dimensions),
    "minimum_m": list(minimum),
    "maximum_m": list(maximum),
    "rail_span_m": rails_max.x - rails_min.x,
    "rung_span_m": rungs_max.x - rungs_min.x,
    "mount_standoff_m": mounts_max.y - mounts_min.y,
    "vertices": vertices,
    "polygons": polygons,
    "materials": sorted(slot_materials),
    "uv_layers": [layer.name for layer in mesh.data.uv_layers],
    "glb_nodes": node_names,
    "glb_mesh_count": glb_mesh_count,
    "glb_material_count": glb_material_count,
    "checkpoint_classification": review.get("classification"),
    "checkpoint_render_count": len(checkpoint_renders),
    "renders": render_receipts,
    "blend": str(FINAL_BLEND),
    "glb": str(FINAL_GLB),
    "limitations": [
        "Generic project-provisional identity",
        "Direct full-resolution visual review remains mandatory",
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
