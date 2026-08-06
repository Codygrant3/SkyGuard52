"""Mutation tests for the Phase 2 Yak-52 R4 offline production contract."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCRIPT = ROOT / "Scripts/verify_phase2_yak52_r4_offline_production_contract.py"
SPEC = importlib.util.spec_from_file_location("yak_r4_contract_gate", SCRIPT)
VERIFIER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VERIFIER)


class Yak52R4OfflineProductionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            VERIFIER.CONTRACT_PATH.read_text(encoding="utf-8")
        )

    def validate(self, contract: dict) -> dict:
        return VERIFIER.validate_contract(contract)

    def errors(self, contract: dict) -> list[str]:
        return self.validate(contract)["errors"]

    def test_current_contract_passes_without_completion_claims(self) -> None:
        report = self.validate(copy.deepcopy(self.contract))
        self.assertEqual([], report["errors"])
        self.assertTrue(report["contract_valid"])
        self.assertEqual(
            "PASS_R4_OFFLINE_CONTRACT_PRODUCTION_NOT_STARTED",
            report["status"],
        )
        self.assertEqual(10, report["ordered_asset_slice_count"])
        self.assertEqual(13, report["visual_acceptance_camera_count"])
        self.assertEqual(10, report["quarantined_donor_mesh_count"])
        self.assertEqual(0, report["quarantined_donor_promoted_count"])
        self.assertEqual([], report["planned_r4_paths_present"])
        self.assertFalse(report["blender_launched"])
        self.assertFalse(report["unreal_launched"])
        self.assertFalse(report["accepted_assets_modified"])
        self.assertFalse(report["r4_production_started"])
        self.assertFalse(report["final"])
        self.assertFalse(report["aaa"])
        self.assertFalse(report["production_ready"])
        self.assertFalse(report["shipping_allowed"])

    def test_authority_hash_drift_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["authority_inputs"][0]["sha256"] = "0" * 64
        errors = self.errors(contract)
        self.assertTrue(any("hash_drift" in error for error in errors))

    def test_current_state_cannot_claim_production_or_final(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["current_state"]["r4_blender_source_created"] = True
        contract["current_state"]["donor_promoted"] = True
        contract["current_state"]["final"] = True
        contract["current_state"]["aaa"] = True
        contract["current_state"]["production_ready"] = True
        errors = self.errors(contract)
        for field in (
            "r4_blender_source_created",
            "donor_promoted",
            "final",
            "aaa",
            "production_ready",
        ):
            self.assertTrue(any(field in error for error in errors))

    def test_source_disposition_cannot_promote_rejected_study(self) -> None:
        contract = copy.deepcopy(self.contract)
        source = next(
            item
            for item in contract["current_blender_source_inventory"]
            if item["id"] == "PRODUCTION_002_REJECTED_DONOR_STUDY"
        )
        source["disposition"] = "APPROVED_WHOLE_AIRCRAFT"
        errors = self.errors(contract)
        self.assertTrue(any("disposition_mismatch" in error for error in errors))

    def test_donor_set_must_be_exact_and_not_promotable(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["donor_compatibility_boundary"]["exact_meshes"].pop()
        contract["donor_compatibility_boundary"][
            "automatic_promotion_allowed"
        ] = True
        errors = self.errors(contract)
        self.assertTrue(any("exact_mesh_set_mismatch" in error for error in errors))
        self.assertTrue(
            any("automatic_promotion_allowed_must_be_false" in e for e in errors)
        )

    def test_slices_must_remain_exactly_ordered(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["ordered_asset_slices"][2], contract["ordered_asset_slices"][3] = (
            contract["ordered_asset_slices"][3],
            contract["ordered_asset_slices"][2],
        )
        errors = self.errors(contract)
        self.assertTrue(any("order_or_id_sequence_mismatch" in e for e in errors))
        self.assertTrue(any("numeric_order_mismatch" in e for e in errors))

    def test_slice_cannot_depend_on_future_or_unknown_work(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["ordered_asset_slices"][0]["depends_on"] = ["R4-S10"]
        errors = self.errors(contract)
        self.assertTrue(any("unknown_or_future_dependencies" in e for e in errors))

    def test_final_slice_must_depend_on_all_prior_slices(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["ordered_asset_slices"][-1]["depends_on"].pop()
        errors = self.errors(contract)
        self.assertTrue(
            any("R4-S10_must_depend_on_all_prior_slices" in e for e in errors)
        )

    def test_visual_camera_set_and_freeze_are_fail_closed(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["visual_acceptance_contract"]["required_cameras"].pop()
        contract["visual_acceptance_contract"][
            "camera_mutation_allowed_after_slice_1"
        ] = True
        errors = self.errors(contract)
        self.assertTrue(any("expected_exactly_13_cameras" in e for e in errors))
        self.assertTrue(any("camera_id_set_mismatch" in e for e in errors))
        self.assertTrue(any("camera_mutation_allowed" in e for e in errors))

    def test_material_and_crew_quality_requirements_cannot_be_removed(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["material_and_texture_contract"]["required_bakes"].pop()
        contract["material_and_texture_contract"]["eight_k_allowed"] = True
        contract["crew_and_rig_contract"]["required_skeletal_assets"].pop()
        contract["crew_and_rig_contract"]["maximum_bones_per_asset"] = 512
        errors = self.errors(contract)
        self.assertTrue(any("required_bake_set_mismatch" in e for e in errors))
        self.assertTrue(any("eight_k_must_be_false" in e for e in errors))
        self.assertTrue(
            any("required_skeletal_asset_set_mismatch" in e for e in errors)
        )
        self.assertTrue(any("maximum_bones_mismatch" in e for e in errors))

    def test_pivots_sockets_and_collision_are_exact(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["pivot_socket_and_axis_contract"]["required_sockets"].pop()
        contract["collision_and_safety_contract"][
            "complex_as_simple_allowed"
        ] = True
        contract["collision_and_safety_contract"][
            "maximum_simple_collision_primitives"
        ] = 400
        errors = self.errors(contract)
        self.assertTrue(any("socket_set_mismatch" in e for e in errors))
        self.assertTrue(any("complex_as_simple_allowed" in e for e in errors))
        self.assertTrue(any("primitive_budget_mismatch" in e for e in errors))

    def test_performance_budgets_cannot_be_silently_relaxed(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["performance_budget_contract"]["content_budgets"][
            "maximum_yak_draw_calls_rear_gunner_view"
        ] = 850
        contract["performance_budget_contract"]["runtime_delta_budgets_ms"][
            "gpu"
        ] = 10.0
        errors = self.errors(contract)
        self.assertTrue(any("content_budget_set_mismatch" in e for e in errors))
        self.assertTrue(
            any("runtime_delta_budget_set_mismatch" in e for e in errors)
        )

    def test_offline_contract_cannot_be_called_completion(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["r4_completion_gate"]["automatic_promotion"] = True
        contract["r4_completion_gate"][
            "offline_contract_pass_is_completion"
        ] = True
        contract["r4_completion_gate"][
            "offline_contract_pass_is_aaa_acceptance"
        ] = True
        errors = self.errors(contract)
        self.assertTrue(any("automatic_promotion_must_be_false" in e for e in errors))
        self.assertTrue(
            any("offline_contract_pass_is_completion_must_be_false" in e for e in errors)
        )
        self.assertTrue(
            any(
                "offline_contract_pass_is_aaa_acceptance_must_be_false" in e
                for e in errors
            )
        )


if __name__ == "__main__":
    unittest.main()
