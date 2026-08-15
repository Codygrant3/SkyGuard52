from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


OUTPUT = Path(r"D:\Skyguard52\Production\Attempts\core-igla-missile-grok-mcp-refinement01\attempt_20260811T0737000000000Z\output")
RENDERS = OUTPUT / "renders"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
FINAL_BLEND = OUTPUT / "CORE_IglaMissile_Refinement01.blend"
FINAL_GLB = EXPORTS / "CORE_IglaMissile_Refinement01.glb"

MESH_NAME = "SM_CORE_IglaMissile_Provisional_A"
AUTHORITY_NAME = "AUTH_IglaMissile_Body_1574x0072"
SOCKET_NAMES = [
    "SOCKET_IglaMissile_ForwardOrigin_PROVISIONAL",
    "SOCKET_IglaMissile_RearAxis_PROVISIONAL",
    "SOCKET_IglaMissile_Exhaust_PROVISIONAL",
]
COLLISION_PREFIX = "UCX_SM_CORE_IglaMissile_Provisional_A_"
EXPECTED_LENGTH = 1.574
EXPECTED_BODY_DIAMETER = 0.072


def fail(message: str) -> None:
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


def remove_collection_objects(collection) -> None:
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def world_bounds(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    minimum = Vector(tuple(min(point[axis] for point in points) for axis in range(3)))
    maximum = Vector(tuple(max(point[axis] for point in points) for axis in range(3)))
    return minimum, maximum


def dimensions(obj):
    minimum, maximum = world_bounds(obj)
    return maximum - minimum


def look_at(obj, target) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def make_camera(direction, occupancy, lens, target_offset=(0.0, 0.0, 0.0)):
    obj = bpy.data.objects[MESH_NAME]
    minimum, maximum = world_bounds(obj)
    center = (minimum + maximum) * 0.5 + Vector(target_offset)
    extent = maximum - minimum
    radius = max(extent.x, extent.y, extent.z) * 0.5
    data = bpy.data.cameras.new("REVIEW_Camera_Data")
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.01
    data.clip_end = 100.0
    camera = bpy.data.objects.new("REVIEW_Camera", data)
    ensure_collection("REVIEW_ONLY").objects.link(camera)
    half_fov = math.atan((data.sensor_width * 0.5) / data.lens)
    distance = max(radius, 0.25) / max(math.sin(half_fov) * occupancy, 0.05)
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
    data.angle = math.radians(2.0)
    data.color = color
    light = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(light)
    light.rotation_euler = rotation


def create_ground(minimum, maximum, wet=False) -> None:
    center = (minimum + maximum) * 0.5
    z = minimum.z - 0.055
    bpy.ops.mesh.primitive_plane_add(size=8.0, location=(center.x, center.y, z))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    for collection in list(ground.users_collection):
        collection.objects.unlink(ground)
    ensure_collection("REVIEW_ONLY").objects.link(ground)
    material = bpy.data.materials.get("REVIEW_Ground_Mat") or bpy.data.materials.new("REVIEW_Ground_Mat")
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.025, 0.032, 0.04, 1.0)
    principled.inputs["Roughness"].default_value = 0.16 if wet else 0.74
    principled.inputs["Metallic"].default_value = 0.0
    ground.data.materials.append(material)


