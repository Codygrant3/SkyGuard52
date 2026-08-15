from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
OUTPUT = ROOT / r"Production\Attempts\m01-streetlight-grok-mcp-production01\attempt_20260811T111500000000Z\output"
CHECKPOINT = OUTPUT / "checkpoint"
RENDERS = OUTPUT / "renders"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
FINAL_BLEND = OUTPUT / "M01_Promenade_Streetlight_Production01.blend"
FINAL_GLB = EXPORTS / "M01_Promenade_Streetlight_Production01.glb"

MESH_NAME = "SM_M01_Promenade_Streetlight_A"
SOCKET_NAME = "SOCKET_Streetlight_Origin"
COLLISION_NAME = "UCX_SM_M01_Promenade_Streetlight_A_00"
SOURCE_NAMES = {
    "SRC_Streetlight_Base",
    "SRC_Streetlight_Pole",
    "SRC_Streetlight_Arm",
    "SRC_Streetlight_Luminaire",
    "SRC_Streetlight_Lens",
    "SRC_Streetlight_AccessDoor",
}
MATERIAL_NAMES = {
    "M_M01_Streetlight_PaintedSteel",
    "M_M01_Streetlight_DarkHardware",
    "M_M01_Streetlight_LED_Lens",
}
CHECK_KEYS = {
    "full_pole_visible",
    "full_arm_visible",
    "full_luminaire_visible",
    "arm_connected_at_both_ends",
    "base_grounded",
    "access_door_readable",
    "lens_readable_without_clipping",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


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
    minimum = Vector(tuple(min(point[index] for point in points) for index in range(3)))
    maximum = Vector(tuple(max(point[index] for point in points) for index in range(3)))
    return minimum, maximum


def look_at(obj, target) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def make_camera(location, target, lens):
    data = bpy.data.cameras.new("REVIEW_Camera_Data")
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.04
    data.clip_end = 5000.0
    camera = bpy.data.objects.new("REVIEW_Camera", data)
    ensure_collection("REVIEW_ONLY").objects.link(camera)
    camera.location = location
    look_at(camera, target)
    return camera


def make_area(name, location, energy, size, color, target=(0.0, 0.0, 3.5)):
    data = bpy.data.lights.new(name + "_Data", "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    light = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(light)
    light.location = location
    look_at(light, target)
    return light


def make_sun(name, rotation, energy, color):
    data = bpy.data.lights.new(name + "_Data", "SUN")
    data.energy = energy
    data.angle = math.radians(3.0)
    data.color = color
    light = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(light)
    light.rotation_euler = rotation
    return light


def create_ground() -> None:
    bpy.ops.mesh.primitive_plane_add(size=80.0, location=(0.0, 0.0, -0.012))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    for collection in list(ground.users_collection):
        collection.objects.unlink(ground)
    ensure_collection("REVIEW_ONLY").objects.link(ground)
    material = bpy.data.materials.get("REVIEW_Ground_Mat") or bpy.data.materials.new("REVIEW_Ground_Mat")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.045, 0.055, 0.065, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.78
    ground.data.materials.clear()
    ground.data.materials.append(material)


def configure_stage(mode: str) -> None:
    review = ensure_collection("REVIEW_ONLY")
    clear_collection(review)
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    scene = bpy.context.scene
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.0
    if mode == "night":
        background.inputs["Color"].default_value = (0.006, 0.011, 0.022, 1.0)
        background.inputs["Strength"].default_value = 0.12
        make_area("REVIEW_Moon", (-6.0, -8.0, 12.0), 1250.0, 9.0, (0.30, 0.48, 0.85))
        make_area("REVIEW_Warm", (4.0, -4.0, 7.0), 600.0, 5.0, (1.0, 0.48, 0.22))
        scene.view_settings.exposure = 0.75
    elif mode == "overcast":
        background.inputs["Color"].default_value = (0.18, 0.23, 0.30, 1.0)
        background.inputs["Strength"].default_value = 0.58
        make_area("REVIEW_CloudKey", (-5.0, -7.0, 12.0), 1700.0, 11.0, (0.72, 0.84, 1.0))
        make_area("REVIEW_CloudFill", (7.0, 4.0, 8.0), 800.0, 8.0, (0.56, 0.66, 0.78))
        scene.view_settings.exposure = 0.20
    elif mode == "wet":
        background.inputs["Color"].default_value = (0.055, 0.075, 0.105, 1.0)
        background.inputs["Strength"].default_value = 0.34
        make_area("REVIEW_WetKey", (-4.0, -7.0, 10.0), 1850.0, 7.0, (0.48, 0.68, 1.0))
        make_area("REVIEW_WetRim", (6.0, 3.0, 7.0), 1200.0, 5.0, (1.0, 0.48, 0.25))
        scene.view_settings.exposure = 0.35
    elif mode == "cockpit":
        background.inputs["Color"].default_value = (0.015, 0.020, 0.026, 1.0)
        background.inputs["Strength"].default_value = 0.15
        make_area("REVIEW_CockpitWorklight", (2.0, -4.0, 6.0), 1550.0, 4.0, (0.48, 0.72, 1.0))
        make_area("REVIEW_AmberRim", (-3.0, 2.0, 4.0), 900.0, 3.0, (1.0, 0.42, 0.16))
        scene.view_settings.exposure = 0.55
    else:
        background.inputs["Color"].default_value = (0.30, 0.45, 0.66, 1.0)
        background.inputs["Strength"].default_value = 0.48
        make_sun("REVIEW_Sun", (math.radians(28), math.radians(-20), math.radians(-34)), 2.1, (1.0, 0.80, 0.58))
        make_area("REVIEW_SkyFill", (5.0, -8.0, 12.0), 1100.0, 8.0, (0.50, 0.68, 1.0))
        make_area("REVIEW_Bounce", (-5.0, 3.0, 4.0), 520.0, 5.0, (1.0, 0.48, 0.24))
    create_ground()


def sampled_luminance():
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
    configure_stage(mode)
    camera = make_camera(location, target, lens)
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.filepath = str(RENDERS / filename)
    bpy.ops.render.render(write_still=True)
    luminance = sampled_luminance()
    if luminance is not None and luminance < 0.045:
        scene.view_settings.exposure += 1.0
        bpy.ops.render.render(write_still=True)
        luminance = sampled_luminance()
    elif luminance is not None and luminance > 0.72:
        scene.view_settings.exposure -= 0.8
        bpy.ops.render.render(write_still=True)
        luminance = sampled_luminance()
    return {"path": str(RENDERS / filename), "mode": mode, "mean_luminance": luminance}


def normalize_material(name, base_color, metallic, roughness, emission=None):
    material = bpy.data.materials.get(name)
    require(material is not None, f"Missing material: {name}")
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    require(bsdf is not None, f"Missing Principled BSDF: {name}")
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission is not None:
        emission_socket = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if emission_socket is not None:
            emission_socket.default_value = (*emission[0], 1.0)
        strength_socket = bsdf.inputs.get("Emission Strength")
        if strength_socket is not None:
            strength_socket.default_value = emission[1]


def selected_export(path: Path, names: list[str]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for name in names:
        bpy.data.objects[name].select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_extras=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
    )


for directory in (OUTPUT, CHECKPOINT, RENDERS, EXPORTS, RECEIPTS):
    directory.mkdir(parents=True, exist_ok=True)

review_path = CHECKPOINT / "checkpoint_visual_review.json"
require(review_path.is_file(), "Missing Grok checkpoint visual review")
review = json.loads(review_path.read_text(encoding="utf-8"))
require(review.get("classification") == "PASSED_CHECKPOINT_VISUAL_REVIEW", "Grok checkpoint review did not pass")
checks = review.get("checks")
require(isinstance(checks, dict), "Checkpoint review is missing checks object")
for key in sorted(CHECK_KEYS):
    require(checks.get(key) is True, f"Checkpoint review check did not pass: {key}")
checkpoint_renders = sorted(path for path in CHECKPOINT.glob("*.png") if path.is_file())
require(len(checkpoint_renders) >= 4, f"Expected at least four checkpoint renders, found {len(checkpoint_renders)}")

required_objects = {MESH_NAME, SOCKET_NAME, COLLISION_NAME} | SOURCE_NAMES
for name in sorted(required_objects):
    require(bpy.data.objects.get(name) is not None, f"Missing required object: {name}")

mesh = bpy.data.objects[MESH_NAME]
socket = bpy.data.objects[SOCKET_NAME]
collision = bpy.data.objects[COLLISION_NAME]
require(mesh.type == "MESH", "Governed streetlight is not a mesh")
require(socket.type == "EMPTY", "Streetlight socket is not an Empty")
require(collision.type == "MESH", "Streetlight collision is not a mesh")
require(all(abs(value) <= 0.001 for value in mesh.location), f"Streetlight location is not at origin: {tuple(mesh.location)}")
require(all(abs(value) <= 0.001 for value in mesh.rotation_euler), f"Streetlight rotation is not applied: {tuple(mesh.rotation_euler)}")
require(all(abs(value - 1.0) <= 0.001 for value in mesh.scale), f"Streetlight scale is not applied: {tuple(mesh.scale)}")
require(all(abs(value) <= 0.001 for value in socket.location), f"Socket is not at world origin: {tuple(socket.location)}")
socket.empty_display_type = "PLAIN_AXES"
require(mesh.data.uv_layers.get("UVMap") is not None, "Governed mesh lacks UVMap")
vertex_count = len(mesh.data.vertices)
polygon_count = len(mesh.data.polygons)
require(vertex_count >= 600, f"Streetlight vertex count is too low: {vertex_count}")
require(polygon_count >= 500, f"Streetlight polygon count is too low: {polygon_count}")

minimum, maximum = bounds(mesh)
dimensions = maximum - minimum
require(7.4 <= dimensions.z <= 7.9, f"Streetlight height is outside contract: {dimensions.z}")
require(-0.03 <= minimum.z <= 0.03, f"Streetlight bottom is not grounded: {minimum.z}")
require(max(abs(minimum.x), abs(maximum.x), abs(minimum.y), abs(maximum.y)) <= 1.85, "Streetlight exceeds horizontal contract")
slot_materials = {slot.material.name for slot in mesh.material_slots if slot.material is not None}
require(MATERIAL_NAMES.issubset(slot_materials), f"Missing governed materials: {sorted(MATERIAL_NAMES - slot_materials)}")

normalize_material("M_M01_Streetlight_PaintedSteel", (0.035, 0.045, 0.055), 0.78, 0.50)
normalize_material("M_M01_Streetlight_DarkHardware", (0.012, 0.016, 0.020), 0.88, 0.38)
normalize_material("M_M01_Streetlight_LED_Lens", (0.70, 0.76, 0.78), 0.05, 0.28, ((0.82, 0.88, 1.0), 0.75))

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
    ("01_daylight_front_three_quarter.png", (13.0, -19.0, 8.5), (0.45, 0.0, 3.90), 48.0, "daylight"),
    ("02_daylight_opposite_three_quarter.png", (-13.0, 19.0, 8.2), (0.45, 0.0, 3.85), 48.0, "daylight"),
    ("03_daylight_side_profile.png", (-18.0, 0.0, 7.7), (0.45, 0.0, 3.85), 40.0, "daylight"),
    ("04_upper_assembly_detail.png", (5.2, -7.2, 8.5), (0.80, 0.0, 7.28), 56.0, "overcast"),
    ("05_grounded_base_detail.png", (2.8, -3.8, 1.55), (0.0, 0.0, 0.62), 52.0, "wet"),
    ("06_overcast_whole_asset.png", (12.0, -20.0, 8.0), (0.45, 0.0, 3.85), 46.0, "overcast"),
    ("07_night_whole_asset.png", (-12.0, -20.0, 8.0), (0.45, 0.0, 3.85), 46.0, "night"),
    ("08_cockpit_worklight_whole_asset.png", (14.0, -19.0, 9.0), (0.45, 0.0, 3.90), 46.0, "cockpit"),
]
render_receipts = [render_view(*view) for view in views]

review_collection = bpy.data.collections.get("REVIEW_ONLY")
if review_collection is not None:
    clear_collection(review_collection)

bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))
selected_export(FINAL_GLB, [MESH_NAME, SOCKET_NAME, COLLISION_NAME])

