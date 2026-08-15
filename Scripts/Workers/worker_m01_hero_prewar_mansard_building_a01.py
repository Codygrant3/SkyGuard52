"""Build one authored Mission 1 prewar coastal hero building.

This is intentionally narrower than the rejected frontage-cell attempt.  It
authors one importable building with explicit facade construction, believable
opening ratios, recessed window assemblies, a composed ground floor and a
distinct mansard roof.  Unreal remains responsible for world assembly, water,
vegetation, atmosphere and final lighting.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.Workers import worker_m01_hero_coastal_frontage_cell01 as base


ASSET_ID = "m01-hero-prewar-mansard-building-a01"
GATE = "M01_HERO_PREWAR_MANSARD_BUILDING_A01"
CHECKPOINT_SIZE = (1280, 720)
RENDER_SIZE = (1920, 1080)
base.ASSET_ID = ASSET_ID


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", required=True)
    values = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    return parser.parse_args(values)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return base.sha256(path)


def box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    role: str,
    bevel: float = 0.035,
) -> bpy.types.Object:
    return base.add_box(
        name,
        location,
        dimensions,
        material,
        collection,
        role,
        bevel,
        "A_PREWAR_MANSARD_PRODUCTION",
    )


def cylinder(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    depth: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    role: str,
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    vertices: int = 24,
) -> bpy.types.Object:
    return base.add_cylinder(
        name,
        location,
        radius,
        depth,
        material,
        collection,
        role,
        rotation,
        vertices,
        "A_PREWAR_MANSARD_PRODUCTION",
    )


def build_materials() -> dict[str, bpy.types.Material]:
    materials = base.build_materials()
    for material in materials.values():
        material.name = material.name.replace("HeroFrontage", "HeroPrewarA01")
    materials.update(
        {
            "glass_cool": base.simple_material(
                "M_M01_HeroPrewarA01_GlassCool", (0.025, 0.055, 0.075, 1.0), 0.16, metallic=0.12
            ),
            "glass_warm": base.simple_material(
                "M_M01_HeroPrewarA01_GlassWarm", (0.32, 0.13, 0.035, 1.0), 0.22, emission=0.55
            ),
            "paint_green": base.simple_material(
                "M_M01_HeroPrewarA01_PaintedMetalGreen", (0.055, 0.12, 0.085, 1.0), 0.48, metallic=0.35
            ),
            "curtain_cream": base.simple_material(
                "M_M01_HeroPrewarA01_CurtainCream", (0.52, 0.39, 0.25, 1.0), 0.82
            ),
            "curtain_red": base.simple_material(
                "M_M01_HeroPrewarA01_CurtainRed", (0.25, 0.025, 0.018, 1.0), 0.76
            ),
            "grime": base.simple_material(
                "M_M01_HeroPrewarA01_SaltGrime", (0.085, 0.075, 0.060, 1.0), 0.92
            ),
            "brass": base.simple_material(
                "M_M01_HeroPrewarA01_Brass", (0.42, 0.24, 0.055, 1.0), 0.26, metallic=0.78
            ),
            "sign_cream": base.simple_material(
                "M_M01_HeroPrewarA01_SignCream", (0.68, 0.54, 0.31, 1.0), 0.62
            ),
        }
    )
    return materials


def add_arch_surround(
    name: str,
    center_x: float,
    front_y: float,
    spring_z: float,
    outer_radius: float,
    inner_radius: float,
    depth: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    segments = 24
    y0, y1 = front_y - depth * 0.5, front_y + depth * 0.5
    vertices: list[tuple[float, float, float]] = []
    for y in (y0, y1):
        for radius in (outer_radius, inner_radius):
            for index in range(segments + 1):
                angle = math.pi * index / segments
                vertices.append(
                    (
                        center_x + radius * math.cos(angle),
                        y,
                        spring_z + radius * math.sin(angle),
                    )
                )
    stride = segments + 1
    outer_front = 0
    inner_front = stride
    outer_back = stride * 2
    inner_back = stride * 3
    faces: list[tuple[int, ...]] = []
    for index in range(segments):
        of0, of1 = outer_front + index, outer_front + index + 1
        inf0, inf1 = inner_front + index, inner_front + index + 1
        ob0, ob1 = outer_back + index, outer_back + index + 1
        inb0, inb1 = inner_back + index, inner_back + index + 1
        faces.extend(
            [
                (of0, of1, inf1, inf0),
                (ob1, ob0, inb0, inb1),
                (of0, ob0, ob1, of1),
                (inf1, inb1, inb0, inf0),
            ]
        )
    faces.extend(
        [
            (outer_front, inner_front, inner_back, outer_back),
            (outer_front + segments, outer_back + segments, inner_back + segments, inner_front + segments),
        ]
    )
    return base.add_custom_mesh(
        name,
        vertices,
        faces,
        material,
        collection,
        "entrance_surround",
        "A_PREWAR_MANSARD_PRODUCTION",
    )


def add_window(
    prefix: str,
    x: float,
    z: float,
    width: float,
    height: float,
    materials: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
    warm: bool,
    curtain: str | None,
) -> None:
    front_y = 0.0
    box(prefix + "_Recess", (x, front_y + 0.18, z), (width + 0.30, 0.10, height + 0.28), materials["dark"], collection, "window_recess", 0.018)
    glass_material = materials["glass_warm"] if warm else materials["glass_cool"]
    box(prefix + "_Glass", (x, front_y + 0.115, z), (width, 0.035, height), glass_material, collection, "window_glazing", 0.008)
    if curtain:
        box(prefix + "_Curtain", (x + width * 0.25, front_y + 0.145, z), (width * 0.34, 0.018, height * 0.88), materials[curtain], collection, "window_interior", 0.005)
    frame = materials["paint_green"]
    jamb = 0.075
    box(prefix + "_FrameL", (x - width * 0.5, front_y + 0.065, z), (jamb, 0.10, height + 0.06), frame, collection, "window_frame", 0.012)
    box(prefix + "_FrameR", (x + width * 0.5, front_y + 0.065, z), (jamb, 0.10, height + 0.06), frame, collection, "window_frame", 0.012)
    box(prefix + "_FrameT", (x, front_y + 0.065, z + height * 0.5), (width + jamb, 0.10, jamb), frame, collection, "window_frame", 0.012)
    box(prefix + "_FrameB", (x, front_y + 0.065, z - height * 0.5), (width + jamb, 0.10, jamb), frame, collection, "window_frame", 0.012)
    box(prefix + "_MullionV", (x, front_y + 0.048, z), (0.055, 0.09, height), frame, collection, "window_frame", 0.009)
    box(prefix + "_MullionH", (x, front_y + 0.048, z + height * 0.12), (width, 0.09, 0.05), frame, collection, "window_frame", 0.009)
    box(prefix + "_Sill", (x, front_y - 0.07, z - height * 0.5 - 0.10), (width + 0.42, 0.36, 0.14), materials["stone"], collection, "facade_trim", 0.026)
    box(prefix + "_Lintel", (x, front_y + 0.01, z + height * 0.5 + 0.13), (width + 0.40, 0.25, 0.18), materials["plaster_cream"], collection, "facade_trim", 0.025)


def add_balcony(
    prefix: str,
    center_x: float,
    z: float,
    width: float,
    materials: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> None:
    box(prefix + "_Slab", (center_x, -0.72, z), (width, 1.55, 0.18), materials["stone"], collection, "balcony", 0.035)
    front_y = -1.48
    box(prefix + "_RailTop", (center_x, front_y, z + 1.08), (width - 0.18, 0.055, 0.065), materials["paint_green"], collection, "balcony_railing", 0.012)
    box(prefix + "_RailMid", (center_x, front_y, z + 0.50), (width - 0.18, 0.045, 0.045), materials["paint_green"], collection, "balcony_railing", 0.010)
    count = max(7, int(width / 0.34))
    for index in range(count):
        x = center_x - width * 0.46 + width * 0.92 * index / max(1, count - 1)
        cylinder(prefix + f"_Baluster_{index:02d}", (x, front_y, z + 0.54), 0.018, 1.02, materials["paint_green"], collection, "balcony_railing", vertices=12)
    for x in (center_x - width * 0.48, center_x + width * 0.48):
        cylinder(prefix + f"_EndPost_{x:+.2f}", (x, front_y, z + 0.56), 0.035, 1.10, materials["paint_green"], collection, "balcony_railing", vertices=16)


def build_building(
    materials: dict[str, bpy.types.Material],
    visible: bpy.types.Collection,
    collision: bpy.types.Collection,
) -> dict[str, Any]:
    prefix = "SM_M01_HeroPrewarA01"
    width, depth, floors, floor_h = 24.0, 14.0, 6, 3.2
    wall_height = floors * floor_h
    wall_depth = 0.44
    # Back, side and floor construction is explicit.  The facade is assembled
    # from spandrels and piers so the window recesses are real openings rather
    # than dark planes pasted over a full front slab.
    box(prefix + "_BackWall", (0.0, depth - 0.22, wall_height * 0.5), (width, wall_depth, wall_height), materials["plaster_warm"], visible, "primary_architecture", 0.06)
    box(prefix + "_SideWallL", (-width * 0.5 + 0.22, depth * 0.5, wall_height * 0.5), (wall_depth, depth, wall_height), materials["plaster_warm"], visible, "primary_architecture", 0.06)
    box(prefix + "_SideWallR", (width * 0.5 - 0.22, depth * 0.5, wall_height * 0.5), (wall_depth, depth, wall_height), materials["plaster_warm"], visible, "primary_architecture", 0.06)
    for floor in range(floors + 1):
        box(prefix + f"_Floor_{floor:02d}", (0.0, depth * 0.5, floor * floor_h + 0.10), (width - 0.42, depth - 0.42, 0.20), materials["concrete"], visible, "structural_floor", 0.024)

    bay_centers = (-9.0, -6.0, -3.0, 0.0, 3.0, 6.0, 9.0)
    pier_centers = (-10.5, -7.5, -4.5, -1.5, 1.5, 4.5, 7.5, 10.5)
    window_width, window_height = 1.46, 1.92
    for floor in range(1, floors):
        z0 = floor * floor_h
        box(prefix + f"_SpandrelLow_{floor:02d}", (0.0, 0.25, z0 + 0.43), (width, 0.50, 0.86), materials["plaster_warm"], visible, "facade_structure", 0.026)
        box(prefix + f"_SpandrelHigh_{floor:02d}", (0.0, 0.25, z0 + 2.83), (width, 0.50, 0.74), materials["plaster_warm"], visible, "facade_structure", 0.026)
        for pier_index, x in enumerate(pier_centers):
            mat = materials["plaster_cream"] if pier_index % 2 == 0 else materials["plaster_warm"]
            box(prefix + f"_Pier_{floor:02d}_{pier_index:02d}", (x, 0.25, z0 + 1.62), (1.40, 0.50, 2.34), mat, visible, "facade_structure", 0.032)
        for bay_index, x in enumerate(bay_centers):
            warm = (floor + bay_index) % 5 in {0, 2}
            curtain = "curtain_cream" if (floor + bay_index) % 4 == 0 else ("curtain_red" if (floor * 3 + bay_index) % 7 == 0 else None)
            add_window(prefix + f"_Window_{floor:02d}_{bay_index:02d}", x, z0 + 1.67, window_width, window_height, materials, visible, warm, curtain)

    # Ground floor: rusticated base, two storefronts and one authored arched entrance.
    box(prefix + "_GroundSpandrel", (0.0, 0.27, 0.40), (width, 0.54, 0.80), materials["stone"], visible, "facade_structure", 0.035)
    box(prefix + "_GroundHeader", (0.0, 0.27, 2.88), (width, 0.54, 0.64), materials["stone"], visible, "facade_structure", 0.035)
    for x in (-10.7, -7.1, -3.5, 3.5, 7.1, 10.7):
        box(prefix + f"_GroundPier_{x:+.1f}", (x, 0.27, 1.66), (0.70, 0.54, 2.04), materials["stone"], visible, "facade_structure", 0.04)
    for index, x in enumerate((-8.9, -5.3, 5.3, 8.9)):
        box(prefix + f"_StoreRecess_{index:02d}", (x, 0.20, 1.72), (2.45, 0.10, 2.15), materials["dark"], visible, "storefront_recess", 0.02)
        box(prefix + f"_StoreGlass_{index:02d}", (x, 0.13, 1.72), (2.12, 0.035, 1.87), materials["glass_warm"] if index in {1, 2} else materials["glass_cool"], visible, "storefront", 0.012)
        box(prefix + f"_StoreMullion_{index:02d}", (x, 0.07, 1.72), (0.065, 0.09, 1.90), materials["paint_green"], visible, "window_frame", 0.01)
        box(prefix + f"_Awning_{index:02d}", (x, -0.64, 2.73), (2.78, 1.36, 0.16), materials["paint_green"], visible, "canopy", 0.035)

    entrance_x = 0.0
    box(prefix + "_EntranceRecess", (entrance_x, 0.22, 1.55), (2.35, 0.12, 2.70), materials["dark"], visible, "entrance_recess", 0.025)
    box(prefix + "_DoorL", (-0.56, 0.10, 1.37), (1.02, 0.08, 2.35), materials["wood"], visible, "entrance", 0.025)
    box(prefix + "_DoorR", (0.56, 0.10, 1.37), (1.02, 0.08, 2.35), materials["wood"], visible, "entrance", 0.025)
    box(prefix + "_DoorGlassL", (-0.56, 0.045, 1.72), (0.62, 0.035, 1.10), materials["glass_warm"], visible, "entrance_glazing", 0.008)
    box(prefix + "_DoorGlassR", (0.56, 0.045, 1.72), (0.62, 0.035, 1.10), materials["glass_warm"], visible, "entrance_glazing", 0.008)
    cylinder(prefix + "_DoorHandleL", (-0.16, -0.015, 1.36), 0.035, 0.18, materials["brass"], visible, "entrance_hardware", (math.pi / 2, 0.0, 0.0), 16)
    cylinder(prefix + "_DoorHandleR", (0.16, -0.015, 1.36), 0.035, 0.18, materials["brass"], visible, "entrance_hardware", (math.pi / 2, 0.0, 0.0), 16)
    add_arch_surround(prefix + "_EntranceArch", entrance_x, -0.03, 2.35, 1.40, 1.12, 0.30, materials["plaster_cream"], visible)
    box(prefix + "_EntranceColumnL", (-1.26, -0.03, 1.20), (0.28, 0.30, 2.40), materials["plaster_cream"], visible, "entrance_surround", 0.026)
    box(prefix + "_EntranceColumnR", (1.26, -0.03, 1.20), (0.28, 0.30, 2.40), materials["plaster_cream"], visible, "entrance_surround", 0.026)

    # Two deliberate balconies, not a repeated strip across every bay.
    add_balcony(prefix + "_BalconyLower", 0.0, floor_h * 2 + 0.50, 8.4, materials, visible)
    add_balcony(prefix + "_BalconyUpper", -6.0, floor_h * 4 + 0.50, 5.4, materials, visible)

    # Cornices, rustication, rainwater goods and salt/water staining.
    box(prefix + "_BaseCourse", (0.0, -0.06, 0.26), (width + 0.30, 0.36, 0.52), materials["stone"], visible, "facade_trim", 0.035)
    for floor in range(1, floors):
        box(prefix + f"_StringCourse_{floor:02d}", (0.0, -0.055, floor * floor_h + 0.18), (width + 0.26, 0.34, 0.17), materials["plaster_cream"], visible, "facade_trim", 0.026)
    box(prefix + "_MainCornice", (0.0, -0.16, wall_height + 0.22), (width + 0.80, 0.72, 0.48), materials["plaster_cream"], visible, "roofline", 0.055)
    for x in (-11.15, 11.15):
        cylinder(prefix + f"_Downpipe_{x:+.2f}", (x, -0.18, wall_height * 0.47), 0.07, wall_height * 0.91, materials["metal"], visible, "drainage", vertices=20)
        cylinder(prefix + f"_GutterDrop_{x:+.2f}", (x, -0.18, 0.42), 0.10, 0.42, materials["metal"], visible, "drainage", (0.0, math.pi / 2, 0.0), 20)
    box(prefix + "_LowerGrimeBand", (0.0, -0.205, 0.72), (width - 0.4, 0.028, 0.42), materials["grime"], visible, "weathering", 0.004)
    for index, x in enumerate((-9.1, -4.4, 2.9, 8.2)):
        box(prefix + f"_RepairPatch_{index:02d}", (x, -0.018, 7.1 + (index % 2) * 5.7), (1.05 + index * 0.12, 0.025, 0.58), materials["plaster_cool"], visible, "weathering", 0.008)

    # Authored mansard roof with dormers, gutters and chimneys.
    x0, x1, y0, y1 = -width * 0.5, width * 0.5, 0.0, depth
    ridge_y, roof_z, ridge_z = depth * 0.56, wall_height, wall_height + 4.2
    vertices = [(x0, y0, roof_z), (x1, y0, roof_z), (x0, y1, roof_z), (x1, y1, roof_z), (x0, ridge_y, ridge_z), (x1, ridge_y, ridge_z)]
    faces = [(0, 1, 5, 4), (2, 4, 5, 3), (0, 4, 2), (1, 3, 5), (0, 2, 3, 1)]
    base.add_custom_mesh(prefix + "_MansardRoof", vertices, faces, materials["roof"], visible, "roofline", "A_PREWAR_MANSARD_PRODUCTION")
    cylinder(prefix + "_FrontGutter", (0.0, -0.28, wall_height + 0.36), 0.10, width + 0.60, materials["metal"], visible, "drainage", (0.0, math.pi / 2, 0.0), 24)
    for dormer_index, x in enumerate((-8.2, -4.1, 0.0, 4.1, 8.2)):
        box(prefix + f"_DormerBody_{dormer_index:02d}", (x, 1.56, wall_height + 1.52), (2.15, 2.35, 2.35), materials["plaster_cream"], visible, "roof_detail", 0.055)
        add_window(prefix + f"_DormerWindow_{dormer_index:02d}", x, wall_height + 1.50, 1.10, 1.25, materials, visible, dormer_index in {1, 4}, None)
        roof_vertices = [
            (x - 1.30, 0.20, wall_height + 2.62),
            (x + 1.30, 0.20, wall_height + 2.62),
            (x - 1.30, 2.86, wall_height + 2.62),
            (x + 1.30, 2.86, wall_height + 2.62),
            (x, 1.55, wall_height + 3.42),
        ]
        roof_faces = [(0, 1, 4), (1, 3, 4), (3, 2, 4), (2, 0, 4), (0, 2, 3, 1)]
        base.add_custom_mesh(prefix + f"_DormerRoof_{dormer_index:02d}", roof_vertices, roof_faces, materials["roof"], visible, "roof_detail", "A_PREWAR_MANSARD_PRODUCTION")
    for chimney_index, x in enumerate((-7.0, 7.2)):
        box(prefix + f"_Chimney_{chimney_index:02d}", (x, ridge_y + 1.0, ridge_z + 0.72), (1.05, 1.05, 1.45), materials["stone"], visible, "roof_detail", 0.055)
        box(prefix + f"_ChimneyCap_{chimney_index:02d}", (x, ridge_y + 1.0, ridge_z + 1.48), (1.30, 1.30, 0.16), materials["stone"], visible, "roof_detail", 0.035)

    # Bounded immediate streetscape context.
    box(prefix + "_Sidewalk", (0.0, -3.0, 0.16), (30.0, 5.8, 0.32), materials["concrete"], visible, "hardscape", 0.07)
    box(prefix + "_Curb", (0.0, -5.85, 0.27), (30.0, 0.30, 0.54), materials["stone"], visible, "hardscape", 0.035)
    for drain_index, x in enumerate((-10.0, 0.0, 10.0)):
        box(prefix + f"_Drain_{drain_index:02d}", (x, -6.03, 0.43), (1.20, 0.44, 0.08), materials["metal"], visible, "drainage", 0.012)
    for planter_index, x in enumerate((-8.2, 7.8)):
        box(prefix + f"_Planter_{planter_index:02d}", (x, -3.20, 0.54), (1.25, 1.25, 0.82), materials["stone"], visible, "street_furniture", 0.06)
        box(prefix + f"_PlanterSoil_{planter_index:02d}", (x, -3.20, 0.94), (1.05, 1.05, 0.07), materials["grime"], visible, "street_furniture", 0.015)
    box(prefix + "_UtilityCabinet", (10.3, -1.20, 1.05), (1.05, 0.52, 1.85), materials["paint_green"], visible, "street_furniture", 0.055)
    box(prefix + "_AddressPlaque", (1.82, -0.21, 2.18), (0.52, 0.05, 0.36), materials["sign_blue"], visible, "signage", 0.018)
    box(prefix + "_ShopSign", (-7.1, -0.30, 3.02), (4.0, 0.20, 0.72), materials["sign_cream"], visible, "signage", 0.025)
    cylinder(prefix + "_LampPole", (9.8, -4.35, 3.55), 0.095, 7.10, materials["metal"], visible, "street_furniture", vertices=24)
    box(prefix + "_LampArm", (10.35, -4.35, 6.92), (1.20, 0.10, 0.10), materials["metal"], visible, "street_furniture", 0.02)
    box(prefix + "_LampHead", (10.88, -4.35, 6.78), (0.50, 0.30, 0.19), materials["lamp"], visible, "street_furniture", 0.04)

    # Simple collision is intentionally separate from rendered construction.
    box("UCX_SM_M01_HeroPrewarA01_Body_00", (0.0, depth * 0.5, wall_height * 0.5), (width, depth, wall_height), materials["dark"], collision, "unreal_collision", 0.0)
    box("UCX_SM_M01_HeroPrewarA01_Roof_00", (0.0, depth * 0.55, wall_height + 2.1), (width, depth * 0.9, 4.2), materials["dark"], collision, "unreal_collision", 0.0)
    return {
        "signature": "A_PREWAR_MANSARD_PRODUCTION",
        "width_m": width,
        "depth_m": depth,
        "wall_height_m": wall_height,
        "total_height_m": ridge_z + 1.6,
        "floors": floors,
        "window_width_m": window_width,
        "window_height_m": window_height,
        "bay_pitch_m": 3.0,
        "window_to_bay_ratio": round(window_width / 3.0, 4),
        "actual_open_facade_construction": True,
    }


def configure_scene(scene: bpy.types.Scene) -> None:
    base.configure_scene(scene)
    scene.view_settings.exposure = 0.82
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.19, 0.27, 0.38, 1.0)
    background.inputs["Strength"].default_value = 0.86


def setup_review(scene: bpy.types.Scene, review: bpy.types.Collection, materials: dict[str, bpy.types.Material]) -> dict[str, bpy.types.Object]:
    rig = base.setup_review(scene, review)
    rig["sun"].data.energy = 2.8
    rig["fill"].data.energy = 3200.0
    rig["fill"].data.size = 38.0
    rim_data = bpy.data.lights.new("REVIEW_Rim", type="AREA")
    rim_data.energy = 1700.0
    rim_data.shape = "RECTANGLE"
    rim_data.size = 22.0
    rim_data.size_y = 16.0
    rim = bpy.data.objects.new("REVIEW_Rim", rim_data)
    rim.location = (-16.0, 8.0, 20.0)
    rim.rotation_euler = (math.radians(44.0), 0.0, math.radians(145.0))
    review.objects.link(rim)
    street_data = bpy.data.lights.new("REVIEW_StreetPool", type="AREA")
    street_data.energy = 0.0
    street_data.color = (1.0, 0.48, 0.18)
    street_data.shape = "RECTANGLE"
    street_data.size = 9.0
    street_data.size_y = 5.0
    street = bpy.data.objects.new("REVIEW_StreetPool", street_data)
    street.location = (2.0, -8.0, 9.0)
    street.rotation_euler = (math.radians(32.0), 0.0, 0.0)
    review.objects.link(street)
    rig.update({"rim": rim, "street": street})
    box("REVIEW_Road", (0.0, -11.0, -0.04), (42.0, 10.0, 0.20), materials["asphalt"], review, "review_only", 0.035)
    box("REVIEW_BackLot", (0.0, 14.0, -0.12), (42.0, 18.0, 0.18), materials["concrete"], review, "review_only", 0.025)
    return rig


def set_condition(scene: bpy.types.Scene, rig: dict[str, bpy.types.Object], condition: str) -> None:
    background = scene.world.node_tree.nodes.get("Background")
    if condition == "daylight":
        rig["sun"].data.energy = 3.0
        rig["fill"].data.energy = 3300.0
        rig["rim"].data.energy = 1550.0
        rig["street"].data.energy = 0.0
        background.inputs["Color"].default_value = (0.22, 0.33, 0.49, 1.0)
        background.inputs["Strength"].default_value = 0.92
        scene.view_settings.exposure = 0.82
    elif condition == "overcast":
        rig["sun"].data.energy = 0.75
        rig["fill"].data.energy = 3900.0
        rig["rim"].data.energy = 850.0
        rig["street"].data.energy = 0.0
        background.inputs["Color"].default_value = (0.32, 0.35, 0.40, 1.0)
        background.inputs["Strength"].default_value = 1.05
        scene.view_settings.exposure = 1.0
    elif condition == "wet":
        rig["sun"].data.energy = 1.2
        rig["fill"].data.energy = 3600.0
        rig["rim"].data.energy = 950.0
        rig["street"].data.energy = 350.0
        background.inputs["Color"].default_value = (0.18, 0.25, 0.34, 1.0)
        background.inputs["Strength"].default_value = 0.92
        scene.view_settings.exposure = 1.02
    else:
        rig["sun"].data.energy = 0.10
        rig["fill"].data.energy = 3100.0
        rig["rim"].data.energy = 1200.0
        rig["street"].data.energy = 2400.0
        background.inputs["Color"].default_value = (0.025, 0.045, 0.085, 1.0)
        background.inputs["Strength"].default_value = 0.68
        scene.view_settings.exposure = 1.55


def render_reviews(scene: bpy.types.Scene, rig: dict[str, bpy.types.Object], output: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    checkpoints_dir, renders_dir = output / "checkpoints", output / "renders"
    checkpoints_dir.mkdir()
    renders_dir.mkdir()
    camera = rig["camera"]
    checkpoint_specs = [
        ("daylight", "checkpoint_01_silhouette", (0.0, -57.0, 19.0), (0.0, 4.0, 10.7), 55.0),
        ("daylight", "checkpoint_02_facade_system", (-4.2, -27.0, 9.5), (-2.0, 0.2, 9.5), 58.0),
        ("night", "checkpoint_03_night_readability", (3.0, -47.0, 13.0), (0.0, 1.0, 9.8), 56.0),
    ]
    checkpoints = []
    for condition, name, location, target, lens in checkpoint_specs:
        set_condition(scene, rig, condition)
        checkpoints.append(base.render_one(scene, camera, checkpoints_dir / f"{name}.png", location, target, lens, CHECKPOINT_SIZE))
    final_specs = [
        ("daylight", "01_overall", (0.0, -56.0, 20.0), (0.0, 4.0, 10.5), 55.0),
        ("daylight", "02_facade_oblique", (-18.0, -33.0, 12.0), (-1.0, 2.0, 9.0), 54.0),
        ("daylight", "03_entrance_storefront", (0.0, -18.0, 3.2), (0.0, 0.0, 2.0), 56.0),
        ("daylight", "04_balcony_windows", (-3.0, -20.0, 10.5), (-2.0, 0.0, 10.0), 62.0),
        ("daylight", "05_roof_dormers", (4.0, -31.0, 23.0), (0.0, 2.0, 20.2), 58.0),
        ("overcast", "06_reargunner_height", (14.0, -48.0, 17.0), (0.0, 2.0, 10.0), 56.0),
        ("wet", "07_street_oblique", (-18.0, -28.0, 5.0), (-1.5, -1.0, 4.0), 53.0),
        ("night", "08_frontage_readability", (2.0, -45.0, 12.0), (0.0, 1.5, 9.6), 56.0),
    ]
    finals = []
    for condition, name, location, target, lens in final_specs:
        set_condition(scene, rig, condition)
        record = base.render_one(scene, camera, renders_dir / f"{condition}_{name}.png", location, target, lens, RENDER_SIZE)
        record.update({"condition": condition, "camera": name})
        finals.append(record)
    return checkpoints, finals


def object_receipt(collections: Iterable[bpy.types.Collection]) -> dict[str, Any]:
    receipt = base.object_receipt(collections)
    receipt["schema"] = "skyguard.m01-hero-prewar-mansard-building-a01.topology-material.v1"
    roles: dict[str, int] = {}
    for record in receipt["objects"]:
        role = str(record.get("role") or "unclassified")
        roles[role] = roles.get(role, 0) + 1
    receipt["role_counts"] = dict(sorted(roles.items()))
    receipt["passed"] = True
    return receipt


def main() -> int:
    args = parse_args()
    require(args.asset_id == ASSET_ID, f"Unexpected asset id: {args.asset_id}")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    require(not any(output.iterdir()), f"Output directory is not empty: {output}")
    require(base.PROVENANCE.is_file(), "Texture provenance manifest is missing")
    for family in base.PBR_SOURCES.values():
        for source in family.values():
            require(source.is_file(), f"Texture authority missing: {source}")

    base.clear_scene()
    scene = bpy.context.scene
    configure_scene(scene)
    visible = base.get_collection("M01_HERO_PREWAR_A01_VISIBLE")
    collision = base.get_collection("M01_HERO_PREWAR_A01_COLLISION")
    sockets = base.get_collection("M01_HERO_PREWAR_A01_SOCKETS")
    review = base.get_collection("M01_HERO_PREWAR_A01_REVIEW_ONLY")
    materials = build_materials()
    design = build_building(materials, visible, collision)
    base.add_empty("SOCKET_M01_HeroPrewarA01_Origin", (0.0, 0.0, 0.0), sockets, "unreal_socket")
    base.add_empty("SOCKET_M01_HeroPrewarA01_Entrance", (0.0, -0.25, 0.0), sockets, "unreal_socket")
    base.add_empty("SOCKET_M01_HeroPrewarA01_Roof", (0.0, 7.5, 23.0), sockets, "unreal_socket")
    base.add_empty("SOCKET_M01_HeroPrewarA01_StreetLamp", (9.8, -4.35, 0.0), sockets, "unreal_socket")
    rig = setup_review(scene, review, materials)

    topology = object_receipt((visible, collision, sockets))
    require(topology["mesh_object_count"] >= 300, f"Insufficient authored object count: {topology['mesh_object_count']}")
    require(topology["renderable_vertex_count"] >= 12000, f"Insufficient authored topology: {topology['renderable_vertex_count']}")
    require(topology["all_renderable_meshes_have_uv0"], "Renderable UV0 coverage failed")
    require(topology["distinct_building_signatures"] == ["A_PREWAR_MANSARD_PRODUCTION"], "Unexpected building signature set")
    require(topology["distinct_material_count"] >= 14, "Material diversity is below the hero-building floor")
    require(topology["role_counts"].get("window_frame", 0) >= 140, "Window-frame construction is incomplete")
    require(topology["role_counts"].get("facade_structure", 0) >= 55, "Facade construction is incomplete")

    checkpoints, renders = render_reviews(scene, rig, output)
    blend_path = output / "M01_Hero_Prewar_Mansard_Building_A01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    glb_path = output / "M01_Hero_Prewar_Mansard_Building_A01.glb"
    base.export_glb(glb_path, (visible, collision, sockets))
    write_json(output / "topology_material_receipt.json", topology)
    write_json(
        output / "design_contract_receipt.json",
        {
            "schema": "skyguard.m01-hero-prewar-mansard-building-a01.design-contract.v1",
            "asset_id": ASSET_ID,
            "fresh_asset_specific_geometry": True,
            "whole_scene_generator": False,
            "external_models": False,
            "generated_substitutes": False,
            "governed_local_pbr": True,
            "single_hero_building_scope": True,
            "actual_open_facade_construction": True,
            "design": design,
            "coordinate_contract": {"units": "meters", "forward": "+X", "up": "+Z"},
            "unreal_owns": ["world_assembly", "water", "shoreline", "vegetation", "atmosphere", "final_lighting"],
            "unreal_import_authorized": False,
            "passed": True,
        },
    )
    write_json(
        output / "artifact_receipt.json",
        {
            "schema": "skyguard.m01-hero-prewar-mansard-building-a01.artifacts.v1",
            "asset_id": ASSET_ID,
            "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size, "sha256": sha256(blend_path)},
            "glb": {"path": str(glb_path), "bytes": glb_path.stat().st_size, "sha256": sha256(glb_path)},
            "checkpoint_count": len(checkpoints),
            "final_render_count": len(renders),
            "total_render_count": len(checkpoints) + len(renders),
            "checkpoint_dimensions": list(CHECKPOINT_SIZE),
            "final_render_dimensions": list(RENDER_SIZE),
            "direct_full_resolution_review_required": True,
            "unreal_import_authorized": False,
            "passed": True,
        },
    )
    print(json.dumps({"gate": GATE, "classification": "PASSED_AUTOMATIC_AWAITING_POSTFLIGHT_AND_DIRECT_VISUAL_REVIEW", "topology": topology}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
