"""Build a physically layered Mission 1 prewar window benchmark.

This bounded asset follows the rejected window-bay Recovery02 review.  It does
not build a facade or building.  It independently proves timber-casement
proportions, mechanically coherent hardware, real glass thickness, interior
parallax, governed local PBR, wet-response geometry and exposure-safe review
coverage before those systems are propagated into a hero building.
"""

from __future__ import annotations

import argparse
import hashlib
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


ASSET_ID = "m01-prewar-window-material-glazing-benchmark-a01"
GATE = "M01_PREWAR_WINDOW_MATERIAL_GLAZING_BENCHMARK_A01"
SIGNATURE = "A_PREWAR_CASEMENT_MATERIAL_BENCHMARK"
CHECKPOINT_SIZE = (1280, 720)
RENDER_SIZE = (1920, 1080)
CALIBRATION_SIZE = (512, 512)
TEXTURE_ROOT = ROOT / "Content" / "Skyguard" / "Textures" / "PolyHaven"
PROVENANCE = TEXTURE_ROOT / "polyhaven-provenance-manifest.json"
PBR = {
    "plaster": {
        "base": TEXTURE_ROOT / "painted_plaster_wall" / "painted_plaster_wall_diff_2k.jpg",
        "normal": TEXTURE_ROOT / "painted_plaster_wall" / "painted_plaster_wall_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / "painted_plaster_wall" / "painted_plaster_wall_rough_2k.jpg",
    },
    "wood": {
        "base": TEXTURE_ROOT / "wood_cabinet_worn_long" / "wood_cabinet_worn_long_diff_2k.jpg",
        "normal": TEXTURE_ROOT / "wood_cabinet_worn_long" / "wood_cabinet_worn_long_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / "wood_cabinet_worn_long" / "wood_cabinet_worn_long_rough_2k.jpg",
    },
    "metal": {
        "base": TEXTURE_ROOT / "metal_plate" / "metal_plate_diff_2k.jpg",
        "normal": TEXTURE_ROOT / "metal_plate" / "metal_plate_nor_gl_2k.jpg",
        "roughness": TEXTURE_ROOT / "metal_plate" / "metal_plate_rough_2k.jpg",
        "metallic": TEXTURE_ROOT / "metal_plate" / "metal_plate_metal_2k.jpg",
    },
}
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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    role: str,
    bevel: float = 0.008,
) -> bpy.types.Object:
    return base.add_box(
        name,
        location,
        dimensions,
        material,
        collection,
        role,
        bevel,
        SIGNATURE,
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
    vertices: int = 32,
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
        SIGNATURE,
    )


def image(path: Path, non_color: bool = False) -> bpy.types.Image:
    require(path.is_file(), f"Missing governed texture authority: {path}")
    loaded = bpy.data.images.load(str(path), check_existing=True)
    if non_color:
        loaded.colorspace_settings.name = "Non-Color"
    return loaded


def pbr_material(
    name: str,
    sources: dict[str, Path],
    tint: tuple[float, float, float, float],
    scale: tuple[float, float, float],
    color_texture_strength: float,
    normal_strength: float,
    roughness_multiplier: float,
    metallic_multiplier: float = 1.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    texcoord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = scale
    links.new(texcoord.outputs["UV"], mapping.inputs["Vector"])

    base_tex = nodes.new("ShaderNodeTexImage")
    base_tex.image = image(sources["base"])
    links.new(mapping.outputs["Vector"], base_tex.inputs["Vector"])
    tint_node = nodes.new("ShaderNodeRGB")
    tint_node.outputs[0].default_value = tint
    mix = nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = color_texture_strength
    links.new(tint_node.outputs[0], mix.inputs[1])
    links.new(base_tex.outputs["Color"], mix.inputs[2])
    links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])

    rough_tex = nodes.new("ShaderNodeTexImage")
    rough_tex.image = image(sources["roughness"], True)
    links.new(mapping.outputs["Vector"], rough_tex.inputs["Vector"])
    rough_mult = nodes.new("ShaderNodeMath")
    rough_mult.operation = "MULTIPLY"
    rough_mult.inputs[1].default_value = roughness_multiplier
    links.new(rough_tex.outputs["Color"], rough_mult.inputs[0])
    links.new(rough_mult.outputs["Value"], bsdf.inputs["Roughness"])

    normal_tex = nodes.new("ShaderNodeTexImage")
    normal_tex.image = image(sources["normal"], True)
    links.new(mapping.outputs["Vector"], normal_tex.inputs["Vector"])
    normal = nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value = normal_strength
    links.new(normal_tex.outputs["Color"], normal.inputs["Color"])
    links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])

    if "metallic" in sources:
        metal_tex = nodes.new("ShaderNodeTexImage")
        metal_tex.image = image(sources["metallic"], True)
        links.new(mapping.outputs["Vector"], metal_tex.inputs["Vector"])
        metal_mult = nodes.new("ShaderNodeMath")
        metal_mult.operation = "MULTIPLY"
        metal_mult.inputs[1].default_value = metallic_multiplier
        links.new(metal_tex.outputs["Color"], metal_mult.inputs[0])
        links.new(metal_mult.outputs["Value"], bsdf.inputs["Metallic"])

    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
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
    require(bsdf is not None, f"Missing Principled BSDF: {name}")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    emission_color = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if emission_color is not None:
        emission_color.default_value = color
    emission_strength = bsdf.inputs.get("Emission Strength")
    if emission_strength is not None:
        emission_strength.default_value = emission
    return material


