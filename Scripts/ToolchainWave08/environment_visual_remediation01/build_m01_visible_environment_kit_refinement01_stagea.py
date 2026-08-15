from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import bpy
import numpy as np
from mathutils import Vector


GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA"
ASSET_ID = "m01-visible-environment-kit-refinement01-stagea"
DISTRICT_LENGTH_M = 100.0
DISTRICT_WIDTH_M = 80.0
SEED = 520811
FINAL_RESOLUTION = (2560, 1440)
CHECKPOINT_RESOLUTION = (1280, 720)
FINAL_CONDITIONS = ("daylight", "overcast", "night", "wet", "storm")
FINAL_VIEWS = ("close", "route", "aerial")


class BuildError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def parse_args() -> argparse.Namespace:
    source = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", default=ASSET_ID)
    parser.add_argument("--expected-source-sha256", required=True)
    return parser.parse_args(source)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BuildError(message)


def reset_scene() -> bpy.types.Scene:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_x, scene.render.resolution_y = FINAL_RESOLUTION
    scene.world = bpy.data.worlds.new("WORLD_M01_STAGEA")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.12, 0.20, 0.34, 1.0)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45
    scene.view_settings.look = "AgX - Medium High Contrast"
    return scene


def collection(name: str, parent: bpy.types.Collection | None = None) -> bpy.types.Collection:
    result = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(result)
    return result


def move_object(obj: bpy.types.Object, target: bpy.types.Collection) -> None:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    target.objects.link(obj)


def activate(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_transforms(obj: bpy.types.Object) -> None:
    activate(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def ensure_uvs(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    activate(obj)
    if not obj.data.uv_layers:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.025)
        bpy.ops.object.mode_set(mode="OBJECT")
    uv0 = obj.data.uv_layers[0]
    uv0.name = "UV0"
    while len(obj.data.uv_layers) > 1:
        obj.data.uv_layers.remove(obj.data.uv_layers[-1])
    uv1 = obj.data.uv_layers.new(name="UV1")
    for index, loop in enumerate(uv0.data):
        uv1.data[index].uv = loop.uv


def add_bevel(obj: bpy.types.Object, width: float, segments: int = 3) -> None:
    if width <= 0:
        return
    modifier = obj.modifiers.new("BEVEL_Production", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"
    modifier.angle_limit = math.radians(24.0)
    activate(obj)
    bpy.ops.object.modifier_apply(modifier=modifier.name)


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
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = f"NOISE_{name}"
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 4.0
    noise.inputs["Roughness"].default_value = 0.65
    bump = nodes.new("ShaderNodeBump")
    bump.name = f"BUMP_{name}"
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = 0.08
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], principled.inputs["Normal"])
    return material


def build_materials() -> dict[str, bpy.types.Material]:
    return {
        "wet_sand": make_material("M_STAGEA_WetSand", (0.16, 0.12, 0.075, 1), 0.32, noise_scale=9.0, bump_strength=0.08),
        "dry_sand": make_material("M_STAGEA_DrySand", (0.47, 0.34, 0.19, 1), 0.72, noise_scale=12.0, bump_strength=0.16),
        "dune_soil": make_material("M_STAGEA_DuneSoil", (0.24, 0.20, 0.095, 1), 0.86, noise_scale=7.0, bump_strength=0.22),
        "grass": make_material("M_STAGEA_DuneGrass", (0.14, 0.22, 0.045, 1), 0.82, noise_scale=4.0, bump_strength=0.08),
        "concrete": make_material("M_STAGEA_SaltConcrete", (0.34, 0.36, 0.35, 1), 0.67, noise_scale=6.0, bump_strength=0.15),
        "concrete_dark": make_material("M_STAGEA_DampConcrete", (0.16, 0.18, 0.18, 1), 0.49, noise_scale=8.0, bump_strength=0.12),
        "asphalt": make_material("M_STAGEA_Asphalt", (0.055, 0.060, 0.065, 1), 0.83, noise_scale=18.0, bump_strength=0.20),
        "paver": make_material("M_STAGEA_PromenadePaver", (0.30, 0.25, 0.21, 1), 0.74, noise_scale=16.0, bump_strength=0.12),
        "plaster_fde": make_material("M_STAGEA_PlasterFDE", (0.43, 0.31, 0.19, 1), 0.72, noise_scale=4.0, bump_strength=0.10),
        "plaster_blue": make_material("M_STAGEA_PlasterBlue", (0.16, 0.27, 0.34, 1), 0.68, noise_scale=4.0, bump_strength=0.09),
        "brick": make_material("M_STAGEA_Brick", (0.30, 0.095, 0.055, 1), 0.82, noise_scale=10.0, bump_strength=0.20),
        "metal": make_material("M_STAGEA_PaintedMetal", (0.06, 0.075, 0.085, 1), 0.34, metallic=0.62, noise_scale=8.0, bump_strength=0.06),
        "rust": make_material("M_STAGEA_Rust", (0.30, 0.075, 0.025, 1), 0.88, metallic=0.20, noise_scale=11.0, bump_strength=0.18),
        "glass": make_material("M_STAGEA_WindowGlass", (0.035, 0.10, 0.15, 1), 0.15, metallic=0.12, noise_scale=2.0, bump_strength=0.02),
        "roof": make_material("M_STAGEA_RoofMembrane", (0.075, 0.08, 0.085, 1), 0.70, noise_scale=9.0, bump_strength=0.10),
        "marking": make_material("M_STAGEA_RoadMarking", (0.67, 0.61, 0.39, 1), 0.55, noise_scale=12.0, bump_strength=0.03),
    }


def add_box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    target: bpy.types.Collection,
    bevel: float = 0.04,
    rotation_z: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=(0.0, 0.0, rotation_z))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    apply_transforms(obj)
    add_bevel(obj, bevel)
    obj.data.materials.append(material)
    ensure_uvs(obj)
    move_object(obj, target)
    return obj


