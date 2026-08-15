from __future__ import annotations

"""Build the first production-look Mission 1 streetscape/shoreline proof.

This is intentionally a small hero-quality proof, not another generated city.
It creates fresh geometry, uses only already-governed local texture authorities,
and exports a bounded Blender/GLB package for direct visual adjudication.
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Callable

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
ASSET_ID = "m01-environment-hero-streetshore-proof01"
GATE = "M01_ENVIRONMENT_PRODUCTION_RESET01_HERO_STREETSHORE_PROOF01"
TEXTURE_ROOT = ROOT / r"Content\Skyguard\Textures"

PBR_SOURCES = {
    "plaster": {
        "base": TEXTURE_ROOT / r"PolyHaven\painted_plaster_wall\painted_plaster_wall_diff_2k.jpg",
        "normal": TEXTURE_ROOT / r"PolyHaven\painted_plaster_wall\painted_plaster_wall_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / r"PolyHaven\painted_plaster_wall\painted_plaster_wall_rough_2k.jpg",
    },
    "concrete": {
        "base": TEXTURE_ROOT / r"PolyHaven\concrete_wall_008\concrete_wall_008_diff_2k.jpg",
        "normal": TEXTURE_ROOT / r"PolyHaven\concrete_wall_008\concrete_wall_008_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / r"PolyHaven\concrete_wall_008\concrete_wall_008_rough_2k.jpg",
    },
    "asphalt": {
        "base": TEXTURE_ROOT / r"PolyHaven\asphalt_02\asphalt_02_diff_2k.jpg",
        "normal": TEXTURE_ROOT / r"PolyHaven\asphalt_02\asphalt_02_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / r"PolyHaven\asphalt_02\asphalt_02_rough_2k.jpg",
    },
    "sand": {
        "base": TEXTURE_ROOT / r"PolyHaven\coast_sand_01\coast_sand_01_diff_2k.jpg",
        "normal": TEXTURE_ROOT / r"PolyHaven\coast_sand_01\coast_sand_01_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / r"PolyHaven\coast_sand_01\coast_sand_01_rough_2k.jpg",
    },
    "roof": {
        "base": TEXTURE_ROOT / r"PolyHaven\roof_07\roof_07_diff_2k.jpg",
        "normal": TEXTURE_ROOT / r"PolyHaven\roof_07\roof_07_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / r"PolyHaven\roof_07\roof_07_rough_2k.jpg",
    },
    "metal": {
        "base": TEXTURE_ROOT / r"PolyHaven\metal_plate\metal_plate_diff_2k.jpg",
        "normal": TEXTURE_ROOT / r"PolyHaven\metal_plate\metal_plate_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / r"PolyHaven\metal_plate\metal_plate_rough_2k.jpg",
        "metallic": TEXTURE_ROOT / r"PolyHaven\metal_plate\metal_plate_metal_2k.jpg",
    },
}
WINDOW_ATLAS = TEXTURE_ROOT / r"WebPBR\city-window-interior-atlas.webp"
PROVENANCE = TEXTURE_ROOT / r"PolyHaven\polyhaven-provenance-manifest.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    raw = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", required=True)
    return parser.parse_args(raw)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def get_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    for source in list(obj.users_collection):
        source.objects.unlink(obj)
    target.objects.link(obj)


def apply_transforms(obj: bpy.types.Object) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


def add_bevel(obj: bpy.types.Object, width: float, segments: int = 3) -> None:
    if width <= 0.0:
        return
    modifier = obj.modifiers.new("ProductionEdgeBevel", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"


def smart_uv(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.025)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)


def add_box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    target: bpy.types.Collection,
    bevel: float = 0.04,
    rotation_z: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=(0.0, 0.0, rotation_z))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    apply_transforms(obj)
    add_bevel(obj, min(bevel, min(dimensions) * 0.24), 3)
    obj.data.materials.append(material)
    move_to_collection(obj, target)
    return obj


def add_cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
    vertices: int = 32,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.025,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    apply_transforms(obj)
    add_bevel(obj, bevel, 2)
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    move_to_collection(obj, target)
    return obj


def add_icosphere(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    apply_transforms(obj)
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    move_to_collection(obj, target)
    return obj


def add_custom_mesh(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    material: bpy.types.Material,
    target: bpy.types.Collection,
    bevel: float = 0.0,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    obj.data.materials.append(material)
    if bevel:
        add_bevel(obj, bevel, 2)
    smart_uv(obj)
    return obj


def add_curve_strip(
    name: str,
    points: list[tuple[float, float, float]],
    radius: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    curve_data = bpy.data.curves.new(name + "_Curve", "CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = 3
    spline = curve_data.splines.new("NURBS")
    spline.points.add(len(points) - 1)
    for index, point in enumerate(points):
        spline.points[index].co = (*point, 1.0)
    spline.order_u = min(4, len(points))
    spline.use_endpoint_u = True
    obj = bpy.data.objects.new(name, curve_data)
    curve_data.materials.append(material)
    target.objects.link(obj)
    return obj


def cylinder_between(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    a, b = Vector(start), Vector(end)
    direction = b - a
    midpoint = (a + b) * 0.5
    obj = add_cylinder(name, tuple(midpoint), radius, direction.length, material, target, 20, bevel=radius * 0.25)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    obj.rotation_mode = "XYZ"
    return obj


def load_image(path: Path, non_color: bool = False) -> bpy.types.Image:
    require(path.is_file(), f"Missing governed texture: {path}")
    image = bpy.data.images.load(str(path), check_existing=True)
    if non_color:
        image.colorspace_settings.name = "Non-Color"
    return image


def make_pbr_material(
    name: str,
    sources: dict[str, Path],
    tint: tuple[float, float, float, float],
    tile_scale: float,
    wet_controls: list[dict[str, Any]],
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.name = "Principled BSDF"
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (tile_scale, tile_scale, tile_scale)
    links.new(texcoord.outputs["UV"], mapping.inputs["Vector"])

    base = nodes.new("ShaderNodeTexImage")
    base.image = load_image(sources["base"])
    base.interpolation = "Linear"
    links.new(mapping.outputs["Vector"], base.inputs["Vector"])
    tint_mix = nodes.new("ShaderNodeMixRGB")
    tint_mix.blend_type = "MULTIPLY"
    tint_mix.inputs[0].default_value = 1.0
    tint_mix.inputs[2].default_value = tint
    links.new(base.outputs["Color"], tint_mix.inputs[1])
    wet_mix = nodes.new("ShaderNodeMixRGB")
    wet_mix.name = "WET_DARKEN"
    wet_mix.blend_type = "MULTIPLY"
    wet_mix.inputs[0].default_value = 0.0
    wet_mix.inputs[2].default_value = (0.42, 0.46, 0.50, 1.0)
    links.new(tint_mix.outputs["Color"], wet_mix.inputs[1])
    links.new(wet_mix.outputs["Color"], bsdf.inputs["Base Color"])

    rough = nodes.new("ShaderNodeTexImage")
    rough.image = load_image(sources["roughness"], True)
    links.new(mapping.outputs["Vector"], rough.inputs["Vector"])
    rough_mult = nodes.new("ShaderNodeMath")
    rough_mult.name = "WET_ROUGHNESS_MULTIPLIER"
    rough_mult.operation = "MULTIPLY"
    rough_mult.inputs[1].default_value = 1.0
    links.new(rough.outputs["Color"], rough_mult.inputs[0])
    links.new(rough_mult.outputs["Value"], bsdf.inputs["Roughness"])

    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.image = load_image(sources["normal"], True)
    links.new(mapping.outputs["Vector"], normal_tex.inputs["Vector"])
    normal = nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value = 0.72
    links.new(normal_tex.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])

    if "metallic" in sources:
        metallic = nodes.new("ShaderNodeTexImage")
        metallic.image = load_image(sources["metallic"], True)
        links.new(mapping.outputs["Vector"], metallic.inputs["Vector"])
        links.new(metallic.outputs["Color"], bsdf.inputs["Metallic"])
    else:
        bsdf.inputs["Metallic"].default_value = 0.0

    wet_controls.append({"material": name, "color": wet_mix, "roughness": rough_mult})
    return material


def make_simple_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    require(bsdf is not None, f"Missing Principled BSDF: {name}")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return material


def make_window_material() -> bpy.types.Material:
    material = bpy.data.materials.new("M_M01_PROOF01_WindowInterior")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.name = "Principled BSDF"
    image = nodes.new("ShaderNodeTexImage")
    image.image = load_image(WINDOW_ATLAS)
    links.new(image.outputs["Color"], bsdf.inputs["Base Color"])
    emission_color = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if emission_color is not None:
        links.new(image.outputs["Color"], emission_color)
    if bsdf.inputs.get("Emission Strength") is not None:
        bsdf.inputs["Emission Strength"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.48
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def make_glass_material() -> bpy.types.Material:
    material = make_simple_material("M_M01_PROOF01_Glass", (0.012, 0.035, 0.060, 1.0), 0.10, 0.02)
    bsdf = material.node_tree.nodes["Principled BSDF"]
    if bsdf.inputs.get("Transmission Weight") is not None:
        bsdf.inputs["Transmission Weight"].default_value = 0.42
    if bsdf.inputs.get("IOR") is not None:
        bsdf.inputs["IOR"].default_value = 1.45
    return material


def make_water_material() -> bpy.types.Material:
    material = make_simple_material("M_M01_PROOF01_OceanWater", (0.006, 0.075, 0.115, 1.0), 0.10, 0.0)
    bsdf = material.node_tree.nodes["Principled BSDF"]
    if bsdf.inputs.get("Transmission Weight") is not None:
        bsdf.inputs["Transmission Weight"].default_value = 0.34
    if bsdf.inputs.get("IOR") is not None:
        bsdf.inputs["IOR"].default_value = 1.333
    normal = material.node_tree.nodes.new("ShaderNodeTexNoise")
    normal.inputs["Scale"].default_value = 5.0
    normal.inputs["Detail"].default_value = 5.0
    bump = material.node_tree.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.22
    bump.inputs["Distance"].default_value = 0.12
    material.node_tree.links.new(normal.outputs["Fac"], bump.inputs["Height"])
    material.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return material


def build_materials() -> tuple[dict[str, bpy.types.Material], list[dict[str, Any]]]:
    wet_controls: list[dict[str, Any]] = []
    materials = {
        "plaster_warm": make_pbr_material("M_M01_PROOF01_PlasterWarm", PBR_SOURCES["plaster"], (0.80, 0.69, 0.55, 1.0), 3.0, wet_controls),
        "plaster_cool": make_pbr_material("M_M01_PROOF01_PlasterCool", PBR_SOURCES["plaster"], (0.58, 0.70, 0.76, 1.0), 3.2, wet_controls),
        "concrete": make_pbr_material("M_M01_PROOF01_Concrete", PBR_SOURCES["concrete"], (0.72, 0.74, 0.72, 1.0), 3.4, wet_controls),
        "asphalt": make_pbr_material("M_M01_PROOF01_Asphalt", PBR_SOURCES["asphalt"], (0.42, 0.45, 0.49, 1.0), 4.0, wet_controls),
        "sand": make_pbr_material("M_M01_PROOF01_DrySand", PBR_SOURCES["sand"], (0.95, 0.82, 0.60, 1.0), 4.2, wet_controls),
        "wet_sand": make_pbr_material("M_M01_PROOF01_WetSand", PBR_SOURCES["sand"], (0.48, 0.38, 0.25, 1.0), 4.5, wet_controls),
        "roof": make_pbr_material("M_M01_PROOF01_Roof", PBR_SOURCES["roof"], (0.54, 0.57, 0.60, 1.0), 3.0, wet_controls),
        "metal": make_pbr_material("M_M01_PROOF01_Metal", PBR_SOURCES["metal"], (0.42, 0.48, 0.52, 1.0), 3.0, wet_controls),
        "window": make_window_material(),
        "glass": make_glass_material(),
        "water": make_water_material(),
        "foam": make_simple_material("M_M01_PROOF01_Foam", (0.78, 0.88, 0.91, 1.0), 0.34),
        "grime": make_simple_material("M_M01_PROOF01_Grime", (0.018, 0.016, 0.013, 1.0), 0.92),
        "rubber": make_simple_material("M_M01_PROOF01_Rubber", (0.006, 0.007, 0.008, 1.0), 0.88),
        "foliage": make_simple_material("M_M01_PROOF01_Foliage", (0.028, 0.115, 0.036, 1.0), 0.78),
        "foliage_light": make_simple_material("M_M01_PROOF01_FoliageLight", (0.060, 0.175, 0.055, 1.0), 0.76),
        "bark": make_simple_material("M_M01_PROOF01_Bark", (0.095, 0.044, 0.018, 1.0), 0.93),
        "marking": make_simple_material("M_M01_PROOF01_RoadMark", (0.72, 0.66, 0.48, 1.0), 0.60),
        "vehicle_red": make_simple_material("M_M01_PROOF01_VehicleRed", (0.26, 0.014, 0.009, 1.0), 0.23, 0.55),
        "vehicle_blue": make_simple_material("M_M01_PROOF01_VehicleBlue", (0.012, 0.060, 0.18, 1.0), 0.22, 0.58),
    }
    return materials, wet_controls


def add_window_module(
    prefix: str,
    x: float,
    y_front: float,
    z: float,
    width: float,
    height: float,
    materials: dict[str, bpy.types.Material],
    target: bpy.types.Collection,
    balcony: bool,
    variant: int,
) -> None:
    add_box(prefix + "_Interior", (x, y_front + 0.32, z), (width - 0.18, 0.08, height - 0.18), materials["window"], target, 0.015)
    add_box(prefix + "_Glass", (x, y_front - 0.035, z), (width, 0.055, height), materials["glass"], target, 0.012)
    frame = 0.075
    add_box(prefix + "_FrameL", (x - width * 0.5, y_front - 0.10, z), (frame, 0.10, height + 0.20), materials["metal"], target, 0.010)
    add_box(prefix + "_FrameR", (x + width * 0.5, y_front - 0.10, z), (frame, 0.10, height + 0.20), materials["metal"], target, 0.010)
    add_box(prefix + "_FrameT", (x, y_front - 0.10, z + height * 0.5), (width + 0.15, 0.10, frame), materials["metal"], target, 0.010)
    add_box(prefix + "_FrameB", (x, y_front - 0.10, z - height * 0.5), (width + 0.15, 0.10, frame), materials["metal"], target, 0.010)
    mullion_x = x + ((variant % 3) - 1) * width * 0.18
    add_box(prefix + "_Mullion", (mullion_x, y_front - 0.105, z), (0.055, 0.11, height), materials["metal"], target, 0.008)
    add_box(prefix + "_Sill", (x, y_front - 0.24, z - height * 0.5 - 0.10), (width + 0.32, 0.42, 0.13), materials["concrete"], target, 0.025)
    if balcony:
        add_box(prefix + "_BalconySlab", (x, y_front - 1.10, z - height * 0.5 - 0.05), (width + 0.70, 2.0, 0.20), materials["concrete"], target, 0.035)
        rail_y = y_front - 2.02
        add_box(prefix + "_RailTop", (x, rail_y, z + 0.15), (width + 0.58, 0.055, 0.055), materials["metal"], target, 0.010)
        for offset in (-0.45, 0.0, 0.45):
            add_box(prefix + f"_RailPost_{offset:+.2f}", (x + offset * width, rail_y, z - 0.33), (0.045, 0.055, 0.95), materials["metal"], target, 0.008)


def add_side_window(
    prefix: str,
    x_side: float,
    y: float,
    z: float,
    materials: dict[str, bpy.types.Material],
    target: bpy.types.Collection,
) -> None:
    add_box(prefix + "_Interior", (x_side, y, z), (0.07, 1.10, 1.42), materials["window"], target, 0.010)
    add_box(prefix + "_Glass", (x_side - 0.035, y, z), (0.055, 1.18, 1.52), materials["glass"], target, 0.010)
    for dy in (-0.66, 0.66):
        add_box(prefix + f"_FrameY_{dy:+.2f}", (x_side - 0.07, y + dy, z), (0.08, 0.07, 1.68), materials["metal"], target, 0.008)
    for dz in (-0.80, 0.80):
        add_box(prefix + f"_FrameZ_{dz:+.2f}", (x_side - 0.07, y, z + dz), (0.08, 1.40, 0.07), materials["metal"], target, 0.008)


def build_building(
    prefix: str,
    center_x: float,
    y_front: float,
    width: float,
    depth: float,
    floors: int,
    bay_widths: list[float],
    plaster_key: str,
    balcony_phase: int,
    materials: dict[str, bpy.types.Material],
    visible: bpy.types.Collection,
    collision: bpy.types.Collection,
) -> None:
    floor_h = 3.25
    total_h = floors * floor_h + 0.7
    y_back = y_front + depth
    wall = 0.42
    plaster = materials[plaster_key]
    add_box(prefix + "_SideL", (center_x - width * 0.5, y_front + depth * 0.5, total_h * 0.5), (wall, depth, total_h), plaster, visible, 0.07)
    add_box(prefix + "_SideR", (center_x + width * 0.5, y_front + depth * 0.5, total_h * 0.5), (wall, depth, total_h), plaster, visible, 0.07)
    add_box(prefix + "_Rear", (center_x, y_back, total_h * 0.5), (width, wall, total_h), plaster, visible, 0.07)
    add_box(prefix + "_Roof", (center_x, y_front + depth * 0.5, total_h + 0.10), (width, depth, 0.28), materials["roof"], visible, 0.05)
    add_box(prefix + "_Base", (center_x, y_front + depth * 0.5, 0.20), (width, depth, 0.40), materials["concrete"], visible, 0.05)

    left = center_x - width * 0.5
    normalized = [value * (width / sum(bay_widths)) for value in bay_widths]
    boundaries = [left]
    for value in normalized:
        boundaries.append(boundaries[-1] + value)
    for boundary_index, x in enumerate(boundaries):
        add_box(prefix + f"_FacadePier_{boundary_index:02d}", (x, y_front, total_h * 0.5), (0.40, wall, total_h), plaster, visible, 0.045)
    for floor in range(floors + 1):
        z = floor * floor_h
        add_box(prefix + f"_FloorBand_{floor:02d}", (center_x, y_front, z), (width, wall, 0.42), materials["concrete"], visible, 0.045)

    for floor in range(floors):
        z = floor * floor_h + 1.78
        for bay_index in range(len(normalized)):
            x = (boundaries[bay_index] + boundaries[bay_index + 1]) * 0.5
            cell_width = boundaries[bay_index + 1] - boundaries[bay_index]
            if floor == 0 and bay_index == (1 if prefix.endswith("A") else len(normalized) - 2):
                add_box(prefix + "_EntranceReveal", (x, y_front - 0.08, 1.45), (cell_width - 0.35, 0.48, 2.75), materials["concrete"], visible, 0.05)
                add_box(prefix + "_EntranceDoor", (x, y_front - 0.34, 1.35), (cell_width - 0.70, 0.09, 2.42), materials["glass"], visible, 0.025)
                add_box(prefix + "_EntranceCanopy", (x, y_front - 1.25, 2.92), (cell_width, 2.0, 0.18), materials["metal"], visible, 0.04)
            else:
                add_window_module(
                    f"{prefix}_F{floor:02d}_B{bay_index:02d}",
                    x,
                    y_front,
                    z,
                    max(1.25, cell_width - 0.72),
                    1.72 if (floor + bay_index) % 3 else 1.54,
                    materials,
                    visible,
                    balcony=(floor > 0 and (floor + bay_index + balcony_phase) % 3 == 0),
                    variant=floor * 7 + bay_index * 3 + balcony_phase,
                )

    for floor in range(1, floors):
        z = floor * floor_h + 1.65
        for side_index, x in enumerate((center_x - width * 0.5 - 0.04, center_x + width * 0.5 + 0.04)):
            if side_index == 1:
                continue
            for y_offset in (depth * 0.30, depth * 0.62):
                add_side_window(f"{prefix}_Side_F{floor:02d}_{y_offset:.2f}", x, y_front + y_offset, z, materials, visible)

    parapet_z = total_h + 0.72
    add_box(prefix + "_ParapetFront", (center_x, y_front + 0.22, parapet_z), (width, 0.32, 1.18), materials["concrete"], visible, 0.05)
    add_box(prefix + "_ParapetRear", (center_x, y_back - 0.22, parapet_z), (width, 0.32, 1.18), materials["concrete"], visible, 0.05)
    add_box(prefix + "_RoofAccess", (center_x - width * 0.24, y_front + depth * 0.56, total_h + 1.45), (4.0, 4.2, 2.7), plaster, visible, 0.10)
    for index, (dx, dy, sx, sy) in enumerate(((-0.05, 0.30, 2.2, 1.5), (0.22, 0.62, 1.7, 1.3), (0.36, 0.35, 1.4, 1.1))):
        add_box(prefix + f"_HVAC_{index:02d}", (center_x + width * dx, y_front + depth * dy, total_h + 0.72), (sx, sy, 1.1), materials["metal"], visible, 0.09)
        for grille in (-0.32, 0.0, 0.32):
            add_box(prefix + f"_HVAC_{index:02d}_Grille_{grille:+.2f}", (center_x + width * dx + grille * sx, y_front + depth * dy - sy * 0.505, total_h + 0.72), (0.045, 0.03, 0.72), materials["grime"], visible, 0.004)
    add_cylinder(prefix + "_RoofTank", (center_x + width * 0.26, y_front + depth * 0.70, total_h + 1.0), 0.78, 1.65, materials["metal"], visible, 32, bevel=0.05)
    add_cylinder(prefix + "_AntennaMast", (center_x + width * 0.08, y_front + depth * 0.48, total_h + 3.0), 0.055, 5.0, materials["metal"], visible, 20, bevel=0.012)

    for stain_index, x_factor in enumerate((-0.34, 0.12, 0.38)):
        add_box(prefix + f"_DrainStain_{stain_index:02d}", (center_x + width * x_factor, y_front - 0.225, total_h * (0.38 + 0.14 * stain_index)), (0.18 + 0.05 * stain_index, 0.028, total_h * 0.44), materials["grime"], visible, 0.004)

    add_box("UCX_" + prefix, (center_x, y_front + depth * 0.5, total_h * 0.5), (width, depth, total_h), materials["grime"], collision, 0.0)


def grid_mesh(
    name: str,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    x_segments: int,
    y_segments: int,
    z_fn: Callable[[float, float], float],
    material: bpy.types.Material,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for yi in range(y_segments + 1):
        y = y_min + (y_max - y_min) * yi / y_segments
        for xi in range(x_segments + 1):
            x = x_min + (x_max - x_min) * xi / x_segments
            vertices.append((x, y, z_fn(x, y)))
    stride = x_segments + 1
    for yi in range(y_segments):
        for xi in range(x_segments):
            a = yi * stride + xi
            faces.append((a, a + 1, a + stride + 1, a + stride))
    return add_custom_mesh(name, vertices, faces, material, target)


def build_shore_and_street(
    materials: dict[str, bpy.types.Material],
    visible: bpy.types.Collection,
    collision: bpy.types.Collection,
) -> None:
    grid_mesh(
        "SM_M01_PROOF01_OceanSurface",
        -44.0,
        44.0,
        -32.0,
        -6.0,
        40,
        18,
        lambda x, y: -0.35 + 0.08 * math.sin(x * 0.42 + y * 0.21) + 0.035 * math.sin(x * 1.15 - y * 0.31),
        materials["water"],
        visible,
    )
    grid_mesh(
        "SM_M01_PROOF01_WetBeach",
        -44.0,
        44.0,
        -8.0,
        -1.0,
        36,
        6,
        lambda x, y: -0.28 + (y + 8.0) * 0.055 + 0.045 * math.sin(x * 0.28 + y),
        materials["wet_sand"],
        visible,
    )
    grid_mesh(
        "SM_M01_PROOF01_DryBeach",
        -44.0,
        44.0,
        -1.0,
        3.8,
        36,
        5,
        lambda x, y: 0.10 + (y + 1.0) * 0.055 + 0.08 * math.sin(x * 0.23 + y * 0.8),
        materials["sand"],
        visible,
    )
    for foam_index, offset in enumerate((0.0, 0.55, 1.1)):
        points = [(x, -6.8 + offset + 0.28 * math.sin(x * 0.21 + offset * 2.0), -0.08 + 0.025 * foam_index) for x in [(-42.0 + i * 1.4) for i in range(61)]]
        add_curve_strip(f"SM_M01_PROOF01_SurfFoam_{foam_index:02d}", points, 0.07 - foam_index * 0.012, materials["foam"], visible)

    for segment in range(8):
        x = -38.5 + segment * 11.0
        add_box(f"SM_M01_PROOF01_Seawall_{segment:02d}", (x, 4.4, 0.95), (10.82, 1.15, 1.90), materials["concrete"], visible, 0.08)
        add_box(f"SM_M01_PROOF01_Coping_{segment:02d}", (x, 4.25, 1.98), (10.88, 1.45, 0.18), materials["concrete"], visible, 0.045)
        add_box(f"SM_M01_PROOF01_SaltBand_{segment:02d}", (x, 3.81, 0.74), (9.80, 0.035, 0.48), materials["grime"], visible, 0.004)
        if segment % 2 == 1:
            add_cylinder(f"SM_M01_PROOF01_DrainOutlet_{segment:02d}", (x + 1.3, 3.78, 0.82), 0.28, 0.18, materials["metal"], visible, 28, (math.radians(90.0), 0.0, 0.0), 0.015)

    add_box("SM_M01_PROOF01_Promenade", (0.0, 8.1, 2.08), (88.0, 6.0, 0.20), materials["concrete"], visible, 0.025)
    for x in range(-40, 41, 4):
        add_box(f"SM_M01_PROOF01_PromenadeJoint_{x:+03d}", (float(x), 8.1, 2.19), (0.035, 5.70, 0.018), materials["grime"], visible, 0.003)
    add_box("SM_M01_PROOF01_CurbOcean", (0.0, 11.28, 2.21), (88.0, 0.32, 0.42), materials["concrete"], visible, 0.04)

    x_values = [-44.0 + i * 4.0 for i in range(23)]
    y_values = [11.6, 14.8, 18.9, 23.0, 26.2]
    vertices = []
    for y in y_values:
        crown = 2.32 + max(0.0, 1.0 - abs(y - 18.9) / 7.5) * 0.17
        for x in x_values:
            vertices.append((x, y, crown + 0.018 * math.sin(x * 0.45)))
    faces = []
    stride = len(x_values)
    for yi in range(len(y_values) - 1):
        for xi in range(len(x_values) - 1):
            a = yi * stride + xi
            faces.append((a, a + 1, a + stride + 1, a + stride))
    add_custom_mesh("SM_M01_PROOF01_CrownedRoad", vertices, faces, materials["asphalt"], visible)
    add_box("SM_M01_PROOF01_CurbInland", (0.0, 26.5, 2.30), (88.0, 0.35, 0.45), materials["concrete"], visible, 0.04)
    add_box("SM_M01_PROOF01_InlandWalk", (0.0, 28.8, 2.36), (88.0, 4.1, 0.20), materials["concrete"], visible, 0.025)

    for x in range(-38, 39, 8):
        add_box(f"SM_M01_PROOF01_LaneMark_{x:+03d}", (float(x), 18.9, 2.53), (4.6, 0.14, 0.025), materials["marking"], visible, 0.008)
    for index, x in enumerate((-32.0, -12.0, 8.0, 28.0)):
        add_box(f"SM_M01_PROOF01_DrainGrate_{index:02d}", (x, 12.05, 2.37), (1.25, 0.42, 0.045), materials["metal"], visible, 0.012)
        for slot in (-0.42, -0.21, 0.0, 0.21, 0.42):
            add_box(f"SM_M01_PROOF01_DrainSlot_{index:02d}_{slot:+.2f}", (x + slot, 11.83, 2.40), (0.055, 0.25, 0.025), materials["grime"], visible, 0.003)

    add_box("UCX_SM_M01_PROOF01_Seawall", (0.0, 4.4, 0.95), (88.0, 1.2, 1.9), materials["grime"], collision, 0.0)
    add_box("UCX_SM_M01_PROOF01_Road", (0.0, 18.9, 2.25), (88.0, 15.0, 0.45), materials["grime"], collision, 0.0)


def add_streetlight(index: int, x: float, materials: dict[str, bpy.types.Material], visible: bpy.types.Collection) -> tuple[bpy.types.Object, bpy.types.Object]:
    pole = add_cylinder(f"SM_M01_PROOF01_Streetlight_{index:02d}_Pole", (x, 9.8, 5.15), 0.065, 5.9, materials["metal"], visible, 24, bevel=0.018)
    arm = cylinder_between(f"SM_M01_PROOF01_Streetlight_{index:02d}_Arm", (x, 9.8, 8.0), (x + 0.72, 9.8, 8.20), 0.052, materials["metal"], visible)
    lamp = add_box(f"SM_M01_PROOF01_Streetlight_{index:02d}_Lamp", (x + 0.91, 9.8, 8.15), (0.52, 0.24, 0.14), materials["window"], visible, 0.035)
    return pole, lamp


def add_bench(index: int, x: float, materials: dict[str, bpy.types.Material], visible: bpy.types.Collection) -> None:
    for slat in range(5):
        add_box(f"SM_M01_PROOF01_Bench_{index:02d}_Seat_{slat:02d}", (x, 7.6 + slat * 0.12, 2.77), (2.0, 0.075, 0.075), materials["metal"], visible, 0.012)
    for slat in range(4):
        add_box(f"SM_M01_PROOF01_Bench_{index:02d}_Back_{slat:02d}", (x, 7.94, 3.13 + slat * 0.14), (2.0, 0.065, 0.075), materials["metal"], visible, 0.012)
    for leg in (-0.72, 0.72):
        add_box(f"SM_M01_PROOF01_Bench_{index:02d}_Leg_{leg:+.2f}", (x + leg, 7.73, 2.52), (0.09, 0.48, 0.48), materials["metal"], visible, 0.015)


def add_vehicle(index: int, x: float, y: float, material: bpy.types.Material, materials: dict[str, bpy.types.Material], visible: bpy.types.Collection) -> None:
    body = add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_Body", (x, y, 3.05), (4.35, 1.78, 0.72), material, visible, 0.20)
    cabin_vertices = [
        (x - 1.35, y - 0.76, 3.38), (x + 1.15, y - 0.76, 3.38), (x + 0.76, y - 0.72, 4.12), (x - 0.72, y - 0.72, 4.12),
        (x - 1.35, y + 0.76, 3.38), (x + 1.15, y + 0.76, 3.38), (x + 0.76, y + 0.72, 4.12), (x - 0.72, y + 0.72, 4.12),
    ]
    cabin_faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (3, 2, 6, 7), (0, 3, 7, 4), (1, 5, 6, 2)]
    add_custom_mesh(f"SM_M01_PROOF01_Vehicle_{index:02d}_Cabin", cabin_vertices, cabin_faces, materials["glass"], visible, 0.08)
    add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_Hood", (x - 1.63, y, 3.38), (1.20, 1.72, 0.24), material, visible, 0.10)
    add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_Trunk", (x + 1.62, y, 3.38), (1.10, 1.72, 0.24), material, visible, 0.10)
    for wheel_index, (dx, dy) in enumerate(((-1.35, -0.91), (-1.35, 0.91), (1.35, -0.91), (1.35, 0.91))):
        add_cylinder(f"SM_M01_PROOF01_Vehicle_{index:02d}_Wheel_{wheel_index:02d}", (x + dx, y + dy, 2.84), 0.38, 0.22, materials["rubber"], visible, 32, (math.radians(90.0), 0.0, 0.0), 0.025)
        add_cylinder(f"SM_M01_PROOF01_Vehicle_{index:02d}_Hub_{wheel_index:02d}", (x + dx, y + dy * 1.012, 2.84), 0.20, 0.235, materials["metal"], visible, 24, (math.radians(90.0), 0.0, 0.0), 0.018)


def add_tree(index: int, x: float, y: float, height: float, materials: dict[str, bpy.types.Material], visible: bpy.types.Collection) -> None:
    base_z = 2.48
    add_cylinder(f"SM_M01_PROOF01_Tree_{index:02d}_Trunk", (x, y, base_z + height * 0.33), 0.18, height * 0.66, materials["bark"], visible, 28, bevel=0.035)
    branch_specs = ((-0.65, 0.20, 0.70), (0.58, -0.24, 0.78), (0.18, 0.58, 0.88), (-0.22, -0.52, 0.82))
    for branch_index, (dx, dy, dz) in enumerate(branch_specs):
        start = (x, y, base_z + height * 0.45)
        end = (x + dx, y + dy, base_z + height * dz)
        cylinder_between(f"SM_M01_PROOF01_Tree_{index:02d}_Branch_{branch_index:02d}", start, end, 0.075, materials["bark"], visible)
    crowns = ((0.0, 0.0, 0.78, 1.0), (-0.65, 0.15, 0.72, 0.72), (0.58, -0.20, 0.75, 0.76), (0.08, 0.55, 0.86, 0.63), (-0.20, -0.48, 0.83, 0.66))
    for crown_index, (dx, dy, dz, scale) in enumerate(crowns):
        add_icosphere(
            f"SM_M01_PROOF01_Tree_{index:02d}_Crown_{crown_index:02d}",
            (x + dx, y + dy, base_z + height * dz),
            height * 0.22,
            (0.95 * scale, 0.85 * scale, 1.15 * scale),
            materials["foliage" if (index + crown_index) % 2 else "foliage_light"],
            visible,
        )
    add_box(f"SM_M01_PROOF01_Tree_{index:02d}_Planter", (x, y, 2.62), (1.45, 1.45, 0.36), materials["concrete"], visible, 0.08)


def add_supporting_details(materials: dict[str, bpy.types.Material], visible: bpy.types.Collection) -> list[tuple[float, float, float]]:
    practical_locations = []
    for index, x in enumerate((-34.0, -17.0, 0.0, 17.0, 34.0)):
        _, lamp = add_streetlight(index, x, materials, visible)
        practical_locations.append(tuple(lamp.location))
    for index, x in enumerate((-25.0, 0.0, 25.0)):
        add_bench(index, x, materials, visible)
    add_vehicle(0, -25.0, 15.0, materials["vehicle_red"], materials, visible)
    add_vehicle(1, 4.0, 23.0, materials["vehicle_blue"], materials, visible)
    add_vehicle(2, 27.0, 15.0, materials["vehicle_blue"], materials, visible)
    for index, (x, y, h) in enumerate(((-34.0, 29.0, 5.4), (-7.0, 29.2, 5.8), (22.0, 29.0, 5.2), (38.0, 28.8, 5.7))):
        add_tree(index, x, y, h, materials, visible)
    for index, x in enumerate((-40.0, -20.0, 0.0, 20.0, 40.0)):
        add_cylinder(f"SM_M01_PROOF01_Bollard_{index:02d}", (x, 5.4, 2.52), 0.10, 0.72, materials["metal"], visible, 24, bevel=0.025)
    return practical_locations


def add_socket(name: str, location: tuple[float, float, float], target: bpy.types.Collection) -> None:
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = 1.0
    empty.location = location
    target.objects.link(empty)


def point_camera(camera: bpy.types.Object, location: tuple[float, float, float], target: tuple[float, float, float], lens: float) -> None:
    camera.location = location
    camera.data.lens = lens
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()


def setup_review(scene: bpy.types.Scene, practical_locations: list[tuple[float, float, float]], review: bpy.types.Collection) -> dict[str, Any]:
    camera_data = bpy.data.cameras.new("CAM_M01_PROOF01")
    camera = bpy.data.objects.new("CAM_M01_PROOF01", camera_data)
    camera_data.clip_start = 0.08
    camera_data.clip_end = 500.0
    review.objects.link(camera)
    scene.camera = camera

    bpy.ops.object.light_add(type="SUN", location=(0.0, -10.0, 70.0))
    sun = bpy.context.object
    sun.name = "LIGHT_M01_PROOF01_Sun"
    sun.rotation_euler = (math.radians(28.0), math.radians(-12.0), math.radians(-34.0))
    sun.data.angle = math.radians(0.7)
    move_to_collection(sun, review)

    bpy.ops.object.light_add(type="AREA", location=(-15.0, -8.0, 35.0))
    fill = bpy.context.object
    fill.name = "LIGHT_M01_PROOF01_Fill"
    fill.data.shape = "DISK"
    fill.data.size = 28.0
    fill.rotation_euler = (math.radians(18.0), 0.0, math.radians(-12.0))
    move_to_collection(fill, review)

    bpy.ops.object.light_add(type="AREA", location=(18.0, 8.0, 32.0))
    moon = bpy.context.object
    moon.name = "LIGHT_M01_PROOF01_Moon"
    moon.data.shape = "DISK"
    moon.data.size = 24.0
    moon.data.color = (0.20, 0.34, 0.66)
    moon.rotation_euler = (math.radians(24.0), 0.0, math.radians(34.0))
    move_to_collection(moon, review)

    practicals = []
    for index, location in enumerate(practical_locations):
        bpy.ops.object.light_add(type="POINT", location=location)
        light = bpy.context.object
        light.name = f"LIGHT_M01_PROOF01_Practical_{index:02d}"
        light.data.color = (1.0, 0.46, 0.19)
        light.data.shadow_soft_size = 0.8
        move_to_collection(light, review)
        practicals.append(light)

    return {"camera": camera, "sun": sun, "fill": fill, "moon": moon, "practicals": practicals}


def configure_condition(scene: bpy.types.Scene, rig: dict[str, Any], condition: str, wet_controls: list[dict[str, Any]], materials: dict[str, bpy.types.Material]) -> None:
    background = scene.world.node_tree.nodes.get("Background")
    require(background is not None, "World background node missing")
    values = {
        "daylight": ((0.16, 0.30, 0.52, 1.0), 0.42, 2.8, 850.0, 0.0, 0.0, 0.35),
        "wet_overcast": ((0.055, 0.075, 0.095, 1.0), 0.34, 0.65, 1250.0, 180.0, 80.0, 0.20),
        "night": ((0.008, 0.018, 0.045, 1.0), 0.14, 0.08, 520.0, 1550.0, 360.0, 0.85),
    }
    color, strength, sun_energy, fill_energy, moon_energy, practical_energy, exposure = values[condition]
    background.inputs["Color"].default_value = color
    background.inputs["Strength"].default_value = strength
    rig["sun"].data.energy = sun_energy
    rig["fill"].data.energy = fill_energy
    rig["moon"].data.energy = moon_energy
    for light in rig["practicals"]:
        light.data.energy = practical_energy
    scene.view_settings.exposure = exposure
    wet = condition == "wet_overcast"
    for control in wet_controls:
        control["color"].inputs[0].default_value = 0.42 if wet else 0.0
        control["roughness"].inputs[1].default_value = 0.33 if wet else 1.0
    window_bsdf = materials["window"].node_tree.nodes.get("Principled BSDF")
    if window_bsdf is not None and window_bsdf.inputs.get("Emission Strength") is not None:
        window_bsdf.inputs["Emission Strength"].default_value = 2.6 if condition == "night" else 0.28 if wet else 0.0


def configure_scene(scene: bpy.types.Scene) -> None:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.render.image_settings.color_mode = "RGBA"
    scene.world.use_nodes = True
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass


def render_checkpoints(scene: bpy.types.Scene, rig: dict[str, Any], output: Path, materials: dict[str, bpy.types.Material], wet_controls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cameras = {
        "route_composite": ((0.0, -43.0, 15.5), (0.0, 26.0, 8.5), 49.0),
        "facade_close": ((-30.0, 9.0, 6.2), (-19.0, 31.5, 8.4), 55.0),
        "shoreline_close": ((27.0, -12.0, 5.8), (7.0, 2.2, 1.2), 54.0),
    }
    results = []
    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    for condition in ("daylight", "wet_overcast", "night"):
        configure_condition(scene, rig, condition, wet_controls, materials)
        for camera_id, (location, target, lens) in cameras.items():
            point_camera(rig["camera"], location, target, lens)
            path = render_dir / f"{condition}_{camera_id}.png"
            scene.render.filepath = str(path)
            print(json.dumps({"event": "render_start", "condition": condition, "camera": camera_id}), flush=True)
            bpy.ops.render.render(write_still=True)
            require(path.is_file() and path.stat().st_size > 0, f"Render missing: {path}")
            results.append({"condition": condition, "camera": camera_id, "path": str(path), "bytes": path.stat().st_size})
            print(json.dumps({"event": "render_complete", "condition": condition, "camera": camera_id, "bytes": path.stat().st_size}), flush=True)
    require(len(results) == 9, "Expected exactly nine governed renders")
    return results


def mesh_statistics(collections: list[bpy.types.Collection]) -> dict[str, int]:
    mesh_objects = []
    vertices = 0
    polygons = 0
    for collection in collections:
        for obj in collection.all_objects:
            if obj.type == "MESH":
                mesh_objects.append(obj)
                vertices += len(obj.data.vertices)
                polygons += len(obj.data.polygons)
    return {"mesh_objects": len(set(mesh_objects)), "vertices": vertices, "polygons": polygons}


def export_glb(path: Path, collections: list[bpy.types.Collection]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    selected = []
    for collection in collections:
        for obj in collection.all_objects:
            obj.select_set(True)
            selected.append(obj)
    require(selected, "No objects selected for GLB export")
    bpy.context.view_layer.objects.active = next((obj for obj in selected if obj.type == "MESH"), selected[0])
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_animations=False,
        export_lights=False,
        export_cameras=False,
    )
    require(path.is_file() and path.stat().st_size > 0, "GLB export was not created")


def main() -> int:
    args = parse_args()
    require(args.asset_id == ASSET_ID, f"Unexpected asset id: {args.asset_id}")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    require(not any(output.iterdir()), f"Controller output directory is not empty: {output}")
    require(PROVENANCE.is_file(), "PolyHaven provenance manifest is missing")
    for texture_set in PBR_SOURCES.values():
        for path in texture_set.values():
            require(path.is_file(), f"Missing PBR authority: {path}")
    require(WINDOW_ATLAS.is_file(), "Window interior atlas is missing")

    clear_scene()
    scene = bpy.context.scene
    configure_scene(scene)
    visible = get_collection("M01_PROOF01_VISIBLE")
    collision = get_collection("M01_PROOF01_COLLISION")
    sockets = get_collection("M01_PROOF01_SOCKETS")
    review = get_collection("M01_PROOF01_REVIEW_ONLY")
    materials, wet_controls = build_materials()

    build_shore_and_street(materials, visible, collision)
    build_building("SM_M01_PROOF01_Midrise_A", -19.0, 31.0, 28.0, 18.0, 6, [3.2, 4.6, 3.8, 5.2, 3.1, 4.1], "plaster_warm", 0, materials, visible, collision)
    build_building("SM_M01_PROOF01_Midrise_B", 20.0, 32.5, 22.0, 20.0, 8, [4.5, 3.4, 5.7, 3.2, 5.2], "plaster_cool", 2, materials, visible, collision)
    practical_locations = add_supporting_details(materials, visible)
    add_socket("SOCKET_District_W", (-44.0, 0.0, 0.0), sockets)
    add_socket("SOCKET_District_E", (44.0, 0.0, 0.0), sockets)
    add_socket("SOCKET_Shoreline_Origin", (0.0, -6.8, 0.0), sockets)
    add_socket("SOCKET_Road_Origin", (0.0, 18.9, 2.4), sockets)
    rig = setup_review(scene, practical_locations, review)

    stats = mesh_statistics([visible, collision])
    require(stats["mesh_objects"] >= 260, f"Insufficient production geometry objects: {stats}")
    require(stats["vertices"] >= 12000, f"Insufficient production geometry vertices: {stats}")
    require(len(materials) >= 20, "Material family is incomplete")

    renders = render_checkpoints(scene, rig, output, materials, wet_controls)
    blend_path = output / "M01_Environment_Hero_Streetshore_Proof01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    glb_path = output / "M01_Environment_Hero_Streetshore_Proof01.glb"
    export_glb(glb_path, [visible, collision, sockets])

    texture_inventory = []
    for family, texture_set in sorted(PBR_SOURCES.items()):
        for role, path in sorted(texture_set.items()):
            texture_inventory.append({"family": family, "role": role, "path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)})
    texture_inventory.append({"family": "window", "role": "interior_atlas", "path": str(WINDOW_ATLAS), "bytes": WINDOW_ATLAS.stat().st_size, "sha256": sha256(WINDOW_ATLAS)})

    write_json(output / "geometry_receipt.json", {
        "schema": "skyguard.m01-environment-production-reset01.hero-streetshore-proof01.geometry.v1",
        "gate": GATE,
        "fresh_geometry": True,
        "recovery10_mesh_reuse": False,
        "external_model_use": False,
        "scope": "two hero midrises plus one bounded shoreline, promenade, road, and street-detail slice",
        "statistics": stats,
        "building_facade_signatures": {
            "A": {"floors": 6, "bay_widths": [3.2, 4.6, 3.8, 5.2, 3.1, 4.1], "balcony_phase": 0},
            "B": {"floors": 8, "bay_widths": [4.5, 3.4, 5.7, 3.2, 5.2], "balcony_phase": 2},
        },
        "sockets": ["SOCKET_District_W", "SOCKET_District_E", "SOCKET_Shoreline_Origin", "SOCKET_Road_Origin"],
        "collision_prefix": "UCX_",
        "passed": True,
    })
    write_json(output / "pbr_receipt.json", {
        "schema": "skyguard.m01-environment-production-reset01.hero-streetshore-proof01.pbr.v1",
        "gate": GATE,
        "texture_authorities": texture_inventory,
        "provenance_manifest": {"path": str(PROVENANCE), "bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)},
        "material_count": len(materials),
        "texture_driven_families": sorted(PBR_SOURCES),
        "wetness_controls": [entry["material"] for entry in wet_controls],
        "passed": True,
    })
    write_json(output / "render_receipt.json", {
        "schema": "skyguard.m01-environment-production-reset01.hero-streetshore-proof01.renders.v1",
        "gate": GATE,
        "resolution": [1920, 1080],
        "conditions": ["daylight", "wet_overcast", "night"],
        "cameras": ["route_composite", "facade_close", "shoreline_close"],
        "renders": renders,
        "direct_full_resolution_review_required": True,
        "passed": True,
    })
    write_json(output / "export_receipt.json", {
        "schema": "skyguard.m01-environment-production-reset01.hero-streetshore-proof01.export.v1",
        "gate": GATE,
        "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size, "sha256": sha256(blend_path)},
        "glb": {"path": str(glb_path), "bytes": glb_path.stat().st_size, "sha256": sha256(glb_path)},
        "exported_collections": [visible.name, collision.name, sockets.name],
        "review_collection_excluded": review.name,
        "unreal_import_authorized": False,
        "passed": True,
    })
    write_json(output / "artifact_manifest.json", {
        "schema": "skyguard.m01-environment-production-reset01.hero-streetshore-proof01.artifacts.v1",
        "gate": GATE,
        "asset_id": ASSET_ID,
        "classification": "PASSED_AUTOMATIC_AWAITING_POSTFLIGHT_AND_DIRECT_VISUAL_REVIEW",
        "blend_count": 1,
        "glb_count": 1,
        "render_count": 9,
        "receipt_count": 4,
        "blender_version": bpy.app.version_string,
        "promotion_authorized": False,
        "unreal_import_authorized": False,
    })
    print(json.dumps({"gate": GATE, "classification": "PASSED_AUTOMATIC_AWAITING_POSTFLIGHT_AND_DIRECT_VISUAL_REVIEW", "stats": stats}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
