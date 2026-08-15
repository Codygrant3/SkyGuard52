from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery06\build_m01_visible_environment_kit_refinement01_stagea_recovery06_checkpoint01.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery06\invoke_m01_visible_environment_kit_refinement01_stagea_recovery06_checkpoint01_once.ps1"
POSTFLIGHT = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery06_postflight\adjudicate_m01_visible_environment_kit_refinement01_stagea_recovery06_checkpoint01.py"
CONTRACT = ROOT / r"Docs\Toolchain\ToolchainWave08\EnvironmentVisibleKitRefinement01StageARecovery06\execution_contract.json"
R05_FREEZE = ROOT / r"Docs\AAA_Review\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY05_CHECKPOINT01_ATTEMPT01_TERMINAL_FREEZE.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_worker():
    spec = importlib.util.spec_from_file_location("skyguard_r06_worker_test", WORKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Recovery06OfflineTests(unittest.TestCase):
    def test_01_terminal_authority_is_frozen(self) -> None:
        self.assertEqual(R05_FREEZE.stat().st_size, 3112)
        self.assertEqual(sha(R05_FREEZE), "c52c74c2a33b111cd37c53442dda67d9ee93d41d353d653e8111092e9ff69e9a")
        data = json.loads(R05_FREEZE.read_text(encoding="utf-8-sig"))
        self.assertEqual(data["classification"], "FAILED_WITH_EVIDENCE")
        self.assertEqual(data["member_count"], 6)

    def test_02_generated_source_has_complete_named_call_graph(self) -> None:
        module = load_worker()
        source, receipt = module.load_recovery06_source()
        ast.parse(source)
        self.assertEqual(receipt["generated_call_graph"]["unresolved_named_calls"], [])
        self.assertTrue(receipt["generated_call_graph"]["passed"])
        self.assertEqual(source.count("def add_side_window("), 1)
        self.assertEqual(source.count(module.RECOVERY06_GATE_TOKEN), 1)

    def test_03_side_window_helper_preserves_material_depth(self) -> None:
        module = load_worker()
        helper = module.SIDE_WINDOW_HELPER
        for token in ("_Reveal", "_Interior", "_Glass", "_FrameTop", "_FrameBottom", "_Mullion", "_Drip"):
            self.assertIn(token, helper)
        self.assertIn("window_warm", helper)
        self.assertIn("window_cool", helper)
        self.assertIn("window_dark", helper)

    def test_04_checkpoint_contract_is_not_narrowed(self) -> None:
        data = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
        output = data["output_contract"]
        self.assertEqual(output["blend_count"], 1)
        self.assertEqual(output["checkpoint_png_count"], 9)
        self.assertEqual(output["checkpoint_resolution"], [1920, 1080])
        self.assertEqual(output["expected_total_file_count"], 16)
        self.assertEqual(output["glb_count"], output["final_png_count"])
        self.assertEqual(output["texture_png_count"], 0)
        self.assertFalse(data["preservation"]["finalization_authorized"])

    def test_05_supervisor_is_one_shot_and_fresh(self) -> None:
        text = SUPERVISOR.read_text(encoding="utf-8-sig")
        self.assertEqual(text.count("Start-Process"), 1)
        self.assertIn("RECOVERY06_CHECKPOINT01\\attempt_01", text)
        self.assertIn("VisibleEnvironmentKit_Refinement01_StageA_Recovery06_Checkpoint01", text)
        self.assertIn("automatic_retry_count", text)
        self.assertNotIn("while ($retry", text)

    def test_06_postflight_and_future_namespaces(self) -> None:
        ast.parse(POSTFLIGHT.read_text(encoding="utf-8-sig"))
        future = (
            ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01\attempt_01",
            ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentKit_Refinement01_StageA_Recovery06_Checkpoint01",
            ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01_TERMINAL_SUPERVISOR.json",
            ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01_EMERGENCY_RECEIPT.jsonl",
            ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY06_CHECKPOINT01_POSTFLIGHT.json",
        )
        self.assertTrue(all(not path.exists() for path in future))


if __name__ == "__main__":
    unittest.main(verbosity=2)
