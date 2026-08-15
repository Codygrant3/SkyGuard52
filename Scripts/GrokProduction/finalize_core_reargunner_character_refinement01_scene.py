from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


OUTPUT = Path(r"D:\Skyguard52\Production\Attempts\core-reargunner-character-grok-mcp-refinement01\attempt_20260811T0805000000000Z\output")
RENDERS = OUTPUT / "renders"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
FINAL_BLEND = OUTPUT / "CORE_RearGunner_Refinement01_GrokMCP.blend"
FINAL_GLB = EXPORTS / "CORE_RearGunner_Refinement01_GrokMCP.glb"

MESH_NAME = "SK_CORE_RearGunner_R01"
HIGH_NAME = "HP_CORE_RearGunner_R01"
ARMATURE_NAME = "RIG_RearGunnerCharacter_R01"
SOCKET_NAMES = (
    "SOCKET_Origin",
    "SOCKET_SeatDatum",
    "SOCKET_Pelvis",
    "SOCKET_Head",
    "SOCKET_RearGunnerCamera",
    "SOCKET_Wrist_R",
    "SOCKET_Wrist_L",
    "SOCKET_RifleShoulder",
    "SOCKET_IglaShoulder",
    "SOCKET_WeaponSweepOrigin",
)
ACTION_NAMES = (
    "ACT_SeatedNeutral",
    "ACT_RifleSupport",
    "ACT_RifleTriggerADS",
    "ACT_IglaSupport",
    "ACT_TurbulenceBrace",
)
MATERIAL_NAMES = (
    "MAT_FlightSuit_Olive_R01",
    "MAT_FlightSuit_Shadow_R01",
    "MAT_Footwear_Black_R01",
    "MAT_Headform_NeutralCloth_R01",
    "MAT_Character_Stitch_R01",
    "MAT_Character_Zipper_R01",
)
REQUIRED_BONES = (
    "root", "pelvis", "spine_01", "spine_02", "chest", "neck", "head",
    "clavicle_R", "upperarm_R", "upperarm_twist_R", "forearm_R", "forearm_twist_R", "wrist_R",
    "clavicle_L", "upperarm_L", "upperarm_twist_L", "forearm_L", "forearm_twist_L", "wrist_L",
    "thigh_R", "thigh_twist_R", "calf_R", "calf_twist_R", "foot_R", "toe_R",
    "thigh_L", "thigh_twist_L", "calf_L", "calf_twist_L", "foot_L", "toe_L",
)


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


def clear_collection(name: str) -> None:
    collection = bpy.data.collections.get(name)
    if collection is None:
        return
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def evaluated_bounds(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        if not points:
            fail("Evaluated character mesh is empty")
        minimum = Vector(tuple(min(point[axis] for point in points) for axis in range(3)))
        maximum = Vector(tuple(max(point[axis] for point in points) for axis in range(3)))
        return minimum, maximum
    finally:
        evaluated.to_mesh_clear()


def look_at(obj, target) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def pose_action(armature, name: str) -> None:
    action = bpy.data.actions.get(name)
    if action is None:
        fail(f"Missing governed action: {name}")
    if armature.animation_data is None:
        armature.animation_data_create()
    armature.animation_data.action = action
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()


def make_camera(direction, occupancy: float, lens: float, target_offset=(0.0, 0.0, 0.0)):
    mesh = bpy.data.objects[MESH_NAME]
    minimum, maximum = evaluated_bounds(mesh)
    center = (minimum + maximum) * 0.5 + Vector(target_offset)
    extent = maximum - minimum
    radius = max(extent.x, extent.y, extent.z) * 0.5
    data = bpy.data.cameras.new("REVIEW_CharacterCamera_Data")
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.02
    data.clip_end = 100.0
    camera = bpy.data.objects.new("REVIEW_CharacterCamera", data)
    ensure_collection("REVIEW_ONLY").objects.link(camera)
    half_fov = math.atan((data.sensor_width * 0.5) / data.lens)
    distance = max(radius, 0.8) / max(math.sin(half_fov) * occupancy, 0.05)
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


def create_review_floor(minimum, maximum, wet: bool) -> None:
    center = (minimum + maximum) * 0.5
    bpy.ops.mesh.primitive_plane_add(size=8.0, location=(center.x, center.y, minimum.z - 0.012))
    floor = bpy.context.object
    floor.name = "REVIEW_Floor"
    for collection in list(floor.users_collection):
        collection.objects.unlink(floor)
    ensure_collection("REVIEW_ONLY").objects.link(floor)
    material = bpy.data.materials.get("REVIEW_Floor_Mat") or bpy.data.materials.new("REVIEW_Floor_Mat")
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.025, 0.032, 0.04, 1.0)
    principled.inputs["Roughness"].default_value = 0.20 if wet else 0.72
    floor.data.materials.append(material)


