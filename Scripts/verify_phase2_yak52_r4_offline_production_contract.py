"""Fail-closed offline verifier for the Phase 2 Yak-52 R4 art contract.

The verifier reads hashes, JSON, text, and file presence only. It never launches
Blender or Unreal, imports assets, edits accepted content, or promotes R3 donors.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT / "Docs/AAA_Review/PHASE2_YAK52_R4_OFFLINE_PRODUCTION_CONTRACT.json"
)
REPORT_ROOT = ROOT / "Saved/Reports/Phase2Yak52R4OfflineProductionContract"
EXPECTED_SCHEMA = "skyguard.phase2.yak52-r4-offline-production-contract.v1"
EXPECTED_ID = "PHASE2-YAK52-R4-FINAL-ART-GAP-20260802-V1"
EXPECTED_SLICE_IDS = [f"R4-S{index:02d}" for index in range(1, 11)]
EXPECTED_CAMERA_IDS = {
    "R4_CAM_BEAUTY_PORT",
    "R4_CAM_SIDE_ORTHO",
    "R4_CAM_TOP_ORTHO",
    "R4_CAM_REAR_QUARTER",
    "R4_CAM_UNDERSIDE_ORTHO",
    "R4_CAM_NOSE_PROP_CLOSE",
    "R4_CAM_CANOPY_CLOSED_PORT",
    "R4_CAM_CANOPY_OPEN_PORT",
    "R4_CAM_REAR_COCKPIT_HERO",
    "R4_CAM_REAR_GUNNER_EYE",
    "R4_CAM_REAR_GUNNER_ADS",
    "R4_CAM_PILOT_SAFETY",
    "R4_CAM_CREW_PORT",
}
EXPECTED_DONORS = {
    "GEO_UPLIFT003R3_DONOR_CowlingShell",
    "GEO_UPLIFT003R3_DONOR_CowlingFrontRing",
    "GEO_UPLIFT003R3_DONOR_CowlingShutters",
    "GEO_UPLIFT003R3_DONOR_CowlingInletCone",
    "GEO_UPLIFT003R3_DONOR_Spinner",
    "GEO_UPLIFT003R3_DONOR_PropBlade_A",
    "GEO_UPLIFT003R3_DONOR_PropBlade_B",
    "GEO_UPLIFT003R3_DONOR_MainWheelWell_L",
    "GEO_UPLIFT003R3_DONOR_MainWheelWell_R",
    "GEO_UPLIFT003R3_DONOR_NoseWheelWell",
}
EXPECTED_DATUMS = {
    "DATUM_UPLIFT003R3_DONOR_CanopyTravel",
    "DATUM_UPLIFT003R3_DONOR_MainGearPivot_L",
    "DATUM_UPLIFT003R3_DONOR_MainGearPivot_R",
    "DATUM_UPLIFT003R3_DONOR_NoseGearPivot",
}
EXPECTED_REJECTION_COUNT = 6
EXPECTED_MATERIAL_FAMILIES = {
    "ExteriorPaint",
    "BareAndAnodizedMetal",
    "EngineAndExhaustMetal",
    "CanopyGlass",
    "RubberAndSeal",
    "CockpitPaintedMetal",
    "InstrumentPanel",
    "GaugeFaceGlassAndEmissive",
    "SeatLeatherAndPadding",
    "HarnessAndFabric",
    "CrewSkin",
    "CrewUniformAndGlove",
    "RifleMetalWoodPolymer",
    "IglaPaintMetalOptics",
    "LiveryPlacardAndDecal",
    "GrimeOilSootSaltAndWetness",
}
EXPECTED_BAKES = {
    "tangent_normal",
    "ambient_occlusion",
    "curvature",
    "thickness",
    "position",
    "material_id",
}
EXPECTED_SKELETAL_ASSETS = {
    "Pilot",
    "RearGunner_FirstPersonArms",
    "RearGunner_ThirdPerson",
}
EXPECTED_PIVOTS = {
    "PIVOT_Propeller",
    "PIVOT_RearCanopy",
    "PIVOT_Aileron_L",
    "PIVOT_Aileron_R",
    "PIVOT_Elevator",
    "PIVOT_Rudder",
    "PIVOT_Flap_L",
    "PIVOT_Flap_R",
    "PIVOT_MainGear_L",
    "PIVOT_MainGear_R",
    "PIVOT_NoseGear",
}
EXPECTED_SOCKETS = {
    "SOCKET_RearGunnerEye",
    "SOCKET_RifleGrip_R",
    "SOCKET_RifleSupport_L",
    "SOCKET_RifleMuzzle",
    "SOCKET_RifleSightAxis",
    "SOCKET_IglaGrip_R",
    "SOCKET_IglaSupport_L",
    "SOCKET_IglaLaunch",
    "SOCKET_IglaBackblast",
    "SOCKET_PropAxis",
    "SOCKET_PilotHead",
    "SOCKET_PilotTorso",
}
EXPECTED_CONTENT_BUDGETS = {
    "maximum_runtime_render_components": 40,
    "maximum_visible_triangles_rear_gunner_view": 500000,
    "maximum_visible_triangles_exterior_15m": 350000,
    "maximum_visible_triangles_exterior_50m": 160000,
    "maximum_visible_triangles_exterior_150m": 60000,
    "maximum_yak_draw_calls_rear_gunner_view": 85,
    "maximum_yak_draw_calls_exterior": 70,
    "maximum_unique_material_instances": 24,
    "maximum_resident_texture_memory_mib": 256,
    "maximum_skeletal_assets_visible": 3,
    "maximum_bones_per_skeletal_asset": 128,
    "maximum_simple_collision_primitives": 40,
    "maximum_physics_bodies": 24,
}
EXPECTED_RUNTIME_BUDGETS = {
    "game_thread": 1.0,
    "render_thread": 1.5,
    "gpu": 2.0,
}
SHA_RE = re.compile(r"^[0-9a-f]{64}$")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def project_path(raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        raise ValueError(f"Path must be project-relative: {raw}")
    resolved = (ROOT / path).resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"Path escapes project root: {raw}")
    return resolved


def unique_by(
    entries: list[dict[str, Any]], key: str, errors: list[str], label: str
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        value = entry.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"{label}[{index}]:missing_{key}")
            continue
        if value in result:
            errors.append(f"{label}:duplicate_{key}:{value}")
            continue
        result[value] = entry
    return result


def validate_contract(
    contract: dict[str, Any], contract_path: Path = CONTRACT_PATH
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    authority_hashes: dict[str, str] = {}

    if contract.get("schema") != EXPECTED_SCHEMA:
        errors.append("contract:schema_mismatch")
    if contract.get("contract_id") != EXPECTED_ID:
        errors.append("contract:id_mismatch")

    state = contract.get("current_state", {})
    if state.get("status") != "OFFLINE_CONTRACT_VALID_PRODUCTION_NOT_STARTED":
        errors.append("state:status_mismatch")
    for field in (
        "r4_blender_source_created",
        "r4_export_created",
        "r4_unreal_imported",
        "donor_promoted",
        "runtime_replaced",
        "manual_visual_acceptance",
        "runtime_performance_acceptance",
        "final",
        "aaa",
        "production_ready",
        "shipping_allowed",
    ):
        if state.get(field) is not False:
            errors.append(f"state:{field}_must_be_false")

    immutable = contract.get("immutability_policy", {})
    for field in (
        "source_files_read_only_until_isolated_r4_copy",
        "accepted_assets_must_not_be_modified",
    ):
        if immutable.get(field) is not True:
            errors.append(f"immutability:{field}_must_be_true")
    if immutable.get("hash_algorithm") != "SHA-256":
        errors.append("immutability:hash_algorithm_mismatch")

    loaded_json: dict[str, dict[str, Any]] = {}
    loaded_text: dict[str, str] = {}
    authority_inputs = contract.get("authority_inputs", [])
    if not isinstance(authority_inputs, list) or len(authority_inputs) != 10:
        errors.append("authority:expected_exactly_10_inputs")
        authority_inputs = []
    source_inventory = contract.get("current_blender_source_inventory", [])
    if not isinstance(source_inventory, list) or len(source_inventory) != 6:
        errors.append("sources:expected_exactly_6_inventory_entries")
        source_inventory = []
    inventory_by_id = unique_by(source_inventory, "id", errors, "sources")

    for label, entries, path_key in (
        ("authority", authority_inputs, "path"),
        ("source", source_inventory, "path"),
    ):
        for entry in entries:
            raw = entry.get(path_key)
            expected_hash = entry.get("sha256")
            expected_bytes = entry.get("bytes")
            if not isinstance(raw, str) or not raw:
                errors.append(f"{label}:path_missing")
                continue
            if not isinstance(expected_hash, str) or not SHA_RE.fullmatch(
                expected_hash
            ):
                errors.append(f"{label}:{raw}:sha256_invalid")
                continue
            try:
                path = project_path(raw)
            except ValueError as exc:
                errors.append(f"{label}:{exc}")
                continue
            if not path.is_file():
                errors.append(f"{label}:{raw}:missing")
                continue
            actual_bytes = path.stat().st_size
            actual_hash = sha256_file(path)
            authority_hashes[raw] = actual_hash
            if actual_bytes != expected_bytes:
                errors.append(f"{label}:{raw}:byte_count_drift")
            if actual_hash != expected_hash:
                errors.append(f"{label}:{raw}:hash_drift")
                continue
            if path.suffix.lower() == ".json":
                loaded_json[raw] = read_json(path)
            elif path.suffix.lower() in {".md", ".py"}:
                loaded_text[raw] = path.read_text(encoding="utf-8-sig")

    expected_source_dispositions = {
        "L88_PRESERVED_RUNTIME_BLOCKOUT": "PRESERVE_IMMUTABLE_BASELINE_COPY_ONLY",
        "PRODUCTION_001_REJECTED_STUDY": "REFERENCE_ONLY_NOT_DONOR_AUTHORITY",
        "PRODUCTION_002_REJECTED_DONOR_STUDY": "DO_NOT_OPEN_OR_IMPORT_DONOR_IDEAS_ONLY",
        "R3_PROVISIONAL_UPLIFT_SOURCE": "PRESERVE_IMMUTABLE_EVALUATION_SOURCE",
        "R3_QUARANTINE_EXPORT": "QUARANTINE_EVALUATION_ONLY",
        "R3_GENERATOR_SOURCE": "HELPER_AND_CAMERA_REFERENCE_ONLY",
    }
    if set(inventory_by_id) != set(expected_source_dispositions):
        errors.append("sources:inventory_id_set_mismatch")
    for source_id, disposition in expected_source_dispositions.items():
        if inventory_by_id.get(source_id, {}).get("disposition") != disposition:
            errors.append(f"sources:{source_id}:disposition_mismatch")

    by_suffix: dict[str, str] = {}
    for raw in loaded_json:
        by_suffix[Path(raw).name] = raw
    r3_manifest = loaded_json.get(
        by_suffix.get("BLD_M01_YAK_UPLIFT_003_R3_MANIFEST.json", ""), {}
    )
    r3_import = loaded_json.get(
        by_suffix.get("M01_YAK_R3_COMPONENT_IMPORT_CONTRACT.json", ""), {}
    )
    r3_quarantine = loaded_json.get(
        by_suffix.get("M01_YAK_R3_COMPONENT_QUARANTINE_AUDIT.json", ""), {}
    )
    r3_ledger = loaded_json.get(
        by_suffix.get("BLD_M01_YAK_UPLIFT_003_R3_COMPONENT_LEDGER.json", ""), {}
    )
    runtime_persistence = loaded_json.get(
        by_suffix.get("PHASE2_YAK_RUNTIME_PERSISTENCE.json", ""), {}
    )

    visual_review_text = next(
        (
            text
            for raw, text in loaded_text.items()
            if raw.endswith("BLD_M01_YAK_UPLIFT_003_R3_VISUAL_REVIEW.md")
        ),
        "",
    )
    for marker in (
        "Still rejected as visible final art",
        "Wing, tail, fuselage and canopy silhouettes remain visibly blockout-grade",
        "Crew anatomy, hands, gloves, sleeves and weapon grips remain simplified",
        "No component has yet passed Unreal scale, socket, collision, ADS",
    ):
        if marker not in visual_review_text:
            errors.append(f"r3_visual_review:missing_marker:{marker}")

    claims = r3_manifest.get("claims", {})
    for field in ("aaa", "final", "matched_visual_review_accepted", "unreal_accepted"):
        if claims.get(field) is not False:
            errors.append(f"r3_manifest:{field}_must_be_false")
    if r3_manifest.get("promotion_allowed") is not False:
        errors.append("r3_manifest:promotion_allowed_must_be_false")

    r3_truth = contract.get("r3_truth_boundary", {})
    if r3_truth.get("governed_component_count") != 240:
        errors.append("r3_truth:governed_component_count_mismatch")
    if r3_truth.get("exact_object_requirement_count") != 232:
        errors.append("r3_truth:exact_object_count_mismatch")
    if r3_truth.get("source_absent_hold_count") != 8:
        errors.append("r3_truth:source_absent_hold_count_mismatch")
    if r3_truth.get("classification_counts") != r3_ledger.get(
        "classification_counts"
    ):
        errors.append("r3_truth:classification_counts_do_not_match_ledger")
    if len(r3_truth.get("visible_final_art_rejections", [])) != (
        EXPECTED_REJECTION_COUNT
    ):
        errors.append("r3_truth:expected_6_final_art_rejections")
    for field in (
        "r3_final",
        "r3_aaa",
        "r3_production_accepted",
        "r3_runtime_replacement_allowed",
    ):
        if r3_truth.get(field) is not False:
            errors.append(f"r3_truth:{field}_must_be_false")

    donor = contract.get("donor_compatibility_boundary", {})
    donor_meshes = set(donor.get("exact_meshes", []))
    donor_datums = set(donor.get("reference_datums", []))
    if donor_meshes != EXPECTED_DONORS:
        errors.append("donor:exact_mesh_set_mismatch")
    if donor_datums != EXPECTED_DATUMS:
        errors.append("donor:reference_datum_set_mismatch")
    if set(r3_import.get("component_meshes", {})) != EXPECTED_DONORS:
        errors.append("donor:r3_import_mesh_set_mismatch")
    if set(r3_import.get("reference_datums", [])) != EXPECTED_DATUMS:
        errors.append("donor:r3_import_datum_set_mismatch")
    if r3_import.get("disposition") != "QUARANTINE_COMPONENT_EVALUATION_ONLY":
        errors.append("donor:r3_import_disposition_mismatch")
    if r3_import.get("unreal", {}).get("promotion_allowed") is not False:
        errors.append("donor:r3_import_allows_promotion")
    if r3_quarantine.get("promotion_allowed") is not False:
        errors.append("donor:r3_quarantine_allows_promotion")
    if len(r3_quarantine.get("components", [])) != 10:
        errors.append("donor:r3_quarantine_component_count_mismatch")
    for component in r3_quarantine.get("components", []):
        if component.get("evidence_complete_for_promotion") is not False:
            errors.append(
                "donor:"
                + str(component.get("ledger_identity"))
                + ":promotion_evidence_must_be_false"
            )
        if int(component.get("simple_collision_primitive_count", 0)) < 1:
            errors.append(
                "donor:"
                + str(component.get("ledger_identity"))
                + ":simple_collision_missing"
            )
        if int(component.get("material_slot_count", 0)) < 1:
            errors.append(
                "donor:"
                + str(component.get("ledger_identity"))
                + ":material_slot_missing"
            )
    for field in ("automatic_promotion_allowed", "whole_aircraft_reuse_allowed"):
        if donor.get(field) is not False:
            errors.append(f"donor:{field}_must_be_false")

    if runtime_persistence.get("gate") != "PASS":
        errors.append("runtime_persistence:gate_not_pass")
    runtime_checks = runtime_persistence.get("checks", {})
    if not runtime_checks or not all(value is True for value in runtime_checks.values()):
        errors.append("runtime_persistence:checks_not_all_true")

    slices = contract.get("ordered_asset_slices", [])
    if not isinstance(slices, list) or len(slices) != 10:
        errors.append("slices:expected_exactly_10")
        slices = []
    slice_by_id = unique_by(slices, "slice_id", errors, "slices")
    observed_ids = [entry.get("slice_id") for entry in slices]
    observed_orders = [entry.get("order") for entry in slices]
    if observed_ids != EXPECTED_SLICE_IDS:
        errors.append("slices:order_or_id_sequence_mismatch")
    if observed_orders != list(range(1, 11)):
        errors.append("slices:numeric_order_mismatch")
    prior: set[str] = set()
    camera_refs: set[str] = set()
    for item in slices:
        slice_id = str(item.get("slice_id"))
        dependencies = item.get("depends_on", [])
        if not isinstance(dependencies, list):
            errors.append(f"slices:{slice_id}:dependencies_not_array")
            dependencies = []
        unknown_or_future = set(dependencies) - prior
        if unknown_or_future:
            errors.append(
                f"slices:{slice_id}:unknown_or_future_dependencies:"
                + ",".join(sorted(unknown_or_future))
            )
        for field in ("name", "scope", "required_outputs", "acceptance_cameras", "exit_gate"):
            value = item.get(field)
            if value in (None, "", []):
                errors.append(f"slices:{slice_id}:empty_{field}")
        camera_refs.update(str(value) for value in item.get("acceptance_cameras", []))
        prior.add(slice_id)
    if set(slice_by_id) != set(EXPECTED_SLICE_IDS):
        errors.append("slices:id_set_mismatch")
    if set(slice_by_id.get("R4-S10", {}).get("depends_on", [])) != set(
        EXPECTED_SLICE_IDS[:-1]
    ):
        errors.append("slices:R4-S10_must_depend_on_all_prior_slices")

    visual = contract.get("visual_acceptance_contract", {})
    cameras = visual.get("required_cameras", [])
    if not isinstance(cameras, list) or len(cameras) != 13:
        errors.append("visual:expected_exactly_13_cameras")
        cameras = []
    camera_by_id = unique_by(cameras, "id", errors, "visual.cameras")
    if set(camera_by_id) != EXPECTED_CAMERA_IDS:
        errors.append("visual:camera_id_set_mismatch")
    if camera_refs != EXPECTED_CAMERA_IDS:
        errors.append("visual:slice_camera_coverage_set_mismatch")
    if visual.get("render_resolution") != [1920, 1080]:
        errors.append("visual:resolution_mismatch")
    if visual.get("blender_engine") != "BLENDER_EEVEE":
        errors.append("visual:blender_engine_mismatch")
    if visual.get("camera_mutation_allowed_after_slice_1") is not False:
        errors.append("visual:camera_mutation_allowed")
    if visual.get("crop_or_reframe_after_render_allowed") is not False:
        errors.append("visual:crop_or_reframe_allowed")
    required_camera_coverage = {
        "primary_silhouette",
        "fuselage_profile",
        "wing_planform",
        "tail",
        "underside",
        "propeller",
        "rear_canopy_closed",
        "rear_canopy_open",
        "rear_cockpit",
        "first_person_clearance",
        "sight_axis",
        "pilot_no_fire",
        "pilot",
    }
    observed_camera_coverage = {
        str(coverage)
        for camera in cameras
        for coverage in camera.get("coverage", [])
    }
    missing_coverage = required_camera_coverage - observed_camera_coverage
    if missing_coverage:
        errors.append(
            "visual:missing_camera_coverage:" + ",".join(sorted(missing_coverage))
        )
    for camera_id, camera in camera_by_id.items():
        if camera.get("projection") not in {"PERSPECTIVE", "ORTHOGRAPHIC"}:
            errors.append(f"visual:{camera_id}:projection_invalid")
        for field in ("location_m", "target_m"):
            vector = camera.get(field)
            if (
                not isinstance(vector, list)
                or len(vector) != 3
                or not all(isinstance(value, (int, float)) for value in vector)
            ):
                errors.append(f"visual:{camera_id}:{field}_invalid")
        if not isinstance(camera.get("lens_mm"), (int, float)):
            errors.append(f"visual:{camera_id}:lens_missing")
        if camera.get("projection") == "ORTHOGRAPHIC" and not isinstance(
            camera.get("ortho_scale_m"), (int, float)
        ):
            errors.append(f"visual:{camera_id}:ortho_scale_missing")

    materials = contract.get("material_and_texture_contract", {})
    if materials.get("maximum_authored_resolution") != 4096:
        errors.append("materials:maximum_authored_resolution_mismatch")
    if materials.get("eight_k_allowed") is not False:
        errors.append("materials:eight_k_must_be_false")
    if set(materials.get("required_bakes", [])) != EXPECTED_BAKES:
        errors.append("materials:required_bake_set_mismatch")
    if set(materials.get("material_families", [])) != EXPECTED_MATERIAL_FAMILIES:
        errors.append("materials:material_family_set_mismatch")
    if len(materials.get("pbr_rules", [])) < 7:
        errors.append("materials:pbr_rules_incomplete")
    densities = materials.get("target_texel_density_px_per_m", {})
    for field in (
        "exterior_primary",
        "cockpit_first_person",
        "crew_first_person",
        "weapon_first_person",
        "gear_and_engine",
    ):
        if not isinstance(densities.get(field), int) or densities[field] <= 0:
            errors.append(f"materials:invalid_texel_density:{field}")

    crew = contract.get("crew_and_rig_contract", {})
    if set(crew.get("required_skeletal_assets", [])) != EXPECTED_SKELETAL_ASSETS:
        errors.append("crew:required_skeletal_asset_set_mismatch")
    if crew.get("maximum_bones_per_asset") != 128:
        errors.append("crew:maximum_bones_mismatch")
    if crew.get("maximum_influences_per_vertex") != 8:
        errors.append("crew:maximum_influences_mismatch")
    if len(crew.get("required_pose_tests", [])) < 7:
        errors.append("crew:pose_tests_incomplete")
    if len(crew.get("required_quality_checks", [])) < 6:
        errors.append("crew:quality_checks_incomplete")

    axes = contract.get("pivot_socket_and_axis_contract", {})
    if set(axes.get("required_pivots", [])) != EXPECTED_PIVOTS:
        errors.append("axes:pivot_set_mismatch")
    if set(axes.get("required_sockets", [])) != EXPECTED_SOCKETS:
        errors.append("axes:socket_set_mismatch")
    if len(axes.get("axis_rules", [])) < 4:
        errors.append("axes:axis_rules_incomplete")

    collision = contract.get("collision_and_safety_contract", {})
    if collision.get("complex_as_simple_allowed") is not False:
        errors.append("collision:complex_as_simple_allowed")
    if collision.get("cosmetic_microdetail_collision_allowed") is not False:
        errors.append("collision:cosmetic_microdetail_collision_allowed")
    if collision.get("maximum_simple_collision_primitives") != 40:
        errors.append("collision:primitive_budget_mismatch")
    if collision.get("maximum_physics_bodies") != 24:
        errors.append("collision:physics_body_budget_mismatch")
    groups = collision.get("collision_groups", [])
    if not isinstance(groups, list) or len(groups) != 5:
        errors.append("collision:expected_exactly_5_groups")
        groups = []
    group_ids = [str(group.get("id")) for group in groups]
    if len(set(group_ids)) != len(group_ids):
        errors.append("collision:duplicate_group_id")
    primitive_sum = sum(
        int(group.get("maximum_primitives", 0)) for group in groups
    )
    if primitive_sum != collision.get("maximum_simple_collision_primitives"):
        errors.append("collision:group_primitive_sum_mismatch")
    if set(collision.get("required_volumes", {})) != {
        "CameraClearance",
        "PilotSafety",
        "RifleMuzzleClearance",
        "IglaBackblastClearance",
    }:
        errors.append("collision:required_volume_set_mismatch")
    if len(collision.get("trace_rules", [])) < 5:
        errors.append("collision:trace_rules_incomplete")

    performance = contract.get("performance_budget_contract", {})
    profile = performance.get("target_profile", {})
    if profile.get("resolution") != "2560x1440":
        errors.append("performance:resolution_mismatch")
    if profile.get("frame_rate_target_fps") != 60:
        errors.append("performance:frame_rate_target_mismatch")
    if profile.get("frame_budget_ms") != 16.67:
        errors.append("performance:frame_budget_mismatch")
    if performance.get("content_budgets") != EXPECTED_CONTENT_BUDGETS:
        errors.append("performance:content_budget_set_mismatch")
    if performance.get("runtime_delta_budgets_ms") != EXPECTED_RUNTIME_BUDGETS:
        errors.append("performance:runtime_delta_budget_set_mismatch")
    if len(performance.get("lod_requirements", [])) < 5:
        errors.append("performance:lod_requirements_incomplete")
    failure_rules = performance.get("failure_rules", [])
    if len(failure_rules) < 5:
        errors.append("performance:failure_rules_incomplete")
    if not any("downloadable" in str(rule) for rule in failure_rules):
        errors.append("performance:downloadable_build_is_not_budget_waiver_missing")
    if not any("one-percent" in str(rule) for rule in failure_rules):
        errors.append("performance:one_percent_frame_time_rule_missing")

    namespace = contract.get("planned_r4_namespace", {})
    planned_paths = [
        namespace.get("blender_directory"),
        namespace.get("blend"),
        namespace.get("export"),
        namespace.get("manifest"),
        namespace.get("comparison_directory"),
    ]
    if namespace.get("paths_must_be_absent_while_contract_status_is_not_started") is not True:
        errors.append("namespace:absence_guard_not_enabled")
    present_planned_paths: list[str] = []
    for raw in planned_paths:
        if not isinstance(raw, str) or not raw:
            errors.append("namespace:planned_path_missing")
            continue
        path = project_path(raw)
        if path.exists():
            present_planned_paths.append(raw)
    if present_planned_paths:
        errors.append(
            "namespace:r4_outputs_exist_while_not_started:"
            + ",".join(present_planned_paths)
        )

    completion = contract.get("r4_completion_gate", {})
    if len(completion.get("required_future_evidence", [])) < 10:
        errors.append("completion:future_evidence_incomplete")
    for field in (
        "automatic_promotion",
        "offline_contract_pass_is_completion",
        "offline_contract_pass_is_aaa_acceptance",
        "offline_contract_pass_is_runtime_acceptance",
    ):
        if completion.get(field) is not False:
            errors.append(f"completion:{field}_must_be_false")

    contract_hash = sha256_file(contract_path)
    return {
        "schema": "skyguard.phase2.yak52-r4-offline-production-audit.v1",
        "contract_path": str(contract_path),
        "contract_sha256": contract_hash,
        "authority_sha256": authority_hashes,
        "authority_input_count": len(authority_inputs),
        "blender_source_inventory_count": len(source_inventory),
        "r3_governed_component_count": r3_truth.get(
            "governed_component_count"
        ),
        "r3_final_art_rejection_count": len(
            r3_truth.get("visible_final_art_rejections", [])
        ),
        "quarantined_donor_mesh_count": len(donor_meshes),
        "quarantined_donor_promoted_count": 0,
        "ordered_asset_slice_count": len(slices),
        "visual_acceptance_camera_count": len(cameras),
        "planned_r4_paths_present": present_planned_paths,
        "contract_valid": not errors,
        "blender_launched": False,
        "unreal_launched": False,
        "accepted_assets_modified": False,
        "r4_production_started": False,
        "r4_imported": False,
        "runtime_replaced": False,
        "final": False,
        "aaa": False,
        "production_ready": False,
        "shipping_allowed": False,
        "warnings": warnings,
        "errors": errors,
        "status": (
            "PASS_R4_OFFLINE_CONTRACT_PRODUCTION_NOT_STARTED"
            if not errors
            else "FAIL_R4_OFFLINE_PRODUCTION_CONTRACT"
        ),
    }


def write_attempt(report: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    attempt_id = (
        f"attempt_{timestamp}_{report['contract_sha256'][:8]}_"
        f"{secrets.token_hex(4)}"
    )
    directory = REPORT_ROOT / attempt_id
    directory.mkdir(parents=True, exist_ok=False)
    completed = datetime.now(timezone.utc).isoformat()
    payload = dict(report)
    payload["attempt_id"] = attempt_id
    payload["completed_at_utc"] = completed
    audit_path = directory / "r4_offline_contract_audit.json"
    audit_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    status = {
        "schema": "skyguard.phase2.yak52-r4-offline-production-status.v1",
        "attempt_id": attempt_id,
        "state": payload["status"],
        "contract_sha256": payload["contract_sha256"],
        "audit_sha256": sha256_file(audit_path),
        "ordered_asset_slice_count": payload["ordered_asset_slice_count"],
        "visual_acceptance_camera_count": payload[
            "visual_acceptance_camera_count"
        ],
        "r4_production_started": False,
        "r4_imported": False,
        "runtime_replaced": False,
        "final": False,
        "aaa": False,
        "production_ready": False,
        "shipping_allowed": False,
        "completed_at_utc": completed,
    }
    (directory / "status.json").write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return directory


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    try:
        contract = read_json(args.contract)
        report = validate_contract(contract, args.contract)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {
                    "status": "FAIL_R4_OFFLINE_PRODUCTION_CONTRACT",
                    "errors": [str(exc)],
                    "production_ready": False,
                    "shipping_allowed": False,
                },
                indent=2,
            )
        )
        return 2
    if not args.no_write:
        report["attempt_directory"] = str(write_attempt(report))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 2 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