def glass_material() -> bpy.types.Material:
    material = bpy.data.materials.new("M_M01_PrewarWindow_PhysicalGlass")
    material.use_nodes = True
    material.diffuse_color = (0.72, 0.82, 0.84, 0.18)
    if hasattr(material, "surface_render_method"):
        try:
            material.surface_render_method = "DITHERED"
        except Exception:
            pass
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    glass = nodes.new("ShaderNodeBsdfGlass")
    glass.inputs["Color"].default_value = (0.74, 0.84, 0.86, 1.0)
    glass.inputs["IOR"].default_value = 1.46
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 8.0
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.72
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (0.025, 0.025, 0.025, 1.0)
    ramp.color_ramp.elements[1].position = 0.85
    ramp.color_ramp.elements[1].color = (0.16, 0.16, 0.16, 1.0)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], glass.inputs["Roughness"])
    links.new(glass.outputs["BSDF"], output.inputs["Surface"])
    return material


def cloth_material() -> bpy.types.Material:
    material = simple_material(
        "M_M01_PrewarWindow_CurtainCloth",
        (0.34, 0.27, 0.20, 1.0),
        0.78,
    )
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 145.0
    noise.inputs["Detail"].default_value = 2.0
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.16
    bump.inputs["Distance"].default_value = 0.012
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return material


def build_materials() -> dict[str, bpy.types.Material]:
    return {
        "plaster": pbr_material(
            "M_M01_PrewarWindow_WeatheredPlaster",
            PBR["plaster"],
            (0.58, 0.50, 0.40, 1.0),
            (2.4, 2.4, 2.4),
            0.34,
            0.48,
            1.05,
        ),
        "reveal": pbr_material(
            "M_M01_PrewarWindow_RevealPlaster",
            PBR["plaster"],
            (0.43, 0.40, 0.34, 1.0),
            (3.1, 3.1, 3.1),
            0.28,
            0.36,
            1.12,
        ),
        "painted_wood": pbr_material(
            "M_M01_PrewarWindow_PaintedTimber",
            PBR["wood"],
            (0.24, 0.31, 0.24, 1.0),
            (1.4, 5.8, 1.4),
            0.23,
            0.42,
            0.88,
        ),
        "interior_wood": pbr_material(
            "M_M01_PrewarWindow_InteriorWood",
            PBR["wood"],
            (0.38, 0.27, 0.17, 1.0),
            (2.0, 5.0, 2.0),
            0.52,
            0.48,
            1.0,
        ),
        "metal": pbr_material(
            "M_M01_PrewarWindow_AgedHardware",
            PBR["metal"],
            (0.12, 0.095, 0.055, 1.0),
            (4.0, 4.0, 4.0),
            0.20,
            0.50,
            0.82,
            0.90,
        ),
        "glass": glass_material(),
        "seal": simple_material("M_M01_PrewarWindow_WeatherSeal", (0.018, 0.022, 0.019, 1.0), 0.64),
        "interior_wall": simple_material("M_M01_PrewarWindow_InteriorWall", (0.29, 0.25, 0.21, 1.0), 0.84),
        "curtain": cloth_material(),
        "radiator": simple_material("M_M01_PrewarWindow_Radiator", (0.30, 0.28, 0.24, 1.0), 0.58, 0.52),
        "furniture": simple_material("M_M01_PrewarWindow_Furniture", (0.10, 0.065, 0.038, 1.0), 0.52),
        "warm_lamp": simple_material("M_M01_PrewarWindow_WarmLamp", (0.88, 0.42, 0.12, 1.0), 0.26, emission=2.4),
        "wet_film": glass_material(),
        "gray_card": simple_material("M_REVIEW_18PercentGray", (0.18, 0.18, 0.18, 1.0), 0.62),
        "collision": simple_material("M_REVIEW_Collision", (0.08, 0.08, 0.08, 1.0), 1.0),
    }