def create_custom_mesh(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    materials: list[bpy.types.Material],
    target: bpy.types.Collection,
    material_indices: list[int] | None = None,
) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    for material in materials:
        mesh.materials.append(material)
    if material_indices:
        require(len(material_indices) == len(mesh.polygons), f"Material-index count mismatch for {name}")
        for polygon, material_index in zip(mesh.polygons, material_indices):
            polygon.material_index = material_index
    ensure_uvs(obj)
    return obj


def terrain_height(x: float, y: float) -> float:
    profile_y = (0.0, 6.0, 18.0, 30.0, 40.0, 44.0, 50.0, 54.0, 64.0, 70.0, 80.0)
    profile_z = (-0.25, -0.05, 0.22, 0.95, 1.65, 2.0, 2.15, 2.28, 2.38, 2.55, 2.72)
    index = min(max(next((i for i in range(len(profile_y) - 1) if profile_y[i] <= y <= profile_y[i + 1]), len(profile_y) - 2), 0), len(profile_y) - 2)
    span = profile_y[index + 1] - profile_y[index]
    alpha = (y - profile_y[index]) / span if span else 0.0
    base = profile_z[index] * (1.0 - alpha) + profile_z[index + 1] * alpha
    coastal_noise = math.sin(x * 0.19 + y * 0.07) * 0.055 + math.sin(x * 0.047 - y * 0.13) * 0.035
    return base + coastal_noise


def build_solid_terrain(materials: dict[str, bpy.types.Material], target: bpy.types.Collection) -> bpy.types.Object:
    x_values = [i * 2.5 for i in range(41)]
    y_values = [0.0, 6.0, 18.0, 30.0, 40.0, 44.0, 50.0, 54.0, 64.0, 70.0, 80.0]
    vertices: list[tuple[float, float, float]] = []
    for z_offset in (None, -2.0):
        for y in y_values:
            for x in x_values:
                z = terrain_height(x, y) if z_offset is None else z_offset
                vertices.append((x, y, z))
    nx, ny = len(x_values), len(y_values)
    layer_size = nx * ny
    faces: list[tuple[int, ...]] = []
    indices: list[int] = []
    terrain_materials = [materials["wet_sand"], materials["dry_sand"], materials["dune_soil"], materials["concrete"], materials["asphalt"]]
    for y_index in range(ny - 1):
        band_mid = (y_values[y_index] + y_values[y_index + 1]) * 0.5
        material_index = 0 if band_mid < 6 else 1 if band_mid < 18 else 2 if band_mid < 44 else 3 if band_mid < 54 else 4
        for x_index in range(nx - 1):
            a = y_index * nx + x_index
            b = a + 1
            c = a + nx + 1
            d = a + nx
            faces.append((a, b, c, d))
            indices.append(material_index)
            faces.append((layer_size + d, layer_size + c, layer_size + b, layer_size + a))
            indices.append(2)
    perimeter: list[int] = []
    perimeter.extend(range(0, nx))
    perimeter.extend(row * nx + nx - 1 for row in range(1, ny))
    perimeter.extend(range((ny - 1) * nx + nx - 2, (ny - 1) * nx - 1, -1))
    perimeter.extend(row * nx for row in range(ny - 2, 0, -1))
    for index, top_a in enumerate(perimeter):
        top_b = perimeter[(index + 1) % len(perimeter)]
        faces.append((top_a, layer_size + top_a, layer_size + top_b, top_b))
        indices.append(2)
    obj = create_custom_mesh("SM_M01_STAGEA_TerrainDistrict_100x80", vertices, faces, terrain_materials, target, indices)
    add_bevel(obj, 0.015, 2)
    ensure_uvs(obj)
    return obj


def add_socket(name: str, location: tuple[float, float, float], target: bpy.types.Collection) -> bpy.types.Object:
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = "PLAIN_AXES"
    obj.empty_display_size = 0.75
    obj.location = location
    target.objects.link(obj)
    return obj


