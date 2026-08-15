import bpy
import json
import math
import hashlib
from pathlib import Path
from mathutils import Vector


OUTPUT = Path(r"D:\Skyguard52\Production\Attempts\m01-promenade-prop-kit-grok-mcp\attempt_20260811T061500000000Z\output")
RENDERS = OUTPUT / "renders"
EXPORTS = OUTPUT / "exports"
RECEIPTS = OUTPUT / "receipts"
FINAL_BLEND = OUTPUT / "M01_Promenade_PropKit_GrokMCP_Production_A.blend"
FINAL_GLB = EXPORTS / "M01_Promenade_PropKit_GrokMCP_Production_A.glb"

ASSETS = {
    "SM_M01_Promenade_Streetlight_A": "SOCKET_Streetlight_Origin",
    "SM_M01_Promenade_Bench_A": "SOCKET_Bench_Origin",
    "SM_M01_Promenade_Bollard_A": "SOCKET_Bollard_Origin",
    "SM_M01_Promenade_LitterBin_A": "SOCKET_LitterBin_Origin",
    "SM_M01_Promenade_Railing_3m_A": "SOCKET_Railing_Origin",
}


def fail(message):
    raise RuntimeError(message)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def object_bounds(names):
    points = []
    for name in names:
        obj = bpy.data.objects.get(name)
        if obj is None:
            fail(f"Missing required object: {name}")
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return minimum, maximum


