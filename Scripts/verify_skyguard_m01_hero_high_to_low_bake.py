from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Any


CONTRACT_SCHEMA = "skyguard.m01.hero-high-to-low-bake.contract.v1"
MANIFEST_SCHEMA = "skyguard.m01.hero-high-to-low-bake.manifest.v1"
REPORT_SCHEMA = "skyguard.m01.hero-high-to-low-bake.readiness.v1"
BUILD_ID = "BLD_M01_HERO_HILO_001"
PROMOTION = (
    "high_to_low_bake_candidate_requires_blender_execution_artifact_"
    "verification_and_unreal_visual_acceptance"
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


def verify_file_evidence(
    evidence: Any,
    root: Path,
    label: str,
    errors: list[str],
) -> bool:
    if not isinstance(evidence, dict):
        errors.append(f"{label}: evidence must be an object")
        return False
    raw = evidence.get("path")
    expected_bytes = evidence.get("bytes")
    expected_sha = evidence.get("sha256")
    if not isinstance(raw, str) or not raw:
        errors.append(f"{label}: path is missing")
        return False
    path = resolve(root, raw)
    if not path.is_file():
        errors.append(f"{label}: file does not exist: {path}")
        return False
    actual_bytes = path.stat().st_size
    actual_sha = sha256_file(path)
    passed = (
        isinstance(expected_bytes, int)
        and expected_bytes > 0
        and expected_bytes == actual_bytes
        and isinstance(expected_sha, str)
        and len(expected_sha) == 64
        and expected_sha.lower() == actual_sha
    )
    if not passed:
        errors.append(f"{label}: byte/hash integrity mismatch")
    return passed


def _contract_assets(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    assets = contract.get("assets")
    if not isinstance(assets, list):
        return {}
    result = {}
    for asset in assets:
        if isinstance(asset, dict) and isinstance(asset.get("id"), str):
            result[asset["id"]] = asset
    return result


def evaluate_source(
    contract: dict[str, Any],
    generator_path: Path,
    root: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    checks: dict[str, bool] = {}

    checks["contract_schema"] = contract.get("schema") == CONTRACT_SCHEMA
    checks["build_id"] = contract.get("build_id") == BUILD_ID
    checks["promotion_is_candidate_only"] = contract.get("promotion") == PROMOTION

    source_raw = contract.get("source_blend")
    source_path = (
        resolve(root, source_raw)
        if isinstance(source_raw, str) and source_raw
        else None
    )
    checks["source_blend_exists"] = bool(
        source_path and source_path.is_file() and source_path.stat().st_size > 0
    )

    bake = contract.get("bake_contract")
    checks["bake_contract_shape"] = (
        isinstance(bake, dict)
        and bake.get("engine") == "CYCLES"
        and bake.get("device") == "CPU"
        and bake.get("selected_to_active") is True
        and bake.get("explicit_cage_required") is True
        and bake.get("normal_space") == "TANGENT"
        and bake.get("tangent_basis") == "MikkTSpace"
        and bake.get("normal_convention") == "OpenGL"
        and bake.get("uv_layer") == "UV_M01_AAA_0"
        and isinstance(bake.get("resolution"), int)
        and bake["resolution"] >= 2048
        and isinstance(bake.get("margin_pixels"), int)
        and bake["margin_pixels"] >= 16
        and isinstance(bake.get("samples"), int)
        and bake["samples"] >= 8
    )
    map_specs = bake.get("maps") if isinstance(bake, dict) else None
    checks["required_map_contract"] = (
        isinstance(map_specs, list)
        and {item.get("type") for item in map_specs if isinstance(item, dict)}
        == REQUIRED_MAPS
        and all(
            isinstance(item, dict)
            and item.get("color_space") == "Non-Color"
            and isinstance(item.get("minimum_varied_rgb_channels"), int)
            and item["minimum_varied_rgb_channels"] >= 1
            for item in map_specs
        )
    )

    assets = _contract_assets(contract)
    checks["asset_scope"] = set(assets) == REQUIRED_ASSETS and len(assets) == 3
    object_names: list[str] = []
    asset_contract_valid = checks["asset_scope"]
    for asset_id, spec in assets.items():
        names = [
            spec.get("source_object"),
            spec.get("low_object"),
            spec.get("high_object"),
            spec.get("cage_object"),
        ]
        object_names.extend(
            name for name in names if isinstance(name, str) and name
        )
        asset_contract_valid &= (
            all(isinstance(name, str) and bool(name) for name in names)
            and len(set(names)) == 4
            and isinstance(spec.get("cage_extrusion_m"), (int, float))
            and 0.001 <= float(spec["cage_extrusion_m"]) <= 0.05
            and isinstance(spec.get("max_ray_distance_m"), (int, float))
            and float(spec["cage_extrusion_m"])
            <= float(spec["max_ray_distance_m"])
            <= 0.10
            and isinstance(
                spec.get("minimum_high_to_low_vertex_ratio"), (int, float)
            )
            and float(spec["minimum_high_to_low_vertex_ratio"]) > 1.0
            and isinstance(
                spec.get("maximum_high_to_low_bounds_delta_m"), (int, float)
            )
            and 0.0
            < float(spec["maximum_high_to_low_bounds_delta_m"])
            <= float(spec["max_ray_distance_m"]) + 0.02
            and isinstance(spec.get("required_detail_groups"), list)
            and len(spec["required_detail_groups"]) >= 4
            and len(spec["required_detail_groups"])
            == len(set(spec["required_detail_groups"]))
        )
    checks["asset_projection_contracts"] = bool(asset_contract_valid)
    checks["globally_unique_object_names"] = (
        len(object_names) == 12 and len(object_names) == len(set(object_names))
    )

    outputs = contract.get("outputs")
    checks["isolated_outputs"] = (
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
            isinstance(raw, str)
            and bool(raw)
            and (
                "HeroHighToLow_001" in raw
                or "M01_HERO_HIGH_TO_LOW_BAKE_" in raw
            )
            for raw in outputs.values()
        )
    )

    source_text = ""
    try:
        source_text = generator_path.read_text(encoding="utf-8-sig")
        ast.parse(source_text)
        checks["generator_python_parses"] = True
    except (OSError, SyntaxError) as exc:
        checks["generator_python_parses"] = False
        errors.append(f"generator parse failed: {exc}")

    required_tokens = {
        "separate_mesh_copy": "obj.data = source.data.copy()",
        "explicit_cage_geometry": "bpy.ops.transform.shrink_fatten(",
        "selected_to_active": "bake.use_selected_to_active = True",
        "cage_enabled": "bake.use_cage = True",
        "named_cage": "bake.cage_object = cage",
        "bounded_ray_distance": "bake.max_ray_distance",
        "tangent_normal_setting": "scene.render.bake.normal_space",
        "actual_bake_operator": "bpy.ops.object.bake(type=map_type.upper())",
        "native_master_output": "bpy.ops.wm.save_as_mainfile(",
        "low_only_export": "export_low_glb(low_objects",
        "texture_hashing": "file_evidence(output)",
        "package_fingerprint": "package_fingerprint_sha256",
    }
    for check, token in required_tokens.items():
        checks[f"generator_{check}"] = token in source_text
    checks["asset_specific_detail_builders"] = all(
        token in source_text
        for token in (
            "def pathfinder_details(",
            "def lighthouse_details(",
            "def radar_details(",
        )
    )
    checks["no_same_mesh_claim"] = (
        "same_mesh_tangent_space_with_authored_shader_bump" not in source_text
    )

    for check, passed in checks.items():
        if not passed:
            errors.append(f"source check failed: {check}")
    return {
        "gate": "PASS" if not errors else "FAIL",
        "checks": checks,
        "errors": errors,
        "contract_sha256": (
            sha256_file(
                root
                / "Docs"
                / "AAA_Review"
                / "M01_HERO_HIGH_TO_LOW_BAKE_CONTRACT.json"
            )
            if (
                root
                / "Docs"
                / "AAA_Review"
                / "M01_HERO_HIGH_TO_LOW_BAKE_CONTRACT.json"
            ).is_file()
            else None
        ),
        "generator_sha256": (
            sha256_file(generator_path) if generator_path.is_file() else None
        ),
        "source_blend_sha256": (
            sha256_file(source_path)
            if source_path and source_path.is_file()
            else None
        ),
    }


def evaluate_artifacts(
    contract: dict[str, Any],
    manifest: dict[str, Any],
    root: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    checks: dict[str, bool] = {}
    checks["manifest_schema"] = manifest.get("schema") == MANIFEST_SCHEMA
    expected_build_id = contract.get("build_id", BUILD_ID)
    expected_promotion = contract.get("promotion", PROMOTION)
    checks["build_id"] = manifest.get("build_id") == expected_build_id
    checks["promotion_is_candidate_only"] = (
        manifest.get("promotion") == expected_promotion
    )

    checks["source_integrity"] = verify_file_evidence(
        manifest.get("source"), root, "source", errors
    )
    outputs = manifest.get("outputs")
    checks["outputs_shape"] = (
        isinstance(outputs, dict)
        and set(outputs) == {"master_blend", "low_glb"}
    )
    output_integrity = checks["outputs_shape"]
    if isinstance(outputs, dict):
        for label in ("master_blend", "low_glb"):
            output_integrity &= verify_file_evidence(
                outputs.get(label), root, f"outputs.{label}", errors
            )
    checks["output_integrity"] = bool(output_integrity)

    expected_bake = contract.get("bake_contract")
    actual_bake = manifest.get("bake_contract")
    checks["bake_contract_matches"] = actual_bake == expected_bake

    contract_assets = _contract_assets(contract)
    raw_assets = manifest.get("assets")
    asset_records = {
        item.get("id"): item
        for item in raw_assets
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    } if isinstance(raw_assets, list) else {}
    checks["asset_scope"] = (
        set(asset_records) == REQUIRED_ASSETS
        and len(asset_records) == len(REQUIRED_ASSETS)
    )

    map_hashes: list[str] = []
    asset_results: dict[str, dict[str, bool]] = {}
    for asset_id in sorted(REQUIRED_ASSETS):
        spec = contract_assets.get(asset_id, {})
        record = asset_records.get(asset_id, {})
        result: dict[str, bool] = {}
        result["object_names"] = (
            record.get("source_object") == spec.get("source_object")
            and isinstance(record.get("low"), dict)
            and record["low"].get("object") == spec.get("low_object")
            and isinstance(record.get("high"), dict)
            and record["high"].get("object") == spec.get("high_object")
            and isinstance(record.get("cage"), dict)
            and record["cage"].get("object") == spec.get("cage_object")
        )
        low = record.get("low") if isinstance(record.get("low"), dict) else {}
        high = record.get("high") if isinstance(record.get("high"), dict) else {}
        cage = record.get("cage") if isinstance(record.get("cage"), dict) else {}
        result["separate_mesh_datablocks"] = (
            isinstance(low.get("mesh_datablock"), str)
            and isinstance(high.get("mesh_datablock"), str)
            and low["mesh_datablock"] != high["mesh_datablock"]
            and cage.get("mesh_datablock") not in {
                low.get("mesh_datablock"),
                high.get("mesh_datablock"),
            }
        )
        low_vertices = low.get("vertices")
        high_vertices = high.get("vertices")
        ratio = record.get("high_to_low_vertex_ratio")
        result["high_vertex_ratio"] = (
            isinstance(low_vertices, int)
            and low_vertices > 0
            and isinstance(high_vertices, int)
            and high_vertices > low_vertices
            and isinstance(ratio, (int, float))
            and abs(float(ratio) - (high_vertices / low_vertices)) <= 0.001
            and float(ratio)
            >= float(spec.get("minimum_high_to_low_vertex_ratio", 999.0))
        )
        result["low_uv"] = (
            isinstance(low.get("uv_layers"), list)
            and contract["bake_contract"]["uv_layer"] in low["uv_layers"]
        )
        bounds_delta = record.get("high_to_low_bounds_delta_m")
        result["bounds_alignment"] = (
            isinstance(bounds_delta, (int, float))
            and 0.0 <= float(bounds_delta)
            <= float(spec.get("maximum_high_to_low_bounds_delta_m", -1.0))
        )
        result["detail_groups"] = (
            isinstance(record.get("detail_groups"), list)
            and set(record["detail_groups"])
            == set(spec.get("required_detail_groups", []))
            and len(record["detail_groups"])
            == len(spec.get("required_detail_groups", []))
        )

        map_records = record.get("maps")
        by_type = {
            item.get("type"): item
            for item in map_records
            if isinstance(item, dict) and isinstance(item.get("type"), str)
        } if isinstance(map_records, list) else {}
        result["map_scope"] = (
            set(by_type) == REQUIRED_MAPS and len(by_type) == len(REQUIRED_MAPS)
        )
        map_integrity = result["map_scope"]
        for map_spec in sorted(
            contract["bake_contract"]["maps"],
            key=lambda item: item["type"],
        ):
            item = by_type.get(map_spec["type"], {})
            projection = (
                item.get("projection")
                if isinstance(item.get("projection"), dict)
                else {}
            )
            map_integrity &= (
                item.get("width") == contract["bake_contract"]["resolution"]
                and item.get("height") == contract["bake_contract"]["resolution"]
                and item.get("channels") == 3
                and item.get("color_space") == map_spec["color_space"]
                and isinstance(item.get("varied_rgb_channels"), int)
                and item["varied_rgb_channels"]
                >= map_spec["minimum_varied_rgb_channels"]
                and projection.get("selected_to_active") is True
                and projection.get("cage_object") == spec.get("cage_object")
                and projection.get("cage_extrusion_m")
                == spec.get("cage_extrusion_m")
                and projection.get("max_ray_distance_m")
                == spec.get("max_ray_distance_m")
            )
            integrity_ok = verify_file_evidence(
                item,
                root,
                f"{asset_id}.{map_spec['type']}",
                errors,
            )
            map_integrity &= integrity_ok
            if integrity_ok:
                map_hashes.append(item["sha256"].lower())
        result["map_integrity_and_projection"] = bool(map_integrity)
        asset_results[asset_id] = result
        for check, passed in result.items():
            if not passed:
                errors.append(f"{asset_id}: artifact check failed: {check}")

    expected_fingerprint = hashlib.sha256(
        "\n".join(map_hashes).encode("ascii")
    ).hexdigest()
    checks["package_fingerprint"] = (
        len(map_hashes) == len(REQUIRED_ASSETS) * len(REQUIRED_MAPS)
        and manifest.get("package_fingerprint_sha256") == expected_fingerprint
    )
    validation = manifest.get("validation")
    checks["author_validation"] = (
        isinstance(validation, dict)
        and validation.get("pass") is True
        and validation.get("failures") == []
    )

    for check, passed in checks.items():
        if not passed:
            errors.append(f"artifact check failed: {check}")
    return {
        "gate": "PASS" if not errors else "FAIL",
        "checks": checks,
        "asset_results": asset_results,
        "computed_package_fingerprint_sha256": expected_fingerprint,
        "errors": errors,
    }


def build_readiness_report(
    contract: dict[str, Any],
    generator_path: Path,
    manifest_path: Path,
    root: Path,
) -> dict[str, Any]:
    source = evaluate_source(contract, generator_path, root)
    if manifest_path.is_file():
        try:
            manifest = json.loads(
                manifest_path.read_text(encoding="utf-8-sig")
            )
            artifacts = evaluate_artifacts(contract, manifest, root)
        except (OSError, json.JSONDecodeError) as exc:
            artifacts = {
                "gate": "FAIL",
                "checks": {},
                "asset_results": {},
                "errors": [f"manifest read failed: {exc}"],
            }
    else:
        artifacts = {
            "gate": "NOT_RUN",
            "checks": {},
            "asset_results": {},
            "errors": [],
            "reason": (
                "No Blender artifact manifest exists. The serialized Blender "
                "build was intentionally not launched during this stability-safe pass."
            ),
        }

    if source["gate"] == "PASS" and artifacts["gate"] == "PASS":
        gate = "PASS"
        terminal = "ARTIFACTS_VERIFIED_CANDIDATE_ONLY"
    elif source["gate"] == "PASS" and artifacts["gate"] == "NOT_RUN":
        gate = "PASS_WITH_GAPS"
        terminal = "SOURCE_READY_ARTIFACTS_NOT_RUN"
    else:
        gate = "FAIL"
        terminal = "CONTRACT_OR_ARTIFACT_VERIFICATION_FAILED"
    return {
        "schema": REPORT_SCHEMA,
        "build_id": BUILD_ID,
        "gate": gate,
        "terminal_state": terminal,
        "source_gate": source,
        "artifact_gate": artifacts,
        "p3_4_closed": False,
        "p3_4_disposition": (
            "INCOMPLETE until the serialized Blender build runs, artifact "
            "verification passes, and visible grazing-angle/Unreal validation is accepted."
        ),
        "promotion": PROMOTION,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Mission 01 high-to-low bake source and artifacts."
    )
    root_default = Path(__file__).resolve().parents[1]
    parser.add_argument("--root", type=Path, default=root_default)
    parser.add_argument(
        "--contract",
        type=Path,
        default=root_default
        / "Docs"
        / "AAA_Review"
        / "M01_HERO_HIGH_TO_LOW_BAKE_CONTRACT.json",
    )
    parser.add_argument(
        "--generator",
        type=Path,
        default=root_default / "Scripts" / "blender_m01_hero_high_to_low_bake.py",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=root_default
        / "Saved"
        / "Reports"
        / "M01_HERO_HIGH_TO_LOW_BAKE_MANIFEST.json",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-artifacts", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    contract = json.loads(args.contract.read_text(encoding="utf-8-sig"))
    report = build_readiness_report(
        contract,
        args.generator,
        args.manifest,
        root,
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
