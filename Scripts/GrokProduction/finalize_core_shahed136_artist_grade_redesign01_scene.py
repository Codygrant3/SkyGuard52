from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


OUTPUT = Path(r"D:\Skyguard52\Production\Attempts\core-shahed136-grok-mcp-redesign01\attempt_20260811T0830000000000Z\output")
CHECKPOINT = OUTPUT / "checkpoint"
RENDERS = OUTPUT / "renders"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
FINAL_BLEND = OUTPUT / "CORE_Shahed136_ArtistGrade_Redesign01.blend"
FINAL_GLB = EXPORTS / "CORE_Shahed136_ArtistGrade_Redesign01.glb"

ROOT_NAME = "ROOT_CORE_Shahed136_Redesign01"
AIRFRAME_NAME = "SM_CORE_Shahed136_R01_Airframe"
PROPELLER_NAME = "SM_CORE_Shahed136_R01_Propeller"
ENGINE_NAME = "SM_CORE_Shahed136_R01_Engine"
HIGH_NAME = "HP_CORE_Shahed136_R01"
PROPELLER_RIG_NAME = "RIG_CORE_Shahed136_R01_Propeller"
AUTHORITY_NAME = "AUTH_CORE_Shahed136_3300x3000"
RENDER_PREFIX = "SM_CORE_Shahed136_R01_"
COLLISION_PREFIX = "UCX_SM_CORE_Shahed136_R01_"
DAMAGE_PREFIX = "DMG_CORE_Shahed136_R01_"
ACTION_NAME = "ANIM_PropellerPreview_1s"
SOCKET_NAMES = (
    "SOCKET_Origin",
    "SOCKET_PropellerPivot",
    "SOCKET_EngineExhaust",
    "SOCKET_ImpactFX",
    "SOCKET_DamageOrigin",
    "SOCKET_WeakpointEngine",
)
MATERIAL_NAMES = (
    "MAT_Shahed_Composite_Base_R01",
    "MAT_Shahed_Composite_Edge_R01",
    "MAT_Shahed_Panel_R01",
    "MAT_Shahed_Engine_Metal_R01",
    "MAT_Shahed_Propeller_R01",
    "MAT_Shahed_Exhaust_Weathering_R01",
)
CHECKPOINT_FILES = (
    "01_top_initial.png",
    "02_side_initial.png",
    "03_rear_initial.png",
    "04_top_corrected.png",
    "05_side_corrected.png",
    "06_rear_corrected.png",
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


def object_world_points(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        return [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    finally:
        evaluated.to_mesh_clear()


def aggregate_bounds(objects):
    points = []
    for obj in objects:
        points.extend(object_world_points(obj))
    if not points:
        fail("Visible Shahed assembly has no evaluated vertices")
    minimum = Vector(tuple(min(point[axis] for point in points) for axis in range(3)))
    maximum = Vector(tuple(max(point[axis] for point in points) for axis in range(3)))
    return minimum, maximum


def object_bounds(obj):
    return aggregate_bounds([obj])


def look_at(obj, target) -> None:
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def make_camera(objects, direction, occupancy: float, lens: float, target_offset=(0.0, 0.0, 0.0)):
    minimum, maximum = aggregate_bounds(objects)
    center = (minimum + maximum) * 0.5 + Vector(target_offset)
    extent = maximum - minimum
    radius = max(extent.x, extent.y, extent.z) * 0.5
    data = bpy.data.cameras.new("REVIEW_ShahedCamera_Data")
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.03
    data.clip_end = 200.0
    camera = bpy.data.objects.new("REVIEW_ShahedCamera", data)
    ensure_collection("REVIEW_ONLY").objects.link(camera)
    half_fov = math.atan((data.sensor_width * 0.5) / data.lens)
    distance = max(radius, 1.5) / max(math.sin(half_fov) * occupancy, 0.05)
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


def create_ground(minimum, maximum, wet: bool) -> None:
    center = (minimum + maximum) * 0.5
    bpy.ops.mesh.primitive_plane_add(size=14.0, location=(center.x, center.y, minimum.z - 0.05))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    for collection in list(ground.users_collection):
        collection.objects.unlink(ground)
    ensure_collection("REVIEW_ONLY").objects.link(ground)
    material = bpy.data.materials.get("REVIEW_Ground_Mat") or bpy.data.materials.new("REVIEW_Ground_Mat")
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.022, 0.028, 0.035, 1.0)
    principled.inputs["Roughness"].default_value = 0.14 if wet else 0.72
    ground.data.materials.append(material)


def configure_stage(objects, mode: str) -> None:
    clear_collection("REVIEW_ONLY")
    minimum, maximum = aggregate_bounds(objects)
    center = (minimum + maximum) * 0.5
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    scene = bpy.context.scene
    if mode == "night":
        background.inputs["Color"].default_value = (0.004, 0.009, 0.022, 1.0)
        background.inputs["Strength"].default_value = 0.18
        make_area("REVIEW_NightKey", center + Vector((3.0, -4.0, 3.5)), 1250.0, 4.0, (0.30, 0.50, 1.0), center)
        make_area("REVIEW_NightRim", center + Vector((-3.0, 3.0, 2.2)), 900.0, 2.6, (1.0, 0.22, 0.08), center)
        scene.view_settings.exposure = 0.55
    elif mode == "wet":
        background.inputs["Color"].default_value = (0.035, 0.065, 0.105, 1.0)
        background.inputs["Strength"].default_value = 0.34
        make_area("REVIEW_WetKey", center + Vector((3.5, -4.0, 4.5)), 1500.0, 5.0, (0.48, 0.70, 1.0), center)
        make_area("REVIEW_WetRim", center + Vector((-3.2, 2.8, 2.5)), 850.0, 3.0, (1.0, 0.52, 0.22), center)
        scene.view_settings.exposure = 0.32
    elif mode == "underside":
        background.inputs["Color"].default_value = (0.13, 0.17, 0.23, 1.0)
        background.inputs["Strength"].default_value = 0.62
        make_area("REVIEW_UndersideKey", center + Vector((2.5, -2.8, -4.0)), 1700.0, 5.0, (0.72, 0.82, 1.0), center)
        make_area("REVIEW_UndersideRim", center + Vector((-3.0, 3.0, 1.5)), 750.0, 3.0, (1.0, 0.55, 0.28), center)
        scene.view_settings.exposure = 0.28
    elif mode == "overcast":
        background.inputs["Color"].default_value = (0.15, 0.20, 0.28, 1.0)
        background.inputs["Strength"].default_value = 0.62
        make_area("REVIEW_CloudKey", center + Vector((3.5, -4.0, 5.0)), 1450.0, 6.0, (0.72, 0.84, 1.0), center)
        make_area("REVIEW_CloudFill", center + Vector((-3.0, 3.0, 2.8)), 620.0, 4.0, (0.56, 0.68, 0.84), center)
        scene.view_settings.exposure = 0.12
    else:
        background.inputs["Color"].default_value = (0.24, 0.37, 0.58, 1.0)
        background.inputs["Strength"].default_value = 0.52
        make_sun("REVIEW_Sun", (math.radians(34), math.radians(-24), math.radians(-38)), 1.75, (1.0, 0.82, 0.64))
        make_area("REVIEW_SkyFill", center + Vector((-3.0, -4.0, 4.0)), 820.0, 5.0, (0.48, 0.68, 1.0), center)
        scene.view_settings.exposure = 0.0
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    if mode != "underside":
        create_ground(minimum, maximum, mode == "wet")


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


def render_shot(objects, filename, direction, mode, occupancy, lens, target_offset=(0.0, 0.0, 0.0)):
    configure_stage(objects, mode)
    camera = make_camera(objects, direction, occupancy, lens, target_offset)
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.filepath = str(RENDERS / filename)
    bpy.ops.render.render(write_still=True)
    luminance = mean_luminance()
    if luminance is not None and luminance < 0.055:
        scene.view_settings.exposure += 1.1
        bpy.ops.render.render(write_still=True)
        luminance = mean_luminance()
    elif luminance is not None and luminance > 0.82:
        scene.view_settings.exposure -= 0.8
        bpy.ops.render.render(write_still=True)
        luminance = mean_luminance()
    return {"file": filename, "mode": mode, "mean_luminance": luminance}


for directory in (OUTPUT, CHECKPOINT, RENDERS, EXPORTS, RECEIPTS):
    directory.mkdir(parents=True, exist_ok=True)

root = bpy.data.objects.get(ROOT_NAME)
airframe = bpy.data.objects.get(AIRFRAME_NAME)
propeller = bpy.data.objects.get(PROPELLER_NAME)
engine = bpy.data.objects.get(ENGINE_NAME)
high = bpy.data.objects.get(HIGH_NAME)
propeller_rig = bpy.data.objects.get(PROPELLER_RIG_NAME)
authority = bpy.data.objects.get(AUTHORITY_NAME)
if root is None or root.type != "EMPTY":
    fail(f"Missing governed root: {ROOT_NAME}")
for required in (airframe, propeller, engine):
    if required is None or required.type != "MESH":
        fail("Missing required governed Shahed render mesh")
if high is None or high.type != "MESH" or not high.hide_render:
    fail(f"Missing hidden high source: {HIGH_NAME}")
if propeller_rig is None or propeller_rig.type != "EMPTY":
    fail(f"Missing propeller pivot: {PROPELLER_RIG_NAME}")
if authority is None or authority.type != "MESH" or not authority.hide_render:
    fail(f"Missing hidden dimensional guide: {AUTHORITY_NAME}")

renderables = sorted(
    [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.name.startswith(RENDER_PREFIX)],
    key=lambda obj: obj.name,
)
if len(renderables) < 3:
    fail(f"Expected at least three renderable Shahed meshes, found {len(renderables)}")
if any(obj.parent not in (root, propeller_rig) for obj in renderables):
    fail("Every renderable mesh must be parented to the governed root or propeller pivot")
if propeller.parent != propeller_rig or propeller_rig.parent != root:
    fail("Propeller hierarchy does not preserve the governed pivot")

evaluated_vertices = 0
evaluated_triangles = 0
material_names = set()
for obj in renderables:
    if any(abs(value - 1.0) > 0.002 for value in obj.scale):
        fail(f"Unapplied scale on {obj.name}: {tuple(obj.scale)}")
    if obj.data.uv_layers.get("UV0") is None or len(obj.data.uv_layers["UV0"].data) == 0:
        fail(f"Missing nonempty UV0 on {obj.name}")
    for slot in obj.material_slots:
        if slot.material is not None:
            material_names.add(slot.material.name)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        evaluated_vertices += len(mesh.vertices)
        evaluated_triangles += len(mesh.loop_triangles)
    finally:
        evaluated.to_mesh_clear()
if evaluated_vertices < 20000:
    fail(f"Renderable evaluated vertex count is below the artist-grade floor: {evaluated_vertices}")
if len(airframe.data.vertices) < 12000:
    fail(f"Primary airframe source vertex count is below the governed floor: {len(airframe.data.vertices)}")
if evaluated_triangles > 300000:
    fail(f"Evaluated triangle count exceeds the governed ceiling: {evaluated_triangles}")
if not set(MATERIAL_NAMES).issubset(material_names):
    fail(f"Governed material set is incomplete: {sorted(material_names)}")

minimum, maximum = aggregate_bounds(renderables)
visible_dimensions = maximum - minimum
if abs(visible_dimensions.x - 3.300) > 0.015:
    fail(f"Visible length outside authority tolerance: {visible_dimensions.x}")
if abs(visible_dimensions.y - 3.000) > 0.015:
    fail(f"Visible span outside authority tolerance: {visible_dimensions.y}")
if not 0.12 <= visible_dimensions.z <= 0.45:
    fail(f"Visible thickness outside provisional visual range: {visible_dimensions.z}")
authority_min, authority_max = object_bounds(authority)
authority_dimensions = authority_max - authority_min
if abs(authority_dimensions.x - 3.300) > 0.0005 or abs(authority_dimensions.y - 3.000) > 0.0005:
    fail(f"Authority guide changed: {tuple(authority_dimensions)}")

sockets = []
for name in SOCKET_NAMES:
    socket = bpy.data.objects.get(name)
    if socket is None or socket.type != "EMPTY":
        fail(f"Missing governed socket: {name}")
    sockets.append({"name": name, "location_m": list(socket.matrix_world.translation)})
if bpy.data.objects["SOCKET_Origin"].matrix_world.translation.length > 0.025:
    fail("SOCKET_Origin is outside the 25 mm origin tolerance")

collisions = sorted(obj for obj in bpy.data.objects if obj.type == "MESH" and obj.name.startswith(COLLISION_PREFIX))
damage_states = sorted(obj for obj in bpy.data.objects if obj.type == "MESH" and obj.name.startswith(DAMAGE_PREFIX))
if len(collisions) < 3:
    fail(f"Expected at least three UCX meshes, found {len(collisions)}")
if len(damage_states) < 4:
    fail(f"Expected at least four damage-state meshes, found {len(damage_states)}")
if any(not obj.hide_render for obj in collisions + damage_states):
    fail("Collision and damage-state meshes must remain hidden from intact renders")
if bpy.data.actions.get(ACTION_NAME) is None:
    fail(f"Missing propeller preview action: {ACTION_NAME}")

for obj in bpy.data.objects:
    lowered = obj.name.lower()
    if obj.type == "FONT" or any(token in lowered for token in ("serial", "insignia", "flag", "unit_mark", "manufacturer", "warhead", "internal_layout")):
        fail(f"Unsupported or invented detail object found: {obj.name}")

checkpoint_paths = [CHECKPOINT / name for name in CHECKPOINT_FILES]
missing_checkpoints = [str(path) for path in checkpoint_paths if not path.is_file() or path.stat().st_size < 50000]
if missing_checkpoints:
    fail(f"Missing or undersized governed checkpoint renders: {missing_checkpoints}")
checkpoint_review_path = CHECKPOINT / "checkpoint_visual_review.json"
if not checkpoint_review_path.is_file():
    fail("Missing checkpoint_visual_review.json")
try:
    checkpoint_review = json.loads(checkpoint_review_path.read_text(encoding="utf-8"))
except Exception as exc:
    fail(f"Checkpoint review is not valid JSON: {exc}")
if not isinstance(checkpoint_review, dict) or not checkpoint_review:
    fail("Checkpoint review is empty")

for obj in renderables:
    obj.hide_render = False
for obj in [high, authority, *collisions, *damage_states]:
    obj.hide_render = True
for name in SOCKET_NAMES:
    bpy.data.objects[name].hide_render = True
propeller_rig.hide_render = True

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 2560
scene.render.resolution_y = 1440
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.render.use_file_extension = True

shots = (
    ("01_top_orthographic_daylight.png", (0.05, -0.08, 6.0), "daylight", 0.76, 65.0, (0.0, 0.0, 0.0)),
    ("02_side_profile_overcast.png", (0.0, -6.0, 0.65), "overcast", 0.75, 68.0, (0.0, 0.0, 0.0)),
    ("03_front_three_quarter_daylight.png", (5.0, -4.0, 2.2), "daylight", 0.73, 62.0, (0.25, 0.0, 0.02)),
    ("04_hero_front_left_daylight.png", (4.2, -4.7, 2.5), "daylight", 0.78, 72.0, (0.18, 0.0, 0.03)),
    ("05_rear_propulsion_overcast.png", (-4.6, 3.5, 1.8), "overcast", 0.80, 76.0, (-0.50, 0.0, 0.02)),
    ("06_underside_inspection.png", (0.6, -1.1, -5.5), "underside", 0.73, 65.0, (0.0, 0.0, -0.02)),
    ("07_night_intercept.png", (4.0, -4.5, 1.9), "night", 0.75, 68.0, (0.0, 0.0, 0.02)),
    ("08_wet_overcast.png", (-3.8, -4.2, 2.0), "wet", 0.75, 68.0, (-0.10, 0.0, 0.02)),
)
render_receipts = [render_shot(renderables, *shot) for shot in shots]

clear_collection("REVIEW_ONLY")
bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

bpy.ops.object.select_all(action="DESELECT")
export_objects = [*renderables, propeller_rig, *collisions, *damage_states]
export_objects.extend(bpy.data.objects[name] for name in SOCKET_NAMES)
for obj in export_objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = airframe
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
    "schema": "skyguard.core-shahed136.grok-mcp.artist-grade-redesign01.report.v1",
    "classification": "PASSED_AWAITING_DIRECT_VISUAL_REVIEW",
    "representation_status": "PROVISIONAL_ARTIST_GRADE_EXTERIOR_SOURCE",
    "authoritative_dimensions_m": {"overall_length_x": 3.300, "wingspan_y": 3.000},
    "visible_dimensions_m": list(visible_dimensions),
    "authority_dimensions_m": list(authority_dimensions),
    "renderable_meshes": [obj.name for obj in renderables],
    "evaluated_vertices": evaluated_vertices,
    "evaluated_triangles": evaluated_triangles,
    "materials": sorted(material_names),
    "sockets": sockets,
    "collisions": [obj.name for obj in collisions],
    "damage_states": [obj.name for obj in damage_states],
    "propeller_action": ACTION_NAME,
    "checkpoints": [path.name for path in checkpoint_paths],
    "checkpoint_review": checkpoint_review,
    "renders": render_receipts,
    "glb": str(FINAL_GLB),
    "limitations": [
        "Only 3.300 m overall length and 3.000 m wingspan are authoritative",
        "Airfoil, cross-sections, propeller construction, panel positions, internals, markings, and damage breakup remain provisional",
        "No operational performance, payload, guidance, manufacturing, or vulnerability claims are encoded",
        "Direct full-resolution visual review and separate reversible Unreal staging remain required",
    ],
}
write_json(OUTPUT / "grok_implementation_report.json", report)
write_json(RECEIPTS / "geometry_material_structure_receipt.json", report)

artifacts = []
for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file() and item.name != "artifact_inventory.json"):
    artifacts.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
write_json(RECEIPTS / "artifact_inventory.json", {"schema": "skyguard.artifact-inventory.v1", "artifacts": artifacts})

print("PASSED_AWAITING_DIRECT_VISUAL_REVIEW")