def configure_stage(mode: str) -> None:
    review = ensure_collection("REVIEW_ONLY")
    remove_collection_objects(review)
    obj = bpy.data.objects[MESH_NAME]
    minimum, maximum = world_bounds(obj)
    center = (minimum + maximum) * 0.5
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    scene = bpy.context.scene
    if mode == "night":
        background.inputs["Color"].default_value = (0.006, 0.012, 0.028, 1.0)
        background.inputs["Strength"].default_value = 0.16
        make_area("REVIEW_NightKey", center + Vector((-2.0, -2.5, 2.0)), 700.0, 2.5, (0.32, 0.50, 1.0), center)
        make_area("REVIEW_NightRim", center + Vector((2.0, 1.8, 1.2)), 520.0, 1.8, (1.0, 0.25, 0.10), center)
        scene.view_settings.exposure = 0.55
    elif mode == "wet":
        background.inputs["Color"].default_value = (0.04, 0.07, 0.11, 1.0)
        background.inputs["Strength"].default_value = 0.30
        make_area("REVIEW_WetKey", center + Vector((-2.4, -2.5, 2.6)), 1050.0, 3.5, (0.48, 0.70, 1.0), center)
        make_area("REVIEW_WetRim", center + Vector((2.2, 1.8, 1.4)), 650.0, 2.2, (1.0, 0.55, 0.28), center)
        scene.view_settings.exposure = 0.30
    elif mode == "cockpit":
        background.inputs["Color"].default_value = (0.018, 0.024, 0.025, 1.0)
        background.inputs["Strength"].default_value = 0.24
        make_area("REVIEW_CockpitKey", center + Vector((-1.4, -1.6, 1.1)), 600.0, 1.6, (0.28, 0.70, 0.44), center)
        make_area("REVIEW_CockpitFill", center + Vector((1.8, 1.4, 1.0)), 360.0, 1.4, (0.95, 0.18, 0.10), center)
        scene.view_settings.exposure = 0.35
    elif mode == "overcast":
        background.inputs["Color"].default_value = (0.16, 0.21, 0.28, 1.0)
        background.inputs["Strength"].default_value = 0.55
        make_area("REVIEW_CloudKey", center + Vector((-2.8, -3.2, 3.5)), 1100.0, 5.0, (0.70, 0.82, 1.0), center)
        make_area("REVIEW_CloudFill", center + Vector((2.0, 2.0, 2.0)), 420.0, 3.0, (0.55, 0.66, 0.82), center)
        scene.view_settings.exposure = 0.10
    else:
        background.inputs["Color"].default_value = (0.25, 0.38, 0.58, 1.0)
        background.inputs["Strength"].default_value = 0.48
        make_sun("REVIEW_Sun", (math.radians(35), math.radians(-22), math.radians(-38)), 1.65, (1.0, 0.82, 0.64))
        make_area("REVIEW_SkyFill", center + Vector((2.2, -3.0, 2.8)), 620.0, 4.0, (0.48, 0.68, 1.0), center)
        scene.view_settings.exposure = 0.0
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    create_ground(minimum, maximum, wet=(mode == "wet"))


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
    if luminance is not None and luminance < 0.045:
        scene.view_settings.exposure += 1.0
        bpy.ops.render.render(write_still=True)
        luminance = mean_luminance()
    elif luminance is not None and luminance > 0.82:
        scene.view_settings.exposure -= 0.8
        bpy.ops.render.render(write_still=True)
        luminance = mean_luminance()
    return {"file": filename, "mode": mode, "mean_luminance": luminance}


for directory in (OUTPUT, RENDERS, EXPORTS, RECEIPTS):
    directory.mkdir(parents=True, exist_ok=True)

obj = bpy.data.objects.get(MESH_NAME)
if obj is None or obj.type != "MESH":
    fail(f"Missing required render mesh: {MESH_NAME}")
if any(abs(value - 1.0) > 0.001 for value in obj.scale):
    fail(f"Unapplied scale: {tuple(obj.scale)}")
if any(abs(value) > 0.001 for value in obj.rotation_euler):
    fail(f"Unapplied rotation: {tuple(obj.rotation_euler)}")
if len(obj.data.uv_layers) == 0 or len(obj.data.uv_layers.active.data) == 0:
    fail("Missing or empty UV map")
if len(obj.material_slots) < 3 or any(slot.material is None for slot in obj.material_slots):
    fail("Expected at least three valid material slots")
if len(obj.data.vertices) < 900:
    fail(f"Vertex count too low for production visual asset: {len(obj.data.vertices)}")
if len(obj.data.polygons) > 100000:
    fail(f"Polygon count too high: {len(obj.data.polygons)}")

authority = bpy.data.objects.get(AUTHORITY_NAME)
if authority is None or authority.type != "MESH":
    fail(f"Missing authority guide: {AUTHORITY_NAME}")
if not authority.hide_render:
    fail("Authority guide must be hidden from renders")
if any(abs(value - 1.0) > 0.001 for value in authority.scale) or any(abs(value) > 0.001 for value in authority.rotation_euler):
    fail("Authority guide must have identity scale and rotation")
authority_dimensions = dimensions(authority)
if abs(authority_dimensions.x - EXPECTED_LENGTH) > 0.0005:
    fail(f"Authority length mismatch: {authority_dimensions.x}")
if abs(authority_dimensions.y - EXPECTED_BODY_DIAMETER) > 0.0005 or abs(authority_dimensions.z - EXPECTED_BODY_DIAMETER) > 0.0005:
    fail(f"Authority body diameter mismatch: {tuple(authority_dimensions)}")

mesh_dimensions = dimensions(obj)
if abs(mesh_dimensions.x - EXPECTED_LENGTH) > 0.003:
    fail(f"Visible overall length mismatch: {mesh_dimensions.x}")
if not (0.072 <= mesh_dimensions.y <= 0.22 and 0.072 <= mesh_dimensions.z <= 0.22):
    fail(f"Visible radial bounds are implausible: {tuple(mesh_dimensions)}")

sockets = []
expected_socket_x = [EXPECTED_LENGTH * 0.5, -EXPECTED_LENGTH * 0.5, -EXPECTED_LENGTH * 0.5]
for name, expected_x in zip(SOCKET_NAMES, expected_socket_x):
    socket = bpy.data.objects.get(name)
    if socket is None or socket.type != "EMPTY":
        fail(f"Missing socket empty: {name}")
    if abs(socket.location.x - expected_x) > 0.006 or abs(socket.location.y) > 0.003 or abs(socket.location.z) > 0.003:
        fail(f"Socket is outside governed centerline/end tolerance: {name} {tuple(socket.location)}")
    sockets.append({"name": name, "location_m": list(socket.location)})

