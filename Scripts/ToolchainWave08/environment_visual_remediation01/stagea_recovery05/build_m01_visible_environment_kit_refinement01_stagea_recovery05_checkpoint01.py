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
GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01"


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


R05_BUILD_MATERIALS = r'''
def build_materials() -> dict[str, bpy.types.Material]:
    warm = make_emissive_material("M_STAGEA_R05_WindowInteriorWarm")
    cool = make_emissive_material("M_STAGEA_R05_WindowInteriorCool")
    dark = make_material("M_STAGEA_R05_WindowInteriorDark", (0.010, 0.014, 0.020, 1), 0.58, noise_scale=3.0, bump_strength=0.01)
    cool_bsdf = cool.node_tree.nodes.get("Principled BSDF")
    if cool_bsdf is not None:
        cool_bsdf.inputs["Base Color"].default_value = (0.030, 0.075, 0.13, 1.0)
        emission_color = cool_bsdf.inputs.get("Emission Color") or cool_bsdf.inputs.get("Emission")
        if emission_color is not None:
            emission_color.default_value = (0.18, 0.42, 1.0, 1.0)
    return {
        "wet_sand": make_material("M_STAGEA_R05_WetSand", (0.115, 0.074, 0.038, 1), 0.25, noise_scale=13.0, bump_strength=0.12),
        "dry_sand": make_material("M_STAGEA_R05_DrySand", (0.47, 0.325, 0.17, 1), 0.78, noise_scale=17.0, bump_strength=0.22),
        "dune_soil": make_material("M_STAGEA_R05_DuneSoil", (0.21, 0.165, 0.073, 1), 0.89, noise_scale=10.0, bump_strength=0.24),
        "grass": make_material("M_STAGEA_R05_Grass", (0.085, 0.17, 0.035, 1), 0.86, noise_scale=7.0, bump_strength=0.10),
        "foliage": make_material("M_STAGEA_R05_Foliage", (0.035, 0.135, 0.035, 1), 0.82, noise_scale=9.0, bump_strength=0.11),
        "foliage_dark": make_material("M_STAGEA_R05_FoliageDark", (0.018, 0.072, 0.022, 1), 0.86, noise_scale=11.0, bump_strength=0.12),
        "trunk": make_material("M_STAGEA_R05_TreeBark", (0.12, 0.052, 0.021, 1), 0.93, noise_scale=14.0, bump_strength=0.28),
        "concrete": make_material("M_STAGEA_R05_SaltConcrete", (0.38, 0.395, 0.39, 1), 0.68, noise_scale=9.0, bump_strength=0.19),
        "concrete_dark": make_material("M_STAGEA_R05_DampConcrete", (0.105, 0.12, 0.125, 1), 0.55, noise_scale=12.0, bump_strength=0.17),
        "asphalt": make_material("M_STAGEA_R05_Asphalt", (0.038, 0.043, 0.050, 1), 0.86, noise_scale=24.0, bump_strength=0.25),
        "paver": make_material("M_STAGEA_R05_PromenadePaver", (0.30, 0.245, 0.195, 1), 0.75, noise_scale=20.0, bump_strength=0.17),
        "plaster_fde": make_material("M_STAGEA_R05_PlasterFDE", (0.43, 0.305, 0.18, 1), 0.73, noise_scale=6.5, bump_strength=0.15),
        "plaster_blue": make_material("M_STAGEA_R05_PlasterBlue", (0.12, 0.225, 0.30, 1), 0.70, noise_scale=6.0, bump_strength=0.14),
        "plaster_warm": make_material("M_STAGEA_R05_PlasterWarm", (0.51, 0.40, 0.285, 1), 0.72, noise_scale=6.5, bump_strength=0.14),
        "plaster_green": make_material("M_STAGEA_R05_PlasterGreen", (0.19, 0.285, 0.22, 1), 0.74, noise_scale=7.0, bump_strength=0.14),
        "brick": make_material("M_STAGEA_R05_Brick", (0.28, 0.078, 0.038, 1), 0.85, noise_scale=14.0, bump_strength=0.26),
        "tile": make_material("M_STAGEA_R05_CeramicTile", (0.20, 0.255, 0.29, 1), 0.43, noise_scale=18.0, bump_strength=0.08),
        "metal": make_material("M_STAGEA_R05_PaintedMetal", (0.045, 0.058, 0.067, 1), 0.34, metallic=0.62, noise_scale=12.0, bump_strength=0.08),
        "rust": make_material("M_STAGEA_R05_Rust", (0.28, 0.058, 0.018, 1), 0.91, metallic=0.17, noise_scale=16.0, bump_strength=0.22),
        "glass": make_glass_material("M_STAGEA_R05_WindowGlass"),
        "window_warm": warm,
        "window_cool": cool,
        "window_dark": dark,
        "roof": make_material("M_STAGEA_R05_RoofMembrane", (0.052, 0.058, 0.066, 1), 0.72, noise_scale=13.0, bump_strength=0.15),
        "marking": make_material("M_STAGEA_R05_RoadMarking", (0.72, 0.65, 0.42, 1), 0.55, noise_scale=16.0, bump_strength=0.04),
        "grime": make_material("M_STAGEA_R05_Grime", (0.035, 0.030, 0.024, 1), 0.90, noise_scale=18.0, bump_strength=0.10),
        "water_stain": make_material("M_STAGEA_R05_WaterStain", (0.055, 0.078, 0.076, 1), 0.60, noise_scale=12.0, bump_strength=0.06),
        "ocean": make_material("M_STAGEA_R05_ReviewOcean", (0.015, 0.115, 0.18, 1), 0.18, metallic=0.05, noise_scale=7.0, bump_strength=0.08),
        "foam": make_material("M_STAGEA_R05_ReviewSurfFoam", (0.78, 0.86, 0.86, 1), 0.44, noise_scale=21.0, bump_strength=0.05),
        "puddle": make_material("M_STAGEA_R05_Puddle", (0.018, 0.055, 0.075, 1), 0.08, metallic=0.04, noise_scale=9.0, bump_strength=0.03),
        "vehicle_red": make_material("M_STAGEA_R05_VehicleRed", (0.31, 0.018, 0.012, 1), 0.26, metallic=0.45, noise_scale=8.0, bump_strength=0.04),
        "vehicle_blue": make_material("M_STAGEA_R05_VehicleBlue", (0.015, 0.085, 0.19, 1), 0.25, metallic=0.48, noise_scale=8.0, bump_strength=0.04),
        "vehicle_white": make_material("M_STAGEA_R05_VehicleWhite", (0.58, 0.62, 0.64, 1), 0.31, metallic=0.28, noise_scale=8.0, bump_strength=0.04),
        "rubber": make_material("M_STAGEA_R05_Rubber", (0.008, 0.009, 0.010, 1), 0.91, noise_scale=22.0, bump_strength=0.12),
    }
'''

