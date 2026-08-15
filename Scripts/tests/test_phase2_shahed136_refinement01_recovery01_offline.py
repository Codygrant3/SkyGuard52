from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(r"D:\Skyguard52")
VERIFIER = ROOT / "Scripts" / "verify_phase2_shahed136_refinement01_recovery01_offline.py"
SPEC = importlib.util.spec_from_file_location("shahed_recovery01_verifier", VERIFIER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load Recovery01 verifier.")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ShahedRefinementRecovery01OfflineTests(unittest.TestCase):
    def test_original_freeze(self) -> None:
        self.assertEqual(MODULE.verify_original_freeze(), 16)

    def test_authority(self) -> None:
        authority = MODULE.load_json(MODULE.AUTHORITY)
        self.assertEqual(len(authority["authorities"]), 15)
        for record in authority["authorities"]:
            MODULE.verify_record(record)

    def test_compatibility_binding(self) -> None:
        result = MODULE.check_compatibility_binding()
        self.assertTrue(result["patched_main_callable"])
        self.assertTrue(result["direct_action_fcurves_removed"])

    def test_supervisor(self) -> None:
        self.assertGreater(MODULE.check_supervisor()["bytes"], 3000)

    def test_manifest(self) -> None:
        result = MODULE.check_manifest()
        self.assertEqual(result["status"], "ready")
        self.assertIn("recovery01", result["worker"])

    def test_full_verification(self) -> None:
        result = MODULE.verify()
        self.assertEqual(result["classification"], "PASS")
        self.assertEqual(result["heavy_process_count"], 0)


if __name__ == "__main__":
    unittest.main()
