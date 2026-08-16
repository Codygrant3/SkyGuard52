from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"

BANNED = ("igla", "yak", "rifle")
HARBOR_BEATS = ("120.f", "240.f", "360.f", "480.f", "600.f", "780.f", "900.f")

M05_KINDS = (
    "Approach",
    "WaterwayBoats",
    "BargeClusters",
    "LightningWindow",
    "ProtectWaterway",
    "Tempest",
    "Extract",
)
M08_KINDS = (
    "Approach",
    "GunLine",
    "KillBattery",
    "BarrageCover",
    "RescueCorridor",
    "IronRain",
    "Extract",
)


def text(name: str) -> str:
    return (SOURCE / name).read_text(encoding="utf-8-sig")


def kinds_block(source: str, marker: str) -> list[str]:
    match = re.search(
        rf"{re.escape(marker)}[\s\S]*?Kinds(?:\s*\[\s*\d*\s*\])?\s*=\s*\{{([^}}]+)\}}",
        source,
    )
    if not match:
        raise AssertionError(f"missing Kinds array after {marker}")
    return [part.strip() for part in match.group(1).split(",") if part.strip()]


def player_copy(source: str) -> str:
    return "\n".join(re.findall(r'TEXT\("([^"]+)"\)', source))


class StormRainBeatKitContractTests(unittest.TestCase):
    def test_helper_files_exist(self) -> None:
        for name in (
            "SkyguardStormRainBeatKit.h",
            "SkyguardStormRainBeatKit.cpp",
            "SkyguardStormRainBeatKitTests.cpp",
        ):
            self.assertTrue((SOURCE / name).is_file(), name)

    def test_m05_and_m08_sequences_differ(self) -> None:
        source = text("SkyguardStormRainBeatKit.cpp")
        river = kinds_block(source, "MakeRiverHammer")
        rain = kinds_block(source, "MakeIronRain")
        self.assertEqual(river, [f"ESkyguardStormRainBeatKind::{kind}" for kind in M05_KINDS])
        self.assertEqual(rain, [f"ESkyguardStormRainBeatKind::{kind}" for kind in M08_KINDS])
        self.assertNotEqual(river, rain)

    def test_m05_is_clear_waterway_tempest(self) -> None:
        source = text("SkyguardStormRainBeatKit.cpp")
        river = kinds_block(source, "MakeRiverHammer")
        self.assertIn("ESkyguardStormRainBeatKind::WaterwayBoats", river)
        self.assertIn("ESkyguardStormRainBeatKind::Tempest", river)
        self.assertNotIn("ESkyguardStormRainBeatKind::KillBattery", river)
        self.assertNotIn("ESkyguardStormRainBeatKind::IronRain", river)

    def test_m08_is_kill_battery_iron_rain(self) -> None:
        source = text("SkyguardStormRainBeatKit.cpp")
        rain = kinds_block(source, "MakeIronRain")
        self.assertIn("ESkyguardStormRainBeatKind::KillBattery", rain)
        self.assertIn("ESkyguardStormRainBeatKind::IronRain", rain)
        self.assertNotIn("ESkyguardStormRainBeatKind::WaterwayBoats", rain)
        self.assertNotIn("ESkyguardStormRainBeatKind::Tempest", rain)

    def test_storm_and_rain_keep_hydra_for_clusters(self) -> None:
        header = text("SkyguardStormRainBeatKit.h")
        source = text("SkyguardStormRainBeatKit.cpp")
        tests = text("SkyguardStormRainBeatKitTests.cpp")
        self.assertIn("bHydraForClusters", header)
        self.assertIn("ApplyHydraForClusters", header)
        self.assertIn("KeepsHydraForClusters", header)
        self.assertIn("ESkyguardMissionWeather::Storm", source)
        self.assertIn("ESkyguardMissionWeather::Rain", source)
        self.assertIn("ApplyWeatherPlayContracts(false, true)", source)
        self.assertIn("ESkyguardGunshipWeapon::Rockets", tests)
        self.assertIn("ESkyguardLoadout::RocketHeavy", tests)

    def test_player_facing_copy_bans_yak_igla_rifle(self) -> None:
        source = text("SkyguardStormRainBeatKit.cpp")
        copy = player_copy(source).lower()
        for term in BANNED:
            self.assertNotIn(term, copy, term)

    def test_directors_expose_kits(self) -> None:
        m05 = text("SkyguardMission05IntegrationDirector.h")
        m08 = text("SkyguardMission08IntegrationDirector.h")
        self.assertIn("GetStormRainBeatKit", m05)
        self.assertIn("GetStormRainBeatKit", m08)
        self.assertIn("ApplyStormRainPlayContract", m05)
        self.assertIn("ApplyStormRainPlayContract", m08)

    def test_harbor_breaker_clock_untouched(self) -> None:
        roster = text("SkyguardCampaignRoster.cpp")
        harbor = roster[roster.index("M02_HarborShield") : roster.index("M03_ConvoyEscort")]
        for beat in HARBOR_BEATS:
            self.assertIn(beat, harbor)
        tests = text("SkyguardStormRainBeatKitTests.cpp")
        for beat in HARBOR_BEATS:
            self.assertIn(beat, tests)

    def test_weather_identities_stay_roster_owned(self) -> None:
        source = text("SkyguardStormRainBeatKit.cpp")
        self.assertIn("SevereSquall", source)
        self.assertIn("RescueSunset", source)
        self.assertNotIn("ApplyMissionWeather", source)


if __name__ == "__main__":
    unittest.main()