R05_ADD_WINDOW = r'''
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
    frame_width = width + 0.30
    frame_height = height + 0.34
    occupancy = ("window_dark", "window_warm", "window_dark", "window_cool", "window_dark")[(variant * 3 + int(abs(x) * 7) + int(z * 5)) % 5]
    result = [
        add_box(prefix + "_Reveal", (x, y - sign * 0.04, z), (frame_width + 0.30, 0.30, frame_height + 0.28), materials["concrete_dark"], target, 0.028),
        add_box(prefix + "_Interior", (x, y - sign * 0.23, z), (width - 0.14, 0.08, height - 0.14), materials[occupancy], target, 0.012),
        add_box(prefix + "_Glass", (x, y + sign * 0.14, z), (width, 0.065, height), materials["glass"], target, 0.018),
        add_box(prefix + "_FrameTop", (x, y + sign * 0.25, z + frame_height * 0.5), (frame_width, 0.14, 0.11), materials["metal"], target, 0.018),
        add_box(prefix + "_FrameBottom", (x, y + sign * 0.25, z - frame_height * 0.5), (frame_width, 0.14, 0.11), materials["metal"], target, 0.018),
        add_box(prefix + "_FrameLeft", (x - frame_width * 0.5, y + sign * 0.25, z), (0.11, 0.14, frame_height), materials["metal"], target, 0.018),
        add_box(prefix + "_FrameRight", (x + frame_width * 0.5, y + sign * 0.25, z), (0.11, 0.14, frame_height), materials["metal"], target, 0.018),
        add_box(prefix + "_MullionV", (x + ((variant % 3) - 1) * width * 0.17, y + sign * 0.27, z), (0.065, 0.15, height), materials["metal"], target, 0.012),
        add_box(prefix + "_Sill", (x, y + sign * 0.42, z - frame_height * 0.5 - 0.08), (frame_width + 0.40, 0.48, 0.14), materials["concrete"], target, 0.025),
        add_box(prefix + "_Drip", (x, y + sign * 0.36, z + frame_height * 0.5 + 0.13), (frame_width + 0.30, 0.34, 0.11), materials["concrete"], target, 0.022),
    ]
    if variant % 3 == 1:
        result.append(add_box(prefix + "_MullionH", (x, y + sign * 0.275, z + 0.20), (width, 0.155, 0.06), materials["metal"], target, 0.012))
    if variant % 4 == 2:
        result.append(add_box(prefix + "_Shade", (x, y + sign * 0.53, z + frame_height * 0.5 + 0.17), (frame_width + 0.52, 0.68, 0.11), materials["metal"], target, 0.025))
    return result
'''

