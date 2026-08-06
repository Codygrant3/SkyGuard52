from __future__ import annotations

from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SUPERVISOR = (
    ROOT
    / "Scripts/run_skyguard_phase4_m01_landscape_visible_gpu_gate_attempt05.ps1"
)
READINESS = (
    ROOT
    / "Scripts/verify_skyguard_phase4_m01_landscape_repair_readiness.py"
)
GATE = (
    ROOT
    / "Scripts/verify_skyguard_phase4_m01_landscape_visible_gpu_gate.py"
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_supervisor_is_sequential_and_refuses_a_busy_heavy_lane():
    source = text(SUPERVISOR)
    assert "Start-Job" not in source
    assert "ForEach-Object -Parallel" not in source
    assert "Get-ExactHeavyProcesses" in source
    assert "Exclusive heavy lane is not free" in source
    assert "Wait-ForZeroHeavyProcesses" in source
    assert '"blender"' in source
    assert "Get-FileHash" not in source
    assert "[System.Security.Cryptography.SHA256]::Create()" in source


def test_supervisor_uses_true_same_process_profile_boundary():
    source = text(SUPERVISOR)
    assert "-csvCaptureFrames" not in source
    assert "SkyguardP45ProfileWarmupSeconds=30" in source
    assert "SkyguardP45ProfileMeasuredSeconds=60" in source
    assert "same_process_warmup_and_measurement = $true" in source
    assert "boot_csv_capture_forbidden = $true" in source
    assert '"-d3d12", "-sm6"' in source


def test_supervisor_preserves_immutable_evidence_and_attempt_namespace():
    source = text(SUPERVISOR)
    assert (
        "cb2c13f3ce18a3462620306bcef4610d87c2f0cf28a7815b444bd68ab773a021"
        in source
    )
    assert (
        "e54682b64f43dbaf0e2c61f08436d495493c6db1f28998cce9583d0542c4042e"
        in source
    )
    assert "Attempt05 immutable outputs already exist; never overwrite an attempt" in source
    assert "LandscapeMaterialValidation_v5_attempt05" in source
    assert "LandscapeValidation_v5_attempt05" in source


def test_supervisor_accepts_technical_pass_pending_human_review_only():
    source = text(SUPERVISOR)
    assert "-AcceptedExitCodes @(0, 2)" in source
    assert 'if ($gateReport.technical_gate -ne "PASS")' in source
    assert 'elseif ($gateReport.gate -eq "INCOMPLETE_HUMAN_REVIEW")' in source
    assert "TECHNICAL_GATE_PASS_PENDING_HUMAN_REVIEW" in source
    assert 'throw "Unexpected attempt05 gate state:' in source


def test_attempt05_capture_and_gate_counts_are_explicit():
    source = text(GATE)
    assert "17 if is_repaired_attempt else 13" in source
    readiness = text(READINESS)
    assert (
        "PASS_IMPLEMENTATION_COMPILED_READY_PENDING_UNREAL_EXECUTION"
        in readiness
    )
    assert "EditorSetLandscapeMaterial" in readiness
    assert "Result: Succeeded" in readiness
    assert "UnrealEditor-Skyguard52.dll" in readiness
