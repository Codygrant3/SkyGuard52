"""Focused offline tests for the Recovery01 representative proof design."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08_RECOVERY01_CONTRACT.json"
EXECUTOR_PATH = ROOT / "Scripts/capture_skyguard_phase4_m01_representative_visual_attempt08_recovery01.py"
SUPERVISOR_PATH = ROOT / "Scripts/invoke_skyguard_phase4_m01_representative_visual_attempt08_recovery01.ps1"
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
EXECUTOR = EXECUTOR_PATH.read_text(encoding="utf-8-sig")
SUPERVISOR = SUPERVISOR_PATH.read_text(encoding="utf-8-sig")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_python_syntax() -> None:
    ast.parse(EXECUTOR)


def test_original_attempt08_authority_is_unchanged() -> None:
    record = CONTRACT["immutable_authority"]["attempt08_freeze"]
    assert sha256(ROOT / record["file"]) == record["sha256"]
    assert record["sha256"] == "3d299d6a2bd4078162edddce9bdc94613db03b98d85d8a52db685cd397331180"


def test_terminal_attempt08_namespace_is_preserved() -> None:
    assert (ROOT / "Saved/BuildAttempts/PHASE4_M01_REPRESENTATIVE_VISUAL_ATTEMPT08/attempt_01").is_dir()


def test_recovery01_namespaces_are_absent() -> None:
    assert not (ROOT / CONTRACT["execution"]["attempt_root"]).exists()
    assert not (ROOT / CONTRACT["execution"]["proof_root"]).exists()


def test_selected_map_and_material_hashes() -> None:
    assets = CONTRACT["locked_assets"]
    for key in ("production_map", "validation_map", "validation_material"):
        path = ROOT / assets[key]["file"]
        assert path.stat().st_size == assets[key]["bytes"]
        assert sha256(path) == assets[key]["sha256"]


def test_non_null_transient_binding_precedes_polling() -> None:
    assert CONTRACT["strategy"]["selected"] == "production_map_transient_material_binding"
    assert "begin_transient_landscape_diagnostic_material_deferred" in EXECUTOR
    assert EXECUTOR.index("_STATE.bind_transient_material()") < EXECUTOR.index(
        "_STATE.callback = unreal.register_slate_post_tick_callback"
    )
    assert "current is None" in EXECUTOR


def test_restoration_is_in_finally_and_independently_verified() -> None:
    assert "finally:" in EXECUTOR
    assert "restoration = self.restore_original_material()" in EXECUTOR
    assert 'set_editor_property("landscape_material", self.original_material)' in EXECUTOR
    assert "property_identity_matches_original" in EXECUTOR
    assert '"restoration_in_finally": True' in EXECUTOR


def test_deferred_tick_driven_shader_wait() -> None:
    assert "register_slate_post_tick_callback" in EXECUTOR
    assert "audit_landscape_material_compilation" in EXECUTOR
    assert "stable_ready_polls_required" in EXECUTOR
    assert "finish_all_compilation" not in EXECUTOR


def test_warmup_measurement_and_sample_count() -> None:
    performance = CONTRACT["performance_contract"]
    assert performance["warmup_seconds_after_ready"] == 30
    assert performance["measured_seconds"] == 30
    assert performance["minimum_tick_samples"] >= 900
    assert "time.monotonic() - self.ready_at < warmup" in EXECUTOR
    assert "len(self.frame_samples) < required" in EXECUTOR


def test_exactly_eight_governed_captures() -> None:
    outputs = CONTRACT["required_outputs"]
    assert outputs["lit_png_count"] == 8
    assert outputs["static_png_count"] == 5
    assert outputs["temporal_png_count"] == 3
    assert outputs["png_dimensions"] == [2560, 1440]


def test_supervisor_persists_real_exit_code() -> None:
    assert "Start-Process" in SUPERVISOR
    assert "-PassThru" in SUPERVISOR
    assert "$process.WaitForExit" in SUPERVISOR
    assert "$process.ExitCode" in SUPERVISOR
    assert "actual_exit_code" in SUPERVISOR


def test_automatic_retry_is_forbidden() -> None:
    assert CONTRACT["execution"]["single_execution_only"]
    assert not CONTRACT["execution"]["automatic_retry"]
    assert not CONTRACT["execution"]["failed_namespace_reuse"]
    assert SUPERVISOR.count("Start-Process") == 1
    assert "automatic_retry = $false" in SUPERVISOR


def test_no_save_import_pcg_promotion_integration_or_packaging_calls() -> None:
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


def test_preflight_fails_before_proof_directory_creation() -> None:
    mkdir = EXECUTOR.index("attempt_root.mkdir")
    assert EXECUTOR.index("verify_locked_sources(contract)") < mkdir
    assert EXECUTOR.index('rhi != "D3D12|SM6"') < mkdir
    assert EXECUTOR.index("len(landscape_matches) != 1") < mkdir
    assert EXECUTOR.index("unreal.load_asset") < mkdir
