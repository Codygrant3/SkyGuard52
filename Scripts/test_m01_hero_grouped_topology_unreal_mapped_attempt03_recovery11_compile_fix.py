"""Focused offline tests for the immutable Recovery11 compile bridge."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(r"D:\Skyguard52\Scripts\audit_m01_hero_grouped_topology_unreal_mapped_attempt03_recovery11_compile_fix.py")
SPEC = importlib.util.spec_from_file_location("recovery11_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class Recovery11CompileFixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.audit(write_report=False)
        cls.bridge = Path(
            r"D:\Skyguard52\Source\Skyguard52\SkyguardM01GroupedTopologyRecovery11CompileFix.h"
        ).read_text(encoding="utf-8-sig")

    def test_offline_gate_passes(self) -> None:
        self.assertEqual(self.result["gate"], "PASS_RECOVERY11_COMPILE_READY_NOT_RUN")

    def test_all_checks_pass(self) -> None:
        self.assertTrue(all(item["passed"] for item in self.result["checks"]))

    def test_exactly_two_owned_copy_calls(self) -> None:
        self.assertEqual(self.bridge.count("SkyguardRecovery11::OwnColors(Colors)"), 2)

    def test_no_recovery12_or_retry(self) -> None:
        contract = MODULE.json.loads(MODULE.CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(contract["execution"]["maximum_attempts"], 1)
        self.assertTrue(contract["execution"]["automatic_retry_forbidden"])
        self.assertIn("do not create Recovery12", contract["acceptance"]["if_compile_fails"])


if __name__ == "__main__":
    unittest.main()
