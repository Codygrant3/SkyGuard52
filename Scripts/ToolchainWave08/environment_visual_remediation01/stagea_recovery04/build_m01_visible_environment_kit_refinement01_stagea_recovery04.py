from __future__ import annotations

import ast
import hashlib
import json
import sys
import textwrap
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
BASE_SOURCE = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\build_m01_visible_environment_kit_refinement01_stagea.py"
BASE_BYTES = 42238
BASE_SHA256 = "773e67931108a2f199f763a4d3ce94348ba9ed9a403c049b3b8b4409bb06fd12"
GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY04"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_function(source: str, name: str, replacement: str) -> str:
    tree = ast.parse(source)
    matches = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one top-level function {name}, found {len(matches)}")
    node = matches[0]
    if node.end_lineno is None:
        raise RuntimeError(f"Function {name} has no end line")
    lines = source.splitlines(keepends=True)
    block = textwrap.dedent(replacement).strip("\n") + "\n\n"
    return "".join(lines[: node.lineno - 1]) + block + "".join(lines[node.end_lineno :])


MAKE_MATERIAL = r'''
def make_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
    noise_scale: float = 5.0,
    bump_strength: float = 0.12,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    principled = nodes.get("Principled BSDF")
    require(principled is not None, f"Missing Principled BSDF for {name}")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = metallic

    macro = nodes.new("ShaderNodeTexNoise")
    macro.name = f"MACRO_{name}"
    macro.inputs["Scale"].default_value = max(0.35, noise_scale * 0.22)
    macro.inputs["Detail"].default_value = 3.0
    macro.inputs["Roughness"].default_value = 0.72
    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.name = f"COLOR_VARIATION_{name}"
    dark = tuple(max(0.0, min(1.0, component * 0.68)) for component in color[:3]) + (1.0,)
    light = tuple(max(0.0, min(1.0, component * 1.18 + 0.018)) for component in color[:3]) + (1.0,)
    color_ramp.color_ramp.elements[0].position = 0.22
    color_ramp.color_ramp.elements[0].color = dark
    color_ramp.color_ramp.elements[1].position = 0.80
    color_ramp.color_ramp.elements[1].color = light
    links.new(macro.outputs["Fac"], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], principled.inputs["Base Color"])

    micro = nodes.new("ShaderNodeTexNoise")
    micro.name = f"MICRO_{name}"
    micro.inputs["Scale"].default_value = noise_scale * 4.0
    micro.inputs["Detail"].default_value = 5.0
    micro.inputs["Roughness"].default_value = 0.62
    rough_ramp = nodes.new("ShaderNodeValToRGB")
    rough_ramp.name = f"ROUGHNESS_VARIATION_{name}"
    low = max(0.04, roughness - 0.13)
    high = min(0.98, roughness + 0.13)
    rough_ramp.color_ramp.elements[0].color = (low, low, low, 1.0)
    rough_ramp.color_ramp.elements[1].color = (high, high, high, 1.0)
    links.new(micro.outputs["Fac"], rough_ramp.inputs["Fac"])
    links.new(rough_ramp.outputs["Color"], principled.inputs["Roughness"])

    bump = nodes.new("ShaderNodeBump")
    bump.name = f"BUMP_{name}"
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = 0.045
    links.new(micro.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return material


def make_glass_material(name: str) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    require(principled is not None, f"Missing Principled BSDF for {name}")
    principled.inputs["Base Color"].default_value = (0.018, 0.055, 0.085, 1.0)
    principled.inputs["Roughness"].default_value = 0.16
    principled.inputs["Metallic"].default_value = 0.04
    if principled.inputs.get("IOR") is not None:
        principled.inputs["IOR"].default_value = 1.45
    if principled.inputs.get("Transmission Weight") is not None:
        principled.inputs["Transmission Weight"].default_value = 0.18
    return material


def make_emissive_material(name: str) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    require(principled is not None, f"Missing Principled BSDF for {name}")
    principled.inputs["Base Color"].default_value = (0.12, 0.072, 0.025, 1.0)
    principled.inputs["Roughness"].default_value = 0.38
    emission_color = principled.inputs.get("Emission Color")
    if emission_color is None:
        emission_color = principled.inputs.get("Emission")
    if emission_color is not None:
        emission_color.default_value = (1.0, 0.40, 0.12, 1.0)
    emission_strength = principled.inputs.get("Emission Strength")
    if emission_strength is not None:
        emission_strength.default_value = 0.0
    return material


def add_cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
    vertices: int = 24,
    bevel: float = 0.025,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    apply_transforms(obj)
    add_bevel(obj, bevel, 2)
    obj.data.materials.append(material)
    ensure_uvs(obj)
    move_object(obj, target)
    return obj
'''


