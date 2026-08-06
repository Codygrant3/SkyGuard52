from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT05_RECOVERY02_CONTRACT.json"
)
SUPERVISOR = (
    ROOT
    / "Scripts"
    / "run_skyguard_phase4_m01_landscape_visible_attempt05_recovery02.ps1"
)
READINESS = (
    ROOT
    / "Scripts"
    / "verify_skyguard_phase4_m01_landscape_attempt05_recovery02_readiness.py"
)
HEADER = (
    ROOT / "Source/Skyguard52/SkyguardPhase4LandscapePerformanceCapture.h"
)
SOURCE = (
    ROOT / "Source/Skyguard52/SkyguardPhase4LandscapePerformanceCapture.cpp"
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))


def test_recovery02_locks_predecessor_packages_and_cpp_fix():
    spec = contract()
    for section in (
        "immutable_predecessor_evidence",
        "immutable_packages",
        "cpp_fix",
    ):
        for item in spec[section].values():
            if not isinstance(item, dict):
                continue
            path = ROOT / item["file"]
            assert path.is_file()
            assert sha256_file(path) == item["sha256"]
    assert spec["recovery_execution"]["authoring_forbidden"] is True
    assert spec["recovery_execution"]["capture_forbidden"] is True
    assert spec["recovery_execution"]["automatic_retry_allowed"] is False


def test_recovery02_reuses_exact_accepted_render_and_capture_evidence():
    spec = contract()
    render = json.loads(
        (
            ROOT
            / spec["immutable_predecessor_evidence"][
                "render_state_acceptance"
            ]["file"]
        ).read_text(encoding="utf-8-sig")
    )
    failure = json.loads(
        (
            ROOT / spec["accepted_capture_evidence"]["hash_manifest"]
        ).read_text(encoding="utf-8-sig")
    )
    assert render["gate"] == "PASS"
    assert render["rhi_validation"] == "D3D12|SM6"
    assert render["landscape_visible_audit"][
        "render_state_created_component_count"
    ] == 16
    captures = failure["captures"]["files"]
    assert len(captures) == 17
    for item in captures:
        path = Path(item["path"])
        assert path.is_file()
        assert sha256_file(path) == item["sha256"]


def test_csv_start_waits_for_later_frame_before_measurement_clock():
    header = text(HEADER)
    source = text(SOURCE)
    assert "bMeasurementStartRequested" in header
    assert "CsvStartActivationTimeoutSeconds = 5.0" in source
    tick = source.split(
        "void USkyguardPhase4LandscapePerformanceCapture::Tick", 1
    )[1].split(
        "bool USkyguardPhase4LandscapePerformanceCapture::IsWorldReady", 1
    )[0]
    assert "RequestMeasurementStart();" in tick
    assert "FCsvProfiler::Get()->IsCapturing()" in tick
    assert "ConfirmMeasurementStart();" in tick
    assert "CsvStartActivationTimeoutSeconds" in tick
    request = source.split(
        "void USkyguardPhase4LandscapePerformanceCapture::"
        "RequestMeasurementStart()",
        1,
    )[1].split(
        "void USkyguardPhase4LandscapePerformanceCapture::"
        "ConfirmMeasurementStart()",
        1,
    )[0]
    assert 'GEngine->Exec(World, TEXT("csvprofile start"))' in request
    assert "IsCapturing()" not in request


def test_recovery02_supervisor_is_profile_only_and_idempotent():
    source = text(SUPERVISOR)
    assert "-ExecutePythonScript" not in source
    assert "-NullRHI" not in source
    assert "author_immutable_candidate" not in source
    assert "CaptureScript" not in source
    assert "RenderVerifier" not in source
    assert "Invoke-ProfileStage" in source
    assert "accepted_capture_evidence.hash_manifest" in source
    assert (
        "Recovery02 root already exists; refuse duplicate or overwrite"
        in source
    )


def test_recovery02_profile_contract_remains_true_same_process():
    source = text(SUPERVISOR)
    assert "-SkyguardP45ProfileWarmupSeconds=30" in source
    assert "-SkyguardP45ProfileMeasuredSeconds=60" in source
    assert "-csvCaptureFrames" not in source
    assert "-d3d12" in source
    assert "-sm6" in source
    persist = source.index("$manifest.stages += $stage")
    save = source.index(
        "Save-Json -Value $manifest -Path $ManifestPath", persist
    )
    assertion = source.index("Assert-StagePassed -Stage $stage", save)
    assert persist < save < assertion


def test_recovery02_readiness_has_static_and_compiled_states():
    source = text(READINESS)
    assert "PASS_RECOVERY02_STATIC_READY_PENDING_CPP_RECOMPILE" in source
    assert "PASS_RECOVERY02_COMPILED_READY_PENDING_AUTHORIZATION" in source
    assert '"captures_will_rerun": False' in source
    assert '"unreal_launched": False' in source
