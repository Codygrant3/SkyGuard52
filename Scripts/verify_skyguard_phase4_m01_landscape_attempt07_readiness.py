"""Offline, fail-closed readiness for the Attempt07 tiny live proof."""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from verify_skyguard_phase4_m01_landscape_visible_gpu_gate import (
    decode_png_rgb8,
)


CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_CONTRACT.json"
)
LAUNCHER = (
    ROOT
    / "Scripts/"
    "run_skyguard_phase4_m01_landscape_visible_attempt07_tiny_proof.ps1"
)
OUTPUT = (
    ROOT
    / "Saved/Reports/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_READINESS.json"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    contract = json.loads(
        CONTRACT_PATH.read_text(encoding="utf-8-sig")
    )
    predecessor_root = ROOT / contract["immutable_predecessor"]["root"]
    predecessor_exact = all(
        (predecessor_root / item["file"]).is_file()
        and sha256_file(predecessor_root / item["file"]) == item["sha256"]
        for item in contract["immutable_predecessor"]["files"].values()
    )
    gate = json.loads(
        (predecessor_root / "gate_report.json").read_text(
            encoding="utf-8-sig"
        )
    )
    packages_exact = all(
        (ROOT / item["file"]).is_file()
        and sha256_file(ROOT / item["file"]) == item["sha256"]
        for item in contract["locked_production_packages"].values()
    )
    module = ROOT / contract["compiled_module"]["file"]
    implementation_paths = {
        "diagnostic_builder": (
            ROOT
            / "Scripts/"
            "build_skyguard_phase4_m01_landscape_material_validation.py"
        ),
        "attempt07_author": (
            ROOT
            / "Scripts/"
            "build_skyguard_phase4_m01_landscape_attempt07_diagnostics.py"
        ),
        "attempt07_tiny_proof": (
            ROOT
            / "Scripts/"
            "prove_skyguard_phase4_m01_landscape_attempt07_tiny_live.py"
        ),
        "attempt07_supervisor": (
            ROOT
            / "Scripts/"
            "supervise_skyguard_phase4_m01_landscape_visible_"
            "attempt07_tiny_proof.py"
        ),
    }
    sources = {
        name: path.read_text(encoding="utf-8")
        for name, path in implementation_paths.items()
    }
    implementation_exact = all(
        sha256_file(implementation_paths[name])
        == contract["implementation_hashes"][name]
        for name in implementation_paths
    )
    capture_root = (
        ROOT
        / "Saved/Profiling/Phase4/M01_LandscapeVisible_Attempt06/"
        "attempt_20260802T180523749Z/recovery_01/artifacts/captures/candidate"
    )
    coverage_maxima = {}
    coverage_rgb = {}
    for camera_id in contract["formal_diagnosis"]["diagnostic_pixels"][
        "coverage_max_rgb8_by_camera"
    ]:
        path = (
            capture_root
            / f"candidate_diagnostic_landscape_coverage_{camera_id}.png"
        )
        rgb = decode_png_rgb8(path)[2]
        coverage_rgb[camera_id] = rgb
        coverage_maxima[camera_id] = max(rgb)
    component_rgb = decode_png_rgb8(
        capture_root / "candidate_diagnostic_component_boundary_C05.png"
    )[2]
    component_pixels = {
        tuple(component_rgb[index : index + 3])
        for index in range(0, len(component_rgb), 3)
    }
    outputs = contract["new_immutable_outputs"]
    execution_root = ROOT / contract["tiny_live_proof"]["execution_root"]
    author_source = sources["attempt07_author"]
    proof_source = sources["attempt07_tiny_proof"]
    supervisor_source = sources["attempt07_supervisor"]
    launcher_source = LAUNCHER.read_text(encoding="utf-8")
    diagnostic_builder_function = sources["diagnostic_builder"].split(
        "def build_unlit_diagnostic_material", 1
    )[1].split("\ndef spawn_review_cameras", 1)[0]
    checks = {
        "recovery02_evidence_hashes_exact": predecessor_exact,
        "recovery02_formal_failure_exact": (
            gate["gate"] == "FAIL"
            and gate["technical_gate"] == "FAIL"
            and gate["checks"][
                "all_five_landscape_coverage_and_readability_gates"
            ]
            is False
            and gate["checks"]["all_16_component_ids_visible"] is False
            and gate["checks"]["candidate_mean_frame_within_budget"] is False
            and gate["checks"]["candidate_p95_frame_within_budget"] is False
            and gate["checks"]["candidate_mean_gpu_within_budget"] is False
            and gate["checks"]["candidate_p95_gpu_within_budget"] is False
            and gate["checks"]["mean_frame_delta_within_budget"] is True
            and gate["checks"]["p95_frame_delta_within_budget"] is True
            and gate["checks"]["p95_gpu_delta_within_budget"] is True
        ),
        "locked_production_packages_exact": packages_exact,
        "compiled_module_exact": (
            module.is_file()
            and sha256_file(module) == contract["compiled_module"]["sha256"]
        ),
        "diagnostic_pixel_diagnosis_reproduced": (
            coverage_maxima
            == contract["formal_diagnosis"]["diagnostic_pixels"][
                "coverage_max_rgb8_by_camera"
            ]
            and all(red == green == blue for red, green, blue in component_pixels)
            and coverage_rgb["C05_COVERAGE_HIGH"] == component_rgb
        ),
        "implementation_hashes_and_python_syntax_exact": (
            implementation_exact
            and all(bool(ast.parse(source)) for source in sources.values())
        ),
        "builder_authors_landscape_usage_before_compile_and_save": (
            'set_editor_property("used_with_landscape", True)'
            in diagnostic_builder_function
            and diagnostic_builder_function.index(
                'set_editor_property("used_with_landscape", True)'
            )
            < diagnostic_builder_function.index(
                "mel.recompile_material(material)"
            )
            < diagnostic_builder_function.index(
                "save_loaded_asset(material, False)"
            )
        ),
        "author_is_new_assets_only_and_hash_locks_production": (
            "Attempt07 immutable diagnostic already exists" in author_source
            and "locked_packages_unchanged" in author_source
            and "used_with_landscape" in author_source
            and "save_current_level" not in author_source
        ),
        "tiny_proof_transform_precedes_native_configuration": (
            proof_source.index("capture.set_actor_location")
            < proof_source.index(
                "configure_landscape_scene_capture_diagnostic"
            )
            and proof_source.index("capture.set_actor_rotation")
            < proof_source.index(
                "configure_landscape_scene_capture_diagnostic"
            )
            and '"transform_applied_before_configuration": True'
            in proof_source
        ),
        "tiny_proof_is_three_images_and_fail_closed": (
            'captures_root / "coverage_C05.png"' in proof_source
            and 'captures_root / "coverage_C04.png"' in proof_source
            and 'captures_root / "component_id_C05.png"' in proof_source
            and "coverage_c05_minimum_fraction" in proof_source
            and "coverage_c04_minimum_fraction" in proof_source
            and "component_palette_minimum_pixels_per_id" in proof_source
            and "Attempt07 tiny live proof failed" in proof_source
        ),
        "supervisor_stops_before_full_capture_profile_or_promotion": (
            supervisor_source.index(
                '"author_attempt07_diagnostic_materials"'
            )
            < supervisor_source.index(
                '"attempt07_tiny_live_proof_d3d12_sm6"'
            )
            and '"full_capture_allowed": False' in supervisor_source
            and '"profile_allowed": False' in supervisor_source
            and '"promotion_allowed": False' in supervisor_source
            and "capture_skyguard_phase4" not in supervisor_source
            and "ProfileWarmupSeconds" not in supervisor_source
        ),
        "launcher_requires_explicit_single_tiny_proof": (
            "if (-not $AuthorizeSingleTinyProof)" in launcher_source
            and "--authorize-single-tiny-proof" in launcher_source
        ),
        "attempt07_outputs_absent": all(
            not (ROOT / outputs[name]["file"]).exists()
            for name in ("coverage_material", "component_id_material")
        ),
        "attempt07_execution_root_absent": not execution_root.exists(),
        "contract_forbids_full_run_retry_network_and_promotion": all(
            contract["execution_authorization"][field] is False
            for field in (
                "unreal_launch_allowed",
                "author_new_diagnostic_assets_allowed",
                "tiny_live_proof_allowed",
                "full_capture_allowed",
                "profile_allowed",
                "automatic_retry_allowed",
                "network_allowed",
                "promotion_allowed",
            )
        ),
    }
    ready = all(checks.values())
    report = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt07-readiness.v1"
        ),
        "contract_id": contract["contract_id"],
        "gate": (
            "PASS_ATTEMPT07_TINY_PROOF_READY_PENDING_AUTHORIZATION"
            if ready
            else "FAIL_ATTEMPT07_OFFLINE_NOT_READY"
        ),
        "root_cause": contract["formal_diagnosis"]["root_cause"],
        "performance_classification": contract[
            "absolute_performance_diagnosis"
        ]["classification"],
        "checks": checks,
        "unreal_launched": False,
        "attempt06_or_recovery02_mutated": False,
        "full_capture_invoked": False,
        "profile_invoked": False,
        "promotion_allowed": False,
        "authorized_command": (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            "\"D:\\Skyguard52\\Scripts\\run_skyguard_phase4_m01_"
            "landscape_visible_attempt07_tiny_proof.ps1\" "
            "-AuthorizeSingleTinyProof"
            if ready
            else None
        ),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
