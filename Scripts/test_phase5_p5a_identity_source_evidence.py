"""Mutation tests for the offline P5-A identity-source evidence gate."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCRIPT = ROOT / "Scripts/verify_phase5_p5a_identity_source_evidence.py"
SPEC = importlib.util.spec_from_file_location("p5a_identity_evidence", SCRIPT)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class P5AIdentitySourceEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(VERIFIER.CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.acquisition = json.loads(
            VERIFIER.ACQUISITION_PATH.read_text(encoding="utf-8")
        )
        cls.provenance = json.loads(
            VERIFIER.PROVENANCE_PATH.read_text(encoding="utf-8")
        )

    def validate(self, contract=None, acquisition=None, provenance=None):
        return VERIFIER.validate(
            contract or self.contract,
            acquisition or self.acquisition,
            provenance or self.provenance,
        )

    def test_current_blocked_contract_is_valid(self):
        errors, approved = self.validate()
        self.assertEqual([], errors)
        self.assertEqual(0, approved)

    def test_generic_aircraft_cannot_be_semantic_match(self):
        mutated = copy.deepcopy(self.contract)
        mutated["reviewed_research_candidates"][0]["semantic_match"] = True
        errors, _ = self.validate(contract=mutated)
        self.assertTrue(any("semantic match" in error for error in errors))

    def test_license_alone_cannot_be_sufficient(self):
        mutated = copy.deepcopy(self.contract)
        mutated["source_candidate_policy"]["license_only_is_sufficient"] = True
        errors, _ = self.validate(contract=mutated)
        self.assertTrue(any("unsafe candidate policy" in error for error in errors))

    def test_approved_candidate_requires_all_evidence(self):
        mutated = copy.deepcopy(self.contract)
        mutated["approved_production_candidates"] = [
            {
                "candidate_id": "UNPROVEN",
                "independent_approvals": ["RIGHTS_APPROVED"],
            }
        ]
        mutated["current_state"]["approved_production_candidate_count"] = 1
        errors, _ = self.validate(contract=mutated)
        self.assertTrue(any("lacks evidence" in error for error in errors))
        self.assertTrue(any("exact independent approvals" in error for error in errors))

    def test_missing_source_cannot_contain_hash(self):
        mutated = copy.deepcopy(self.provenance)
        for entry in mutated["entries"]:
            if entry["category"] == "EngineIdle":
                entry["source_sha256"] = "a" * 64
                break
        errors, _ = self.validate(provenance=mutated)
        self.assertTrue(any("contains source proof" in error for error in errors))

    def test_download_count_must_remain_zero(self):
        mutated = copy.deepcopy(self.acquisition)
        mutated["downloaded_asset_count"] = 1
        errors, _ = self.validate(acquisition=mutated)
        self.assertTrue(any("reports downloads" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