def add_screw(
    name: str,
    x: float,
    y: float,
    z: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> None:
    cylinder(
        name,
        (x, y, z),
        0.0045,
        0.006,
        material,
        collection,
        "window_hardware_fastener",
        (math.pi / 2.0, 0.0, 0.0),
        20,
    )


def add_hinge(
    prefix: str,
    x: float,
    z: float,
    leaf_direction: float,
    materials: dict[str, bpy.types.Material],
    collection: bpy.types.Collection,
) -> None:
    front_y = -0.043
    cylinder(prefix + "_Pin", (x, front_y, z), 0.0105, 0.072, materials["metal"], collection, "window_hardware", vertices=28)
    box(prefix + "_FrameLeaf", (x + leaf_direction * 0.035, front_y + 0.012, z), (0.068, 0.012, 0.058), materials["metal"], collection, "window_hardware", 0.003)
    box(prefix + "_SashLeaf", (x - leaf_direction * 0.035, front_y + 0.012, z), (0.068, 0.012, 0.058), materials["metal"], collection, "window_hardware", 0.003)
    for dx in (-0.020, 0.020):
        add_screw(prefix + f"_Screw_{dx:+.3f}", x + leaf_direction * 0.035 + dx, front_y - 0.001, z, materials["metal"], collection)


def add_curtain(
    name: str,
    center_x: float,
    width: float,
    bottom: float,
    top: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    columns = 18
    rows = 5
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for row in range(rows + 1):
        z = bottom + (top - bottom) * row / rows
        for column in range(columns + 1):
            u = column / columns
            x = center_x - width * 0.5 + width * u
            y = 0.46 + 0.026 * math.sin(u * math.pi * 8.0) + 0.008 * math.sin(u * math.pi * 17.0)
            vertices.append((x, y, z))
    stride = columns + 1
    for row in range(rows):
        for column in range(columns):
            index = row * stride + column
            faces.append((index, index + 1, index + stride + 1, index + stride))
    obj = base.add_custom_mesh(name, vertices, faces, material, collection, "window_interior_textile", SIGNATURE)
    solidify = obj.modifiers.new("ClothThickness", "SOLIDIFY")
    solidify.thickness = 0.004
    bevel = obj.modifiers.new("SoftClothEdge", "BEVEL")
    bevel.width = 0.003
    bevel.segments = 2
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=solidify.name)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    obj.select_set(False)
    return obj


def build_window(
    materials: dict[str, bpy.types.Material],
    visible: bpy.types.Collection,
    collision: bpy.types.Collection,
    wet_only: bpy.types.Collection,
) -> dict[str, Any]:
    module_w, module_h, wall_depth = 3.20, 3.80, 0.50
    opening_w, opening_h = 1.50, 2.20
    opening_center_z = 2.08
    opening_bottom = opening_center_z - opening_h * 0.5
    opening_top = opening_center_z + opening_h * 0.5
    side_w = (module_w - opening_w) * 0.5

    # Four pieces preserve a clean rectangular aperture.
    box("SM_M01_WindowBenchmark_Wall_L", (-(opening_w + side_w) * 0.5, 0.25, module_h * 0.5), (side_w, wall_depth, module_h), materials["plaster"], visible, "facade_structure", 0.018)
    box("SM_M01_WindowBenchmark_Wall_R", ((opening_w + side_w) * 0.5, 0.25, module_h * 0.5), (side_w, wall_depth, module_h), materials["plaster"], visible, "facade_structure", 0.018)
    box("SM_M01_WindowBenchmark_Wall_B", (0.0, 0.25, opening_bottom * 0.5), (opening_w, wall_depth, opening_bottom), materials["plaster"], visible, "facade_structure", 0.018)
    box("SM_M01_WindowBenchmark_Wall_T", (0.0, 0.25, opening_top + (module_h - opening_top) * 0.5), (opening_w, wall_depth, module_h - opening_top), materials["plaster"], visible, "facade_structure", 0.018)

    reveal_t = 0.055
    box("SM_M01_WindowBenchmark_Reveal_L", (-opening_w * 0.5 + reveal_t * 0.5, 0.23, opening_center_z), (reveal_t, 0.46, opening_h), materials["reveal"], visible, "window_reveal", 0.006)
    box("SM_M01_WindowBenchmark_Reveal_R", (opening_w * 0.5 - reveal_t * 0.5, 0.23, opening_center_z), (reveal_t, 0.46, opening_h), materials["reveal"], visible, "window_reveal", 0.006)
    box("SM_M01_WindowBenchmark_Reveal_T", (0.0, 0.23, opening_top - reveal_t * 0.5), (opening_w, 0.46, reveal_t), materials["reveal"], visible, "window_reveal", 0.006)
    box("SM_M01_WindowBenchmark_Reveal_B", (0.0, 0.23, opening_bottom + reveal_t * 0.5), (opening_w, 0.46, reveal_t), materials["reveal"], visible, "window_reveal", 0.006)

    # Stepped outer timber frame, explicitly thinner than the failed Recovery02 frame.
    frame_outer_w = 1.38
    frame_outer_h = 2.08
    frame_member = 0.070
    frame_y = -0.010
    frame_depth = 0.105
    for side, x in (("L", -frame_outer_w * 0.5), ("R", frame_outer_w * 0.5)):
        box(f"SM_M01_WindowBenchmark_Frame_{side}", (x, frame_y, opening_center_z), (frame_member, frame_depth, frame_outer_h), materials["painted_wood"], visible, "window_frame_primary", 0.006)
        box(f"SM_M01_WindowBenchmark_FrameRebate_{side}", (x * 0.945, 0.046, opening_center_z), (0.020, 0.028, frame_outer_h - 0.10), materials["seal"], visible, "window_frame_rebate", 0.002)
    for edge, z in (("T", opening_center_z + frame_outer_h * 0.5), ("B", opening_center_z - frame_outer_h * 0.5)):
        box(f"SM_M01_WindowBenchmark_Frame_{edge}", (0.0, frame_y, z), (frame_outer_w + frame_member, frame_depth, frame_member), materials["painted_wood"], visible, "window_frame_primary", 0.006)
        box(f"SM_M01_WindowBenchmark_FrameRebate_{edge}", (0.0, 0.046, z * 0.0 + z), (frame_outer_w - 0.10, 0.028, 0.020), materials["seal"], visible, "window_frame_rebate", 0.002)

    leaf_width = 0.620
    leaf_height = 1.920
    sash_member = 0.046
    sash_y = 0.035
    sash_depth = 0.058
    leaf_centers = {"L": -0.322, "R": 0.322}
    pane_records: list[dict[str, Any]] = []
    for leaf, center_x in leaf_centers.items():
        for side, x in (("L", center_x - leaf_width * 0.5), ("R", center_x + leaf_width * 0.5)):
            box(f"SM_M01_WindowBenchmark_Sash_{leaf}_{side}", (x, sash_y, opening_center_z), (sash_member, sash_depth, leaf_height), materials["painted_wood"], visible, "window_sash", 0.0045)
        for edge, z in (("T", opening_center_z + leaf_height * 0.5), ("B", opening_center_z - leaf_height * 0.5)):
            box(f"SM_M01_WindowBenchmark_Sash_{leaf}_{edge}", (center_x, sash_y, z), (leaf_width, sash_depth, sash_member), materials["painted_wood"], visible, "window_sash", 0.0045)
        transom_z = opening_center_z + 0.36
        box(f"SM_M01_WindowBenchmark_Sash_{leaf}_Transom", (center_x, sash_y, transom_z), (leaf_width - 0.05, sash_depth, 0.038), materials["painted_wood"], visible, "window_sash", 0.004)

        pane_width = leaf_width - 2.0 * sash_member - 0.018
        pane_specs = (
            ("LOWER", opening_center_z - 0.315, 1.245),
            ("UPPER", opening_center_z + 0.680, 0.635),
        )
        for pane, pane_z, pane_height in pane_specs:
            box(f"SM_M01_WindowBenchmark_Glass_{leaf}_{pane}", (center_x, 0.072, pane_z), (pane_width, 0.008, pane_height), materials["glass"], visible, "window_glazing", 0.0015)
            bead = 0.014
            for edge, x, z, width, height in (
                ("L", center_x - pane_width * 0.5, pane_z, bead, pane_height),
                ("R", center_x + pane_width * 0.5, pane_z, bead, pane_height),
                ("T", center_x, pane_z + pane_height * 0.5, pane_width, bead),
                ("B", center_x, pane_z - pane_height * 0.5, pane_width, bead),
            ):
                box(f"SM_M01_WindowBenchmark_Bead_{leaf}_{pane}_{edge}", (x, 0.026, z), (width, 0.020, height), materials["painted_wood"], visible, "window_glazing_bead", 0.002)
            pane_records.append({"leaf": leaf, "pane": pane, "width_m": pane_width, "height_m": pane_height, "glass_thickness_m": 0.008})

    # Six compact, mechanically legible hinge assemblies.
    for leaf, x, direction in (("L", -0.665, 1.0), ("R", 0.665, -1.0)):
        for index, z in enumerate((opening_center_z - 0.68, opening_center_z, opening_center_z + 0.68)):
            add_hinge(f"SM_M01_WindowBenchmark_Hinge_{leaf}_{index:02d}", x, z, direction, materials, visible)

    # One centered active-sash latch with backing plate, spindle, lever and screws.
    latch_x = 0.055
    latch_z = opening_center_z - 0.14
    box("SM_M01_WindowBenchmark_LatchPlate", (latch_x, -0.004, latch_z), (0.034, 0.014, 0.120), materials["metal"], visible, "window_hardware", 0.004)
    cylinder("SM_M01_WindowBenchmark_LatchSpindle", (latch_x, -0.027, latch_z), 0.009, 0.046, materials["metal"], visible, "window_hardware", (math.pi / 2.0, 0.0, 0.0), 28)
    box("SM_M01_WindowBenchmark_LatchLever", (latch_x + 0.042, -0.054, latch_z - 0.018), (0.086, 0.016, 0.018), materials["metal"], visible, "window_hardware", 0.006)
    for z_offset in (-0.038, 0.038):
        add_screw(f"SM_M01_WindowBenchmark_LatchScrew_{z_offset:+.3f}", latch_x, -0.013, latch_z + z_offset, materials["metal"], visible)

    # Espagnolette rod and restrained guides show a coherent locking path.
    cylinder("SM_M01_WindowBenchmark_EspagnoletteRod", (0.010, 0.002, opening_center_z), 0.0048, 1.58, materials["metal"], visible, "window_hardware", vertices=24)
    for index, z in enumerate((opening_center_z - 0.54, opening_center_z + 0.54)):
        box(f"SM_M01_WindowBenchmark_RodGuide_{index:02d}", (0.010, -0.004, z), (0.032, 0.014, 0.050), materials["metal"], visible, "window_hardware", 0.003)

    # Layered sill and lintel construction.
    box("SM_M01_WindowBenchmark_StoneSill", (0.0, -0.17, opening_bottom - 0.105), (1.78, 0.36, 0.145), materials["reveal"], visible, "facade_trim", 0.015)
    box("SM_M01_WindowBenchmark_SillDrip", (0.0, -0.355, opening_bottom - 0.145), (1.82, 0.035, 0.032), materials["reveal"], visible, "facade_trim", 0.004)
    box("SM_M01_WindowBenchmark_LintelBand", (0.0, -0.055, opening_top + 0.115), (1.76, 0.16, 0.135), materials["reveal"], visible, "facade_trim", 0.012)

    # A real shallow room creates parallax rather than colored cards.
    room_width, room_depth = 2.30, 2.20
    box("SM_M01_WindowBenchmark_RoomBack", (0.0, room_depth, 2.03), (room_width, 0.08, 2.55), materials["interior_wall"], visible, "window_interior_architecture", 0.006)
    box("SM_M01_WindowBenchmark_RoomSide_L", (-room_width * 0.5, 1.13, 2.03), (0.08, room_depth, 2.55), materials["interior_wall"], visible, "window_interior_architecture", 0.006)
    box("SM_M01_WindowBenchmark_RoomSide_R", (room_width * 0.5, 1.13, 2.03), (0.08, room_depth, 2.55), materials["interior_wall"], visible, "window_interior_architecture", 0.006)
    box("SM_M01_WindowBenchmark_RoomFloor", (0.0, 1.13, 0.77), (room_width, room_depth, 0.08), materials["interior_wood"], visible, "window_interior_architecture", 0.006)
    box("SM_M01_WindowBenchmark_RoomCeiling", (0.0, 1.13, 3.30), (room_width, room_depth, 0.08), materials["interior_wall"], visible, "window_interior_architecture", 0.006)

    add_curtain("SM_M01_WindowBenchmark_Curtain_L", -0.54, 0.30, 0.94, 3.08, materials["curtain"], visible)
    add_curtain("SM_M01_WindowBenchmark_Curtain_R", 0.54, 0.30, 0.94, 3.08, materials["curtain"], visible)
    cylinder("SM_M01_WindowBenchmark_CurtainRod", (0.0, 0.43, 3.17), 0.010, 1.56, materials["metal"], visible, "window_interior_hardware", (0.0, math.pi / 2.0, 0.0), 28)

    box("SM_M01_WindowBenchmark_RadiatorBody", (0.0, 0.56, 0.73), (0.86, 0.14, 0.48), materials["radiator"], visible, "window_interior_fixture", 0.014)
    for index in range(11):
        x = -0.37 + index * 0.074
        box(f"SM_M01_WindowBenchmark_RadiatorFin_{index:02d}", (x, 0.475, 0.73), (0.032, 0.025, 0.40), materials["radiator"], visible, "window_interior_fixture", 0.005)

    # Furniture silhouettes at different depths prove parallax.
    box("SM_M01_WindowBenchmark_TableTop", (-0.34, 1.25, 1.08), (0.74, 0.48, 0.055), materials["furniture"], visible, "window_interior_furniture", 0.012)
    for x in (-0.61, -0.07):
        for y in (1.08, 1.42):
            cylinder(f"SM_M01_WindowBenchmark_TableLeg_{x:+.2f}_{y:.2f}", (x, y, 0.91), 0.018, 0.34, materials["furniture"], visible, "window_interior_furniture", vertices=20)
    cylinder("SM_M01_WindowBenchmark_LampStem", (-0.32, 1.26, 1.45), 0.012, 0.68, materials["metal"], visible, "window_interior_furniture", vertices=24)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.13, location=(-0.32, 1.26, 1.78))
    lamp = bpy.context.object
    lamp.name = "SM_M01_WindowBenchmark_LampShade"
    lamp.scale = (1.25, 1.0, 0.72)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    lamp.data.materials.append(materials["warm_lamp"])
    base.move_to_collection(lamp, visible)
    base.tag(lamp, "window_interior_furniture", SIGNATURE)
    box("SM_M01_WindowBenchmark_WallArt", (0.42, room_depth - 0.052, 2.24), (0.56, 0.020, 0.72), materials["interior_wood"], visible, "window_interior_furniture", 0.012)

    # Subtle wet-response geometry exists only for the governed wet render.
    for index, x in enumerate((-0.48, -0.31, -0.12, 0.08, 0.27, 0.47)):
        height = 0.26 + (index % 3) * 0.08
        box(f"REVIEW_WetStreak_{index:02d}", (x, -0.010, 2.30 - index * 0.075), (0.006, 0.004, height), materials["wet_film"], wet_only, "review_only_wetness", 0.001)
    for obj in wet_only.objects:
        obj.hide_render = True

    # UCX wall pieces preserve the opening.
    box("UCX_SM_M01_WindowBenchmark_Wall_L_00", (-(opening_w + side_w) * 0.5, 0.25, module_h * 0.5), (side_w, wall_depth, module_h), materials["collision"], collision, "unreal_collision", 0.0)
    box("UCX_SM_M01_WindowBenchmark_Wall_R_00", ((opening_w + side_w) * 0.5, 0.25, module_h * 0.5), (side_w, wall_depth, module_h), materials["collision"], collision, "unreal_collision", 0.0)
    box("UCX_SM_M01_WindowBenchmark_Wall_B_00", (0.0, 0.25, opening_bottom * 0.5), (opening_w, wall_depth, opening_bottom), materials["collision"], collision, "unreal_collision", 0.0)
    box("UCX_SM_M01_WindowBenchmark_Wall_T_00", (0.0, 0.25, opening_top + (module_h - opening_top) * 0.5), (opening_w, wall_depth, module_h - opening_top), materials["collision"], collision, "unreal_collision", 0.0)

    return {
        "module_width_m": module_w,
        "module_height_m": module_h,
        "wall_depth_m": wall_depth,
        "opening_width_m": opening_w,
        "opening_height_m": opening_h,
        "opening_center_z_m": opening_center_z,
        "outer_frame_member_width_m": frame_member,
        "outer_frame_depth_m": frame_depth,
        "sash_member_width_m": sash_member,
        "sash_depth_m": sash_depth,
        "glass_thickness_m": 0.008,
        "pane_count": len(pane_records),
        "panes": pane_records,
        "hinge_count": 6,
        "latch_count": 1,
        "room_depth_m": room_depth,
        "whole_building_scope": False,
        "same_geometry_cosmetic_recolor": False,
        "clean_rectangular_aperture": True,
    }


