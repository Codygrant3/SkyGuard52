from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardStormRainBeatKit.h"
STRUCT_NAME = "FSkyguardStormRainBeatKit"
# Leftover #56–#64 plus StormRainBeatKit production sources. This lane
# only adds an isolated Python Title / WeatherLabel TEXT("") contract.
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
# Isolated-test drafts stay off this lane. FName fields (#258 sibling),
# beat-kind enum (#245), kit defaults BeatCount/Weather/bHydra (#248),
# Kinds[BeatCount] (#255), Threats[BeatCount] (#257), Stations/Calls
# (opening now), day-kit fields (#256), night-kit fields (#254), kit
# Beats[7] (#251/#252), and loadout defaults (#253) stay sibling-only.
# RiverHammer()/IronRain()/ForMission() stay on-main.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_kinds_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_threats_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_stations_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_calls_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_fields_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Apache CPG storm-rain kit empty TCHAR labels only.
LOCKED_LABELS = (
    'const TCHAR* Title = TEXT("");',
    'const TCHAR* WeatherLabel = TEXT("");',
)
LOCKED_LABEL_DEFAULTS = {
    "Title": 'TEXT("")',
    "WeatherLabel": 'TEXT("")',
}
# These members may appear in the kit body but are not this lock surface.
SIBLING_FIELDS_NOT_LOCKED = (
    "FName MissionId;",
    "FName WeatherIdentity;",
    "static constexpr int32 BeatCount = 7;",
    "ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Storm;",
    "bool bHydraForClusters = true;",
    "ESkyguardStormRainBeatKind Kinds[BeatCount] = {};",
    "ESkyguardThreatKind Threats[BeatCount] = {};",
    "ESkyguardGunshipWeapon Stations[BeatCount] = {};",
    "const TCHAR* Calls[BeatCount] = {};",
)
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
KIT_SEQUENCES_NOT_LOCKED = (
    "RiverHammer",
    "IronRain",
    "ForMission",
    "KeepsHydraForClusters",
    "ApplyHydraForClusters",
    "BeatIndexForElapsed",
)
DAY_NIGHT_FIELDS_NOT_LOCKED = (
    "FSkyguardDaySortieBeat Beats[7];",
    "FSkyguardNightSortieBeat Beats[7];",
    "bool bKeepThermal = true;",
)
LOADOUT_NOT_LOCKED = (
    "FSkyguardLoadoutSpec",
    "ESkyguardLoadout",
    "CannonMagazineSize",
    "GuidedMagazineSize",
    "FlareCount",
    "PlaystyleLine",
    "StartingStation",
)
SIBLING_TYPES = (
    "enum class ESkyguardStormRainBeatKind",
    "namespace SkyguardStormRainBeatKits",
    "FSkyguardDaySortieBeatKit",
    "FSkyguardDaySortieBeat",
    "ESkyguardDaySortieBeatKind",
    "FSkyguardNightSortieBeatKit",
    "FSkyguardNightSortieBeat",
    "ESkyguardNightSortieBeatKind",
    "ESkyguardSortieBeat",
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
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
STRUCT_BODY_RE = re.compile(rf"struct {STRUCT_NAME}\s*\{{")
TCHAR_LABEL_RE = re.compile(
    r'const TCHAR\*\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(TEXT\("[^"]*"\));'
)


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{HEADER_PATH} is missing from origin/main:{HEADER_PATH}: "
            f"{result.stderr.strip()}"
        )
    return result.stdout


