"""Fail-closed verifier for Mission 1 third-party final-use receipts.

The verifier is offline and read-only. It never downloads, imports, promotes,
builds, launches Unreal, or modifies the record it inspects.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORD = (
    ROOT
    / "Docs"
    / "AAA_Review"
    / "M01_THIRD_PARTY_FINAL_USE_RECEIPT_TEMPLATE.json"
)
SCHEMA = "skyguard.m01.third-party-final-use-receipt.v1"
READY_STATUS = "EVIDENCE_COMPLETE_READY_FOR_RELEASE_AUDIT"
READY_DISPOSITION = "FINAL_USE_RECEIPT_COMPLETE_NOT_RELEASE_ACCEPTANCE"
PROVIDERS = {"FAB", "QUIXEL_BRIDGE", "POLY_HAVEN", "OTHER_LICENSED"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_ASSERTIONS = {
    "every_third_party_runtime_asset_listed",
    "every_source_and_license_receipt_hash_bound",
    "every_project_file_hash_bound",
    "every_dependency_resolved",
    "every_mission_use_declared",
    "every_visual_acceptance_hash_bound",
    "every_performance_acceptance_hash_bound",
    "shipping_notice_obligations_resolved",
    "no_quarantine_package_referenced",
    "no_engine_content_reference_used_as_project_copy",
}
REQUIRED_POLICY = {
    "content_presence_is_license_evidence": False,
    "catalog_metadata_is_acquisition_evidence": False,
    "quarantine_acceptance_is_runtime_acceptance": False,
    "runtime_promotion_requires_exact_project_file_hashes": True,
    "runtime_promotion_requires_visual_acceptance": True,
    "runtime_promotion_requires_performance_acceptance": True,
    "runtime_promotion_allowed": False,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def issue(issues: list[dict[str, str]], path: str, code: str, detail: Any) -> None:
    issues.append({"path": path, "code": code, "detail": str(detail)})


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve_relative(project_root: Path, raw: Any) -> Path | None:
    if not nonempty(raw):
        return None
    pure = PurePosixPath(str(raw).replace("\\", "/"))
    if pure.is_absolute() or ".." in pure.parts:
        return None
    resolved = (project_root / Path(*pure.parts)).resolve()
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError:
        return None
    return resolved


def validate_artifact(
    artifact: Any,
    path: str,
    project_root: Path,
    issues: list[dict[str, str]],
    *,
    required_prefix: str | None = None,
) -> None:
    if not isinstance(artifact, dict):
        issue(issues, path, "INVALID_ARTIFACT", "Object required.")
        return
    raw_path = artifact.get("path")
    expected_bytes = artifact.get("bytes")
    expected_sha = artifact.get("sha256")
    resolved = resolve_relative(project_root, raw_path)
    if resolved is None:
        issue(issues, f"{path}.path", "INVALID_EVIDENCE_PATH", raw_path)
        return
    normalized = PurePosixPath(str(raw_path).replace("\\", "/")).as_posix()
    if required_prefix and not normalized.startswith(required_prefix):
        issue(
            issues,
            f"{path}.path",
            "INVALID_PATH_PREFIX",
            f"Expected {required_prefix}: {normalized}",
        )
    if not isinstance(expected_bytes, int) or isinstance(expected_bytes, bool) or expected_bytes <= 0:
        issue(issues, f"{path}.bytes", "INVALID_BYTE_COUNT", expected_bytes)
    if not isinstance(expected_sha, str) or not SHA256_RE.fullmatch(expected_sha):
        issue(issues, f"{path}.sha256", "INVALID_SHA256", expected_sha)
    if not resolved.is_file():
        issue(issues, f"{path}.path", "MISSING_ARTIFACT", normalized)
        return
    actual_bytes = resolved.stat().st_size
    if isinstance(expected_bytes, int) and actual_bytes != expected_bytes:
        issue(
            issues,
            f"{path}.bytes",
            "BYTE_COUNT_MISMATCH",
            f"expected={expected_bytes} actual={actual_bytes}",
        )
    actual_sha = sha256_file(resolved)
    if isinstance(expected_sha, str) and actual_sha != expected_sha:
        issue(
            issues,
            f"{path}.sha256",
            "SHA256_MISMATCH",
            f"expected={expected_sha} actual={actual_sha}",
        )


def validate_record(record: Any, project_root: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if not isinstance(record, dict):
        return [{"path": "$", "code": "INVALID_RECORD", "detail": "Object required."}]
    if record.get("schema") != SCHEMA:
        issue(issues, "schema", "INVALID_SCHEMA", record.get("schema"))
    if not nonempty(record.get("receipt_id")):
        issue(issues, "receipt_id", "MISSING_RECEIPT_ID", record.get("receipt_id"))
    if record.get("status") != READY_STATUS:
        issue(issues, "status", "NOT_READY", record.get("status"))
    policy = record.get("policy")
    if not isinstance(policy, dict):
        issue(issues, "policy", "INVALID_POLICY", policy)
    else:
        for field, expected in REQUIRED_POLICY.items():
            if policy.get(field) is not expected:
                issue(
                    issues,
                    f"policy.{field}",
                    "INVALID_POLICY_VALUE",
                    f"expected={expected} actual={policy.get(field)}",
                )
    candidate = record.get("candidate")
    if not isinstance(candidate, dict):
        issue(issues, "candidate", "INVALID_CANDIDATE", candidate)
    else:
        if not nonempty(candidate.get("candidate_id")):
            issue(
                issues,
                "candidate.candidate_id",
                "MISSING_CANDIDATE_ID",
                candidate.get("candidate_id"),
            )
        validate_artifact(
            candidate.get("package_or_build_artifact"),
            "candidate.package_or_build_artifact",
            project_root,
            issues,
        )

    assets = record.get("assets")
    if not isinstance(assets, list) or not assets:
        issue(issues, "assets", "NO_FINAL_USE_ASSETS", assets)
        assets = []
    seen_ids: set[str] = set()
    for index, asset in enumerate(assets):
        prefix = f"assets[{index}]"
        if not isinstance(asset, dict):
            issue(issues, prefix, "INVALID_ASSET", asset)
            continue
        asset_id = asset.get("asset_record_id")
        if not nonempty(asset_id):
            issue(issues, f"{prefix}.asset_record_id", "MISSING_ASSET_RECORD_ID", asset_id)
        elif asset_id in seen_ids:
            issue(issues, f"{prefix}.asset_record_id", "DUPLICATE_ASSET_RECORD_ID", asset_id)
        else:
            seen_ids.add(asset_id)
        provider = asset.get("provider")
        if provider not in PROVIDERS:
            issue(issues, f"{prefix}.provider", "INVALID_PROVIDER", provider)

        source = asset.get("source_identity")
        if not isinstance(source, dict):
            issue(issues, f"{prefix}.source_identity", "INVALID_SOURCE_IDENTITY", source)
        else:
            for field in ("product_or_asset_id", "asset_name", "creator_or_publisher", "version"):
                if not nonempty(source.get(field)):
                    issue(
                        issues,
                        f"{prefix}.source_identity.{field}",
                        "MISSING_SOURCE_FIELD",
                        source.get(field),
                    )
            url = source.get("source_url")
            if not nonempty(url) or not str(url).startswith("https://"):
                issue(
                    issues,
                    f"{prefix}.source_identity.source_url",
                    "INVALID_SOURCE_URL",
                    url,
                )

        license_info = asset.get("license")
        if not isinstance(license_info, dict):
            issue(issues, f"{prefix}.license", "INVALID_LICENSE", license_info)
        else:
            for field in ("license_name", "license_tier", "acquired_at"):
                if not nonempty(license_info.get(field)):
                    issue(
                        issues,
                        f"{prefix}.license.{field}",
                        "MISSING_LICENSE_FIELD",
                        license_info.get(field),
                    )
            acquired_at = license_info.get("acquired_at")
            if nonempty(acquired_at):
                try:
                    parsed_at = datetime.fromisoformat(
                        str(acquired_at).replace("Z", "+00:00")
                    )
                    if parsed_at.tzinfo is None:
                        raise ValueError("timezone missing")
                except ValueError:
                    issue(
                        issues,
                        f"{prefix}.license.acquired_at",
                        "INVALID_ACQUISITION_TIMESTAMP",
                        acquired_at,
                    )
            if license_info.get("cooked_windows_redistribution_covered") is not True:
                issue(
                    issues,
                    f"{prefix}.license.cooked_windows_redistribution_covered",
                    "REDISTRIBUTION_NOT_CONFIRMED",
                    license_info.get("cooked_windows_redistribution_covered"),
                )
            validate_artifact(
                license_info.get("license_snapshot"),
                f"{prefix}.license.license_snapshot",
                project_root,
                issues,
            )
            validate_artifact(
                license_info.get("acquisition_record"),
                f"{prefix}.license.acquisition_record",
                project_root,
                issues,
            )

        validate_artifact(
            asset.get("source_inventory"),
            f"{prefix}.source_inventory",
            project_root,
            issues,
        )

        project_assets = asset.get("project_assets")
        if not isinstance(project_assets, list) or not project_assets:
            issue(issues, f"{prefix}.project_assets", "NO_PROJECT_ASSETS", project_assets)
            project_assets = []
        for project_index, project_asset in enumerate(project_assets):
            project_prefix = f"{prefix}.project_assets[{project_index}]"
            if not isinstance(project_asset, dict):
                issue(issues, project_prefix, "INVALID_PROJECT_ASSET", project_asset)
                continue
            game_path = project_asset.get("game_package_path")
            if not nonempty(game_path) or not str(game_path).startswith("/Game/Skyguard/"):
                issue(
                    issues,
                    f"{project_prefix}.game_package_path",
                    "INVALID_GAME_PACKAGE_PATH",
                    game_path,
                )
            if isinstance(game_path, str) and "/Quarantine/" in game_path:
                issue(
                    issues,
                    f"{project_prefix}.game_package_path",
                    "QUARANTINE_REFERENCE_FORBIDDEN",
                    game_path,
                )
            if isinstance(game_path, str) and game_path.startswith("/Engine/"):
                issue(
                    issues,
                    f"{project_prefix}.game_package_path",
                    "ENGINE_CONTENT_REFERENCE_FORBIDDEN",
                    game_path,
                )
            if not nonempty(project_asset.get("asset_class")):
                issue(
                    issues,
                    f"{project_prefix}.asset_class",
                    "MISSING_ASSET_CLASS",
                    project_asset.get("asset_class"),
                )
            validate_artifact(
                project_asset.get("project_file"),
                f"{project_prefix}.project_file",
                project_root,
                issues,
                required_prefix="Content/Skyguard/",
            )

        mission_uses = asset.get("mission_uses")
        if not isinstance(mission_uses, list) or not mission_uses:
            issue(issues, f"{prefix}.mission_uses", "NO_MISSION_USE", mission_uses)
            mission_uses = []
        if not any(
            isinstance(item, dict)
            and item.get("mission_id") == "M01"
            and nonempty(item.get("purpose"))
            and nonempty(item.get("map_path"))
            for item in mission_uses
        ):
            issue(
                issues,
                f"{prefix}.mission_uses",
                "M01_USE_NOT_PROVEN",
                mission_uses,
            )
        if not isinstance(asset.get("modifications"), list):
            issue(
                issues,
                f"{prefix}.modifications",
                "INVALID_MODIFICATIONS",
                asset.get("modifications"),
            )

        dependencies = asset.get("dependencies")
        if not isinstance(dependencies, dict):
            issue(issues, f"{prefix}.dependencies", "INVALID_DEPENDENCIES", dependencies)
        else:
            if not isinstance(dependencies.get("items"), list):
                issue(
                    issues,
                    f"{prefix}.dependencies.items",
                    "INVALID_DEPENDENCY_ITEMS",
                    dependencies.get("items"),
                )
            validate_artifact(
                dependencies.get("evidence"),
                f"{prefix}.dependencies.evidence",
                project_root,
                issues,
            )

        acceptance = asset.get("acceptance")
        if not isinstance(acceptance, dict):
            issue(issues, f"{prefix}.acceptance", "INVALID_ACCEPTANCE", acceptance)
        else:
            for field in (
                "intake_record",
                "technical_evaluation",
                "visual_acceptance",
                "performance_acceptance",
            ):
                validate_artifact(
                    acceptance.get(field),
                    f"{prefix}.acceptance.{field}",
                    project_root,
                    issues,
                )

        release = asset.get("release")
        if not isinstance(release, dict):
            issue(issues, f"{prefix}.release", "INVALID_RELEASE", release)
        else:
            if release.get("ship_original_source_files") is not False:
                issue(
                    issues,
                    f"{prefix}.release.ship_original_source_files",
                    "SOURCE_REDISTRIBUTION_FORBIDDEN",
                    release.get("ship_original_source_files"),
                )
            if not isinstance(release.get("redistribution_constraints"), list):
                issue(
                    issues,
                    f"{prefix}.release.redistribution_constraints",
                    "INVALID_REDISTRIBUTION_CONSTRAINTS",
                    release.get("redistribution_constraints"),
                )
            if release.get("shipping_notice_required") is True:
                validate_artifact(
                    release.get("shipping_notice"),
                    f"{prefix}.release.shipping_notice",
                    project_root,
                    issues,
                )
        if asset.get("final_disposition") != "ACCEPTED_FOR_M01_FINAL_CANDIDATE":
            issue(
                issues,
                f"{prefix}.final_disposition",
                "ASSET_NOT_ACCEPTED_FOR_FINAL_CANDIDATE",
                asset.get("final_disposition"),
            )

    assertions = record.get("final_assertions")
    if not isinstance(assertions, dict):
        issue(issues, "final_assertions", "INVALID_FINAL_ASSERTIONS", assertions)
    else:
        for field in sorted(REQUIRED_ASSERTIONS):
            if assertions.get(field) is not True:
                issue(
                    issues,
                    f"final_assertions.{field}",
                    "ASSERTION_NOT_PROVEN",
                    assertions.get(field),
                )
    if record.get("final_disposition") != READY_DISPOSITION:
        issue(
            issues,
            "final_disposition",
            "INVALID_FINAL_DISPOSITION",
            record.get("final_disposition"),
        )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        issues = validate_record(record, args.project_root.resolve())
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "schema": "skyguard.m01.third-party-final-use-audit.v1",
            "gate_status": "ERROR",
            "disposition": "HOLD_NO_RUNTIME_PROMOTION",
            "error": str(exc),
        }, indent=2))
        return 2
    passed = not issues
    print(json.dumps({
        "schema": "skyguard.m01.third-party-final-use-audit.v1",
        "receipt_id": record.get("receipt_id"),
        "gate_status": "PASS" if passed else "FAIL_CLOSED",
        "disposition": (
            "READY_FOR_SEPARATE_RELEASE_AUDIT"
            if passed
            else "HOLD_NO_RUNTIME_PROMOTION"
        ),
        "runtime_promotion_allowed": passed,
        "release_accepted": False,
        "asset_count": len(record.get("assets", []))
        if isinstance(record.get("assets"), list)
        else 0,
        "issue_count": len(issues),
        "issues": issues,
    }, indent=2))
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
