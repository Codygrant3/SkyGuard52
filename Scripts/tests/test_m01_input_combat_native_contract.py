from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"


def text(name: str) -> str:
    return (SOURCE / name).read_text(encoding="utf-8-sig")


class M01InputCombatNativeContractTests(unittest.TestCase):
    def test_capture_is_command_line_gated_and_writes_exact_schema(self) -> None:
        source = text("SkyguardInputCombatPerformanceCapture.cpp")
        for argument in (
            "SkyguardCombatPerfRunId=",
            "SkyguardCombatPerfKind=",
            "SkyguardCombatPerfDurationSeconds=",
            "SkyguardCombatPerfReceipt=",
            "SkyguardCombatPerfExpectedMap=",
        ):
            self.assertIn(argument, source)
        self.assertIn(
            "skyguard.m01.input-combat.runtime-receipt.v1", source
        )
        self.assertRegex(
            source,
            r"bCaptureRequested\s*=\s*!RunId\.IsEmpty\(\)",
        )

    def test_capture_observes_and_never_drives_combat(self) -> None:
        source = text("SkyguardInputCombatPerformanceCapture.cpp")
        forbidden = (
            "FireShot(",
            "FireIgla(",
            "ApplyWeaponHit(",
            "ApplyIglaStrike(",
            "SetBossPhase(",
        )
        for call in forbidden:
            self.assertNotIn(call, source)
        self.assertIn('GEngine->Exec(World, TEXT("csvprofile start"))', source)
        self.assertIn('GEngine->Exec(World, TEXT("csvprofile stop"))', source)

    def test_all_required_runtime_events_are_fail_closed(self) -> None:
        source = text("SkyguardInputCombatPerformanceCapture.cpp")
        for event in (
            "aim_input",
            "ads_started",
            "ads_left_fire_overlap",
            "rifle_shot",
            "weapon_switch",
            "igla_lock_acquired",
            "igla_launch",
            "drone_breakup",
            "boss_destroyed",
            "weather_visibility_transition",
        ):
            self.assertIn(f'TEXT("{event}")', source)
        self.assertIn("MinimumRepeatedRifleShots = 5", source)
        self.assertIn("HasRequiredEventCounts(Issues)", source)

    def test_input_bindings_use_telemetry_wrappers(self) -> None:
        source = text("SkyguardGunner.cpp")
        for wrapper in (
            "InputLookX",
            "InputLookY",
            "InputADSPressed",
            "InputADSReleased",
            "InputFirePressed",
            "InputFireReleased",
            "InputSwitchWeaponPressed",
            "InputLaunchIglaPressed",
        ):
            self.assertRegex(source, rf"Bind(?:Axis|Action)\([^;]+::{wrapper}\)")
        self.assertNotRegex(
            source,
            r"BindAction\([^;]+::(?:ADSPressed|FirePressed|SwitchWeaponPressed|LaunchIglaPressed)\)",
        )

    def test_rejected_forward_rifle_shot_is_not_recorded(self) -> None:
        source = text("SkyguardGunner.cpp")
        fire_start = source.index("void ASkyguardGunner::FireShot()")
        fire_end = source.index(
            "bool ASkyguardGunner::IsRifleDirectionOutsidePilotSafetyArc",
            fire_start,
        )
        fire = source[fire_start:fire_end]
        safety = fire.index("if (!IsRifleDirectionOutsidePilotSafetyArc())")
        telemetry = fire.index('TEXT("rifle_shot")')
        muzzle = fire.index("SpawnMuzzleFlash")
        self.assertLess(safety, telemetry)
        self.assertLess(telemetry, muzzle)

    def test_igla_launch_requires_spawned_missile(self) -> None:
        source = text("SkyguardGunner.cpp")
        start = source.index("void ASkyguardGunner::FireIgla()")
        end = source.index("void ASkyguardGunner::FireShot()", start)
        body = source[start:end]
        self.assertIn("bMissileSpawned = true", body)
        self.assertRegex(
            body,
            r"if \(bMissileSpawned &&\s*\(bIglaLaunchRequestedFromPlayerInput \|\| bFireHeldFromPlayerInput\)\)",
        )
        self.assertIn('TEXT("igla_launch")', body)

    def test_breakup_and_defeat_are_recorded_after_bounded_breakup(self) -> None:
        source = text("SkyguardBossDroneBase.cpp")
        start = source.index("void ASkyguardBossDroneBase::HandleDefeated()")
        body = source[start:]
        bounded = body.index(
            "FMath::Min(DefeatDebrisComponents.Num(), MaxDefeatDebrisPieces)"
        )
        breakup = body.index('TEXT("drone_breakup")')
        defeated = body.index('TEXT("boss_destroyed")')
        self.assertLess(bounded, breakup)
        self.assertLess(breakup, defeated)
        self.assertIn("if (DebrisCount > 0)", body)

    def test_visibility_event_follows_a_real_fog_density_change(self) -> None:
        source = text("SkyguardMission01EnvironmentDirector.cpp")
        start = source.index("void ASkyguardMission01EnvironmentDirector::Tick")
        body = source[start:]
        applied = body.index("Fog->SetFogDensity(HazeDensity)")
        event = body.index('TEXT("weather_visibility_transition")')
        restored = body.index("Fog->SetFogDensity(RuntimeBaseFogDensity)")
        self.assertLess(applied, event)
        self.assertLess(event, restored)
        self.assertIn("bEnableCoastalHazeTransition", body)


if __name__ == "__main__":
    unittest.main()
