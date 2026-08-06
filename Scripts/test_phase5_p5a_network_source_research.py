"""Mutation tests for the P5-A dated network-source research."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
SCRIPT = ROOT / "Scripts/verify_phase5_p5a_network_source_research.py"
SPEC = importlib.util.spec_from_file_location("p5a_network_research", SCRIPT)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class P5ANetworkSourceResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(VERIFIER.RESEARCH_PATH.read_text(encoding="utf-8"))

    def test_current_research_is_valid_but_blocked(self):
        self.assertEqual([], VERIFIER.validate(self.data))
        self.assertFalse(self.data["overall_status"]["production_ready"])
        self.assertEqual(0, self.data["overall_status"]["licensed_source_count"])

    def test_download_claim_is_rejected(self):
        mutated = copy.deepcopy(self.data)
        mutated["network_method"]["audio_files_downloaded"] = 1
        self.assertTrue(
            any("must remain zero" in error for error in VERIFIER.validate(mutated))
        )

    def test_candidate_cannot_claim_audition(self):
        mutated = copy.deepcopy(self.data)
        mutated["production_candidates"][0]["technical_state"] = "AUDITIONED"
        self.assertTrue(
            any("technical state" in error for error in VERIFIER.validate(mutated))
        )

    def test_candidate_cannot_change_missing_source(self):
        mutated = copy.deepcopy(self.data)
        mutated["production_candidates"][0]["source_status_must_remain"] = (
            "LICENSED_THIRD_PARTY"
        )
        self.assertTrue(
            any("production source status" in error for error in VERIFIER.validate(mutated))
        )

    def test_open_cockpit_wind_must_remain_blocked(self):
        mutated = copy.deepcopy(self.data)
        for item in mutated["category_disposition"]:
            if item["category"] == "OpenCockpitWind":
                item["conditional_production_candidate_count"] = 1
        self.assertTrue(
            any("falsely covered" in error for error in VERIFIER.validate(mutated))
        )

    def test_dcs_extraction_must_remain_blocked(self):
        mutated = copy.deepcopy(self.data)
        for item in mutated["blocked_or_ambiguous_sources"]:
            if item["source_id"] == "DCS_YAK52_INSTALLED_AUDIO":
                item["classification"] = "PRODUCTION_CANDIDATE"
        self.assertTrue(
            any("DCS installed audio" in error for error in VERIFIER.validate(mutated))
        )

    def test_research_cannot_authorize_purchase(self):
        mutated = copy.deepcopy(self.data)
        mutated["next_authorized_acquisition_action"][
            "purchase_or_download_authorized_by_this_research"
        ] = True
        self.assertTrue(
            any("improperly authorizes" in error for error in VERIFIER.validate(mutated))
        )


if __name__ == "__main__":
    unittest.main()
