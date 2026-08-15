from __future__ import annotations

"""Production refinement binding for the frozen Mission 1 street/shore proof.

Recovery02 loads the immutable source without executing it, applies only fresh
identity and Blender 5.2 renderer compatibility substitutions, then replaces
the bounded art functions identified by Recovery01 direct visual review.
"""

import hashlib
import math
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\Workers\worker_m01_environment_hero_streetshore_proof01.py")
EXPECTED_SOURCE_SHA256 = "94a831f9c0c70c67741e2b1bb7448796f8da70cc875e84c8d5c925583f933866"
ASSET_ID = "m01-environment-hero-streetshore-proof01-recovery02"
GATE_ID = "M01_ENVIRONMENT_PRODUCTION_RESET01_HERO_STREETSHORE_PROOF01_RECOVERY02"
RECOVERY01_FREEZE = Path(
    r"D:\Skyguard52\Docs\AAA_Review\M01_ENVIRONMENT_PRODUCTION_RESET01_"
    r"HERO_STREETSHORE_PROOF01_RECOVERY01_ATTEMPT01_TERMINAL_FREEZE.json"
)
EXPECTED_RECOVERY01_FREEZE_SHA256 = "b49d338c68f7c32f229ac16ed0671d9844172c0ad0c0b705bd5a5953bd5d12d3"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if not SOURCE.is_file() or sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Frozen source worker authority mismatch")
if not RECOVERY01_FREEZE.is_file() or sha256(RECOVERY01_FREEZE) != EXPECTED_RECOVERY01_FREEZE_SHA256:
    raise RuntimeError("Recovery01 terminal authority mismatch")

source_text = SOURCE.read_text(encoding="utf-8")
substitutions = (
    ('ASSET_ID = "m01-environment-hero-streetshore-proof01"', f'ASSET_ID = "{ASSET_ID}"'),
    ('GATE = "M01_ENVIRONMENT_PRODUCTION_RESET01_HERO_STREETSHORE_PROOF01"', f'GATE = "{GATE_ID}"'),
    ('scene.render.engine = "BLENDER_EEVEE_NEXT"', 'scene.render.engine = "BLENDER_EEVEE"'),
)
for old_value, new_value in substitutions:
    if source_text.count(old_value) != 1:
        raise RuntimeError(f"Frozen source substitution cardinality mismatch: {old_value}")
    source_text = source_text.replace(old_value, new_value, 1)

namespace = {"__name__": "_skyguard_frozen_m01_worker", "__file__": str(SOURCE)}
exec(compile(source_text, str(SOURCE) + "::Recovery02Base", "exec"), namespace)

bpy = namespace["bpy"]
Vector = namespace["Vector"]
add_box = namespace["add_box"]
add_cylinder = namespace["add_cylinder"]
add_icosphere = namespace["add_icosphere"]
add_custom_mesh = namespace["add_custom_mesh"]
add_curve_strip = namespace["add_curve_strip"]
cylinder_between = namespace["cylinder_between"]
ORIGINAL_BUILD_BUILDING = namespace["build_building"]
ORIGINAL_BUILD_SHORE = namespace["build_shore_and_street"]


