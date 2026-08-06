from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_attempt06_camera_math import build_proof
from phase4_m01_landscape_attempt06_contract import load_attempt06_contract


CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review"
    / "PHASE4_M01_LANDSCAPE_VISIBLE_REPAIR_CONTRACT_ATTEMPT06.json"
)
READINESS = (
    ROOT
    / "Scripts"
    / "verify_skyguard_phase4_m01_landscape_attempt06_readiness.py"
)


def contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def test_attempt06_preserves_recovery03_and_attempt05_packages():
    spec = contract()
    predecessor = spec["immutable_predecessor"]
    for item in (
        predecessor["recovery_manifest"],
        predecessor["gate_report"],
        *predecessor["package_hashes"].values(),
    ):
        path = ROOT / item["file"]
        assert path.is_file()
        assert sha256_file(path) == item["sha256"]
    assert predecessor["mutation_allowed"] is False
    assert predecessor["promotion_allowed"] is False


def test_attempt05_failure_is_not_dismissed_as_name_only():
    diagnosis = contract()["attempt05_failure_diagnosis"]
    assert diagnosis["substantive_visual_failure"] is True
    assert diagnosis["actual_capture_camera_ids"] != diagnosis[
        "gate_expected_camera_ids"
    ]
    assert len(diagnosis["actual_per_camera_coverage_fraction"]) == 5
    assert all(
        value == 0.0
        for value in diagnosis[
            "actual_per_camera_coverage_fraction"
        ].values()
    )
    assert diagnosis["actual_component_color_bucket_count"] == 0
    assert len(diagnosis["capture_path_failure"]) >= 3
    assert len(diagnosis["camera_framing_failure"]) >= 3


def test_attempt06_loader_replaces_legacy_camera_list():
    effective = load_attempt06_contract()
    assert effective["contract_id"] == "P4.5-M01-LANDSCAPE-VISIBLE-006"
    assert [camera["id"] for camera in effective["capture"]["cameras"]] == [
        "C01_ESTABLISHING_HIGH",
        "C02_SHORELINE_GRAZE",
        "C03_ROUTE_LOW",
        "C04_INLAND_CLOSE",
        "C05_COVERAGE_HIGH",
    ]
    assert effective["capture"]["cameras"] == effective["repair"][
        "capture_revision"
    ]["cameras"]


def test_attempt06_camera_math_and_all_16_component_proof():
    proof = build_proof()
    assert proof["attempt05_all_five_camera_framing_proofs_pass"] is False
    assert proof["all_five_camera_framing_proofs_pass"] is True
    assert len(proof["camera_results"]) == 5
    assert all(
        item["forward_ray_intersects_landscape_bounds"]
        and item["projected_top_surface_fraction"]
        >= item["minimum_landscape_pixel_fraction"]
        for item in proof["camera_results"]
    )
    c05 = proof["c05_all_component_proof"]
    assert c05["all_16_component_bounds_inside_viewport"] is True
    assert c05["component_count"] == 16
    assert len(c05["components"]) == 16
    assert c05["minimum_conservative_component_pixel_area"] >= 40000.0
    assert all(
        item["all_8_bounds_corners_inside_viewport"]
        and item["conservative_projected_pixel_area"] >= 40000.0
        for item in c05["components"]
    )


def test_attempt06_contract_requires_exact_show_only_sync_and_palette():
    capture = contract()["capture_revision"]
    diagnostic = capture["diagnostic_capture"]
    assert diagnostic["show_only_population"] == (
        "explicit_16_ULandscapeComponent_enumeration"
    )
    assert diagnostic["show_only_component_count_required"] == 16
    assert diagnostic["flush_rendering_commands_before_capture_required"] is True
    component = capture["component_id_gate"]
    assert component["expected_ids"] == 16
    assert component["minimum_pixels_per_expected_id"] >= 10000
    assert component["generic_color_bucket_count_is_forbidden"] is True


def test_attempt06_is_implemented_but_offline_and_not_authorized():
    spec = contract()
    assert all(
        spec["execution_authorization"][key] is False
        for key in (
            "unreal_launch_allowed",
            "authoring_allowed",
            "capture_allowed",
            "profiling_allowed",
            "automatic_retry_allowed",
            "promotion_allowed",
        )
    )
    assert spec["native_implementation_boundary"][
        "implementation_complete"
    ] is True
    source = READINESS.read_text(encoding="utf-8")
    assert "UnrealEditor" not in source
    assert "subprocess" not in source
    assert '"unreal_launched": False' in source


def test_attempt06_immutable_outputs_do_not_exist_before_authoring():
    outputs = contract()["future_immutable_outputs"]
    for key in (
        "map_file",
        "material_file",
        "coverage_material_file",
        "component_id_material_file",
        "attempt_root",
    ):
        assert not (ROOT / outputs[key]).exists()