def ensure_collection(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def remove_collection_objects(collection):
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def look_at(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def make_camera(name, names, direction, occupancy=0.64, lens=52.0, target_offset=(0.0, 0.0, 0.0)):
    minimum, maximum = object_bounds(names)
    center = (minimum + maximum) * 0.5 + Vector(target_offset)
    extent = maximum - minimum
    radius = max(extent.x, extent.y, extent.z) * 0.5
    radius = max(radius, 0.45)
    data = bpy.data.cameras.new(name + "_Data")
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.05
    data.clip_end = 5000.0
    camera = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(camera)
    direction = Vector(direction).normalized()
    half_fov = math.atan((data.sensor_width * 0.5) / data.lens)
    distance = radius / max(math.sin(half_fov) * occupancy, 0.05)
    camera.location = center + direction * distance
    look_at(camera, center)
    return camera


def make_area(name, location, energy, size, color):
    data = bpy.data.lights.new(name + "_Data", "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(obj)
    obj.location = location
    look_at(obj, (0.0, 0.0, 1.5))
    return obj


def make_sun(name, rotation, energy, color):
    data = bpy.data.lights.new(name + "_Data", "SUN")
    data.energy = energy
    data.angle = math.radians(4.0)
    data.color = color
    obj = bpy.data.objects.new(name, data)
    ensure_collection("REVIEW_ONLY").objects.link(obj)
    obj.rotation_euler = rotation
    return obj


def configure_stage(mode):
    review = ensure_collection("REVIEW_ONLY")
    remove_collection_objects(review)
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")

    if mode == "night":
        background.inputs["Color"].default_value = (0.006, 0.012, 0.025, 1.0)
        background.inputs["Strength"].default_value = 0.10
        make_area("REVIEW_MoonFill", (3.0, -8.0, 10.0), 850.0, 8.0, (0.32, 0.48, 0.80))
        street = bpy.data.objects["SM_M01_Promenade_Streetlight_A"]
        minimum, maximum = object_bounds([street.name])
        point_data = bpy.data.lights.new("REVIEW_LampGlow_Data", "POINT")
        point_data.energy = 950.0
        point_data.color = (1.0, 0.72, 0.42)
        point_data.shadow_soft_size = 0.8
        point = bpy.data.objects.new("REVIEW_LampGlow", point_data)
        review.objects.link(point)
        point.location = ((minimum.x + maximum.x) * 0.5, (minimum.y + maximum.y) * 0.5, maximum.z - 0.25)
        bpy.context.scene.view_settings.look = "AgX - Medium High Contrast"
        bpy.context.scene.view_settings.exposure = 1.0
    elif mode == "overcast":
        background.inputs["Color"].default_value = (0.19, 0.23, 0.28, 1.0)
        background.inputs["Strength"].default_value = 0.55
        make_area("REVIEW_CloudKey", (-4.0, -5.0, 11.0), 1300.0, 10.0, (0.76, 0.84, 0.95))
        make_area("REVIEW_CloudFill", (7.0, 4.0, 6.0), 650.0, 7.0, (0.52, 0.64, 0.78))
        bpy.context.scene.view_settings.look = "AgX - Medium High Contrast"
        bpy.context.scene.view_settings.exposure = 0.15
    elif mode == "wet":
        background.inputs["Color"].default_value = (0.08, 0.10, 0.13, 1.0)
        background.inputs["Strength"].default_value = 0.32
        make_area("REVIEW_WetKey", (-3.0, -6.0, 7.0), 1800.0, 6.0, (0.55, 0.70, 0.95))
        make_area("REVIEW_WetRim", (5.0, 3.0, 4.0), 1150.0, 4.0, (0.95, 0.55, 0.28))
        bpy.context.scene.view_settings.look = "AgX - Medium High Contrast"
        bpy.context.scene.view_settings.exposure = 0.45
    else:
        background.inputs["Color"].default_value = (0.28, 0.43, 0.62, 1.0)
        background.inputs["Strength"].default_value = 0.48
        make_sun("REVIEW_Sun", (math.radians(28), math.radians(-18), math.radians(-32)), 2.0, (1.0, 0.78, 0.56))
        make_area("REVIEW_SkyFill", (4.0, -7.0, 10.0), 1050.0, 8.0, (0.50, 0.68, 1.0))
        make_area("REVIEW_WarmBounce", (-5.0, 3.0, 3.0), 520.0, 5.0, (1.0, 0.48, 0.25))
        bpy.context.scene.view_settings.look = "AgX - Medium High Contrast"
        bpy.context.scene.view_settings.exposure = 0.05

    bpy.context.scene.view_settings.view_transform = "AgX"


def create_ground():
    bpy.ops.mesh.primitive_plane_add(size=80.0, location=(0.0, 0.0, -0.012))
    ground = bpy.context.object
    ground.name = "REVIEW_Ground"
    for collection in list(ground.users_collection):
        collection.objects.unlink(ground)
    ensure_collection("REVIEW_ONLY").objects.link(ground)
    material = bpy.data.materials.get("REVIEW_Ground_Mat") or bpy.data.materials.new("REVIEW_Ground_Mat")
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.035, 0.045, 0.055, 1.0)
    principled.inputs["Roughness"].default_value = 0.72
    ground.data.materials.append(material)


def sampled_render_metrics():
    image = bpy.data.images.get("Render Result")
    if image is None or not image.has_data:
        return {"mean_luminance": None, "mean_saturation": None}
    pixels = image.pixels[:]
    pixel_count = len(pixels) // 4
    stride = max(pixel_count // 8192, 1)
    luminance = []
    saturation = []
    for index in range(0, pixel_count, stride):
        r, g, b = pixels[index * 4:index * 4 + 3]
        luminance.append(0.2126 * r + 0.7152 * g + 0.0722 * b)
        maximum = max(r, g, b)
        minimum = min(r, g, b)
        saturation.append(0.0 if maximum <= 1e-6 else (maximum - minimum) / maximum)
    return {
        "mean_luminance": sum(luminance) / len(luminance),
        "mean_saturation": sum(saturation) / len(saturation),
    }


def render_shot(filename, names, direction, mode, occupancy, lens=52.0, target_offset=(0.0, 0.0, 0.0)):
    configure_stage(mode)
    create_ground()
    camera = make_camera("REVIEW_Camera", names, direction, occupancy, lens, target_offset)
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.filepath = str(RENDERS / filename)
    bpy.ops.render.render(write_still=True)
    metrics = sampled_render_metrics()
    if metrics["mean_luminance"] is not None:
        if metrics["mean_luminance"] < 0.055:
            scene.view_settings.exposure += 1.25
            bpy.ops.render.render(write_still=True)
            metrics = sampled_render_metrics()
        elif metrics["mean_luminance"] > 0.72:
            scene.view_settings.exposure -= 1.0
            bpy.ops.render.render(write_still=True)
            metrics = sampled_render_metrics()
    return {"file": filename, "mode": mode, **metrics}


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

asset_receipts = []
all_materials = set()
total_vertices = 0
total_polygons = 0

for mesh_name, socket_name in ASSETS.items():
    obj = bpy.data.objects.get(mesh_name)
    if obj is None or obj.type != "MESH":
        fail(f"Missing required render mesh: {mesh_name}")
    if any(abs(value - 1.0) > 0.001 for value in obj.scale):
        fail(f"Unapplied scale on {mesh_name}: {tuple(obj.scale)}")
    if any(abs(value) > 0.001 for value in obj.rotation_euler):
        fail(f"Unapplied rotation on {mesh_name}: {tuple(obj.rotation_euler)}")
    if len(obj.data.uv_layers) == 0:
        fail(f"Missing UV map: {mesh_name}")
    if len(obj.material_slots) == 0 or any(slot.material is None for slot in obj.material_slots):
        fail(f"Missing material slot: {mesh_name}")
    if bpy.data.objects.get(socket_name) is None:
        fail(f"Missing required socket: {socket_name}")
    collisions = sorted(o.name for o in bpy.data.objects if o.name.startswith(f"UCX_{mesh_name}_"))
    if not collisions:
        fail(f"Missing UCX collision for {mesh_name}")
    minimum, maximum = object_bounds([mesh_name])
    dimensions = maximum - minimum
    total_vertices += len(obj.data.vertices)
    total_polygons += len(obj.data.polygons)
    materials = [slot.material.name for slot in obj.material_slots]
    all_materials.update(materials)
    asset_receipts.append({
        "mesh": mesh_name,
        "socket": socket_name,
        "collision": collisions,
        "vertices": len(obj.data.vertices),
        "polygons": len(obj.data.polygons),
        "dimensions_m": [dimensions.x, dimensions.y, dimensions.z],
        "location_m": list(obj.location),
        "materials": materials,
        "uv_layers": [layer.name for layer in obj.data.uv_layers],
    })

if len(all_materials) < 6:
    fail(f"Expected at least six material families, found {len(all_materials)}")
if total_polygons < 5000:
    fail(f"Renderable polygon count is too low for production review: {total_polygons}")
if total_polygons > 220000:
    fail(f"Renderable polygon count exceeds the bounded kit budget: {total_polygons}")

shots = [
    ("01_daylight_lineup_front.png", list(ASSETS), (1.4, -2.4, 0.85), "daylight", 0.64, 54.0, (0.0, 0.0, 0.35)),
    ("02_daylight_lineup_rear.png", list(ASSETS), (-1.2, 2.6, 0.70), "daylight", 0.64, 54.0, (0.0, 0.0, 0.35)),
    ("03_overcast_streetlight_bench.png", ["SM_M01_Promenade_Streetlight_A", "SM_M01_Promenade_Bench_A"], (1.3, -2.0, 0.55), "overcast", 0.70, 58.0, (0.0, 0.0, 0.25)),
    ("04_wet_bollard_bin.png", ["SM_M01_Promenade_Bollard_A", "SM_M01_Promenade_LitterBin_A"], (1.0, -2.0, 0.45), "wet", 0.72, 62.0, (0.0, 0.0, 0.10)),
    ("05_night_streetlight.png", ["SM_M01_Promenade_Streetlight_A"], (1.1, -2.2, 0.55), "night", 0.69, 58.0, (0.0, 0.0, 0.20)),
    ("06_close_bench_hardware.png", ["SM_M01_Promenade_Bench_A"], (1.15, -1.9, 0.35), "daylight", 0.78, 72.0, (0.0, 0.0, 0.02)),
    ("07_close_railing_joints.png", ["SM_M01_Promenade_Railing_3m_A"], (-1.0, -2.0, 0.42), "overcast", 0.76, 70.0, (0.0, 0.0, 0.05)),
    ("08_gameplay_scale_oblique.png", list(ASSETS), (2.0, -3.5, 1.55), "daylight", 0.53, 50.0, (0.0, 0.0, 0.55)),
]

render_receipts = []
for shot in shots:
    render_receipts.append(render_shot(*shot))

# Remove transient review objects before the governed production save.
review_collection = bpy.data.collections.get("REVIEW_ONLY")
if review_collection is not None:
    remove_collection_objects(review_collection)

bpy.ops.wm.save_as_mainfile(filepath=str(FINAL_BLEND))

combined_names = []
for mesh_name, socket_name in ASSETS.items():
    combined_names.extend([mesh_name, socket_name])
    combined_names.extend(o.name for o in bpy.data.objects if o.name.startswith(f"UCX_{mesh_name}_"))
selected_export(FINAL_GLB, combined_names)

individual_exports = []
for mesh_name, socket_name in ASSETS.items():
    stem = mesh_name.replace("SM_M01_Promenade_", "M01_Promenade_")
    path = EXPORTS / f"{stem}.glb"
    names = [mesh_name, socket_name] + [o.name for o in bpy.data.objects if o.name.startswith(f"UCX_{mesh_name}_")]
    selected_export(path, names)
    individual_exports.append(str(path))

report = {
    "schema": "skyguard.m01-promenade-prop-kit.grok-mcp.production-a.report.v1",
    "classification": "PASSED_AWAITING_DIRECT_VISUAL_REVIEW",
    "asset_scope": "Five generic non-branded coastal promenade props",
    "total_vertices": total_vertices,
    "total_polygons": total_polygons,
    "material_families": sorted(all_materials),
    "assets": asset_receipts,
    "renders": render_receipts,
    "combined_glb": str(FINAL_GLB),
    "individual_glbs": individual_exports,
    "limitations": [
        "Project-provisional dimensions and generic design identity",
        "Final Unreal material remapping and in-engine D3D12 review remain required",
        "No runtime promotion is authorized by this Blender report",
    ],
}
write_json(OUTPUT / "grok_implementation_report.json", report)
write_json(RECEIPTS / "structure_and_dimensions.json", report)

artifact_rows = []
for path in sorted(p for p in OUTPUT.rglob("*") if p.is_file() and p.name != "artifact_inventory.json"):
    artifact_rows.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
write_json(RECEIPTS / "artifact_inventory.json", {"schema": "skyguard.artifact-inventory.v1", "artifacts": artifact_rows})

print("PASSED_AWAITING_DIRECT_VISUAL_REVIEW")
