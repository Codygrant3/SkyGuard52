"""Offline-only readiness audit for native frame-driven Recovery05."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY05_NATIVE_DESIGN_CONTRACT.json"
OUTPUT_PATH = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY05_NATIVE_DESIGN_READINESS.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add(checks: list[dict], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def audit(write_report: bool = True) -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    checks: list[dict] = []

    evidence_ok = True
    for record in contract["bound_evidence"].values():
        path = ROOT / record["path"]
        evidence_ok &= (
            path.is_file()
            and path.stat().st_size == record["bytes"]
            and sha256_file(path) == record["sha256"]
        )
    add(checks, "invalid_run_known_nonblank_and_review_map_bound", evidence_ok, "all hashes exact")

    sources_ok = True
    for record in contract["native_sources"].values():
        path = ROOT / record["path"]
        sources_ok &= (
            path.is_file()
            and path.stat().st_size == record["bytes"]
            and sha256_file(path) == record["sha256"]
        )
    add(checks, "native_sources_hash_bound", sources_ok, "header and implementation exact")

    diagnosis = json.loads(
        (ROOT / contract["bound_evidence"]["recovery05_diagnosis"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    add(
        checks,
        "frame_lifecycle_root_cause_specific",
        diagnosis.get("gate")
        == "PASS_OFFLINE_FRAME_LIFECYCLE_DIAGNOSIS_READY_FOR_NATIVE_RECOVERY05"
        and diagnosis["root_cause"]["classification"]
        == "OFFSCREEN_PYTHON_CAPTURE_BEFORE_NATIVE_WORLD_VIEWPORT_RENDER_READINESS"
        and diagnosis["known_nonblank_lifecycle"]["capture_rhi_validation_log_frame"] == 313
        and diagnosis["failed_recovery_lifecycle"]["saved_review_map_loaded_then_python_capture_started_near_log_frame"] == 2,
        diagnosis["root_cause"]["classification"],
    )
    add(
        checks,
        "recovery04_explicitly_toctou_invalid",
        diagnosis["recovery04_status"]["provenance"]
        == "TOCTOU_INVALID_PRESERVED_DIAGNOSTIC_ONLY"
        and diagnosis["recovery04_status"]["full_view_capture_count"] == 0,
        "preserved diagnostic evidence, never acceptance evidence",
    )

    header_path = ROOT / contract["native_sources"]["header"]["path"]
    cpp_path = ROOT / contract["native_sources"]["implementation"]["path"]
    header = header_path.read_text(encoding="utf-8-sig")
    cpp = cpp_path.read_text(encoding="utf-8-sig")
    add(
        checks,
        "native_tickable_inert_by_default",
        "UTickableWorldSubsystem" in header
        and "RequiredContractId" in cpp
        and "ContractId == RequiredContractId" in cpp
        and "return bRequested" in cpp,
        "exact contract id activates native worker",
    )
    add(
        checks,
        "actual_viewport_capture_not_python_scene_capture",
        "FScreenshotRequest::RequestScreenshot" in cpp
        and "OnScreenshotCaptured" in cpp
        and "PNGCompressImageArray" in cpp
        and "SceneCapture2D" not in cpp
        and "ExecutePythonScript" not in cpp,
        "real game viewport callback and native PNG persistence",
    )
    runtime = contract["native_runtime"]
    add(
        checks,
        "real_frame_shader_idle_warmup",
        "GShaderCompilingManager->IsCompiling()" in cpp
        and "RequiredConsecutiveReadyFrames = 30" in cpp
        and "RequiredWarmupFrames = 120" in cpp
        and "RequiredWarmupSeconds = 5.0" in cpp
        and runtime["world_ready_consecutive_frames"] == 30
        and runtime["warmup_frames"] == 120
        and runtime["warmup_seconds_minimum"] == 5.0,
        "shader activity resets a 120-frame, five-second warmup",
    )
    add(
        checks,
        "pilot_precedes_governed_views",
        "PilotIndex < 3" in cpp
        and cpp.index("PilotRecords.Add(Record)") < cpp.index("ViewRecords.Add(Record)")
        and runtime["pilot_capture_count"] == 3
        and runtime["full_view_capture_count"] == 9
        and runtime["pilot_must_pass_before_full_views"],
        "three live native frames before nine views",
    )
    hard = contract["hard_bounds"]
    add(
        checks,
        "hard_bounds_unchanged",
        hard["active_pixel_threshold_luma"] == 8
        and hard["maximum_active_clipped_fraction_luma_ge_250"] == 0.02
        and hard["active_p50_range"] == [35, 210]
        and hard["active_p95_range"] == [100, 248]
        and hard["minimum_active_dynamic_range_p95_minus_p05"] == 35,
        "no acceptance relaxation",
    )
    add(
        checks,
        "native_build_and_launch_separately_gated",
        contract["future_build"]["requires_separate_authorization"]
        and contract["future_build"]["unreal_launch_allowed_during_build_stage"] is False
        and contract["future_build"]["post_build_dll_hash_must_be_bound_before_execution"]
        and contract["future_build"]["post_build_execution_contract_required"]
        and contract["future_build"]["root_must_wait_for_final_execution_handoff"]
        and contract["native_build_authorized"] is False
        and contract["unreal_launch_authorized"] is False,
        "build first, rebind DLL, then final execution handoff",
    )
    output_root = ROOT / contract["future_output"]["attempt_root"]
    add(checks, "immutable_recovery05_output_absent", not output_root.exists(), str(output_root))
    add(
        checks,
        "content_immutable_and_never_promotes",
        contract["immutability"]["content_package_writes"] == 0
        and contract["immutability"]["runtime_map_writes"] == 0
        and contract["immutability"]["config_writes"] == 0
        and contract["promotion_allowed"] is False
        and contract["p3_4_closed"] is False,
        "source-only design; no content, promotion, or P3.4 closure",
    )

    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery05-native-design-readiness.v1",
        "gate": (
            "PASS_OFFLINE_RECOVERY05_NATIVE_DESIGN_READY_AWAITING_SEPARATE_BUILD_AUTHORIZATION"
            if not failures
            else "FAIL_OFFLINE_RECOVERY05_NATIVE_DESIGN_NOT_READY"
        ),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "failure_count": len(failures),
        "failures": failures,
        "native_build_executed": False,
        "unreal_launched": False,
        "content_packages_created_or_modified": 0,
        "promotion_allowed": False,
        "p3_4_closed": False,
    }
    if write_report:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    result = audit(write_report=True)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if not result["failures"] else 1)
