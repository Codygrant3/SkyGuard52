"""Create one temporary MetaSound solely for UE5.8 edge persistence diagnosis."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
ATTEMPT = Path(os.environ["SKYGUARD_PHASE5_CONNECTIVITY_ATTEMPT_DIR"])
REPORT = ATTEMPT / "author_connectivity.json"
ASSET_PATH = "/Game/Skyguard/Diagnostics/Temporary/MS_P5ConnectivityProbe"
PACKAGE_PATH = "/Game/Skyguard/Diagnostics/Temporary"
ASSET_NAME = "MS_P5ConnectivityProbe"
BUILDER_NAME = "Skyguard_P5ConnectivityProbe"


def load_helpers():
    path = ROOT / "Scripts" / "build_skyguard_phase5_metasound_topology.py"
    spec = importlib.util.spec_from_file_location("p5_topology_helpers", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main():
    h = load_helpers()
    subsystem = unreal.get_engine_subsystem(
        unreal.MetaSoundBuilderSubsystem
    )
    editor = unreal.get_editor_subsystem(unreal.MetaSoundEditorSubsystem)
    if subsystem is None or editor is None:
        raise RuntimeError("MetaSound diagnostic subsystems unavailable")
    if unreal.EditorAssetLibrary.does_asset_exist(ASSET_PATH):
        raise RuntimeError("Temporary connectivity probe already exists")

    result = subsystem.create_source_builder(
        BUILDER_NAME,
        unreal.MetaSoundOutputAudioFormat.STEREO,
        True,
    )
    builder, on_play, on_finished, audio_outputs = (
        h.parse_source_builder_result(result, ASSET_NAME)
    )

    sources = {}
    for name, constructor in (
        ("ProbeWaveRuntime", False),
        ("ProbeWaveConstructor", True),
    ):
        items = h.require_call(
            builder.add_graph_input_node(
                name,
                "WaveAsset",
                unreal.MetasoundFrontendLiteral(),
                constructor,
            ),
            "AddGraphInputNode " + name,
        )
        sources[name] = h.item_with_handle(items, "output")

    wave_spec = {
        "namespace": "UE",
        "name": "Wave Player",
        "variant": "Stereo",
        "major_version": 1,
    }
    waves = {}
    edges = []
    for name in ("Runtime", "Constructor"):
        node = h.add_node(builder, wave_spec, wave_spec["name"])
        wave_input = h.find_node_input(builder, node, "Wave Asset")
        play_input = h.find_node_input(builder, node, "Play")
        loop_input = h.find_node_input(builder, node, "Loop")
        h.require_call(
            builder.set_node_input_default(
                loop_input, h.create_literal(subsystem, "Bool", False)
            ),
            "Set Loop false " + name,
        )
        source_name = "ProbeWave" + name
        h.connect(
            builder,
            sources[source_name],
            wave_input,
            name + " WaveAsset",
            edges,
        )
        h.connect(
            builder,
            on_play,
            play_input,
            name + " OnPlay",
            edges,
        )
        waves[name] = {
            "node": node,
            "wave_input": wave_input,
            "play_input": play_input,
            "left": h.find_node_output(builder, node, "Out Left"),
            "right": h.find_node_output(builder, node, "Out Right"),
            "finished": h.find_node_output(builder, node, "On Finished"),
        }

    mixer_spec = {
        "namespace": "AudioMixer",
        "name": "Audio Mixer (Stereo, 2)",
        "variant": "",
        "major_version": 1,
    }
    mixer = h.add_node(builder, mixer_spec, mixer_spec["name"])
    for index, name in enumerate(("Runtime", "Constructor")):
        h.connect(
            builder,
            waves[name]["left"],
            h.find_node_input(builder, mixer, "In %d L" % index),
            name + " left",
            edges,
        )
        h.connect(
            builder,
            waves[name]["right"],
            h.find_node_input(builder, mixer, "In %d R" % index),
            name + " right",
            edges,
        )
    h.connect(
        builder,
        h.find_node_output(builder, mixer, "Out L"),
        audio_outputs[0],
        "Mixer left output",
        edges,
    )
    h.connect(
        builder,
        h.find_node_output(builder, mixer, "Out R"),
        audio_outputs[1],
        "Mixer right output",
        edges,
    )

    trigger_spec = {
        "namespace": "TriggerAny",
        "name": "Trigger Any (2)",
        "variant": "",
        "major_version": 1,
    }
    trigger = h.add_node(builder, trigger_spec, trigger_spec["name"])
    for index, name in enumerate(("Runtime", "Constructor")):
        h.connect(
            builder,
            waves[name]["finished"],
            h.find_node_input(builder, trigger, "In %d" % index),
            name + " finished",
            edges,
        )
    h.connect(
        builder,
        h.find_node_output(builder, trigger, "Out"),
        on_finished,
        "Probe OnFinished",
        edges,
    )

    diagnostic_pairs = {
        "runtime_wave": (sources["ProbeWaveRuntime"], waves["Runtime"]["wave_input"]),
        "runtime_play": (on_play, waves["Runtime"]["play_input"]),
        "constructor_wave": (
            sources["ProbeWaveConstructor"],
            waves["Constructor"]["wave_input"],
        ),
        "constructor_play": (
            on_play,
            waves["Constructor"]["play_input"],
        ),
    }
    original = {}
    for label, (source, destination) in diagnostic_pairs.items():
        original[label] = {
            "source_export_text": source.export_text(),
            "destination_export_text": destination.export_text(),
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

    built = h.require_call(
        editor.build_to_asset(
            builder,
            "Skyguard 52 connectivity diagnostic",
            ASSET_NAME,
            PACKAGE_PATH,
            None,
        ),
        "BuildToAsset connectivity probe",
    )
    asset = next(
        (
            item
            for item in built
            if hasattr(item, "get_class")
            and h.class_name(item) == "MetaSoundSource"
        ),
        None,
    )
    if asset is None:
        asset = unreal.EditorAssetLibrary.load_asset(ASSET_PATH)
    if asset is None:
        raise RuntimeError("Temporary connectivity asset was not created")
    unreal.EditorAssetLibrary.save_asset(ASSET_PATH, False)

    report = {
        "schema": "skyguard.phase5.metasound-connectivity-author.v1",
        "asset_path": ASSET_PATH,
        "production_path": False,
        "temporary_asset": True,
        "original": original,
        "wave_nodes": {
            name: {
                "node_export_text": data["node"].export_text(),
                "wave_input_export_text": data["wave_input"].export_text(),
                "play_input_export_text": data["play_input"].export_text(),
            }
            for name, data in waves.items()
        },
        "status": "BUILT_TEMPORARY_CONNECTIVITY_PROBE",
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    unreal.log("[Skyguard52] P5_CONNECTIVITY_AUTHOR_COMPLETE")


if __name__ == "__main__":
    main()
