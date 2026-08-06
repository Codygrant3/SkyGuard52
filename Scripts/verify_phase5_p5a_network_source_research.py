"""Offline integrity gate for the dated P5-A network-source research."""

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
RESEARCH_PATH = (
    ROOT / "Docs/AAA_Review/PHASE5_P5A_NETWORK_SOURCE_RESEARCH_2026-08-02.json"
)
AUDIT_PATH = (
    ROOT / "Saved/Reports/PHASE5_P5A_NETWORK_SOURCE_RESEARCH_AUDIT.json"
)
IDENTITY = {
    "EngineIdle",
    "EngineCruise",
    "EnginePower",
    "Propeller",
    "OpenCockpitWind",
}


def validate(data):
    errors = []
    if data.get("schema") != "skyguard.phase5.p5a-network-source-research.v1":
        errors.append("unexpected schema")
    method = data.get("network_method", {})
    for field in ("audio_files_downloaded", "preview_files_downloaded", "assets_imported"):
        if method.get(field) != 0:
            errors.append(field + " must remain zero")

    license_sources = data.get("license_sources", [])
    pse = next(
        (item for item in license_sources if item.get("publisher") == "Pro Sound Effects"),
        None,
    )
    if not pse:
        errors.append("Pro Sound Effects license evidence missing")
    else:
        terms = pse.get("verified_terms", {})
        for field in (
            "commercial_synchronization",
            "all_media",
            "worldwide",
            "perpetual_for_lifetime_purchase",
            "editing_and_looping_allowed",
            "single_user_default",
            "multi_user_requires_separate_license",
        ):
            if terms.get(field) is not True:
                errors.append("PSE license term missing: " + field)
        if terms.get("standalone_redistribution_allowed") is not False:
            errors.append("standalone redistribution must be prohibited")

    candidates = data.get("production_candidates", [])
    candidate_ids = [item.get("candidate_id") for item in candidates]
    if len(candidates) != 5 or len(candidate_ids) != len(set(candidate_ids)):
        errors.append("expected five unique conditional source-page candidates")
    for item in candidates:
        if item.get("classification") != "CONDITIONAL_PRODUCTION_CANDIDATE":
            errors.append("candidate has invalid classification")
        if item.get("source_page_http_status") != 200:
            errors.append("candidate source page was not HTTP 200")
        if not str(item.get("source_page_url", "")).startswith(
            "https://www.prosoundeffects.com/sound-effects/"
        ):
            errors.append("candidate does not use direct publisher source page")
        if item.get("rights_state") != (
            "TERMS_VERIFIED_PURCHASE_AND_SEAT_CONFIRMATION_REQUIRED"
        ):
            errors.append("candidate rights state is overstated")
        if item.get("technical_state") != "NOT_DOWNLOADED_NOT_AUDITIONED":
            errors.append("candidate technical state is overstated")
        if item.get("source_status_must_remain") != "MISSING_SOURCE":
            errors.append("candidate improperly changes production source status")
        if not item.get("remaining_gates"):
            errors.append("candidate lacks remaining gates")

    disposition = data.get("category_disposition", [])
    categories = [item.get("category") for item in disposition]
    if len(disposition) != 5 or set(categories) != IDENTITY:
        errors.append("category disposition must cover exact identity five")
    wind = next(
        (item for item in disposition if item.get("category") == "OpenCockpitWind"),
        {},
    )
    if wind.get("conditional_production_candidate_count") != 0:
        errors.append("open-cockpit wind is falsely covered")
    if wind.get("status") != "BLOCKED_NO_EXPLICIT_OPEN_CANOPY_SOURCE":
        errors.append("open-cockpit wind does not remain blocked")

    blocked = data.get("blocked_or_ambiguous_sources", [])
    dcs = next(
        (item for item in blocked if item.get("source_id") == "DCS_YAK52_INSTALLED_AUDIO"),
        None,
    )
    if not dcs or dcs.get("classification") != "BLOCKED_NO_REUSE_OR_EXTRACTION_RIGHT":
        errors.append("DCS installed audio is not explicitly blocked")

    overall = data.get("overall_status", {})
    if overall.get("categories_with_conditional_candidate") != 4:
        errors.append("candidate-covered category count must be four")
    if overall.get("categories_without_candidate") != 1:
        errors.append("uncovered category count must be one")
    for field in ("licensed_source_count", "downloaded_source_count", "production_bound_count"):
        if overall.get(field) != 0:
            errors.append(field + " must remain zero")
    if overall.get("production_ready") is not False:
        errors.append("research falsely claims production readiness")

    action = data.get("next_authorized_acquisition_action", {})
    if action.get("purchase_or_download_authorized_by_this_research") is not False:
        errors.append("research improperly authorizes purchase or download")
    if action.get("recipient") != "licensing@prosoundeffects.com":
        errors.append("next action lacks publisher licensing contact")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-all-categories-covered", action="store_true")
    parser.add_argument("--require-production-ready", action="store_true")
    args = parser.parse_args()
    data = json.loads(RESEARCH_PATH.read_text(encoding="utf-8"))
    errors = validate(data)
    overall = data.get("overall_status", {})
    all_covered = overall.get("categories_without_candidate") == 0
    ready = bool(not errors and overall.get("production_ready") is True)
    result = {
        "schema": "skyguard.phase5.p5a-network-source-research-audit.v1",
        "conditional_candidate_page_count": len(data.get("production_candidates", [])),
        "categories_with_conditional_candidate": overall.get(
            "categories_with_conditional_candidate"
        ),
        "categories_without_candidate": overall.get("categories_without_candidate"),
        "reference_only_source_count": len(data.get("reference_only_sources", [])),
        "blocked_or_ambiguous_source_count": len(
            data.get("blocked_or_ambiguous_sources", [])
        ),
        "downloads": data.get("network_method", {}).get("audio_files_downloaded"),
        "production_ready": ready,
        "errors": errors,
        "contract_valid": not errors,
        "status": (
            "INVALID_RESEARCH_CONTRACT"
            if errors
            else "RESEARCH_COMPLETE_ACQUISITION_AUTHORIZATION_REQUIRED"
        ),
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if errors:
        return 2
    if args.require_all_categories_covered and not all_covered:
        return 3
    if args.require_production_ready and not ready:
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
