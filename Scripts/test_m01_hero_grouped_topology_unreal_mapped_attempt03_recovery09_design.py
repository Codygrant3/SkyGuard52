"""Focused offline tests for the Recovery09 design."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AUDIT_PATH = ROOT / (
    "Scripts/"
    "audit_m01_hero_grouped_topology_unreal_mapped_attempt03_"
    "recovery09_design.py"
)
CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY09_DESIGN_CONTRACT.json"
)

SPEC = importlib.util.spec_from_file_location("recovery09_audit", AUDIT_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class Recovery09DesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
        cls.report = AUDIT.audit(write_report=False)
        implementation = cls.contract["recovery09_implementation"]
        cls.source = AUDIT.resolve(implementation["source"]["path"]).read_text(
            encoding="utf-8-sig"
        )
        cls.wrapper = AUDIT.resolve(
            implementation["future_wrapper"]["path"]
        ).read_text(encoding="utf-8-sig")

    def test_01_all_readiness_checks_pass(self) -> None:
        self.assertEqual(self.report["failure_count"], 0)
        self.assertEqual(self.report["pass_count"], self.report["check_count"])

    def test_02_recovery07_terminal_receipts_are_exact(self) -> None:
        failure = self.contract["recovery07_terminal_failure"]
        self.assertTrue(AUDIT.exact(failure["supervisor_receipt"]))
        self.assertTrue(AUDIT.exact(failure["capture_receipt"]))

    def test_03_written_png_is_exact_2048(self) -> None:
        png = self.contract["recovery07_terminal_failure"][
            "written_pilot_png"
        ]
        signature, chunk, width, height = AUDIT.png_ihdr(
            AUDIT.resolve(png["path"])
        )
        self.assertEqual(signature, "89504e470d0a1a0a")
        self.assertEqual(chunk, "IHDR")
        self.assertEqual((width, height), (2048, 2048))

    def test_04_recovery07_and_08_are_unchanged(self) -> None:
        preserved = self.contract["preserved_recovery07_08"]
        for record in preserved.values():
            if isinstance(record, dict) and "path" in record:
                self.assertTrue(AUDIT.exact(record))

    def test_05_correct_ue_delegate_is_used(self) -> None:
        self.assertIn(
            "UGameViewportClient::OnScreenshotCaptured().AddUObject(",
            self.source,
        )
        self.assertNotIn(
            "FScreenshotRequest::OnScreenshotCaptured",
            self.source,
        )

    def test_06_delegate_cvar_is_restored(self) -> None:
        self.assertIn(
            "PreviousScreenshotDelegateValue",
            self.source,
        )
        self.assertIn(
            "RestoreScreenshotDelegateCVar();",
            self.source,
        )

    def test_07_filesystem_fallback_is_stable_and_validated(self) -> None:
        self.assertIn("FilesystemStableFramesRequired = 3", self.source)
        self.assertIn("PngBytes[12] != 0x49", self.source)
        self.assertIn("SceneViewport->ReadPixels(Colors)", self.source)

    def test_08_completion_method_is_receipted(self) -> None:
        self.assertIn('TEXT("completion_method")', self.source)
        self.assertIn("[RECOVERY09][CAPTURE_COMPLETE]", self.source)

    def test_09_recovery09_artifacts_are_exact(self) -> None:
        implementation = self.contract["recovery09_implementation"]
        for key in ("generator", "header", "source", "future_wrapper"):
            self.assertTrue(AUDIT.exact(implementation[key]))

    def test_10_wrapper_requires_future_contract_hash(self) -> None:
        self.assertIn("AuthorizeSingleRecovery09Run", self.wrapper)
        self.assertIn("ExpectedExecutionContractSha256", self.wrapper)
        self.assertIn("RECOVERY09_EXECUTION_CONTRACT.json", self.wrapper)

    def test_11_new_namespace_is_distinct_and_absent(self) -> None:
        output = self.contract["future_output"]
        old = self.contract["recovery07_terminal_failure"]["output_root"]
        self.assertNotEqual(output["attempt_root"], old)
        self.assertFalse(AUDIT.resolve(output["attempt_root"]).exists())

    def test_12_no_build_launch_or_promotion_is_claimed(self) -> None:
        self.assertFalse(self.contract["native_build_executed"])
        self.assertFalse(self.contract["unreal_launched"])
        self.assertFalse(self.contract["blender_launched"])
        self.assertFalse(self.contract["promotion_allowed"])
        self.assertFalse(self.contract["p3_4_closed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