def add_collision_box(name: str, location: tuple[float, float, float], dimensions: tuple[float, float, float], target: bpy.types.Collection) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    apply_transforms(obj)
    obj.display_type = "WIRE"
    obj.hide_render = True
    move_object(obj, target)
    return obj


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
        objects.append(add_box(f"SM_M01_STAGEA_Seawall_{segment:02d}", (x, 43.0, z_seawall), (9.86, 1.25, 1.5), materials["concrete"], visible, 0.09))
        objects.append(add_box(f"SM_M01_STAGEA_SeawallCoping_{segment:02d}", (x, 43.0, z_seawall + 0.82), (9.90, 1.48, 0.18), materials["concrete_dark"], visible, 0.05))
        objects.append(add_box(f"SM_M01_STAGEA_Promenade_{segment:02d}", (x, 48.0, terrain_height(x, 48.0) + 0.06), (9.92, 6.8, 0.12), materials["paver"], visible, 0.025))
        objects.append(add_box(f"SM_M01_STAGEA_Curb_{segment:02d}", (x, 53.2, terrain_height(x, 53.2) + 0.11), (9.88, 0.28, 0.22), materials["concrete"], visible, 0.035))
        if segment % 2 == 0:
            drain_x = x + 2.0
            objects.append(add_box(f"SM_M01_STAGEA_DrainGrate_{segment:02d}", (drain_x, 53.45, terrain_height(drain_x, 53.45) + 0.025), (1.15, 0.42, 0.05), materials["metal"], visible, 0.015))
    road_y = (54.0, 58.0, 62.0)
    road_z = [terrain_height(50.0, y) + offset for y, offset in zip(road_y, (0.06, 0.12, 0.06))]
    road_vertices = [(x, y, z) for x in (0.0, 100.0) for y, z in zip(road_y, road_z)]
    road_faces = [(0, 3, 4, 1), (1, 4, 5, 2)]
    road = create_custom_mesh("SM_M01_STAGEA_RoadCrowned_100m", road_vertices, road_faces, [materials["asphalt"]], visible, [0, 0])
    objects.append(road)
    for x in range(5, 100, 10):
        objects.append(add_box(f"SM_M01_STAGEA_RoadMark_{x:03d}", (float(x), 58.0, terrain_height(float(x), 58.0) + 0.15), (4.5, 0.14, 0.025), materials["marking"], visible, 0.008))
    for x in range(8, 100, 14):
        base_z = terrain_height(float(x), 48.5)
        objects.append(add_box(f"SM_M01_STAGEA_LampPost_{x:03d}", (float(x), 49.0, base_z + 2.8), (0.10, 0.10, 5.6), materials["metal"], visible, 0.025))
        objects.append(add_box(f"SM_M01_STAGEA_LampHead_{x:03d}", (float(x), 48.75, base_z + 5.58), (0.65, 0.22, 0.16), materials["metal"], visible, 0.04))
    rng = random.Random(SEED)
    for index in range(72):
        x = rng.uniform(1.0, 99.0)
        y = rng.uniform(20.0, 39.0)
        base_z = terrain_height(x, y)
        height = rng.uniform(0.35, 0.85)
        blade = add_box(f"SM_M01_STAGEA_DuneGrass_{index:03d}", (x, y, base_z + height * 0.5), (0.025, 0.16, height), materials["grass"], visible, 0.005, rng.uniform(-0.4, 0.4))
        objects.append(blade)
    add_collision_box("UCX_SM_M01_STAGEA_TerrainDistrict_100x80_00", (50.0, 40.0, 0.0), (100.0, 80.0, 4.0), collision)
    add_collision_box("UCX_SM_M01_STAGEA_Seawall_00", (50.0, 43.0, 2.4), (100.0, 1.4, 2.0), collision)
    add_collision_box("UCX_SM_M01_STAGEA_RoadCrowned_100m_00", (50.0, 58.0, 2.4), (100.0, 8.0, 0.4), collision)
    add_socket("SOCKET_District_W", (0.0, 0.0, terrain_height(0.0, 0.0)), sockets)
    add_socket("SOCKET_District_E", (100.0, 0.0, terrain_height(100.0, 0.0)), sockets)
    add_socket("SOCKET_District_S", (50.0, 0.0, terrain_height(50.0, 0.0)), sockets)
    add_socket("SOCKET_District_N", (50.0, 80.0, terrain_height(50.0, 80.0)), sockets)
    return objects


def add_window(
    prefix: str,
    x: float,
    y: float,
    z: float,
    front: bool,
    materials: dict[str, bpy.types.Material],
    target: bpy.types.Collection,
) -> list[bpy.types.Object]:
    depth = 0.14
    y_offset = -depth if front else depth
    result = [
        add_box(prefix + "_Glass", (x, y + y_offset * 0.35, z), (1.55, depth, 1.62), materials["glass"], target, 0.025),
        add_box(prefix + "_FrameTop", (x, y + y_offset, z + 0.86), (1.82, 0.12, 0.10), materials["metal"], target, 0.02),
        add_box(prefix + "_FrameBottom", (x, y + y_offset, z - 0.86), (1.82, 0.12, 0.10), materials["metal"], target, 0.02),
        add_box(prefix + "_FrameLeft", (x - 0.86, y + y_offset, z), (0.10, 0.12, 1.62), materials["metal"], target, 0.02),
        add_box(prefix + "_FrameRight", (x + 0.86, y + y_offset, z), (0.10, 0.12, 1.62), materials["metal"], target, 0.02),
        add_box(prefix + "_Mullion", (x, y + y_offset * 1.1, z), (0.07, 0.12, 1.62), materials["metal"], target, 0.015),
        add_box(prefix + "_Sill", (x, y + y_offset * 1.5, z - 0.95), (2.05, 0.32, 0.13), materials["concrete_dark"], target, 0.025),
    ]
    return result


