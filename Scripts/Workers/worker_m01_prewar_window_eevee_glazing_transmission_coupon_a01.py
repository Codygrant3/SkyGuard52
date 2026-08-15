"""Build a bounded Blender 5.2 Eevee glazing-transmission coupon.

The coupon exists because the preceding physical-window benchmark used a pure
Glass BSDF that passed full-frame luminance checks while rendering the panes as
opaque black/white bands.  This diagnostic asset compares two Eevee-compatible
transparent/reflection approaches against the same depth targets.  It is not a
runtime building asset and can never authorize Unreal import by itself.
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


ASSET_ID = "m01-prewar-window-eevee-glazing-transmission-coupon-a01"
GATE = "M01_PREWAR_WINDOW_EEVEE_GLAZING_TRANSMISSION_COUPON_A01"
SIGNATURE = "A_EEVEE_GLAZING_TRANSMISSION_COUPON"
CALIBRATION_SIZE = (512, 512)
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


def material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float,
    metallic: float = 0.0,
    emission: float = 0.0,
) -> bpy.types.Material:
    value = bpy.data.materials.new(name)
    value.use_nodes = True
    value.diffuse_color = color
    bsdf = value.node_tree.nodes.get("Principled BSDF")
    require(bsdf is not None, f"Missing Principled BSDF for {name}")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    emission_color = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if emission_color is not None:
        emission_color.default_value = color
    emission_strength = bsdf.inputs.get("Emission Strength")
    if emission_strength is not None:
        emission_strength.default_value = emission
    return value


def configure_transparency(value: bpy.types.Material) -> None:
    if hasattr(value, "surface_render_method"):
        value.surface_render_method = "DITHERED"
    if hasattr(value, "use_transparency_overlap"):
        value.use_transparency_overlap = False


def alpha_principled_glazing() -> bpy.types.Material:
    value = bpy.data.materials.new("M_COUPON_Glass_A_PrincipledAlpha")
    value.use_nodes = True
    value.diffuse_color = (0.56, 0.72, 0.76, 0.14)
    configure_transparency(value)
    bsdf = value.node_tree.nodes.get("Principled BSDF")
    require(bsdf is not None, "Candidate A Principled BSDF is missing")
    bsdf.inputs["Base Color"].default_value = (0.19, 0.31, 0.34, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.095
    bsdf.inputs["IOR"].default_value = 1.46
    bsdf.inputs["Alpha"].default_value = 0.14
    coat = bsdf.inputs.get("Coat Weight")
    if coat is not None:
        coat.default_value = 0.18
    return value


def fresnel_transparent_glazing() -> bpy.types.Material:
    value = bpy.data.materials.new("M_COUPON_Glass_B_FresnelTransparentMix")
    value.use_nodes = True
    value.diffuse_color = (0.62, 0.77, 0.80, 0.10)
    configure_transparency(value)
    nodes = value.node_tree.nodes
    links = value.node_tree.links
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
    return value


def box(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    role: str,
    bevel: float = 0.006,
) -> bpy.types.Object:
    return base.add_box(name, location, dimensions, mat, collection, role, bevel, SIGNATURE)


def build_coupon(
    visible: bpy.types.Collection,
    sockets: bpy.types.Collection,
    mats: dict[str, bpy.types.Material],
) -> dict[str, Any]:
    centers = {"A": -0.72, "B": 0.72}
    pane_width = 0.72
    pane_height = 1.48
    pane_z = 1.55
    frame_member = 0.052

    box("SM_COUPON_Wall_L", (-1.52, 0.26, 1.45), (0.42, 0.38, 2.90), mats["wall"], visible, "coupon_wall", 0.012)
    box("SM_COUPON_Wall_C", (0.0, 0.26, 1.45), (0.34, 0.38, 2.90), mats["wall"], visible, "coupon_wall", 0.012)
    box("SM_COUPON_Wall_R", (1.52, 0.26, 1.45), (0.42, 0.38, 2.90), mats["wall"], visible, "coupon_wall", 0.012)
    box("SM_COUPON_Wall_T", (0.0, 0.26, 2.72), (2.66, 0.38, 0.36), mats["wall"], visible, "coupon_wall", 0.012)
    box("SM_COUPON_Wall_B", (0.0, 0.26, 0.20), (2.66, 0.38, 0.40), mats["wall"], visible, "coupon_wall", 0.012)

    panes: dict[str, str] = {}
    for key, center in centers.items():
        for side, x in (("L", center - pane_width * 0.5), ("R", center + pane_width * 0.5)):
            box(f"SM_COUPON_Frame_{key}_{side}", (x, 0.02, pane_z), (frame_member, 0.09, pane_height + 0.10), mats["frame"], visible, "coupon_frame", 0.005)
        for edge, z in (("T", pane_z + pane_height * 0.5), ("B", pane_z - pane_height * 0.5)):
            box(f"SM_COUPON_Frame_{key}_{edge}", (center, 0.02, z), (pane_width + 0.10, 0.09, frame_member), mats["frame"], visible, "coupon_frame", 0.005)
        pane_name = f"SM_COUPON_Glass_{key}"
        box(pane_name, (center, -0.010, pane_z), (pane_width, 0.008, pane_height), mats[f"glass_{key.lower()}"], visible, "coupon_glazing", 0.001)
        panes[key] = pane_name

        # Identical foreground and background depth targets behind each pane.
        box(f"SM_COUPON_Target_{key}_Near", (center - 0.16, 0.74, 1.38), (0.16, 0.16, 0.92), mats["target_near"], visible, "coupon_depth_target", 0.012)
        box(f"SM_COUPON_Target_{key}_Mid", (center + 0.14, 1.08, 1.62), (0.20, 0.12, 1.16), mats["target_mid"], visible, "coupon_depth_target", 0.010)
        box(f"SM_COUPON_Target_{key}_Far", (center - 0.04, 1.52, 1.26), (0.42, 0.08, 0.34), mats["target_far"], visible, "coupon_depth_target", 0.008)
        for index, offset in enumerate((-0.22, 0.0, 0.22)):
            box(f"SM_COUPON_Shelf_{key}_{index:02d}", (center + offset, 1.68, 1.00 + index * 0.38), (0.12, 0.06, 0.28), mats["books"], visible, "coupon_depth_target", 0.006)

    box("SM_COUPON_RoomBack", (0.0, 1.82, 1.48), (3.0, 0.08, 2.52), mats["room"], visible, "coupon_room", 0.008)
    box("SM_COUPON_RoomFloor", (0.0, 1.02, 0.40), (3.0, 1.65, 0.08), mats["floor"], visible, "coupon_room", 0.008)
    base.add_empty("SOCKET_COUPON_Origin", (0.0, 0.0, 0.0), sockets, "unreal_socket")
    base.add_empty("SOCKET_COUPON_Pane_A", (centers["A"], -0.010, pane_z), sockets, "unreal_socket")
    base.add_empty("SOCKET_COUPON_Pane_B", (centers["B"], -0.010, pane_z), sockets, "unreal_socket")
    return {
        "pane_width_m": pane_width,
        "pane_height_m": pane_height,
        "pane_thickness_m": 0.008,
        "ior": 1.46,
        "candidate_a": "Principled alpha/dithered",
        "candidate_b": "Transparent-Principled Fresnel mix/dithered",
        "pane_nodes": panes,
    }


def configure_scene(scene: bpy.types.Scene) -> None:
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.60
    scene.view_settings.gamma = 1.0
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.055, 0.075, 0.11, 1.0)
    background.inputs["Strength"].default_value = 0.20


def setup_review(scene: bpy.types.Scene, review: bpy.types.Collection, mats: dict[str, bpy.types.Material]) -> dict[str, Any]:
    camera_data = bpy.data.cameras.new("CAM_COUPON_Review")
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    review.objects.link(camera)
    scene.camera = camera

    bpy.ops.object.light_add(type="AREA", location=(-2.4, -3.0, 4.6))
    key = bpy.context.object
    key.name = "LGT_COUPON_Key"
    key.data.energy = 620.0
    key.data.shape = "DISK"
    key.data.size = 3.0
    base.move_to_collection(key, review)
    look_at(key, (0.0, 0.25, 1.50))

    bpy.ops.object.light_add(type="AREA", location=(2.5, -1.4, 3.2))
    fill = bpy.context.object
    fill.name = "LGT_COUPON_Fill"
    fill.data.energy = 340.0
    fill.data.size = 2.2
    base.move_to_collection(fill, review)
    look_at(fill, (0.0, 0.30, 1.45))

    bpy.ops.object.light_add(type="AREA", location=(0.0, 1.10, 2.45))
    interior = bpy.context.object
    interior.name = "LGT_COUPON_Interior"
    interior.data.energy = 460.0
    interior.data.color = (1.0, 0.58, 0.30)
    interior.data.size = 1.25
    base.move_to_collection(interior, review)
    look_at(interior, (0.0, 0.80, 1.25))

    gray = box("REVIEW_COUPON_GrayCard", (0.0, -0.45, 1.50), (1.35, 0.025, 1.35), mats["gray"], review, "review_only", 0.005)
    gray.hide_render = True
    return {"camera": camera, "key": key, "fill": fill, "interior": interior, "gray": gray}


def set_condition(scene: bpy.types.Scene, rig: dict[str, Any], condition: str) -> None:
    background = scene.world.node_tree.nodes.get("Background")
    if condition == "daylight":
        rig["key"].data.energy = 620.0
        rig["fill"].data.energy = 340.0
        rig["interior"].data.energy = 460.0
        background.inputs["Strength"].default_value = 0.20
        scene.view_settings.exposure = -0.60
    elif condition == "overcast":
        rig["key"].data.energy = 280.0
        rig["fill"].data.energy = 480.0
        rig["interior"].data.energy = 500.0
        background.inputs["Strength"].default_value = 0.28
        scene.view_settings.exposure = -0.44
    elif condition == "night":
        rig["key"].data.energy = 28.0
        rig["fill"].data.energy = 55.0
        rig["interior"].data.energy = 690.0
        background.inputs["Strength"].default_value = 0.05
        scene.view_settings.exposure = -0.10
    else:
        raise RuntimeError(f"Unknown condition: {condition}")


def render_reviews(scene: bpy.types.Scene, rig: dict[str, Any], output: Path) -> dict[str, Any]:
    calibration_dir = output / "calibration"
    checkpoints_dir = output / "checkpoints"
    renders_dir = output / "renders"
    calibration_dir.mkdir()
    checkpoints_dir.mkdir()
    renders_dir.mkdir()
    camera = rig["camera"]

    set_condition(scene, rig, "daylight")
    rig["gray"].hide_render = False
    calibration = base.render_one(scene, camera, calibration_dir / "gray_card.png", (0.0, -3.0, 1.50), (0.0, -0.45, 1.50), 78.0, CALIBRATION_SIZE)
    rig["gray"].hide_render = True

    checkpoints: list[dict[str, Any]] = []
    for condition, name, location, target, lens in (
        ("daylight", "checkpoint_01_front_transmission", (0.0, -5.1, 1.48), (0.0, 0.65, 1.45), 70.0),
        ("overcast", "checkpoint_02_left_oblique_parallax", (-2.5, -4.1, 1.72), (0.0, 0.92, 1.45), 76.0),
        ("overcast", "checkpoint_03_right_oblique_parallax", (2.5, -4.1, 1.72), (0.0, 0.92, 1.45), 76.0),
    ):
        set_condition(scene, rig, condition)
        record = base.render_one(scene, camera, checkpoints_dir / f"{name}.png", location, target, lens, CHECKPOINT_SIZE)
        record.update({"condition": condition, "camera": name})
        checkpoints.append(record)

    finals: list[dict[str, Any]] = []
    for condition, name, location, target, lens in (
        ("daylight", "daylight_front_both_candidates", (0.0, -5.5, 1.48), (0.0, 0.72, 1.45), 72.0),
        ("daylight", "daylight_candidate_a_oblique", (-2.2, -3.8, 1.65), (-0.55, 0.86, 1.44), 82.0),
        ("daylight", "daylight_candidate_b_oblique", (2.2, -3.8, 1.65), (0.55, 0.86, 1.44), 82.0),
        ("overcast", "overcast_front_both_candidates", (0.0, -5.3, 1.48), (0.0, 0.74, 1.45), 72.0),
        ("night", "night_front_interior_visibility", (0.0, -5.2, 1.48), (0.0, 0.82, 1.42), 72.0),
        ("night", "night_candidate_b_oblique", (2.0, -3.7, 1.62), (0.50, 0.94, 1.42), 82.0),
    ):
        set_condition(scene, rig, condition)
        record = base.render_one(scene, camera, renders_dir / f"{name}.png", location, target, lens, RENDER_SIZE)
        record.update({"condition": condition, "camera": name})
        finals.append(record)
    return {"calibration": calibration, "checkpoints": checkpoints, "renders": finals}


def receipt(collections: Iterable[bpy.types.Collection]) -> dict[str, Any]:
    value = base.object_receipt(collections)
    value["schema"] = "skyguard.m01-prewar-window-eevee-glazing-transmission-coupon-a01.topology.v1"
    roles: dict[str, int] = {}
    for record in value["objects"]:
        role = str(record.get("role") or "unclassified")
        roles[role] = roles.get(role, 0) + 1
    value["role_counts"] = dict(sorted(roles.items()))
    value["passed"] = True
    return value


def main() -> int:
    args = parse_args()
    require(args.asset_id == ASSET_ID, f"Unexpected asset id: {args.asset_id}")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    require(not any(output.iterdir()), f"Output directory is not empty: {output}")

    base.clear_scene()
    scene = bpy.context.scene
    configure_scene(scene)
    visible = base.get_collection("M01_GLAZING_COUPON_VISIBLE")
    sockets = base.get_collection("M01_GLAZING_COUPON_SOCKETS")
    review = base.get_collection("M01_GLAZING_COUPON_REVIEW_ONLY")
    mats = {
        "wall": material("M_COUPON_Wall", (0.39, 0.36, 0.31, 1.0), 0.76),
        "frame": material("M_COUPON_Frame", (0.18, 0.26, 0.22, 1.0), 0.42),
        "room": material("M_COUPON_Room", (0.31, 0.27, 0.22, 1.0), 0.84),
        "floor": material("M_COUPON_Floor", (0.18, 0.11, 0.06, 1.0), 0.58),
        "target_near": material("M_COUPON_TargetNear", (0.55, 0.07, 0.035, 1.0), 0.44),
        "target_mid": material("M_COUPON_TargetMid", (0.04, 0.19, 0.46, 1.0), 0.48),
        "target_far": material("M_COUPON_TargetFar", (0.70, 0.38, 0.05, 1.0), 0.52, emission=0.18),
        "books": material("M_COUPON_Books", (0.14, 0.47, 0.18, 1.0), 0.56),
        "glass_a": alpha_principled_glazing(),
        "glass_b": fresnel_transparent_glazing(),
        "gray": material("M_COUPON_18PercentGray", (0.18, 0.18, 0.18, 1.0), 0.62),
    }
    design = build_coupon(visible, sockets, mats)
    rig = setup_review(scene, review, mats)
    topology = receipt((visible, sockets))
    require(topology["all_renderable_meshes_have_uv0"], "Renderable UV0 coverage failed")
    require(topology["role_counts"].get("coupon_glazing", 0) == 2, "Exactly two candidate panes are required")
    require(topology["role_counts"].get("coupon_depth_target", 0) >= 12, "Depth target set is incomplete")

    render_records = render_reviews(scene, rig, output)
    blend_path = output / "M01_Prewar_Window_Eevee_Glazing_Transmission_Coupon_A01.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    glb_path = output / "M01_Prewar_Window_Eevee_Glazing_Transmission_Coupon_A01.glb"
    base.export_glb(glb_path, (visible, sockets))

    write_json(output / "topology_receipt.json", topology)
    write_json(
        output / "shader_candidate_receipt.json",
        {
            "schema": "skyguard.m01-prewar-window-eevee-glazing-transmission-coupon-a01.shader-candidates.v1",
            "asset_id": ASSET_ID,
            "blender_engine": scene.render.engine,
            "pure_glass_bsdf_reused": False,
            "pane_thickness_m": 0.008,
            "ior": 1.46,
            "candidate_a": {"method": "principled_alpha_dithered", "alpha": 0.14, "roughness": 0.095},
            "candidate_b": {"method": "transparent_principled_fresnel_mix_dithered", "ior": 1.46, "reflection_roughness": 0.11},
            "same_depth_targets_for_both_candidates": True,
            "unreal_import_authorized": False,
            "passed": True,
        },
    )
    write_json(
        output / "visibility_intent_receipt.json",
        {
            "schema": "skyguard.m01-prewar-window-eevee-glazing-transmission-coupon-a01.visibility-intent.v1",
            "asset_id": ASSET_ID,
            "front_candidate_a_roi_normalized": [0.25, 0.28, 0.45, 0.80],
            "front_candidate_b_roi_normalized": [0.55, 0.28, 0.75, 0.80],
            "pane_local_gate_required": True,
            "minimum_pane_luminance_stddev_required": True,
            "left_right_oblique_parallax_proof_required": True,
            "direct_full_resolution_review_required": True,
            "passed": True,
        },
    )
    write_json(
        output / "artifact_receipt.json",
        {
            "schema": "skyguard.m01-prewar-window-eevee-glazing-transmission-coupon-a01.artifacts.v1",
            "asset_id": ASSET_ID,
            "blend": {"path": str(blend_path), "bytes": blend_path.stat().st_size, "sha256": sha256(blend_path)},
            "glb": {"path": str(glb_path), "bytes": glb_path.stat().st_size, "sha256": sha256(glb_path)},
            "calibration_count": 1,
            "checkpoint_count": len(render_records["checkpoints"]),
            "final_render_count": len(render_records["renders"]),
            "total_render_count": 1 + len(render_records["checkpoints"]) + len(render_records["renders"]),
            "unreal_import_authorized": False,
            "passed": True,
        },
    )
    print(json.dumps({"gate": GATE, "classification": "PASSED_AUTOMATIC_AWAITING_POSTFLIGHT_AND_DIRECT_VISUAL_REVIEW", "design": design}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
