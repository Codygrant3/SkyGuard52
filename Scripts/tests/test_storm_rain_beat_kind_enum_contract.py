from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardStormRainBeatKit.h"
# Leftover #56–#64 plus StormRainBeatKit production sources and the
# on-main beat-kit contract. This lane only adds an isolated Python
# enum contract.
LOCKED = {
    "SkyguardStormRainBeatKit.h",
    "SkyguardStormRainBeatKit.cpp",
    "SkyguardStormRainBeatKitTests.cpp",
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
# Isolated-test drafts #107–#242 and newer stay off this lane.
# Mission 09 pool-runtime is now being opened. Day/night sortie
# beat-kind contracts are in-flight. IronRain maneuver (#239) and
# ESkyguardSortieBeat (#240) stay unlocked.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_night_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_sortie_beat_enum_contract.py",
    "Scripts/tests/test_iron_rain_maneuver_enum_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_defaults_contract.py",
    "Scripts/tests/test_mission09_pool_budget_defaults_contract.py",
    "Scripts/tests/test_audio_source_status_enum_contract.py",
    "Scripts/tests/test_mission09_wave_state_enum_contract.py",
    "Scripts/tests/test_mission08_wave_state_enum_contract.py",
    "Scripts/tests/test_mission07_wave_state_enum_contract.py",
    "Scripts/tests/test_mission06_wave_state_enum_contract.py",
    "Scripts/tests/test_mission05_wave_state_enum_contract.py",
    "Scripts/tests/test_mission04_wave_state_enum_contract.py",
    "Scripts/tests/test_mission03_wave_state_enum_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_landscape_capture_diagnostic_enum_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Apache CPG storm/rain sortie identity. Not Harbor IncomingRadar 40/80
# and not ESkyguardSortieBeat. IronRain here is a beat kind, not
# ESkyguardIronRainManeuver (#239).
LIVE_BEAT_KINDS = [
    "Approach",
    "WaterwayBoats",
    "BargeClusters",
    "LightningWindow",
    "ProtectWaterway",
    "Tempest",
    "GunLine",
    "KillBattery",
    "BarrageCover",
    "RescueCorridor",
    "IronRain",
    "Extract",
]
SORTIE_BEAT_LIST = [
    "Approach",
    "InitialContact",
    "ShoreAssault",
    "RadarNet",
    "Choice",
    "Climax",
    "Extraction",
    "Succeeded",
    "Failed",
]
IRON_RAIN_MANEUVER_LIST = [
    "None",
    "Climb",
    "Cross",
]
# FSkyguardStormRainBeatKit sequences, day/night beat kinds, sortie
# beats, IronRain maneuvers, and Mission 09 pool-runtime stay unlocked.
SIBLING_TYPES = (
    "FSkyguardStormRainBeatKit",
    "ESkyguardSortieBeat",
    "ESkyguardIronRainManeuver",
    "ESkyguardDaySortieBeatKind",
    "ESkyguardNightSortieBeatKind",
    "FSkyguardDaySortieBeatKit",
    "FSkyguardNightSortieBeatKit",
    "ESkyguardMissionWeather",
    "FSkyguardMission09PoolRuntime",
    "FSkyguardMission09PoolBudget",
)
SIBLING_DEFAULT_TOKENS = (
    "BeatCount",
    "bHydraForClusters",
    "RiverHammer",
    "KeepsHydraForClusters",
    "ApplyHydraForClusters",
    "BeatIndexForElapsed",
    "SevereSquall",
    "RescueSunset",
    "InitialContact",
    "ShoreAssault",
    "RadarNet",
    "RidgeIngress",
    "DarkIngress",
    "Climb",
    "Cross",
    "Available",
    "PeakActive",
    "Recycled",
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


class StormRainBeatKindEnumContractTests(unittest.TestCase):
    def test_beat_kind_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "enum class ESkyguardStormRainBeatKind : uint8",
            header,
        )
        self.assertNotIn(
            "enum class ESkyguardStormRainBeatKind : uint8\n{\n\tINDEX_NONE",
            header,
        )

    def test_missing_enum_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            enum_body(
                "enum class ESkyguardUnrelated : uint8\n{\n};\n",
                "ESkyguardStormRainBeatKind",
            )
        self.assertIn("ESkyguardStormRainBeatKind", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardStormRainBeatKind",
        )
        self.assertEqual(enumerators, LIVE_BEAT_KINDS)
        self.assertEqual(
            enumerators,
            [
                "Approach",
                "WaterwayBoats",
                "BargeClusters",
                "LightningWindow",
                "ProtectWaterway",
                "Tempest",
                "GunLine",
                "KillBattery",
                "BarrageCover",
                "RescueCorridor",
                "IronRain",
                "Extract",
            ],
        )
        self.assertEqual(len(enumerators), 12, enumerators)
        self.assertNotEqual(enumerators, SORTIE_BEAT_LIST)
        self.assertNotEqual(enumerators, IRON_RAIN_MANEUVER_LIST)
        body = enum_body(header, "ESkyguardStormRainBeatKind")
        for name in LIVE_BEAT_KINDS:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_beat_kind_enum_does_not_invent_index_none(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardStormRainBeatKind",
        )
        body = enum_body(header, "ESkyguardStormRainBeatKind")
        self.assertNotIn("INDEX_NONE", enumerators)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", enumerators)
        self.assertNotIn("NAME_None", body)

    def test_beat_kind_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardStormRainBeatKind",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_storm_rain_beat_kind_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardStormRainBeatKind")
        self.assertIn("Approach", body)
        self.assertIn("Extract", body)
        self.assertIn("IronRain", body)
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
            "ESkyguardStormRainBeatKind",
        )
        self.assertEqual(enumerators, LIVE_BEAT_KINDS)
        self.assertEqual(len(enumerators), 12, enumerators)
        self.assertNotEqual(enumerators, SORTIE_BEAT_LIST)
        self.assertNotEqual(enumerators, IRON_RAIN_MANEUVER_LIST)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

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
