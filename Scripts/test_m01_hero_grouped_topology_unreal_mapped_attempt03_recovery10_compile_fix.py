"""Focused offline tests for Recovery10 compile compatibility."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AUDIT_PATH = ROOT / (
    "Scripts/"
    "audit_m01_hero_grouped_topology_unreal_mapped_attempt03_"
    "recovery10_compile_fix.py"
)
CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY10_COMPILE_FIX_CONTRACT.json"
)

SPEC = importlib.util.spec_from_file_location("recovery10_audit", AUDIT_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class Recovery10CompileFixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
        cls.report = AUDIT.audit(write_report=False)
        correction = cls.contract["recovery10_correction"]
        cls.bridge = AUDIT.resolve(
            correction["forced_include_header"]["path"]
        ).read_text(encoding="utf-8-sig")
        cls.rules = AUDIT.resolve(correction["module_rules"]["path"]).read_text(
            encoding="utf-8-sig"
        )

    def test_01_all_readiness_checks_pass(self) -> None:
        self.assertEqual(self.report["failure_count"], 0)
        self.assertEqual(self.report["pass_count"], self.report["check_count"])

    def test_02_failed_receipt_and_log_are_exact(self) -> None:
        failed = self.contract["failed_build_evidence"]
        self.assertTrue(AUDIT.exact(failed["compile_receipt"]))
        self.assertTrue(AUDIT.exact(failed["build_stdout"]))

    def test_03_all_recovery09_artifacts_are_frozen(self) -> None:
        frozen = self.contract["frozen_recovery09"]
        for record in frozen.values():
            if isinstance(record, dict) and "path" in record:
                self.assertTrue(AUDIT.exact(record))

    def test_04_bridge_rewrites_only_two_member_declarations(self) -> None:
        self.assertEqual(self.bridge.count("#define BuildRecord(...)"), 1)
        self.assertEqual(self.bridge.count("#define WritePng(...)"), 1)
        self.assertEqual(self.bridge.count("const TArray<FColor>& Colors"), 2)

    def test_05_member_macros_end_after_header_include(self) -> None:
        include = self.bridge.index(
            "SkyguardM01GroupedTopologyRecovery09Capture.h"
        )
        self.assertGreater(self.bridge.index("#undef WritePng"), include)
        self.assertGreater(self.bridge.index("#undef BuildRecord"), include)

    def test_06_feature_proxy_targets_line_380(self) -> None:
        self.assertEqual(
            self.bridge.count(
                "TSkyguardRecovery08FeatureLevelAtLine<380>"
            ),
            1,
        )

    def test_07_no_lex_to_string_macro_or_suppression(self) -> None:
        self.assertNotIn("#define LexToString", self.bridge)
        self.assertNotIn("PRAGMA_DISABLE", self.bridge)

    def test_08_force_include_order_is_exact(self) -> None:
        self.assertLess(
            self.rules.index("Recovery06CompileFix.h"),
            self.rules.index("Recovery08CompileFix.h"),
        )
        self.assertLess(
            self.rules.index("Recovery08CompileFix.h"),
            self.rules.index("Recovery10CompileFix.h"),
        )

    def test_09_line_380_has_one_project_owner(self) -> None:
        sites = AUDIT.line_sites(
            ROOT / "Source", 380, "GMaxRHIFeatureLevel"
        )
        relative = [Path(path).relative_to(ROOT).as_posix() for path in sites]
        self.assertEqual(
            relative,
            [
                "Source/Skyguard52/"
                "SkyguardM01GroupedTopologyRecovery09Capture.cpp"
            ],
        )

    def test_10_no_build_launch_or_promotion_is_claimed(self) -> None:
        self.assertFalse(self.contract["native_build_executed"])
        self.assertFalse(self.contract["unreal_launched"])
        self.assertFalse(self.contract["blender_launched"])
        self.assertFalse(self.contract["promotion_allowed"])
        self.assertFalse(self.contract["p3_4_closed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
