from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
MODULE = ROOT / "Scripts/verify_skyguard_phase4_m01_representative_visual_attempt08.py"
SPEC = importlib.util.spec_from_file_location("attempt08_verify", MODULE)
VERIFY = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(VERIFY)


class Attempt08OfflineDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = VERIFY.verify()

    def test_gate_passes(self):
        self.assertEqual(
            self.result["gate"],
            "PASSED_READY_FOR_EXPLICIT_SINGLE_UNREAL_VISUAL_PROOF_AUTHORIZATION",
        )

    def test_every_check_passes(self):
        self.assertTrue(all(self.result["checks"].values()), self.result["checks"])

    def test_namespace_is_absent(self):
        contract = VERIFY.load(VERIFY.CONTRACT)
        self.assertFalse((ROOT / contract["execution"]["output_root"]).exists())
        self.assertFalse((ROOT / contract["execution"]["attempt_root"]).exists())

    def test_no_heavy_process_is_launched_by_offline_verifier(self):
        source = MODULE.read_text(encoding="utf-8-sig")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("UnrealEditor", source)
        self.assertNotIn("blender", source.lower())

    def test_camera_and_temporal_coverage(self):
        cameras = VERIFY.load(VERIFY.CAMERAS)
        kinds = {item["kind"] for item in cameras["cameras"]}
        self.assertIn("rear_gunner_gameplay", kinds)
        self.assertIn("exterior_review", kinds)
        self.assertEqual(len(cameras["temporal_route_samples"]), 3)

    def test_visual_rejections_are_explicit(self):
        visual = VERIFY.load(VERIFY.VISUAL)
        rejected = " ".join(visual["human_checks"]["reject_if_any"])
        for phrase in ("floating", "grounded terrain", "tiling", "water and shore", "camera clipping"):
            self.assertIn(phrase, rejected)

    def test_performance_is_absolute_and_fail_closed(self):
        performance = VERIFY.load(VERIFY.PERFORMANCE)
        self.assertTrue(performance["policy"]["absolute_budgets_are_required"])
        self.assertTrue(performance["policy"]["missing_metric_is_failure"])


if __name__ == "__main__":
    unittest.main()
