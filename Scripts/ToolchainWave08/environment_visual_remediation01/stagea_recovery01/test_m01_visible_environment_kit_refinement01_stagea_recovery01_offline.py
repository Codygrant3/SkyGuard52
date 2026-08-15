from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
VERIFIER = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/stagea_recovery01/verify_m01_visible_environment_kit_refinement01_stagea_recovery01_offline.py"
CONTRACT = ROOT / "Docs/Toolchain/ToolchainWave08/EnvironmentVisibleKitRefinement01StageARecovery01/execution_contract.json"
WRAPPER = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/stagea_recovery01/build_m01_visible_environment_kit_refinement01_stagea_recovery01.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verifier = load(VERIFIER, "stagea_recovery01_verifier")
wrapper = load(WRAPPER, "stagea_recovery01_wrapper_test")


class StageARecovery01OfflineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_complete_offline_verifier_passes(self) -> None:
        self.assertEqual("PASS", verifier.validate()["classification"])

    def test_exact_bounded_replacement(self) -> None:
        corrected, receipt = wrapper.load_bounded_source()
        self.assertEqual(1, receipt["old_token_count"])
        self.assertEqual(1, receipt["new_token_count"])
        self.assertNotIn("rough = np.repeat(rough, size, axis=1)", corrected)
        self.assertEqual(1, corrected.count("rough.shape == (size, size, 1)"))

    def test_memory_bound_is_sixty_four_mib(self) -> None:
        self.assertEqual(67_108_864, self.contract["bounded_correction"]["future_memory_bound"]["largest_single_texture_array_bytes"])

    def test_visual_and_export_contract_unchanged(self) -> None:
        output = self.contract["output_contract"]
        self.assertEqual((1, 4, 3, 15, 5), (output["blend_count"], output["glb_count"], output["checkpoint_png_count"], output["final_png_count"], output["texture_png_count"]))

    def test_failed_attempt_preserved_and_future_fresh(self) -> None:
        self.assertTrue(verifier.FAILED_OUTPUT.is_dir())
        self.assertFalse(any(path.is_file() for path in verifier.FAILED_OUTPUT.rglob("*")))
        self.assertFalse(any(path.exists() for path in verifier.FUTURE))

    def test_one_launch_zero_retry(self) -> None:
        execution = self.contract["execution"]
        self.assertEqual(1, execution["blender_launch_count"])
        self.assertEqual(0, execution["automatic_retry_count"])
        self.assertEqual(0, execution["unreal_launch_count"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
