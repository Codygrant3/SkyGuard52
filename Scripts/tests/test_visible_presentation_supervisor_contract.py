from __future__ import annotations

import json
import unittest
from pathlib import Path


SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
SUPERVISOR = SCRIPTS_ROOT / "run_skyguard_visible_presentation_preflight.ps1"
VERIFIER = SCRIPTS_ROOT / "verify_skyguard_visible_presentation_preflight.py"
SCHEMA = (
    SCRIPTS_ROOT / "skyguard_visible_presentation_preflight_report_v1.schema.json"
)


class VisiblePresentationSupervisorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SUPERVISOR.read_text(encoding="utf-8-sig")

    def test_exact_bounded_two_stage_contract_is_present(self) -> None:
        self.assertIn('$entryMap = "/Engine/Maps/Entry"', self.source)
        self.assertIn(
            '$m01Map = "/Game/Skyguard/Maps/Lvl_M01_CoastalIntercept_Playable_v1"',
            self.source,
        )
        self.assertIn("$smokeSeconds = 10", self.source)
        self.assertIn("$stageTimeoutSeconds = 35", self.source)
        self.assertIn('"entry_visible"', self.source)
        self.assertIn('"m01_visible"', self.source)
        self.assertIn("SKIPPED_ENTRY_FAILED", self.source)
        self.assertIn("$entryCoreRenderHealthy", self.source)
        self.assertIn("$entryStage.module_scan.query_complete", self.source)
        self.assertIn(
            "$entryStage.signatures.gpu_timeout_count -eq 0",
            self.source,
        )
        self.assertIn(
            "the verifier still rejects the overall gate",
            self.source,
        )

    def test_firewall_collection_is_read_only(self) -> None:
        self.assertIn("Get-NetFirewallApplicationFilter", self.source)
        self.assertIn("Get-NetFirewallRule", self.source)
        self.assertIn('operation = "READ_ONLY_INSPECTION"', self.source)
        self.assertIn("mutation_attempted = $false", self.source)
        for forbidden in (
            "Set-NetFirewallRule",
            "New-NetFirewallRule",
            "Remove-NetFirewallRule",
            "netsh advfirewall",
        ):
            self.assertNotIn(forbidden, self.source)

    def test_driver_module_timeout_and_cleanup_evidence_are_present(self) -> None:
        self.assertIn("Win32_VideoController", self.source)
        self.assertIn("$process.Modules", self.source)
        self.assertIn("nvspcap", self.source)
        self.assertIn("GPU timeout:", self.source)
        self.assertIn("$signatureMatches", self.source)
        self.assertIn("$overlayMatches", self.source)
        self.assertNotIn("$matches = @()", self.source)
        self.assertIn("taskkill.exe /PID", self.source)
        self.assertIn("post_cleanup_process_exists", self.source)
        self.assertIn("Get-Process -Id $process.Id", self.source)

    def test_supervisor_hands_report_to_fail_closed_verifier(self) -> None:
        self.assertIn(str(VERIFIER.name), self.source)
        self.assertIn("--report $reportPath --output $verificationPath", self.source)
        self.assertIn("if ($verificationExitCode -ne 0)", self.source)
        self.assertIn("exit 2", self.source)

    def test_report_schema_is_current_and_canonical(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(
            "skyguard.visible-presentation-preflight.report.v1", schema["$id"]
        )
        self.assertEqual(
            {"x": 1280, "y": 720},
            schema["properties"]["configuration"]["properties"]["resolution"]["const"],
        )
        self.assertEqual(
            35,
            schema["properties"]["configuration"]["properties"][
                "stage_timeout_seconds"
            ]["const"],
        )
        self.assertEqual(2, schema["properties"]["stages"]["minItems"])
        self.assertEqual(2, schema["properties"]["stages"]["maxItems"])


if __name__ == "__main__":
    unittest.main()
