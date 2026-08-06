"""Offline evidence gate for the five P5-A Yak-52 identity sources."""

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT / "Docs/AAA_Review/PHASE5_P5A_IDENTITY_SOURCE_EVIDENCE_CONTRACT.json"
)
ACQUISITION_PATH = (
    ROOT / "Docs/AAA_Review/PHASE5_AUDIO_SOURCE_ACQUISITION_LEDGER.json"
)
PROVENANCE_PATH = (
    ROOT / "Docs/AAA_Review/PHASE5_AUDIO_PRODUCTION_PROVENANCE_TEMPLATE.json"
)
AUDIT_PATH = (
    ROOT / "Saved/Reports/PHASE5_P5A_IDENTITY_SOURCE_EVIDENCE_AUDIT.json"
)
IDENTITY = {
    "EngineIdle",
    "EngineCruise",
    "EnginePower",
    "Propeller",
    "OpenCockpitWind",
}
RESEARCH_IDS = {
    "FS_CRAIGSMITH_437835",
    "FS_CRAIGSMITH_437726",
    "FS_PRSHS70_445137",
    "FS_COLUMBIA23_395684",
}
APPROVALS = {
    "RIGHTS_APPROVED",
    "SEMANTIC_MATCH_APPROVED",
    "TECHNICAL_INGEST_APPROVED",
}


