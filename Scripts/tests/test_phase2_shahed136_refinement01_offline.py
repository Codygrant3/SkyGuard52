from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(r"D:\Skyguard52")
VERIFIER = ROOT / "Scripts" / "verify_phase2_shahed136_refinement01_offline.py"
SPEC = importlib.util.spec_from_file_location("shahed_verifier", VERIFIER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load Shahed-136 verifier.")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ShahedRefinementOfflineTests(unittest.TestCase):
    def test_authority_records(self) -> None:
        authority = MODULE.load_json(MODULE.AUTHORITY)
        self.assertEqual(authority["asset_id"], "core-shahed136")
        self.assertEqual(len(authority["authorities"]), 13)
        for record in authority["authorities"]:
            MODULE.verify_record(record)

    def test_prior_freeze(self) -> None:
        self.assertEqual(MODULE.verify_prior_freeze(), 24)

    def test_contracts(self) -> None:
        result = MODULE.check_contracts()
        self.assertEqual(result["cameras"], 8)
        self.assertEqual(result["required_damage_states"], 4)

    def test_worker(self) -> None:
        result = MODULE.check_worker()
        self.assertGreater(result["bytes"], 20000)

    def test_supervisor_and_manifest(self) -> None:
        MODULE.check_supervisor()
        result = MODULE.check_manifest()
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["minimum_renders"], 8)

    def test_full_offline_verification(self) -> None:
        result = MODULE.verify()
        self.assertEqual(result["classification"], "PASS")
        self.assertFalse(result["blender_launched"])
        self.assertFalse(result["unreal_launched"])


if __name__ == "__main__":
    unittest.main()