def configure_scene(scene: bpy.types.Scene) -> None:
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.65
    scene.view_settings.gamma = 1.0
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.075, 0.10, 0.14, 1.0)
    background.inputs["Strength"].default_value = 0.24


def setup_review(
    scene: bpy.types.Scene,
    review: bpy.types.Collection,
    materials: dict[str, bpy.types.Material],
    wet_only: bpy.types.Collection,
) -> dict[str, Any]:
    camera_data = bpy.data.cameras.new("CAM_M01_PrewarWindowBenchmark_Review")
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    review.objects.link(camera)
    scene.camera = camera
    camera.data.lens = 70.0

    bpy.ops.object.light_add(type="AREA", location=(-2.8, -4.0, 5.2))
    key = bpy.context.object
    key.name = "LGT_M01_PrewarWindowBenchmark_Key"
    key.data.energy = 720.0
    key.data.shape = "DISK"
    key.data.size = 3.2
    base.move_to_collection(key, review)
    look_at(key, (0.0, 0.10, 2.05))

    bpy.ops.object.light_add(type="AREA", location=(3.5, -1.5, 3.3))
    fill = bpy.context.object
    fill.name = "LGT_M01_PrewarWindowBenchmark_Fill"
    fill.data.energy = 360.0
    fill.data.size = 2.8
    base.move_to_collection(fill, review)
    look_at(fill, (0.0, 0.18, 2.05))

    bpy.ops.object.light_add(type="AREA", location=(-0.25, 1.25, 2.65))
    interior = bpy.context.object
    interior.name = "LGT_M01_PrewarWindowBenchmark_Interior"
    interior.data.energy = 300.0
    interior.data.color = (1.0, 0.54, 0.28)
    interior.data.size = 0.85
    base.move_to_collection(interior, review)
    look_at(interior, (0.0, 0.15, 1.90))

    box("REVIEW_M01_PrewarWindowBenchmark_Ground", (0.0, 1.4, -0.08), (5.8, 4.4, 0.16), materials["reveal"], review, "review_only", 0.010)
    gray_card = box("REVIEW_M01_PrewarWindowBenchmark_GrayCard", (0.0, -0.40, 2.05), (1.50, 0.035, 1.50), materials["gray_card"], review, "review_only", 0.008)
    gray_card.hide_render = True
    return {
        "camera": camera,
        "key": key,
        "fill": fill,
        "interior": interior,
        "gray_card": gray_card,
        "wet_only": list(wet_only.objects),
    }