R05_BUILD_SHORE_AND_STREET = r'''
def build_shore_and_street(
    materials: dict[str, bpy.types.Material],
    visible: bpy.types.Collection,
    collision: bpy.types.Collection,
    sockets: bpy.types.Collection,
) -> list[bpy.types.Object]:
    objects = [build_solid_terrain(materials, visible)]
    review_water = collection("REVIEW_ONLY_OCEAN_AND_WEATHER")
    ocean = add_box("REVIEW_ONLY_OceanSurface", (50.0, -27.0, -0.55), (116.0, 55.0, 0.24), materials["ocean"], review_water, 0.04)
    foam = add_box("REVIEW_ONLY_SurfContactFoam", (50.0, -0.35, -0.12), (102.0, 1.35, 0.08), materials["foam"], review_water, 0.018)
    objects.extend([ocean, foam])

    for segment in range(10):
        x = 5.0 + segment * 10.0
        z_seawall = terrain_height(x, 43.0) + 0.75
        objects.append(add_box(f"SM_M01_STAGEA_R05_Seawall_{segment:02d}", (x, 43.0, z_seawall), (9.86, 1.25, 1.5), materials["concrete"], visible, 0.09))
        objects.append(add_box(f"SM_M01_STAGEA_R05_SeawallCoping_{segment:02d}", (x, 43.0, z_seawall + 0.82), (9.90, 1.48, 0.18), materials["concrete_dark"], visible, 0.05))
        objects.append(add_box(f"SM_M01_STAGEA_R05_SeawallStain_{segment:02d}", (x, 42.34, z_seawall - 0.18), (8.95, 0.025, 0.58), materials["water_stain"], visible, 0.006))
        objects.append(add_box(f"SM_M01_STAGEA_R05_Promenade_{segment:02d}", (x, 48.0, terrain_height(x, 48.0) + 0.06), (9.92, 6.8, 0.12), materials["paver"], visible, 0.025))
        objects.append(add_box(f"SM_M01_STAGEA_R05_Curb_{segment:02d}", (x, 53.2, terrain_height(x, 53.2) + 0.11), (9.88, 0.28, 0.22), materials["concrete"], visible, 0.035))
        if segment % 2 == 0:
            drain_x = x + 2.0
            objects.append(add_box(f"SM_M01_STAGEA_R05_DrainGrate_{segment:02d}", (drain_x, 53.45, terrain_height(drain_x, 53.45) + 0.025), (1.15, 0.42, 0.05), materials["metal"], visible, 0.015))
            for slot in (-0.40, -0.20, 0.0, 0.20, 0.40):
                objects.append(add_box(f"SM_M01_STAGEA_R05_DrainSlot_{segment:02d}_{slot:+.2f}", (drain_x + slot, 53.21, terrain_height(drain_x + slot, 53.21) + 0.08), (0.06, 0.31, 0.025), materials["grime"], visible, 0.004))

    for x in range(10, 100, 10):
        wall_z = terrain_height(float(x), 43.0) + 0.74
        objects.append(add_box(f"SM_M01_STAGEA_R05_SeawallJoint_{x:03d}", (float(x), 42.36, wall_z), (0.045, 0.035, 1.32), materials["grime"], visible, 0.004))
    for x in range(5, 100, 5):
        z = terrain_height(float(x), 48.0) + 0.132
        objects.append(add_box(f"SM_M01_STAGEA_R05_PromenadeJoint_{x:03d}", (float(x), 48.0, z), (0.035, 6.55, 0.018), materials["grime"], visible, 0.003))

    road_y = (54.0, 58.0, 62.0)
    road_z = [terrain_height(50.0, y) + offset for y, offset in zip(road_y, (0.06, 0.12, 0.06))]
    road_vertices = [(x, y, z) for x in (0.0, 100.0) for y, z in zip(road_y, road_z)]
    road_faces = [(0, 3, 4, 1), (1, 4, 5, 2)]
    objects.append(create_custom_mesh("SM_M01_STAGEA_R05_RoadCrowned_100m", road_vertices, road_faces, [materials["asphalt"]], visible, [0, 0]))
    for y in (54.22, 61.78):
        objects.append(add_box(f"SM_M01_STAGEA_R05_Gutter_{y:.2f}", (50.0, y, terrain_height(50.0, y) + 0.075), (100.0, 0.28, 0.055), materials["concrete_dark"], visible, 0.015))
    for x in range(5, 100, 10):
        objects.append(add_box(f"SM_M01_STAGEA_R05_RoadMark_{x:03d}", (float(x), 58.0, terrain_height(float(x), 58.0) + 0.15), (4.5, 0.14, 0.025), materials["marking"], visible, 0.008))
    for x in range(10, 100, 20):
        objects.append(add_box(f"SM_M01_STAGEA_R05_RoadPatch_{x:03d}", (float(x), 59.6, terrain_height(float(x), 59.6) + 0.095), (5.3, 1.3, 0.018), materials["concrete_dark"], visible, 0.01, 0.03))

    objects.append(add_box("SM_M01_STAGEA_R05_InlandSidewalk", (50.0, 64.1, terrain_height(50.0, 64.1) + 0.09), (100.0, 3.6, 0.16), materials["paver"], visible, 0.03))
    for x in range(4, 100, 8):
        objects.append(add_box(f"SM_M01_STAGEA_R05_SidewalkJoint_{x:03d}", (float(x), 64.1, terrain_height(float(x), 64.1) + 0.18), (0.035, 3.3, 0.02), materials["grime"], visible, 0.004))

    def add_tree(index: int, x: float, y: float, height: float) -> None:
        z = terrain_height(x, y)
        trunk = add_cylinder(f"SM_M01_STAGEA_R05_Tree_{index:02d}_Trunk", (x, y, z + height * 0.33), 0.17, height * 0.66, materials["trunk"], visible, 14, 0.035)
        objects.append(trunk)
        for crown_index, (dx, dy, dz, scale) in enumerate(((0.0, 0.0, 0.0, 1.0), (-0.48, 0.10, -0.12, 0.74), (0.42, -0.18, -0.04, 0.78), (0.06, 0.34, 0.36, 0.62))):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=height * 0.23 * scale, location=(x + dx, y + dy, z + height * 0.72 + dz))
            crown = bpy.context.object
            crown.name = f"SM_M01_STAGEA_R05_Tree_{index:02d}_Crown_{crown_index:02d}"
            crown.scale.z = 1.18
            apply_transforms(crown)
            crown.data.materials.append(materials["foliage" if (index + crown_index) % 2 else "foliage_dark"])
            ensure_uvs(crown)
            move_object(crown, visible)
            objects.append(crown)
        objects.append(add_box(f"SM_M01_STAGEA_R05_Tree_{index:02d}_Planter", (x, y, z + 0.30), (1.55, 1.55, 0.60), materials["concrete_dark"], visible, 0.09))

    for index, x in enumerate((6.0, 14.0, 26.0, 34.0, 46.0, 54.0, 66.0, 74.0, 86.0, 94.0)):
        add_tree(index, x, 50.2 if index % 2 == 0 else 65.0, 4.2 + (index % 3) * 0.55)

    def add_streetlight(index: int, x: float, y: float) -> None:
        z = terrain_height(x, y)
        objects.append(add_cylinder(f"SM_M01_STAGEA_R05_Streetlight_{index:02d}_Pole", (x, y, z + 2.9), 0.075, 5.8, materials["metal"], visible, 16, 0.022))
        objects.append(add_box(f"SM_M01_STAGEA_R05_Streetlight_{index:02d}_Arm", (x + 0.42, y, z + 5.70), (0.88, 0.07, 0.07), materials["metal"], visible, 0.018))
        objects.append(add_box(f"SM_M01_STAGEA_R05_Streetlight_{index:02d}_Lamp", (x + 0.84, y, z + 5.62), (0.48, 0.22, 0.16), materials["window_warm"], visible, 0.035))

    for index, x in enumerate(range(5, 100, 10)):
        add_streetlight(index, float(x), 52.0)
        if index % 2 == 0:
            z = terrain_height(float(x), 48.7)
            objects.append(add_box(f"SM_M01_STAGEA_R05_Bench_{index:02d}_Seat", (float(x), 48.7, z + 0.62), (2.0, 0.55, 0.12), materials["metal"], visible, 0.04))
            objects.append(add_box(f"SM_M01_STAGEA_R05_Bench_{index:02d}_Back", (float(x), 49.0, z + 1.02), (2.0, 0.10, 0.72), materials["metal"], visible, 0.035))

    def add_vehicle(index: int, x: float, y: float, material_key: str) -> None:
        z = terrain_height(x, y)
        objects.append(add_box(f"SM_M01_STAGEA_R05_Vehicle_{index:02d}_Body", (x, y, z + 0.68), (4.15, 1.76, 0.78), materials[material_key], visible, 0.18))
        objects.append(add_box(f"SM_M01_STAGEA_R05_Vehicle_{index:02d}_Cabin", (x - 0.20, y, z + 1.28), (2.35, 1.58, 0.72), materials["glass"], visible, 0.18))
        objects.append(add_box(f"SM_M01_STAGEA_R05_Vehicle_{index:02d}_BumperF", (x - 2.10, y, z + 0.48), (0.15, 1.72, 0.25), materials["metal"], visible, 0.03))
        objects.append(add_box(f"SM_M01_STAGEA_R05_Vehicle_{index:02d}_BumperR", (x + 2.10, y, z + 0.48), (0.15, 1.72, 0.25), materials["metal"], visible, 0.03))
        for wheel_index, (dx, dy) in enumerate(((-1.35, -0.91), (-1.35, 0.91), (1.35, -0.91), (1.35, 0.91))):
            wheel = add_cylinder(f"SM_M01_STAGEA_R05_Vehicle_{index:02d}_Wheel_{wheel_index:02d}", (x + dx, y + dy, z + 0.44), 0.38, 0.22, materials["rubber"], visible, 20, 0.025)
            wheel.rotation_euler = (math.radians(90.0), 0.0, 0.0)
            apply_transforms(wheel)
            objects.append(wheel)

    vehicle_specs = ((10.0, 56.2, "vehicle_red"), (22.0, 60.0, "vehicle_white"), (35.0, 56.2, "vehicle_blue"), (47.0, 60.0, "vehicle_white"), (59.0, 56.2, "vehicle_red"), (72.0, 60.0, "vehicle_blue"), (84.0, 56.2, "vehicle_white"), (94.0, 60.0, "vehicle_red"))
    for index, (x, y, material_key) in enumerate(vehicle_specs):
        add_vehicle(index, x, y, material_key)

    puddle_specs = ((18.0, 57.0, 5.0, 1.6), (41.0, 59.0, 7.0, 1.9), (64.0, 56.5, 4.6, 1.4), (88.0, 59.4, 6.4, 1.7), (29.0, 48.6, 3.2, 0.8), (76.0, 48.2, 4.1, 0.9))
    for index, (x, y, length, width) in enumerate(puddle_specs):
        objects.append(add_box(f"SM_M01_STAGEA_R05_Puddle_{index:02d}", (x, y, terrain_height(x, y) + 0.18), (length, width, 0.025), materials["puddle"], visible, 0.012, 0.07 if index % 2 else -0.05))

    add_collision_box("UCX_SM_M01_STAGEA_R05_TerrainDistrict_100x80_00", (50.0, 40.0, 0.0), (100.0, 80.0, 4.0), collision)
    add_collision_box("UCX_SM_M01_STAGEA_R05_Seawall_00", (50.0, 43.0, 2.4), (100.0, 1.4, 2.0), collision)
    add_collision_box("UCX_SM_M01_STAGEA_R05_RoadCrowned_100m_00", (50.0, 58.0, 2.4), (100.0, 8.0, 0.4), collision)
    add_socket("SOCKET_District_W", (0.0, 0.0, terrain_height(0.0, 0.0)), sockets)
    add_socket("SOCKET_District_E", (100.0, 0.0, terrain_height(100.0, 0.0)), sockets)
    add_socket("SOCKET_District_S", (50.0, 0.0, terrain_height(50.0, 0.0)), sockets)
    add_socket("SOCKET_District_N", (50.0, 80.0, terrain_height(50.0, 80.0)), sockets)
    return objects
'''