BUILD_MATERIALS = r'''
def build_materials() -> dict[str, bpy.types.Material]:
    return {
        "wet_sand": make_material("M_STAGEA_R04_WetSand", (0.14, 0.095, 0.052, 1), 0.29, noise_scale=10.0, bump_strength=0.10),
        "dry_sand": make_material("M_STAGEA_R04_DrySand", (0.46, 0.32, 0.17, 1), 0.76, noise_scale=14.0, bump_strength=0.20),
        "dune_soil": make_material("M_STAGEA_R04_DuneSoil", (0.23, 0.18, 0.085, 1), 0.88, noise_scale=8.0, bump_strength=0.24),
        "grass": make_material("M_STAGEA_R04_ReservedGrass", (0.12, 0.19, 0.04, 1), 0.84, noise_scale=5.0, bump_strength=0.08),
        "concrete": make_material("M_STAGEA_R04_SaltConcrete", (0.39, 0.40, 0.38, 1), 0.69, noise_scale=7.0, bump_strength=0.18),
        "concrete_dark": make_material("M_STAGEA_R04_DampConcrete", (0.15, 0.16, 0.16, 1), 0.54, noise_scale=9.0, bump_strength=0.14),
        "asphalt": make_material("M_STAGEA_R04_Asphalt", (0.052, 0.056, 0.061, 1), 0.85, noise_scale=20.0, bump_strength=0.24),
        "paver": make_material("M_STAGEA_R04_PromenadePaver", (0.31, 0.255, 0.205, 1), 0.75, noise_scale=18.0, bump_strength=0.15),
        "plaster_fde": make_material("M_STAGEA_R04_PlasterFDE", (0.44, 0.315, 0.19, 1), 0.73, noise_scale=5.0, bump_strength=0.13),
        "plaster_blue": make_material("M_STAGEA_R04_PlasterBlue", (0.155, 0.255, 0.32, 1), 0.70, noise_scale=5.0, bump_strength=0.12),
        "plaster_warm": make_material("M_STAGEA_R04_PlasterWarm", (0.53, 0.43, 0.31, 1), 0.71, noise_scale=5.5, bump_strength=0.12),
        "brick": make_material("M_STAGEA_R04_Brick", (0.29, 0.085, 0.045, 1), 0.84, noise_scale=12.0, bump_strength=0.24),
        "metal": make_material("M_STAGEA_R04_PaintedMetal", (0.055, 0.068, 0.078, 1), 0.36, metallic=0.58, noise_scale=10.0, bump_strength=0.07),
        "rust": make_material("M_STAGEA_R04_Rust", (0.29, 0.065, 0.022, 1), 0.90, metallic=0.18, noise_scale=13.0, bump_strength=0.20),
        "glass": make_glass_material("M_STAGEA_R04_WindowGlass"),
        "window_lit": make_emissive_material("M_STAGEA_R04_WindowInteriorLit"),
        "roof": make_material("M_STAGEA_R04_RoofMembrane", (0.067, 0.072, 0.078, 1), 0.73, noise_scale=11.0, bump_strength=0.13),
        "marking": make_material("M_STAGEA_R04_RoadMarking", (0.70, 0.63, 0.40, 1), 0.57, noise_scale=14.0, bump_strength=0.04),
        "grime": make_material("M_STAGEA_R04_Grime", (0.055, 0.047, 0.037, 1), 0.89, noise_scale=16.0, bump_strength=0.09),
        "water_stain": make_material("M_STAGEA_R04_WaterStain", (0.075, 0.095, 0.092, 1), 0.62, noise_scale=10.0, bump_strength=0.05),
    }
'''


BUILD_SHORE_AND_STREET = r'''
def build_shore_and_street(
    materials: dict[str, bpy.types.Material],
    visible: bpy.types.Collection,
    collision: bpy.types.Collection,
    sockets: bpy.types.Collection,
) -> list[bpy.types.Object]:
    objects = [build_solid_terrain(materials, visible)]
    for segment in range(10):
        x = 5.0 + segment * 10.0
        z_seawall = terrain_height(x, 43.0) + 0.75
        objects.append(add_box(f"SM_M01_STAGEA_R04_Seawall_{segment:02d}", (x, 43.0, z_seawall), (9.86, 1.25, 1.5), materials["concrete"], visible, 0.09))
        objects.append(add_box(f"SM_M01_STAGEA_R04_SeawallCoping_{segment:02d}", (x, 43.0, z_seawall + 0.82), (9.90, 1.48, 0.18), materials["concrete_dark"], visible, 0.05))
        objects.append(add_box(f"SM_M01_STAGEA_R04_SeawallStain_{segment:02d}", (x, 42.34, z_seawall - 0.18), (8.95, 0.025, 0.58), materials["water_stain"], visible, 0.006))
        objects.append(add_box(f"SM_M01_STAGEA_R04_Promenade_{segment:02d}", (x, 48.0, terrain_height(x, 48.0) + 0.06), (9.92, 6.8, 0.12), materials["paver"], visible, 0.025))
        objects.append(add_box(f"SM_M01_STAGEA_R04_Curb_{segment:02d}", (x, 53.2, terrain_height(x, 53.2) + 0.11), (9.88, 0.28, 0.22), materials["concrete"], visible, 0.035))
        if segment % 2 == 0:
            drain_x = x + 2.0
            objects.append(add_box(f"SM_M01_STAGEA_R04_DrainGrate_{segment:02d}", (drain_x, 53.45, terrain_height(drain_x, 53.45) + 0.025), (1.15, 0.42, 0.05), materials["metal"], visible, 0.015))
            for slot in (-0.40, -0.20, 0.0, 0.20, 0.40):
                objects.append(add_box(f"SM_M01_STAGEA_R04_DrainSlot_{segment:02d}_{slot:+.2f}", (drain_x + slot, 53.21, terrain_height(drain_x + slot, 53.21) + 0.08), (0.06, 0.31, 0.025), materials["grime"], visible, 0.004))

    for x in range(10, 100, 10):
        wall_z = terrain_height(float(x), 43.0) + 0.74
        objects.append(add_box(f"SM_M01_STAGEA_R04_SeawallJoint_{x:03d}", (float(x), 42.36, wall_z), (0.045, 0.035, 1.32), materials["grime"], visible, 0.004))
    for x in range(5, 100, 5):
        z = terrain_height(float(x), 48.0) + 0.132
        objects.append(add_box(f"SM_M01_STAGEA_R04_PromenadeJoint_{x:03d}", (float(x), 48.0, z), (0.035, 6.55, 0.018), materials["grime"], visible, 0.003))
    for x in (25.0, 75.0):
        z = terrain_height(x, 52.85) + 0.09
        objects.append(add_box(f"SM_M01_STAGEA_R04_CurbCut_{int(x):03d}", (x, 52.95, z), (3.2, 0.72, 0.10), materials["paver"], visible, 0.025))

    road_y = (54.0, 58.0, 62.0)
    road_z = [terrain_height(50.0, y) + offset for y, offset in zip(road_y, (0.06, 0.12, 0.06))]
    road_vertices = [(x, y, z) for x in (0.0, 100.0) for y, z in zip(road_y, road_z)]
    road_faces = [(0, 3, 4, 1), (1, 4, 5, 2)]
    road = create_custom_mesh("SM_M01_STAGEA_R04_RoadCrowned_100m", road_vertices, road_faces, [materials["asphalt"]], visible, [0, 0])
    objects.append(road)
    for y in (54.22, 61.78):
        objects.append(add_box(f"SM_M01_STAGEA_R04_Gutter_{y:.2f}", (50.0, y, terrain_height(50.0, y) + 0.075), (100.0, 0.28, 0.055), materials["concrete_dark"], visible, 0.015))
    for x in range(5, 100, 10):
        objects.append(add_box(f"SM_M01_STAGEA_R04_RoadMark_{x:03d}", (float(x), 58.0, terrain_height(float(x), 58.0) + 0.15), (4.5, 0.14, 0.025), materials["marking"], visible, 0.008))
    for x in range(12, 100, 20):
        objects.append(add_box(f"SM_M01_STAGEA_R04_RoadPatch_{x:03d}", (float(x), 59.7, terrain_height(float(x), 59.7) + 0.095), (5.5, 1.4, 0.018), materials["concrete_dark"], visible, 0.01, 0.03))

    add_collision_box("UCX_SM_M01_STAGEA_TerrainDistrict_100x80_00", (50.0, 40.0, 0.0), (100.0, 80.0, 4.0), collision)
    add_collision_box("UCX_SM_M01_STAGEA_Seawall_00", (50.0, 43.0, 2.4), (100.0, 1.4, 2.0), collision)
    add_collision_box("UCX_SM_M01_STAGEA_RoadCrowned_100m_00", (50.0, 58.0, 2.4), (100.0, 8.0, 0.4), collision)
    add_socket("SOCKET_District_W", (0.0, 0.0, terrain_height(0.0, 0.0)), sockets)
    add_socket("SOCKET_District_E", (100.0, 0.0, terrain_height(100.0, 0.0)), sockets)
    add_socket("SOCKET_District_S", (50.0, 0.0, terrain_height(50.0, 0.0)), sockets)
    add_socket("SOCKET_District_N", (50.0, 80.0, terrain_height(50.0, 80.0)), sockets)
    return objects
'''