def configure_stage(mode: str) -> None:
    clear_collection("REVIEW_ONLY")
    mesh = bpy.data.objects[MESH_NAME]
    minimum, maximum = evaluated_bounds(mesh)
    center = (minimum + maximum) * 0.5
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    scene = bpy.context.scene
    if mode == "night":
        background.inputs["Color"].default_value = (0.006, 0.012, 0.028, 1.0)
        background.inputs["Strength"].default_value = 0.16
        make_area("REVIEW_NightKey", center + Vector((-2.3, -2.7, 2.7)), 900.0, 3.0, (0.32, 0.50, 1.0), center)
        make_area("REVIEW_NightRim", center + Vector((2.0, 1.8, 1.8)), 580.0, 2.0, (1.0, 0.25, 0.10), center)
        scene.view_settings.exposure = 0.55
    elif mode == "wet":
        background.inputs["Color"].default_value = (0.04, 0.07, 0.11, 1.0)
        background.inputs["Strength"].default_value = 0.30
        make_area("REVIEW_WetKey", center + Vector((-2.6, -2.8, 3.2)), 1200.0, 4.0, (0.48, 0.70, 1.0), center)
        make_area("REVIEW_WetRim", center + Vector((2.2, 1.8, 2.0)), 700.0, 2.4, (1.0, 0.55, 0.28), center)
        scene.view_settings.exposure = 0.25
    elif mode == "cockpit":
        background.inputs["Color"].default_value = (0.018, 0.024, 0.025, 1.0)
        background.inputs["Strength"].default_value = 0.24
        make_area("REVIEW_CockpitKey", center + Vector((-1.6, -1.8, 1.8)), 720.0, 1.8, (0.28, 0.70, 0.44), center)
        make_area("REVIEW_CockpitFill", center + Vector((1.8, 1.4, 1.5)), 430.0, 1.5, (0.95, 0.18, 0.10), center)
        scene.view_settings.exposure = 0.35
    elif mode == "overcast":
        background.inputs["Color"].default_value = (0.16, 0.21, 0.28, 1.0)
        background.inputs["Strength"].default_value = 0.55
        make_area("REVIEW_CloudKey", center + Vector((-3.0, -3.2, 3.8)), 1250.0, 5.0, (0.70, 0.82, 1.0), center)
        make_area("REVIEW_CloudFill", center + Vector((2.0, 2.0, 2.5)), 480.0, 3.0, (0.55, 0.66, 0.82), center)
        scene.view_settings.exposure = 0.10
    else:
        background.inputs["Color"].default_value = (0.25, 0.38, 0.58, 1.0)
        background.inputs["Strength"].default_value = 0.48
        make_sun("REVIEW_Sun", (math.radians(35), math.radians(-22), math.radians(-38)), 1.65, (1.0, 0.82, 0.64))
        make_area("REVIEW_SkyFill", center + Vector((2.2, -3.0, 3.0)), 720.0, 4.0, (0.48, 0.68, 1.0), center)
        scene.view_settings.exposure = 0.0
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    create_review_floor(minimum, maximum, mode == "wet")


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


def render_shot(armature, filename, action, direction, mode, occupancy, lens, target_offset=(0.0, 0.0, 0.0)):
    pose_action(armature, action)
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
    return {"file": filename, "action": action, "mode": mode, "mean_luminance": luminance}


