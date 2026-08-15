from __future__ import annotations

"""Build one authored Mission 1 coastal frontage cell.

This is intentionally not a whole-city generator.  It creates three distinct
modular building signatures and their immediate streetscape so visual quality
can be proven before the kit is propagated through the coastal corridor.
"""

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
ASSET_ID = "m01-hero-coastal-frontage-cell01"
GATE = "M01_HERO_COASTAL_FRONTAGE_CELL01"
TEXTURE_ROOT = ROOT / r"Content\Skyguard\Textures"
PROVENANCE = TEXTURE_ROOT / r"PolyHaven\polyhaven-provenance-manifest.json"
WINDOW_ATLAS = TEXTURE_ROOT / r"WebPBR\city-window-interior-atlas.webp"
RENDER_SIZE = (1920, 1080)
CHECKPOINT_SIZE = (1280, 720)

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
    for blocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(blocks):
            if block.users == 0:
                blocks.remove(block)


def get_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def load_image(path: Path, non_color: bool = False) -> bpy.types.Image:
    require(path.is_file(), f"Missing governed texture authority: {path}")
    image = bpy.data.images.load(str(path), check_existing=True)
    if non_color:
        image.colorspace_settings.name = "Non-Color"
    return image


def pbr_material(
    name: str,
    sources: dict[str, Path],
    tint: tuple[float, float, float, float],
    tile_scale: float,
    roughness_multiplier: float = 1.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (tile_scale, tile_scale, tile_scale)
    links.new(texcoord.outputs["UV"], mapping.inputs["Vector"])

    base = nodes.new("ShaderNodeTexImage")
    base.image = load_image(sources["base"])
    links.new(mapping.outputs["Vector"], base.inputs["Vector"])
    tint_mix = nodes.new("ShaderNodeMixRGB")
    tint_mix.blend_type = "MULTIPLY"
    tint_mix.inputs[0].default_value = 1.0
    tint_mix.inputs[2].default_value = tint
    links.new(base.outputs["Color"], tint_mix.inputs[1])
    links.new(tint_mix.outputs["Color"], bsdf.inputs["Base Color"])

    rough = nodes.new("ShaderNodeTexImage")
    rough.image = load_image(sources["roughness"], True)
    links.new(mapping.outputs["Vector"], rough.inputs["Vector"])
    rough_mult = nodes.new("ShaderNodeMath")
    rough_mult.operation = "MULTIPLY"
    rough_mult.inputs[1].default_value = roughness_multiplier
    links.new(rough.outputs["Color"], rough_mult.inputs[0])
    links.new(rough_mult.outputs["Value"], bsdf.inputs["Roughness"])

    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.image = load_image(sources["normal"], True)
    links.new(mapping.outputs["Vector"], normal_tex.inputs["Vector"])
    normal = nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value = 0.55
    links.new(normal_tex.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])

    if "metallic" in sources:
        metallic = nodes.new("ShaderNodeTexImage")
        metallic.image = load_image(sources["metallic"], True)
        links.new(mapping.outputs["Vector"], metallic.inputs["Vector"])
        links.new(metallic.outputs["Color"], bsdf.inputs["Metallic"])
    return material


def simple_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
    emission: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    require(bsdf is not None, f"Missing Principled BSDF in {name}")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    emission_color = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if emission_color is not None:
        emission_color.default_value = color
    if bsdf.inputs.get("Emission Strength") is not None:
        bsdf.inputs["Emission Strength"].default_value = emission
    return material


