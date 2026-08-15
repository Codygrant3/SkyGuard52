import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\environment_authoring01_recovery05_postflight\adjudicate_environment_authoring01_recovery05_once.py")
spec = importlib.util.spec_from_file_location("recovery05_postflight", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PostflightTests(unittest.TestCase):
    def test_success_fixture(self):
        manifest, receipt = module.success_fixture()
        result = module.evaluate(manifest, receipt, input_hash=module.EXPECTED_INPUT, output_exists=True, output_hash="fixture-output")
        self.assertEqual(result["classification"], module.SUCCESS_MANIFEST)

    def test_failure_fixture(self):
        manifest, _ = module.success_fixture()
        manifest.update(classification="FAILED_WITH_EVIDENCE", exit_code=-1)
        receipt = {"classification": "FAILED_WITH_EVIDENCE", "error": {"message": "bounded failure"}}
        result = module.evaluate(manifest, receipt, input_hash=module.EXPECTED_INPUT, output_exists=False, output_hash=None)
        self.assertEqual(result["classification"], "FAILED_WITH_EVIDENCE")
        self.assertEqual(result["failure"], "bounded failure")

    def test_retry_rejected(self):
        manifest, receipt = module.success_fixture()
        manifest["retry_count"] = 1
        with self.assertRaisesRegex(RuntimeError, "retry count"):
            module.evaluate(manifest, receipt, input_hash=module.EXPECTED_INPUT, output_exists=True, output_hash="fixture-output")

    def test_changed_input_rejected(self):
        manifest, receipt = module.success_fixture()
        with self.assertRaisesRegex(RuntimeError, "input map"):
            module.evaluate(manifest, receipt, input_hash="wrong", output_exists=True, output_hash="fixture-output")

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


if __name__ == "__main__":
    unittest.main()
