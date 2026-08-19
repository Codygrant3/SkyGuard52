from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
LOCKED = {
    "SkyguardApacheAircraft.cpp",
    "SkyguardApacheAircraft.h",
    "SkyguardCpgHud.cpp",
    "SkyguardCpgHud.h",
    "SkyguardCpgHudTests.cpp",
    "SkyguardCpgSightHud.cpp",
    "SkyguardCpgSightHud.h",
    "SkyguardGunner.cpp",
    "SkyguardGunner.h",
    "SkyguardGunnerCampaign.cpp",
    "SkyguardGunshipSortieDirector.cpp",
    "SkyguardGunshipSortieDirector.h",
    "SkyguardPatrolShipBoss.cpp",
    "SkyguardPatrolShipBoss.h",
    "SkyguardCampaignRoster.cpp",
    "SkyguardCampaignRoster.h",
    "SkyguardNightSortieBeatKit.cpp",
    "SkyguardNightSortieBeatKit.h",
    "SkyguardDaySortieBeatKit.cpp",
    "SkyguardDaySortieBeatKit.h",
    "SkyguardMission04IntegrationDirector.cpp",
    "SkyguardMission04IntegrationDirector.h",
    "SkyguardMission07IntegrationDirector.cpp",
    "SkyguardMission07IntegrationDirector.h",
    "SkyguardMission05IntegrationDirector.cpp",
    "SkyguardMission05IntegrationDirector.h",
    "SkyguardMission08IntegrationDirector.cpp",
    "SkyguardMission08IntegrationDirector.h",
    "SkyguardCampaignTheaterKit.cpp",
    "SkyguardCampaignTheaterKit.h",
    "SkyguardCampaignTheaterKitTests.cpp",
    "SkyguardRadarNode.cpp",
    "SkyguardRadarNode.h",
    "SkyguardGuidedLockRules.cpp",
    "SkyguardGuidedLockRules.h",
    "SkyguardProtectAsset.cpp",
    "SkyguardProtectAsset.h",
    "SkyguardHarborProofTests.cpp",
}
HARBOR_CLOCK = "120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f"


def text(name: str) -> str:
    return (SOURCE / name).read_text(encoding="utf-8-sig")


def between(source: str, start: str, end: str) -> str:
    begin = source.index(start)
    finish = source.index(end, begin)
    return source[begin:finish]


def beat_kinds(block: str) -> list[str]:
    return re.findall(r"ESkyguardStormRainBeatKind::([A-Za-z]+)", block)


