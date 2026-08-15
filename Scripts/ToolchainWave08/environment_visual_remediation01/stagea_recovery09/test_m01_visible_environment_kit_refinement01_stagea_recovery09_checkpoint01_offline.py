from __future__ import annotations

import ast
import importlib.util
import unittest
from pathlib import Path


WORKER = Path(__file__).with_name("build_m01_visible_environment_kit_refinement01_stagea_recovery09_checkpoint01.py")


def load_worker():
    spec = importlib.util.spec_from_file_location("skyguard_r09_test", WORKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Recovery09 worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Recovery09Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_worker()
        cls.source, cls.receipt = cls.module.load_recovery09_source()
        ast.parse(cls.source)

    def test_graph(self) -> None:
        self.assertTrue(self.receipt["generated_call_graph"]["passed"])
        self.assertEqual([], self.receipt["generated_call_graph"]["unresolved_named_calls"])

    def test_targeted_review_lighting(self) -> None:
        self.assertIn('"night_review_lighting_aimed"', self.source)
        self.assertIn("fill_energy=2500.0", self.source)
        self.assertIn("to_track_quat(\"-Z\", \"Y\")", self.source)

    def test_bounded_calibration(self) -> None:
        self.assertIn("for calibration_index in range(2):", self.source)
        self.assertIn("new_exposure = min(7.0", self.source)

    def test_output_contract(self) -> None:
        self.assertEqual(9, self.receipt["checkpoint_count"])
        self.assertEqual(0, self.receipt["glb_count"])
        self.assertFalse(self.receipt["finalization_authorized"])

    def test_r08_not_reused(self) -> None:
        self.assertFalse(self.receipt["recovery08_attempt_or_output_reused"])
        self.assertEqual(self.module.R08_WORKER_SHA256, self.module.sha256_file(self.module.R08_WORKER))


if __name__ == "__main__":
    unittest.main()
