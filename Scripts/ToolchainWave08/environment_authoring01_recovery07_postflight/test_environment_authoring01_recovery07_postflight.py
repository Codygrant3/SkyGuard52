import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\environment_authoring01_recovery07_postflight\adjudicate_environment_authoring01_recovery07_once.py")
spec = importlib.util.spec_from_file_location("recovery07_postflight", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PostflightTests(unittest.TestCase):
    def test_success_fixture(self):
        manifest, receipt = module.success_fixture()
        result = module.evaluate(manifest, receipt, input_hash=module.EXPECTED_INPUT, output_exists=True, output_hash="fixture-output")
        self.assertEqual(result["classification"], module.SUCCESS_MANIFEST)

    def test_failure_fixture(self):
        manifest, _ = module.success_fixture()
        manifest.update(classification="FAILED_WITH_EVIDENCE", exit_code=-1, failure="bounded failure")
        receipt = {"classification": "FAILED_WITH_EVIDENCE", "error": {"message": "bounded failure"}}
        result = module.evaluate(manifest, receipt, input_hash=module.EXPECTED_INPUT, output_exists=False, output_hash=None)
        self.assertEqual(result["classification"], "FAILED_WITH_EVIDENCE")
        self.assertEqual(result["failure"], "bounded failure")

    def test_failed_execution_without_receipt_is_frozen(self):
        manifest, _ = module.success_fixture()
        manifest.update(classification="FAILED_WITH_EVIDENCE", exit_code=-1, failure="engine crash")
        result = module.evaluate(manifest, None, input_hash=module.EXPECTED_INPUT, output_exists=False, output_hash=None)
        self.assertEqual(result["classification"], "FAILED_WITH_EVIDENCE")
        self.assertFalse(result["receipt_present"])

    def test_zero_launch_preflight_failure_is_frozen(self):
        manifest = {
            "classification": "FAILED_WITH_EVIDENCE",
            "unreal_launch_count": 0,
            "retry_count": 0,
            "exit_code": None,
            "exit_code_type": None,
            "timed_out": False,
            "failure": "preflight failed",
        }
        result = module.evaluate(manifest, None, input_hash=module.EXPECTED_INPUT, output_exists=False, output_hash=None)
        self.assertEqual(result["classification"], "FAILED_WITH_EVIDENCE")

    def test_retry_rejected(self):
        manifest, receipt = module.success_fixture()
        manifest["retry_count"] = 1
        with self.assertRaisesRegex(RuntimeError, "retry count"):
            module.evaluate(manifest, receipt, input_hash=module.EXPECTED_INPUT, output_exists=True, output_hash="fixture-output")

    def test_changed_input_rejected(self):
        manifest, receipt = module.success_fixture()
        with self.assertRaisesRegex(RuntimeError, "input map"):
            module.evaluate(manifest, receipt, input_hash="wrong", output_exists=True, output_hash="fixture-output")

    def test_success_without_receipt_rejected(self):
        manifest, _ = module.success_fixture()
        with self.assertRaisesRegex(RuntimeError, "lacks an authoring receipt"):
            module.evaluate(manifest, None, input_hash=module.EXPECTED_INPUT, output_exists=True, output_hash="fixture-output")

    def test_director_count_rejected(self):
        manifest, receipt = module.success_fixture()
        receipt["director_acquisition"]["after_count"] = 0
        with self.assertRaisesRegex(RuntimeError, "director acquisition"):
            module.evaluate(manifest, receipt, input_hash=module.EXPECTED_INPUT, output_exists=True, output_hash="fixture-output")

    def test_shoreline_rejected(self):
        manifest, receipt = module.success_fixture()
        receipt["shore_contact_checks"]["observed_vertical_delta_cm"] = 121.0
        with self.assertRaisesRegex(RuntimeError, "shore vertical"):
            module.evaluate(manifest, receipt, input_hash=module.EXPECTED_INPUT, output_exists=True, output_hash="fixture-output")


    def test_failed_execution_preserves_partial_output_evidence(self):
        manifest, _ = module.success_fixture()
        manifest.update(classification="FAILED_WITH_EVIDENCE", exit_code=3, failure="bounded failure")
        result = module.evaluate(
            manifest,
            None,
            input_hash=module.EXPECTED_INPUT,
            output_exists=True,
            output_hash="partial-output",
        )
        self.assertEqual(result["classification"], "FAILED_WITH_EVIDENCE")
        self.assertTrue(result["output_map_exists"])
        self.assertEqual(result["output_sha256"], "partial-output")

    def test_tool_contains_no_heavy_launch_path(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("UnrealEditor", source)
        self.assertNotIn("Start-Process", source)
        self.assertIn("verify_execution_binding()", source)

    def test_missing_terminal_manifest_has_freezable_failure_outcome(self):
        result = module.missing_manifest_outcome()
        self.assertEqual(result["classification"], "FAILED_WITH_EVIDENCE")
        self.assertEqual(result["next_gate"], "OFFLINE_ONLY_RECOVERY08_CORRECTION_DESIGN")
        self.assertIn("terminal supervisor manifest is missing", result["failure"])


if __name__ == "__main__":
    unittest.main()
