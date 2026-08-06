"""Offline verifier for the Recovery02 design gate."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY02_CONTRACT.json"
EXECUTOR_PATH = ROOT / "Scripts/capture_skyguard_phase4_m01_representative_visual_attempt08_recovery02.py"
SUPERVISOR_PATH = ROOT / "Scripts/invoke_skyguard_phase4_m01_representative_visual_attempt08_recovery02.ps1"
TEST_PATH = ROOT / "Scripts/tests/test_phase4_m01_representative_visual_attempt08_recovery02.py"
CONTRACT_ID = "P4.6-M01-REPRESENTATIVE-VISUAL-008-RECOVERY-02"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_path(record: dict) -> Path:
    return Path(record["absolute_file"]) if "absolute_file" in record else ROOT / record["file"]


def record_matches(record: dict) -> bool:
    path = record_path(record)
    return (
        path.is_file()
        and path.stat().st_size == record["bytes"]
        and sha256_file(path) == record["sha256"]
    )


def verify() -> dict:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
    executor = EXECUTOR_PATH.read_text(encoding="utf-8-sig")
    supervisor = SUPERVISOR_PATH.read_text(encoding="utf-8-sig")
    ast.parse(executor)
    checks: dict[str, bool] = {}
    checks["identity"] = contract["contract_id"] == CONTRACT_ID
    checks["terminal_recovery01_hashes"] = all(
        record_matches(record)
        for record in contract["terminal_recovery01_authority"].values()
    )
    checks["engine_authority"] = all(
        record_matches(record) for record in contract["engine_authority"].values()
    )
    editor = Path(contract["engine_authority"]["editor"]["absolute_file"])
    checks["engine_version"] = (
        editor.is_file()
        and contract["engine_authority"]["editor"]["version"]
        == "++UE5+Release-5.8-CL-56057345"
    )
    checks["asset_hashes"] = all(
        record_matches(record) for record in contract["locked_assets"].values()
    )
    checks["inherited_design_hashes"] = all(
        record_matches(record)
        for record in contract["inherited_design_authority"].values()
    )
    recovery01 = ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY01"
    attempt08 = ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08/attempt_01"
    execution = contract["execution"]
    attempt = ROOT / execution["attempt_root"]
    proof = ROOT / execution["proof_root"]
    launcher = ROOT / execution["launcher_root"]
    preflight = ROOT / execution["preflight_receipt"]
    checks["attempt08_preserved"] = attempt08.is_dir()
    checks["recovery01_not_reused"] = not (recovery01 / "attempt_01").exists()
    checks["recovery02_namespaces_absent"] = all(
        not path.exists() for path in (attempt, proof, launcher, preflight)
    )
    checks["transient_strategy"] = (
        contract["strategy"]["selected"] == "production_map_transient_material_binding"
        and contract["strategy"]["original_material_recorded_before_binding"]
        and contract["strategy"]["non_null_validation_material_before_polling"]
        and contract["strategy"]["restoration_location"] == "finally"
        and contract["strategy"]["independent_restoration_identity_verification"]
    )
    checks["landscape_and_capture_contract"] = (
        contract["landscape_contract"]["exact_actor_count"] == 1
        and contract["landscape_contract"]["expected_component_count"] == 16
        and contract["required_outputs"]["lit_png_count"] == 8
        and contract["required_outputs"]["static_png_count"] == 5
        and contract["required_outputs"]["temporal_png_count"] == 3
        and contract["required_outputs"]["png_dimensions"] == [2560, 1440]
    )
    performance = contract["performance_contract"]
    checks["warmup_measurement"] = (
        performance["warmup_seconds_after_ready"] == 30
        and performance["measured_seconds"] == 30
        and performance["minimum_tick_samples"] >= 900
    )
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
    checks["executor_syntax"] = True
    checks["executor_deferred_poll"] = (
        "register_slate_post_tick_callback" in executor
        and "audit_landscape_material_compilation" in executor
        and "stable_ready_polls_required" in executor
        and "finish_all_compilation" not in executor
    )
    checks["executor_restore_finally"] = (
        "finally:" in executor
        and "restoration = self.restore_original_material()" in executor
        and 'set_editor_property("landscape_material", self.original_material)' in executor
        and '"restoration_in_finally": True' in executor
    )
    checks["executor_pre_namespace_checks"] = (
        executor.index("verify_locked_sources(contract)") < executor.index("attempt_root.mkdir")
        and executor.index('rhi != "D3D12|SM6"') < executor.index("attempt_root.mkdir")
        and executor.index("len(matches) != 1") < executor.index("attempt_root.mkdir")
        and executor.index("unreal.load_asset") < executor.index("attempt_root.mkdir")
    )
    forbidden = (
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
    checks["executor_no_prohibited_calls"] = all(token not in executor for token in forbidden)
    checks["supervisor_engine_binding"] = (
        "$editor = 'D:\\UE_5.8\\Engine\\Binaries\\Win64\\UnrealEditor-Cmd.exe'" in supervisor
        and "expectedEditorBytes = 512952" in supervisor
        and "expectedEditorVersion = '++UE5+Release-5.8-CL-56057345'" in supervisor
        and "0fb325cf215cc800ce260a1890af3f3dc314b8cc6331061d4e7e7246489af2e0"
        in supervisor
    )
    checks["supervisor_preflight_receipt"] = (
        "Write-PreflightReceipt" in supervisor
        and "PASS_READY_TO_START_SINGLE_UNREAL_PROCESS" in supervisor
        and "FAILED_WITH_EVIDENCE" in supervisor
        and supervisor.index("Write-PreflightReceipt 'PASS_READY_TO_START_SINGLE_UNREAL_PROCESS'")
        < supervisor.index("Start-Process")
    )
    checks["supervisor_real_exit_code"] = (
        "Start-Process" in supervisor
        and "-PassThru" in supervisor
        and "$process.WaitForExit" in supervisor
        and "$process.ExitCode" in supervisor
        and "actual_exit_code" in supervisor
    )
    checks["supervisor_no_retry"] = (
        supervisor.count("Start-Process") == 1
        and "automatic_retry = $false" in supervisor
        and "retry is forbidden" in supervisor.lower()
    )
    checks["focused_tests_present"] = TEST_PATH.is_file()
    gate = (
        "PASSED_READY_FOR_EXPLICIT_SINGLE_RECOVERY02_UNREAL_AUTHORIZATION"
        if all(checks.values())
        else "FAILED_WITH_EVIDENCE"
    )
    return {
        "schema": "skyguard.phase4.m01-representative-visual-attempt08-recovery02-readiness.v1",
        "contract_id": CONTRACT_ID,
        "gate": gate,
        "checks": checks,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
