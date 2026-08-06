"""Offline fail-closed readiness for profiling-only recovery03."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT05_RECOVERY03_CONTRACT.json"
)
SUPERVISOR = (
    ROOT
    / "Scripts"
    / "run_skyguard_phase4_m01_landscape_visible_attempt05_recovery03.ps1"
)
PROFILE_HEADER = (
    ROOT / "Source/Skyguard52/SkyguardPhase4LandscapePerformanceCapture.h"
)
PROFILE_SOURCE = (
    ROOT / "Source/Skyguard52/SkyguardPhase4LandscapePerformanceCapture.cpp"
)
COMPILED_MODULE = ROOT / "Binaries/Win64/UnrealEditor-Skyguard52.dll"
OUTPUT = (
    ROOT
    / "Saved/Reports"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT05_RECOVERY03_READINESS.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def locked_files_pass(section: dict) -> bool:
    return all(
        (ROOT / item["file"]).is_file()
        and sha256_file(ROOT / item["file"]) == item["sha256"]
        for item in section.values()
        if isinstance(item, dict) and "file" in item
    )


def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    supervisor = SUPERVISOR.read_text(encoding="utf-8")
    header = PROFILE_HEADER.read_text(encoding="utf-8")
    source = PROFILE_SOURCE.read_text(encoding="utf-8")
    recovery01_failure = json.loads(
        (
            ROOT / contract["accepted_capture_evidence"]["hash_manifest"]
        ).read_text(encoding="utf-8-sig")
    )
    recovery02_failure = json.loads(
        (
            ROOT
            / contract["immutable_predecessor_evidence"][
                "recovery02_failure_receipt"
            ]["file"]
        ).read_text(encoding="utf-8-sig")
    )
    recovery02_manifest = json.loads(
        (
            ROOT
            / contract["immutable_predecessor_evidence"][
                "recovery02_manifest"
            ]["file"]
        ).read_text(encoding="utf-8-sig")
    )
    render = json.loads(
        (
            ROOT
            / contract["immutable_predecessor_evidence"][
                "render_state_acceptance"
            ]["file"]
        ).read_text(encoding="utf-8-sig")
    )
    baseline_capture = json.loads(
        (
            ROOT
            / contract["immutable_predecessor_evidence"][
                "baseline_capture_manifest"
            ]["file"]
        ).read_text(encoding="utf-8-sig")
    )
    candidate_capture = json.loads(
        (
            ROOT
            / contract["immutable_predecessor_evidence"][
                "candidate_capture_manifest"
            ]["file"]
        ).read_text(encoding="utf-8-sig")
    )
    capture_records = recovery01_failure["captures"]["files"]
    capture_hashes_pass = (
        len(capture_records) == 17
        and all(
            Path(item["path"]).is_file()
            and sha256_file(Path(item["path"])) == item["sha256"]
            for item in capture_records
        )
    )
    cpp_sources_match = locked_files_pass(contract["cpp_fix"])
    compiled = (
        COMPILED_MODULE.is_file()
        and COMPILED_MODULE.stat().st_mtime_ns
        >= max(
            PROFILE_HEADER.stat().st_mtime_ns,
            PROFILE_SOURCE.stat().st_mtime_ns,
        )
    )
    recovery_root = ROOT / contract["recovery_execution"]["recovery_root"]
    request_method = source.split(
        "void USkyguardPhase4LandscapePerformanceCapture::"
        "RequestMeasurementStart()",
        1,
    )[1].split(
        "void USkyguardPhase4LandscapePerformanceCapture::"
        "ConfirmMeasurementStart()",
        1,
    )[0]
    checks = {
        "contract_is_offline_pending_authorization": (
            contract["status"]
            == "OFFLINE_RECOVERY03_DESIGN_READY_PENDING_AUTHORIZATION"
            and contract["recovery_execution"]["promotion_allowed"] is False
            and contract["recovery_execution"]["automatic_retry_allowed"]
            is False
        ),
        "predecessor_evidence_hashes_locked": locked_files_pass(
            contract["immutable_predecessor_evidence"]
        ),
        "all_five_packages_locked": locked_files_pass(
            contract["immutable_packages"]
        ),
        "cpp_fix_sources_and_binary_ready": cpp_sources_match and compiled,
        "async_csv_start_state_machine_exact": (
            "bMeasurementStartRequested" in header
            and "MeasurementStartRequestPlatformSeconds" in header
            and "RequestMeasurementStart" in header
            and "ConfirmMeasurementStart" in header
            and "FailMeasurementStart" in header
            and "CsvStartActivationTimeoutSeconds = 5.0" in source
            and 'GEngine->Exec(World, TEXT("csvprofile start"))'
            in request_method
            and "IsCapturing()" not in request_method
            and "FCsvProfiler::Get()->IsCapturing()" in source
            and "[P4_PROFILE_MEASURED_START_REQUESTED]" in source
            and "[P4_PROFILE_MEASURED_START]" in source
        ),
        "recovery02_failure_boundary_exact": (
            recovery02_failure["terminal_state"]
            == "FAILED_PARTIAL_PROFILE_REJECTED"
            and recovery02_failure["failure_classification"]
            == "UNREAL_BENCHMARK_LIFETIME_CONTROLLED_EXIT"
            and recovery02_failure["immutable_evidence"][
                "rejected_partial_csv"
            ]["accepted_for_gate"]
            is False
            and recovery02_failure["immutable_evidence"][
                "rejected_partial_csv"
            ]["captureduration_seconds"]
            == 14.875955
            and recovery02_manifest["terminal_state"] == "FAILED"
            and len(recovery02_manifest["stages"]) == 1
        ),
        "render_state_acceptance_reused_exact": (
            render["gate"] == "PASS"
            and render["rhi_validation"] == "D3D12|SM6"
            and render["landscape_visible_audit"][
                "render_state_created_component_count"
            ]
            == 16
            and render["landscape_visible_audit"][
                "contract_camera_frustum_intersection_count"
            ]
            == 5
        ),
        "capture_manifests_reused_exact": (
            baseline_capture["rhi_validation"] == "D3D12|SM6"
            and candidate_capture["rhi_validation"] == "D3D12|SM6"
            and baseline_capture["requested_lit_count"] == 5
            and baseline_capture["requested_diagnostic_count"] == 0
            and candidate_capture["requested_lit_count"] == 5
            and candidate_capture["requested_diagnostic_count"] == 7
            and baseline_capture["files_complete_at_script_exit"] is True
            and candidate_capture["files_complete_at_script_exit"] is True
            and baseline_capture["world_saved"] is False
            and candidate_capture["world_saved"] is False
            and baseline_capture["pcg_generation_invoked"] is False
            and candidate_capture["pcg_generation_invoked"] is False
        ),
        "all_17_capture_hashes_locked": capture_hashes_pass,
        "supervisor_is_profile_only": (
            "-ExecutePythonScript" not in supervisor
            and "-NullRHI" not in supervisor
            and "author_immutable_candidate" not in supervisor
            and "CaptureScript" not in supervisor
            and "RenderVerifier" not in supervisor
            and "Invoke-ProfileStage" in supervisor
        ),
        "benchmark_lifetime_flags_absent": all(
            token not in supervisor
            for token in (
                '"-benchmark",',
                '"-benchmarkseconds=',
                '"-fps=',
            )
        ),
        "native_controller_owns_profile_lifetime": (
            "-SkyguardP45ProfileWarmupSeconds=30" in supervisor
            and "-SkyguardP45ProfileMeasuredSeconds=60" in supervisor
            and "-csvCaptureFrames" not in supervisor
            and "-d3d12" in supervisor
            and "-sm6" in supervisor
        ),
        "supervisor_reuses_accepted_evidence_and_refuses_duplicate": (
            "accepted_capture_evidence.hash_manifest" in supervisor
            and "Accepted predecessor capture hash failed" in supervisor
            and "Recovery03 root already exists; refuse duplicate or overwrite"
            in supervisor
        ),
        "recovery03_root_absent": not recovery_root.exists(),
    }
    ready = all(checks.values())
    gate = (
        "PASS_RECOVERY03_READY_PENDING_AUTHORIZATION"
        if ready
        else "FAIL_RECOVERY03_OFFLINE_NOT_READY"
    )
    report = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt05-recovery03-readiness.v1"
        ),
        "recovery_id": contract["recovery_id"],
        "gate": gate,
        "scope": "offline profiling-only continuation",
        "unreal_launched": False,
        "candidate_mutated": False,
        "authoring_will_rerun": False,
        "render_state_verifier_will_rerun": False,
        "captures_will_rerun": False,
        "recovery02_partial_csv_will_be_used": False,
        "promotion_allowed": False,
        "compiled_module_fresh_for_fix": compiled,
        "compiled_module_sha256": (
            sha256_file(COMPILED_MODULE)
            if COMPILED_MODULE.is_file()
            else None
        ),
        "checks": checks,
        "remaining_before_execution": (
            ["obtain explicit authorization for exactly one recovery03 run"]
            if ready
            else ["repair failing offline readiness checks"]
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
