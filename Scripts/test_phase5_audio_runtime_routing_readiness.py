#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "Scripts" / "verify_phase5_audio_runtime_routing_readiness.py"
SPEC = importlib.util.spec_from_file_location("routing_readiness", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RuntimeRoutingReadinessTests(unittest.TestCase):
    def test_current_tree_is_structurally_valid_but_fail_closed(self):
        report = MODULE.evaluate(ROOT)
        self.assertTrue(report["structural_contract_valid"])
        self.assertFalse(report["runtime_routing_ready"])
        if report["serialized_unreal_audit"]["fresh_for_current_contract"]:
            self.assertEqual(
                report["status"],
                "CONTRACT_VALID_EXTERNAL_AUDIO_AND_ACCEPTANCE_REQUIRED",
            )
        self.assertEqual(report["assets"]["routing"]["present_count"], 7)
        topology_accepted = report["serialized_unreal_audit"][
            "metasound_topology"
        ]["accepted_topology_only"]
        self.assertEqual(
            report["assets"]["metasounds"]["present_count"],
            6 if topology_accepted else 0,
        )
        self.assertEqual(report["assets"]["attenuation"]["present_count"], 15)
        self.assertEqual(report["assets"]["concurrency"]["present_count"], 14)
        self.assertEqual(report["authentic_sources"]["approved_count"], 0)
        self.assertEqual(report["runtime_source"]["event_binding_count"], 11)
        self.assertEqual(report["runtime_source"]["gameplay_marker_errors"], {})
        self.assertEqual(
            report["runtime_source"]["production_bank_markers_missing"], []
        )
        self.assertEqual(
            report["routing_primitive_specs"],
            {
                "attenuation_count": 15,
                "concurrency_count": 14,
                "metasound_interface_count": 6,
                "errors": [],
            },
        )
        self.assertTrue(
            report["serialized_unreal_audit"]["routing_primitives"][
                "accepted_routing_only"
            ]
        )
        self.assertEqual(
            report["serialized_unreal_audit"]["fresh_for_current_contract"],
            topology_accepted,
        )

    def test_missing_async_prime_marker_fails_contract(self):
        path = ROOT / "Source" / "Skyguard52" / "SkyguardAudioDirectorComponent.cpp"
        text = path.read_text(encoding="utf-8-sig").replace(
            "RequestAsyncLoad(", "RequestDeferred("
        )
        report = MODULE.evaluate(
            ROOT, source_overrides={"SkyguardAudioDirectorComponent.cpp": text}
        )
        self.assertFalse(report["structural_contract_valid"])
        self.assertIn(
            "runtime_source_required_marker_missing", report["structural_errors"]
        )

    def test_synchronous_gameplay_load_fails_contract(self):
        path = ROOT / "Source" / "Skyguard52" / "SkyguardAudioDirectorComponent.cpp"
        text = path.read_text(encoding="utf-8-sig") + "\n// LoadSynchronous\n"
        report = MODULE.evaluate(
            ROOT, source_overrides={"SkyguardAudioDirectorComponent.cpp": text}
        )
        self.assertFalse(report["structural_contract_valid"])
        self.assertIn(
            "runtime_source_synchronous_load_forbidden", report["structural_errors"]
        )

    def test_missing_mission_prime_fails_contract(self):
        name = "SkyguardMission10IntegrationDirector.cpp"
        path = ROOT / "Source" / "Skyguard52" / name
        text = path.read_text(encoding="utf-8-sig").replace(
            "AudioDirector->PrimeConfiguredAssets()",
            "AudioDirector->DeferConfiguredAssets()",
        )
        report = MODULE.evaluate(ROOT, source_overrides={name: text})
        self.assertFalse(report["structural_contract_valid"])
        self.assertEqual(report["runtime_source"]["missions_missing_prime"], [name])

    def test_missing_gameplay_audio_hook_fails_contract(self):
        name = "SkyguardDrone.cpp"
        path = ROOT / "Source" / "Skyguard52" / name
        text = path.read_text(encoding="utf-8-sig").replace(
            "ESkyguardAudioEvent::ExplosionHeavy",
            "ESkyguardAudioEvent::ExplosionSmall",
        )
        report = MODULE.evaluate(ROOT, source_overrides={name: text})
        self.assertFalse(report["structural_contract_valid"])
        self.assertIn(
            "gameplay_audio_routing_marker_missing", report["structural_errors"]
        )

    def test_missing_production_routing_guard_fails_contract(self):
        name = "SkyguardAudioProductionBank.cpp"
        path = ROOT / "Source" / "Skyguard52" / name
        text = path.read_text(encoding="utf-8-sig").replace(
            "Audit.MissingConcurrencyBindings.IsEmpty()",
            "true",
        )
        report = MODULE.evaluate(ROOT, source_overrides={name: text})
        self.assertFalse(report["structural_contract_valid"])
        self.assertIn(
            "production_bank_routing_guard_missing", report["structural_errors"]
        )

    def test_production_bank_is_asynchronously_bound_and_loops_are_routed(self):
        report = MODULE.evaluate(ROOT)
        self.assertEqual(
            report["runtime_source"]["required_markers_missing"], []
        )
        self.assertEqual(
            report["runtime_source"]["forbidden_markers_found"], []
        )

    def test_routing_primitive_specs_fail_on_missing_named_recipe(self):
        contract = MODULE.load_json(
            ROOT / "Docs" / "AAA_Review"
            / "PHASE5_AUDIO_RUNTIME_ROUTING_READINESS_CONTRACT.json"
        )
        briefs = MODULE.load_json(
            ROOT / "Docs" / "AAA_Review"
            / "PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json"
        )
        specs = MODULE.load_json(
            ROOT / "Docs" / "AAA_Review"
            / "PHASE5_AUDIO_ROUTING_PRIMITIVE_SPECS.json"
        )
        specs["attenuation"] = specs["attenuation"][:-1]
        errors = MODULE.validate_routing_primitive_specs(specs, briefs, contract)
        self.assertIn(
            "attenuation primitive specs are not exact and unique", errors
        )

    def test_asset_presence_cannot_override_source_and_acceptance_blocks(self):
        contract = MODULE.load_json(
            ROOT / "Docs" / "AAA_Review"
            / "PHASE5_AUDIO_RUNTIME_ROUTING_READINESS_CONTRACT.json"
        )
        briefs = MODULE.load_json(
            ROOT / "Docs" / "AAA_Review"
            / "PHASE5_AUDIO_CATEGORY_ACQUISITION_BRIEFS.json"
        )
        attenuation, concurrency = MODULE.expected_named_assets(briefs, contract)
        all_expected = set(contract["routing_assets"])
        all_expected.update(contract["metasound_assets"])
        all_expected.update(attenuation)
        all_expected.update(concurrency)
        all_expected.add(
            "/Game/Skyguard/Audio/Production/DA_P5A_ProductionAudioBank"
        )
        absent_topology = {
            "present": False,
            "path": None,
            "accepted_topology_only": False,
            "contract_hash_bound": False,
            "contract_bundle_sha256": None,
            "note": "test fixture: no topology receipt",
        }
        with mock.patch.object(
            MODULE,
            "find_latest_metasound_topology_audit",
            return_value=absent_topology,
        ):
            report = MODULE.evaluate(ROOT, virtual_asset_paths=all_expected)
        self.assertEqual(report["assets"]["metasounds"]["present_count"], 6)
        self.assertFalse(report["runtime_routing_ready"])
        self.assertIn(
            "authentic licensed or project-owned sources", report["external_blocks"]
        )
        self.assertIn(
            "fresh final serialized Unreal graph audit",
            report["external_blocks"],
        )


if __name__ == "__main__":
    unittest.main()
