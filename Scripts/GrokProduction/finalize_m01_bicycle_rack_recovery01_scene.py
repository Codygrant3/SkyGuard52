import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector


OUTPUT = Path(r"D:\Skyguard52\Production\Attempts\m01-bicycle-rack-grok-mcp-recovery01\attempt_20260811T072500000000Z\output")
RENDERS = OUTPUT / "renders"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
FINAL_BLEND = OUTPUT / "M01_Promenade_BicycleRack_Recovery01.blend"
FINAL_GLB = EXPORTS / "M01_Promenade_BicycleRack_Recovery01.glb"
MESH_NAME = "SM_M01_Promenade_BicycleRack_A"
SOCKET_NAME = "SOCKET_BicycleRack_Origin"
COLLISION_PREFIX = "UCX_SM_M01_Promenade_BicycleRack_A_"


def fail(message):
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


def ensure_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def remove_collection_objects(collection):
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def bounds(name):
    obj = bpy.data.objects.get(name)
    if obj is None:
        fail(f"Missing object: {name}")
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    minimum = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
    maximum = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
    return minimum, maximum


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def make_camera(direction, occupancy, lens, target_offset):
    minimum, maximum = bounds(MESH_NAME)
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
    distance = max(radius, 0.35) / max(math.sin(half_fov) * occupancy, 0.05)
    camera.location = center + Vector(direction).normalized() * distance
    look_at(camera, center)
    return camera


def make_area(name, location, energy, size, color, target):
    data = bpy.data.lights.new(name + "_Data", "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    light = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(light)
    light.location = location
    look_at(light, target)


def make_sun(name, rotation, energy, color):
    data = bpy.data.lights.new(name + "_Data", "SUN")
    data.energy = energy
    data.angle = math.radians(3.0)
    data.color = color
    light = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(light)
    light.rotation_euler = rotation


def create_ground(center):
    bpy.ops.mesh.primitive_plane_add(size=20.0, location=(center.x, center.y, -0.012))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    for collection in list(ground.users_collection):
        collection.objects.unlink(ground)
    ensure_collection("REVIEW_ONLY").objects.link(ground)
    material = bpy.data.materials.get("REVIEW_Ground_Mat") or bpy.data.materials.new("REVIEW_Ground_Mat")
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.05, 0.06, 0.07, 1.0)
    principled.inputs["Roughness"].default_value = 0.76
    ground.data.materials.append(material)


def configure_stage(mode):
    review = ensure_collection("REVIEW_ONLY")
    remove_collection_objects(review)
    minimum, maximum = bounds(MESH_NAME)
    center = (minimum + maximum) * 0.5
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if mode == "wet":
        background.inputs["Color"].default_value = (0.07, 0.09, 0.12, 1.0)
        background.inputs["Strength"].default_value = 0.38
        make_area("REVIEW_WetKey", center + Vector((-3.0, -4.0, 5.0)), 1400.0, 4.5, (0.55, 0.72, 1.0), center)
        make_area("REVIEW_WetRim", center + Vector((3.0, 2.0, 2.5)), 760.0, 3.0, (1.0, 0.58, 0.34), center)
        bpy.context.scene.view_settings.exposure = 0.35
    elif mode == "overcast":
        background.inputs["Color"].default_value = (0.20, 0.25, 0.31, 1.0)
        background.inputs["Strength"].default_value = 0.60
        make_area("REVIEW_CloudKey", center + Vector((-3.0, -4.0, 6.0)), 1150.0, 7.0, (0.76, 0.86, 1.0), center)
        make_area("REVIEW_CloudFill", center + Vector((3.0, 2.0, 3.0)), 480.0, 4.0, (0.55, 0.67, 0.84), center)
        bpy.context.scene.view_settings.exposure = 0.10
    else:
        background.inputs["Color"].default_value = (0.29, 0.43, 0.61, 1.0)
        background.inputs["Strength"].default_value = 0.52
        make_sun("REVIEW_Sun", (math.radians(28), math.radians(-18), math.radians(-32)), 1.8, (1.0, 0.80, 0.60))
        make_area("REVIEW_SkyFill", center + Vector((3.0, -4.0, 5.0)), 720.0, 5.0, (0.55, 0.72, 1.0), center)
        bpy.context.scene.view_settings.exposure = 0.0
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
    if luminance is not None and luminance < 0.055:
        scene.view_settings.exposure += 1.0
        bpy.ops.render.render(write_still=True)
        luminance = mean_luminance()
    elif luminance is not None and luminance > 0.78:
        scene.view_settings.exposure -= 0.8
        bpy.ops.render.render(write_still=True)
        luminance = mean_luminance()
    return {"file": filename, "mode": mode, "mean_luminance": luminance}


for directory in (OUTPUT, RENDERS, EXPORTS, RECEIPTS):
    directory.mkdir(parents=True, exist_ok=True)

obj = bpy.data.objects.get(MESH_NAME)
if obj is None or obj.type != "MESH":
    fail(f"Missing required mesh: {MESH_NAME}")