R05_BUILD_MIDRISE = r'''
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
    style_index = max(0, min(4, ord(facade_style[0].upper()) - ord("A")))
    ground_z = terrain_height(center_x, 72.5)
    floor_height = 3.0
    ground_floor = 3.6
    height = ground_floor + (floors - 1) * floor_height
    front_y, back_y = 66.66, 78.34
    wall_keys = ("plaster_fde", "plaster_blue", "brick", "plaster_green", "plaster_warm")
    accent_keys = ("brick", "tile", "plaster_warm", "concrete_dark", "plaster_blue")
    wall_material = materials[wall_keys[style_index]]
    accent_material = materials[accent_keys[style_index]]
    objects = [
        add_box(name + "_Core", (center_x, 72.5, ground_z + height * 0.5), (18.0, 11.2, height), wall_material, target, 0.16),
        add_box(name + "_Foundation", (center_x, 72.5, ground_z - 0.32), (18.4, 11.6, 0.64), materials["concrete_dark"], target, 0.08),
        add_box(name + "_GroundPlinthFront", (center_x, front_y - 0.20, ground_z + 0.62), (17.65, 0.26, 1.24), materials["concrete_dark"], target, 0.035),
        add_box(name + "_GroundPlinthRear", (center_x, back_y + 0.20, ground_z + 0.62), (17.65, 0.26, 1.24), materials["concrete_dark"], target, 0.035),
    ]
    bay_patterns = (
        [(-7.10, 1.28), (-4.45, 1.72), (-1.40, 1.44), (1.40, 1.44), (4.45, 1.72), (7.10, 1.28)],
        [(-7.15, 1.55), (-4.20, 1.32), (-1.50, 1.82), (1.50, 1.82), (4.20, 1.32), (7.15, 1.55)],
        [(-7.20, 1.22), (-4.72, 1.22), (-1.60, 1.92), (1.60, 1.92), (4.72, 1.22), (7.20, 1.22)],
        [(-7.0, 1.70), (-3.85, 1.48), (-1.20, 1.20), (1.20, 1.20), (3.85, 1.48), (7.0, 1.70)],
        [(-7.25, 1.38), (-4.40, 1.82), (-1.35, 1.38), (1.35, 1.38), (4.40, 1.82), (7.25, 1.38)],
    )
    bay_specs = bay_patterns[style_index]
    service_x = center_x + (-6.15, 5.85, -4.9, 6.1, 0.0)[style_index]
    service_width = (1.75, 2.25, 1.35, 1.9, 3.0)[style_index]
    objects.append(add_box(name + "_ServiceBand", (service_x, front_y - 0.26, ground_z + height * 0.5), (service_width, 0.34, height - 0.45), accent_material, target, 0.05))
    objects.append(add_box(name + "_ServiceBandInset", (service_x, front_y - 0.46, ground_z + height * 0.55), (service_width * 0.32, 0.08, height * 0.62), materials["grime"], target, 0.016))

    for floor in range(1, floors):
        z_course = ground_z + ground_floor + (floor - 1) * floor_height
        if (floor + style_index) % 2 == 0:
            objects.append(add_box(f"{name}_StringCourse_{floor:02d}", (center_x, front_y - 0.27, z_course + 0.03), (17.75, 0.34, 0.13), materials["concrete"], target, 0.022))

    for floor in range(floors):
        z = ground_z + (1.86 if floor == 0 else ground_floor + (floor - 1) * floor_height + 1.50)
        for bay_index, (offset, width) in enumerate(bay_specs):
            if floor == 0 and bay_index in ((2, 3) if style_index != 4 else (1, 4)):
                continue
            variant = style_index * 7 + floor * 3 + bay_index
            objects.extend(add_window(f"{name}_F{floor:02d}_B{bay_index:02d}_Front", center_x + offset, front_y, z, True, materials, target, width, 1.64 if floor else 1.82, variant))
            if (bay_index + floor + style_index) % 3 != 1:
                objects.extend(add_window(f"{name}_F{floor:02d}_B{bay_index:02d}_Rear", center_x + offset, back_y, z, False, materials, target, max(1.18, width - 0.14), 1.52, variant + 11))

        if floor > 0 and style_index in (0, 1, 2, 4):
            groups = ((-4.6, 3.1), (-1.7, 5.8), (-5.7, 1.5), (-3.2, 4.7), (-6.0, 1.8))[style_index]
            for group_index, balcony_x in enumerate(groups):
                if (floor + group_index + style_index) % 2 == 0 or style_index == 1:
                    objects.extend(add_balcony(f"{name}_F{floor:02d}_Balcony_{group_index:02d}", center_x + balcony_x, front_y, z, materials, target, 3.55 if group_index == 0 else 3.05))

        if floor in tuple(range(1, floors, 2)) + (floors - 1,):
            for side_y_index, side_y in enumerate((69.5, 72.5, 75.5)):
                objects.extend(add_side_window(f"{name}_F{floor:02d}_SideL_{side_y_index:02d}", center_x - 9.0, side_y, z, False, materials, target))
                if (floor + side_y_index + style_index) % 2 == 0:
                    objects.extend(add_side_window(f"{name}_F{floor:02d}_SideR_{side_y_index:02d}", center_x + 9.0, side_y, z, True, materials, target))

    portal_x = center_x + (-0.5, 1.3, -1.4, 0.8, 0.0)[style_index]
    objects.append(add_box(name + "_EntrancePortal", (portal_x, front_y - 0.28, ground_z + 1.68), (4.2 + style_index * 0.18, 0.60, 3.36), accent_material, target, 0.09))
    objects.append(add_box(name + "_EntranceRecess", (portal_x, front_y - 0.62, ground_z + 1.58), (3.10, 0.14, 2.94), materials["grime"], target, 0.025))
    objects.append(add_box(name + "_EntranceGlass", (portal_x, front_y - 0.72, ground_z + 1.55), (2.82, 0.07, 2.72), materials["glass"], target, 0.018))
    objects.append(add_box(name + "_EntranceCanopy", (portal_x, front_y - 1.24, ground_z + 3.12), (4.8, 1.72, 0.18), materials["metal"], target, 0.05))
    objects.append(add_box(name + "_ShopSign", (center_x + (4.2 if style_index % 2 else -4.2), front_y - 0.52, ground_z + 3.05), (5.0, 0.12, 0.72), materials["tile"], target, 0.03))

    for x_offset in (-8.74, 8.74):
        objects.append(add_box(name + f"_CornerPilaster_{x_offset:+.2f}", (center_x + x_offset, front_y - 0.16, ground_z + height * 0.5), (0.40, 0.42, height), materials["concrete"], target, 0.055))
        objects.append(add_box(name + f"_Downspout_{x_offset:+.2f}", (center_x + x_offset * 0.96, front_y - 0.47, ground_z + height * 0.48), (0.12, 0.14, height * 0.92), materials["metal"], target, 0.025))
        objects.append(add_box(name + f"_DownspoutStain_{x_offset:+.2f}", (center_x + x_offset * 0.96, front_y - 0.37, ground_z + height * 0.30), (0.34, 0.035, height * 0.48), materials["water_stain"], target, 0.012))

    roof_z = ground_z + height
    objects.append(add_box(name + "_Roof", (center_x, 72.5, roof_z + 0.18), (18.0, 11.2, 0.36), materials["roof"], target, 0.05))
    for x_offset in (-8.75, 8.75):
        objects.append(add_box(name + f"_ParapetLong_{x_offset:+.2f}", (center_x + x_offset, 72.5, roof_z + 0.72), (0.24, 11.2, 1.1), materials["concrete"], target, 0.04))
        objects.append(add_box(name + f"_ParapetCopingLong_{x_offset:+.2f}", (center_x + x_offset, 72.5, roof_z + 1.30), (0.38, 11.35, 0.10), materials["metal"], target, 0.025))
    for y in (67.02, 77.98):
        objects.append(add_box(name + f"_ParapetShort_{y:.2f}", (center_x, y, roof_z + 0.72), (17.5, 0.24, 1.1), materials["concrete"], target, 0.04))
        objects.append(add_box(name + f"_ParapetCopingShort_{y:.2f}", (center_x, y, roof_z + 1.30), (17.65, 0.38, 0.10), materials["metal"], target, 0.025))
    access_x = center_x + (-3.8, 3.6, -1.2, 4.0, -4.1)[style_index]
    objects.append(add_box(name + "_RoofAccess", (access_x, 73.1, roof_z + 1.42), (3.8 + style_index * 0.15, 3.05, 2.48), wall_material, target, 0.11))
    objects.append(add_box(name + "_RoofAccessCoping", (access_x, 73.1, roof_z + 2.72), (4.15 + style_index * 0.15, 3.36, 0.12), materials["metal"], target, 0.03))
    objects.append(add_box(name + "_RoofAccessDoor", (access_x, 71.54, roof_z + 1.20), (1.15, 0.08, 2.05), materials["metal"], target, 0.025))
    for unit_index, (dx, dy, sx, sy) in enumerate(((-5.7, -1.2, 2.1, 1.3), (-2.0, 2.2, 1.4, 1.0), (5.2, 1.0, 2.4, 1.6))):
        objects.append(add_box(name + f"_RoofHVAC_{unit_index:02d}", (center_x + dx, 72.5 + dy, roof_z + 0.92), (sx, sy, 1.15), materials["metal"], target, 0.08))
        objects.append(add_box(name + f"_RoofHVACGrille_{unit_index:02d}", (center_x + dx, 72.5 + dy - sy * 0.51, roof_z + 0.92), (sx * 0.72, 0.035, 0.62), materials["grime"], target, 0.008))
    antenna_x = center_x + (6.0 if style_index % 2 == 0 else -6.0)
    objects.append(add_cylinder(name + "_RoofAntennaMast", (antenna_x, 74.2, roof_z + 2.7), 0.055, 4.0, materials["metal"], target, 12, 0.012))

    add_collision_box("UCX_" + name + "_00", (center_x, 72.5, ground_z + height * 0.5), (18.0, 11.2, height), collision)
    add_socket("SOCKET_" + name + "_Origin", (center_x - 9.0, 66.9, ground_z), sockets)
    return objects
'''