ADD_WINDOW = r'''
def add_window(
    prefix: str,
    x: float,
    y: float,
    z: float,
    front: bool,
    materials: dict[str, bpy.types.Material],
    target: bpy.types.Collection,
    width: float = 1.55,
    height: float = 1.62,
    variant: int = 0,
) -> list[bpy.types.Object]:
    sign = -1.0 if front else 1.0
    frame_width = width + 0.28
    frame_height = height + 0.30
    result = [
        add_box(prefix + "_Reveal", (x, y - sign * 0.015, z), (frame_width + 0.22, 0.20, frame_height + 0.20), materials["concrete_dark"], target, 0.025),
        add_box(prefix + "_Interior", (x, y - sign * 0.13, z), (width - 0.12, 0.025, height - 0.12), materials["window_lit"], target, 0.01),
        add_box(prefix + "_Glass", (x, y + sign * 0.11, z), (width, 0.055, height), materials["glass"], target, 0.018),
        add_box(prefix + "_FrameTop", (x, y + sign * 0.21, z + frame_height * 0.5), (frame_width, 0.13, 0.105), materials["metal"], target, 0.018),
        add_box(prefix + "_FrameBottom", (x, y + sign * 0.21, z - frame_height * 0.5), (frame_width, 0.13, 0.105), materials["metal"], target, 0.018),
        add_box(prefix + "_FrameLeft", (x - frame_width * 0.5, y + sign * 0.21, z), (0.105, 0.13, frame_height), materials["metal"], target, 0.018),
        add_box(prefix + "_FrameRight", (x + frame_width * 0.5, y + sign * 0.21, z), (0.105, 0.13, frame_height), materials["metal"], target, 0.018),
        add_box(prefix + "_MullionV", (x, y + sign * 0.23, z), (0.065, 0.14, height), materials["metal"], target, 0.012),
        add_box(prefix + "_Sill", (x, y + sign * 0.34, z - frame_height * 0.5 - 0.07), (frame_width + 0.34, 0.42, 0.13), materials["concrete"], target, 0.025),
        add_box(prefix + "_Drip", (x, y + sign * 0.31, z + frame_height * 0.5 + 0.12), (frame_width + 0.24, 0.30, 0.10), materials["concrete"], target, 0.022),
    ]
    if variant % 3 == 1:
        result.append(add_box(prefix + "_MullionH", (x, y + sign * 0.235, z + 0.20), (width, 0.145, 0.055), materials["metal"], target, 0.012))
    if variant % 3 == 2:
        result.append(add_box(prefix + "_Shade", (x, y + sign * 0.48, z + frame_height * 0.5 + 0.15), (frame_width + 0.48, 0.62, 0.105), materials["metal"], target, 0.025))
    return result


def add_side_window(
    prefix: str,
    x: float,
    y: float,
    z: float,
    right_side: bool,
    materials: dict[str, bpy.types.Material],
    target: bpy.types.Collection,
) -> list[bpy.types.Object]:
    sign = 1.0 if right_side else -1.0
    result = [
        add_box(prefix + "_Reveal", (x - sign * 0.02, y, z), (0.20, 2.05, 2.02), materials["concrete_dark"], target, 0.025),
        add_box(prefix + "_Interior", (x - sign * 0.13, y, z), (0.025, 1.58, 1.56), materials["window_lit"], target, 0.01),
        add_box(prefix + "_Glass", (x + sign * 0.11, y, z), (0.055, 1.72, 1.70), materials["glass"], target, 0.018),
        add_box(prefix + "_FrameTop", (x + sign * 0.21, y, z + 0.92), (0.13, 2.02, 0.105), materials["metal"], target, 0.018),
        add_box(prefix + "_FrameBottom", (x + sign * 0.21, y, z - 0.92), (0.13, 2.02, 0.105), materials["metal"], target, 0.018),
        add_box(prefix + "_FrameA", (x + sign * 0.21, y - 0.96, z), (0.13, 0.105, 1.84), materials["metal"], target, 0.018),
        add_box(prefix + "_FrameB", (x + sign * 0.21, y + 0.96, z), (0.13, 0.105, 1.84), materials["metal"], target, 0.018),
    ]
    return result
'''