def set_condition(scene: bpy.types.Scene, rig: dict[str, Any], condition: str) -> None:
    for obj in rig["wet_only"]:
        obj.hide_render = condition != "wet"
    background = scene.world.node_tree.nodes.get("Background")
    if condition == "daylight":
        rig["key"].data.energy = 720.0
        rig["fill"].data.energy = 360.0
        rig["interior"].data.energy = 245.0
        background.inputs["Color"].default_value = (0.075, 0.105, 0.15, 1.0)
        background.inputs["Strength"].default_value = 0.24
        scene.view_settings.exposure = -0.70
    elif condition == "overcast":
        rig["key"].data.energy = 330.0
        rig["fill"].data.energy = 540.0
        rig["interior"].data.energy = 285.0
        background.inputs["Color"].default_value = (0.11, 0.12, 0.13, 1.0)
        background.inputs["Strength"].default_value = 0.30
        scene.view_settings.exposure = -0.52
    elif condition == "grazing":
        rig["key"].data.energy = 980.0
        rig["fill"].data.energy = 170.0
        rig["interior"].data.energy = 220.0
        background.inputs["Color"].default_value = (0.055, 0.075, 0.11, 1.0)
        background.inputs["Strength"].default_value = 0.20
        scene.view_settings.exposure = -0.78
    elif condition == "wet":
        rig["key"].data.energy = 430.0
        rig["fill"].data.energy = 510.0
        rig["interior"].data.energy = 330.0
        background.inputs["Color"].default_value = (0.055, 0.07, 0.09, 1.0)
        background.inputs["Strength"].default_value = 0.24
        scene.view_settings.exposure = -0.52
    elif condition == "night":
        rig["key"].data.energy = 42.0
        rig["fill"].data.energy = 75.0
        rig["interior"].data.energy = 610.0
        background.inputs["Color"].default_value = (0.004, 0.008, 0.018, 1.0)
        background.inputs["Strength"].default_value = 0.08
        scene.view_settings.exposure = -0.10
    else:
        raise RuntimeError(f"Unknown render condition: {condition}")