if any(abs(value - 1.0) > 0.001 for value in obj.scale):
    fail(f"Unapplied scale: {tuple(obj.scale)}")
if any(abs(value) > 0.001 for value in obj.rotation_euler):
    fail(f"Unapplied rotation: {tuple(obj.rotation_euler)}")
if len(obj.data.uv_layers) == 0:
    fail("Missing UV map")
if len(obj.material_slots) == 0 or any(slot.material is None for slot in obj.material_slots):
    fail("Missing or null material slot")
socket = bpy.data.objects.get(SOCKET_NAME)
if socket is None or socket.type != "EMPTY":
    fail(f"Missing socket empty: {SOCKET_NAME}")
collisions = sorted(item.name for item in bpy.data.objects if item.name.startswith(COLLISION_PREFIX))
if not collisions:
    fail("Missing UCX collision")
minimum, maximum = bounds(MESH_NAME)
dimensions = maximum - minimum
dimension_limits = ((1.65, 1.90), (0.48, 0.62), (0.68, 0.82))
for axis, value, limits in zip("XYZ", dimensions, dimension_limits):
    if value < limits[0] or value > limits[1]:
        fail(f"{axis} dimension {value:.6f} outside [{limits[0]:.6f}, {limits[1]:.6f}]")
if len(obj.data.vertices) < 800:
    fail(f"Vertex count too low for five smooth loops: {len(obj.data.vertices)}")
if len(obj.data.polygons) > 50000:
    fail(f"Polygon count too high: {len(obj.data.polygons)}")

for item in bpy.data.objects:
    if item.type == "MESH" and item.name != MESH_NAME:
        item.hide_render = True
    if item.name.startswith("UCX_") or item.name.startswith("SOCKET_"):
        item.hide_render = True

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.use_file_extension = True
scene.render.image_settings.color_mode = "RGBA"

shots = [
    ("01_full_front_daylight.png", (1.35, -2.2, 0.85), "daylight", 0.68, 58.0, (0.0, 0.0, 0.02)),
    ("02_full_rear_daylight.png", (-1.25, 2.1, 0.78), "daylight", 0.68, 58.0, (0.0, 0.0, 0.02)),
    ("03_end_profile_daylight.png", (2.2, -0.12, 0.65), "daylight", 0.72, 64.0, (0.0, 0.0, 0.02)),
    ("04_top_oblique_overcast.png", (1.0, -1.4, 1.75), "overcast", 0.70, 62.0, (0.0, 0.0, -0.02)),
    ("05_left_crown_joint_close.png", (1.2, -1.8, 0.32), "overcast", 0.86, 82.0, (-0.55, 0.0, 0.21)),
    ("06_center_crown_joint_close.png", (-0.8, -1.7, 0.30), "overcast", 0.86, 82.0, (0.0, 0.0, 0.21)),
    ("07_base_connections_wet.png", (1.0, -1.6, 0.18), "wet", 0.82, 76.0, (0.0, 0.0, -0.23)),
    ("08_eye_level_context.png", (1.8, -3.4, 1.05), "daylight", 0.60, 54.0, (0.0, 0.0, 0.04)),
]
render_receipts = [render_shot(*shot) for shot in shots]

for item in bpy.data.objects:
    item.hide_render = False
review = bpy.data.collections.get("REVIEW_ONLY")
if review is not None:
    remove_collection_objects(review)

bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

bpy.ops.object.select_all(action="DESELECT")
for name in [MESH_NAME, SOCKET_NAME] + collisions:
    item = bpy.data.objects.get(name)
    if item is not None:
        item.select_set(True)
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
    "schema": "skyguard.m01-bicycle-rack.grok-mcp.recovery01.report.v1",
    "classification": "PASSED_AWAITING_DIRECT_VISUAL_REVIEW",
    "mesh": MESH_NAME,
    "socket": SOCKET_NAME,
    "collision": collisions,
    "vertices": len(obj.data.vertices),
    "polygons": len(obj.data.polygons),
    "dimensions_m": [dimensions.x, dimensions.y, dimensions.z],
    "materials": [slot.material.name for slot in obj.material_slots],
    "uv_layers": [layer.name for layer in obj.data.uv_layers],
    "renders": render_receipts,
    "glb": str(FINAL_GLB),
    "limitations": [
        "Direct visual review remains required",
        "Candidate is for mid-distance Mission 1 environment use",
        "Unreal import and in-engine D3D12 validation remain separate gates"
    ],
}
write_json(OUTPUT / "grok_implementation_report.json", report)
write_json(RECEIPTS / "structure_and_dimensions.json", report)

artifacts = []
for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file() and item.name != "artifact_inventory.json"):
    artifacts.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
write_json(RECEIPTS / "artifact_inventory.json", {"schema": "skyguard.artifact-inventory.v1", "artifacts": artifacts})

print("PASSED_AWAITING_DIRECT_VISUAL_REVIEW")

