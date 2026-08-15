#!/usr/bin/env python3
"""Build Mission 1 StageB visible landmarks and environment variation assets."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import random
import sys
from pathlib import Path
from typing import Any, Iterable

import bpy
import numpy as np
from mathutils import Vector


GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEB"
ASSET_ID = "m01-visible-environment-kit-refinement01-stageb"
SEED = 520812
CHECKPOINT_RESOLUTION = (1280, 720)
FINAL_RESOLUTION = (2560, 1440)
FINAL_CONDITIONS = ("daylight", "overcast", "night", "wet", "storm")
FINAL_VIEWS = ("landmarks", "street", "aerial")
STAGEA_HELPER = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visual_remediation01\build_m01_visible_environment_kit_refinement01_stagea.py"
)
STAGEA_HELPER_SHA256 = "773e67931108a2f199f763a4d3ce94348ba9ed9a403c049b3b8b4409bb06fd12"


class BuildError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--expected-stagea-helper-sha256", required=True)
    return parser.parse_args(values)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BuildError(message)


def load_stagea_helpers():
    require(STAGEA_HELPER.is_file(), f"Missing StageA helper: {STAGEA_HELPER}")
    spec = importlib.util.spec_from_file_location("skyguard_stagea_helpers", STAGEA_HELPER)
    require(spec is not None and spec.loader is not None, "Unable to load StageA helper specification")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


A = load_stagea_helpers()


def add_cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
    vertices: int = 48,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel: float = 0.04,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    A.apply_transforms(obj)
    A.add_bevel(obj, bevel, 3)
    obj.data.materials.append(material)
    A.ensure_uvs(obj)
    A.move_object(obj, target)
    return obj


def add_cone(
    name: str,
    location: tuple[float, float, float],
    radius1: float,
    radius2: float,
    depth: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
    vertices: int = 64,
    bevel: float = 0.04,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    A.apply_transforms(obj)
    A.add_bevel(obj, bevel, 3)
    obj.data.materials.append(material)
    A.ensure_uvs(obj)
    A.move_object(obj, target)
    return obj


def add_icosphere(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    target: bpy.types.Collection,
    subdivisions: int = 2,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    A.apply_transforms(obj)
    obj.data.materials.append(material)
    A.ensure_uvs(obj)
    A.move_object(obj, target)
    return obj


def add_torus(
    name: str,
    location: tuple[float, float, float],
    major_radius: float,
    minor_radius: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=64,
        minor_segments=12,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    A.apply_transforms(obj)
    obj.data.materials.append(material)
    A.ensure_uvs(obj)
    A.move_object(obj, target)
    return obj


def add_collision_cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = name
    A.apply_transforms(obj)
    obj.display_type = "WIRE"
    obj.hide_render = True
    A.ensure_uvs(obj)
    A.move_object(obj, target)
    return obj


def add_beam_between(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    thickness: float,
    material: bpy.types.Material,
    target: bpy.types.Collection,
) -> bpy.types.Object:
    start_vector = Vector(start)
    end_vector = Vector(end)
    direction = end_vector - start_vector
    require(direction.length > 0.001, f"Beam endpoints overlap: {name}")
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(start_vector + end_vector) * 0.5)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (thickness, thickness, direction.length)
    A.apply_transforms(obj)
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    A.add_bevel(obj, min(0.025, thickness * 0.2), 2)
    obj.data.materials.append(material)
    A.ensure_uvs(obj)
    A.move_object(obj, target)
    return obj


def emission_material(name: str, color: tuple[float, float, float, float], strength: float) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = color
    emission.inputs["Strength"].default_value = strength
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return material


def build_materials() -> dict[str, bpy.types.Material]:
    materials = A.build_materials()
    materials.update(
        {
            "white_paint": A.make_material("M_STAGEB_SaltWhitePaint", (0.58, 0.58, 0.54, 1), 0.55, noise_scale=5.0, bump_strength=0.12),
            "red_paint": A.make_material("M_STAGEB_FadedRedPaint", (0.48, 0.035, 0.022, 1), 0.48, metallic=0.08, noise_scale=7.0, bump_strength=0.10),
            "olive": A.make_material("M_STAGEB_RadarOlive", (0.14, 0.17, 0.095, 1), 0.58, metallic=0.18, noise_scale=6.0, bump_strength=0.08),
            "wood": A.make_material("M_STAGEB_WeatheredWood", (0.27, 0.14, 0.065, 1), 0.78, noise_scale=14.0, bump_strength=0.20),
            "foliage_tamarisk": A.make_material("M_STAGEB_FoliageTamarisk", (0.12, 0.24, 0.10, 1), 0.82, noise_scale=5.0, bump_strength=0.05),
            "foliage_pine": A.make_material("M_STAGEB_FoliagePine", (0.045, 0.15, 0.075, 1), 0.85, noise_scale=5.0, bump_strength=0.05),
            "foliage_poplar": A.make_material("M_STAGEB_FoliagePoplar", (0.19, 0.31, 0.085, 1), 0.80, noise_scale=5.0, bump_strength=0.05),
            "foliage_shrub": A.make_material("M_STAGEB_FoliageShrub", (0.22, 0.27, 0.075, 1), 0.86, noise_scale=5.0, bump_strength=0.05),
            "soot": A.make_material("M_STAGEB_Soot", (0.018, 0.016, 0.014, 1), 0.92, noise_scale=18.0, bump_strength=0.16),
            "warning": A.make_material("M_STAGEB_WarningYellow", (0.64, 0.37, 0.025, 1), 0.47, metallic=0.08, noise_scale=9.0, bump_strength=0.08),
            "beacon": emission_material("M_STAGEB_BeaconEmission", (1.0, 0.08, 0.02, 1), 8.0),
        }
    )
    return materials


def build_lighthouse(
    materials: dict[str, bpy.types.Material],
    visible: bpy.types.Collection,
    collision: bpy.types.Collection,
    sockets: bpy.types.Collection,
) -> dict[str, Any]:
    objects: list[bpy.types.Object] = []
    objects.append(add_cylinder("SM_M01_STAGEB_Lighthouse_Platform", (0, 0, 0.45), 4.8, 0.9, materials["concrete_dark"], visible, 64, bevel=0.10))
    objects.append(add_cone("SM_M01_STAGEB_Lighthouse_Tower", (0, 0, 11.9), 4.0, 2.75, 22.0, materials["white_paint"], visible, 96, 0.08))
    for z in (6.0, 13.0, 20.0):
        radius = 3.72 - z * 0.047
        objects.append(add_cylinder(f"SM_M01_STAGEB_Lighthouse_RedBand_{int(z):02d}", (0, 0, z), radius, 1.25, materials["red_paint"], visible, 96, bevel=0.025))
    objects.append(A.add_box("SM_M01_STAGEB_Lighthouse_Door", (0, -3.83, 2.25), (1.5, 0.24, 3.4), materials["metal"], visible, 0.08))
    for index, angle in enumerate((0.0, math.pi * 0.5, math.pi, math.pi * 1.5)):
        radius = 3.25
        z = 8.0 + (index % 2) * 5.5
        x, y = math.sin(angle) * radius, -math.cos(angle) * radius
        window = A.add_box(f"SM_M01_STAGEB_Lighthouse_Window_{index:02d}", (x, y, z), (1.1, 0.18, 1.55), materials["glass"], visible, 0.04, angle)
        objects.append(window)
    objects.append(add_cylinder("SM_M01_STAGEB_Lighthouse_GallerySlab", (0, 0, 23.25), 3.65, 0.42, materials["concrete"], visible, 64, bevel=0.06))
    objects.append(add_torus("SM_M01_STAGEB_Lighthouse_GalleryRailTop", (0, 0, 24.45), 3.45, 0.075, materials["metal"], visible))
    for index in range(24):
        angle = math.tau * index / 24
        objects.append(add_cylinder(f"SM_M01_STAGEB_Lighthouse_GalleryPost_{index:02d}", (math.cos(angle) * 3.45, math.sin(angle) * 3.45, 23.85), 0.045, 1.2, materials["metal"], visible, 12, bevel=0.01))
    objects.append(add_cylinder("SM_M01_STAGEB_Lighthouse_LanternBase", (0, 0, 23.75), 2.15, 0.55, materials["red_paint"], visible, 64, bevel=0.05))
    objects.append(add_cylinder("SM_M01_STAGEB_Lighthouse_LanternGlass", (0, 0, 25.45), 1.85, 2.8, materials["glass"], visible, 64, bevel=0.04))
    for index in range(12):
        angle = math.tau * index / 12
        objects.append(add_cylinder(f"SM_M01_STAGEB_Lighthouse_LanternMullion_{index:02d}", (math.cos(angle) * 1.78, math.sin(angle) * 1.78, 25.45), 0.035, 2.65, materials["metal"], visible, 10, bevel=0.008))
    objects.append(add_icosphere("SM_M01_STAGEB_Lighthouse_Beacon", (0, 0, 25.55), (0.45, 0.45, 0.30), materials["beacon"], visible, 3))
    objects.append(add_cone("SM_M01_STAGEB_Lighthouse_Roof", (0, 0, 28.0), 2.45, 0.15, 2.5, materials["red_paint"], visible, 64, 0.04))
    objects.append(add_cylinder("SM_M01_STAGEB_Lighthouse_Finial", (0, 0, 29.65), 0.10, 1.1, materials["metal"], visible, 16, bevel=0.02))
    add_collision_cylinder("UCX_SM_M01_STAGEB_Lighthouse_00", (0, 0, 11.9), 4.0, 22.0, collision)
    add_collision_cylinder("UCX_SM_M01_STAGEB_Lighthouse_Lantern_00", (0, 0, 25.45), 2.2, 4.8, collision)
    A.add_socket("SOCKET_SM_M01_STAGEB_Lighthouse_Origin", (0, 0, 0), sockets)
    A.add_socket("SOCKET_SM_M01_STAGEB_Lighthouse_Beacon", (0, 0, 25.55), sockets)
    return {"objects": objects, "height_m": 30.2, "tower_base_diameter_m": 8.0}


def parabolic_dish(material: bpy.types.Material, target: bpy.types.Collection) -> bpy.types.Object:
    rings, segments, radius, focal = 9, 64, 4.0, 2.8
    vertices: list[tuple[float, float, float]] = [(0.0, 0.0, 0.0)]
    for ring in range(1, rings + 1):
        r = radius * ring / rings
        y = -(r * r) / (4.0 * focal)
        for segment in range(segments):
            angle = math.tau * segment / segments
            vertices.append((math.cos(angle) * r, y, math.sin(angle) * r))
    faces: list[tuple[int, ...]] = []
    for segment in range(segments):
        faces.append((0, 1 + segment, 1 + (segment + 1) % segments))
    for ring in range(1, rings):
        lower = 1 + (ring - 1) * segments
        upper = 1 + ring * segments
        for segment in range(segments):
            faces.append((lower + segment, lower + (segment + 1) % segments, upper + (segment + 1) % segments, upper + segment))
    dish = A.create_custom_mesh("SM_M01_STAGEB_Radar_Dish", vertices, faces, [material], target)
    dish.location = (0.0, 0.0, 12.8)
    A.add_bevel(dish, 0.018, 2)
    return dish


def build_radar(
    materials: dict[str, bpy.types.Material],
    visible: bpy.types.Collection,
    collision: bpy.types.Collection,
    sockets: bpy.types.Collection,
) -> dict[str, Any]:
    objects = [
        A.add_box("SM_M01_STAGEB_Radar_Bunker", (0, 0, 1.65), (12.0, 9.0, 3.3), materials["concrete_dark"], visible, 0.18),
        A.add_box("SM_M01_STAGEB_Radar_BunkerCap", (0, 0, 3.45), (12.5, 9.5, 0.3), materials["concrete"], visible, 0.08),
        A.add_box("SM_M01_STAGEB_Radar_Door", (0, -4.58, 1.5), (2.0, 0.24, 2.7), materials["olive"], visible, 0.06),
    ]
    for x in (-3.4, 3.4):
        objects.append(A.add_box(f"SM_M01_STAGEB_Radar_TowerLeg_{x:+.1f}", (x, 0, 7.1), (0.45, 0.45, 7.2), materials["metal"], visible, 0.05))
    for z in (4.5, 6.3, 8.1, 9.9):
        objects.append(A.add_box(f"SM_M01_STAGEB_Radar_Crossbeam_{z:.1f}", (0, 0, z), (7.2, 0.38, 0.38), materials["metal"], visible, 0.04))
        lower = max(3.55, z - 1.65)
        upper = min(10.65, z + 1.65)
        objects.append(add_beam_between(f"SM_M01_STAGEB_Radar_BraceA_{z:.1f}", (-3.4, 0.02, lower), (3.4, 0.02, upper), 0.18, materials["metal"], visible))
        objects.append(add_beam_between(f"SM_M01_STAGEB_Radar_BraceB_{z:.1f}", (3.4, -0.02, lower), (-3.4, -0.02, upper), 0.18, materials["metal"], visible))
    objects.append(A.add_box("SM_M01_STAGEB_Radar_ServicePlatform", (0, 0, 10.8), (8.4, 5.4, 0.32), materials["metal"], visible, 0.05))
    dish = parabolic_dish(materials["olive"], visible)
    objects.append(dish)
    objects.append(add_torus("SM_M01_STAGEB_Radar_DishRim", (0, -1.42, 12.8), 4.0, 0.09, materials["metal"], visible, (math.pi * 0.5, 0, 0)))
    objects.append(add_cylinder("SM_M01_STAGEB_Radar_FeedHorn", (0, -3.6, 12.8), 0.34, 2.0, materials["olive"], visible, 32, (math.pi * 0.5, 0, 0), 0.04))
    for angle in (-0.55, 0.55):
        objects.append(A.add_box(f"SM_M01_STAGEB_Radar_FeedStrut_{angle:+.2f}", (math.sin(angle) * 1.2, -2.4, 12.8 + math.cos(angle) * 1.0), (0.12, 3.0, 0.12), materials["metal"], visible, 0.02, angle * 0.25))
    add_collision_box = A.add_collision_box
    add_collision_box("UCX_SM_M01_STAGEB_Radar_Bunker_00", (0, 0, 1.65), (12.0, 9.0, 3.3), collision)
    add_collision_box("UCX_SM_M01_STAGEB_Radar_Tower_00", (0, 0, 7.2), (7.4, 5.0, 7.6), collision)
    A.add_socket("SOCKET_SM_M01_STAGEB_Radar_Origin", (0, 0, 0), sockets)
    A.add_socket("SOCKET_SM_M01_STAGEB_Radar_DishPivot", (0, 0, 12.8), sockets)
    A.add_socket("SOCKET_SM_M01_STAGEB_Radar_Weakpoint", (0, -1.0, 12.8), sockets)
    return {"objects": objects, "dish_diameter_m": 8.0, "maximum_height_m": 16.8}


def build_street_furniture(materials: dict[str, bpy.types.Material], target: bpy.types.Collection, collision: bpy.types.Collection) -> dict[str, int]:
    families: dict[str, int] = {}
    for index, x in enumerate((-5.0, 0.0, 5.0)):
        A.add_box(f"SM_M01_STAGEB_Bench_{index:02d}_Seat", (x, 0, 0.72), (3.0, 0.62, 0.16), materials["wood"], target, 0.06)
        A.add_box(f"SM_M01_STAGEB_Bench_{index:02d}_Back", (x, 0.27, 1.25), (3.0, 0.15, 0.85), materials["wood"], target, 0.05)
        for leg in (-1.15, 1.15):
            A.add_box(f"SM_M01_STAGEB_Bench_{index:02d}_Leg_{leg:+.2f}", (x + leg, 0, 0.35), (0.14, 0.55, 0.7), materials["metal"], target, 0.03)
    families["bench"] = 3
    for index, x in enumerate((-7.0, -3.5, 3.5, 7.0)):
        add_cylinder(f"SM_M01_STAGEB_Bollard_{index:02d}", (x, 3.0, 0.55), 0.16, 1.1, materials["metal"], target, 20, bevel=0.03)
    families["bollard"] = 4
    for index, x in enumerate((-4.0, 4.0)):
        add_cylinder(f"SM_M01_STAGEB_LitterBin_{index:02d}", (x, 5.5, 0.65), 0.42, 1.3, materials["olive"], target, 32, bevel=0.05)
        add_torus(f"SM_M01_STAGEB_LitterBin_{index:02d}_Rim", (x, 5.5, 1.25), 0.39, 0.045, materials["metal"], target)
    families["litter_bin"] = 2
    for index, x in enumerate((-6.0, 0.0, 6.0)):
        A.add_box(f"SM_M01_STAGEB_Barrier_{index:02d}_Beam", (x, 8.0, 0.75), (4.2, 0.18, 0.32), materials["warning"], target, 0.04)
        for offset in (-1.8, 1.8):
            A.add_box(f"SM_M01_STAGEB_Barrier_{index:02d}_Foot_{offset:+.1f}", (x + offset, 8.0, 0.26), (0.18, 0.75, 0.52), materials["metal"], target, 0.03)
    families["barrier"] = 3
    for index, x in enumerate((-4.5, 4.5)):
        A.add_box(f"SM_M01_STAGEB_Sign_{index:02d}_Post", (x, 11.0, 1.5), (0.10, 0.10, 3.0), materials["metal"], target, 0.025)
        A.add_box(f"SM_M01_STAGEB_Sign_{index:02d}_Panel", (x, 11.0, 2.55), (1.4, 0.10, 0.8), materials["warning"], target, 0.04)
    families["sign"] = 2
    add_cylinder("SM_M01_STAGEB_Hydrant_Body", (0, 13.5, 0.58), 0.28, 1.16, materials["red_paint"], target, 32, bevel=0.05)
    add_cylinder("SM_M01_STAGEB_Hydrant_Cap", (0, 13.5, 1.18), 0.34, 0.18, materials["metal"], target, 32, bevel=0.04)
    families["hydrant"] = 1
    A.add_collision_box("UCX_SM_M01_STAGEB_StreetFurniture_00", (0, 6.0, 1.4), (18.0, 16.0, 2.8), collision)
    return families


def build_tree(
    name: str,
    x: float,
    y: float,
    height: float,
    trunk_radius: float,
    canopy: str,
    foliage: bpy.types.Material,
    materials: dict[str, bpy.types.Material],
    target: bpy.types.Collection,
) -> None:
    add_cylinder(name + "_Trunk", (x, y, height * 0.35), trunk_radius, height * 0.70, materials["wood"], target, 20, bevel=0.025)
    crown_z = height * 0.76
    if canopy == "pine":
        for level in range(4):
            add_cone(name + f"_Crown_{level:02d}", (x, y, crown_z + level * height * 0.10), height * (0.24 - level * 0.035), 0.05, height * 0.30, foliage, target, 28, 0.02)
    elif canopy == "poplar":
        for level in range(3):
            add_icosphere(name + f"_Crown_{level:02d}", (x, y, crown_z + level * height * 0.13), (height * 0.14, height * 0.14, height * 0.24), foliage, target, 2)
    elif canopy == "tamarisk":
        for index, offset in enumerate(((-0.7, 0.1), (0.6, -0.2), (0.0, 0.6), (0.2, -0.7))):
            add_icosphere(name + f"_Crown_{index:02d}", (x + offset[0], y + offset[1], crown_z + (index % 2) * 0.3), (height * 0.22, height * 0.18, height * 0.16), foliage, target, 2)
    else:
        for index, offset in enumerate(((-0.45, 0), (0.45, 0), (0, 0.42))):
            add_icosphere(name + f"_Crown_{index:02d}", (x + offset[0], y + offset[1], crown_z), (height * 0.18, height * 0.18, height * 0.14), foliage, target, 2)


def build_vegetation(materials: dict[str, bpy.types.Material], target: bpy.types.Collection, collision: bpy.types.Collection) -> dict[str, int]:
    rng = random.Random(SEED)
    species = {
        "tamarisk": materials["foliage_tamarisk"],
        "pine": materials["foliage_pine"],
        "poplar": materials["foliage_poplar"],
        "shrub": materials["foliage_shrub"],
    }
    counts: dict[str, int] = {}
    for species_index, (species_name, material) in enumerate(species.items()):
        counts[species_name] = 3
        for variant in range(3):
            x = (species_index - 1.5) * 5.0
            y = variant * 4.0
            height = (5.8 if species_name != "shrub" else 2.8) * rng.uniform(0.88, 1.14)
            build_tree(
                f"SM_M01_STAGEB_{species_name.title()}_{variant:02d}",
                x,
                y,
                height,
                0.22 if species_name != "shrub" else 0.12,
                species_name,
                material,
                materials,
                target,
            )
    A.add_collision_box("UCX_SM_M01_STAGEB_VegetationSet_00", (0, 4.0, 4.0), (22.0, 14.0, 8.0), collision)
    return counts


def build_damage_and_variants(
    materials: dict[str, bpy.types.Material],
    damage: bpy.types.Collection,
    variants: bpy.types.Collection,
) -> tuple[dict[str, int], dict[str, int]]:
    rng = random.Random(SEED + 77)
    damage_states = {"salt_spall": 1, "soot_blast": 1, "rubble_cluster": 1}
    A.add_box("SM_M01_STAGEB_Damage_SaltSpallWall", (0, 0, 2.0), (7.0, 0.35, 4.0), materials["white_paint"], damage, 0.08)
    for index in range(18):
        x = rng.uniform(-3.0, 3.0)
        z = rng.uniform(0.2, 3.7)
        add_icosphere(f"SM_M01_STAGEB_Damage_Spall_{index:02d}", (x, -0.22, z), (rng.uniform(0.08, 0.25), 0.05, rng.uniform(0.06, 0.20)), materials["concrete_dark"], damage, 1)
    A.add_box("SM_M01_STAGEB_Damage_SootPanel", (9.0, 0, 2.0), (7.0, 0.35, 4.0), materials["brick"], damage, 0.08)
    A.add_box("SM_M01_STAGEB_Damage_SootOverlay", (9.0, -0.22, 2.45), (4.8, 0.05, 2.6), materials["soot"], damage, 0.03)
    for index in range(7):
        add_icosphere(f"SM_M01_STAGEB_Damage_Rubble_{index:02d}", (18.0 + rng.uniform(-2.0, 2.0), rng.uniform(-1.2, 1.2), rng.uniform(0.15, 0.6)), (rng.uniform(0.25, 0.7), rng.uniform(0.25, 0.6), rng.uniform(0.18, 0.5)), materials["concrete_dark"], damage, 1)

    compositions: dict[str, int] = {}
    wall_materials = [materials["plaster_fde"], materials["plaster_blue"], materials["brick"], materials["white_paint"], materials["concrete"], materials["olive"]]
    for index, material in enumerate(wall_materials):
        x = index * 5.0
        height = 3.0 + (index % 3) * 0.65
        A.add_box(f"SM_M01_STAGEB_FacadeVariant_{index+4:02d}_Wall", (x, 0, height * 0.5), (4.2, 0.38, height), material, variants, 0.07)
        A.add_window(f"SM_M01_STAGEB_FacadeVariant_{index+4:02d}_Window", x, -0.25, min(1.75, height * 0.55), True, materials, variants)
        if index in (1, 3, 5):
            A.add_balcony(f"SM_M01_STAGEB_FacadeVariant_{index+4:02d}_Balcony", x, -0.25, min(1.75, height * 0.55), materials, variants)
        roof_shape = "stepped" if index % 2 else "parapet"
        compositions[f"facade_{index+4:02d}_{roof_shape}"] = 1
        if roof_shape == "stepped":
            A.add_box(f"SM_M01_STAGEB_FacadeVariant_{index+4:02d}_RoofStep", (x + 0.8, 0, height + 0.35), (2.2, 0.55, 0.7), materials["roof"], variants, 0.05)
        else:
            A.add_box(f"SM_M01_STAGEB_FacadeVariant_{index+4:02d}_Parapet", (x, 0, height + 0.3), (4.2, 0.42, 0.6), materials["roof"], variants, 0.05)
    return damage_states, compositions


def create_texture_atlas(output: Path) -> list[Path]:
    texture_dir = output / "textures"
    texture_dir.mkdir(parents=True, exist_ok=True)
    size = 2048
    rng = np.random.default_rng(SEED)
    noise = rng.normal(0.0, 0.022, (size, size, 1)).astype(np.float32)
    palette = np.array(
        [
            [0.58, 0.58, 0.54],
            [0.48, 0.035, 0.022],
            [0.14, 0.17, 0.095],
            [0.27, 0.14, 0.065],
            [0.12, 0.24, 0.10],
            [0.045, 0.15, 0.075],
            [0.19, 0.31, 0.085],
            [0.018, 0.016, 0.014],
        ],
        dtype=np.float32,
    )
    bands = np.minimum(np.arange(size) * len(palette) // size, len(palette) - 1)
    base = np.clip(palette[bands][:, None, :] + noise, 0.0, 1.0)
    base = np.repeat(base, size, axis=1)
    rough_values = np.array([0.55, 0.48, 0.58, 0.78, 0.82, 0.85, 0.80, 0.92], dtype=np.float32)
    rough = np.clip(rough_values[bands][:, None, None] + noise * 0.45, 0.0, 1.0)
    rough = np.repeat(rough, size, axis=1)
    metallic = np.zeros((size, size, 1), dtype=np.float32)
    normal = np.zeros((size, size, 3), dtype=np.float32)
    normal[:, :, 0] = 0.5 + noise[:, :, 0] * 0.35
    normal[:, :, 1] = 0.5 + np.roll(noise[:, :, 0], 2, axis=0) * 0.35
    normal[:, :, 2] = 1.0
    ao = np.clip(0.93 + noise * 0.55, 0.72, 1.0)
    maps = {
        "T_M01_STAGEB_Atlas_BaseColor.png": base,
        "T_M01_STAGEB_Atlas_Normal.png": normal,
        "T_M01_STAGEB_Atlas_Roughness.png": np.repeat(rough, 3, axis=2),
        "T_M01_STAGEB_Atlas_Metallic.png": np.repeat(metallic, 3, axis=2),
        "T_M01_STAGEB_Atlas_AO.png": np.repeat(ao, 3, axis=2),
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


def translate_groups(groups: Iterable[bpy.types.Collection], offset: Vector) -> None:
    seen: set[int] = set()
    for obj in A.recursive_objects(groups):
        pointer = obj.as_pointer()
        if pointer in seen:
            continue
        obj.location += offset
        seen.add(pointer)


def render_suite(
    scene: bpy.types.Scene,
    rig: dict[str, bpy.types.Object],
    materials: dict[str, bpy.types.Material],
    output: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    scene.render.resolution_x, scene.render.resolution_y = CHECKPOINT_RESOLUTION
    checkpoints = [
        ("checkpoint_01_lighthouse", (-18.0, -38.0, 18.0), (0.0, 0.0, 14.0), 58.0),
        ("checkpoint_02_radar", (23.0, -32.0, 15.0), (24.0, 0.0, 9.0), 58.0),
        ("checkpoint_03_variation", (80.0, -44.0, 20.0), (86.0, 4.0, 5.0), 52.0),
    ]
    checkpoint_results: list[dict[str, Any]] = []
    A.configure_condition(scene, rig, "daylight", materials)
    correction_used = False
    for name, location, target, lens in checkpoints:
        A.point_camera(rig["camera"], location, target, lens)
        path = output / "renders" / "checkpoints" / f"{name}.png"
        metrics = A.render_and_measure(scene, path)
        passed = metrics["mean_luma_linear"] >= 0.03 and metrics["black_fraction_linear_0_01"] <= 0.35
        corrected = False
        if not passed and not correction_used:
            rig["fill"].data.energy *= 1.6
            metrics = A.render_and_measure(scene, path)
            passed = metrics["mean_luma_linear"] >= 0.03 and metrics["black_fraction_linear_0_01"] <= 0.35
            correction_used = True
            corrected = True
        require(passed, f"Checkpoint luminance failed: {name}")
        require((metrics["width"], metrics["height"]) == CHECKPOINT_RESOLUTION, f"Checkpoint resolution failed: {name}")
        checkpoint_results.append({"id": name, "path": str(path), "metrics": metrics, "bounded_correction_used": corrected})

    scene.render.resolution_x, scene.render.resolution_y = FINAL_RESOLUTION
    views = {
        "landmarks": ((10.0, -70.0, 28.0), (12.0, 0.0, 13.0), 52.0),
        "street": ((62.0, -48.0, 13.0), (68.0, 4.0, 5.0), 58.0),
        "aerial": ((74.0, -88.0, 58.0), (64.0, 5.0, 8.0), 48.0),
    }
    final_results: list[dict[str, Any]] = []
    for condition in FINAL_CONDITIONS:
        A.configure_condition(scene, rig, condition, materials)
        for view in FINAL_VIEWS:
            location, target, lens = views[view]
            A.point_camera(rig["camera"], location, target, lens)
            path = output / "renders" / "final" / f"{condition}_{view}.png"
            metrics = A.render_and_measure(scene, path)
            require((metrics["width"], metrics["height"]) == FINAL_RESOLUTION, f"Final resolution failed: {condition}_{view}")
            require(metrics["mean_luma_linear"] >= (0.008 if condition == "night" else 0.025), f"Final render is too dark: {condition}_{view}")
            require(metrics["black_fraction_linear_0_01"] <= (0.70 if condition == "night" else 0.42), f"Final render is excessively black: {condition}_{view}")
            final_results.append({"condition": condition, "view": view, "path": str(path), "metrics": metrics})
    require(len(final_results) == 15, "Final render count is not exactly fifteen")
    return checkpoint_results, final_results


def main() -> int:
    args = parse_args()
    require(args.asset_id == ASSET_ID, f"Unexpected asset id: {args.asset_id}")
    source_path = Path(__file__).resolve()
    require(A.sha256(source_path) == args.expected_source_sha256.lower(), "Attempt source hash does not match frozen authority")
    require(args.expected_stagea_helper_sha256.lower() == STAGEA_HELPER_SHA256, "StageA helper argument does not match contract")
    require(A.sha256(STAGEA_HELPER) == STAGEA_HELPER_SHA256, "StageA helper hash mismatch")
    output = Path(args.output).resolve()
    require(not output.exists(), f"Output namespace already exists: {output}")
    output.mkdir(parents=True)

    scene = A.reset_scene()
    root = A.collection("M01_VISIBLE_ENVIRONMENT_KIT_STAGEB")
    lighthouse = A.collection("ASSET_Lighthouse", root)
    lighthouse_collision = A.collection("COLLISION_Lighthouse", root)
    lighthouse_sockets = A.collection("SOCKETS_Lighthouse", root)
    radar = A.collection("ASSET_RadarPost", root)
    radar_collision = A.collection("COLLISION_RadarPost", root)
    radar_sockets = A.collection("SOCKETS_RadarPost", root)
    street = A.collection("ASSET_StreetFurniture", root)
    street_collision = A.collection("COLLISION_StreetFurniture", root)
    vegetation = A.collection("ASSET_Vegetation", root)
    vegetation_collision = A.collection("COLLISION_Vegetation", root)
    damage = A.collection("ASSET_DamageDebris", root)
    variants = A.collection("ASSET_DistrictVariants", root)
    materials = build_materials()

    lighthouse_receipt = build_lighthouse(materials, lighthouse, lighthouse_collision, lighthouse_sockets)
    radar_receipt = build_radar(materials, radar, radar_collision, radar_sockets)
    street_families = build_street_furniture(materials, street, street_collision)
    vegetation_species = build_vegetation(materials, vegetation, vegetation_collision)
    damage_states, facade_compositions = build_damage_and_variants(materials, damage, variants)
    textures = create_texture_atlas(output)

    layout = [
        ((lighthouse, lighthouse_collision, lighthouse_sockets), Vector((0, 0, 0))),
        ((radar, radar_collision, radar_sockets), Vector((24, 0, 0))),
        ((street, street_collision), Vector((52, 0, 0))),
        ((vegetation, vegetation_collision), Vector((76, 0, 0))),
        ((damage,), Vector((104, 0, 0))),
        ((variants,), Vector((126, 0, 0))),
    ]
    for groups, offset in layout:
        translate_groups(groups, offset)
    rig = A.add_review_rig(scene)
    rig["camera"].name = "CAM_STAGEB_Review"
    rig["sun"].name = "LIGHT_STAGEB_Sun"
    rig["fill"].name = "LIGHT_STAGEB_Fill"
    checkpoints, final_renders = render_suite(scene, rig, materials, output)
    for groups, offset in reversed(layout):
        translate_groups(groups, -offset)

    blend_path = output / "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEB.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    export_root = output / "exports"
    exports = [
        export_root / "SM_M01_STAGEB_Lighthouse.glb",
        export_root / "SM_M01_STAGEB_RadarPost.glb",
        export_root / "SM_M01_STAGEB_StreetFurniture.glb",
        export_root / "SM_M01_STAGEB_VegetationSet.glb",
        export_root / "SM_M01_STAGEB_DamageDebrisSet.glb",
        export_root / "SM_M01_STAGEB_DistrictVariants.glb",
    ]
    A.export_glb(exports[0], (lighthouse, lighthouse_collision, lighthouse_sockets))
    A.export_glb(exports[1], (radar, radar_collision, radar_sockets))
    A.export_glb(exports[2], (street, street_collision))
    A.export_glb(exports[3], (vegetation, vegetation_collision))
    A.export_glb(exports[4], (damage,))
    A.export_glb(exports[5], (variants,))

    visible_groups = (lighthouse, radar, street, vegetation, damage, variants)
    stats = A.collection_stats(visible_groups)
    required_sockets = [
        "SOCKET_SM_M01_STAGEB_Lighthouse_Origin",
        "SOCKET_SM_M01_STAGEB_Lighthouse_Beacon",
        "SOCKET_SM_M01_STAGEB_Radar_Origin",
        "SOCKET_SM_M01_STAGEB_Radar_DishPivot",
        "SOCKET_SM_M01_STAGEB_Radar_Weakpoint",
    ]
    missing_sockets = [name for name in required_sockets if bpy.data.objects.get(name) is None]
    collision_objects = sorted(obj.name for obj in bpy.data.objects if obj.name.startswith("UCX_"))
    require(not missing_sockets, f"Missing sockets: {missing_sockets}")
    require(len(collision_objects) >= 6, "Insufficient collision objects")
    require(len(street_families) >= 6, "Street-furniture family count is below six")
    require(len(vegetation_species) >= 4, "Vegetation species count is below four")
    require(len(facade_compositions) >= 6, "Facade composition count is below six")
    require(len(damage_states) >= 3, "Damage-state count is below three")
    require(all(path.is_file() and path.stat().st_size > 0 for path in exports), "One or more exports are missing")

    A.atomic_json(output / "dimension_identity_receipt.json", {
        "schema": "skyguard.m01-visible-environment-kit.stageb.dimension-identity.v1",
        "gate": GATE,
        "lighthouse": lighthouse_receipt,
        "radar": radar_receipt,
        "identity_policy": "Mission 1 coastal lighthouse and radar post; no unsupported real installation or manufacturer claim",
        "passed": lighthouse_receipt["height_m"] >= 29.0 and radar_receipt["dish_diameter_m"] == 8.0,
    })
    A.atomic_json(output / "variation_receipt.json", {
        "schema": "skyguard.m01-visible-environment-kit.stageb.variation.v1",
        "gate": GATE,
        "street_furniture_families": street_families,
        "vegetation_species": vegetation_species,
        "damage_states": damage_states,
        "facade_compositions": facade_compositions,
        "passed": True,
    })
    A.atomic_json(output / "topology_uv_receipt.json", {"schema":"skyguard.m01-visible-environment-kit.stageb.topology-uv.v1","gate":GATE,"statistics":stats,"passed":True})
    A.atomic_json(output / "material_texture_receipt.json", {
        "schema":"skyguard.m01-visible-environment-kit.stageb.material-texture.v1",
        "gate":GATE,
        "materials":sorted(materials),
        "texture_maps":[{"path":path.relative_to(output).as_posix(),"bytes":path.stat().st_size,"sha256":A.sha256(path)} for path in textures],
        "atlas_resolution":[2048,2048],
        "maps":["BaseColor","Normal","Roughness","Metallic","AO"],
        "passed":len(textures)==5,
    })
    A.atomic_json(output / "checkpoint_receipt.json", {"schema":"skyguard.m01-visible-environment-kit.stageb.checkpoints.v1","gate":GATE,"checkpoints":checkpoints,"count":len(checkpoints),"passed":len(checkpoints)==3})
    A.atomic_json(output / "render_receipt.json", {"schema":"skyguard.m01-visible-environment-kit.stageb.renders.v1","gate":GATE,"resolution":list(FINAL_RESOLUTION),"renders":final_renders,"count":len(final_renders),"passed":len(final_renders)==15})
    A.atomic_json(output / "export_receipt.json", {
        "schema":"skyguard.m01-visible-environment-kit.stageb.exports.v1",
        "gate":GATE,
        "exports":[{"path":path.relative_to(output).as_posix(),"bytes":path.stat().st_size,"sha256":A.sha256(path)} for path in exports],
        "required_sockets":required_sockets,
        "missing_sockets":missing_sockets,
        "collision_objects":collision_objects,
        "passed":len(exports)==6 and not missing_sockets and len(collision_objects)>=6,
    })
    A.atomic_json(output / "source_parity_receipt.json", {
        "schema":"skyguard.m01-visible-environment-kit.stageb.source-parity.v1",
        "source":str(source_path),
        "bytes":source_path.stat().st_size,
        "sha256":A.sha256(source_path),
        "expected_sha256":args.expected_source_sha256.lower(),
        "stagea_helper":str(STAGEA_HELPER),
        "stagea_helper_sha256":A.sha256(STAGEA_HELPER),
        "passed":True,
    })
    artifact_path = output / "artifact_inventory.json"
    terminal_path = output / "terminal_receipt.json"
    A.atomic_json(artifact_path, {"schema":"skyguard.m01-visible-environment-kit.stageb.inventory.v1","gate":GATE,"files":A.inventory(output,{artifact_path,terminal_path})})
    A.atomic_json(terminal_path, {
        "schema":"skyguard.m01-visible-environment-kit.stageb.terminal.v1",
        "gate":GATE,
        "asset_id":ASSET_ID,
        "status":"BLENDER_COMPLETED_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW",
        "created_utc":A.utc_now(),
        "blend_count":1,
        "glb_count":6,
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