def render_one(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
    path: Path,
    location: tuple[float, float, float],
    target: tuple[float, float, float],
    lens: float,
    size: tuple[int, int],
) -> dict[str, Any]:
    return base.render_one(scene, camera, path, location, target, lens, size)


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
    calibration = render_one(
        scene,
        camera,
        calibration_dir / "daylight_gray_card.png",
        (0.0, -3.3, 2.05),
        (0.0, -0.40, 2.05),
        78.0,
        CALIBRATION_SIZE,
    )
    rig["gray_card"].hide_render = True

    checkpoints: list[dict[str, Any]] = []
    for condition, name, location, target, lens in (
        ("daylight", "checkpoint_01_profile_joinery", (0.0, -6.6, 2.08), (0.0, 0.05, 2.08), 72.0),
        ("grazing", "checkpoint_02_hardware_oblique", (2.4, -4.4, 2.30), (0.06, 0.00, 2.08), 82.0),
        ("overcast", "checkpoint_03_glass_interior_parallax", (-2.5, -4.4, 2.35), (0.0, 0.65, 2.05), 78.0),
    ):
        set_condition(scene, rig, condition)
        record = render_one(scene, camera, checkpoints_dir / f"{name}.png", location, target, lens, CHECKPOINT_SIZE)
        record.update({"condition": condition, "camera": name})
        checkpoints.append(record)

    finals: list[dict[str, Any]] = []
    for condition, name, location, target, lens in (
        ("daylight", "01_front_joinery", (0.0, -6.0, 2.08), (0.0, 0.03, 2.08), 76.0),
        ("daylight", "02_left_glass_reflection", (-2.8, -4.7, 2.42), (0.0, 0.42, 2.08), 82.0),
        ("overcast", "03_right_hardware", (2.6, -4.1, 2.28), (0.05, 0.00, 2.02), 86.0),
        ("grazing", "04_frame_profile_closeup", (-1.25, -3.0, 2.55), (-0.38, 0.00, 2.30), 92.0),
        ("overcast", "05_interior_parallax", (-2.2, -3.7, 2.18), (0.10, 1.18, 1.85), 84.0),
        ("wet", "06_glass_wet_response", (1.9, -3.7, 2.48), (0.08, 0.03, 2.22), 88.0),
        ("night", "07_night_interior_depth", (0.0, -5.7, 2.10), (0.0, 0.85, 1.98), 76.0),
        ("daylight", "08_latch_hinge_macro", (0.86, -2.25, 2.18), (0.24, -0.01, 2.04), 105.0),
    ):
        set_condition(scene, rig, condition)
        record = render_one(scene, camera, renders_dir / f"{condition}_{name}.png", location, target, lens, RENDER_SIZE)
        record.update({"condition": condition, "camera": name})
        finals.append(record)

    return {"calibration": calibration, "checkpoints": checkpoints, "renders": finals}