R05_BUILD_FACADE_EXPORT_MODULES = r'''
def build_facade_export_modules(materials: dict[str, bpy.types.Material], target: bpy.types.Collection) -> list[bpy.types.Object]:
    return []
'''

R05_ADD_REVIEW_RIG = r'''
def add_review_rig(scene: bpy.types.Scene) -> dict[str, Any]:
    review = collection("REVIEW_ONLY_RIG")
    camera_data = bpy.data.cameras.new("CAM_STAGEA_R05_Checkpoint")
    camera = bpy.data.objects.new("CAM_STAGEA_R05_Checkpoint", camera_data)
    review.objects.link(camera)
    camera.data.lens = 52.0
    camera.data.clip_start = 0.10
    camera.data.clip_end = 650.0
    scene.camera = camera

    bpy.ops.object.light_add(type="SUN", location=(50.0, 20.0, 80.0))
    sun = bpy.context.object
    sun.name = "LIGHT_STAGEA_R05_Sun"
    sun.data.energy = 3.0
    sun.data.angle = math.radians(0.535)
    sun.rotation_euler = (math.radians(34.0), math.radians(-16.0), math.radians(-38.0))
    move_object(sun, review)

    bpy.ops.object.light_add(type="AREA", location=(45.0, 28.0, 42.0))
    fill = bpy.context.object
    fill.name = "LIGHT_STAGEA_R05_Fill"
    fill.data.energy = 1350.0
    fill.data.shape = "DISK"
    fill.data.size = 55.0
    fill.rotation_euler = (math.radians(24.0), 0.0, math.radians(18.0))
    move_object(fill, review)

    bpy.ops.object.light_add(type="AREA", location=(70.0, 42.0, 40.0))
    moon = bpy.context.object
    moon.name = "LIGHT_STAGEA_R05_MoonKey"
    moon.data.energy = 0.0
    moon.data.color = (0.22, 0.40, 0.82)
    moon.data.shape = "DISK"
    moon.data.size = 36.0
    moon.rotation_euler = (math.radians(29.0), 0.0, math.radians(-44.0))
    move_object(moon, review)

    practicals: list[bpy.types.Object] = []
    for index, x in enumerate(range(5, 100, 10)):
        bpy.ops.object.light_add(type="POINT", location=(float(x) + 0.8, 52.0, terrain_height(float(x), 52.0) + 5.6))
        light = bpy.context.object
        light.name = f"LIGHT_STAGEA_R05_Promenade_{index:02d}"
        light.data.energy = 0.0
        light.data.color = (1.0, 0.43, 0.17)
        light.data.shadow_soft_size = 1.25
        move_object(light, review)
        practicals.append(light)

    rain = collection("REVIEW_ONLY_RAIN")
    for index in range(72):
        x = 1.5 + ((index * 17) % 97)
        y = -8.0 + ((index * 29) % 92)
        z = 3.0 + ((index * 13) % 32)
        drop = add_box(f"REVIEW_ONLY_RainStreak_{index:03d}", (x, y, z), (0.018, 0.018, 2.2 + (index % 5) * 0.3), bpy.data.materials["M_STAGEA_R05_WindowInteriorCool"], rain, 0.004, -0.10)
        drop.hide_render = True

    world_nodes = scene.world.node_tree.nodes
    world_links = scene.world.node_tree.links
    volume = world_nodes.new("ShaderNodeVolumeScatter")
    volume.name = "VOLUME_STAGEA_R05_Atmosphere"
    volume.inputs["Color"].default_value = (0.20, 0.28, 0.34, 1.0)
    volume.inputs["Density"].default_value = 0.0
    output = world_nodes.get("World Output")
    if output is not None:
        world_links.new(volume.outputs["Volume"], output.inputs["Volume"])
    return {"camera": camera, "sun": sun, "fill": fill, "moon": moon, "practicals": practicals, "rain": rain, "volume": volume}
'''