report = {
    "schema": "skyguard.m01-streetlight.grok-mcp.production01.implementation.v1",
    "classification": "PASSED_AWAITING_DIRECT_VISUAL_REVIEW",
    "asset": "M01 promenade streetlight, generic non-branded mid-distance candidate",
    "mesh": MESH_NAME,
    "socket": SOCKET_NAME,
    "collision": COLLISION_NAME,
    "dimensions_m": [dimensions.x, dimensions.y, dimensions.z],
    "minimum_m": list(minimum),
    "maximum_m": list(maximum),
    "vertices": vertex_count,
    "polygons": polygon_count,
    "materials": sorted(slot_materials),
    "uv_layers": [layer.name for layer in mesh.data.uv_layers],
    "checkpoint_review": str(review_path),
    "checkpoint_render_count": len(checkpoint_renders),
    "renders": render_receipts,
    "blend": str(FINAL_BLEND),
    "glb": str(FINAL_GLB),
    "limitations": [
        "Generic project-provisional streetlight identity",
        "Accepted scope, if visually approved, is repeated mid-distance environment use",
        "Unreal material replacement and D3D12 visual proof remain required",
        "No runtime promotion is authorized by this Blender report",
    ],
}
write_json(OUTPUT / "grok_implementation_report.json", report)
write_json(RECEIPTS / "structure_and_dimensions.json", report)

inventory = []
for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file() and item.name != "artifact_inventory.json"):
    inventory.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
write_json(RECEIPTS / "artifact_inventory.json", {"schema": "skyguard.artifact-inventory.v1", "artifacts": inventory})

print("PASSED_AWAITING_DIRECT_VISUAL_REVIEW")