def window_material() -> bpy.types.Material:
    material = bpy.data.materials.new("M_M01_HeroFrontage_WindowInterior")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    image = nodes.new("ShaderNodeTexImage")
    image.image = load_image(WINDOW_ATLAS)
    links.new(image.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 0.1
    bsdf.inputs["Roughness"].default_value = 0.22
    emission_color = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if emission_color is not None:
        links.new(image.outputs["Color"], emission_color)
    if bsdf.inputs.get("Emission Strength") is not None:
        bsdf.inputs["Emission Strength"].default_value = 0.10
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    return material


def build_materials() -> dict[str, bpy.types.Material]:
    return {
        "plaster_warm": pbr_material("M_M01_HeroFrontage_PlasterWarm", PBR_SOURCES["plaster"], (0.78, 0.58, 0.40, 1.0), 2.8),
        "plaster_cream": pbr_material("M_M01_HeroFrontage_PlasterCream", PBR_SOURCES["plaster"], (0.88, 0.82, 0.68, 1.0), 3.1),
        "plaster_cool": pbr_material("M_M01_HeroFrontage_PlasterCool", PBR_SOURCES["plaster"], (0.50, 0.64, 0.68, 1.0), 3.0),
        "concrete": pbr_material("M_M01_HeroFrontage_Concrete", PBR_SOURCES["concrete"], (0.60, 0.62, 0.59, 1.0), 3.4),
        "stone": pbr_material("M_M01_HeroFrontage_StoneBase", PBR_SOURCES["concrete"], (0.38, 0.34, 0.30, 1.0), 4.4),
        "asphalt": pbr_material("M_M01_HeroFrontage_Asphalt", PBR_SOURCES["asphalt"], (0.27, 0.29, 0.31, 1.0), 3.8),
        "roof": pbr_material("M_M01_HeroFrontage_Roof", PBR_SOURCES["roof"], (0.35, 0.30, 0.28, 1.0), 3.2),
        "metal": pbr_material("M_M01_HeroFrontage_Metal", PBR_SOURCES["metal"], (0.34, 0.38, 0.39, 1.0), 3.0, 0.85),
        "window": window_material(),
        "dark": simple_material("M_M01_HeroFrontage_RecessShadow", (0.012, 0.018, 0.024, 1.0), 0.32),
        "wood": simple_material("M_M01_HeroFrontage_Wood", (0.20, 0.09, 0.035, 1.0), 0.58),
        "sign_red": simple_material("M_M01_HeroFrontage_SignRed", (0.34, 0.025, 0.018, 1.0), 0.48),
        "sign_blue": simple_material("M_M01_HeroFrontage_SignBlue", (0.018, 0.08, 0.18, 1.0), 0.42),
        "lamp": simple_material("M_M01_HeroFrontage_Lamp", (1.0, 0.62, 0.26, 1.0), 0.22, emission=4.0),
    }


def tag(obj: bpy.types.Object, role: str, signature: str | None = None) -> None:
    obj["SKG_Role"] = role
    obj["SKG_AssetId"] = ASSET_ID
    if signature:
        obj["SKG_BuildingSignature"] = signature


def add_box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    role: str,
    bevel: float = 0.04,
    signature: str | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        modifier = obj.modifiers.new("ControlledEdge", "BEVEL")
        modifier.width = min(bevel, min(dimensions) * 0.20)
        modifier.segments = 3
        modifier.limit_method = "ANGLE"
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.data.materials.append(material)
    move_to_collection(obj, collection)
    tag(obj, role, signature)
    return obj


def add_cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    role: str,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    vertices: int = 32,
    signature: str | None = None,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    move_to_collection(obj, collection)
    tag(obj, role, signature)
    return obj


def add_custom_mesh(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    role: str,
    signature: str,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.data.materials.append(material)
    tag(obj, role, signature)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(island_margin=0.025)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)
    return obj


def add_empty(name: str, location: tuple[float, float, float], collection: bpy.types.Collection, role: str) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.75
    obj.location = location
    collection.objects.link(obj)
    tag(obj, role)
    return obj


def add_railing(prefix: str, x0: float, x1: float, y: float, z: float, materials: dict[str, bpy.types.Material], collection: bpy.types.Collection, signature: str) -> None:
    add_box(prefix + "_Top", ((x0 + x1) * 0.5, y, z + 0.95), (x1 - x0, 0.055, 0.06), materials["metal"], collection, "balcony_railing", 0.012, signature)
    for index in range(7):
        x = x0 + (x1 - x0) * index / 6.0
        add_cylinder(prefix + f"_Post_{index:02d}", (x, y, z + 0.48), 0.022, 0.94, materials["metal"], collection, "balcony_railing", vertices=16, signature=signature)


def shell_and_floorplates(prefix: str, center_x: float, front_y: float, width: float, depth: float, height: float, floors: int, material: bpy.types.Material, collection: bpy.types.Collection, signature: str, base_z: float = 0.0) -> None:
    back_y = front_y + depth
    add_box(prefix + "_Back", (center_x, back_y - 0.22, base_z + height * 0.5), (width, 0.44, height), material, collection, "primary_architecture", 0.06, signature)
    add_box(prefix + "_Side_L", (center_x - width * 0.5 + 0.22, front_y + depth * 0.5, base_z + height * 0.5), (0.44, depth, height), material, collection, "primary_architecture", 0.06, signature)
    add_box(prefix + "_Side_R", (center_x + width * 0.5 - 0.22, front_y + depth * 0.5, base_z + height * 0.5), (0.44, depth, height), material, collection, "primary_architecture", 0.06, signature)
    for floor in range(floors + 1):
        z = base_z + height * floor / floors
        add_box(prefix + f"_FloorPlate_{floor:02d}", (center_x, front_y + depth * 0.51, z + 0.10), (width - 0.35, depth - 0.45, 0.20), material, collection, "structural_floor", 0.025, signature)


def build_signature_a(materials: dict[str, bpy.types.Material], visible: bpy.types.Collection, collision: bpy.types.Collection) -> dict[str, Any]:
    signature = "A_PREWAR_MANSARD"
    prefix = "SM_M01_HeroFrontage_A"
    center_x, front_y, width, depth, floors, floor_h = -31.0, 0.0, 24.0, 14.0, 6, 3.25
    height = floors * floor_h
    shell_and_floorplates(prefix, center_x, front_y, width, depth, height, floors, materials["plaster_warm"], visible, signature)
    bay_centers = [center_x - 8.4, center_x - 2.8, center_x + 2.8, center_x + 8.4]
    bay_width = 4.55
    for floor in range(floors):
        z0 = floor * floor_h
        add_box(prefix + f"_Spandrel_{floor:02d}", (center_x, front_y + 0.18, z0 + 0.28), (width, 0.38, 0.56), materials["stone"] if floor == 0 else materials["plaster_warm"], visible, "facade_structure", 0.035, signature)
        for pier in range(5):
            x = center_x - width * 0.5 + pier * (width / 4.0)
            add_box(prefix + f"_Pier_{floor:02d}_{pier:02d}", (x, front_y + 0.18, z0 + floor_h * 0.58), (0.72, 0.40, floor_h - 0.56), materials["plaster_cream"], visible, "facade_structure", 0.045, signature)
        for bay, x in enumerate(bay_centers):
            window_z = z0 + 1.82
            add_box(prefix + f"_Recess_{floor:02d}_{bay:02d}", (x, front_y + 0.36, window_z), (bay_width, 0.22, 2.20), materials["dark"], visible, "window_recess", 0.025, signature)
            add_box(prefix + f"_Window_{floor:02d}_{bay:02d}", (x, front_y + 0.27, window_z), (bay_width - 0.42, 0.045, 1.86), materials["window"], visible, "window_glazing", 0.018, signature)
            add_box(prefix + f"_Mullion_{floor:02d}_{bay:02d}", (x, front_y + 0.225, window_z), (0.075, 0.075, 1.88), materials["metal"], visible, "window_frame", 0.012, signature)
            add_box(prefix + f"_Sill_{floor:02d}_{bay:02d}", (x, front_y - 0.03, window_z - 1.03), (bay_width + 0.22, 0.45, 0.12), materials["stone"], visible, "facade_trim", 0.025, signature)
            if floor in {2, 4} and bay in {1, 2}:
                add_box(prefix + f"_BalconySlab_{floor:02d}_{bay:02d}", (x, front_y - 0.78, z0 + 0.58), (bay_width + 0.38, 1.65, 0.18), materials["concrete"], visible, "balcony", 0.035, signature)
                add_railing(prefix + f"_BalconyRail_{floor:02d}_{bay:02d}", x - bay_width * 0.48, x + bay_width * 0.48, front_y - 1.57, z0 + 0.66, materials, visible, signature)
    add_box(prefix + "_EntranceRecess", (center_x - 2.8, front_y + 0.34, 1.55), (4.55, 0.32, 2.70), materials["dark"], visible, "entrance_recess", 0.03, signature)
    add_box(prefix + "_EntranceDoor", (center_x - 2.8, front_y + 0.22, 1.48), (2.1, 0.065, 2.55), materials["wood"], visible, "entrance", 0.04, signature)
    roof_z = height
    x0, x1, y0, y1 = center_x - width * 0.5, center_x + width * 0.5, front_y, front_y + depth
    ridge = y0 + depth * 0.52
    vertices = [(x0, y0, roof_z), (x1, y0, roof_z), (x0, y1, roof_z), (x1, y1, roof_z), (x0, ridge, roof_z + 4.1), (x1, ridge, roof_z + 4.1)]
    faces = [(0, 1, 5, 4), (2, 4, 5, 3), (0, 4, 2), (1, 3, 5), (0, 2, 3, 1)]
    add_custom_mesh(prefix + "_MansardRoof", vertices, faces, materials["roof"], visible, "roofline", signature)
    for x in (center_x - 7.8, center_x, center_x + 7.8):
        add_box(prefix + f"_Dormer_{x:+.1f}", (x, front_y + 2.1, roof_z + 1.75), (3.0, 2.4, 2.6), materials["plaster_cream"], visible, "roof_detail", 0.08, signature)
        add_box(prefix + f"_DormerWindow_{x:+.1f}", (x, front_y + 0.87, roof_z + 1.72), (2.1, 0.055, 1.52), materials["window"], visible, "window_glazing", 0.02, signature)
    add_box("UCX_SM_M01_HeroFrontage_A_00", (center_x, front_y + depth * 0.5, height * 0.5), (width, depth, height), materials["dark"], collision, "unreal_collision", 0.0, signature)
    return {"signature": signature, "width": width, "height": height + 4.1, "floors": floors}


def build_signature_b(materials: dict[str, bpy.types.Material], visible: bpy.types.Collection, collision: bpy.types.Collection) -> dict[str, Any]:
    signature = "B_MODERN_STEPPED"
    prefix = "SM_M01_HeroFrontage_B"
    center_x, front_y, width, depth, floor_h = 0.0, 1.5, 18.0, 12.5, 3.45
    lower_floors, upper_floors = 4, 2
    lower_h = lower_floors * floor_h
    shell_and_floorplates(prefix + "_Lower", center_x, front_y, width, depth, lower_h, lower_floors, materials["plaster_cool"], visible, signature)
    for floor in range(lower_floors):
        z0 = floor * floor_h
        add_box(prefix + f"_HorizontalBand_{floor:02d}", (center_x, front_y + 0.16, z0 + 0.32), (width, 0.42, 0.64), materials["concrete"], visible, "facade_structure", 0.03, signature)
        for bay in range(3):
            x = center_x - 5.8 + bay * 5.8
            add_box(prefix + f"_RibbonRecess_{floor:02d}_{bay:02d}", (x, front_y + 0.34, z0 + 1.98), (5.05, 0.24, 2.22), materials["dark"], visible, "window_recess", 0.025, signature)
            add_box(prefix + f"_RibbonGlass_{floor:02d}_{bay:02d}", (x, front_y + 0.24, z0 + 1.98), (4.64, 0.05, 1.82), materials["window"], visible, "window_glazing", 0.018, signature)
        for fin in range(7):
            x = center_x - width * 0.5 + fin * (width / 6.0)
            add_box(prefix + f"_Fin_{floor:02d}_{fin:02d}", (x, front_y - 0.24, z0 + 1.93), (0.16, 0.78, 2.50), materials["metal"], visible, "facade_fin", 0.025, signature)
    upper_center_x = center_x + 2.2
    upper_width = width - 4.4
    upper_front_y = front_y + 2.4
    upper_h = upper_floors * floor_h
    shell_and_floorplates(prefix + "_Upper", upper_center_x, upper_front_y, upper_width, depth - 2.4, upper_h, upper_floors, materials["plaster_cream"], visible, signature, lower_h)
    for floor in range(upper_floors):
        z0 = lower_h + floor * floor_h
        add_box(prefix + f"_UpperVolume_{floor:02d}", (upper_center_x, upper_front_y + (depth - 2.4) * 0.5, z0 + floor_h * 0.5), (upper_width, depth - 2.4, floor_h), materials["plaster_cream"], visible, "primary_architecture", 0.08, signature)
        for bay, x in enumerate((upper_center_x - 4.1, upper_center_x, upper_center_x + 4.1)):
            add_box(prefix + f"_UpperWindow_{floor:02d}_{bay:02d}", (x, upper_front_y - 0.06, z0 + 1.9), (3.25, 0.055, 1.72), materials["window"], visible, "window_glazing", 0.02, signature)
    add_box(prefix + "_StorefrontRecess", (center_x, front_y + 0.36, 1.72), (15.8, 0.24, 2.85), materials["dark"], visible, "entrance_recess", 0.03, signature)
    add_box(prefix + "_StorefrontGlass", (center_x, front_y + 0.22, 1.72), (15.2, 0.055, 2.55), materials["window"], visible, "storefront", 0.02, signature)
    add_box(prefix + "_Canopy", (center_x, front_y - 1.12, 3.48), (15.7, 2.35, 0.20), materials["metal"], visible, "canopy", 0.05, signature)
    terrace_z = lower_h + upper_h + 0.25
    for x in (upper_center_x - 4.5, upper_center_x, upper_center_x + 4.5):
        add_box(prefix + f"_PergolaPost_{x:+.1f}", (x, upper_front_y + 4.3, terrace_z + 1.35), (0.18, 0.18, 2.7), materials["metal"], visible, "roof_detail", 0.025, signature)
    add_box(prefix + "_PergolaBeam", (upper_center_x, upper_front_y + 4.3, terrace_z + 2.68), (upper_width - 1.2, 0.22, 0.22), materials["metal"], visible, "roof_detail", 0.025, signature)
    total_h = lower_h + upper_h
    add_box("UCX_SM_M01_HeroFrontage_B_00", (center_x, front_y + depth * 0.5, total_h * 0.5), (width, depth, total_h), materials["dark"], collision, "unreal_collision", 0.0, signature)
    return {"signature": signature, "width": width, "height": total_h + 3.0, "floors": lower_floors + upper_floors}


def build_signature_c(materials: dict[str, bpy.types.Material], visible: bpy.types.Collection, collision: bpy.types.Collection) -> dict[str, Any]:
    signature = "C_CORNER_TOWER"
    prefix = "SM_M01_HeroFrontage_C"
    center_x, front_y, width, depth, floors, floor_h = 27.5, 0.4, 25.0, 15.5, 5, 3.30
    height = floors * floor_h
    shell_and_floorplates(prefix, center_x, front_y, width, depth, height, floors, materials["plaster_cream"], visible, signature)
    tower_x = center_x - width * 0.5 + 3.5
    add_cylinder(prefix + "_CornerTower", (tower_x, front_y + 2.3, height * 0.52), 3.35, height + 1.2, materials["plaster_warm"], visible, "primary_architecture", vertices=48, signature=signature)
    for floor in range(floors):
        z0 = floor * floor_h
        add_box(prefix + f"_Course_{floor:02d}", (center_x + 2.5, front_y + 0.18, z0 + 0.28), (width - 5.0, 0.38, 0.56), materials["stone"] if floor == 0 else materials["plaster_cream"], visible, "facade_structure", 0.035, signature)
        for bay, x in enumerate((center_x - 3.0, center_x + 2.5, center_x + 8.0)):
            window_z = z0 + 1.85
            add_box(prefix + f"_Recess_{floor:02d}_{bay:02d}", (x, front_y + 0.34, window_z), (4.35, 0.22, 2.18), materials["dark"], visible, "window_recess", 0.025, signature)
            add_box(prefix + f"_Window_{floor:02d}_{bay:02d}", (x, front_y + 0.24, window_z), (3.92, 0.05, 1.78), materials["window"], visible, "window_glazing", 0.018, signature)
            add_box(prefix + f"_ArchLintel_{floor:02d}_{bay:02d}", (x, front_y - 0.01, window_z + 1.19), (4.62, 0.48, 0.20), materials["stone"], visible, "facade_trim", 0.06, signature)
        for angle_index, angle in enumerate((-58.0, -29.0, 0.0, 29.0, 58.0)):
            radians = math.radians(angle)
            x = tower_x + math.sin(radians) * 3.32
            y = front_y + 2.3 - math.cos(radians) * 3.32
            add_box(prefix + f"_TowerWindow_{floor:02d}_{angle_index:02d}", (x, y, z0 + 1.85), (1.28, 0.055, 1.72), materials["window"], visible, "window_glazing", 0.018, signature).rotation_euler.z = -radians
    add_box(prefix + "_CornerEntranceRecess", (tower_x, front_y - 1.02, 1.60), (3.1, 0.40, 2.85), materials["dark"], visible, "entrance_recess", 0.04, signature)
    add_box(prefix + "_CornerEntrance", (tower_x, front_y - 1.25, 1.55), (2.15, 0.055, 2.58), materials["wood"], visible, "entrance", 0.035, signature)
    add_cylinder(prefix + "_TowerCap", (tower_x, front_y + 2.3, height + 1.25), 3.75, 1.3, materials["roof"], visible, "roofline", vertices=48, signature=signature)
    add_box(prefix + "_Parapet", (center_x + 2.5, front_y + depth * 0.52, height + 0.65), (width - 5.0, depth - 0.4, 1.3), materials["stone"], visible, "roofline", 0.08, signature)
    add_box("UCX_SM_M01_HeroFrontage_C_00", (center_x, front_y + depth * 0.5, height * 0.5), (width, depth, height), materials["dark"], collision, "unreal_collision", 0.0, signature)
    return {"signature": signature, "width": width, "height": height + 2.0, "floors": floors}


def build_streetscape(materials: dict[str, bpy.types.Material], visible: bpy.types.Collection, review: bpy.types.Collection) -> dict[str, int]:
    add_box("SM_M01_HeroFrontage_Sidewalk", (0.0, -3.2, 0.16), (82.0, 6.2, 0.32), materials["concrete"], visible, "hardscape", 0.08)
    add_box("SM_M01_HeroFrontage_Curb", (0.0, -6.22, 0.28), (82.0, 0.28, 0.56), materials["stone"], visible, "hardscape", 0.045)
    for drain_index, x in enumerate((-36.0, -17.0, 3.0, 22.0, 39.0)):
        add_box(f"SM_M01_HeroFrontage_Drain_{drain_index:02d}", (x, -6.38, 0.42), (1.15, 0.42, 0.08), materials["metal"], visible, "drainage", 0.015)
    for light_index, x in enumerate((-38.0, -20.0, 0.0, 20.0, 38.0)):
        add_cylinder(f"SM_M01_HeroFrontage_Light_{light_index:02d}_Pole", (x, -4.7, 3.6), 0.095, 7.2, materials["metal"], visible, "street_furniture", vertices=24)
        add_box(f"SM_M01_HeroFrontage_Light_{light_index:02d}_Arm", (x + 0.52, -4.7, 7.05), (1.08, 0.10, 0.10), materials["metal"], visible, "street_furniture", 0.025)
        add_box(f"SM_M01_HeroFrontage_Light_{light_index:02d}_Lamp", (x + 1.02, -4.7, 6.88), (0.42, 0.30, 0.18), materials["lamp"], visible, "street_furniture", 0.05)
    for bench_index, x in enumerate((-26.0, 11.0, 32.0)):
        add_box(f"SM_M01_HeroFrontage_Bench_{bench_index:02d}_Seat", (x, -2.9, 0.72), (2.2, 0.62, 0.14), materials["wood"], visible, "street_furniture", 0.035)
        add_box(f"SM_M01_HeroFrontage_Bench_{bench_index:02d}_Back", (x, -2.62, 1.27), (2.2, 0.14, 1.0), materials["wood"], visible, "street_furniture", 0.035)
        for side in (-0.82, 0.82):
            add_box(f"SM_M01_HeroFrontage_Bench_{bench_index:02d}_Leg_{side:+.2f}", (x + side, -2.9, 0.37), (0.12, 0.48, 0.62), materials["metal"], visible, "street_furniture", 0.025)
    for bollard_index, x in enumerate((-10.0, -7.4, 44.0)):
        add_cylinder(f"SM_M01_HeroFrontage_Bollard_{bollard_index:02d}", (x, -5.25, 0.55), 0.12, 1.1, materials["metal"], visible, "street_furniture", vertices=24)
    add_box("REVIEW_Road", (0.0, -11.8, -0.06), (96.0, 11.0, 0.22), materials["asphalt"], review, "review_only", 0.04)
    add_box("REVIEW_BackLot", (0.0, 10.0, -0.16), (96.0, 38.0, 0.20), materials["concrete"], review, "review_only", 0.02)
    return {"streetlights": 5, "benches": 3, "drains": 5, "bollards": 3}


def configure_scene(scene: bpy.types.Scene) -> None:
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.exposure = 0.7
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    world = scene.world or bpy.data.worlds.new("M01_HeroFrontage_World")
    scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    require(background is not None, "World background node is missing")
    background.inputs["Color"].default_value = (0.20, 0.28, 0.38, 1.0)
    background.inputs["Strength"].default_value = 0.72


def setup_review(scene: bpy.types.Scene, review: bpy.types.Collection) -> dict[str, bpy.types.Object]:
    camera_data = bpy.data.cameras.new("REVIEW_Camera")
    camera = bpy.data.objects.new("REVIEW_Camera", camera_data)
    review.objects.link(camera)
    scene.camera = camera
    sun_data = bpy.data.lights.new("REVIEW_Sun", type="SUN")
    sun_data.energy = 3.0
    sun_data.angle = math.radians(4.5)
    sun = bpy.data.objects.new("REVIEW_Sun", sun_data)
    sun.rotation_euler = (math.radians(38.0), math.radians(-18.0), math.radians(-32.0))
    review.objects.link(sun)
    fill_data = bpy.data.lights.new("REVIEW_Fill", type="AREA")
    fill_data.energy = 2100.0
    fill_data.shape = "RECTANGLE"
    fill_data.size = 48.0
    fill_data.size_y = 26.0
    fill = bpy.data.objects.new("REVIEW_Fill", fill_data)
    fill.location = (0.0, -34.0, 26.0)
    fill.rotation_euler = (math.radians(58.0), 0.0, 0.0)
    review.objects.link(fill)
    return {"camera": camera, "sun": sun, "fill": fill}


def point_camera(camera: bpy.types.Object, location: tuple[float, float, float], target: tuple[float, float, float], lens: float) -> None:
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = lens


def set_condition(scene: bpy.types.Scene, rig: dict[str, bpy.types.Object], condition: str) -> None:
    background = scene.world.node_tree.nodes.get("Background")
    require(background is not None, "World background node is missing")
    if condition == "daylight":
        rig["sun"].data.energy = 3.2
        rig["fill"].data.energy = 2200.0
        background.inputs["Color"].default_value = (0.24, 0.34, 0.48, 1.0)
        background.inputs["Strength"].default_value = 0.78
        scene.view_settings.exposure = 0.65
    elif condition == "overcast":
        rig["sun"].data.energy = 1.0
        rig["fill"].data.energy = 2500.0
        background.inputs["Color"].default_value = (0.31, 0.34, 0.38, 1.0)
        background.inputs["Strength"].default_value = 0.92
        scene.view_settings.exposure = 0.85
    elif condition == "wet":
        rig["sun"].data.energy = 1.6
        rig["fill"].data.energy = 2450.0
        background.inputs["Color"].default_value = (0.18, 0.24, 0.31, 1.0)
        background.inputs["Strength"].default_value = 0.82
        scene.view_settings.exposure = 0.9
    else:
        rig["sun"].data.energy = 0.18
        rig["fill"].data.energy = 1250.0
        background.inputs["Color"].default_value = (0.018, 0.028, 0.055, 1.0)
        background.inputs["Strength"].default_value = 0.42
        scene.view_settings.exposure = 1.2


def render_one(scene: bpy.types.Scene, camera: bpy.types.Object, path: Path, location: tuple[float, float, float], target: tuple[float, float, float], lens: float, size: tuple[int, int]) -> dict[str, Any]:
    scene.render.resolution_x, scene.render.resolution_y = size
    point_camera(camera, location, target, lens)
    scene.render.filepath = str(path)
    print(json.dumps({"event": "render_start", "path": str(path)}), flush=True)
    bpy.ops.render.render(write_still=True)
    require(path.is_file() and path.stat().st_size > 0, f"Render missing: {path}")
    print(json.dumps({"event": "render_complete", "path": str(path), "bytes": path.stat().st_size}), flush=True)
    return {"path": str(path), "bytes": path.stat().st_size, "resolution": list(size)}


def render_reviews(scene: bpy.types.Scene, rig: dict[str, bpy.types.Object], output: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    checkpoints_dir = output / "checkpoints"
    renders_dir = output / "renders"
    checkpoints_dir.mkdir()
    renders_dir.mkdir()
    camera = rig["camera"]
    set_condition(scene, rig, "daylight")
    checkpoint_views = [
        ("checkpoint_01_overall", (0.0, -76.0, 28.0), (0.0, 5.0, 10.0), 54.0),
        ("checkpoint_02_facade_depth", (-8.0, -31.0, 10.0), (-8.0, 1.0, 9.0), 60.0),
        ("checkpoint_03_flight_height", (0.0, -54.0, 18.0), (4.0, 3.0, 10.5), 57.0),
    ]
    checkpoints = [
        render_one(scene, camera, checkpoints_dir / f"{name}.png", location, target, lens, CHECKPOINT_SIZE)
        for name, location, target, lens in checkpoint_views
    ]
    final_views = [
        ("daylight", "01_overall", (0.0, -74.0, 27.0), (0.0, 5.0, 10.0), 54.0),
        ("daylight", "02_signature_a", (-31.0, -26.0, 10.0), (-31.0, 1.5, 10.5), 58.0),
        ("daylight", "03_signature_b", (0.0, -25.0, 9.0), (0.0, 2.5, 9.5), 60.0),
        ("daylight", "04_signature_c", (28.0, -27.0, 9.5), (28.0, 2.0, 9.0), 58.0),
        ("daylight", "05_rear_gunner_height", (-7.0, -51.0, 17.0), (3.0, 3.0, 11.0), 58.0),
        ("overcast", "06_shadow_side_readability", (41.0, -40.0, 15.0), (5.0, 4.0, 10.0), 56.0),
        ("wet", "07_streetscape_oblique", (-42.0, -31.0, 5.2), (-8.0, -1.0, 3.0), 54.0),
        ("night", "08_night_frontage", (2.0, -48.0, 12.0), (2.0, 2.0, 10.0), 57.0),
    ]
    finals = []
    for condition, name, location, target, lens in final_views:
        set_condition(scene, rig, condition)
        record = render_one(scene, camera, renders_dir / f"{condition}_{name}.png", location, target, lens, RENDER_SIZE)
        record.update({"condition": condition, "camera": name})
        finals.append(record)
    return checkpoints, finals


def object_receipt(collections: Iterable[bpy.types.Collection]) -> dict[str, Any]:
    records = []
    for collection in collections:
        for obj in sorted(collection.all_objects, key=lambda item: item.name):
            record: dict[str, Any] = {
                "name": obj.name,
                "type": obj.type,
                "role": obj.get("SKG_Role"),
                "signature": obj.get("SKG_BuildingSignature"),
                "materials": [slot.material.name for slot in obj.material_slots if slot.material],
            }
            if obj.type == "MESH":
                record.update({
                    "vertices": len(obj.data.vertices),
                    "polygons": len(obj.data.polygons),
                    "uv_layers": len(obj.data.uv_layers),
                })
            records.append(record)
    renderable = [record for record in records if record["type"] == "MESH" and record["role"] != "unreal_collision"]
    return {
        "schema": "skyguard.m01-hero-coastal-frontage-cell01.topology-material.v1",
        "objects": records,
        "mesh_object_count": sum(record["type"] == "MESH" for record in records),
        "renderable_vertex_count": sum(int(record.get("vertices", 0)) for record in renderable),
        "renderable_polygon_count": sum(int(record.get("polygons", 0)) for record in renderable),
        "all_renderable_meshes_have_uv0": all(int(record.get("uv_layers", 0)) >= 1 for record in renderable),
        "distinct_material_count": len({material for record in renderable for material in record["materials"]}),
        "distinct_building_signatures": sorted({record["signature"] for record in renderable if record["signature"]}),
        "passed": True,
    }


def export_glb(path: Path, collections: Iterable[bpy.types.Collection]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    selected = []
    for collection in collections:
        for obj in collection.all_objects:
            obj.select_set(True)
            selected.append(obj)
    require(selected, "No governed objects selected for GLB export")
    bpy.context.view_layer.objects.active = next(obj for obj in selected if obj.type == "MESH")
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True, export_apply=True, export_animations=False, export_lights=False, export_cameras=False)
    require(path.is_file() and path.stat().st_size > 0, "GLB export was not created")


def main() -> int:
    args = parse_args()
    require(args.asset_id == ASSET_ID, f"Unexpected asset id: {args.asset_id}")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    require(not any(output.iterdir()), f"Output directory is not empty: {output}")
    require(PROVENANCE.is_file(), "Texture provenance manifest is missing")
    require(WINDOW_ATLAS.is_file(), "Window atlas is missing")
    for family in PBR_SOURCES.values():
        for path in family.values():
            require(path.is_file(), f"Texture authority missing: {path}")

    clear_scene()
    scene = bpy.context.scene
    configure_scene(scene)
    visible = get_collection("M01_HERO_FRONTAGE_VISIBLE")
    collision = get_collection("M01_HERO_FRONTAGE_COLLISION")
    sockets = get_collection("M01_HERO_FRONTAGE_SOCKETS")
    review = get_collection("M01_HERO_FRONTAGE_REVIEW_ONLY")
    materials = build_materials()
    signatures = [
        build_signature_a(materials, visible, collision),
        build_signature_b(materials, visible, collision),
        build_signature_c(materials, visible, collision),
    ]
    streetscape = build_streetscape(materials, visible, review)
    add_empty("SOCKET_M01_HeroFrontage_Origin", (0.0, 0.0, 0.0), sockets, "unreal_socket")
    add_empty("SOCKET_M01_HeroFrontage_A", (-31.0, 0.0, 0.0), sockets, "unreal_socket")
    add_empty("SOCKET_M01_HeroFrontage_B", (0.0, 1.5, 0.0), sockets, "unreal_socket")
    add_empty("SOCKET_M01_HeroFrontage_C", (27.5, 0.4, 0.0), sockets, "unreal_socket")
    rig = setup_review(scene, review)

    topology = object_receipt((visible, collision, sockets))
    require(topology["mesh_object_count"] >= 180, f"Insufficient authored object count: {topology['mesh_object_count']}")
    require(topology["renderable_vertex_count"] >= 8000, f"Insufficient authored topology: {topology['renderable_vertex_count']}")
    require(topology["all_renderable_meshes_have_uv0"], "Renderable UV0 coverage failed")
    require(len(topology["distinct_building_signatures"]) == 3, "Three distinct building signatures are required")
    require(topology["distinct_material_count"] >= 10, "Material diversity is below the hero-cell floor")

    checkpoints, renders = render_reviews(scene, rig, output)
    blend_path = output / "M01_Hero_Coastal_Frontage_Cell01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    glb_path = output / "M01_Hero_Coastal_Frontage_Cell01.glb"
    export_glb(glb_path, (visible, collision, sockets))

    write_json(output / "topology_material_receipt.json", topology)
    write_json(
        output / "design_contract_receipt.json",
        {
            "schema": "skyguard.m01-hero-coastal-frontage-cell01.design-contract.v1",
            "asset_id": ASSET_ID,
            "fresh_asset_specific_geometry": True,
            "whole_scene_generator": False,
            "external_models": False,
            "generated_substitutes": False,
            "governed_local_pbr": True,
            "building_signatures": signatures,
            "streetscape": streetscape,
            "coordinate_contract": {"units": "meters", "forward": "+X", "up": "+Z"},
            "unreal_owns": ["final_water", "shoreline_simulation", "vegetation", "lighting", "atmosphere", "world_assembly"],
            "promotion_authorized": False,
            "unreal_import_authorized": False,
            "passed": True,
        },
    )
    write_json(
        output / "artifact_receipt.json",
        {
            "schema": "skyguard.m01-hero-coastal-frontage-cell01.artifacts.v1",
            "asset_id": ASSET_ID,
            "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size, "sha256": sha256(blend_path)},
            "glb": {"path": str(glb_path), "bytes": glb_path.stat().st_size, "sha256": sha256(glb_path)},
            "checkpoint_count": len(checkpoints),
            "final_render_count": len(renders),
            "total_render_count": len(checkpoints) + len(renders),
            "checkpoint_dimensions": list(CHECKPOINT_SIZE),
            "final_render_dimensions": list(RENDER_SIZE),
            "checkpointed_visual_review": True,
            "direct_full_resolution_review_required": True,
            "unreal_import_authorized": False,
            "passed": True,
        },
    )
    print(json.dumps({"gate": GATE, "classification": "PASSED_AUTOMATIC_AWAITING_POSTFLIGHT_AND_DIRECT_VISUAL_REVIEW", "topology": topology}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