def validate(contract, acquisition, provenance):
    errors = []
    if contract.get("schema") != "skyguard.phase5.p5a-identity-source-evidence.v1":
        errors.append("unexpected evidence-contract schema")
    if set(contract.get("identity_categories", [])) != IDENTITY:
        errors.append("identity category set must be the exact five P5-A beds")

    policy = contract.get("source_candidate_policy", {})
    for key in (
        "generic_aircraft_reference_is_candidate",
        "license_only_is_sufficient",
        "source_page_http_200_is_sufficient",
        "synthetic_wind_is_authentic_cockpit_source",
        "download_before_candidate_acceptance_allowed",
    ):
        if policy.get(key) is not False:
            errors.append("unsafe candidate policy: " + key)

    if set(contract.get("rights_evidence_required", [])) != {
        "rights_evidence_id",
        "legal_rights_holder_name",
        "signed_recording_or_license_agreement_path",
        "agreement_sha256",
        "signing_date_utc",
        "commercial_interactive_game_use_allowed",
        "modification_and_derivative_creation_allowed",
        "cooked_build_embedding_and_distribution_allowed",
        "marketing_and_trailer_use_allowed",
        "territory",
        "term",
        "raw_source_redistribution_policy",
        "aircraft_owner_or_operator_permission",
        "recording_location_permission",
        "performer_or_crew_releases_if_audible",
    }:
        errors.append("rights evidence field set drift")

    rights = contract.get("rights_acceptance_values", {})
    for key in (
        "commercial_interactive_game_use_allowed",
        "modification_and_derivative_creation_allowed",
        "cooked_build_embedding_and_distribution_allowed",
        "marketing_and_trailer_use_allowed",
    ):
        if rights.get(key) is not True:
            errors.append("rights acceptance does not require: " + key)
    if rights.get("raw_source_redistribution_policy") != "EXCLUDED_FROM_DISTRIBUTION":
        errors.append("raw-source redistribution policy is unsafe")
    if rights.get("territory") != "WORLDWIDE":
        errors.append("territory is not worldwide")

    semantic = contract.get("category_semantic_contracts", [])
    names = [item.get("category") for item in semantic]
    if len(semantic) != 5 or set(names) != IDENTITY or len(names) != len(set(names)):
        errors.append("semantic contracts must cover the exact five categories once")
    for item in semantic:
        if item.get("required_aircraft") != "Yak-52":
            errors.append("non-Yak semantic contract: " + str(item.get("category")))
        if not item.get("required_perspectives") or not item.get("forbidden_substitutes"):
            errors.append("incomplete semantic contract: " + str(item.get("category")))

    gate = contract.get("candidate_gate", {})
    if set(gate.get("required_independent_approvals", [])) != APPROVALS:
        errors.append("candidate approvals must include rights, semantic and ingest")
    if gate.get("binding_forbidden_until_audible_qa") is not True:
        errors.append("binding is not blocked pending audible QA")
    if gate.get("audition_does_not_equal_production_binding") is not True:
        errors.append("audition is incorrectly allowed to imply binding")

    reviewed = contract.get("reviewed_research_candidates", [])
    reviewed_ids = {item.get("candidate_id") for item in reviewed}
    if reviewed_ids != RESEARCH_IDS or len(reviewed) != 4:
        errors.append("reviewed identity research set drift")
    for item in reviewed:
        if item.get("semantic_match") is not False:
            errors.append("generic research incorrectly has semantic match")
        if not str(item.get("disposition", "")).startswith("REJECTED_"):
            errors.append("semantic mismatch was not rejected")

    acquisition_candidates = {
        item.get("candidate_id"): item
        for item in acquisition.get("source_candidates", [])
    }
    for candidate_id in RESEARCH_IDS:
        if candidate_id not in acquisition_candidates:
            errors.append("reviewed candidate missing from acquisition ledger: " + candidate_id)
    if acquisition.get("downloaded_asset_count") != 0:
        errors.append("acquisition ledger reports downloads")
    if acquisition.get("hashed_asset_count") != 0:
        errors.append("acquisition ledger reports hashes")

    approved = contract.get("approved_production_candidates", [])
    for candidate in approved:
        missing = [
            field
            for field in (
                "candidate_id",
                "rights_evidence",
                "semantic_evidence",
                "technical_evidence",
                "independent_approvals",
            )
            if not candidate.get(field)
        ]
        if missing:
            errors.append(
                "approved candidate lacks evidence: "
                + str(candidate.get("candidate_id"))
                + " fields="
                + ",".join(missing)
            )
        if set(candidate.get("independent_approvals", [])) != APPROVALS:
            errors.append("approved candidate lacks exact independent approvals")

    state = contract.get("current_state", {})
    if state.get("approved_production_candidate_count") != len(approved):
        errors.append("approved candidate count does not match list")
    if state.get("identity_sources_bound") != 0:
        errors.append("identity sources are falsely reported bound")
    if state.get("identity_sources_missing") != 5:
        errors.append("five identity sources are not explicitly missing")
    if state.get("production_ready") is not False:
        errors.append("evidence contract falsely reports production ready")

    provenance_entries = {
        item.get("category"): item
        for item in provenance.get("entries", [])
        if item.get("category") in IDENTITY
    }
    if set(provenance_entries) != IDENTITY:
        errors.append("provenance template lacks identity entries")
    for category, entry in provenance_entries.items():
        if entry.get("source_status") != "MISSING_SOURCE":
            errors.append("provenance no longer marks source missing: " + category)
        if any(
            entry.get(field)
            for field in ("source_sha256", "unreal_sound_asset", "license_identifier")
        ):
            errors.append("missing provenance entry contains source proof: " + category)

    return errors, len(approved)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-candidate", action="store_true")
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    acquisition = json.loads(ACQUISITION_PATH.read_text(encoding="utf-8"))
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    errors, approved_count = validate(contract, acquisition, provenance)
    state = contract.get("current_state", {})
    ready = bool(
        not errors
        and approved_count > 0
        and state.get("identity_sources_missing") == 0
        and state.get("production_ready") is True
    )
    result = {
        "schema": "skyguard.phase5.p5a-identity-source-evidence-audit.v1",
        "identity_category_count": len(contract.get("identity_categories", [])),
        "reviewed_research_candidate_count": len(
            contract.get("reviewed_research_candidates", [])
        ),
        "rejected_identity_mismatch_count": sum(
            1
            for item in contract.get("reviewed_research_candidates", [])
            if str(item.get("disposition", "")).startswith("REJECTED_")
        ),
        "approved_production_candidate_count": approved_count,
        "identity_sources_missing": state.get("identity_sources_missing"),
        "downloaded_identity_source_count": state.get(
            "downloaded_identity_source_count"
        ),
        "production_ready": ready,
        "errors": errors,
        "contract_valid": not errors,
        "status": (
            "INVALID_EVIDENCE_CONTRACT"
            if errors
            else "BLOCKED_NO_EVIDENCE_COMPLETE_YAK52_IDENTITY_SOURCE"
            if approved_count == 0
            else "CANDIDATE_EVIDENCE_COMPLETE_NOT_PRODUCTION_BOUND"
        ),
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if errors:
        return 2
    if args.require_candidate and approved_count == 0:
        return 3
    if args.require_ready and not ready:
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
