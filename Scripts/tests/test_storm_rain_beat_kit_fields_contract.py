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
# only adds an isolated Python FName field-presence contract.
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
# Isolated-test drafts stay off this lane. Beat-kind enum (#245), kit
# defaults (#248), Kinds[BeatCount] (#255), Threats[BeatCount]
# (opening now), Stations/Calls (in-flight siblings), Title/WeatherLabel
# TEXT("") defaults, day-kit fields (#256), night-kit fields (#254),
# kit Beats[7] (#251/#252), and loadout defaults (#253) stay sibling-only.
# RiverHammer()/IronRain()/ForMission() stay on-main.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_kinds_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_threats_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_stations_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_calls_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_fields_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_fields_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Apache CPG storm-rain kit FName field presence only.
# MissionId / WeatherIdentity have no in-struct initializer on
# origin/main. Lock declaration presence, not values.
LOCKED_FIELDS = (
    "FName MissionId;",
    "FName WeatherIdentity;",
)
# These members may appear in the kit body but are not this lock surface.
SIBLING_FIELDS_NOT_LOCKED = (
    "static constexpr int32 BeatCount = 7;",
    'const TCHAR* Title = TEXT("");',
    'const TCHAR* WeatherLabel = TEXT("");',
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
INVENTED_FIELDS = (
    "BeatCount",
    "Kinds",
    "Threats",
    "Stations",
    "Calls",
    "Title",
    "WeatherLabel",
    "bHydraForClusters",
    "bKeepThermal",
    "INDEX_NONE",
    "NAME_None",
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


def fname_declaration(body: str, name: str) -> str:
    match = re.search(rf"FName\s+{re.escape(name)};", body)
    if match is None:
        raise AssertionError(
            f"FName {name} is missing from origin/main:{HEADER_PATH} "
            f"struct {STRUCT_NAME}"
        )
    return match.group(0)


def fname_declarations(body: str) -> list[str]:
    return re.findall(r"FName\s+[A-Za-z_][A-Za-z0-9_]*;", body)


def fname_assignments(body: str) -> dict[str, str]:
    return dict(re.findall(r"FName\s+(\w+)\s*=\s*([^;]+);", body))


class StormRainBeatKitFieldsContractTests(unittest.TestCase):
    def test_storm_rain_beat_kit_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        body = kit_body(header)
        self.assertIn("FName MissionId;", body)
        self.assertIn("FName WeatherIdentity;", body)
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

    def test_missing_mission_id_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            fname_declaration(
                "{\n\tFName WeatherIdentity;\n};\n",
                "MissionId",
            )
        self.assertIn("MissionId", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_missing_weather_identity_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            fname_declaration(
                "{\n\tFName MissionId;\n};\n",
                "WeatherIdentity",
            )
        self.assertIn("WeatherIdentity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_initialized_fname_does_not_satisfy_declaration(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            fname_declaration(
                "{\n\tFName MissionId = NAME_None;\n"
                "\tFName WeatherIdentity = NAME_None;\n};\n",
                "MissionId",
            )
        self.assertIn("MissionId", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_public_fname_fields_match_origin_main_in_order(self) -> None:
        body = kit_body(origin_main_header())
        fields = fname_declarations(body)
        self.assertEqual(fields, list(LOCKED_FIELDS))
        positions = [body.index(field) for field in LOCKED_FIELDS]
        self.assertEqual(positions, sorted(positions), LOCKED_FIELDS)
        for field in LOCKED_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(fname_declaration(body, "MissionId"), "FName MissionId;")
        self.assertEqual(
            fname_declaration(body, "WeatherIdentity"),
            "FName WeatherIdentity;",
        )
        self.assertEqual(body.count("UPROPERTY("), 0)

    def test_fname_fields_have_no_in_struct_initializer(self) -> None:
        body = kit_body(origin_main_header())
        self.assertEqual(fname_assignments(body), {})
        self.assertNotIn("MissionId =", body)
        self.assertNotIn("WeatherIdentity =", body)
        self.assertNotIn("FName MissionId =", body)
        self.assertNotIn("FName WeatherIdentity =", body)
        self.assertNotIn(" = NAME_None", body)
        self.assertNotIn(" = INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("= INDEX_NONE", body)
        for field in LOCKED_FIELDS:
            self.assertNotIn(f"{field[:-1]} =", body)

    def test_struct_does_not_invent_index_none_or_extra_fname_fields(self) -> None:
        body = kit_body(origin_main_header())
        fields = fname_declarations(body)
        self.assertEqual(fields, list(LOCKED_FIELDS))
        for token in INVENTED_FIELDS:
            self.assertNotIn(token, fields)
            if token in ("INDEX_NONE", "NAME_None"):
                self.assertNotIn(token, body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("FString", body)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_lock_kit_defaults_or_array_members(self) -> None:
        self.assertEqual(
            LOCKED_FIELDS,
            (
                "FName MissionId;",
                "FName WeatherIdentity;",
            ),
        )
        joined = "\n".join(LOCKED_FIELDS)
        for field in SIBLING_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, LOCKED_FIELDS)
            self.assertNotIn(field, joined)
        self.assertNotIn("BeatCount = 7", joined)
        self.assertNotIn("Weather =", joined)
        self.assertNotIn("bHydraForClusters", joined)
        self.assertNotIn("Kinds[BeatCount]", joined)
        self.assertNotIn("Threats[BeatCount]", joined)
        self.assertNotIn("Stations[BeatCount]", joined)
        self.assertNotIn("Calls[BeatCount]", joined)
        self.assertNotIn("Title", joined)
        self.assertNotIn("WeatherLabel", joined)
        self.assertNotIn("TEXT(\"\")", joined)

    def test_contract_does_not_relock_beat_kind_enum(self) -> None:
        body = kit_body(origin_main_header())
        self.assertNotIn("enum class ESkyguardStormRainBeatKind", body)
        self.assertNotIn("enum class", body)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(f"ESkyguardStormRainBeatKind::{name}", body)

    def test_contract_does_not_lock_kit_sequences(self) -> None:
        body = kit_body(origin_main_header())
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, body)
        self.assertNotIn("RiverHammer()", body)
        self.assertNotIn("IronRain()", body)
        self.assertNotIn("ForMission(", body)
        self.assertNotIn("namespace SkyguardStormRainBeatKits", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)

    def test_contract_does_not_lock_day_night_fields_or_loadout(self) -> None:
        body = kit_body(origin_main_header())
        fields = fname_declarations(body)
        self.assertEqual(fields, list(LOCKED_FIELDS))
        for token in DAY_NIGHT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, body)
            self.assertNotIn(token, LOCKED_FIELDS)
        for token in LOADOUT_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn("Beats[7]", "\n".join(LOCKED_FIELDS))
        self.assertNotIn("bKeepThermal", "\n".join(LOCKED_FIELDS))
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
        fields = fname_declarations(body)
        self.assertEqual(fields, list(LOCKED_FIELDS))
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(fields, ["Rifle", "Igla"])
        self.assertNotEqual(fields, ["FName Rifle;", "FName Igla;"])

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = kit_body(origin_main_header())
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{STRUCT_NAME} contains {banned}; "
                "storm-rain-beat-kit FName fields are Apache CPG "
                "mission/weather identity, not Yak",
            )

    def test_contract_is_storm_rain_beat_kit_fields_only(self) -> None:
        header = origin_main_header()
        body = kit_body(header)
        fields = fname_declarations(body)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertEqual(fields, list(LOCKED_FIELDS))
        self.assertIn("FName MissionId;", body)
        self.assertIn("FName WeatherIdentity;", body)
        self.assertEqual(fname_assignments(body), {})
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
        self.assertNotEqual(fields, ["Rifle", "Igla"])
        self.assertNotIn("RiverHammer", body)
        self.assertNotIn("ForMission", body)
        self.assertNotIn("Beats", fields)
        for field in SIBLING_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, LOCKED_FIELDS)

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
