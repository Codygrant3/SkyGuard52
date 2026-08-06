"""Fresh-process serialized audit for six governed Phase 5 MetaSounds.

This verifier must run in a different Unreal Editor process from the author.
It reopens each MetaSound, reconstructs every recorded node/vertex handle,
checks all declared graph members and every governed edge, validates contract
metadata and serialized file hashes, and proves the production bank still has
25 null MISSING_SOURCE entries. It never upgrades audible or Shipping state.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
DOCS = ROOT / "Docs" / "AAA_Review"
CONTRACT_PATH = DOCS / "PHASE5_METASOUND_TOPOLOGY_CONTRACT.json"
SPECS_PATH = DOCS / "PHASE5_AUDIO_ROUTING_PRIMITIVE_SPECS.json"
RUNTIME_PATH = DOCS / "PHASE5_AUDIO_RUNTIME_ROUTING_READINESS_CONTRACT.json"
BANK_PATH = "/Game/Skyguard/Audio/Production/DA_P5A_ProductionAudioBank"
ATTEMPT_DIRECTORY = os.environ.get("SKYGUARD_PHASE5_METASOUND_ATTEMPT_DIR")
if not ATTEMPT_DIRECTORY:
    raise RuntimeError(
        "SKYGUARD_PHASE5_METASOUND_ATTEMPT_DIR is required for fresh audit"
    )
ATTEMPT = Path(ATTEMPT_DIRECTORY)
BUILD_MANIFEST_PATH = ATTEMPT / "build_topology_manifest.json"
REPORT_PATH = ATTEMPT / "fresh_topology_audit.json"
CONNECTIVITY_EVIDENCE_PATH = (
    ROOT
    / "Saved"
    / "Reports"
    / "Phase5MetaSoundConnectivity"
    / "attempt_20260802T151515217Z_e954a456"
    / "fresh_connectivity.json"
)
CONNECTIVITY_EVIDENCE_SHA256 = (
    "3467e1a4926b05dac36f8f3a503c65b9bf65895003204407d7be832c5e8e7e84"
)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def contract_bundle(contract: dict) -> dict:
    hashes = {
        relative: sha256_file(ROOT / relative)
        for relative in contract["contract_hash_inputs"]
    }
    return {
        "files": hashes,
        "bundle_sha256": hashlib.sha256(canonical_bytes(hashes)).hexdigest(),
    }


def class_name(value: object) -> str:
    return value.get_class().get_name() if value is not None else ""


def is_success(value: object) -> bool:
    text = str(value).upper()
    return "SUCCEEDED" in text and "FAILED" not in text


def flatten_result(value: object) -> tuple:
    return value if isinstance(value, tuple) else (value,)


def require_call(value: object, label: str) -> tuple:
    items = flatten_result(value)
    if not any(is_success(item) for item in items):
        raise RuntimeError(
            "%s did not return SUCCEEDED: %s" % (label, repr(value))
        )
    return items


def item_with_method(items: tuple, method: str):
    for item in items:
        if hasattr(item, method):
            return item
    raise RuntimeError("Call result missing object method " + method)


def item_with_name_array(items: tuple) -> list[str]:
    for item in items:
        if isinstance(item, (str, bytes, dict)):
            continue
        try:
            entries = list(item)
        except TypeError:
            continue
        return [str(entry) for entry in entries]
    raise RuntimeError("Call result missing graph member array")


def canonical_interface_name(name: str, source_interface: bool) -> str:
    if not source_interface:
        return name
    mapping = {
        "On Play": "UE.Source.OnPlay",
        "On Finished": "UE.Source.OneShot.OnFinished",
    }
    if name not in mapping:
        raise RuntimeError("Unknown governed source interface " + name)
    return mapping[name]


def graph_member_handle(builder, name: str, output: bool):
    items = require_call(
        builder.find_graph_input_node(name)
        if output
        else builder.find_graph_output_node(name),
        ("FindGraphInputNode " if output else "FindGraphOutputNode ") + name,
    )
    expected_type = (
        "MetaSoundBuilderNodeOutputHandle"
        if output
        else "MetaSoundBuilderNodeInputHandle"
    )
    for item in items:
        if type(item).__name__ == expected_type:
            return item
    raise RuntimeError(
        "%s omitted %s" % (name, expected_type)
    )


def node_input_handle(builder, node_record_value: dict, name: str):
    items = require_call(
        builder.find_node_input_by_name(
            node_handle(node_record_value), name
        ),
        "FindNodeInputByName " + name,
    )
    for item in items:
        if type(item).__name__ == "MetaSoundBuilderNodeInputHandle":
            return item
    raise RuntimeError(
        "%s omitted MetaSoundBuilderNodeInputHandle" % name
    )


def record_key(record: dict) -> tuple[str, str]:
    return (record["node_id"], record["vertex_id"])


def vertex_export_text(record: dict) -> str:
    return "(NodeID=%s,VertexID=%s)" % (
        record["node_id"],
        record["vertex_id"],
    )


def guid(text: str):
    return unreal.Guid(text)


def vertex_handle(record: dict, output: bool):
    value = (
        unreal.MetaSoundBuilderNodeOutputHandle()
        if output
        else unreal.MetaSoundBuilderNodeInputHandle()
    )
    value.import_text(
        "(NodeID=%s,VertexID=%s)"
        % (record["node_id"], record["vertex_id"])
    )
    return value


def node_handle(record: dict):
    value = unreal.MetaSoundNodeHandle()
    value.import_text("(NodeID=%s)" % record["node_id"])
    return value


def asset_file(asset_path: str) -> Path:
    return ROOT / "Content" / (
        asset_path.removeprefix("/Game/") + ".uasset"
    )


def member_data(builder, handle, output: bool) -> tuple[str, str]:
    items = require_call(
        builder.get_node_output_data(handle)
        if output
        else builder.get_node_input_data(handle),
        "GetNodeOutputData" if output else "GetNodeInputData",
    )
    names = [str(item) for item in items if not is_success(item)]
    if len(names) != 2:
        raise RuntimeError(
            "Node member data must return exact reflected name/type pair: %s"
            % repr(items)
        )
    return names[0], names[1]


def graph_input_literal_text(builder, name: str) -> str:
    items = require_call(
        builder.get_graph_input_default(name),
        "GetGraphInputDefault " + name,
    )
    for item in items:
        if type(item).__name__ == "MetasoundFrontendLiteral":
            if hasattr(item, "export_text"):
                return str(item.export_text())
            return str(item)
    raise RuntimeError("Graph input default omitted literal for " + name)


def assert_bank_truth(errors: list[str]) -> dict:
    bank = unreal.EditorAssetLibrary.load_asset(BANK_PATH)
    if bank is None or class_name(bank) != "SkyguardAudioProductionBank":
        errors.append("production bank missing or wrong class")
        return {}
    entries = list(bank.get_editor_property("entries") or [])
    missing = 0
    unauthorized = []
    for index, entry in enumerate(entries):
        if (
            entry.get_editor_property("source_status")
            == unreal.SkyguardAudioSourceStatus.MISSING_SOURCE
        ):
            missing += 1
        else:
            unauthorized.append("status[%d]" % index)
        if entry.get_editor_property("sound"):
            unauthorized.append("sound[%d]" % index)
        if str(entry.get_editor_property("provenance_id")) not in ("", "None"):
            unauthorized.append("provenance[%d]" % index)
        if str(entry.get_editor_property("source_sha256")):
            unauthorized.append("source_hash[%d]" % index)
    audit = bank.evaluate_readiness()
    if len(entries) != 25:
        errors.append("production bank entry count is not 25")
    if missing != 25:
        errors.append("production bank does not retain 25 MISSING_SOURCE entries")
    if unauthorized:
        errors.append(
            "unauthorized production source fields: " + ", ".join(unauthorized)
        )
    if int(audit.bound_production_source_count) != 0:
        errors.append("production bank reports a bound production source")
    if bool(audit.production_ready):
        errors.append("unsourced production bank falsely reports ready")
    return {
        "entry_count": len(entries),
        "explicit_missing_source_count": missing,
        "bound_production_source_count": int(
            audit.bound_production_source_count
        ),
        "production_ready": bool(audit.production_ready),
        "unauthorized_source_fields": unauthorized,
    }


def audit_graph(
    graph_contract: dict,
    manifest: dict,
    contract: dict,
    bundle: dict,
    expected_asset_hash: str,
) -> dict:
    errors: list[str] = []
    asset_path = manifest["asset_path"]
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if asset is None or class_name(asset) != "MetaSoundSource":
        return {
            "name": graph_contract["name"],
            "asset_path": asset_path,
            "errors": ["asset missing or wrong class"],
            "status": "FAIL_SERIALIZED_TOPOLOGY",
        }

    tags = contract["metadata_tags"]
    tag_values = {
        key: str(unreal.EditorAssetLibrary.get_metadata_tag(asset, tag))
        for key, tag in tags.items()
    }
    expected_graph_hash = hashlib.sha256(
        canonical_bytes(graph_contract)
    ).hexdigest()
    if tag_values["contract_bundle_sha256"] != bundle["bundle_sha256"]:
        errors.append("serialized contract bundle metadata is stale")
    if tag_values["graph_contract_sha256"] != expected_graph_hash:
        errors.append("serialized graph contract metadata is stale")
    if tag_values["topology_schema"] != contract["schema"]:
        errors.append("serialized topology schema metadata mismatch")
    if tag_values["source_state"] != "25_OF_25_MISSING_SOURCE_BANK_WIDE":
        errors.append("serialized source-state metadata crossed boundary")
    if tag_values["behavior_state"] != graph_contract[
        "behavior_acceptance_state"
    ]:
        errors.append("serialized behavior-state metadata mismatch")

    disk_path = asset_file(asset_path)
    actual_asset_hash = sha256_file(disk_path) if disk_path.is_file() else ""
    if actual_asset_hash != expected_asset_hash:
        errors.append("serialized MetaSound hash changed after authoring")

    editor_subsystem = unreal.get_editor_subsystem(
        unreal.MetaSoundEditorSubsystem
    )
    try:
        builder = item_with_method(
            require_call(
                editor_subsystem.find_or_begin_building(asset),
                "FindOrBeginBuilding " + graph_contract["name"],
            ),
            "get_graph_input_names",
        )
    except RuntimeError as exc:
        errors.append(str(exc))
        return {
            "name": graph_contract["name"],
            "asset_path": asset_path,
            "metadata": tag_values,
            "asset_sha256": actual_asset_hash,
            "errors": errors,
            "status": "FAIL_SERIALIZED_TOPOLOGY",
        }

    try:
        actual_inputs = set(
            item_with_name_array(
                require_call(
                    builder.get_graph_input_names(), "GetGraphInputNames"
                )
            )
        )
        actual_outputs = set(
            item_with_name_array(
                require_call(
                    builder.get_graph_output_names(), "GetGraphOutputNames"
                )
            )
        )
        expected_inputs = {
            canonical_interface_name(
                item["serialized_name"],
                bool(item.get("source_interface")),
            )
            for item in manifest["controls"]
        }
        expected_outputs = {
            canonical_interface_name(
                item["serialized_name"],
                bool(item.get("uses_source_interface")),
            )
            for item in manifest["outputs"]
        }
        if actual_inputs != expected_inputs:
            errors.append(
                "graph input set mismatch expected=%s actual=%s"
                % (sorted(expected_inputs), sorted(actual_inputs))
            )
        if actual_outputs != expected_outputs:
            errors.append(
                "graph output set mismatch expected=%s actual=%s"
                % (sorted(expected_outputs), sorted(actual_outputs))
            )

        null_wave_defaults = []
        resolved_graph_inputs = {}
        for control in manifest["controls"]:
            expected_name = canonical_interface_name(
                control["serialized_name"],
                bool(control.get("source_interface")),
            )
            handle = graph_member_handle(builder, expected_name, True)
            resolved_graph_inputs[record_key(control["handle"])] = handle
            if handle.export_text() != vertex_export_text(control["handle"]):
                errors.append(
                    "reopened graph input handle changed "
                    + control["serialized_name"]
                )
            if not builder.contains_node_output(handle):
                errors.append(
                    "missing graph input handle " + control["serialized_name"]
                )
                continue
            actual_name, actual_type = member_data(builder, handle, True)
            if actual_name != expected_name:
                errors.append(
                    "input handle name mismatch " + control["serialized_name"]
                )
            if actual_type != control["data_type"]:
                errors.append(
                    "input handle type mismatch " + control["serialized_name"]
                )
            if control["data_type"] == "WaveAsset":
                literal_text = graph_input_literal_text(
                    builder, control["serialized_name"]
                )
                if "/Game/" in literal_text or "SoundWave'" in literal_text:
                    errors.append(
                        "WaveAsset default is not null: "
                        + control["serialized_name"]
                    )
                null_wave_defaults.append(
                    {
                        "name": control["serialized_name"],
                        "literal_sha256": hashlib.sha256(
                            literal_text.encode("utf-8")
                        ).hexdigest(),
                        "contains_game_asset_path": "/Game/" in literal_text,
                    }
                )

        resolved_graph_outputs = {}
        for output in manifest["outputs"]:
            expected_name = canonical_interface_name(
                output["serialized_name"],
                bool(output.get("uses_source_interface")),
            )
            handle = graph_member_handle(builder, expected_name, False)
            resolved_graph_outputs[record_key(output["handle"])] = handle
            if handle.export_text() != vertex_export_text(output["handle"]):
                errors.append(
                    "reopened graph output handle changed "
                    + output["serialized_name"]
                )
            if not builder.contains_node_input(handle):
                errors.append(
                    "missing graph output handle " + output["serialized_name"]
                )
                continue
            actual_name, actual_type = member_data(builder, handle, False)
            if actual_name != expected_name:
                errors.append(
                    "output handle name mismatch " + output["serialized_name"]
                )
            if actual_type != output["data_type"]:
                errors.append(
                    "output handle type mismatch " + output["serialized_name"]
                )

        resolved_wave_inputs = {}
        wave_class = contract["node_classes"]["wave_player"]
        for category in manifest["categories"]:
            resolved_wave_inputs[
                record_key(category["wave_asset_pin"])
            ] = node_input_handle(
                builder,
                category["wave_node_handle"],
                wave_class["wave_input"],
            )
            resolved_wave_inputs[
                record_key(category["play_pin"])
            ] = node_input_handle(
                builder,
                category["wave_node_handle"],
                wave_class["play_input"],
            )
            if (
                resolved_wave_inputs[
                    record_key(category["wave_asset_pin"])
                ].export_text()
                != vertex_export_text(category["wave_asset_pin"])
            ):
                errors.append(
                    "reopened WaveAsset pin handle changed "
                    + category["category"]
                )
            if (
                resolved_wave_inputs[
                    record_key(category["play_pin"])
                ].export_text()
                != vertex_export_text(category["play_pin"])
            ):
                errors.append(
                    "reopened Play pin handle changed "
                    + category["category"]
                )

        for node in manifest["nodes"]:
            if not builder.contains_node(node_handle(node["handle"])):
                errors.append(
                    "missing governed internal node "
                    + node["role"]
                    + ":"
                    + str(node.get("category", ""))
                )

        connected_edges = 0
        exact_pair_connected_edges = 0
        interface_endpoint_connected_edges = 0
        interface_exact_pair_observed_edges = 0
        for edge in manifest["edges"]:
            source_key = record_key(edge["from"])
            destination_key = record_key(edge["to"])
            source_is_graph_interface = source_key in resolved_graph_inputs
            destination_is_graph_interface = (
                destination_key in resolved_graph_outputs
            )
            source = (
                resolved_graph_inputs[source_key]
                if source_is_graph_interface
                else vertex_handle(edge["from"], True)
            )
            destination = (
                resolved_graph_outputs[destination_key]
                if destination_is_graph_interface
                else (
                    resolved_wave_inputs[destination_key]
                    if destination_key in resolved_wave_inputs
                    else vertex_handle(edge["to"], False)
                )
            )
            is_interface_edge = (
                source_is_graph_interface
                or destination_is_graph_interface
            )
            exact_pair_connected = builder.nodes_are_connected(
                source, destination
            )
            if is_interface_edge:
                if exact_pair_connected:
                    interface_exact_pair_observed_edges += 1
                if (
                    builder.node_output_is_connected(source)
                    and builder.node_input_is_connected(destination)
                ):
                    connected_edges += 1
                    interface_endpoint_connected_edges += 1
                else:
                    errors.append(
                        "missing governed interface endpoint edge: "
                        + edge["label"]
                    )
            elif exact_pair_connected:
                connected_edges += 1
                if not is_interface_edge:
                    exact_pair_connected_edges += 1
            else:
                errors.append("missing governed edge: " + edge["label"])
        expected_edge_count = 5 * len(graph_contract["categories"]) + 3
        expected_exact_pair_count = 3 * len(
            graph_contract["categories"]
        )
        expected_interface_endpoint_count = (
            2 * len(graph_contract["categories"]) + 3
        )
        if len(manifest["edges"]) != expected_edge_count:
            errors.append("topology manifest edge count formula mismatch")
        if connected_edges != expected_edge_count:
            errors.append("connected governed edge count mismatch")
        if exact_pair_connected_edges != expected_exact_pair_count:
            errors.append("exact internal pair proof count mismatch")
        if (
            interface_endpoint_connected_edges
            != expected_interface_endpoint_count
        ):
            errors.append("interface endpoint proof count mismatch")
    except RuntimeError as exc:
        errors.append(str(exc))
        actual_inputs = set()
        actual_outputs = set()
        null_wave_defaults = []
        connected_edges = 0
        exact_pair_connected_edges = 0
        interface_endpoint_connected_edges = 0
        interface_exact_pair_observed_edges = 0
        expected_edge_count = 5 * len(graph_contract["categories"]) + 3
        expected_exact_pair_count = 3 * len(
            graph_contract["categories"]
        )
        expected_interface_endpoint_count = (
            2 * len(graph_contract["categories"]) + 3
        )

    return {
        "name": graph_contract["name"],
        "asset_path": asset_path,
        "asset_class": class_name(asset),
        "metadata": tag_values,
        "asset_sha256": actual_asset_hash,
        "graph_input_count": len(actual_inputs),
        "graph_output_count": len(actual_outputs),
        "internal_node_count": len(manifest["nodes"]),
        "governed_edge_count": len(manifest["edges"]),
        "connected_governed_edge_count": connected_edges,
        "expected_governed_edge_count": expected_edge_count,
        "exact_internal_pair_connected_edge_count": (
            exact_pair_connected_edges
        ),
        "expected_exact_internal_pair_count": expected_exact_pair_count,
        "interface_endpoint_connected_edge_count": (
            interface_endpoint_connected_edges
        ),
        "interface_exact_pair_observed_edge_count": (
            interface_exact_pair_observed_edges
        ),
        "expected_interface_endpoint_count": (
            expected_interface_endpoint_count
        ),
        "interface_edge_proof": (
            "UNCHANGED_REOPENED_HANDLES_PLUS_BOTH_ENDPOINTS_CONNECTED"
        ),
        "null_wave_asset_defaults": null_wave_defaults,
        "authentic_source_count": 0,
        "procedural_generator_count": 0,
        "errors": errors,
        "status": (
            "PASS_SERIALIZED_SILENT_UNTIL_SOURCED_TOPOLOGY"
            if not errors
            else "FAIL_SERIALIZED_TOPOLOGY"
        ),
    }


def main():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    specs = json.loads(SPECS_PATH.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME_PATH.read_text(encoding="utf-8"))
    build_manifest = json.loads(
        BUILD_MANIFEST_PATH.read_text(encoding="utf-8")
    )
    bundle = contract_bundle(contract)
    errors: list[str] = []
    connectivity_evidence_sha256 = (
        sha256_file(CONNECTIVITY_EVIDENCE_PATH)
        if CONNECTIVITY_EVIDENCE_PATH.is_file()
        else ""
    )
    if connectivity_evidence_sha256 != CONNECTIVITY_EVIDENCE_SHA256:
        errors.append(
            "UE5.8 persisted-connectivity diagnostic evidence missing or stale"
        )
    if build_manifest.get("contract_bundle") != bundle:
        errors.append("build manifest is stale for current contract bundle")
    if build_manifest.get("graph_count") != 6:
        errors.append("build manifest graph count is not six")
    if build_manifest.get("primitive_count") != 29:
        errors.append("build manifest primitive count is not 29")
    if build_manifest.get("governed_asset_count") != 35:
        errors.append("build manifest governed asset count is not 35")

    current_asset_hashes = {}
    for asset_path, expected_hash in build_manifest.get(
        "serialized_asset_sha256", {}
    ).items():
        path = asset_file(asset_path)
        actual_hash = sha256_file(path) if path.is_file() else ""
        current_asset_hashes[asset_path] = actual_hash
        if actual_hash != expected_hash:
            errors.append("governed asset hash mismatch: " + asset_path)

    graph_contracts = {
        graph["name"]: graph for graph in contract["graphs"]
    }
    graph_manifests = {
        graph["name"]: graph for graph in build_manifest.get("graphs", [])
    }
    graph_reports = []
    for name in sorted(graph_contracts):
        manifest = graph_manifests.get(name)
        if manifest is None:
            errors.append("build topology manifest missing graph " + name)
            continue
        graph_report = audit_graph(
            graph_contracts[name],
            manifest,
            contract,
            bundle,
            build_manifest["serialized_asset_sha256"].get(
                manifest["asset_path"], ""
            ),
        )
        graph_reports.append(graph_report)
        errors.extend(
            name + ": " + error for error in graph_report["errors"]
        )

    primitive_paths = [
        runtime["attenuation_asset_root"] + "/ATT_" + item["name"]
        for item in specs["attenuation"]
    ] + [
        runtime["concurrency_asset_root"] + "/CON_" + item["name"]
        for item in specs["concurrency"]
    ]
    if len(primitive_paths) != 29:
        errors.append("current primitive specification is not 29 assets")
    if any(path not in current_asset_hashes for path in primitive_paths):
        errors.append("fresh hash receipt does not cover all 29 primitives")

    bank = assert_bank_truth(errors)
    fresh_for_current_contract = (
        not errors
        and len(graph_reports) == 6
        and all(not graph["errors"] for graph in graph_reports)
        and bank.get("explicit_missing_source_count") == 25
        and bank.get("bound_production_source_count") == 0
        and bank.get("production_ready") is False
    )
    result = {
        "schema": "skyguard.phase5.metasound-topology-fresh-audit.v1",
        "topology_contract_schema": contract["schema"],
        "contract_bundle": bundle,
        "ue58_connectivity_diagnostic": {
            "path": str(CONNECTIVITY_EVIDENCE_PATH),
            "expected_sha256": CONNECTIVITY_EVIDENCE_SHA256,
            "actual_sha256": connectivity_evidence_sha256,
            "finding": (
                "ORIGINAL_AND_REOPENED_HANDLES_UNCHANGED;"
                "INTERFACE_PAIR_QUERY_FALSE;"
                "BOTH_ENDPOINT_QUERIES_TRUE"
            ),
        },
        "graph_count": len(graph_reports),
        "primitive_count": len(primitive_paths),
        "governed_asset_count": len(current_asset_hashes),
        "graph_reports": graph_reports,
        "serialized_asset_sha256": current_asset_hashes,
        "production_bank": bank,
        "authentic_source_count": 0,
        "metasound_soundwave_binding_count": 0,
        "procedural_generator_count": 0,
        "fresh_for_current_contract": fresh_for_current_contract,
        "production_ready": False,
        "shipping_allowed": False,
        "packaged_audible_acceptance": False,
        "errors": errors,
        "status": (
            "PASS_FRESH_GOVERNED_METASOUND_TOPOLOGY_SOURCES_MISSING"
            if fresh_for_current_contract
            else "FAIL_FRESH_METASOUND_TOPOLOGY"
        ),
    }
    REPORT_PATH.write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    unreal.log("[Skyguard52] " + json.dumps(result, sort_keys=True))
    if errors:
        raise RuntimeError("; ".join(errors))


if __name__ == "__main__":
    main()