R05_CONFIGURE_CONDITION = r'''
def configure_condition(scene: bpy.types.Scene, rig: dict[str, Any], condition: str, materials: dict[str, bpy.types.Material]) -> None:
    background = scene.world.node_tree.nodes["Background"]
    values = {
        "daylight": ((0.16, 0.29, 0.52, 1.0), 0.50, 3.15, 1320.0, 0.0, 0.0, 0.0, 0.0),
        "night": ((0.018, 0.038, 0.090, 1.0), 0.20, 0.32, 1280.0, 1180.0, 410.0, 1.05, 0.0015),
        "storm": ((0.045, 0.065, 0.085, 1.0), 0.30, 0.62, 1180.0, 220.0, 105.0, 0.32, 0.010),
    }
    color, strength, sun_energy, fill_energy, moon_energy, practical_energy, exposure, fog_density = values[condition]
    background.inputs["Color"].default_value = color
    background.inputs["Strength"].default_value = strength
    rig["sun"].data.energy = sun_energy
    rig["fill"].data.energy = fill_energy
    rig["moon"].data.energy = moon_energy
    for practical in rig["practicals"]:
        practical.data.energy = practical_energy
    scene.view_settings.exposure = exposure
    rig["volume"].inputs["Density"].default_value = fog_density
    for obj in rig["rain"].objects:
        obj.hide_render = condition != "storm"
    for obj in bpy.data.objects:
        if obj.name.startswith("SM_M01_STAGEA_R05_Puddle_"):
            obj.hide_render = condition != "storm"
    for key, strength_value in (("window_warm", 3.1), ("window_cool", 2.4)):
        bsdf = materials[key].node_tree.nodes.get("Principled BSDF")
        if bsdf is not None and bsdf.inputs.get("Emission Strength") is not None:
            bsdf.inputs["Emission Strength"].default_value = strength_value if condition == "night" else 0.7 if condition == "storm" else 0.0
    wet = condition == "storm"
    materials["wet_sand"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.13 if wet else 0.25
    materials["asphalt"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.31 if wet else 0.86
    materials["concrete"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.43 if wet else 0.68
    materials["paver"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.36 if wet else 0.75
    materials["ocean"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.09 if wet else 0.18
'''

