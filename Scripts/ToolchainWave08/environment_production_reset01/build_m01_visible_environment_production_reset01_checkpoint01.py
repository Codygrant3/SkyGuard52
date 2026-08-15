"""Build a fresh Mission 1 modular coastal-environment production checkpoint.

The generator starts from Blender's factory scene and does not read any failed
StageA mesh.  It authors new modular geometry, uses only the governed local
Poly Haven surface library, packs resources, exports Unreal-ready GLBs, and
renders four fixed daylight review cameras.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"D:\Skyguard52")
OUTPUT = ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentProductionReset01_Checkpoint01"
EXPORTS = OUTPUT / "exports"
RENDERS = OUTPUT / "renders"
TEXTURES = ROOT / r"Content\Skyguard\Textures\PolyHaven"
BLEND_PATH = OUTPUT / "M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01.blend"
RNG = random.Random(5201)

ASSETS: dict[str, list[bpy.types.Object]] = {}
MATERIALS: dict[str, bpy.types.Material] = {}
TEXTURE_AUTHORITIES: list[dict[str, object]] = []


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def record_file(path: Path) -> dict[str, object]:
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def ensure_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_asset(obj: bpy.types.Object, asset: str) -> bpy.types.Object:
    collection = ensure_collection(asset)
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    collection.objects.link(obj)
    ASSETS.setdefault(asset, []).append(obj)
    obj["skyguard_asset_family"] = asset
    return obj


def set_active(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_bevel(obj: bpy.types.Object, width: float, segments: int = 3) -> None:
    if width <= 0:
        return
    modifier = obj.modifiers.new("BEVEL_PRODUCTION", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"
    set_active(obj)
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def assign_material(obj: bpy.types.Object, material: bpy.types.Material | None) -> None:
    if material is not None and hasattr(obj.data, "materials"):
        obj.data.materials.append(material)


def box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material | None,
    asset: str,
    bevel: float = 0.035,
    render: bool = True,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_bevel(obj, min(bevel, min(dimensions) * 0.2), 3)
    assign_material(obj, material)
    obj.hide_render = not render
    return move_to_asset(obj, asset)


def cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    material: bpy.types.Material | None,
    asset: str,
    vertices: int = 24,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.02,
    render: bool = True,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_bevel(obj, bevel, 2)
    assign_material(obj, material)
    obj.hide_render = not render
    return move_to_asset(obj, asset)


def sphere(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    asset: str,
    subdivisions: int = 2,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign_material(obj, material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return move_to_asset(obj, asset)


def mesh_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    material: bpy.types.Material,
    asset: str,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    ensure_collection(asset).objects.link(obj)
    ASSETS.setdefault(asset, []).append(obj)
    obj["skyguard_asset_family"] = asset
    assign_material(obj, material)
    return obj


def empty(name: str, location: tuple[float, float, float], asset: str, display: str = "PLAIN_AXES") -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = display
    obj.empty_display_size = 0.75
    obj.location = location
    ensure_collection(asset).objects.link(obj)
    ASSETS.setdefault(asset, []).append(obj)
    obj["skyguard_asset_family"] = asset
    return obj


def texture_triplet(folder: str, stem: str) -> tuple[Path, Path, Path]:
    directory = TEXTURES / folder
    files = list(directory.iterdir())
    diffuse = next(path for path in files if "diff" in path.name.lower())
    normal = next(path for path in files if "nor_gl" in path.name.lower())
    rough = next(path for path in files if "rough" in path.name.lower())
    for path in (diffuse, normal, rough):
        require(path.is_file(), f"Missing texture authority: {path}")
        TEXTURE_AUTHORITIES.append(record_file(path))
    return diffuse, normal, rough


def pbr_material(name: str, folder: str, stem: str, tile_scale: float = 0.4, metallic: float = 0.0) -> bpy.types.Material:
    if name in MATERIALS:
        return MATERIALS[name]
    diffuse, normal, rough = texture_triplet(folder, stem)
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (tile_scale, tile_scale, tile_scale)
    color = nodes.new("ShaderNodeTexImage")
    color.image = bpy.data.images.load(str(diffuse), check_existing=True)
    color.extension = "REPEAT"
    roughness = nodes.new("ShaderNodeTexImage")
    roughness.image = bpy.data.images.load(str(rough), check_existing=True)
    roughness.image.colorspace_settings.name = "Non-Color"
    roughness.extension = "REPEAT"
    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.image = bpy.data.images.load(str(normal), check_existing=True)
    normal_tex.image.colorspace_settings.name = "Non-Color"
    normal_tex.extension = "REPEAT"
    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.inputs["Strength"].default_value = 0.65
    bsdf.inputs["Metallic"].default_value = metallic
    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])
    for node in (color, roughness, normal_tex):
        links.new(mapping.outputs["Vector"], node.inputs["Vector"])
    links.new(color.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(roughness.outputs["Color"], bsdf.inputs["Roughness"])
    links.new(normal_tex.outputs["Color"], normal_map.inputs["Color"])
    links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    material["skyguard_provenance"] = "governed_project_local_polyhaven"
    MATERIALS[name] = material
    return material


def flat_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    if name in MATERIALS:
        return MATERIALS[name]
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emission
            bsdf.inputs["Emission Strength"].default_value = emission_strength
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = emission
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    MATERIALS[name] = material
    return material


def water_material() -> bpy.types.Material:
    material = bpy.data.materials.new("M_ENV_Ocean_Review")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 1.2
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.55
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.2
    texcoord = nodes.new("ShaderNodeTexCoord")
    bsdf.inputs["Base Color"].default_value = (0.012, 0.09, 0.14, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.18
    bsdf.inputs["Metallic"].default_value = 0.15
    links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    MATERIALS[material.name] = material
    return material


def build_materials() -> dict[str, bpy.types.Material]:
    return {
        "sand": pbr_material("M_ENV_Sand_Coast_2K", "coast_sand_01", "coast_sand_01", 0.32),
        "asphalt": pbr_material("M_ENV_Asphalt_2K", "asphalt_02", "asphalt_02", 0.28),
        "concrete": pbr_material("M_ENV_Concrete_Wall_2K", "concrete_wall_006", "concrete_wall_006", 0.42),
        "pavers": pbr_material("M_ENV_Concrete_Pavers_2K", "concrete_floor_painted", "concrete_floor_painted", 0.4),
        "plaster_blue": pbr_material("M_ENV_Plaster_Blue_Weathered_2K", "blue_plaster_weathered", "blue_plaster_weathered", 0.5),
        "plaster_warm": pbr_material("M_ENV_Plaster_Warm_2K", "painted_plaster_wall", "painted_plaster_wall", 0.48),
        "brick": pbr_material("M_ENV_Brick_2K", "brick_wall_006", "brick_wall_006", 0.34),
        "roof": pbr_material("M_ENV_Roof_2K", "roof_07", "roof_07", 0.44),
        "metal": pbr_material("M_ENV_Metal_Plate_2K", "metal_plate", "metal_plate", 0.55, 0.75),
        "rust": pbr_material("M_ENV_Rust_Metal_2K", "green_metal_rust", "green_metal_rust", 0.52, 0.5),
        "wood": pbr_material("M_ENV_Wood_Worn_2K", "wood_cabinet_worn_long", "wood_cabinet_worn_long", 0.55),
        "glass": flat_material("M_ENV_Glass_Dark", (0.015, 0.045, 0.065, 1.0), 0.12, 0.18),
        "interior": flat_material("M_ENV_Interior_Shadow", (0.004, 0.006, 0.008, 1.0), 0.95),
        "lane": flat_material("M_ENV_Road_Marking", (0.72, 0.70, 0.56, 1.0), 0.62),
        "leaf_a": flat_material("M_ENV_Leaf_A", (0.055, 0.19, 0.07, 1.0), 0.72),
        "leaf_b": flat_material("M_ENV_Leaf_B", (0.09, 0.27, 0.105, 1.0), 0.68),
        "leaf_c": flat_material("M_ENV_Leaf_C", (0.035, 0.125, 0.055, 1.0), 0.78),
        "bark": flat_material("M_ENV_Bark", (0.12, 0.055, 0.025, 1.0), 0.88),
        "foam": flat_material("M_ENV_Foam", (0.72, 0.82, 0.82, 1.0), 0.35),
        "lamp": flat_material("M_ENV_Lamp_Emission", (0.4, 0.24, 0.08, 1.0), 0.18, 0.0, (1.0, 0.42, 0.08, 1.0), 3.5),
        "water": water_material(),
    }


def add_railing(asset: str, prefix: str, x0: float, x1: float, y: float, z0: float, height: float, material: bpy.types.Material) -> None:
    box(prefix + "_TOP", ((x0 + x1) / 2, y, z0 + height), (x1 - x0, 0.055, 0.055), material, asset, 0.012)
    box(prefix + "_MID", ((x0 + x1) / 2, y, z0 + height * 0.52), (x1 - x0, 0.04, 0.04), material, asset, 0.01)
    spacing = 0.45
    count = max(2, int((x1 - x0) / spacing))
    for index in range(count + 1):
        x = x0 + (x1 - x0) * index / count
        box(f"{prefix}_POST_{index:02d}", (x, y, z0 + height / 2), (0.045, 0.045, height), material, asset, 0.008)


def build_building(
    asset: str,
    center_x: float,
    center_y: float,
    width: float,
    depth: float,
    floors: int,
    bays: int,
    facade: bpy.types.Material,
    accent: bpy.types.Material,
    mats: dict[str, bpy.types.Material],
    balcony_mode: int,
) -> None:
    floor_h = 3.05
    ground_h = 3.65
    total_h = ground_h + floors * floor_h
    front_y = center_y - depth / 2
    rear_volume_depth = depth - 0.75
    box(f"{asset}_STRUCTURE", (center_x, front_y + 0.75 + rear_volume_depth / 2, total_h / 2), (width, rear_volume_depth, total_h), facade, asset, 0.12)
    box(f"{asset}_FOUNDATION", (center_x, center_y, -0.35), (width + 0.4, depth + 0.4, 0.7), mats["concrete"], asset, 0.06)
    bay_w = width / bays
    pier_w = 0.32

    # Ground floor arcade/storefronts with deep glazing and varied entrances.
    box(f"{asset}_GROUND_SPANDREL", (center_x, front_y - 0.04, ground_h - 0.28), (width, 0.48, 0.56), accent, asset, 0.035)
    for bay in range(bays):
        x_center = center_x - width / 2 + bay_w * (bay + 0.5)
        opening_w = bay_w - pier_w * 1.4
        box(f"{asset}_GF_VOID_{bay:02d}", (x_center, front_y + 0.39, ground_h * 0.48), (opening_w, 0.06, ground_h - 0.72), mats["interior"], asset, 0.015)
        box(f"{asset}_GF_GLASS_{bay:02d}", (x_center, front_y + 0.31, ground_h * 0.5), (opening_w - 0.12, 0.035, ground_h - 0.96), mats["glass"], asset, 0.008)
        box(f"{asset}_GF_MULLION_V_{bay:02d}", (x_center, front_y + 0.25, ground_h * 0.5), (0.075, 0.075, ground_h - 0.88), mats["metal"], asset, 0.012)
        box(f"{asset}_GF_MULLION_H_{bay:02d}", (x_center, front_y + 0.25, 2.45), (opening_w - 0.06, 0.075, 0.075), mats["metal"], asset, 0.012)
        if bay % 3 == 1:
            box(f"{asset}_CANOPY_{bay:02d}", (x_center, front_y - 0.78, 3.08), (opening_w, 1.45, 0.12), mats["metal"], asset, 0.04)

    for boundary in range(bays + 1):
        x = center_x - width / 2 + bay_w * boundary
        box(f"{asset}_PIER_{boundary:02d}", (x, front_y, total_h / 2), (pier_w, 0.52, total_h), accent if boundary % 2 else facade, asset, 0.035)

    # Upper facade is assembled from piers, spandrels, recessed glass and frames.
    for floor in range(floors):
        z_base = ground_h + floor * floor_h
        box(f"{asset}_SPANDREL_{floor:02d}", (center_x, front_y, z_base + floor_h - 0.28), (width, 0.52, 0.56), facade, asset, 0.035)
        for bay in range(bays):
            x_center = center_x - width / 2 + bay_w * (bay + 0.5)
            opening_w = bay_w - pier_w * 1.55
            win_h = 1.82 if (bay + floor) % 4 else 1.62
            win_z = z_base + 1.55
            box(f"{asset}_VOID_{floor:02d}_{bay:02d}", (x_center, front_y + 0.37, win_z), (opening_w, 0.08, win_h + 0.24), mats["interior"], asset, 0.018)
            box(f"{asset}_GLASS_{floor:02d}_{bay:02d}", (x_center, front_y + 0.29, win_z), (opening_w - 0.14, 0.035, win_h), mats["glass"], asset, 0.006)
            frame_mat = mats["metal"]
            for suffix, loc, dims in (
                ("L", (x_center - opening_w / 2, front_y + 0.20, win_z), (0.085, 0.11, win_h + 0.18)),
                ("R", (x_center + opening_w / 2, front_y + 0.20, win_z), (0.085, 0.11, win_h + 0.18)),
                ("T", (x_center, front_y + 0.20, win_z + win_h / 2), (opening_w, 0.11, 0.085)),
                ("B", (x_center, front_y + 0.20, win_z - win_h / 2), (opening_w, 0.11, 0.085)),
                ("V", (x_center, front_y + 0.18, win_z), (0.055, 0.10, win_h)),
            ):
                box(f"{asset}_FRAME_{floor:02d}_{bay:02d}_{suffix}", loc, dims, frame_mat, asset, 0.012)

            has_balcony = ((bay + floor + balcony_mode) % 3 == 0) or (balcony_mode == 2 and bay in (1, bays - 2))
            if has_balcony:
                slab_y = front_y - 0.82
                box(f"{asset}_BALCONY_SLAB_{floor:02d}_{bay:02d}", (x_center, slab_y, z_base + 0.36), (opening_w + 0.48, 1.65, 0.16), mats["concrete"], asset, 0.045)
                add_railing(asset, f"{asset}_BALCONY_RAIL_{floor:02d}_{bay:02d}", x_center - opening_w / 2 - 0.18, x_center + opening_w / 2 + 0.18, front_y - 1.62, z_base + 0.45, 1.05, mats["metal"])

            if (bay * 7 + floor * 3 + balcony_mode) % 11 == 0:
                box(f"{asset}_AC_{floor:02d}_{bay:02d}", (x_center + opening_w * 0.34, front_y - 0.18, z_base + 0.62), (0.52, 0.32, 0.38), mats["metal"], asset, 0.035)

    # Side returns, layered cornice and non-identical roof equipment.
    for side in (-1, 1):
        side_x = center_x + side * width / 2
        box(f"{asset}_SIDE_RETURN_{'L' if side < 0 else 'R'}", (side_x, center_y, total_h / 2), (0.42, depth, total_h), accent, asset, 0.05)
        cylinder(f"{asset}_DOWNSPOUT_{'L' if side < 0 else 'R'}", (side_x - side * 0.22, front_y - 0.15, total_h / 2), 0.075, total_h, mats["metal"], asset, 18, bevel=0.01)

    box(f"{asset}_CORNICE", (center_x, front_y - 0.12, total_h - 0.08), (width + 0.45, 0.72, 0.34), mats["concrete"], asset, 0.07)
    box(f"{asset}_ROOF", (center_x, center_y, total_h + 0.18), (width + 0.15, depth + 0.1, 0.36), mats["roof"], asset, 0.06)
    for side in (-1, 1):
        box(f"{asset}_PARAPET_X_{side:+d}", (center_x + side * (width / 2 - 0.16), center_y, total_h + 0.72), (0.28, depth, 1.1), mats["concrete"], asset, 0.045)
    for side in (-1, 1):
        box(f"{asset}_PARAPET_Y_{side:+d}", (center_x, center_y + side * (depth / 2 - 0.16), total_h + 0.72), (width, 0.28, 1.1), mats["concrete"], asset, 0.045)

    box(f"{asset}_ROOF_SERVICE", (center_x - width * 0.18, center_y + 0.3, total_h + 1.55), (width * 0.26, depth * 0.28, 1.65), accent, asset, 0.07)
    for index in range(3):
        box(f"{asset}_ROOF_LOUVRE_{index:02d}", (center_x - width * 0.18, center_y - depth * 0.15, total_h + 1.18 + index * 0.31), (width * 0.18, 0.08, 0.08), mats["metal"], asset, 0.012)
    cylinder(f"{asset}_ROOF_VENT", (center_x + width * 0.18, center_y, total_h + 1.15), 0.42, 1.65, mats["metal"], asset, 28, bevel=0.025)
    cylinder(f"{asset}_ANTENNA", (center_x + width * 0.31, center_y + depth * 0.15, total_h + 2.8), 0.035, 4.2, mats["metal"], asset, 12, bevel=0.005)
    empty(f"SOCKET_{asset}_Origin", (center_x - width / 2, center_y - depth / 2, 0.0), asset)
    collision = box(f"UCX_{asset}_00", (center_x, center_y, total_h / 2), (width, depth, total_h), None, asset, 0.0, False)
    collision.display_type = "WIRE"


def build_tree(asset: str, origin: tuple[float, float, float], scale: float, mats: dict[str, bpy.types.Material], seed: int) -> None:
    rng = random.Random(seed)
    x, y, z = origin
    trunk_h = 3.8 * scale
    cylinder(f"{asset}_TRUNK", (x, y, z + trunk_h / 2), 0.22 * scale, trunk_h, mats["bark"], asset, 18, bevel=0.035 * scale)
    branch_tips: list[tuple[float, float, float]] = []
    for index in range(9):
        angle = index * math.tau / 9 + rng.uniform(-0.22, 0.22)
        length = rng.uniform(1.3, 2.25) * scale
        start_z = z + rng.uniform(2.2, 3.65) * scale
        end = (x + math.cos(angle) * length, y + math.sin(angle) * length, start_z + rng.uniform(0.6, 1.65) * scale)
        direction = Vector(end) - Vector((x, y, start_z))
        midpoint = Vector((x, y, start_z)) + direction * 0.5
        obj = cylinder(f"{asset}_BRANCH_{index:02d}", tuple(midpoint), 0.075 * scale, direction.length, mats["bark"], asset, 14, bevel=0.018 * scale)
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(direction.normalized())
        branch_tips.append(end)
    for branch_index, tip in enumerate(branch_tips):
        for leaf_index in range(7):
            offset = Vector((rng.uniform(-0.75, 0.75), rng.uniform(-0.75, 0.75), rng.uniform(-0.5, 0.65))) * scale
            loc = Vector(tip) + offset
            leaf_mat = mats[("leaf_a", "leaf_b", "leaf_c")[(branch_index + leaf_index) % 3]]
            sphere(f"{asset}_LEAF_{branch_index:02d}_{leaf_index:02d}", tuple(loc), (rng.uniform(0.45, 0.82) * scale, rng.uniform(0.32, 0.62) * scale, rng.uniform(0.24, 0.5) * scale), leaf_mat, asset, 2)
    empty(f"SOCKET_{asset}_Origin", origin, asset)


def build_street_lamp(asset: str, x: float, y: float, mats: dict[str, bpy.types.Material]) -> None:
    cylinder(f"{asset}_POLE", (x, y, 3.25), 0.09, 6.5, mats["metal"], asset, 20, bevel=0.018)
    box(f"{asset}_BASE", (x, y, 0.18), (0.48, 0.48, 0.36), mats["concrete"], asset, 0.055)
    box(f"{asset}_ARM", (x, y - 0.58, 6.22), (0.08, 1.18, 0.08), mats["metal"], asset, 0.018)
    box(f"{asset}_HEAD", (x, y - 1.12, 6.04), (0.62, 0.42, 0.22), mats["metal"], asset, 0.06)
    box(f"{asset}_LAMP", (x, y - 1.13, 5.91), (0.46, 0.3, 0.045), mats["lamp"], asset, 0.02)


def build_bench(asset: str, x: float, y: float, mats: dict[str, bpy.types.Material]) -> None:
    for side in (-1, 1):
        box(f"{asset}_LEG_{side:+d}", (x + side * 0.78, y, 0.45), (0.12, 0.72, 0.82), mats["metal"], asset, 0.035)
    for index in range(5):
        box(f"{asset}_SEAT_{index:02d}", (x, y - 0.28 + index * 0.14, 0.82), (2.0, 0.105, 0.105), mats["wood"], asset, 0.025)
    for index in range(4):
        box(f"{asset}_BACK_{index:02d}", (x, y + 0.35, 1.02 + index * 0.17), (2.0, 0.105, 0.105), mats["wood"], asset, 0.025)


def build_lighthouse(mats: dict[str, bpy.types.Material]) -> None:
    asset = "SM_M01_Lighthouse_Production_A"
    x, y = 56.0, -1.5
    # Tapered tower from stacked subtly narrowing drums; gallery and rail are separate.
    base_z = 0.0
    sections = [(3.2, 4.8), (3.0, 4.6), (2.75, 4.4), (2.5, 4.2)]
    running = base_z
    for index, (radius, height) in enumerate(sections):
        cylinder(f"{asset}_TOWER_{index:02d}", (x, y, running + height / 2), radius, height, mats["plaster_warm"] if index % 2 == 0 else mats["concrete"], asset, 64, bevel=0.08)
        running += height - 0.12
        cylinder(f"{asset}_BAND_{index:02d}", (x, y, running), radius + 0.08, 0.22, mats["metal"], asset, 64, bevel=0.025)
    gallery_z = running + 0.55
    cylinder(f"{asset}_GALLERY_DECK", (x, y, gallery_z), 3.1, 0.34, mats["metal"], asset, 64, bevel=0.06)
    cylinder(f"{asset}_LANTERN_BASE", (x, y, gallery_z + 1.3), 1.95, 2.35, mats["glass"], asset, 48, bevel=0.045)
    for index in range(16):
        angle = index * math.tau / 16
        px = x + math.cos(angle) * 2.7
        py = y + math.sin(angle) * 2.7
        cylinder(f"{asset}_RAIL_POST_{index:02d}", (px, py, gallery_z + 0.7), 0.035, 1.25, mats["metal"], asset, 10, bevel=0.005)
    for level in (0.35, 0.98):
        bpy.ops.mesh.primitive_torus_add(major_radius=2.7, minor_radius=0.035, major_segments=64, minor_segments=8, location=(x, y, gallery_z + level))
        rail = bpy.context.object
        rail.name = f"{asset}_RAIL_RING_{int(level*100):03d}"
        assign_material(rail, mats["metal"])
        move_to_asset(rail, asset)
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=2.35, radius2=0.18, depth=2.2, location=(x, y, gallery_z + 3.55))
    roof = bpy.context.object
    roof.name = f"{asset}_ROOF"
    assign_material(roof, mats["rust"])
    move_to_asset(roof, asset)
    cylinder(f"{asset}_FINIAL", (x, y, gallery_z + 5.05), 0.07, 0.9, mats["metal"], asset, 12, bevel=0.012)
    empty(f"SOCKET_{asset}_Origin", (x, y, 0.0), asset)
    collision = cylinder(f"UCX_{asset}_00", (x, y, running / 2), 3.2, running, None, asset, 20, bevel=0, render=False)
    collision.display_type = "WIRE"


def build_coastal_district(mats: dict[str, bpy.types.Material]) -> None:
    asset = "SM_M01_CoastalDistrict_Production_A"
    length = 140.0
    x0 = -length / 2
    segments = 28
    bands = [(-46.0, -0.7), (-24.0, -0.45), (-17.0, -0.12), (-11.0, 0.2)]
    vertices: list[tuple[float, float, float]] = []
    for yi, (y, base_z) in enumerate(bands):
        for xi in range(segments + 1):
            x = x0 + length * xi / segments
            noise = (math.sin(x * 0.17 + yi) * 0.11 + math.sin(x * 0.043 + yi * 2.1) * 0.08) * (0.2 if yi == 0 else 1.0)
            vertices.append((x, y, base_z + noise))
    faces = []
    row = segments + 1
    for yi in range(len(bands) - 1):
        for xi in range(segments):
            a = yi * row + xi
            faces.append((a, a + 1, a + 1 + row, a + row))
    beach = mesh_object(f"{asset}_BEACH_DUNE", vertices, faces, mats["sand"], asset)
    apply_bevel(beach, 0.035, 2)
    box(f"{asset}_WATER", (0, -58, -0.95), (180, 68, 0.3), mats["water"], asset, 0.0)
    # Layered foam/wet contact strips avoid the old hard brown waterline.
    for index, (y, width, z) in enumerate(((-24.2, 1.2, -0.30), (-22.8, 0.55, -0.23), (-21.4, 0.3, -0.18))):
        strip = box(f"{asset}_FOAM_{index:02d}", (0, y, z), (150, width, 0.025), mats["foam"], asset, 0.0)
        strip.rotation_euler[2] = math.radians(0.25 * (-1 if index % 2 else 1))
    # Seawall with panel joints, battered base and cap.
    box(f"{asset}_SEAWALL_BODY", (0, -9.4, 1.35), (length, 1.2, 2.7), mats["concrete"], asset, 0.08)
    box(f"{asset}_SEAWALL_CAP", (0, -9.55, 2.82), (length, 1.6, 0.24), mats["concrete"], asset, 0.045)
    for x in range(-65, 66, 5):
        box(f"{asset}_SEAWALL_JOINT_{x:+04d}", (float(x), -8.79, 1.38), (0.04, 0.025, 2.35), mats["interior"], asset, 0.005)
    # Promenade, curb, road and inland sidewalk.
    box(f"{asset}_PROMENADE", (0, -5.5, 2.92), (length, 6.8, 0.32), mats["pavers"], asset, 0.055)
    box(f"{asset}_CURB_SEA", (0, -1.85, 2.98), (length, 0.34, 0.36), mats["concrete"], asset, 0.05)
    box(f"{asset}_ROAD", (0, 2.7, 2.84), (length, 8.7, 0.34), mats["asphalt"], asset, 0.035)
    box(f"{asset}_CURB_CITY", (0, 7.18, 2.98), (length, 0.34, 0.36), mats["concrete"], asset, 0.05)
    box(f"{asset}_CITY_SIDEWALK", (0, 9.15, 2.93), (length, 3.6, 0.28), mats["pavers"], asset, 0.04)
    for x in range(-62, 63, 12):
        box(f"{asset}_LANE_{x:+04d}", (float(x), 2.7, 3.02), (5.5, 0.13, 0.025), mats["lane"], asset, 0.0)
    for x in range(-60, 61, 10):
        box(f"{asset}_DRAIN_{x:+04d}", (float(x), 6.92, 3.16), (0.75, 0.31, 0.055), mats["metal"], asset, 0.018)
        for slot in range(5):
            box(f"{asset}_DRAIN_{x:+04d}_SLOT_{slot:02d}", (x - 0.24 + slot * 0.12, 6.91, 3.195), (0.035, 0.22, 0.02), mats["interior"], asset, 0.004)

    for index, x in enumerate(range(-55, 56, 22)):
        build_street_lamp(f"SM_M01_StreetLamp_{index:02d}", float(x), -3.7, mats)
        build_bench(f"SM_M01_Bench_{index:02d}", float(x + 5), -5.4, mats)
    for index, x in enumerate((-48, -27, -7, 16, 39, 61)):
        build_tree(f"SM_M01_CoastalTree_{index:02d}", (float(x), 9.4, 3.08), 0.92 + (index % 3) * 0.08, mats, 900 + index)

    empty("SOCKET_M01_CoastalDistrict_Origin", (-70.0, -46.0, -1.0), asset)
    collision = box("UCX_M01_CoastalDistrict_00", (0, 0, 1.25), (length, 22, 3.5), None, asset, 0.0, False)
    collision.display_type = "WIRE"


def setup_scene() -> None:
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    if hasattr(scene, "render"):
        scene.render.image_settings.color_mode = "RGBA"
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
        scene.eevee.taa_render_samples = 96
    except Exception:
        pass
    scene.world = bpy.data.worlds.new("M01_DAYLIGHT_WORLD")
    scene.world.use_nodes = True
    nodes = scene.world.node_tree.nodes
    links = scene.world.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputWorld")
    background = nodes.new("ShaderNodeBackground")
    background.inputs["Strength"].default_value = 0.42
    sky = nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_elevation = math.radians(28.0)
    sky.sun_rotation = math.radians(125.0)
    sky.air_density = 1.05
    sky.dust_density = 1.2
    links.new(sky.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass

    sun_data = bpy.data.lights.new("M01_SUN", "SUN")
    sun_data.energy = 3.1
    sun_data.angle = math.radians(5.0)
    sun = bpy.data.objects.new("M01_SUN", sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(32), math.radians(-18), math.radians(-42))

    area_data = bpy.data.lights.new("M01_SKY_FILL", "AREA")
    area_data.energy = 1450.0
    area_data.shape = "DISK"
    area_data.size = 55.0
    area = bpy.data.objects.new("M01_SKY_FILL", area_data)
    scene.collection.objects.link(area)
    area.location = (-22.0, -12.0, 46.0)
    area.rotation_euler = (0.0, 0.0, 0.0)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_camera(name: str, location: tuple[float, float, float], target: tuple[float, float, float], lens: float) -> bpy.types.Object:
    camera_data = bpy.data.cameras.new(name + "_DATA")
    camera_data.lens = lens
    camera_data.sensor_width = 36.0
    camera = bpy.data.objects.new(name, camera_data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = location
    look_at(camera, target)
    return camera


def render_cameras() -> list[Path]:
    cameras = [
        ("C01_COASTAL_ROUTE", (0.0, -72.0, 18.0), (0.0, 13.0, 12.0), 44.0),
        ("C02_STREET_CLOSE", (-15.0, -2.5, 9.0), (-16.0, 18.0, 10.5), 52.0),
        ("C03_DISTRICT_AERIAL", (3.0, -32.0, 72.0), (0.0, 4.0, 5.0), 46.0),
        ("C04_LIGHTHOUSE_SHORE", (67.0, -45.0, 12.0), (55.0, -1.0, 11.0), 52.0),
    ]
    outputs: list[Path] = []
    for name, location, target, lens in cameras:
        camera = add_camera(name, location, target, lens)
        bpy.context.scene.camera = camera
        path = RENDERS / f"{name}.png"
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        require(path.is_file(), f"Render not produced: {path}")
        outputs.append(path)
    return outputs


def export_asset(asset: str, path: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    objects = ASSETS.get(asset, [])
    require(objects, f"No objects registered for export asset {asset}")
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_extras=True,
        export_materials="EXPORT",
    )
    require(path.is_file(), f"GLB export not produced: {path}")


def validate_scene() -> dict[str, object]:
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == "MESH" and not obj.name.startswith("UCX_")]
    collision = [obj for obj in bpy.data.objects if obj.name.startswith("UCX_")]
    sockets = [obj for obj in bpy.data.objects if obj.name.startswith("SOCKET_")]
    triangles = 0
    nonmanifold_candidates = []
    for obj in mesh_objects:
        mesh = obj.data
        mesh.calc_loop_triangles()
        triangles += len(mesh.loop_triangles)
        if len(mesh.polygons) == 0:
            nonmanifold_candidates.append(obj.name)
    require(len(mesh_objects) >= 350, f"Expected production-detail object count >= 350; found {len(mesh_objects)}")
    require(len(collision) >= 5, f"Expected at least five collision objects; found {len(collision)}")
    require(len(sockets) >= 10, f"Expected at least ten sockets; found {len(sockets)}")
    require(not nonmanifold_candidates, f"Empty mesh objects: {nonmanifold_candidates}")
    return {
        "mesh_object_count": len(mesh_objects),
        "collision_object_count": len(collision),
        "socket_count": len(sockets),
        "material_count": len(MATERIALS),
        "triangle_count": triangles,
        "asset_family_count": len(ASSETS),
        "asset_families": {name: len(objects) for name, objects in sorted(ASSETS.items())},
    }


def main() -> int:
    require(not OUTPUT.exists(), f"Fresh output namespace already exists: {OUTPUT}")
    OUTPUT.mkdir(parents=True)
    EXPORTS.mkdir()
    RENDERS.mkdir()
    reset_scene()
    setup_scene()
    mats = build_materials()
    build_coastal_district(mats)
    build_building("SM_M01_Apartment_Production_A", -38.0, 18.5, 24.0, 12.5, 5, 6, mats["plaster_blue"], mats["concrete"], mats, 0)
    build_building("SM_M01_Midrise_Production_B", -3.0, 20.5, 29.0, 15.0, 7, 7, mats["plaster_warm"], mats["brick"], mats, 1)
    build_building("SM_M01_CornerResidence_Production_C", 34.0, 18.8, 26.0, 13.5, 6, 6, mats["brick"], mats["plaster_warm"], mats, 2)
    build_lighthouse(mats)

    scene_stats = validate_scene()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), compress=True)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH), compress=True)
    require(BLEND_PATH.is_file(), "Governed blend was not saved")

    export_assets = [
        "SM_M01_Apartment_Production_A",
        "SM_M01_Midrise_Production_B",
        "SM_M01_CornerResidence_Production_C",
        "SM_M01_CoastalDistrict_Production_A",
        "SM_M01_Lighthouse_Production_A",
    ]
    for asset in export_assets:
        export_asset(asset, EXPORTS / f"{asset}.glb")
    render_paths = render_cameras()

    receipt = {
        "schema": "skyguard.m01-visible-environment-production-reset01.checkpoint01-receipt.v1",
        "created_utc": utc_now(),
        "classification": "PASSED_AUTOMATIC_AWAITING_DIRECT_FULL_RESOLUTION_VISUAL_REVIEW",
        "source_policy": {
            "factory_empty_scene": True,
            "failed_stagea_geometry_read": False,
            "external_models_imported": False,
            "texture_source": "governed project-local Poly Haven library",
        },
        "coordinate_contract": {"units": "meters", "forward": "+X", "up": "+Z"},
        "scene_stats": scene_stats,
        "texture_authorities": sorted({item["path"]: item for item in TEXTURE_AUTHORITIES}.values(), key=lambda item: item["path"]),
        "outputs": {
            "blend": record_file(BLEND_PATH),
            "exports": [record_file(EXPORTS / f"{asset}.glb") for asset in export_assets],
            "renders": [record_file(path) for path in render_paths],
        },
        "acceptance_boundary": "DIRECT_FULL_RESOLUTION_VISUAL_REVIEW_REQUIRED_BEFORE_UNREAL_IMPORT",
    }
    receipt_path = OUTPUT / "production_checkpoint_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    inventory_files = sorted(path for path in OUTPUT.rglob("*") if path.is_file() and path.name != "artifact_inventory.json")
    inventory = {
        "schema": "skyguard.m01-visible-environment-production-reset01.checkpoint01-inventory.v1",
        "created_utc": utc_now(),
        "member_count": len(inventory_files),
        "members": [record_file(path) for path in inventory_files],
    }
    (OUTPUT / "artifact_inventory.json").write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"classification": receipt["classification"], "stats": scene_stats, "output": str(OUTPUT)}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FATAL: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
