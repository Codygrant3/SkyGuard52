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
    HERE / "adjudicate_recovery07_mapped_visual_proof01_recovery03_once.py",
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
        source = (HERE / "capture_recovery07_mapped_visual_proof01_recovery03.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("register_slate_post_tick_callback", source)
        self.assertIn("audit_landscape_material_compilation", source)
        self.assertNotIn("save_current_level", source)
        self.assertNotIn("save_loaded_asset", source)

    def test_recovery03_supervisor_uses_editor_mode_and_stable_csv(self) -> None:
        supervisor = (HERE / "invoke_recovery07_mapped_visual_proof01_recovery03_once.ps1").read_text(encoding="utf-8")
        executor = (HERE / "capture_recovery07_mapped_visual_proof01_recovery03.py").read_text(encoding="utf-8")
        self.assertNotIn("            '-game',", supervisor)
        self.assertIn("-csvCompression=0", supervisor)
        self.assertIn("csv_stable_polls", executor)
        self.assertIn("CSV profile did not become stable within ten seconds", executor)

    def test_recovery03_quotes_exec_cmd_as_one_native_argument(self) -> None:
        supervisor = (HERE / "invoke_recovery07_mapped_visual_proof01_recovery03_once.ps1").read_text(encoding="utf-8")
        self.assertIn("$execCmdValue = \"py $($executor.Replace", supervisor)
        self.assertIn("$execCmdArgument = '-ExecCmds=\"' + $execCmdValue + '\"'", supervisor)
        self.assertIn("$execCmdArgument,", supervisor)
        self.assertNotIn('"-ExecCmds=py $($executor.Replace', supervisor)

    def test_recovery03_has_executor_startup_watchdog(self) -> None:
        supervisor = (HERE / "invoke_recovery07_mapped_visual_proof01_recovery03_once.ps1").read_text(encoding="utf-8")
        executor = (HERE / "capture_recovery07_mapped_visual_proof01_recovery03.py").read_text(encoding="utf-8")
        self.assertIn("$executorStartupTimeoutSeconds = 120", supervisor)
        self.assertIn("executor_startup_receipt_observed", supervisor)
        self.assertIn("SkyguardRecovery07ProofStartupReceipt", supervisor)
        self.assertIn("EXECUTOR_INVOKED", executor)
        self.assertIn("write_json_atomic", executor)

    def test_recovery03_executor_uses_versioned_contract_and_cameras(self) -> None:
        executor = (HERE / "capture_recovery07_mapped_visual_proof01_recovery03.py").read_text(encoding="utf-8")
        self.assertIn("MAPPED_VISUAL_PROOF01_RECOVERY03_CONTRACT.json", executor)
        self.assertIn("MAPPED_VISUAL_PROOF01_RECOVERY03_CAMERAS.json", executor)
        self.assertNotIn('"MAPPED_VISUAL_PROOF01_CONTRACT.json"', executor)
        self.assertNotIn('"MAPPED_VISUAL_PROOF01_CAMERAS.json"', executor)


if __name__ == "__main__":
    unittest.main()
