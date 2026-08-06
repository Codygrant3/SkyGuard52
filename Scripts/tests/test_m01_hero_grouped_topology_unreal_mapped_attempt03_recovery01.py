from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY01_CONTRACT.json"
EXECUTION_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY01_EXECUTION_CONTRACT.json"
BASE_CONTRACT_PATH = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_CONTRACT.json"
AUDIT_PATH = ROOT / "Scripts/audit_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery01.py"
CAPTURE_PATH = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery01.py"
SELECTOR_PATH = ROOT / "Scripts/select_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery01.py"
SUPERVISOR_PATH = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery01.ps1"
EXECUTION_AUDITOR_PATH = ROOT / "Scripts/verify_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery01_execution.py"


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


AUDIT = load_module("attempt03_recovery01_audit", AUDIT_PATH)


class Attempt03Recovery01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
        cls.execution = json.loads(
            EXECUTION_CONTRACT_PATH.read_text(encoding="utf-8-sig")
        )
        cls.base_contract = json.loads(
            BASE_CONTRACT_PATH.read_text(encoding="utf-8-sig")
        )
        cls.capture = CAPTURE_PATH.read_text(encoding="utf-8-sig")
        cls.selector = SELECTOR_PATH.read_text(encoding="utf-8-sig")
        cls.supervisor = SUPERVISOR_PATH.read_text(encoding="utf-8-sig")
        cls.execution_auditor = EXECUTION_AUDITOR_PATH.read_text(
            encoding="utf-8-sig"
        )

    def test_01_offline_readiness_passes(self) -> None:
        result = AUDIT.audit(write_report=False)
        self.assertEqual(
            result["gate"],
            "PASS_OFFLINE_READY_AWAITING_SEPARATE_RECOVERY01_AUTHORIZATION",
        )
        self.assertEqual(result["failure_count"], 0)

    def test_02_all_evidence_and_execution_files_are_hash_bound(self) -> None:
        for group in (
            self.contract["bound_evidence"],
            self.execution["bound_files"],
        ):
            for record in group.values():
                path = ROOT / record["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(path.stat().st_size, record["bytes"])
                self.assertEqual(sha256_file(path), record["sha256"])

    def test_03_eight_rigs_cover_bounded_physical_range(self) -> None:
        rigs = self.contract["capture"]["rig_candidates"]
        self.assertEqual(len(rigs), 8)
        self.assertEqual(
            [rig["key_lux"] for rig in rigs],
            [250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0, 16000.0, 32000.0],
        )
        self.assertEqual(self.contract["capture"]["capture_count"], 72)
        self.assertEqual(
            self.contract["capture"]["fixed_manual_exposure_bias_ev"], -12
        )

    def test_04_original_hard_bounds_are_not_relaxed(self) -> None:
        base = self.base_contract["exposure_sweep"]["selector"]
        recovery = self.contract["selector"]
        for key in (
            "active_pixel_threshold_luma",
            "maximum_active_clipped_fraction_luma_ge_250",
            "active_p50_range",
            "active_p95_range",
            "minimum_active_dynamic_range_p95_minus_p05",
            "canonical_capture_count",
        ):
            self.assertEqual(recovery[key], base[key])

    def test_05_capture_reuses_map_without_content_writes(self) -> None:
        self.assertIn('load_level(recovery["review_map"])', self.capture)
        for forbidden in (
            "new_level",
            "save_current_level",
            "save_loaded_asset",
            "import_asset_tasks",
            "rename_asset",
            "delete_asset",
        ):
            self.assertNotIn(forbidden, self.capture)

    def test_06_selector_requires_one_global_rig_for_all_nine_views(self) -> None:
        self.assertIn("all_nine_hard_bounds_passed", self.selector)
        self.assertIn("shutil.copyfile", self.selector)
        self.assertIn("rig_index", self.selector)
        self.assertIn(
            "FAIL_CLOSED_NO_GLOBAL_PHYSICAL_RIG_PASSED_ALL_NINE_HARD_BOUNDS",
            self.selector,
        )

    def test_07_supervisor_is_single_process_explicit_and_owned_cleanup(self) -> None:
        self.assertIn("AuthorizeSingleRecovery01Run", self.supervisor)
        self.assertIn("ExpectedExecutionContractSha256", self.supervisor)
        self.assertEqual(self.supervisor.count("-FilePath $EditorExe"), 1)
        self.assertIn("Stop-OwnedProcessTree", self.supervisor)
        self.assertNotIn("Stop-Process -Name", self.supervisor)
        self.assertIn("-d3d12", self.supervisor)
        self.assertIn("-sm6", self.supervisor)
        self.assertNotIn("-NullRHI", self.supervisor)

    def test_08_execution_auditor_covers_every_hash_domain(self) -> None:
        for marker in (
            "failed_evidence_and_review_map_still_bound",
            "original_candidate_hash_invariance",
            "attempt03_review_map_hash_invariance",
            "runtime_map_hash_invariance",
            "config_hash_invariance",
        ):
            self.assertIn(marker, self.execution_auditor)

    def test_09_recovery_outputs_are_new_and_immutable(self) -> None:
        output = ROOT / self.execution["outputs"]["attempt_root"]
        self.assertFalse(output.exists())
        self.assertIn("recovery_01", output.name)
        self.assertFalse(self.execution["immutability"]["overwrite_or_retry_in_same_namespace"])
        self.assertEqual(self.execution["immutability"]["new_content_package_count"], 0)

    def test_10_promotion_and_p3_4_remain_false(self) -> None:
        self.assertFalse(self.contract["promotion_allowed"])
        self.assertFalse(self.contract["p3_4_closed"])
        self.assertFalse(self.execution["promotion_allowed"])
        self.assertFalse(self.execution["p3_4_closed"])
        self.assertIn("promotion_allowed = $false", self.supervisor)
        self.assertIn("p3_4_closed = $false", self.supervisor)


if __name__ == "__main__":
    unittest.main()
