from __future__ import annotations

import re
import unittest
from pathlib import Path


SUPERVISOR = (
    Path(__file__).resolve().parents[1]
    / "run_skyguard_phase8_release_gate.ps1"
)


class ReleaseSupervisorSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SUPERVISOR.read_text(encoding="utf-8-sig")
        cls.lines = cls.source.splitlines()

    def test_packaged_cook_contract_uses_report_gate_not_ambient_exit_code(self) -> None:
        invocation = self.source.rfind("& py -3 $CookContractVerifier")
        self.assertGreaterEqual(invocation, 0)
        decision = self.source.find(
            'if ($null -eq $cookContract -or $cookContract.gate -ne "PASS")',
            invocation,
        )
        self.assertGreater(decision, invocation)
        decision_block = self.source[invocation:decision]
        self.assertNotIn("$LASTEXITCODE", decision_block)
        self.assertIn("ConvertFrom-Json", decision_block)

    def test_every_last_exit_code_read_is_snapshotted_immediately(self) -> None:
        reads = [
            (index, line.strip())
            for index, line in enumerate(self.lines)
            if "$LASTEXITCODE" in line
        ]
        self.assertTrue(reads)
        for index, line in reads:
            self.assertRegex(
                line,
                r"^\$[A-Za-z][A-Za-z0-9]*ExitCode\s*=\s*\$LASTEXITCODE$",
                msg=f"Ambient LASTEXITCODE read at line {index + 1}: {line}",
            )
            previous = next(
                (
                    candidate.strip()
                    for candidate in reversed(self.lines[:index])
                    if candidate.strip()
                ),
                "",
            )
            self.assertTrue(
                previous.startswith("& ")
                or previous.startswith("-PackageAttemptRoot")
                or previous.startswith("--output")
                or previous.startswith("--latest-output"),
                msg=(
                    f"LASTEXITCODE snapshot at line {index + 1} is not "
                    f"immediately after an external invocation: {previous}"
                ),
            )

    def test_named_exit_codes_drive_only_their_own_decisions(self) -> None:
        expected = {
            "releaseTierPreflightExitCode": (
                r"if \(\$releaseTierPreflightExitCode -ne 0\)"
            ),
            "cookPreflightExitCode": r"if \(\$cookPreflightExitCode -ne 0\)",
            "runtimeValidationExitCode": (
                r"if \(\$runtimeValidationExitCode -ne 0\)"
            ),
            "releaseVerifierExitCode": r"exit \$releaseVerifierExitCode",
        }
        for variable, decision in expected.items():
            self.assertEqual(
                1,
                len(re.findall(rf"\${variable}\s*=\s*\$LASTEXITCODE", self.source)),
            )
            self.assertRegex(self.source, decision)

    def test_release_tier_preflight_runs_before_any_packaging(self) -> None:
        tier_invocation = self.source.find("& py -3 @releaseTierArguments")
        packaging_loop = self.source.find("foreach ($configuration in $configurations)")
        build_cook_run = self.source.find("BuildCookRun")
        self.assertGreaterEqual(tier_invocation, 0)
        self.assertGreater(packaging_loop, tier_invocation)
        self.assertGreater(build_cook_run, tier_invocation)
        self.assertIn(
            'terminal_state = "RELEASE_TIER_PREFLIGHT_FAILED"',
            self.source[tier_invocation:packaging_loop],
        )

    def test_backward_compatible_default_is_explicit_engineering_exception(self) -> None:
        self.assertRegex(
            self.source,
            r'\[string\]\$ReleaseTier\s*=\s*"Engineering"',
        )
        self.assertRegex(
            self.source,
            r"\[bool\]\$EngineeringAudioException\s*=\s*\$true",
        )
        self.assertIn("release_tier = $ReleaseTier", self.source)
        self.assertIn(
            "engineering_audio_exception = $EffectiveEngineeringAudioException",
            self.source,
        )
        self.assertIn(
            '$ReleaseTier -eq "Engineering" -and $EngineeringAudioException',
            self.source,
        )


if __name__ == "__main__":
    unittest.main()
