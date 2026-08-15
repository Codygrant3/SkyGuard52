from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
WORKER = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery04\build_m01_visible_environment_kit_refinement01_stagea_recovery04.py"
SUPERVISOR = ROOT / r"Scripts\ToolchainWave08\environment_visual_remediation01\stagea_recovery04\invoke_m01_visible_environment_kit_refinement01_stagea_recovery04_once.ps1"
FUTURE = (
    ROOT / r"Saved\BuildAttempts\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY04\attempt_01",
    ROOT / r"Content\Skyguard\Meshes\Source\Mission01\VisibleEnvironmentKit_Refinement01_StageA_Recovery04",
    ROOT / r"Saved\Reports\M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY04_TERMINAL_SUPERVISOR.json",
)


def load_worker():
    spec = importlib.util.spec_from_file_location("stagea_recovery04_test_worker", WORKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SUPERVISOR), *args],
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )


class Recovery04OfflineTests(unittest.TestCase):
    def test_worker_rebuilds_thirteen_functions(self) -> None:
        module = load_worker()
        corrected, receipt = module.load_recovery04_source()
        self.assertEqual(receipt["function_replacement_count"], 13)
        self.assertIn('GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY04"', corrected)

    def test_failed_geometry_and_markers_are_not_reused(self) -> None:
        corrected, receipt = load_worker().load_recovery04_source()
        self.assertFalse(receipt["failed_output_geometry_reused"])
        self.assertNotIn("VisibleEnvironmentKit_Refinement01_StageA_Recovery03", corrected)
        self.assertNotIn("SM_M01_STAGEA_DuneGrass_", corrected)

    def test_luminance_guards_are_not_relaxed(self) -> None:
        corrected, receipt = load_worker().load_recovery04_source()
        self.assertFalse(receipt["threshold_relaxation"])
        self.assertIn('0.008 if condition == "night" else 0.025', corrected)
        self.assertIn('0.70 if condition == "night" else 0.42', corrected)

    def test_preliminary_conditions_and_final_cardinality(self) -> None:
        corrected, receipt = load_worker().load_recovery04_source()
        self.assertEqual(receipt["preliminary_conditions"], ["daylight", "overcast", "night"])
        self.assertIn('require(len(results) == 15, "Final render count is not exactly fifteen")', corrected)

    def test_offline_contract_mode_writes_only_temporary_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skyguard_stagea_recovery04_offline_") as temporary:
            result = invoke("-OfflineContractTest", "-OfflineEvidenceRoot", temporary)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = Path(temporary) / "terminal_manifest.json"
            self.assertTrue(manifest.is_file())
            data = json.loads(manifest.read_text(encoding="utf-8-sig"))
            self.assertEqual(data["classification"], "PASS")
            self.assertEqual(data["blender_launch_count"], 0)
            self.assertEqual(data["retry_count"], 0)

    def test_authorization_refusal_exit_code(self) -> None:
        result = invoke()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_conflicting_modes_exit_code(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skyguard_stagea_recovery04_conflict_") as temporary:
            result = invoke("-AuthorizeSingleBlender", "-OfflineContractTest", "-OfflineEvidenceRoot", temporary)
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
            data = json.loads((Path(temporary) / "terminal_manifest.json").read_text(encoding="utf-8-sig"))
            self.assertEqual(data["blender_launch_count"], 0)

    def test_future_namespaces_remain_absent(self) -> None:
        for path in FUTURE:
            self.assertFalse(path.exists(), str(path))


if __name__ == "__main__":
    unittest.main(verbosity=2)