def refined_build_building(
    prefix,
    center_x,
    y_front,
    width,
    depth,
    floors,
    bay_widths,
    plaster_key,
    balcony_phase,
    materials,
    visible,
    collision,
):
    ORIGINAL_BUILD_BUILDING(
        prefix,
        center_x,
        y_front,
        width,
        depth,
        floors,
        bay_widths,
        plaster_key,
        balcony_phase,
        materials,
        visible,
        collision,
    )
    floor_h = 3.25
    total_h = floors * floor_h + 0.7
    normalized = [value * (width / sum(bay_widths)) for value in bay_widths]
    boundaries = [center_x - width * 0.5]
    for value in normalized:
        boundaries.append(boundaries[-1] + value)
    detail_material = materials["metal"] if prefix.endswith("A") else materials["concrete"]
    accent_material = materials["plaster_cool"] if prefix.endswith("A") else materials["plaster_warm"]

    for side, x in (("L", center_x - width * 0.5 + 0.65), ("R", center_x + width * 0.5 - 0.65)):
        add_cylinder(
            f"{prefix}_Rainwater_{side}",
            (x, y_front - 0.34, total_h * 0.48),
            0.075,
            total_h * 0.92,
            materials["metal"],
            visible,
            20,
            bevel=0.012,
        )
        for clamp_index in range(1, floors + 1):
            add_box(
                f"{prefix}_Rainwater_{side}_Clamp_{clamp_index:02d}",
                (x, y_front - 0.43, clamp_index * floor_h - 0.32),
                (0.24, 0.08, 0.055),
                materials["metal"],
                visible,
                0.008,
            )

    for floor in range(1, floors):
        if (floor + balcony_phase) % 2 == 0:
            add_box(
                f"{prefix}_ShadowCourse_{floor:02d}",
                (center_x, y_front - 0.31, floor * floor_h + 0.38),
                (width - 0.85, 0.20, 0.16),
                accent_material,
                visible,
                0.018,
            )
        for bay_index in range(len(normalized)):
            if (floor * 3 + bay_index + balcony_phase) % 5 != 0:
                continue
            x = (boundaries[bay_index] + boundaries[bay_index + 1]) * 0.5
            z = floor * floor_h + 1.32
            add_box(
                f"{prefix}_AC_{floor:02d}_{bay_index:02d}_Body",
                (x, y_front - 0.44, z),
                (0.82, 0.34, 0.48),
                detail_material,
                visible,
                0.055,
            )
            for grille in (-0.25, -0.08, 0.08, 0.25):
                add_box(
                    f"{prefix}_AC_{floor:02d}_{bay_index:02d}_Grille_{grille:+.2f}",
                    (x + grille, y_front - 0.625, z),
                    (0.025, 0.018, 0.34),
                    materials["grime"],
                    visible,
                    0.002,
                )

    for bay_index in range(len(normalized)):
        if (bay_index + balcony_phase) % 2:
            continue
        x = (boundaries[bay_index] + boundaries[bay_index + 1]) * 0.5
        add_box(
            f"{prefix}_GroundAwning_{bay_index:02d}",
            (x, y_front - 0.92, 3.18),
            (max(1.4, normalized[bay_index] - 0.95), 1.34, 0.12),
            detail_material,
            visible,
            0.025,
        )
        add_box(
            f"{prefix}_GroundSign_{bay_index:02d}",
            (x, y_front - 0.34, 2.42),
            (max(1.1, normalized[bay_index] - 1.3), 0.11, 0.40),
            accent_material,
            visible,
            0.018,
        )

    roof_z = total_h + 1.38
    for vent_index in range(5 if prefix.endswith("A") else 7):
        angle = vent_index * 2.399963
        radius = 2.4 + (vent_index % 3) * 1.2
        add_cylinder(
            f"{prefix}_RoofVent_{vent_index:02d}",
            (center_x + math.cos(angle) * radius, y_front + depth * 0.55 + math.sin(angle) * radius, roof_z),
            0.22 + 0.035 * (vent_index % 2),
            1.15 + 0.18 * (vent_index % 3),
            materials["metal"],
            visible,
            24,
            bevel=0.025,
        )


