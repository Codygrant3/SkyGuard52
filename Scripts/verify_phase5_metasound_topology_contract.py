#!/usr/bin/env python3
"""Validate the governed Phase 5 MetaSound topology contract offline."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
DOCS = ROOT / "Docs" / "AAA_Review"
CONTRACT_PATH = DOCS / "PHASE5_METASOUND_TOPOLOGY_CONTRACT.json"
SPECS_PATH = DOCS / "PHASE5_AUDIO_ROUTING_PRIMITIVE_SPECS.json"
RUNTIME_PATH = DOCS / "PHASE5_AUDIO_RUNTIME_ROUTING_READINESS_CONTRACT.json"
BRIEFS_PATH = DOCS / "PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json"
REPORT_PATH = ROOT / "Saved" / "Reports" / (
    "PHASE5_METASOUND_TOPOLOGY_CONTRACT_AUDIT.json"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_bundle(contract: dict) -> dict:
    hashes = {}
    for relative in contract.get("contract_hash_inputs", []):
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(str(path))
        hashes[relative] = sha256_file(path)
    return {
        "files": hashes,
        "bundle_sha256": hashlib.sha256(canonical_bytes(hashes)).hexdigest(),
    }


def evaluate(
    contract: dict, specs: dict, runtime: dict, briefs: dict
) -> dict:
    errors: list[str] = []
    if contract.get("schema") != (
        "skyguard.phase5.metasound-topology-contract.v1"
    ):
        errors.append("topology contract schema mismatch")
    if contract.get("asset_root") != (
        "/Game/Skyguard/Audio/Production/MetaSounds"
    ):
        errors.append("MetaSound asset root is not the governed Production root")
    if contract.get("output_format") != "Stereo":
        errors.append("all governed topology must use Stereo output")

    truth = contract.get("truth_boundary", {})
    exact_truth = {
        "authentic_source_count": 0,
        "required_explicit_missing_source_count": 25,
        "wave_asset_defaults_must_be_null": True,
        "procedural_generators_allowed": False,
        "production_bank_sound_bindings_allowed": False,
        "production_ready_allowed": False,
        "shipping_allowed": False,
        "packaged_audible_acceptance_claim_allowed": False,
    }
    for key, expected in exact_truth.items():
        if truth.get(key) != expected:
            errors.append("unsafe truth boundary: " + key)

    expected_hash_inputs = {
        "Docs/AAA_Review/PHASE5_AUDIO_ROUTING_PRIMITIVE_SPECS.json",
        "Docs/AAA_Review/PHASE5_AUDIO_RUNTIME_ROUTING_READINESS_CONTRACT.json",
        "Docs/AAA_Review/PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json",
        "Docs/AAA_Review/PHASE5_METASOUND_TOPOLOGY_CONTRACT.json",
    }
    if set(contract.get("contract_hash_inputs", [])) != expected_hash_inputs:
        errors.append("contract hash input coverage mismatch")

    interfaces = {
        item.get("name"): item
        for item in specs.get("metasound_interfaces", [])
    }
    runtime_assets = {
        path.rsplit("/", 1)[-1]: path
        for path in runtime.get("metasound_assets", [])
    }
    runtime_composition = runtime.get("composition_coverage", {})
    graphs = contract.get("graphs", [])
    by_name = {item.get("name"): item for item in graphs}
    if len(graphs) != 6 or len(by_name) != 6:
        errors.append("exactly six unique MetaSound graphs are required")
    if set(by_name) != set(interfaces) or set(by_name) != set(runtime_assets):
        errors.append("graph names do not exactly match governed interfaces")

    all_categories: list[str] = []
    all_wave_inputs: list[str] = []
    allowed_types = {"Trigger", "Float", "Int32", "Bool"}
    for name, graph in sorted(by_name.items()):
        interface = interfaces.get(name, {})
        controls = graph.get("controls", [])
        semantic_inputs = [item.get("semantic_name") for item in controls]
        if semantic_inputs != interface.get("inputs", []):
            errors.append(name + ": semantic input order/coverage mismatch")
        if len(semantic_inputs) != len(set(semantic_inputs)):
            errors.append(name + ": duplicate semantic controls")
        outputs = [
            item.get("semantic_name") for item in graph.get("outputs", [])
        ]
        if outputs != interface.get("outputs", []):
            errors.append(name + ": semantic output coverage mismatch")
        output_spec = (graph.get("outputs") or [{}])[0]
        if graph.get("one_shot"):
            if (
                output_spec.get("serialized_name") != "On Finished"
                or output_spec.get("uses_source_interface") is not True
            ):
                errors.append(name + ": one-shot output interface mismatch")
        elif (
            output_spec.get("serialized_name") != "OnFinished"
            or output_spec.get("uses_source_interface") is not False
        ):
            errors.append(name + ": persistent output interface mismatch")
        if graph.get("behavior_acceptance_state", "").startswith("BLOCKED_") is False:
            errors.append(name + ": behavior state must remain explicitly blocked")
        if runtime_assets.get(name) != (
            contract.get("asset_root", "") + "/" + name
        ):
            errors.append(name + ": runtime asset path mismatch")

        serialized_inputs = {
            item.get("serialized_name") for item in controls
        }
        for control in controls:
            data_type = control.get("data_type")
            if data_type not in allowed_types:
                errors.append(name + ": unsupported control type " + str(data_type))
            if control.get("uses_source_interface"):
                if (
                    control.get("semantic_name") != "OnPlay"
                    or control.get("serialized_name") != "On Play"
                    or data_type != "Trigger"
                ):
                    errors.append(name + ": invalid source-interface alias")
            elif "default" not in control:
                errors.append(name + ": custom control lacks explicit default")

        categories = graph.get("categories", [])
        category_names = [item.get("category") for item in categories]
        if category_names != runtime_composition.get(name, []):
            errors.append(name + ": category composition/order mismatch")
        if category_names != interface.get("categories", []):
            errors.append(name + ": primitive interface category mismatch")
        if len(category_names) < 2 or len(category_names) > 8:
            errors.append(name + ": category mixer lane count outside 2..8")
        for category in categories:
            if category.get("wave_input") != (
                "Source_" + str(category.get("category"))
            ):
                errors.append(name + ": nonsemantic WaveAsset input name")
            trigger = category.get("trigger")
            if trigger != "On Play" and trigger not in serialized_inputs:
                errors.append(
                    name + ": category trigger is not a declared graph input"
                )
            if category.get("loop") not in (True, False):
                errors.append(name + ": category loop must be explicit bool")
            all_categories.append(category.get("category"))
            all_wave_inputs.append(category.get("wave_input"))

    brief_categories = [
        item.get("category") for item in briefs.get("categories", [])
    ]
    if (
        len(all_categories) != 25
        or len(set(all_categories)) != 25
        or set(all_categories) != set(brief_categories)
    ):
        errors.append("25-category authentic source coverage mismatch")
    if len(all_wave_inputs) != 25 or len(set(all_wave_inputs)) != 25:
        errors.append("WaveAsset source input names are not exact and unique")

    node_classes = contract.get("node_classes", {})
    expected_roles = {"wave_player", "mixer", "finished_trigger_any"}
    if set(node_classes) != expected_roles:
        errors.append("node class allowlist roles mismatch")
    serialized_node_classes = json.dumps(node_classes, sort_keys=True).lower()
    for forbidden in (
        "oscillator",
        "noise",
        "granular",
        "procedural",
        "synth",
    ):
        if forbidden in serialized_node_classes:
            errors.append("forbidden synthesized node class: " + forbidden)

    bundle = {}
    try:
        bundle = compute_bundle(contract)
    except (FileNotFoundError, OSError) as exc:
        errors.append("contract hash input unavailable: " + str(exc))

    return {
        "schema": "skyguard.phase5.metasound-topology-contract-audit.v1",
        "contract_schema": contract.get("schema"),
        "contract_bundle": bundle,
        "graph_count": len(graphs),
        "category_count": len(all_categories),
        "wave_asset_input_count": len(all_wave_inputs),
        "procedural_generator_count": 0,
        "authentic_source_count": truth.get("authentic_source_count"),
        "explicit_missing_source_count_required": truth.get(
            "required_explicit_missing_source_count"
        ),
        "production_ready": False,
        "shipping_allowed": False,
        "errors": errors,
        "status": (
            "PASS_GOVERNED_SILENT_UNTIL_SOURCED_TOPOLOGY_CONTRACT"
            if not errors
            else "FAIL_METASOUND_TOPOLOGY_CONTRACT"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    args = parser.parse_args()
    try:
        contract = load_json(args.contract)
        specs = load_json(SPECS_PATH)
        runtime = load_json(RUNTIME_PATH)
        briefs = load_json(BRIEFS_PATH)
        report = evaluate(contract, specs, runtime, briefs)
    except (OSError, json.JSONDecodeError) as exc:
        report = {
            "schema": (
                "skyguard.phase5.metasound-topology-contract-audit.v1"
            ),
            "errors": [str(exc)],
            "status": "FAIL_METASOUND_TOPOLOGY_CONTRACT",
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if not report.get("errors") else 1


if __name__ == "__main__":
    sys.exit(main())