ADD_BALCONY = r'''
def add_balcony(
    prefix: str,
    x: float,
    y: float,
    z: float,
    materials: dict[str, bpy.types.Material],
    target: bpy.types.Collection,
    width: float = 3.35,
) -> list[bpy.types.Object]:
    result = [
        add_box(prefix + "_Slab", (x, y - 0.92, z - 0.96), (width, 1.70, 0.20), materials["concrete"], target, 0.045),
        add_box(prefix + "_Fascia", (x, y - 1.77, z - 0.99), (width + 0.08, 0.14, 0.34), materials["concrete_dark"], target, 0.025),
        add_box(prefix + "_RailTop", (x, y - 1.77, z - 0.08), (width - 0.10, 0.065, 0.075), materials["metal"], target, 0.018),
        add_box(prefix + "_RailMid", (x, y - 1.77, z - 0.52), (width - 0.14, 0.052, 0.052), materials["metal"], target, 0.014),
        add_box(prefix + "_SideRailL", (x - width * 0.5 + 0.06, y - 0.98, z - 0.48), (0.06, 1.48, 0.92), materials["metal"], target, 0.014),
        add_box(prefix + "_SideRailR", (x + width * 0.5 - 0.06, y - 0.98, z - 0.48), (0.06, 1.48, 0.92), materials["metal"], target, 0.014),
        add_box(prefix + "_Drain", (x + width * 0.34, y - 1.24, z - 1.08), (0.12, 0.28, 0.08), materials["grime"], target, 0.01),
    ]
    post_count = max(4, int(width / 0.55))
    for index in range(post_count + 1):
        offset = -width * 0.5 + 0.12 + (width - 0.24) * index / post_count
        result.append(add_box(prefix + f"_Post_{index:02d}", (x + offset, y - 1.77, z - 0.52), (0.045, 0.045, 0.88), materials["metal"], target, 0.011))
    return result
'''


