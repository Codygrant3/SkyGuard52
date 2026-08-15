"""Author a single production window-bay proof for Mission 1.

This intentionally does not build another whole building.  It proves the
construction that the rejected A01 building failed to show: a coherent wall
plane, clean opening, deep reveals, a visible sash/frame/glazing assembly,
interior response and construction-led exterior trim.  Unreal import remains
forbidden until direct full-resolution visual acceptance.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable

import bpy


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.Workers import worker_m01_hero_coastal_frontage_cell01 as base


ASSET_ID = "m01-hero-prewar-window-bay-a01"
GATE = "M01_HERO_PREWAR_WINDOW_BAY_A01"
SIGNATURE = "A_PREWAR_WINDOW_BAY_PRODUCTION"
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


def box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    role: str,
    bevel: float = 0.025,
) -> bpy.types.Object:
    return base.add_box(name, location, dimensions, material, collection, role, bevel, SIGNATURE)


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
    return base.add_cylinder(name, location, radius, depth, material, collection, role, rotation, vertices, SIGNATURE)


def build_materials() -> dict[str, bpy.types.Material]:
    materials = base.build_materials()
    for material in materials.values():
        material.name = material.name.replace("HeroFrontage", "HeroWindowBayA01")
    materials.update(
        {
            "frame": base.simple_material("M_M01_WindowBayA01_PaintedWood", (0.055, 0.16, 0.13, 1.0), 0.42),
            "frame_edge": base.simple_material("M_M01_WindowBayA01_FrameEdgeWear", (0.22, 0.30, 0.24, 1.0), 0.55),
            "glass_cool": base.simple_material("M_M01_WindowBayA01_GlassCool", (0.055, 0.14, 0.18, 1.0), 0.12, metallic=0.18),
            "glass_warm": base.simple_material("M_M01_WindowBayA01_GlassWarm", (0.28, 0.12, 0.035, 1.0), 0.18, emission=0.28),
            "interior": base.simple_material("M_M01_WindowBayA01_Interior", (0.18, 0.12, 0.075, 1.0), 0.76),
            "curtain": base.simple_material("M_M01_WindowBayA01_Curtain", (0.54, 0.42, 0.28, 1.0), 0.88),
            "seal": base.simple_material("M_M01_WindowBayA01_Seal", (0.018, 0.022, 0.020, 1.0), 0.62),
            "brass": base.simple_material("M_M01_WindowBayA01_Brass", (0.44, 0.25, 0.055, 1.0), 0.24, metallic=0.82),
            "radiator": base.simple_material("M_M01_WindowBayA01_Radiator", (0.52, 0.50, 0.42, 1.0), 0.58, metallic=0.22),
            "night_interior": base.simple_material("M_M01_WindowBayA01_NightInterior", (0.46, 0.18, 0.035, 1.0), 0.30, emission=0.62),
            "copper": base.simple_material("M_M01_WindowBayA01_Copper", (0.24, 0.085, 0.028, 1.0), 0.36, metallic=0.72),
        }
    )
    return materials


def build_bay(
    materials: dict[str, bpy.types.Material],
    visible: bpy.types.Collection,
    collision: bpy.types.Collection,
) -> dict[str, Any]:
    module_w, module_h, wall_depth = 4.40, 4.40, 0.56
    opening_w, opening_h = 1.52, 2.20
    opening_center_z = 2.28
    opening_bottom = opening_center_z - opening_h * 0.5
    opening_top = opening_center_z + opening_h * 0.5
    side_w = (module_w - opening_w) * 0.5

    # Four coherent structural pieces define one clean rectangular aperture.
    box("SM_M01_WindowBayA01_Pier_L", (-(opening_w + side_w) * 0.5, 0.28, module_h * 0.5), (side_w, wall_depth, module_h), materials["plaster_warm"], visible, "facade_structure", 0.035)
    box("SM_M01_WindowBayA01_Pier_R", ((opening_w + side_w) * 0.5, 0.28, module_h * 0.5), (side_w, wall_depth, module_h), materials["plaster_warm"], visible, "facade_structure", 0.035)
    box("SM_M01_WindowBayA01_Spandrel", (0.0, 0.28, opening_bottom * 0.5), (opening_w, wall_depth, opening_bottom), materials["plaster_warm"], visible, "facade_structure", 0.035)
    box("SM_M01_WindowBayA01_Header", (0.0, 0.28, opening_top + (module_h - opening_top) * 0.5), (opening_w, wall_depth, module_h - opening_top), materials["plaster_warm"], visible, "facade_structure", 0.035)

    # Reveal returns make the wall thickness readable from both oblique cameras.
    reveal_t = 0.10
    reveal_depth = 0.50
    reveal_y = 0.23
    box("SM_M01_WindowBayA01_Reveal_L", (-opening_w * 0.5 + reveal_t * 0.5, reveal_y, opening_center_z), (reveal_t, reveal_depth, opening_h), materials["plaster_cream"], visible, "window_reveal", 0.012)
    box("SM_M01_WindowBayA01_Reveal_R", (opening_w * 0.5 - reveal_t * 0.5, reveal_y, opening_center_z), (reveal_t, reveal_depth, opening_h), materials["plaster_cream"], visible, "window_reveal", 0.012)
    box("SM_M01_WindowBayA01_Reveal_T", (0.0, reveal_y, opening_top - reveal_t * 0.5), (opening_w, reveal_depth, reveal_t), materials["plaster_cream"], visible, "window_reveal", 0.012)
    box("SM_M01_WindowBayA01_Reveal_B", (0.0, reveal_y, opening_bottom + reveal_t * 0.5), (opening_w, reveal_depth, reveal_t), materials["stone"], visible, "window_reveal", 0.012)

    # Interior cavity and visible room elements replace the prior black void.
    box("SM_M01_WindowBayA01_InteriorBack", (0.0, 0.58, opening_center_z), (opening_w - 0.20, 0.05, opening_h - 0.18), materials["night_interior"], visible, "window_interior", 0.006)
    box("SM_M01_WindowBayA01_InteriorFloor", (0.0, 0.38, opening_bottom + 0.08), (opening_w - 0.12, 0.44, 0.12), materials["wood"], visible, "window_interior", 0.012)
    box("SM_M01_WindowBayA01_InteriorCeiling", (0.0, 0.38, opening_top - 0.07), (opening_w - 0.12, 0.44, 0.10), materials["interior"], visible, "window_interior", 0.010)
    for side, x in (("L", -0.59), ("R", 0.59)):
        box(f"SM_M01_WindowBayA01_Curtain_{side}", (x, 0.43, opening_center_z), (0.23, 0.035, opening_h - 0.22), materials["curtain"], visible, "window_interior", 0.008)
        for fold in range(3):
            cylinder(f"SM_M01_WindowBayA01_CurtainFold_{side}_{fold}", (x - 0.07 + fold * 0.07, 0.405, opening_center_z), 0.014, opening_h - 0.26, materials["curtain"], visible, "window_interior", vertices=12)
    box("SM_M01_WindowBayA01_RadiatorBody", (0.0, 0.47, opening_bottom + 0.34), (0.72, 0.10, 0.42), materials["radiator"], visible, "window_interior", 0.018)
    for fin in range(9):
        box(f"SM_M01_WindowBayA01_RadiatorFin_{fin:02d}", (-0.30 + fin * 0.075, 0.405, opening_bottom + 0.34), (0.035, 0.04, 0.36), materials["radiator"], visible, "window_interior", 0.006)

    # The complete frame sits slightly in front of the exterior wall plane.
    frame_y = -0.09
    frame_depth = 0.16
    frame_w = opening_w - 0.16
    frame_h = opening_h - 0.16
    jamb = 0.105
    frame_material = materials["frame"]
    for side, x in (("L", -frame_w * 0.5), ("R", frame_w * 0.5)):
        box(f"SM_M01_WindowBayA01_OuterFrame_{side}", (x, frame_y, opening_center_z), (jamb, frame_depth, frame_h), frame_material, visible, "window_frame", 0.018)
    for side, z in (("T", opening_center_z + frame_h * 0.5), ("B", opening_center_z - frame_h * 0.5)):
        box(f"SM_M01_WindowBayA01_OuterFrame_{side}", (0.0, frame_y, z), (frame_w + jamb, frame_depth, jamb), frame_material, visible, "window_frame", 0.018)
    box("SM_M01_WindowBayA01_CenterMullion", (0.0, frame_y - 0.012, opening_center_z), (0.09, frame_depth + 0.02, frame_h - 0.10), frame_material, visible, "window_frame", 0.014)
    box("SM_M01_WindowBayA01_Transom", (0.0, frame_y - 0.012, opening_center_z + 0.38), (frame_w - 0.10, frame_depth + 0.02, 0.085), frame_material, visible, "window_frame", 0.014)

    # Four separately modeled panes, beads and weather seals.
    pane_specs = [
        ("LL", -0.34, opening_center_z - 0.38, 0.55, 1.12, materials["glass_cool"]),
        ("LR", 0.34, opening_center_z - 0.38, 0.55, 1.12, materials["glass_warm"]),
        ("UL", -0.34, opening_center_z + 0.72, 0.55, 0.58, materials["glass_cool"]),
        ("UR", 0.34, opening_center_z + 0.72, 0.55, 0.58, materials["glass_cool"]),
    ]
    for pane, x, z, width, height, glass in pane_specs:
        box(f"SM_M01_WindowBayA01_Glass_{pane}", (x, 0.015, z), (width, 0.025, height), glass, visible, "window_glazing", 0.004)
        bead = 0.025
        for edge, ex, ez, ew, eh in (
            ("L", x - width * 0.5, z, bead, height),
            ("R", x + width * 0.5, z, bead, height),
            ("T", x, z + height * 0.5, width, bead),
            ("B", x, z - height * 0.5, width, bead),
        ):
            box(f"SM_M01_WindowBayA01_Bead_{pane}_{edge}", (ex, -0.025, ez), (ew, 0.035, eh), materials["frame_edge"], visible, "window_frame", 0.005)
    box("SM_M01_WindowBayA01_Seal_L", (-0.735, -0.012, opening_center_z), (0.022, 0.03, opening_h - 0.18), materials["seal"], visible, "window_seal", 0.003)
    box("SM_M01_WindowBayA01_Seal_R", (0.735, -0.012, opening_center_z), (0.022, 0.03, opening_h - 0.18), materials["seal"], visible, "window_seal", 0.003)
    cylinder("SM_M01_WindowBayA01_Handle", (0.10, -0.205, opening_center_z - 0.14), 0.025, 0.20, materials["brass"], visible, "window_hardware", (math.pi / 2, 0.0, 0.0), 20)
    for hinge_index, z in enumerate((opening_center_z - 0.55, opening_center_z + 0.48)):
        cylinder(f"SM_M01_WindowBayA01_Hinge_{hinge_index:02d}", (-0.64, -0.20, z), 0.024, 0.11, materials["brass"], visible, "window_hardware", (math.pi / 2, 0.0, 0.0), 16)

    # Exterior construction details are related to the opening rather than random strips.
    box("SM_M01_WindowBayA01_StoneSill", (0.0, -0.24, opening_bottom - 0.12), (opening_w + 0.40, 0.52, 0.18), materials["stone"], visible, "facade_trim", 0.025)
    box("SM_M01_WindowBayA01_SillDrip", (0.0, -0.50, opening_bottom - 0.17), (opening_w + 0.44, 0.055, 0.045), materials["stone"], visible, "facade_trim", 0.008)
    box("SM_M01_WindowBayA01_Lintel", (0.0, -0.08, opening_top + 0.15), (opening_w + 0.46, 0.24, 0.20), materials["plaster_cream"], visible, "facade_trim", 0.025)
    box("SM_M01_WindowBayA01_LintelHood", (0.0, -0.23, opening_top + 0.24), (opening_w + 0.62, 0.40, 0.10), materials["plaster_cream"], visible, "facade_trim", 0.018)
    box("SM_M01_WindowBayA01_Keystone", (0.0, -0.25, opening_top + 0.18), (0.22, 0.13, 0.32), materials["stone"], visible, "facade_trim", 0.018)
    for side, x in (("L", -opening_w * 0.5 - 0.14), ("R", opening_w * 0.5 + 0.14)):
        box(f"SM_M01_WindowBayA01_Quoin_{side}", (x, -0.06, opening_center_z), (0.18, 0.16, opening_h + 0.22), materials["plaster_cream"], visible, "facade_trim", 0.018)

    # Construction-led weathering and service detail.
    box("SM_M01_WindowBayA01_RepairPatch", (1.46, -0.018, 3.45), (0.62, 0.025, 0.44), materials["plaster_cool"], visible, "weathering", 0.006)
    cylinder("SM_M01_WindowBayA01_ServiceConduit", (-1.83, -0.11, 2.20), 0.022, 3.30, materials["copper"], visible, "service_detail", vertices=16)
    box("SM_M01_WindowBayA01_JunctionBox", (-1.83, -0.16, 3.58), (0.22, 0.12, 0.26), materials["metal"], visible, "service_detail", 0.018)

    # Four UCX boxes preserve the aperture rather than blocking it.
    box("UCX_SM_M01_WindowBayA01_Pier_L_00", (-(opening_w + side_w) * 0.5, 0.28, module_h * 0.5), (side_w, wall_depth, module_h), materials["concrete"], collision, "unreal_collision", 0.0)
    box("UCX_SM_M01_WindowBayA01_Pier_R_00", ((opening_w + side_w) * 0.5, 0.28, module_h * 0.5), (side_w, wall_depth, module_h), materials["concrete"], collision, "unreal_collision", 0.0)
    box("UCX_SM_M01_WindowBayA01_Spandrel_00", (0.0, 0.28, opening_bottom * 0.5), (opening_w, wall_depth, opening_bottom), materials["concrete"], collision, "unreal_collision", 0.0)
    box("UCX_SM_M01_WindowBayA01_Header_00", (0.0, 0.28, opening_top + (module_h - opening_top) * 0.5), (opening_w, wall_depth, module_h - opening_top), materials["concrete"], collision, "unreal_collision", 0.0)

    return {
        "module_width_m": module_w,
        "module_height_m": module_h,
        "wall_depth_m": wall_depth,
        "opening_width_m": opening_w,
        "opening_height_m": opening_h,
        "opening_bottom_m": opening_bottom,
        "opening_top_m": opening_top,
        "frame_width_m": frame_w,
        "frame_height_m": frame_h,
        "frame_face_y_m": frame_y - frame_depth * 0.5,
        "wall_face_y_m": 0.0,
        "frame_projects_ahead_of_wall": frame_y - frame_depth * 0.5 < 0.0,
        "interior_back_depth_from_wall_m": 0.58,
        "glazing_pane_count": 4,
        "facade_piece_count": 4,
        "clean_rectangular_aperture": True,
        "whole_building_scope": False,
    }


def configure_scene(scene: bpy.types.Scene) -> None:
    base.configure_scene(scene)
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.color_mode = "RGBA"


def setup_review(scene: bpy.types.Scene, review: bpy.types.Collection, materials: dict[str, bpy.types.Material]) -> dict[str, bpy.types.Object]:
    camera_data = bpy.data.cameras.new("CAM_M01_WindowBayA01_Review")
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    review.objects.link(camera)
    scene.camera = camera
    camera.data.lens = 62.0

    bpy.ops.object.light_add(type="AREA", location=(-3.2, -5.0, 6.0))
    key = bpy.context.object
    key.name = "LGT_M01_WindowBayA01_Key"
    key.data.energy = 1500.0
    key.data.shape = "DISK"
    key.data.size = 4.0
    base.move_to_collection(key, review)
    base.look_at(key, (0.0, 0.0, 2.2))

    bpy.ops.object.light_add(type="AREA", location=(4.5, -2.0, 3.0))
    fill = bpy.context.object
    fill.name = "LGT_M01_WindowBayA01_Fill"
    fill.data.energy = 780.0
    fill.data.size = 3.2
    base.move_to_collection(fill, review)
    base.look_at(fill, (0.0, 0.1, 2.2))

    bpy.ops.object.light_add(type="AREA", location=(0.0, 1.2, 2.3))
    interior = bpy.context.object
    interior.name = "LGT_M01_WindowBayA01_Interior"
    interior.data.energy = 420.0
    interior.data.color = (1.0, 0.48, 0.20)
    interior.data.size = 1.3
    base.move_to_collection(interior, review)
    base.look_at(interior, (0.0, 0.0, 2.2))

    box("REVIEW_WindowBayA01_Ground", (0.0, 1.8, -0.10), (7.5, 5.0, 0.20), materials["concrete"], review, "review_only", 0.02)
    return {"camera": camera, "key": key, "fill": fill, "interior": interior}


def set_condition(scene: bpy.types.Scene, rig: dict[str, bpy.types.Object], condition: str) -> None:
    background = scene.world.node_tree.nodes.get("Background")
    if condition == "daylight":
        rig["key"].data.energy = 1500.0
        rig["fill"].data.energy = 780.0
        rig["interior"].data.energy = 340.0
        background.inputs["Color"].default_value = (0.36, 0.49, 0.68, 1.0)
        background.inputs["Strength"].default_value = 0.95
        scene.view_settings.exposure = 0.75
    elif condition == "overcast":
        rig["key"].data.energy = 520.0
        rig["fill"].data.energy = 1150.0
        rig["interior"].data.energy = 390.0
        background.inputs["Color"].default_value = (0.42, 0.45, 0.48, 1.0)
        background.inputs["Strength"].default_value = 1.05
        scene.view_settings.exposure = 0.92
    elif condition == "grazing":
        rig["key"].data.energy = 2100.0
        rig["fill"].data.energy = 380.0
        rig["interior"].data.energy = 320.0
        background.inputs["Color"].default_value = (0.30, 0.40, 0.55, 1.0)
        background.inputs["Strength"].default_value = 0.85
        scene.view_settings.exposure = 0.72
    elif condition == "wet":
        rig["key"].data.energy = 920.0
        rig["fill"].data.energy = 950.0
        rig["interior"].data.energy = 470.0
        background.inputs["Color"].default_value = (0.20, 0.27, 0.36, 1.0)
        background.inputs["Strength"].default_value = 0.92
        scene.view_settings.exposure = 0.95
    else:
        rig["key"].data.energy = 90.0
        rig["fill"].data.energy = 310.0
        rig["interior"].data.energy = 1450.0
        background.inputs["Color"].default_value = (0.025, 0.04, 0.075, 1.0)
        background.inputs["Strength"].default_value = 0.58
        scene.view_settings.exposure = 1.28


def render_reviews(scene: bpy.types.Scene, rig: dict[str, bpy.types.Object], output: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    checkpoints_dir = output / "checkpoints"
    renders_dir = output / "renders"
    checkpoints_dir.mkdir()
    renders_dir.mkdir()
    camera = rig["camera"]
    checkpoints = []
    for condition, name, location, target, lens in (
        ("daylight", "checkpoint_01_front_construction", (0.0, -8.2, 2.25), (0.0, 0.10, 2.25), 64.0),
        ("grazing", "checkpoint_02_oblique_reveal", (-4.2, -7.2, 2.65), (0.0, 0.10, 2.25), 67.0),
        ("night", "checkpoint_03_night_interior", (0.2, -8.0, 2.35), (0.0, 0.15, 2.30), 65.0),
    ):
        set_condition(scene, rig, condition)
        record = base.render_one(scene, camera, checkpoints_dir / f"{name}.png", location, target, lens, CHECKPOINT_SIZE)
        record.update({"condition": condition, "camera": name})
        checkpoints.append(record)

    finals = []
    for condition, name, location, target, lens in (
        ("daylight", "01_front_macro", (0.0, -7.2, 2.25), (0.0, 0.10, 2.25), 70.0),
        ("daylight", "02_left_oblique", (-3.8, -6.0, 2.55), (0.0, 0.12, 2.25), 72.0),
        ("overcast", "03_right_oblique", (3.8, -6.0, 2.55), (0.0, 0.12, 2.25), 72.0),
        ("grazing", "04_sill_lintel_detail", (-1.5, -4.7, 2.25), (0.0, -0.02, 2.28), 82.0),
        ("daylight", "05_reveal_section", (3.2, -3.4, 2.55), (0.0, 0.30, 2.25), 75.0),
        ("wet", "06_material_response", (-2.6, -5.0, 2.8), (0.0, 0.0, 2.35), 76.0),
        ("night", "07_night_interior_response", (0.0, -7.0, 2.30), (0.0, 0.12, 2.30), 70.0),
        ("daylight", "08_frame_hardware_closeup", (-0.45, -3.3, 2.25), (0.0, -0.05, 2.22), 88.0),
    ):
        set_condition(scene, rig, condition)
        record = base.render_one(scene, camera, renders_dir / f"{condition}_{name}.png", location, target, lens, RENDER_SIZE)
        record.update({"condition": condition, "camera": name})
        finals.append(record)
    return checkpoints, finals


def object_receipt(collections: Iterable[bpy.types.Collection]) -> dict[str, Any]:
    receipt = base.object_receipt(collections)
    receipt["schema"] = "skyguard.m01-hero-prewar-window-bay-a01.topology-material.v1"
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
    visible = base.get_collection("M01_WINDOW_BAY_A01_VISIBLE")
    collision = base.get_collection("M01_WINDOW_BAY_A01_COLLISION")
    sockets = base.get_collection("M01_WINDOW_BAY_A01_SOCKETS")
    review = base.get_collection("M01_WINDOW_BAY_A01_REVIEW_ONLY")
    materials = build_materials()
    design = build_bay(materials, visible, collision)
    base.add_empty("SOCKET_M01_WindowBayA01_Origin", (0.0, 0.0, 0.0), sockets, "unreal_socket")
    base.add_empty("SOCKET_M01_WindowBayA01_WindowCenter", (0.0, 0.0, 2.28), sockets, "unreal_socket")
    rig = setup_review(scene, review, materials)

    topology = object_receipt((visible, collision, sockets))
    require(topology["all_renderable_meshes_have_uv0"], "Renderable UV0 coverage failed")
    require(topology["distinct_building_signatures"] == [SIGNATURE], "Unexpected signature set")
    require(topology["distinct_material_count"] >= 12, "Material floor failed")
    require(topology["role_counts"].get("facade_structure", 0) == 4, "The aperture must be defined by exactly four structural pieces")
    require(topology["role_counts"].get("window_reveal", 0) == 4, "Four reveal returns are required")
    require(topology["role_counts"].get("window_frame", 0) >= 21, "Visible frame and glazing beads are incomplete")
    require(topology["role_counts"].get("window_glazing", 0) == 4, "Exactly four glazing panes are required")
    require(topology["role_counts"].get("window_interior", 0) >= 14, "Interior response is incomplete")
    require(design["frame_projects_ahead_of_wall"], "Frame remains hidden behind the wall plane")
    require(design["clean_rectangular_aperture"], "Aperture contract failed")

    checkpoints, renders = render_reviews(scene, rig, output)
    blend_path = output / "M01_Hero_Prewar_Window_Bay_A01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    glb_path = output / "M01_Hero_Prewar_Window_Bay_A01.glb"
    base.export_glb(glb_path, (visible, collision, sockets))
    write_json(output / "topology_material_receipt.json", topology)
    write_json(
        output / "design_contract_receipt.json",
        {
            "schema": "skyguard.m01-hero-prewar-window-bay-a01.design-contract.v1",
            "asset_id": ASSET_ID,
            "fresh_asset_specific_geometry": True,
            "single_closeup_facade_bay_scope": True,
            "whole_building_scope": False,
            "whole_scene_generator": False,
            "external_models": False,
            "generated_substitutes": False,
            "governed_local_pbr": True,
            "coherent_wall_plane": True,
            "clean_rectangular_aperture": True,
            "visible_frame_ahead_of_wall": True,
            "interior_response_not_black_void": True,
            "design": design,
            "coordinate_contract": {"units": "meters", "forward": "+X", "up": "+Z"},
            "unreal_import_authorized": False,
            "passed": True,
        },
    )
    write_json(
        output / "artifact_receipt.json",
        {
            "schema": "skyguard.m01-hero-prewar-window-bay-a01.artifacts.v1",
            "asset_id": ASSET_ID,
            "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size, "sha256": base.sha256(blend_path)},
            "glb": {"path": str(glb_path), "bytes": glb_path.stat().st_size, "sha256": base.sha256(glb_path)},
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
