"""Offline-only verifier for the Recovery01 design gate."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DOCS = ROOT / "Docs/AAA_Review"
CONTRACT_PATH = DOCS / "PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY01_CONTRACT.json"
EXECUTOR_PATH = ROOT / "Scripts/capture_skyguard_phase4_m01_representative_visual_attempt08_recovery01.py"
SUPERVISOR_PATH = ROOT / "Scripts/invoke_skyguard_phase4_m01_representative_visual_attempt08_recovery01.ps1"
TEST_PATH = ROOT / "Scripts/tests/test_phase4_m01_representative_visual_attempt08_recovery01.py"
CONTRACT_ID = "P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-01"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_record(record: dict) -> bool:
    path = ROOT / record["file"]
    return (
        path.is_file()
        and ("bytes" not in record or path.stat().st_size == record["bytes"])
        and ("sha256" not in record or sha256_file(path) == record["sha256"])
    )


def verify() -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    executor = EXECUTOR_PATH.read_text(encoding="utf-8-sig")
    supervisor = SUPERVISOR_PATH.read_text(encoding="utf-8-sig")
    ast.parse(executor)
    checks: dict[str, bool] = {}
    checks["identity"] = contract["contract_id"] == CONTRACT_ID
    checks["authority_hashes"] = all(
        verify_record(record) for record in contract["immutable_authority"].values()
    )
    checks["asset_hashes"] = all(
        verify_record(record) for record in contract["locked_assets"].values()
    )
    checks["representativeness_hashes"] = all(
        verify_record(record) for record in contract["representativeness_evidence"].values()
    )
    checks["attempt08_design_hashes"] = all(
        verify_record(record) for record in contract["inherited_attempt08_design"].values()
    )
    checks["native_binding_hashes"] = all(
        verify_record(record) for record in contract["native_binding_authority"].values()
    )
    failed_attempt = ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08/attempt_01"
    attempt = ROOT / contract["execution"]["attempt_root"]
    proof = ROOT / contract["execution"]["proof_root"]
    checks["attempt08_preserved"] = failed_attempt.is_dir()
    checks["new_namespaces_absent"] = not attempt.exists() and not proof.exists()
    checks["strategy_is_transient_production_map"] = (
        contract["strategy"]["selected"] == "production_map_transient_material_binding"
        and contract["strategy"]["transient_binding_used"]
        and contract["strategy"]["validation_map_rejected_as_representative"]
    )
    checks["landscape_contract"] = (
        contract["landscape_contract"]["exact_actor_count"] == 1
        and contract["landscape_contract"]["expected_component_count"] == 16
        and contract["landscape_contract"]["expected_compilation_finished_resource_count"] == 16
        and contract["landscape_contract"]["expected_valid_shader_map_resource_count"] == 16
        and contract["landscape_contract"]["non_null_bound_material_before_polling"]
    )
    performance = contract["performance_contract"]
    checks["bounded_measurement"] = (
        performance["warmup_seconds_after_ready"] == 30
        and performance["measured_seconds"] == 30
        and performance["minimum_tick_samples"] >= 900
        and performance["maximum_single_hitch_ms"] == 50.0
        and performance["frames_over_50_ms"] == 0
        and performance["shader_compiles_during_measured_interval"] == 0
    )
    outputs = contract["required_outputs"]
    checks["eight_governed_captures"] = (
        outputs["lit_png_count"] == 8
        and outputs["static_png_count"] == 5
        and outputs["temporal_png_count"] == 3
        and outputs["png_dimensions"] == [2560, 1440]
    )
    execution = contract["execution"]
    checks["single_attempt_policy"] = (
        execution["single_execution_only"]
        and not execution["automatic_retry"]
        and not execution["failed_namespace_reuse"]
        and execution["unreal_process_count"] == 1
    )
    checks["read_only_policy"] = all(
        execution[key]
        for key in (
            "world_save_forbidden",
            "asset_mutation_forbidden",
            "pcg_generation_forbidden",
            "network_forbidden",
            "promotion_forbidden",
            "integration_forbidden",
            "packaging_forbidden",
        )
    )
    checks["executor_python_syntax"] = True
    checks["executor_pre_namespace_fail_closed"] = (
        executor.index("verify_locked_sources(contract)") < executor.index("attempt_root.mkdir")
        and executor.index('rhi != "D3D12|SM6"') < executor.index("attempt_root.mkdir")
        and executor.index("len(landscape_matches) != 1") < executor.index("attempt_root.mkdir")
        and executor.index("unreal.load_asset") < executor.index("attempt_root.mkdir")
    )
    checks["executor_non_null_before_poll"] = (
        "begin_transient_landscape_diagnostic_material_deferred" in executor
        and "Transient material is not non-null and exact before deferred polling" in executor
        and executor.index("_STATE.bind_transient_material()")
        < executor.index("_STATE.callback = unreal.register_slate_post_tick_callback")
    )
    checks["executor_restoration_in_finally"] = (
        "finally:" in executor
        and "restoration = self.restore_original_material()" in executor
        and "property_identity_matches_original" in executor
        and '"restoration_in_finally": True' in executor
    )
    checks["executor_deferred_tick_wait"] = (
        "register_slate_post_tick_callback" in executor
        and "audit_landscape_material_compilation" in executor
        and "stable_ready_polls_required" in executor
        and "finish_all_compilation" not in executor
    )
    forbidden_tokens = (
        "save_current_level",
        "save_loaded_asset",
        "save_directory",
        "save_asset",
        "generate_local",
        "import_asset_tasks",
        "rename_asset",
        "delete_asset",
        "BuildCookRun",
    )
    checks["executor_has_no_prohibited_calls"] = all(
        token not in executor for token in forbidden_tokens
    )
    checks["supervisor_retains_handle_and_exit_code"] = (
        "Start-Process" in supervisor
        and "-PassThru" in supervisor
        and "$process.WaitForExit" in supervisor
        and "$process.ExitCode" in supervisor
        and "actual_exit_code" in supervisor
    )
    checks["supervisor_no_retry"] = (
        "automatic_retry = $false" in supervisor
        and "automatic retry is forbidden" in supervisor.lower()
        and supervisor.count("Start-Process") == 1
    )
    checks["focused_tests_present"] = TEST_PATH.is_file()
    gate = (
        "PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY01_UNREAL_AUTHORIZATION"
        if all(checks.values())
        else "FAILED_WITH_EVIDENCE"
    )
    return {
        "schema": "skyguard.phase4.m01-representative-visual-attempt08-recovery01-readiness.v1",
        "contract_id": CONTRACT_ID,
        "gate": gate,
        "checks": checks,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
