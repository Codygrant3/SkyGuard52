from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(r"D:\Skyguard52\Scripts\verify_phase2_yak52_airframe_refinement01_offline.py")
SPEC = importlib.util.spec_from_file_location("yak52_airframe_refinement01_verify", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Yak52AirframeRefinement01OfflineTests(unittest.TestCase):
    def test_full_offline_verification(self) -> None:
        result = MODULE.verify()
        self.assertEqual(result["classification"], "PASS")
        self.assertEqual(result["heavy_process_count"], 0)

    def test_r3_glb_is_substantial_unrigged_source(self) -> None:
        glb = MODULE.inspect_glb(Path(r"D:\Skyguard52\Content\Skyguard\Meshes\Source\Mission01\Yak52_Uplift_003_R3\bld_m01_yak_uplift_003_r3.glb"))
        self.assertGreaterEqual(glb["nodes"], 200)
        self.assertGreaterEqual(glb["meshes"], 200)
        self.assertEqual(glb["skins"], 0)
        self.assertEqual(glb["animations"], 0)

    def test_policy_separates_authoritative_and_derived(self) -> None:
        policy = MODULE.load_json(MODULE.POLICY)
        self.assertEqual(policy["derived_artistic_geometry"]["required_label"], "PROJECT_DERIVED_NONAUTHORITATIVE")
        self.assertIn("absolute measurement", policy["photographic_authority"]["prohibited_uses"])

    def test_camera_and_visual_review_contract(self) -> None:
        cameras = MODULE.load_json(MODULE.CAMERAS)
        rubric = MODULE.load_json(MODULE.RUBRIC)
        self.assertEqual(len(cameras["views"]), 11)
        self.assertEqual(cameras["resolution"], [2560, 1440])
        self.assertTrue(rubric["automatic_pass_is_not_visual_acceptance"])

    def test_bad_authority_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authority.bin"
            path.write_bytes(b"test")
            record = {"path": str(path), "bytes": 4, "sha256": "0" * 64}
            with self.assertRaises(MODULE.VerificationError):
                MODULE.verify_record(record)

    def test_worker_and_supervisor_static_contracts(self) -> None:
        worker = MODULE.check_worker()
        supervisor = MODULE.check_supervisor()
        self.assertEqual(len(worker["sha256"]), 64)
        self.assertEqual(len(supervisor["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