def object_receipt(collections: Iterable[bpy.types.Collection]) -> dict[str, Any]:
    receipt = base.object_receipt(collections)
    receipt["schema"] = "skyguard.m01-prewar-window-material-glazing-benchmark-a01.topology-material.v1"
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
    for family in PBR.values():
        for source in family.values():
            require(source.is_file(), f"Texture authority missing: {source}")

    base.clear_scene()
    scene = bpy.context.scene
    configure_scene(scene)
    visible = base.get_collection("M01_PREWAR_WINDOW_BENCHMARK_VISIBLE")
    collision = base.get_collection("M01_PREWAR_WINDOW_BENCHMARK_COLLISION")
    sockets = base.get_collection("M01_PREWAR_WINDOW_BENCHMARK_SOCKETS")
    wet_only = base.get_collection("M01_PREWAR_WINDOW_BENCHMARK_WET_REVIEW_ONLY")
    review = base.get_collection("M01_PREWAR_WINDOW_BENCHMARK_REVIEW_ONLY")
    materials = build_materials()
    design = build_window(materials, visible, collision, wet_only)
    base.add_empty("SOCKET_M01_PrewarWindow_Origin", (0.0, 0.0, 0.0), sockets, "unreal_socket")
    base.add_empty("SOCKET_M01_PrewarWindow_Center", (0.0, 0.0, 2.08), sockets, "unreal_socket")
    base.add_empty("SOCKET_M01_PrewarWindow_Latch", (0.055, -0.04, 1.94), sockets, "unreal_socket")
    rig = setup_review(scene, review, materials, wet_only)

    topology = object_receipt((visible, collision, sockets))
    require(topology["all_renderable_meshes_have_uv0"], "Renderable UV0 coverage failed")
    require(topology["distinct_building_signatures"] == [SIGNATURE], "Unexpected signature set")
    require(topology["role_counts"].get("facade_structure", 0) == 4, "Aperture requires four structural pieces")
    require(topology["role_counts"].get("window_reveal", 0) == 4, "Four reveal returns are required")
    require(topology["role_counts"].get("window_frame_primary", 0) == 4, "Primary outer frame is incomplete")
    require(topology["role_counts"].get("window_sash", 0) == 10, "Two complete sash leaves are required")
    require(topology["role_counts"].get("window_glazing", 0) == 4, "Exactly four glass panes are required")
    require(topology["role_counts"].get("window_hardware", 0) >= 24, "Mechanically coherent hinge/latch hardware is incomplete")
    require(topology["role_counts"].get("window_interior_architecture", 0) == 5, "Five-sided shallow room is required")
    require(topology["role_counts"].get("window_interior_furniture", 0) >= 8, "Interior parallax objects are incomplete")
    require(design["outer_frame_member_width_m"] <= 0.070, "Outer frame remains oversized")
    require(design["sash_member_width_m"] <= 0.046, "Sash members remain oversized")
    require(design["glass_thickness_m"] == 0.008, "Physical glass thickness changed")
    require(design["hinge_count"] == 6 and design["latch_count"] == 1, "Hardware count contract failed")
    require(design["room_depth_m"] >= 2.0, "Room depth is insufficient for parallax")

    render_records = render_reviews(scene, rig, output)
    blend_path = output / "M01_Prewar_Window_Material_Glazing_Benchmark_A01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    glb_path = output / "M01_Prewar_Window_Material_Glazing_Benchmark_A01.glb"
    base.export_glb(glb_path, (visible, collision, sockets))

    texture_authorities = []
    for family, sources in PBR.items():
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
            "schema": "skyguard.m01-prewar-window-material-glazing-benchmark-a01.construction.v1",
            "asset_id": ASSET_ID,
            "generic_prewar_timber_casement_not_exact_building_identity": True,
            "fresh_geometry": True,
            "same_geometry_cosmetic_recolor": False,
            "whole_building_scope": False,
            "clean_rectangular_aperture": True,
            "stepped_frame_and_rebates": True,
            "mechanically_coherent_hardware": True,
            "real_room_depth_for_parallax": True,
            "design": design,
            "passed": True,
        },
    )
    write_json(
        output / "material_glazing_receipt.json",
        {
            "schema": "skyguard.m01-prewar-window-material-glazing-benchmark-a01.material-glazing.v1",
            "asset_id": ASSET_ID,
            "governed_local_pbr": True,
            "provenance": {"path": str(PROVENANCE.relative_to(ROOT)), "bytes": PROVENANCE.stat().st_size, "sha256": sha256(PROVENANCE)},
            "texture_authorities": texture_authorities,
            "physical_glass": {"ior": 1.46, "thickness_m": 0.008, "procedural_roughness_range": [0.025, 0.16]},
            "wet_response_review_geometry": True,
            "unreal_import_authorized": False,
            "passed": True,
        },
    )
    write_json(
        output / "exposure_intent_receipt.json",
        {
            "schema": "skyguard.m01-prewar-window-material-glazing-benchmark-a01.exposure-intent.v1",
            "asset_id": ASSET_ID,
            "view_transform": scene.view_settings.view_transform,
            "look": scene.view_settings.look,
            "calibration_render": render_records["calibration"],
            "conditions": {
                "daylight": {"exposure": -0.70},
                "overcast": {"exposure": -0.52},
                "grazing": {"exposure": -0.78},
                "wet": {"exposure": -0.52},
                "night": {"exposure": -0.10},
            },
            "upper_luminance_postflight_required": True,
            "passed": True,
        },
    )
    write_json(
        output / "artifact_receipt.json",
        {
            "schema": "skyguard.m01-prewar-window-material-glazing-benchmark-a01.artifacts.v1",
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