R05_RENDER_CHECKPOINTS = r'''
def render_checkpoints(scene: bpy.types.Scene, rig: dict[str, Any], output: Path, materials: dict[str, bpy.types.Material]) -> list[dict[str, Any]]:
    scene.render.resolution_x, scene.render.resolution_y = (1920, 1080)
    cameras = {
        "coastal_route": ((50.0, -54.0, 22.0), (50.0, 54.0, 7.0), 52.0),
        "street_close": ((24.0, 39.0, 9.5), (31.0, 72.0, 8.0), 58.0),
        "district_aerial": ((50.0, -42.0, 44.0), (50.0, 52.0, 7.0), 50.0),
    }
    results: list[dict[str, Any]] = []
    for condition in ("daylight", "night", "storm"):
        configure_condition(scene, rig, condition, materials)
        for camera_id, (location, target, lens) in cameras.items():
            point_camera(rig["camera"], location, target, lens)
            path = output / "renders" / "checkpoints" / f"{condition}_{camera_id}.png"
            metrics = render_and_measure(scene, path)
            require((metrics["width"], metrics["height"]) == (1920, 1080), f"Checkpoint resolution failed: {condition}_{camera_id}")
            minimum_luma = 0.008 if condition == "night" else 0.018 if condition == "storm" else 0.030
            maximum_black = 0.70 if condition == "night" else 0.58 if condition == "storm" else 0.35
            require(metrics["mean_luma_linear"] >= minimum_luma, f"Checkpoint is too dark: {condition}_{camera_id}")
            require(metrics["black_fraction_linear_0_01"] <= maximum_black, f"Checkpoint is excessively black: {condition}_{camera_id}")
            results.append({"condition": condition, "camera": camera_id, "path": str(path), "metrics": metrics, "passed": True})
    require(len(results) == 9, "Checkpoint render count is not exactly nine")
    return results
'''