def refined_add_vehicle(index, x, y, material, materials, visible):
    variants = (
        {"length": 4.55, "width": 1.86, "body_h": 0.68, "cabin_h": 1.12, "rear": 0.95},
        {"length": 4.82, "width": 1.92, "body_h": 0.72, "cabin_h": 1.05, "rear": 1.18},
        {"length": 5.12, "width": 1.98, "body_h": 0.84, "cabin_h": 1.30, "rear": 1.42},
    )
    spec = variants[index % len(variants)]
    road_z = 2.48
    body_z = road_z + 0.62
    length = spec["length"]
    width = spec["width"]
    add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_LowerBody", (x, y, body_z), (length, width, spec["body_h"]), material, visible, 0.24)
    add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_Rocker", (x, y, road_z + 0.34), (length - 0.18, width + 0.04, 0.20), materials["metal"], visible, 0.065)
    cabin_y = width * 0.43
    cabin_z0 = body_z + spec["body_h"] * 0.35
    cabin_z1 = cabin_z0 + spec["cabin_h"]
    front_x = x - length * 0.25
    rear_x = x + length * 0.28
    cabin_vertices = [
        (front_x - 0.32, y - cabin_y, cabin_z0), (rear_x + 0.28, y - cabin_y, cabin_z0),
        (rear_x - 0.12, y - cabin_y * 0.95, cabin_z1), (front_x + 0.28, y - cabin_y * 0.95, cabin_z1),
        (front_x - 0.32, y + cabin_y, cabin_z0), (rear_x + 0.28, y + cabin_y, cabin_z0),
        (rear_x - 0.12, y + cabin_y * 0.95, cabin_z1), (front_x + 0.28, y + cabin_y * 0.95, cabin_z1),
    ]
    cabin_faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (3, 2, 6, 7), (0, 3, 7, 4), (1, 5, 6, 2)]
    add_custom_mesh(f"SM_M01_PROOF01_Vehicle_{index:02d}_Cabin", cabin_vertices, cabin_faces, material, visible, 0.10)

    window_z = cabin_z0 + spec["cabin_h"] * 0.53
    for side_index, side in enumerate((-1.0, 1.0)):
        side_y = y + side * (cabin_y + 0.018)
        for pane_index, pane_x in enumerate((front_x + 0.38, rear_x - 0.28)):
            add_box(
                f"SM_M01_PROOF01_Vehicle_{index:02d}_SideWindow_{side_index}_{pane_index}",
                (pane_x, side_y, window_z),
                (1.02 if pane_index == 0 else 0.92, 0.035, spec["cabin_h"] * 0.60),
                materials["glass"],
                visible,
                0.025,
            )
        add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_Mirror_{side_index}", (front_x - 0.05, y + side * (width * 0.58), window_z - 0.15), (0.24, 0.20, 0.15), material, visible, 0.045)
        for seam_x in (x - 0.35, x + 1.02):
            add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_DoorSeam_{side_index}_{seam_x:+.2f}", (seam_x, side_y + side * 0.006, body_z + 0.13), (0.018, 0.018, 0.58), materials["grime"], visible, 0.002)

    add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_Windshield", (front_x - 0.26, y, window_z), (0.06, width * 0.78, spec["cabin_h"] * 0.62), materials["glass"], visible, 0.018)
    add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_RearGlass", (rear_x + 0.22, y, window_z), (0.055, width * 0.75, spec["cabin_h"] * 0.55), materials["glass"], visible, 0.018)
    add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_FrontBumper", (x - length * 0.51, y, road_z + 0.47), (0.16, width * 0.88, 0.24), materials["metal"], visible, 0.045)
    add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_RearBumper", (x + length * 0.51, y, road_z + 0.47), (0.16, width * 0.88, 0.24), materials["metal"], visible, 0.045)
    add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_Grille", (x - length * 0.516, y, road_z + 0.72), (0.035, width * 0.54, 0.26), materials["grime"], visible, 0.008)
    for lamp_index, side in enumerate((-1.0, 1.0)):
        add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_Headlamp_{lamp_index}", (x - length * 0.52, y + side * width * 0.31, road_z + 0.87), (0.045, 0.34, 0.19), materials["window"], visible, 0.018)
        add_box(f"SM_M01_PROOF01_Vehicle_{index:02d}_TailLamp_{lamp_index}", (x + length * 0.52, y + side * width * 0.32, road_z + 0.85), (0.045, 0.30, 0.20), materials["vehicle_red"], visible, 0.018)
    axle = length * 0.33
    for wheel_index, (dx, dy) in enumerate(((-axle, -width * 0.51), (-axle, width * 0.51), (axle, -width * 0.51), (axle, width * 0.51))):
        add_cylinder(f"SM_M01_PROOF01_Vehicle_{index:02d}_Wheel_{wheel_index:02d}", (x + dx, y + dy, road_z + 0.25), 0.40, 0.24, materials["rubber"], visible, 40, (math.radians(90.0), 0.0, 0.0), 0.028)
        add_cylinder(f"SM_M01_PROOF01_Vehicle_{index:02d}_Hub_{wheel_index:02d}", (x + dx, y + dy * 1.01, road_z + 0.25), 0.22, 0.255, materials["metal"], visible, 32, (math.radians(90.0), 0.0, 0.0), 0.022)


