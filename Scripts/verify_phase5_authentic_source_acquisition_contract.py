"""Offline, fail-closed verifier for the immutable Phase 5 source contract.

This verifier never downloads, auditions, imports, or mutates media or Unreal
assets. It proves that the acquisition inventory still describes the exact 25
null WaveAsset inputs in the accepted MetaSound topology and that all production
claims remain blocked while authentic source evidence is absent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = (
    ROOT
    / "Docs/AAA_Review/PHASE5_AUTHENTIC_SOURCE_ACQUISITION_CONTRACT.json"
)
REPORT_ROOT = ROOT / "Saved/Reports/Phase5AuthenticSourceAcquisition"
EXPECTED_SCHEMA = "skyguard.phase5.authentic-source-acquisition-contract.v1"
EXPECTED_CONTRACT_ID = "phase5-authentic-source-acquisition-20260802-v1"
EXPECTED_TOPOLOGY_BUNDLE_SHA256 = (
    "296f1ce6cfff00b949d8ae8e83461eedf73f56321dc34c0d27a9fbb4cc9afcfd"
)
EXPECTED_ATTEMPT_ID = "attempt_20260802T151943423Z_7fd745f0"
EXPECTED_SLOT_COUNT = 25
EXPECTED_GRAPH_COUNT = 6
EXPECTED_CURRENT_STATE = "MISSING_SOURCE"
ALLOWED_ROUTES = {"PROJECT_OWNED_RECORDING", "LICENSED_LIBRARY"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def game_asset_to_file(asset_path: str) -> Path:
    prefix = "/Game/"
    if not asset_path.startswith(prefix):
        raise ValueError(f"Not a /Game asset path: {asset_path}")
    return ROOT / "Content" / (asset_path[len(prefix) :] + ".uasset")


def relative_project_path(raw: str) -> Path:
    value = Path(raw)
    if value.is_absolute():
        raise ValueError(f"Contract authority path must be project-relative: {raw}")
    resolved = (ROOT / value).resolve()
    if ROOT.resolve() not in resolved.parents:
        raise ValueError(f"Contract authority path escapes project root: {raw}")
    return resolved


def unique_index(
    entries: list[dict[str, Any]],
    key: str,
    errors: list[str],
    label: str,
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        value = entry.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"{label}[{index}]:missing_{key}")
            continue
        if value in result:
            errors.append(f"{label}:duplicate_{key}:{value}")
            continue
        result[value] = entry
    return result


def topology_slots(
    topology: dict[str, Any], errors: list[str]
) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    graphs = topology.get("graphs", [])
    if not isinstance(graphs, list) or len(graphs) != EXPECTED_GRAPH_COUNT:
        errors.append("topology:expected_exactly_6_graphs")
        return result
    for graph in graphs:
        graph_name = graph.get("name")
        for category in graph.get("categories", []):
            category_name = category.get("category")
            if not isinstance(category_name, str) or not category_name:
                errors.append(f"topology:{graph_name}:category_name_missing")
                continue
            if category_name in result:
                errors.append(f"topology:duplicate_category:{category_name}")
                continue
            result[category_name] = {
                "category": category_name,
                "graph": str(graph_name),
                "wave_input": str(category.get("wave_input")),
            }
    if len(result) != EXPECTED_SLOT_COUNT:
        errors.append(f"topology:expected_25_slots_got_{len(result)}")
    return result


def fresh_audit_null_slots(
    audit: dict[str, Any], errors: list[str]
) -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    for graph in audit.get("graph_reports", []):
        graph_name = str(graph.get("name"))
        if graph.get("authentic_source_count") != 0:
            errors.append(f"fresh_audit:{graph_name}:authentic_source_count_not_zero")
        for item in graph.get("null_wave_asset_defaults", []):
            wave_input = str(item.get("name"))
            key = f"{graph_name}:{wave_input}"
            if key in result:
                errors.append(f"fresh_audit:duplicate_null_slot:{key}")
                continue
            result[key] = (graph_name, wave_input)
            if item.get("contains_game_asset_path") is not False:
                errors.append(f"fresh_audit:{key}:contains_game_asset_path")
    if len(result) != EXPECTED_SLOT_COUNT:
        errors.append(f"fresh_audit:expected_25_null_slots_got_{len(result)}")
    return result


def validate_contract(
    contract: dict[str, Any], contract_path: Path = CONTRACT_PATH
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    input_hashes: dict[str, str] = {}

    if contract.get("schema") != EXPECTED_SCHEMA:
        errors.append("contract:schema_mismatch")
    if contract.get("contract_id") != EXPECTED_CONTRACT_ID:
        errors.append("contract:id_mismatch")

    immutability = contract.get("immutability_policy", {})
    if immutability.get("change_method") != (
        "Create a new versioned contract file and a new immutable verification "
        "attempt; never silently rewrite accepted requirements or evidence."
    ):
        errors.append("contract:immutability_change_method_mismatch")
    if immutability.get("contract_hash_algorithm") != "SHA-256":
        errors.append("contract:hash_algorithm_must_be_sha256")
    if immutability.get("external_evidence_must_be_content_hashed") is not True:
        errors.append("contract:external_evidence_hashing_not_required")
    if (
        immutability.get(
            "source_media_must_remain_outside_unreal_content_until_governed_import"
        )
        is not True
    ):
        errors.append("contract:source_media_build_exclusion_not_required")

    boundary = contract.get("accepted_topology_boundary", {})
    if boundary.get("attempt_id") != EXPECTED_ATTEMPT_ID:
        errors.append("boundary:accepted_attempt_id_mismatch")
    if boundary.get("attempt_status") != "PASS_TOPOLOGY_ONLY_SOURCES_MISSING":
        errors.append("boundary:accepted_attempt_status_mismatch")
    if (
        boundary.get("topology_contract_bundle_sha256")
        != EXPECTED_TOPOLOGY_BUNDLE_SHA256
    ):
        errors.append("boundary:topology_bundle_sha256_mismatch")
    for field, expected in (
        ("graph_count", EXPECTED_GRAPH_COUNT),
        ("required_source_slot_count", EXPECTED_SLOT_COUNT),
        ("authentic_source_count", 0),
        ("metasound_soundwave_binding_count", 0),
    ):
        if boundary.get(field) != expected:
            errors.append(f"boundary:{field}_mismatch")
    if boundary.get("wave_asset_defaults_must_remain_null") is not True:
        errors.append("boundary:null_wave_assets_not_required")

    hashed_authorities: list[tuple[str, str, str]] = []
    for label, path_field, hash_field in (
        ("accepted_status", "status_path", "status_sha256"),
        ("accepted_fresh_audit", "fresh_audit_path", "fresh_audit_sha256"),
        (
            "topology_contract",
            "topology_contract_path",
            "topology_contract_sha256",
        ),
    ):
        raw_path = boundary.get(path_field)
        expected_hash = boundary.get(hash_field)
        if not isinstance(raw_path, str) or not raw_path:
            errors.append(f"boundary:{path_field}_missing")
            continue
        if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(
            expected_hash
        ):
            errors.append(f"boundary:{hash_field}_invalid")
            continue
        hashed_authorities.append((label, raw_path, expected_hash))

    authority_inputs = contract.get("authority_inputs", [])
    if not isinstance(authority_inputs, list) or len(authority_inputs) != 4:
        errors.append("contract:expected_exactly_4_authority_inputs")
        authority_inputs = []
    for entry in authority_inputs:
        raw_path = entry.get("path")
        expected_hash = entry.get("sha256")
        if not isinstance(raw_path, str) or not raw_path:
            errors.append("authority_input:path_missing")
            continue
        if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(
            expected_hash
        ):
            errors.append(f"authority_input:{raw_path}:sha256_invalid")
            continue
        hashed_authorities.append(("authority_input", raw_path, expected_hash))

    loaded_by_path: dict[str, dict[str, Any]] = {}
    for label, raw_path, expected_hash in hashed_authorities:
        try:
            path = relative_project_path(raw_path)
        except ValueError as exc:
            errors.append(f"{label}:{exc}")
            continue
        if not path.is_file():
            errors.append(f"{label}:missing_file:{raw_path}")
            continue
        actual_hash = sha256_file(path)
        input_hashes[raw_path] = actual_hash
        if actual_hash != expected_hash:
            errors.append(f"{label}:hash_mismatch:{raw_path}")
            continue
        try:
            loaded_by_path[raw_path] = read_json(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{label}:invalid_json:{raw_path}:{exc}")

    topology_path = str(boundary.get("topology_contract_path", ""))
    status_path = str(boundary.get("status_path", ""))
    fresh_audit_path = str(boundary.get("fresh_audit_path", ""))
    topology = loaded_by_path.get(topology_path, {})
    status = loaded_by_path.get(status_path, {})
    fresh_audit = loaded_by_path.get(fresh_audit_path, {})

    if status.get("attempt_id") != EXPECTED_ATTEMPT_ID:
        errors.append("accepted_status:attempt_id_mismatch")
    if status.get("state") != "PASS_TOPOLOGY_ONLY_SOURCES_MISSING":
        errors.append("accepted_status:state_mismatch")
    if status.get("authentic_source_count") != 0:
        errors.append("accepted_status:authentic_source_count_not_zero")
    if status.get("expected_missing_source_count") != EXPECTED_SLOT_COUNT:
        errors.append("accepted_status:expected_missing_source_count_mismatch")
    if status.get("production_ready") is not False:
        errors.append("accepted_status:production_ready_not_false")
    if status.get("shipping_allowed") is not False:
        errors.append("accepted_status:shipping_allowed_not_false")

    if fresh_audit.get("fresh_for_current_contract") is not True:
        errors.append("fresh_audit:not_fresh_for_current_contract")
    if fresh_audit.get("authentic_source_count") != 0:
        errors.append("fresh_audit:authentic_source_count_not_zero")
    if fresh_audit.get("metasound_soundwave_binding_count") != 0:
        errors.append("fresh_audit:soundwave_binding_count_not_zero")
    if fresh_audit.get("production_ready") is not False:
        errors.append("fresh_audit:production_ready_not_false")
    if fresh_audit.get("shipping_allowed") is not False:
        errors.append("fresh_audit:shipping_allowed_not_false")
    if fresh_audit.get("packaged_audible_acceptance") is not False:
        errors.append("fresh_audit:packaged_audible_acceptance_not_false")
    if fresh_audit.get("errors") != []:
        errors.append("fresh_audit:contains_errors")

    topo_slots = topology_slots(topology, errors)
    fresh_nulls = fresh_audit_null_slots(fresh_audit, errors)

    brief_path = next(
        (
            str(item.get("path"))
            for item in authority_inputs
            if str(item.get("path", "")).endswith(
                "PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json"
            )
        ),
        "",
    )
    ledger_path = next(
        (
            str(item.get("path"))
            for item in authority_inputs
            if str(item.get("path", "")).endswith(
                "PHASE5_AUDIO_SOURCE_ACQUISITION_LEDGER.json"
            )
        ),
        "",
    )
    manifest_path = next(
        (
            str(item.get("path"))
            for item in authority_inputs
            if str(item.get("path", "")).endswith(
                "PHASE5_AUTHENTIC_AUDIO_ACQUISITION_MANIFEST.json"
            )
        ),
        "",
    )
    briefs = loaded_by_path.get(brief_path, {})
    ledger = loaded_by_path.get(ledger_path, {})
    acquisition_manifest = loaded_by_path.get(manifest_path, {})

    brief_entries = briefs.get("categories", [])
    if not isinstance(brief_entries, list):
        errors.append("briefs:categories_not_array")
        brief_entries = []
    brief_by_category = unique_index(
        brief_entries, "category", errors, "briefs.categories"
    )
    if len(brief_by_category) != EXPECTED_SLOT_COUNT:
        errors.append(
            f"briefs:expected_25_unique_categories_got_{len(brief_by_category)}"
        )

    slots = contract.get("slots", [])
    if not isinstance(slots, list):
        errors.append("contract:slots_not_array")
        slots = []
    slot_by_category = unique_index(slots, "category", errors, "contract.slots")
    if len(slots) != EXPECTED_SLOT_COUNT:
        errors.append(f"contract:expected_25_slots_got_{len(slots)}")
    if set(slot_by_category) != set(topo_slots):
        missing = sorted(set(topo_slots) - set(slot_by_category))
        extra = sorted(set(slot_by_category) - set(topo_slots))
        if missing:
            errors.append("contract:missing_topology_slots:" + ",".join(missing))
        if extra:
            errors.append("contract:extra_slots:" + ",".join(extra))
    if set(brief_by_category) != set(topo_slots):
        errors.append("briefs:category_set_does_not_match_topology")

    route_config = contract.get("allowed_source_routes", {})
    if set(route_config) != ALLOWED_ROUTES:
        errors.append("contract:allowed_source_route_set_mismatch")
    route_allowed_slots: dict[str, set[str]] = {}
    for route in ALLOWED_ROUTES:
        config = route_config.get(route, {})
        route_allowed_slots[route] = set(config.get("allowed_for_slots", []))
        if not config.get("required_rights_evidence"):
            errors.append(f"route:{route}:rights_evidence_requirements_empty")

    candidate_entries = ledger.get("source_candidates", [])
    if not isinstance(candidate_entries, list):
        errors.append("ledger:source_candidates_not_array")
        candidate_entries = []
    candidate_by_id = unique_index(
        candidate_entries, "candidate_id", errors, "ledger.source_candidates"
    )
    referenced_candidates: set[str] = set()
    slots_with_candidate = 0
    for category, slot in slot_by_category.items():
        topo = topo_slots.get(category, {})
        brief = brief_by_category.get(category, {})
        for field in (
            "graph",
            "wave_input",
            "allowed_route",
            "current_state",
            "candidate_ids",
            "candidate_disposition",
            "unreal_destination",
        ):
            if field not in slot:
                errors.append(f"slot:{category}:missing_{field}")
        if slot.get("graph") != topo.get("graph"):
            errors.append(f"slot:{category}:graph_mismatch")
        if slot.get("wave_input") != topo.get("wave_input"):
            errors.append(f"slot:{category}:wave_input_mismatch")
        null_key = f"{slot.get('graph')}:{slot.get('wave_input')}"
        if null_key not in fresh_nulls:
            errors.append(f"slot:{category}:not_null_in_accepted_fresh_audit")
        route = slot.get("allowed_route")
        if route not in ALLOWED_ROUTES:
            errors.append(f"slot:{category}:invalid_route")
        if route != brief.get("acquisition_mode"):
            errors.append(f"slot:{category}:route_does_not_match_brief")
        if category not in route_allowed_slots.get(str(route), set()):
            errors.append(f"slot:{category}:not_allowlisted_for_route")
        if slot.get("unreal_destination") != brief.get("unreal_destination"):
            errors.append(f"slot:{category}:unreal_destination_mismatch")
        if slot.get("current_state") != EXPECTED_CURRENT_STATE:
            errors.append(f"slot:{category}:current_state_must_be_missing")
        candidate_ids = slot.get("candidate_ids")
        if not isinstance(candidate_ids, list):
            errors.append(f"slot:{category}:candidate_ids_not_array")
            candidate_ids = []
        if candidate_ids:
            slots_with_candidate += 1
        for candidate_id in candidate_ids:
            if candidate_id not in candidate_by_id:
                errors.append(f"slot:{category}:unknown_candidate:{candidate_id}")
            referenced_candidates.add(str(candidate_id))
        if not isinstance(slot.get("candidate_disposition"), str) or not slot.get(
            "candidate_disposition"
        ):
            errors.append(f"slot:{category}:candidate_disposition_empty")

    inventory = contract.get("research_candidate_inventory", {})
    if inventory.get("downloaded_asset_count") != 0:
        errors.append("inventory:downloaded_asset_count_not_zero")
    if inventory.get("hashed_asset_count") != 0:
        errors.append("inventory:hashed_asset_count_not_zero")
    if inventory.get("candidate_count") != len(candidate_by_id):
        errors.append("inventory:candidate_count_mismatch")
    disposition_ids = {
        str(candidate_id)
        for values in inventory.get("dispositions", {}).values()
        for candidate_id in values
    }
    if disposition_ids != set(candidate_by_id):
        errors.append("inventory:dispositions_do_not_cover_exact_candidate_set")
    if referenced_candidates - set(candidate_by_id):
        errors.append("inventory:contract_references_unknown_candidates")

    if ledger.get("downloaded_asset_count") != 0:
        errors.append("ledger:downloaded_asset_count_not_zero")
    if ledger.get("hashed_asset_count") != 0:
        errors.append("ledger:hashed_asset_count_not_zero")
    for candidate_id, candidate in candidate_by_id.items():
        if not str(candidate.get("download_status", "")).startswith(
            "NOT_DOWNLOADED"
        ):
            errors.append(f"ledger:{candidate_id}:not_explicitly_not_downloaded")
        if candidate.get("downloaded_path") is not None:
            errors.append(f"ledger:{candidate_id}:downloaded_path_not_null")
        if candidate.get("sha256") is not None:
            errors.append(f"ledger:{candidate_id}:sha256_not_null")

    if acquisition_manifest.get("overall_state") != "EMPTY_BLOCKED":
        errors.append("acquisition_manifest:overall_state_not_empty_blocked")
    manifest_bindings = [
        binding
        for entry in acquisition_manifest.get("entries", [])
        for binding in entry.get("bank_bindings", [])
    ]
    if len(manifest_bindings) != EXPECTED_SLOT_COUNT:
        errors.append("acquisition_manifest:expected_25_bindings")
    if len(set(manifest_bindings)) != EXPECTED_SLOT_COUNT:
        errors.append("acquisition_manifest:bindings_not_unique")
    if set(manifest_bindings) != set(topo_slots):
        errors.append("acquisition_manifest:bindings_do_not_match_topology")
    for entry in acquisition_manifest.get("entries", []):
        if entry.get("acquisition_state") != "MISSING_LICENSE_AND_SOURCE":
            errors.append(
                "acquisition_manifest:"
                + str(entry.get("category_id"))
                + ":state_not_missing"
            )

    serialized_hashes = fresh_audit.get("serialized_asset_sha256", {})
    graph_asset_hashes: dict[str, str] = {}
    for graph in topology.get("graphs", []):
        graph_name = graph.get("name")
        asset_path = (
            "/Game/Skyguard/Audio/Production/MetaSounds/" + str(graph_name)
        )
        expected_hash = serialized_hashes.get(asset_path)
        if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(
            expected_hash
        ):
            errors.append(f"graph_asset:{graph_name}:accepted_hash_missing")
            continue
        file_path = game_asset_to_file(asset_path)
        if not file_path.is_file():
            errors.append(f"graph_asset:{graph_name}:missing")
            continue
        actual_hash = sha256_file(file_path)
        graph_asset_hashes[asset_path] = actual_hash
        if actual_hash != expected_hash:
            errors.append(f"graph_asset:{graph_name}:hash_drift")

    universal = contract.get("universal_promotion_requirements", [])
    if not isinstance(universal, list) or len(universal) < 8:
        errors.append("contract:universal_promotion_requirements_incomplete")
    promotion_rules = contract.get("state_model", {}).get(
        "promotion_rules", {}
    )
    if set(promotion_rules) != {
        "CANDIDATE_RESEARCH_ONLY",
        "ACQUIRED_QUARANTINED",
        "RIGHTS_AND_SEMANTIC_REVIEW_PENDING",
        "APPROVED_FOR_GOVERNED_IMPORT",
    }:
        errors.append("contract:promotion_rule_set_mismatch")

    truth = contract.get("current_truth", {})
    expected_truth = {
        "slot_count": EXPECTED_SLOT_COUNT,
        "missing_source_count": EXPECTED_SLOT_COUNT,
        "slots_with_candidate_reference_count": slots_with_candidate,
        "slots_without_candidate_reference_count": (
            EXPECTED_SLOT_COUNT - slots_with_candidate
        ),
        "approved_source_count": 0,
        "downloaded_source_count": 0,
        "hashed_source_count": 0,
        "unreal_imported_source_count": 0,
        "production_ready": False,
        "shipping_allowed": False,
        "packaged_audible_acceptance": False,
        "status": "CONTRACT_VALID_AUTHENTIC_SOURCES_MISSING",
    }
    for field, expected in expected_truth.items():
        if truth.get(field) != expected:
            errors.append(f"current_truth:{field}_mismatch")

    contract_hash = sha256_file(contract_path)
    return {
        "schema": "skyguard.phase5.authentic-source-acquisition-audit.v1",
        "contract_path": str(contract_path),
        "contract_sha256": contract_hash,
        "accepted_topology_attempt_id": boundary.get("attempt_id"),
        "accepted_topology_contract_bundle_sha256": boundary.get(
            "topology_contract_bundle_sha256"
        ),
        "authority_input_sha256": input_hashes,
        "current_graph_asset_sha256": graph_asset_hashes,
        "expected_graph_count": EXPECTED_GRAPH_COUNT,
        "observed_graph_count": len(topology.get("graphs", [])),
        "expected_source_slot_count": EXPECTED_SLOT_COUNT,
        "observed_source_slot_count": len(slots),
        "observed_null_wave_asset_slot_count": len(fresh_nulls),
        "slots_with_candidate_reference_count": slots_with_candidate,
        "slots_without_candidate_reference_count": (
            EXPECTED_SLOT_COUNT - slots_with_candidate
        ),
        "research_candidate_count": len(candidate_by_id),
        "downloaded_source_count": int(
            ledger.get("downloaded_asset_count", -1)
        ),
        "hashed_source_count": int(ledger.get("hashed_asset_count", -1)),
        "approved_source_count": 0,
        "unreal_imported_source_count": 0,
        "contract_valid": not errors,
        "authentic_source_acquisition_ready": False,
        "production_ready": False,
        "shipping_allowed": False,
        "packaged_audible_acceptance": False,
        "warnings": warnings,
        "errors": errors,
        "status": (
            "PASS_IMMUTABLE_SOURCE_CONTRACT_AUTHENTIC_SOURCES_MISSING"
            if not errors
            else "FAIL_AUTHENTIC_SOURCE_ACQUISITION_CONTRACT"
        ),
    }


def write_immutable_attempt(report: dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    attempt_id = (
        f"attempt_{timestamp}_{report['contract_sha256'][:8]}_"
        f"{secrets.token_hex(4)}"
    )
    attempt_dir = REPORT_ROOT / attempt_id
    attempt_dir.mkdir(parents=True, exist_ok=False)
    completed_at = datetime.now(timezone.utc).isoformat()
    report = dict(report)
    report["attempt_id"] = attempt_id
    report["completed_at_utc"] = completed_at
    audit_path = attempt_dir / "source_acquisition_audit.json"
    audit_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    audit_hash = sha256_file(audit_path)
    status = {
        "schema": "skyguard.phase5.authentic-source-acquisition-status.v1",
        "attempt_id": attempt_id,
        "state": report["status"],
        "contract_sha256": report["contract_sha256"],
        "audit_sha256": audit_hash,
        "source_slot_count": report["observed_source_slot_count"],
        "authentic_source_count": report["approved_source_count"],
        "missing_source_count": (
            EXPECTED_SLOT_COUNT - report["approved_source_count"]
        ),
        "production_ready": False,
        "shipping_allowed": False,
        "packaged_audible_acceptance": False,
        "completed_at_utc": completed_at,
    }
    status_path = attempt_dir / "status.json"
    status_path.write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return attempt_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()

    try:
        contract = read_json(args.contract)
        report = validate_contract(contract, args.contract)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(
            json.dumps(
                {
                    "status": "FAIL_AUTHENTIC_SOURCE_ACQUISITION_CONTRACT",
                    "errors": [str(exc)],
                    "production_ready": False,
                    "shipping_allowed": False,
                },
                indent=2,
            )
        )
        return 2

    if not args.no_write:
        attempt_dir = write_immutable_attempt(report)
        report["attempt_directory"] = str(attempt_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["errors"]:
        return 2
    if args.require_ready:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
