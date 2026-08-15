import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Vector


OUTPUT = Path(r"D:\Skyguard52\Production\Attempts\m01-street-detail-kit-grok-mcp\attempt_20260811T070000000000Z\output")
RENDERS = OUTPUT / "renders"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
FINAL_BLEND = OUTPUT / "M01_StreetDetailKit_GrokMCP_Production_A.blend"
FINAL_GLB = EXPORTS / "M01_StreetDetailKit_GrokMCP_Production_A.glb"

ASSETS = {
    "SM_M01_Promenade_Planter_A": {
        "socket": "SOCKET_Planter_Origin",
        "dimension_min": (1.10, 0.45, 0.70),
        "dimension_max": (1.40, 0.70, 1.20),
        "export": "M01_Promenade_Planter_A.glb",
    },
    "SM_M01_Promenade_BicycleRack_A": {
        "socket": "SOCKET_BicycleRack_Origin",
        "dimension_min": (1.50, 0.35, 0.55),
        "dimension_max": (2.20, 0.70, 0.85),
        "export": "M01_Promenade_BicycleRack_A.glb",
    },
    "SM_M01_Promenade_UtilityCabinet_A": {
        "socket": "SOCKET_UtilityCabinet_Origin",
        "dimension_min": (0.70, 0.30, 1.10),
        "dimension_max": (1.10, 0.60, 1.60),
        "export": "M01_Promenade_UtilityCabinet_A.glb",
    },
    "SM_M01_Promenade_StormDrain_A": {
        "socket": "SOCKET_StormDrain_Origin",
        "dimension_min": (0.55, 0.35, 0.04),
        "dimension_max": (0.85, 0.65, 0.15),
        "export": "M01_Promenade_StormDrain_A.glb",
    },
}


def fail(message):
    raise RuntimeError(message)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
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


def object_bounds(names):
    points = []
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            fail(f"Missing required object: {name}")
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))
    if not points:
        fail(f"No bounds were available for: {names}")
    minimum = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
    maximum = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
    return minimum, maximum


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def make_camera(name, names, direction, occupancy=0.68, lens=58.0, target_offset=(0.0, 0.0, 0.0)):
    minimum, maximum = object_bounds(names)
    center = (minimum + maximum) * 0.5 + Vector(target_offset)
    extent = maximum - minimum
    radius = max(extent.x, extent.y, extent.z) * 0.5
    radius = max(radius, 0.25)
    data = bpy.data.cameras.new(name + "_Data")
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.025
    data.clip_end = 500.0
    camera = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(camera)
    half_fov = math.atan((data.sensor_width * 0.5) / data.lens)
    distance = radius / max(math.sin(half_fov) * occupancy, 0.05)
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


def create_ground(center):
    bpy.ops.mesh.primitive_plane_add(size=30.0, location=(center.x, center.y, -0.012))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    for collection in list(ground.users_collection):
        collection.objects.unlink(ground)
    ensure_collection("REVIEW_ONLY").objects.link(ground)
    material = bpy.data.materials.get("REVIEW_Ground_Mat") or bpy.data.materials.new("REVIEW_Ground_Mat")
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.055, 0.065, 0.075, 1.0)
    principled.inputs["Roughness"].default_value = 0.74
    if not ground.data.materials:
        ground.data.materials.append(material)


def configure_stage(mode, center):
    review = ensure_collection("REVIEW_ONLY")
    remove_collection_objects(review)
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if mode == "wet":
        background.inputs["Color"].default_value = (0.075, 0.095, 0.125, 1.0)
        background.inputs["Strength"].default_value = 0.36
        make_area("REVIEW_WetKey", center + Vector((-3.0, -5.0, 6.0)), 1450.0, 5.0, (0.55, 0.72, 1.0), center)
        make_area("REVIEW_WetRim", center + Vector((4.0, 2.0, 3.0)), 850.0, 3.0, (1.0, 0.57, 0.31), center)
        bpy.context.scene.view_settings.exposure = 0.35
    elif mode == "overcast":
        background.inputs["Color"].default_value = (0.22, 0.27, 0.33, 1.0)
        background.inputs["Strength"].default_value = 0.60
        make_area("REVIEW_CloudKey", center + Vector((-4.0, -4.0, 8.0)), 1200.0, 8.0, (0.78, 0.86, 0.98), center)
        make_area("REVIEW_CloudFill", center + Vector((4.0, 3.0, 4.0)), 520.0, 5.0, (0.54, 0.66, 0.82), center)
        bpy.context.scene.view_settings.exposure = 0.10
    else:
        background.inputs["Color"].default_value = (0.29, 0.43, 0.61, 1.0)
        background.inputs["Strength"].default_value = 0.52
        make_sun("REVIEW_Sun", (math.radians(28), math.radians(-18), math.radians(-32)), 1.8, (1.0, 0.80, 0.60))
        make_area("REVIEW_SkyFill", center + Vector((4.0, -5.0, 7.0)), 800.0, 6.0, (0.55, 0.72, 1.0), center)
        bpy.context.scene.view_settings.exposure = 0.0
    bpy.context.scene.view_settings.view_transform = "AgX"
    bpy.context.scene.view_settings.look = "AgX - Medium High Contrast"
    create_ground(center)


