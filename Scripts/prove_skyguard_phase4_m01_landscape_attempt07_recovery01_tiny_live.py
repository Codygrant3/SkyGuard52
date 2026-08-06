"""Three-image D3D12 proof for Attempt07 Recovery01 diagnostics."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
import prove_skyguard_phase4_m01_landscape_attempt07_tiny_live as proof_base
from phase4_m01_landscape_attempt06_contract import load_attempt06_contract


CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/"
    "PHASE4_M01_LANDSCAPE_VISIBLE_ATTEMPT07_RECOVERY01_CONTRACT.json"
)
CONTRACT_ID = "P4.5-M01-LANDSCAPE-VISIBLE-007-RECOVERY-01"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def compilation_audit(authoring, landscape, material) -> dict:
    audit = authoring.audit_landscape_material_compilation(
        landscape, material
    )
    result = {
        "success": bool(audit.success),
        "landscape_component_count": int(
            audit.landscape_component_count
        ),
        "generated_material_instance_count": int(
            audit.generated_material_instance_count
        ),
        "material_resource_count": int(audit.material_resource_count),
        "compilation_finished_resource_count": int(
            audit.compilation_finished_resource_count
        ),
        "valid_shader_map_resource_count": int(
            audit.valid_shader_map_resource_count
        ),
        "asset_compilation_queue_empty": bool(
            audit.asset_compilation_queue_empty
        ),
        "shader_compilation_queue_empty": bool(
            audit.shader_compilation_queue_empty
        ),
        "error": str(audit.error),
    }
    if not result["success"]:
        raise RuntimeError(
            "Attempt07 Recovery01 material compilation audit failed: "
            + json.dumps(result)
        )
    return result


def main() -> None:
    contract = json.loads(
        CONTRACT_PATH.read_text(encoding="utf-8-sig")
    )
    if contract["contract_id"] != CONTRACT_ID:
        raise RuntimeError("Attempt07 Recovery01 contract ID mismatch")
    output_root = Path(
        proof_base.parse_switch("SkyguardAttempt07Recovery01ProofRoot")
    )
    author_receipt = Path(
        proof_base.parse_switch(
            "SkyguardAttempt07Recovery01AuthorReceipt"
        )
    )
    proof_receipt = output_root / "tiny_proof_receipt.json"
    if proof_receipt.exists() or (output_root / "captures").exists():
        raise RuntimeError(
            "Attempt07 Recovery01 tiny proof output already exists"
        )
    if not author_receipt.is_file():
        raise RuntimeError(
            "Attempt07 Recovery01 author receipt is missing"
        )
    authored = json.loads(
        author_receipt.read_text(encoding="utf-8-sig")
    )
    if authored.get("gate") != "PASS":
        raise RuntimeError(
            "Attempt07 Recovery01 author receipt did not pass"
        )

    failed = contract["immutable_failed_attempt07"]
    failed_root = ROOT / failed["root"]
    for name, item in failed["files"].items():
        path = failed_root / item["file"]
        if not path.is_file() or sha256_file(path) != item["sha256"]:
            raise RuntimeError(
                "Failed Attempt07 evidence hash changed: " + name
            )

    authoring = unreal.SkyguardMission01EnvironmentAuthoringLibrary
    rhi = authoring.get_active_rhi_and_feature_level().strip().upper()
    proof = contract["tiny_live_proof"]
    if rhi != proof["rhi_required"]:
        raise RuntimeError(
            "Attempt07 Recovery01 tiny proof requires D3D12|SM6: " + rhi
        )

    locked_before = {}
    for name, item in contract["locked_production_packages"].items():
        digest = sha256_file(ROOT / item["file"])
        if digest != item["sha256"]:
            raise RuntimeError("Locked package hash failed: " + name)
        locked_before[name] = digest

    outputs = contract["new_immutable_outputs"]
    for name in ("coverage_material", "component_id_material"):
        path = ROOT / outputs[name]["file"]
        if sha256_file(path) != authored["output_hashes"][name]:
            raise RuntimeError(
                "Attempt07 Recovery01 authored material hash changed: "
                + name
            )

    effective = load_attempt06_contract()
    candidate_map = effective["candidate"]["immutable_map"]
    if not unreal.EditorLevelLibrary.load_level(candidate_map):
        raise RuntimeError("Could not load Attempt06 candidate map read-only")
    landscape = proof_base.find_landscape(effective)
    governed = unreal.load_asset(
        effective["candidate"]["landscape_material"]
    )
    coverage = unreal.load_asset(outputs["coverage_material"]["asset"])
    component = unreal.load_asset(
        outputs["component_id_material"]["asset"]
    )
    if not governed or not coverage or not component:
        raise RuntimeError(
            "Attempt07 Recovery01 material set is incomplete"
        )

    specs = {
        item["id"]: item for item in effective["capture"]["cameras"]
    }
    width, height = proof["resolution"]
    captures_root = output_root / "captures"
    capture_records = []
    material_audits = {}
    try:
        material_audits["coverage"] = proof_base.apply_material(
            authoring, landscape, coverage
        )
        material_audits["coverage_compilation"] = compilation_audit(
            authoring, landscape, coverage
        )
        coverage_c05 = captures_root / "coverage_C05.png"
        coverage_c04 = captures_root / "coverage_C04.png"
        capture_records.append(
            proof_base.capture_one(
                authoring,
                landscape,
                specs["C05_COVERAGE_HIGH"],
                unreal.SkyguardLandscapeCaptureDiagnosticMode
                .LANDSCAPE_COVERAGE,
                coverage_c05,
                width,
                height,
                proof["fov_degrees"],
            )
        )
        capture_records.append(
            proof_base.capture_one(
                authoring,
                landscape,
                specs["C04_INLAND_CLOSE"],
                unreal.SkyguardLandscapeCaptureDiagnosticMode
                .LANDSCAPE_COVERAGE,
                coverage_c04,
                width,
                height,
                proof["fov_degrees"],
            )
        )
        material_audits["component_id"] = proof_base.apply_material(
            authoring, landscape, component
        )
        material_audits["component_id_compilation"] = compilation_audit(
            authoring, landscape, component
        )
        component_c05 = captures_root / "component_id_C05.png"
        capture_records.append(
            proof_base.capture_one(
                authoring,
                landscape,
                specs["C05_COVERAGE_HIGH"],
                unreal.SkyguardLandscapeCaptureDiagnosticMode
                .COMPONENT_BOUNDARY,
                component_c05,
                width,
                height,
                proof["fov_degrees"],
            )
        )
    finally:
        material_audits["governed_restore"] = proof_base.apply_material(
            authoring, landscape, governed
        )

    coverage_c05_result = proof_base.coverage_analysis(
        coverage_c05, proof["coverage_white_rgb8_minimum"]
    )
    coverage_c04_result = proof_base.coverage_analysis(
        coverage_c04, proof["coverage_white_rgb8_minimum"]
    )
    palette = proof_base.palette_analysis(
        component_c05,
        proof["component_palette_rgb8_tolerance_per_channel"],
    )
    palette_minimum = proof[
        "component_palette_minimum_pixels_per_id"
    ]
    checks = {
        "active_rhi_exact": rhi == "D3D12|SM6",
        "native_compilation_audits_exact": all(
            material_audits[name]["success"]
            and material_audits[name]["landscape_component_count"] == 16
            and material_audits[name][
                "generated_material_instance_count"
            ]
            == 16
            and material_audits[name]["material_resource_count"] == 16
            and material_audits[name][
                "compilation_finished_resource_count"
            ]
            == 16
            and material_audits[name][
                "valid_shader_map_resource_count"
            ]
            == 16
            for name in (
                "coverage_compilation",
                "component_id_compilation",
            )
        ),
        "three_captures_exact": len(capture_records) == 3,
        "all_camera_transforms_applied_before_configuration": all(
            item["transform_applied_before_configuration"]
            for item in capture_records
        ),
        "all_show_only_material_sync_audits_exact": all(
            item["show_only_component_count"] == 16
            and item["generated_material_instance_count"] == 16
            and item["material_parent_match_count"] == 16
            and item["render_thread_synchronized"]
            for item in capture_records
        ),
        "coverage_c05_visible_white": (
            coverage_c05_result["white_fraction"]
            >= proof["coverage_c05_minimum_fraction"]
        ),
        "coverage_c04_visible_white": (
            coverage_c04_result["white_fraction"]
            >= proof["coverage_c04_minimum_fraction"]
        ),
        "all_16_component_ids_visible": (
            palette["matching_id_count"] == 16
            and all(
                count >= palette_minimum
                for count in palette["pixel_counts"].values()
            )
        ),
        "governed_material_restored": (
            material_audits["governed_restore"]["success"]
        ),
    }
    locked_after = {
        name: sha256_file(ROOT / item["file"])
        for name, item in contract["locked_production_packages"].items()
    }
    checks["locked_production_packages_unchanged"] = (
        locked_after == locked_before
    )
    report = {
        "schema": (
            "skyguard.phase4.m01-landscape-visible-"
            "attempt07-recovery01-tiny-proof.v1"
        ),
        "contract_id": contract["contract_id"],
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "rhi": rhi,
        "resolution": [width, height],
        "landscape_usage_flag_claimed": False,
        "material_audits": material_audits,
        "capture_records": capture_records,
        "coverage_c05": coverage_c05_result,
        "coverage_c04": coverage_c04_result,
        "component_palette": palette,
        "checks": checks,
        "locked_packages_before": locked_before,
        "locked_packages_after": locked_after,
        "failed_attempt07_evidence_unchanged": True,
        "world_saved": False,
        "pcg_generation_invoked": False,
        "full_capture_invoked": False,
        "profile_invoked": False,
        "promotion_allowed": False,
    }
    proof_receipt.parent.mkdir(parents=True, exist_ok=True)
    proof_receipt.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    if report["gate"] != "PASS":
        raise RuntimeError(
            "Attempt07 Recovery01 tiny live proof failed"
        )
    unreal.log(
        "[SkyguardAttempt07Recovery01TinyProof] " + json.dumps(report)
    )


if __name__ == "__main__":
    main()
