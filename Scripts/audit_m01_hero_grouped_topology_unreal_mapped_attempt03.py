"""Offline readiness audit for the Build008 Unreal mapped-view Attempt03."""

from __future__ import annotations

import ast
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
EXECUTION_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_EXECUTION_CONTRACT.json"
DIAGNOSIS_PATH = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_DIAGNOSIS.json"
BUILDER_PATH = ROOT / "Scripts/build_m01_hero_grouped_topology_unreal_mapped_attempt03.py"
CAPTURE_PATH = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03.py"
SELECTOR_PATH = ROOT / "Scripts/select_m01_hero_grouped_topology_unreal_mapped_attempt03_exposure.py"
ENTRYPOINT_PATH = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_mapped_attempt03.py"
SUPERVISOR_PATH = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_mapped_attempt03.ps1"
EXECUTION_AUDITOR_PATH = ROOT / "Scripts/verify_m01_hero_grouped_topology_unreal_mapped_attempt03_execution.py"
OUTPUT_PATH = ROOT / "Saved/Reports/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_OFFLINE_READINESS.json"
ATTEMPT03_CONTENT = ROOT / "Content/Skyguard/Candidates/Mission01/HeroGroupedTopology_008_Attempt03"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check(records: list[dict], name: str, passed: bool, detail: str) -> None:
    records.append({"name": name, "passed": bool(passed), "detail": detail})


