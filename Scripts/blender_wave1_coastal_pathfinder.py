"""Author the Mission 1 coastal kit and Pathfinder boss candidate.

This is the first deterministic production wave for the Unreal-only AAA track.
It produces a native Blender master, an Unreal-importable GLB, an asset manifest,
three visual proofs, stable UV metadata and gameplay-oriented pivots.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
SOURCE_DIR = ROOT / "Content" / "Skyguard" / "Meshes" / "Source" / "Mission01"
REPORT_DIR = ROOT / "Saved" / "Reports"
SCREEN_DIR = ROOT / "Saved" / "Screenshots" / "Mission01_Wave1"
MASTER_BLEND = SOURCE_DIR / "M01_WAVE1_COASTAL_PATHFINDER_MASTER.blend"
EXPORT_GLB = SOURCE_DIR / "wave1_coastal_pathfinder.glb"
MANIFEST_PATH = REPORT_DIR / "M01_WAVE1_ASSET_MANIFEST.json"
REPORT_PATH = REPORT_DIR / "M01_WAVE1_BLENDER_REPORT.json"

UV_NAME = "UV_M01_0"
assets: list[bpy.types.Object] = []
placements: list[dict] = []
collision_contracts: list[dict] = []


def material(name, color, roughness=0.6, metallic=0.0, noise_scale=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if noise_scale > 0.0:
        noise = mat.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = noise_scale
        noise.inputs["Detail"].default_value = 4.0
        noise.inputs["Roughness"].default_value = 0.72
        bump = mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.14
        bump.inputs["Distance"].default_value = 0.035
        mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def finish_mesh(obj, mat, bevel=0.04, collision="box", role="shared"):
    obj.data.materials.append(mat)
    activate(obj)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0.0:
        mod = obj.modifiers.new("ProductionBevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
        bpy.ops.object.modifier_apply(modifier=mod.name)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    activate(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")
    layer = obj.data.uv_layers.active
    if layer:
        layer.name = UV_NAME
    obj["SKG_AssetRole"] = role
    obj["SKG_CollisionContract"] = collision
    obj["SKG_UVLayer"] = UV_NAME
    obj["SKG_ForwardAxis"] = "+X"
    assets.append(obj)
    collision_contracts.append({"asset": obj.name, "shape": collision})
    return obj


def cube(name, dims, mat, bevel=0.04, role="shared", collision="box"):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.0))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    return finish_mesh(obj, mat, bevel, collision, role)


def cylinder(name, radius, depth, mat, vertices=48, rotation=(0.0, 0.0, 0.0),
             role="shared", collision="capsule"):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=(0.0, 0.0, 0.0),
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    return finish_mesh(obj, mat, min(radius * 0.08, 0.04), collision, role)


def sphere(name, scale, mat, role="shared", collision="convex"):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1.0)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    return finish_mesh(obj, mat, 0.0, collision, role)


def custom_mesh(name, vertices, faces, mat, role="shared", collision="convex", bevel=0.02):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return finish_mesh(obj, mat, bevel, collision, role)


def set_origin(obj, location):
    old = bpy.context.scene.cursor.location.copy()
    activate(obj)
    bpy.context.scene.cursor.location = location
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    bpy.context.scene.cursor.location = old
    obj["SKG_PivotWorld"] = [round(float(v), 5) for v in location]


def place(asset, location, rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0),
          mission_role="dressing"):
    placements.append(
        {
            "asset": asset.name,
            "location_m": [float(v) for v in location],
            "rotation_deg": [math.degrees(float(v)) for v in rotation],
            "scale": [float(v) for v in scale],
            "mission_role": mission_role,
        }
    )


def make_pathfinder_body(name, mat, damaged=False):
    x0, x1 = -2.1, 2.1
    half_span = 2.7
    z = 0.0
    vertices = [
        (x1, 0.0, z + 0.05),
        (0.6, -half_span, z),
        (-1.55, -1.25, z),
        (x0, -0.45, z),
        (x0, 0.45, z),
        (-1.55, 1.25, z),
        (0.6, half_span, z),
        (1.15, 0.0, z + 0.42),
        (0.25, -0.45, z + 0.32),
        (-1.45, -0.32, z + 0.22),
        (-1.45, 0.32, z + 0.22),
        (0.25, 0.45, z + 0.32),
        (1.15, 0.0, z - 0.20),
        (0.25, -0.42, z - 0.16),
        (-1.45, -0.30, z - 0.12),
        (-1.45, 0.30, z - 0.12),
        (0.25, 0.42, z - 0.16),
    ]
    faces = [
        (0, 1, 2, 3, 4, 5, 6),
        (0, 7, 8, 1),
        (1, 8, 9, 2),
        (2, 9, 3),
        (0, 6, 11, 7),
        (6, 5, 10, 11),
        (5, 4, 10),
        (7, 11, 10, 9, 8),
        (9, 10, 4, 3),
        (0, 12, 13, 1),
        (1, 13, 14, 2),
        (2, 14, 3),
        (0, 6, 16, 12),
        (6, 5, 15, 16),
        (5, 4, 15),
        (12, 16, 15, 14, 13),
        (14, 15, 4, 3),
    ]
    obj = custom_mesh(name, vertices, faces, mat, "boss_body", "convex", 0.035)
    if damaged:
        obj.scale.z = 0.94
        obj["SKG_DamageState"] = "critical"
    else:
        obj["SKG_DamageState"] = "intact"
    return obj


def configure_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.world = bpy.data.worlds.new("M01_World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.035, 0.07, 0.11, 1.0)
    bg.inputs["Strength"].default_value = 0.48
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass


def add_camera(name, location, target, lens=52.0):
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.object
    camera.name = name
    camera.data.lens = lens
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return camera


def render_proofs(preview_objects):
    for obj in assets:
        obj.hide_render = True
    for obj in preview_objects:
        obj.hide_render = False

    bpy.ops.object.light_add(type="AREA", location=(20.0, -18.0, 22.0))
    key = bpy.context.object
    key.data.energy = 1900.0
    key.data.shape = "DISK"
    key.data.size = 14.0
    key.rotation_euler = (math.radians(30.0), 0.0, math.radians(48.0))
    bpy.ops.object.light_add(type="AREA", location=(-15.0, 10.0, 12.0))
    bpy.context.object.data.energy = 1050.0
    bpy.context.object.data.size = 10.0
    bpy.ops.object.light_add(type="SUN", location=(0.0, 0.0, 20.0))
    bpy.context.object.data.energy = 2.2
    bpy.context.object.rotation_euler = (math.radians(25.0), math.radians(-18.0), math.radians(-35.0))

    cameras = [
        ("M01_Coast", (-76.0, -92.0, 52.0), (1.0, 12.0, 7.0), 48.0),
        ("M01_AssetGrid", (72.0, -82.0, 58.0), (0.0, 10.0, 8.0), 48.0),
        ("M01_Pathfinder", (18.0, -13.0, 11.0), (8.0, 4.0, 7.0), 62.0),
    ]
    renders = []
    for label, location, target, lens in cameras:
        for obj in preview_objects:
            is_boss = "Boss_Pathfinder" in obj.name
            obj.hide_render = (label == "M01_Pathfinder" and not is_boss) or (
                label == "M01_Coast" and is_boss
            )
        camera = add_camera("CAM_" + label, location, target, lens)
        bpy.context.scene.camera = camera
        output = SCREEN_DIR / f"{label}_FINAL.png"
        bpy.context.scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        renders.append({"camera": label, "path": str(output), "bytes": output.stat().st_size})
    return renders


def main():
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    SCREEN_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    configure_scene()

    sand = material("M_M01_Sand", (0.58, 0.46, 0.28), 0.88, 0.0, 7.0)
    concrete = material("M_M01_Concrete", (0.31, 0.34, 0.33), 0.82, 0.0, 18.0)
    asphalt = material("M_M01_Asphalt", (0.055, 0.065, 0.068), 0.94, 0.0, 25.0)
    plaster = material("M_M01_Plaster", (0.46, 0.50, 0.46), 0.76, 0.0, 12.0)
    blue = material("M_M01_PaintedBlue", (0.035, 0.16, 0.36), 0.48, 0.18, 20.0)
    metal = material("M_M01_Metal", (0.09, 0.11, 0.12), 0.44, 0.72, 35.0)
    glass = material("M_M01_Glass", (0.035, 0.13, 0.19), 0.18, 0.08, 0.0)
    red = material("M_M01_Red", (0.48, 0.025, 0.018), 0.48, 0.12, 12.0)
    radar = material("M_M01_Radar", (0.22, 0.25, 0.19), 0.64, 0.28, 18.0)
    boss_paint = material("M_Boss_Pathfinder_Paint", (0.12, 0.14, 0.11), 0.56, 0.36, 40.0)
    boss_metal = material("M_Boss_Pathfinder_Metal", (0.035, 0.042, 0.038), 0.42, 0.78, 48.0)
    hot = material("M_Boss_Pathfinder_Heat", (0.38, 0.075, 0.015), 0.28, 0.45, 24.0)

    # Shared coastal kit.
    beach_a = cube("SM_Coast_BeachSegment_A", (42.0, 18.0, 0.8), sand, 0.25, "coastal_terrain")
    beach_b = cube("SM_Coast_BeachSegment_B", (30.0, 14.0, 1.2), sand, 0.35, "coastal_terrain")
    dune_a = sphere("SM_Coast_Dune_A", (5.5, 3.4, 1.35), sand, "coastal_terrain")
    dune_b = sphere("SM_Coast_Dune_B", (3.8, 2.8, 0.95), sand, "coastal_terrain")
    seawall = cube("SM_Coast_SeawallStraight_A", (18.0, 1.2, 3.2), concrete, 0.12, "coastal_structure")
    seawall_corner = cube("SM_Coast_SeawallCorner_A", (6.0, 6.0, 3.2), concrete, 0.14, "coastal_structure")
    road = cube("SM_Road_CoastalTransition_A", (36.0, 8.0, 0.35), asphalt, 0.06, "road")
    promenade = cube("SM_Coast_Promenade_A", (30.0, 5.0, 0.45), concrete, 0.08, "promenade")
    groyne = cube("SM_Coast_Groyne_A", (1.2, 12.0, 0.9), concrete, 0.09, "coastal_structure")
    drain = cylinder("SM_Coast_DrainOutlet_A", 0.85, 3.2, concrete, 48, (math.radians(90.0), 0.0, 0.0), "coastal_structure")

    # Ukrainian coastal urban modules.
    apt_a = cube("SM_Urban_Apartment_Module_A", (12.0, 9.0, 18.0), plaster, 0.18, "urban_module")
    apt_b = cube("SM_Urban_Apartment_Module_B", (9.0, 8.0, 14.0), plaster, 0.16, "urban_module")
    mid_a = cube("SM_Urban_Midrise_Module_A", (14.0, 10.0, 24.0), plaster, 0.20, "urban_module")
    mid_b = cube("SM_Urban_Midrise_Module_B", (10.0, 10.0, 20.0), plaster, 0.18, "urban_module")
    balcony = cube("SM_Urban_BalconyBank_A", (0.85, 7.2, 11.5), concrete, 0.06, "urban_detail")
    windows = cube("SM_Urban_WindowBank_A", (0.28, 6.6, 10.0), glass, 0.025, "urban_detail", "none")
    entrance = cube("SM_Urban_Entrance_A", (1.1, 3.2, 3.0), blue, 0.07, "urban_detail")
    roof_service = cube("SM_Urban_RoofService_A", (4.2, 3.6, 2.6), metal, 0.10, "urban_detail")
    damage_facade = custom_mesh(
        "SM_Urban_DamagedFacade_A",
        [(-0.3, -4.0, -7.0), (-0.3, 4.0, -7.0), (-0.3, 4.0, 7.0),
         (-0.3, 1.0, 4.0), (-0.3, -0.8, 6.0), (-0.3, -4.0, 7.0),
         (0.3, -4.0, -7.0), (0.3, 4.0, -7.0), (0.3, 4.0, 7.0),
         (0.3, 1.0, 4.0), (0.3, -0.8, 6.0), (0.3, -4.0, 7.0)],
        [(0, 1, 2, 3, 4, 5), (6, 11, 10, 9, 8, 7), (0, 6, 7, 1),
         (1, 7, 8, 2), (2, 8, 9, 3), (3, 9, 10, 4), (4, 10, 11, 5), (5, 11, 6, 0)],
        concrete, "urban_damage", "box", 0.03,
    )

    # Lighthouse and radar landmarks.
    lighthouse_tower = cylinder("SM_Landmark_LighthouseTower_A", 2.7, 22.0, plaster, 64, role="landmark")
    lighthouse_gallery = cylinder("SM_Landmark_LighthouseGallery_A", 3.6, 0.65, metal, 64, role="landmark")
    lighthouse_lantern = cylinder("SM_Landmark_LighthouseLantern_A", 2.15, 3.0, glass, 48, role="landmark", collision="box")
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=2.8, radius2=0.25, depth=2.4)
    lighthouse_roof = bpy.context.object
    lighthouse_roof.name = "SM_Landmark_LighthouseRoof_A"
    finish_mesh(lighthouse_roof, red, 0.05, "convex", "landmark")
    radar_bunker = cube("SM_Landmark_RadarPost_Bunker_A", (10.0, 8.0, 4.0), concrete, 0.18, "landmark")
    radar_mast = cylinder("SM_Landmark_RadarPost_Mast_A", 0.42, 14.0, metal, 32, role="landmark")
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32)
    radar_dish = bpy.context.object
    radar_dish.name = "SM_Landmark_RadarPost_Dish_A"
    radar_dish.scale = (0.55, 4.2, 2.8)
    finish_mesh(radar_dish, radar, 0.02, "convex", "landmark")
    radar_array = cube("SM_Landmark_RadarPost_AntennaArray_A", (0.6, 6.8, 1.2), radar, 0.06, "landmark")
    set_origin(radar_dish, (0.0, 0.0, 0.0))
    radar_dish["SKG_PivotRole"] = "radar_azimuth_elevation"

    # Pathfinder boss, weak points and bounded damage pieces.
    boss_body = make_pathfinder_body("SM_Boss_Pathfinder_Body", boss_paint)
    boss_damaged = make_pathfinder_body("SM_Boss_Pathfinder_Body_Damaged", boss_paint, True)
    antenna = cylinder("SM_Boss_Pathfinder_CommandAntenna", 0.055, 1.05, boss_metal, 24, role="boss_weakpoint", collision="capsule")
    camera = sphere("SM_Boss_Pathfinder_NoseCamera", (0.23, 0.20, 0.20), glass, "boss_weakpoint", "sphere")
    engine = cylinder("SM_Boss_Pathfinder_Engine", 0.38, 0.78, hot, 48, (0.0, math.radians(90.0), 0.0), "boss_weakpoint", "capsule")
    linkage = cube("SM_Boss_Pathfinder_ControlLinkage", (0.65, 0.16, 0.14), boss_metal, 0.025, "boss_weakpoint", "box")
    chunk_l = custom_mesh("SM_Boss_Pathfinder_BreakChunk_L", [(0,0,0),(1.4,-1.4,0),(0.5,-2.2,0),(0.1,-0.4,0.3)], [(0,1,2),(0,3,1),(1,3,2),(2,3,0)], boss_paint, "boss_debris", "convex", 0.015)
    chunk_r = custom_mesh("SM_Boss_Pathfinder_BreakChunk_R", [(0,0,0),(1.4,1.4,0),(0.5,2.2,0),(0.1,0.4,0.3)], [(0,2,1),(0,1,3),(1,2,3),(2,0,3)], boss_paint, "boss_debris", "convex", 0.015)
    chunk_engine = cylinder("SM_Boss_Pathfinder_BreakChunk_Engine", 0.31, 0.45, boss_metal, 32, (0.0, math.radians(90.0), 0.0), "boss_debris", "capsule")
    for weak, weak_id, pivot_role in [
        (antenna, "CommandAntenna", "breakaway_base"),
        (camera, "NoseCamera", "camera_gimbal"),
        (engine, "Engine", "engine_mount"),
        (linkage, "ControlLinkage", "control_hinge"),
    ]:
        weak["SKG_WeakPointId"] = weak_id
        weak["SKG_PivotRole"] = pivot_role
        set_origin(weak, (0.0, 0.0, 0.0))

    # Preview composition manifest. Meshes remain authored at local origin.
    place(beach_a, (0, 0, 0), mission_role="shoreline")
    place(beach_b, (31, 1, 0.2), mission_role="shoreline")
    place(dune_a, (-8, 1, 1.0), mission_role="terrain")
    place(dune_b, (18, -3, 0.8), mission_role="terrain")
    place(seawall, (0, 10, 2.0), mission_role="coast_boundary")
    place(seawall_corner, (17, 10, 2.0), mission_role="coast_boundary")
    place(road, (0, 18, 1.0), mission_role="flight_route_landmark")
    place(promenade, (0, 12.8, 1.1), mission_role="promenade")
    for x in (-13, 0, 13):
        place(groyne, (x, -7.0, 0.5), mission_role="shore_detail")
    place(drain, (7, 9.8, 1.0), (math.radians(90), 0, 0), mission_role="shore_detail")

    building_specs = [
        (apt_a, (-17, 24, 9.6)), (apt_b, (-4, 25, 7.6)),
        (mid_a, (10, 25, 12.6)), (mid_b, (25, 24, 10.6)),
    ]
    for index, (building, loc) in enumerate(building_specs):
        place(building, loc, mission_role="urban_skyline")
        detail_x = loc[0] - building.dimensions.x * 0.51
        place(windows, (detail_x, loc[1], loc[2]), scale=(1, 1, 1), mission_role="facade_detail")
        if index < 3:
            place(balcony, (detail_x - 0.2, loc[1], loc[2]), mission_role="facade_detail")
    place(entrance, (-23.2, 24, 2.2), mission_role="facade_detail")
    place(roof_service, (10, 25, 25.8), mission_role="roof_detail")
    place(damage_facade, (24.4, 19.0, 10.6), mission_role="damage_state")

    place(lighthouse_tower, (-23, -3, 11.5), mission_role="hero_landmark")
    place(lighthouse_gallery, (-23, -3, 22.7), mission_role="hero_landmark")
    place(lighthouse_lantern, (-23, -3, 24.4), mission_role="hero_landmark")
    place(lighthouse_roof, (-23, -3, 27.0), mission_role="hero_landmark")
    place(radar_bunker, (26, 8, 2.5), mission_role="defended_objective")
    place(radar_mast, (26, 8, 11.0), mission_role="defended_objective")
    place(radar_dish, (26, 8, 18.2), rotation=(0, math.radians(-18), math.radians(22)), mission_role="defended_objective")
    place(radar_array, (26, 8, 15.5), mission_role="defended_objective")

    boss_origin = (8.0, 4.0, 7.0)
    place(boss_body, boss_origin, rotation=(0, 0, math.radians(8)), mission_role="boss_intact")
    place(antenna, (8.2, 4.0, 7.8), mission_role="boss_weakpoint")
    place(camera, (10.0, 4.0, 7.0), mission_role="boss_weakpoint")
    place(engine, (6.2, 4.0, 7.0), rotation=(0, math.radians(90), 0), mission_role="boss_heat_lock")
    place(linkage, (7.5, 4.0, 7.3), mission_role="boss_finish")

    # Preview duplicates retain local source meshes and do not enter the export.
    preview_collection = bpy.data.collections.new("PREVIEW_M01")
    bpy.context.scene.collection.children.link(preview_collection)
    preview_objects = []
    by_name = {obj.name: obj for obj in assets}
    for index, spec in enumerate(placements):
        source = by_name[spec["asset"]]
        preview = source.copy()
        preview.data = source.data
        preview.name = f"PREVIEW_{index:03d}_{source.name}"
        preview.location = spec["location_m"]
        preview.rotation_euler = [math.radians(v) for v in spec["rotation_deg"]]
        preview.scale = spec["scale"]
        preview_collection.objects.link(preview)
        preview_objects.append(preview)

    renders = render_proofs(preview_objects)

    # Export source assets only. Preview instances, lights and cameras are excluded.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in assets:
        obj.hide_render = False
        obj.select_set(True)
    bpy.context.view_layer.objects.active = assets[0]
    bpy.ops.export_scene.gltf(
        filepath=str(EXPORT_GLB),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
    )
    for obj in assets:
        obj.hide_render = True

    manifest = {
        "schema": "skyguard.m01.wave1.assets.v1",
        "coordinate_contract": "+X forward, +Z up, meters",
        "asset_count": len(assets),
        "assets": [
            {
                "name": obj.name,
                "role": obj.get("SKG_AssetRole"),
                "collision": obj.get("SKG_CollisionContract"),
                "uv_layer": obj.get("SKG_UVLayer"),
                "pivot_role": obj.get("SKG_PivotRole"),
                "weak_point_id": obj.get("SKG_WeakPointId"),
                "dimensions_m": [round(float(v), 4) for v in obj.dimensions],
            }
            for obj in sorted(assets, key=lambda item: item.name)
        ],
        "placements": placements,
        "collision_contracts": collision_contracts,
        "boss": {
            "name": "Pathfinder",
            "body": boss_body.name,
            "damaged_body": boss_damaged.name,
            "weak_points": [antenna.name, camera.name, engine.name, linkage.name],
            "breakup_pool": [chunk_l.name, chunk_r.name, chunk_engine.name],
            "rifle_then_igla_then_rifle": True,
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    bpy.ops.wm.save_as_mainfile(filepath=str(MASTER_BLEND))

    glb_bytes = EXPORT_GLB.read_bytes()
    report = {
        "schema": "skyguard.m01.wave1.blender-report.v1",
        "master_blend": str(MASTER_BLEND),
        "export_glb": str(EXPORT_GLB),
        "export_glb_bytes": len(glb_bytes),
        "export_glb_sha256": hashlib.sha256(glb_bytes).hexdigest(),
        "asset_count": len(assets),
        "uv_complete": sum(
            1 for obj in assets if obj.data.uv_layers.get(UV_NAME) is not None
        ),
        "collision_contract_count": len(collision_contracts),
        "placement_count": len(placements),
        "boss_weak_point_count": 4,
        "boss_breakup_piece_count": 3,
        "renders": renders,
        "gate": "PASS" if all(
            obj.data.uv_layers.get(UV_NAME) is not None for obj in assets
        ) else "FAIL",
        "promotion": "wave1_candidate_not_final_aaa_acceptance",
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("[SkyguardM01] " + json.dumps(report))


if __name__ == "__main__":
    main()
