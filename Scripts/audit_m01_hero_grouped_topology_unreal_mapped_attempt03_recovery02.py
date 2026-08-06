"""Offline readiness audit for pilot-gated synchronized Recovery02."""

from __future__ import annotations

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY02_CONTRACT.json"
EXECUTION_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY02_EXECUTION_CONTRACT.json"
BASE_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
CAPTURE_PATH = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery02.py"
SELECTOR_PATH = ROOT / "Scripts/select_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery02.py"
AUDITOR_PATH = ROOT / "Scripts/verify_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery02_execution.py"
SUPERVISOR_PATH = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery02.ps1"
OUTPUT_PATH = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY02_OFFLINE_READINESS.json"


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
    execution = json.loads(EXECUTION_CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    base = json.loads(BASE_CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    capture = CAPTURE_PATH.read_text(encoding="utf-8-sig")
    selector = SELECTOR_PATH.read_text(encoding="utf-8-sig")
    auditor = AUDITOR_PATH.read_text(encoding="utf-8-sig")
    supervisor = SUPERVISOR_PATH.read_text(encoding="utf-8-sig")
    checks: list[dict] = []

    bound_ok = True
    for record in contract["bound_evidence"].values():
        path = ROOT / record["path"]
        bound_ok &= (
            path.is_file()
            and path.stat().st_size == record["bytes"]
            and sha256_file(path) == record["sha256"]
        )
    add(checks, "failed_evidence_and_review_map_bound", bound_ok, "all hashes exact")
    execution_ok = True
    for record in execution["bound_files"].values():
        path = ROOT / record["path"]
        execution_ok &= (
            path.is_file()
            and path.stat().st_size == record["bytes"]
            and sha256_file(path) == record["sha256"]
        )
    add(checks, "execution_files_hash_bound", execution_ok, "all execution hashes exact")

    diagnosis = json.loads(
        (ROOT / contract["bound_evidence"]["diagnosis"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    add(
        checks,
        "blank_stale_diagnosis_specific",
        diagnosis.get("gate")
        == "PASS_OFFLINE_BLANK_STALE_CAPTURE_DIAGNOSIS_READY_FOR_RECOVERY02"
        and diagnosis["comparison"]["attempt03_unique_png_hash_count"] == 63
        and diagnosis["comparison"]["recovery01_unique_png_hash_count"] == 3
        and diagnosis["comparison"]["all_recovery01_metrics_blank"] is True,
        diagnosis["root_cause"]["classification"],
    )
    pilot = contract["pilot"]
    add(
        checks,
        "tiny_pilot_is_hard_gate_before_full_sweep",
        pilot["must_pass_before_full_sweep"]
        and pilot["capture_count"] == 3
        and pilot["hard_liveness_bounds"]["unique_png_hash_count"] == 3
        and pilot["hard_liveness_bounds"][
            "minimum_active_pixel_fraction_luma_gt_8"
        ]
        == 0.02
        and pilot["hard_liveness_bounds"]["minimum_max_channel_value"] == 64
        and pilot["hard_liveness_bounds"]["minimum_unique_color_count"] == 64
        and pilot["hard_liveness_bounds"]["maximum_sentinel_magenta_fraction"]
        == 0.001,
        "3 live unique pilot PNGs required before any full-sweep output",
    )
    add(
        checks,
        "synchronized_fresh_lifecycle_exact_75_total",
        contract["capture"]["fresh_scene_capture_actor_per_frame"]
        and contract["capture"]["fresh_render_target_per_frame"]
        and contract["capture"]["sentinel_clear_before_capture"]
        and contract["capture"]["render_state_dirty_after_light_change"]
        and contract["capture"]["immediate_capture_scene_calls_per_frame"] == 6
        and contract["capture"]["full_sweep_capture_count"] == 72
        and contract["capture"]["total_process_capture_count"] == 75,
        "3 pilot + 72 full sweep",
    )
    keys = [rig["key_lux"] for rig in contract["capture"]["rig_candidates"]]
    add(
        checks,
        "bounded_transition_rig_range",
        keys
        == [36000.0, 44000.0, 52000.0, 60000.0, 68000.0, 76000.0, 84000.0, 92000.0],
        str(keys),
    )
    add(
        checks,
        "original_selector_bounds_unchanged",
        all(
            contract["selector"][key] == base["exposure_sweep"]["selector"][key]
            for key in (
                "active_pixel_threshold_luma",
                "maximum_active_clipped_fraction_luma_ge_250",
                "active_p50_range",
                "active_p95_range",
                "minimum_active_dynamic_range_p95_minus_p05",
                "canonical_capture_count",
            )
        ),
        "no acceptance relaxation",
    )
    for path in (CAPTURE_PATH, SELECTOR_PATH, AUDITOR_PATH):
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    add(checks, "python_sources_parse", True, "capture,selector,auditor")
    add(
        checks,
        "capture_is_pilot_gated_and_read_only",
        capture.index("if not pilot_pass:") < capture.index("sweep_output.mkdir()")
        and "create_render_target2d" in capture
        and "clear_render_target2d" in capture
        and "decode_png_rgb" in capture
        and "new_level" not in capture
        and "save_current_level" not in capture
        and "save_loaded_asset" not in capture,
        "in-process liveness proof gates full sweep; no content saves",
    )
    add(
        checks,
        "selector_requires_bound_pilot_and_global_rig",
        "pilot_receipt_sha256" in selector
        and "PASS_RECOVERY02_PILOT_LIVE_FULL_SWEEP_ALLOWED" in selector
        and "all_nine_hard_bounds_passed" in selector
        and "shutil.copyfile" in selector,
        "pilot receipt first, one global rig second",
    )
    add(
        checks,
        "supervisor_explicit_single_process_owned_cleanup",
        "AuthorizeSingleRecovery02Run" in supervisor
        and "ExpectedExecutionContractSha256" in supervisor
        and supervisor.count("-FilePath $EditorExe") == 1
        and "-d3d12" in supervisor
        and "-sm6" in supervisor
        and "-NullRHI" not in supervisor
        and "Stop-OwnedProcessTree" in supervisor
        and "pilot_passed_before_full_sweep = $true" in supervisor,
        "one bounded future Unreal process",
    )
    add(
        checks,
        "execution_auditor_detects_duplicate_or_stale_full_sweep",
        "len(set(capture_hashes)) == 72" in auditor
        and "pilot_proved_live_synchronized_rendering" in auditor
        and "attempt03_review_map_hash_invariance" in auditor
        and "runtime_map_hash_invariance" in auditor
        and "config_hash_invariance" in auditor,
        "72 unique full-sweep hashes plus all package domains",
    )
    attempt_root = ROOT / execution["outputs"]["attempt_root"]
    add(checks, "immutable_output_absent", not attempt_root.exists(), str(attempt_root))
    add(
        checks,
        "promotion_and_p3_4_false",
        contract["promotion_allowed"] is False
        and contract["p3_4_closed"] is False
        and execution["promotion_allowed"] is False
        and execution["p3_4_closed"] is False,
        "Recovery02 cannot promote or close P3.4",
    )
    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery02-offline-readiness.v1",
        "gate": (
            "PASS_OFFLINE_READY_AWAITING_SEPARATE_RECOVERY02_AUTHORIZATION"
            if not failures
            else "FAIL_OFFLINE_RECOVERY02_NOT_READY"
        ),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "failure_count": len(failures),
        "failures": failures,
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
