#!/usr/bin/env python3
"""Fail-closed Phase 5 runtime audio routing readiness audit.

This verifier intentionally distinguishes source-readable structure from
serialized Unreal topology and audible packaged-build acceptance.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def asset_to_file(project_root: Path, asset_path: str) -> Path:
    relative = asset_path.removeprefix("/Game/") + ".uasset"
    return project_root / "Content" / Path(relative)


def parse_enum_categories(header: str) -> list[str]:
    match = re.search(
        r"enum class ESkyguardProductionAudioCategory\s*:\s*uint8\s*\{(?P<body>.*?)\};",
        header,
        re.S,
    )
    if not match:
        return []
    return [
        item.strip().split("=")[0].strip()
        for item in match.group("body").split(",")
        if item.strip()
    ]


def expected_named_assets(
    briefs: dict[str, Any], runtime_contract: dict[str, Any]
) -> tuple[list[str], list[str]]:
    attenuation_names = sorted(
        {entry["attenuation_contract"] for entry in briefs["categories"]}
    )
    concurrency_names = sorted(
        {entry["concurrency_contract"] for entry in briefs["categories"]}
    )
    attenuation = [
        f"{runtime_contract['attenuation_asset_root']}/ATT_{name}"
        for name in attenuation_names
    ]
    concurrency = [
        f"{runtime_contract['concurrency_asset_root']}/CON_{name}"
        for name in concurrency_names
    ]
    return attenuation, concurrency


def validate_routing_primitive_specs(
    specs: dict[str, Any],
    briefs: dict[str, Any],
    runtime_contract: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    expected_attenuation = {
        entry["attenuation_contract"] for entry in briefs["categories"]
    }
    expected_concurrency = {
        entry["concurrency_contract"] for entry in briefs["categories"]
    }
    attenuation = specs.get("attenuation", [])
    concurrency = specs.get("concurrency", [])
    metasounds = specs.get("metasound_interfaces", [])
    attenuation_names = [entry.get("name") for entry in attenuation]
    concurrency_names = [entry.get("name") for entry in concurrency]
    metasound_names = [entry.get("name") for entry in metasounds]
    expected_metasounds = {
        path.rsplit("/", 1)[-1] for path in runtime_contract["metasound_assets"]
    }
    if len(attenuation_names) != len(set(attenuation_names)) or set(
        attenuation_names
    ) != expected_attenuation:
        errors.append("attenuation primitive specs are not exact and unique")
    if len(concurrency_names) != len(set(concurrency_names)) or set(
        concurrency_names
    ) != expected_concurrency:
        errors.append("concurrency primitive specs are not exact and unique")
    if len(metasound_names) != len(set(metasound_names)) or set(
        metasound_names
    ) != expected_metasounds:
        errors.append("MetaSound interface specs are not exact and unique")
    for entry in attenuation:
        name = str(entry.get("name", "UNKNOWN"))
        if entry.get("spatialize") not in (True, False) or entry.get(
            "attenuate"
        ) not in (True, False):
            errors.append(name + ": attenuation booleans invalid")
        for field in ("inner_radius_cm", "falloff_cm"):
            value = entry.get(field)
            if not isinstance(value, (int, float)) or value < 0:
                errors.append(name + ": invalid " + field)
    allowed_rules = {
        "PreventNew",
        "StopOldest",
        "StopFarthestThenPreventNew",
        "StopFarthestThenOldest",
        "StopLowestPriority",
        "StopQuietest",
        "StopLowestPriorityThenPreventNew",
    }
    for entry in concurrency:
        name = str(entry.get("name", "UNKNOWN"))
        if not isinstance(entry.get("max_count"), int) or not (
            1 <= entry["max_count"] <= 32
        ):
            errors.append(name + ": invalid max_count")
        if entry.get("resolution_rule") not in allowed_rules:
            errors.append(name + ": invalid resolution_rule")
        for field in ("retrigger_seconds", "voice_steal_release_seconds"):
            value = entry.get(field)
            if not isinstance(value, (int, float)) or value < 0:
                errors.append(name + ": invalid " + field)
    composed = {
        category
        for entry in metasounds
        for category in entry.get("categories", [])
    }
    governed = {entry["category"] for entry in briefs["categories"]}
    if composed != governed:
        errors.append("MetaSound interface category coverage mismatch")
    if any(
        not entry.get("inputs") or not entry.get("outputs")
        for entry in metasounds
    ):
        errors.append("MetaSound interface input or output contract missing")
    return errors


def find_latest_primitive_fresh_audit(project_root: Path) -> dict[str, Any]:
    candidates = list(
        (
            project_root / "Saved" / "Reports" / "Phase5RoutingPrimitives"
        ).glob("attempt_*/fresh_audit.json")
    )
    canonical = (
        project_root
        / "Saved"
        / "Reports"
        / "PHASE5_ROUTING_PRIMITIVES_FRESH_AUDIT.json"
    )
    if canonical.exists():
        candidates.append(canonical)
    for path in sorted(
        candidates, key=lambda item: item.stat().st_mtime, reverse=True
    ):
        try:
            data = load_json(path)
        except (OSError, ValueError):
            continue
        accepted = bool(
            data.get("status")
            == "PASS_ROUTING_PRIMITIVES_SOURCES_AND_METASOUNDS_MISSING"
            and data.get("attenuation_asset_count") == 15
            and data.get("concurrency_asset_count") == 14
            and data.get("bank_routing_binding_count") == 25
            and data.get("explicit_missing_source_count") == 25
            and data.get("metasound_shell_count") == 0
            and data.get("production_ready") is False
            and not data.get("errors")
        )
        return {
            "present": True,
            "path": str(path),
            "accepted_routing_only": accepted,
            "contract_hash_bound": False,
            "note": (
                "Fresh process proves the 29 serialized routing primitives and "
                "25 routing-only bank bindings. This receipt predates contract "
                "hash binding and does not cover MetaSound topology or audio."
            ),
        }
    return {
        "present": False,
        "path": None,
        "accepted_routing_only": False,
        "contract_hash_bound": False,
        "note": "No routing-primitives fresh-process receipt found.",
    }


def find_latest_metasound_topology_audit(
    project_root: Path,
) -> dict[str, Any]:
    candidates = list(
        (
            project_root
            / "Saved"
            / "Reports"
            / "Phase5MetaSoundTopology"
        ).glob("attempt_*/fresh_topology_audit.json")
    )
    canonical = (
        project_root
        / "Saved"
        / "Reports"
        / "PHASE5_METASOUND_TOPOLOGY_FRESH_AUDIT.json"
    )
    if canonical.exists():
        candidates.append(canonical)
    for path in sorted(
        candidates, key=lambda item: item.stat().st_mtime, reverse=True
    ):
        try:
            data = load_json(path)
        except (OSError, ValueError):
            continue
        accepted = bool(
            data.get("status")
            == "PASS_FRESH_GOVERNED_METASOUND_TOPOLOGY_SOURCES_MISSING"
            and data.get("graph_count") == 6
            and data.get("primitive_count") == 29
            and data.get("governed_asset_count") == 35
            and data.get("authentic_source_count") == 0
            and data.get("metasound_soundwave_binding_count") == 0
            and data.get("procedural_generator_count") == 0
            and data.get("fresh_for_current_contract") is True
            and data.get("production_ready") is False
            and data.get("shipping_allowed") is False
            and data.get("packaged_audible_acceptance") is False
            and data.get("production_bank", {}).get(
                "explicit_missing_source_count"
            )
            == 25
            and data.get("production_bank", {}).get(
                "bound_production_source_count"
            )
            == 0
            and not data.get("errors")
        )
        return {
            "present": True,
            "path": str(path),
            "accepted_topology_only": accepted,
            "contract_hash_bound": accepted,
            "contract_bundle_sha256": data.get(
                "contract_bundle", {}
            ).get("bundle_sha256"),
            "note": (
                "Fresh process proves six connected silent-until-sourced "
                "MetaSound topologies plus current hashes for all 29 routing "
                "primitives. Authentic sources and audible acceptance remain "
                "separate fail-closed requirements."
            ),
        }
    return {
        "present": False,
        "path": None,
        "accepted_topology_only": False,
        "contract_hash_bound": False,
        "contract_bundle_sha256": None,
        "note": "No contract-hash-bound MetaSound topology receipt found.",
    }


def evaluate(
    project_root: Path,
    *,
    virtual_asset_paths: set[str] | None = None,
    source_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    docs = project_root / "Docs" / "AAA_Review"
    source = project_root / "Source" / "Skyguard52"
    contract = load_json(docs / "PHASE5_AUDIO_RUNTIME_ROUTING_READINESS_CONTRACT.json")
    import_contract = load_json(
        docs / "PHASE5_AUDIO_UNREAL_IMPORT_NAMING_LOUDNESS_CONTRACT.json"
    )
    briefs = load_json(docs / "PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json")
    acquisition = load_json(
        docs / "PHASE5_AUTHENTIC_AUDIO_ACQUISITION_MANIFEST.json"
    )
    routing_specs = load_json(
        docs / "PHASE5_AUDIO_ROUTING_PRIMITIVE_SPECS.json"
    )

    source_overrides = source_overrides or {}

    def read_source(name: str) -> str:
        return source_overrides.get(name, (source / name).read_text(encoding="utf-8-sig"))

    director_text = read_source("SkyguardAudioDirectorComponent.cpp")
    bank_source_text = read_source("SkyguardAudioProductionBank.cpp")
    bank_header = read_source("SkyguardAudioProductionBank.h")
    categories = list(import_contract["required_bank_categories"])
    brief_categories = [entry["category"] for entry in briefs["categories"]]
    enum_categories = parse_enum_categories(bank_header)

    assets = virtual_asset_paths
    if assets is None:
        assets = {
            "/" + path.relative_to(project_root / "Content").as_posix()[:-7]
            for path in (project_root / "Content").rglob("*.uasset")
        }
        assets = {"/Game/" + path.removeprefix("/") for path in assets}

    attenuation_assets, concurrency_assets = expected_named_assets(briefs, contract)
    primitive_spec_errors = validate_routing_primitive_specs(
        routing_specs, briefs, contract
    )
    groups = {
        "routing": list(contract["routing_assets"]),
        "metasounds": list(contract["metasound_assets"]),
        "attenuation": attenuation_assets,
        "concurrency": concurrency_assets,
        "production_bank": [
            "/Game/Skyguard/Audio/Production/DA_P5A_ProductionAudioBank"
        ],
    }
    asset_checks: dict[str, Any] = {}
    for group_name, expected in groups.items():
        present = sorted(path for path in expected if path in assets)
        missing = sorted(set(expected) - set(present))
        asset_checks[group_name] = {
            "expected_count": len(expected),
            "present_count": len(present),
            "present": present,
            "missing": missing,
        }

    covered_categories = sorted(
        {
            category
            for group in contract["composition_coverage"].values()
            for category in group
        }
    )
    coverage_missing = sorted(set(categories) - set(covered_categories))
    coverage_unknown = sorted(set(covered_categories) - set(categories))

    required_markers = contract["runtime_source_markers"]["required"]
    forbidden_markers = contract["runtime_source_markers"]["forbidden"]
    missing_markers = [marker for marker in required_markers if marker not in director_text]
    forbidden_found = [marker for marker in forbidden_markers if marker in director_text]
    gameplay_marker_errors: dict[str, list[str]] = {}
    for source_name, markers in contract.get("gameplay_source_markers", {}).items():
        gameplay_text = read_source(source_name)
        missing = [marker for marker in markers if marker not in gameplay_text]
        if missing:
            gameplay_marker_errors[source_name] = missing
    production_bank_markers_missing = [
        marker
        for marker in contract.get("production_bank_source_markers", [])
        if marker not in bank_source_text
    ]

    binding_matches = dict(
        re.findall(
            r"BindEvent\(ESkyguardAudioEvent::(\w+),\s*"
            r"ESkyguardProductionAudioCategory::(\w+)\);",
            director_text,
        )
    )
    expected_bindings = contract["direct_event_bindings"]
    binding_errors = {
        key: {"expected": value, "actual": binding_matches.get(key)}
        for key, value in expected_bindings.items()
        if binding_matches.get(key) != value
    }

    mission_prime_files: list[str] = []
    missing_mission_prime_files: list[str] = []
    for mission in range(1, 11):
        name = f"SkyguardMission{mission:02d}IntegrationDirector.cpp"
        text = read_source(name)
        if "AudioDirector->PrimeConfiguredAssets()" in text:
            mission_prime_files.append(name)
        else:
            missing_mission_prime_files.append(name)

    acquisition_entries = acquisition["entries"]
    acquisition_categories = [
        category
        for entry in acquisition_entries
        for category in entry.get("bank_bindings", [])
    ]
    approved_source_states = {"PROJECT_OWNED_RECORDING", "LICENSED_THIRD_PARTY"}
    approved_sources = [
        entry["category_id"]
        for entry in acquisition_entries
        if entry.get("acquisition_state") in approved_source_states
    ]

    legacy_uassets = sorted(
        "/Game/" + path.relative_to(project_root / "Content").as_posix()[:-7]
        for path in (project_root / "Content" / "Skyguard" / "Audio" / "Imported").rglob(
            "*.uasset"
        )
    ) if (project_root / "Content" / "Skyguard" / "Audio" / "Imported").exists() else []

    serialized_report = (
        project_root / "Saved" / "Reports" / "PHASE5_P5A_ROUTING_FRESH_AUDIT.json"
    )
    primitive_serialized_audit = find_latest_primitive_fresh_audit(project_root)
    topology_serialized_audit = find_latest_metasound_topology_audit(
        project_root
    )
    serialized_audit = {
        "required": True,
        "present": (
            serialized_report.exists()
            or primitive_serialized_audit["present"]
            or topology_serialized_audit["present"]
        ),
        "fresh_for_current_contract": topology_serialized_audit[
            "accepted_topology_only"
        ],
        "scope": (
            "P5A_BASE_ROUTING_PLUS_29_PRIMITIVES_PLUS_6_GOVERNED_METASOUND_"
            "TOPOLOGIES_WHEN_ACCEPTED; AUTHENTIC_SOURCE_AND_AUDIBLE_"
            "ACCEPTANCE_REMAIN_SEPARATE"
        ),
        "insufficient_for_final_graph": not topology_serialized_audit[
            "accepted_topology_only"
        ],
        "insufficient_for_audible_production": True,
        "routing_primitives": primitive_serialized_audit,
        "metasound_topology": topology_serialized_audit,
        "note": (
            "A passing topology receipt may prove six connected MetaSound "
            "graphs and contract freshness for those graphs plus all 29 "
            "routing primitives. It intentionally does not prove approved "
            "sources, final mix behavior, or packaged audible acceptance."
        ),
    }

    packaged_acceptance = (
        project_root / "Saved" / "Reports" / "PHASE5_AUDIO_PACKAGED_AUDIBLE_ACCEPTANCE.json"
    )
    packaged_audit = {
        "required": True,
        "present": packaged_acceptance.exists(),
        "accepted": False,
    }
    if packaged_acceptance.exists():
        try:
            packaged_data = load_json(packaged_acceptance)
            packaged_audit["accepted"] = packaged_data.get("status") == "PASS"
        except (OSError, ValueError):
            packaged_audit["parse_error"] = True

    structural_errors: list[str] = []
    if len(categories) != contract["required_category_count"]:
        structural_errors.append("required_category_count_mismatch")
    if categories != brief_categories:
        structural_errors.append("category_brief_order_or_membership_mismatch")
    if categories != enum_categories:
        structural_errors.append("cpp_enum_order_or_membership_mismatch")
    if sorted(acquisition_categories) != sorted(categories):
        structural_errors.append("acquisition_binding_coverage_mismatch")
    if coverage_missing or coverage_unknown:
        structural_errors.append("metasound_composition_coverage_mismatch")
    if missing_markers:
        structural_errors.append("runtime_source_required_marker_missing")
    if forbidden_found:
        structural_errors.append("runtime_source_synchronous_load_forbidden")
    if gameplay_marker_errors:
        structural_errors.append("gameplay_audio_routing_marker_missing")
    if production_bank_markers_missing:
        structural_errors.append("production_bank_routing_guard_missing")
    if binding_errors or len(binding_matches) != contract["required_event_definition_count"]:
        structural_errors.append("direct_event_binding_mismatch")
    if missing_mission_prime_files:
        structural_errors.append("mission_briefing_prime_coverage_mismatch")
    if primitive_spec_errors:
        structural_errors.append("routing_primitive_specs_invalid")

    required_asset_groups_ready = all(
        not asset_checks[group]["missing"]
        for group in ("routing", "metasounds", "attenuation", "concurrency", "production_bank")
    )
    sources_ready = len(approved_sources) == len(categories)
    production_ready = bool(
        not structural_errors
        and required_asset_groups_ready
        and sources_ready
        and serialized_audit["fresh_for_current_contract"]
        and packaged_audit["accepted"]
        and not legacy_uassets
    )
    structural_valid = not structural_errors
    status = (
        "PASS_PHASE5_AUDIO_RUNTIME_ROUTING_READY"
        if production_ready
        else (
            (
                "CONTRACT_VALID_EXTERNAL_AUDIO_AND_ACCEPTANCE_REQUIRED"
                if (
                    structural_valid
                    and required_asset_groups_ready
                    and serialized_audit["fresh_for_current_contract"]
                )
                else "CONTRACT_VALID_AUTHORING_BLOCKED"
            )
            if structural_valid
            else "FAIL_RUNTIME_ROUTING_CONTRACT"
        )
    )

    return {
        "schema": "skyguard.phase5.audio-runtime-routing-readiness-audit.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "structural_contract_valid": structural_valid,
        "runtime_routing_ready": production_ready,
        "production_ready": production_ready,
        "truth_boundary": {
            "asset_presence_is_serialized_topology_proof": False,
            "offline_scan_is_audible_acceptance": False,
            "media_downloaded_or_imported_by_verifier": False,
        },
        "categories": {
            "required_count": len(categories),
            "brief_count": len(brief_categories),
            "cpp_enum_count": len(enum_categories),
            "composition_covered_count": len(covered_categories),
            "composition_missing": coverage_missing,
            "composition_unknown": coverage_unknown,
        },
        "runtime_source": {
            "required_markers_missing": missing_markers,
            "forbidden_markers_found": forbidden_found,
            "gameplay_marker_errors": gameplay_marker_errors,
            "production_bank_markers_missing": production_bank_markers_missing,
            "event_binding_count": len(binding_matches),
            "event_binding_errors": binding_errors,
            "mission_prime_count": len(mission_prime_files),
            "missions_missing_prime": missing_mission_prime_files,
        },
        "routing_primitive_specs": {
            "attenuation_count": len(routing_specs.get("attenuation", [])),
            "concurrency_count": len(routing_specs.get("concurrency", [])),
            "metasound_interface_count": len(
                routing_specs.get("metasound_interfaces", [])
            ),
            "errors": primitive_spec_errors,
        },
        "assets": asset_checks,
        "authentic_sources": {
            "required_count": len(categories),
            "manifest_entry_count": len(acquisition_entries),
            "approved_count": len(approved_sources),
            "approved_categories": approved_sources,
            "missing_or_unapproved_count": len(categories) - len(approved_sources),
        },
        "serialized_unreal_audit": serialized_audit,
        "packaged_audible_acceptance": packaged_audit,
        "shipping_boundary": {
            "legacy_imported_uasset_count": len(legacy_uassets),
            "legacy_imported_uassets": legacy_uassets,
        },
        "structural_errors": structural_errors,
        "external_blocks": [
            item
            for item, blocked in (
                ("authentic licensed or project-owned sources", not sources_ready),
                ("MetaSound authoring", bool(asset_checks["metasounds"]["missing"])),
                ("attenuation asset authoring", bool(asset_checks["attenuation"]["missing"])),
                ("concurrency asset authoring", bool(asset_checks["concurrency"]["missing"])),
                (
                    "fresh final serialized Unreal graph audit",
                    not serialized_audit["fresh_for_current_contract"],
                ),
                ("packaged audible acceptance", not packaged_audit["accepted"]),
                ("legacy Imported audio removal from shipping boundary", bool(legacy_uassets)),
            )
            if blocked
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--require-runtime-ready", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    report = evaluate(args.project_root.resolve())
    report_path = args.report or (
        args.project_root / "Saved" / "Reports"
        / "PHASE5_AUDIO_RUNTIME_ROUTING_READINESS_AUDIT.json"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["structural_contract_valid"]:
        return 2
    if args.require_runtime_ready and not report["runtime_routing_ready"]:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
