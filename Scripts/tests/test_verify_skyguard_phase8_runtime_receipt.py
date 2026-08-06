from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "verify_skyguard_phase8_runtime_receipt.py"
)
SPEC = importlib.util.spec_from_file_location("runtime_receipt_verifier", SCRIPT)
assert SPEC and SPEC.loader
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class RuntimeReceiptVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.executable = self.root / "Skyguard52.exe"
        self.executable.write_bytes(b"packaged-game")
        self.artifact = self.root / "case.json"
        self.artifact.write_text('{"result":"PASS"}\n', encoding="utf-8")
        self.log_one = self.root / "launch-one.log"
        self.log_two = self.root / "launch-two.log"
        self.log_one.write_text("LogInit: Display: Engine is initialized.\n", encoding="utf-8")
        self.log_two.write_text("LogExit: Exiting.\n", encoding="utf-8")
        self.receipt_path = self.root / "receipt.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def make_cases(self, prefix: str, count: int) -> list[dict[str, str]]:
        return [
            {
                "name": f"{prefix}_{index:02d}",
                "result": "PASS",
                "artifact": str(self.artifact),
            }
            for index in range(count)
        ]

    def write_receipt(self) -> None:
        receipt = {
            "schema": VERIFIER.SCHEMA,
            "gate": "PASS",
            "package_attempt_id": "attempt-test",
            "package_configuration": "Development",
            "package_executable_sha256": VERIFIER.sha256_file(self.executable),
            "input": "PASS",
            "save_round_trip": "PASS",
            "settings_round_trip": "PASS",
            "evidence": {
                "input_cases": self.make_cases("input", 8),
                "save_cases": self.make_cases("save", 4),
                "settings_cases": self.make_cases("settings", 5),
                "launches": [
                    {
                        "pid": 101,
                        "exit_code": 0,
                        "timed_out": False,
                        "log": str(self.log_one),
                    },
                    {
                        "pid": 102,
                        "exit_code": 0,
                        "timed_out": False,
                        "log": str(self.log_two),
                    },
                ],
            },
        }
        self.receipt_path.write_text(
            json.dumps(receipt, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_valid_receipt_passes(self) -> None:
        self.write_receipt()
        report = VERIFIER.verify_receipt(
            self.receipt_path,
            self.executable,
            "attempt-test",
        )
        self.assertEqual(report["gate"], "PASS", report["issues"])

    def test_tampered_executable_fails(self) -> None:
        self.write_receipt()
        self.executable.write_bytes(b"tampered")
        report = VERIFIER.verify_receipt(
            self.receipt_path,
            self.executable,
            "attempt-test",
        )
        self.assertEqual(report["gate"], "FAIL")
        self.assertFalse(report["checks"]["package_executable_hash_matches"])

    def test_critical_launch_log_fails(self) -> None:
        self.write_receipt()
        self.log_two.write_text("Fatal error: synthetic validation failure\n", encoding="utf-8")
        report = VERIFIER.verify_receipt(
            self.receipt_path,
            self.executable,
            "attempt-test",
        )
        self.assertEqual(report["gate"], "FAIL")
        self.assertFalse(report["checks"]["launch_logs_no_critical_signatures"])


if __name__ == "__main__":
    unittest.main()
