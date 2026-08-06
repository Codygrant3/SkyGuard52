from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "verify_skyguard_phase7_second_pass_gate.py"
)
SPEC = importlib.util.spec_from_file_location("phase7_second_pass_verifier", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Phase7SecondPassVerifierTests(unittest.TestCase):
    def _fixture(self, mutate=None):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        report_dir = root / "automation-report"
        report_dir.mkdir()
        tests = []
        for prefix, count in MODULE.EXPECTED_FAMILIES.items():
            for index in range(count):
                tests.append(
                    {
                        "fullTestPath": f"{prefix}.Test{index + 1}",
                        "state": "Success",
                        "warnings": 0,
                        "errors": 0,
                    }
                )
        report = {
            "succeeded": len(tests),
            "succeededWithWarnings": 0,
            "failed": 0,
            "notRun": 0,
            "inProcess": 0,
            "tests": tests,
        }
        manifest = {
            "schema": "skyguard.phase7.second-pass-run.v1",
            "terminal_state": "EXECUTION_COMPLETE",
            "stages": [
                {"name": "build_editor", "timed_out": False, "exit_code": 0},
                {
                    "name": "mission_01_10_second_pass",
                    "timed_out": False,
                    "exit_code": 0,
                },
            ],
            "automation_report": str(report_dir / "index.json"),
            "automation_stdout": str(root / "automation.stdout.log"),
        }
        if mutate:
            mutate(manifest, report)
        (report_dir / "index.json").write_text(
            json.dumps(report), encoding="utf-8"
        )
        (root / "automation.stdout.log").write_text(
            "Automation Test Queue Empty 39 tests performed.\n", encoding="utf-8"
        )
        manifest_path = root / "run_manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return temporary, manifest_path

    def test_complete_exact_second_pass_is_accepted(self):
        temporary, manifest_path = self._fixture()
        self.addCleanup(temporary.cleanup)
        result, passed = MODULE.verify(manifest_path)
        self.assertTrue(passed)
        self.assertEqual(result["gate"], "PASS")
        self.assertEqual(result["verified_unique_test_count"], 39)

    def test_missing_mission_test_fails_closed(self):
        def mutate(_manifest, report):
            report["tests"] = [
                test
                for test in report["tests"]
                if test["fullTestPath"] != "Skyguard52.Mission10.Test4"
            ]
            report["succeeded"] -= 1

        temporary, manifest_path = self._fixture(mutate)
        self.addCleanup(temporary.cleanup)
        result, passed = MODULE.verify(manifest_path)
        self.assertFalse(passed)
        self.assertTrue(
            any(item.startswith("family_count:Skyguard52.Mission10") for item in result["failures"])
        )

    def test_warning_or_error_fails_closed(self):
        def mutate(_manifest, report):
            report["tests"][0]["warnings"] = 1
            report["succeededWithWarnings"] = 1

        temporary, manifest_path = self._fixture(mutate)
        self.addCleanup(temporary.cleanup)
        result, passed = MODULE.verify(manifest_path)
        self.assertFalse(passed)
        self.assertIn(
            "family_unsuccessful:Skyguard52.Mission01Integration",
            result["failures"],
        )

    def test_critical_runtime_signature_fails_closed(self):
        temporary, manifest_path = self._fixture()
        self.addCleanup(temporary.cleanup)
        log_path = Path(
            json.loads(manifest_path.read_text(encoding="utf-8"))[
                "automation_stdout"
            ]
        )
        log_path.write_text("GPU timeout waiting for queue\n", encoding="utf-8")
        result, passed = MODULE.verify(manifest_path)
        self.assertFalse(passed)
        self.assertIn("critical_log:gpu_timeout", result["failures"])


if __name__ == "__main__":
    unittest.main()
