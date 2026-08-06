"""Mutation tests for the fail-closed Phase 5 audio Shipping boundary."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCRIPT = ROOT / "Scripts/verify_phase5_audio_shipping_boundary.py"
SPEC = importlib.util.spec_from_file_location("phase5_shipping", SCRIPT)
VERIFY = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VERIFY)


class Phase5AudioShippingBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = VERIFY.load_json(VERIFY.POLICY_PATH)
        cls.readiness = VERIFY.load_json(VERIFY.READINESS_PATH)
        cls.acquisition = VERIFY.load_json(VERIFY.ACQUISITION_PATH)

    def evaluate(
        self,
        *,
        policy=None,
        readiness=None,
        acquisition=None,
        runtime=None,
        config=None,
        imported=None,
        loose=None,
    ):
        return VERIFY.evaluate(
            policy or self.policy,
            readiness or self.readiness,
            acquisition or self.acquisition,
            runtime or {},
            config or {},
            imported or {},
            loose or {},
        )

    def make_approved_state(self):
        acquisition = copy.deepcopy(self.acquisition)
        for entry in acquisition["entries"]:
            entry["acquisition_state"] = "APPROVED_FOR_GOVERNED_IMPORT"
        readiness = copy.deepcopy(self.readiness)
        readiness["production_ready"] = True
        readiness["summary"]["production_ready"] = True
        readiness["summary"]["import_contract"][
            "fresh_unreal_routing_audit_present"
        ] = True
        readiness["summary"]["packaged_audible_acceptance_passed"] = True
        return readiness, acquisition

    def test_clean_fully_accepted_state_allows_shipping(self):
        readiness, acquisition = self.make_approved_state()
        result = self.evaluate(readiness=readiness, acquisition=acquisition)
        self.assertEqual([], result["blockers"])
        self.assertTrue(result["shipping_allowed"])

    def test_current_runtime_and_cook_config_no_longer_reference_imported_audio(self):
        runtime = VERIFY.collect_scan_files(
            self.policy.get("runtime_scan_globs", [])
        )
        config = VERIFY.collect_scan_files(
            self.policy.get("config_scan_globs", [])
        )
        result = self.evaluate(runtime=runtime, config=config)
        self.assertEqual([], result["runtime_references"])
        self.assertEqual([], result["forbidden_cook_references"])

    def test_runtime_imported_reference_blocks_shipping(self):
        readiness, acquisition = self.make_approved_state()
        result = self.evaluate(
            readiness=readiness,
            acquisition=acquisition,
            runtime={
                "Source/Test.cpp": (
                    'TEXT("/Game/Skyguard/Audio/Imported/legacy.legacy")'
                )
            },
        )
        self.assertIn("FORBIDDEN_LEGACY_RUNTIME_REFERENCES", result["blockers"])
        self.assertFalse(result["shipping_allowed"])

    def test_always_cook_imported_root_blocks_shipping(self):
        readiness, acquisition = self.make_approved_state()
        result = self.evaluate(
            readiness=readiness,
            acquisition=acquisition,
            config={
                "Config/Test.ini": (
                    '+DirectoriesToAlwaysCook=(Path="/Game/Skyguard/Audio/Imported")'
                )
            },
        )
        self.assertIn(
            "FORBIDDEN_LEGACY_ALWAYS_COOK_DIRECTIVE", result["blockers"]
        )

    def test_legacy_imported_uasset_blocks_shipping(self):
        readiness, acquisition = self.make_approved_state()
        result = self.evaluate(
            readiness=readiness,
            acquisition=acquisition,
            imported={
                "Content/Skyguard/Audio/Imported": [
                    "Content/Skyguard/Audio/Imported/legacy.uasset"
                ]
            },
        )
        self.assertIn(
            "FORBIDDEN_LEGACY_IMPORTED_ASSETS_PRESENT", result["blockers"]
        )

    def test_loose_source_media_blocks_shipping(self):
        readiness, acquisition = self.make_approved_state()
        result = self.evaluate(
            readiness=readiness,
            acquisition=acquisition,
            loose={
                "Content/Skyguard/Audio/Source": [
                    "Content/Skyguard/Audio/Source/legacy.ogg"
                ]
            },
        )
        self.assertIn(
            "FORBIDDEN_LOOSE_SOURCE_MEDIA_IN_CONTENT", result["blockers"]
        )

    def test_incomplete_acquisition_blocks_shipping(self):
        readiness, _ = self.make_approved_state()
        result = self.evaluate(readiness=readiness)
        self.assertIn("AUTHENTIC_SOURCE_BUNDLES_NOT_APPROVED", result["blockers"])

    def test_missing_packaged_audible_acceptance_blocks_shipping(self):
        readiness, acquisition = self.make_approved_state()
        readiness["summary"]["packaged_audible_acceptance_passed"] = False
        result = self.evaluate(readiness=readiness, acquisition=acquisition)
        self.assertIn(
            "PACKAGED_AUDIBLE_ACCEPTANCE_MISSING", result["blockers"]
        )

    def test_unsafe_policy_is_invalid(self):
        policy = copy.deepcopy(self.policy)
        policy["shipping_gate_exit_code_when_blocked"] = 0
        result = self.evaluate(policy=policy)
        self.assertTrue(result["policy_errors"])
        self.assertFalse(result["shipping_allowed"])


if __name__ == "__main__":
    unittest.main()
