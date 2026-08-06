from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUPERVISOR = ROOT / "Scripts" / "run_m01_hero_high_to_low_bake.ps1"


class M01HighToLowSupervisorSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SUPERVISOR.read_text(encoding="utf-8-sig")

    def test_validate_only_never_starts_blender(self) -> None:
        validate_index = self.source.index("if ($ValidateOnly)")
        start_index = self.source.index("$process = Start-Process")
        self.assertLess(validate_index, start_index)
        block = self.source[validate_index:start_index]
        self.assertIn("exit 0", block)

    def test_overlapping_blender_process_is_rejected(self) -> None:
        self.assertIn('Get-Process -Name "blender"', self.source)
        self.assertIn("Refusing to overlap serialized asset builds", self.source)

    def test_process_has_bounded_timeout_and_attempt_logs(self) -> None:
        self.assertIn("$process.WaitForExit($TimeoutSeconds * 1000)", self.source)
        self.assertIn("-RedirectStandardOutput $stdoutPath", self.source)
        self.assertIn("-RedirectStandardError $stderrPath", self.source)
        self.assertIn("attempt_$stamp", self.source)

    def test_artifact_verifier_is_required_after_success(self) -> None:
        self.assertIn("--require-artifacts", self.source)
        self.assertIn("ARTIFACTS_VERIFIED_CANDIDATE_ONLY", self.source)


if __name__ == "__main__":
    unittest.main()
