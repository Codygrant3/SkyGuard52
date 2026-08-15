from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(r"D:\Skyguard52\Scripts\verify_phase2_reargunner_character_refinement01_offline.py")
SPEC = importlib.util.spec_from_file_location("reargunner_character_refinement01_verify", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RearGunnerCharacterRefinement01OfflineTests(unittest.TestCase):
    def test_full_offline_verification(self) -> None:
        result = MODULE.verify()
        self.assertEqual(result["classification"], "PASS")
        self.assertEqual(result["heavy_process_count"], 0)
        self.assertTrue(result["future_attempt_absent"])

    def test_contracts_cover_all_poses_lighting_and_eye_datum(self) -> None:
        result = MODULE.check_contracts()
        self.assertEqual(result["cameras"], 12)
        self.assertEqual(result["lighting"], ["cockpit", "daylight", "night", "overcast", "wet"])
        self.assertEqual(result["frames"], [1, 20, 40, 60, 80])
        self.assertEqual(result["ads_eye_datum_m"], 0.780)

    def test_worker_is_fresh_and_donor_import_is_forbidden(self) -> None:
        result = MODULE.check_worker()
        self.assertEqual(len(result["sha256"]), 64)
        source = MODULE.WORKER.read_text(encoding="utf-8")
        self.assertNotIn("bpy.ops.import_", source)
        self.assertNotIn("bpy.data.libraries.load", source)
        self.assertIn('"exported_hand_mesh_count": 0', source)

    def test_manifest_preserves_original_lane_and_adds_ready_refinement(self) -> None:
        result = MODULE.check_manifest()
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["old_lane"], "queued")

    def test_selected_dimensions_are_inside_frozen_envelope(self) -> None:
        result = MODULE.check_anthropometric_boundary()
        self.assertEqual(result["classification"], "READY_FOR_BLOCKOUT_ONLY")
        self.assertEqual(result["selected_mm"]["sitting_height"], 895)

    def test_character_capability_is_not_geometry_acceptance(self) -> None:
        result = MODULE.check_character_capability_boundary()
        self.assertEqual(result["classification"], "PASSED_CHARACTER_STACK_CAPABILITY_SMOKE")
        self.assertEqual(result["classes"], ["ControlRig", "IKRigDefinition", "MetaHumanCharacter"])

    def test_bad_authority_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authority.bin"
            path.write_bytes(b"test")
            with self.assertRaises(MODULE.VerificationError):
                MODULE.verify_record({"path": str(path), "bytes": 4, "sha256": "0" * 64})

    def test_supervisor_has_one_controller_path_and_no_retry_loop(self) -> None:
        result = MODULE.check_supervisor()
        self.assertEqual(len(result["sha256"]), 64)
        source = MODULE.SUPERVISOR.read_text(encoding="utf-8")
        self.assertEqual(source.count("run $AssetId"), 1)
        self.assertNotIn("Start-Process", source)


if __name__ == "__main__":
    unittest.main()
