"""Fresh-process inspection and cleanup of the temporary connectivity probe."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ATTEMPT = Path(os.environ["SKYGUARD_PHASE5_CONNECTIVITY_ATTEMPT_DIR"])
AUTHOR_REPORT = ATTEMPT / "author_connectivity.json"
REPORT = ATTEMPT / "fresh_connectivity.json"
ASSET_PATH = "/Game/Skyguard/Diagnostics/Temporary/MS_P5ConnectivityProbe"


def load_helpers():
    path = ROOT / "Scripts" / "build_skyguard_phase5_metasound_topology.py"
    spec = importlib.util.spec_from_file_location("p5_topology_helpers", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def node_handle(exported: str):
    value = unreal.MetaSoundNodeHandle()
    value.import_text(exported)
    return value


def exact_handle(items, type_name: str):
    for item in items:
        if type(item).__name__ == type_name:
            return item
    raise RuntimeError("Return tuple omitted " + type_name)


def exact_array(items):
    arrays = [item for item in items if type(item).__name__ == "Array"]
    if len(arrays) != 1:
        raise RuntimeError("Return tuple omitted exact Unreal Array")
    return list(arrays[0])


def main():
    h = load_helpers()
    author = json.loads(AUTHOR_REPORT.read_text(encoding="utf-8"))
    report = {
        "schema": "skyguard.phase5.metasound-connectivity-fresh.v1",
        "asset_path": ASSET_PATH,
        "production_path": False,
        "temporary_asset": True,
        "author_status": author["status"],
        "fresh": {},
        "temporary_asset_deleted": False,
        "errors": [],
    }
    deferred_error = None
    try:
        asset = unreal.EditorAssetLibrary.load_asset(ASSET_PATH)
        if asset is None:
            raise RuntimeError("Temporary connectivity probe asset missing")
        editor = unreal.get_editor_subsystem(unreal.MetaSoundEditorSubsystem)
        items = h.require_call(
            editor.find_or_begin_building(asset),
            "FindOrBeginBuilding connectivity probe",
        )
        builder = h.item_with_method(items, "nodes_are_connected")

        graph_inputs = {}
        for name in (
            "ProbeWaveRuntime",
            "ProbeWaveConstructor",
            "UE.Source.OnPlay",
        ):
            find_items = h.require_call(
                builder.find_graph_input_node(name),
                "FindGraphInputNode " + name,
            )
            graph_inputs[name] = exact_handle(
                find_items, "MetaSoundBuilderNodeOutputHandle"
            )

        reopened_nodes = {}
        for name, node_data in author["wave_nodes"].items():
            node = node_handle(node_data["node_export_text"])
            wave_items = h.require_call(
                builder.find_node_input_by_name(node, "Wave Asset"),
                "FindNodeInputByName Wave Asset " + name,
            )
            play_items = h.require_call(
                builder.find_node_input_by_name(node, "Play"),
                "FindNodeInputByName Play " + name,
            )
            reopened_nodes[name] = {
                "wave_input": exact_handle(
                    wave_items, "MetaSoundBuilderNodeInputHandle"
                ),
                "play_input": exact_handle(
                    play_items, "MetaSoundBuilderNodeInputHandle"
                ),
            }

        pairs = {
            "runtime_wave": (
                graph_inputs["ProbeWaveRuntime"],
                reopened_nodes["Runtime"]["wave_input"],
            ),
            "runtime_play": (
                graph_inputs["UE.Source.OnPlay"],
                reopened_nodes["Runtime"]["play_input"],
            ),
            "constructor_wave": (
                graph_inputs["ProbeWaveConstructor"],
                reopened_nodes["Constructor"]["wave_input"],
            ),
            "constructor_play": (
                graph_inputs["UE.Source.OnPlay"],
                reopened_nodes["Constructor"]["play_input"],
            ),
        }
        for label, (source, destination) in pairs.items():
            original = author["original"][label]
            report["fresh"][label] = {
                "original_source_export_text": original[
                    "source_export_text"
                ],
                "original_destination_export_text": original[
                    "destination_export_text"
                ],
                "reopened_source_export_text": source.export_text(),
                "reopened_destination_export_text": (
                    destination.export_text()
                ),
                "source_handle_changed": (
                    original["source_export_text"] != source.export_text()
                ),
                "destination_handle_changed": (
                    original["destination_export_text"]
                    != destination.export_text()
                ),
                "nodes_are_connected": bool(
                    builder.nodes_are_connected(source, destination)
                ),
                "source_is_connected": bool(
                    builder.node_output_is_connected(source)
                ),
                "destination_is_connected": bool(
                    builder.node_input_is_connected(destination)
                ),
            }

        report["graph_input_names"] = [
            str(item)
            for item in exact_array(
                h.require_call(
                    builder.get_graph_input_names(),
                    "GetGraphInputNames",
                )
            )
        ]
        report["status"] = "PASS_FRESH_CONNECTIVITY_CAPTURED"
    except Exception as error:
        deferred_error = error
        report["errors"].append(
            "%s: %s" % (type(error).__name__, str(error))
        )
        report["status"] = "FAIL_FRESH_CONNECTIVITY_CAPTURE"
    finally:
        deleted = unreal.EditorAssetLibrary.delete_asset(ASSET_PATH)
        report["delete_asset_returned"] = bool(deleted)
        report["temporary_asset_deleted"] = not (
            unreal.EditorAssetLibrary.does_asset_exist(ASSET_PATH)
        )
        if not report["temporary_asset_deleted"]:
            report["errors"].append(
                "Temporary connectivity probe deletion did not persist"
            )
            if deferred_error is None:
                deferred_error = RuntimeError(
                    "Temporary connectivity probe deletion failed"
                )
        REPORT.write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        unreal.log("[Skyguard52] P5_CONNECTIVITY_FRESH_COMPLETE")
    if deferred_error is not None:
        raise RuntimeError(str(deferred_error))


if __name__ == "__main__":
    main()
