"""Focused offline tests for the Recovery07 mapped visual-proof gate."""

from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "recovery07_adjudicator",
    HERE / "adjudicate_recovery07_mapped_visual_proof01_once.py",
)
assert SPEC is not None and SPEC.loader is not None
ADJUDICATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADJUDICATOR)


class Recovery07MappedVisualProofTests(unittest.TestCase):
    def test_percentile_interpolates(self) -> None:
        self.assertEqual(ADJUDICATOR.percentile([0.0, 10.0], 0.5), 5.0)

    def test_parse_number_rejects_invalid_values(self) -> None:
        self.assertIsNone(ADJUDICATOR.parse_number("not-a-number"))
        self.assertIsNone(ADJUDICATOR.parse_number("nan"))
        self.assertEqual(ADJUDICATOR.parse_number("12.5"), 12.5)

    def test_profile_parser_accepts_complete_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "profile.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["FrameTime", "GPUTime", "GPUMem/LocalUsedMB"])
                for _ in range(900):
                    writer.writerow(["10.0", "8.0", "2048.0"])
            result = ADJUDICATOR.parse_profile(path)
            self.assertEqual(result["sample_count"], 900)
            self.assertEqual(result["mean_frame_ms"], 10.0)
            self.assertEqual(result["peak_gpu_memory_mib"], 2048.0)

    def test_profile_parser_rejects_missing_gpu_memory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "profile.csv"
            path.write_text("FrameTime,GPUTime\n10,8\n", encoding="utf-8")
            with self.assertRaises(AssertionError):
                ADJUDICATOR.parse_profile(path)

    def test_executor_uses_deferred_tick_without_save_api(self) -> None:
        source = (HERE / "capture_recovery07_mapped_visual_proof01.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("register_slate_post_tick_callback", source)
        self.assertIn("audit_landscape_material_compilation", source)
        self.assertNotIn("save_current_level", source)
        self.assertNotIn("save_loaded_asset", source)


if __name__ == "__main__":
    unittest.main()
