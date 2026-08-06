"""Offline mutation tests for the P5-A audio routing contract."""

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
VERIFIER_PATH = ROOT / "Scripts/verify_phase5_p5a_audio_routing_contract.py"
CONTRACT_PATH = (
    ROOT / "Docs/AAA_Review/PHASE5_P5A_IDENTITY_BED_ROUTING_CONTRACT.json"
)

SPEC = importlib.util.spec_from_file_location("p5a_verifier", VERIFIER_PATH)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class Phase5P5ARoutingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_authoritative_contract_is_valid(self):
        self.assertEqual([], VERIFIER.validate_contract(self.contract))
        self.assertEqual([], VERIFIER.validate_builder(VERIFIER.DEFAULT_BUILDER))

    def test_fresh_audit_and_supervisor_are_present(self):
        fresh = ROOT / "Scripts/verify_skyguard_phase5_p5a_audio_routing.py"
        supervisor = ROOT / "Scripts/run_skyguard_phase5_p5a_audio_routing_gate.ps1"
        self.assertTrue(fresh.is_file())
        self.assertTrue(supervisor.is_file())
        fresh_text = fresh.read_text(encoding="utf-8")
        supervisor_text = supervisor.read_text(encoding="utf-8")
        self.assertNotIn("AssetImportTask", fresh_text)
        self.assertIn("Assert-NoActiveUnrealLane", supervisor_text)
        self.assertIn("PASS_ROUTING_ONLY", supervisor_text)
        self.assertIn("identity_sources_missing = 5", supervisor_text)

    def test_duplicate_routing_path_is_rejected(self):
        mutated = copy.deepcopy(self.contract)
        mutated["routing_assets"][1]["asset_path"] = (
            mutated["routing_assets"][0]["asset_path"]
        )
        errors = VERIFIER.validate_contract(mutated)
        self.assertTrue(any("unique" in error for error in errors))

    def test_unsourced_placeholder_cannot_claim_production(self):
        mutated = copy.deepcopy(self.contract)
        mutated["identity_bed_placeholders"][0]["source_status"] = (
            "PROJECT_OWNED_RECORDING"
        )
        mutated["current_state"]["production_ready"] = True
        errors = VERIFIER.validate_contract(mutated)
        self.assertTrue(any("MISSING_SOURCE" in error for error in errors))
        self.assertTrue(any("production readiness" in error for error in errors))

    def test_missing_receipt_is_valid_but_not_built(self):
        with tempfile.TemporaryDirectory() as temp:
            absent = Path(temp) / "absent.json"
            audit = VERIFIER.run(
                CONTRACT_PATH, VERIFIER.DEFAULT_BUILDER, absent
            )
        self.assertTrue(audit["offline_contract_valid"])
        self.assertFalse(audit["routing_scaffold_built"])
        self.assertFalse(audit["production_ready"])


if __name__ == "__main__":
    unittest.main()
