from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
EXECUTION_CONTRACT = (
    ROOT
    / "Docs/AAA_Review/M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_EXECUTION_CONTRACT.json"
)
SUPERVISOR = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_mapped_attempt03.ps1"
ENTRYPOINT = ROOT / "Scripts/run_m01_hero_grouped_topology_unreal_mapped_attempt03.py"
EXECUTION_AUDITOR = (
    ROOT / "Scripts/verify_m01_hero_grouped_topology_unreal_mapped_attempt03_execution.py"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Attempt03SupervisorTests(unittest.TestCase):
    def test_execution_contract_binds_every_execution_file(self) -> None:
        contract = json.loads(EXECUTION_CONTRACT.read_text(encoding="utf-8-sig"))
        for record in contract["bound_files"].values():
            path = ROOT / record["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(path.stat().st_size, record["bytes"])
            self.assertEqual(sha256_file(path), record["sha256"])

    def test_supervisor_requires_explicit_authorization_and_contract_hash(self) -> None:
        source = SUPERVISOR.read_text(encoding="utf-8-sig")
        self.assertIn("[switch]$AuthorizeSingleAttempt03Run", source)
        self.assertIn("[string]$ExpectedExecutionContractSha256", source)
        self.assertIn(
            "Execution contract hash mismatch; Unreal was not launched.", source
        )

    def test_supervisor_launches_exactly_one_unreal_process(self) -> None:
        source = SUPERVISOR.read_text(encoding="utf-8-sig")
        self.assertEqual(source.count("-FilePath $EditorExe"), 1)
        self.assertIn("exactly_one_unreal_process_launched = $true", source)
        self.assertIn("-d3d12", source)
        self.assertIn("-sm6", source)
        self.assertNotIn("-NullRHI", source)

    def test_unreal_entrypoint_builds_then_captures_sequentially(self) -> None:
        source = ENTRYPOINT.read_text(encoding="utf-8-sig")
        self.assertLess(source.index("builder.main()"), source.index("capture.main()"))
        self.assertIn(
            "PASS_ATTEMPT03_ONE_PROCESS_BUILD_AND_SWEEP_AWAITING_OFFLINE_SELECTION",
            source,
        )

    def test_supervisor_owns_timeout_cleanup_and_never_broad_kills(self) -> None:
        source = SUPERVISOR.read_text(encoding="utf-8-sig")
        self.assertIn("Get-DescendantProcessIds", source)
        self.assertIn("Stop-OwnedProcessTree", source)
        self.assertIn("Stop-Process -Id $RootProcessId", source)
        self.assertNotIn("Stop-Process -Name", source)

    def test_selector_and_auditor_run_only_after_unreal_stage(self) -> None:
        source = SUPERVISOR.read_text(encoding="utf-8-sig")
        self.assertGreater(
            source.index("$selectorArguments"), source.index("$unrealArguments")
        )
        self.assertGreater(
            source.index("$auditorArguments"), source.index("$selectorArguments")
        )

    def test_independent_auditor_checks_package_hash_invariance(self) -> None:
        source = EXECUTION_AUDITOR.read_text(encoding="utf-8-sig")
        for marker in (
            "original_candidate_hash_invariance",
            "runtime_map_hash_invariance",
            "config_hash_invariance",
            "one_new_attempt03_map_only",
            "d3d12_sm6_exact_63_sweep",
            "offline_global_ev_selection",
        ):
            self.assertIn(marker, source)

    def test_every_terminal_gate_remains_non_promotable(self) -> None:
        contract = json.loads(EXECUTION_CONTRACT.read_text(encoding="utf-8-sig"))
        self.assertFalse(contract["promotion_allowed"])
        self.assertFalse(contract["p3_4_closed"])
        source = SUPERVISOR.read_text(encoding="utf-8-sig")
        self.assertIn("promotion_allowed = $false", source)
        self.assertIn("p3_4_closed = $false", source)


if __name__ == "__main__":
    unittest.main()
