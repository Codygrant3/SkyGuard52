import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class InsightsReviewContractTests(unittest.TestCase):
    def test_supervisor_is_headless_bounded_and_uses_engine_export_commands(self) -> None:
        text = (
            ROOT / "Scripts" / "run_skyguard_phase1_insights_review_gate.ps1"
        ).read_text(encoding="utf-8")
        for token in (
            "-Unattended",
            "-AutoQuit",
            "-NoUI",
            "-NullRHI",
            "WaitForExit($TimeoutSeconds * 1000)",
            "TimingInsights.ExportThreads",
            "TimingInsights.ExportTimers",
            "TimingInsights.ExportTimerStatistics",
            "TimingInsights.ExportTimingEvents",
        ):
            self.assertIn(token, text)

    def test_report_schema_forbids_p1_4_promotion(self) -> None:
        text = (
            ROOT
            / "Scripts"
            / "skyguard_phase1_insights_review_report_v1.schema.json"
        ).read_text(encoding="utf-8")
        self.assertIn(
            '"p1_4_disposition": {"const": "INSUFFICIENT_EVIDENCE"}', text
        )


if __name__ == "__main__":
    unittest.main()
