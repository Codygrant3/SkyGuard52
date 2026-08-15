from __future__ import annotations

import ast
import importlib.util
import json
import re
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery05\build_m01_visible_environment_kit_refinement01_stagea_recovery05_checkpoint01.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery05\invoke_m01_visible_environment_kit_refinement01_stagea_recovery05_checkpoint01_once.ps1"
CONTRACT_DIR = ROOT / r"Docs\Toolchain\ToolchainWave08\EnvironmentVisibleKitRefinement01StageARecovery05"


def load_worker():
    spec = importlib.util.spec_from_file_location("recovery05_checkpoint_worker", WORKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Recovery05CheckpointOfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_worker()
        cls.source, cls.receipt = cls.module.load_recovery05_source()
        cls.tree = ast.parse(cls.source)
        cls.supervisor = SUPERVISOR.read_text(encoding="utf-8")

    def test_checkpoint_receipt(self) -> None:
        self.assertTrue(self.receipt["passed"])
        self.assertTrue(self.receipt["checkpoint_only"])
        self.assertEqual(self.receipt["checkpoint_count"], 9)
        self.assertEqual(self.receipt["final_render_count"], 0)
        self.assertFalse(self.receipt["recovery04_output_geometry_reused"])

    def test_checkpoint_main_has_no_finalization_calls(self) -> None:
        main = next(node for node in self.tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
        calls = [node.func.id for node in ast.walk(main) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
        self.assertNotIn("create_texture_atlas", calls)
        self.assertNotIn("render_final_views", calls)
        self.assertNotIn("export_glb", calls)
        self.assertEqual(calls.count("build_midrise"), 1)

    def test_art_structure_tokens(self) -> None:
        for token in ('"buildings": 5', '"vehicles": 8', '"trees": 10', 'REVIEW_ONLY_OceanSurface', 'SM_M01_STAGEA_R05_Puddle_', 'REVIEW_ONLY_RAIN'):
            self.assertIn(token, self.source)

    def test_nine_fixed_review_frames(self) -> None:
        self.assertIn('for condition in ("daylight", "night", "storm")', self.source)
        for camera in ("coastal_route", "street_close", "district_aerial"):
            self.assertIn(f'"{camera}"', self.source)
        self.assertIn('require(len(results) == 9, "Checkpoint render count is not exactly nine")', self.source)

    def test_int32_safe_png_parser(self) -> None:
        self.assertIn("([int]$bytes[16] * 16777216)", self.supervisor)
        self.assertIn("([int]$bytes[18] * 256)", self.supervisor)
        self.assertNotIn("$bytes[16] -shl 24", self.supervisor)
        for size in ("1280,720", "1920,1080", "2560,1440", "2048,2048"):
            self.assertIn(f"@({size})", self.supervisor)

    def test_one_launch_zero_retry(self) -> None:
        self.assertEqual(len(re.findall(r"\bStart-Process\b", self.supervisor)), 1)
        self.assertIn("retry_count = 0", self.supervisor)
        self.assertNotRegex(self.supervisor, r"(?i)retry\s*\+")

    def test_contracts_are_checkpoint_only(self) -> None:
        execution = json.loads((CONTRACT_DIR / "execution_contract.json").read_text(encoding="utf-8"))
        output = execution["output_contract"]
        self.assertEqual(output["checkpoint_png_count"], 9)
        self.assertEqual(output["expected_total_file_count"], 16)
        self.assertEqual(output["glb_count"], 0)
        self.assertEqual(output["final_png_count"], 0)
        self.assertEqual(output["texture_png_count"], 0)

    def test_finalization_remains_deferred(self) -> None:
        deferred = json.loads((CONTRACT_DIR / "finalization01_deferred_contract.json").read_text(encoding="utf-8"))
        self.assertFalse(deferred["authorized"])
        self.assertTrue(deferred["separate_explicit_authorization_required"])


if __name__ == "__main__":
    unittest.main()
