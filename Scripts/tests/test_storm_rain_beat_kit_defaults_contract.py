from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardStormRainBeatKit.h"
STRUCT_NAME = "FSkyguardStormRainBeatKit"
# Leftover #56–#64 plus StormRainBeatKit production sources and the
# on-main beat-kit contract. This lane only adds an isolated Python
# defaults contract.
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
# Isolated-test drafts #107–#243 and newer stay off this lane.
# Day/night/storm beat-kind enum contracts are in-flight. The on-main
# beat-kit contract already locks RiverHammer()/IronRain() sequences.
# ESkyguardMissionWeather (#155) stays unlocked.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
    "Scripts/tests/test_day_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_night_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_sortie_beat_enum_contract.py",
    "Scripts/tests/test_iron_rain_maneuver_enum_contract.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
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
    "Scripts/tests/test_landscape_capture_diagnostic_enum_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Apache CPG storm/rain kit identity defaults. Storm is the in-struct
# Weather default — not a re-lock of ESkyguardMissionWeather (#155)
# and not Harbor IncomingRadar 40/80.
PUBLIC_FIELDS = (
    "static constexpr int32 BeatCount = 7;",
    'const TCHAR* Title = TEXT("");',
    'const TCHAR* WeatherLabel = TEXT("");',
    "ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Storm;",
    "bool bHydraForClusters = true;",
)
IN_CLASS_DEFAULTS = {
    "BeatCount": "7",
    "Title": 'TEXT("")',
    "WeatherLabel": 'TEXT("")',
    "Weather": "ESkyguardMissionWeather::Storm",
    "bHydraForClusters": "true",
}
# Beat-kind enumerators belong to the in-flight enum contract.
# RiverHammer()/IronRain() sequences are already on-main.
BEAT_KIND_ENUMERATORS_NOT_LOCKED = (
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
)
WEATHER_ENUMERATORS_NOT_LOCKED = (
    "Clear",
    "Overcast",
    "Rain",
    "NightClear",
    "NightOvercast",
)
TYPES_NOT_LOCKED = (
    "enum class ESkyguardStormRainBeatKind",
    "enum class ESkyguardMissionWeather",
    "RiverHammer",
    "IronRain",
    "MakeRiverHammer",
    "MakeIronRain",
    "KeepsHydraForClusters",
    "ApplyHydraForClusters",
    "BeatIndexForElapsed",
    "FSkyguardDaySortieBeatKit",
    "FSkyguardNightSortieBeatKit",
    "ESkyguardDaySortieBeatKind",
    "ESkyguardNightSortieBeatKind",
    "ESkyguardSortieBeat",
    "ESkyguardIronRainManeuver",
    "FSkyguardStormRuntime",
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
UNLOCKED_MEMBER_NAMES = (
    "MissionId",
    "WeatherIdentity",
    "Kinds",
    "Threats",
    "Stations",
    "Calls",
)
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "Error =",
    "FString()",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_TUNING = ("40.f", "80.f")
HARBOR_INCOMING = "IncomingRadar"


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def beat_kit_body(header: str) -> str:
    marker = f"struct {STRUCT_NAME}"
    if marker not in header:
        raise AssertionError(
            f"{STRUCT_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = header.index(marker)
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: re.sub(r"\s+", " ", value).strip()
        for name, value in re.findall(
            r"(?:static constexpr int32|const TCHAR\*|ESkyguardMissionWeather|bool)"
            r"\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class StormRainBeatKitDefaultsContractTests(unittest.TestCase):
    def test_storm_rain_beat_kit_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        body = beat_kit_body(header)
        self.assertNotIn("USTRUCT(BlueprintType)", body)
        self.assertNotIn("GENERATED_BODY()", body)

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            beat_kit_body("struct FSkyguardUnrelated {\n};\n")
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = beat_kit_body(origin_main_header())
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 0)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = beat_kit_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(defaults.get("BeatCount"), "7")
        self.assertEqual(defaults.get("Title"), 'TEXT("")')
        self.assertEqual(defaults.get("WeatherLabel"), 'TEXT("")')
        self.assertEqual(
            defaults.get("Weather"),
            "ESkyguardMissionWeather::Storm",
        )
        self.assertEqual(defaults.get("bHydraForClusters"), "true")
        self.assertIn("static constexpr int32 BeatCount = 7;", body)
        self.assertIn('const TCHAR* Title = TEXT("");', body)
        self.assertIn('const TCHAR* WeatherLabel = TEXT("");', body)
        self.assertIn(
            "ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Storm;",
            body,
        )
        self.assertIn("bool bHydraForClusters = true;", body)
        self.assertNotIn("BeatCount = INDEX_NONE", body)
        self.assertNotIn("bHydraForClusters = false", body)
        self.assertNotIn("Weather = ESkyguardMissionWeather::Rain", body)
        self.assertEqual(len(defaults), 5, defaults)
        self.assertNotIn("Error", defaults)
        for name in UNLOCKED_MEMBER_NAMES:
            self.assertNotIn(name, defaults)

    def test_struct_does_not_invent_index_none_or_error_defaults(self) -> None:
        body = beat_kit_body(origin_main_header())
        defaults = in_class_defaults(body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("INDEX_NONE", defaults.values())
        self.assertNotIn("NAME_None", defaults.values())
        self.assertNotIn("Error", defaults)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("FString Error", body)
        self.assertNotIn("FString", body)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})
        self.assertIn("FName MissionId;", body)
        self.assertIn("FName WeatherIdentity;", body)
        self.assertNotIn("MissionId = NAME_None", body)
        self.assertNotIn("WeatherIdentity = NAME_None", body)

    def test_contract_does_not_lock_beat_kind_or_weather_enumerators(self) -> None:
        body = beat_kit_body(origin_main_header())
        defaults = in_class_defaults(body)
        for name in TYPES_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        self.assertNotIn("enum class ESkyguardStormRainBeatKind", body)
        self.assertNotIn("enum class ESkyguardMissionWeather", body)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        for name in WEATHER_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        self.assertNotIn("RiverHammer", body)
        self.assertNotIn("IronRain", body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = beat_kit_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = beat_kit_body(origin_main_header())
        defaults = in_class_defaults(body)
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{STRUCT_NAME} contains {banned}; "
                "storm-rain beat-kit defaults are Apache CPG Hydra/"
                "Storm identity, not Yak",
            )
            self.assertNotIn(banned, defaults)

    def test_contract_is_storm_rain_beat_kit_defaults_only(self) -> None:
        body = beat_kit_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertIn("static constexpr int32 BeatCount = 7;", body)
        self.assertIn('const TCHAR* Title = TEXT("");', body)
        self.assertIn('const TCHAR* WeatherLabel = TEXT("");', body)
        self.assertIn(
            "ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Storm;",
            body,
        )
        self.assertIn("bool bHydraForClusters = true;", body)
        for name in TYPES_NOT_LOCKED:
            self.assertNotIn(name, body)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
        for name in WEATHER_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotEqual(list(defaults), ["Rifle", "Igla"])
        self.assertNotIn("RiverHammer", defaults)
        self.assertNotIn("IronRain", defaults)
        for name in UNLOCKED_MEMBER_NAMES:
            self.assertNotIn(name, defaults)
        self.assertEqual(len(defaults), 5, defaults)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        existing.append("Scripts/tests/test_storm_rain_beat_kit_contract.py")
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
