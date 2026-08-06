"""Mutation tests for the source-only BLD-M01-COAST-PROD-001 gate."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_bld_m01_coast_prod_001 as verifier


class CoastProductionSourceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = verifier.load_json(verifier.CONTRACT_PATH)
        cls.generator_text = verifier.GENERATOR_PATH.read_text(encoding="utf-8")

    def status(self, contract: dict | None = None, generator: str | None = None) -> str:
        checks = verifier.source_checks(
            contract if contract is not None else copy.deepcopy(self.contract),
            generator if generator is not None else self.generator_text,
        )
        return "PASS" if all(item["passed"] for item in checks) else "FAIL"

    def test_current_source_passes_without_artifacts(self) -> None:
        result = verifier.evaluate()
        self.assertEqual(result["source_status"], "PASS")
        self.assertIn(result["artifact_status"], {"NOT_RUN", "PASS"})

    def test_rejection_evidence_hash_drift_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["rejection_evidence"]["sha256"] = "0" * 64
        self.assertEqual(self.status(contract), "FAIL")

    def test_forbidden_asset_name_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["asset_specs"][0]["name"] = "GEO_COAST001_PROXY"
        self.assertEqual(self.status(contract), "FAIL")

    def test_missing_uv1_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["uv_contract"]["required_layers"] = ["UV0"]
        self.assertEqual(self.status(contract), "FAIL")

    def test_wrong_terrain_length_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["asset_specs"][0]["dimensions_m"][0] = 99.0
        self.assertEqual(self.status(contract), "FAIL")

    def test_missing_snap_and_collision_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["asset_specs"][0]["snap_sockets"] = []
        contract["asset_specs"][0]["collision"] = ""
        self.assertEqual(self.status(contract), "FAIL")

    def test_external_geometry_import_fails(self) -> None:
        generator = self.generator_text + "\nbpy.ops.import_scene.gltf(filepath='forbidden.glb')\n"
        self.assertEqual(self.status(generator=generator), "FAIL")

    def test_aaa_claim_fails(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["quality_claim"] = "AAA complete"
        self.assertEqual(self.status(contract), "FAIL")

    def test_serialized_contract_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "contract.json"
            path.write_text(json.dumps(self.contract, indent=2), encoding="utf-8")
            self.assertEqual(verifier.load_json(path)["build_id"], verifier.BUILD_ID)


if __name__ == "__main__":
    unittest.main()
