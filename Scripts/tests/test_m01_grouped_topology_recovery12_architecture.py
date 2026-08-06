from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


AUDITOR = Path(r"D:\Skyguard52\Scripts\audit_m01_grouped_topology_recovery12_architecture.py")
SPEC = importlib.util.spec_from_file_location("recovery12_audit", AUDITOR)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class Recovery12ArchitectureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.audit(write_outputs=False)
        cls.contract = json.loads(MODULE.CONTRACT.read_text(encoding="utf-8"))

    def test_gate_passes(self) -> None:
        self.assertEqual(self.result["gate"], "PASS_RECOVERY12_ARCHITECTURE_READY_NOT_RUN")

    def test_all_checks_pass(self) -> None:
        self.assertTrue(all(item["passed"] for item in self.result["checks"]))

    def test_single_attempt_policy(self) -> None:
        self.assertEqual(self.contract["compile"]["maximum_attempts"], 1)
        self.assertFalse(self.contract["compile"]["automatic_retry"])
        self.assertEqual(self.contract["visual_proof"]["maximum_attempts"], 1)
        self.assertFalse(self.contract["visual_proof"]["automatic_retry"])

    def test_recovery13_is_forbidden(self) -> None:
        self.assertIn("do not retry or create Recovery13", self.contract["failure_policy"]["compile_failure"])

    def test_proof_is_compile_gated(self) -> None:
        self.assertTrue(self.contract["visual_proof"]["requires_compile_pass"])


if __name__ == "__main__":
    unittest.main()