BUILD_MIDRISE = r'''
def build_midrise(
    name: str,
    center_x: float,
    floors: int,
    facade_style: str,
    materials: dict[str, bpy.types.Material],
    target: bpy.types.Collection,
    collision: bpy.types.Collection,
    sockets: bpy.types.Collection,
) -> list[bpy.types.Object]:
    ground_z = terrain_height(center_x, 72.5)
    floor_height = 3.0
    ground_floor = 3.6
    height = ground_floor + (floors - 1) * floor_height
    front_y, back_y = 66.66, 78.34
    wall_material = materials["plaster_fde"] if facade_style == "A" else materials["plaster_blue"]
    accent_material = materials["brick"] if facade_style == "A" else materials["plaster_warm"]
    objects = [
        add_box(name + "_Core", (center_x, 72.5, ground_z + height * 0.5), (18.0, 11.2, height), wall_material, target, 0.16),
        add_box(name + "_Foundation", (center_x, 72.5, ground_z - 0.32), (18.4, 11.6, 0.64), materials["concrete_dark"], target, 0.08),
        add_box(name + "_GroundPlinthFront", (center_x, front_y - 0.20, ground_z + 0.62), (17.65, 0.26, 1.24), materials["concrete_dark"], target, 0.035),
        add_box(name + "_GroundPlinthRear", (center_x, back_y + 0.20, ground_z + 0.62), (17.65, 0.26, 1.24), materials["concrete_dark"], target, 0.035),
    ]

    bay_specs = (
        [(-7.10, 1.35, 0), (-4.35, 1.78, 1), (-1.35, 1.50, 2), (1.35, 1.50, 0), (4.35, 1.78, 2), (7.10, 1.35, 1)]
        if facade_style == "A"
        else [(-7.20, 1.55, 2), (-4.30, 1.42, 0), (-1.45, 1.82, 1), (1.45, 1.82, 2), (4.30, 1.42, 1), (7.20, 1.55, 0)]
    )

    service_x = center_x - 6.0 if facade_style == "A" else center_x + 5.8
    objects.append(add_box(name + "_ServiceBand", (service_x, front_y - 0.23, ground_z + height * 0.5), (2.15, 0.28, height - 0.45), accent_material, target, 0.045))
    objects.append(add_box(name + "_ServiceBandInset", (service_x, front_y - 0.39, ground_z + height * 0.55), (0.68, 0.07, height * 0.62), materials["grime"], target, 0.015))

    for floor in range(1, floors):
        z = ground_z + ground_floor + (floor - 1) * floor_height
        objects.append(add_box(f"{name}_StringCourse_{floor:02d}", (center_x, front_y - 0.26, z + 0.03), (17.75, 0.32, 0.13), materials["concrete"], target, 0.022))

    for floor in range(floors):
        z = ground_z + (1.86 if floor == 0 else ground_floor + (floor - 1) * floor_height + 1.50)
        for bay_index, (offset, width, variant) in enumerate(bay_specs):
            if floor == 0 and bay_index in (2, 3):
                continue
            objects.extend(add_window(f"{name}_F{floor:02d}_B{bay_index:02d}_Front", center_x + offset, front_y, z, True, materials, target, width, 1.64 if floor else 1.82, variant + floor))
            if (bay_index + floor) % 2 == 0:
                objects.extend(add_window(f"{name}_F{floor:02d}_B{bay_index:02d}_Rear", center_x + offset, back_y, z, False, materials, target, max(1.30, width - 0.16), 1.55, variant + floor + 1))

        if floor > 0:
            if facade_style == "A":
                balcony_groups = (-4.35, 3.05) if floor % 2 else (-1.35, 6.10)
            else:
                balcony_groups = (-5.75, 1.45) if floor % 2 else (-2.85, 5.75)
            for group_index, balcony_x in enumerate(balcony_groups):
                objects.extend(add_balcony(f"{name}_F{floor:02d}_Balcony_{group_index:02d}", center_x + balcony_x, front_y, z, materials, target, 3.65 if group_index == 0 else 3.15))

        if floor in (1, floors - 1):
            for side_y_index, side_y in enumerate((70.35, 74.65)):
                objects.extend(add_side_window(f"{name}_F{floor:02d}_SideL_{side_y_index:02d}", center_x - 9.0, side_y, z, False, materials, target))
                objects.extend(add_side_window(f"{name}_F{floor:02d}_SideR_{side_y_index:02d}", center_x + 9.0, side_y, z, True, materials, target))

    entrance_material = materials["brick"] if facade_style == "A" else materials["concrete_dark"]
    objects.append(add_box(name + "_EntrancePortal", (center_x, front_y - 0.24, ground_z + 1.68), (4.6, 0.52, 3.36), entrance_material, target, 0.08))
    objects.append(add_box(name + "_EntranceRecess", (center_x, front_y - 0.51, ground_z + 1.58), (3.40, 0.12, 2.94), materials["grime"], target, 0.025))
    objects.append(add_box(name + "_EntranceGlassL", (center_x - 0.78, front_y - 0.59, ground_z + 1.55), (1.40, 0.06, 2.72), materials["glass"], target, 0.018))
    objects.append(add_box(name + "_EntranceGlassR", (center_x + 0.78, front_y - 0.59, ground_z + 1.55), (1.40, 0.06, 2.72), materials["glass"], target, 0.018))
    objects.append(add_box(name + "_EntranceCanopy", (center_x, front_y - 1.12, ground_z + 3.12), (5.15, 1.55, 0.18), materials["metal"], target, 0.05))

    for x_offset in (-8.74, 8.74):
        objects.append(add_box(name + f"_CornerPilaster_{x_offset:+.2f}", (center_x + x_offset, front_y - 0.16, ground_z + height * 0.5), (0.40, 0.42, height), materials["concrete"], target, 0.055))
        objects.append(add_box(name + f"_Downspout_{x_offset:+.2f}", (center_x + x_offset * 0.96, front_y - 0.43, ground_z + height * 0.48), (0.12, 0.13, height * 0.92), materials["metal"], target, 0.025))
        objects.append(add_box(name + f"_DownspoutStain_{x_offset:+.2f}", (center_x + x_offset * 0.96, front_y - 0.34, ground_z + height * 0.30), (0.34, 0.035, height * 0.48), materials["water_stain"], target, 0.012))

    roof_z = ground_z + height
    objects.append(add_box(name + "_Roof", (center_x, 72.5, roof_z + 0.18), (18.0, 11.2, 0.36), materials["roof"], target, 0.05))
    for x_offset in (-8.75, 8.75):
        objects.append(add_box(name + f"_ParapetLong_{x_offset:+.2f}", (center_x + x_offset, 72.5, roof_z + 0.72), (0.24, 11.2, 1.1), materials["concrete"], target, 0.04))
        objects.append(add_box(name + f"_ParapetCopingLong_{x_offset:+.2f}", (center_x + x_offset, 72.5, roof_z + 1.30), (0.38, 11.35, 0.10), materials["metal"], target, 0.025))
    for y in (67.02, 77.98):
        objects.append(add_box(name + f"_ParapetShort_{y:.2f}", (center_x, y, roof_z + 0.72), (17.5, 0.24, 1.1), materials["concrete"], target, 0.04))
        objects.append(add_box(name + f"_ParapetCopingShort_{y:.2f}", (center_x, y, roof_z + 1.30), (17.65, 0.38, 0.10), materials["metal"], target, 0.025))

    access_x = center_x + (3.8 if facade_style == "A" else -3.8)
    objects.append(add_box(name + "_RoofAccess", (access_x, 73.1, roof_z + 1.42), (4.35, 3.20, 2.48), wall_material, target, 0.11))
    objects.append(add_box(name + "_RoofAccessCoping", (access_x, 73.1, roof_z + 2.72), (4.60, 3.45, 0.12), materials["metal"], target, 0.03))
    objects.append(add_box(name + "_RoofAccessDoor", (access_x, 71.46, roof_z + 1.20), (1.15, 0.08, 2.05), materials["metal"], target, 0.025))
    for vent_index, vent_x in enumerate((center_x - 5.5, center_x - 2.8)):
        objects.append(add_cylinder(name + f"_RoofVent_{vent_index:02d}", (vent_x, 72.0 + vent_index * 1.5, roof_z + 1.10), 0.48, 1.65, materials["metal"], target, 24, 0.035))
        objects.append(add_cylinder(name + f"_RoofVentCap_{vent_index:02d}", (vent_x, 72.0 + vent_index * 1.5, roof_z + 1.95), 0.68, 0.16, materials["metal"], target, 24, 0.025))

    add_collision_box("UCX_" + name + "_00", (center_x, 72.5, ground_z + height * 0.5), (18.0, 11.2, height), collision)
    add_socket("SOCKET_" + name + "_Origin", (center_x - 9.0, 66.9, ground_z), sockets)
    return objects
'''


