"""Build the Mission 01 Wave 1 AAA-refinement candidate.

This script is deliberately separate from the Wave 1 blockout.  It authors a
denser coastal/urban/landmark kit and a mechanically readable Pathfinder boss,
then writes a native Blender master, Unreal-importable GLB, manifest, report,
and visual proof renders.

Contract:
* Blender metres, +X forward, +Z up.
* Every exported object remains at local origin with applied scale.
* Gameplay pivots, collision intent and semantic roles are custom properties.
* Boss breakup is a bounded, pre-authored pool (never runtime fracture).
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
SOURCE_DIR = ROOT / "Content" / "Skyguard" / "Meshes" / "Source" / "Mission01" / "Wave1_Refinement"
REPORT_DIR = ROOT / "Saved" / "Reports"
SCREEN_DIR = ROOT / "Saved" / "Screenshots" / "Mission01_Wave1_Refinement"
MASTER_BLEND = SOURCE_DIR / "M01_WAVE1_AAA_REFINEMENT_MASTER.blend"
EXPORT_GLB = SOURCE_DIR / "m01_wave1_aaa_refinement.glb"
MANIFEST_PATH = REPORT_DIR / "M01_WAVE1_AAA_REFINEMENT_MANIFEST.json"
REPORT_PATH = REPORT_DIR / "M01_WAVE1_AAA_REFINEMENT_REPORT.json"
UV_NAME = "UV_M01_AAA_0"

assets: list[bpy.types.Object] = []
placements: list[dict] = []
materials: dict[str, bpy.types.Material] = {}


def mat(name: str, color, roughness=0.65, metallic=0.0, noise=0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if noise:
        tex = material.node_tree.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = noise
        tex.inputs["Detail"].default_value = 5.0
        tex.inputs["Roughness"].default_value = 0.7
        ramp = material.node_tree.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.28
        ramp.color_ramp.elements[1].position = 0.76
        ramp.color_ramp.elements[0].color = (*tuple(c * 0.58 for c in color), 1.0)
        ramp.color_ramp.elements[1].color = (*tuple(min(1.0, c * 1.25) for c in color), 1.0)
        bump = material.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.18
        bump.inputs["Distance"].default_value = 0.035
        material.node_tree.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        material.node_tree.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        material.node_tree.links.new(tex.outputs["Fac"], bump.inputs["Height"])
        material.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    materials[name] = material
    return material


def configure_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 80
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("M01_AAA_Refinement_World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.025, 0.055, 0.085, 1.0)
    bg.inputs["Strength"].default_value = 0.42
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass


def select_only(objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def cube_part(name, dims, material, location=(0, 0, 0), bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new("EdgeChamfer", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        mod.limit_method = "ANGLE"
        select_only([obj])
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def rotated_cube_part(name, dims, material, location=(0, 0, 0), rotation=(0, 0, 0), bevel=0.03):
    obj = cube_part(name, dims, material, location, bevel)
    obj.rotation_euler = rotation
    return obj


def cyl_part(name, radius, depth, material, location=(0, 0, 0), rotation=(0, 0, 0), vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def sphere_part(name, scale, material, location=(0, 0, 0), subdivisions=3):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj


def custom_part(name, vertices, faces, material):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def finalize(parts, name, role, collision, pivot_role="center", nanite=True, damage_state="intact"):
    select_only(parts)
    if len(parts) > 1:
        bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    # Bake authored offsets into the mesh while returning the exported asset to
    # a deterministic zero-origin, identity-scale transform.
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    select_only([obj])
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.015)
    bpy.ops.object.mode_set(mode="OBJECT")
    if obj.data.uv_layers.active:
        obj.data.uv_layers.active.name = UV_NAME
    for poly in obj.data.polygons:
        poly.use_smooth = False
    obj["SKG_AssetRole"] = role
    obj["SKG_CollisionContract"] = collision
    obj["SKG_PivotRole"] = pivot_role
    obj["SKG_UVLayer"] = UV_NAME
    obj["SKG_ForwardAxis"] = "+X"
    obj["SKG_Units"] = "meters"
    obj["SKG_NaniteCandidate"] = bool(nanite)
    obj["SKG_DamageState"] = damage_state
    assets.append(obj)
    return obj


def place(obj, location, rotation=(0, 0, 0), scale=(1, 1, 1), role="dressing"):
    placements.append(
        {
            "asset": obj.name,
            "location_m": [round(float(v), 4) for v in location],
            "rotation_deg": [round(math.degrees(float(v)), 3) for v in rotation],
            "scale": [round(float(v), 4) for v in scale],
            "mission_role": role,
        }
    )


def make_beach(name="SM_M01_Coast_Beach_Detailed_A"):
    verts = []
    faces = []
    x_count, y_count = 17, 9
    for x in range(x_count):
        px = -24.0 + x * 3.0
        for y in range(y_count):
            py = -10.0 + y * 2.5
            shore = (py + 10.0) / 20.0
            pz = 0.10 + 0.55 * shore + 0.13 * math.sin(x * 0.88 + y * 0.31)
            verts.append((px, py, pz))
    for x in range(x_count - 1):
        for y in range(y_count - 1):
            a = x * y_count + y
            faces.append((a, a + y_count, a + y_count + 1, a + 1))
    top = custom_part(name + "_surface", verts, faces, materials["sand"])
    under = cube_part(name + "_foundation", (48, 20, 0.8), materials["sand_dark"], (0, 0, -0.35), 0.0)
    return finalize([top, under], name, "coastal_terrain", "complex_as_simple", "tile_center")


def make_seawall():
    parts = [
        cube_part("wall", (24, 1.4, 3.8), materials["concrete"], (0, 0, 1.9), 0.08),
        cube_part("cap", (24.3, 1.8, 0.28), materials["concrete_light"], (0, 0, 3.93), 0.04),
    ]
    for x in (-9, -3, 3, 9):
        parts.append(cube_part("buttress", (0.55, 1.1, 3.2), materials["concrete_dark"], (x, -1.1, 1.6), 0.03))
    for rung in range(7):
        parts.append(cyl_part("ladder", 0.035, 0.62, materials["steel"], (8.8, -0.86, 0.7 + rung * 0.42), (math.pi / 2, 0, 0), 16))
    parts.extend([
        cyl_part("rail_l", 0.05, 3.1, materials["steel"], (8.48, -0.86, 2.0), vertices=16),
        cyl_part("rail_r", 0.05, 3.1, materials["steel"], (9.12, -0.86, 2.0), vertices=16),
    ])
    return finalize(parts, "SM_M01_Coast_Seawall_Detailed_A", "coastal_structure", "box", "segment_center")


def make_road_transition():
    parts = [
        cube_part("road", (30, 9, 0.28), materials["asphalt"], (0, 0, 0.14), 0.025),
        cube_part("curb_l", (30, 0.42, 0.38), materials["concrete_light"], (0, -4.65, 0.25), 0.035),
        cube_part("curb_r", (30, 0.42, 0.38), materials["concrete_light"], (0, 4.65, 0.25), 0.035),
    ]
    for x in range(-13, 14, 4):
        parts.append(cube_part("line", (2.1, 0.12, 0.018), materials["road_mark"], (x, 0, 0.30), 0.0))
    return finalize(parts, "SM_M01_Road_CoastalTransition_Detailed_A", "road", "box", "segment_center")


def make_promenade():
    parts = [
        cube_part("deck", (30, 5.2, 0.45), materials["paving"], (0, 0, 0.225), 0.045),
        cube_part("edge", (30, 0.3, 0.65), materials["concrete_light"], (0, -2.7, 0.45), 0.035),
    ]
    for x in range(-14, 15, 2):
        parts.append(cube_part("joint", (0.045, 5.0, 0.012), materials["concrete_dark"], (x, 0, 0.457), 0))
    for x in range(-13, 14, 4):
        parts.append(cyl_part("bollard", 0.12, 0.9, materials["steel"], (x, -2.2, 0.9), vertices=20))
    return finalize(parts, "SM_M01_Coast_Promenade_Detailed_A", "promenade", "box", "segment_center")


def make_building(name, size, floors, bays, palette="warm", damaged=False):
    width, depth, height = size
    wall = materials["plaster_warm" if palette == "warm" else "plaster_cool"]
    parts = [cube_part("shell", size, wall, (0, 0, height / 2), 0.10)]
    floor_h = height / floors
    bay_w = depth / bays
    facade_x = -width / 2 - 0.035
    for floor in range(floors):
        z = 1.25 + floor * floor_h
        for bay in range(bays):
            y = -depth / 2 + bay_w * (bay + 0.5)
            if damaged and floor >= floors - 2 and bay in (1, 2):
                continue
            parts.append(cube_part("window_reveal", (0.14, bay_w * 0.56, floor_h * 0.48), materials["window"], (facade_x, y, z), 0.018))
            if floor > 0 and bay % 2 == 0:
                parts.append(cube_part("balcony_slab", (0.72, bay_w * 0.82, 0.13), materials["concrete_light"], (facade_x - 0.30, y, z - floor_h * 0.32), 0.025))
                parts.append(cube_part("balcony_rail", (0.08, bay_w * 0.72, 0.62), materials["steel"], (facade_x - 0.66, y, z - floor_h * 0.05), 0.018))
    parts.append(cube_part("entrance", (0.22, 1.7, 2.55), materials["door"], (facade_x - 0.02, 0, 1.28), 0.04))
    parts.append(cube_part("parapet_f", (0.35, depth, 0.72), wall, (-width / 2 + 0.18, 0, height + 0.36), 0.035))
    parts.append(cube_part("parapet_b", (0.35, depth, 0.72), wall, (width / 2 - 0.18, 0, height + 0.36), 0.035))
    parts.append(cube_part("roof_plant", (3.2, 2.4, 1.4), materials["steel_dark"], (1.2, 0, height + 0.72), 0.07))
    if damaged:
        parts.append(custom_part(
            "broken_slab",
            [(-width / 2 - .08, -depth / 2, height * .68), (-width / 2 - .08, depth / 2, height * .68),
             (-width / 2 - .08, depth / 2, height), (-width / 2 - .55, .7, height * .86),
             (-width / 2 - .40, -.8, height * .79), (-width / 2 - .08, -depth / 2, height)],
            [(0, 1, 2, 3, 4, 5)], materials["damage"]))
    return finalize(parts, name, "urban_module", "box", "ground_center", True, "damaged" if damaged else "intact")


def make_lighthouse():
    parts = [
        cyl_part("tower_lower", 3.2, 6.0, materials["lighthouse_white"], (0, 0, 3), vertices=64),
        cyl_part("tower_mid", 2.75, 7.0, materials["lighthouse_white"], (0, 0, 9.5), vertices=64),
        cyl_part("tower_upper", 2.25, 7.0, materials["lighthouse_white"], (0, 0, 16.5), vertices=64),
        cyl_part("stripe_1", 2.88, 2.2, materials["lighthouse_red"], (0, 0, 8.0), vertices=64),
        cyl_part("stripe_2", 2.38, 2.0, materials["lighthouse_red"], (0, 0, 15.0), vertices=64),
        cyl_part("gallery", 3.35, 0.42, materials["steel"], (0, 0, 20.25), vertices=64),
        cyl_part("lantern", 1.82, 2.5, materials["glass"], (0, 0, 21.7), vertices=48),
    ]
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=2.25, radius2=0.18, depth=2.0, location=(0, 0, 24.0))
    roof = bpy.context.object
    roof.data.materials.append(materials["lighthouse_red"])
    parts.append(roof)
    for i in range(20):
        a = i * math.tau / 20
        parts.append(cyl_part("rail_post", 0.035, 1.05, materials["steel"], (3.05 * math.cos(a), 3.05 * math.sin(a), 20.9), vertices=12))
    return finalize(parts, "SM_M01_Landmark_Lighthouse_Hero_A", "hero_landmark", "complex_as_simple", "base_center", True)


def make_radar():
    parts = [
        cube_part("bunker", (10, 8, 4.2), materials["concrete"], (0, 0, 2.1), 0.18),
        cube_part("blast_door", (0.18, 2.7, 2.9), materials["door"], (-5.09, 0, 1.55), 0.04),
        cyl_part("mast", 0.38, 12.0, materials["steel"], (0, 0, 10.2), vertices=32),
        cyl_part("turntable", 1.2, 0.55, materials["steel_dark"], (0, 0, 16.3), vertices=48),
    ]
    # Readable open-grid mast.
    for z in (5.1, 8.1, 11.1, 14.1):
        parts.append(cube_part("cross_x", (2.0, 0.14, 0.14), materials["steel"], (0, 0, z), 0.01))
        parts.append(cube_part("cross_y", (0.14, 2.0, 0.14), materials["steel"], (0, 0, z), 0.01))
    # Parabolic dish as layered shallow shells, with rear support.
    for radius, x in ((3.2, 0), (2.45, 0.12), (1.65, 0.22)):
        bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=0.065, major_segments=64, minor_segments=10, location=(0, 0, 17.0), rotation=(0, math.radians(76), 0))
        torus = bpy.context.object
        torus.data.materials.append(materials["radar"])
        parts.append(torus)
    parts += [
        cube_part("dish_spine", (0.20, 6.5, 0.20), materials["radar"], (0, 0, 17.0), 0.02),
        cube_part("dish_spine_2", (0.20, 0.20, 5.3), materials["radar"], (0, 0, 17.0), 0.02),
        cyl_part("feed_arm", 0.06, 2.3, materials["steel"], (-1.0, 0, 17.0), (0, math.pi / 2, 0), 16),
        sphere_part("feed", (.22, .22, .22), materials["radar_dark"], (-2.15, 0, 17.0), 2),
    ]
    return finalize(parts, "SM_M01_Landmark_RadarPost_Hero_A", "defended_objective", "complex_as_simple", "base_center", True)


def make_pathfinder_body(name, damaged=False):
    parts = []
    # Low observable delta planform with an actual central fuselage volume.
    verts_top = [
        (2.65, 0, 0.04), (0.75, -3.05, 0), (-1.25, -1.68, 0), (-2.35, -.55, 0),
        (-2.35, .55, 0), (-1.25, 1.68, 0), (.75, 3.05, 0),
        (1.25, 0, .38), (.15, -.62, .32), (-1.6, -.42, .21),
        (-1.6, .42, .21), (.15, .62, .32),
        (1.25, 0, -.22), (.15, -.58, -.18), (-1.6, -.38, -.13),
        (-1.6, .38, -.13), (.15, .58, -.18),
    ]
    faces = [
        (0,1,2,3,4,5,6), (0,7,8,1), (1,8,9,2), (2,9,3),
        (0,6,11,7), (6,5,10,11), (5,4,10), (7,11,10,9,8),
        (9,10,4,3), (0,12,13,1), (1,13,14,2), (2,14,3),
        (0,6,16,12), (6,5,15,16), (5,4,15), (12,16,15,14,13),
        (14,15,4,3),
    ]
    parts.append(custom_part("airframe", verts_top, faces, materials["boss_paint"]))
    # Panel seams as real geometry to preserve readability at medium distance.
    parts += [
        cube_part("center_spine", (2.8, .07, .045), materials["boss_edge"], (-.2, 0, .39), .01),
        cube_part("panel_l", (1.75, .035, .035), materials["boss_edge"], (.15, -1.23, .12), .006),
        cube_part("panel_r", (1.75, .035, .035), materials["boss_edge"], (.15, 1.23, .12), .006),
        cube_part("service_hatch", (.80, .62, .035), materials["boss_dark"], (-.72, 0, .34), .035),
        cyl_part("exhaust_l", .17, .43, materials["heat"], (-1.70, -.52, -.02), (0, math.pi / 2, 0), 32),
        cyl_part("exhaust_r", .17, .43, materials["heat"], (-1.70, .52, -.02), (0, math.pi / 2, 0), 32),
        cube_part("elevon_l", (1.18, 1.02, .07), materials["boss_edge"], (-1.45, -1.22, -.04), .02),
        cube_part("elevon_r", (1.18, 1.02, .07), materials["boss_edge"], (-1.45, 1.22, -.04), .02),
        rotated_cube_part("tail_fin_l", (.65, .08, .58), materials["boss_edge"], (-1.68, -.62, .42), (0, math.radians(-17), math.radians(5)), .015),
        rotated_cube_part("tail_fin_r", (.65, .08, .58), materials["boss_edge"], (-1.68, .62, .42), (0, math.radians(-17), math.radians(-5)), .015),
        rotated_cube_part("leading_edge_l", (2.75, .065, .07), materials["boss_edge"], (.08, -1.55, .06), (0, 0, math.radians(-31)), .008),
        rotated_cube_part("leading_edge_r", (2.75, .065, .07), materials["boss_edge"], (.08, 1.55, .06), (0, 0, math.radians(31)), .008),
    ]
    if damaged:
        parts += [
            custom_part("tear_l", [(-1.4,-1.3,.22),(-.25,-2.0,.08),(-.9,-.85,.38),(-1.5,-.45,.2)], [(0,1,2),(0,2,3)], materials["damage"]),
            cube_part("scorch", (1.35,.78,.04), materials["soot"], (-.55,0,.37), .015),
        ]
    obj = finalize(parts, name, "boss_body", "convex_decomposition", "center_of_mass", True, "critical" if damaged else "intact")
    obj["SKG_MassClass"] = "heavy_uav"
    return obj


def make_pathfinder_weakpoints():
    antenna_parts = [
        cyl_part("antenna_base", .13, .18, materials["boss_dark"], (0,0,.09), vertices=24),
        cyl_part("antenna_whip", .035, .92, materials["steel"], (0,0,.62), vertices=16),
        sphere_part("antenna_cap", (.07,.07,.07), materials["warning"], (0,0,1.09), 2),
    ]
    antenna = finalize(antenna_parts, "SM_Boss_Pathfinder_CommandAntenna_AAA", "boss_weakpoint", "capsule", "breakaway_base", False)
    camera_parts = [
        sphere_part("camera_housing", (.28,.24,.24), materials["boss_dark"]),
        sphere_part("camera_lens", (.12,.07,.12), materials["glass"], (.245,0,0), 3),
        cyl_part("gimbal", .07, .62, materials["steel"], (0,0,0), (math.pi/2,0,0), 20),
    ]
    camera = finalize(camera_parts, "SM_Boss_Pathfinder_NoseCamera_AAA", "boss_weakpoint", "sphere", "camera_gimbal", False)
    engine_parts = [
        cyl_part("engine_case", .43, .84, materials["boss_dark"], rotation=(0,math.pi/2,0), vertices=48),
        cyl_part("engine_hot", .31, .87, materials["heat"], rotation=(0,math.pi/2,0), vertices=48),
    ]
    for i in range(8):
        a = i * math.tau / 8
        engine_parts.append(cube_part("fin", (.72,.035,.16), materials["steel"], (0,.33*math.cos(a),.33*math.sin(a)), .008))
    engine = finalize(engine_parts, "SM_Boss_Pathfinder_Engine_AAA", "boss_weakpoint", "capsule", "engine_mount", False)
    linkage_parts = [
        cube_part("link", (.78,.16,.12), materials["steel"], (0,0,0), .025),
        cyl_part("hinge_a", .12, .24, materials["boss_dark"], (-.39,0,0), (math.pi/2,0,0), 24),
        cyl_part("hinge_b", .12, .24, materials["boss_dark"], (.39,0,0), (math.pi/2,0,0), 24),
    ]
    linkage = finalize(linkage_parts, "SM_Boss_Pathfinder_ControlLinkage_AAA", "boss_weakpoint", "box", "control_hinge", False)
    for obj, weak_id, weapon in [
        (antenna, "CommandAntenna", "rifle"),
        (camera, "NoseCamera", "rifle"),
        (engine, "Engine", "igla"),
        (linkage, "ControlLinkage", "rifle"),
    ]:
        obj["SKG_WeakPointId"] = weak_id
        obj["SKG_RequiredWeapon"] = weapon
    return antenna, camera, engine, linkage


def make_debris():
    pieces = []
    specs = [
        ("Wing_L", [(0,0,0),(1.55,-1.6,0),(.35,-2.35,0),(-.25,-.4,.26)]),
        ("Wing_R", [(0,0,0),(.35,2.35,0),(1.55,1.6,0),(-.25,.4,.26)]),
        ("Spine", [(-.75,-.34,-.12),(.85,-.26,-.08),(.65,.30,.25),(-.85,.38,.20)]),
    ]
    for suffix, verts in specs:
        part = custom_part(suffix, verts, [(0,1,2),(0,2,3),(0,3,1),(1,3,2)], materials["boss_paint"])
        pieces.append(finalize([part], f"SM_Boss_Pathfinder_BreakChunk_{suffix}_AAA", "boss_debris", "convex", "center_of_mass", False, "detached"))
    core_parts = [
        cyl_part("core", .32, .48, materials["boss_dark"], rotation=(0,math.pi/2,0), vertices=32),
        cyl_part("hot_ring", .34, .08, materials["heat"], (.24,0,0), (0,math.pi/2,0), 32),
    ]
    pieces.append(finalize(core_parts, "SM_Boss_Pathfinder_BreakChunk_Engine_AAA", "boss_debris", "capsule", "center_of_mass", False, "detached"))
    return pieces


def preview_instances():
    collection = bpy.data.collections.new("PREVIEW_M01_AAA")
    bpy.context.scene.collection.children.link(collection)
    lookup = {obj.name: obj for obj in assets}
    previews = []
    for i, spec in enumerate(placements):
        src = lookup[spec["asset"]]
        dup = src.copy()
        dup.data = src.data
        dup.name = f"PREVIEW_{i:03d}_{src.name}"
        dup.location = spec["location_m"]
        dup.rotation_euler = [math.radians(v) for v in spec["rotation_deg"]]
        dup.scale = spec["scale"]
        collection.objects.link(dup)
        previews.append(dup)
    return previews


def add_camera(name, location, target, lens=55):
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.object
    cam.name = name
    cam.data.lens = lens
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    return cam


def render_proofs(previews):
    for source in assets:
        source.hide_render = True
    bpy.ops.object.light_add(type="SUN", location=(0,0,30))
    sun = bpy.context.object
    sun.data.energy = 2.8
    sun.rotation_euler = (math.radians(28), math.radians(-16), math.radians(-34))
    bpy.ops.object.light_add(type="AREA", location=(18,-22,20))
    bpy.context.object.data.energy = 1600
    bpy.context.object.data.shape = "DISK"
    bpy.context.object.data.size = 12
    bpy.ops.object.light_add(type="AREA", location=(-18,10,11))
    bpy.context.object.data.energy = 900
    bpy.context.object.data.size = 10
    cameras = [
        ("CoastalVerticalSlice", (-64,-72,43), (2,13,8), 48),
        ("ArchitectureLandmarks", (58,-58,38), (0,13,10), 52),
        ("PathfinderQuarter", (18,-16,13.0), (8,2,7), 58),
        ("PathfinderTop", (13,-7,20), (8,2,7), 62),
    ]
    outputs = []
    for label, position, target, lens in cameras:
        for obj in previews:
            boss = "Boss_Pathfinder" in obj.name
            if label.startswith("Pathfinder"):
                obj.hide_render = not boss
            else:
                obj.hide_render = boss
        cam = add_camera("CAM_" + label, position, target, lens)
        bpy.context.scene.camera = cam
        path = SCREEN_DIR / f"M01_AAA_{label}.png"
        bpy.context.scene.render.filepath = str(path)
        started = time.perf_counter()
        bpy.ops.render.render(write_still=True)
        outputs.append({"label": label, "path": str(path), "bytes": path.stat().st_size, "render_seconds": round(time.perf_counter()-started, 2)})
    return outputs


def main():
    started = time.perf_counter()
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    SCREEN_DIR.mkdir(parents=True, exist_ok=True)
    configure_scene()

    # PBR-calibrated material intent. Procedural microdetail is for source/proof;
    # Unreal receives stable material slot names for production master materials.
    mat("M_M01_Sand", (.48,.35,.20), .91, 0, 8); materials["sand"] = materials["M_M01_Sand"]
    mat("M_M01_SandDark", (.31,.22,.12), .94, 0, 12); materials["sand_dark"] = materials["M_M01_SandDark"]
    mat("M_M01_Concrete", (.31,.32,.30), .82, 0, 19); materials["concrete"] = materials["M_M01_Concrete"]
    mat("M_M01_ConcreteLight", (.48,.49,.45), .78, 0, 15); materials["concrete_light"] = materials["M_M01_ConcreteLight"]
    mat("M_M01_ConcreteDark", (.18,.20,.19), .88, 0, 24); materials["concrete_dark"] = materials["M_M01_ConcreteDark"]
    mat("M_M01_Asphalt", (.035,.042,.044), .95, 0, 32); materials["asphalt"] = materials["M_M01_Asphalt"]
    mat("M_M01_RoadMark", (.82,.76,.48), .72, 0); materials["road_mark"] = materials["M_M01_RoadMark"]
    mat("M_M01_Paving", (.39,.37,.33), .84, 0, 22); materials["paving"] = materials["M_M01_Paving"]
    mat("M_M01_Steel", (.12,.14,.14), .45, .74, 30); materials["steel"] = materials["M_M01_Steel"]
    mat("M_M01_SteelDark", (.045,.052,.053), .39, .82, 36); materials["steel_dark"] = materials["M_M01_SteelDark"]
    mat("M_M01_PlasterWarm", (.51,.46,.36), .78, 0, 16); materials["plaster_warm"] = materials["M_M01_PlasterWarm"]
    mat("M_M01_PlasterCool", (.40,.46,.47), .80, 0, 17); materials["plaster_cool"] = materials["M_M01_PlasterCool"]
    mat("M_M01_Window", (.025,.10,.14), .20, .10); materials["window"] = materials["M_M01_Window"]
    mat("M_M01_Door", (.025,.12,.24), .48, .22, 20); materials["door"] = materials["M_M01_Door"]
    mat("M_M01_Damage", (.17,.12,.09), .94, 0, 25); materials["damage"] = materials["M_M01_Damage"]
    mat("M_M01_LighthouseWhite", (.70,.71,.66), .64, 0, 12); materials["lighthouse_white"] = materials["M_M01_LighthouseWhite"]
    mat("M_M01_LighthouseRed", (.48,.025,.018), .48, .12, 12); materials["lighthouse_red"] = materials["M_M01_LighthouseRed"]
    mat("M_M01_Glass", (.025,.11,.15), .16, .12); materials["glass"] = materials["M_M01_Glass"]
    mat("M_M01_Radar", (.20,.25,.18), .60, .32, 18); materials["radar"] = materials["M_M01_Radar"]
    mat("M_M01_RadarDark", (.07,.09,.065), .52, .44, 24); materials["radar_dark"] = materials["M_M01_RadarDark"]
    mat("M_Boss_Pathfinder_Paint_AAA", (.11,.135,.105), .55, .38, 42); materials["boss_paint"] = materials["M_Boss_Pathfinder_Paint_AAA"]
    mat("M_Boss_Pathfinder_Edge_AAA", (.035,.045,.04), .42, .76, 42); materials["boss_edge"] = materials["M_Boss_Pathfinder_Edge_AAA"]
    mat("M_Boss_Pathfinder_Dark_AAA", (.022,.028,.026), .36, .86, 50); materials["boss_dark"] = materials["M_Boss_Pathfinder_Dark_AAA"]
    mat("M_Boss_Pathfinder_Heat_AAA", (.55,.07,.008), .26, .38, 25); materials["heat"] = materials["M_Boss_Pathfinder_Heat_AAA"]
    mat("M_Boss_Pathfinder_Soot_AAA", (.018,.012,.009), .98, 0, 36); materials["soot"] = materials["M_Boss_Pathfinder_Soot_AAA"]
    mat("M_Boss_Pathfinder_Warning_AAA", (.85,.28,.015), .48, .10); materials["warning"] = materials["M_Boss_Pathfinder_Warning_AAA"]

    beach = make_beach()
    seawall = make_seawall()
    road = make_road_transition()
    promenade = make_promenade()
    apartment_a = make_building("SM_M01_Urban_Apartment_Detailed_A", (11.5,9.0,18.5), 6, 5, "warm")
    apartment_b = make_building("SM_M01_Urban_Apartment_Detailed_B", (9.5,8.2,15.0), 5, 4, "cool")
    midrise_a = make_building("SM_M01_Urban_Midrise_Detailed_A", (14.0,10.5,25.0), 8, 6, "cool")
    midrise_damaged = make_building("SM_M01_Urban_Midrise_Damaged_A", (12.5,9.5,22.0), 7, 5, "warm", True)
    lighthouse = make_lighthouse()
    radar = make_radar()
    body = make_pathfinder_body("SM_Boss_Pathfinder_Body_AAA")
    damaged_body = make_pathfinder_body("SM_Boss_Pathfinder_Body_Damaged_AAA", True)
    antenna, camera, engine, linkage = make_pathfinder_weakpoints()
    debris = make_debris()

    place(beach, (0,0,0), role="shoreline")
    place(seawall, (0,10,0), role="coast_boundary")
    place(promenade, (0,12.8,.25), role="promenade")
    place(road, (0,18,.55), role="flight_route_landmark")
    place(apartment_a, (-18,26,.7), role="urban_skyline")
    place(apartment_b, (-5,25,.7), role="urban_skyline")
    place(midrise_a, (10,26,.7), role="urban_skyline")
    place(midrise_damaged, (26,25,.7), role="urban_damage")
    place(lighthouse, (-24,-3,.6), role="hero_landmark")
    place(radar, (27,8,.6), role="defended_objective")
    boss_origin = (8,2,7)
    place(body, boss_origin, (0,0,math.radians(8)), role="boss_intact")
    place(antenna, (7.6,2,7.48), role="boss_weakpoint")
    place(camera, (10.53,2,7.02), role="boss_weakpoint")
    place(engine, (6.25,2,6.92), (0,math.pi/2,0), role="boss_heat_lock")
    place(linkage, (6.8,2,7.28), role="boss_finish")

    previews = preview_instances()
    renders = render_proofs(previews)

    # Export source assets only.
    select_only(assets)
    bpy.ops.export_scene.gltf(
        filepath=str(EXPORT_GLB),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_materials="EXPORT",
    )
    bpy.ops.wm.save_as_mainfile(filepath=str(MASTER_BLEND))

    asset_records = []
    for obj in sorted(assets, key=lambda item: item.name):
        triangles = sum(len(poly.vertices) - 2 for poly in obj.data.polygons)
        asset_records.append({
            "name": obj.name,
            "role": obj.get("SKG_AssetRole"),
            "collision": obj.get("SKG_CollisionContract"),
            "pivot_role": obj.get("SKG_PivotRole"),
            "uv_layer": obj.get("SKG_UVLayer"),
            "nanite_candidate": obj.get("SKG_NaniteCandidate"),
            "damage_state": obj.get("SKG_DamageState"),
            "weak_point_id": obj.get("SKG_WeakPointId"),
            "required_weapon": obj.get("SKG_RequiredWeapon"),
            "vertices": len(obj.data.vertices),
            "triangles": triangles,
            "material_slots": [slot.material.name for slot in obj.material_slots if slot.material],
            "dimensions_m": [round(float(v), 4) for v in obj.dimensions],
        })
    manifest = {
        "schema": "skyguard.m01.wave1.aaa-refinement.v2",
        "coordinate_contract": "+X forward, +Z up, metres; Unreal importer converts to centimetres",
        "source_master": str(MASTER_BLEND),
        "shipping_candidate": str(EXPORT_GLB),
        "asset_count": len(assets),
        "material_count": len(bpy.data.materials),
        "assets": asset_records,
        "placements": placements,
        "boss": {
            "name": "Pathfinder",
            "body": body.name,
            "damaged_body": damaged_body.name,
            "weak_points": [antenna.name, camera.name, engine.name, linkage.name],
            "breakup_pool": [obj.name for obj in debris],
            "interaction_sequence": ["rifle_antenna_camera", "igla_engine", "rifle_control_linkage"],
            "runtime_fracture": False,
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    glb_data = EXPORT_GLB.read_bytes()
    missing_uv = [obj.name for obj in assets if not obj.data.uv_layers.get(UV_NAME)]
    invalid_origin = [
        obj.name for obj in assets
        if max(abs(float(v)) for v in obj.location) > 0.0001
        or max(abs(float(v) - 1.0) for v in obj.scale) > 0.0001
    ]
    report = {
        "schema": "skyguard.m01.wave1.aaa-refinement.report.v2",
        "master_blend": str(MASTER_BLEND),
        "master_blend_bytes": MASTER_BLEND.stat().st_size,
        "export_glb": str(EXPORT_GLB),
        "export_glb_bytes": len(glb_data),
        "export_glb_sha256": hashlib.sha256(glb_data).hexdigest(),
        "asset_count": len(assets),
        "material_count": len(bpy.data.materials),
        "total_vertices": sum(r["vertices"] for r in asset_records),
        "total_triangles": sum(r["triangles"] for r in asset_records),
        "missing_uv": missing_uv,
        "invalid_local_transform": invalid_origin,
        "boss_weak_point_count": 4,
        "boss_breakup_piece_count": len(debris),
        "proof_renders": renders,
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "gate": "PASS" if not missing_uv and not invalid_origin and len(debris) == 4 else "FAIL",
        "promotion": "mission01_wave1_refinement_candidate_requires_unreal_visual_and_performance_gate",
        "known_limitations": [
            "Procedural Blender microdetail must be replaced or baked into Unreal master materials.",
            "Collision contracts are semantic metadata; UCX generation/import remains an Unreal pipeline step.",
            "This is production-ready geometry direction, not final photogrammetric texture acceptance.",
        ],
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("[SkyguardM01AAA] " + json.dumps(report))


if __name__ == "__main__":
    main()
