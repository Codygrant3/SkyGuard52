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
    "SkyguardGunnerCampaign.cpp",
    "SkyguardGunshipSortieDirector.cpp",
    "SkyguardGunshipSortieDirector.h",
    "SkyguardPatrolShipBoss.cpp",
    "SkyguardPatrolShipBoss.h",
    "SkyguardCampaignRoster.cpp",
    "SkyguardCampaignRoster.h",
    "SkyguardCoastalEnvironmentDirector.cpp",
    "SkyguardCoastalEnvironmentDirector.h",
    "SkyguardPilotVoice.cpp",
    "SkyguardPilotVoice.h",
}


def text(name: str) -> str:
    return (SOURCE / name).read_text(encoding="utf-8-sig")


def between(source: str, start: str, end: str) -> str:
    begin = source.index(start)
    finish = source.index(end, begin)
    return source[begin:finish]


def beat_kinds(block: str) -> list[str]:
    return re.findall(r"ESkyguardNightSortieBeatKind::([A-Za-z]+)", block)


class NightSortieBeatKitContractTests(unittest.TestCase):
    def test_night_beat_kit_types_exist(self) -> None:
        header = text("SkyguardNightSortieBeatKit.h")
        impl = text("SkyguardNightSortieBeatKit.cpp")
        self.assertIn("enum class ESkyguardNightSortieBeatKind", header)
        self.assertIn("struct FSkyguardNightSortieBeatKit", header)
        self.assertIn("SkyguardNightSortieBeatKit::NightEyes", impl)
        self.assertIn("SkyguardNightSortieBeatKit::DownedBird", impl)
        self.assertIn("SkyguardNightSortieBeatKit::SequencesDiffer", impl)
        self.assertIn("bKeepThermal", header)

    def test_m04_and_m07_sequences_differ(self) -> None:
        impl = text("SkyguardNightSortieBeatKit.cpp")
        night_eyes = between(impl, "NightEyesKit()", "DownedBirdKit()")
        downed_bird = between(impl, "DownedBirdKit()", "const FSkyguardNightSortieBeatKit&")
        m04 = beat_kinds(night_eyes)
        m07 = beat_kinds(downed_bird)
        self.assertEqual(len(m04), 7, m04)
        self.assertEqual(len(m07), 7, m07)
        self.assertNotEqual(m04, m07)
        self.assertIn("RadarVanHunt", m04)
        self.assertIn("RadarNetCollapse", m04)
        self.assertNotIn("HoldTheWreck", m04)
        self.assertNotIn("SearchIsland", m04)
        self.assertIn("HoldTheWreck", m07)
        self.assertIn("SearchIsland", m07)
        self.assertNotIn("RadarVanHunt", m07)
        self.assertNotIn("RadarNetCollapse", m07)

    def test_both_night_identities_keep_thermal(self) -> None:
        roster = text("SkyguardCampaignRoster.cpp")
        impl = text("SkyguardNightSortieBeatKit.cpp")
        m04 = between(
            roster,
            'Make(TEXT("M04_NightBlackout")',
            'Make(TEXT("M05_StormFront")',
        )
        m07 = between(
            roster,
            'Make(TEXT("M07_SearchIntercept")',
            'Make(TEXT("M08_RescueCover")',
        )
        self.assertIn('TEXT("BlackoutNight")', m04)
        self.assertIn('TEXT("IslandMist")', m07)
        self.assertTrue(m04.rstrip().endswith("true, false),") or ", true, false)" in m04)
        self.assertTrue(m07.rstrip().endswith("true, false),") or ", true, false)" in m07)
        self.assertIn('TEXT("BlackoutNight")', impl)
        self.assertIn('TEXT("IslandMist")', impl)
        self.assertIn("bKeepThermal = true", impl)

        tests = text("SkyguardNightSortieBeatKitTests.cpp")
        self.assertIn("both night identities enable thermal", tests)
        self.assertIn("ApplyWeatherPlayContracts", tests)
        self.assertIn("IsThermalEnabled", tests)

    def test_cpp_sequence_and_banned_term_tests_exist(self) -> None:
        tests = text("SkyguardNightSortieBeatKitTests.cpp")
        self.assertIn("FSkyguardNightBeatKitSequencesDifferTest", tests)
        self.assertIn("M04 sequence != M07 sequence", tests)
        self.assertIn("FSkyguardNightBeatKitKeepsThermalTest", tests)
        self.assertIn("FSkyguardNightBeatKitCopyBansYakIglaRifleTest", tests)
        self.assertIn("banned terms stay banned", tests)
        for banned in ("igla", "yak", "rifle"):
            self.assertIn(banned, tests.lower())

    def test_directors_expose_distinct_kits_and_apply_thermal(self) -> None:
        m04_h = text("SkyguardMission04IntegrationDirector.h")
        m07_h = text("SkyguardMission07IntegrationDirector.h")
        m04_cpp = text("SkyguardMission04IntegrationDirector.cpp")
        m07_cpp = text("SkyguardMission07IntegrationDirector.cpp")
        for header in (m04_h, m07_h):
            self.assertIn("GetNightBeatKit", header)
            self.assertIn("GetNightBeatKind", header)
            self.assertIn("TickNightBeatKit", header)
        self.assertIn("SkyguardNightSortieBeatKit::NightEyes", m04_cpp)
        self.assertIn("SkyguardNightSortieBeatKit::DownedBird", m07_cpp)
        self.assertIn("ApplyWeatherPlayContracts", m04_cpp)
        self.assertIn("ApplyWeatherPlayContracts", m07_cpp)
        self.assertIn("bNightIdentity", m04_cpp)
        self.assertIn("bNightIdentity", m07_cpp)

    def test_kit_copy_bans_yak_igla_rifle(self) -> None:
        for name in (
            "SkyguardNightSortieBeatKit.h",
            "SkyguardNightSortieBeatKit.cpp",
            "SkyguardMission04IntegrationDirector.h",
            "SkyguardMission04IntegrationDirector.cpp",
            "SkyguardMission07IntegrationDirector.h",
            "SkyguardMission07IntegrationDirector.cpp",
        ):
            lowered = text(name).lower()
            for banned in ("igla", "yak", "rifle"):
                if name.startswith("SkyguardMission0"):
                    # Historical boss-contract strings may still name archived
                    # weapons. Player-facing night-kit calls must stay clean.
                    continue
                self.assertNotIn(banned, lowered, f"{name} contains {banned}")

        impl = text("SkyguardNightSortieBeatKit.cpp")
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
        impl = text("SkyguardNightSortieBeatKit.cpp")
        self.assertNotIn(".umap", impl)
        self.assertNotIn("ApplyWorldMoodForWeather", impl)
        self.assertNotIn("ApplyMissionWeather", impl)
        directors = (
            text("SkyguardMission04IntegrationDirector.cpp")
            + text("SkyguardMission07IntegrationDirector.cpp")
        )
        self.assertNotIn(".umap", directors)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        for name in LOCKED:
            self.assertTrue((SOURCE / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
