"""Bounded art correction for Mission 1 visible-environment Checkpoint02.

This executes a text-audited derivative of the frozen factory-empty Checkpoint01
generator. It never reads or reuses geometry from failed Checkpoint01 outputs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SOURCE = ROOT / r"Scripts\ToolchainWave08\environment_production_reset01\build_m01_visible_environment_production_reset01_checkpoint01.py"
API_PROBE = ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_BLENDER52_API_PROBE01_RESULT.json"
EXPECTED_SOURCE = "fefa08e50cb9e78d8d5a3965635d8f065df251d8861c777821c2a88d64eaf891"
EXPECTED_API_PROBE = "c017409181b17a9f27fc909445d458ada586d096f0ab66a40fe4fe2b3d37f53e"


def replace_once(source: str, old: str, new: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one binding for {old[:80]!r}; found {count}")
    return source.replace(old, new, 1)


def main() -> None:
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_SOURCE:
        raise RuntimeError("Frozen Checkpoint01 generator hash mismatch")
    probe_raw = API_PROBE.read_bytes()
    if hashlib.sha256(probe_raw).hexdigest() != EXPECTED_API_PROBE:
        raise RuntimeError("Frozen Blender 5.2 API probe hash mismatch")
    probe = json.loads(probe_raw)
    if "MULTIPLE_SCATTERING" not in probe["sky_texture"]["sky_type_enum"]:
        raise RuntimeError("Required Blender 5.2 sky implementation absent")
    if "aerosol_density" not in probe["sky_texture"]["properties"]:
        raise RuntimeError("Required Blender 5.2 aerosol property absent")

    source = raw.decode("utf-8")
    substitutions = [
        ('VisibleEnvironmentProductionReset01_Checkpoint01"', 'VisibleEnvironmentProductionReset01_Checkpoint02"'),
        ('M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT01.blend', 'M01_VISIBLE_ENVIRONMENT_PRODUCTION_RESET01_CHECKPOINT02.blend'),
        ('sky.sky_type = "NISHITA"', 'sky.sky_type = "MULTIPLE_SCATTERING"'),
        ('sky.dust_density = 1.2', 'sky.aerosol_density = 0.8'),
        ('"skyguard.m01-visible-environment-production-reset01.checkpoint01-receipt.v1"', '"skyguard.m01-visible-environment-production-reset01.checkpoint02-receipt.v1"'),
        ('"skyguard.m01-visible-environment-production-reset01.checkpoint01-inventory.v1"', '"skyguard.m01-visible-environment-production-reset01.checkpoint02-inventory.v1"'),
        ('background.inputs["Strength"].default_value = 0.42', 'background.inputs["Strength"].default_value = 0.24'),
        ('sun_data.energy = 3.1', 'sun_data.energy = 1.65'),
        ('sun_data.angle = math.radians(5.0)', 'sun_data.angle = math.radians(3.0)'),
        ('area_data.energy = 1450.0', 'area_data.energy = 620.0'),
        ('noise.inputs["Scale"].default_value = 1.2', 'noise.inputs["Scale"].default_value = 0.42'),
        ('bump.inputs["Strength"].default_value = 0.35', 'bump.inputs["Strength"].default_value = 0.22'),
        ('bump.inputs["Distance"].default_value = 0.2', 'bump.inputs["Distance"].default_value = 0.08'),
        ('bsdf.inputs["Roughness"].default_value = 0.18', 'bsdf.inputs["Roughness"].default_value = 0.10'),
        ('bsdf.inputs["Metallic"].default_value = 0.15', 'bsdf.inputs["Metallic"].default_value = 0.0'),
        ('"leaf_a": flat_material("M_ENV_Leaf_A", (0.055, 0.19, 0.07, 1.0), 0.72),', '"leaf_a": flat_material("M_ENV_Leaf_A", (0.018, 0.075, 0.024, 1.0), 0.78),'),
        ('"leaf_b": flat_material("M_ENV_Leaf_B", (0.09, 0.27, 0.105, 1.0), 0.68),', '"leaf_b": flat_material("M_ENV_Leaf_B", (0.028, 0.12, 0.038, 1.0), 0.74),'),
        ('"leaf_c": flat_material("M_ENV_Leaf_C", (0.035, 0.125, 0.055, 1.0), 0.78),', '"leaf_c": flat_material("M_ENV_Leaf_C", (0.012, 0.052, 0.018, 1.0), 0.84),'),
    ]
    for old, new in substitutions:
        source = replace_once(source, old, new)

    source = replace_once(
        source,
        '    color.extension = "REPEAT"\n',
        '    color.extension = "REPEAT"\n'
        '    color.projection = "BOX"\n'
        '    if hasattr(color, "projection_blend"):\n'
        '        color.projection_blend = 0.16\n',
    )
    source = replace_once(
        source,
        '    roughness.extension = "REPEAT"\n',
        '    roughness.extension = "REPEAT"\n'
        '    roughness.projection = "BOX"\n'
        '    if hasattr(roughness, "projection_blend"):\n'
        '        roughness.projection_blend = 0.16\n',
    )
    source = replace_once(
        source,
        '    normal_tex.extension = "REPEAT"\n',
        '    normal_tex.extension = "REPEAT"\n'
        '    normal_tex.projection = "BOX"\n'
        '    if hasattr(normal_tex, "projection_blend"):\n'
        '        normal_tex.projection_blend = 0.16\n',
    )

    source = replace_once(
        source,
        '        "water": water_material(),\n',
        '        "wet_sand": flat_material("M_ENV_Wet_Sand", (0.055, 0.065, 0.055, 1.0), 0.34),\n'
        '        "awning_red": flat_material("M_ENV_Awning_Red", (0.20, 0.028, 0.018, 1.0), 0.62),\n'
        '        "awning_blue": flat_material("M_ENV_Awning_Blue", (0.018, 0.055, 0.13, 1.0), 0.58),\n'
        '        "curtain_warm": flat_material("M_ENV_Curtain_Warm", (0.20, 0.095, 0.035, 1.0), 0.82),\n'
        '        "planter": flat_material("M_ENV_Planter", (0.11, 0.045, 0.018, 1.0), 0.88),\n'
        '        "water": water_material(),\n',
    )

    foliage_old = '''        for leaf_index in range(7):
            offset = Vector((rng.uniform(-0.75, 0.75), rng.uniform(-0.75, 0.75), rng.uniform(-0.5, 0.65))) * scale
            loc = Vector(tip) + offset
            leaf_mat = mats[("leaf_a", "leaf_b", "leaf_c")[(branch_index + leaf_index) % 3]]
            sphere(f"{asset}_LEAF_{branch_index:02d}_{leaf_index:02d}", tuple(loc), (rng.uniform(0.45, 0.82) * scale, rng.uniform(0.32, 0.62) * scale, rng.uniform(0.24, 0.5) * scale), leaf_mat, asset, 2)
'''
    foliage_new = '''        for leaf_index in range(11):
            offset = Vector((rng.uniform(-0.92, 0.92), rng.uniform(-0.92, 0.92), rng.uniform(-0.62, 0.78))) * scale
            loc = Vector(tip) + offset
            leaf_mat = mats[("leaf_a", "leaf_b", "leaf_c")[(branch_index + leaf_index) % 3]]
            leaf = sphere(
                f"{asset}_LEAF_{branch_index:02d}_{leaf_index:02d}",
                tuple(loc),
                (rng.uniform(0.24, 0.52) * scale, rng.uniform(0.18, 0.40) * scale, rng.uniform(0.10, 0.25) * scale),
                leaf_mat,
                asset,
                2,
            )
            leaf.rotation_euler = (rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), rng.uniform(0.0, math.tau))
'''
    source = replace_once(source, foliage_old, foliage_new)

    art_helpers = '''

def build_irregular_ribbon(name: str, asset: str, y_center: float, width: float, z: float, amplitude: float, phase: float, material: bpy.types.Material) -> bpy.types.Object:
    segments = 72
    length = 150.0
    vertices: list[tuple[float, float, float]] = []
    for index in range(segments + 1):
        x = -length / 2 + length * index / segments
        wave = math.sin(x * 0.23 + phase) * amplitude + math.sin(x * 0.071 - phase * 0.7) * amplitude * 0.55
        vertices.append((x, y_center + wave - width / 2, z + math.sin(x * 0.17) * 0.015))
        vertices.append((x, y_center + wave + width / 2, z + math.sin(x * 0.13 + 1.2) * 0.015))
    faces = [(index * 2, index * 2 + 2, index * 2 + 3, index * 2 + 1) for index in range(segments)]
    return mesh_object(name, vertices, faces, material, asset)


def add_checkpoint02_facade_detail(asset: str, center_x: float, center_y: float, width: float, depth: float, floors: int, bays: int, variant: int, mats: dict[str, bpy.types.Material]) -> None:
    floor_h = 3.05
    ground_h = 3.65
    total_h = ground_h + floors * floor_h
    front_y = center_y - depth / 2
    bay_w = width / bays
    for bay in range(bays):
        x = center_x - width / 2 + bay_w * (bay + 0.5)
        if (bay + variant) % 2 == 0:
            awning = mats["awning_red"] if (bay + variant) % 4 == 0 else mats["awning_blue"]
            box(f"{asset}_AWNING_{bay:02d}", (x, front_y - 0.80, 3.03), (bay_w * 0.68, 1.35, 0.10), awning, asset, 0.035)
        for floor in range(floors):
            z_base = ground_h + floor * floor_h
            signature = bay * 13 + floor * 7 + variant * 5
            if signature % 5 == 0:
                box(f"{asset}_CURTAIN_{floor:02d}_{bay:02d}", (x, front_y + 0.315, z_base + 1.55), (bay_w * 0.52, 0.018, 1.28), mats["curtain_warm"], asset, 0.0)
            if signature % 7 == 0:
                box(f"{asset}_PLANTER_{floor:02d}_{bay:02d}", (x, front_y - 1.48, z_base + 0.64), (bay_w * 0.48, 0.24, 0.26), mats["planter"], asset, 0.035)
                for plant in (-0.30, 0.0, 0.30):
                    sphere(f"{asset}_PLANT_{floor:02d}_{bay:02d}_{plant:+.2f}", (x + bay_w * plant, front_y - 1.50, z_base + 0.91), (0.18, 0.15, 0.22), mats["leaf_b"], asset, 2)
    cylinder(f"{asset}_ROOF_TANK", (center_x + width * 0.24, center_y + depth * 0.10, total_h + 1.55), 0.92, 1.65, mats["metal"], asset, 36, bevel=0.04)
    for side in (-1, 1):
        pipe_x = center_x + side * (width / 2 + 0.24)
        cylinder(f"{asset}_SERVICE_PIPE_{side:+d}", (pipe_x, center_y, total_h * 0.46), 0.055, total_h * 0.88, mats["rust"], asset, 14, bevel=0.008)
'''
    source = replace_once(source, '\n\ndef build_tree(', art_helpers + '\n\ndef build_tree(')

    foam_old = '''    # Layered foam/wet contact strips avoid the old hard brown waterline.
    for index, (y, width, z) in enumerate(((-24.2, 1.2, -0.30), (-22.8, 0.55, -0.23), (-21.4, 0.3, -0.18))):
        strip = box(f"{asset}_FOAM_{index:02d}", (0, y, z), (150, width, 0.025), mats["foam"], asset, 0.0)
        strip.rotation_euler[2] = math.radians(0.25 * (-1 if index % 2 else 1))
'''
    foam_new = '''    # Irregular wet-sand and foam ribbons provide legible water-to-shore contact.
    build_irregular_ribbon(f"{asset}_WET_CONTACT", asset, -20.8, 3.8, -0.20, 0.42, 0.3, mats["wet_sand"])
    for index, (y, width, z, amplitude, phase) in enumerate(((-24.0, 1.05, -0.28, 0.46, 0.0), (-22.6, 0.48, -0.21, 0.31, 1.7), (-21.25, 0.24, -0.15, 0.18, 3.1))):
        build_irregular_ribbon(f"{asset}_FOAM_{index:02d}", asset, y, width, z, amplitude, phase, mats["foam"])
'''
    source = replace_once(source, foam_old, foam_new)

    detail_calls = '''    add_checkpoint02_facade_detail("SM_M01_Apartment_Production_A", -38.0, 18.5, 24.0, 12.5, 5, 6, 0, mats)
    add_checkpoint02_facade_detail("SM_M01_Midrise_Production_B", -3.0, 20.5, 29.0, 15.0, 7, 7, 1, mats)
    add_checkpoint02_facade_detail("SM_M01_CornerResidence_Production_C", 34.0, 18.8, 26.0, 13.5, 6, 6, 2, mats)
'''
    source = replace_once(source, '    build_lighthouse(mats)\n', detail_calls + '    build_lighthouse(mats)\n')

    camera_old = '''        ("C01_COASTAL_ROUTE", (0.0, -72.0, 18.0), (0.0, 13.0, 12.0), 44.0),
        ("C02_STREET_CLOSE", (-15.0, -2.5, 9.0), (-16.0, 18.0, 10.5), 52.0),
        ("C03_DISTRICT_AERIAL", (3.0, -32.0, 72.0), (0.0, 4.0, 5.0), 46.0),
        ("C04_LIGHTHOUSE_SHORE", (67.0, -45.0, 12.0), (55.0, -1.0, 11.0), 52.0),
'''
    camera_new = '''        ("C01_COASTAL_ROUTE", (0.0, -58.0, 11.5), (0.0, 5.0, 7.0), 42.0),
        ("C02_STREET_CLOSE", (-18.0, -12.0, 10.0), (-15.0, 18.0, 10.0), 45.0),
        ("C03_DISTRICT_AERIAL", (3.0, -48.0, 48.0), (0.0, -4.0, 4.0), 44.0),
        ("C04_LIGHTHOUSE_SHORE", (72.0, 14.0, 10.0), (56.0, -25.0, 2.0), 46.0),
'''
    source = replace_once(source, camera_old, camera_new)

    code = compile(source, str(SOURCE) + "::Checkpoint02", "exec")
    namespace = {"__name__": "__main__", "__file__": str(SOURCE)}
    exec(code, namespace, namespace)


if __name__ == "__main__":
    main()
