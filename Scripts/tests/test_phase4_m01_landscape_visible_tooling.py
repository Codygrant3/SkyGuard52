from __future__ import annotations

import ast
import importlib.util
import json
import re
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_contract import load_effective_contract


CONTRACT = load_effective_contract()
BUILDER = ROOT / "Scripts/build_skyguard_phase4_m01_landscape_material_validation.py"
CAPTURE = ROOT / "Scripts/capture_skyguard_phase4_m01_landscape_visible_review.py"
EDITOR_VERIFY = ROOT / "Scripts/verify_skyguard_phase4_m01_landscape_material_assets.py"
GATE_VERIFY = ROOT / "Scripts/verify_skyguard_phase4_m01_landscape_visible_gpu_gate.py"
SUPERVISOR = ROOT / "Scripts/run_skyguard_phase4_m01_landscape_visible_gpu_gate.ps1"
DIRECTOR_H = ROOT / "Source/Skyguard52/SkyguardMission01EnvironmentDirector.h"
DIRECTOR_CPP = ROOT / "Source/Skyguard52/SkyguardMission01EnvironmentDirector.cpp"
AUTHOR_H = ROOT / "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.h"
AUTHOR_CPP = ROOT / "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.cpp"
UE58_CSV_FIXTURE = (
    ROOT / "Scripts/tests/fixtures/phase4_m01_ue58_dynamic_profile.csv"
)
SHADER_LOG_FIXTURE = (
    ROOT / "Scripts/tests/fixtures/phase4_m01_shader_classification.log"
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def call_names(path: Path) -> list[str]:
    tree = ast.parse(text(path), filename=str(path))
    names = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Attribute):
            names.append(function.attr.lower())
        elif isinstance(function, ast.Name):
            names.append(function.id.lower())
    return names


