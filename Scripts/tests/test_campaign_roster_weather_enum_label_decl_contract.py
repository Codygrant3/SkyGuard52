from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardCampaignRoster.h"
NAMESPACE_NAME = "SkyguardCampaignRoster"
# Declaration presence only. Do not invent INDEX_NONE, a
# returned label string, or lock the WeatherEnumLabel body
# in the .cpp. origin/main is one line
# (`const TCHAR* WeatherEnumLabel(ESkyguardMissionWeather Weather);`);
# accept that form and other split-line wraps.
WEATHER_ENUM_LABEL = (
    "const TCHAR* WeatherEnumLabel(ESkyguardMissionWeather Weather);"
)
# Leftover #56–#64 plus CampaignRoster production sources.
# This lane only adds an isolated Python WeatherEnumLabel
# declaration contract. Stay off leftover mission-weather
# enum contract #96d2 (ESkyguardMissionWeather body), leftover
# campaign-roster lookup #111 (IndexOf), leftover loadout
# #8/#114/#154, NumMissions #332, Get / IdAt (sibling drafts
# this wave), LoadoutLabel (sibling in-flight),
# FSkyguardCampaignMissionSpec fields, BeatSeconds, Harbor
# Breaker proof-clock comments, leftover Harbor 40/80,
# leftover campaign-save empty-fail-closed, leftover CPG
# debrief, FillResultCombatStats / FillAndFinalize /
# FillAndFail / ApplyHydraForClusters leftover Gunner,
# leftover Harbor #6/#8/#9, leftover theater-kit #59,
# leftover flare/HUD #57/#61/#62, leftover drafts #56–#64,
# leftover #147 ApacheSystem, leftover #149 weapon stations,
# leftover #152 pilot commands, leftover settings
# invert-look / ApplySettings broadcast #134, Harbor
# IncomingRadar 40/80, leftover live copy,
# FSkyguardMission0NIntegrationReadiness (bYakRuntimeReady),
# and dirty D:\Skyguard52.
LOCKED = {
    "SkyguardCampaignRoster.h",
    "SkyguardCampaignRoster.cpp",
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
# Isolated-test drafts stay off this lane. Leftover
# campaign-roster lookup #111, leftover campaign-save
# empty-fail-closed, leftover CPG debrief, leftover
# mission-weather enum #96d2, leftover loadout #8/#114/#154,
# leftover ApacheSystem #147 / weapon stations #149 /
# pilot commands #152, leftover settings invert-look #134,
# leftover Harbor / theater-kit, NumMissions #332, Get /
# IdAt siblings this wave, and LoadoutLabel (in-flight)
# stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
    "Scripts/tests/test_campaign_roster_get_decl_contract.py",
    "Scripts/tests/test_campaign_roster_id_at_decl_contract.py",
    "Scripts/tests/test_campaign_roster_index_of_decl_contract.py",
    "Scripts/tests/test_campaign_roster_loadout_label_decl_contract.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
    "Scripts/tests/test_cpg_debrief_copy_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_campaign_sortie_flow_contract.py",
    "Scripts/tests/test_m09_campaign_handoff_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_gunship_weapon_stations_contract.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_loadout_display_name_contract.py",
    "Scripts/tests/test_loadout_slot_helpers_contract.py",
    "Scripts/tests/test_resolve_loadout_decl_contract.py",
    "Scripts/tests/test_gunship_types_loadout_contract.py",
    "Scripts/tests/test_gunship_types_loadout_tests.py",
    "Scripts/tests/test_game_user_settings_getter_decl_contract.py",
    "Scripts/tests/test_set_invert_look_decl_contract.py",
    "Scripts/tests/test_invert_look_decl_contract.py",
    "Scripts/tests/test_validate_settings_decl_contract.py",
    "Scripts/tests/test_apply_and_save_settings_decl_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
# NumMissions is leftover #332. Get / IdAt are sibling drafts
# this wave. IndexOf is leftover lookup #111. LoadoutLabel
# is a sibling in-flight.
UNLOCKED_NEIGHBORS = (
    "int32 NumMissions();",
    "const FSkyguardCampaignMissionSpec& Get(int32 Index);",
    "int32 IndexOf(FName MissionId);",
    "FName IdAt(int32 Index);",
    "const TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);",
)
NUM_MISSIONS_NOT_LOCKED = ("int32 NumMissions();",)
GET_NOT_LOCKED = ("const FSkyguardCampaignMissionSpec& Get(int32 Index);",)
INDEX_OF_NOT_LOCKED = ("int32 IndexOf(FName MissionId);",)
ID_AT_NOT_LOCKED = ("FName IdAt(int32 Index);",)
LOADOUT_LABEL_NOT_LOCKED = (
    "const TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);",
)
# Leftover mission-weather enum contract #96d2 owns the
# ESkyguardMissionWeather body. Parse the namespace, not
# the enum.
WEATHER_ENUM_BODY_NOT_LOCKED = (
    "enum class ESkyguardMissionWeather",
    "ESkyguardMissionWeather::Clear",
    "ESkyguardMissionWeather::Overcast",
    "ESkyguardMissionWeather::Rain",
    "ESkyguardMissionWeather::Storm",
    "ESkyguardMissionWeather::NightClear",
    "ESkyguardMissionWeather::NightOvercast",
    "NightClear",
    "NightOvercast",
)
# Do not invent a returned label string. The .cpp switch
# payloads stay unlocked.
INVENTED_LABELS_NOT_LOCKED = (
    'TEXT("Clear")',
    'TEXT("Overcast")',
    'TEXT("Rain")',
    'TEXT("Storm")',
    'TEXT("Night clear")',
    'TEXT("Night overcast")',
    'TEXT("Unknown")',
    'return TEXT("',
    "switch (Weather)",
)
# FSkyguardCampaignMissionSpec fields / BeatSeconds /
# Harbor Breaker proof-clock comments stay unlocked.
# Use default-initialized field forms so the parameter
# type on WeatherEnumLabel is not treated as a spec field.
SPEC_FIELDS_NOT_LOCKED = (
    "FName MissionId;",
    "const TCHAR* Title = TEXT(\"\");",
    "const TCHAR* Brief = TEXT(\"\");",
    "const TCHAR* Success = TEXT(\"\");",
    "const TCHAR* Failure = TEXT(\"\");",
    "ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Clear;",
    "FName WeatherIdentity;",
    "const TCHAR* WeatherLabel = TEXT(\"\");",
    "float TimeOfDayHours = 12.f;",
    "float BeatSeconds[7]",
    "ESkyguardThreatKind ContactKind",
    "ESkyguardThreatKind ShoreKind",
    "ESkyguardThreatKind SupportKind",
    "ESkyguardThreatKind ExtractKind",
    "ESkyguardClimaxKind Climax",
    "bool bNightIdentity = false;",
    "bool bStormRocketContract = false;",
)
HARBOR_PROOF_NOT_LOCKED = (
    "Harbor Breaker",
    "proof clock",
    "BeatSeconds",
    "120.f",
    "240.f",
    "360.f",
    "480.f",
    "600.f",
    "780.f",
    "900.f",
)
# Leftover CPG debrief copy #284 / snapshot defaults #195 /
# fail-closed #8ccd / empty-capture #130 stay unlocked.
LEFTOVER_CPG_DEBRIEF_NOT_LOCKED = (
    "SkyguardBuildCpgDebriefCopy",
    "SkyguardCpgCopyHasBannedTerm",
    "SkyguardCaptureCpgDebrief",
    "FSkyguardCpgDebriefSnapshot",
)
# Leftover campaign-save empty-fail-closed stay unlocked.
LEFTOVER_CAMPAIGN_SAVE_NOT_LOCKED = (
    "MigrateCampaignSave",
    "CurrentSaveVersion",
    "already-v2",
    "Identity migrate",
)
# FillResultCombatStats / FillAndFinalize / FillAndFail /
# ApplyHydraForClusters leftover Gunner stay unlocked.
FILL_AND_GUNNER_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
    "FillAndFinalize",
    "FillAndFail",
    "ApplyHydraForClusters",
    "ASkyguardGunner",
)
# Leftover #147 / #149 / #152 / #154 / #8 / #114 / #134 stay
# unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "FSkyguardLoadoutSpec",
    "ApplyHydraForClusters",
    "FillResultCombatStats",
    "FillAndFinalize",
    "FillAndFail",
    "SetInvertVerticalLook",
    "GetInvertVerticalLook",
    "bInvertVerticalLook",
    "InvertLook",
    "HandleInvertLookChanged",
    "ApplySettings",
)
# .cpp WeatherEnumLabel body / invented return values stay
# unlocked. Do not invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return TEXT(",
    "switch (Weather)",
    "case ESkyguardMissionWeather::",
    "default:",
    "SkyguardCampaignRoster::WeatherEnumLabel",
    "SkyguardCampaignRoster.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "ASkyguardIglaMissile",
    "enum class ESkyguardMissionWeather",
    "struct FSkyguardCampaignMissionSpec",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_INCOMING = "IncomingRadar"
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
HARBOR_TUNING = ("40.f", "80.f")
NAMESPACE_RE = re.compile(rf"namespace\s+{re.escape(NAMESPACE_NAME)}\b")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*&\s*", "& ", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
    return compact


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