def refined_add_tree(index, x, y, height, materials, visible):
    base_z = 2.48
    trunk_top = base_z + height * 0.76
    add_cylinder(f"SM_M01_PROOF01_Tree_{index:02d}_Trunk", (x, y, base_z + height * 0.34), 0.19 + 0.012 * index, height * 0.68, materials["bark"], visible, 36, bevel=0.045)
    for branch_index in range(11):
        angle = branch_index * 2.399963 + index * 0.51
        level = 0.38 + (branch_index % 5) * 0.075
        reach = height * (0.12 + 0.018 * (branch_index % 4))
        start = (x, y, base_z + height * level)
        end = (x + math.cos(angle) * reach, y + math.sin(angle) * reach, base_z + height * (0.66 + 0.035 * (branch_index % 5)))
        cylinder_between(f"SM_M01_PROOF01_Tree_{index:02d}_Branch_{branch_index:02d}", start, end, 0.055 + 0.008 * (branch_index % 3), materials["bark"], visible)
    for crown_index in range(19):
        angle = crown_index * 2.399963 + index * 0.37
        ring = 0.20 + 0.045 * (crown_index % 5)
        radial = height * ring
        z_factor = 0.62 + 0.045 * (crown_index % 7)
        scale = 0.66 + 0.08 * ((crown_index * 3 + index) % 5)
        add_icosphere(
            f"SM_M01_PROOF01_Tree_{index:02d}_Crown_{crown_index:02d}",
            (x + math.cos(angle) * radial, y + math.sin(angle) * radial * 0.82, base_z + height * z_factor),
            height * 0.145,
            (0.90 * scale, 0.76 * scale, 1.18 * scale),
            materials["foliage" if (index + crown_index) % 3 else "foliage_light"],
            visible,
        )
    add_box(f"SM_M01_PROOF01_Tree_{index:02d}_Planter", (x, y, 2.62), (1.45, 1.45, 0.36), materials["concrete"], visible, 0.08)


def refined_build_shore_and_street(materials, visible, collision):
    ORIGINAL_BUILD_SHORE(materials, visible, collision)
    for rock_index in range(34):
        x = -42.0 + rock_index * (84.0 / 33.0)
        y = -4.55 + 0.42 * math.sin(rock_index * 1.73)
        radius = 0.20 + 0.065 * (rock_index % 4)
        add_icosphere(
            f"SM_M01_PROOF01_WaterlineRock_{rock_index:02d}",
            (x, y, 0.02 + radius * 0.40),
            radius,
            (1.35, 0.82, 0.66),
            materials["concrete" if rock_index % 3 else "grime"],
            visible,
        )
    for ladder_index, x in enumerate((-29.0, -3.0, 23.0)):
        for rail_side in (-0.34, 0.34):
            add_cylinder(f"SM_M01_PROOF01_SeawallLadder_{ladder_index}_Rail_{rail_side:+.2f}", (x + rail_side, 3.70, 1.18), 0.035, 2.15, materials["metal"], visible, 18, bevel=0.008)
        for rung in range(7):
            add_box(f"SM_M01_PROOF01_SeawallLadder_{ladder_index}_Rung_{rung:02d}", (x, 3.63, 0.35 + rung * 0.29), (0.72, 0.055, 0.055), materials["metal"], visible, 0.010)


