"""Author six governed, silent-until-sourced MetaSound Source graphs.

Run only in Unreal Editor Python. The graph topology is real and connected:
each authentic category owns a null WaveAsset graph input, a stereo Wave
Player, a stereo mixer lane, and a completion lane. No recording is imported,
network-retrieved, synthesized, or bound to the production bank. The resulting
MetaSounds therefore remain deliberately inaudible and release-blocking.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

import unreal


ROOT = Path(r"D:\Skyguard52")
DOCS = ROOT / "Docs" / "AAA_Review"
CONTRACT_PATH = DOCS / "PHASE5_METASOUND_TOPOLOGY_CONTRACT.json"
SPECS_PATH = DOCS / "PHASE5_AUDIO_ROUTING_PRIMITIVE_SPECS.json"
RUNTIME_PATH = DOCS / "PHASE5_AUDIO_RUNTIME_ROUTING_READINESS_CONTRACT.json"
BRIEFS_PATH = DOCS / "PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json"
BANK_PATH = "/Game/Skyguard/Audio/Production/DA_P5A_ProductionAudioBank"
ATTEMPT_DIRECTORY = os.environ.get("SKYGUARD_PHASE5_METASOUND_ATTEMPT_DIR")
REPORT_PATH = (
    Path(ATTEMPT_DIRECTORY) / "build_topology_manifest.json"
    if ATTEMPT_DIRECTORY
    else ROOT / "Saved" / "Reports" / "PHASE5_METASOUND_TOPOLOGY_BUILD.json"
)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def contract_bundle(contract: dict) -> dict:
    hashes = {}
    for relative in contract["contract_hash_inputs"]:
        path = ROOT / relative
        hashes[relative] = sha256_file(path)
    return {
        "files": hashes,
        "bundle_sha256": sha256_bytes(canonical_bytes(hashes)),
    }


def class_name(value: object) -> str:
    if value is None:
        return ""
    return value.get_class().get_name()


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


def unreal_struct_property(item: object, name: str):
    """Read a reflected UStruct field across UE Python wrapper variants."""
    if hasattr(item, name):
        return getattr(item, name)
    getter = getattr(item, "get_editor_property", None)
    if getter is not None:
        try:
            return getter(name)
        except Exception:
            pass
    tuple_getter = getattr(item, "to_tuple", None)
    if tuple_getter is not None:
        try:
            values = tuple(tuple_getter())
            field_index = {"node_id": 0, "vertex_id": 1}.get(name)
            if field_index is not None and field_index < len(values):
                return values[field_index]
        except Exception:
            pass
    exporter = getattr(item, "export_text", None)
    if exporter is not None:
        try:
            exported = str(exporter())
            vertex_match = re.fullmatch(
                r"\(NodeID=([0-9A-Fa-f]{32}),"
                r"VertexID=([0-9A-Fa-f]{32})\)",
                exported,
            )
            node_match = re.fullmatch(
                r"\(NodeID=([0-9A-Fa-f]{32})\)", exported
            )
            if vertex_match:
                return vertex_match.group(
                    1 if name == "node_id" else 2
                ).upper()
            if node_match and name == "node_id":
                return node_match.group(1).upper()
        except Exception:
            pass
    raise AttributeError(
        "%s omitted reflected property %s" % (type(item).__name__, name)
    )


def is_vertex_handle(item: object, direction: str | None = None) -> bool:
    type_name = type(item).__name__.lower()
    reflected_vertex_handle = (
        "metasoundbuildernode" in type_name
        and ("inputhandle" in type_name or "outputhandle" in type_name)
    )
    if direction == "input" and "inputhandle" not in type_name:
        return False
    if direction == "output" and "outputhandle" not in type_name:
        return False
    if reflected_vertex_handle:
        return True
    try:
        unreal_struct_property(item, "node_id")
        unreal_struct_property(item, "vertex_id")
        return True
    except AttributeError:
        return False


def is_node_handle(item: object) -> bool:
    type_name = type(item).__name__.lower()
    if (
        "metasoundnodehandle" in type_name
        and "inputhandle" not in type_name
        and "outputhandle" not in type_name
    ):
        return True
    try:
        unreal_struct_property(item, "node_id")
    except AttributeError:
        return False
    try:
        unreal_struct_property(item, "vertex_id")
        return False
    except AttributeError:
        return True


def item_with_handle(items: tuple, direction: str | None = None):
    for item in items:
        if is_vertex_handle(item, direction):
            return item
    qualifier = " " + direction if direction else ""
    raise RuntimeError("Call result missing%s vertex handle" % qualifier)


def item_with_node_handle(items: tuple):
    for item in items:
        if is_node_handle(item):
            return item
    raise RuntimeError("Call result missing node handle")


def item_with_handle_array(items: tuple):
    for item in items:
        if isinstance(item, (str, bytes, dict)):
            continue
        try:
            entries = list(item)
        except TypeError:
            continue
        if entries and all(
            is_vertex_handle(entry, "input") for entry in entries
        ):
            return entries
    # Some UE Python binding revisions flatten an output TArray into the outer
    # return tuple. C++ declares OnFinished before AudioOutNodeInputs, so the
    # final two direct input handles are the stereo audio destinations.
    direct_inputs = [
        item for item in items if is_vertex_handle(item, "input")
    ]
    if len(direct_inputs) >= 3:
        return direct_inputs[-2:]
    raise RuntimeError("Call result missing vertex handle array")


def parse_source_builder_result(value: object, graph_name: str) -> tuple:
    if not isinstance(value, tuple) or len(value) != 5:
        raise RuntimeError(
            "%s CreateSourceBuilder must return exact five-item UE5.8 tuple"
            % graph_name
        )
    builder, on_play, on_finished, wrapped_audio_outputs, result = value
    if not hasattr(builder, "add_graph_input_node"):
        raise RuntimeError(graph_name + " source builder object missing")
    if not is_vertex_handle(on_play, "output"):
        raise RuntimeError(graph_name + " OnPlay output handle missing")
    if not is_vertex_handle(on_finished, "input"):
        raise RuntimeError(graph_name + " OnFinished input handle missing")
    if type(wrapped_audio_outputs).__name__ != "Array":
        raise RuntimeError(
            graph_name + " stereo output destinations are not Unreal Array"
        )
    try:
        audio_outputs = list(wrapped_audio_outputs)
    except TypeError as error:
        raise RuntimeError(
            graph_name + " Unreal output Array is not iterable"
        ) from error
    if (
        len(audio_outputs) != 2
        or not all(
            is_vertex_handle(entry, "input") for entry in audio_outputs
        )
    ):
        raise RuntimeError(
            graph_name + " must return exactly two audio input handles"
        )
    if not is_success(result):
        raise RuntimeError(
            graph_name + " CreateSourceBuilder result is not SUCCEEDED"
        )
    return builder, on_play, on_finished, audio_outputs


def handle_record(handle) -> dict:
    return {
        "node_id": str(unreal_struct_property(handle, "node_id")),
        "vertex_id": str(unreal_struct_property(handle, "vertex_id")),
    }


def node_record(handle) -> dict:
    return {"node_id": str(unreal_struct_property(handle, "node_id"))}


def new_class_name(namespace: str, name: str, variant: str):
    value = unreal.MetasoundFrontendClassName()
    value.set_editor_property("namespace", namespace)
    value.set_editor_property("name", name)
    value.set_editor_property("variant", variant)
    return value


def create_literal(subsystem, data_type: str, default):
    if data_type in ("Trigger", "WaveAsset"):
        return unreal.MetasoundFrontendLiteral()
    calls = {
        "Float": (
            subsystem.create_float_meta_sound_literal,
            float(default),
        ),
        "Int32": (
            subsystem.create_int_meta_sound_literal,
            int(default),
        ),
        "Bool": (
            subsystem.create_bool_meta_sound_literal,
            bool(default),
        ),
    }
    if data_type not in calls:
        raise RuntimeError("Unsupported governed literal type " + data_type)
    function, value = calls[data_type]
    result = flatten_result(function(value))
    for item in result:
        if type(item).__name__ == "MetasoundFrontendLiteral":
            return item
    raise RuntimeError("Could not create " + data_type + " MetaSound literal")


def add_graph_input(builder, subsystem, name, data_type, default):
    result = require_call(
        builder.add_graph_input_node(
            name,
            data_type,
            create_literal(subsystem, data_type, default),
            False,
        ),
        "AddGraphInputNode " + name,
    )
    return item_with_handle(result)


def add_graph_output(builder, subsystem, name, data_type, default):
    result = require_call(
        builder.add_graph_output_node(
            name,
            data_type,
            create_literal(subsystem, data_type, default),
            False,
        ),
        "AddGraphOutputNode " + name,
    )
    return item_with_handle(result)


def find_node_input(builder, node, name):
    return item_with_handle(
        require_call(
            builder.find_node_input_by_name(node, name),
            "FindNodeInputByName " + name,
        )
    )


def find_node_output(builder, node, name):
    return item_with_handle(
        require_call(
            builder.find_node_output_by_name(node, name),
            "FindNodeOutputByName " + name,
        )
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


def connect(builder, output_handle, input_handle, label, edges):
    require_call(builder.connect_nodes(output_handle, input_handle), label)
    edges.append(
        {
            "label": label,
            "from": handle_record(output_handle),
            "to": handle_record(input_handle),
        }
    )


def add_node(builder, class_spec, resolved_name):
    class_name_value = new_class_name(
        class_spec["namespace"],
        resolved_name,
        class_spec["variant"],
    )
    return item_with_node_handle(
        require_call(
            builder.add_node_by_class_name(
                class_name_value, int(class_spec["major_version"])
            ),
            "AddNodeByClassName " + resolved_name,
        )
    )


def build_graph(graph: dict, contract: dict, bundle: dict) -> dict:
    builder_subsystem = unreal.get_engine_subsystem(
        unreal.MetaSoundBuilderSubsystem
    )
    editor_subsystem = unreal.get_editor_subsystem(
        unreal.MetaSoundEditorSubsystem
    )
    if builder_subsystem is None or editor_subsystem is None:
        raise RuntimeError("MetaSound builder/editor subsystem unavailable")

    format_value = getattr(
        unreal.MetaSoundOutputAudioFormat, contract["output_format"].upper()
    )
    create_result = builder_subsystem.create_source_builder(
            "Skyguard_" + graph["name"],
            format_value,
            bool(graph["one_shot"]),
        )
    builder, on_play, source_on_finished, audio_outputs = (
        parse_source_builder_result(create_result, graph["name"])
    )
    if graph["one_shot"]:
        on_finished = source_on_finished
    else:
        output_spec = graph["outputs"][0]
        if output_spec.get("uses_source_interface"):
            raise RuntimeError(
                "Persistent graph cannot retain the OneShot source interface"
            )
        on_finished = add_graph_output(
            builder,
            builder_subsystem,
            output_spec["serialized_name"],
            output_spec["data_type"],
            None,
        )
    if len(audio_outputs) != 2:
        raise RuntimeError(
            "%s must expose two stereo output inputs, got %d"
            % (graph["name"], len(audio_outputs))
        )

    # CreateSourceBuilder always supplies the Source "On Play" interface,
    # including persistent sources. The persistent Yak contract intentionally
    # lists only its custom continuous controls, while its loop categories
    # still consume this implicit interface.
    inputs = {"On Play": on_play}
    input_manifest = []
    if not any(
        control["serialized_name"] == "On Play"
        for control in graph["controls"]
    ):
        input_manifest.append(
            {
                "semantic_name": "On Play",
                "serialized_name": "On Play",
                "data_type": "Trigger",
                "default": None,
                "handle": handle_record(on_play),
                "source_interface": True,
                "implicit_source_interface": True,
            }
        )
    for control in graph["controls"]:
        if control.get("uses_source_interface"):
            if control["serialized_name"] != "On Play":
                raise RuntimeError(
                    "Only On Play may use the source input interface"
                )
            inputs[control["serialized_name"]] = on_play
            input_manifest.append(
                {
                    **control,
                    "handle": handle_record(on_play),
                    "source_interface": True,
                }
            )
            continue
        handle = add_graph_input(
            builder,
            builder_subsystem,
            control["serialized_name"],
            control["data_type"],
            control.get("default"),
        )
        inputs[control["serialized_name"]] = handle
        input_manifest.append(
            {
                **control,
                "handle": handle_record(handle),
                "source_interface": False,
            }
        )

    category_manifest = []
    nodes = []
    edges = []
    wave_nodes = []
    for index, category in enumerate(graph["categories"]):
        wave_handle = add_graph_input(
            builder,
            builder_subsystem,
            category["wave_input"],
            "WaveAsset",
            None,
        )
        inputs[category["wave_input"]] = wave_handle
        input_manifest.append(
            {
                "semantic_name": category["wave_input"],
                "serialized_name": category["wave_input"],
                "data_type": "WaveAsset",
                "default": None,
                "category": category["category"],
                "handle": handle_record(wave_handle),
                "source_interface": False,
            }
        )
        wave_class = contract["node_classes"]["wave_player"]
        wave_node = add_node(builder, wave_class, wave_class["name"])
        nodes.append(
            {
                "role": "wave_player",
                "category": category["category"],
                "class": wave_class,
                "handle": node_record(wave_node),
            }
        )
        wave_input = find_node_input(
            builder, wave_node, wave_class["wave_input"]
        )
        play_input = find_node_input(
            builder, wave_node, wave_class["play_input"]
        )
        loop_input = find_node_input(builder, wave_node, "Loop")
        require_call(
            builder.set_node_input_default(
                loop_input,
                create_literal(
                    builder_subsystem, "Bool", category["loop"]
                ),
            ),
            "SetNodeInputDefault Loop " + category["category"],
        )
        connect(
            builder,
            wave_handle,
            wave_input,
            "%s wave input" % category["category"],
            edges,
        )
        trigger_name = category["trigger"]
        if trigger_name not in inputs:
            raise RuntimeError(
                "%s trigger %s is not a declared input"
                % (category["category"], trigger_name)
            )
        connect(
            builder,
            inputs[trigger_name],
            play_input,
            "%s play trigger" % category["category"],
            edges,
        )
        wave_nodes.append(wave_node)
        category_manifest.append(
            {
                **category,
                "index": index,
                "wave_input_handle": handle_record(wave_handle),
                "wave_node_handle": node_record(wave_node),
                "wave_asset_pin": handle_record(wave_input),
                "play_pin": handle_record(play_input),
                "loop_pin": handle_record(loop_input),
                "left_output": handle_record(
                    find_node_output(
                        builder, wave_node, wave_class["left_output"]
                    )
                ),
                "right_output": handle_record(
                    find_node_output(
                        builder, wave_node, wave_class["right_output"]
                    )
                ),
                "finished_output": handle_record(
                    find_node_output(
                        builder, wave_node, wave_class["finished_output"]
                    )
                ),
            }
        )

    count = len(graph["categories"])
    mixer_class = contract["node_classes"]["mixer"]
    mixer_name = mixer_class["name_template"].format(category_count=count)
    mixer_node = add_node(builder, mixer_class, mixer_name)
    nodes.append(
        {
            "role": "category_mixer",
            "class": {**mixer_class, "resolved_name": mixer_name},
            "handle": node_record(mixer_node),
        }
    )
    for index, (wave_node, category) in enumerate(
        zip(wave_nodes, category_manifest)
    ):
        wave_left = find_node_output(
            builder,
            wave_node,
            contract["node_classes"]["wave_player"]["left_output"],
        )
        wave_right = find_node_output(
            builder,
            wave_node,
            contract["node_classes"]["wave_player"]["right_output"],
        )
        mixer_left = find_node_input(
            builder,
            mixer_node,
            mixer_class["left_input_template"].format(index=index),
        )
        mixer_right = find_node_input(
            builder,
            mixer_node,
            mixer_class["right_input_template"].format(index=index),
        )
        connect(
            builder,
            wave_left,
            mixer_left,
            "%s left to mixer" % category["category"],
            edges,
        )
        connect(
            builder,
            wave_right,
            mixer_right,
            "%s right to mixer" % category["category"],
            edges,
        )

    mixer_left_output = find_node_output(
        builder, mixer_node, mixer_class["left_output"]
    )
    mixer_right_output = find_node_output(
        builder, mixer_node, mixer_class["right_output"]
    )
    connect(
        builder,
        mixer_left_output,
        audio_outputs[0],
        "mixer left to graph audio output",
        edges,
    )
    connect(
        builder,
        mixer_right_output,
        audio_outputs[1],
        "mixer right to graph audio output",
        edges,
    )

    trigger_class = contract["node_classes"]["finished_trigger_any"]
    trigger_name = trigger_class["name_template"].format(category_count=count)
    trigger_node = add_node(builder, trigger_class, trigger_name)
    nodes.append(
        {
            "role": "finished_trigger_any",
            "class": {**trigger_class, "resolved_name": trigger_name},
            "handle": node_record(trigger_node),
        }
    )
    for index, wave_node in enumerate(wave_nodes):
        finished_output = find_node_output(
            builder,
            wave_node,
            contract["node_classes"]["wave_player"]["finished_output"],
        )
        trigger_input = find_node_input(
            builder,
            trigger_node,
            trigger_class["input_template"].format(index=index),
        )
        connect(
            builder,
            finished_output,
            trigger_input,
            "category %d finished to trigger any" % index,
            edges,
        )
    connect(
        builder,
        find_node_output(builder, trigger_node, trigger_class["output"]),
        on_finished,
        "trigger any to graph On Finished",
        edges,
    )

    asset_path = contract["asset_root"] + "/" + graph["name"]
    package_path, asset_name = asset_path.rsplit("/", 1)
    existing = unreal.EditorAssetLibrary.load_asset(asset_path)
    if existing is not None:
        if class_name(existing) != "MetaSoundSource":
            raise RuntimeError(
                "Wrong class at %s: %s" % (asset_path, class_name(existing))
            )
        builder.build_and_overwrite_meta_sound(existing, True)
        asset = existing
        build_mode = "OVERWROTE_GOVERNED_EXISTING_ASSET"
    else:
        built_items = require_call(
            editor_subsystem.build_to_asset(
                builder,
                contract["author"],
                asset_name,
                package_path,
                None,
            ),
            "BuildToAsset " + asset_name,
        )
        asset = None
        for item in built_items:
            if hasattr(item, "get_class") and class_name(item) == "MetaSoundSource":
                asset = item
                break
        if asset is None:
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        if asset is None or class_name(asset) != "MetaSoundSource":
            raise RuntimeError("BuildToAsset did not create " + asset_path)
        build_mode = "CREATED_GOVERNED_ASSET"

    graph_contract_sha256 = sha256_bytes(canonical_bytes(graph))
    tags = contract["metadata_tags"]
    unreal.EditorAssetLibrary.set_metadata_tag(
        asset, tags["contract_bundle_sha256"], bundle["bundle_sha256"]
    )
    unreal.EditorAssetLibrary.set_metadata_tag(
        asset, tags["graph_contract_sha256"], graph_contract_sha256
    )
    unreal.EditorAssetLibrary.set_metadata_tag(
        asset, tags["topology_schema"], contract["schema"]
    )
    unreal.EditorAssetLibrary.set_metadata_tag(
        asset, tags["source_state"], "25_OF_25_MISSING_SOURCE_BANK_WIDE"
    )
    unreal.EditorAssetLibrary.set_metadata_tag(
        asset,
        tags["behavior_state"],
        graph["behavior_acceptance_state"],
    )
    unreal.EditorAssetLibrary.save_asset(asset_path, False)

    audio_left_name, audio_left_type = member_data(
        builder, audio_outputs[0], False
    )
    audio_right_name, audio_right_type = member_data(
        builder, audio_outputs[1], False
    )
    if audio_left_type != "Audio" or audio_right_type != "Audio":
        raise RuntimeError("Source builder stereo outputs are not Audio")

    return {
        "name": graph["name"],
        "asset_path": asset_path,
        "build_mode": build_mode,
        "one_shot": graph["one_shot"],
        "graph_contract_sha256": graph_contract_sha256,
        "behavior_acceptance_state": graph["behavior_acceptance_state"],
        "controls": input_manifest,
        "outputs": [
            {
                **graph["outputs"][0],
                "handle": handle_record(on_finished),
                "source_interface": bool(
                    graph["outputs"][0].get("uses_source_interface")
                ),
            },
            {
                "semantic_name": "AudioLeft",
                "serialized_name": audio_left_name,
                "data_type": audio_left_type,
                "handle": handle_record(audio_outputs[0]),
                "source_interface": True,
            },
            {
                "semantic_name": "AudioRight",
                "serialized_name": audio_right_name,
                "data_type": audio_right_type,
                "handle": handle_record(audio_outputs[1]),
                "source_interface": True,
            },
        ],
        "nodes": nodes,
        "categories": category_manifest,
        "edges": edges,
    }


def asset_file(asset_path: str) -> Path:
    relative = asset_path.removeprefix("/Game/")
    return ROOT / "Content" / (relative + ".uasset")


def primitive_paths(specs: dict, runtime: dict) -> list[str]:
    attenuation = [
        runtime["attenuation_asset_root"] + "/ATT_" + item["name"]
        for item in specs["attenuation"]
    ]
    concurrency = [
        runtime["concurrency_asset_root"] + "/CON_" + item["name"]
        for item in specs["concurrency"]
    ]
    return attenuation + concurrency


def assert_bank_truth_boundary() -> dict:
    bank = unreal.EditorAssetLibrary.load_asset(BANK_PATH)
    if bank is None or class_name(bank) != "SkyguardAudioProductionBank":
        raise RuntimeError("Governed production bank missing or wrong class")
    entries = list(bank.get_editor_property("entries") or [])
    missing = 0
    for entry in entries:
        if (
            entry.get_editor_property("source_status")
            != unreal.SkyguardAudioSourceStatus.MISSING_SOURCE
        ):
            raise RuntimeError("Production bank source status crossed boundary")
        if entry.get_editor_property("sound"):
            raise RuntimeError("Production bank acquired unauthorized Sound")
        if str(entry.get_editor_property("provenance_id")) not in ("", "None"):
            raise RuntimeError("Production bank acquired unauthorized provenance")
        if str(entry.get_editor_property("source_sha256")):
            raise RuntimeError("Production bank acquired unauthorized source hash")
        missing += 1
    audit = bank.evaluate_readiness()
    if (
        len(entries) != 25
        or missing != 25
        or int(audit.bound_production_source_count) != 0
        or int(audit.explicit_missing_source_count) != 25
        or bool(audit.production_ready)
    ):
        raise RuntimeError("Production bank no longer proves 25 missing sources")
    return {
        "entry_count": len(entries),
        "explicit_missing_source_count": missing,
        "bound_production_source_count": int(
            audit.bound_production_source_count
        ),
        "production_ready": bool(audit.production_ready),
    }


def main():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    specs = json.loads(SPECS_PATH.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME_PATH.read_text(encoding="utf-8"))
    bundle = contract_bundle(contract)
    graph_manifests = [
        build_graph(graph, contract, bundle) for graph in contract["graphs"]
    ]
    bank = assert_bank_truth_boundary()

    governed_paths = primitive_paths(specs, runtime) + [
        graph["asset_path"] for graph in graph_manifests
    ]
    asset_hashes = {}
    for path in governed_paths:
        disk_path = asset_file(path)
        if not disk_path.is_file():
            raise RuntimeError("Serialized governed asset missing: " + str(disk_path))
        asset_hashes[path] = sha256_file(disk_path)

    result = {
        "schema": "skyguard.phase5.metasound-topology-build.v1",
        "topology_contract_schema": contract["schema"],
        "contract_bundle": bundle,
        "graph_count": len(graph_manifests),
        "primitive_count": len(governed_paths) - len(graph_manifests),
        "governed_asset_count": len(governed_paths),
        "authentic_source_count": 0,
        "metasound_soundwave_binding_count": 0,
        "procedural_generator_count": 0,
        "production_bank": bank,
        "graphs": graph_manifests,
        "serialized_asset_sha256": asset_hashes,
        "fresh_for_current_contract": False,
        "production_ready": False,
        "shipping_allowed": False,
        "packaged_audible_acceptance": False,
        "status": "BUILT_SILENT_GOVERNED_TOPOLOGY_REQUIRES_FRESH_AUDIT",
    }
    if (
        result["graph_count"] != 6
        or result["primitive_count"] != 29
        or result["governed_asset_count"] != 35
    ):
        raise RuntimeError("Governed graph/primitive coverage mismatch")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    unreal.log("[Skyguard52] " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
