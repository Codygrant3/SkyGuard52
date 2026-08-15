from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
VERIFIER_PATH = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/verify_m01_visible_environment_kit_refinement01_stagea_offline.py"
CONTRACT_PATH = ROOT / "Docs/Toolchain/ToolchainWave08/EnvironmentVisibleKitRefinement01StageA/execution_contract.json"
GENERATOR_PATH = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/build_m01_visible_environment_kit_refinement01_stagea.py"
SUPERVISOR_PATH = ROOT / "Scripts/ToolchainWave08/environment_visual_remediation01/invoke_m01_visible_environment_kit_refinement01_stagea_once.ps1"


spec = importlib.util.spec_from_file_location("stagea_verifier", VERIFIER_PATH)
assert spec and spec.loader
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class StageAOfflineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.generator = GENERATOR_PATH.read_text(encoding="utf-8")
        self.supervisor = SUPERVISOR_PATH.read_text(encoding="utf-8")

    def test_complete_offline_verifier(self) -> None:
        result = verifier.validate()
        self.assertEqual("PASS", result["classification"])
        self.assertEqual(8, result["authority_count"])

    def test_single_heavy_launch_and_no_retry(self) -> None:
        execution = self.contract["execution"]
        self.assertEqual(1, execution["blender_launch_count"])
        self.assertEqual(0, execution["automatic_retry_count"])
        self.assertEqual(0, execution["unreal_launch_count"])
        self.assertEqual(1, self.supervisor.count("Start-Process"))

    def test_output_cardinality(self) -> None:
        output = self.contract["output_contract"]
        self.assertEqual((1, 4, 3, 15, 5), (
            output["blend_count"],
            output["glb_count"],
            output["checkpoint_png_count"],
            output["final_png_count"],
            output["texture_png_count"],
        ))

    def test_fresh_geometry_boundary(self) -> None:
        self.assertNotIn("bpy.data.libraries.load", self.generator)
        self.assertNotIn("Coastal_Production_001", self.generator)
        self.assertIn("build_solid_terrain", self.generator)
        self.assertIn("build_midrise", self.generator)

    def test_blender_52_compatibility_tokens(self) -> None:
        self.assertIn('scene.render.engine = "BLENDER_EEVEE"', self.generator)
        self.assertNotIn("BLENDER_EEVEE_NEXT", self.generator)
        self.assertIn('obj.empty_display_type = "PLAIN_AXES"', self.generator)
        self.assertNotIn('empty_display_type = "CROSS"', self.generator)

    def test_visual_review_is_not_automatic_acceptance(self) -> None:
        self.assertTrue(self.contract["visual_review"]["direct_full_resolution_review_required"])
        self.assertTrue(self.contract["visual_review"]["automatic_luminance_is_not_visual_acceptance"])
        self.assertIn("BLENDER_COMPLETED_AWAITING_EXTERNAL_FULL_RESOLUTION_VISUAL_REVIEW", self.generator)


if __name__ == "__main__":
    unittest.main()
