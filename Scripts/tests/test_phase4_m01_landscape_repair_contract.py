from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_REPAIR_CONTRACT_ATTEMPT05.json"
)
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))


def test_attempt04_remains_failed_immutable_evidence():
    evidence = CONTRACT[
        "accepted_attempt04_is_immutable_failed_visual_evidence"
    ]
    assert evidence["sha256"] == (
        "cb2c13f3ce18a3462620306bcef4610d87c2f0cf28a7815b444bd68ab773a021"
    )
    assert evidence["material_sha256"] == (
        "e54682b64f43dbaf0e2c61f08436d495493c6db1f28998cce9583d0542c4042e"
    )
    assert evidence["visual_acceptance"] is False
    assert evidence["promotion_allowed"] is False


def test_attempt05_never_overwrites_prior_packages():
    outputs = CONTRACT["future_immutable_outputs"]
    evidence = CONTRACT[
        "accepted_attempt04_is_immutable_failed_visual_evidence"
    ]
    assert "attempt05" in outputs["map"].lower()
    assert "attempt05" in outputs["material"].lower()
    assert outputs["map"] != evidence["map"]
    assert outputs["material"] != evidence["material"]
    assert outputs["must_not_exist_before_authoring"] is True
    assert outputs["must_never_overwrite_attempt04"] is True
    assert outputs["must_never_overwrite_baseline"] is True


def test_all_components_require_live_render_readiness():
    audit = CONTRACT["authoring_revision"]["serialized_and_live_audit"]
    assert audit["landscape_component_count"] == 16
    assert audit["visible_component_count"] == 16
    assert audit["registered_component_count"] == 16
    assert audit["render_state_created_component_count"] == 16
    assert audit["hidden_in_game_component_count"] == 0
    assert audit["components_with_generated_material_instance"] == 16
    assert (
        audit[
            "components_whose_material_parent_resolves_to_governed_material"
        ]
        == 16
    )
    assert audit["bounds_intersect_all_contract_camera_frusta"] is True


def test_all_five_cameras_have_nonzero_coverage_and_readability_gates():
    capture = CONTRACT["capture_revision"]
    thresholds = capture["minimum_landscape_pixel_fraction_by_camera"]
    assert set(thresholds) == set(capture["camera_ids"])
    assert len(thresholds) == 5
    assert all(0.0 < value < 1.0 for value in thresholds.values())
    readability = capture["readability_inside_coverage_mask"]
    assert readability["minimum_median_luminance"] > 0.0
    assert readability["minimum_p90_minus_p10_luminance"] > 0.0
    assert (
        readability["minimum_largest_connected_region_fraction_of_mask"]
        >= 0.5
    )


def test_diagnostics_target_scene_capture_not_editor_viewport():
    capture = CONTRACT["capture_revision"]
    assert capture["landscape_coverage_capture"][
        "primitive_render_mode"
    ] == "PRM_UseShowOnlyList"
    assert capture["shader_complexity"][
        "viewport_console_command_forbidden"
    ] is True
    assert "ApplyViewMode(VMI_ShaderComplexity" in capture[
        "shader_complexity"
    ]["scene_capture_show_flags_source"]
    assert capture["component_boundary"][
        "viewport_console_command_forbidden"
    ] is True
    assert capture["component_boundary"]["per_component_color_ids"] == 16
    assert capture["component_boundary"][
        "all_component_ids_must_have_pixels"
    ] is True


def test_startup_frames_are_excluded_by_capture_boundary_not_filtering():
    performance = CONTRACT["performance_revision"]
    assert performance["same_process_warmup_and_measurement"] is True
    assert performance["boot_capture_forbidden"] is True
    assert performance["csvCaptureFrames_switch_forbidden"] is True
    assert (
        performance[
            "warmup_seconds_after_world_begin_play_and_camera_ready"
        ]
        == 30
    )
    assert performance["measured_seconds"] == 60
    assert "not filtered after capture" in performance["budget_scope"]


def test_contract_is_not_execution_authorization():
    authorization = CONTRACT["execution_authorization"]
    assert authorization["unreal_launch_allowed"] is False
    assert authorization["candidate_authoring_allowed"] is False
    assert authorization["promotion_allowed"] is False
