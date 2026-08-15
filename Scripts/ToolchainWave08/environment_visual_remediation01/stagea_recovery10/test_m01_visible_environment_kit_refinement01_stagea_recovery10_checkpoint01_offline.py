from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name(
    "build_m01_visible_environment_kit_refinement01_stagea_recovery10_checkpoint01.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("skyguard_r10_worker_test", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Recovery10 worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Recovery10WorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.source, cls.receipt = cls.module.load_recovery10_source()

    def test_generated_graph(self) -> None:
        self.assertTrue(self.receipt["generated_call_graph"]["passed"])
        self.assertEqual([], self.receipt["generated_call_graph"]["unresolved_named_calls"])

    def test_both_targeted_lighting_paths(self) -> None:
        self.assertIn('"night_review_lighting_aimed"', self.source)
        self.assertIn('"storm_review_lighting_aimed"', self.source)

    def test_storm_candidate_b(self) -> None:
        self.assertIn("fill_energy=2800.0", self.source)
        self.assertEqual("B", self.receipt["selected_storm_probe_candidate"])

    def test_checkpoint_only(self) -> None:
        self.assertEqual(9, self.receipt["checkpoint_count"])
        self.assertEqual(0, self.receipt["glb_count"])
        self.assertFalse(self.receipt["finalization_authorized"])

    def test_recovery09_output_not_reused(self) -> None:
        self.assertFalse(self.receipt["recovery09_attempt_or_output_reused"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
