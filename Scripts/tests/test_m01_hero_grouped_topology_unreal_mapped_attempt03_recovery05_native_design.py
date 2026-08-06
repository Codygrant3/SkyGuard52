from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY05_NATIVE_DESIGN_CONTRACT.json"
AUDIT_PATH = ROOT / "Scripts/audit_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery05_native_design.py"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


AUDIT = load_module("recovery05_native_design_audit", AUDIT_PATH)


class Recovery05NativeDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
        cls.header = (
            ROOT / cls.contract["native_sources"]["header"]["path"]
        ).read_text(encoding="utf-8-sig")
        cls.cpp = (
            ROOT / cls.contract["native_sources"]["implementation"]["path"]
        ).read_text(encoding="utf-8-sig")

    def test_01_readiness(self) -> None:
        result = AUDIT.audit(write_report=False)
        self.assertEqual(
            result["gate"],
            "PASS_OFFLINE_RECOVERY05_NATIVE_DESIGN_READY_AWAITING_SEPARATE_BUILD_AUTHORIZATION",
        )
        self.assertEqual(result["failure_count"], 0)

    def test_02_all_hash_bindings(self) -> None:
        for group in (
            self.contract["bound_evidence"],
            self.contract["native_sources"],
        ):
            for record in group.values():
                path = ROOT / record["path"]
                self.assertEqual(path.stat().st_size, record["bytes"])
                self.assertEqual(sha256_file(path), record["sha256"])

    def test_03_no_python_scene_capture(self) -> None:
        self.assertNotIn("SceneCapture2D", self.cpp)
        self.assertNotIn("ExecutePythonScript", self.cpp)
        self.assertIn("FScreenshotRequest::RequestScreenshot", self.cpp)

    def test_04_real_frame_shader_idle_warmup(self) -> None:
        self.assertIn("GShaderCompilingManager->IsCompiling()", self.cpp)
        self.assertIn("RequiredWarmupFrames = 120", self.cpp)
        self.assertIn("RequiredWarmupSeconds = 5.0", self.cpp)

    def test_05_three_frame_pilot_before_nine_views(self) -> None:
        self.assertIn("PilotIndex < 3", self.cpp)
        self.assertEqual(self.contract["native_runtime"]["pilot_capture_count"], 3)
        self.assertEqual(self.contract["native_runtime"]["full_view_capture_count"], 9)

    def test_06_exact_native_viewport(self) -> None:
        self.assertIn("RequiredWidth = 2048", self.cpp)
        self.assertIn("RequiredHeight = 2048", self.cpp)
        self.assertIn('Contains(TEXT("D3D12"))', self.cpp)
        self.assertIn('TEXT("SM6")', self.cpp)

    def test_07_fail_closed_and_timeout(self) -> None:
        self.assertIn("ScreenshotTimeoutSeconds = 15.0", self.cpp)
        self.assertIn("RequestExitWithStatus", self.cpp)
        self.assertIn("FAIL_CLOSED_RECOVERY05_NATIVE_CAPTURE", self.cpp)

    def test_08_build_requires_separate_authorization(self) -> None:
        future = self.contract["future_build"]
        self.assertTrue(future["requires_separate_authorization"])
        self.assertTrue(future["post_build_dll_hash_must_be_bound_before_execution"])
        self.assertTrue(future["root_must_wait_for_final_execution_handoff"])

    def test_09_content_is_read_only(self) -> None:
        immutable = self.contract["immutability"]
        self.assertEqual(immutable["content_package_writes"], 0)
        self.assertEqual(immutable["runtime_map_writes"], 0)
        self.assertEqual(immutable["config_writes"], 0)

    def test_10_never_promotes(self) -> None:
        self.assertFalse(self.contract["promotion_allowed"])
        self.assertFalse(self.contract["p3_4_closed"])
        self.assertFalse(self.contract["native_build_authorized"])
        self.assertFalse(self.contract["unreal_launch_authorized"])


if __name__ == "__main__":
    unittest.main()