BUILD_FACADE_EXPORT_MODULES = r'''
def build_facade_export_modules(materials: dict[str, bpy.types.Material], target: bpy.types.Collection) -> list[bpy.types.Object]:
    result: list[bpy.types.Object] = []
    compositions = (
        (120.0, materials["plaster_fde"], 1.70, 0, False),
        (125.0, materials["plaster_blue"], 1.45, 1, True),
        (130.0, materials["brick"], 1.20, 2, False),
    )
    for composition, (x, wall_material, width, variant, balcony) in enumerate(compositions, 1):
        result.append(add_box(f"SM_M01_STAGEA_R04_FacadeComposition_{composition:02d}_Wall", (x, 0.0, 1.65), (4.0, 0.42, 3.30), wall_material, target, 0.07))
        result.extend(add_window(f"SM_M01_STAGEA_R04_FacadeComposition_{composition:02d}_Window", x, -0.28, 1.72, True, materials, target, width, 1.72, variant))
        result.append(add_box(f"SM_M01_STAGEA_R04_FacadeComposition_{composition:02d}_Band", (x - 1.55 if composition == 1 else x + 1.50, -0.31, 1.65), (0.42, 0.16, 3.10), materials["concrete_dark"], target, 0.035))
        if balcony:
            result.extend(add_balcony("SM_M01_STAGEA_R04_FacadeComposition_02_Balcony", x, -0.28, 1.72, materials, target, 3.55))
    for obj in target.all_objects:
        obj.hide_render = True
    return result
'''


CREATE_TEXTURE_ATLAS = r'''
def create_texture_atlas(output: Path) -> list[Path]:
    texture_dir = output / "textures"
    texture_dir.mkdir(parents=True, exist_ok=True)
    size = 2048
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    bands = np.minimum((np.arange(size) * 8 // size), 7)
    palette = np.array([
        [0.14, 0.095, 0.052], [0.46, 0.32, 0.17], [0.23, 0.18, 0.085], [0.39, 0.40, 0.38],
        [0.052, 0.056, 0.061], [0.44, 0.315, 0.19], [0.155, 0.255, 0.32], [0.29, 0.085, 0.045],
    ], dtype=np.float32)
    macro = (np.sin(x * 0.013 + y * 0.007) * 0.016 + np.sin(x * 0.051 - y * 0.027) * 0.009).astype(np.float32)
    micro = (np.sin(x * 0.41) * np.sin(y * 0.37) * 0.008).astype(np.float32)
    streaks = (np.maximum(0.0, np.sin(x * 0.018 + np.sin(y * 0.006) * 2.0)) ** 10 * 0.035).astype(np.float32)
    base = np.repeat(palette[bands][:, None, :], size, axis=1)
    base = np.clip(base + (macro + micro - streaks)[..., None], 0.0, 1.0)
    rough_values = np.array([0.29, 0.76, 0.88, 0.69, 0.85, 0.73, 0.70, 0.84], dtype=np.float32)
    rough = np.repeat(rough_values[bands][:, None], size, axis=1)
    rough = np.clip(rough + macro * 1.8 + streaks * 0.8, 0.05, 0.98)
    metallic = np.zeros((size, size), dtype=np.float32)
    ao = np.clip(0.94 - streaks * 2.2 + macro * 0.4, 0.72, 1.0)
    grad_y, grad_x = np.gradient(macro + micro)
    normal = np.empty((size, size, 3), dtype=np.float32)
    normal[:, :, 0] = np.clip(0.5 - grad_x * 4.0, 0.0, 1.0)
    normal[:, :, 1] = np.clip(0.5 - grad_y * 4.0, 0.0, 1.0)
    normal[:, :, 2] = 1.0
    maps = (
        ("T_M01_STAGEA_Atlas_BaseColor.png", base),
        ("T_M01_STAGEA_Atlas_Normal.png", normal),
        ("T_M01_STAGEA_Atlas_Roughness.png", np.repeat(rough[..., None], 3, axis=2)),
        ("T_M01_STAGEA_Atlas_Metallic.png", np.repeat(metallic[..., None], 3, axis=2)),
        ("T_M01_STAGEA_Atlas_AO.png", np.repeat(ao[..., None], 3, axis=2)),
    )
    paths: list[Path] = []
    alpha = np.ones((size, size, 1), dtype=np.float32)
    for filename, rgb in maps:
        rgba = np.concatenate((rgb.astype(np.float32, copy=False), alpha), axis=2)
        image = bpy.data.images.new(filename[:-4], width=size, height=size, alpha=True, float_buffer=False)
        image.pixels.foreach_set(rgba.reshape(-1))
        image.filepath_raw = str(texture_dir / filename)
        image.file_format = "PNG"
        image.save()
        bpy.data.images.remove(image)
        paths.append(texture_dir / filename)
    return paths
'''


ADD_REVIEW_RIG = r'''
def add_review_rig(scene: bpy.types.Scene) -> dict[str, Any]:
    review = collection("REVIEW_ONLY")
    camera_data = bpy.data.cameras.new("CAM_STAGEA_R04_Review")
    camera = bpy.data.objects.new("CAM_STAGEA_R04_Review", camera_data)
    review.objects.link(camera)
    camera.data.lens = 50.0
    camera.data.clip_start = 0.10
    camera.data.clip_end = 500.0
    scene.camera = camera

    bpy.ops.object.light_add(type="SUN", location=(50.0, 35.0, 70.0))
    sun = bpy.context.object
    sun.name = "LIGHT_STAGEA_R04_Sun"
    sun.data.energy = 3.2
    sun.data.angle = math.radians(0.535)
    sun.rotation_euler = (math.radians(35.0), math.radians(-18.0), math.radians(-35.0))
    move_object(sun, review)

    bpy.ops.object.light_add(type="AREA", location=(40.0, 32.0, 38.0))
    fill = bpy.context.object
    fill.name = "LIGHT_STAGEA_R04_Fill"
    fill.data.energy = 1200.0
    fill.data.shape = "DISK"
    fill.data.size = 48.0
    fill.rotation_euler = (math.radians(22.0), 0.0, math.radians(20.0))
    move_object(fill, review)

    bpy.ops.object.light_add(type="AREA", location=(66.0, 48.0, 34.0))
    moon = bpy.context.object
    moon.name = "LIGHT_STAGEA_R04_MoonKey"
    moon.data.energy = 0.0
    moon.data.color = (0.26, 0.42, 0.78)
    moon.data.shape = "DISK"
    moon.data.size = 32.0
    moon.rotation_euler = (math.radians(28.0), 0.0, math.radians(-42.0))
    move_object(moon, review)

    practicals: list[bpy.types.Object] = []
    for index, x in enumerate((12.0, 32.0, 52.0, 72.0, 92.0)):
        bpy.ops.object.light_add(type="POINT", location=(x, 50.5, terrain_height(x, 50.5) + 5.2))
        light = bpy.context.object
        light.name = f"LIGHT_STAGEA_R04_Promenade_{index:02d}"
        light.data.energy = 0.0
        light.data.color = (1.0, 0.42, 0.16)
        light.data.shadow_soft_size = 1.8
        move_object(light, review)
        practicals.append(light)
    for index, x in enumerate((22.0, 66.0)):
        bpy.ops.object.light_add(type="AREA", location=(x, 63.2, terrain_height(x, 72.5) + 9.0))
        light = bpy.context.object
        light.name = f"LIGHT_STAGEA_R04_WindowBounce_{index:02d}"
        light.data.energy = 0.0
        light.data.color = (1.0, 0.32, 0.09)
        light.data.shape = "RECTANGLE"
        light.data.size = 8.0
        light.data.size_y = 5.0
        light.rotation_euler = (math.radians(90.0), 0.0, 0.0)
        move_object(light, review)
        practicals.append(light)
    return {"camera": camera, "sun": sun, "fill": fill, "moon": moon, "practicals": practicals}
'''


