"""Mutation tests for the Yak-52 R4 Slice 01 offline readiness gate."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts"))

import verify_phase2_yak52_r4_slice01_readiness as gate  # noqa: E402


def load_json(relative: Path) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


class Slice01ReadinessMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_json(gate.CONTRACT_REL)
        self.ledger = load_json(gate.LEDGER_REL)
        self.cameras = load_json(gate.CAMERA_REL)
        self.r4 = load_json(gate.R4_REL)

    def validate(
        self,
        contract: dict | None = None,
        ledger: dict | None = None,
        cameras: dict | None = None,
        r4: dict | None = None,
    ) -> list[str]:
        return gate.validate_contract_data(
            contract if contract is not None else self.contract,
            ledger if ledger is not None else self.ledger,
            cameras if cameras is not None else self.cameras,
            r4 if r4 is not None else self.r4,
        )

    def assert_error_contains(self, errors: list[str], text: str) -> None:
        self.assertTrue(
            any(text in error for error in errors),
            msg=f"Expected error containing {text!r}; got {errors}",
        )

    def test_01_canonical_data_passes(self) -> None:
        self.assertEqual([], self.validate())

    def test_02_readiness_status_cannot_claim_execution(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["current_status"] = "OUTPUTS_CREATED"
        self.assert_error_contains(
            self.validate(contract=mutated),
            "readiness status must remain",
        )

    def test_03_completion_claims_remain_false(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["claims"]["silhouette_locked"] = True
        self.assert_error_contains(
            self.validate(contract=mutated),
            "claim must remain false: silhouette_locked",
        )

    def test_04_reference_package_cannot_be_falsified(self) -> None:
        mutated = copy.deepcopy(self.ledger)
        mutated["reference_package_status"][
            "orthographic_or_dimensioned_drawing"
        ] = "PRESENT"
        mutated["reference_package_status"]["silhouette_lock_allowed"] = True
        errors = self.validate(ledger=mutated)
        self.assert_error_contains(errors, "must remain MISSING")
        self.assert_error_contains(errors, "silhouette lock cannot be allowed")

    def test_05_dimension_target_drift_fails(self) -> None:
        mutated = copy.deepcopy(self.ledger)
        mutated["governed_dimensions_m"][0]["target"] = 7.9
        self.assert_error_contains(
            self.validate(ledger=mutated),
            "dimension target mismatch: overall_length",
        )

    def test_06_dimension_tolerance_relaxation_fails(self) -> None:
        mutated = copy.deepcopy(self.ledger)
        mutated["governed_dimensions_m"][1]["tolerance"] = 0.8
        self.assert_error_contains(
            self.validate(ledger=mutated),
            "dimension tolerance mismatch: wingspan",
        )

    def test_07_station_order_drift_fails(self) -> None:
        mutated = copy.deepcopy(self.ledger)
        mutated["normalized_station_plan"][4]["x_fraction_of_half_length"] = -0.9
        self.assert_error_contains(
            self.validate(ledger=mutated),
            "station fractions are not strictly increasing",
        )

    def test_08_camera_removal_fails(self) -> None:
        mutated = copy.deepcopy(self.cameras)
        mutated["cameras"].pop()
        self.assert_error_contains(
            self.validate(cameras=mutated),
            "camera entry order/ids mismatch",
        )

    def test_09_camera_transform_drift_fails(self) -> None:
        mutated = copy.deepcopy(self.cameras)
        mutated["cameras"][0]["location_m"][0] = 12.0
        self.assert_error_contains(
            self.validate(cameras=mutated),
            "camera authority mismatch: R4_CAM_BEAUTY_PORT location_m",
        )

    def test_10_namespace_drift_fails(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["namespace_contract"]["primary_objects"].pop()
        self.assert_error_contains(
            self.validate(contract=mutated),
            "primary object namespace mismatch",
        )

    def test_11_triangle_budget_relaxation_fails(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["topology_contract"][
            "primary_mesh_total_triangle_budget"
        ] = 500000
        self.assert_error_contains(
            self.validate(contract=mutated),
            "topology contract mismatch: primary_mesh_total_triangle_budget",
        )

    def test_12_donor_import_policy_relaxation_fails(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["source_policy"]["r3_donor_geometry_allowed"] = True
        self.assert_error_contains(
            self.validate(contract=mutated),
            "source policy must forbid r3_donor_geometry_allowed",
        )

    def test_13_authoring_script_hash_drift_fails(self) -> None:
        mutated = copy.deepcopy(self.contract)
        mutated["authoring_script"]["sha256"] = "0" * 64
        self.assert_error_contains(
            gate.validate_authoring_script(ROOT, mutated),
            "authoring script hash drift",
        )

    def test_14_existing_canonical_output_fails(self) -> None:
        mutated = copy.deepcopy(self.contract)
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            relative = Path("canonical") / "slice01.blend"
            (temp_root / relative).parent.mkdir(parents=True)
            (temp_root / relative).write_bytes(b"must fail")
            mutated["output_policy"]["paths"] = {
                "blend": relative.as_posix(),
                "glb": "canonical/slice01.glb",
                "manifest": "reports/manifest.json",
                "screenshot_directory": "renders/slice01",
            }
            self.assert_error_contains(
                gate.validate_output_absence(temp_root, mutated),
                "canonical output must be absent before run",
            )


if __name__ == "__main__":
    unittest.main()
