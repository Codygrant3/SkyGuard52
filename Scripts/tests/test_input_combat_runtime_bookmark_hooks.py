from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "Scripts" / "skyguard_input_combat_performance_contract_v1.json"
CAPTURE = ROOT / "Source" / "Skyguard52" / "SkyguardInputCombatPerformanceCapture.cpp"
MISSILE = ROOT / "Source" / "Skyguard52" / "SkyguardIglaMissile.cpp"
BOSS = ROOT / "Source" / "Skyguard52" / "SkyguardBossDroneBase.cpp"


class InputCombatRuntimeBookmarkHooksTests(unittest.TestCase):
    def test_all_fifteen_contract_literals_exist_in_runtime_source(self):
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        source = CAPTURE.read_text(encoding="utf-8")
        literals = [
            window[field]
            for window in contract["required_windows"]
            for field in ("region", "begin_bookmark", "end_bookmark")
        ]
        self.assertEqual(len(literals), 15)
        for literal in literals:
            self.assertIn(literal, source)

    def test_regions_use_id_based_trace_pairing_and_bookmarks(self):
        source = CAPTURE.read_text(encoding="utf-8")
        self.assertIn("TRACE_BEGIN_REGION_WITH_ID", source)
        self.assertIn("TRACE_END_REGION_WITH_ID", source)
        self.assertIn("TRACE_BOOKMARK", source)
        self.assertIn("EndAllTraceWindows", source)

    def test_igla_impact_and_boss_weakpoint_lifecycle_hooks_exist(self):
        self.assertIn(
            'TEXT("igla_impact")',
            MISSILE.read_text(encoding="utf-8"),
        )
        self.assertIn(
            'TEXT("boss_weak_point_destroyed")',
            BOSS.read_text(encoding="utf-8"),
        )
        capture = CAPTURE.read_text(encoding="utf-8")
        for event in (
            "ads_ended",
            "drone_breakup_cleanup",
            "boss_destruction_cleanup",
            "weather_visibility_transition_complete",
        ):
            self.assertIn(f'TEXT("{event}")', capture)

    def test_windows_are_bounded_to_contract_maximum(self):
        source = CAPTURE.read_text(encoding="utf-8")
        self.assertIn("FMath::Clamp(MaximumDuration, 1.0, 30.0)", source)
        self.assertIn("Window.MaximumEndSeconds", source)


if __name__ == "__main__":
    unittest.main()
