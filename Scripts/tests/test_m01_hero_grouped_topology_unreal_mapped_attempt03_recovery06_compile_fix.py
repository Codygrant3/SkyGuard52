from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
CONTRACT = ROOT / (
    "Docs/AAA_Review/"
    "M01_HERO_GROUPED_TOPOLOGY_UNREAL_MAPPED_ATTEMPT03_"
    "RECOVERY06_COMPILE_FIX_CONTRACT.json"
)
AUDIT_PATH = ROOT / (
    "Scripts/"
    "audit_m01_hero_grouped_topology_unreal_mapped_attempt03_"
    "recovery06_compile_fix.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


AUDIT = load_module("recovery06_compile_bridge_audit", AUDIT_PATH)


class Recovery06CompileBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
        cls.frozen = (
            ROOT / cls.contract["frozen_recovery05_source"]["path"]
        ).read_text(encoding="utf-8-sig")
        bridge = cls.contract["recovery06_compile_bridge"]
        cls.header = (
            ROOT / bridge["forced_include_header"]["path"]
        ).read_text(encoding="utf-8-sig")
        cls.helper = (
            ROOT / bridge["runtime_cast_source"]["path"]
        ).read_text(encoding="utf-8-sig")
        cls.rules = (
            ROOT / bridge["module_rules_file"]["path"]
        ).read_text(encoding="utf-8-sig")

    def test_01_readiness(self) -> None:
        result = AUDIT.audit(write_report=False)
        self.assertEqual(
            result["gate"],
            "PASS_OFFLINE_RECOVERY06_COMPILE_BRIDGE_READY_"
            "AWAITING_SEPARATE_BUILD_AUTHORIZATION",
        )
        self.assertEqual(result["failure_count"], 0)

    def test_02_recovery05_is_frozen(self) -> None:
        record = self.contract["frozen_recovery05_source"]
        self.assertTrue(AUDIT.exact(record))
        self.assertEqual(
            record["sha256"],
            "4c2438dff632f69e3606703f3a4ff8ddd0401ff104f00df1fe7f24e2cc408d81",
        )
        self.assertTrue(record["direct_edit_forbidden"])

    def test_03_failure_surface_preserved(self) -> None:
        self.assertEqual(
            self.frozen.count("GetDirectionalLightComponent()"), 1
        )
        self.assertNotIn(
            '#include "Components/SkyLightComponent.h"', self.frozen
        )

    def test_04_sky_component_header_forced(self) -> None:
        self.assertIn(
            '#include "Components/SkyLightComponent.h"', self.header
        )
        self.assertIn("ForceIncludeFiles.Add(Path.Combine(", self.rules)

    def test_05_directional_runtime_cast(self) -> None:
        self.assertIn("Cast<UDirectionalLightComponent>(", self.helper)
        self.assertIn(
            "Light ? Light->GetLightComponent() : nullptr", self.helper
        )
        self.assertNotIn("Light->GetComponent()", self.helper)

    def test_06_typed_null_guard(self) -> None:
        self.assertIn("checkf(", self.helper)
        self.assertIn("return Component;", self.helper)

    def test_07_macro_bridge_is_single_site(self) -> None:
        self.assertEqual(
            self.header.count("#define GetDirectionalLightComponent()"), 1
        )
        self.assertEqual(
            self.header.count(
                "SkyguardRecovery06RequireDirectionalLight(Key)"
            ),
            1,
        )

    def test_08_failed_build_and_ue_evidence_bound(self) -> None:
        failed = self.contract["failed_build_evidence"]
        self.assertTrue(failed["phase4_recovery02_consumed_and_failed"])
        self.assertEqual(len(failed["compiler_errors"]), 2)
        self.assertEqual(len(self.contract["ue58_api_evidence"]), 6)

    def test_09_build_requires_new_authorization(self) -> None:
        future = self.contract["future_build"]
        self.assertTrue(future["requires_separate_authorization"])
        self.assertFalse(future["unreal_launch_allowed"])
        self.assertTrue(
            future["post_build_dll_hash_must_be_bound_before_execution"]
        )
        self.assertFalse(self.contract["native_build_executed"])

    def test_10_new_namespace_never_promotes(self) -> None:
        self.assertIn(
            "mapped_view_capture_03_recovery_06_native",
            self.contract["future_execution_output"],
        )
        self.assertFalse(self.contract["native_build_authorized"])
        self.assertFalse(self.contract["unreal_launch_authorized"])
        self.assertFalse(self.contract["promotion_allowed"])
        self.assertFalse(self.contract["p3_4_closed"])


if __name__ == "__main__":
    unittest.main()
