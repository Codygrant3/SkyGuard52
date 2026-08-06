from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "analyze_skyguard_phase8_soak_performance.py"
)
SPEC = importlib.util.spec_from_file_location("phase8_soak_performance", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class Phase8SoakPerformanceTests(unittest.TestCase):
    def test_thresholds_accept_budget_values(self) -> None:
        checks = MODULE.thresholds(
            {
                "frame_time_ms_mean": 16.7,
                "frame_time_ms_p95": 22.2,
                "frame_time_ms_max": 100.0,
                "hitch_over_100ms_count": 0,
            }
        )
        self.assertTrue(all(checks.values()))

    def test_thresholds_reject_over_budget_hitch(self) -> None:
        checks = MODULE.thresholds(
            {
                "frame_time_ms_mean": 10.0,
                "frame_time_ms_p95": 15.0,
                "frame_time_ms_max": 100.1,
                "hitch_over_100ms_count": 1,
            }
        )
        self.assertFalse(checks["max_hitch_at_or_below_100_ms"])
        self.assertFalse(checks["zero_hitches_over_100_ms"])

    def test_exact_mission_ids(self) -> None:
        self.assertEqual(10, len(MODULE.MISSION_IDS))
        self.assertEqual("M01", MODULE.MISSION_IDS[0])
        self.assertEqual("M10", MODULE.MISSION_IDS[-1])


if __name__ == "__main__":
    unittest.main()
