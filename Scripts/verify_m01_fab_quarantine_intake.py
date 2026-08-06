"""Fail-closed offline verifier for the M01 Fab/Quixel quarantine intake."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "Docs" / "AAA_Review" / "M01_FAB_QUARANTINE_PROVENANCE_SCHEMA.json"
TEMPLATE_PATH = ROOT / "Docs" / "AAA_Review" / "M01_FAB_QUARANTINE_INTAKE_TEMPLATE.json"
SHORTLIST_PATH = ROOT / "Docs" / "AAA_Review" / "M01_FAB_VISIBLE_ART_SHORTLIST_2026-08-02.md"
VISUAL_REVIEW_PATH = ROOT / "Docs" / "AAA_Review" / "BLD_M01_COAST_PROD_001_VISUAL_REVIEW.md"
EVIDENCE_PREFIX = "Saved/FabQuarantine/M01_FAB_QUARANTINE_INTAKE_001/"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PRODUCT_ID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
FORBIDDEN_ACCEPTANCE_PATH_PREFIXES = ("Content/", "Plugins/", "Engine/")
FEATURES = ("nanite", "lod", "collision", "material_instances")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def issue(issues: list[dict], path: str, code: str, detail: str) -> None:
    issues.append({"path": path, "code": code, "detail": detail})


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_timestamp(value: object) -> bool:
    if not nonempty(value):
        return False
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.tzinfo is not None
    except ValueError:
        return False


def safe_relative_path(value: object) -> bool:
    if not nonempty(value):
        return False
    path = PurePosixPath(str(value).replace("\\", "/"))
    return not path.is_absolute() and ".." not in path.parts


def validate_evidence(
    evidence: object,
    field_path: str,
    issues: list[dict],
    root: Path,
    *,
    required_prefix: str = EVIDENCE_PREFIX,
) -> None:
    if not isinstance(evidence, dict):
        issue(issues, field_path, "MISSING_EVIDENCE_RECORD", "Expected path, bytes and sha256.")
        return
    path_value = evidence.get("path")
    bytes_value = evidence.get("bytes")
    digest_value = evidence.get("sha256")
    if not safe_relative_path(path_value):
        issue(issues, field_path + ".path", "INVALID_EVIDENCE_PATH", "Use a non-empty relative path.")
        return
    normalized = str(path_value).replace("\\", "/")
    if required_prefix and not normalized.startswith(required_prefix):
        issue(issues, field_path + ".path", "OUTSIDE_QUARANTINE",
              f"Evidence must be under {required_prefix}")
    if normalized.startswith(FORBIDDEN_ACCEPTANCE_PATH_PREFIXES):
        issue(issues, field_path + ".path", "CONTENT_IS_NOT_PROVENANCE",
              "Project Content presence cannot satisfy intake evidence.")
    if not isinstance(bytes_value, int) or isinstance(bytes_value, bool) or bytes_value <= 0:
        issue(issues, field_path + ".bytes", "INVALID_BYTE_COUNT", "Expected a positive integer.")
    if not isinstance(digest_value, str) or not SHA256_RE.fullmatch(digest_value):
        issue(issues, field_path + ".sha256", "INVALID_SHA256", "Expected lowercase SHA-256.")
    evidence_path = root / normalized
    if not evidence_path.is_file():
        issue(issues, field_path + ".path", "EVIDENCE_FILE_MISSING", normalized)
        return
    if isinstance(bytes_value, int) and evidence_path.stat().st_size != bytes_value:
        issue(issues, field_path + ".bytes", "BYTE_COUNT_MISMATCH", normalized)
    if isinstance(digest_value, str) and SHA256_RE.fullmatch(digest_value):
        if sha256_file(evidence_path) != digest_value:
            issue(issues, field_path + ".sha256", "HASH_MISMATCH", normalized)


def validate_decision_basis(record: dict, issues: list[dict], root: Path) -> None:
    basis = record.get("decision_basis")
    if not isinstance(basis, dict):
        issue(issues, "decision_basis", "MISSING_DECISION_BASIS", "Shortlist and visual review are required.")
        return
    expected = (
        ("shortlist_path", "Docs/AAA_Review/M01_FAB_VISIBLE_ART_SHORTLIST_2026-08-02.md",
         "shortlist_sha256", SHORTLIST_PATH),
        ("visual_review_path", "Docs/AAA_Review/BLD_M01_COAST_PROD_001_VISUAL_REVIEW.md",
         "visual_review_sha256", VISUAL_REVIEW_PATH),
    )
    for path_key, expected_path, hash_key, canonical_path in expected:
        if basis.get(path_key) != expected_path:
            issue(issues, f"decision_basis.{path_key}", "WRONG_DECISION_SOURCE", expected_path)
        expected_hash = sha256_file(canonical_path)
        if basis.get(hash_key) != expected_hash:
            issue(issues, f"decision_basis.{hash_key}", "DECISION_SOURCE_HASH_MISMATCH", expected_hash)
    if basis.get("visual_review_status") != "ACCEPTED_AS_LAYOUT_SCAFFOLD_REJECTED_AS_VISIBLE_AAA_ART":
        issue(issues, "decision_basis.visual_review_status", "WRONG_VISUAL_DECISION",
              "Visible scaffold art was rejected.")


def validate_policy(record: dict, issues: list[dict]) -> None:
    expected = {
        "automatic_purchase_allowed": False,
        "automatic_download_allowed": False,
        "automatic_import_allowed": False,
        "content_presence_is_acceptance": False,
        "first_inspection_city_kit_limit": 1,
        "first_inspection_coast_kit_limit": 1,
        "quarantine_only": True,
        "runtime_promotion_allowed": False,
    }
    policy = record.get("policy")
    if not isinstance(policy, dict):
        issue(issues, "policy", "MISSING_POLICY", "Fail-closed policy is required.")
        return
    for key, value in expected.items():
        if policy.get(key) != value:
            issue(issues, f"policy.{key}", "UNSAFE_POLICY_DRIFT", f"Must equal {value!r}.")


def validate_asset(asset: object, index: int, issues: list[dict], root: Path, shortlist: str) -> None:
    base = f"assets[{index}]"
    if not isinstance(asset, dict):
        issue(issues, base, "INVALID_ASSET_RECORD", "Expected an object.")
        return
    slot = asset.get("slot")
    if slot not in {"CITY_KIT", "BEACH_COAST_KIT"}:
        issue(issues, base + ".slot", "INVALID_SLOT", "Expected CITY_KIT or BEACH_COAST_KIT.")

    catalog = asset.get("catalog")
    if not isinstance(catalog, dict):
        issue(issues, base + ".catalog", "MISSING_CATALOG", "Catalog provenance is required.")
    else:
        for key in ("product_name", "source_url", "product_id", "seller"):
            if not nonempty(catalog.get(key)):
                issue(issues, f"{base}.catalog.{key}", "MISSING_CATALOG_FIELD", key)
        product_id = catalog.get("product_id")
        source_url = catalog.get("source_url")
        if not isinstance(product_id, str) or not PRODUCT_ID_RE.fullmatch(product_id):
            issue(issues, base + ".catalog.product_id", "INVALID_PRODUCT_ID", str(product_id))
        expected_url = f"https://www.fab.com/listings/{product_id}"
        if source_url != expected_url:
            issue(issues, base + ".catalog.source_url", "URL_PRODUCT_ID_MISMATCH", expected_url)
        if nonempty(source_url):
            parsed = urlparse(str(source_url))
            if parsed.scheme != "https" or parsed.netloc != "www.fab.com":
                issue(issues, base + ".catalog.source_url", "NON_FAB_SOURCE", str(source_url))
        if any(nonempty(catalog.get(key)) and str(catalog[key]) not in shortlist
               for key in ("source_url", "product_name", "seller")):
            issue(issues, base + ".catalog", "NOT_IN_GOVERNED_SHORTLIST",
                  "URL, product name and seller must match the shortlist.")
        validate_evidence(catalog.get("product_page_snapshot"),
                          base + ".catalog.product_page_snapshot", issues, root)

    commerce = asset.get("commerce")
    if not isinstance(commerce, dict):
        issue(issues, base + ".commerce", "MISSING_COMMERCE", "Acquisition and license evidence required.")
    else:
        paid_status = commerce.get("paid_free_status")
        if paid_status not in {"PAID", "FREE"}:
            issue(issues, base + ".commerce.paid_free_status", "INVALID_PAID_FREE_STATUS", str(paid_status))
        price = commerce.get("price_paid")
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            issue(issues, base + ".commerce.price_paid", "INVALID_PRICE", str(price))
        elif paid_status == "PAID" and price <= 0:
            issue(issues, base + ".commerce.price_paid", "PAID_PRICE_MUST_BE_POSITIVE", str(price))
        elif paid_status == "FREE" and price != 0:
            issue(issues, base + ".commerce.price_paid", "FREE_PRICE_MUST_BE_ZERO", str(price))
        if not re.fullmatch(r"[A-Z]{3}", str(commerce.get("currency", ""))):
            issue(issues, base + ".commerce.currency", "INVALID_CURRENCY", str(commerce.get("currency")))
        if not valid_timestamp(commerce.get("acquired_at")):
            issue(issues, base + ".commerce.acquired_at", "INVALID_ACQUISITION_TIMESTAMP",
                  "ISO-8601 timestamp with timezone required.")
        if not nonempty(commerce.get("license_tier")):
            issue(issues, base + ".commerce.license_tier", "MISSING_LICENSE_TIER", "Exact tier required.")
        validate_evidence(commerce.get("license_text_snapshot"),
                          base + ".commerce.license_text_snapshot", issues, root)
        validate_evidence(commerce.get("receipt_or_acquisition_record"),
                          base + ".commerce.receipt_or_acquisition_record", issues, root)

    compatibility = asset.get("compatibility")
    if not isinstance(compatibility, dict):
        issue(issues, base + ".compatibility", "MISSING_COMPATIBILITY", "Engine evidence required.")
    else:
        versions = compatibility.get("supported_unreal_versions")
        if not isinstance(versions, list) or not versions or not all(nonempty(v) for v in versions):
            issue(issues, base + ".compatibility.supported_unreal_versions",
                  "MISSING_SUPPORTED_VERSIONS", "At least one exact supported version required.")
        if compatibility.get("target_engine") != "5.8":
            issue(issues, base + ".compatibility.target_engine", "WRONG_TARGET_ENGINE", "Expected 5.8.")
        if compatibility.get("target_engine_supported") is not True:
            issue(issues, base + ".compatibility.target_engine_supported",
                  "TARGET_ENGINE_UNSUPPORTED", "Fab evidence must explicitly cover UE 5.8.")
        restrictions = compatibility.get("platform_restrictions")
        if not isinstance(restrictions, list) or not all(nonempty(item) for item in restrictions):
            issue(issues, base + ".compatibility.platform_restrictions",
                  "INVALID_PLATFORM_RESTRICTIONS", "Use [] only if evidence confirms none.")
        if compatibility.get("cooked_windows_redistribution_covered") is not True:
            issue(issues, base + ".compatibility.cooked_windows_redistribution_covered",
                  "REDISTRIBUTION_NOT_CONFIRMED", "Cooked Windows redistribution must be covered.")
        validate_evidence(compatibility.get("evidence"), base + ".compatibility.evidence", issues, root)

    storage = asset.get("storage")
    if not isinstance(storage, dict):
        issue(issues, base + ".storage", "MISSING_STORAGE", "Download and installed sizes required.")
    else:
        for key in ("download_bytes", "installed_bytes"):
            value = storage.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                issue(issues, f"{base}.storage.{key}", "INVALID_STORAGE_BYTES", str(value))
        validate_evidence(storage.get("download_package"), base + ".storage.download_package", issues, root)
        validate_evidence(storage.get("installed_inventory_manifest"),
                          base + ".storage.installed_inventory_manifest", issues, root)

    textures = asset.get("texture_inventory")
    if not isinstance(textures, dict):
        issue(issues, base + ".texture_inventory", "MISSING_TEXTURE_INVENTORY", "Resolution inventory required.")
    else:
        total = textures.get("total_textures")
        resolutions = textures.get("resolutions")
        if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
            issue(issues, base + ".texture_inventory.total_textures",
                  "INVALID_TEXTURE_TOTAL", str(total))
        if not isinstance(resolutions, list) or not resolutions:
            issue(issues, base + ".texture_inventory.resolutions",
                  "MISSING_TEXTURE_RESOLUTIONS", "At least one resolution bucket required.")
        else:
            counted = 0
            for ridx, resolution in enumerate(resolutions):
                rbase = f"{base}.texture_inventory.resolutions[{ridx}]"
                if not isinstance(resolution, dict):
                    issue(issues, rbase, "INVALID_TEXTURE_BUCKET", "Expected object.")
                    continue
                for key in ("width", "height", "count"):
                    value = resolution.get(key)
                    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                        issue(issues, f"{rbase}.{key}", "INVALID_TEXTURE_DIMENSION_OR_COUNT", str(value))
                counted += resolution.get("count", 0) if isinstance(resolution.get("count"), int) else 0
                for key in ("formats", "usage"):
                    value = resolution.get(key)
                    if not isinstance(value, list) or not value or not all(nonempty(v) for v in value):
                        issue(issues, f"{rbase}.{key}", "MISSING_TEXTURE_BUCKET_DETAIL", key)
            if isinstance(total, int) and counted != total:
                issue(issues, base + ".texture_inventory.total_textures",
                      "TEXTURE_COUNT_MISMATCH", f"total={total} buckets={counted}")
        validate_evidence(textures.get("inventory_evidence"),
                          base + ".texture_inventory.inventory_evidence", issues, root)

    features = asset.get("runtime_features")
    if not isinstance(features, dict):
        issue(issues, base + ".runtime_features", "MISSING_RUNTIME_FEATURES", "Four feature records required.")
    else:
        for name in FEATURES:
            feature = features.get(name)
            if not isinstance(feature, dict) or not isinstance(feature.get("supported"), bool):
                issue(issues, f"{base}.runtime_features.{name}", "INVALID_FEATURE_SUPPORT",
                      "Boolean supported field required.")
                continue
            validate_evidence(feature.get("evidence"),
                              f"{base}.runtime_features.{name}.evidence", issues, root)

    dependencies = asset.get("dependencies")
    if not isinstance(dependencies, dict):
        issue(issues, base + ".dependencies", "MISSING_DEPENDENCIES", "Dependency inventory required.")
    else:
        items = dependencies.get("items")
        if not isinstance(items, list) or not all(nonempty(item) for item in items):
            issue(issues, base + ".dependencies.items", "INVALID_DEPENDENCY_LIST",
                  "Use [] only when evidence confirms no dependencies.")
        validate_evidence(dependencies.get("inventory_evidence"),
                          base + ".dependencies.inventory_evidence", issues, root)

    immutable = asset.get("immutable_artifacts")
    if not isinstance(immutable, list) or not immutable:
        issue(issues, base + ".immutable_artifacts", "MISSING_IMMUTABLE_HASH_SET",
              "At least one separately hash-bound artifact required.")
    else:
        for aidx, evidence in enumerate(immutable):
            validate_evidence(evidence, f"{base}.immutable_artifacts[{aidx}]", issues, root)

    quarantine = asset.get("quarantine_disposition")
    final = asset.get("final_disposition")
    if quarantine not in {
        "HOLD_EVIDENCE_INCOMPLETE",
        "APPROVED_FOR_MANUAL_QUARANTINE_INSPECTION",
        "REJECTED_BEFORE_IMPORT",
    }:
        issue(issues, base + ".quarantine_disposition", "INVALID_QUARANTINE_DISPOSITION", str(quarantine))
    if final not in {"NOT_EVALUATED", "QUARANTINE_ONLY_NOT_RUNTIME_APPROVED", "REJECTED"}:
        issue(issues, base + ".final_disposition", "INVALID_FINAL_DISPOSITION", str(final))


def evaluate(record: dict, evidence_root: Path = ROOT) -> dict:
    issues: list[dict] = []
    if record.get("schema") != "skyguard.m01.fab-quarantine-provenance.v1":
        issue(issues, "schema", "WRONG_SCHEMA", str(record.get("schema")))
    if record.get("intake_id") != "M01-FAB-QUARANTINE-INTAKE-001":
        issue(issues, "intake_id", "WRONG_INTAKE_ID", str(record.get("intake_id")))
    validate_policy(record, issues)
    validate_decision_basis(record, issues, evidence_root)

    assets = record.get("assets")
    if not isinstance(assets, list) or len(assets) != 2:
        issue(issues, "assets", "WRONG_FIRST_INSPECTION_COUNT",
              "Exactly two records required: one city and one beach/coast kit.")
        assets = assets if isinstance(assets, list) else []
    slots = [asset.get("slot") for asset in assets if isinstance(asset, dict)]
    if slots.count("CITY_KIT") != 1 or slots.count("BEACH_COAST_KIT") != 1:
        issue(issues, "assets", "WRONG_SLOT_CARDINALITY",
              "Exactly one CITY_KIT and one BEACH_COAST_KIT required.")
    shortlist = SHORTLIST_PATH.read_text(encoding="utf-8")
    for index, asset in enumerate(assets):
        validate_asset(asset, index, issues, evidence_root, shortlist)

    status = record.get("status")
    dispositions = [
        (asset.get("quarantine_disposition"), asset.get("final_disposition"))
        for asset in assets if isinstance(asset, dict)
    ]
    if not issues:
        if status == "EVIDENCE_COMPLETE_READY_FOR_MANUAL_QUARANTINE_INSPECTION":
            if not all(pair == (
                "APPROVED_FOR_MANUAL_QUARANTINE_INSPECTION",
                "QUARANTINE_ONLY_NOT_RUNTIME_APPROVED",
            ) for pair in dispositions):
                issue(issues, "status", "DISPOSITION_STATUS_MISMATCH",
                      "Ready status requires both assets approved only for manual quarantine inspection.")
        elif status == "EVIDENCE_COMPLETE_REJECTED":
            if not all(pair == ("REJECTED_BEFORE_IMPORT", "REJECTED") for pair in dispositions):
                issue(issues, "status", "DISPOSITION_STATUS_MISMATCH",
                      "Rejected status requires both assets rejected before import.")
        else:
            issue(issues, "status", "FAIL_CLOSED_STATUS_NOT_PROMOTABLE",
                  "Complete records must declare ready-for-manual-inspection or rejected.")

    gate_status = "PASS" if not issues else "FAIL_CLOSED"
    disposition = (
        "READY_FOR_MANUAL_QUARANTINE_INSPECTION"
        if gate_status == "PASS" and status == "EVIDENCE_COMPLETE_READY_FOR_MANUAL_QUARANTINE_INSPECTION"
        else "VALIDATED_REJECTION"
        if gate_status == "PASS" and status == "EVIDENCE_COMPLETE_REJECTED"
        else "HOLD_NO_PURCHASE_NO_IMPORT"
    )
    return {
        "schema": "skyguard.m01.fab-quarantine-audit.v1",
        "intake_id": record.get("intake_id"),
        "gate_status": gate_status,
        "disposition": disposition,
        "automatic_purchase_allowed": False,
        "automatic_import_allowed": False,
        "runtime_promotion_allowed": False,
        "issue_count": len(issues),
        "issues": issues,
    }


def validate_schema_source() -> list[str]:
    errors: list[str] = []
    schema = load_json(SCHEMA_PATH)
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("Schema must declare JSON Schema draft 2020-12.")
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    for marker in (
        "automatic_purchase_allowed",
        "automatic_import_allowed",
        "first_inspection_city_kit_limit",
        "source_url",
        "license_text_snapshot",
        "download_bytes",
        "texture_inventory",
        "material_instances",
        "immutable_artifacts",
        "quarantine_disposition",
        "final_disposition",
    ):
        if marker not in text:
            errors.append(f"Schema missing marker: {marker}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", type=Path, default=TEMPLATE_PATH)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    schema_errors = validate_schema_source()
    record = load_json(args.record)
    result = evaluate(record)
    if schema_errors:
        result["gate_status"] = "FAIL_CLOSED"
        result["disposition"] = "HOLD_NO_PURCHASE_NO_IMPORT"
        for detail in schema_errors:
            result["issues"].append({"path": "schema_source", "code": "SCHEMA_SOURCE_INVALID", "detail": detail})
        result["issue_count"] = len(result["issues"])
    print(json.dumps(result, indent=2))
    if result["gate_status"] != "PASS":
        return 3
    if args.require_ready and result["disposition"] != "READY_FOR_MANUAL_QUARANTINE_INSPECTION":
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
