"""Offline readiness audit for persistent-capture Recovery03."""

from __future__ import annotations

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY03_CONTRACT.json"
EXECUTION_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY03_EXECUTION_CONTRACT.json"
BASE_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
CAPTURE_PATH = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery03.py"
SELECTOR_PATH = ROOT / "Scripts/select_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery03.py"
AUDITOR_PATH = ROOT / "Scripts/verify_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery03_execution.py"
SUPERVISOR_PATH = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery03.ps1"
OUTPUT_PATH = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY03_OFFLINE_READINESS.json"


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
    add(checks, "failed_evidence_known_good_and_review_map_bound", bound_ok, "all hashes exact")

    execution_ok = True
    for name, record in execution["bound_files"].items():
        if name == "readiness_auditor":
            continue
        path = ROOT / record["path"]
        execution_ok &= (
            path.is_file()
            and path.stat().st_size == record["bytes"]
            and sha256_file(path) == record["sha256"]
        )
    add(checks, "execution_files_hash_bound", execution_ok, "all non-self execution hashes exact")

    diagnosis = json.loads(
        (ROOT / contract["bound_evidence"]["diagnosis"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    add(
        checks,
        "capture_lifecycle_root_cause_specific",
        diagnosis.get("gate")
        == "PASS_OFFLINE_CAPTURE_LIFECYCLE_DIAGNOSIS_READY_FOR_RECOVERY03"
        and diagnosis["root_cause"]["classification"]
        == "FRESH_SCENE_CAPTURE_COMPONENT_NOT_RENDER_READY_WITHIN_SAME_OFFSCREEN_PYTHON_TICK",
        diagnosis["root_cause"]["classification"],
    )

    pilot = contract["pilot"]
    add(
        checks,
        "three_frame_pilot_hard_gates_full_sweep",
        pilot["must_pass_before_full_sweep"]
        and pilot["capture_count"] == 3
        and pilot["hard_liveness_bounds"]["unique_png_hash_count"] == 3
        and pilot["hard_liveness_bounds"]["minimum_active_pixel_fraction_luma_gt_8"] == 0.02
        and pilot["hard_liveness_bounds"]["minimum_max_channel_value"] == 64
        and pilot["hard_liveness_bounds"]["minimum_unique_color_count"] == 64
        and pilot["hard_liveness_bounds"]["maximum_sentinel_magenta_fraction"] == 0.001,
        "three unique live non-sentinel pilot PNGs required",
    )

    capture_policy = contract["capture"]
    add(
        checks,
        "persistent_lifecycle_exact_75_exports",
        capture_policy["persistent_scene_capture_actor_count"] == 1
        and capture_policy["persistent_render_target_count"] == 1
        and capture_policy["reuse_same_capture_and_target_for_pilot_and_sweep"]
        and capture_policy["sentinel_clear_before_every_export"]
        and capture_policy["immediate_capture_scene_calls_per_export"] == 6
        and capture_policy["unexported_warmup_captures_after_rig_change"] == 3
        and capture_policy["full_sweep_capture_count"] == 72
        and capture_policy["total_exported_capture_count"] == 75,
        "one actor and target; 3 pilot plus 72 sweep exports",
    )
    keys = [rig["key_lux"] for rig in capture_policy["rig_candidates"]]
    add(
        checks,
        "bounded_transition_rig_range",
        keys == [36000.0, 44000.0, 52000.0, 60000.0, 68000.0, 76000.0, 84000.0, 92000.0],
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
    add(checks, "python_sources_parse", True, "capture, selector, execution auditor")
    add(
        checks,
        "capture_persistent_pilot_gated_and_read_only",
        capture.count("BASE.make_capture_component(") == 1
        and capture.index("if not pilot_pass:") < capture.index("sweep_output.mkdir()")
        and "clear_render_target2d" in capture
        and "always_persist_rendering_state" in capture
        and "unexported_warmup_captures_after_rig_change" in capture
        and "new_level" not in capture
        and "save_current_level" not in capture
        and "save_loaded_asset" not in capture
        and "import_asset_tasks" not in capture
        and "rename_asset" not in capture
        and "delete_asset" not in capture,
        "single persistent capture creation, hard pilot gate, no content writes",
    )
    add(
        checks,
        "selector_requires_pilot_and_one_global_rig",
        "PASS_RECOVERY03_PERSISTENT_PILOT_LIVE_FULL_SWEEP_ALLOWED" in selector
        and "all_nine_hard_bounds_passed" in selector
        and "shutil.copyfile" in selector,
        "bound pilot first, one global rig second",
    )
    add(
        checks,
        "supervisor_explicit_single_process_owned_cleanup",
        "AuthorizeSingleRecovery03Run" in supervisor
        and "ExpectedExecutionContractSha256" in supervisor
        and supervisor.count("-FilePath $EditorExe") == 1
        and "-d3d12" in supervisor
        and "-sm6" in supervisor
        and "-NullRHI" not in supervisor
        and "Stop-OwnedProcessTree" in supervisor
        and "pilot_passed_before_sweep = $true" in supervisor,
        "one bounded future Unreal process",
    )
    add(
        checks,
        "execution_auditor_rejects_stale_or_duplicate_output",
        "len(set(hashes)) == 72" in auditor
        and "persistent_pilot_proved_live_rendering" in auditor
        and "attempt03_review_map_hash_invariance" in auditor
        and "runtime_map_hash_invariance" in auditor
        and "config_hash_invariance" in auditor,
        "72 unique sweep hashes and all package domains",
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
        "Recovery03 cannot promote or close P3.4",
    )

    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery03-offline-readiness.v1",
        "gate": (
            "PASS_OFFLINE_READY_AWAITING_SEPARATE_RECOVERY03_AUTHORIZATION"
            if not failures
            else "FAIL_OFFLINE_RECOVERY03_NOT_READY"
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
