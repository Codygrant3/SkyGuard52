"""Mutation tests for the exact 25-slot authentic-source contract."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCRIPT = ROOT / "Scripts/verify_phase5_authentic_source_acquisition_contract.py"
SPEC = importlib.util.spec_from_file_location(
    "source_acquisition_contract_gate", SCRIPT
)
VERIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VERIFIER)


class AuthenticSourceAcquisitionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            VERIFIER.CONTRACT_PATH.read_text(encoding="utf-8")
        )

    def validate(self, contract: dict) -> dict:
        return VERIFIER.validate_contract(contract)

    def errors(self, contract: dict) -> list[str]:
        return self.validate(contract)["errors"]

    def test_current_contract_passes_but_never_claims_ready(self) -> None:
        report = self.validate(copy.deepcopy(self.contract))
        self.assertEqual([], report["errors"])
        self.assertTrue(report["contract_valid"])
        self.assertEqual(
            "PASS_IMMUTABLE_SOURCE_CONTRACT_AUTHENTIC_SOURCES_MISSING",
            report["status"],
        )
        self.assertEqual(25, report["observed_source_slot_count"])
        self.assertEqual(25, report["observed_null_wave_asset_slot_count"])
        self.assertEqual(20, report["slots_with_candidate_reference_count"])
        self.assertEqual(5, report["slots_without_candidate_reference_count"])
        self.assertEqual(14, report["research_candidate_count"])
        self.assertEqual(0, report["downloaded_source_count"])
        self.assertEqual(0, report["hashed_source_count"])
        self.assertFalse(report["authentic_source_acquisition_ready"])
        self.assertFalse(report["production_ready"])
        self.assertFalse(report["shipping_allowed"])
        self.assertFalse(report["packaged_audible_acceptance"])

    def test_missing_slot_fails_exact_topology_coverage(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["slots"].pop()
        errors = self.errors(contract)
        self.assertTrue(any("expected_25_slots" in error for error in errors))
        self.assertTrue(any("missing_topology_slots" in error for error in errors))

    def test_duplicate_slot_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["slots"][-1] = copy.deepcopy(contract["slots"][0])
        errors = self.errors(contract)
        self.assertTrue(any("duplicate_category" in error for error in errors))

    def test_topology_authority_hash_drift_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["accepted_topology_boundary"]["topology_contract_sha256"] = (
            "0" * 64
        )
        errors = self.errors(contract)
        self.assertTrue(any("hash_mismatch" in error for error in errors))

    def test_accepted_attempt_cannot_be_substituted(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["accepted_topology_boundary"]["attempt_id"] = "other_attempt"
        errors = self.errors(contract)
        self.assertTrue(
            any("accepted_attempt_id_mismatch" in error for error in errors)
        )

    def test_slot_graph_and_wave_input_must_match_topology(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["slots"][0]["graph"] = "MS_RifleShot"
        contract["slots"][0]["wave_input"] = "Source_NotReal"
        errors = self.errors(contract)
        self.assertTrue(any("graph_mismatch" in error for error in errors))
        self.assertTrue(any("wave_input_mismatch" in error for error in errors))
        self.assertTrue(
            any("not_null_in_accepted_fresh_audit" in error for error in errors)
        )

    def test_source_route_must_match_category_brief(self) -> None:
        contract = copy.deepcopy(self.contract)
        engine = next(
            slot for slot in contract["slots"] if slot["category"] == "EngineIdle"
        )
        engine["allowed_route"] = "LICENSED_LIBRARY"
        errors = self.errors(contract)
        self.assertTrue(
            any("route_does_not_match_brief" in error for error in errors)
        )
        self.assertTrue(any("not_allowlisted_for_route" in error for error in errors))

    def test_candidate_reference_must_exist_in_hashed_ledger(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["slots"][0]["candidate_ids"] = ["INVENTED_CANDIDATE"]
        errors = self.errors(contract)
        self.assertTrue(any("unknown_candidate" in error for error in errors))

    def test_research_candidate_cannot_be_promoted_in_contract(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["slots"][0]["current_state"] = "APPROVED_FOR_GOVERNED_IMPORT"
        errors = self.errors(contract)
        self.assertTrue(
            any("current_state_must_be_missing" in error for error in errors)
        )

    def test_current_truth_cannot_claim_download_or_shipping(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["current_truth"]["downloaded_source_count"] = 1
        contract["current_truth"]["production_ready"] = True
        contract["current_truth"]["shipping_allowed"] = True
        contract["current_truth"]["packaged_audible_acceptance"] = True
        errors = self.errors(contract)
        self.assertTrue(
            any(
                error == "current_truth:downloaded_source_count_mismatch"
                for error in errors
            )
        )
        self.assertTrue(
            any(
                error == "current_truth:production_ready_mismatch"
                for error in errors
            )
        )
        self.assertTrue(
            any(error == "current_truth:shipping_allowed_mismatch" for error in errors)
        )
        self.assertTrue(
            any(
                error == "current_truth:packaged_audible_acceptance_mismatch"
                for error in errors
            )
        )

    def test_research_inventory_must_cover_exact_ledger_candidate_set(self) -> None:
        contract = copy.deepcopy(self.contract)
        first_group = next(
            iter(contract["research_candidate_inventory"]["dispositions"].values())
        )
        first_group.pop()
        errors = self.errors(contract)
        self.assertTrue(
            any(
                "dispositions_do_not_cover_exact_candidate_set" in error
                for error in errors
            )
        )

    def test_required_evidence_and_state_promotion_rules_are_fail_closed(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["universal_promotion_requirements"] = []
        contract["state_model"]["promotion_rules"].pop("ACQUIRED_QUARANTINED")
        errors = self.errors(contract)
        self.assertTrue(
            any("universal_promotion_requirements_incomplete" in e for e in errors)
        )
        self.assertTrue(any("promotion_rule_set_mismatch" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
