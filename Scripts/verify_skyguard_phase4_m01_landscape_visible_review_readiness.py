"""Offline readiness gate for the M01 Landscape visible GPU review.

This script never launches Unreal, imports content, generates PCG, or mutates
serialized assets. It verifies the immutable baseline and the exact local,
provenance-approved material inputs required by the visible review contract.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_contract import (
    AMENDMENT_PATH,
    ATTEMPT03_PATH,
    ATTEMPT04_PATH,
    BASE_PATH,
    load_effective_contract,
)


CONTRACT_PATH = ATTEMPT04_PATH
REPORT_PATH = (
    ROOT
    / "Saved/Reports/PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_READINESS.json"
)
GPU_REPORT_PATH = (
    ROOT
    / "Saved/Reports/PHASE4_M01_LANDSCAPE_VISIBLE_GPU_REVIEW_ATTEMPT04_LATEST.json"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def verify_locked_file(entry: dict, checks: dict, errors: list[str], prefix: str) -> None:
    path = ROOT / entry["file"]
    key = prefix + "_" + path.stem
    checks[key + "_present"] = path.is_file()
    if not path.is_file():
        errors.append(f"Missing locked file: {path}")
        checks[key + "_bytes"] = False
        checks[key + "_hash"] = False
        return
    checks[key + "_bytes"] = path.stat().st_size == int(entry["bytes"])
    checks[key + "_hash"] = sha256(path) == entry["sha256"]
    if not checks[key + "_bytes"]:
        errors.append(f"Byte mismatch: {path}")
    if not checks[key + "_hash"]:
        errors.append(f"Hash mismatch: {path}")


def main() -> int:
    checks: dict[str, bool] = {}
    errors: list[str] = []

    checks["contract_present"] = CONTRACT_PATH.is_file()
    if not CONTRACT_PATH.is_file():
        raise SystemExit(f"Missing contract: {CONTRACT_PATH}")
    contract = load_effective_contract()

    checks["contract_schema"] = (
        contract.get("schema")
        == "skyguard.phase4.m01-landscape-visible-gpu-review-contract.v4"
    )
    checks["contract_id"] = (
        contract.get("contract_id") == "P4.5-M01-LANDSCAPE-VISIBLE-004"
    )
    checks["base_contract_hash_locked"] = (
        contract.get("amendment", {}).get("base_sha256")
        == "a82c85a2dde46ebdf668129c94c5fa2a953fc738d65f6f8dc6bb6d5647a07cb0"
        and BASE_PATH.is_file()
    )
    failed_evidence = contract["amendment"]["failed_attempt01_evidence"]
    failed_evidence_path = ROOT / failed_evidence["candidate_file"]
    checks["failed_attempt01_preserved"] = (
        failed_evidence_path.is_file()
        and failed_evidence_path.stat().st_size
        == failed_evidence["candidate_file_bytes"]
        and sha256(failed_evidence_path)
        == failed_evidence["candidate_file_sha256"]
        and failed_evidence["performance_evidence_eligible"] is False
    )
    failed_attempt02 = contract["amendment"]["failed_attempt02_evidence"]
    failed_attempt02_map = ROOT / failed_attempt02["candidate_file"]
    failed_attempt02_material = ROOT / failed_attempt02["material_file"]
    checks["failed_attempt02_preserved"] = (
        failed_attempt02_map.is_file()
        and failed_attempt02_map.stat().st_size
        == failed_attempt02["candidate_file_bytes"]
        and sha256(failed_attempt02_map)
        == failed_attempt02["candidate_file_sha256"]
        and failed_attempt02_material.is_file()
        and failed_attempt02_material.stat().st_size
        == failed_attempt02["material_file_bytes"]
        and sha256(failed_attempt02_material)
        == failed_attempt02["material_file_sha256"]
        and failed_attempt02["performance_evidence_eligible"] is False
    )
    failed_attempt03 = contract["amendment"]["failed_attempt03_evidence"]
    failed_attempt03_map = ROOT / failed_attempt03["candidate_file"]
    failed_attempt03_material = ROOT / failed_attempt03["material_file"]
    checks["failed_attempt03_preserved"] = (
        failed_attempt03_map.is_file()
        and failed_attempt03_map.stat().st_size
        == failed_attempt03["candidate_file_bytes"]
        and sha256(failed_attempt03_map)
        == failed_attempt03["candidate_file_sha256"]
        and failed_attempt03_material.is_file()
        and failed_attempt03_material.stat().st_size
        == failed_attempt03["material_file_bytes"]
        and sha256(failed_attempt03_material)
        == failed_attempt03["material_file_sha256"]
        and failed_attempt03["performance_evidence_eligible"] is False
    )

    baseline = contract["baseline"]
    verify_locked_file(baseline, checks, errors, "baseline")
    acceptance_path = ROOT / baseline["serialized_acceptance_report"]
    checks["serialized_acceptance_report_present"] = acceptance_path.is_file()
    checks["serialized_acceptance_report_hash"] = (
        acceptance_path.is_file()
        and sha256(acceptance_path)
        == baseline["serialized_acceptance_report_sha256"]
    )
    if acceptance_path.is_file():
        acceptance = read_json(acceptance_path)
        checks["serialized_gate_pass"] = (
            acceptance.get("gate") == baseline["required_serialized_gate"]
        )
        checks["serialized_map_exact"] = (
            acceptance.get("map") == baseline["immutable_map"]
        )
        checks["visible_review_pending"] = (
            acceptance.get("rendered_review_status")
            == baseline["required_rendered_review_status"]
        )
    else:
        checks["serialized_gate_pass"] = False
        checks["serialized_map_exact"] = False
        checks["visible_review_pending"] = False

    provenance = contract["provenance"]
    ledger_entry = {
        "file": provenance["ledger"]["path"],
        "bytes": (ROOT / provenance["ledger"]["path"]).stat().st_size
        if (ROOT / provenance["ledger"]["path"]).is_file()
        else -1,
        "sha256": provenance["ledger"]["sha256"],
    }
    verify_locked_file(ledger_entry, checks, errors, "provenance")
    manifest_entry = {
        "file": provenance["expanded_manifest"]["path"],
        "bytes": (
            ROOT / provenance["expanded_manifest"]["path"]
        ).stat().st_size
        if (ROOT / provenance["expanded_manifest"]["path"]).is_file()
        else -1,
        "sha256": provenance["expanded_manifest"]["sha256"],
    }
    verify_locked_file(manifest_entry, checks, errors, "provenance")

    manifest_path = ROOT / provenance["expanded_manifest"]["path"]
    manifest = read_json(manifest_path) if manifest_path.is_file() else {}
    checks["expanded_manifest_gate"] = manifest.get("gate") == "PASS"
    checks["expanded_manifest_verified_count"] = (
        manifest.get("verified_record_count")
        == provenance["expanded_manifest"]["verified_record_count"]
    )
    records = manifest.get("records", [])
    for family in provenance["approved_external_families"]:
        matching = [
            record
            for record in records
            if record.get("family") == family["family"]
        ]
        family_key = "family_" + family["family"]
        checks[family_key + "_record_count"] = (
            len(matching) == family["verified_record_count"]
        )
        checks[family_key + "_canonical_verified"] = all(
            record.get("canonical_url_and_length_verified") is True
            and record.get("license") == "CC0-1.0"
            and Path(record["path"]).is_file()
            and sha256(Path(record["path"])) == record["local_sha256"]
            for record in matching
        )

    for asset in provenance["locked_unreal_assets"]:
        verify_locked_file(asset, checks, errors, "asset")

    candidate = contract["candidate"]
    checks["baseline_immutable"] = baseline["must_not_be_modified"] is True
    checks["candidate_does_not_overwrite_baseline"] = (
        candidate["immutable_map"] != baseline["immutable_map"]
        and candidate["must_never_overwrite_baseline"] is True
    )
    checks["candidate_pcg_locked"] = (
        candidate["pcg_generation_invoked"] is False
        and candidate["generated_pcg_component_count"] == 0
        and candidate["generated_pcg_instance_count"] == 0
    )
    checks["landscape_only_inland_surface_policy"] = (
        "disable_LandTiles" in candidate["legacy_land_tile_policy"]
    )

    material = contract["material_design"]
    checks["bounded_material"] = (
        material["selected_texture_samples"] <= material["texture_sample_budget"]
        and material["displacement"] is False
        and material["tessellation"] is False
        and material["runtime_virtual_texture"] is False
        and material["procedural_generation"] is False
    )

    capture = contract["capture"]
    checks["capture_platform_exact"] = (
        capture["rhi"] == "D3D12"
        and capture["shader_model"] == "SM6"
        and capture["resolution"] == [1920, 1080]
        and capture["screen_percentage"] == 100
    )
    checks["five_fixed_cameras"] = (
        len(capture["cameras"]) == 5
        and len({camera["id"] for camera in capture["cameras"]}) == 5
    )
    profile = capture["profile_runs"]
    checks["bounded_profile"] = (
        profile["baseline_count"] == 1
        and profile["candidate_count"] == 1
        and profile["warmup_seconds"] == 30
        and profile["measured_seconds"] == 60
        and profile["hard_timeout_seconds_per_process"] <= 180
        and profile["maximum_total_gpu_lane_minutes"] <= 8
    )

    safety = contract["execution_safety"]
    checks["exclusive_lane_required"] = (
        safety["requires_root_exclusive_heavy_lane_authorization"] is True
    )
    checks["external_imports_forbidden"] = (
        safety["no_Fab_or_Quixel_import"] is True
        and safety["no_network_download"] is True
    )
    checks["pcg_generation_forbidden"] = (
        safety["no_PCG_generate_or_generate_local_call"] is True
        and safety["no_runtime_PCG_regeneration"] is True
    )

    tooling = {
        "candidate_builder": (
            ROOT
            / "Scripts/build_skyguard_phase4_m01_landscape_material_validation.py"
        ),
        "candidate_editor_verifier": (
            ROOT
            / "Scripts/verify_skyguard_phase4_m01_landscape_material_assets.py"
        ),
        "capture_harness": (
            ROOT
            / "Scripts/capture_skyguard_phase4_m01_landscape_visible_review.py"
        ),
        "gpu_gate_verifier": (
            ROOT
            / "Scripts/verify_skyguard_phase4_m01_landscape_visible_gpu_gate.py"
        ),
        "fail_closed_supervisor": (
            ROOT
            / "Scripts/run_skyguard_phase4_m01_landscape_visible_gpu_gate.ps1"
        ),
        "human_review_template": (
            ROOT
            / "Docs/AAA_Review/PHASE4_M01_LANDSCAPE_VISIBLE_HUMAN_REVIEW_ATTEMPT04_TEMPLATE.json"
        ),
    }
    for name, path in tooling.items():
        checks["tooling_" + name + "_present"] = path.is_file()
    builder_text = (
        tooling["candidate_builder"].read_text(encoding="utf-8")
        if tooling["candidate_builder"].is_file()
        else ""
    )
    capture_text = (
        tooling["capture_harness"].read_text(encoding="utf-8")
        if tooling["capture_harness"].is_file()
        else ""
    )
    supervisor_text = (
        tooling["fail_closed_supervisor"].read_text(encoding="utf-8")
        if tooling["fail_closed_supervisor"].is_file()
        else ""
    )
    checks["tooling_candidate_immutable_paths"] = (
        candidate["immutable_map"] in builder_text
        and candidate["landscape_material"] in builder_text
        and baseline["immutable_map"] in builder_text
    )
    checks["tooling_six_locked_texture_assets"] = all(
        item["asset"] in builder_text
        for item in provenance["locked_unreal_assets"]
        if item["asset"].startswith("/Game/Skyguard/Textures/Imported/")
    )
    checks["tooling_mixed_normal_green_policy"] = (
        "required_flip" in builder_text
        and "apply_normal_green_correction" in builder_text
        and "LinearColor(1.0, -1.0, 1.0, 1.0)" in builder_text
        and "NORMALMAP" in builder_text
    )
    checks["tooling_ue58_exported_material_expression_api"] = (
        "MaterialEditingLibrary.get_material_expressions" in builder_text
        and "MaterialEditingLibrary.get_num_material_expressions"
        in builder_text
        and 'get_editor_property("expressions")' not in builder_text
    )
    checks["tooling_five_views_and_three_diagnostics"] = (
        "capture_lit_views" in capture_text
        and "candidate_diagnostic_landscape_lod_C05.png" in capture_text
        and "candidate_diagnostic_shader_complexity_C04.png" in capture_text
        and "candidate_diagnostic_component_boundary_C05.png" in capture_text
    )
    checks["tooling_render_target_exports_exact_png_extension"] = (
        'filename + ".png"' in capture_text
        and "str(output.parent), output.name" in capture_text
        and "str(output.parent), output.stem" not in capture_text
    )
    capture_stage_start = supervisor_text.find("foreach ($captureSpec in @(")
    capture_stage_end = supervisor_text.find(
        "$expectedCapturePaths = @()", capture_stage_start
    )
    capture_stage_text = (
        supervisor_text[capture_stage_start:capture_stage_end]
        if capture_stage_start >= 0 and capture_stage_end > capture_stage_start
        else ""
    )
    checks["tooling_gpu_capture_uses_normal_editor_not_commandlet"] = (
        "-ExecutePythonScript=$CaptureScript" in capture_stage_text
        and "-FilePath $EditorExe" in capture_stage_text
        and "-run=pythonscript" not in capture_stage_text.lower()
    )
    checks["tooling_gpu_capture_runtime_rhi_guard"] = (
        "require_d3d12_sm6" in capture_text
        and "get_active_rhi_and_feature_level" in capture_text
        and 'EXPECTED_RHI_VALIDATION = "D3D12|SM6"' in capture_text
        and "Assert-CaptureRHIValidated -Stage $stage" in capture_stage_text
    )
    checks["tooling_sequential_30s_60s_d3d12_sm6"] = all(
        marker in supervisor_text
        for marker in (
            "Invoke-ProfileStage",
            "-Seconds 30",
            "-Seconds 60",
            "-d3d12",
            "-sm6",
            "maximum_total_gpu_lane_minutes = 8",
        )
    )
    checks["tooling_exact_heavy_process_pre_and_postflight"] = all(
        marker in supervisor_text
        for marker in (
            "Get-ExactHeavyProcesses",
            "Wait-ForZeroHeavyProcesses",
            "ShaderCompileWorker",
            "UbaAgent",
            "UbaServer",
        )
    )

    candidate_file = (
        ROOT
        / "Content/Skyguard/Maps/"
        / (candidate["immutable_map"].rsplit("/", 1)[-1] + ".umap")
    )
    capture_revision_path = (
        ROOT
        / "Docs/AAA_Review/PHASE4_M01_LANDSCAPE_CAPTURE_TOOLING_REVISION_01.json"
    )
    capture_revision02_path = (
        ROOT
        / "Docs/AAA_Review/PHASE4_M01_LANDSCAPE_CAPTURE_TOOLING_REVISION_02.json"
    )
    capture_revision03_path = (
        ROOT
        / "Docs/AAA_Review/PHASE4_M01_LANDSCAPE_CAPTURE_TOOLING_REVISION_03.json"
    )
    checks["capture_tooling_revision_present"] = capture_revision_path.is_file()
    if capture_revision_path.is_file():
        capture_revision = read_json(capture_revision_path)
        accepted_candidate = capture_revision["accepted_candidate"]
        candidate_material_file = ROOT / accepted_candidate["material_file"]
        checks["accepted_candidate_hash_locked"] = (
            candidate_file.is_file()
            and candidate_file.stat().st_size
            == accepted_candidate["bytes"]
            and sha256(candidate_file) == accepted_candidate["sha256"]
            and candidate_material_file.is_file()
            and candidate_material_file.stat().st_size
            == accepted_candidate["material_bytes"]
            and sha256(candidate_material_file)
            == accepted_candidate["material_sha256"]
        )
        checks["capture_crash_api_forbidden"] = (
            capture_revision["repair"][
                "automation_library_high_res_screenshot_forbidden"
            ]
            is True
            and "AutomationLibrary.take_high_res_screenshot"
            not in capture_text
        )
    else:
        checks["accepted_candidate_hash_locked"] = False
        checks["capture_crash_api_forbidden"] = False
    checks["capture_tooling_revision02_present"] = capture_revision02_path.is_file()
    if capture_revision02_path.is_file():
        capture_revision02 = read_json(capture_revision02_path)
        failed_capture = capture_revision02["preserved_failed_capture_attempt"]
        failed_capture_records = [
            failed_capture["run_manifest"],
            failed_capture["supervisor_receipt"],
            failed_capture["baseline_capture_log"],
            failed_capture["candidate_capture_log"],
        ]
        checks["nullrhi_failed_capture_evidence_hash_locked"] = all(
            (ROOT / record["file"]).is_file()
            and sha256(ROOT / record["file"]) == record["sha256"]
            for record in failed_capture_records
        )
        checks["capture_tooling_revision02_policy"] = (
            failed_capture["terminal_state"] == "FAIL"
            and failed_capture["performance_evidence_eligible"] is False
            and capture_revision02["offline_repair"][
                "commandlet_capture_forbidden"
            ]
            is True
            and capture_revision02["offline_repair"][
                "runtime_rhi_marker_required_before_screenshot"
            ]
            == "D3D12|SM6"
            and capture_revision02["execution_state"]
            == "OFFLINE_TOOLING_PATCH_ONLY_REQUIRES_FRESH_EXCLUSIVE_GPU_LANE_GRANT"
        )
    else:
        checks["nullrhi_failed_capture_evidence_hash_locked"] = False
        checks["capture_tooling_revision02_policy"] = False
    checks["capture_tooling_revision03_present"] = capture_revision03_path.is_file()
    if capture_revision03_path.is_file():
        capture_revision03 = read_json(capture_revision03_path)
        revision03_records = [
            capture_revision03["run_manifest"],
            capture_revision03["supervisor_receipt"],
            *capture_revision03["preserved_extensionless_png_payloads"],
        ]
        checks["extensionless_capture_failure_evidence_hash_locked"] = all(
            (ROOT / record["file"]).is_file()
            and sha256(ROOT / record["file"]) == record["sha256"]
            for record in revision03_records
        )
        checks["extensionless_capture_failure_policy"] = (
            capture_revision03["terminal_state"] == "FAIL"
            and capture_revision03["root_cause"][
                "performance_evidence_eligible"
            ]
            is False
            and len(capture_revision03["preserved_extensionless_png_payloads"])
            == 13
            and capture_revision03["provisional_launcher_receipt_correction"][
                "status"
            ]
            == "SUPERSEDED_BY_LIVE_SUPERVISOR_CONTINUATION"
            and capture_revision03["execution_state"]
            == "OFFLINE_FILENAME_REPAIR_ONLY_REQUIRES_FRESH_EXCLUSIVE_GPU_LANE_GRANT"
        )
    else:
        checks["extensionless_capture_failure_evidence_hash_locked"] = False
        checks["extensionless_capture_failure_policy"] = False
    if not candidate_file.exists():
        authoring_status = "READY_FOR_AUTHORIZED_GPU_AUTHORING"
    elif not GPU_REPORT_PATH.exists():
        authoring_status = "CANDIDATE_PRESENT_REQUIRES_VISIBLE_GPU_GATE"
    else:
        gpu_report = read_json(GPU_REPORT_PATH)
        authoring_status = (
            "VISIBLE_GPU_GATE_PASS"
            if gpu_report.get("gate") == "PASS"
            else "VISIBLE_GPU_GATE_NOT_PASSED"
        )

    failed = sorted(key for key, value in checks.items() if not value)
    errors.extend(f"Failed check: {key}" for key in failed)
    gate = "PASS" if not errors else "FAIL"
    report = {
        "schema": "skyguard.phase4.m01-landscape-visible-review-readiness.v1",
        "contract_id": contract["contract_id"],
        "gate": gate,
        "authoring_status": authoring_status,
        "checks": checks,
        "errors": errors,
        "selected_external_families": [
            item["family"] for item in provenance["approved_external_families"]
        ],
        "selected_unreal_asset_count": len(provenance["locked_unreal_assets"]),
        "candidate_asset_present": candidate_file.exists(),
        "visible_gpu_report_present": GPU_REPORT_PATH.exists(),
        "promotion": {
            "ready_for_authorized_gpu_authoring": (
                gate == "PASS"
                and authoring_status == "READY_FOR_AUTHORIZED_GPU_AUTHORING"
            ),
            "tooling_ready_for_exclusive_gpu_lane": gate == "PASS",
            "landscape_material_visible_accepted": (
                gate == "PASS" and authoring_status == "VISIBLE_GPU_GATE_PASS"
            ),
            "production_vegetation_complete": False,
            "mission01_aaa_complete": False,
        },
        "limitations": [
            "This is an offline provenance and contract gate; no rendered GPU judgment occurred.",
            "No Fab/Quixel content or vegetation is authorized.",
            "PCG generation remains prohibited.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        "PHASE4_M01_LANDSCAPE_VISIBLE_REVIEW_READINESS="
        + gate
        + " STATUS="
        + authoring_status
    )
    return 0 if gate == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
