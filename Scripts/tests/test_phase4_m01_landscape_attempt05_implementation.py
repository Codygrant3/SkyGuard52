from __future__ import annotations

import importlib.util
import struct
import sys
import tempfile
import zlib
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_repair_contract import load_attempt05_contract


AUTHOR_H = (
    ROOT
    / "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.h"
)
AUTHOR_CPP = (
    ROOT
    / "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.cpp"
)
PROFILE_H = (
    ROOT
    / "Source/Skyguard52/SkyguardPhase4LandscapePerformanceCapture.h"
)
PROFILE_CPP = (
    ROOT
    / "Source/Skyguard52/SkyguardPhase4LandscapePerformanceCapture.cpp"
)
BUILDER = (
    ROOT
    / "Scripts/build_skyguard_phase4_m01_landscape_material_validation.py"
)
ATTEMPT05_BUILDER = (
    ROOT
    / "Scripts/build_skyguard_phase4_m01_landscape_material_validation_attempt05.py"
)
CAPTURE = (
    ROOT / "Scripts/capture_skyguard_phase4_m01_landscape_visible_review.py"
)
ATTEMPT05_CAPTURE = (
    ROOT
    / "Scripts/capture_skyguard_phase4_m01_landscape_visible_review_attempt05.py"
)
GATE = (
    ROOT / "Scripts/verify_skyguard_phase4_m01_landscape_visible_gpu_gate.py"
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_gate_module():
    spec = importlib.util.spec_from_file_location("attempt05_gate_test", GATE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def test_attempt05_paths_are_loaded_without_changing_attempt04_contract():
    contract = load_attempt05_contract()
    assert contract["contract_id"] == "P4.5-M01-LANDSCAPE-VISIBLE-005"
    assert "attempt05" in contract["candidate"]["immutable_map"].lower()
    assert "attempt05" in contract["candidate"]["landscape_material"].lower()
    assert "load_attempt05_contract" in text(ATTEMPT05_BUILDER)
    assert "load_attempt05_contract" in text(ATTEMPT05_CAPTURE)


def test_native_refresh_and_live_audit_are_fail_closed():
    header = text(AUTHOR_H)
    source = text(AUTHOR_CPP)
    for marker in (
        "PrepareGovernedLandscapeForVisibleValidation",
        "AuditLandscapeVisibleReadiness",
        "VisibleComponentCount",
        "RegisteredComponentCount",
        "RenderStateCreatedComponentCount",
        "GeneratedMaterialInstanceReadyComponentCount",
        "GovernedMaterialParentMatchComponentCount",
        "ContractCameraFrustumIntersectionCount",
    ):
        assert marker in header
    for marker in (
        "SetActorHiddenInGame(false)",
        "SetIsTemporarilyHiddenInEditor(false)",
        "SetVisibility(true, true)",
        "SetHiddenInGame(false, true)",
        "RegisterComponent()",
        "UpdateAllComponentMaterialInstances(true)",
        "RecreateRenderState_Concurrent()",
        "UpdateCachedBounds(false)",
        "Result.ContractCameraFrustumIntersectionCount == 5",
    ):
        assert marker in source
    assert "MATUSAGE_Landscape" not in source
    assert "prepare_governed_landscape_for_visible_validation" in text(BUILDER)


def test_scene_capture_diagnostics_do_not_depend_on_viewport_commands():
    header = text(AUTHOR_H)
    source = text(AUTHOR_CPP)
    capture = text(CAPTURE)
    assert "ConfigureLandscapeSceneCaptureDiagnostic" in header
    assert "FEngineShowFlags Flags(ESFIM_Game)" in source
    assert "ApplyViewMode(VMI_ShaderComplexity, true, Flags)" in source
    assert "PRM_UseShowOnlyList" in source
    assert "ShowOnlyActorComponents(Landscape, false)" not in source
    assert "Capture->ShowOnlyComponent(Component)" in source
    assert "Components.Num() != 16" in source
    attempt05_function = capture.split(
        "def capture_repaired_candidate_diagnostics", 1
    )[1].split("\ndef main", 1)[0]
    assert "viewmode " not in attempt05_function
    assert "Landscape.DebugViewMode" not in attempt05_function
    assert "finally:" in attempt05_function
    assert "apply_transient_material" in attempt05_function
    assert attempt05_function.count(
        "candidate_diagnostic_landscape_coverage_"
    ) == 1


def test_profiler_has_true_same_process_capture_boundary():
    header = text(PROFILE_H)
    source = text(PROFILE_CPP)
    assert "UTickableWorldSubsystem" in header
    assert "SkyguardP45ProfileContractId=" in source
    assert "World->HasBegunPlay()" in source
    assert "FIntPoint(1920, 1080)" in source
    assert "D3D12" in source and "SM6" in source
    assert "[P4_PROFILE_WARMUP_COMPLETE]" in source
    assert "[P4_PROFILE_MEASURED_START]" in source
    assert "[P4_PROFILE_MEASURED_STOP]" in source
    assert 'TEXT("csvprofile start")' in source
    assert 'TEXT("csvprofile stop")' in source
    assert "startup_frames_excluded" in source
    assert "csvCaptureFrames" not in source


def test_profiler_waits_across_frames_for_csv_start_activation():
    header = text(PROFILE_H)
    source = text(PROFILE_CPP)
    assert "bMeasurementStartRequested" in header
    assert "MeasurementStartRequestPlatformSeconds" in header
    assert "RequestMeasurementStart" in header
    assert "ConfirmMeasurementStart" in header
    assert "FailMeasurementStart" in header
    assert "CsvStartActivationTimeoutSeconds = 5.0" in source
    request = source.index(
        "void USkyguardPhase4LandscapePerformanceCapture::"
        "RequestMeasurementStart()"
    )
    confirm = source.index(
        "void USkyguardPhase4LandscapePerformanceCapture::"
        "ConfirmMeasurementStart()"
    )
    assert request < confirm
    request_body = source[request:confirm]
    assert 'GEngine->Exec(World, TEXT("csvprofile start"))' in request_body
    assert "bMeasurementStartRequested = true" in request_body
    assert "IsCapturing()" not in request_body
    tick = source.split(
        "void USkyguardPhase4LandscapePerformanceCapture::Tick", 1
    )[1].split(
        "bool USkyguardPhase4LandscapePerformanceCapture::IsWorldReady", 1
    )[0]
    assert "bMeasurementStartRequested" in tick
    assert "FCsvProfiler::Get()->IsCapturing()" in tick
    assert "ConfirmMeasurementStart();" in tick
    assert "CsvStartActivationTimeoutSeconds" in tick
    assert "MeasurementStartPlatformSeconds" in source[confirm:]


def test_attempt05_visual_analyzer_decodes_png_and_connectivity():
    gate = load_gate_module()
    width, height = 3, 2
    rows = (
        b"\x00"
        + bytes((255, 0, 0, 255, 0, 255, 0, 255, 0))
        + b"\x00"
        + bytes((0, 0, 255, 255, 255, 255, 0, 0, 0))
    )
    payload = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(
            b"IHDR",
            struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0),
        )
        + png_chunk(b"IDAT", zlib.compress(rows))
        + png_chunk(b"IEND", b"")
    )
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "fixture.png"
        path.write_bytes(payload)
        decoded_width, decoded_height, rgb = gate.decode_png_rgb8(path)
    assert (decoded_width, decoded_height) == (width, height)
    assert rgb[:3] == bytes((255, 0, 0))
    mask = bytearray((1, 1, 0, 0, 1, 0))
    assert gate.largest_connected_run_fraction(mask, 3, 2) == 1.0
