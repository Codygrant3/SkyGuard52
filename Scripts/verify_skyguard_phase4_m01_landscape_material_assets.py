"""Fresh-process acceptance for the immutable M01 Landscape material candidate.

This script is read-only with respect to Unreal packages. It loads the exact
candidate, verifies the governed Landscape/material/PCG handoff, and writes an
external JSON receipt. It never saves the world and never generates PCG.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
sys.path.insert(0, str(ROOT / "Scripts"))
from phase4_m01_landscape_contract import load_effective_contract


REPORT_PATH = (
    ROOT
    / "Saved/Reports/PHASE4_M01_LANDSCAPE_MATERIAL_EDITOR_ACCEPTANCE_ATTEMPT04.json"
)
CAMERA_PREFIX = "M01_P45_Camera_"
GRAPH_PATH = (
    "/Game/Skyguard/Environment/Mission01/PCG/PCG_M01_InlandVegetation"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def vector_close(value, expected: list[float], tolerance: float = 0.05) -> bool:
    return all(
        abs(actual - target) <= tolerance
        for actual, target in zip((value.x, value.y, value.z), expected)
    )


def rotation_close(value, expected: dict, tolerance: float = 0.05) -> bool:
    return all(
        abs(actual - target) <= tolerance
        for actual, target in (
            (value.pitch, expected["pitch"]),
            (value.yaw, expected["yaw"]),
            (value.roll, expected["roll"]),
        )
    )


def object_path(asset) -> str:
    if asset is None:
        return ""
    return unreal.SystemLibrary.get_path_name(asset).split(".", 1)[0]


def material_texture_samples(material) -> list:
    expressions = list(
        unreal.MaterialEditingLibrary.get_material_expressions(material) or []
    )
    return [
        expression
        for expression in expressions
        if isinstance(expression, unreal.MaterialExpressionTextureSample)
    ]


def main() -> None:
    contract = load_effective_contract()
    baseline = contract["baseline"]
    candidate = contract["candidate"]
    map_path = candidate["immutable_map"]
    material_path = candidate["landscape_material"]
    baseline_file = ROOT / baseline["file"]
    baseline_hash_before = sha256_file(baseline_file)

    if baseline_hash_before != baseline["sha256"]:
        raise RuntimeError("Immutable baseline hash failed before verification")
    if not unreal.EditorAssetLibrary.does_asset_exist(map_path):
        raise RuntimeError("Missing immutable candidate map: " + map_path)
    if not unreal.EditorAssetLibrary.does_asset_exist(material_path):
        raise RuntimeError("Missing immutable candidate material: " + material_path)
    if not unreal.EditorLevelLibrary.load_level(map_path):
        raise RuntimeError("Could not load immutable candidate map")

    actors = list(unreal.EditorLevelLibrary.get_all_level_actors())
    tag = unreal.Name(candidate["landscape_actor_tag"])
    landscapes = [
        actor
        for actor in actors
        if actor.get_class().get_name() in {"Landscape", "LandscapeStreamingProxy"}
        and tag in list(actor.get_editor_property("tags") or [])
    ]
    directors = [
        actor
        for actor in actors
        if actor.get_class().get_name()
        == "SkyguardMission01EnvironmentDirector"
    ]
    camera_by_id = {}
    for actor in actors:
        if not isinstance(actor, unreal.CameraActor):
            continue
        label = actor.get_actor_label() or ""
        if label.startswith(CAMERA_PREFIX):
            camera_by_id[label[len(CAMERA_PREFIX) :]] = actor

    authoring = getattr(
        unreal, "SkyguardMission01EnvironmentAuthoringLibrary", None
    )
    if authoring is None:
        raise RuntimeError("Native Phase 4 audit bridge is unavailable")
    director = directors[0] if len(directors) == 1 else None
    landscape = landscapes[0] if len(landscapes) == 1 else None
    audit = (
        authoring.audit_governed_landscape_and_graph(director)
        if director is not None
        else None
    )
    readiness = director.get_readiness() if director is not None else None
    material = unreal.load_asset(material_path)
    visible_audit = (
        authoring.audit_landscape_visible_readiness(landscape, material)
        if landscape is not None and material is not None
        else None
    )
    samples = material_texture_samples(material) if material is not None else []
    sampled_assets = sorted(
        object_path(sample.get_editor_property("texture")) for sample in samples
    )
    required_assets = sorted(
        item["asset"]
        for item in contract["provenance"]["locked_unreal_assets"]
        if item["asset"].startswith("/Game/Skyguard/Textures/Imported/")
    )

    normal_checks = []
    policy = contract["material_design"]["normal_green_handling"]
    for normal_path in (
        "/Game/Skyguard/Textures/Imported/T_L3_sand_N",
        "/Game/Skyguard/Textures/Imported/T_L4_grassrock_N",
    ):
        texture = unreal.load_asset(normal_path)
        compression = (
            str(texture.get_editor_property("compression_settings")).upper()
            if texture is not None
            else ""
        )
        normal_checks.append(
            bool(
                texture is not None
                and bool(texture.get_editor_property("flip_green_channel"))
                is bool(policy[normal_path][
                    "required_source_flip_green_channel"
                ])
                and "NORMALMAP" in compression
            )
        )
    expressions = (
        list(
            unreal.MaterialEditingLibrary.get_material_expressions(material)
            or []
        )
        if material is not None
        else []
    )
    correction_vectors = [
        expression.get_editor_property("constant")
        for expression in expressions
        if isinstance(expression, unreal.MaterialExpressionConstant3Vector)
    ]
    material_green_correction_exact = any(
        abs(value.r - 1.0) <= 0.001
        and abs(value.g + 1.0) <= 0.001
        and abs(value.b - 1.0) <= 0.001
        for value in correction_vectors
    )

    transform_spec = candidate["landscape_transform"]
    landscape_transform_exact = bool(
        landscape is not None
        and vector_close(
            landscape.get_actor_location(), transform_spec["location_cm"]
        )
        and rotation_close(
            landscape.get_actor_rotation(),
            {
                "pitch": transform_spec["rotation_degrees"][0],
                "yaw": transform_spec["rotation_degrees"][1],
                "roll": transform_spec["rotation_degrees"][2],
            },
        )
        and vector_close(landscape.get_actor_scale3d(), transform_spec["scale"])
    )

    camera_checks = {}
    for spec in contract["capture"]["cameras"]:
        actor = camera_by_id.get(spec["id"])
        camera_checks[spec["id"]] = bool(
            actor is not None
            and vector_close(actor.get_actor_location(), spec["location_cm"])
            and rotation_close(
                actor.get_actor_rotation(), spec["rotation_degrees"]
            )
        )

    bound_material = (
        landscape.get_editor_property("landscape_material")
        if landscape is not None
        else None
    )
    checks = {
        "baseline_hash_unchanged_before": (
            baseline_hash_before == baseline["sha256"]
        ),
        "candidate_map_round_trip_loaded": True,
        "exactly_one_governed_landscape": len(landscapes) == 1,
        "landscape_label_exact": bool(
            landscape is not None
            and landscape.get_actor_label()
            == candidate["landscape_actor_label"]
        ),
        "landscape_transform_exact": landscape_transform_exact,
        "landscape_component_count_exact": bool(
            audit is not None
            and int(audit.landscape_component_count)
            == int(candidate["landscape_component_count"])
        ),
        "exactly_one_environment_director": len(directors) == 1,
        "candidate_surface_exposed": bool(
            readiness is not None
            and readiness.authored_landscape_surface_exposed
            and int(readiness.land_tile_count) == 0
            and director.is_authored_landscape_surface_exposed()
        ),
        "legacy_land_tiles_not_visible": bool(
            director is not None
            and director.land_tiles is not None
            and not director.land_tiles.is_visible()
        ),
        "ocean_tiles_retained": bool(
            readiness is not None and int(readiness.ocean_tile_count) == 6
        ),
        "beach_tiles_retained": bool(
            readiness is not None and int(readiness.beach_tile_count) == 6
        ),
        "candidate_material_bound": object_path(bound_material) == material_path,
        "landscape_live_render_readiness": bool(
            visible_audit is not None
            and visible_audit.success
            and int(visible_audit.landscape_component_count) == 16
            and int(visible_audit.visible_component_count) == 16
            and int(visible_audit.registered_component_count) == 16
            and int(
                visible_audit.render_state_created_component_count
            )
            == 16
            and int(visible_audit.hidden_in_game_component_count) == 0
            and int(
                visible_audit.generated_material_instance_ready_component_count
            )
            == 16
            and int(
                visible_audit.governed_material_parent_match_component_count
            )
            == 16
            and int(
                visible_audit.contract_camera_frustum_intersection_count
            )
            == 5
        ),
        "exactly_six_texture_samples": len(samples) == 6,
        "locked_texture_assets_exact": sampled_assets == required_assets,
        "locked_normal_metadata_matches_attempt02_policy": all(normal_checks),
        "inland_normal_material_green_correction_exact": (
            material_green_correction_exact
        ),
        "existing_graph_bound": bool(
            audit is not None
            and audit.graph_contract_valid
            and object_path(audit.graph) == GRAPH_PATH
        ),
        "pcg_generation_locked": bool(
            audit is not None
            and audit.generation_locked
            and not director.is_pcg_generation_authorized()
        ),
        "pcg_output_zero": bool(
            audit is not None
            and int(audit.generated_pcg_component_count) == 0
            and int(audit.generated_pcg_instance_count) == 0
        ),
        "five_contract_cameras_exact": (
            len(camera_by_id) == 5 and all(camera_checks.values())
        ),
        "native_audit_passed": bool(audit is not None and audit.success),
    }
    if contract["contract_id"] in {
        "P4.5-M01-LANDSCAPE-VISIBLE-005",
        "P4.5-M01-LANDSCAPE-VISIBLE-006",
    }:
        outputs = contract["repair"]["future_immutable_outputs"]
        checks["immutable_diagnostic_materials_ready"] = all(
            unreal.EditorAssetLibrary.does_asset_exist(outputs[key])
            for key in ("coverage_material", "component_id_material")
        )

    baseline_hash_after = sha256_file(baseline_file)
    checks["baseline_hash_unchanged_after"] = (
        baseline_hash_after == baseline["sha256"]
        and baseline_hash_after == baseline_hash_before
    )
    report = {
        "schema": (
            "skyguard.phase4.m01-landscape-material-editor-acceptance.v1"
        ),
        "contract_id": contract["contract_id"],
        "map": map_path,
        "material": material_path,
        "baseline_sha256_before": baseline_hash_before,
        "baseline_sha256_after": baseline_hash_after,
        "material_texture_sample_count": len(samples),
        "sampled_texture_assets": sampled_assets,
        "landscape_visible_audit": {
            "success": bool(visible_audit and visible_audit.success),
            "visible_component_count": (
                int(visible_audit.visible_component_count)
                if visible_audit
                else -1
            ),
            "registered_component_count": (
                int(visible_audit.registered_component_count)
                if visible_audit
                else -1
            ),
            "render_state_created_component_count": (
                int(visible_audit.render_state_created_component_count)
                if visible_audit
                else -1
            ),
            "contract_camera_frustum_intersection_count": (
                int(visible_audit.contract_camera_frustum_intersection_count)
                if visible_audit
                else -1
            ),
        },
        "camera_checks": camera_checks,
        "generated_pcg_component_count": (
            int(audit.generated_pcg_component_count) if audit else -1
        ),
        "generated_pcg_instance_count": (
            int(audit.generated_pcg_instance_count) if audit else -1
        ),
        "checks": checks,
        "gate": "PASS" if all(checks.values()) else "FAIL",
        "limitations": [
            "This is a serialized fresh-process audit, not visible GPU acceptance.",
            "No package was saved and PCG generation was never invoked.",
        ],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    unreal.log("[SkyguardP45LandscapeAcceptance] " + json.dumps(report))
    if report["gate"] != "PASS":
        raise RuntimeError("Landscape material candidate acceptance failed")


if __name__ == "__main__":
    main()