collisions = sorted(item.name for item in bpy.data.objects if item.name.startswith(COLLISION_PREFIX))
if not collisions:
    fail("Missing UCX body collision")
collision_obj = bpy.data.objects.get(collisions[0])
collision_dimensions = dimensions(collision_obj)
if abs(collision_dimensions.x - EXPECTED_LENGTH) > 0.006:
    fail(f"Collision length mismatch: {collision_dimensions.x}")
if abs(collision_dimensions.y - EXPECTED_BODY_DIAMETER) > 0.004 or abs(collision_dimensions.z - EXPECTED_BODY_DIAMETER) > 0.004:
    fail(f"Collision must follow 0.072 m body rather than fin span: {tuple(collision_dimensions)}")

for item in bpy.data.objects:
    lowered = item.name.lower()
    if item.type == "FONT" or any(token in lowered for token in ("serial", "marking", "label", "warhead", "propellant", "fuze", "seeker_internal")):
        fail(f"Unsupported detail object found: {item.name}")
    if item.type == "MESH" and item.name != MESH_NAME:
        item.hide_render = True
    if item.name.startswith("UCX_") or item.name.startswith("SOCKET_") or item.name.startswith("AUTH_"):
        item.hide_render = True

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
    ("01_full_side_daylight.png", (0.05, -3.0, 0.55), "daylight", 0.72, 62.0, (0.0, 0.0, 0.0)),
    ("02_opposite_side_overcast.png", (-0.05, 3.0, 0.52), "overcast", 0.72, 62.0, (0.0, 0.0, 0.0)),
    ("03_nose_three_quarter_daylight.png", (2.5, -2.2, 0.9), "daylight", 0.73, 68.0, (0.26, 0.0, 0.0)),
    ("04_tail_three_quarter_overcast.png", (-2.5, 2.1, 0.82), "overcast", 0.73, 68.0, (-0.28, 0.0, 0.0)),
    ("05_top_profile_daylight.png", (0.18, -0.45, 3.0), "daylight", 0.70, 66.0, (0.0, 0.0, 0.0)),
    ("06_tail_detail_wet.png", (-2.5, -1.8, 0.35), "wet", 0.86, 82.0, (-0.57, 0.0, 0.0)),
    ("07_full_side_night.png", (0.05, -3.0, 0.45), "night", 0.72, 62.0, (0.0, 0.0, 0.0)),
    ("08_cockpit_light_context.png", (1.8, -2.6, 0.65), "cockpit", 0.67, 58.0, (0.0, 0.0, 0.0)),
]
render_receipts = [render_shot(*shot) for shot in shots]

for item in bpy.data.objects:
    if not item.name.startswith("AUTH_") and not item.name.startswith("UCX_") and not item.name.startswith("SOCKET_"):
        item.hide_render = False
review = bpy.data.collections.get("REVIEW_ONLY")
if review is not None:
    remove_collection_objects(review)

bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

bpy.ops.object.select_all(action="DESELECT")
for name in [MESH_NAME, AUTHORITY_NAME] + SOCKET_NAMES + collisions:
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
    "schema": "skyguard.core-igla-missile.grok-mcp.refinement01.report.v1",
    "classification": "PASSED_AWAITING_DIRECT_VISUAL_REVIEW",
    "representation_status": "PROVISIONAL_VISUAL_EXTERIOR",
    "non_operational_game_asset": True,
    "mesh": MESH_NAME,
    "authority_guide": AUTHORITY_NAME,
    "sockets": sockets,
    "collision": collisions,
    "vertices": len(obj.data.vertices),
    "polygons": len(obj.data.polygons),
    "visible_dimensions_m": list(mesh_dimensions),
    "authority_dimensions_m": list(authority_dimensions),
    "collision_dimensions_m": list(collision_dimensions),
    "materials": [slot.material.name for slot in obj.material_slots],
    "uv_layers": [layer.name for layer in obj.data.uv_layers],
    "renders": render_receipts,
    "glb": str(FINAL_GLB),
    "limitations": [
        "Visual exterior game asset only; not a technical reconstruction",
        "Only 1.574 m overall length and 0.072 m body diameter are authoritative",
        "Nose, bands, and fin proportions remain provisional visual interpretation",
        "Launcher, internals, performance, and readable markings are intentionally absent",
        "Direct full-resolution review and separate reversible Unreal import remain required",
    ],
}
write_json(OUTPUT / "grok_implementation_report.json", report)
write_json(RECEIPTS / "structure_dimensions_and_representation.json", report)

artifacts = []
for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file() and item.name != "artifact_inventory.json"):
    artifacts.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
write_json(RECEIPTS / "artifact_inventory.json", {"schema": "skyguard.artifact-inventory.v1", "artifacts": artifacts})

print("PASSED_AWAITING_DIRECT_VISUAL_REVIEW")