def sampled_luminance():
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


def render_shot(filename, asset_name, direction, mode, occupancy, lens, target_offset=(0.0, 0.0, 0.0)):
    for name in ASSETS:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            obj.hide_render = name != asset_name
    minimum, maximum = object_bounds([asset_name])
    center = (minimum + maximum) * 0.5
    configure_stage(mode, center)
    camera = make_camera("REVIEW_Camera", [asset_name], direction, occupancy, lens, target_offset)
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.filepath = str(RENDERS / filename)
    bpy.ops.render.render(write_still=True)
    luminance = sampled_luminance()
    if luminance is not None and luminance < 0.055:
        scene.view_settings.exposure += 1.0
        bpy.ops.render.render(write_still=True)
        luminance = sampled_luminance()
    elif luminance is not None and luminance > 0.78:
        scene.view_settings.exposure -= 0.8
        bpy.ops.render.render(write_still=True)
        luminance = sampled_luminance()
    return {"file": filename, "asset": asset_name, "mode": mode, "mean_luminance": luminance}


def selected_export(path, names):
    bpy.ops.object.select_all(action="DESELECT")
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            obj.select_set(True)
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


def validate_asset(mesh_name, spec):
    failures = []
    obj = bpy.data.objects.get(mesh_name)
    if obj is None or obj.type != "MESH":
        return {"mesh": mesh_name, "classification": "AUTOMATIC_STRUCTURE_REJECTED", "failures": ["Missing required render mesh"]}
    if any(abs(value - 1.0) > 0.001 for value in obj.scale):
        failures.append(f"Unapplied scale: {tuple(obj.scale)}")
    if any(abs(value) > 0.001 for value in obj.rotation_euler):
        failures.append(f"Unapplied rotation: {tuple(obj.rotation_euler)}")
    if len(obj.data.uv_layers) == 0:
        failures.append("Missing UV map")
    if len(obj.material_slots) == 0 or any(slot.material is None for slot in obj.material_slots):
        failures.append("Missing or null material slot")
    socket = bpy.data.objects.get(spec["socket"])
    if socket is None or socket.type != "EMPTY":
        failures.append(f"Missing separate socket empty: {spec['socket']}")
    collisions = sorted(item.name for item in bpy.data.objects if item.name.startswith(f"UCX_{mesh_name}_"))
    if not collisions:
        failures.append("Missing UCX collision")
    minimum, maximum = object_bounds([mesh_name])
    dimensions = maximum - minimum
    for axis, value, lower, upper in zip("XYZ", dimensions, spec["dimension_min"], spec["dimension_max"]):
        if value < lower or value > upper:
            failures.append(f"{axis} dimension {value:.6f} outside [{lower:.6f}, {upper:.6f}]")
    if len(obj.data.vertices) < 24:
        failures.append(f"Vertex count too low: {len(obj.data.vertices)}")
    if len(obj.data.polygons) > 80000:
        failures.append(f"Polygon count too high: {len(obj.data.polygons)}")
    materials = [slot.material.name for slot in obj.material_slots if slot.material is not None]
    return {
        "mesh": mesh_name,
        "socket": spec["socket"],
        "collision": collisions,
        "vertices": len(obj.data.vertices),
        "polygons": len(obj.data.polygons),
        "dimensions_m": [dimensions.x, dimensions.y, dimensions.z],
        "materials": materials,
        "uv_layers": [layer.name for layer in obj.data.uv_layers],
        "classification": "AUTOMATIC_STRUCTURE_PASS" if not failures else "AUTOMATIC_STRUCTURE_REJECTED",
        "failures": failures,
    }


for directory in (OUTPUT, RENDERS, EXPORTS, RECEIPTS):
    directory.mkdir(parents=True, exist_ok=True)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.use_file_extension = True
scene.render.image_settings.color_mode = "RGBA"

