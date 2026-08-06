"""Offline-only Attempt06 diagnosis and design-readiness verifier.

This verifier deliberately cannot launch Unreal. A PASS means the immutable
repair design, source implementation, supervisor, and mathematical evidence
are coherent. It does not authorize or execute the bounded Unreal run.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_attempt06_camera_math import build_proof
from phase4_m01_landscape_attempt06_contract import load_attempt06_contract
from verify_skyguard_phase4_m01_landscape_visible_gpu_gate import (
    decode_png_rgb8,
)


CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_REPAIR_CONTRACT_ATTEMPT06.json"
)
OUTPUT = (
    ROOT
    / "Saved/Reports"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT06_OFFLINE_READINESS.json"
)
NATIVE_HEADER = (
    ROOT / "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.h"
)
NATIVE_SOURCE = (
    ROOT / "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.cpp"
)
CAPTURE_SOURCE = (
    ROOT / "Scripts/capture_skyguard_phase4_m01_landscape_visible_review.py"
)
GATE_SOURCE = (
    ROOT
    / "Scripts/verify_skyguard_phase4_m01_landscape_visible_gpu_gate.py"
)
SUPERVISOR = (
    ROOT
    / "Scripts/supervise_skyguard_phase4_m01_landscape_visible_attempt06.py"
)
PROFILE_SOURCE = (
    ROOT
    / "Source/Skyguard52/"
    "SkyguardPhase4LandscapePerformanceCaptureAttempt06.cpp"
)
POWERSHELL_LAUNCHER = (
    ROOT
    / "Scripts/run_skyguard_phase4_m01_landscape_visible_attempt06.ps1"
)
ATTEMPT06_IMPLEMENTATION_FILES = (
    ROOT
    / "Scripts/build_skyguard_phase4_m01_landscape_material_validation_attempt06.py",
    ROOT
    / "Scripts/verify_skyguard_phase4_m01_landscape_material_assets_attempt06.py",
    ROOT
    / "Scripts/capture_skyguard_phase4_m01_landscape_visible_review_attempt06.py",
    ROOT
    / "Scripts/verify_skyguard_phase4_m01_landscape_visible_gpu_gate_attempt06.py",
    SUPERVISOR,
)
ATTEMPT05_CAPTURE_ROOT = (
    ROOT
    / "Saved/Profiling/Phase4/M01_LandscapeVisible_Attempt05/"
    "attempt_20260802T164911778Z/recovery_01/artifacts/captures/candidate"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def locked_files_pass(items: dict) -> bool:
    return all(
        (ROOT / item["file"]).is_file()
        and sha256_file(ROOT / item["file"]) == item["sha256"]
        for item in items.values()
        if isinstance(item, dict) and "file" in item
    )


def actual_attempt05_mask_pixels(camera_id: str) -> int:
    path = (
        ATTEMPT05_CAPTURE_ROOT
        / f"candidate_diagnostic_landscape_coverage_{camera_id}.png"
    )
    width, height, rgb = decode_png_rgb8(path)
    if (width, height) != (1920, 1080):
        raise ValueError(f"unexpected dimensions for {path}")
    visible = 0
    for index in range(0, len(rgb), 3):
        if sum(rgb[index : index + 3]) / (3.0 * 255.0) >= 0.5:
            visible += 1
    return visible


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    effective = load_attempt06_contract()
    proof = build_proof()
    predecessor = contract["immutable_predecessor"]
    actual_camera_ids = contract["attempt05_failure_diagnosis"][
        "actual_capture_camera_ids"
    ]
    mask_pixels = {
        camera_id: actual_attempt05_mask_pixels(camera_id)
        for camera_id in actual_camera_ids
    }
    output_files = contract["future_immutable_outputs"]
    camera_ids = [
        camera["id"] for camera in contract["capture_revision"]["cameras"]
    ]
    effective_camera_ids = [
        camera["id"] for camera in effective["capture"]["cameras"]
    ]
    c05_proof = proof["c05_all_component_proof"]
    header_source = NATIVE_HEADER.read_text(encoding="utf-8")
    native_source = NATIVE_SOURCE.read_text(encoding="utf-8")
    capture_source = CAPTURE_SOURCE.read_text(encoding="utf-8")
    gate_source = GATE_SOURCE.read_text(encoding="utf-8")
    supervisor_source = SUPERVISOR.read_text(encoding="utf-8")
    profile_source = PROFILE_SOURCE.read_text(encoding="utf-8")
    launcher_source = POWERSHELL_LAUNCHER.read_text(encoding="utf-8")
    checks = {
        "attempt05_predecessor_evidence_hashes_locked": locked_files_pass(
            {
                "manifest": predecessor["recovery_manifest"],
                "gate": predecessor["gate_report"],
            }
        ),
        "attempt05_package_hashes_locked": locked_files_pass(
            predecessor["package_hashes"]
        ),
        "attempt05_actual_camera_names_proven": all(
            (
                ATTEMPT05_CAPTURE_ROOT
                / f"candidate_lit_{camera_id}.png"
            ).is_file()
            and (
                ATTEMPT05_CAPTURE_ROOT
                / f"candidate_diagnostic_landscape_coverage_{camera_id}.png"
            ).is_file()
            for camera_id in actual_camera_ids
        ),
        "attempt05_all_five_actual_coverage_masks_blank": (
            len(mask_pixels) == 5
            and all(count == 0 for count in mask_pixels.values())
        ),
        "attempt05_renamed_camera_contract_mismatch_explicit": (
            actual_camera_ids
            != contract["attempt05_failure_diagnosis"][
                "gate_expected_camera_ids"
            ]
        ),
        "attempt05_offline_camera_model_exposes_failure": (
            proof["attempt05_all_five_camera_framing_proofs_pass"] is False
            and any(
                result["id"] == "C03_SHORE_GRAZE"
                and result["forward_ray_intersects_landscape_bounds"] is False
                for result in proof["attempt05_actual_camera_results"]
            )
        ),
        "attempt06_loader_replaces_camera_contract": (
            effective_camera_ids == camera_ids
            and effective_camera_ids
            == [
                "C01_ESTABLISHING_HIGH",
                "C02_SHORELINE_GRAZE",
                "C03_ROUTE_LOW",
                "C04_INLAND_CLOSE",
                "C05_COVERAGE_HIGH",
            ]
        ),
        "attempt06_all_five_camera_math_passes": (
            proof["all_five_camera_framing_proofs_pass"] is True
            and all(
                result["forward_ray_intersects_landscape_bounds"]
                and result["threshold_margin"] > 0.0
                for result in proof["camera_results"]
            )
        ),
        "attempt06_c05_contains_all_16_component_bounds": (
            c05_proof["all_16_component_bounds_inside_viewport"] is True
            and c05_proof["component_count"] == 16
            and c05_proof[
                "minimum_conservative_component_pixel_area"
            ]
            >= contract["capture_revision"]["offline_camera_proof"][
                "c05_minimum_conservative_projected_pixel_area_per_component"
            ]
        ),
        "attempt06_exact_component_palette_gate_required": (
            contract["capture_revision"]["component_id_gate"][
                "expected_ids"
            ]
            == 16
            and contract["capture_revision"]["component_id_gate"][
                "minimum_pixels_per_expected_id"
            ]
            >= 10000
            and contract["capture_revision"]["component_id_gate"][
                "generic_color_bucket_count_is_forbidden"
            ]
            is True
        ),
        "attempt06_explicit_show_only_and_sync_required": (
            contract["capture_revision"]["diagnostic_capture"][
                "show_only_population"
            ]
            == "explicit_16_ULandscapeComponent_enumeration"
            and contract["capture_revision"]["diagnostic_capture"][
                "show_only_component_count_required"
            ]
            == 16
            and contract["capture_revision"]["diagnostic_capture"][
                "flush_rendering_commands_before_capture_required"
            ]
            is True
        ),
        "attempt06_outputs_and_root_absent": (
            all(
                not (ROOT / output_files[key]).exists()
                for key in (
                    "map_file",
                    "material_file",
                    "coverage_material_file",
                    "component_id_material_file",
                    "attempt_root",
                )
            )
        ),
        "attempt06_execution_and_promotion_forbidden": all(
            contract["execution_authorization"][key] is False
            for key in (
                "unreal_launch_allowed",
                "authoring_allowed",
                "capture_allowed",
                "profiling_allowed",
                "automatic_retry_allowed",
                "promotion_allowed",
            )
        ),
        "attempt06_performance_reprofile_required": (
            contract["performance_policy"][
                "attempt06_may_reuse_recovery03_performance"
            ]
            is False
            and contract["performance_policy"][
                "future_execution_requires_sequential_baseline_then_candidate_profile"
            ]
            is True
        ),
        "attempt06_native_explicit_16_show_only_implemented": (
            "ShowOnlyLandscapeComponentCount" in header_source
            and "DiagnosticMaterialParentMatchComponentCount"
            in header_source
            and "bRenderThreadSynchronized" in header_source
            and "Landscape->GetComponents<ULandscapeComponent>(Components)"
            in native_source
            and "Components.Num() != 16" in native_source
            and "Capture->ShowOnlyComponent(Component)" in native_source
            and "Result.ShowOnlyLandscapeComponentCount != 16"
            in native_source
            and "ShowOnlyActorComponents" not in native_source
        ),
        "attempt06_native_material_audit_and_sync_implemented": (
            "SetTransientLandscapeDiagnosticMaterialSynchronized"
            in header_source
            and "SetTransientLandscapeDiagnosticMaterialSynchronized"
            in native_source
            and native_source.count("FlushRenderingCommands();") >= 2
            and "GeneratedMaterialInstanceReadyComponentCount != 16"
            in native_source
            and "DiagnosticMaterialParentMatchComponentCount != 16"
            in native_source
            and "Flags.SetTonemapper(false)" in native_source
            and "Flags.SetPostProcessing(false)" in native_source
            and "Flags.SetAtmosphere(false)" in native_source
            and "Flags.SetCloud(false)" in native_source
            and "Flags.SetFog(false)" in native_source
        ),
        "attempt06_capture_contract_only_and_manifest_proof_implemented": (
            "record_capture_evidence" in capture_source
            and "camera_transform_authority" in capture_source
            and "serialized_camera_actor_fallback_used" in capture_source
            and "set_transient_landscape_diagnostic_material_synchronized"
            in capture_source
            and "show_only_landscape_component_count" in capture_source
            and "render_thread_synchronization_complete" in capture_source
            and '!= "P4.5-M01-LANDSCAPE-VISIBLE-006"'
            in capture_source
        ),
        "attempt06_exact_palette_verifier_implemented": (
            "def analyze_attempt06_visuals" in gate_source
            and "srgb8_to_linear" in gate_source
            and "component_expected_id_pixel_counts" in gate_source
            and '"generic_color_bucket_count_used"] = False'
            in gate_source
            and "minimum_pixels_per_expected_id" in gate_source
            and "attempt06_exact_component_palette_gate" in gate_source
        ),
        "attempt06_immutable_entrypoints_parse": all(
            path.is_file()
            and bool(ast.parse(path.read_text(encoding="utf-8")))
            for path in ATTEMPT06_IMPLEMENTATION_FILES
        ),
        "attempt06_supervisor_fail_closed_and_sequential": (
            "--authorize-single-run" in supervisor_source
            and "--skip-build" not in supervisor_source
            and "active_heavy_processes()" in supervisor_source
            and "assert_locked_items" in supervisor_source
            and "build_skyguard52_editor_attempt06" in supervisor_source
            and "author_immutable_candidate_attempt06" in supervisor_source
            and 'f"{mode}_capture_attempt06"' in supervisor_source
            and 'f"{mode}_profile_measured_attempt06"' in supervisor_source
            and "-csvCaptureFrames" not in supervisor_source
            and "-benchmark" not in supervisor_source
            and '"promotion_allowed": False' in supervisor_source
            and "Attempt06 output/root already exists" in supervisor_source
            and "P4.5-M01-LANDSCAPE-VISIBLE-006" in profile_source
            and "RequiredAttempt06ContractId" in profile_source
            and "P4.5-M01-LANDSCAPE-VISIBLE-005" not in profile_source
        ),
        "attempt06_launcher_requires_explicit_authorization": (
            "AuthorizeSingleRun" in launcher_source
            and "if (-not $AuthorizeSingleRun)" in launcher_source
            and "--authorize-single-run" in launcher_source
            and "SkipBuild" not in launcher_source
        ),
        "attempt06_contract_marks_implementation_complete": (
            contract["native_implementation_boundary"][
                "implementation_complete"
            ]
            is True
        ),
    }
    design_ready = all(checks.values())
    report = {
        "schema": "skyguard.phase4.m01-landscape-attempt06-readiness.v1",
        "contract_id": contract["contract_id"],
        "gate": (
            "PASS_ATTEMPT06_OFFLINE_IMPLEMENTATION_READY_PENDING_AUTHORIZED_RUN"
            if design_ready
            else "FAIL_ATTEMPT06_OFFLINE_DESIGN_NOT_READY"
        ),
        "scope": (
            "offline diagnosis, immutable repair implementation, and "
            "single-run supervisor validation only"
        ),
        "unreal_launched": False,
        "attempt05_mutated": False,
        "attempt06_authored": False,
        "native_implementation_complete": contract[
            "native_implementation_boundary"
        ]["implementation_complete"],
        "execution_ready": False,
        "authorized_supervisor_will_build_before_launch": True,
        "authorized_launch_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            "\"D:\\Skyguard52\\Scripts\\run_skyguard_phase4_m01_"
            "landscape_visible_attempt06.ps1\" -AuthorizeSingleRun"
            if design_ready
            else None
        ),
        "promotion_allowed": False,
        "attempt05_actual_mask_pixels": mask_pixels,
        "camera_proof": proof,
        "checks": checks,
        "remaining_before_execution_readiness": [
            "obtain explicit root authorization for exactly one bounded Attempt06 run; the supervisor compiles before any editor stage",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if design_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
