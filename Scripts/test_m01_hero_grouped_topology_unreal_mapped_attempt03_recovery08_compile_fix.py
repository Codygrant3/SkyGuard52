"""Focused offline tests for the Recovery08 compile-only correction."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
AUDIT_PATH = ROOT / (
    "Scripts/"
    "audit_m01_hero_grouped_topology_unreal_mapped_attempt03_"
    "recovery08_compile_fix.py"
)
CONTRACT_PATH = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY08_COMPILE_FIX_CONTRACT.json"
)

SPEC = importlib.util.spec_from_file_location("recovery08_audit", AUDIT_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class Recovery08CompileFixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8-sig"))
        cls.report = AUDIT.audit(write_report=False)
        correction = cls.contract["recovery08_correction"]
        cls.bridge = AUDIT.resolve(
            correction["forced_include_header"]["path"]
        ).read_text(encoding="utf-8-sig")
        cls.rules = AUDIT.resolve(correction["module_rules"]["path"]).read_text(
            encoding="utf-8-sig"
        )
        frozen = cls.contract["frozen_recovery07"]
        cls.frozen_source = AUDIT.resolve(frozen["source"]["path"]).read_text(
            encoding="utf-8-sig"
        )

    def test_01_all_readiness_checks_pass(self) -> None:
        self.assertEqual(self.report["failure_count"], 0)
        self.assertEqual(self.report["pass_count"], self.report["check_count"])

    def test_02_failure_receipt_and_stdout_are_exact(self) -> None:
        evidence = self.contract["failed_build_evidence"]
        self.assertTrue(AUDIT.exact(evidence["compile_receipt"]))
        self.assertTrue(AUDIT.exact(evidence["build_stdout"]))

    def test_03_recovery07_files_are_immutable(self) -> None:
        frozen = self.contract["frozen_recovery07"]
        self.assertTrue(AUDIT.exact(frozen["source"]))
        self.assertTrue(AUDIT.exact(frozen["header"]))

    def test_04_failure_expression_stays_unedited(self) -> None:
        line = self.frozen_source.splitlines()[348]
        self.assertIn("LexToString(GMaxRHIFeatureLevel)", line)
        self.assertNotIn("*LexToString(GMaxRHIFeatureLevel)", line)

    def test_05_bridge_has_one_target_specialization(self) -> None:
        self.assertEqual(
            self.bridge.count(
                "TSkyguardRecovery08FeatureLevelAtLine<349>"
            ),
            1,
        )

    def test_06_bridge_returns_const_tchar_for_target(self) -> None:
        self.assertIn(
            "FORCEINLINE const TCHAR* LexToString(",
            self.bridge,
        )
        self.assertIn(
            "FSkyguardRecovery08PrintfFeatureLevel Get()",
            self.bridge,
        )

    def test_07_default_bridge_path_returns_feature_enum(self) -> None:
        self.assertIn(
            "static ERHIFeatureLevel::Type Get()",
            self.bridge,
        )

    def test_08_target_line_has_one_project_owner(self) -> None:
        sites = AUDIT.project_sites_at_line(349, "GMaxRHIFeatureLevel")
        self.assertEqual(
            sites,
            [
                "Source/Skyguard52/"
                "SkyguardM01GroupedTopologyRecovery07Capture.cpp"
            ],
        )

    def test_09_force_include_order_is_preserved(self) -> None:
        recovery06 = self.rules.index(
            "SkyguardM01GroupedTopologyRecovery06CompileFix.h"
        )
        recovery08 = self.rules.index(
            "SkyguardM01GroupedTopologyRecovery08CompileFix.h"
        )
        self.assertLess(recovery06, recovery08)

    def test_10_no_build_launch_or_promotion_is_claimed(self) -> None:
        self.assertFalse(self.contract["native_build_executed"])
        self.assertFalse(self.contract["unreal_launched"])
        self.assertFalse(self.contract["blender_launched"])
        self.assertFalse(self.contract["promotion_allowed"])
        self.assertFalse(self.contract["p3_4_closed"])

    def test_11_installed_ue_headers_have_no_target_line_collision(self) -> None:
        sites = AUDIT.engine_header_sites_at_line(
            349, "GMaxRHIFeatureLevel"
        )
        self.assertEqual(sites, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
