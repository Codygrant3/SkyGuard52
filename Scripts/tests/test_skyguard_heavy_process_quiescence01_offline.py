from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
VERIFIER = ROOT / "Scripts/verify_skyguard_heavy_process_quiescence01_offline.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("heavy_process_quiescence_verifier", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verifier = load_verifier()


class HeavyProcessQuiescence01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verifier.validate()

    def test_complete_verification_passes(self) -> None:
        self.assertEqual("PASS", self.result["classification"])

    def test_dotnet_and_msbuild_are_governed(self) -> None:
        self.assertTrue(self.result["dotnet_governed"])
        self.assertTrue(self.result["msbuild_governed"])

    def test_blender_mcp_is_not_misclassified(self) -> None:
        self.assertTrue(self.result["blender_mcp_excluded"])

    def test_gate_is_read_only(self) -> None:
        self.assertEqual(0, self.result["child_process_launches_by_gate"])
        self.assertEqual(0, self.result["filesystem_writes_by_gate"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