class StormRainBeatKitContractTests(unittest.TestCase):
    def test_storm_rain_beat_kit_types_exist(self) -> None:
        header = text("SkyguardStormRainBeatKit.h")
        impl = text("SkyguardStormRainBeatKit.cpp")
        self.assertIn("enum class ESkyguardStormRainBeatKind", header)
        self.assertIn("struct FSkyguardStormRainBeatKit", header)
        self.assertIn("SkyguardStormRainBeatKits::RiverHammer", impl)
        self.assertIn("SkyguardStormRainBeatKits::IronRain", impl)
        self.assertIn("bool bHydraForClusters", header)
        self.assertIn("KeepsHydraForClusters", header)
        self.assertIn("ApplyHydraForClusters", header)

    def test_m05_and_m08_seven_kind_sequences_differ(self) -> None:
        impl = text("SkyguardStormRainBeatKit.cpp")
        river = between(impl, "MakeRiverHammer()", "MakeIronRain()")
        rain = between(impl, "MakeIronRain()", "const FSkyguardStormRainBeatKit&")
        m05 = beat_kinds(river)
        m08 = beat_kinds(rain)
        self.assertEqual(len(m05), 7, m05)
        self.assertEqual(len(m08), 7, m08)
        self.assertNotEqual(m05, m08)
        self.assertEqual(
            m05,
            [
                "Approach",
                "WaterwayBoats",
                "BargeClusters",
                "LightningWindow",
                "ProtectWaterway",
                "Tempest",
                "Extract",
            ],
        )
        self.assertEqual(
            m08,
            [
                "Approach",
                "GunLine",
                "KillBattery",
                "BarrageCover",
                "RescueCorridor",
                "IronRain",
                "Extract",
            ],
        )
        self.assertIn("WaterwayBoats", m05)
        self.assertIn("Tempest", m05)
        self.assertNotIn("KillBattery", m05)
        self.assertNotIn("IronRain", m05)
        self.assertIn("KillBattery", m08)
        self.assertIn("IronRain", m08)
        self.assertNotIn("WaterwayBoats", m08)
        self.assertNotIn("Tempest", m08)

    def test_cpp_sequence_hydra_and_banned_term_tests_exist(self) -> None:
        tests = text("SkyguardStormRainBeatKitTests.cpp")
        self.assertIn("FSkyguardStormRainBeatSequencesDifferTest", tests)
        self.assertIn("M05 sequence is not M08 sequence", tests)
        self.assertIn("FSkyguardStormRainKeepsHydraContractTest", tests)
        self.assertIn("FSkyguardStormRainBannedCopyAndHarborClockTest", tests)
        self.assertIn("M05 copy bans Igla/Yak/rifle", tests)
        self.assertIn("M08 copy bans Igla/Yak/rifle", tests)
        for banned in ("igla", "yak", "rifle"):
            self.assertIn(banned, tests.lower())

    def test_directors_expose_get_storm_rain_beat_kit(self) -> None:
        m05_h = text("SkyguardMission05IntegrationDirector.h")
        m08_h = text("SkyguardMission08IntegrationDirector.h")
        m05_cpp = text("SkyguardMission05IntegrationDirector.cpp")
        m08_cpp = text("SkyguardMission08IntegrationDirector.cpp")
        for header in (m05_h, m08_h):
            self.assertIn("GetStormRainBeatKit", header)
            self.assertIn("ApplyStormRainPlayContract", header)
        self.assertIn("SkyguardStormRainBeatKits::RiverHammer", m05_cpp)
        self.assertIn("SkyguardStormRainBeatKits::IronRain", m08_cpp)

    def test_hydra_for_clusters_stays_true_for_storm_and_rain(self) -> None:
        header = text("SkyguardStormRainBeatKit.h")
        impl = text("SkyguardStormRainBeatKit.cpp")
        tests = text("SkyguardStormRainBeatKitTests.cpp")
        self.assertIn("bHydraForClusters = true", header + impl)
        self.assertGreaterEqual(impl.count("bHydraForClusters = true"), 2)
        self.assertIn("ESkyguardMissionWeather::Storm", impl)
        self.assertIn("ESkyguardMissionWeather::Rain", impl)
        self.assertIn("Weather == ESkyguardMissionWeather::Storm", impl)
        self.assertIn("Weather == ESkyguardMissionWeather::Rain", impl)
        self.assertIn("ApplyWeatherPlayContracts(false, true)", impl)
        self.assertIn("ESkyguardGunshipWeapon::Rockets", tests)
        self.assertIn("ESkyguardLoadout::RocketHeavy", tests)
        self.assertIn("M05 keeps Hydra for clusters", tests)
        self.assertIn("M08 rain keeps Hydra for clusters", tests)

    def test_kit_copy_bans_yak_igla_rifle(self) -> None:
        for name in (
            "SkyguardStormRainBeatKit.h",
            "SkyguardStormRainBeatKit.cpp",
        ):
            lowered = text(name).lower()
            for banned in ("igla", "yak", "rifle"):
                self.assertNotIn(banned, lowered, f"{name} contains {banned}")

        impl = text("SkyguardStormRainBeatKit.cpp")
        calls = re.findall(r'TEXT\("([^"]+)"\)', impl)
        for call in calls:
            lowered = call.lower()
            for banned in ("igla", "yak", "rifle"):
                self.assertNotIn(banned, lowered, call)

    def test_harbor_breaker_beats_stay_fifteen_minutes(self) -> None:
        roster = text("SkyguardCampaignRoster.cpp")
        harbor = between(
            roster,
            'Make(TEXT("M02_HarborShield")',
            'Make(TEXT("M03_ConvoyEscort")',
        )
        self.assertIn(HARBOR_CLOCK, harbor)
        self.assertNotIn("40.f, 80.f", harbor)
        tests = text("SkyguardStormRainBeatKitTests.cpp")
        self.assertIn("120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f", tests)

    def test_weather_identities_stay_severe_squall_and_rescue_sunset(self) -> None:
        impl = text("SkyguardStormRainBeatKit.cpp")
        self.assertIn('TEXT("SevereSquall")', impl)
        self.assertIn('TEXT("RescueSunset")', impl)
        roster = text("SkyguardCampaignRoster.cpp")
        m05 = between(
            roster,
            'Make(TEXT("M05_StormFront")',
            'Make(TEXT("M06_AirfieldDefense")',
        )
        m08 = between(
            roster,
            'Make(TEXT("M08_RescueCover")',
            'Make(TEXT("M09_SaturationAttack")',
        )
        self.assertIn('TEXT("SevereSquall")', m05)
        self.assertIn('TEXT("RescueSunset")', m08)
        self.assertNotIn("ApplyMissionWeather", impl)
        self.assertNotIn("ApplyWorldMoodForWeather", impl)

    def test_beat_index_for_elapsed_when_present(self) -> None:
        header = text("SkyguardStormRainBeatKit.h")
        impl = text("SkyguardStormRainBeatKit.cpp")
        if "BeatIndexForElapsed" not in header:
            self.skipTest(
                "BeatIndexForElapsed is not on this tree; C++ edit is out of scope"
            )
        self.assertIn(
            "int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);",
            header,
        )
        self.assertIn("SkyguardStormRainBeatKits::BeatIndexForElapsed", impl)
        m05_cpp = text("SkyguardMission05IntegrationDirector.cpp")
        m08_cpp = text("SkyguardMission08IntegrationDirector.cpp")
        m05_h = text("SkyguardMission05IntegrationDirector.h")
        m08_h = text("SkyguardMission08IntegrationDirector.h")
        for header_text in (m05_h, m08_h):
            self.assertIn("GetStormRainBeatKind", header_text)
            self.assertIn("TickStormRainBeatKit", header_text)
        self.assertIn("SkyguardStormRainBeatKits::BeatIndexForElapsed", m05_cpp)
        self.assertIn("SkyguardStormRainBeatKits::BeatIndexForElapsed", m08_cpp)
        tests = text("SkyguardStormRainBeatKitTests.cpp")
        self.assertIn(
            "FSkyguardStormRainBeatKitDirectorsDriveDistinctClocksTest", tests
        )
        self.assertIn("M05 vs M08 clocks differ at the same elapsed time", tests)

    def test_clocks_diverge_after_thirty_seconds(self) -> None:
        impl = text("SkyguardStormRainBeatKit.cpp")
        roster = text("SkyguardCampaignRoster.cpp")
        river = beat_kinds(between(impl, "MakeRiverHammer()", "MakeIronRain()"))
        rain = beat_kinds(
            between(impl, "MakeIronRain()", "const FSkyguardStormRainBeatKit&")
        )

        def first_threshold(mission_make: str, next_make: str) -> float:
            block = between(roster, mission_make, next_make)
            for line in block.splitlines():
                floats = re.findall(r"(\d+\.?\d*)f", line)
                if len(floats) == 7:
                    return float(floats[0])
            self.fail(f"no seven-beat clock in {mission_make}")
            return 0.0

        m05_t0 = first_threshold(
            'Make(TEXT("M05_StormFront")',
            'Make(TEXT("M06_AirfieldDefense")',
        )
        m08_t0 = first_threshold(
            'Make(TEXT("M08_RescueCover")',
            'Make(TEXT("M09_SaturationAttack")',
        )
        self.assertLess(m05_t0, 30.0)
        self.assertLess(m08_t0, 30.0)
        self.assertNotEqual(m05_t0, m08_t0)
        self.assertEqual(river[1], "WaterwayBoats")
        self.assertEqual(rain[1], "GunLine")
        self.assertNotEqual(river[1], rain[1])

    def test_no_unique_umap_or_weather_rebuild(self) -> None:
        impl = text("SkyguardStormRainBeatKit.cpp")
        self.assertNotIn(".umap", impl)
        self.assertNotIn("ApplyWorldMoodForWeather", impl)
        self.assertNotIn("ApplyMissionWeather", impl)
        directors = (
            text("SkyguardMission05IntegrationDirector.cpp")
            + text("SkyguardMission08IntegrationDirector.cpp")
        )
        self.assertNotIn(".umap", directors)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        existing.append("Config/DefaultInput.ini")
        sight_glass = ROOT / "Scripts" / "tests" / "test_cpg_sight_glass_projection_contract.py"
        if sight_glass.exists():
            existing.append(
                "Scripts/tests/test_cpg_sight_glass_projection_contract.py"
            )
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", *existing],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
