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
    "SkyguardPatrolShipBoss.cpp",
    "SkyguardPatrolShipBoss.h",
    "SkyguardCpgDebrief.cpp",
    "SkyguardCpgDebrief.h",
    "SkyguardSortiePresentationComponent.cpp",
    "SkyguardSortiePresentationComponent.h",
    "SkyguardSortiePresentationWidgets.cpp",
    "SkyguardSortiePresentationWidgets.h",
}


def text(name: str) -> str:
    return (SOURCE / name).read_text(encoding="utf-8-sig")


def between(source: str, start: str, end: str) -> str:
    begin = source.index(start)
    finish = source.index(end, begin)
    return source[begin:finish]


class CampaignTheaterKitContractTests(unittest.TestCase):
    def test_theater_kit_types_and_apply_exist(self) -> None:
        header = text("SkyguardCampaignTheaterKit.h")
        impl = text("SkyguardCampaignTheaterKit.cpp")
        self.assertIn("struct FSkyguardTheaterKitSpec", header)
        self.assertIn("class SKYGUARD52_API ASkyguardCampaignTheaterKit", header)
        self.assertIn("void ApplyTheaterKit(FName WeatherIdentity)", header)
        self.assertIn("static void ApplyTheaterKitToWorld", header)
        self.assertIn("GetNamedLandmark", header)
        self.assertIn("RoadInstances", header)
        self.assertIn("BuildingInstances", header)
        self.assertIn("LampInstances", header)
        self.assertIn("SilhouetteInstances", header)
        self.assertIn("NamedLandmarkMesh", header)
        self.assertIn("SkyguardCampaignTheaterKit::Resolve", impl)
        self.assertIn("SkyguardCampaignTheaterKit::AreKitsPairwiseDistinct", impl)

    def test_ten_kits_key_off_roster_weather_identities(self) -> None:
        roster = text("SkyguardCampaignRoster.cpp")
        kit = text("SkyguardCampaignTheaterKit.cpp")
        identities = [
            "ClearNoon",
            "HarborOvercast",
            "DryMorning",
            "BlackoutNight",
            "SevereSquall",
            "AirfieldHaze",
            "IslandMist",
            "RescueSunset",
            "CityDusk",
            "EvacuationDawn",
        ]
        for identity in identities:
            self.assertIn(f'TEXT("{identity}")', roster)
            self.assertIn(f'TEXT("{identity}")', kit)
            self.assertIn(f"Kit.{identity}.", kit)

    def test_kit_ids_and_named_landmarks_are_unique(self) -> None:
        kit = text("SkyguardCampaignTheaterKit.cpp")
        table = between(kit, "const FSkyguardTheaterKitSpec GKits[]", "const FName BuildingTag")
        kit_ids = re.findall(r'TEXT\("Kit\.[A-Za-z]+\.[A-Za-z]+"\)', table)
        landmarks = re.findall(
            r'TEXT\("(WatchPier|BreakwaterLight|RidgeOverpass|DarkGridTower|'
            r'RiverSpan|ControlTower|WreckBeacon|BatteryHouse|TelYardStack|'
            r'FortressKeep)"\)',
            table,
        )
        self.assertEqual(len(kit_ids), 10, kit_ids)
        self.assertEqual(len(set(kit_ids)), 10, kit_ids)
        self.assertEqual(len(landmarks), 10, landmarks)
        self.assertEqual(len(set(landmarks)), 10, landmarks)

    def test_sortie_start_calls_apply_theater_kit(self) -> None:
        director = text("SkyguardGunshipSortieDirector.cpp")
        start = between(
            director,
            "void ASkyguardGunshipSortieDirector::StartMissionIndex",
            "void ASkyguardGunshipSortieDirector::StartNextMission",
        )
        mood = start.index("ApplyWorldMoodForWeather")
        coast = start.index("ApplyMissionWeather")
        theater = start.index("ApplyTheaterKitToWorld")
        identity = start.index("Spec.WeatherIdentity")
        self.assertLess(mood, theater)
        self.assertLess(coast, theater)
        self.assertLess(theater, identity + 1)
        self.assertIn("Spec.WeatherIdentity", start[theater:])

    def test_harbor_breaker_beats_stay_fifteen_minutes(self) -> None:
        roster = text("SkyguardCampaignRoster.cpp")
        harbor = between(
            roster,
            'Make(TEXT("M02_HarborShield")',
            'Make(TEXT("M03_ConvoyEscort")',
        )
        self.assertIn("120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f", harbor)
        self.assertIn('TEXT("HarborOvercast")', harbor)

    def test_theater_copy_bans_yak_igla_rifle(self) -> None:
        for name in (
            "SkyguardCampaignTheaterKit.h",
            "SkyguardCampaignTheaterKit.cpp",
        ):
            lowered = text(name).lower()
            for banned in ("igla", "yak", "rifle"):
                self.assertNotIn(banned, lowered, f"{name} contains {banned}")

    def test_cpp_uniqueness_test_exists(self) -> None:
        tests = text("SkyguardCampaignTheaterKitTests.cpp")
        self.assertIn("FSkyguardTheaterKitsAreUniquePerMissionTest", tests)
        self.assertIn("two missions cannot apply the same kit", tests)
        self.assertIn("harbor swaps the named landmark", tests)
        self.assertIn("FSkyguardSortieDirectorAppliesTheaterKitTest", tests)
        self.assertIn("FSkyguardTheaterKitKeepsHarborBreakerClockTest", tests)

    def test_no_unique_umap_or_art_import(self) -> None:
        impl = text("SkyguardCampaignTheaterKit.cpp")
        self.assertNotIn("/Game/Skyguard/Meshes", impl)
        self.assertNotIn(".umap", impl)
        self.assertIn("/Engine/BasicShapes/", impl)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        for name in LOCKED:
            self.assertTrue((SOURCE / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