def kit_body(header: str) -> str:
    match = STRUCT_BODY_RE.search(header)
    if match is None:
        raise AssertionError(
            f"{STRUCT_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = match.start()
    brace = header.index("{", start)
    depth = 0
    for index, char in enumerate(header[brace:], start=brace):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                finish = index + 1
                if finish < len(header) and header[finish] == ";":
                    finish += 1
                return header[brace:finish]
    raise AssertionError(
        f"{STRUCT_NAME} body is unclosed in origin/main:{HEADER_PATH}"
    )


def tchar_label_declaration(body: str, name: str) -> str:
    match = re.search(
        rf'const TCHAR\*\s+{re.escape(name)}\s*=\s*TEXT\(""\);',
        body,
    )
    if match is None:
        raise AssertionError(
            f'const TCHAR* {name} = TEXT("") is missing from '
            f"origin/main:{HEADER_PATH} struct {STRUCT_NAME}"
        )
    return match.group(0)


def tchar_label_defaults(body: str) -> dict[str, str]:
    return dict(TCHAR_LABEL_RE.findall(body))


class StormRainBeatKitLabelsContractTests(unittest.TestCase):
    def test_storm_rain_beat_kit_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        body = kit_body(header)
        self.assertIn('const TCHAR* Title = TEXT("");', body)
        self.assertIn('const TCHAR* WeatherLabel = TEXT("");', body)
        self.assertNotIn("USTRUCT(", body)
        self.assertNotIn("GENERATED_BODY()", body)

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            kit_body("struct FSkyguardUnrelated {\n};\n")
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enum_or_namespace_alone_does_not_satisfy_kit_struct(self) -> None:
        enum_only = (
            "enum class ESkyguardStormRainBeatKind : uint8\n"
            "{\n"
            "\tApproach,\n"
            "\tIronRain,\n"
            "\tExtract\n"
            "};\n"
            "namespace SkyguardStormRainBeatKits\n"
            "{\n"
            "\tconst FSkyguardStormRainBeatKit& RiverHammer();\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            kit_body(enum_only)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_title_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            tchar_label_declaration(
                '{\n\tconst TCHAR* WeatherLabel = TEXT("");\n};\n',
                "Title",
            )
        self.assertIn("Title", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_missing_weather_label_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            tchar_label_declaration(
                '{\n\tconst TCHAR* Title = TEXT("");\n};\n',
                "WeatherLabel",
            )
        self.assertIn("WeatherLabel", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_nonempty_text_does_not_satisfy_empty_label(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            tchar_label_declaration(
                '{\n\tconst TCHAR* Title = TEXT("River Hammer");\n'
                '\tconst TCHAR* WeatherLabel = TEXT("Storm");\n};\n',
                "Title",
            )
        self.assertIn("Title", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_declaration_without_default_does_not_satisfy(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            tchar_label_declaration(
                "{\n\tconst TCHAR* Title;\n"
                "\tconst TCHAR* WeatherLabel;\n};\n",
                "Title",
            )
        self.assertIn("Title", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_calls_array_does_not_satisfy_label_default(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            tchar_label_declaration(
                "{\n\tconst TCHAR* Calls[BeatCount] = {};\n};\n",
                "Calls",
            )
        self.assertIn("Calls", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_public_label_defaults_match_origin_main_in_order(self) -> None:
        body = kit_body(origin_main_header())
        defaults = tchar_label_defaults(body)
        self.assertEqual(defaults, LOCKED_LABEL_DEFAULTS)
        positions = [body.index(field) for field in LOCKED_LABELS]
        self.assertEqual(positions, sorted(positions), LOCKED_LABELS)
        for field in LOCKED_LABELS:
            self.assertIn(field, body)
        self.assertEqual(
            tchar_label_declaration(body, "Title"),
            'const TCHAR* Title = TEXT("");',
        )
        self.assertEqual(
            tchar_label_declaration(body, "WeatherLabel"),
            'const TCHAR* WeatherLabel = TEXT("");',
        )
        self.assertEqual(body.count("UPROPERTY("), 0)

    def test_struct_does_not_invent_index_none_or_extra_label_defaults(self) -> None:
        body = kit_body(origin_main_header())
        defaults = tchar_label_defaults(body)
        self.assertEqual(defaults, LOCKED_LABEL_DEFAULTS)
        self.assertEqual(list(defaults), ["Title", "WeatherLabel"])
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
            self.assertNotIn(token, defaults)
            self.assertNotIn(token, defaults.values())
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("FString", body)
        self.assertNotIn("Calls", defaults)
        self.assertNotIn("MissionId", defaults)
        self.assertNotIn("WeatherIdentity", defaults)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_lock_fname_fields(self) -> None:
        self.assertEqual(
            LOCKED_LABELS,
            (
                'const TCHAR* Title = TEXT("");',
                'const TCHAR* WeatherLabel = TEXT("");',
            ),
        )
        joined = "\n".join(LOCKED_LABELS)
        self.assertNotIn("FName MissionId;", joined)
        self.assertNotIn("FName WeatherIdentity;", joined)
        self.assertNotIn("FName MissionId;", LOCKED_LABELS)
        self.assertNotIn("FName WeatherIdentity;", LOCKED_LABELS)
        self.assertNotIn("MissionId", LOCKED_LABEL_DEFAULTS)
        self.assertNotIn("WeatherIdentity", LOCKED_LABEL_DEFAULTS)

    def test_contract_does_not_lock_kit_defaults_or_array_members(self) -> None:
        joined = "\n".join(LOCKED_LABELS)
        for field in SIBLING_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, LOCKED_LABELS)
            self.assertNotIn(field, joined)
        self.assertNotIn("BeatCount = 7", joined)
        self.assertNotIn("Weather =", joined)
        self.assertNotIn("bHydraForClusters", joined)
        self.assertNotIn("Kinds[BeatCount]", joined)
        self.assertNotIn("Threats[BeatCount]", joined)
        self.assertNotIn("Stations[BeatCount]", joined)
        self.assertNotIn("Calls[BeatCount]", joined)
        self.assertNotIn("FName", joined)
        self.assertEqual(
            LOCKED_LABEL_DEFAULTS,
            {
                "Title": 'TEXT("")',
                "WeatherLabel": 'TEXT("")',
            },
        )
        self.assertNotIn("BeatCount", LOCKED_LABEL_DEFAULTS)
        self.assertNotIn("Weather", LOCKED_LABEL_DEFAULTS)
        self.assertNotIn("bHydraForClusters", LOCKED_LABEL_DEFAULTS)

    def test_contract_does_not_relock_beat_kind_enum(self) -> None:
        body = kit_body(origin_main_header())
        defaults = tchar_label_defaults(body)
        self.assertNotIn("enum class ESkyguardStormRainBeatKind", body)
        self.assertNotIn("enum class", body)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
            self.assertNotIn(f"ESkyguardStormRainBeatKind::{name}", body)

    def test_contract_does_not_lock_kit_sequences(self) -> None:
        body = kit_body(origin_main_header())
        defaults = tchar_label_defaults(body)
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        self.assertNotIn("RiverHammer()", body)
        self.assertNotIn("IronRain()", body)
        self.assertNotIn("ForMission(", body)
        self.assertNotIn("namespace SkyguardStormRainBeatKits", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)

    def test_contract_does_not_lock_day_night_fields_or_loadout(self) -> None:
        body = kit_body(origin_main_header())
        defaults = tchar_label_defaults(body)
        self.assertEqual(defaults, LOCKED_LABEL_DEFAULTS)
        for token in DAY_NIGHT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, body)
            self.assertNotIn(token, LOCKED_LABELS)
        for token in LOADOUT_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn("Beats[7]", "\n".join(LOCKED_LABELS))
        self.assertNotIn("bKeepThermal", "\n".join(LOCKED_LABELS))
        self.assertNotIn("FSkyguardDaySortieBeat Beats[7];", body)
        self.assertNotIn("FSkyguardNightSortieBeat Beats[7];", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = kit_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", body)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = kit_body(origin_main_header())
        defaults = tchar_label_defaults(body)
        self.assertEqual(defaults, LOCKED_LABEL_DEFAULTS)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(list(defaults), ["Rifle", "Igla"])
        self.assertNotEqual(
            list(LOCKED_LABELS),
            ["const TCHAR* Rifle;", "const TCHAR* Igla;"],
        )

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = kit_body(origin_main_header())
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{STRUCT_NAME} contains {banned}; "
                "storm-rain-beat-kit labels are Apache CPG Title/"
                "WeatherLabel TEXT(\"\"), not Yak",
            )

    def test_contract_is_storm_rain_beat_kit_labels_only(self) -> None:
        header = origin_main_header()
        body = kit_body(header)
        defaults = tchar_label_defaults(body)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertEqual(defaults, LOCKED_LABEL_DEFAULTS)
        self.assertIn('const TCHAR* Title = TEXT("");', body)
        self.assertIn('const TCHAR* WeatherLabel = TEXT("");', body)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, body)
        for token in DAY_NIGHT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, body)
        for token in LOADOUT_NOT_LOCKED:
            self.assertNotIn(token, body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotEqual(list(defaults), ["Rifle", "Igla"])
        self.assertNotIn("RiverHammer", body)
        self.assertNotIn("ForMission", body)
        self.assertNotIn("Beats", defaults)
        self.assertNotIn("Calls", defaults)
        self.assertNotIn("BeatCount", defaults)
        self.assertNotIn("Weather", defaults)
        self.assertNotIn("bHydraForClusters", defaults)
        for field in SIBLING_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, LOCKED_LABELS)

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