CONFIGURE_CONDITION = r'''
def configure_condition(scene: bpy.types.Scene, rig: dict[str, Any], condition: str, materials: dict[str, bpy.types.Material]) -> None:
    background = scene.world.node_tree.nodes["Background"]
    values = {
        "daylight": ((0.16, 0.28, 0.50, 1.0), 0.48, 3.2, 1200.0, 0.0, 0.0, 0.0),
        "overcast": ((0.20, 0.23, 0.28, 1.0), 0.58, 1.15, 1850.0, 0.0, 0.0, 0.28),
        "night": ((0.025, 0.045, 0.095, 1.0), 0.23, 0.38, 1550.0, 1050.0, 520.0, 1.10),
        "wet": ((0.13, 0.18, 0.23, 1.0), 0.44, 1.85, 1550.0, 0.0, 220.0, 0.18),
        "storm": ((0.055, 0.075, 0.095, 1.0), 0.34, 0.72, 1420.0, 280.0, 300.0, 0.45),
    }
    color, strength, sun_energy, fill_energy, moon_energy, practical_energy, exposure = values[condition]
    background.inputs["Color"].default_value = color
    background.inputs["Strength"].default_value = strength
    rig["sun"].data.energy = sun_energy
    rig["fill"].data.energy = fill_energy
    rig["moon"].data.energy = moon_energy
    for practical in rig["practicals"]:
        practical.data.energy = practical_energy
    scene.view_settings.exposure = exposure
    emission = materials["window_lit"].node_tree.nodes.get("Principled BSDF")
    if emission is not None:
        emission_strength = emission.inputs.get("Emission Strength")
        if emission_strength is not None:
            emission_strength.default_value = 3.2 if condition == "night" else 0.55 if condition in ("wet", "storm") else 0.0
    wet = condition in ("wet", "storm")
    materials["wet_sand"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.17 if wet else 0.29
    materials["asphalt"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.38 if wet else 0.85
    materials["concrete"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.50 if wet else 0.69
'''


RENDER_AND_MEASURE = r'''
def render_and_measure(scene: bpy.types.Scene, path: Path) -> dict[str, float]:
    path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    require(path.is_file() and path.stat().st_size > 0, f"Saved render is unavailable: {path}")
    measured = bpy.data.images.load(str(path), check_existing=False)
    try:
        width, height = measured.size
        require(width > 0 and height > 0, f"Saved render dimensions are invalid: {path}")
        expected_values = int(width) * int(height) * 4
        pixels = np.empty(expected_values, dtype=np.float32)
        measured.pixels.foreach_get(pixels)
        require(pixels.size == expected_values and pixels.size > 0, f"Saved render pixel buffer is invalid: {path}")
        rgb = pixels.reshape((-1, 4))[:, :3]
        luma = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        require(luma.size == width * height and luma.size > 0, f"Saved render luminance buffer is invalid: {path}")
        return {
            "width": int(width),
            "height": int(height),
            "mean_luma_linear": float(np.mean(luma)),
            "black_fraction_linear_0_01": float(np.mean(luma < 0.01)),
            "max_luma_linear": float(np.max(luma)),
        }
    finally:
        bpy.data.images.remove(measured)
'''


RENDER_CHECKPOINTS = r'''
def render_checkpoints(scene: bpy.types.Scene, rig: dict[str, Any], output: Path, materials: dict[str, bpy.types.Material]) -> list[dict[str, Any]]:
    scene.render.resolution_x, scene.render.resolution_y = CHECKPOINT_RESOLUTION
    specs = [
        ("checkpoint_01_cross_section", "daylight", (10.0, -24.0, 16.0), (42.0, 48.0, 4.0), 52.0),
        ("checkpoint_02_facade_street", "overcast", (30.0, 45.0, 10.0), (22.0, 69.0, 8.0), 58.0),
        ("checkpoint_03_pbr_composition", "night", (30.0, 45.0, 10.0), (22.0, 69.0, 8.0), 58.0),
    ]
    results: list[dict[str, Any]] = []
    for name, condition, location, target, lens in specs:
        configure_condition(scene, rig, condition, materials)
        point_camera(rig["camera"], location, target, lens)
        path = output / "renders" / "checkpoints" / f"{name}.png"
        metrics = render_and_measure(scene, path)
        require((metrics["width"], metrics["height"]) == CHECKPOINT_RESOLUTION, f"Checkpoint resolution failed: {name}")
        minimum_luma = 0.008 if condition == "night" else 0.03
        maximum_black = 0.70 if condition == "night" else 0.35
        require(metrics["mean_luma_linear"] >= minimum_luma, f"Checkpoint is too dark: {name}")
        require(metrics["black_fraction_linear_0_01"] <= maximum_black, f"Checkpoint is excessively black: {name}")
        results.append({"id": name, "condition": condition, "path": str(path), "metrics": metrics, "passed": True, "bounded_correction_used": False})
    return results
'''


