import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("adjudicate_m01_visible_environment_kit_refinement01_stagea_recovery02.py")
SPEC = importlib.util.spec_from_file_location("stagea_recovery02_postflight", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class Recovery02PostflightTests(unittest.TestCase):
    def test_expected_file_cardinality(self):
        self.assertEqual(len(MODULE.exact_expected_files()), 37)

    def test_relative_path_normalization(self):
        self.assertEqual(MODULE.normalized_relative(r"renders\final\daylight_close.png"), "renders/final/daylight_close.png")
        with self.assertRaises(MODULE.ContractError):
            MODULE.normalized_relative("../escape")

    def test_complete_fixture_passes(self):
        with tempfile.TemporaryDirectory(prefix="skyguard_stagea_recovery02_postflight_test_") as temporary:
            output, attempt, manifest = MODULE.make_fixture(Path(temporary))
            report, visual = MODULE.evaluate(output, attempt, manifest)
            self.assertEqual(report["classification"], MODULE.AUTOMATIC_PASS)
            self.assertEqual(visual["render_count"], 18)

    def test_inventory_tamper_fails(self):
        with tempfile.TemporaryDirectory(prefix="skyguard_stagea_recovery02_postflight_test_") as temporary:
            output, attempt, manifest = MODULE.make_fixture(Path(temporary))
            path = output / MODULE.TEXTURES[0]
            path.write_bytes(path.read_bytes() + b"tamper")
            with self.assertRaises(MODULE.ContractError):
                MODULE.evaluate(output, attempt, manifest)

    def test_supervisor_retry_fails(self):
        passing = {
            "classification": MODULE.SUPERVISOR_SUCCESS,
            "terminal": True,
            "preflight_passed": True,
            "supervisor_launch_count": 1,
            "blender_launch_count": 1,
            "retry_count": 1,
            "unreal_launch_count": 0,
        }
        with self.assertRaises(MODULE.ContractError):
            MODULE.verify_supervisor(passing)


if __name__ == "__main__":
    unittest.main()
