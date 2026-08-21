from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardDaySortieBeatKit.h"
# Leftover #56–#64 plus DaySortieBeatKit production sources/tests.
# This lane only adds an isolated Python enum contract.
LOCKED = {
    "SkyguardDaySortieBeatKit.h",
    "SkyguardDaySortieBeatKit.cpp",
    "SkyguardDaySortieBeatKitTests.cpp",
    "SkyguardRadarNode.cpp",
    "SkyguardRadarNode.h",
    "SkyguardGuidedLockRules.cpp",
    "SkyguardGuidedLockRules.h",
    "SkyguardCpgHud.cpp",
    "SkyguardCpgHud.h",
    "SkyguardCpgHudTests.cpp",
    "SkyguardCpgSightHud.cpp",
    "SkyguardCpgSightHud.h",
    "SkyguardGunner.cpp",
    "SkyguardGunner.h",
    "SkyguardGunnerCampaign.cpp",
    "SkyguardProtectAsset.cpp",
    "SkyguardProtectAsset.h",
    "SkyguardHarborProofTests.cpp",
    "SkyguardCampaignTheaterKitTests.cpp",
}
# Isolated-test drafts #107–#240 and newer stay off this lane.
# Day-sortie beat-kit contract is already on main. Audio-source-status
# and Mission 09 pool-budget contracts are now being opened.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_sortie_beat_enum_contract.py",
    "Scripts/tests/test_audio_source_status_enum_contract.py",
    "Scripts/tests/test_mission09_pool_budget_defaults_contract.py",
    "Scripts/tests/test_mission04_wave_state_enum_contract.py",
    "Scripts/tests/test_mission03_wave_state_enum_contract.py",
    "Scripts/tests/test_mission05_wave_state_enum_contract.py",
    "Scripts/tests/test_mission06_wave_state_enum_contract.py",
    "Scripts/tests/test_mission07_wave_state_enum_contract.py",
    "Scripts/tests/test_mission08_wave_state_enum_contract.py",
    "Scripts/tests/test_mission09_wave_state_enum_contract.py",
    "Scripts/tests/test_iron_rain_maneuver_enum_contract.py",
    "Scripts/tests/test_landscape_capture_diagnostic_enum_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_searchlight_track_runtime_defaults_contract.py",
)
# Apache CPG day/dusk sortie identity. Not a weather label and not
# Harbor IncomingRadar 40/80.
LIVE_BEAT_KINDS = [
    "RidgeIngress",
    "TechnicalScreen",
    "ClusterRidge",
    "TankAmbush",
    "ConvoyPressure",
    "ArmorColumn",
    "HazeIngress",
    "FenceSweep",
    "DugInLine",
    "AdaAcquire",
    "AdaSuppress",
    "ArmorPush",
    "DuskIngress",
    "SensorTrack",
    "DecoyScreen",
    "TelAcquire",
    "TelStrike",
    "ConvoyBreak",
    "Extraction",
]
# FSkyguardDaySortieBeatKit sequences, BrokenHighway(), and sibling
# night/storm beat-kit contracts stay unlocked.
SIBLING_TYPES = (
    "FSkyguardDaySortieBeat",
    "FSkyguardDaySortieBeatKit",
    "ESkyguardNightSortieBeatKind",
    "FSkyguardNightSortieBeat",
    "FSkyguardNightSortieBeatKit",
    "ESkyguardStormRainBeatKind",
    "FSkyguardStormRainBeatKit",
    "ESkyguardSortieBeat",
    "ESkyguardMissionWeather",
)
SIBLING_DEFAULT_TOKENS = (
    "BrokenHighway",
    "DustOffensive",
    "HunterKiller",
    "ForMission",
    "SequencesDiffer",
    "BeatIndexForElapsed",
    "KindAt",
    "WeatherIdentity",
    "NightEyes",
    "DownedBird",
    "RiverHammer",
    "IronRain",
    "bKeepThermal",
    "WeatherLabel",
    "bHydraForClusters",
    "DarkIngress",
    "ThermalHunt",
    "RadarVanHunt",
    "RadarNetCollapse",
    "HoldTheWreck",
    "MixedSwarm",
    "WaterwayBoats",
    "LightningWindow",
    "ProtectWaterway",
    "Clear",
    "Overcast",
    "NightClear",
    "NightOvercast",
    "bYakRuntimeReady",
    "NAME_None",
)
HARBOR_TUNING = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
    "40.f",
    "80.f",
)


