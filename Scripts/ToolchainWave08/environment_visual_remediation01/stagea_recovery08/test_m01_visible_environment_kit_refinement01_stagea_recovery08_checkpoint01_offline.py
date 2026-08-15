from __future__ import annotations

import ast
import importlib.util
import unittest
from pathlib import Path


WORKER = Path(__file__).with_name(
    "build_m01_visible_environment_kit_refinement01_stagea_recovery08_checkpoint01.py"
)


def load_worker():
    spec = importlib.util.spec_from_file_location("skyguard_r08_worker_test", WORKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Recovery08 worker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Recovery08WorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_worker()
        cls.source, cls.receipt = cls.module.load_recovery08_source()
        cls.tree = ast.parse(cls.source)

    def test_generated_source_parses_and_has_no_unresolved_calls(self) -> None:
        self.assertTrue(self.receipt["generated_call_graph"]["passed"])
        self.assertEqual([], self.receipt["generated_call_graph"]["unresolved_named_calls"])

    def test_calibration_is_bounded(self) -> None:
        self.assertIn("for calibration_index in range(2):", self.source)
        self.assertIn("new_exposure = min(7.0", self.source)
        self.assertEqual(2, self.receipt["night_calibration_max_passes_per_camera"])

    def test_calibration_preserves_nine_final_checkpoint_files(self) -> None:
        self.assertIn('require(len(results) == 9, "Checkpoint render count is not exactly nine")', self.source)
        self.assertEqual(9, self.receipt["checkpoint_count"])
        self.assertEqual(0, self.receipt["glb_count"])
        self.assertEqual(0, self.receipt["texture_count"])

    def test_recovery07_geometry_and_output_are_not_reused(self) -> None:
        self.assertFalse(self.receipt["recovery07_attempt_or_output_reused"])
        self.assertEqual(12591, self.module.RECOVERY07_WORKER.stat().st_size)
        self.assertEqual(self.module.RECOVERY07_WORKER_SHA256, self.module.sha256_file(self.module.RECOVERY07_WORKER))

    def test_finalization_remains_forbidden(self) -> None:
        self.assertIn('"finalization_authorized":False', self.source)
        self.assertFalse(self.receipt["finalization_authorized"])


if __name__ == "__main__":
    unittest.main()