def refined_configure_condition(scene, rig, condition, wet_controls, materials):
    background = scene.world.node_tree.nodes.get("Background")
    if background is None:
        raise RuntimeError("World background node missing")
    values = {
        "daylight": ((0.24, 0.38, 0.58, 1.0), 0.75, 4.2, 2600.0, 0.0, 0.0, 1.05),
        "wet_overcast": ((0.16, 0.20, 0.25, 1.0), 0.82, 1.65, 3800.0, 520.0, 260.0, 1.85),
        "night": ((0.012, 0.028, 0.070, 1.0), 0.58, 0.03, 680.0, 3600.0, 2400.0, 3.20),
    }
    color, strength, sun_energy, fill_energy, moon_energy, practical_energy, exposure = values[condition]
    background.inputs["Color"].default_value = color
    background.inputs["Strength"].default_value = strength
    rig["sun"].data.energy = sun_energy
    rig["fill"].data.energy = fill_energy
    rig["moon"].data.energy = moon_energy
    for light in rig["practicals"]:
        light.data.energy = practical_energy
        light.data.shadow_soft_size = 1.15
    scene.view_settings.exposure = exposure
    wet = condition == "wet_overcast"
    for control in wet_controls:
        control["color"].inputs[0].default_value = 0.36 if wet else 0.0
        control["roughness"].inputs[1].default_value = 0.27 if wet else 1.0
    window_bsdf = materials["window"].node_tree.nodes.get("Principled BSDF")
    if window_bsdf is not None and window_bsdf.inputs.get("Emission Strength") is not None:
        window_bsdf.inputs["Emission Strength"].default_value = 6.5 if condition == "night" else 0.55 if wet else 0.12


def refined_render_checkpoints(scene, rig, output, materials, wet_controls):
    cameras = {
        "route_composite": ((-42.0, -38.0, 18.5), (2.0, 22.0, 8.2), 52.0),
        "facade_close": ((-34.0, 8.5, 9.5), (-18.0, 31.0, 10.0), 58.0),
        "shoreline_close": ((31.0, 9.0, 8.2), (1.0, -12.0, -0.15), 50.0),
    }
    results = []
    render_dir = output / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    for condition in ("daylight", "wet_overcast", "night"):
        refined_configure_condition(scene, rig, condition, wet_controls, materials)
        for camera_id, (location, target, lens) in cameras.items():
            camera = rig["camera"]
            camera.location = location
            camera.data.lens = lens
            camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
            path = render_dir / f"{condition}_{camera_id}.png"
            scene.render.filepath = str(path)
            print(namespace["json"].dumps({"event": "render_start", "condition": condition, "camera": camera_id}), flush=True)
            bpy.ops.render.render(write_still=True)
            if not path.is_file() or path.stat().st_size <= 0:
                raise RuntimeError(f"Render missing: {path}")
            results.append({"condition": condition, "camera": camera_id, "path": str(path), "bytes": path.stat().st_size})
            print(namespace["json"].dumps({"event": "render_complete", "condition": condition, "camera": camera_id, "bytes": path.stat().st_size}), flush=True)
    if len(results) != 9:
        raise RuntimeError("Expected exactly nine governed renders")
    return results


namespace.update(
    {
        "build_building": refined_build_building,
        "add_vehicle": refined_add_vehicle,
        "add_tree": refined_add_tree,
        "build_shore_and_street": refined_build_shore_and_street,
        "configure_condition": refined_configure_condition,
        "render_checkpoints": refined_render_checkpoints,
    }
)

raise SystemExit(namespace["main"]())
