"""Mutation tests for the Phase 5 offline production-readiness boundary."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCRIPT = ROOT / "Scripts/verify_phase5_audio_production_readiness.py"
SPEC = importlib.util.spec_from_file_location("phase5_readiness", SCRIPT)
VERIFY = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VERIFY)


class Phase5AudioProductionReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session_schema = VERIFY.load_json(VERIFY.SESSION_SCHEMA)
        cls.session = VERIFY.load_json(VERIFY.SESSION_MANIFEST)
        cls.contract = VERIFY.load_json(VERIFY.IMPORT_CONTRACT)
        cls.briefs = VERIFY.load_json(VERIFY.BRIEFS)
        cls.provenance = VERIFY.load_json(VERIFY.PROVENANCE)
        cls.authentic_schema = VERIFY.load_json(VERIFY.AUTHENTIC_SCHEMA)
        cls.authentic = VERIFY.load_json(VERIFY.AUTHENTIC_MANIFEST)
        cls.cpp = VERIFY.CPP_BANK.read_text(encoding="utf-8")

    def validate_all(self, **overrides):
        values = {
            "session_schema": self.session_schema,
            "session_manifest": self.session,
            "import_contract": self.contract,
            "briefs": self.briefs,
            "provenance": self.provenance,
            "authentic_schema": self.authentic_schema,
            "authentic_manifest": self.authentic,
            "cpp_source": self.cpp,
        }
        values.update(overrides)
        return VERIFY.validate_all(**values)

    def test_current_contract_is_valid_but_not_production_ready(self):
        errors, summary = self.validate_all()
        self.assertEqual([], errors)
        self.assertFalse(summary["production_ready"])
        self.assertEqual(0, summary["approved_for_governed_import_count"])
        self.assertEqual(0, summary["legacy_imported_runtime_reference_count"])

    def test_session_cannot_claim_clearance_without_rights(self):
        session = copy.deepcopy(self.session)
        session["session_state"] = "CLEARED_TO_RECORD"
        errors, _ = self.validate_all(session_manifest=session)
        self.assertTrue(any("without all rights" in error for error in errors))

    def test_captured_shot_requires_planned_take_count(self):
        session = copy.deepcopy(self.session)
        session["shots"][0]["capture_state"] = "CAPTURED_QUARANTINED"
        errors, _ = self.validate_all(session_manifest=session)
        self.assertTrue(any("take count is below plan" in error for error in errors))

    def test_open_canopy_shot_requires_semantic_proof_fields(self):
        session = copy.deepcopy(self.session)
        shot = next(
            item for item in session["shots"] if item["canopy_state"] == "RearOpen"
        )
        shot["required_metadata"].remove("canopy_open_fraction")
        errors, _ = self.validate_all(session_manifest=session)
        self.assertTrue(any("open-canopy proof fields" in error for error in errors))

    def test_missing_bank_binding_fails_cross_contract_coverage(self):
        authentic = copy.deepcopy(self.authentic)
        drone = next(
            item for item in authentic["entries"]
            if item["category_id"] == "DronePropulsion"
        )
        drone["bank_bindings"].remove("DroneFlyby")
        errors, _ = self.validate_all(authentic_manifest=authentic)
        self.assertTrue(any("bindings are not exact" in error for error in errors))
        self.assertTrue(any("do not cover all 25" in error for error in errors))

    def test_duplicate_unreal_destination_fails(self):
        briefs = copy.deepcopy(self.briefs)
        briefs["categories"][1]["unreal_destination"] = briefs["categories"][0][
            "unreal_destination"
        ]
        errors, _ = self.validate_all(briefs=briefs)
        self.assertTrue(any("duplicate Unreal destinations" in error for error in errors))

    def test_old_soundwave_prefix_fails(self):
        briefs = copy.deepcopy(self.briefs)
        briefs["categories"][0]["unreal_destination"] = (
            "/Game/Skyguard/Audio/Production/Aircraft/Engine/S_EngineIdle"
        )
        errors, _ = self.validate_all(briefs=briefs)
        self.assertTrue(any("lacks SW_ naming" in error for error in errors))

    def test_cpp_category_drift_fails(self):
        cpp = self.cpp.replace("\tDroneFlyby,\n", "", 1)
        errors, _ = self.validate_all(cpp_source=cpp)
        self.assertTrue(any("C++ production bank enum" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
