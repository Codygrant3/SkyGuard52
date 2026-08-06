"""Mutation tests for the Yak-52 R4 Slice 01 Recovery01 gate."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts"))

import verify_phase2_yak52_r4_slice01_recovery01_readiness as gate  # noqa: E402


class Recovery01MutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(
            (ROOT / gate.CONTRACT_REL).read_text(encoding="utf-8-sig")
        )

    def errors(self, contract: dict | None = None) -> list[str]:
        return gate.validate_contract_data(
            contract if contract is not None else self.contract
        )

    def assert_has(self, errors: list[str], text: str) -> None:
        self.assertTrue(
            any(text in error for error in errors),
            msg=f"Expected {text!r} in {errors}",
        )

    def test_01_canonical_contract_passes(self) -> None:
        self.assertEqual([], self.errors())

    def test_02_frozen_source_access_extraction_is_exact(self) -> None:
        source = (ROOT / gate.FROZEN_SCRIPT_REL).read_text(encoding="utf-8")
        self.assertEqual(
            gate.EXPECTED_ACCESS_PATHS,
            gate.extract_frozen_contract_paths(source),
        )

    def test_03_every_declared_key_path_exists(self) -> None:
        for key_path in gate.EXPECTED_ACCESS_PATHS:
            self.assertTrue(
                gate.contract_path_exists(self.contract, key_path),
                msg=key_path,
            )

    def test_04_missing_outputs_root_fails(self) -> None:
        mutated = copy.deepcopy(self.contract)
        del mutated["outputs"]
        errors = self.errors(mutated)
        self.assert_has(errors, "Recovery01 contract key path missing: outputs")
        self.assert_has(errors, "output alias and output policy disagree")

    def test_05_missing_nested_output_key_fails(self) -> None:
        mutated = copy.deepcopy(self.contract)
        del mutated["outputs"]["comparison_directory"]
        self.assert_has(
            self.errors(mutated),
            "contract key path missing: outputs.comparison_directory",
        )

    def test_06_missing_authority_item_hash_fails(self) -> None:
        mutated = copy.deepcopy(self.contract)
        del mutated["authority_inputs"][0]["sha256"]
        self.assert_has(
            self.errors(mutated),
            "contract key path missing: authority_inputs[].sha256",
        )

    def test_07_missing_authoring_hash_fails(self) -> None:
        mutated = copy.deepcopy(self.contract)
        del mutated["authoring_script"]["sha256"]
        self.assert_has(
            self.errors(mutated),
            "contract key path missing: authoring_script.sha256",
        )

    def test_08_output_alias_drift_fails(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["outputs"]["blend"] = "wrong.blend"
        self.assert_has(
            self.errors(mutated),
            "output alias and output policy disagree",
        )

    def test_09_premature_silhouette_claim_fails(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["claims"]["silhouette_locked"] = True
        self.assert_has(
            self.errors(mutated),
            "claim must remain false: silhouette_locked",
        )

    def test_10_launch_authorization_cannot_be_preclaimed(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["launch_contract"]["launch_authorized"] = True
        self.assert_has(
            self.errors(mutated),
            "launch must remain unauthorized",
        )

    def test_11_source_policy_cannot_allow_donor_geometry(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["source_policy"]["r3_donor_geometry_allowed"] = True
        self.assert_has(
            self.errors(mutated),
            "source policy must forbid r3_donor_geometry_allowed",
        )

    def test_12_authoring_hash_mutation_fails_source_gate(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["authoring_script"]["sha256"] = "0" * 64
        self.assert_has(
            gate.validate_sources(ROOT, mutated),
            "authoring script hash drift",
        )

    def test_13_wrapper_hash_mutation_fails_source_gate(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["launch_contract"]["wrapper_sha256"] = "0" * 64
        self.assert_has(
            gate.validate_sources(ROOT, mutated),
            "launch wrapper hash drift",
        )

    def test_14_failure_logs_prove_exact_keyerror(self) -> None:
        self.assertEqual([], gate.validate_failure_evidence(ROOT))


if __name__ == "__main__":
    unittest.main()
