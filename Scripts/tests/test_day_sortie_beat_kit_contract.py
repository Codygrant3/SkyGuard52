from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
LOCKED = {
    "SkyguardApacheAircraft.cpp",
    "SkyguardApacheAircraft.h",
    "SkyguardCpgHud.cpp",
    "SkyguardCpgHud.h",
    "SkyguardGunner.cpp",
    "SkyguardGunner.h",
    "SkyguardGunshipSortieDirector.cpp",
    "SkyguardGunshipSortieDirector.h",
    "SkyguardPatrolShipBoss.cpp",
    "SkyguardPatrolShipBoss.h",
    "SkyguardCampaignRoster.cpp",
    "SkyguardCampaignRoster.h",
    "SkyguardNightSortieBeatKit.cpp",
    "SkyguardNightSortieBeatKit.h",
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
}


def text(name: str) -> str:
    return (SOURCE / name).read_text(encoding="utf-8-sig")


def between(source: str, start: str, end: str) -> str:
    begin = source.index(start)
    finish = source.index(end, begin)
    return source[begin:finish]


def beat_kinds(block: str) -> list[str]:
    return re.findall(r"ESkyguardDaySortieBeatKind::([A-Za-z]+)", block)


class DaySortieBeatKitContractTests(unittest.TestCase):
    def test_day_beat_kit_types_exist(self) -> None:
        header = text("SkyguardDaySortieBeatKit.h")
        impl = text("SkyguardDaySortieBeatKit.cpp")
        self.assertIn("enum class ESkyguardDaySortieBeatKind", header)
        self.assertIn("struct FSkyguardDaySortieBeatKit", header)
        self.assertIn("SkyguardDaySortieBeatKit::BrokenHighway", impl)
        self.assertIn("SkyguardDaySortieBeatKit::DustOffensive", impl)
        self.assertIn("SkyguardDaySortieBeatKit::HunterKiller", impl)
        self.assertIn("SkyguardDaySortieBeatKit::SequencesDiffer", impl)

    def test_three_sequences_are_pairwise_unequal(self) -> None:
        impl = text("SkyguardDaySortieBeatKit.cpp")
        highway = between(impl, "BrokenHighwayKit()", "DustOffensiveKit()")
        airfield = between(impl, "DustOffensiveKit()", "HunterKillerKit()")
        metro = between(impl, "HunterKillerKit()", "const FSkyguardDaySortieBeatKit&")
        m03 = beat_kinds(highway)
        m06 = beat_kinds(airfield)
        m09 = beat_kinds(metro)
        self.assertEqual(len(m03), 7, m03)
        self.assertEqual(len(m06), 7, m06)
        self.assertEqual(len(m09), 7, m09)
        self.assertNotEqual(m03, m06)
        self.assertNotEqual(m03, m09)
        self.assertNotEqual(m06, m09)
        self.assertIn("RidgeIngress", m03)
        self.assertIn("TankAmbush", m03)
        self.assertIn("HazeIngress", m06)
        self.assertIn("AdaSuppress", m06)
        self.assertIn("DuskIngress", m09)
        self.assertIn("TelStrike", m09)
        self.assertNotIn("AdaSuppress", m03)
        self.assertNotIn("TelStrike", m03)
        self.assertNotIn("TankAmbush", m06)
        self.assertNotIn("TelStrike", m06)
        self.assertNotIn("TankAmbush", m09)
        self.assertNotIn("AdaSuppress", m09)

    def test_cpp_sequence_and_banned_term_tests_exist(self) -> None:
        tests = text("SkyguardDaySortieBeatKitTests.cpp")
        self.assertIn("FSkyguardDayBeatKitSequencesDifferTest", tests)
        self.assertIn("M03 sequence != M06 sequence", tests)
        self.assertIn("M03 sequence != M09 sequence", tests)
        self.assertIn("M06 sequence != M09 sequence", tests)
        self.assertIn("FSkyguardDayBeatKitCopyBansYakIglaRifleTest", tests)
        self.assertIn("banned terms stay banned", tests)
        for banned in ("igla", "yak", "rifle"):
            self.assertIn(banned, tests.lower())

    def test_directors_expose_distinct_kits(self) -> None:
        m03_h = text("SkyguardMission03IntegrationDirector.h")
        m06_h = text("SkyguardMission06IntegrationDirector.h")
        m09_h = text("SkyguardMission09IntegrationDirector.h")
        m03_cpp = text("SkyguardMission03IntegrationDirector.cpp")
        m06_cpp = text("SkyguardMission06IntegrationDirector.cpp")
        m09_cpp = text("SkyguardMission09IntegrationDirector.cpp")
        for header in (m03_h, m06_h, m09_h):
            self.assertIn("GetDayBeatKit", header)
            self.assertIn("GetDayBeatKind", header)
            self.assertIn("TickDayBeatKit", header)
        self.assertIn("SkyguardDaySortieBeatKit::BrokenHighway", m03_cpp)
        self.assertIn("SkyguardDaySortieBeatKit::DustOffensive", m06_cpp)
        self.assertIn("SkyguardDaySortieBeatKit::HunterKiller", m09_cpp)

    def test_kit_copy_bans_yak_igla_rifle(self) -> None:
        for name in (
            "SkyguardDaySortieBeatKit.h",
            "SkyguardDaySortieBeatKit.cpp",
        ):
            lowered = text(name).lower()
            for banned in ("igla", "yak", "rifle"):
                self.assertNotIn(banned, lowered, f"{name} contains {banned}")

        impl = text("SkyguardDaySortieBeatKit.cpp")
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
        self.assertIn("120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f", harbor)

    def test_no_unique_umap_or_weather_rebuild(self) -> None:
        impl = text("SkyguardDaySortieBeatKit.cpp")
        self.assertNotIn(".umap", impl)
        self.assertNotIn("ApplyWorldMoodForWeather", impl)
        self.assertNotIn("ApplyMissionWeather", impl)
        directors = (
            text("SkyguardMission03IntegrationDirector.cpp")
            + text("SkyguardMission06IntegrationDirector.cpp")
            + text("SkyguardMission09IntegrationDirector.cpp")
        )
        self.assertNotIn(".umap", directors)

    def test_clocks_diverge_after_thirty_seconds(self) -> None:
        impl = text("SkyguardDaySortieBeatKit.cpp")
        roster = text("SkyguardCampaignRoster.cpp")
        highway = beat_kinds(between(impl, "BrokenHighwayKit()", "DustOffensiveKit()"))
        airfield = beat_kinds(between(impl, "DustOffensiveKit()", "HunterKillerKit()"))
        metro = beat_kinds(between(impl, "HunterKillerKit()", "const FSkyguardDaySortieBeatKit&"))

        def first_threshold(mission_make: str, next_make: str) -> float:
            block = between(roster, mission_make, next_make)
            for line in block.splitlines():
                floats = re.findall(r"(\d+\.?\d*)f", line)
                if len(floats) == 7:
                    return float(floats[0])
            self.fail(f"no seven-beat clock in {mission_make}")
            return 0.0

        m03_t0 = first_threshold(
            'Make(TEXT("M03_ConvoyEscort")',
            'Make(TEXT("M04_NightBlackout")',
        )
        m06_t0 = first_threshold(
            'Make(TEXT("M06_AirfieldDefense")',
            'Make(TEXT("M07_SearchIntercept")',
        )
        m09_t0 = first_threshold(
            'Make(TEXT("M09_SaturationAttack")',
            'Make(TEXT("M10_EvacuationFinale")',
        )
        self.assertLess(m03_t0, 30.0)
        self.assertLess(m06_t0, 30.0)
        self.assertLess(m09_t0, 30.0)
        self.assertNotEqual(highway[1], airfield[1])
        self.assertNotEqual(highway[1], metro[1])
        self.assertNotEqual(airfield[1], metro[1])
        self.assertEqual(highway[1], "TechnicalScreen")
        self.assertEqual(airfield[1], "FenceSweep")
        self.assertEqual(metro[1], "SensorTrack")

    def test_weather_identities_stay_on_existing_profiles(self) -> None:
        impl = text("SkyguardDaySortieBeatKit.cpp")
        self.assertIn('TEXT("DryMorning")', impl)
        self.assertIn('TEXT("AirfieldHaze")', impl)
        self.assertIn('TEXT("CityDusk")', impl)
        roster = text("SkyguardCampaignRoster.cpp")
        self.assertIn('TEXT("DryMorning")', roster)
        self.assertIn('TEXT("AirfieldHaze")', roster)
        self.assertIn('TEXT("CityDusk")', roster)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        import subprocess

        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        existing.append("Config/DefaultInput.ini")
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