def namespace_body(header: str) -> str:
    match = NAMESPACE_RE.search(header)
    if match is None:
        raise AssertionError(
            f"namespace {NAMESPACE_NAME} is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = match.start()
    brace = header.index("{", start)
    finish = header.index("}", brace)
    return header[brace : finish + 1]


def has_declaration(region: str, declaration: str) -> bool:
    if declaration in region:
        return True
    return collapsed(declaration) in collapsed(region)


def declaration_count(region: str, declaration: str) -> int:
    if declaration in region:
        return region.count(declaration)
    return collapsed(region).count(collapsed(declaration))


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"namespace {NAMESPACE_NAME}"
        )
    return declaration


class CampaignRosterWeatherEnumLabelDeclContractTests(unittest.TestCase):
    def test_campaign_roster_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertTrue(has_declaration(body, WEATHER_ENUM_LABEL), body)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)

    def test_missing_namespace_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            namespace_body(
                "namespace SkyguardUnrelatedCampaignRoster\n{\n};\n"
            )
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_struct_alone_does_not_satisfy_namespace(self) -> None:
        struct_only = (
            "struct FSkyguardCampaignMissionSpec\n"
            "{\n"
            "\tFName MissionId;\n"
            "\tfloat BeatSeconds[7] = "
            "{120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f};\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            namespace_body(struct_only)
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enum_body_alone_does_not_satisfy_namespace(self) -> None:
        enum_only = (
            "enum class ESkyguardMissionWeather : uint8\n"
            "{\n"
            "\tClear,\n"
            "\tOvercast,\n"
            "\tRain,\n"
            "\tStorm,\n"
            "\tNightClear,\n"
            "\tNightOvercast\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            namespace_body(enum_only)
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_weather_enum_label_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "\tint32 NumMissions();\n"
            "\tconst FSkyguardCampaignMissionSpec& Get(int32 Index);\n"
            "\tint32 IndexOf(FName MissionId);\n"
            "\tFName IdAt(int32 Index);\n"
            "\tconst TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, WEATHER_ENUM_LABEL)
        self.assertIn("WeatherEnumLabel", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        neighbors_only = (
            "{\n"
            "\tint32 NumMissions();\n"
            "\tconst FSkyguardCampaignMissionSpec& Get(int32 Index);\n"
            "\tint32 IndexOf(FName MissionId);\n"
            "\tFName IdAt(int32 Index);\n"
            "\tconst TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);\n"
            "}\n"
        )
        self.assertFalse(
            has_declaration(neighbors_only, WEATHER_ENUM_LABEL),
            neighbors_only,
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, WEATHER_ENUM_LABEL)
        self.assertIn("WeatherEnumLabel", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        wrongs = (
            "{\n\tTCHAR* WeatherEnumLabel("
            "ESkyguardMissionWeather Weather);\n}\n",
            "{\n\tFString WeatherEnumLabel("
            "ESkyguardMissionWeather Weather);\n}\n",
            "{\n\tconst TCHAR* WeatherEnumLabel();\n}\n",
            "{\n\tconst TCHAR* WeatherEnumLabel("
            "ESkyguardMissionWeather Weather) const;\n}\n",
            "{\n\tconst TCHAR* WeatherEnumLabel(int32 Weather);\n}\n",
            "{\n\tconst TCHAR* WeatherLabel("
            "ESkyguardMissionWeather Weather);\n}\n",
            "{\n\tconst TCHAR* LoadoutLabel("
            "ESkyguardMissionWeather Weather);\n}\n",
            "{\n\tconst TCHAR* WeatherEnumLabel("
            "ESkyguardLoadout Loadout);\n}\n",
            "{\n\tconst TCHAR* WeatherEnumLabel("
            "ESkyguardMissionWeather Weather = INDEX_NONE);\n}\n",
        )
        for region in wrongs:
            self.assertFalse(
                has_declaration(region, WEATHER_ENUM_LABEL),
                region,
            )
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, WEATHER_ENUM_LABEL)
            self.assertIn("missing", str(raised.exception).lower())

    def test_weather_enum_label_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(body, WEATHER_ENUM_LABEL),
            WEATHER_ENUM_LABEL,
        )
        self.assertTrue(has_declaration(body, WEATHER_ENUM_LABEL))
        self.assertEqual(declaration_count(body, WEATHER_ENUM_LABEL), 1)
        self.assertTrue(WEATHER_ENUM_LABEL.endswith(";"), WEATHER_ENUM_LABEL)
        self.assertTrue(
            WEATHER_ENUM_LABEL.startswith("const TCHAR* "),
            WEATHER_ENUM_LABEL,
        )
        self.assertIn("ESkyguardMissionWeather Weather", WEATHER_ENUM_LABEL)
        self.assertNotIn("INDEX_NONE", WEATHER_ENUM_LABEL)
        self.assertNotIn("return ", WEATHER_ENUM_LABEL)
        self.assertNotIn("{", WEATHER_ENUM_LABEL)
        self.assertNotIn("}", WEATHER_ENUM_LABEL)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "{\n"
            "\tconst TCHAR*\n"
            "\tWeatherEnumLabel(ESkyguardMissionWeather Weather);\n"
            "}\n"
        )
        wrap_args = (
            "{\n"
            "\tconst TCHAR* WeatherEnumLabel(\n"
            "\t\tESkyguardMissionWeather Weather);\n"
            "}\n"
        )
        wrap_arg_type = (
            "{\n"
            "\tconst TCHAR* WeatherEnumLabel(ESkyguardMissionWeather\n"
            "\t\tWeather);\n"
            "}\n"
        )
        wrap_star = (
            "{\n"
            "\tconst TCHAR *\n"
            "\tWeatherEnumLabel(\n"
            "\t\tESkyguardMissionWeather Weather);\n"
            "}\n"
        )
        self.assertTrue(
            has_declaration(wrap_type, WEATHER_ENUM_LABEL),
            wrap_type,
        )
        self.assertTrue(
            has_declaration(wrap_args, WEATHER_ENUM_LABEL),
            wrap_args,
        )
        self.assertTrue(
            has_declaration(wrap_arg_type, WEATHER_ENUM_LABEL),
            wrap_arg_type,
        )
        self.assertTrue(
            has_declaration(wrap_star, WEATHER_ENUM_LABEL),
            wrap_star,
        )
        self.assertEqual(
            require_declaration(wrap_type, WEATHER_ENUM_LABEL),
            WEATHER_ENUM_LABEL,
        )
        self.assertEqual(
            require_declaration(wrap_args, WEATHER_ENUM_LABEL),
            WEATHER_ENUM_LABEL,
        )
        self.assertEqual(
            require_declaration(wrap_arg_type, WEATHER_ENUM_LABEL),
            WEATHER_ENUM_LABEL,
        )
        self.assertEqual(
            require_declaration(wrap_star, WEATHER_ENUM_LABEL),
            WEATHER_ENUM_LABEL,
        )
        self.assertEqual(declaration_count(wrap_type, WEATHER_ENUM_LABEL), 1)
        self.assertEqual(declaration_count(wrap_args, WEATHER_ENUM_LABEL), 1)
        self.assertEqual(
            declaration_count(wrap_arg_type, WEATHER_ENUM_LABEL),
            1,
        )
        self.assertEqual(declaration_count(wrap_star, WEATHER_ENUM_LABEL), 1)
        one_line = f"{{\n\t{WEATHER_ENUM_LABEL}\n}}\n"
        self.assertTrue(has_declaration(one_line, WEATHER_ENUM_LABEL))
        body = namespace_body(origin_main_header())
        self.assertTrue(has_declaration(body, WEATHER_ENUM_LABEL), body)
        self.assertEqual(
            require_declaration(body, WEATHER_ENUM_LABEL),
            WEATHER_ENUM_LABEL,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", WEATHER_ENUM_LABEL)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", WEATHER_ENUM_LABEL)
        body = namespace_body(origin_main_header())
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("= INDEX_NONE", WEATHER_ENUM_LABEL)

    def test_declaration_does_not_invent_returned_label_string(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        self.assertNotIn("return ", WEATHER_ENUM_LABEL)
        self.assertNotIn("TEXT(", WEATHER_ENUM_LABEL)
        self.assertNotIn("switch (Weather)", WEATHER_ENUM_LABEL)
        for token in INVENTED_LABELS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        body = namespace_body(origin_main_header())
        for token in INVENTED_LABELS_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn("{", WEATHER_ENUM_LABEL)
        self.assertNotIn("}", WEATHER_ENUM_LABEL)

    def test_contract_does_not_lock_weather_enum_label_cpp_body(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        self.assertNotIn("{", WEATHER_ENUM_LABEL)
        self.assertNotIn("}", WEATHER_ENUM_LABEL)
        self.assertNotIn("return ", WEATHER_ENUM_LABEL)
        self.assertNotIn(
            "SkyguardCampaignRoster::WeatherEnumLabel",
            WEATHER_ENUM_LABEL,
        )
        self.assertNotIn("SkyguardCampaignRoster.cpp", WEATHER_ENUM_LABEL)
        self.assertNotIn("SkyguardCampaignRoster.cpp", locked_only)
        self.assertNotIn("switch (Weather)", WEATHER_ENUM_LABEL)
        self.assertNotIn("case ESkyguardMissionWeather::", WEATHER_ENUM_LABEL)
        self.assertNotIn('return TEXT("Clear")', WEATHER_ENUM_LABEL)
        self.assertNotIn("default:", WEATHER_ENUM_LABEL)

    def test_contract_does_not_relock_num_missions(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        for neighbor in NUM_MISSIONS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER_ENUM_LABEL)
        self.assertNotIn("NumMissions", WEATHER_ENUM_LABEL)
        self.assertNotIn("NumMissions", locked_only)

    def test_contract_does_not_relock_get(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        for neighbor in GET_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER_ENUM_LABEL)
        self.assertNotIn(
            "const FSkyguardCampaignMissionSpec& Get(int32 Index);",
            locked_only,
        )
        self.assertNotIn("FSkyguardCampaignMissionSpec& Get", WEATHER_ENUM_LABEL)

    def test_contract_does_not_relock_index_of(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        for neighbor in INDEX_OF_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER_ENUM_LABEL)
        self.assertNotIn("IndexOf", WEATHER_ENUM_LABEL)
        self.assertNotIn("IndexOf", locked_only)

    def test_contract_does_not_relock_id_at(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        for neighbor in ID_AT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER_ENUM_LABEL)
        self.assertNotIn("IdAt", WEATHER_ENUM_LABEL)
        self.assertNotIn("IdAt", locked_only)

    def test_contract_does_not_relock_loadout_label(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        self.assertNotIn(LOADOUT_LABEL_NOT_LOCKED, locked_only)
        self.assertNotIn(LOADOUT_LABEL_NOT_LOCKED, WEATHER_ENUM_LABEL)
        self.assertNotIn("LoadoutLabel", WEATHER_ENUM_LABEL)
        self.assertNotIn("LoadoutLabel", locked_only)
        self.assertNotIn("ESkyguardLoadout", WEATHER_ENUM_LABEL)
        self.assertNotIn("ESkyguardLoadout", locked_only)

    def test_contract_does_not_relock_mission_weather_enum(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        for token in WEATHER_ENUM_BODY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        self.assertNotIn("enum class ESkyguardMissionWeather", locked_only)
        self.assertNotIn("NightClear", WEATHER_ENUM_LABEL)
        self.assertNotIn("NightOvercast", WEATHER_ENUM_LABEL)
        body = namespace_body(origin_main_header())
        self.assertNotIn("enum class ESkyguardMissionWeather", body)
        self.assertNotIn("NightClear", body)
        self.assertNotIn("NightOvercast", body)

    def test_contract_does_not_relock_spec_fields_or_proof_clock(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        for token in SPEC_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        for token in HARBOR_PROOF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        self.assertNotIn("BeatSeconds", WEATHER_ENUM_LABEL)
        self.assertNotIn("BeatSeconds", locked_only)
        self.assertNotIn("Harbor Breaker proof clock", locked_only)
        self.assertNotIn("bNightIdentity", locked_only)
        self.assertNotIn("bStormRocketContract", locked_only)
        body = namespace_body(origin_main_header())
        self.assertNotIn("float BeatSeconds[7]", body)
        self.assertNotIn("Harbor Breaker proof clock", body)
        self.assertNotIn("struct FSkyguardCampaignMissionSpec", body)

    def test_contract_does_not_relock_leftover_cpg_debrief(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        body = namespace_body(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
            self.assertNotIn(token, body)

    def test_contract_does_not_relock_leftover_campaign_save(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        body = namespace_body(origin_main_header())
        for token in LEFTOVER_CAMPAIGN_SAVE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
            self.assertNotIn(token, body)

    def test_contract_does_not_relock_fill_and_gunner(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        for token in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ASkyguardGunner", WEATHER_ENUM_LABEL)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        self.assertNotIn("SetInvertVerticalLook", locked_only)
        self.assertNotIn("bInvertVerticalLook", locked_only)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn("ESkyguardGunshipWeaponStation", locked_only)
        self.assertNotIn("ESkyguardPilotCommand", locked_only)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        self.assertEqual(
            require_declaration(locked_only, WEATHER_ENUM_LABEL),
            WEATHER_ENUM_LABEL,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER_ENUM_LABEL)
        self.assertNotIn("NumMissions", locked_only)
        self.assertNotIn("IndexOf", locked_only)
        self.assertNotIn("IdAt", locked_only)
        self.assertNotIn("LoadoutLabel", locked_only)
        self.assertNotIn(
            "const FSkyguardCampaignMissionSpec& Get(int32 Index);",
            locked_only,
        )

    def test_contract_parses_namespace_not_struct_or_cpp(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertNotIn("struct FSkyguardCampaignMissionSpec", body)
        self.assertNotIn("enum class ESkyguardMissionWeather", body)
        self.assertNotIn("float BeatSeconds[7]", body)
        self.assertNotIn("Harbor Breaker proof clock", body)
        self.assertEqual(
            require_declaration(body, WEATHER_ENUM_LABEL),
            WEATHER_ENUM_LABEL,
        )
        self.assertNotIn("SkyguardCampaignRoster.cpp", body)
        self.assertNotIn("SkyguardCampaignRoster::WeatherEnumLabel", body)
        self.assertNotIn("switch (Weather)", body)
        self.assertNotIn("TEXT(", body)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
            self.assertNotIn(token, body)
        self.assertNotIn("SkyguardCampaignRoster.cpp", body)
        self.assertNotIn("SkyguardCampaignRoster::WeatherEnumLabel", body)
        self.assertNotIn("return TEXT(", body)
        self.assertNotIn("switch (Weather)", body)
        self.assertNotIn("{", WEATHER_ENUM_LABEL)
        self.assertNotIn("}", WEATHER_ENUM_LABEL)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = namespace_body(origin_main_header())
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)
        self.assertNotIn("Harbor Breaker proof clock", body)
        self.assertNotIn("float BeatSeconds[7]", body)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        body = namespace_body(origin_main_header())
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            "40.f, 80.f",
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
            self.assertNotIn(token, body)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(WEATHER_ENUM_LABEL, "Rifle")
        self.assertNotEqual(WEATHER_ENUM_LABEL, "Igla")
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", body)
        self.assertNotIn("ASkyguardIglaMissile", body)

    def test_declaration_bans_igla_yak_rifle(self) -> None:
        body = namespace_body(origin_main_header())
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"campaign roster WeatherEnumLabel contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not leftover live copy",
            )
            self.assertNotIn(banned, WEATHER_ENUM_LABEL.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        body = namespace_body(header)
        self.assertNotIn("D:\\Skyguard52", body)
        self.assertNotIn("D:/Skyguard52", WEATHER_ENUM_LABEL)

    def test_locked_scripts_list_sibling_isolated_contracts(self) -> None:
        self.assertIn(
            "Scripts/tests/test_campaign_roster_lookup_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_campaign_roster_get_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_campaign_roster_id_at_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_campaign_roster_loadout_label_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission_weather_enum_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_campaign_save_empty_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_cpg_debrief_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_apache_own_ship_systems_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_gunship_weapon_stations_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_pilot_command_roster_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_settings_apply_broadcast_tests.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn(
            "Scripts/tests/test_campaign_roster_weather_enum_label_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_is_weather_enum_label_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(
            require_declaration(body, WEATHER_ENUM_LABEL),
            WEATHER_ENUM_LABEL,
        )
        locked_only = f"{WEATHER_ENUM_LABEL}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER_ENUM_LABEL)
        self.assertNotIn("NumMissions", locked_only)
        self.assertNotIn("IndexOf", locked_only)
        self.assertNotIn("IdAt", locked_only)
        self.assertNotIn("LoadoutLabel", locked_only)
        self.assertNotIn(
            "const FSkyguardCampaignMissionSpec& Get(int32 Index);",
            locked_only,
        )
        for token in SPEC_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        for token in HARBOR_PROOF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        for token in WEATHER_ENUM_BODY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        for token in INVENTED_LABELS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        for token in LEFTOVER_CAMPAIGN_SAVE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        for token in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
            self.assertNotIn(token, body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, WEATHER_ENUM_LABEL)
            self.assertNotIn(token, body)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("return ", WEATHER_ENUM_LABEL)
        self.assertNotIn("{", WEATHER_ENUM_LABEL)
        self.assertNotIn("BeatSeconds", locked_only)
        self.assertNotIn("Harbor Breaker proof clock", locked_only)
        self.assertNotEqual(WEATHER_ENUM_LABEL, "Rifle")
        self.assertNotEqual(WEATHER_ENUM_LABEL, "Igla")
        self.assertNotIn("ApplyHydraForClusters", body)
        self.assertNotIn("FillResultCombatStats", body)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("enum class ESkyguardMissionWeather", body)
        self.assertNotIn("TEXT(", WEATHER_ENUM_LABEL)
        self.assertNotIn("switch (Weather)", body)

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