for directory in (OUTPUT, RENDERS, EXPORTS, RECEIPTS):
    directory.mkdir(parents=True, exist_ok=True)

mesh = bpy.data.objects.get(MESH_NAME)
high = bpy.data.objects.get(HIGH_NAME)
armature = bpy.data.objects.get(ARMATURE_NAME)
if mesh is None or mesh.type != "MESH":
    fail(f"Missing game mesh: {MESH_NAME}")
if high is None or high.type != "MESH" or not high.hide_render:
    fail(f"Missing hidden preserved high source: {HIGH_NAME}")
if armature is None or armature.type != "ARMATURE":
    fail(f"Missing armature: {ARMATURE_NAME}")
if any(abs(value - 1.0) > 0.002 for value in mesh.scale) or any(abs(value) > 0.002 for value in mesh.rotation_euler):
    fail("Character game mesh transforms are not applied")
if any(abs(value - 1.0) > 0.002 for value in armature.scale) or any(abs(value) > 0.002 for value in armature.rotation_euler):
    fail("Character armature transforms are not applied")
if len(mesh.data.vertices) < 30000 or len(mesh.data.vertices) > 180000:
    fail(f"Character vertex count outside governed range: {len(mesh.data.vertices)}")
mesh.data.calc_loop_triangles()
triangles = len(mesh.data.loop_triangles)
if triangles > 180000:
    fail(f"Character triangle count exceeds budget: {triangles}")
uv = mesh.data.uv_layers.get("UV0")
if uv is None or len(uv.data) == 0:
    fail("Character UV0 is missing or empty")
material_names = [slot.material.name for slot in mesh.material_slots if slot.material is not None]
if not set(MATERIAL_NAMES).issubset(material_names):
    fail(f"Character material contract changed: {material_names}")
modifiers = [modifier for modifier in mesh.modifiers if modifier.type == "ARMATURE" and modifier.object == armature]
if not modifiers:
    fail("Character mesh is not bound to the governed armature")

bone_names = {bone.name for bone in armature.data.bones}
if len(bone_names) < 31 or not set(REQUIRED_BONES).issubset(bone_names):
    fail(f"Character deform-bone contract changed: count={len(bone_names)} missing={sorted(set(REQUIRED_BONES) - bone_names)}")
for name in ACTION_NAMES:
    if bpy.data.actions.get(name) is None:
        fail(f"Missing governed character action: {name}")

sockets = []
for name in SOCKET_NAMES:
    socket = bpy.data.objects.get(name)
    if socket is None or socket.type != "EMPTY":
        fail(f"Missing character socket: {name}")
    sockets.append({"name": name, "location_m": list(socket.matrix_world.translation)})

weighted = sum(1 for vertex in mesh.data.vertices if len(vertex.groups) > 0)
weight_coverage = weighted / max(len(mesh.data.vertices), 1)
if weight_coverage < 0.995:
    fail(f"Character vertex-group coverage is insufficient: {weight_coverage:.6f}")

for obj in bpy.data.objects:
    lowered = obj.name.lower()
    if obj.type == "FONT" or any(token in lowered for token in ("weapon", "rifle_mesh", "igla_mesh", "insignia", "rank", "flag", "metahuman", "webgame")):
        fail(f"Prohibited character detail found: {obj.name}")
    if obj.type == "MESH" and any(token in lowered for token in ("hand", "palm", "finger", "thumb")):
        fail(f"Placeholder hand geometry is prohibited: {obj.name}")

pose_action(armature, "ACT_SeatedNeutral")
minimum, maximum = evaluated_bounds(mesh)
sitting_height = maximum.z
if abs(sitting_height - 0.895) > 0.020:
    fail(f"Project-provisional sitting-height contract changed: {sitting_height}")
camera_socket = bpy.data.objects["SOCKET_RearGunnerCamera"]
camera_z = camera_socket.matrix_world.translation.z
if abs(camera_z - 0.780) > 0.018:
    fail(f"Project-provisional eye-height contract changed: {camera_z}")