def add_balcony(
    prefix: str,
    x: float,
    y: float,
    z: float,
    materials: dict[str, bpy.types.Material],
    target: bpy.types.Collection,
) -> list[bpy.types.Object]:
    result = [add_box(prefix + "_Slab", (x, y - 0.85, z - 0.95), (2.75, 1.55, 0.18), materials["concrete"], target, 0.04)]
    result.append(add_box(prefix + "_RailTop", (x, y - 1.57, z - 0.10), (2.65, 0.055, 0.07), materials["metal"], target, 0.018))
    for offset in (-1.25, -0.62, 0.0, 0.62, 1.25):
        result.append(add_box(prefix + f"_Rail_{offset:+.2f}", (x + offset, y - 1.57, z - 0.53), (0.045, 0.045, 0.86), materials["metal"], target, 0.012))
    return result


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
    front_y, back_y = 66.6, 78.55
    wall_material = materials["plaster_fde"] if facade_style == "A" else materials["plaster_blue"]
    objects = [
        add_box(name + "_Core", (center_x, 72.5, ground_z + height * 0.5), (18.0, 11.2, height), wall_material, target, 0.18),
        add_box(name + "_Foundation", (center_x, 72.5, ground_z - 0.35), (18.4, 11.6, 0.7), materials["concrete_dark"], target, 0.08),
    ]
    for floor in range(floors + 1):
        z = ground_z + (ground_floor if floor else 0.0) + max(0, floor - 1) * floor_height
        objects.append(add_box(f"{name}_Slab_{floor:02d}", (center_x, 72.5, z + 0.06), (18.1, 11.35, 0.12), materials["concrete"], target, 0.025))
    bay_offsets = (-7.5, -4.5, -1.5, 1.5, 4.5, 7.5)
    for floor in range(floors):
        z = ground_z + (1.8 if floor == 0 else ground_floor + (floor - 1) * floor_height + 1.5)
        for bay_index, offset in enumerate(bay_offsets):
            if floor == 0 and bay_index in (2, 3):
                continue
            objects.extend(add_window(f"{name}_F{floor:02d}_B{bay_index:02d}_Front", center_x + offset, front_y, z, True, materials, target))
            if bay_index % 2 == 0 or facade_style == "B":
                objects.extend(add_window(f"{name}_F{floor:02d}_B{bay_index:02d}_Rear", center_x + offset, back_y, z, False, materials, target))
            if floor > 0 and ((bay_index + floor + (0 if facade_style == "A" else 1)) % 3 == 0):
                objects.extend(add_balcony(f"{name}_F{floor:02d}_B{bay_index:02d}_Balcony", center_x + offset, front_y, z, materials, target))
    entrance_material = materials["brick"] if facade_style == "A" else materials["concrete_dark"]
    objects.append(add_box(name + "_EntrancePortal", (center_x, front_y - 0.14, ground_z + 1.55), (4.2, 0.38, 3.1), entrance_material, target, 0.08))
    objects.append(add_box(name + "_EntranceGlass", (center_x, front_y - 0.37, ground_z + 1.45), (2.5, 0.14, 2.7), materials["glass"], target, 0.025))
    for x_offset in (-8.7, 8.7):
        objects.append(add_box(name + f"_CornerPilaster_{x_offset:+.1f}", (center_x + x_offset, front_y - 0.10, ground_z + height * 0.5), (0.45, 0.45, height), materials["concrete"], target, 0.06))
    roof_z = ground_z + height
    objects.append(add_box(name + "_Roof", (center_x, 72.5, roof_z + 0.18), (18.0, 11.2, 0.36), materials["roof"], target, 0.05))
    for x_offset in (-8.75, 8.75):
        objects.append(add_box(name + f"_ParapetLong_{x_offset:+.2f}", (center_x + x_offset, 72.5, roof_z + 0.72), (0.24, 11.2, 1.1), materials["concrete"], target, 0.04))
    for y in (67.02, 77.98):
        objects.append(add_box(name + f"_ParapetShort_{y:.2f}", (center_x, y, roof_z + 0.72), (17.5, 0.24, 1.1), materials["concrete"], target, 0.04))
    objects.append(add_box(name + "_RoofService", (center_x + 3.6, 73.0, roof_z + 1.2), (4.8, 3.3, 1.7), materials["metal"], target, 0.10))
    objects.append(add_box(name + "_RoofVent", (center_x - 4.4, 72.0, roof_z + 1.45), (1.4, 1.4, 2.2), materials["rust"], target, 0.08))
    add_collision_box("UCX_" + name + "_00", (center_x, 72.5, ground_z + height * 0.5), (18.0, 11.2, height), collision)
    add_socket("SOCKET_" + name + "_Origin", (center_x - 9.0, 66.9, ground_z), sockets)
    return objects