def origin_main(name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:Source/Skyguard52/{name}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{name} is missing from origin/main:Source/Skyguard52/{name}: "
            f"{result.stderr.strip()}"
        )
    return result.stdout


def enum_body(header: str, enum_name: str) -> str:
    marker = f"enum class {enum_name}"
    if marker not in header:
        raise AssertionError(
            f"{enum_name} is missing from origin/main:Source/Skyguard52/{HEADER_NAME}"
        )
    start = header.index(marker)
    brace = header.index("{", start)
    finish = header.index("}", brace)
    return header[brace : finish + 1]


def enum_enumerators(header: str, enum_name: str) -> list[str]:
    return re.findall(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\b",
        enum_body(header, enum_name),
        re.M,
    )


class DaySortieBeatKindEnumContractTests(unittest.TestCase):
    def test_day_sortie_beat_kind_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "enum class ESkyguardDaySortieBeatKind : uint8",
            header,
        )

    def test_missing_enum_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            enum_body(
                "enum class ESkyguardUnrelated : uint8\n{\n};\n",
                "ESkyguardDaySortieBeatKind",
            )
        self.assertIn("ESkyguardDaySortieBeatKind", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardDaySortieBeatKind",
        )
        self.assertEqual(enumerators, LIVE_BEAT_KINDS)
        self.assertEqual(
            enumerators,
            [
                "RidgeIngress",
                "TechnicalScreen",
                "ClusterRidge",
                "TankAmbush",
                "ConvoyPressure",
                "ArmorColumn",
                "HazeIngress",
                "FenceSweep",
                "DugInLine",
                "AdaAcquire",
                "AdaSuppress",
                "ArmorPush",
                "DuskIngress",
                "SensorTrack",
                "DecoyScreen",
                "TelAcquire",
                "TelStrike",
                "ConvoyBreak",
                "Extraction",
            ],
        )
        self.assertEqual(len(enumerators), 19, enumerators)
        body = enum_body(header, "ESkyguardDaySortieBeatKind")
        for name in LIVE_BEAT_KINDS:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)
        self.assertNotEqual(
            enumerators,
            [
                "DarkIngress",
                "ThermalHunt",
                "RadarVanHunt",
                "RooftopHeat",
                "RadarNetCollapse",
                "IslandIngress",
                "SearchIsland",
                "HoldTheWreck",
                "RescuePressure",
                "RescueLift",
                "MixedSwarm",
                "Extraction",
            ],
        )
        self.assertNotEqual(
            enumerators,
            [
                "Clear",
                "Overcast",
                "Rain",
                "Storm",
                "NightClear",
                "NightOvercast",
            ],
        )

    def test_day_sortie_beat_kind_enum_does_not_invent_index_none(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardDaySortieBeatKind",
        )
        body = enum_body(header, "ESkyguardDaySortieBeatKind")
        self.assertNotIn("INDEX_NONE", enumerators)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", enumerators)
        self.assertNotIn("NAME_None", body)

    def test_day_sortie_beat_kind_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardDaySortieBeatKind",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_day_sortie_beat_kind_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardDaySortieBeatKind")
        self.assertIn("RidgeIngress", body)
        self.assertIn("Extraction", body)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
        for token in SIBLING_DEFAULT_TOKENS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("IncomingRadar", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        enumerators = enum_enumerators(
            header,
            "ESkyguardDaySortieBeatKind",
        )
        self.assertEqual(enumerators, LIVE_BEAT_KINDS)
        self.assertEqual(len(enumerators), 19, enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])
        self.assertNotEqual(
            enumerators,
            [
                "Approach",
                "InitialContact",
                "ShoreAssault",
                "RadarNet",
                "Choice",
                "Climax",
                "Extraction",
                "Succeeded",
                "Failed",
            ],
        )

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in LOCKED_SCRIPTS:
            if (ROOT / sibling).exists():
                existing.append(sibling)
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
