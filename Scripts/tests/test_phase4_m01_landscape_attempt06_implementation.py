from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
HEADER = (
    ROOT / "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.h"
)
SOURCE = (
    ROOT / "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.cpp"
)
PROFILE_SOURCE = (
    ROOT
    / "Source/Skyguard52/"
    "SkyguardPhase4LandscapePerformanceCaptureAttempt06.cpp"
)
CAPTURE = (
    ROOT / "Scripts/capture_skyguard_phase4_m01_landscape_visible_review.py"
)
GATE = (
    ROOT
    / "Scripts/verify_skyguard_phase4_m01_landscape_visible_gpu_gate.py"
)
SUPERVISOR = (
    ROOT
    / "Scripts/supervise_skyguard_phase4_m01_landscape_visible_attempt06.py"
)
LAUNCHER = (
    ROOT
    / "Scripts/run_skyguard_phase4_m01_landscape_visible_attempt06.ps1"
)
CONTRACT = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_REPAIR_CONTRACT_ATTEMPT06.json"
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_native_capture_explicitly_selects_exact_16_components():
    header = text(HEADER)
    source = text(SOURCE)
    for marker in (
        "ShowOnlyLandscapeComponentCount",
        "GeneratedMaterialInstanceReadyComponentCount",
        "DiagnosticMaterialParentMatchComponentCount",
        "bRenderThreadSynchronized",
    ):
        assert marker in header
    assert "ShowOnlyActorComponents" not in source
    assert "Components.Num() != 16" in source
    assert "Capture->ShowOnlyComponent(Component)" in source
    assert "Result.ShowOnlyLandscapeComponentCount != 16" in source
    assert "Result.GeneratedMaterialInstanceReadyComponentCount != 16" in source
    assert "Result.DiagnosticMaterialParentMatchComponentCount != 16" in source


def test_native_material_switch_audits_parents_and_flushes_render_thread():
    source = text(SOURCE)
    assert "SetTransientLandscapeDiagnosticMaterialSynchronized" in source
    synchronized = source.split(
        "SetTransientLandscapeDiagnosticMaterialSynchronized(", 1
    )[1]
    assert "UpdateAllComponentMaterialInstances(true)" in synchronized
    assert "RecreateRenderState_Concurrent()" in synchronized
    assert "FlushRenderingCommands();" in synchronized
    assert "AuditLandscapeVisibleReadiness(Landscape, Material)" in synchronized
    assert source.count("FlushRenderingCommands();") >= 2
    assert "Flags.SetTonemapper(false)" in source
    assert "Flags.SetPostProcessing(false)" in source
    assert "Flags.SetAtmosphere(false)" in source
    assert "Flags.SetCloud(false)" in source
    assert "Flags.SetFog(false)" in source


def test_attempt06_capture_forbids_actor_fallback_and_records_proof():
    source = text(CAPTURE)
    assert '!= "P4.5-M01-LANDSCAPE-VISIBLE-006"' in source
    assert "record_capture_evidence" in source
    for field in (
        "exact_location_cm",
        "exact_rotation_degrees",
        "camera_transform_authority",
        "forward_ray_intersects_bounds",
        "projected_top_surface_fraction",
        "show_only_component_count",
        "generated_material_instance_count",
        "material_parent_match_count",
        "render_thread_synchronization_complete",
    ):
        assert field in source
    assert "set_transient_landscape_diagnostic_material_synchronized" in source
    assert "Attempt06 explicit 16-component diagnostic audit failed" in source


def test_attempt06_gate_uses_expected_palette_not_generic_buckets():
    source = text(GATE)
    function = source.split("def analyze_attempt06_visuals", 1)[1].split(
        "\ndef percentile", 1
    )[0]
    assert "srgb8_to_linear" in function
    assert "component_expected_id_pixel_counts" in function
    assert "minimum_pixels_per_expected_id" in function
    assert 'result.pop("component_color_bucket_count", None)' in function
    assert 'result["generic_color_bucket_count_used"] = False' in function
    assert "red // 16" not in function
    assert "green // 16" not in function
    assert "blue // 16" not in function


def test_attempt06_entrypoints_are_immutable_and_parse():
    paths = (
        ROOT
        / "Scripts/build_skyguard_phase4_m01_landscape_material_validation_attempt06.py",
        ROOT
        / "Scripts/verify_skyguard_phase4_m01_landscape_material_assets_attempt06.py",
        ROOT
        / "Scripts/capture_skyguard_phase4_m01_landscape_visible_review_attempt06.py",
        ROOT
        / "Scripts/verify_skyguard_phase4_m01_landscape_visible_gpu_gate_attempt06.py",
        SUPERVISOR,
    )
    for path in paths:
        ast.parse(text(path))
    author = text(paths[0])
    assert "v6_attempt06" in author
    assert "Attempt06 immutable output already exists" in author
    assert "load_attempt06_contract" in author


def test_attempt06_supervisor_builds_then_runs_sequentially_and_never_promotes():
    source = text(SUPERVISOR)
    assert "--authorize-single-run" in source
    assert "--skip-build" not in source
    assert "active_heavy_processes()" in source
    assert "Attempt06 output/root already exists" in source
    assert "build_skyguard52_editor_attempt06" in source
    assert "author_immutable_candidate_attempt06" in source
    assert 'f"{mode}_capture_attempt06"' in source
    assert 'f"{mode}_profile_measured_attempt06"' in source
    assert "-csvCaptureFrames" not in source
    assert "-benchmark" not in source
    assert '"promotion_allowed": False' in source
    assert "capture_manifest_pass" in source
    assert "assert_locked_items" in source
    assert "predecessor_packages_after" in source
    profile_source = text(PROFILE_SOURCE)
    assert "P4.5-M01-LANDSCAPE-VISIBLE-006" in profile_source
    assert "RequiredAttempt06ContractId" in profile_source
    assert "P4.5-M01-LANDSCAPE-VISIBLE-005" not in profile_source


def test_attempt06_launcher_and_contract_remain_authorization_gated():
    launcher = text(LAUNCHER)
    assert "if (-not $AuthorizeSingleRun)" in launcher
    assert "--authorize-single-run" in launcher
    assert "SkipBuild" not in launcher
    contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    assert contract["native_implementation_boundary"][
        "implementation_complete"
    ] is True
    assert contract["execution_authorization"]["unreal_launch_allowed"] is False
    assert contract["execution_authorization"]["promotion_allowed"] is False
