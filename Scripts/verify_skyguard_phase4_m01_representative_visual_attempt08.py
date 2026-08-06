"""Offline verifier for the Attempt08 representative visual-proof design."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DOCS = ROOT / "Docs/AAA_Review"
CONTRACT = DOCS / "PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_CONTRACT.json"
CAMERAS = DOCS / "PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_CAMERAS.json"
VISUAL = DOCS / "PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_VISUAL_RUBRIC.json"
PERFORMANCE = DOCS / "PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_PERFORMANCE_RUBRIC.json"
EXECUTOR = ROOT / "Scripts/capture_skyguard_phase4_m01_representative_visual_attempt08.py"
CONTRACT_ID = "P4.6-M01-REPRESENTATIVE-VISUAL-008"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def verify() -> dict:
    contract, cameras, visual, performance = map(load, (CONTRACT, CAMERAS, VISUAL, PERFORMANCE))
    checks: dict[str, bool] = {}
    checks["identity"] = all(
        item["contract_id"] == CONTRACT_ID for item in (contract, cameras, visual, performance)
    )
    checks["authority_hashes"] = all(
        sha256_file(ROOT / item["file"]) == item["sha256"]
        for item in contract["immutable_authority"].values()
    )
    checks["locked_source_hashes"] = all(
        "sha256" not in item or (
            (ROOT / item["file"]).is_file()
            and (ROOT / item["file"]).stat().st_size == item["bytes"]
            and sha256_file(ROOT / item["file"]) == item["sha256"]
        )
        for item in contract["locked_sources"].values()
    )
    output = ROOT / contract["execution"]["output_root"]
    attempt = ROOT / contract["execution"]["attempt_root"]
    checks["new_namespace_absent"] = not output.exists() and not attempt.exists()
    checks["camera_counts"] = (
        len(cameras["cameras"]) == 5
        and len(cameras["temporal_route_samples"]) == 3
        and cameras["coverage"]["rear_gunner_gameplay_camera_count"] == 2
    )
    checks["camera_roll_zero"] = all(
        spec["rotation_degrees"]["roll"] == 0
        for spec in cameras["cameras"] + cameras["temporal_route_samples"]
    )
    checks["visual_fail_closed"] = (
        visual["decision"]["automatic_checks_must_all_pass"]
        and visual["decision"]["human_checks_must_all_pass"]
        and len(visual["human_checks"]["reject_if_any"]) >= 10
    )
    measured = performance["measured_interval"]
    checks["performance_absolute"] = (
        performance["policy"]["absolute_budgets_are_required"]
        and measured["frames_over_50_ms"] == 0
        and measured["shader_compiles_during_measured_interval"] == 0
        and measured["critical_log_hits"] == 0
    )
    execution = contract["execution"]
    checks["single_attempt_policy"] = (
        execution["single_execution_only"]
        and not execution["automatic_retry"]
        and not execution["failed_namespace_reuse"]
        and execution["unreal_process_count"] == 1
    )
    checks["read_only_policy"] = (
        execution["world_save_forbidden"]
        and execution["asset_mutation_forbidden"]
        and execution["pcg_generation_forbidden"]
        and execution["network_forbidden"]
    )
    source = EXECUTOR.read_text(encoding="utf-8-sig")
    ast.parse(source)
    checks["executor_syntax"] = True
    checks["executor_deferred_tick"] = (
        "register_slate_post_tick_callback" in source
        and "stable_ready_polls_required" in source
        and "same_stack_compilation_finish_called" in source
        and "finish_all_compilation" not in source
        and "measurement_started" in source
        and "warmup_seconds" in source
    )
    checks["executor_no_mutation_calls"] = all(
        token not in source for token in (
            "save_current_level", "save_loaded_asset", "save_directory",
            "generate_local", "import_asset_tasks", "rename_asset", "delete_asset"
        )
    )
    gate = (
        "PASSED_READY_FOR_EXPLICIT_SINGLE_UNREAL_VISUAL_PROOF_AUTHORIZATION"
        if all(checks.values())
        else "FAILED_WITH_EVIDENCE"
    )
    return {"schema": "skyguard.phase4.m01-representative-visual-attempt08-readiness.v1", "contract_id": CONTRACT_ID, "gate": gate, "checks": checks}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
