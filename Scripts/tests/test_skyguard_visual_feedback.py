from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
MODULE_PATH = TEST_DIR.parent / "skyguard_visual_feedback.py"
SPEC = importlib.util.spec_from_file_location("skyguard_visual_feedback", MODULE_PATH)
assert SPEC and SPEC.loader
FEEDBACK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FEEDBACK)


class VisualFeedbackTests(unittest.TestCase):
    def make_review(self, root: Path, name: str, categories: list[str]) -> Path:
        path = root / name
        path.write_text(
            json.dumps(
                {
                    "schema": "test.review.v1",
                    "attempt_id": name,
                    "classification": "FAILED_WITH_EVIDENCE",
                    "blocking_findings": [
                        {"category": category, "finding": f"{category} failed"}
                        for category in categories
                    ],
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_two_independent_failures_force_strategy_pivot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            memory = FEEDBACK.empty_memory()
            first = self.make_review(root, "first.json", ["architecture", "shoreline"])
            second = self.make_review(root, "second.json", ["architecture", "shoreline"])
            memory, inserted = FEEDBACK.ingest_review(memory, first, "m01_environment", "a01", ["procedural"])
            self.assertTrue(inserted)
            self.assertEqual(memory["lanes"]["m01_environment"]["classification"], "CONTINUE_BOUNDED")
            memory, inserted = FEEDBACK.ingest_review(memory, second, "m01_environment", "a02", ["procedural"])
            self.assertTrue(inserted)
            decision = memory["lanes"]["m01_environment"]
            self.assertEqual(decision["classification"], "PIVOT_REQUIRED")
            self.assertEqual(decision["repeated_categories"], ["architecture", "shoreline"])

    def test_ingestion_is_idempotent_by_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            review = self.make_review(Path(directory), "same.json", ["lighting"])
            memory, first = FEEDBACK.ingest_review(FEEDBACK.empty_memory(), review, "lane", "a01", [])
            memory, second = FEEDBACK.ingest_review(memory, review, "lane", "a01", [])
            self.assertTrue(first)
            self.assertFalse(second)
            self.assertEqual(len(memory["reviews"]), 1)

    def test_guard_rejects_cosmetic_retry_after_pivot(self) -> None:
        memory = FEEDBACK.empty_memory()
        memory["lanes"] = {
            "m01_environment": {
                "classification": "PIVOT_REQUIRED",
                "required_strategy_tags": list(FEEDBACK.PIVOT_REQUIRED_TAGS),
                "forbidden_strategy_tags": list(FEEDBACK.PIVOT_FORBIDDEN_TAGS),
                "repeated_categories": ["architecture"],
                "next_work_requirements": ["Author geometry."],
            }
        }
        result = FEEDBACK.evaluate_strategy(
            memory,
            "m01_environment",
            ["lighting_only_recovery"],
        )
        self.assertFalse(result["pass"])
        self.assertIn("lighting_only_recovery", result["present_forbidden_tags"])
        self.assertIn("authored_geometry", result["missing_required_tags"])

    def test_guard_accepts_required_asset_specific_strategy(self) -> None:
        memory = FEEDBACK.empty_memory()
        memory["lanes"] = {
            "m01_environment": {
                "classification": "PIVOT_REQUIRED",
                "required_strategy_tags": list(FEEDBACK.PIVOT_REQUIRED_TAGS),
                "forbidden_strategy_tags": list(FEEDBACK.PIVOT_FORBIDDEN_TAGS),
                "repeated_categories": ["facades"],
                "next_work_requirements": [],
            }
        }
        result = FEEDBACK.evaluate_strategy(
            memory,
            "m01_environment",
            FEEDBACK.PIVOT_REQUIRED_TAGS,
        )
        self.assertTrue(result["pass"])
        self.assertEqual(result["classification"], "STRATEGY_ALLOWED_AFTER_PIVOT")

    def test_failure_analysis_text_is_categorized(self) -> None:
        review = {
            "classification": "FAILED_WITH_EVIDENCE",
            "remaining_failures": [
                "procedural facade repetition remains dominant",
                "water visibly tiles and lacks physical surf contact behavior",
            ],
        }
        findings = FEEDBACK.extract_findings(review)
        self.assertEqual(findings[0]["category"], "facades")
        self.assertEqual(findings[1]["category"], "shoreline")


if __name__ == "__main__":
    unittest.main()
