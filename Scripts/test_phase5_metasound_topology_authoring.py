#!/usr/bin/env python3

import copy
import importlib.util
import json
import os
import sys
import types
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "Docs" / "AAA_Review"
SCRIPTS = ROOT / "Scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


VERIFIER = load_module(
    "phase5_metasound_topology_contract_verifier",
    SCRIPTS / "verify_phase5_metasound_topology_contract.py",
)


def load_author_module():
    previous = sys.modules.get("unreal")
    sys.modules["unreal"] = types.ModuleType("unreal")
    try:
        return load_module(
            "phase5_metasound_topology_author",
            SCRIPTS / "build_skyguard_phase5_metasound_topology.py",
        )
    finally:
        if previous is None:
            sys.modules.pop("unreal", None)
        else:
            sys.modules["unreal"] = previous


def load_fresh_verifier_module():
    previous = sys.modules.get("unreal")
    previous_attempt = os.environ.get(
        "SKYGUARD_PHASE5_METASOUND_ATTEMPT_DIR"
    )
    sys.modules["unreal"] = types.ModuleType("unreal")
    os.environ["SKYGUARD_PHASE5_METASOUND_ATTEMPT_DIR"] = str(
        ROOT / "Saved" / "Reports" / "OfflineFreshVerifierTest"
    )
    try:
        return load_module(
            "phase5_metasound_topology_fresh_verifier",
            SCRIPTS / "verify_skyguard_phase5_metasound_topology.py",
        )
    finally:
        if previous is None:
            sys.modules.pop("unreal", None)
        else:
            sys.modules["unreal"] = previous
        if previous_attempt is None:
            os.environ.pop(
                "SKYGUARD_PHASE5_METASOUND_ATTEMPT_DIR", None
            )
        else:
            os.environ[
                "SKYGUARD_PHASE5_METASOUND_ATTEMPT_DIR"
            ] = previous_attempt


class Phase5MetaSoundTopologyAuthoringTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(
            (
                DOCS / "PHASE5_METASOUND_TOPOLOGY_CONTRACT.json"
            ).read_text(encoding="utf-8")
        )
        self.specs = json.loads(
            (
                DOCS / "PHASE5_AUDIO_ROUTING_PRIMITIVE_SPECS.json"
            ).read_text(encoding="utf-8")
        )
        self.runtime = json.loads(
            (
                DOCS
                / "PHASE5_AUDIO_RUNTIME_ROUTING_READINESS_CONTRACT.json"
            ).read_text(encoding="utf-8")
        )
        self.briefs = json.loads(
            (
                DOCS / "PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json"
            ).read_text(encoding="utf-8")
        )

    def evaluate(self, contract=None):
        return VERIFIER.evaluate(
            contract or self.contract,
            self.specs,
            self.runtime,
            self.briefs,
        )

    def test_current_contract_passes_exact_coverage(self):
        report = self.evaluate()
        self.assertEqual([], report["errors"])
        self.assertEqual(6, report["graph_count"])
        self.assertEqual(25, report["category_count"])
        self.assertEqual(25, report["wave_asset_input_count"])
        self.assertEqual(0, report["authentic_source_count"])
        self.assertFalse(report["production_ready"])
        self.assertFalse(report["shipping_allowed"])
        self.assertEqual(64, len(report["contract_bundle"]["bundle_sha256"]))

    def test_truth_boundary_mutations_fail_closed(self):
        for key, unsafe in (
            ("authentic_source_count", 1),
            ("required_explicit_missing_source_count", 24),
            ("wave_asset_defaults_must_be_null", False),
            ("procedural_generators_allowed", True),
            ("production_bank_sound_bindings_allowed", True),
            ("production_ready_allowed", True),
            ("shipping_allowed", True),
            ("packaged_audible_acceptance_claim_allowed", True),
        ):
            with self.subTest(key=key):
                mutated = copy.deepcopy(self.contract)
                mutated["truth_boundary"][key] = unsafe
                self.assertTrue(self.evaluate(mutated)["errors"])

    def test_missing_graph_is_rejected(self):
        mutated = copy.deepcopy(self.contract)
        mutated["graphs"].pop()
        self.assertIn(
            "exactly six unique MetaSound graphs are required",
            self.evaluate(mutated)["errors"],
        )

    def test_semantic_interface_drift_is_rejected(self):
        mutated = copy.deepcopy(self.contract)
        mutated["graphs"][0]["controls"][0]["semantic_name"] = "WrongRPM"
        self.assertTrue(
            any(
                "semantic input order/coverage mismatch" in error
                for error in self.evaluate(mutated)["errors"]
            )
        )

    def test_category_composition_drift_is_rejected(self):
        mutated = copy.deepcopy(self.contract)
        mutated["graphs"][0]["categories"].reverse()
        self.assertTrue(
            any(
                "category composition/order mismatch" in error
                for error in self.evaluate(mutated)["errors"]
            )
        )

    def test_non_null_or_implicit_loop_contract_is_rejected(self):
        mutated = copy.deepcopy(self.contract)
        mutated["graphs"][0]["categories"][0]["loop"] = None
        self.assertTrue(
            any(
                "loop must be explicit bool" in error
                for error in self.evaluate(mutated)["errors"]
            )
        )

    def test_procedural_node_class_is_rejected(self):
        mutated = copy.deepcopy(self.contract)
        mutated["node_classes"]["wave_player"]["name"] = "Noise Generator"
        self.assertIn(
            "forbidden synthesized node class: noise",
            self.evaluate(mutated)["errors"],
        )

    def test_author_does_not_import_download_or_bind_audio(self):
        source = (
            SCRIPTS / "build_skyguard_phase5_metasound_topology.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("AudioImport", source)
        self.assertNotIn("download", source.lower())
        self.assertNotIn("set_editor_property(\"sound\"", source)
        self.assertIn("MISSING_SOURCE", source)
        self.assertIn("bound_production_source_count", source)
        self.assertIn("metasound_soundwave_binding_count", source)
        self.assertIn("procedural_generator_count", source)

    def test_author_serializes_contract_metadata_and_35_hashes(self):
        source = (
            SCRIPTS / "build_skyguard_phase5_metasound_topology.py"
        ).read_text(encoding="utf-8")
        self.assertIn("set_metadata_tag", source)
        self.assertIn("contract_bundle_sha256", source)
        self.assertIn("graph_contract_sha256", source)
        self.assertIn("serialized_asset_sha256", source)
        self.assertIn('result["governed_asset_count"] != 35', source)

    def test_persistent_yak_implicit_on_play_is_manifested(self):
        source = (
            SCRIPTS / "build_skyguard_phase5_metasound_topology.py"
        ).read_text(encoding="utf-8")
        self.assertIn('inputs = {"On Play": on_play}', source)
        self.assertIn('"implicit_source_interface": True', source)
        yak = self.contract["graphs"][0]
        self.assertFalse(yak["one_shot"])
        self.assertNotIn(
            "On Play",
            [item["serialized_name"] for item in yak["controls"]],
        )
        self.assertEqual(
            {"On Play"},
            {item["trigger"] for item in yak["categories"]},
        )

    def test_ue58_source_builder_return_shapes_are_parsed_semantically(self):
        author = load_author_module()

        class MetaSoundBuilderNodeOutputHandle:
            def __init__(self, node_id, vertex_id):
                self.node_id = node_id
                self.vertex_id = vertex_id

        class MetaSoundBuilderNodeInputHandle:
            def __init__(self, node_id, vertex_id):
                self._values = {
                    "node_id": node_id,
                    "vertex_id": vertex_id,
                }

            def get_editor_property(self, name):
                return self._values[name]

        class MetaSoundNodeHandle:
            def __init__(self, node_id):
                self._values = {"node_id": node_id}

            def get_editor_property(self, name):
                if name not in self._values:
                    raise RuntimeError("missing property")
                return self._values[name]

        class MetaSoundBuilderNodeInputHandleTupleOnly:
            def __init__(self, node_id, vertex_id):
                self._values = (node_id, vertex_id)

            def to_tuple(self):
                return self._values

        class MetaSoundBuilderNodeOutputHandleExportOnly:
            def to_tuple(self):
                return ()

            def export_text(self):
                return (
                    "(NodeID=FB13FA364E032BF8CF7EE7954085E6C9,"
                    "VertexID=CC02F2799674D5DA72ABBEB51D1DC820)"
                )

        class Builder:
            def add_graph_input_node(self):
                return None

        class UnrealArrayWrapper:
            def __init__(self, values):
                self._values = values

            def __iter__(self):
                return iter(self._values)

        on_play = MetaSoundBuilderNodeOutputHandle("play-node", "play-pin")
        on_finished = MetaSoundBuilderNodeInputHandle(
            "finish-node", "finish-pin"
        )
        audio_outputs = [
            MetaSoundBuilderNodeInputHandle("left-node", "left-pin"),
            MetaSoundBuilderNodeInputHandle("right-node", "right-pin"),
        ]
        create_items = (
            Builder(),
            on_play,
            on_finished,
            audio_outputs,
            "MetaSoundBuilderResult.SUCCEEDED",
        )

        self.assertIs(
            on_play, author.item_with_handle(create_items, "output")
        )
        self.assertIs(
            on_finished, author.item_with_handle(create_items, "input")
        )
        self.assertEqual(
            audio_outputs, author.item_with_handle_array(create_items)
        )
        self.assertEqual(
            {"node_id": "finish-node", "vertex_id": "finish-pin"},
            author.handle_record(on_finished),
        )
        self.assertEqual(
            {"node_id": "node-only"},
            author.node_record(MetaSoundNodeHandle("node-only")),
        )
        tuple_only = MetaSoundBuilderNodeInputHandleTupleOnly(
            "tuple-node", "tuple-pin"
        )
        self.assertTrue(author.is_vertex_handle(tuple_only, "input"))
        self.assertEqual(
            {"node_id": "tuple-node", "vertex_id": "tuple-pin"},
            author.handle_record(tuple_only),
        )
        wrapped_outputs = UnrealArrayWrapper(audio_outputs)
        wrapped_items = (
            Builder(),
            on_play,
            on_finished,
            wrapped_outputs,
            "MetaSoundBuilderResult.SUCCEEDED",
        )
        self.assertEqual(
            audio_outputs, author.item_with_handle_array(wrapped_items)
        )
        flattened_items = (
            Builder(),
            on_play,
            on_finished,
            *audio_outputs,
            "MetaSoundBuilderResult.SUCCEEDED",
        )
        self.assertEqual(
            audio_outputs, author.item_with_handle_array(flattened_items)
        )
        export_only = MetaSoundBuilderNodeOutputHandleExportOnly()
        self.assertEqual(
            {
                "node_id": "FB13FA364E032BF8CF7EE7954085E6C9",
                "vertex_id": "CC02F2799674D5DA72ABBEB51D1DC820",
            },
            author.handle_record(export_only),
        )

        class Array:
            def __init__(self, values):
                self._values = values

            def __iter__(self):
                return iter(self._values)

        strict_tuple = (
            Builder(),
            on_play,
            on_finished,
            Array(audio_outputs),
            "MetaSoundBuilderResult.SUCCEEDED",
        )
        parsed = author.parse_source_builder_result(
            strict_tuple, "MS_Test"
        )
        self.assertIs(on_play, parsed[1])
        self.assertEqual(audio_outputs, parsed[3])
        with self.assertRaises(RuntimeError):
            author.parse_source_builder_result(
                strict_tuple[:-1], "MS_Test"
            )
        with self.assertRaises(RuntimeError):
            author.parse_source_builder_result(
                (
                    Builder(),
                    on_play,
                    on_finished,
                    audio_outputs,
                    "MetaSoundBuilderResult.SUCCEEDED",
                ),
                "MS_Test",
            )

        class Name:
            def __init__(self, value):
                self.value = value

            def __str__(self):
                return self.value

        class MemberDataBuilder:
            def get_node_input_data(self, _handle):
                return (
                    Name("Audio Left"),
                    Name("Audio"),
                    "MetaSoundBuilderResult.SUCCEEDED",
                )

        self.assertEqual(
            ("Audio Left", "Audio"),
            author.member_data(MemberDataBuilder(), object(), False),
        )

    def test_fresh_audit_reopens_handles_edges_hashes_and_bank(self):
        source = (
            SCRIPTS / "verify_skyguard_phase5_metasound_topology.py"
        ).read_text(encoding="utf-8")
        for marker in (
            "find_or_begin_building",
            "contains_node_output",
            "contains_node_input",
            "contains_node",
            "nodes_are_connected",
            "get_graph_input_default",
            "serialized_asset_sha256",
            "fresh_for_current_contract",
            "explicit_missing_source_count",
            "production_ready",
            "import_text",
            "canonical_interface_name",
            "UE.Source.OnPlay",
            "UE.Source.OneShot.OnFinished",
            "find_graph_input_node",
            "find_graph_output_node",
            "resolved_graph_inputs",
            "resolved_graph_outputs",
            "node_input_handle",
            "resolved_wave_inputs",
            "exact_internal_pair_connected_edge_count",
            "interface_endpoint_connected_edge_count",
            "interface_exact_pair_observed_edge_count",
            "UNCHANGED_REOPENED_HANDLES_PLUS_BOTH_ENDPOINTS_CONNECTED",
            "CONNECTIVITY_EVIDENCE_SHA256",
            "ORIGINAL_AND_REOPENED_HANDLES_UNCHANGED",
        ):
            self.assertIn(marker, source)

    def test_fresh_audit_normalizes_ue_source_interfaces(self):
        fresh = load_fresh_verifier_module()
        self.assertEqual(
            "UE.Source.OnPlay",
            fresh.canonical_interface_name("On Play", True),
        )
        self.assertEqual(
            "UE.Source.OneShot.OnFinished",
            fresh.canonical_interface_name("On Finished", True),
        )
        self.assertEqual(
            "Source_RifleMuzzle",
            fresh.canonical_interface_name("Source_RifleMuzzle", False),
        )
        with self.assertRaises(RuntimeError):
            fresh.canonical_interface_name("Unknown Interface", True)

        class MetaSoundBuilderNodeOutputHandle:
            pass

        class MetaSoundBuilderNodeInputHandle:
            pass

        class Builder:
            def find_graph_input_node(self, name):
                self.input_name = name
                return (
                    object(),
                    "Trigger",
                    MetaSoundBuilderNodeOutputHandle(),
                    "MetaSoundBuilderResult.SUCCEEDED",
                )

            def find_graph_output_node(self, name):
                self.output_name = name
                return (
                    object(),
                    "Trigger",
                    MetaSoundBuilderNodeInputHandle(),
                    "MetaSoundBuilderResult.SUCCEEDED",
                )

            def find_node_input_by_name(self, node, name):
                self.internal_node = node
                self.internal_input_name = name
                return (
                    MetaSoundBuilderNodeInputHandle(),
                    "MetaSoundBuilderResult.SUCCEEDED",
                )

        builder = Builder()
        self.assertEqual(
            "MetaSoundBuilderNodeOutputHandle",
            type(
                fresh.graph_member_handle(
                    builder, "UE.Source.OnPlay", True
                )
            ).__name__,
        )
        self.assertEqual(
            "MetaSoundBuilderNodeInputHandle",
            type(
                fresh.graph_member_handle(
                    builder, "UE.Source.OneShot.OnFinished", False
                )
            ).__name__,
        )
        fresh.node_handle = lambda record: ("node", record["node_id"])
        self.assertEqual(
            "MetaSoundBuilderNodeInputHandle",
            type(
                fresh.node_input_handle(
                    builder, {"node_id": "ABC"}, "Wave Asset"
                )
            ).__name__,
        )
        self.assertEqual(("node", "ABC"), builder.internal_node)
        self.assertEqual("Wave Asset", builder.internal_input_name)

    def test_fresh_audit_is_attempt_scoped(self):
        for filename in (
            "build_skyguard_phase5_metasound_topology.py",
            "verify_skyguard_phase5_metasound_topology.py",
        ):
            source = (SCRIPTS / filename).read_text(encoding="utf-8")
            self.assertIn(
                "SKYGUARD_PHASE5_METASOUND_ATTEMPT_DIR", source
            )

    def test_persisted_connectivity_probe_is_temporary_and_self_cleaning(self):
        author = (
            SCRIPTS
            / "diagnose_phase5_metasound_persisted_connectivity_author.py"
        ).read_text(encoding="utf-8")
        fresh = (
            SCRIPTS
            / "diagnose_phase5_metasound_persisted_connectivity_fresh.py"
        ).read_text(encoding="utf-8")
        runner = (
            SCRIPTS
            / "run_phase5_metasound_persisted_connectivity_diagnostic.ps1"
        ).read_text(encoding="utf-8")
        temporary_path = (
            "/Game/Skyguard/Diagnostics/Temporary/"
            "MS_P5ConnectivityProbe"
        )
        self.assertIn(temporary_path, author)
        self.assertIn(temporary_path, fresh)
        self.assertNotIn(
            "/Game/Skyguard/Audio/Production/MetaSounds", author
        )
        self.assertNotIn(
            "/Game/Skyguard/Audio/Production/MetaSounds", fresh
        )
        self.assertIn('("ProbeWaveRuntime", False)', author)
        self.assertIn('("ProbeWaveConstructor", True)', author)
        self.assertIn("nodes_are_connected", author)
        self.assertIn("nodes_are_connected", fresh)
        self.assertIn("source_handle_changed", fresh)
        self.assertIn("destination_handle_changed", fresh)
        self.assertIn("delete_asset(ASSET_PATH)", fresh)
        self.assertIn("Quarantine-TemporaryAssetFiles", runner)
        self.assertIn("PASS_DIAGNOSTIC_ONLY", runner)


if __name__ == "__main__":
    unittest.main()
