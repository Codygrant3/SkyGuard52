from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(r"D:\Skyguard52\Scripts\verify_p0_core_rifle_method05_deterministic_stagea_offline.py")
SPEC = importlib.util.spec_from_file_location("rifle_method05_stagea_verify", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RifleMethod05DeterministicStageAOfflineTests(unittest.TestCase):
    def test_full_offline_verification(self) -> None:
        result = MODULE.verify()
        self.assertEqual(result["classification"], "PASS")
        self.assertEqual(result["heavy_process_count"], 0)
        self.assertTrue(result["future_namespaces_absent"])

    def test_pure_cage_is_closed_oriented_and_compact(self) -> None:
        worker = MODULE.load_worker_module()
        result = MODULE.check_pure_topology(worker)
        self.assertEqual(result["non_manifold_edges"], 0)
        self.assertEqual(result["orientation_errors"], 0)
        self.assertEqual(result["loose_vertices"], 0)
        self.assertGreater(result["void_cells"], 0)
        self.assertLess(result["estimated_python_geometry_bytes"], 16 * 1024 * 1024)

    def test_accepted_rail_dimensions_are_exact(self) -> None:
        result = MODULE.check_rail_authority()
        self.assertEqual(result["dimensions"], MODULE.EXPECTED_RAIL)
        worker = MODULE.load_worker_module()
        self.assertEqual(worker.RAIL_TOP_WIDTH_M, MODULE.EXPECTED_RAIL["top_width"])
        self.assertEqual(worker.RAIL_PITCH_M, MODULE.EXPECTED_RAIL["pitch"])

    def test_render_and_visual_review_contracts(self) -> None:
        worker = MODULE.load_worker_module()
        result = MODULE.check_contracts(worker)
        self.assertEqual(result["checkpoint_views"], 15)
        self.assertEqual(result["final_views"], 12)
        rubric = MODULE.load_json(MODULE.RUBRIC)
        self.assertTrue(rubric["automatic_pass_is_not_visual_acceptance"])

    def test_bad_authority_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authority.bin"
            path.write_bytes(b"method05")
            record = {"path": str(path), "bytes": path.stat().st_size, "sha256": "0" * 64}
            with self.assertRaises(MODULE.VerificationError):
                MODULE.verify_record(record)

    def test_worker_supervisor_and_manifest_are_bounded(self) -> None:
        authority = MODULE.load_json(MODULE.AUTHORITY)
        worker = MODULE.check_worker()
        supervisor = MODULE.check_supervisor()
        manifest = MODULE.check_manifest(authority)
        self.assertFalse(worker["numpy_usage"])
        self.assertEqual(supervisor["controller_run_paths"], 1)
        self.assertEqual(manifest["status"], "ready")
        self.assertEqual(manifest["legacy_status"], "failed")


if __name__ == "__main__":
    unittest.main()
