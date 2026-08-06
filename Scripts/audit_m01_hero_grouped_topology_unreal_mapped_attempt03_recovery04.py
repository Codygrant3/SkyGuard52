"""Offline readiness audit for base-lighting Recovery04."""

from __future__ import annotations

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY04_CONTRACT.json"
EXECUTION_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY04_EXECUTION_CONTRACT.json"
BASE_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
CAPTURE_PATH = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery04.py"
AUDITOR_PATH = ROOT / "Scripts/verify_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery04_execution.py"
SUPERVISOR_PATH = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery04.ps1"
OUTPUT_PATH = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY04_OFFLINE_READINESS.json"


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
    add(checks, "recovery03_failure_known_good_and_review_map_bound", bound_ok, "all hashes exact")

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
        (ROOT / contract["bound_evidence"]["diagnosis"]["path"]).read_text(encoding="utf-8-sig")
    )
    add(
        checks,
        "light_proxy_and_exposure_diagnosis_specific",
        diagnosis.get("gate")
        == "PASS_OFFLINE_LIGHT_PROXY_AND_EXPOSURE_DIAGNOSIS_READY_FOR_RECOVERY04"
        and diagnosis["root_cause"]["classification"]
        == "TRANSIENT_LIGHT_PROXY_INVALIDATION_WITHOUT_EDITOR_TICK_COMBINED_WITH_UNRESOLVED_EXPOSURE"
        and diagnosis["failed_recovery03"]["persistent_scene_capture_actor_count"] == 1
        and diagnosis["failed_recovery03"]["maximum_channel_value_all_frames"] == 1,
        diagnosis["root_cause"]["classification"],
    )

    base_lighting = base["exposure_sweep"]["lighting"]
    lighting = contract["lighting"]
    add(
        checks,
        "exact_known_nonblank_lighting_without_proxy_changes",
        lighting["use_exact_base_spawn_lighting"]
        and lighting["key_directional_lux"] == base_lighting["key_directional_lux"]
        and lighting["fill_directional_lux"] == base_lighting["fill_directional_lux"]
        and lighting["skylight_intensity"] == base_lighting["skylight_intensity"]
        and lighting["spawn_once"]
        and lighting["light_intensity_changes_after_spawn"] == 0
        and lighting["mark_render_state_dirty_calls"] == 0
        and lighting["recapture_sky_calls"] == 0,
        "BASE.spawn_lighting once; no proxy invalidation",
    )
    pilot = contract["pilot"]
    add(
        checks,
        "tiny_more_negative_exposure_pilot_hard_gates_full_views",
        pilot["must_pass_before_full_views"]
        and pilot["exposure_candidates_ev"] == [-14, -18, -22, -26, -30, -34]
        and pilot["capture_count"] == 6
        and pilot["capture_scene_calls_per_export"] == 3
        and max(pilot["exposure_candidates_ev"]) < -12,
        "six Pathfinder three-quarter pilot frames below EV -12",
    )
    original_selector = base["exposure_sweep"]["selector"]
    hard = pilot["exposure_hard_bounds"]
    add(
        checks,
        "original_exposure_bounds_unchanged",
        all(
            hard[key] == original_selector[key]
            for key in (
                "active_pixel_threshold_luma",
                "maximum_active_clipped_fraction_luma_ge_250",
                "active_p50_range",
                "active_p95_range",
                "minimum_active_dynamic_range_p95_minus_p05",
            )
        ),
        "no acceptance relaxation",
    )
    add(
        checks,
        "exact_nine_full_views_after_selection",
        contract["full_views"]["capture_only_after_pilot_selection"]
        and contract["full_views"]["selected_exposure_fixed_for_all_views"]
        and contract["full_views"]["capture_count"] == 9
        and contract["full_views"]["each_view_must_pass_original_hard_bounds"]
        and contract["capture"]["total_exported_capture_count"] == 15,
        "6 pilot + conditional 9 full views",
    )

    for path in (CAPTURE_PATH, AUDITOR_PATH):
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    add(checks, "python_sources_parse", True, "capture and execution auditor")
    add(
        checks,
        "capture_exact_base_lifecycle_pilot_gated_read_only",
        capture.count("BASE.spawn_lighting(base_contract)") == 1
        and capture.count("BASE.make_capture_component(") == 1
        and "mark_render_state_dirty" not in capture
        and "recapture_sky" not in capture
        and capture.index("if selected is None:") < capture.index("full_output.mkdir()")
        and "new_level" not in capture
        and "save_current_level" not in capture
        and "save_loaded_asset" not in capture
        and "import_asset_tasks" not in capture
        and "rename_asset" not in capture
        and "delete_asset" not in capture,
        "known-good light lifecycle; pilot before full views; no content writes",
    )
    add(
        checks,
        "execution_auditor_requires_pilot_and_nine_unique_views",
        "exact_base_lighting_live_exposure_pilot" in auditor
        and "len(set(hashes)) == 9" in auditor
        and "attempt03_review_map_hash_invariance" in auditor
        and "runtime_map_hash_invariance" in auditor
        and "config_hash_invariance" in auditor,
        "selected live EV and nine hard-bound-passing views",
    )
    add(
        checks,
        "supervisor_explicit_single_process_owned_cleanup",
        "AuthorizeSingleRecovery04Run" in supervisor
        and "ExpectedExecutionContractSha256" in supervisor
        and supervisor.count("-FilePath $EditorExe") == 1
        and "-d3d12" in supervisor
        and "-sm6" in supervisor
        and "-NullRHI" not in supervisor
        and "Stop-OwnedProcessTree" in supervisor
        and "pilot_passed_before_full_views = $true" in supervisor,
        "one bounded future Unreal process",
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
        "Recovery04 cannot promote or close P3.4",
    )

    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery04-offline-readiness.v1",
        "gate": (
            "PASS_OFFLINE_READY_AWAITING_SEPARATE_RECOVERY04_AUTHORIZATION"
            if not failures
            else "FAIL_OFFLINE_RECOVERY04_NOT_READY"
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