RENDER_FINAL_VIEWS = r'''
def render_final_views(scene: bpy.types.Scene, rig: dict[str, Any], output: Path, materials: dict[str, bpy.types.Material]) -> list[dict[str, Any]]:
    scene.render.resolution_x, scene.render.resolution_y = FINAL_RESOLUTION
    view_specs = {
        "close": ((30.0, 43.0, 10.5), (22.0, 69.5, 8.2), 60.0),
        "route": ((12.0, -24.0, 19.0), (50.0, 58.0, 5.2), 54.0),
        "aerial": ((50.0, -38.0, 44.0), (50.0, 51.0, 6.2), 54.0),
    }
    results: list[dict[str, Any]] = []
    for condition in FINAL_CONDITIONS:
        configure_condition(scene, rig, condition, materials)
        for view in FINAL_VIEWS:
            location, target, lens = view_specs[view]
            point_camera(rig["camera"], location, target, lens)
            path = output / "renders" / "final" / f"{condition}_{view}.png"
            metrics = render_and_measure(scene, path)
            require((metrics["width"], metrics["height"]) == FINAL_RESOLUTION, f"Final render resolution failed: {condition}_{view}")
            require(metrics["mean_luma_linear"] >= (0.008 if condition == "night" else 0.025), f"Final render is too dark: {condition}_{view}")
            require(metrics["black_fraction_linear_0_01"] <= (0.70 if condition == "night" else 0.42), f"Final render is excessively black: {condition}_{view}")
            results.append({"condition": condition, "view": view, "path": str(path), "metrics": metrics})
    require(len(results) == 15, "Final render count is not exactly fifteen")
    return results
'''


REPLACEMENTS = {
    "make_material": MAKE_MATERIAL,
    "build_materials": BUILD_MATERIALS,
    "build_shore_and_street": BUILD_SHORE_AND_STREET,
    "add_window": ADD_WINDOW,
    "add_balcony": ADD_BALCONY,
    "build_midrise": BUILD_MIDRISE,
    "build_facade_export_modules": BUILD_FACADE_EXPORT_MODULES,
    "create_texture_atlas": CREATE_TEXTURE_ATLAS,
    "add_review_rig": ADD_REVIEW_RIG,
    "configure_condition": CONFIGURE_CONDITION,
    "render_and_measure": RENDER_AND_MEASURE,
    "render_checkpoints": RENDER_CHECKPOINTS,
    "render_final_views": RENDER_FINAL_VIEWS,
}


def load_recovery04_source() -> tuple[str, dict[str, object]]:
    raw = BASE_SOURCE.read_bytes()
    if len(raw) != BASE_BYTES:
        raise RuntimeError(f"Frozen StageA source byte mismatch: {len(raw)}")
    digest = sha256_bytes(raw)
    if digest != BASE_SHA256:
        raise RuntimeError(f"Frozen StageA source hash mismatch: {digest}")
    source = raw.decode("utf-8")
    old_gate = 'GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA"'
    if source.count(old_gate) != 1:
        raise RuntimeError("Frozen StageA gate token cardinality is not one")
    source = source.replace(old_gate, f'GATE = "{GATE}"', 1)
    for name, replacement in REPLACEMENTS.items():
        source = replace_function(source, name, replacement)
    ast.parse(source)
    forbidden = (
        "VisibleEnvironmentKit_Refinement01_StageA_Recovery03",
        "SM_M01_STAGEA_DuneGrass_",
        "Final render is too dark: night_close",
    )
    for token in forbidden:
        if token in source:
            raise RuntimeError(f"Forbidden Recovery04 token remains: {token}")
    required = (
        'GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY04"',
        '"window_lit": make_emissive_material',
        '"night": ((0.025, 0.045, 0.095, 1.0), 0.23, 0.38, 1550.0, 1050.0, 520.0, 1.10)',
        'metrics["mean_luma_linear"] >= (0.008 if condition == "night" else 0.025)',
        'metrics["black_fraction_linear_0_01"] <= (0.70 if condition == "night" else 0.42)',
        'require(len(results) == 15, "Final render count is not exactly fifteen")',
    )
    for token in required:
        if token not in source:
            raise RuntimeError(f"Required Recovery04 token is absent: {token}")
    receipt = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery04.in-memory-rebuild.v1",
        "gate": GATE,
        "base_source": str(BASE_SOURCE),
        "base_bytes": BASE_BYTES,
        "base_sha256": BASE_SHA256,
        "function_replacements": sorted(REPLACEMENTS),
        "function_replacement_count": len(REPLACEMENTS),
        "failed_output_geometry_reused": False,
        "threshold_relaxation": False,
        "stageb_assets_added": False,
        "visible_dune_grass_markers_removed": True,
        "preliminary_conditions": ["daylight", "overcast", "night"],
        "passed": True,
    }
    return source, receipt


def main() -> int:
    corrected, receipt = load_recovery04_source()
    print(json.dumps(receipt, sort_keys=True))
    namespace: dict[str, object] = {
        "__name__": "skyguard_stagea_recovery04_embedded",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
    }
    exec(compile(corrected, str(Path(__file__).resolve()), "exec"), namespace)
    embedded_main = namespace.get("main")
    if not callable(embedded_main):
        raise RuntimeError("Recovery04 embedded main is unavailable")
    return int(embedded_main())


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"gate": GATE, "status": "FAILED_WITH_EVIDENCE", "error": f"{type(exc).__name__}: {exc}"}), file=sys.stderr)
        raise
