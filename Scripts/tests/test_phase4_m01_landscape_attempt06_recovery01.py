from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT06_RECOVERY01_CONTRACT.json"
)
RENDER_VERIFIER = (
    ROOT
    / "Scripts/"
    "verify_skyguard_phase4_m01_landscape_attempt06_"
    "recovery01_render_state.py"
)
SUPERVISOR = (
    ROOT
    / "Scripts/"
    "supervise_skyguard_phase4_m01_landscape_visible_"
    "attempt06_recovery01.py"
)
READINESS = (
    ROOT
    / "Scripts/"
    "verify_skyguard_phase4_m01_landscape_attempt06_"
    "recovery01_readiness.py"
)
LAUNCHER = (
    ROOT
    / "Scripts/"
    "run_skyguard_phase4_m01_landscape_visible_attempt06_recovery01.ps1"
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def test_recovery01_contract_binds_failed_attempt_and_immutable_packages():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    assert contract["recovery_id"] == (
        "P4.5-M01-LANDSCAPE-VISIBLE-006-RECOVERY-01"
    )
    assert contract["failure_boundary"]["classification"] == (
        "NULLRHI_CANNOT_PROVE_LANDSCAPE_RENDER_STATE"
    )
    for item in (
        contract["failure_boundary"]["failed_manifest"],
        contract["failure_boundary"]["failed_editor_acceptance"],
        *contract["immutable_packages"].values(),
        contract["compiled_module"],
    ):
        path = ROOT / item["file"]
        assert path.is_file()
        assert sha256_file(path) == item["sha256"]


def test_recovery01_contract_is_resume_only_and_fail_closed():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    execution = contract["recovery_execution"]
    assert execution["authoring_forbidden"] is True
    assert execution["build_forbidden"] is True
    assert execution["null_rhi_forbidden"] is True
    assert execution["fresh_render_verification_required"] == "D3D12|SM6"
    assert execution["render_state_created_component_count_required"] == 16
    assert execution["capture_allowed_only_after_render_verification_pass"]
    assert execution["profile_allowed_only_after_capture_manifest_pass"]
    for field in (
        "automatic_retry_allowed",
        "world_or_package_save_allowed",
        "pcg_generation_allowed",
        "network_download_allowed",
        "promotion_allowed",
    ):
        assert execution[field] is False


def test_recovery01_render_verifier_is_read_only_and_d3d12_bound():
    source = text(RENDER_VERIFIER)
    ast.parse(source)
    assert 'if rhi != "D3D12|SM6"' in source
    assert "render_state_created_component_count" in source
    assert "render_count == 16" in source
    assert "package_hashes_unchanged" in source
    assert '"world_saved": False' in source
    assert '"pcg_generation_invoked": False' in source
    assert "save_current_level" not in source
    assert "save_asset" not in source


def test_recovery01_supervisor_has_strict_stage_order_and_no_reauthoring():
    source = text(SUPERVISOR)
    ast.parse(source)
    render = source.index('"verify_candidate_render_state_d3d12_sm6"')
    capture = source.index('f"{mode}_capture"')
    profile = source.index('f"{mode}_profile_measured"')
    assert render < capture < profile
    assert "render_state_created_component_count" in source
    assert "capture_manifest_pass" in source
    assert "build_skyguard52_editor_attempt06" not in source
    assert "author_immutable_candidate_attempt06" not in source
    assert "Build.bat" not in source
    assert "-run=pythonscript" not in source
    assert "-NullRHI" not in source
    assert "-csvCaptureFrames" not in source
    assert "-benchmark" not in source
    assert '"promotion_allowed": False' in source


def test_recovery01_profile_is_same_process_and_baseline_then_candidate():
    source = text(SUPERVISOR)
    assert "-SkyguardP45ProfileWarmupSeconds=30" in source
    assert "-SkyguardP45ProfileMeasuredSeconds=60" in source
    assert source.count('("baseline", baseline["asset"])') == 2
    assert source.count('("candidate", candidate["asset"])') == 2
    assert "same_process_warmup_and_measurement" in source
    assert "startup_frames_excluded" in source


def test_recovery01_refuses_duplicate_and_requires_explicit_authorization():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    recovery_root = ROOT / contract["recovery_execution"]["recovery_root"]
    assert not recovery_root.exists()
    supervisor = text(SUPERVISOR)
    launcher = text(LAUNCHER)
    assert "Recovery01 root already exists" in supervisor
    assert "--authorize-single-recovery-run" in supervisor
    assert "if (-not $AuthorizeSingleRecoveryRun)" in launcher
    assert "--authorize-single-recovery-run" in launcher


def test_recovery01_readiness_checker_is_parseable_and_reports_no_launch():
    source = text(READINESS)
    ast.parse(source)
    assert '"unreal_launched": False' in source
    assert '"attempt06_reauthored": False' in source
    assert '"failed_attempt_mutated": False' in source
    assert '"promotion_allowed": False' in source
    assert "PASS_RECOVERY01_READY_PENDING_AUTHORIZATION" in source
