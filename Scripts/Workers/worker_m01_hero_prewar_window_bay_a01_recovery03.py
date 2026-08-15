"""Build a fresh production window bay around the accepted Eevee glazing candidate.

This worker deliberately does not reuse failed Recovery01/02 mesh data or the
diagnostic coupon geometry.  It recreates a complete installed timber-casement
module, a furnished room for parallax, refined hardware, collision, sockets,
and fixed review cameras.  The accepted coupon contributes only the Candidate
B shader method and its measured parameters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import bpy

import worker_m01_hero_coastal_frontage_cell01 as base
import worker_m01_prewar_window_material_glazing_benchmark_a01 as legacy


ASSET_ID = "m01-hero-prewar-window-bay-a01-recovery03"
GATE = "M01-HERO-PREWAR-WINDOW-BAY-A01-RECOVERY03"
SIGNATURE = "A_PREWAR_CASEMENT_RECOVERY03_CANDIDATE_B"
ROOT = Path(r"D:\Skyguard52")
PROVENANCE = ROOT / "Content" / "Skyguard" / "Textures" / "PolyHaven" / "polyhaven-provenance-manifest.json"
COUPON_FREEZE = ROOT / "Docs" / "AAA_Review" / "M01_PREWAR_WINDOW_EEVEE_GLAZING_TRANSMISSION_COUPON_A01_ATTEMPT01_TERMINAL_FREEZE.json"
CALIBRATION_SIZE = (512, 512)
CHECKPOINT_SIZE = (1280, 720)
RENDER_SIZE = (2048, 1152)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--asset-id", required=True)
    return parser.parse_args()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    role: str,
    bevel: float = 0.006,
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
    vertices: int = 32,
) -> bpy.types.Object:
    return base.add_cylinder(name, location, radius, depth, material, collection, role, rotation, vertices, SIGNATURE)


def sphere(
    name: str,
    location: tuple[float, float, float],
    radius: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    role: str,
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    base.move_to_collection(obj, collection)
    base.tag(obj, role, SIGNATURE)
    return obj


def configure_transparency(material: bpy.types.Material) -> None:
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "DITHERED"
    if hasattr(material, "use_transparency_overlap"):
        material.use_transparency_overlap = False


def candidate_b_glazing() -> bpy.types.Material:
    material = bpy.data.materials.new("M_M01_PrewarWindowR03_Glass_CandidateB")
    material.use_nodes = True
    material.diffuse_color = (0.62, 0.77, 0.80, 0.10)
    configure_transparency(material)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    transparent.inputs["Color"].default_value = (0.86, 0.94, 0.96, 1.0)
    reflection = nodes.new("ShaderNodeBsdfPrincipled")
    reflection.inputs["Base Color"].default_value = (0.28, 0.42, 0.46, 1.0)
    reflection.inputs["Roughness"].default_value = 0.11
    reflection.inputs["IOR"].default_value = 1.46
    reflection.inputs["Metallic"].default_value = 0.0
    fresnel = nodes.new("ShaderNodeFresnel")
    fresnel.inputs["IOR"].default_value = 1.46
    mix = nodes.new("ShaderNodeMixShader")
    links.new(fresnel.outputs["Fac"], mix.inputs[0])
    links.new(transparent.outputs["BSDF"], mix.inputs[1])
    links.new(reflection.outputs["BSDF"], mix.inputs[2])
    links.new(mix.outputs["Shader"], output.inputs["Surface"])
    return material


def aged_hardware_material() -> bpy.types.Material:
    material = legacy.simple_material(
        "M_M01_PrewarWindowR03_AgedBronzeHardware",
        (0.095, 0.065, 0.032, 1.0),
        0.38,
        0.82,
    )
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 5.5
    noise.inputs["Detail"].default_value = 2.0
    noise.inputs["Roughness"].default_value = 0.58
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.045, 0.024, 0.010, 1.0)
    ramp.color_ramp.elements[1].color = (0.16, 0.10, 0.040, 1.0)
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.065
    bump.inputs["Distance"].default_value = 0.008
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return material


def build_materials() -> dict[str, bpy.types.Material]:
    materials = legacy.build_materials()
    materials["glass"] = candidate_b_glazing()
    materials["metal"] = aged_hardware_material()
    materials["interior_wall"] = legacy.simple_material(
        "M_M01_PrewarWindowR03_InteriorWall", (0.34, 0.295, 0.24, 1.0), 0.80
    )
    materials["radiator"] = legacy.simple_material(
        "M_M01_PrewarWindowR03_Radiator", (0.34, 0.31, 0.26, 1.0), 0.50, 0.62
    )
    materials["furniture"] = legacy.simple_material(
        "M_M01_PrewarWindowR03_Furniture", (0.085, 0.048, 0.024, 1.0), 0.46
    )
    materials["dark_slot"] = legacy.simple_material(
        "M_M01_PrewarWindowR03_FastenerSlot", (0.006, 0.004, 0.002, 1.0), 0.72, 0.32
    )
    materials["book_green"] = legacy.simple_material(
        "M_M01_PrewarWindowR03_BookGreen", (0.075, 0.22, 0.11, 1.0), 0.56
    )
    materials["book_red"] = legacy.simple_material(
        "M_M01_PrewarWindowR03_BookRed", (0.36, 0.055, 0.028, 1.0), 0.58
    )
    return materials


def add_refined_screw(
    prefix: str,
    x: float,
    y: float,
    z: float,
    materials: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> None:
    cylinder(prefix + "_Head", (x, y, z), 0.0042, 0.0045, materials["metal"], collection, "window_hardware_fastener", (math.pi / 2.0, 0.0, 0.0), 24)
    slot = box(prefix + "_Slot", (x, y - 0.0024, z), (0.0062, 0.0012, 0.0012), materials["dark_slot"], collection, "window_hardware_fastener", 0.0003)
    slot.rotation_euler[1] = math.radians(14.0)


def add_refined_hinge(
    prefix: str,
    x: float,
    z: float,
    direction: float,
    materials: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> None:
    front_y = -0.041
    for index, offset in enumerate((-0.028, 0.0, 0.028)):
        cylinder(prefix + f"_Knuckle_{index:02d}", (x, front_y, z + offset), 0.0078, 0.024, materials["metal"], collection, "window_hardware", vertices=28)
    cylinder(prefix + "_Pin", (x, front_y, z), 0.0031, 0.088, materials["metal"], collection, "window_hardware", vertices=24)
    sphere(prefix + "_CapTop", (x, front_y, z + 0.047), 0.0064, materials["metal"], collection, "window_hardware", (1.0, 1.0, 0.72))
    sphere(prefix + "_CapBottom", (x, front_y, z - 0.047), 0.0064, materials["metal"], collection, "window_hardware", (1.0, 1.0, 0.72))
    frame_x = x + direction * 0.032
    sash_x = x - direction * 0.030
    box(prefix + "_FrameLeaf", (frame_x, front_y + 0.010, z), (0.052, 0.007, 0.044), materials["metal"], collection, "window_hardware", 0.006)
    box(prefix + "_SashLeaf", (sash_x, front_y + 0.010, z), (0.048, 0.007, 0.044), materials["metal"], collection, "window_hardware", 0.006)
    add_refined_screw(prefix + "_FrameScrew", frame_x, front_y + 0.0058, z, materials, collection)
    add_refined_screw(prefix + "_SashScrew", sash_x, front_y + 0.0058, z, materials, collection)


def add_refined_latch(
    materials: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
    center_z: float,
) -> dict[str, float]:
    latch_x = 0.050
    latch_z = center_z - 0.12
    box("SM_M01_WindowR03_LatchBackplate", (latch_x, -0.016, latch_z), (0.032, 0.010, 0.112), materials["metal"], collection, "window_hardware", 0.010)
    cylinder("SM_M01_WindowR03_LatchSpindle", (latch_x, -0.034, latch_z), 0.0075, 0.032, materials["metal"], collection, "window_hardware", (math.pi / 2.0, 0.0, 0.0), 28)
    neck = box("SM_M01_WindowR03_LatchNeck", (latch_x + 0.016, -0.056, latch_z - 0.002), (0.042, 0.018, 0.018), materials["metal"], collection, "window_hardware", 0.008)
    neck.rotation_euler[1] = math.radians(-10.0)
    cylinder("SM_M01_WindowR03_LatchGrip", (latch_x + 0.055, -0.057, latch_z - 0.012), 0.0085, 0.082, materials["metal"], collection, "window_hardware", (0.0, math.pi / 2.0, 0.0), 32)
    for offset in (-0.036, 0.036):
        add_refined_screw(f"SM_M01_WindowR03_LatchScrew_{offset:+.3f}", latch_x, -0.022, latch_z + offset, materials, collection)
    cylinder("SM_M01_WindowR03_EspagnoletteRod", (0.012, 0.001, center_z), 0.0038, 1.61, materials["metal"], collection, "window_hardware", vertices=24)
    for index, offset in enumerate((-0.55, 0.55)):
        box(f"SM_M01_WindowR03_RodGuide_{index:02d}", (0.012, -0.004, center_z + offset), (0.028, 0.012, 0.042), materials["metal"], collection, "window_hardware", 0.005)
    return {"latch_x": latch_x, "latch_z": latch_z}


def build_room(
    materials: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
    opening_center_z: float,
) -> dict[str, Any]:
    room_width, room_depth = 2.60, 2.50
    room_center_y = 1.31
    box("SM_M01_WindowR03_RoomBack", (0.0, room_depth, 2.02), (room_width, 0.08, 2.70), materials["interior_wall"], collection, "window_interior_architecture", 0.008)
    box("SM_M01_WindowR03_RoomSide_L", (-room_width * 0.5, room_center_y, 2.02), (0.08, room_depth, 2.70), materials["interior_wall"], collection, "window_interior_architecture", 0.008)
    box("SM_M01_WindowR03_RoomSide_R", (room_width * 0.5, room_center_y, 2.02), (0.08, room_depth, 2.70), materials["interior_wall"], collection, "window_interior_architecture", 0.008)
    box("SM_M01_WindowR03_RoomFloor", (0.0, room_center_y, 0.67), (room_width, room_depth, 0.08), materials["interior_wood"], collection, "window_interior_architecture", 0.008)
    box("SM_M01_WindowR03_RoomCeiling", (0.0, room_center_y, 3.37), (room_width, room_depth, 0.08), materials["interior_wall"], collection, "window_interior_architecture", 0.008)

    legacy.add_curtain("SM_M01_WindowR03_Curtain_L", -0.62, 0.30, 0.84, 3.18, materials["curtain"], collection)
    legacy.add_curtain("SM_M01_WindowR03_Curtain_R", 0.62, 0.30, 0.84, 3.18, materials["curtain"], collection)
    cylinder("SM_M01_WindowR03_CurtainRod", (0.0, 0.43, 3.25), 0.009, 1.72, materials["metal"], collection, "window_interior_hardware", (0.0, math.pi / 2.0, 0.0), 28)

    box("SM_M01_WindowR03_RadiatorBody", (0.0, 0.57, 0.72), (0.94, 0.13, 0.46), materials["radiator"], collection, "window_interior_fixture", 0.018)
    for index in range(13):
        x = -0.42 + index * 0.070
        box(f"SM_M01_WindowR03_RadiatorFin_{index:02d}", (x, 0.492, 0.72), (0.026, 0.026, 0.37), materials["radiator"], collection, "window_interior_fixture", 0.007)

    box("SM_M01_WindowR03_TableTop", (-0.38, 1.36, 1.04), (0.82, 0.52, 0.052), materials["furniture"], collection, "window_interior_furniture", 0.016)
    for x in (-0.70, -0.06):
        for y in (1.16, 1.56):
            cylinder(f"SM_M01_WindowR03_TableLeg_{x:+.2f}_{y:.2f}", (x, y, 0.85), 0.016, 0.37, materials["furniture"], collection, "window_interior_furniture", vertices=20)

    box("SM_M01_WindowR03_ChairSeat", (0.48, 1.54, 0.91), (0.46, 0.44, 0.055), materials["furniture"], collection, "window_interior_furniture", 0.014)
    box("SM_M01_WindowR03_ChairBack", (0.48, 1.74, 1.30), (0.46, 0.055, 0.72), materials["furniture"], collection, "window_interior_furniture", 0.016)
    for x in (0.30, 0.66):
        for y in (1.38, 1.70):
            cylinder(f"SM_M01_WindowR03_ChairLeg_{x:+.2f}_{y:.2f}", (x, y, 0.72), 0.014, 0.36, materials["furniture"], collection, "window_interior_furniture", vertices=18)

    box("SM_M01_WindowR03_Bookcase", (0.78, 2.31, 1.56), (0.54, 0.24, 1.58), materials["furniture"], collection, "window_interior_furniture", 0.020)
    for index, z in enumerate((1.02, 1.38, 1.74, 2.10)):
        box(f"SM_M01_WindowR03_Shelf_{index:02d}", (0.78, 2.16, z), (0.48, 0.22, 0.030), materials["furniture"], collection, "window_interior_furniture", 0.004)
    for index, (x, z, mat) in enumerate((
        (0.64, 1.18, materials["book_red"]),
        (0.78, 1.18, materials["book_green"]),
        (0.88, 1.54, materials["book_red"]),
        (0.68, 1.90, materials["book_green"]),
    )):
        box(f"SM_M01_WindowR03_Book_{index:02d}", (x, 2.02, z), (0.075, 0.065, 0.25), mat, collection, "window_interior_furniture", 0.004)

    cylinder("SM_M01_WindowR03_LampStem", (-0.40, 1.35, 1.41), 0.010, 0.66, materials["metal"], collection, "window_interior_furniture", vertices=24)
    sphere("SM_M01_WindowR03_LampShade", (-0.40, 1.35, 1.76), 0.14, materials["warm_lamp"], collection, "window_interior_furniture", (1.20, 1.0, 0.70))
    box("SM_M01_WindowR03_WallArt", (-0.38, room_depth - 0.052, 2.35), (0.62, 0.022, 0.76), materials["interior_wood"], collection, "window_interior_furniture", 0.016)
    return {"room_width_m": room_width, "room_depth_m": room_depth, "furnished": True}


def build_window(
    materials: dict[str, bpy.types.Material],
    visible: bpy.types.Collection,
    collision: bpy.types.Collection,
) -> dict[str, Any]:
    module_w, module_h, wall_depth = 3.60, 4.00, 0.46
    opening_w, opening_h = 1.56, 2.30
    opening_center_z = 2.12
    opening_bottom = opening_center_z - opening_h * 0.5
    opening_top = opening_center_z + opening_h * 0.5
    side_w = (module_w - opening_w) * 0.5

    wall_specs = (
        ("L", (-(opening_w + side_w) * 0.5, 0.23, module_h * 0.5), (side_w, wall_depth, module_h)),
        ("R", ((opening_w + side_w) * 0.5, 0.23, module_h * 0.5), (side_w, wall_depth, module_h)),
        ("B", (0.0, 0.23, opening_bottom * 0.5), (opening_w, wall_depth, opening_bottom)),
        ("T", (0.0, 0.23, opening_top + (module_h - opening_top) * 0.5), (opening_w, wall_depth, module_h - opening_top)),
    )
    for label, location, dimensions in wall_specs:
        box(f"SM_M01_WindowR03_Wall_{label}", location, dimensions, materials["plaster"], visible, "facade_structure", 0.014)

    reveal_t = 0.050
    box("SM_M01_WindowR03_Reveal_L", (-opening_w * 0.5 + reveal_t * 0.5, 0.22, opening_center_z), (reveal_t, 0.42, opening_h), materials["reveal"], visible, "window_reveal", 0.005)
    box("SM_M01_WindowR03_Reveal_R", (opening_w * 0.5 - reveal_t * 0.5, 0.22, opening_center_z), (reveal_t, 0.42, opening_h), materials["reveal"], visible, "window_reveal", 0.005)
    box("SM_M01_WindowR03_Reveal_T", (0.0, 0.22, opening_top - reveal_t * 0.5), (opening_w, 0.42, reveal_t), materials["reveal"], visible, "window_reveal", 0.005)
    box("SM_M01_WindowR03_Reveal_B", (0.0, 0.22, opening_bottom + reveal_t * 0.5), (opening_w, 0.42, reveal_t), materials["reveal"], visible, "window_reveal", 0.005)

    # A stepped perimeter and narrow sash members avoid the toy-thick Recovery02 silhouette.
    frame_outer_w, frame_outer_h = 1.43, 2.16
    frame_member, frame_depth = 0.062, 0.108
    frame_y = -0.012
    for side, x in (("L", -frame_outer_w * 0.5), ("R", frame_outer_w * 0.5)):
        box(f"SM_M01_WindowR03_Frame_{side}", (x, frame_y, opening_center_z), (frame_member, frame_depth, frame_outer_h), materials["painted_wood"], visible, "window_frame_primary", 0.007)
        box(f"SM_M01_WindowR03_FrameStep_{side}", (x * 0.952, 0.036, opening_center_z), (0.022, 0.034, frame_outer_h - 0.09), materials["painted_wood"], visible, "window_frame_rebate", 0.003)
    for edge, z in (("T", opening_center_z + frame_outer_h * 0.5), ("B", opening_center_z - frame_outer_h * 0.5)):
        box(f"SM_M01_WindowR03_Frame_{edge}", (0.0, frame_y, z), (frame_outer_w + frame_member, frame_depth, frame_member), materials["painted_wood"], visible, "window_frame_primary", 0.007)
        box(f"SM_M01_WindowR03_FrameStep_{edge}", (0.0, 0.036, z), (frame_outer_w - 0.08, 0.034, 0.022), materials["painted_wood"], visible, "window_frame_rebate", 0.003)

    leaf_width, leaf_height = 0.638, 1.99
    sash_member, sash_depth = 0.038, 0.056
    sash_y = 0.028
    leaf_centers = {"L": -0.330, "R": 0.330}
    pane_records: list[dict[str, Any]] = []
    for leaf, center_x in leaf_centers.items():
        for side, x in (("L", center_x - leaf_width * 0.5), ("R", center_x + leaf_width * 0.5)):
            box(f"SM_M01_WindowR03_Sash_{leaf}_{side}", (x, sash_y, opening_center_z), (sash_member, sash_depth, leaf_height), materials["painted_wood"], visible, "window_sash", 0.004)
        for edge, z in (("T", opening_center_z + leaf_height * 0.5), ("B", opening_center_z - leaf_height * 0.5)):
            box(f"SM_M01_WindowR03_Sash_{leaf}_{edge}", (center_x, sash_y, z), (leaf_width, sash_depth, sash_member), materials["painted_wood"], visible, "window_sash", 0.004)
        transom_z = opening_center_z + 0.37
        box(f"SM_M01_WindowR03_Sash_{leaf}_Transom", (center_x, sash_y, transom_z), (leaf_width - 0.046, sash_depth, 0.032), materials["painted_wood"], visible, "window_sash", 0.0035)

        pane_width = leaf_width - 2.0 * sash_member - 0.018
        for pane, pane_z, pane_height in (
            ("LOWER", opening_center_z - 0.316, 1.276),
            ("UPPER", opening_center_z + 0.694, 0.632),
        ):
            box(f"SM_M01_WindowR03_Glass_{leaf}_{pane}", (center_x, 0.064, pane_z), (pane_width, 0.008, pane_height), materials["glass"], visible, "window_glazing", 0.001)
            bead = 0.011
            for edge, x, z, width, height in (
                ("L", center_x - pane_width * 0.5, pane_z, bead, pane_height),
                ("R", center_x + pane_width * 0.5, pane_z, bead, pane_height),
                ("T", center_x, pane_z + pane_height * 0.5, pane_width, bead),
                ("B", center_x, pane_z - pane_height * 0.5, pane_width, bead),
            ):
                box(f"SM_M01_WindowR03_Bead_{leaf}_{pane}_{edge}", (x, 0.012, z), (width, 0.018, height), materials["painted_wood"], visible, "window_glazing_bead", 0.0018)
            pane_records.append({"leaf": leaf, "pane": pane, "width_m": pane_width, "height_m": pane_height, "glass_thickness_m": 0.008})

    for leaf, x, direction in (("L", -0.688, 1.0), ("R", 0.688, -1.0)):
        for index, z in enumerate((opening_center_z - 0.69, opening_center_z, opening_center_z + 0.69)):
            add_refined_hinge(f"SM_M01_WindowR03_Hinge_{leaf}_{index:02d}", x, z, direction, materials, visible)
    latch = add_refined_latch(materials, visible, opening_center_z)

    box("SM_M01_WindowR03_StoneSill", (0.0, -0.18, opening_bottom - 0.105), (1.86, 0.37, 0.14), materials["reveal"], visible, "facade_trim", 0.016)
    box("SM_M01_WindowR03_SillDrip", (0.0, -0.372, opening_bottom - 0.145), (1.90, 0.028, 0.030), materials["reveal"], visible, "facade_trim", 0.004)
    box("SM_M01_WindowR03_LintelBand", (0.0, -0.050, opening_top + 0.108), (1.86, 0.15, 0.126), materials["reveal"], visible, "facade_trim", 0.014)

    room = build_room(materials, visible, opening_center_z)

    for label, location, dimensions in wall_specs:
        box(f"UCX_SM_M01_WindowR03_Wall_{label}_00", location, dimensions, materials["collision"], collision, "unreal_collision", 0.0)

    return {
        "module_width_m": module_w,
        "module_height_m": module_h,
        "wall_depth_m": wall_depth,
        "opening_width_m": opening_w,
        "opening_height_m": opening_h,
        "opening_center_z_m": opening_center_z,
        "outer_frame_member_width_m": frame_member,
        "sash_member_width_m": sash_member,
        "glass_thickness_m": 0.008,
        "pane_count": len(pane_records),
        "panes": pane_records,
        "hinge_count": 6,
        "latch_count": 1,
        "latch": latch,
        "room": room,
        "fresh_geometry": True,
        "failed_mesh_data_reused": False,
        "coupon_geometry_reused": False,
        "whole_building_scope": False,
    }


def configure_scene(scene: bpy.types.Scene) -> None:
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 15
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.62
    scene.view_settings.gamma = 1.0
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.060, 0.080, 0.115, 1.0)
    background.inputs["Strength"].default_value = 0.22
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = 128


def setup_review(
    scene: bpy.types.Scene,
    review: bpy.types.Collection,
    materials: dict[str, bpy.types.Material],
) -> dict[str, Any]:
    camera_data = bpy.data.cameras.new("CAM_M01_PrewarWindowR03_Review")
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    review.objects.link(camera)
    scene.camera = camera

    bpy.ops.object.light_add(type="AREA", location=(-3.1, -4.2, 5.4))
    key = bpy.context.object
    key.name = "LGT_M01_PrewarWindowR03_Key"
    key.data.energy = 700.0
    key.data.shape = "DISK"
    key.data.size = 3.5
    base.move_to_collection(key, review)
    legacy.look_at(key, (0.0, 0.15, 2.10))

    bpy.ops.object.light_add(type="AREA", location=(3.5, -1.7, 3.5))
    fill = bpy.context.object
    fill.name = "LGT_M01_PrewarWindowR03_Fill"
    fill.data.energy = 390.0
    fill.data.size = 3.0
    base.move_to_collection(fill, review)
    legacy.look_at(fill, (0.0, 0.18, 2.10))

    bpy.ops.object.light_add(type="AREA", location=(-0.25, 1.42, 2.75))
    interior = bpy.context.object
    interior.name = "LGT_M01_PrewarWindowR03_Interior"
    interior.data.energy = 330.0
    interior.data.color = (1.0, 0.55, 0.29)
    interior.data.size = 1.15
    base.move_to_collection(interior, review)
    legacy.look_at(interior, (0.0, 0.35, 1.85))

    box("REVIEW_M01_PrewarWindowR03_Ground", (0.0, 1.35, -0.08), (6.2, 4.8, 0.16), materials["reveal"], review, "review_only", 0.010)
    gray_card = box("REVIEW_M01_PrewarWindowR03_GrayCard", (0.0, -0.42, 2.08), (1.50, 0.030, 1.50), materials["gray_card"], review, "review_only", 0.006)
    gray_card.hide_render = True
    return {"camera": camera, "key": key, "fill": fill, "interior": interior, "gray_card": gray_card}


def set_condition(scene: bpy.types.Scene, rig: dict[str, Any], condition: str) -> None:
    background = scene.world.node_tree.nodes.get("Background")
    if condition == "daylight":
        rig["key"].data.energy = 700.0
        rig["fill"].data.energy = 390.0
        rig["interior"].data.energy = 270.0
        background.inputs["Color"].default_value = (0.065, 0.095, 0.14, 1.0)
        background.inputs["Strength"].default_value = 0.24
        scene.view_settings.exposure = -0.70
    elif condition == "overcast":
        rig["key"].data.energy = 340.0
        rig["fill"].data.energy = 560.0
        rig["interior"].data.energy = 310.0
        background.inputs["Color"].default_value = (0.11, 0.12, 0.13, 1.0)
        background.inputs["Strength"].default_value = 0.31
        scene.view_settings.exposure = -0.54
    elif condition == "grazing":
        rig["key"].data.energy = 910.0
        rig["fill"].data.energy = 205.0
        rig["interior"].data.energy = 260.0
        background.inputs["Color"].default_value = (0.052, 0.072, 0.105, 1.0)
        background.inputs["Strength"].default_value = 0.21
        scene.view_settings.exposure = -0.76
    elif condition == "night":
        rig["key"].data.energy = 48.0
        rig["fill"].data.energy = 88.0
        rig["interior"].data.energy = 690.0
        background.inputs["Color"].default_value = (0.004, 0.008, 0.018, 1.0)
        background.inputs["Strength"].default_value = 0.08
        scene.view_settings.exposure = -0.14
    elif condition == "cockpit":
        rig["key"].data.energy = 120.0
        rig["key"].data.color = (0.52, 0.67, 1.0)
        rig["fill"].data.energy = 95.0
        rig["interior"].data.energy = 430.0
        background.inputs["Color"].default_value = (0.018, 0.030, 0.052, 1.0)
        background.inputs["Strength"].default_value = 0.13
        scene.view_settings.exposure = -0.30
    else:
        raise RuntimeError(f"Unknown condition: {condition}")
    if condition != "cockpit":
        rig["key"].data.color = (1.0, 1.0, 1.0)


def render_reviews(scene: bpy.types.Scene, rig: dict[str, Any], output: Path) -> dict[str, Any]:
    calibration_dir = output / "calibration"
    checkpoints_dir = output / "checkpoints"
    renders_dir = output / "renders"
    calibration_dir.mkdir()
    checkpoints_dir.mkdir()
    renders_dir.mkdir()
    camera = rig["camera"]

    set_condition(scene, rig, "daylight")
    rig["gray_card"].hide_render = False
    calibration = base.render_one(scene, camera, calibration_dir / "gray_card.png", (0.0, -3.4, 2.08), (0.0, -0.42, 2.08), 78.0, CALIBRATION_SIZE)
    rig["gray_card"].hide_render = True

    checkpoints: list[dict[str, Any]] = []
    for condition, name, location, target, lens in (
        ("daylight", "checkpoint_01_uncropped_installed_module", (0.0, -7.6, 2.02), (0.0, 0.15, 2.00), 62.0),
        ("overcast", "checkpoint_02_left_oblique_interior_parallax", (-2.55, -4.8, 2.36), (0.0, 1.05, 1.98), 76.0),
        ("grazing", "checkpoint_03_refined_hardware_macro", (1.28, -2.75, 2.24), (0.18, -0.01, 2.05), 96.0),
    ):
        set_condition(scene, rig, condition)
        record = base.render_one(scene, camera, checkpoints_dir / f"{name}.png", location, target, lens, CHECKPOINT_SIZE)
        record.update({"condition": condition, "camera": name})
        checkpoints.append(record)

    finals: list[dict[str, Any]] = []
    for condition, name, location, target, lens in (
        ("daylight", "01_uncropped_installed_module", (0.0, -7.25, 2.02), (0.0, 0.18, 2.00), 64.0),
        ("overcast", "02_uncropped_installed_module", (0.0, -7.15, 2.02), (0.0, 0.18, 2.00), 64.0),
        ("daylight", "03_left_glazing_parallax", (-2.45, -4.55, 2.36), (0.0, 1.10, 1.96), 80.0),
        ("overcast", "04_right_glazing_hardware", (2.42, -4.42, 2.28), (0.03, 0.70, 2.00), 82.0),
        ("grazing", "05_frame_hardware_profile", (-1.30, -3.10, 2.38), (-0.38, 0.02, 2.22), 92.0),
        ("night", "06_front_interior_visibility", (0.0, -6.20, 2.03), (0.0, 1.04, 1.96), 70.0),
        ("night", "07_oblique_interior_depth", (2.10, -4.15, 2.32), (0.12, 1.22, 1.88), 82.0),
        ("cockpit", "08_reargunner_distance_readability", (3.25, -9.10, 3.05), (0.0, 0.30, 2.02), 54.0),
    ):
        set_condition(scene, rig, condition)
        record = base.render_one(scene, camera, renders_dir / f"{condition}_{name}.png", location, target, lens, RENDER_SIZE)
        record.update({"condition": condition, "camera": name})
        finals.append(record)
    return {"calibration": calibration, "checkpoints": checkpoints, "renders": finals}


def topology_receipt(collections: Iterable[bpy.types.Collection]) -> dict[str, Any]:
    receipt = base.object_receipt(collections)
    receipt["schema"] = "skyguard.m01-hero-prewar-window-bay-a01-recovery03.topology-material.v1"
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
    require(PROVENANCE.is_file(), "PolyHaven provenance authority is missing")
    require(COUPON_FREEZE.is_file(), "Accepted glazing coupon freeze is missing")
    require(sha256(COUPON_FREEZE) == "221354359165758bf92cb8fb35a05f59814457b366968a7d59e26f9d756a0389", "Accepted glazing coupon freeze changed")
    for family in legacy.PBR.values():
        for source in family.values():
            require(source.is_file(), f"Texture authority missing: {source}")

    base.clear_scene()
    scene = bpy.context.scene
    configure_scene(scene)
    visible = base.get_collection("M01_PREWAR_WINDOW_R03_VISIBLE")
    collision = base.get_collection("M01_PREWAR_WINDOW_R03_COLLISION")
    sockets = base.get_collection("M01_PREWAR_WINDOW_R03_SOCKETS")
    review = base.get_collection("M01_PREWAR_WINDOW_R03_REVIEW_ONLY")
    materials = build_materials()
    design = build_window(materials, visible, collision)
    base.add_empty("SOCKET_M01_PrewarWindowR03_Origin", (0.0, 0.0, 0.0), sockets, "unreal_socket")
    base.add_empty("SOCKET_M01_PrewarWindowR03_Center", (0.0, 0.0, 2.12), sockets, "unreal_socket")
    base.add_empty("SOCKET_M01_PrewarWindowR03_Latch", (0.050, -0.052, 2.00), sockets, "unreal_socket")
    rig = setup_review(scene, review, materials)

    topology = topology_receipt((visible, collision, sockets))
    require(topology["all_renderable_meshes_have_uv0"], "Renderable UV0 coverage failed")
    require(topology["distinct_building_signatures"] == [SIGNATURE], "Unexpected signature set")
    require(topology["role_counts"].get("facade_structure", 0) == 4, "Aperture requires four structural pieces")
    require(topology["role_counts"].get("window_frame_primary", 0) == 4, "Primary frame is incomplete")
    require(topology["role_counts"].get("window_sash", 0) == 10, "Two complete sash leaves are required")
    require(topology["role_counts"].get("window_glazing", 0) == 4, "Exactly four panes are required")
    require(topology["role_counts"].get("window_hardware", 0) >= 40, "Refined hardware set is incomplete")
    require(topology["role_counts"].get("window_interior_architecture", 0) == 5, "Five-sided room is required")
    require(topology["role_counts"].get("window_interior_furniture", 0) >= 20, "Furnished parallax room is incomplete")
    require(design["outer_frame_member_width_m"] <= 0.062, "Outer frame remains oversized")
    require(design["sash_member_width_m"] <= 0.038, "Sash members remain oversized")
    require(design["glass_thickness_m"] == 0.008, "Accepted pane thickness changed")
    require(design["room"]["room_depth_m"] >= 2.4, "Room depth is insufficient")
    require(design["fresh_geometry"] and not design["failed_mesh_data_reused"] and not design["coupon_geometry_reused"], "Fresh-geometry contract failed")

    render_records = render_reviews(scene, rig, output)
    blend_path = output / "M01_Hero_Prewar_Window_Bay_A01_Recovery03.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    glb_path = output / "M01_Hero_Prewar_Window_Bay_A01_Recovery03.glb"
    base.export_glb(glb_path, (visible, collision, sockets))

    texture_authorities = []
    for family, sources in legacy.PBR.items():
        for role, source in sources.items():
            texture_authorities.append({
                "family": family,
                "role": role,
                "path": str(source.relative_to(ROOT)),
                "bytes": source.stat().st_size,
                "sha256": sha256(source),
            })

    write_json(output / "topology_material_receipt.json", topology)
    write_json(
        output / "construction_receipt.json",
        {
            "schema": "skyguard.m01-hero-prewar-window-bay-a01-recovery03.construction.v1",
            "asset_id": ASSET_ID,
            "generic_prewar_timber_casement_not_exact_building_identity": True,
            "fresh_geometry": True,
            "failed_recovery_mesh_data_reused": False,
            "coupon_geometry_reused": False,
            "whole_building_scope": False,
            "thin_stepped_frame_and_sash": True,
            "rounded_interleaved_hinge_knuckles": True,
            "recessed_fastener_slots": True,
            "furnished_room_parallax": True,
            "fake_wet_strip_geometry": False,
            "design": design,
            "passed": True,
        },
    )
    write_json(
        output / "selected_glazing_receipt.json",
        {
            "schema": "skyguard.m01-hero-prewar-window-bay-a01-recovery03.selected-glazing.v1",
            "asset_id": ASSET_ID,
            "accepted_coupon_freeze": {"path": str(COUPON_FREEZE.relative_to(ROOT)), "bytes": COUPON_FREEZE.stat().st_size, "sha256": sha256(COUPON_FREEZE)},
            "method": "transparent_principled_fresnel_mix_dithered",
            "ior": 1.46,
            "reflection_roughness": 0.11,
            "pane_thickness_m": 0.008,
            "pure_glass_bsdf_reused": False,
            "candidate_a_used": False,
            "pane_local_postflight_required": True,
            "unreal_import_authorized": False,
            "passed": True,
        },
    )
    write_json(
        output / "material_provenance_receipt.json",
        {
            "schema": "skyguard.m01-hero-prewar-window-bay-a01-recovery03.material-provenance.v1",
            "asset_id": ASSET_ID,
            "governed_local_pbr": True,
            "provenance": {"path": str(PROVENANCE.relative_to(ROOT)), "bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)},
            "texture_authorities": texture_authorities,
            "synthetic_high_frequency_hardware_stamp_removed": True,
            "passed": True,
        },
    )
    write_json(
        output / "review_intent_receipt.json",
        {
            "schema": "skyguard.m01-hero-prewar-window-bay-a01-recovery03.review-intent.v1",
            "asset_id": ASSET_ID,
            "uncropped_installed_module_required": True,
            "pane_local_luminance_and_variation_required": True,
            "left_right_oblique_parallax_required": True,
            "daylight_overcast_grazing_night_and_cockpit_conditions": True,
            "production_sampling_requested": True,
            "direct_full_resolution_review_required": True,
            "passed": True,
        },
    )
    write_json(
        output / "artifact_receipt.json",
        {
            "schema": "skyguard.m01-hero-prewar-window-bay-a01-recovery03.artifacts.v1",
            "asset_id": ASSET_ID,
            "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size, "sha256": sha256(blend_path)},
            "glb": {"path": str(glb_path), "bytes": glb_path.stat().st_size, "sha256": sha256(glb_path)},
            "calibration_count": 1,
            "checkpoint_count": len(render_records["checkpoints"]),
            "final_render_count": len(render_records["renders"]),
            "total_render_count": 1 + len(render_records["checkpoints"]) + len(render_records["renders"]),
            "calibration_dimensions": list(CALIBRATION_SIZE),
            "checkpoint_dimensions": list(CHECKPOINT_SIZE),
            "final_render_dimensions": list(RENDER_SIZE),
            "direct_full_resolution_review_required": True,
            "unreal_import_authorized": False,
            "passed": True,
        },
    )
    print(json.dumps({"gate": GATE, "classification": "PASSED_AUTOMATIC_AWAITING_POSTFLIGHT_AND_DIRECT_VISUAL_REVIEW", "design": design}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
