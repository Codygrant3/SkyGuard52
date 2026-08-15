from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFY_PATH = ROOT / "Scripts" / "verify_campaign_m02_m10_final_art_production_offline.py"
SPEC = importlib.util.spec_from_file_location("campaign_verify", VERIFY_PATH)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class CampaignFinalArtOfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        docs = ROOT / "Docs" / "AAA_Review"
        cls.contract = json.loads((docs / "CAMPAIGN_M02_M10_FINAL_ART_PRODUCTION_CONTRACT.json").read_text(encoding="utf-8"))
        cls.matrix = json.loads((docs / "CAMPAIGN_M02_M10_MISSION_BOSS_PRODUCTION_MATRIX.json").read_text(encoding="utf-8"))
        cls.rubric = json.loads((docs / "CAMPAIGN_M02_M10_VISUAL_PERFORMANCE_ACCEPTANCE_RUBRIC.json").read_text(encoding="utf-8"))

    def test_real_package_passes(self) -> None:
        self.assertEqual([], VERIFY.validate_package())

    def test_exact_nine_missions(self) -> None:
        self.assertEqual(list(range(2, 11)), [item["order"] for item in self.matrix["missions"]])

    def test_unique_route_boss_and_identity(self) -> None:
        missions = self.matrix["missions"]
        self.assertEqual(9, len({item["boss"] for item in missions}))
        self.assertEqual(9, len({json.dumps(item["route_signature_cm"]) for item in missions}))
        self.assertEqual(9, len({item["environment_identity"] for item in missions}))

    def test_hero_asset_bounds_and_weakpoints(self) -> None:
        for mission in self.matrix["missions"]:
            self.assertGreaterEqual(len(mission["exclusive_hero_assets"]), 3)
            self.assertLessEqual(len(mission["exclusive_hero_assets"]), 10)
            self.assertEqual(4, len(mission["canonical_weakpoints"]))

    def test_no_production_acceptance_overclaim(self) -> None:
        self.assertEqual("0_OF_10", self.contract["baseline_truth"]["production_mission_acceptance"])
        self.assertTrue(all(item["production_acceptance"] == "UNVERIFIED" for item in self.matrix["missions"]))

    def test_no_heavy_execution_authority(self) -> None:
        self.assertFalse(self.contract["heavy_execution_authorized"])

    def test_rejects_duplicate_boss(self) -> None:
        mutated = copy.deepcopy(self.matrix)
        mutated["missions"][1]["boss"] = mutated["missions"][0]["boss"]
        errors = VERIFY.validate_contract(self.contract, mutated, self.rubric)
        self.assertIn("bosses are not unique", errors)

    def test_rejects_hero_asset_underflow(self) -> None:
        mutated = copy.deepcopy(self.matrix)
        mutated["missions"][0]["exclusive_hero_assets"] = ["only", "two"]
        errors = VERIFY.validate_contract(self.contract, mutated, self.rubric)
        self.assertTrue(any("outside 3-10" in error for error in errors))

    def test_performance_thresholds_preserved(self) -> None:
        thresholds = self.rubric["thresholds"]
        self.assertEqual(16.7, thresholds["mean_frame_ms_max"])
        self.assertEqual(0, thresholds["frames_over_50ms_max"])
        self.assertEqual(900, self.rubric["measurement"]["minimum_frame_samples"])


if __name__ == "__main__":
    unittest.main()
