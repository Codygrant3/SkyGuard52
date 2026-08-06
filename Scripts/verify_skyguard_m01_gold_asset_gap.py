from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA = "skyguard.m01.gold-asset-gap.v1"
ALLOWED_STATUSES = {"production", "blockout_proxy", "missing", "unverified"}
REQUIRED_FAMILY_IDS = {
    "yak52_exterior",
    "rear_cockpit",
    "crew_arms_gloves",
    "rifle",
    "igla",
    "pathfinder",
    "lighthouse",
    "radar_post",
    "coast",
}
REQUIRED_QUALITY_GATES = {
    "authoritative_source",
    "final_geometry",
    "uv_and_bake",
    "pbr_materials",
    "runtime_binding",
    "collision_lod_sockets",
    "rendered_visual_acceptance",
    "packaged_performance_acceptance",
    "provenance_complete",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve(root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else root / path


def evaluate(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {}

    checks["schema"] = manifest.get("schema") == SCHEMA
    if not checks["schema"]:
        errors.append(f"schema must equal {SCHEMA}")

    required_ids = manifest.get("required_asset_family_ids")
    checks["declared_required_family_ids"] = (
        isinstance(required_ids, list)
        and set(required_ids) == REQUIRED_FAMILY_IDS
        and len(required_ids) == len(REQUIRED_FAMILY_IDS)
    )
    if not checks["declared_required_family_ids"]:
        errors.append("required_asset_family_ids does not match the governed scope")

    required_gates = manifest.get("required_quality_gates")
    checks["declared_quality_gates"] = (
        isinstance(required_gates, list)
        and set(required_gates) == REQUIRED_QUALITY_GATES
        and len(required_gates) == len(REQUIRED_QUALITY_GATES)
    )
    if not checks["declared_quality_gates"]:
        errors.append("required_quality_gates does not match the governed contract")

    evidence_catalog = manifest.get("evidence_catalog")
    checks["evidence_catalog_shape"] = isinstance(evidence_catalog, dict)
    if not isinstance(evidence_catalog, dict):
        evidence_catalog = {}
        errors.append("evidence_catalog must be an object")

    evidence_results: dict[str, dict[str, Any]] = {}
    for evidence_id, record in evidence_catalog.items():
        result = {
            "path_exists": False,
            "bytes_match": False,
            "sha256_match": False,
        }
        if not isinstance(record, dict):
            errors.append(f"evidence {evidence_id} must be an object")
            evidence_results[evidence_id] = result
            continue
        raw_path = record.get("path")
        expected_bytes = record.get("bytes")
        expected_sha = record.get("sha256")
        if not isinstance(raw_path, str) or not raw_path:
            errors.append(f"evidence {evidence_id} has no path")
            evidence_results[evidence_id] = result
            continue
        path = _resolve(root, raw_path)
        result["path_exists"] = path.is_file()
        if result["path_exists"]:
            result["bytes_match"] = path.stat().st_size == expected_bytes
            result["sha256_match"] = (
                isinstance(expected_sha, str)
                and len(expected_sha) == 64
                and sha256_file(path) == expected_sha.lower()
            )
        if not all(result.values()):
            errors.append(f"evidence integrity failed: {evidence_id}")
        evidence_results[evidence_id] = result
    checks["all_evidence_integrity"] = bool(evidence_results) and all(
        all(result.values()) for result in evidence_results.values()
    )

    families = manifest.get("asset_families")
    checks["asset_families_shape"] = isinstance(families, list)
    if not isinstance(families, list):
        families = []
        errors.append("asset_families must be a list")

    family_results: dict[str, dict[str, Any]] = {}
    seen_ids: list[str] = []
    statuses: Counter[str] = Counter()

    for index, family in enumerate(families):
        label = f"asset_families[{index}]"
        if not isinstance(family, dict):
            errors.append(f"{label} must be an object")
            continue
        family_id = family.get("id")
        if not isinstance(family_id, str) or not family_id:
            errors.append(f"{label} has no id")
            continue
        seen_ids.append(family_id)
        status = family.get("status")
        statuses[str(status)] += 1
        result: dict[str, Any] = {
            "allowed_status": status in ALLOWED_STATUSES,
            "evidence_references_valid": False,
            "quality_gate_shape": False,
            "classification_valid": False,
        }
        if not result["allowed_status"]:
            errors.append(f"{family_id}: invalid status {status!r}")

        evidence = family.get("evidence")
        evidence_valid = (
            isinstance(evidence, list)
            and bool(evidence)
            and len(evidence) == len(set(evidence))
            and all(
                isinstance(evidence_id, str)
                and evidence_id in evidence_catalog
                and all(evidence_results.get(evidence_id, {}).values())
                for evidence_id in evidence
            )
        )
        result["evidence_references_valid"] = evidence_valid
        if not evidence_valid:
            errors.append(f"{family_id}: invalid or failed evidence reference")

        gates = family.get("quality_gates")
        gate_shape = (
            isinstance(gates, dict)
            and set(gates) == REQUIRED_QUALITY_GATES
            and all(isinstance(value, bool) for value in gates.values())
        )
        result["quality_gate_shape"] = gate_shape
        if not gate_shape:
            errors.append(f"{family_id}: quality_gates must contain governed booleans")
            gates = {}

        missing_requirements = family.get("missing_requirements")
        has_missing_requirements = (
            isinstance(missing_requirements, list)
            and bool(missing_requirements)
            and all(
                isinstance(requirement, str) and requirement.strip()
                for requirement in missing_requirements
            )
        )
        proxy_markers = family.get("proxy_markers")
        has_proxy_markers = (
            isinstance(proxy_markers, list)
            and bool(proxy_markers)
            and all(
                isinstance(marker, str) and marker.strip()
                for marker in proxy_markers
            )
        )

        classification_valid = False
        if status == "production":
            classification_valid = (
                evidence_valid
                and gate_shape
                and all(gates.values())
                and isinstance(missing_requirements, list)
                and not missing_requirements
                and isinstance(proxy_markers, list)
                and not proxy_markers
            )
        elif status == "blockout_proxy":
            classification_valid = (
                evidence_valid
                and gate_shape
                and not all(gates.values())
                and has_missing_requirements
                and has_proxy_markers
            )
        elif status == "missing":
            classification_valid = (
                isinstance(evidence, list)
                and not evidence
                and gate_shape
                and not any(gates.values())
                and has_missing_requirements
                and isinstance(proxy_markers, list)
                and not proxy_markers
            )
        elif status == "unverified":
            classification_valid = (
                evidence_valid
                and gate_shape
                and not all(gates.values())
                and has_missing_requirements
                and isinstance(proxy_markers, list)
                and not proxy_markers
            )
        result["classification_valid"] = classification_valid
        if not classification_valid:
            errors.append(f"{family_id}: status-specific classification contract failed")

        next_action = family.get("next_action")
        result["next_action_present"] = (
            isinstance(next_action, str) and bool(next_action.strip())
        )
        if not result["next_action_present"]:
            errors.append(f"{family_id}: next_action is required")
        family_results[family_id] = result

    checks["unique_family_ids"] = len(seen_ids) == len(set(seen_ids))
    if not checks["unique_family_ids"]:
        errors.append("asset family ids must be unique")
    checks["required_family_coverage"] = (
        set(seen_ids) == REQUIRED_FAMILY_IDS
        and len(seen_ids) == len(REQUIRED_FAMILY_IDS)
    )
    if not checks["required_family_coverage"]:
        errors.append("asset_families does not cover the governed scope exactly once")

    summary = manifest.get("summary")
    if not isinstance(summary, dict):
        summary = {}
        errors.append("summary must be an object")
    expected_counts = {
        "required_family_count": len(REQUIRED_FAMILY_IDS),
        "production_count": statuses["production"],
        "blockout_proxy_count": statuses["blockout_proxy"],
        "missing_count": statuses["missing"],
        "unverified_count": statuses["unverified"],
    }
    checks["summary_counts"] = all(
        summary.get(key) == value for key, value in expected_counts.items()
    )
    if not checks["summary_counts"]:
        errors.append("summary counts do not match asset_families")

    computed_ready = (
        len(families) == len(REQUIRED_FAMILY_IDS)
        and statuses["production"] == len(REQUIRED_FAMILY_IDS)
        and not errors
    )
    checks["gold_slice_ready_consistent"] = (
        summary.get("gold_slice_ready") is computed_ready
    )
    if not checks["gold_slice_ready_consistent"]:
        errors.append("summary.gold_slice_ready is inconsistent with classifications")

    expected_asset_gate = "PASS" if computed_ready else "PASS_WITH_GAPS"
    checks["asset_gate_consistent"] = summary.get("asset_gate") == expected_asset_gate
    if not checks["asset_gate_consistent"]:
        errors.append(f"summary.asset_gate must equal {expected_asset_gate}")

    next_build = manifest.get("next_serialized_blender_build")
    checks["next_serialized_build"] = (
        isinstance(next_build, dict)
        and isinstance(next_build.get("build_id"), str)
        and bool(next_build.get("build_id"))
        and isinstance(next_build.get("closes_or_unblocks"), list)
        and bool(next_build.get("closes_or_unblocks"))
        and set(next_build.get("closes_or_unblocks", [])).issubset(REQUIRED_FAMILY_IDS)
        and isinstance(next_build.get("required_outputs"), list)
        and bool(next_build.get("required_outputs"))
        and isinstance(next_build.get("acceptance_before_unreal_import"), list)
        and bool(next_build.get("acceptance_before_unreal_import"))
    )
    if not checks["next_serialized_build"]:
        errors.append("next_serialized_blender_build contract is incomplete")

    if statuses["production"] == 0:
        warnings.append("No scoped asset family has production acceptance.")
    if statuses["blockout_proxy"]:
        warnings.append(
            f"{statuses['blockout_proxy']} scoped families remain blockout/proxy."
        )
    if statuses["unverified"]:
        warnings.append(
            f"{statuses['unverified']} scoped families remain unverified candidates."
        )

    return {
        "schema": "skyguard.m01.gold-asset-gap.audit.v1",
        "audit_id": manifest.get("audit_id"),
        "gate": "PASS" if not errors else "FAIL",
        "asset_gate": expected_asset_gate if not errors else "FAIL",
        "gold_slice_ready": computed_ready if not errors else False,
        "checks": checks,
        "status_counts": dict(sorted(statuses.items())),
        "evidence_results": evidence_results,
        "family_results": family_results,
        "warnings": warnings,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the offline Mission 01 gold-slice asset gap manifest."
    )
    default_root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help="Skyguard52 project root.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=default_root
        / "Docs"
        / "AAA_Review"
        / "M01_GOLD_ASSET_GAP_MANIFEST.json",
        help="Gap manifest to verify.",
    )
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    report = evaluate(manifest, args.root.resolve())
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