def load_gate_module():
    spec = importlib.util.spec_from_file_location(
        "phase4_m01_visible_gpu_gate_test_module", GATE_VERIFY
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_contract_remains_bounded_and_immutable():
    assert CONTRACT["contract_id"] == "P4.5-M01-LANDSCAPE-VISIBLE-004"
    assert CONTRACT["baseline"]["sha256"] == (
        "447e7ac49dc6c843f33bfc177ff46134b10035b6c6765d354ef790acf7f58d72"
    )
    assert CONTRACT["candidate"]["must_not_exist_before_authoring"] is True
    assert CONTRACT["candidate"]["must_never_overwrite_baseline"] is True
    assert CONTRACT["material_design"]["selected_texture_samples"] == 6
    assert CONTRACT["material_design"]["texture_sample_budget"] == 8
    assert CONTRACT["capture"]["profile_runs"]["warmup_seconds"] == 30
    assert CONTRACT["capture"]["profile_runs"]["measured_seconds"] == 60
    assert CONTRACT["capture"]["profile_runs"]["maximum_total_gpu_lane_minutes"] == 8


def test_candidate_builder_uses_exact_paths_and_six_locked_textures():
    source = text(BUILDER)
    assert CONTRACT["baseline"]["immutable_map"] in source
    assert CONTRACT["candidate"]["immutable_map"] in source
    assert CONTRACT["candidate"]["landscape_material"] in source
    locked_textures = [
        item["asset"]
        for item in CONTRACT["provenance"]["locked_unreal_assets"]
        if item["asset"].startswith("/Game/Skyguard/Textures/Imported/")
    ]
    assert len(locked_textures) == 6
    assert all(path in source for path in locked_textures)
    assert "required_flip" in source
    assert "apply_normal_green_correction" in source
    assert "LinearColor(1.0, -1.0, 1.0, 1.0)" in source
    assert "NORMALMAP" in source
    assert "baseline_hash_before" in source
    assert "baseline_hash_after" in source
    assert "author_governed_landscape_with_existing_graph" in source
    assert "post_edit_change" not in source
    assert 'set_editor_property("landscape_material", material)' in source
    assert "save_current_level()" in source
    assert "save_asset(TARGET_MAP, False)" in source
    assert "MaterialEditingLibrary.get_material_expressions" in source
    assert "MaterialEditingLibrary.get_num_material_expressions" in source
    assert 'get_editor_property("expressions")' not in source
    assert 'get_editor_property("expressions")' not in text(EDITOR_VERIFY)


def test_python_authoring_and_capture_never_generate_or_import_pcg():
    forbidden_calls = {
        "generate",
        "generate_local",
        "import_asset_tasks",
        "import_assets_automated",
        "download",
        "urlopen",
    }
    for path in (BUILDER, CAPTURE, EDITOR_VERIFY):
        assert forbidden_calls.isdisjoint(call_names(path)), path
    assert "PCG generation is never invoked" in text(CAPTURE)
    assert "world_saved" in text(CAPTURE)


def test_native_candidate_switch_preserves_candidate_only_landscape_policy():
    header = text(DIRECTOR_H)
    source = text(DIRECTOR_CPP)
    assert "SetUseAuthoredLandscapeSurfaceForValidation" in header
    assert "bUseAuthoredLandscapeSurface = false" in header
    assert "bAuthoredLandscapeSurfaceExposed" in header
    assert "if (!bUseAuthoredLandscapeSurface)" in source
    assert "LandTiles->ClearInstances()" in source
    assert "LandTiles->SetVisibility(!bUseAuthoredLandscapeSurface, true)" in source


def test_native_existing_graph_authoring_does_not_create_or_generate_graph():
    header = text(AUTHOR_H)
    source = text(AUTHOR_CPP)
    assert "AuthorGovernedLandscapeWithExistingGraph" in header
    method = source.split(
        "AuthorGovernedLandscapeWithExistingGraph", 1
    )[1]
    method = method.split(
        "USkyguardMission01EnvironmentAuthoringLibrary::AuditGovernedLandscapeAndGraph",
        1,
    )[0]
    assert "LoadObject<UPCGGraph>" in method
    assert "CreatePackage" not in method
    assert not re.search(r"\bGenerate(?:Local)?\s*\(", method)


def test_capture_contract_has_five_lit_views_and_three_fixed_diagnostics():
    source = text(CAPTURE)
    assert "capture_lit_views" in source
    assert "RenderingLibrary.create_render_target2d" in source
    assert 'filename + ".png"' in source
    assert "str(output.parent), output.name" in source
    assert "str(output.parent), output.stem" not in source
    assert "AutomationLibrary.take_high_res_screenshot" not in source
    assert "require_d3d12_sm6" in source
    assert "get_active_rhi_and_feature_level" in source
    assert 'EXPECTED_RHI_VALIDATION = "D3D12|SM6"' in source
    assert "get_editor_property(\"size_x\")" not in source
    assert 'requested_lit_count": 5' in source
    for diagnostic in (
        "candidate_diagnostic_landscape_lod_C05.png",
        "candidate_diagnostic_shader_complexity_C04.png",
        "candidate_diagnostic_component_boundary_C05.png",
    ):
        assert diagnostic in source
    assert "Landscape.DebugViewMode 5" in source
    assert "Landscape.DebugViewMode 6" in source
    assert "viewmode shadercomplexity" in source


def test_supervisor_is_sequential_bounded_and_fail_closed():
    source = text(SUPERVISOR)
    assert "Start-Job" not in source
    assert "ForEach-Object -Parallel" not in source
    for marker in (
        "$ExactHeavyNames",
        "Get-ExactHeavyProcesses",
        "Wait-ForZeroHeavyProcesses",
        "-Seconds 30",
        "-Seconds 60",
        "-d3d12",
        "-sm6",
        "maximum_total_gpu_lane_minutes = 8",
        "ShaderCompileWorker",
        "UbaAgent",
        "UbaServer",
        '"blender"',
    ):
        assert marker in source
    profile_loop = source.index("foreach ($profile in @(")
    baseline_entry = source.index('mode = "baseline"', profile_loop)
    candidate_entry = source.index('mode = "candidate"', profile_loop)
    assert baseline_entry < candidate_entry
    capture_loop = source.index("foreach ($captureSpec in @(")
    capture_end = source.index("$expectedCapturePaths = @()", capture_loop)
    capture_stage = source[capture_loop:capture_end]
    assert "-ExecutePythonScript=$CaptureScript" in capture_stage
    assert "-FilePath $EditorExe" in capture_stage
    assert "-run=pythonscript" not in capture_stage.lower()
    assert "Assert-CaptureRHIValidated -Stage $stage" in capture_stage
    profile_function = source[
        source.index("function Invoke-ProfileStage"):
        source.index("foreach ($required in @(")
    ]
    assert "-run=pythonscript" not in profile_function.lower()


def test_gate_verifier_requires_all_performance_and_visual_evidence():
    source = text(GATE_VERIFY)
    for marker in (
        "mean_frame_time_ms",
        "p95_frame_time_ms",
        "mean_gpu_time_ms",
        "p95_gpu_time_ms",
        "p95_draw_calls",
        "peak_working_set_mib",
        "INCOMPLETE_HUMAN_REVIEW",
        "all_captures_exact_1920x1080",
        "no_shader_compiles_measured",
        "no_texture_pool_over_budget",
    ):
        assert marker in source


def test_ue58_csv_and_shader_classification_regressions():
    gate = load_gate_module()
    profile = gate.analyze_csv(UE58_CSV_FIXTURE)
    assert profile["parseable"] is True
    assert profile["frame_count"] == 3
    assert profile["columns"] == {
        "frame": "FrameTime",
        "gpu": "GPUTime",
        "draw_calls": "RHI/DrawCalls",
    }
    assert profile["metrics"]["mean_frame_time_ms"] == 17.0
    assert profile["metrics"]["mean_gpu_time_ms"] == 8.0
    assert profile["metrics"]["p95_draw_calls"] == 219.0
    scan = gate.scan_logs([SHADER_LOG_FIXTURE])
    assert scan["shader_autogen_header_hits"] == 1
    assert scan["shader_compile_hits"] == 1
    assert "AutogenShaderHeaders.ush" in scan[
        "shader_autogen_header_samples"
    ][0]
