"""Focused offline tests for the Recovery07/08 execution contract."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AUDIT_PATH = ROOT / (
    "Scripts/"
    "audit_m01_hero_grouped_topology_unreal_mapped_attempt03_"
    "recovery07_runtime_recovery08_execution.py"
)
CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY07_EXECUTION_CONTRACT.json"
)

SPEC = importlib.util.spec_from_file_location("recovery0708_audit", AUDIT_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class Recovery0708ExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
        cls.report = AUDIT.audit(write_report=False)
        cls.bound = cls.contract["bound_files"]

    def test_01_all_readiness_checks_pass(self) -> None:
        self.assertEqual(self.report["failure_count"], 0)
        self.assertEqual(self.report["pass_count"], self.report["check_count"])

    def test_02_every_bound_file_is_exact(self) -> None:
        self.assertTrue(
            all(AUDIT.exact(record) for record in self.bound.values())
        )

    def test_03_receipt_is_successful_full_module_build(self) -> None:
        receipt = json.loads(
            AUDIT.resolve(self.bound["compile_receipt"]["path"]).read_text(
                encoding="utf-8-sig"
            )
        )
        self.assertEqual(
            receipt["gate"], "PASS_FULL_SKYGUARD52EDITOR_MODULE_COMPILE"
        )
        self.assertEqual(receipt["build_exit_code"], 0)
        self.assertFalse(receipt["timed_out"])

    def test_04_dll_is_exact_and_matches_receipt(self) -> None:
        receipt = json.loads(
            AUDIT.resolve(self.bound["compile_receipt"]["path"]).read_text(
                encoding="utf-8-sig"
            )
        )
        self.assertTrue(AUDIT.exact(self.bound["compiled_module"]))
        self.assertEqual(
            receipt["compiled_module_sha256"],
            self.bound["compiled_module"]["sha256"],
        )

    def test_05_inventory_contains_recovery08_bridge(self) -> None:
        inventory = json.loads(
            AUDIT.resolve(self.bound["source_inventory"]["path"]).read_text(
                encoding="utf-8-sig"
            )
        )
        records = AUDIT.inventory_records(inventory)
        bridge = self.bound["recovery08_compile_bridge"]
        record = records[
            "Source/Skyguard52/"
            "SkyguardM01GroupedTopologyRecovery08CompileFix.h"
        ]
        self.assertEqual(record["sha256"], bridge["sha256"])

    def test_06_generic_contract_id_mismatch_is_disclosed(self) -> None:
        disclosure = self.contract[
            "generic_supervisor_contract_id_disclosure"
        ]
        self.assertFalse(disclosure["exact_match"])
        self.assertFalse(
            disclosure["violates_recovery08_execution_contract"]
        )
        self.assertFalse(disclosure["fail_closed_due_to_mismatch"])

    def test_07_wrapper_hash_is_exact(self) -> None:
        self.assertTrue(AUDIT.exact(self.bound["powershell_supervisor"]))
        self.assertEqual(
            self.bound["powershell_supervisor"]["sha256"],
            "993500b976d552056cc02f8a8238a17a1ac15755fac5b66db8305d9c78d32aa7",
        )

    def test_08_output_namespace_is_absent(self) -> None:
        outputs = self.contract["outputs"]
        self.assertFalse(AUDIT.resolve(outputs["attempt_root"]).exists())
        self.assertFalse(AUDIT.resolve(outputs["capture_root"]).exists())
        self.assertFalse(AUDIT.resolve(outputs["supervisor_receipt"]).exists())

    def test_09_launch_remains_unauthorized(self) -> None:
        self.assertFalse(self.contract["unreal_launch_authorized"])
        self.assertFalse(self.contract["unreal_launched"])
        self.assertFalse(self.contract["blender_launched"])

    def test_10_no_promotion_or_phase_closure(self) -> None:
        self.assertFalse(self.contract["promotion_allowed"])
        self.assertFalse(self.contract["p3_4_closed"])
        self.assertEqual(
            self.contract["content_packages_created_or_modified"], 0
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
