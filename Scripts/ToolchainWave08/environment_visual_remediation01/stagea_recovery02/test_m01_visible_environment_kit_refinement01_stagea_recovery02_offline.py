from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
VERIFIER = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/stagea_recovery02/verify_m01_visible_environment_kit_refinement01_stagea_recovery02_offline.py"
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/EnvironmentVisibleKitRefinement01StageARecovery02/execution_contract.json"
WRAPPER = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/stagea_recovery02/build_m01_visible_environment_kit_refinement01_stagea_recovery02.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verifier = load(VERIFIER, "stagea_recovery02_verifier")
wrapper = load(WRAPPER, "stagea_recovery02_wrapper_test")


class StageARecovery02OfflineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_complete_offline_verifier_passes(self) -> None:
        self.assertEqual("PASS", verifier.validate()["classification"])

    def test_two_exact_bounded_replacements(self) -> None:
        corrected, receipt = wrapper.load_bounded_source()
        self.assertEqual(1, receipt["roughness_token_count"])
        self.assertEqual(1, receipt["measurement_token_count"])
        self.assertNotIn("rough = np.repeat(rough, size, axis=1)", corrected)
        self.assertNotIn('bpy.data.images.get("Render Result")', corrected)

    def test_saved_png_is_measured_and_removed(self) -> None:
        corrected, _ = wrapper.load_bounded_source()
        self.assertEqual(1, corrected.count("bpy.data.images.load(str(path), check_existing=False)"))
        self.assertEqual(1, corrected.count("bpy.data.images.remove(measured)"))
        self.assertIn("finally:", corrected)

    def test_empty_buffers_fail_closed(self) -> None:
        corrected, _ = wrapper.load_bounded_source()
        self.assertIn("width > 0 and height > 0", corrected)
        self.assertIn("pixels.size == expected_values and pixels.size > 0", corrected)
        self.assertIn("luma.size == width * height and luma.size > 0", corrected)

    def test_visual_and_export_contract_unchanged(self) -> None:
        output = self.contract["output_contract"]
        self.assertEqual((1, 4, 3, 15, 5), (output["blend_count"], output["glb_count"], output["checkpoint_png_count"], output["final_png_count"], output["texture_png_count"]))
        correction = self.contract["bounded_correction"]
        self.assertEqual((0, 0, 0, 0, 0, 0), tuple(correction[key] for key in ("geometry_changes", "material_changes", "camera_changes", "render_setting_changes", "export_changes", "receipt_contract_changes")))

    def test_recovery01_preserved_and_recovery02_fresh(self) -> None:
        self.assertEqual(13, verifier.verify_recovery01_freeze())
        self.assertFalse(any(path.exists() for path in verifier.FUTURE))

    def test_one_launch_zero_retry(self) -> None:
        execution = self.contract["execution"]
        self.assertEqual(1, execution["blender_launch_count"])
        self.assertEqual(0, execution["automatic_retry_count"])
        self.assertEqual(0, execution["unreal_launch_count"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
