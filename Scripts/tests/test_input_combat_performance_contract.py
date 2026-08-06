from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class InputCombatContractTests(unittest.TestCase):
    def test_contract_covers_memory_vram_and_all_five_windows(self) -> None:
        contract = json.loads(
            (
                ROOT
                / "Scripts"
                / "skyguard_input_combat_performance_contract_v1.json"
            ).read_text(encoding="utf-8")
        )
        self.assertIn("memory", contract["required_trace_channels"])
        self.assertIn("GPUUsage", contract["required_csv_categories"])
        self.assertIn("TextureStreaming", contract["required_csv_categories"])
        self.assertEqual(len(contract["required_windows"]), 5)
        self.assertEqual(
            {window["id"] for window in contract["required_windows"]},
            {
                "ads_rifle",
                "igla_launch",
                "drone_breakup",
                "boss_destruction",
                "weather_fast_camera",
            },
        )
        self.assertEqual(
            contract["capture_matrix"]["combat_profile"]["required_repeats"], 3
        )
        self.assertEqual(
            contract["capture_matrix"]["combat_soak"]["minimum_seconds_each"],
            1200,
        )

    def test_supervisor_validate_only_precedes_any_execution_path(self) -> None:
        text = (
            ROOT / "Scripts" / "run_skyguard_input_combat_performance_gate.ps1"
        ).read_text(encoding="utf-8")
        self.assertIn("if (-not $ValidateOnly)", text)
        self.assertIn("BLOCKED_PREREQUISITE", text)
        self.assertIn("BLOCKED_RUNTIME_BOOKMARKS", text)
        self.assertIn("nvidia-smi.exe", text)
        self.assertIn("CloseMainWindow()", text)
        self.assertIn("Stop-ExactProcessTree", text)
        self.assertIn("Get-CaptureMachineEventEvidence", text)
        self.assertIn("windows_machine_events.json", text)
        self.assertIn("nvlddmkm|Display", text)
        self.assertIn("Microsoft-Windows-WHEA-Logger", text)
        self.assertIn("NahimicSvc", text)
        self.assertNotIn("-WindowStyle Hidden", text)
        self.assertIn('"memory"', (
            ROOT
            / "Scripts"
            / "skyguard_input_combat_performance_contract_v1.json"
        ).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