high.hide_render = True
for name in SOCKET_NAMES:
    bpy.data.objects[name].hide_render = True

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.render.use_file_extension = True

shots = (
    ("01_neutral_front_three_quarter_daylight.png", "ACT_SeatedNeutral", (3.0, -3.2, 2.0), "daylight", 0.72, 62.0, (0.0, 0.0, 0.05)),
    ("02_neutral_side_overcast.png", "ACT_SeatedNeutral", (0.1, -4.0, 1.4), "overcast", 0.72, 64.0, (0.0, 0.0, 0.05)),
    ("03_neutral_rear_daylight.png", "ACT_SeatedNeutral", (-3.2, 2.8, 1.8), "daylight", 0.72, 62.0, (0.0, 0.0, 0.05)),
    ("04_rifle_support_overcast.png", "ACT_RifleSupport", (3.2, -3.0, 1.8), "overcast", 0.72, 64.0, (0.12, 0.0, 0.10)),
    ("05_trigger_ads_cockpit.png", "ACT_RifleTriggerADS", (3.4, -2.4, 1.45), "cockpit", 0.76, 70.0, (0.18, 0.0, 0.15)),
    ("06_igla_support_daylight.png", "ACT_IglaSupport", (3.1, 2.9, 1.9), "daylight", 0.72, 64.0, (0.12, 0.0, 0.12)),
    ("07_turbulence_brace_wet.png", "ACT_TurbulenceBrace", (2.7, -3.1, 1.7), "wet", 0.72, 62.0, (0.0, 0.0, 0.06)),
    ("08_neutral_night.png", "ACT_SeatedNeutral", (3.0, -3.2, 1.8), "night", 0.72, 62.0, (0.0, 0.0, 0.05)),
)
render_receipts = [render_shot(armature, *shot) for shot in shots]

clear_collection("REVIEW_ONLY")
pose_action(armature, "ACT_SeatedNeutral")
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

bpy.ops.object.select_all(action="DESELECT")
for obj in (mesh, armature):
    obj.select_set(True)
for name in SOCKET_NAMES:
    bpy.data.objects[name].select_set(True)
bpy.context.view_layer.objects.active = mesh
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
    export_animations=True,
)

report = {
    "schema": "skyguard.core-reargunner-character.grok-mcp.refinement01.report.v1",
    "classification": "PASSED_AWAITING_DIRECT_VISUAL_REVIEW",
    "representation_status": "PROJECT_PROVISIONAL_SEATED_CHARACTER_SOURCE",
    "mesh": MESH_NAME,
    "high_source": HIGH_NAME,
    "armature": ARMATURE_NAME,
    "vertices": len(mesh.data.vertices),
    "triangles": triangles,
    "weight_coverage": weight_coverage,
    "neutral_bounds_m": {"minimum": list(minimum), "maximum": list(maximum)},
    "sitting_height_m": sitting_height,
    "eye_height_m": camera_z,
    "bones": sorted(bone_names),
    "actions": list(ACTION_NAMES),
    "sockets": sockets,
    "materials": material_names,
    "uv_layers": [layer.name for layer in mesh.data.uv_layers],
    "renders": render_receipts,
    "glb": str(FINAL_GLB),
    "limitations": [
        "Project-provisional accommodation profile, not a measured percentile or real identity",
        "No hands, weapons, cockpit, harness, headset, helmet, insignia, or personal likeness are included",
        "Direct full-resolution review remains mandatory",
        "Passing this asset does not prove wrist attachment, weapon contact, cockpit clearance, Unreal retargeting, pilot safety, performance, or packaged-game acceptance",
    ],
}
write_json(OUTPUT / "grok_implementation_report.json", report)
write_json(RECEIPTS / "geometry_rig_receipt.json", report)

artifacts = []
for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file() and item.name != "artifact_inventory.json"):
    artifacts.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
write_json(RECEIPTS / "artifact_inventory.json", {"schema": "skyguard.artifact-inventory.v1", "artifacts": artifacts})

print("PASSED_AWAITING_DIRECT_VISUAL_REVIEW")
