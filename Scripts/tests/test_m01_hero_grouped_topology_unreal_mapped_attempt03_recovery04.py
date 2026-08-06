from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY04_CONTRACT.json"
EXECUTION = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY04_EXECUTION_CONTRACT.json"
AUDIT_PATH = ROOT / "Scripts/audit_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery04.py"
CAPTURE = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery04.py"
SUPERVISOR = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery04.ps1"
EXECUTION_AUDITOR = ROOT / "Scripts/verify_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery04_execution.py"


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


AUDIT = load_module("attempt03_recovery04_audit", AUDIT_PATH)


class Recovery04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
        cls.execution = json.loads(EXECUTION.read_text(encoding="utf-8-sig"))
        cls.capture = CAPTURE.read_text(encoding="utf-8-sig")
        cls.supervisor = SUPERVISOR.read_text(encoding="utf-8-sig")
        cls.auditor = EXECUTION_AUDITOR.read_text(encoding="utf-8-sig")

    def test_01_readiness(self) -> None:
        result = AUDIT.audit(write_report=False)
        self.assertEqual(
            result["gate"],
            "PASS_OFFLINE_READY_AWAITING_SEPARATE_RECOVERY04_AUTHORIZATION",
        )
        self.assertEqual(result["failure_count"], 0)

    def test_02_hash_binding(self) -> None:
        for record in self.contract["bound_evidence"].values():
            path = ROOT / record["path"]
            self.assertEqual(path.stat().st_size, record["bytes"])
            self.assertEqual(sha256_file(path), record["sha256"])
        for name, record in self.execution["bound_files"].items():
            if name == "readiness_auditor":
                continue
            path = ROOT / record["path"]
            self.assertEqual(path.stat().st_size, record["bytes"])
            self.assertEqual(sha256_file(path), record["sha256"])

    def test_03_exact_base_lighting_lifecycle(self) -> None:
        self.assertEqual(self.capture.count("BASE.spawn_lighting(base_contract)"), 1)
        self.assertNotIn("mark_render_state_dirty", self.capture)
        self.assertNotIn("recapture_sky", self.capture)

    def test_04_more_negative_pilot_gates_full_views(self) -> None:
        self.assertEqual(
            self.contract["pilot"]["exposure_candidates_ev"],
            [-14, -18, -22, -26, -30, -34],
        )
        self.assertIn("require_exposure_readback", self.capture)
        self.assertLess(
            self.capture.index("if selected is None:"),
            self.capture.index("full_output.mkdir()"),
        )

    def test_05_read_only_content(self) -> None:
        for forbidden in (
            "new_level",
            "save_current_level",
            "save_loaded_asset",
            "import_asset_tasks",
            "rename_asset",
            "delete_asset",
        ):
            self.assertNotIn(forbidden, self.capture)

    def test_06_exact_capture_counts(self) -> None:
        self.assertEqual(self.contract["pilot"]["capture_count"], 6)
        self.assertEqual(self.contract["full_views"]["capture_count"], 9)
        self.assertEqual(self.contract["capture"]["total_exported_capture_count"], 15)

    def test_07_execution_audit_requires_unique_hard_bound_views(self) -> None:
        self.assertIn("len(set(hashes)) == 9", self.auditor)
        self.assertIn("hard_bounds_passed", self.auditor)

    def test_08_supervisor_explicit_single_process(self) -> None:
        self.assertIn("AuthorizeSingleRecovery04Run", self.supervisor)
        self.assertIn("ExpectedExecutionContractSha256", self.supervisor)
        self.assertEqual(self.supervisor.count("-FilePath $EditorExe"), 1)
        self.assertIn("Stop-OwnedProcessTree", self.supervisor)
        self.assertIn("-d3d12", self.supervisor)
        self.assertIn("-sm6", self.supervisor)
        self.assertNotIn("-NullRHI", self.supervisor)

    def test_09_pilot_uses_unchanged_hard_bounds(self) -> None:
        hard = self.contract["pilot"]["exposure_hard_bounds"]
        self.assertEqual(hard["maximum_active_clipped_fraction_luma_ge_250"], 0.02)
        self.assertEqual(hard["active_p95_range"], [100, 248])
        self.assertEqual(hard["minimum_active_dynamic_range_p95_minus_p05"], 35)

    def test_10_never_promotes(self) -> None:
        self.assertFalse(self.contract["promotion_allowed"])
        self.assertFalse(self.contract["p3_4_closed"])
        self.assertFalse(self.execution["promotion_allowed"])
        self.assertFalse(self.execution["p3_4_closed"])


if __name__ == "__main__":
    unittest.main()
