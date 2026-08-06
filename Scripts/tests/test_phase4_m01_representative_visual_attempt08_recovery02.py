"""Focused offline tests for Recovery02."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY02_CONTRACT.json"
EXECUTOR_PATH = ROOT / "Scripts/capture_skyguard_phase4_m01_representative_visual_attempt08_recovery02.py"
SUPERVISOR_PATH = ROOT / "Scripts/invoke_skyguard_phase4_m01_representative_visual_attempt08_recovery02.ps1"
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
EXECUTOR = EXECUTOR_PATH.read_text(encoding="utf-8-sig")
SUPERVISOR = SUPERVISOR_PATH.read_text(encoding="utf-8-sig")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_python_syntax() -> None:
    ast.parse(EXECUTOR)


def test_attempt08_and_recovery01_preserved() -> None:
    assert (ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08/attempt_01").is_dir()
    terminal = CONTRACT["terminal_recovery01_authority"]["terminal_freeze"]
    assert sha256(ROOT / terminal["file"]) == terminal["sha256"]
    assert terminal["sha256"] == "0cf5d9fbc550ef7df2c11f51008b0a0a7ba57a04399169170e4667a23a88255f"


def test_installed_editor_authority() -> None:
    record = CONTRACT["engine_authority"]["editor"]
    path = Path(record["absolute_file"])
    assert str(path) == r"D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
    assert path.stat().st_size == 512952 == record["bytes"]
    assert record["version"] == "++UE5+Release-5.8-CL-56057345"
    assert sha256(path) == record["sha256"]


def test_launcher_manifest_authority() -> None:
    record = CONTRACT["engine_authority"]["epic_launcher_manifest"]
    path = Path(record["absolute_file"])
    assert path.stat().st_size == record["bytes"] == 2350
    assert sha256(path) == record["sha256"]


def test_recovery02_namespaces_absent() -> None:
    execution = CONTRACT["execution"]
    assert not (ROOT / execution["attempt_root"]).exists()
    assert not (ROOT / execution["proof_root"]).exists()
    assert not (ROOT / execution["launcher_root"]).exists()
    assert not (ROOT / execution["preflight_receipt"]).exists()


def test_production_map_and_material_hashes() -> None:
    for record in CONTRACT["locked_assets"].values():
        path = ROOT / record["file"]
        assert path.stat().st_size == record["bytes"]
        assert sha256(path) == record["sha256"]


def test_non_null_material_precedes_polling() -> None:
    assert "begin_transient_landscape_diagnostic_material_deferred" in EXECUTOR
    assert "current is None" in EXECUTOR
    assert EXECUTOR.index("_STATE.bind_transient_material()") < EXECUTOR.index(
        "_STATE.callback = unreal.register_slate_post_tick_callback"
    )


def test_restoration_in_finally_and_verified() -> None:
    assert "finally:" in EXECUTOR
    assert "restoration = self.restore_original_material()" in EXECUTOR
    assert 'set_editor_property("landscape_material", self.original_material)' in EXECUTOR
    assert "property_identity_matches_original" in EXECUTOR
    assert '"restoration_in_finally": True' in EXECUTOR


def test_deferred_tick_shader_wait() -> None:
    assert "register_slate_post_tick_callback" in EXECUTOR
    assert "audit_landscape_material_compilation" in EXECUTOR
    assert "stable_ready_polls_required" in EXECUTOR
    assert "finish_all_compilation" not in EXECUTOR


def test_warmup_measurement_and_samples() -> None:
    perf = CONTRACT["performance_contract"]
    assert perf["warmup_seconds_after_ready"] == 30
    assert perf["measured_seconds"] == 30
    assert perf["minimum_tick_samples"] >= 900
    assert "time.monotonic() - self.ready_at" in EXECUTOR
    assert "len(self.frame_samples) < performance" in EXECUTOR


def test_exact_eight_captures() -> None:
    outputs = CONTRACT["required_outputs"]
    assert outputs["lit_png_count"] == 8
    assert outputs["static_png_count"] == 5
    assert outputs["temporal_png_count"] == 3
    assert outputs["png_dimensions"] == [2560, 1440]


def test_real_exit_code_persistence() -> None:
    assert "Start-Process" in SUPERVISOR
    assert "-PassThru" in SUPERVISOR
    assert "$process.WaitForExit" in SUPERVISOR
    assert "$process.ExitCode" in SUPERVISOR
    assert "actual_exit_code" in SUPERVISOR


def test_preflight_receipt_precedes_start_process() -> None:
    assert "Write-PreflightReceipt" in SUPERVISOR
    assert "FAILED_WITH_EVIDENCE" in SUPERVISOR
    assert SUPERVISOR.index(
        "Write-PreflightReceipt 'PASS_READY_TO_START_SINGLE_UNREAL_PROCESS'"
    ) < SUPERVISOR.index("Start-Process")


def test_one_execution_no_retry() -> None:
    assert CONTRACT["execution"]["single_execution_only"]
    assert not CONTRACT["execution"]["automatic_retry"]
    assert not CONTRACT["execution"]["failed_namespace_reuse"]
    assert SUPERVISOR.count("Start-Process") == 1
    assert "automatic_retry = $false" in SUPERVISOR


def test_no_prohibited_executor_calls() -> None:
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
    assert all(token not in EXECUTOR for token in forbidden)
    execution = CONTRACT["execution"]
    assert execution["world_save_forbidden"]
    assert execution["asset_mutation_forbidden"]
    assert execution["pcg_generation_forbidden"]
    assert execution["network_forbidden"]
    assert execution["promotion_forbidden"]
    assert execution["integration_forbidden"]
    assert execution["packaging_forbidden"]


def test_executor_preflight_before_namespace_creation() -> None:
    mkdir = EXECUTOR.index("attempt_root.mkdir")
    assert EXECUTOR.index("verify_locked_sources(contract)") < mkdir
    assert EXECUTOR.index('rhi != "D3D12|SM6"') < mkdir
    assert EXECUTOR.index("len(matches) != 1") < mkdir
    assert EXECUTOR.index("unreal.load_asset") < mkdir
