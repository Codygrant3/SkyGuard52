"""Offline readiness audit for Attempt03 physical-light recovery_01."""

from __future__ import annotations

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY01_CONTRACT.json"
EXECUTION_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY01_EXECUTION_CONTRACT.json"
BASE_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
CAPTURE_PATH = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery01.py"
SELECTOR_PATH = ROOT / "Scripts/select_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery01.py"
SUPERVISOR_PATH = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery01.ps1"
EXECUTION_AUDITOR_PATH = ROOT / "Scripts/verify_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery01_execution.py"
OUTPUT_PATH = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY01_OFFLINE_READINESS.json"


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
    base_contract = json.loads(BASE_CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    capture = CAPTURE_PATH.read_text(encoding="utf-8-sig")
    selector = SELECTOR_PATH.read_text(encoding="utf-8-sig")
    supervisor = SUPERVISOR_PATH.read_text(encoding="utf-8-sig")
    execution_auditor = EXECUTION_AUDITOR_PATH.read_text(encoding="utf-8-sig")
    checks: list[dict] = []

    bound_ok = True
    for record in contract["bound_evidence"].values():
        path = ROOT / record["path"]
        bound_ok = (
            bound_ok
            and path.is_file()
            and path.stat().st_size == record["bytes"]
            and sha256_file(path) == record["sha256"]
        )
    add(checks, "failed_evidence_and_review_map_bound", bound_ok, "all recovery inputs exact")

    execution_bound_ok = True
    for record in execution["bound_files"].values():
        path = ROOT / record["path"]
        execution_bound_ok = (
            execution_bound_ok
            and path.is_file()
            and path.stat().st_size == record["bytes"]
            and sha256_file(path) == record["sha256"]
        )
    add(checks, "execution_files_hash_bound", execution_bound_ok, "all execution inputs exact")

    diagnosis = json.loads(
        (ROOT / contract["bound_evidence"]["diagnosis"]["path"]).read_text(
            encoding="utf-8-sig"
        )
    )
    add(
        checks,
        "saturation_diagnosis_is_specific",
        diagnosis.get("gate")
        == "PASS_OFFLINE_SATURATION_DIAGNOSIS_READY_FOR_RECOVERY01"
        and diagnosis["root_cause"]["classification"]
        == "PHYSICAL_LIGHT_RIG_SATURATION"
        and diagnosis["failed_run_facts"][
            "every_view_at_every_ev_failed_clipping_and_p95_bounds"
        ]
        is True,
        diagnosis["root_cause"]["classification"],
    )

    rigs = contract["capture"]["rig_candidates"]
    add(
        checks,
        "bounded_eight_rig_exact_72_sweep",
        len(rigs) == 8
        and [rig["rig_index"] for rig in rigs] == list(range(8))
        and [rig["key_lux"] for rig in rigs]
        == [250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0, 16000.0, 32000.0]
        and contract["capture"]["fixed_manual_exposure_bias_ev"] == -12
        and contract["capture"]["captures_per_candidate"] == 9
        and contract["capture"]["capture_count"] == 72
        and contract["capture"]["one_global_rig_for_all_views"],
        "8 rigs x 9 mapped views = 72 captures",
    )
    base_selector = base_contract["exposure_sweep"]["selector"]
    recovery_selector = contract["selector"]
    add(
        checks,
        "original_hard_bounds_are_unchanged",
        all(
            recovery_selector[key] == base_selector[key]
            for key in (
                "active_pixel_threshold_luma",
                "maximum_active_clipped_fraction_luma_ge_250",
                "active_p50_range",
                "active_p95_range",
                "minimum_active_dynamic_range_p95_minus_p05",
                "canonical_capture_count",
            )
        ),
        "no acceptance-bound relaxation",
    )

    for path in (CAPTURE_PATH, SELECTOR_PATH, EXECUTION_AUDITOR_PATH):
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    add(checks, "python_sources_parse", True, "capture,selector,execution-auditor")
    add(
        checks,
        "capture_reuses_map_and_never_saves_packages",
        "load_level(recovery[\"review_map\"])" in capture
        and "new_level" not in capture
        and "save_current_level" not in capture
        and "save_loaded_asset" not in capture
        and "import_asset_tasks" not in capture
        and "rename_asset" not in capture
        and "delete_asset" not in capture
        and "package_save_invoked" in capture,
        "PNG and JSON export only",
    )
    selector_tree = ast.parse(selector, filename=str(SELECTOR_PATH))
    imports = {
        alias.name
        for node in ast.walk(selector_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module
        for node in ast.walk(selector_tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    add(
        checks,
        "selector_is_offline_deterministic_and_global",
        "subprocess" not in imports
        and "unreal" not in imports
        and "bpy" not in imports
        and "all_nine_hard_bounds_passed" in selector
        and "shutil.copyfile" in selector
        and "rig_index" in selector,
        "one global rig, deterministic tie-break, byte-for-byte canonical copies",
    )
    add(
        checks,
        "supervisor_is_explicit_single_process_and_fail_closed",
        "AuthorizeSingleRecovery01Run" in supervisor
        and "ExpectedExecutionContractSha256" in supervisor
        and supervisor.count("-FilePath $EditorExe") == 1
        and "-d3d12" in supervisor
        and "-sm6" in supervisor
        and "-NullRHI" not in supervisor
        and "Stop-OwnedProcessTree" in supervisor
        and "existing_review_map_reused_without_reassembly = $true" in supervisor
        and "FAIL_CLOSED_RECOVERY01_NOT_ACCEPTED" in supervisor,
        "one future Unreal process; bounded offline stages after exit",
    )
    add(
        checks,
        "independent_auditor_checks_all_hash_domains",
        all(
            marker in execution_auditor
            for marker in (
                "original_candidate_hash_invariance",
                "attempt03_review_map_hash_invariance",
                "runtime_map_hash_invariance",
                "config_hash_invariance",
                "failed_evidence_and_review_map_still_bound",
            )
        ),
        "candidate, review map, runtime, Config, and failed evidence",
    )
    attempt_root = ROOT / execution["outputs"]["attempt_root"]
    add(
        checks,
        "immutable_recovery_output_currently_absent",
        not attempt_root.exists(),
        str(attempt_root),
    )
    add(
        checks,
        "promotion_and_p3_4_remain_false",
        contract["promotion_allowed"] is False
        and contract["p3_4_closed"] is False
        and execution["promotion_allowed"] is False
        and execution["p3_4_closed"] is False,
        "recovery cannot promote or close P3.4",
    )
    failures = [record for record in checks if not record["passed"]]
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-recovery01-offline-readiness.v1",
        "gate": (
            "PASS_OFFLINE_READY_AWAITING_SEPARATE_RECOVERY01_AUTHORIZATION"
            if not failures
            else "FAIL_OFFLINE_RECOVERY01_NOT_READY"
        ),
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "check_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "failure_count": len(failures),
        "failures": failures,
        "unreal_launched": False,
        "blender_launched": False,
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