def audit(write_report: bool = True) -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    execution_contract = json.loads(
        EXECUTION_CONTRACT_PATH.read_text(encoding="utf-8-sig")
    )
    diagnosis = json.loads(DIAGNOSIS_PATH.read_text(encoding="utf-8-sig"))
    builder = BUILDER_PATH.read_text(encoding="utf-8-sig")
    capture = CAPTURE_PATH.read_text(encoding="utf-8-sig")
    selector = SELECTOR_PATH.read_text(encoding="utf-8-sig")
    entrypoint = ENTRYPOINT_PATH.read_text(encoding="utf-8-sig")
    supervisor = SUPERVISOR_PATH.read_text(encoding="utf-8-sig")
    execution_auditor = EXECUTION_AUDITOR_PATH.read_text(encoding="utf-8-sig")
    checks = []

    bound_ok = True
    bound_details = []
    for name, record in contract["bound_inputs"].items():
        path = ROOT / record["path"]
        exists = path.is_file()
        size_ok = exists and path.stat().st_size == record["bytes"]
        hash_ok = exists and sha256_file(path) == record["sha256"]
        bound_ok = bound_ok and size_ok and hash_ok
        bound_details.append(
            f"{name}:exists={exists},size={size_ok},sha256={hash_ok}"
        )
    check(checks, "exact_bound_inputs", bound_ok, "; ".join(bound_details))
    execution_bound_ok = True
    execution_bound_details = []
    for name, record in execution_contract["bound_files"].items():
        path = ROOT / record["path"]
        exists = path.is_file()
        size_ok = exists and path.stat().st_size == record["bytes"]
        hash_ok = exists and sha256_file(path) == record["sha256"]
        execution_bound_ok = execution_bound_ok and size_ok and hash_ok
        execution_bound_details.append(
            f"{name}:exists={exists},size={size_ok},sha256={hash_ok}"
        )
    check(
        checks,
        "exact_execution_bound_files",
        execution_bound_ok,
        "; ".join(execution_bound_details),
    )
    check(
        checks,
        "diagnosis_gate",
        diagnosis.get("gate") == "PASS_OFFLINE_DIAGNOSIS_READY_FOR_ATTEMPT03_CONTRACT",
        str(diagnosis.get("gate")),
    )

    actors = contract["assembly"]["actors"]
    diagnosis_actors = {
        item["key"]: item
        for item in diagnosis["assembly_diagnosis"]["source_authoritative_actor_transforms"]
    }
    actor_keys = [item["key"] for item in actors]
    actor_meshes = [item["mesh"] for item in actors]
    check(
        checks,
        "exact_12_unique_actors",
        len(actors) == 12
        and len(set(actor_keys)) == 12
        and len(set(actor_meshes)) == 12,
        f"actors={len(actors)},keys={len(set(actor_keys))},meshes={len(set(actor_meshes))}",
    )
    transform_match = all(
        item["key"] in diagnosis_actors
        and item["relative_location_cm"]
        == diagnosis_actors[item["key"]]["unreal_relative_location_cm"]
        and item["actor_location_cm"]
        == diagnosis_actors[item["key"]]["attempt03_actor_location_cm"]
        for item in actors
    )
    check(
        checks,
        "source_authoritative_transforms_exact",
        transform_match,
        "contract actor locations equal GLB-derived diagnosis locations",
    )
    check(
        checks,
        "identity_rotation_scale",
        contract["assembly"]["rotation_degrees"] == [0.0, 0.0, 0.0]
        and contract["assembly"]["scale"] == [1.0, 1.0, 1.0],
        "no geometry-space workaround is permitted",
    )

    candidate = contract["candidate"]
    immutable_policy = (
        candidate["existing_packages_are_immutable"]
        and not candidate["replace_existing"]
        and not candidate["geometry_change_allowed"]
        and not candidate["uv_change_allowed"]
        and not candidate["bake_change_allowed"]
        and not candidate["material_change_allowed"]
        and not candidate["mesh_setting_change_allowed"]
        and not candidate["runtime_map_change_allowed"]
        and not candidate["config_change_allowed"]
        and candidate["attempt03_new_package_count"] == 1
    )
    check(
        checks,
        "one_new_map_only_policy",
        immutable_policy,
        candidate["attempt03_review_map"],
    )
    check(
        checks,
        "attempt03_namespace_currently_absent",
        not ATTEMPT03_CONTENT.exists(),
        str(ATTEMPT03_CONTENT),
    )

    sweep = contract["exposure_sweep"]
    expected_pilots = (
        len(sweep["manual_exposure_bias_candidates_ev"])
        * len(sweep["families"])
        * len(sweep["views_per_family"])
    )
    check(
        checks,
        "single_process_exact_63_sweep",
        sweep["single_unreal_process"]
        and sweep["pilot_capture_count"] == 63
        and expected_pilots == 63
        and sweep["one_global_bias_for_all_views"],
        f"calculated={expected_pilots},contract={sweep['pilot_capture_count']}",
    )
    selector_policy = sweep["selector"]
    check(
        checks,
        "bounded_numeric_selector",
        selector_policy["maximum_active_clipped_fraction_luma_ge_250"] == 0.02
        and selector_policy["minimum_active_dynamic_range_p95_minus_p05"] == 35
        and selector_policy["canonical_capture_count"] == 9
        and selector_policy["selector_must_run_after_unreal_exit"],
        json.dumps(selector_policy, sort_keys=True),
    )

    for path in (
        BUILDER_PATH,
        CAPTURE_PATH,
        SELECTOR_PATH,
        ENTRYPOINT_PATH,
        EXECUTION_AUDITOR_PATH,
    ):
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    check(
        checks,
        "python_sources_parse",
        True,
        "builder,capture,selector,one-process-entrypoint,execution-auditor",
    )
    check(
        checks,
        "builder_reuses_meshes_without_asset_mutation",
        "import_asset_tasks" not in builder
        and "rename_asset" not in builder
        and "delete_asset" not in builder
        and "save_loaded_asset" not in builder
        and "set_material" not in builder
        and "set_editor_property(\"nanite_settings\"" not in builder
        and "save_current_level" in builder,
        "only the new Attempt03 review map may be saved",
    )
    check(
        checks,
        "capture_is_read_only",
        "save_current_level" not in capture
        and "save_directory" not in capture
        and "save_loaded_asset" not in capture
        and "capture_count" in capture
        and "package_save_invoked" in capture,
        "capture exports PNG/JSON only",
    )
    selector_tree = ast.parse(selector, filename=str(SELECTOR_PATH))
    selector_imports = {
        alias.name
        for node in ast.walk(selector_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module
        for node in ast.walk(selector_tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    check(
        checks,
        "selector_is_offline_and_deterministic",
        "subprocess" not in selector_imports
        and "unreal" not in selector_imports
        and "bpy" not in selector_imports
        and "shutil.copyfile" in selector
        and "all_nine_hard_bounds_passed" in selector,
        "no heavy tool import/launch path",
    )
    check(
        checks,
        "one_unreal_process_entrypoint_is_sequential",
        "builder.main()" in entrypoint
        and "capture.main()" in entrypoint
        and entrypoint.index("builder.main()") < entrypoint.index("capture.main()")
        and "PASS_ATTEMPT03_ONE_PROCESS_BUILD_AND_SWEEP_AWAITING_OFFLINE_SELECTION"
        in entrypoint,
        "map assembly then full sweep in the same Unreal process",
    )
    check(
        checks,
        "supervisor_is_explicit_bounded_and_fail_closed",
        "AuthorizeSingleAttempt03Run" in supervisor
        and "ExpectedExecutionContractSha256" in supervisor
        and supervisor.count("-FilePath $EditorExe") == 1
        and "-d3d12" in supervisor
        and "-sm6" in supervisor
        and "-NullRHI" not in supervisor
        and "Stop-OwnedProcessTree" in supervisor
        and "exactly_one_unreal_process_launched = $true" in supervisor
        and "FAIL_CLOSED_ATTEMPT03_NOT_ACCEPTED" in supervisor,
        "one governed Unreal process plus bounded offline Python stages",
    )
    check(
        checks,
        "supervisor_runs_selector_and_independent_auditor_after_unreal",
        supervisor.index("$selectorArguments") > supervisor.index("$unrealArguments")
        and supervisor.index("$auditorArguments") > supervisor.index("$selectorArguments")
        and "original_candidate_hash_invariance" in execution_auditor
        and "runtime_map_hash_invariance" in execution_auditor
        and "config_hash_invariance" in execution_auditor,
        "offline selector and package-hash audit are sequenced after Unreal exit",
    )
    attempt_output = ROOT / execution_contract["outputs"]["attempt_root"]
    build_report = ROOT / execution_contract["outputs"]["build_report"]
    check(
        checks,
        "immutable_execution_outputs_currently_absent",
        not attempt_output.exists()
        and not build_report.exists()
        and not ATTEMPT03_CONTENT.exists(),
        f"attempt={attempt_output},build_report={build_report},content={ATTEMPT03_CONTENT}",
    )
    check(
        checks,
        "promotion_and_p3_4_remain_false",
        contract["promotion_allowed"] is False
        and contract["p3_4_closed"] is False
        and contract["acceptance"]["promotion_allowed_on_pass"] is False
        and contract["acceptance"]["p3_4_closed_on_pass"] is False,
        "Attempt03 cannot authorize promotion or close P3.4",
    )
    failures = [item for item in checks if not item["passed"]]
    report = {
        "schema": "skyguard.m01.hero-grouped-topology-unreal-mapped-attempt03-offline-readiness.v1",
        "gate": (
            "PASS_OFFLINE_READY_AWAITING_SEPARATE_UNREAL_ATTEMPT03_AUTHORIZATION"
            if not failures
            else "FAIL_OFFLINE_NOT_READY"
        ),
        "build_id": contract["build_id"],
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "contract": {
            "path": str(CONTRACT_PATH),
            "sha256": sha256_file(CONTRACT_PATH),
        },
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
