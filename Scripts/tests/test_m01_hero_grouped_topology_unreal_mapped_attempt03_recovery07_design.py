from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY07_DESIGN_CONTRACT.json"
)
AUDIT_PATH = ROOT / (
    "Scripts/"
    "audit_m01_hero_grouped_topology_unreal_mapped_attempt03_"
    "recovery07_design.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


AUDIT = load_module("recovery07_design_audit", AUDIT_PATH)


class Recovery07DesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
        impl = cls.contract["native_sources"]["implementation"]["path"]
        cls.source = (ROOT / impl).read_text(encoding="utf-8-sig")

    def test_01_readiness(self) -> None:
        result = AUDIT.audit(write_report=False)
        self.assertEqual(
            result["gate"],
            "PASS_RECOVERY07_OFFLINE_DESIGN_READY_"
            "AWAITING_SEPARATE_FULL_MODULE_COMPILE_AUTHORIZATION",
        )
        self.assertEqual(result["failure_count"], 0)

    def test_02_recovery06_failure_preserved(self) -> None:
        self.assertTrue(
            all(
                AUDIT.exact(record)
                for record in self.contract[
                    "recovery06_failure_evidence"
                ].values()
            )
        )

    def test_03_highres_dummy_viewport_path(self) -> None:
        self.assertIn(
            "HighRes.SetResolution(RequiredWidth, RequiredHeight, 1.0f)",
            self.source,
        )
        self.assertIn(
            "SceneViewport->TakeHighResScreenShot()", self.source
        )

    def test_04_live_viewport_size_not_hard_gate(self) -> None:
        self.assertNotIn("Viewport is not exact 2048x2048", self.source)
        self.assertIn(
            "live_viewport_has_no_renderable_extent", self.source
        )

    def test_05_callback_dimensions_hard_gate(self) -> None:
        self.assertIn(
            "Width != RequiredWidth || Height != RequiredHeight",
            self.source,
        )

    def test_06_bounded_waits(self) -> None:
        self.assertIn("WorldReadinessTimeoutSeconds = 45.0", self.source)
        self.assertIn("ScreenshotTimeoutSeconds = 30.0", self.source)
        self.assertIn("AbsoluteSessionTimeoutSeconds = 300.0", self.source)

    def test_07_diagnostics(self) -> None:
        self.assertIn("[RECOVERY07][STATE]", self.source)
        self.assertIn("[RECOVERY07][CAPTURE_CALLBACK]", self.source)
        self.assertIn("[RECOVERY07][FAIL]", self.source)

    def test_08_post_build_rebind_required(self) -> None:
        future = self.contract["future_build"]
        self.assertTrue(future["full_module_compile_required"])
        self.assertTrue(future["post_build_dll_hash_must_be_bound"])
        self.assertTrue(future["post_build_execution_contract_required"])

    def test_09_new_namespace(self) -> None:
        self.assertIn(
            "mapped_view_capture_03_recovery_07_highres",
            self.contract["future_output"]["attempt_root"],
        )

    def test_10_offline_only(self) -> None:
        self.assertFalse(self.contract["native_build_executed"])
        self.assertFalse(self.contract["unreal_launched"])
        self.assertFalse(self.contract["promotion_allowed"])
        self.assertFalse(self.contract["p3_4_closed"])


if __name__ == "__main__":
    unittest.main()