def build_facade_export_modules(materials: dict[str, bpy.types.Material], target: bpy.types.Collection) -> list[bpy.types.Object]:
    result: list[bpy.types.Object] = []
    base_x = 120.0
    for composition, wall_material in enumerate((materials["plaster_fde"], materials["plaster_blue"], materials["brick"])):
        x = base_x + composition * 5.0
        result.append(add_box(f"SM_M01_STAGEA_FacadeComposition_{composition+1:02d}_Wall", (x, 0.0, 1.5), (3.0, 0.28, 3.0), wall_material, target, 0.06))
        result.extend(add_window(f"SM_M01_STAGEA_FacadeComposition_{composition+1:02d}_Window", x, -0.18, 1.55, True, materials, target))
        if composition == 1:
            result.extend(add_balcony("SM_M01_STAGEA_FacadeComposition_02_Balcony", x, -0.18, 1.55, materials, target))
    for obj in target.all_objects:
        obj.hide_render = True
    return result


def create_texture_atlas(output: Path) -> list[Path]:
    texture_dir = output / "textures"
    texture_dir.mkdir(parents=True, exist_ok=True)
    size = 2048
    rng = np.random.default_rng(SEED)
    noise = rng.normal(0.0, 0.025, (size, size, 1)).astype(np.float32)
    palette = np.array([
        [0.16, 0.12, 0.075], [0.47, 0.34, 0.19], [0.24, 0.20, 0.095], [0.34, 0.36, 0.35],
        [0.055, 0.060, 0.065], [0.43, 0.31, 0.19], [0.16, 0.27, 0.34], [0.30, 0.095, 0.055],
    ], dtype=np.float32)
    bands = np.minimum((np.arange(size) * len(palette) // size), len(palette) - 1)
    base_rgb = np.clip(palette[bands][:, None, :] + noise, 0.0, 1.0)
    base_rgb = np.repeat(base_rgb, size, axis=1) if base_rgb.shape[1] == 1 else base_rgb
    rough_values = np.array([0.32, 0.72, 0.86, 0.67, 0.83, 0.72, 0.68, 0.82], dtype=np.float32)
    rough = np.clip(rough_values[bands][:, None, None] + noise * 0.6, 0.0, 1.0)
    rough = np.repeat(rough, size, axis=1)
    metallic = np.zeros((size, size, 1), dtype=np.float32)
    ao = np.clip(0.94 + noise * 0.5, 0.75, 1.0)
    normal = np.zeros((size, size, 3), dtype=np.float32)
    normal[:, :, 0] = 0.5 + noise[:, :, 0] * 0.4
    normal[:, :, 1] = 0.5 + np.roll(noise[:, :, 0], 3, axis=0) * 0.4
    normal[:, :, 2] = 1.0

    maps = {
        "T_M01_STAGEA_Atlas_BaseColor.png": base_rgb,
        "T_M01_STAGEA_Atlas_Normal.png": normal,
        "T_M01_STAGEA_Atlas_Roughness.png": np.repeat(rough, 3, axis=2),
        "T_M01_STAGEA_Atlas_Metallic.png": np.repeat(metallic, 3, axis=2),
        "T_M01_STAGEA_Atlas_AO.png": np.repeat(ao, 3, axis=2),
    }
    paths: list[Path] = []
    for filename, rgb in maps.items():
        rgba = np.concatenate((rgb, np.ones((size, size, 1), dtype=np.float32)), axis=2)
        image = bpy.data.images.new(filename[:-4], width=size, height=size, alpha=True, float_buffer=False)
        image.pixels.foreach_set(rgba.reshape(-1))
        image.filepath_raw = str(texture_dir / filename)
        image.file_format = "PNG"
        image.save()
        bpy.data.images.remove(image)
        paths.append(texture_dir / filename)
    return paths


def add_review_rig(scene: bpy.types.Scene) -> dict[str, bpy.types.Object]:
    review = collection("REVIEW_ONLY")
    camera_data = bpy.data.cameras.new("CAM_STAGEA_Review")
    camera = bpy.data.objects.new("CAM_STAGEA_Review", camera_data)
    review.objects.link(camera)
    camera.data.lens = 50.0
    scene.camera = camera
    bpy.ops.object.light_add(type="SUN", location=(50.0, 35.0, 70.0))
    sun = bpy.context.object
    sun.name = "LIGHT_STAGEA_Sun"
    sun.data.energy = 3.2
    sun.data.angle = math.radians(0.535)
    sun.rotation_euler = (math.radians(35.0), math.radians(-18.0), math.radians(-35.0))
    move_object(sun, review)
    bpy.ops.object.light_add(type="AREA", location=(40.0, 32.0, 38.0))
    fill = bpy.context.object
    fill.name = "LIGHT_STAGEA_Fill"
    fill.data.energy = 1100.0
    fill.data.shape = "DISK"
    fill.data.size = 45.0
    fill.rotation_euler = (math.radians(22.0), 0.0, math.radians(20.0))
    move_object(fill, review)
    return {"camera": camera, "sun": sun, "fill": fill}


def point_camera(camera: bpy.types.Object, location: tuple[float, float, float], target: tuple[float, float, float], lens: float) -> None:
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = lens


def configure_condition(scene: bpy.types.Scene, rig: dict[str, bpy.types.Object], condition: str, materials: dict[str, bpy.types.Material]) -> None:
    background = scene.world.node_tree.nodes["Background"]
    values = {
        "daylight": ((0.16, 0.28, 0.50, 1.0), 0.48, 3.2, 1100.0),
        "overcast": ((0.20, 0.23, 0.28, 1.0), 0.55, 1.1, 1700.0),
        "night": ((0.008, 0.015, 0.038, 1.0), 0.075, 0.12, 650.0),
        "wet": ((0.13, 0.18, 0.23, 1.0), 0.42, 1.8, 1400.0),
        "storm": ((0.055, 0.075, 0.095, 1.0), 0.30, 0.65, 1250.0),
    }
    color, strength, sun_energy, fill_energy = values[condition]
    background.inputs["Color"].default_value = color
    background.inputs["Strength"].default_value = strength
    rig["sun"].data.energy = sun_energy
    rig["fill"].data.energy = fill_energy
    wet = condition in ("wet", "storm")
    materials["wet_sand"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.18 if wet else 0.32
    materials["asphalt"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.40 if wet else 0.83
    materials["concrete"].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.50 if wet else 0.67


def render_and_measure(scene: bpy.types.Scene, path: Path) -> dict[str, float]:
    path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    render = bpy.data.images.get("Render Result")
    require(render is not None, "Render Result is unavailable")
    width, height = render.size
    pixels = np.empty(width * height * 4, dtype=np.float32)
    render.pixels.foreach_get(pixels)
    rgb = pixels.reshape((-1, 4))[:, :3]
    luma = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    return {
        "width": int(width),
        "height": int(height),
        "mean_luma_linear": float(np.mean(luma)),
        "black_fraction_linear_0_01": float(np.mean(luma < 0.01)),
        "max_luma_linear": float(np.max(luma)),
    }


def render_checkpoints(scene: bpy.types.Scene, rig: dict[str, bpy.types.Object], output: Path, materials: dict[str, bpy.types.Material]) -> list[dict[str, Any]]:
    scene.render.resolution_x, scene.render.resolution_y = CHECKPOINT_RESOLUTION
    specs = [
        ("checkpoint_01_cross_section", (15.0, -38.0, 14.0), (35.0, 43.0, 2.0), 50.0),
        ("checkpoint_02_facade_street", (34.0, 46.0, 10.0), (28.0, 72.0, 8.0), 58.0),
        ("checkpoint_03_pbr_composition", (50.0, -62.0, 42.0), (50.0, 53.0, 5.5), 52.0),
    ]
    results: list[dict[str, Any]] = []
    configure_condition(scene, rig, "daylight", materials)
    correction_used = False
    for name, location, target, lens in specs:
        corrected_this_checkpoint = False
        point_camera(rig["camera"], location, target, lens)
        path = output / "renders" / "checkpoints" / f"{name}.png"
        metrics = render_and_measure(scene, path)
        require((metrics["width"], metrics["height"]) == CHECKPOINT_RESOLUTION, f"Checkpoint resolution failed: {name}")
        passed = metrics["mean_luma_linear"] >= 0.03 and metrics["black_fraction_linear_0_01"] <= 0.35
        if not passed and not correction_used:
            rig["fill"].data.energy *= 1.7
            metrics = render_and_measure(scene, path)
            require((metrics["width"], metrics["height"]) == CHECKPOINT_RESOLUTION, f"Corrected checkpoint resolution failed: {name}")
            correction_used = True
            corrected_this_checkpoint = True
            passed = metrics["mean_luma_linear"] >= 0.03 and metrics["black_fraction_linear_0_01"] <= 0.35
        require(passed, f"Checkpoint luminance failed: {name}")
        results.append({"id": name, "path": str(path), "metrics": metrics, "passed": True, "bounded_correction_used": corrected_this_checkpoint})
    return results


def render_final_views(scene: bpy.types.Scene, rig: dict[str, bpy.types.Object], output: Path, materials: dict[str, bpy.types.Material]) -> list[dict[str, Any]]:
    scene.render.resolution_x, scene.render.resolution_y = FINAL_RESOLUTION
    view_specs = {
        "close": ((31.0, 46.0, 9.0), (24.0, 72.0, 7.0), 58.0),
        "route": ((18.0, -46.0, 18.0), (48.0, 58.0, 4.0), 50.0),
        "aerial": ((50.0, -75.0, 68.0), (50.0, 48.0, 5.5), 48.0),
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


def recursive_objects(groups: Iterable[bpy.types.Collection]) -> list[bpy.types.Object]:
    values: list[bpy.types.Object] = []
    seen: set[int] = set()
    for group in groups:
        for obj in group.all_objects:
            if obj.as_pointer() not in seen:
                values.append(obj)
                seen.add(obj.as_pointer())
    return values


def export_glb(path: Path, groups: Iterable[bpy.types.Collection]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    selected = recursive_objects(groups)
    require(any(obj.type == "MESH" for obj in selected), f"No mesh for export {path.name}")
    for obj in selected:
        obj.hide_set(False)
        obj.select_set(True)
    bpy.context.view_layer.objects.active = next(obj for obj in selected if obj.type == "MESH")
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
    )
    require(path.is_file() and path.stat().st_size > 0, f"GLB export failed: {path}")


def collection_stats(groups: Iterable[bpy.types.Collection]) -> dict[str, Any]:
    objects = recursive_objects(groups)
    meshes = [obj for obj in objects if obj.type == "MESH" and not obj.name.startswith("UCX_")]
    vertices = 0
    triangles = 0
    uv_failures: list[str] = []
    unapplied: list[str] = []
    for obj in meshes:
        obj.data.calc_loop_triangles()
        vertices += len(obj.data.vertices)
        triangles += len(obj.data.loop_triangles)
        if [layer.name for layer in obj.data.uv_layers] != ["UV0", "UV1"]:
            uv_failures.append(obj.name)
        if any(abs(value - 1.0) > 1e-4 for value in obj.scale):
            unapplied.append(obj.name)
    require(not uv_failures, f"UV contract failed: {uv_failures[:8]}")
    require(not unapplied, f"Unapplied mesh scales: {unapplied[:8]}")
    return {"objects": len(objects), "meshes": len(meshes), "vertices": vertices, "triangles": triangles, "uv_failures": uv_failures, "unapplied_scales": unapplied}


def bounds_for(groups: Iterable[bpy.types.Collection]) -> dict[str, list[float]]:
    corners: list[Vector] = []
    for obj in recursive_objects(groups):
        if obj.type == "MESH" and not obj.name.startswith("UCX_"):
            corners.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    require(corners, "No visible bounds")
    minimum = [min(point[index] for point in corners) for index in range(3)]
    maximum = [max(point[index] for point in corners) for index in range(3)]
    dimensions = [maximum[index] - minimum[index] for index in range(3)]
    return {"min_m": minimum, "max_m": maximum, "dimensions_m": dimensions}


def inventory(output: Path, exclude: set[Path] | None = None) -> list[dict[str, Any]]:
    excluded = {path.resolve() for path in (exclude or set())}
    records = []
    for path in sorted(item for item in output.rglob("*") if item.is_file()):
        if path.resolve() in excluded:
            continue
        records.append({"relative_path": path.relative_to(output).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)})
    return records


def main() -> int:
    args = parse_args()
    require(args.asset_id == ASSET_ID, f"Unexpected asset id: {args.asset_id}")
    source_path = Path(__file__).resolve()
    require(sha256(source_path) == args.expected_source_sha256.lower(), "Attempt source hash does not match the frozen authority")
    output = Path(args.output).resolve()
    require(not output.exists(), f"Output namespace already exists: {output}")
    output.mkdir(parents=True)

    scene = reset_scene()
    root = collection("M01_VISIBLE_ENVIRONMENT_KIT_STAGEA")
    shore = collection("ASSET_ShoreStreet", root)
    building5 = collection("ASSET_Midrise5F", root)
    building7 = collection("ASSET_Midrise7F", root)
    facade = collection("ASSET_FacadeModules", root)
    collision_shore = collection("COLLISION_ShoreStreet", root)
    collision_5 = collection("COLLISION_Midrise5F", root)
    collision_7 = collection("COLLISION_Midrise7F", root)
    sockets_shore = collection("SOCKETS_ShoreStreet", root)
    sockets_5 = collection("SOCKETS_Midrise5F", root)
    sockets_7 = collection("SOCKETS_Midrise7F", root)
    materials = build_materials()
    build_shore_and_street(materials, shore, collision_shore, sockets_shore)
    build_midrise("SM_M01_STAGEA_Midrise5F_A", 22.0, 5, "A", materials, building5, collision_5, sockets_5)
    build_midrise("SM_M01_STAGEA_Midrise7F_B", 66.0, 7, "B", materials, building7, collision_7, sockets_7)
    build_facade_export_modules(materials, facade)
    textures = create_texture_atlas(output)
    rig = add_review_rig(scene)
    checkpoints = render_checkpoints(scene, rig, output, materials)
    final_renders = render_final_views(scene, rig, output, materials)

    blend_path = output / "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    export_root = output / "exports"
    exports = [
        export_root / "SM_M01_STAGEA_ShoreStreetDistrict.glb",
        export_root / "SM_M01_STAGEA_Midrise5F_A.glb",
        export_root / "SM_M01_STAGEA_Midrise7F_B.glb",
        export_root / "SM_M01_STAGEA_FacadeCompositions.glb",
    ]
    export_glb(exports[0], (shore, collision_shore, sockets_shore))
    export_glb(exports[1], (building5, collision_5, sockets_5))
    export_glb(exports[2], (building7, collision_7, sockets_7))
    export_glb(exports[3], (facade,))

    visible_groups = (shore, building5, building7)
    stats = collection_stats((shore, building5, building7, facade))
    district_bounds = bounds_for(visible_groups)
    dimension_receipt = {
        "schema": "skyguard.m01-visible-environment-kit.stagea.dimension-receipt.v1",
        "gate": GATE,
        "district_authority_m": [DISTRICT_LENGTH_M, DISTRICT_WIDTH_M],
        "observed_visible_bounds": district_bounds,
        "coast_axis": "+X",
        "inland_axis": "+Y",
        "up_axis": "+Z",
        "district_x_min_abs_tolerance_m": 0.01,
        "district_x_max_abs_tolerance_m": 0.01,
        "district_y_min_abs_tolerance_m": 0.01,
        "district_y_max_abs_tolerance_m": 0.01,
        "passed": (
            abs(district_bounds["min_m"][0]) <= 0.01
            and abs(district_bounds["max_m"][0] - 100.0) <= 0.01
            and abs(district_bounds["min_m"][1]) <= 0.01
            and abs(district_bounds["max_m"][1] - 80.0) <= 0.01
        ),
    }
    require(dimension_receipt["passed"], f"District dimension contract failed: {district_bounds}")
    atomic_json(output / "dimension_receipt.json", dimension_receipt)
    atomic_json(output / "topology_uv_receipt.json", {"schema":"skyguard.m01-visible-environment-kit.stagea.topology-uv.v1","gate":GATE,"statistics":stats,"passed":True})
    atomic_json(output / "material_texture_receipt.json", {
        "schema":"skyguard.m01-visible-environment-kit.stagea.material-texture.v1",
        "gate":GATE,
        "materials":sorted(materials),
        "texture_maps":[{"path":path.relative_to(output).as_posix(),"bytes":path.stat().st_size,"sha256":sha256(path)} for path in textures],
        "atlas_resolution":[2048,2048],
        "maps":["BaseColor","Normal","Roughness","Metallic","AO"],
        "passed":len(textures)==5 and all(path.is_file() and path.stat().st_size > 0 for path in textures),
    })
    atomic_json(output / "checkpoint_receipt.json", {"schema":"skyguard.m01-visible-environment-kit.stagea.checkpoints.v1","gate":GATE,"checkpoints":checkpoints,"count":len(checkpoints),"passed":len(checkpoints)==3})
    atomic_json(output / "render_receipt.json", {"schema":"skyguard.m01-visible-environment-kit.stagea.renders.v1","gate":GATE,"resolution":list(FINAL_RESOLUTION),"renders":final_renders,"count":len(final_renders),"passed":len(final_renders)==15})
    required_sockets = ["SOCKET_District_W","SOCKET_District_E","SOCKET_District_S","SOCKET_District_N","SOCKET_SM_M01_STAGEA_Midrise5F_A_Origin","SOCKET_SM_M01_STAGEA_Midrise7F_B_Origin"]
    missing_sockets = [name for name in required_sockets if bpy.data.objects.get(name) is None]
    collision_objects = sorted(obj.name for obj in bpy.data.objects if obj.name.startswith("UCX_"))
    require(not missing_sockets, f"Required sockets are missing: {missing_sockets}")
    require(len(collision_objects) >= 5, "Insufficient governed collision objects")
    require(all(path.is_file() and path.stat().st_size > 0 for path in exports), "One or more GLB exports are missing or empty")
    atomic_json(output / "export_receipt.json", {
        "schema":"skyguard.m01-visible-environment-kit.stagea.exports.v1",
        "gate":GATE,
        "exports":[{"path":path.relative_to(output).as_posix(),"bytes":path.stat().st_size,"sha256":sha256(path)} for path in exports],
        "required_sockets":required_sockets,
        "missing_sockets":missing_sockets,
        "collision_prefix":"UCX_",
        "collision_objects":collision_objects,
        "passed":len(exports)==4 and not missing_sockets and len(collision_objects) >= 5,
    })
    source_receipt = {"schema":"skyguard.m01-visible-environment-kit.stagea.source-parity.v1","source":str(source_path),"bytes":source_path.stat().st_size,"sha256":sha256(source_path),"expected_sha256":args.expected_source_sha256.lower(),"passed":True}
    atomic_json(output / "source_parity_receipt.json", source_receipt)
    artifact_path = output / "artifact_inventory.json"
    terminal_path = output / "terminal_receipt.json"
    atomic_json(artifact_path, {"schema":"skyguard.m01-visible-environment-kit.stagea.inventory.v1","gate":GATE,"files":inventory(output, {artifact_path, terminal_path})})
    atomic_json(terminal_path, {
        "schema":"skyguard.m01-visible-environment-kit.stagea.terminal.v1",
        "gate":GATE,
        "asset_id":ASSET_ID,
        "status":"BLENDER_COMPLETED_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW",
        "created_utc":utc_now(),
        "blend_count":1,
        "glb_count":4,
        "checkpoint_count":3,
        "final_render_count":15,
        "texture_count":5,
        "automatic_validation_passed":True,
        "human_visual_acceptance":"NOT_PERFORMED",
    })
    print(json.dumps({"gate":GATE,"status":"BLENDER_COMPLETED_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW","output":str(output)}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"gate":GATE,"status":"FAILED_WITH_EVIDENCE","error":f"{type(exc).__name__}: {exc}"}), file=sys.stderr)
        raise
