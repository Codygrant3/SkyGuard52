from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY03_CONTRACT.json"
EXECUTION = ROOT / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_RECOVERY03_EXECUTION_CONTRACT.json"
AUDIT_PATH = ROOT / "Scripts/audit_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery03.py"
CAPTURE = ROOT / "Scripts/capture_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery03.py"
SELECTOR = ROOT / "Scripts/select_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery03.py"
SUPERVISOR = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery03.ps1"
EXECUTION_AUDITOR = ROOT / "Scripts/verify_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery03_execution.py"


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


AUDIT = load_module("attempt03_recovery03_audit", AUDIT_PATH)


class Recovery03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
        cls.execution = json.loads(EXECUTION.read_text(encoding="utf-8-sig"))
        cls.capture = CAPTURE.read_text(encoding="utf-8-sig")
        cls.selector = SELECTOR.read_text(encoding="utf-8-sig")
        cls.supervisor = SUPERVISOR.read_text(encoding="utf-8-sig")
        cls.auditor = EXECUTION_AUDITOR.read_text(encoding="utf-8-sig")

    def test_01_readiness(self) -> None:
        result = AUDIT.audit(write_report=False)
        self.assertEqual(
            result["gate"],
            "PASS_OFFLINE_READY_AWAITING_SEPARATE_RECOVERY03_AUTHORIZATION",
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

    def test_03_pilot_gates_sweep(self) -> None:
        self.assertTrue(self.contract["pilot"]["must_pass_before_full_sweep"])
        self.assertEqual(self.contract["pilot"]["capture_count"], 3)
        self.assertLess(
            self.capture.index("if not pilot_pass:"),
            self.capture.index("sweep_output.mkdir()"),
        )

    def test_04_one_persistent_capture_and_target(self) -> None:
        self.assertEqual(self.capture.count("BASE.make_capture_component("), 1)
        self.assertIn("always_persist_rendering_state", self.capture)
        self.assertIn("clear_render_target2d", self.capture)

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
        capture = self.contract["capture"]
        self.assertEqual(capture["full_sweep_capture_count"], 72)
        self.assertEqual(capture["total_exported_capture_count"], 75)
        self.assertEqual(len(capture["rig_candidates"]), 8)

    def test_07_selector_requires_pilot_and_global_rig(self) -> None:
        self.assertIn("PASS_RECOVERY03_PERSISTENT_PILOT_LIVE_FULL_SWEEP_ALLOWED", self.selector)
        self.assertIn("all_nine_hard_bounds_passed", self.selector)
        self.assertIn("shutil.copyfile", self.selector)

    def test_08_supervisor_explicit_single_process(self) -> None:
        self.assertIn("AuthorizeSingleRecovery03Run", self.supervisor)
        self.assertIn("ExpectedExecutionContractSha256", self.supervisor)
        self.assertEqual(self.supervisor.count("-FilePath $EditorExe"), 1)
        self.assertIn("Stop-OwnedProcessTree", self.supervisor)
        self.assertIn("-d3d12", self.supervisor)
        self.assertIn("-sm6", self.supervisor)
        self.assertNotIn("-NullRHI", self.supervisor)

    def test_09_execution_audit_rejects_duplicate_sweep(self) -> None:
        self.assertIn("len(set(hashes)) == 72", self.auditor)
        self.assertIn("persistent_pilot_proved_live_rendering", self.auditor)

    def test_10_never_promotes(self) -> None:
        self.assertFalse(self.contract["promotion_allowed"])
        self.assertFalse(self.contract["p3_4_closed"])
        self.assertFalse(self.execution["promotion_allowed"])
        self.assertFalse(self.execution["p3_4_closed"])


if __name__ == "__main__":
    unittest.main()