for obj in bpy.data.objects:
    if obj.name.startswith("UCX_") or obj.name.startswith("SOCKET_"):
        obj.hide_render = True

asset_receipts = [validate_asset(mesh_name, spec) for mesh_name, spec in ASSETS.items()]
passing_names = [row["mesh"] for row in asset_receipts if row["classification"] == "AUTOMATIC_STRUCTURE_PASS"]

shots = [
    ("01_planter_daylight_full.png", "SM_M01_Promenade_Planter_A", (1.4, -2.2, 0.9), "daylight", 0.68, 58.0, (0.0, 0.0, 0.03)),
    ("02_planter_wet_detail.png", "SM_M01_Promenade_Planter_A", (-1.2, -1.8, 0.45), "wet", 0.78, 72.0, (0.0, 0.0, -0.05)),
    ("03_bicycle_rack_daylight_full.png", "SM_M01_Promenade_BicycleRack_A", (1.3, -2.0, 0.75), "daylight", 0.69, 58.0, (0.0, 0.0, 0.02)),
    ("04_bicycle_rack_joint_close.png", "SM_M01_Promenade_BicycleRack_A", (-0.8, -1.6, 0.35), "overcast", 0.79, 75.0, (0.2, 0.0, -0.08)),
    ("05_utility_cabinet_overcast_full.png", "SM_M01_Promenade_UtilityCabinet_A", (1.2, -2.2, 0.8), "overcast", 0.70, 60.0, (0.0, 0.0, 0.0)),
    ("06_utility_cabinet_wet_detail.png", "SM_M01_Promenade_UtilityCabinet_A", (-1.0, -1.7, 0.45), "wet", 0.79, 74.0, (0.0, 0.0, 0.02)),
    ("07_storm_drain_daylight_full.png", "SM_M01_Promenade_StormDrain_A", (1.2, -1.8, 1.35), "daylight", 0.72, 62.0, (0.0, 0.0, 0.0)),
    ("08_storm_drain_wet_close.png", "SM_M01_Promenade_StormDrain_A", (-0.8, -1.2, 0.75), "wet", 0.80, 78.0, (0.0, 0.0, 0.0)),
]

render_receipts = [render_shot(*shot) for shot in shots]

for name in ASSETS:
    obj = bpy.data.objects.get(name)
    if obj is not None:
        obj.hide_render = False
review_collection = bpy.data.collections.get("REVIEW_ONLY")
if review_collection is not None:
    remove_collection_objects(review_collection)

bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

individual_exports = []
for row in asset_receipts:
    if row["classification"] != "AUTOMATIC_STRUCTURE_PASS":
        continue
    mesh_name = row["mesh"]
    spec = ASSETS[mesh_name]
    export_path = EXPORTS / spec["export"]
    export_names = [mesh_name, spec["socket"]] + row["collision"]
    selected_export(export_path, export_names)
    individual_exports.append(str(export_path))

if not passing_names:
    fail("All four assets failed automatic structural validation")

combined_names = []
for row in asset_receipts:
    if row["classification"] != "AUTOMATIC_STRUCTURE_PASS":
        continue
    combined_names.extend([row["mesh"], row["socket"]])
    combined_names.extend(row["collision"])
selected_export(FINAL_GLB, combined_names)

classification = "PASSED_AWAITING_DIRECT_VISUAL_REVIEW" if len(passing_names) == len(ASSETS) else "PARTIAL_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW"
report = {
    "schema": "skyguard.m01-street-detail-kit.grok-mcp.production-a.report.v1",
    "classification": classification,
    "asset_scope": "Four generic non-branded Mission 1 street-detail props",
    "automatic_pass_count": len(passing_names),
    "automatic_reject_count": len(ASSETS) - len(passing_names),
    "assets": asset_receipts,
    "renders": render_receipts,
    "combined_glb": str(FINAL_GLB),
    "individual_glbs": individual_exports,
    "limitations": [
        "Automatic structural acceptance is not direct visual acceptance",
        "All assets remain mid-distance environment candidates until full-resolution review",
        "Unreal material remapping and in-engine D3D12 review remain required",
        "No runtime promotion is authorized by this Blender report"
    ],
}
write_json(OUTPUT / "grok_implementation_report.json", report)
write_json(RECEIPTS / "structure_and_dimensions.json", report)

artifact_rows = []
for path in sorted(item for item in OUTPUT.rglob("*") if item.is_file() and item.name != "artifact_inventory.json"):
    artifact_rows.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
write_json(RECEIPTS / "artifact_inventory.json", {"schema": "skyguard.artifact-inventory.v1", "artifacts": artifact_rows})

print(classification)

