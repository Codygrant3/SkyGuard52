from __future__ import annotations

import argparse
import ast
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


ROOT_DEFAULT = Path(__file__).resolve().parents[1]
CONTRACT_SCHEMA = (
    "skyguard.m01.hero-grouped-topology-bake.contract.v1"
)
MANIFEST_SCHEMA = (
    "skyguard.m01.hero-grouped-topology-bake.manifest.v1"
)
REPORT_SCHEMA = (
    "skyguard.m01.hero-grouped-topology-bake.verification.v1"
)
PROMOTION = (
    "grouped_topology_candidate_requires_direct_original_resolution_map_"
    "review_then_mapped_mesh_grazing_angle_and_unreal_acceptance"
)
REQUIRED_ASSETS = {"Pathfinder", "Lighthouse", "RadarPost"}
REQUIRED_MAPS = {"Normal", "AO"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(root: Path, raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else root / path


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if (
            isinstance(value, dict)
            and isinstance(merged.get(key), dict)
        ):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_effective_contract(
    path: Path,
    root: Path,
) -> tuple[dict[str, Any], Path | None]:
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    base_raw = raw.get("extends_contract")
    if not isinstance(base_raw, str) or not base_raw:
        return raw, None
    base_path = resolve(root, base_raw)
    expected_hash = raw.get("extends_contract_sha256")
    if (
        not base_path.is_file()
        or not isinstance(expected_hash, str)
        or sha256_file(base_path) != expected_hash
    ):
        raise ValueError("extended contract hash mismatch")
    base = json.loads(base_path.read_text(encoding="utf-8-sig"))
    return deep_merge(base, raw), base_path


def verify_file_evidence(
    evidence: Any,
    root: Path,
    label: str,
    errors: list[str],
) -> bool:
    if not isinstance(evidence, dict):
        errors.append(f"{label}: evidence is not an object")
        return False
    raw = evidence.get("path")
    if not isinstance(raw, str) or not raw:
        errors.append(f"{label}: path is missing")
        return False
    path = resolve(root, raw)
    if not path.is_file():
        errors.append(f"{label}: missing file {path}")
        return False
    passed = (
        evidence.get("bytes") == path.stat().st_size
        and isinstance(evidence.get("bytes"), int)
        and evidence["bytes"] > 0
        and isinstance(evidence.get("sha256"), str)
        and evidence["sha256"].lower() == sha256_file(path)
    )
    if not passed:
        errors.append(f"{label}: byte/hash integrity mismatch")
    return passed


def png_header(path: Path) -> tuple[int, int, int, int] | None:
    try:
        with path.open("rb") as handle:
            if handle.read(8) != b"\x89PNG\r\n\x1a\n":
                return None
            length = struct.unpack(">I", handle.read(4))[0]
            if handle.read(4) != b"IHDR" or length != 13:
                return None
            width, height, bit_depth, color_type = struct.unpack(
                ">IIBB",
                handle.read(10),
            )
            return width, height, bit_depth, color_type
    except (OSError, struct.error):
        return None


def contract_assets(
    contract: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        item["id"]: item
        for item in contract.get("assets", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def contract_groups(
    asset: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        item["id"]: item
        for item in asset.get("groups", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def evaluate_source(
    contract: dict[str, Any],
    contract_path: Path,
    generator_path: Path,
    root: Path,
) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    errors: list[str] = []
    build_id = contract.get("build_id")
    revision = (
        build_id.rsplit("_", 1)[-1]
        if isinstance(build_id, str)
        else ""
    )
    checks["contract_schema"] = contract.get("schema") == CONTRACT_SCHEMA
    checks["build_id"] = build_id in {
        "BLD_M01_HERO_GROUPED_TOPOLOGY_003",
        "BLD_M01_HERO_GROUPED_TOPOLOGY_004",
        "BLD_M01_HERO_GROUPED_TOPOLOGY_005",
        "BLD_M01_HERO_GROUPED_TOPOLOGY_006",
        "BLD_M01_HERO_GROUPED_TOPOLOGY_007",
    }
    checks["supersedes_rejected_candidates"] = (
        isinstance(contract.get("supersedes_candidates"), list)
        and contract["supersedes_candidates"][:2]
        == ["BLD_M01_HERO_HILO_001", "BLD_M01_HERO_HILO_002"]
        and (
            revision == "003"
            or (
                "BLD_M01_HERO_GROUPED_TOPOLOGY_003"
                in contract["supersedes_candidates"]
                and (
                    revision not in {"005", "006", "007"}
                    or "BLD_M01_HERO_GROUPED_TOPOLOGY_004"
                    in contract["supersedes_candidates"]
                )
            )
        )
    )
    if revision == "006":
        checks["supersedes_005_failure"] = (
            "BLD_M01_HERO_GROUPED_TOPOLOGY_005"
            in contract["supersedes_candidates"]
            and contract.get("attempt_correction_basis")
            == "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_BAKE_005_FAILURE_REVIEW_2026-08-02.md"
        )
    if revision == "007":
        checks["supersedes_006_failure"] = (
            all(
                f"BLD_M01_HERO_GROUPED_TOPOLOGY_{item}"
                in contract["supersedes_candidates"]
                for item in ("003", "004", "005", "006")
            )
            and contract.get("attempt_correction_basis")
            == "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_BAKE_006_FAILURE_REVIEW_2026-08-02.md"
        )
    checks["correction_basis"] = (
        contract.get("correction_basis")
        == "Docs/AAA_Review/M01_HERO_HIGH_TO_LOW_BAKE_CORRECTIVE_002_VISUAL_REVIEW_2026-08-02.md"
    )
    checks["promotion_fail_closed"] = contract.get("promotion") == PROMOTION

    source_raw = contract.get("source_blend")
    source_path = (
        resolve(root, source_raw)
        if isinstance(source_raw, str) and source_raw
        else None
    )
    checks["source_exists"] = bool(
        source_path and source_path.is_file() and source_path.stat().st_size > 0
    )
    checks["source_hash_bound"] = bool(
        checks["source_exists"]
        and isinstance(contract.get("source_sha256"), str)
        and len(contract["source_sha256"]) == 64
        and sha256_file(source_path) == contract["source_sha256"]
    )
    if isinstance(contract.get("extends_contract"), str):
        base_path = resolve(root, contract["extends_contract"])
        checks["extended_contract_hash_bound"] = (
            base_path.is_file()
            and contract.get("extends_contract_sha256")
            == sha256_file(base_path)
        )
    if revision == "007":
        classification_raw = contract.get("classification_report")
        classification_path = (
            resolve(root, classification_raw)
            if isinstance(classification_raw, str)
            else None
        )
        checks["classification_report_hash_bound"] = bool(
            classification_path
            and classification_path.is_file()
            and contract.get("classification_report_sha256")
            == sha256_file(classification_path)
        )
        try:
            classification = json.loads(
                classification_path.read_text(encoding="utf-8-sig")
            )
        except (AttributeError, OSError, json.JSONDecodeError):
            classification = {}
        checks["classification_report_scope"] = (
            classification.get("source_build_id")
            == "BLD_M01_HERO_GROUPED_TOPOLOGY_006"
            and classification.get("target_build_id")
            == "BLD_M01_HERO_GROUPED_TOPOLOGY_007"
            and classification.get("analysis_mode")
            == "offline_glb_only_no_blender_no_unreal"
            and classification.get("group_count") == 12
            and classification.get("gate") == "PASS"
        )

    bake = contract.get("bake_contract", {})
    checks["bake_contract"] = (
        isinstance(bake, dict)
        and bake.get("engine") == "CYCLES"
        and bake.get("device") == "CPU"
        and bake.get("selected_to_active") is True
        and bake.get("group_isolation_required") is True
        and bake.get("explicit_cage_required") is True
        and bake.get("normal_space") == "TANGENT"
        and bake.get("tangent_basis") == "MikkTSpace"
        and bake.get("normal_convention") == "OpenGL"
        and bake.get("uv_layer") == "UV_M01_GROUPED_0"
        and isinstance(bake.get("resolution"), int)
        and bake["resolution"] >= 2048
        and isinstance(bake.get("margin_pixels"), int)
        and bake["margin_pixels"] >= 32
        and isinstance(bake.get("samples"), int)
        and bake["samples"] >= 16
        and bake.get("preserve_neutral_background") is True
    )
    maps = bake.get("maps", []) if isinstance(bake, dict) else []
    checks["map_contract"] = (
        isinstance(maps, list)
        and {item.get("type") for item in maps} == REQUIRED_MAPS
        and all(
            item.get("color_space") == "Non-Color"
            and isinstance(item.get("neutral_background"), list)
            and len(item["neutral_background"]) == 3
            and isinstance(item.get("minimum_varied_rgb_channels"), int)
            and (
                revision not in {"005", "006", "007"}
                or (
                    item.get("bake_mode")
                    in {
                        "selected_to_active_tangent_normal",
                        "direct_low_self_occlusion",
                        "governed_per_group_direct_or_dedicated_bounded_occluder",
                    }
                    and isinstance(
                        item.get("maximum_black_pixel_fraction"),
                        (int, float),
                    )
                )
            )
            for item in maps
        )
    )

    topology = contract.get("topology_contract", {})
    uv_contract = topology.get("uv_authoring", {})
    smoothing = topology.get("smoothing", {})
    cage = topology.get("cage", {})
    expected_uv_method = (
        "semantic_group_connected_source_charts_repacked_and_seams_authored"
        if revision in {"005", "006", "007"}
        else "semantic_group_explicit_face_islands_then_angle_based_unwrap"
    )
    checks["topology_contract"] = (
        topology.get("partition_method")
        == "exact_disjoint_source_material_partition"
        and topology.get("source_face_coverage_required") is True
        and topology.get("orphan_vertices_allowed") is False
        and topology.get("duplicate_material_membership_allowed") is False
        and uv_contract.get("method") == expected_uv_method
        and uv_contract.get("smart_project_forbidden") is True
        and uv_contract.get("average_island_scale") is True
        and uv_contract.get("pack_islands") is True
        and smoothing.get("polygon_smoothing") is True
        and smoothing.get("sharp_edges_follow_group_hard_angle") is True
        and cage.get("topology_must_match_low") is True
        and cage.get("normal_offset_only") is True
    )
    if revision in {"006", "007"}:
        face_normals = topology.get("face_normal_authoring", {})
        checks["face_normal_contract"] = (
            face_normals.get("method")
            == "bmesh_recalc_face_normals_per_partition"
            and (
                face_normals.get("low_before_smoothing") is True
                or face_normals.get(
                    "low_after_topology_repair_before_smoothing"
                )
                is True
            )
            and face_normals.get("high_after_bevel_or_subdivision") is True
            and face_normals.get("zero_normal_faces_allowed") is False
        )
    if revision == "007":
        repair = contract.get("topology_repair_contract", {})
        policies = repair.get("group_policies", {})
        direct = [
            item
            for item in policies.values()
            if item.get("ao_policy") == "direct_low_self_occlusion"
        ]
        dedicated = [
            item
            for item in policies.values()
            if item.get("ao_policy")
            == "selected_to_active_from_dedicated_bounded_ao_occluder"
        ]
        occluder_names = [
            item.get("ao_occluder_object") for item in dedicated
        ]
        checks["topology_repair_contract"] = (
            repair.get("analysis_mode")
            == "offline_glb_only_no_blender_no_unreal"
            and repair.get("zero_area_faces_after_repair") == 0
            and repair.get("nonmanifold_edges_after_repair") == 0
            and repair.get("render_visibility_isolation_required") is True
            and len(policies) == 12
            and len(direct) == repair.get("direct_low_ao_count") == 3
            and len(dedicated)
            == repair.get("dedicated_ao_occluder_count")
            == 9
            and len(occluder_names) == len(set(occluder_names))
            and all(
                isinstance(item, str) and item.startswith("AOCC_M01_")
                for item in occluder_names
            )
            and policies.get("Pathfinder/AccessPanels", {}).get(
                "remove_zero_area_faces"
            )
            is True
            and policies.get("Pathfinder/PaintShell", {}).get(
                "split_nonmanifold_edges"
            )
            is True
        )

    assets = contract_assets(contract)
    checks["asset_scope"] = set(assets) == REQUIRED_ASSETS
    total_groups = 0
    all_object_names: list[str] = []
    all_prefixes: list[str] = []
    group_contracts_valid = checks["asset_scope"]
    for asset in assets.values():
        groups = contract_groups(asset)
        total_groups += len(groups)
        required_materials = asset.get("required_source_materials")
        memberships = [
            material
            for group in groups.values()
            for material in group.get("materials", [])
        ]
        group_contracts_valid &= (
            len(groups) == 4
            and isinstance(required_materials, list)
            and len(required_materials) == len(set(required_materials))
            and set(memberships) == set(required_materials)
            and len(memberships) == len(set(memberships))
        )
        for group in groups.values():
            names = [
                group.get("low_object"),
                group.get("high_object"),
                group.get("cage_object"),
            ]
            all_object_names.extend(
                name for name in names if isinstance(name, str)
            )
            all_prefixes.append(group.get("texture_prefix"))
            group_contracts_valid &= (
                all(isinstance(name, str) and name for name in names)
                and len(set(names)) == 3
                and isinstance(group.get("materials"), list)
                and bool(group["materials"])
                and isinstance(
                    group.get("hard_edge_angle_degrees"),
                    (int, float),
                )
                and 30.0 <= float(group["hard_edge_angle_degrees"]) <= 70.0
                and isinstance(group.get("bevel_width_m"), (int, float))
                and 0.0005 <= float(group["bevel_width_m"]) <= 0.02
                and isinstance(
                    group.get("cage_extrusion_m"),
                    (int, float),
                )
                and 0.001 <= float(group["cage_extrusion_m"]) <= 0.03
                and isinstance(
                    group.get("max_ray_distance_m"),
                    (int, float),
                )
                and float(group["cage_extrusion_m"])
                < float(group["max_ray_distance_m"])
                <= 0.04
            )
    checks["twelve_group_contracts"] = (
        total_groups == 12 and bool(group_contracts_valid)
    )
    checks["globally_unique_object_names"] = (
        len(all_object_names) == 36
        and len(all_object_names) == len(set(all_object_names))
    )
    checks["globally_unique_texture_prefixes"] = (
        len(all_prefixes) == 12
        and len(all_prefixes) == len(set(all_prefixes))
        and all(isinstance(item, str) and item for item in all_prefixes)
    )

    outputs = contract.get("outputs", {})
    checks["isolated_revision_outputs"] = (
        isinstance(outputs, dict)
        and set(outputs)
        == {
            "master_blend",
            "low_glb",
            "texture_root",
            "manifest",
            "report",
        }
        and all(
            isinstance(value, str)
            and (
                revision in value
                or f"HeroGroupedTopology_{revision}" in value
            )
            for value in outputs.values()
        )
    )

    try:
        source_text = generator_path.read_text(encoding="utf-8-sig")
        ast.parse(source_text)
        checks["generator_parses"] = True
    except (OSError, SyntaxError) as exc:
        source_text = ""
        checks["generator_parses"] = False
        errors.append(f"generator parse failed: {exc}")
    required_tokens = {
        "material_partition": "def extract_material_group(",
        "source_partition_validation": "def validate_source_partition(",
        "authored_uv": "def author_group_uv(",
        "smart_project_absent": "bpy.ops.uv.smart_project" ,
        "island_scale": "bpy.ops.uv.average_islands_scale()",
        "island_pack": "bpy.ops.uv.pack_islands(",
        "authored_smoothing": "def author_smoothing(",
        "separate_high": "apply_high_bevel(",
        "normal_offset_cage": "def make_normal_offset_cage(",
        "selected_to_active": "bake.use_selected_to_active = True",
        "explicit_cage": "bake.cage_object = cage",
        "neutral_background": "scene.render.bake.use_clear = False",
        "native_master": "bpy.ops.wm.save_as_mainfile(",
        "low_glb": "export_low_glb(all_low_objects",
        "fingerprint": "package_fingerprint_sha256",
    }
    if revision in {"005", "006", "007"}:
        required_tokens.update(
            {
                "connected_chart_seed": 'obj.data.uv_layers.get("UV_M01_AAA_0")',
                "uv_discontinuity_seams": "def mark_uv_chart_seams(",
                "high_density_fallback": "def ensure_high_density(",
                "direct_low_ao": 'if map_type == "AO":',
                "map_black_limits": "maximum_black_pixel_fraction",
            }
        )
        if revision == "006":
            required_tokens["component_face_normals"] = (
                "def author_consistent_face_normals("
            )
        if revision == "007":
            required_tokens.update(
                {
                    "component_face_normals": "def author_consistent_face_normals(",
                    "topology_defect_counts": "def topology_defect_counts(",
                    "partition_topology_repair": "def repair_partition_topology(",
                    "render_visibility_isolation": "def isolate_render_meshes(",
                    "zero_area_face_repair": '"remove_zero_area_faces"',
                    "nonmanifold_edge_split": '"split_nonmanifold_edges"',
                    "dedicated_ao_occluder": "dedicated_bounded_ao_occluder",
                }
            )
    else:
        required_tokens["angle_unwrap"] = "bpy.ops.uv.unwrap("
    for name, token in required_tokens.items():
        if name == "smart_project_absent":
            checks[f"generator_{name}"] = token not in source_text
        else:
            checks[f"generator_{name}"] = token in source_text

    checks["contract_path_is_current"] = contract_path.is_file()
    for check, passed in checks.items():
        if not passed:
            errors.append(f"source check failed: {check}")
    return {
        "gate": "PASS" if not errors else "FAIL",
        "checks": checks,
        "errors": errors,
        "contract_sha256": (
            sha256_file(contract_path) if contract_path.is_file() else None
        ),
        "generator_sha256": (
            sha256_file(generator_path) if generator_path.is_file() else None
        ),
        "source_sha256": (
            sha256_file(source_path)
            if source_path and source_path.is_file()
            else None
        ),
    }


def evaluate_artifacts(
    contract: dict[str, Any],
    manifest: dict[str, Any],
    root: Path,
    contract_path: Path,
    generator_path: Path,
) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    errors: list[str] = []
    build_id = contract.get("build_id")
    checks["manifest_schema"] = manifest.get("schema") == MANIFEST_SCHEMA
    checks["build_id"] = manifest.get("build_id") == build_id
    checks["promotion_fail_closed"] = manifest.get("promotion") == PROMOTION
    checks["source_integrity"] = verify_file_evidence(
        manifest.get("source"),
        root,
        "source",
        errors,
    )
    checks["contract_integrity"] = verify_file_evidence(
        manifest.get("contract"),
        root,
        "contract",
        errors,
    ) and (
        Path(manifest["contract"]["path"]).resolve()
        == contract_path.resolve()
    )
    if isinstance(contract.get("extends_contract"), str):
        base_path = resolve(root, contract["extends_contract"])
        checks["base_contract_integrity"] = verify_file_evidence(
            manifest.get("base_contract"),
            root,
            "base_contract",
            errors,
        ) and (
            Path(manifest["base_contract"]["path"]).resolve()
            == base_path.resolve()
        )
    checks["generator_integrity"] = verify_file_evidence(
        manifest.get("generator"),
        root,
        "generator",
        errors,
    ) and (
        Path(manifest["generator"]["path"]).resolve()
        == generator_path.resolve()
    )
    if build_id == "BLD_M01_HERO_GROUPED_TOPOLOGY_007":
        classification_path = resolve(
            root,
            contract["classification_report"],
        )
        checks["classification_report_integrity"] = verify_file_evidence(
            manifest.get("classification_report"),
            root,
            "classification_report",
            errors,
        ) and (
            Path(manifest["classification_report"]["path"]).resolve()
            == classification_path.resolve()
        )
    checks["bake_contract_matches"] = (
        manifest.get("bake_contract") == contract.get("bake_contract")
    )
    checks["topology_contract_matches"] = (
        manifest.get("topology_contract")
        == contract.get("topology_contract")
    )
    if build_id == "BLD_M01_HERO_GROUPED_TOPOLOGY_007":
        checks["topology_repair_contract_matches"] = (
            manifest.get("topology_repair_contract")
            == contract.get("topology_repair_contract")
        )

    outputs = manifest.get("outputs", {})
    checks["outputs_shape"] = (
        isinstance(outputs, dict)
        and set(outputs) == {"master_blend", "low_glb"}
    )
    output_integrity = checks["outputs_shape"]
    for label in ("master_blend", "low_glb"):
        output_integrity &= verify_file_evidence(
            outputs.get(label),
            root,
            f"outputs.{label}",
            errors,
        )
    checks["output_integrity"] = bool(output_integrity)

    asset_specs = contract_assets(contract)
    asset_records = {
        item["id"]: item
        for item in manifest.get("assets", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    checks["asset_scope"] = set(asset_records) == REQUIRED_ASSETS
    map_hashes: list[str] = []
    group_result: dict[str, dict[str, bool]] = {}
    total_groups = 0
    for asset_id in sorted(REQUIRED_ASSETS):
        asset_spec = asset_specs.get(asset_id, {})
        record = asset_records.get(asset_id, {})
        expected_groups = contract_groups(asset_spec)
        actual_groups = {
            item["id"]: item
            for item in record.get("groups", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        asset_key = f"{asset_id}.__asset__"
        group_result[asset_key] = {
            "source_object": (
                record.get("source_object") == asset_spec.get("source_object")
            ),
            "group_scope": (
                set(actual_groups) == set(expected_groups)
                and len(actual_groups) == 4
            ),
            "face_coverage": (
                isinstance(record.get("source_face_count"), int)
                and record["source_face_count"] > 0
                and record.get("retained_group_face_count")
                == record["source_face_count"]
                and sum(
                    int(value)
                    for value in record.get(
                        "source_material_face_counts",
                        {},
                    ).values()
                )
                == record["source_face_count"]
            ),
        }
        for passed_name, passed in group_result[asset_key].items():
            if not passed:
                errors.append(f"{asset_id}: artifact check failed: {passed_name}")

        for group_id, group_spec in expected_groups.items():
            total_groups += 1
            item = actual_groups.get(group_id, {})
            low = item.get("low", {})
            high = item.get("high", {})
            cage = item.get("cage", {})
            uv = item.get("uv", {})
            smoothing = item.get("low_smoothing", {})
            group_key = f"{asset_id}/{group_id}"
            repair_policy = contract.get(
                "topology_repair_contract",
                {},
            ).get("group_policies", {}).get(group_key, {})
            result: dict[str, bool] = {}
            result["materials"] = (
                item.get("materials") == group_spec.get("materials")
                and set(low.get("material_face_counts", {}))
                == set(group_spec.get("materials", []))
            )
            result["object_names"] = (
                low.get("object") == group_spec.get("low_object")
                and high.get("object") == group_spec.get("high_object")
                and cage.get("object") == group_spec.get("cage_object")
            )
            result["separate_mesh_datablocks"] = (
                isinstance(low.get("mesh_datablock"), str)
                and isinstance(high.get("mesh_datablock"), str)
                and isinstance(cage.get("mesh_datablock"), str)
                and len(
                    {
                        low["mesh_datablock"],
                        high["mesh_datablock"],
                        cage["mesh_datablock"],
                    }
                )
                == 3
            )
            result["production_low_topology"] = (
                isinstance(low.get("vertices"), int)
                and low["vertices"] > 0
                and isinstance(low.get("faces"), int)
                and low["faces"] > 0
                and low.get("orphan_vertices") == 0
                and uv.get("layer") == contract["bake_contract"]["uv_layer"]
                and uv.get("method")
                == contract["topology_contract"]["uv_authoring"]["method"]
                and uv.get("smart_project_used") is False
                and uv.get("finite") is True
                and isinstance(uv.get("authored_seam_edges"), int)
                and uv["authored_seam_edges"] >= 1
                and min(uv.get("bounds_min", [-1])) >= -1.0e-5
                and max(uv.get("bounds_max", [2])) <= 1.0 + 1.0e-5
            )
            result["authored_smoothing"] = (
                smoothing.get("polygon_smoothing") is True
                and smoothing.get("hard_edge_angle_degrees")
                == group_spec.get("hard_edge_angle_degrees")
                and isinstance(smoothing.get("sharp_edges"), int)
                and smoothing["sharp_edges"]
                >= int(
                    contract["topology_contract"]["smoothing"].get(
                        "minimum_sharp_edges",
                        1,
                    )
                )
                and smoothing.get("smooth_polygons")
                == smoothing.get("polygon_count")
                == low.get("faces")
            )
            ratio = item.get("high_to_low_vertex_ratio")
            result["high_source"] = (
                isinstance(high.get("vertices"), int)
                and high["vertices"] > low.get("vertices", 10**12)
                and isinstance(ratio, (int, float))
                and abs(
                    float(ratio)
                    - high["vertices"] / low["vertices"]
                )
                <= 1.0e-5
                and float(ratio)
                >= contract["topology_contract"]["high_source"][
                    "minimum_high_to_low_vertex_ratio"
                ]
                and (
                    contract.get("build_id")
                    not in {
                        "BLD_M01_HERO_GROUPED_TOPOLOGY_005",
                        "BLD_M01_HERO_GROUPED_TOPOLOGY_006",
                        "BLD_M01_HERO_GROUPED_TOPOLOGY_007",
                    }
                    or item.get("high_density_method")
                    in {
                        "three_segment_angle_bevel",
                        "three_segment_angle_bevel_plus_linear_edge_subdivision",
                    }
                )
            )
            result["cage_topology"] = (
                item.get("cage_zero_normal_vertices") == 0
                and cage.get("vertices") == low.get("vertices")
                and cage.get("edges") == low.get("edges")
                and cage.get("faces") == low.get("faces")
            )
            if (
                contract.get("build_id")
                in {
                    "BLD_M01_HERO_GROUPED_TOPOLOGY_006",
                    "BLD_M01_HERO_GROUPED_TOPOLOGY_007",
                }
            ):
                low_orientation = item.get("low_face_orientation", {})
                high_orientation = item.get("high_face_orientation", {})
                result["component_face_normals"] = (
                    low_orientation.get("method")
                    == "bmesh_recalc_face_normals_per_partition"
                    and low_orientation.get("faces") == low.get("faces")
                    and low_orientation.get("zero_normal_faces") == 0
                    and low_orientation.get("component_consistent") is True
                    and high_orientation.get("method")
                    == "bmesh_recalc_face_normals_per_partition"
                    and high_orientation.get("faces") == high.get("faces")
                    and high_orientation.get("zero_normal_faces") == 0
                    and high_orientation.get("component_consistent") is True
                )
            if build_id == "BLD_M01_HERO_GROUPED_TOPOLOGY_007":
                topology_repair = item.get("topology_repair", {})
                result["topology_repair"] = (
                    topology_repair.get("policy") == repair_policy
                    and topology_repair.get("after", {}).get(
                        "zero_area_faces"
                    )
                    == 0
                    and topology_repair.get("after", {}).get(
                        "nonmanifold_edges"
                    )
                    == 0
                    and (
                        not repair_policy.get("remove_zero_area_faces")
                        or topology_repair.get("removed_zero_area_faces", 0)
                        > 0
                    )
                    and (
                        not repair_policy.get("split_nonmanifold_edges")
                        or topology_repair.get(
                            "split_nonmanifold_edges",
                            0,
                        )
                        > 0
                    )
                )
                ao_occluder = item.get("ao_occluder")
                expected_ao_policy = repair_policy.get("ao_policy")
                result["ao_policy"] = item.get("ao_policy") == expected_ao_policy
                result["ao_occluder"] = (
                    ao_occluder is None
                    if expected_ao_policy == "direct_low_self_occlusion"
                    else (
                        isinstance(ao_occluder, dict)
                        and ao_occluder.get("object")
                        == repair_policy.get("ao_occluder_object")
                        and ao_occluder.get("mesh_datablock")
                        not in {
                            low.get("mesh_datablock"),
                            high.get("mesh_datablock"),
                            cage.get("mesh_datablock"),
                        }
                        and ao_occluder.get("faces") == high.get("faces")
                    )
                )

            maps = {
                map_item["type"]: map_item
                for map_item in item.get("maps", [])
                if isinstance(map_item, dict)
                and isinstance(map_item.get("type"), str)
            }
            result["map_scope"] = set(maps) == REQUIRED_MAPS
            map_integrity = result["map_scope"]
            for map_spec in contract["bake_contract"]["maps"]:
                map_type = map_spec["type"]
                map_item = maps.get(map_type, {})
                integrity = verify_file_evidence(
                    map_item,
                    root,
                    f"{asset_id}/{group_id}/{map_type}",
                    errors,
                )
                if integrity:
                    path = resolve(root, map_item["path"])
                    header = png_header(path)
                    integrity &= (
                        header is not None
                        and header[0]
                        == contract["bake_contract"]["resolution"]
                        and header[1]
                        == contract["bake_contract"]["resolution"]
                        and header[2] == 8
                        and header[3] == 2
                    )
                    map_hashes.append(map_item["sha256"].lower())
                projection = map_item.get("projection", {})
                diagnostics = map_item.get("diagnostics", {})
                expected_mode = map_spec.get(
                    "bake_mode",
                    "selected_to_active_tangent_normal",
                )
                if (
                    build_id == "BLD_M01_HERO_GROUPED_TOPOLOGY_007"
                    and map_type == "AO"
                ):
                    expected_mode = repair_policy.get("ao_policy")
                expected_projection = (
                    {
                        "selected_to_active": False,
                        "cage_object": None,
                        "cage_method": None,
                        "cage_extrusion_m": 0.0,
                        "max_ray_distance_m": 0.0,
                    }
                    if expected_mode == "direct_low_self_occlusion"
                    else {
                        "selected_to_active": True,
                        "cage_object": group_spec.get("cage_object"),
                        "cage_method": "vertex_normal_offset",
                        "cage_extrusion_m": group_spec.get(
                            "cage_extrusion_m"
                        ),
                        "max_ray_distance_m": group_spec.get(
                            "max_ray_distance_m"
                        ),
                    }
                )
                if build_id == "BLD_M01_HERO_GROUPED_TOPOLOGY_007":
                    expected_projection["render_visibility_isolated"] = True
                    if (
                        map_type == "AO"
                        and expected_mode
                        == "selected_to_active_from_dedicated_bounded_ao_occluder"
                    ):
                        expected_projection["ao_occluder_object"] = (
                            repair_policy.get("ao_occluder_object")
                        )
                integrity &= (
                    map_item.get("width")
                    == contract["bake_contract"]["resolution"]
                    and map_item.get("height")
                    == contract["bake_contract"]["resolution"]
                    and map_item.get("channels") == 3
                    and map_item.get("color_space") == "Non-Color"
                    and map_item.get("neutral_background")
                    == map_spec.get("neutral_background")
                    and isinstance(
                        map_item.get("varied_rgb_channels"),
                        int,
                    )
                    and map_item["varied_rgb_channels"]
                    >= map_spec["minimum_varied_rgb_channels"]
                    and projection.get("isolated_group") is True
                    and projection.get("mode") == expected_mode
                    and all(
                        projection.get(key) == value
                        for key, value in expected_projection.items()
                    )
                    and isinstance(
                        diagnostics.get("neutral_background_fraction"),
                        (int, float),
                    )
                    and isinstance(
                        diagnostics.get("black_pixel_fraction"),
                        (int, float),
                    )
                    and diagnostics["black_pixel_fraction"]
                    <= float(
                        map_spec.get(
                            "maximum_black_pixel_fraction",
                            0.0001
                            if map_type == "Normal"
                            else 1.0,
                        )
                    )
                )
                map_integrity &= integrity
            result["map_integrity"] = bool(map_integrity)
            group_result[f"{asset_id}.{group_id}"] = result
            for check_name, passed in result.items():
                if not passed:
                    errors.append(
                        f"{asset_id}/{group_id}: artifact check failed: "
                        f"{check_name}"
                    )

    checks["twelve_groups"] = (
        total_groups == 12
        and manifest.get("group_count") == 12
    )
    checks["twenty_four_maps"] = (
        len(map_hashes) == 24 and manifest.get("map_count") == 24
    )
    expected_fingerprint = hashlib.sha256(
        "\n".join(sorted(map_hashes)).encode("ascii")
    ).hexdigest()
    checks["package_fingerprint"] = (
        len(map_hashes) == 24
        and manifest.get("package_fingerprint_sha256")
        == expected_fingerprint
    )
    validation = manifest.get("validation", {})
    checks["author_validation"] = (
        validation.get("pass") is True
        and validation.get("failures") == []
    )

    for check, passed in checks.items():
        if not passed:
            errors.append(f"artifact check failed: {check}")
    return {
        "gate": "PASS" if not errors else "FAIL",
        "checks": checks,
        "group_results": group_result,
        "computed_package_fingerprint_sha256": expected_fingerprint,
        "errors": errors,
    }


def build_report(
    contract: dict[str, Any],
    contract_path: Path,
    generator_path: Path,
    manifest_path: Path,
    root: Path,
) -> dict[str, Any]:
    source = evaluate_source(
        contract,
        contract_path,
        generator_path,
        root,
    )
    if manifest_path.is_file():
        try:
            manifest = json.loads(
                manifest_path.read_text(encoding="utf-8-sig")
            )
            artifacts = evaluate_artifacts(
                contract,
                manifest,
                root,
                contract_path,
                generator_path,
            )
        except (OSError, json.JSONDecodeError) as exc:
            artifacts = {
                "gate": "FAIL",
                "checks": {},
                "group_results": {},
                "errors": [f"manifest read failed: {exc}"],
            }
    else:
        artifacts = {
            "gate": "NOT_RUN",
            "checks": {},
            "group_results": {},
            "errors": [],
            "reason": (
                "The exclusive Blender lane has not yet authored "
                f"{contract.get('build_id')}."
            ),
        }
    if source["gate"] == "PASS" and artifacts["gate"] == "PASS":
        gate = "PASS"
        terminal = (
            "GROUPED_ARTIFACTS_VERIFIED_AWAITING_DIRECT_MAP_REVIEW"
        )
    elif source["gate"] == "PASS" and artifacts["gate"] == "NOT_RUN":
        gate = "PASS_WITH_GAPS"
        terminal = "GROUPED_SOURCE_READY_BLENDER_NOT_RUN"
    else:
        gate = "FAIL"
        terminal = "GROUPED_SOURCE_OR_ARTIFACT_VERIFICATION_FAILED"
    return {
        "schema": REPORT_SCHEMA,
        "build_id": contract.get("build_id"),
        "gate": gate,
        "terminal_state": terminal,
        "source_gate": source,
        "artifact_gate": artifacts,
        "direct_original_resolution_map_review": "NOT_RUN",
        "mapped_mesh_grazing_angle_review": "NOT_RUN",
        "unreal_acceptance": "NOT_RUN",
        "p3_4_closed": False,
        "promotion": PROMOTION,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify a Mission 01 grouped topology bake build."
    )
    parser.add_argument("--root", type=Path, default=ROOT_DEFAULT)
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT_DEFAULT
        / "Docs"
        / "AAA_Review"
        / "M01_HERO_GROUPED_TOPOLOGY_BAKE_003_CONTRACT.json",
    )
    parser.add_argument(
        "--generator",
        type=Path,
        default=ROOT_DEFAULT
        / "Scripts"
        / "blender_m01_hero_grouped_topology_bake.py",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT_DEFAULT
        / "Saved"
        / "Reports"
        / "M01_HERO_GROUPED_TOPOLOGY_BAKE_MANIFEST_003.json",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-artifacts", action="store_true")
    args = parser.parse_args()
    try:
        contract, _ = load_effective_contract(
            args.contract,
            args.root.resolve(),
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "schema": REPORT_SCHEMA,
                    "gate": "FAIL",
                    "terminal_state": "CONTRACT_LOAD_FAILED",
                    "errors": [str(exc)],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    report = build_report(
        contract,
        args.contract,
        args.generator,
        args.manifest,
        args.root.resolve(),
    )
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    if report["gate"] == "FAIL":
        return 1
    if args.require_artifacts and report["artifact_gate"]["gate"] != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
