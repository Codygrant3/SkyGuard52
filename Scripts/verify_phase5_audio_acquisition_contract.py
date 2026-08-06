"""Offline validator for the Phase 5 audio acquisition/production contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
BRIEFS = ROOT / "Docs/AAA_Review/PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json"
PROVENANCE = ROOT / "Docs/AAA_Review/PHASE5_AUDIO_PRODUCTION_PROVENANCE_TEMPLATE.json"
ACQUISITION = ROOT / "Docs/AAA_Review/PHASE5_AUDIO_SOURCE_ACQUISITION_LEDGER.json"
REPORT = ROOT / "Saved/Reports/PHASE5_AUDIO_ACQUISITION_CONTRACT_AUDIT.json"

EXPECTED = [
    "EngineIdle", "EngineCruise", "EnginePower", "Propeller", "OpenCockpitWind",
    "RifleMuzzle", "RifleMechanical", "RifleCasing", "RifleReflection",
    "IglaSearch", "IglaLock", "IglaLaunch", "IglaFlyby", "IglaImpact",
    "DroneLightMotor", "DroneHeavyMotor", "DroneFlyby",
    "ExplosionSmallCrack", "ExplosionSmallBody", "ExplosionSmallDebris",
    "ExplosionSmallTail", "ExplosionHeavyCrack", "ExplosionHeavyBody",
    "ExplosionHeavyDebris", "ExplosionHeavyTail",
]
ALLOWED_STATES = {
    "MISSING_SOURCE",
    "CANDIDATE_UNVERIFIED",
    "ACQUIRED_UNVERIFIED",
    "PRODUCTION_BOUND",
}
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
REQUIRED_BRIEF_FIELDS = {
    "category", "status", "priority", "acquisition_mode", "technical_profile",
    "identity_requirement", "listener_perspectives", "unreal_destination",
    "output_submix", "attenuation_contract", "concurrency_contract",
    "acceptance_tests",
}
PRODUCTION_PROOF_FIELDS = {
    "approved_source_id", "source_sha256", "derivative_sha256",
    "unreal_sound_asset", "attenuation_asset", "concurrency_asset",
    "output_submix", "rights_verified", "audio_qa_passed",
}


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()

    briefs = read_json(BRIEFS)
    provenance = read_json(PROVENANCE)
    acquisition = read_json(ACQUISITION)
    entries = briefs.get("categories", [])
    by_category: dict[str, list[dict]] = {}
    for entry in entries:
        by_category.setdefault(entry.get("category"), []).append(entry)

    errors: list[str] = []
    missing = sorted(set(EXPECTED) - set(by_category))
    extra = sorted(set(by_category) - set(EXPECTED))
    duplicates = sorted(key for key, value in by_category.items() if len(value) != 1)
    if missing:
        errors.append("missing_briefs:" + ",".join(missing))
    if extra:
        errors.append("extra_briefs:" + ",".join(extra))
    if duplicates:
        errors.append("duplicate_briefs:" + ",".join(duplicates))

    state_counts = {state: 0 for state in sorted(ALLOWED_STATES)}
    production_proof_failures: list[str] = []
    for category in EXPECTED:
        matches = by_category.get(category, [])
        if len(matches) != 1:
            continue
        entry = matches[0]
        absent_fields = sorted(REQUIRED_BRIEF_FIELDS - set(entry))
        if absent_fields:
            errors.append(category + ":missing_fields:" + ",".join(absent_fields))
        if not entry.get("listener_perspectives"):
            errors.append(category + ":empty_listener_perspectives")
        if not entry.get("acceptance_tests"):
            errors.append(category + ":empty_acceptance_tests")
        if entry.get("technical_profile") not in briefs.get("technical_profiles", {}):
            errors.append(category + ":unknown_technical_profile")
        if entry.get("acquisition_mode") not in briefs.get("rights_profiles", {}):
            errors.append(category + ":unknown_rights_profile")
        state = entry.get("status")
        if state not in ALLOWED_STATES:
            errors.append(category + ":invalid_status:" + str(state))
            continue
        state_counts[state] += 1
        if state == "PRODUCTION_BOUND":
            absent_proof = sorted(PRODUCTION_PROOF_FIELDS - set(entry))
            invalid_hash = not (
                SHA256.fullmatch(str(entry.get("source_sha256", "")))
                and SHA256.fullmatch(str(entry.get("derivative_sha256", "")))
            )
            if (
                absent_proof
                or invalid_hash
                or entry.get("rights_verified") is not True
                or entry.get("audio_qa_passed") is not True
            ):
                production_proof_failures.append(category)

    provenance_entries = provenance.get("entries", [])
    provenance_categories = [entry.get("category") for entry in provenance_entries]
    provenance_exact = (
        len(provenance_categories) == len(EXPECTED)
        and set(provenance_categories) == set(EXPECTED)
        and len(set(provenance_categories)) == len(EXPECTED)
    )
    provenance_defaults = provenance.get("entry_defaults", {})
    provenance_proof_failures: list[str] = []
    provenance_missing_count = 0
    allowed_provenance_states = {
        "MISSING_SOURCE",
        "PROJECT_OWNED_RECORDING",
        "LICENSED_THIRD_PARTY",
    }
    for entry in provenance_entries:
        category = entry.get("category")
        source_status = entry.get("source_status")
        if source_status not in allowed_provenance_states:
            provenance_proof_failures.append(str(category) + ":invalid_source_status")
            continue
        if source_status == "MISSING_SOURCE":
            provenance_missing_count += 1
            continue
        resolved = dict(provenance_defaults)
        resolved.update(entry)
        required_values = (
            "source_owner_or_publisher",
            "license_identifier",
            "redistribution_terms",
            "original_filename",
            "unreal_sound_asset",
            "attenuation_asset",
            "concurrency_asset",
            "output_submix",
        )
        if (
            not SHA256.fullmatch(str(resolved.get("source_sha256", "")))
            or any(not resolved.get(key) for key in required_values)
        ):
            provenance_proof_failures.append(str(category))
    routing = provenance.get("routing_assets", {})
    missing_routing = sorted(
        key for key, value in routing.items() if value == "MISSING_SOURCE"
    )
    if not provenance_exact:
        errors.append("provenance_ledger_not_exact_25_unique_categories")
    if provenance_proof_failures:
        errors.append("provenance_proof_failures")

    downloaded_count = int(acquisition.get("downloaded_asset_count", -1))
    hashed_count = int(acquisition.get("hashed_asset_count", -1))
    acquisition_consistent = downloaded_count == 0 and hashed_count == 0 and all(
        candidate.get("sha256") is None
        and str(candidate.get("download_status", "")).startswith("NOT_DOWNLOADED")
        for candidate in acquisition.get("source_candidates", [])
    )
    if not acquisition_consistent:
        errors.append("acquisition_ledger_download_or_hash_claim_requires_review")

    production_ready = (
        not errors
        and not production_proof_failures
        and not provenance_proof_failures
        and state_counts["PRODUCTION_BOUND"] == len(EXPECTED)
        and provenance_missing_count == 0
        and not missing_routing
        and provenance.get("acceptance") == "READY_FOR_AUDIBLE_ACCEPTANCE"
    )
    status = (
        "PRODUCTION_READY"
        if production_ready
        else "CONTRACT_VALID_BLOCKED_MISSING_SOURCE"
        if not errors and state_counts["MISSING_SOURCE"] == len(EXPECTED)
        else "CONTRACT_INVALID_OR_PARTIAL"
    )
    report = {
        "schema": "skyguard.phase5.audio-acquisition-contract-audit.v1",
        "brief_path": str(BRIEFS),
        "expected_category_count": len(EXPECTED),
        "actual_category_count": len(entries),
        "state_counts": state_counts,
        "missing_categories": missing,
        "extra_categories": extra,
        "duplicate_categories": duplicates,
        "missing_routing_assets": missing_routing,
        "production_proof_failures": production_proof_failures,
        "provenance_missing_source_count": provenance_missing_count,
        "provenance_proof_failures": provenance_proof_failures,
        "acquisition_downloaded_count": downloaded_count,
        "acquisition_hashed_count": hashed_count,
        "acquisition_consistent": acquisition_consistent,
        "contract_errors": errors,
        "contract_valid": not errors,
        "production_ready": production_ready,
        "status": status,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with REPORT.open("w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
    print(json.dumps(report, indent=2))

    if errors:
        return 2
    if args.require_ready and not production_ready:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
