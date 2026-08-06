"""Three-image D3D12 proof for Attempt07 diagnostic materials and camera order."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_attempt06_contract import load_attempt06_contract
from verify_skyguard_phase4_m01_landscape_visible_gpu_gate import (
    decode_png_rgb8,
    srgb8_to_linear,
)


CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_CONTRACT.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def parse_switch(name: str) -> str:
    command_line = unreal.SystemLibrary.get_command_line()
    match = re.search(
        rf'(?:^|\s)-{re.escape(name)}=(?:"([^"]+)"|(\S+))',
        command_line,
        re.IGNORECASE,
    )
    if not match:
        raise RuntimeError("Missing required -" + name + " switch")
    return match.group(1) or match.group(2)


def find_landscape(effective: dict):
    label = effective["candidate"]["landscape_actor_label"]
    tag = unreal.Name(effective["candidate"]["landscape_actor_tag"])
    matches = []
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_class().get_name() not in {
            "Landscape",
            "LandscapeStreamingProxy",
        }:
            continue
        if (
            actor.get_actor_label() == label
            and tag in list(actor.get_editor_property("tags") or [])
        ):
            matches.append(actor)
    if len(matches) != 1:
        raise RuntimeError(
            "Expected exactly one governed Landscape; found "
            + str(len(matches))
        )
    return matches[0]


def camera_transform(spec: dict) -> tuple:
    rotation = spec["rotation_degrees"]
    return (
        unreal.Vector(*spec["location_cm"]),
        unreal.Rotator(
            pitch=rotation["pitch"],
            yaw=rotation["yaw"],
            roll=rotation["roll"],
        ),
    )


def apply_material(authoring, landscape, material) -> dict:
    audit = authoring.set_transient_landscape_diagnostic_material_synchronized(
        landscape, material
    )
    result = {
        "success": bool(audit.success),
        "landscape_component_count": int(audit.landscape_component_count),
        "visible_component_count": int(audit.visible_component_count),
        "registered_component_count": int(audit.registered_component_count),
        "render_state_created_component_count": int(
            audit.render_state_created_component_count
        ),
        "generated_material_instance_count": int(
            audit.generated_material_instance_ready_component_count
        ),
        "material_parent_match_count": int(
            audit.governed_material_parent_match_component_count
        ),
        "error": str(audit.error),
    }
    if not (
        result["success"]
        and result["landscape_component_count"] == 16
        and result["visible_component_count"] == 16
        and result["registered_component_count"] == 16
        and result["render_state_created_component_count"] == 16
        and result["generated_material_instance_count"] == 16
        and result["material_parent_match_count"] == 16
    ):
        raise RuntimeError(
            "Attempt07 transient material audit failed: "
            + json.dumps(result)
        )
    return result


def capture_one(
    authoring,
    landscape,
    spec: dict,
    mode,
    output: Path,
    width: int,
    height: int,
    fov: float,
) -> dict:
    world = unreal.EditorLevelLibrary.get_editor_world()
    target = unreal.RenderingLibrary.create_render_target2d(
        world,
        width,
        height,
        unreal.TextureRenderTargetFormat.RTF_RGBA8,
    )
    target.set_editor_property(
        "clear_color", unreal.LinearColor(0.0, 0.0, 0.0, 1.0)
    )
    capture = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator()
    )
    if capture is None:
        raise RuntimeError("Could not spawn Attempt07 tiny SceneCapture")
    try:
        component = capture.capture_component2d
        component.set_editor_property("texture_target", target)
        component.set_editor_property(
            "capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR
        )
        component.set_editor_property("capture_every_frame", False)
        component.set_editor_property("capture_on_movement", False)
        component.set_editor_property("fov_angle", fov)
        location, rotation = camera_transform(spec)
        # Attempt06 configured and flushed before this transform. Attempt07
        # makes the contract camera part of the synchronized render state.
        capture.set_actor_location(location, False, False)
        capture.set_actor_rotation(rotation, False)
        configured = authoring.configure_landscape_scene_capture_diagnostic(
            component, landscape, mode
        )
        configuration = {
            "success": bool(configured.success),
            "show_only_component_count": int(
                configured.show_only_landscape_component_count
            ),
            "generated_material_instance_count": int(
                configured.generated_material_instance_ready_component_count
            ),
            "material_parent_match_count": int(
                configured.diagnostic_material_parent_match_component_count
            ),
            "render_thread_synchronized": bool(
                configured.render_thread_synchronized
            ),
            "error": str(configured.error),
        }
        if not (
            configuration["success"]
            and configuration["show_only_component_count"] == 16
            and configuration["generated_material_instance_count"] == 16
            and configuration["material_parent_match_count"] == 16
            and configuration["render_thread_synchronized"]
        ):
            raise RuntimeError(
                "Attempt07 tiny capture configuration failed: "
                + json.dumps(configuration)
            )
        component.capture_scene()
        output.parent.mkdir(parents=True, exist_ok=True)
        unreal.RenderingLibrary.export_render_target(
            world, target, str(output.parent), output.name
        )
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError("Attempt07 tiny capture missing: " + str(output))
        configuration.update(
            {
                "camera_id": spec["id"],
                "exact_location_cm": list(spec["location_cm"]),
                "exact_rotation_degrees": dict(spec["rotation_degrees"]),
                "transform_applied_before_configuration": True,
                "fov_degrees": fov,
                "output": str(output),
                "sha256": sha256_file(output),
            }
        )
        return configuration
    finally:
        unreal.EditorLevelLibrary.destroy_actor(capture)


def coverage_analysis(path: Path, white_minimum: int) -> dict:
    width, height, rgb = decode_png_rgb8(path)
    white = sum(
        min(rgb[index : index + 3]) >= white_minimum
        for index in range(0, len(rgb), 3)
    )
    return {
        "dimensions": [width, height],
        "white_rgb8_minimum": white_minimum,
        "white_pixel_count": white,
        "white_fraction": white / (width * height),
        "maximum_rgb8": max(rgb),
    }


def palette_analysis(path: Path, tolerance_rgb8: int) -> dict:
    width, height, rgb = decode_png_rgb8(path)
    expected = []
    for y_index in range(2):
        for x_index in range(8):
            component_id = x_index + 8 * y_index
            expected.append(
                (
                    component_id,
                    (x_index + 1) / 9.0,
                    (y_index + 1) / 3.0,
                    0.25
                    + 0.75
                    * (
                        component_id * 0.61803398875
                        - math.floor(component_id * 0.61803398875)
                    ),
                )
            )
    tolerance = tolerance_rgb8 / 255.0
    counts = {str(item[0]): 0 for item in expected}
    for index in range(0, len(rgb), 3):
        pixel = tuple(
            srgb8_to_linear(channel) for channel in rgb[index : index + 3]
        )
        best_id = None
        best_distance = float("inf")
        for component_id, red, green, blue in expected:
            distance = max(
                abs(pixel[0] - red),
                abs(pixel[1] - green),
                abs(pixel[2] - blue),
            )
            if distance <= tolerance and distance < best_distance:
                best_id = component_id
                best_distance = distance
        if best_id is not None:
            counts[str(best_id)] += 1
    return {
        "dimensions": [width, height],
        "tolerance_rgb8_per_channel": tolerance_rgb8,
        "pixel_counts": counts,
        "matching_id_count": sum(value > 0 for value in counts.values()),
    }


def main() -> None:
    contract = json.loads(
        CONTRACT_PATH.read_text(encoding="utf-8-sig")
    )
    output_root = Path(parse_switch("SkyguardAttempt07TinyProofRoot"))
    author_receipt = Path(parse_switch("SkyguardAttempt07AuthorReceipt"))
    proof_receipt = output_root / "tiny_proof_receipt.json"
    if proof_receipt.exists() or (output_root / "captures").exists():
        raise RuntimeError("Attempt07 tiny proof output already exists")
    if not author_receipt.is_file():
        raise RuntimeError("Attempt07 author receipt is missing")
    authored = json.loads(author_receipt.read_text(encoding="utf-8-sig"))
    if authored.get("gate") != "PASS":
        raise RuntimeError("Attempt07 author receipt did not pass")
    rhi = (
        unreal.SkyguardMission01EnvironmentAuthoringLibrary
        .get_active_rhi_and_feature_level()
        .strip()
        .upper()
    )
    if rhi != contract["tiny_live_proof"]["rhi_required"]:
        raise RuntimeError("Attempt07 tiny proof requires D3D12|SM6: " + rhi)
    locked_before = {}
    for name, item in contract["locked_production_packages"].items():
        digest = sha256_file(ROOT / item["file"])
        if digest != item["sha256"]:
            raise RuntimeError("Locked package hash failed: " + name)
        locked_before[name] = digest
    outputs = contract["new_immutable_outputs"]
    for name in ("coverage_material", "component_id_material"):
        path = ROOT / outputs[name]["file"]
        if sha256_file(path) != authored["output_hashes"][name]:
            raise RuntimeError("Attempt07 authored material hash changed: " + name)
    effective = load_attempt06_contract()
    candidate_map = effective["candidate"]["immutable_map"]
    if not unreal.EditorLevelLibrary.load_level(candidate_map):
        raise RuntimeError("Could not load Attempt06 candidate map read-only")
    landscape = find_landscape(effective)
    authoring = unreal.SkyguardMission01EnvironmentAuthoringLibrary
    governed = unreal.load_asset(effective["candidate"]["landscape_material"])
    coverage = unreal.load_asset(outputs["coverage_material"]["asset"])
    component = unreal.load_asset(outputs["component_id_material"]["asset"])
    if not governed or not coverage or not component:
        raise RuntimeError("Attempt07 material set is incomplete")
    usage = {
        "coverage": bool(coverage.get_editor_property("used_with_landscape")),
        "component_id": bool(
            component.get_editor_property("used_with_landscape")
        ),
    }
    if not all(usage.values()):
        raise RuntimeError("Attempt07 Landscape usage flag is absent")
    specs = {
        item["id"]: item for item in effective["capture"]["cameras"]
    }
    proof = contract["tiny_live_proof"]
    width, height = proof["resolution"]
    captures_root = output_root / "captures"
    capture_records = []
    material_audits = {}
    try:
        material_audits["coverage"] = apply_material(
            authoring, landscape, coverage
        )
        coverage_c05 = captures_root / "coverage_C05.png"
        coverage_c04 = captures_root / "coverage_C04.png"
        capture_records.append(
            capture_one(
                authoring,
                landscape,
                specs["C05_COVERAGE_HIGH"],
                unreal.SkyguardLandscapeCaptureDiagnosticMode.LANDSCAPE_COVERAGE,
                coverage_c05,
                width,
                height,
                proof["fov_degrees"],
            )
        )
        capture_records.append(
            capture_one(
                authoring,
                landscape,
                specs["C04_INLAND_CLOSE"],
                unreal.SkyguardLandscapeCaptureDiagnosticMode.LANDSCAPE_COVERAGE,
                coverage_c04,
                width,
                height,
                proof["fov_degrees"],
            )
        )
        material_audits["component_id"] = apply_material(
            authoring, landscape, component
        )
        component_c05 = captures_root / "component_id_C05.png"
        capture_records.append(
            capture_one(
                authoring,
                landscape,
                specs["C05_COVERAGE_HIGH"],
                unreal.SkyguardLandscapeCaptureDiagnosticMode.COMPONENT_BOUNDARY,
                component_c05,
                width,
                height,
                proof["fov_degrees"],
            )
        )
    finally:
        material_audits["governed_restore"] = apply_material(
            authoring, landscape, governed
        )
    coverage_c05_result = coverage_analysis(
        coverage_c05, proof["coverage_white_rgb8_minimum"]
    )
    coverage_c04_result = coverage_analysis(
        coverage_c04, proof["coverage_white_rgb8_minimum"]
    )
    palette = palette_analysis(
        component_c05,
        proof["component_palette_rgb8_tolerance_per_channel"],
    )
    palette_minimum = proof["component_palette_minimum_pixels_per_id"]
    checks = {
        "active_rhi_exact": rhi == "D3D12|SM6",
        "usage_flags_exact": all(usage.values()),
        "three_captures_exact": len(capture_records) == 3,
        "all_camera_transforms_applied_before_configuration": all(
            item["transform_applied_before_configuration"]
            for item in capture_records
        ),
        "all_show_only_material_sync_audits_exact": all(
            item["show_only_component_count"] == 16
            and item["generated_material_instance_count"] == 16
            and item["material_parent_match_count"] == 16
            and item["render_thread_synchronized"]
            for item in capture_records
        ),
        "coverage_c05_visible_white": (
            coverage_c05_result["white_fraction"]
            >= proof["coverage_c05_minimum_fraction"]
        ),
        "coverage_c04_visible_white": (
            coverage_c04_result["white_fraction"]
            >= proof["coverage_c04_minimum_fraction"]
        ),
        "all_16_component_ids_visible": (
            palette["matching_id_count"] == 16
            and all(
                count >= palette_minimum
                for count in palette["pixel_counts"].values()
            )
        ),
        "governed_material_restored": (
            material_audits["governed_restore"]["success"]
        ),
    }
    locked_after = {
        name: sha256_file(ROOT / item["file"])
        for name, item in contract["locked_production_packages"].items()
    }
    checks["locked_production_packages_unchanged"] = (
        locked_after == locked_before
    )
    report = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt07-tiny-proof.v1"
        ),
        "contract_id": contract["contract_id"],
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "rhi": rhi,
        "resolution": [width, height],
        "material_usage": usage,
        "material_audits": material_audits,
        "capture_records": capture_records,
        "coverage_c05": coverage_c05_result,
        "coverage_c04": coverage_c04_result,
        "component_palette": palette,
        "checks": checks,
        "locked_packages_before": locked_before,
        "locked_packages_after": locked_after,
        "world_saved": False,
        "pcg_generation_invoked": False,
        "full_capture_invoked": False,
        "profile_invoked": False,
        "promotion_allowed": False,
    }
    proof_receipt.parent.mkdir(parents=True, exist_ok=True)
    proof_receipt.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    if report["gate"] != "PASS":
        raise RuntimeError("Attempt07 tiny live proof failed")
    unreal.log("[SkyguardAttempt07TinyProof] " + json.dumps(report))


if __name__ == "__main__":
    main()