R05_MAIN = r'''
def main() -> int:
    args = parse_args()
    require(args.asset_id == ASSET_ID, f"Unexpected asset id: {args.asset_id}")
    source_path = Path(__file__).resolve()
    require(sha256(source_path) == args.expected_source_sha256.lower(), "Attempt source hash does not match the frozen authority")
    output = Path(args.output).resolve()
    require(not output.exists(), f"Output namespace already exists: {output}")
    output.mkdir(parents=True)

    scene = reset_scene()
    root = collection("M01_VISIBLE_ENVIRONMENT_KIT_STAGEA_RECOVERY05_CHECKPOINT01")
    district = collection("ASSET_CoastalDistrict", root)
    collision = collection("COLLISION_CoastalDistrict", root)
    sockets = collection("SOCKETS_CoastalDistrict", root)
    materials = build_materials()
    build_shore_and_street(materials, district, collision, sockets)
    building_specs = ((10.0, 5, "A"), (30.0, 7, "B"), (50.0, 4, "C"), (70.0, 6, "D"), (90.0, 5, "E"))
    for index, (center_x, floors, style) in enumerate(building_specs, 1):
        build_midrise(f"SM_M01_STAGEA_R05_Midrise_{style}_{index:02d}", center_x, floors, style, materials, district, collision, sockets)
    rig = add_review_rig(scene)
    checkpoints = render_checkpoints(scene, rig, output, materials)

    blend_path = output / "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    stats = collection_stats((district, collision, sockets))
    district_bounds = bounds_for((district,))
    dimension_receipt = {
        "schema": "skyguard.m01-visible-environment-kit.stagea-recovery05-checkpoint01.dimension-receipt.v1",
        "gate": GATE,
        "district_authority_m": [DISTRICT_LENGTH_M, DISTRICT_WIDTH_M],
        "observed_visible_bounds": district_bounds,
        "review_ocean_excluded_from_export_bounds": True,
        "building_count": 5,
        "facade_style_count": 5,
        "passed": abs(district_bounds["min_m"][0]) <= 0.01 and abs(district_bounds["max_m"][0] - 100.0) <= 0.01 and abs(district_bounds["min_m"][1]) <= 0.01 and abs(district_bounds["max_m"][1] - 80.0) <= 0.01,
    }
    require(dimension_receipt["passed"], f"District dimension contract failed: {district_bounds}")
    structural_counts = {
        "buildings": len([obj for obj in bpy.data.objects if obj.name.endswith("_Core") and "R05_Midrise" in obj.name]),
        "vehicles": len([obj for obj in bpy.data.objects if obj.name.startswith("SM_M01_STAGEA_R05_Vehicle_") and obj.name.endswith("_Body")]),
        "trees": len([obj for obj in bpy.data.objects if obj.name.startswith("SM_M01_STAGEA_R05_Tree_") and obj.name.endswith("_Trunk")]),
        "streetlights": len([obj for obj in bpy.data.objects if obj.name.startswith("SM_M01_STAGEA_R05_Streetlight_") and obj.name.endswith("_Pole")]),
        "puddles": len([obj for obj in bpy.data.objects if obj.name.startswith("SM_M01_STAGEA_R05_Puddle_")]),
        "review_ocean": len([obj for obj in bpy.data.objects if obj.name == "REVIEW_ONLY_OceanSurface"]),
        "review_surf_foam": len([obj for obj in bpy.data.objects if obj.name == "REVIEW_ONLY_SurfContactFoam"]),
    }
    require(structural_counts == {"buildings": 5, "vehicles": 8, "trees": 10, "streetlights": 10, "puddles": 6, "review_ocean": 1, "review_surf_foam": 1}, f"Structural checkpoint counts failed: {structural_counts}")
    atomic_json(output / "dimension_receipt.json", dimension_receipt)
    atomic_json(output / "topology_uv_receipt.json", {"schema":"skyguard.m01-visible-environment-kit.stagea-recovery05-checkpoint01.topology-uv.v1","gate":GATE,"statistics":stats,"structural_counts":structural_counts,"passed":True})
    atomic_json(output / "checkpoint_receipt.json", {"schema":"skyguard.m01-visible-environment-kit.stagea-recovery05-checkpoint01.checkpoints.v1","gate":GATE,"resolution":[1920,1080],"conditions":["daylight","night","storm"],"cameras":["coastal_route","street_close","district_aerial"],"checkpoints":checkpoints,"count":len(checkpoints),"passed":len(checkpoints)==9})
    atomic_json(output / "source_parity_receipt.json", {"schema":"skyguard.m01-visible-environment-kit.stagea-recovery05-checkpoint01.source-parity.v1","source":str(source_path),"bytes":source_path.stat().st_size,"sha256":sha256(source_path),"expected_sha256":args.expected_source_sha256.lower(),"passed":True})
    artifact_path = output / "artifact_inventory.json"
    terminal_path = output / "terminal_receipt.json"
    atomic_json(artifact_path, {"schema":"skyguard.m01-visible-environment-kit.stagea-recovery05-checkpoint01.inventory.v1","gate":GATE,"files":inventory(output,{artifact_path,terminal_path})})
    atomic_json(terminal_path, {
        "schema":"skyguard.m01-visible-environment-kit.stagea-recovery05-checkpoint01.terminal.v1",
        "gate":GATE,
        "asset_id":ASSET_ID,
        "status":"CHECKPOINT_COMPLETED_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW",
        "created_utc":utc_now(),
        "blend_count":1,
        "glb_count":0,
        "checkpoint_count":9,
        "final_render_count":0,
        "texture_count":0,
        "automatic_validation_passed":True,
        "human_visual_acceptance":"NOT_PERFORMED",
        "finalization_authorized":False,
    })
    print(json.dumps({"gate":GATE,"status":"CHECKPOINT_COMPLETED_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW","output":str(output)}))
    return 0
'''

REPLACEMENTS = {
    "make_material": MAKE_MATERIAL,
    "build_materials": R05_BUILD_MATERIALS,
    "build_shore_and_street": R05_BUILD_SHORE_AND_STREET,
    "add_window": R05_ADD_WINDOW,
    "add_balcony": ADD_BALCONY,
    "build_midrise": R05_BUILD_MIDRISE,
    "build_facade_export_modules": R05_BUILD_FACADE_EXPORT_MODULES,
    "add_review_rig": R05_ADD_REVIEW_RIG,
    "configure_condition": R05_CONFIGURE_CONDITION,
    "render_and_measure": RENDER_AND_MEASURE,
    "render_checkpoints": R05_RENDER_CHECKPOINTS,
    "main": R05_MAIN,
}


def load_recovery05_source() -> tuple[str, dict[str, object]]:
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
    tree = ast.parse(source)
    main_nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]
    if len(main_nodes) != 1:
        raise RuntimeError("Embedded checkpoint main cardinality is not one")
    calls = [node.func.id for node in ast.walk(main_nodes[0]) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
    for forbidden_call in ("create_texture_atlas", "render_final_views", "export_glb"):
        if forbidden_call in calls:
            raise RuntimeError(f"Checkpoint main contains forbidden finalization call: {forbidden_call}")
    required = (
        'GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01"',
        'require(len(results) == 9, "Checkpoint render count is not exactly nine")',
        '"status":"CHECKPOINT_COMPLETED_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW"',
        '"finalization_authorized":False',
        '"review_ocean": 1',
        '"buildings": 5',
    )
    for token in required:
        if token not in source:
            raise RuntimeError(f"Required Recovery05 token is absent: {token}")
    receipt = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery05-checkpoint01.in-memory-rebuild.v1",
        "gate": GATE,
        "base_source": str(BASE_SOURCE),
        "base_bytes": BASE_BYTES,
        "base_sha256": BASE_SHA256,
        "function_replacements": sorted(REPLACEMENTS),
        "function_replacement_count": len(REPLACEMENTS),
        "recovery04_output_geometry_reused": False,
        "checkpoint_only": True,
        "checkpoint_count": 9,
        "final_render_count": 0,
        "texture_count": 0,
        "glb_count": 0,
        "finalization_authorized": False,
        "passed": True,
    }
    return source, receipt


def main() -> int:
    corrected, receipt = load_recovery05_source()
    print(json.dumps(receipt, sort_keys=True))
    namespace: dict[str, object] = {
        "__name__": "skyguard_stagea_recovery05_checkpoint01_embedded",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
    }
    exec(compile(corrected, str(Path(__file__).resolve()), "exec"), namespace)
    embedded_main = namespace.get("main")
    if not callable(embedded_main):
        raise RuntimeError("Recovery05 checkpoint embedded main is unavailable")
    return int(embedded_main())


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"gate": GATE, "status": "FAILED_WITH_EVIDENCE", "error": f"{type(exc).__name__}: {exc}"}), file=sys.stderr)
        raise
