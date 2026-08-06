from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY06_NATIVE_EXECUTION_CONTRACT.json"
)
AUDIT_PATH = ROOT / (
    "Scripts/"
    "audit_m01_hero_grouped_topology_unreal_mapped_attempt03_"
    "recovery06_native_execution.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


AUDIT = load_module("recovery06_native_execution_audit", AUDIT_PATH)


class Recovery06NativeExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            CONTRACT_PATH.read_text(encoding="utf-8-sig")
        )
        cls.bound = cls.contract["bound_files"]

    def test_01_readiness_gate(self) -> None:
        result = AUDIT.audit(write_report=False)
        self.assertEqual(
            result["gate"],
            "PASS_RECOVERY06_NATIVE_EXECUTION_READY_"
            "AWAITING_EXPLICIT_SINGLE_RUN_AUTHORIZATION",
        )
        self.assertEqual(result["failure_count"], 0)

    def test_02_activation_and_dll_bound(self) -> None:
        self.assertEqual(
            self.bound["compile_activation"]["sha256"],
            "cdf500aa142f0ace326305c65226d7bc6c05de44e97576d5c26437b4d44e20b8",
        )
        self.assertEqual(
            self.bound["compiled_module"]["sha256"],
            "160706b823b79ff22b1631f87ca768f75f998956ba9fc508ad49c19ada665bbd",
        )

    def test_03_all_bound_files_exact(self) -> None:
        self.assertTrue(all(AUDIT.exact(r) for r in self.bound.values()))

    def test_04_source_inventory_unchanged(self) -> None:
        inventory = json.loads(
            AUDIT.resolve(self.bound["source_inventory"]["path"]).read_text(
                encoding="utf-8-sig"
            )
        )
        self.assertEqual(inventory["files"], AUDIT.current_source_inventory())

    def test_05_exact_native_contract_id(self) -> None:
        self.assertEqual(
            self.contract["native_runtime"]["required_contract_id"],
            "M01-HERO-GROUPED-TOPOLOGY-ATTEMPT03-RECOVERY05",
        )

    def test_06_explicit_authorization_required(self) -> None:
        auth = self.contract["authorization"]
        self.assertTrue(auth["explicit_authorization_required"])
        self.assertEqual(
            auth["authorize_switch"],
            "AuthorizeSingleRecovery06NativeRun",
        )
        self.assertTrue(auth["expected_contract_hash_must_be_supplied"])

    def test_07_new_namespace_absent(self) -> None:
        self.assertFalse(
            (ROOT / self.contract["outputs"]["attempt_root"]).exists()
        )

    def test_08_build_passed_but_launch_did_not(self) -> None:
        self.assertTrue(self.contract["native_build_executed"])
        self.assertEqual(
            self.contract["native_build_gate"],
            "PASS_FULL_SKYGUARD52EDITOR_MODULE_COMPILE",
        )
        self.assertFalse(self.contract["unreal_launch_authorized"])
        self.assertFalse(self.contract["unreal_launched"])

    def test_09_failed_attempts_preserved(self) -> None:
        self.assertTrue(
            self.contract["immutability"]["all_failed_attempts_preserved"]
        )
        self.assertFalse(
            self.contract["immutability"][
                "overwrite_or_retry_in_same_namespace"
            ]
        )

    def test_10_never_promotes(self) -> None:
        self.assertEqual(
            self.contract["content_packages_created_or_modified"], 0
        )
        self.assertFalse(self.contract["promotion_allowed"])
        self.assertFalse(self.contract["p3_4_closed"])


if __name__ == "__main__":
    unittest.main()
