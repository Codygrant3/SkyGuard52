from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_CONTRACT.json"
)
BUILDER = (
    ROOT
    / "Scripts/"
    "build_skyguard_phase4_m01_landscape_material_validation.py"
)
AUTHOR = (
    ROOT
    / "Scripts/"
    "build_skyguard_phase4_m01_landscape_attempt07_diagnostics.py"
)
PROOF = (
    ROOT
    / "Scripts/"
    "prove_skyguard_phase4_m01_landscape_attempt07_tiny_live.py"
)
SUPERVISOR = (
    ROOT
    / "Scripts/"
    "supervise_skyguard_phase4_m01_landscape_visible_"
    "attempt07_tiny_proof.py"
)
READINESS = (
    ROOT
    / "Scripts/"
    "verify_skyguard_phase4_m01_landscape_attempt07_readiness.py"
)
LAUNCHER = (
    ROOT
    / "Scripts/"
    "run_skyguard_phase4_m01_landscape_visible_attempt07_tiny_proof.ps1"
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8-sig"))


def test_attempt07_binds_formal_recovery02_failure_and_locked_packages():
    spec = contract()
    predecessor = spec["immutable_predecessor"]
    root = ROOT / predecessor["root"]
    for item in predecessor["files"].values():
        assert sha256_file(root / item["file"]) == item["sha256"]
    gate = json.loads(
        (root / "gate_report.json").read_text(encoding="utf-8-sig")
    )
    assert gate["gate"] == "FAIL"
    assert gate["technical_gate"] == "FAIL"
    for item in spec["locked_production_packages"].values():
        assert sha256_file(ROOT / item["file"]) == item["sha256"]


def test_attempt07_diagnosis_distinguishes_shader_fallback_from_selection():
    diagnosis = contract()["formal_diagnosis"]
    assert diagnosis["show_only_lifecycle"]["explicit_component_count"] == 16
    assert diagnosis["show_only_lifecycle"][
        "material_parent_match_count"
    ] == 16
    pixels = diagnosis["diagnostic_pixels"]
    assert pixels["coverage_c05_and_component_id_c05_decoded_rgb_identical"]
    assert pixels["component_id_all_pixels_grayscale"]
    assert pixels["observed_matching_palette_ids"] == 0
    assert "used_with_landscape" in diagnosis["root_cause"]["primary"]
    assert "after native capture configuration" in diagnosis[
        "root_cause"
    ]["secondary"]


def test_attempt07_builder_sets_landscape_usage_before_compile_and_save():
    source = text(BUILDER).split(
        "def build_unlit_diagnostic_material", 1
    )[1].split("\ndef spawn_review_cameras", 1)[0]
    usage = source.index('set_editor_property("used_with_landscape", True)')
    compile_material = source.index("mel.recompile_material(material)")
    save = source.index("save_loaded_asset(material, False)")
    assert usage < compile_material < save
    assert "did not retain Landscape usage" in source


def test_attempt07_author_and_proof_are_parseable_and_immutable():
    for path in (AUTHOR, PROOF, SUPERVISOR, READINESS):
        ast.parse(text(path))
    author = text(AUTHOR)
    assert "Attempt07 immutable diagnostic already exists" in author
    assert "locked_packages_unchanged" in author
    assert '"world_saved": False' in author
    assert '"only_new_diagnostic_packages_saved": True' in author
    proof = text(PROOF)
    assert proof.index("capture.set_actor_location") < proof.index(
        "configure_landscape_scene_capture_diagnostic"
    )
    assert proof.index("capture.set_actor_rotation") < proof.index(
        "configure_landscape_scene_capture_diagnostic"
    )
    assert 'captures_root / "coverage_C05.png"' in proof
    assert 'captures_root / "coverage_C04.png"' in proof
    assert 'captures_root / "component_id_C05.png"' in proof
    assert '"full_capture_invoked": False' in proof
    assert '"profile_invoked": False' in proof


def test_attempt07_tiny_proof_gate_is_strict_and_precedes_any_full_run():
    spec = contract()
    proof = spec["tiny_live_proof"]
    assert proof["resolution"] == [640, 360]
    assert proof["coverage_white_rgb8_minimum"] >= 240
    assert proof["coverage_c05_minimum_fraction"] >= 0.05
    assert proof["coverage_c04_minimum_fraction"] >= 0.01
    assert proof["component_palette_minimum_pixels_per_id"] >= 500
    assert proof["all_16_component_ids_required"] is True
    for field in (
        "world_save_forbidden",
        "pcg_generation_forbidden",
        "full_capture_forbidden",
        "profile_forbidden",
        "automatic_retry_forbidden",
        "promotion_forbidden",
    ):
        assert proof[field] is True


def test_attempt07_performance_failure_is_absolute_not_relative():
    performance = contract()["absolute_performance_diagnosis"]
    assert performance["classification"] == (
        "ENVIRONMENT_WIDE_ABSOLUTE_FRAME_BUDGET_MISS_"
        "NOT_LANDSCAPE_REGRESSION"
    )
    assert performance["baseline_also_misses_absolute_budgets"] is True
    assert performance["candidate_passes_all_relative_delta_budgets"] is True
    assert performance[
        "unchanged_full_profile_rerun_has_no_evidentiary_value"
    ] is True
    assert len(performance["dominant_existing_signals"]) >= 7


def test_attempt07_supervisor_and_launcher_are_single_proof_only():
    source = text(SUPERVISOR)
    assert source.index('"author_attempt07_diagnostic_materials"') < source.index(
        '"attempt07_tiny_live_proof_d3d12_sm6"'
    )
    assert "--authorize-single-tiny-proof" in source
    assert "capture_skyguard_phase4" not in source
    assert "ProfileWarmupSeconds" not in source
    assert '"full_capture_allowed": False' in source
    assert '"profile_allowed": False' in source
    assert '"promotion_allowed": False' in source
    launcher = text(LAUNCHER)
    assert "if (-not $AuthorizeSingleTinyProof)" in launcher
    assert "--authorize-single-tiny-proof" in launcher
    spec = contract()
    assert not (
        ROOT / spec["tiny_live_proof"]["execution_root"]
    ).exists()
    for name in ("coverage_material", "component_id_material"):
        assert not (
            ROOT / spec["new_immutable_outputs"][name]["file"]
        ).exists()
