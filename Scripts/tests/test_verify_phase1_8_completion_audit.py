from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "verify_phase1_8_completion_audit.py"
)
SPEC = importlib.util.spec_from_file_location("completion_audit", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def audit_text(
    *,
    duplicate: bool = False,
    bad_class: bool = False,
    wrong_summary: bool = False,
    omit_phase: int | None = None,
) -> str:
    rows = []
    classifications = []
    for phase in range(1, 9):
        if phase == omit_phase:
            continue
        requirement_id = "P1.1" if duplicate and phase == 2 else f"P{phase}.1"
        classification = (
            "UNKNOWN" if bad_class and phase == 1 else "PROVEN COMPLETE"
        )
        classifications.append(classification)
        rows.append(
            f"| {requirement_id} | Requirement for phase {phase} is concrete "
            f"| **{classification}** | Evidence path and accepted field for phase {phase}. |"
        )
    proven = 99 if wrong_summary else len(classifications)
    return "\n".join(
        [
            "# Audit",
            "",
            "The 8 audited requirements classify as:",
            "",
            f"- {proven} **PROVEN COMPLETE**;",
            "- 0 **INCOMPLETE**;",
            "- 0 **INSUFFICIENTLY EVIDENCED**;",
            "- 0 **BLOCKED — EXTERNAL LICENSED SOURCE**.",
            "",
            *rows,
            "",
            "**M01 Gold Visual and Input-Driven Performance Candidate**",
            "",
        ]
    )


class CompletionAuditTests(unittest.TestCase):
    def run_case(self, text: str) -> dict:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "audit.md"
            path.write_text(text, encoding="utf-8")
            return MODULE.verify(path)

    def test_valid_matrix_passes(self) -> None:
        report = self.run_case(audit_text())
        self.assertEqual(report["gate"], "PASS")
        self.assertEqual(report["requirement_count"], 8)

    def test_duplicate_id_fails(self) -> None:
        report = self.run_case(audit_text(duplicate=True))
        self.assertEqual(report["gate"], "FAIL")
        self.assertIn(
            "DUPLICATE_REQUIREMENT_IDS",
            {issue["code"] for issue in report["issues"]},
        )

    def test_unknown_classification_fails(self) -> None:
        report = self.run_case(audit_text(bad_class=True))
        self.assertEqual(report["gate"], "FAIL")
        self.assertIn(
            "UNKNOWN_CLASSIFICATION",
            {issue["code"] for issue in report["issues"]},
        )

    def test_summary_count_mismatch_fails(self) -> None:
        report = self.run_case(audit_text(wrong_summary=True))
        self.assertEqual(report["gate"], "FAIL")
        self.assertIn(
            "SUMMARY_COUNT_MISMATCH",
            {issue["code"] for issue in report["issues"]},
        )

    def test_missing_phase_fails(self) -> None:
        report = self.run_case(audit_text(omit_phase=8))
        self.assertEqual(report["gate"], "FAIL")
        self.assertIn(
            "MISSING_PHASE_REQUIREMENTS",
            {issue["code"] for issue in report["issues"]},
        )


if __name__ == "__main__":
    unittest.main()
