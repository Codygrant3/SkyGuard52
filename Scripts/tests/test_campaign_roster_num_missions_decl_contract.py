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
# mission-count return value, or lock the NumMissions body
# in the .cpp. origin/main is one line
# (`int32 NumMissions();`); accept that form and other
# split-line wraps.
NUM_MISSIONS = "int32 NumMissions();"
# Leftover #56–#64 plus CampaignRoster production sources.
# This lane only adds an isolated Python NumMissions
# declaration contract. Stay off leftover campaign-roster
# lookup #111 (IndexOf), leftover campaign-save
# empty-fail-closed, LoadCampaignProgressAfterConfigure
# (#290), leftover loadout #8/#114/#154, leftover weather
# enum contracts, leftover CPG debrief #284/#195/#130/#8ccd,
# FillResultCombatStats / FillAndFinalize / FillAndFail /
# ApplyHydraForClusters (leftover ASkyguardGunner*), leftover
# Harbor #6/#8/#9, leftover theater-kit #59, leftover
# flare/HUD #57/#61/#62, leftover drafts #56–#64, leftover
# #147 ApacheSystem, leftover #149 weapon stations,
# leftover #152 pilot commands, leftover settings
# invert-look / ApplySettings broadcast #134, Harbor
# IncomingRadar 40/80, leftover live copy,
# FSkyguardMission0NIntegrationReadiness (bYakRuntimeReady),
# dirty D:\Skyguard52, and in-flight DeleteCampaignSlot /
# ValidateDefinition / LoadCampaignFromSlot sibling drafts
# this wave. Do not lock Get, IdAt, LoadoutLabel,
# WeatherEnumLabel, FSkyguardCampaignMissionSpec fields,
# BeatSeconds, or Harbor Breaker proof-clock comments.
LOCKED = {
    "SkyguardCampaignRoster.h",
    "SkyguardCampaignRoster.cpp",
    "SkyguardCampaignRosterLookupTests.cpp",
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
# campaign-roster lookup, leftover campaign-save
# empty-fail-closed, leftover LoadCampaignProgressAfterConfigure,
# leftover CPG debrief copy / snapshot / fail-closed,
# leftover loadout / weather enum, leftover theater-kit /
# Harbor / flare/HUD, leftover settings invert-look /
# ApplySettings broadcast, leftover ApacheSystem / weapon
# stations / pilot commands, and in-flight
# DeleteCampaignSlot / ValidateDefinition /
# LoadCampaignFromSlot siblings stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
    "Scripts/tests/test_get_active_mission_decl_contract.py",
    "Scripts/tests/test_configure_campaign_decl_contract.py",
    "Scripts/tests/test_can_start_mission_decl_contract.py",
    "Scripts/tests/test_start_mission_decl_contract.py",
    "Scripts/tests/test_is_mission_unlocked_decl_contract.py",
    "Scripts/tests/test_is_valid_campaign_slot_name_decl_contract.py",
    "Scripts/tests/test_get_earned_campaign_medals_decl_contract.py",
    "Scripts/tests/test_acknowledge_debrief_decl_contract.py",
    "Scripts/tests/test_can_travel_to_next_mission_decl_contract.py",
    "Scripts/tests/test_get_next_mission_map_package_name_decl_contract.py",
    "Scripts/tests/test_travel_to_next_mission_decl_contract.py",
    "Scripts/tests/test_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_get_active_mission_elapsed_seconds_decl_contract.py",
    "Scripts/tests/test_add_objective_progress_decl_contract.py",
    "Scripts/tests/test_fail_objective_decl_contract.py",
    "Scripts/tests/test_complete_survive_objective_if_intact_decl_contract.py",
    "Scripts/tests/test_complete_active_mission_decl_contract.py",
    "Scripts/tests/test_finalize_active_mission_decl_contract.py",
    "Scripts/tests/test_fail_active_mission_decl_contract.py",
    "Scripts/tests/test_get_route_runtime_decl_contract.py",
    "Scripts/tests/test_calculate_mission_score_decl_contract.py",
    "Scripts/tests/test_calculate_medal_tier_decl_contract.py",
    "Scripts/tests/test_apply_save_game_decl_contract.py",
    "Scripts/tests/test_build_save_game_decl_contract.py",
    "Scripts/tests/test_save_campaign_to_slot_decl_contract.py",
    "Scripts/tests/test_delete_campaign_slot_decl_contract.py",
    "Scripts/tests/test_load_campaign_from_slot_decl_contract.py",
    "Scripts/tests/test_validate_definition_decl_contract.py",
    "Scripts/tests/test_retry_save_last_debrief_decl_contract.py",
    "Scripts/tests/test_get_mission_records_decl_contract.py",
    "Scripts/tests/test_objective_runtime_fail_closed.py",
    "Scripts/tests/test_objective_runtime_empty_fail_closed.py",
    "Scripts/tests/test_objective_runtime_fail_closed_contract.py",
    "Scripts/tests/test_route_runtime_fail_closed.py",
    "Scripts/tests/test_route_runtime_empty_fail_closed.py",
    "Scripts/tests/test_route_runtime_fail_closed_contract.py",
    "Scripts/tests/test_cpg_debrief_copy_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_campaign_sortie_flow_contract.py",
    "Scripts/tests/test_m09_campaign_handoff_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_gunship_weapon_stations_contract.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
    "Scripts/tests/test_gunship_types_loadout_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
# leftover campaign-roster lookup #111 owns IndexOf.
UNLOCKED_NEIGHBORS = (
    "const FSkyguardCampaignMissionSpec& Get(int32 Index);",
    "int32 IndexOf(FName MissionId);",
    "FName IdAt(int32 Index);",
    "const TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);",
    "const TCHAR* WeatherEnumLabel(ESkyguardMissionWeather Weather);",
)
INDEX_OF_NOT_LOCKED = "int32 IndexOf(FName MissionId);"
GET_NOT_LOCKED = "const FSkyguardCampaignMissionSpec& Get(int32 Index);"
ID_AT_NOT_LOCKED = "FName IdAt(int32 Index);"
LOADOUT_LABEL_NOT_LOCKED = (
    "const TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);"
)
WEATHER_ENUM_LABEL_NOT_LOCKED = (
    "const TCHAR* WeatherEnumLabel(ESkyguardMissionWeather Weather);"
)
# FSkyguardCampaignMissionSpec fields / BeatSeconds /
# Harbor Breaker proof-clock comments stay unlocked.
SPEC_FIELDS_NOT_LOCKED = (
    "struct FSkyguardCampaignMissionSpec",
    "FName MissionId;",
    "const TCHAR* Title",
    "const TCHAR* Brief",
    "const TCHAR* Success",
    "const TCHAR* Failure",
    "ESkyguardMissionWeather Weather",
    "FName WeatherIdentity;",
    "const TCHAR* WeatherLabel",
    "float TimeOfDayHours",
    "float BeatSeconds[7]",
    "ESkyguardThreatKind ContactKind",
    "ESkyguardThreatKind ShoreKind",
    "ESkyguardThreatKind SupportKind",
    "ESkyguardThreatKind ExtractKind",
    "ESkyguardClimaxKind Climax",
    "bool bNightIdentity",
    "bool bStormRocketContract",
)
BEAT_SECONDS_NOT_LOCKED = (
    "float BeatSeconds[7]",
    "120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f",
    "Harbor Breaker proof clock",
)
# Leftover CPG debrief copy #284 / snapshot defaults #195 /
# fail-closed #8ccd / empty-capture #130 stay unlocked.
LEFTOVER_CPG_DEBRIEF_NOT_LOCKED = (
    "SkyguardBuildCpgDebriefCopy",
    "SkyguardCpgCopyHasBannedTerm",
    "SkyguardCaptureCpgDebrief",
    "FSkyguardCpgDebriefSnapshot",
)
# Leftover #147 / #149 / #152 / #154 / #290 / Hydra cluster
# apply / leftover Gunner FillAnd* stay unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "LoadCampaignProgressAfterConfigure",
    "FillResultCombatStats",
    "FillAndFinalize",
    "FillAndFail",
    "ValidateDefinition",
    "DeleteCampaignSlot",
    "LoadCampaignFromSlot",
)
# In-flight DeleteCampaignSlot / ValidateDefinition /
# LoadCampaignFromSlot sibling drafts this wave stay unlocked.
IN_FLIGHT_SIBLINGS_NOT_LOCKED = (
    "bool DeleteCampaignSlot(",
    "bool ValidateDefinition(",
    "bool LoadCampaignFromSlot(",
)
# .cpp NumMissions body / invented mission-count return
# values stay unlocked. Do not invent INDEX_NONE or lock
# the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return 0",
    "return -1",
    "return 10",
    "UE_ARRAY_COUNT",
    "GMissions",
    "SkyguardCampaignRoster::NumMissions",
    "SkyguardCampaignRoster.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "ASkyguardIglaMissile",
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


class CampaignRosterNumMissionsDeclContractTests(unittest.TestCase):
    def test_campaign_roster_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertTrue(has_declaration(body, NUM_MISSIONS), body)
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

    def test_missing_num_missions_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "\tconst FSkyguardCampaignMissionSpec& Get(int32 Index);\n"
            "\tint32 IndexOf(FName MissionId);\n"
            "\tFName IdAt(int32 Index);\n"
            "\tconst TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);\n"
            "\tconst TCHAR* WeatherEnumLabel("
            "ESkyguardMissionWeather Weather);\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, NUM_MISSIONS)
        self.assertIn("NumMissions", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        neighbors_only = (
            "{\n"
            "\tconst FSkyguardCampaignMissionSpec& Get(int32 Index);\n"
            "\tint32 IndexOf(FName MissionId);\n"
            "\tFName IdAt(int32 Index);\n"
            "\tconst TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);\n"
            "\tconst TCHAR* WeatherEnumLabel("
            "ESkyguardMissionWeather Weather);\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, NUM_MISSIONS)
        self.assertIn("NumMissions", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        with_index = "{\n\tint32 NumMissions(int32 Index);\n}\n"
        wrong_return = "{\n\tint64 NumMissions();\n}\n"
        const_method = "{\n\tint32 NumMissions() const;\n}\n"
        named_get = "{\n\tint32 GetNumMissions();\n}\n"
        for region in (with_index, wrong_return, const_method, named_get):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, NUM_MISSIONS)
            self.assertIn("NumMissions", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_num_missions_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(body, NUM_MISSIONS),
            NUM_MISSIONS,
        )
        self.assertTrue(has_declaration(body, NUM_MISSIONS))
        self.assertEqual(declaration_count(body, NUM_MISSIONS), 1)
        self.assertTrue(NUM_MISSIONS.endswith(";"), NUM_MISSIONS)
        self.assertTrue(NUM_MISSIONS.startswith("int32 "), NUM_MISSIONS)
        self.assertNotIn("INDEX_NONE", NUM_MISSIONS)
        self.assertNotIn("return ", NUM_MISSIONS)
        self.assertNotIn("{", NUM_MISSIONS)
        self.assertNotIn("}", NUM_MISSIONS)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "{\n"
            "\tint32\n"
            "\tNumMissions();\n"
            "}\n"
        )
        wrap_args = (
            "{\n"
            "\tint32 NumMissions(\n"
            "\t);\n"
            "}\n"
        )
        wrap_name = (
            "{\n"
            "\tint32\n"
            "\tNumMissions(\n"
            "\t);\n"
            "}\n"
        )
        self.assertTrue(has_declaration(wrap_type, NUM_MISSIONS), wrap_type)
        self.assertTrue(has_declaration(wrap_args, NUM_MISSIONS), wrap_args)
        self.assertTrue(has_declaration(wrap_name, NUM_MISSIONS), wrap_name)
        self.assertEqual(
            require_declaration(wrap_type, NUM_MISSIONS),
            NUM_MISSIONS,
        )
        self.assertEqual(
            require_declaration(wrap_args, NUM_MISSIONS),
            NUM_MISSIONS,
        )
        self.assertEqual(
            require_declaration(wrap_name, NUM_MISSIONS),
            NUM_MISSIONS,
        )
        self.assertEqual(declaration_count(wrap_type, NUM_MISSIONS), 1)
        self.assertEqual(declaration_count(wrap_args, NUM_MISSIONS), 1)
        self.assertEqual(declaration_count(wrap_name, NUM_MISSIONS), 1)
        one_line = f"{{\n\t{NUM_MISSIONS}\n}}\n"
        self.assertTrue(has_declaration(one_line, NUM_MISSIONS))
        body = namespace_body(origin_main_header())
        self.assertTrue(has_declaration(body, NUM_MISSIONS), body)
        self.assertEqual(
            require_declaration(body, NUM_MISSIONS),
            NUM_MISSIONS,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", NUM_MISSIONS)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", NUM_MISSIONS)
        body = namespace_body(origin_main_header())
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)

    def test_declaration_does_not_invent_mission_count_return_value(
        self,
    ) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        self.assertNotIn("return ", NUM_MISSIONS)
        self.assertNotIn("return 0", NUM_MISSIONS)
        self.assertNotIn("return 10", NUM_MISSIONS)
        self.assertNotIn("return -1", NUM_MISSIONS)
        self.assertNotIn("UE_ARRAY_COUNT", NUM_MISSIONS)
        self.assertNotIn("GMissions", NUM_MISSIONS)
        self.assertNotIn("return 0", locked_only)
        self.assertNotIn("return 10", locked_only)
        self.assertNotIn("UE_ARRAY_COUNT", locked_only)
        self.assertNotIn("GMissions", locked_only)
        body = namespace_body(origin_main_header())
        self.assertNotIn("return ", body)
        self.assertNotIn("UE_ARRAY_COUNT", body)
        self.assertNotIn("GMissions", body)
        self.assertNotIn("return 10", body)

    def test_contract_does_not_lock_num_missions_cpp_body(self) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        self.assertNotIn("{", NUM_MISSIONS)
        self.assertNotIn("}", NUM_MISSIONS)
        self.assertNotIn("return ", NUM_MISSIONS)
        self.assertNotIn(
            "SkyguardCampaignRoster::NumMissions",
            NUM_MISSIONS,
        )
        self.assertNotIn("SkyguardCampaignRoster.cpp", NUM_MISSIONS)
        self.assertNotIn("SkyguardCampaignRoster.cpp", locked_only)
        self.assertNotIn("UE_ARRAY_COUNT", NUM_MISSIONS)
        self.assertNotIn("GMissions", NUM_MISSIONS)
        self.assertNotIn("return UE_ARRAY_COUNT(GMissions);", NUM_MISSIONS)

    def test_contract_does_not_relock_index_of(self) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        self.assertEqual(
            require_declaration(locked_only, NUM_MISSIONS),
            NUM_MISSIONS,
        )
        self.assertNotIn(INDEX_OF_NOT_LOCKED, locked_only)
        self.assertNotIn(INDEX_OF_NOT_LOCKED, NUM_MISSIONS)
        self.assertNotIn("IndexOf", NUM_MISSIONS)
        self.assertNotIn("IndexOf", locked_only)

    def test_contract_does_not_relock_get(self) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        self.assertNotIn(GET_NOT_LOCKED, locked_only)
        self.assertNotIn(GET_NOT_LOCKED, NUM_MISSIONS)
        self.assertNotIn("FSkyguardCampaignMissionSpec& Get", NUM_MISSIONS)
        self.assertNotIn("FSkyguardCampaignMissionSpec& Get", locked_only)

    def test_contract_does_not_relock_id_at(self) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        self.assertNotIn(ID_AT_NOT_LOCKED, locked_only)
        self.assertNotIn(ID_AT_NOT_LOCKED, NUM_MISSIONS)
        self.assertNotIn("IdAt", NUM_MISSIONS)
        self.assertNotIn("IdAt", locked_only)

    def test_contract_does_not_relock_loadout_label(self) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        self.assertNotIn(LOADOUT_LABEL_NOT_LOCKED, locked_only)
        self.assertNotIn(LOADOUT_LABEL_NOT_LOCKED, NUM_MISSIONS)
        self.assertNotIn("LoadoutLabel", NUM_MISSIONS)
        self.assertNotIn("LoadoutLabel", locked_only)
        self.assertNotIn("ESkyguardLoadout", NUM_MISSIONS)
        self.assertNotIn("ESkyguardLoadout", locked_only)

    def test_contract_does_not_relock_weather_enum_label(self) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        self.assertNotIn(WEATHER_ENUM_LABEL_NOT_LOCKED, locked_only)
        self.assertNotIn(WEATHER_ENUM_LABEL_NOT_LOCKED, NUM_MISSIONS)
        self.assertNotIn("WeatherEnumLabel", NUM_MISSIONS)
        self.assertNotIn("WeatherEnumLabel", locked_only)
        self.assertNotIn("ESkyguardMissionWeather", NUM_MISSIONS)
        self.assertNotIn("ESkyguardMissionWeather", locked_only)

    def test_contract_does_not_relock_spec_fields_or_beat_seconds(
        self,
    ) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        for token in SPEC_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, NUM_MISSIONS)
        for token in BEAT_SECONDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, NUM_MISSIONS)
        body = namespace_body(origin_main_header())
        self.assertNotIn("float BeatSeconds[7]", body)
        self.assertNotIn("Harbor Breaker proof clock", body)
        self.assertNotIn("struct FSkyguardCampaignMissionSpec", body)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, NUM_MISSIONS)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, NUM_MISSIONS)
        self.assertNotIn("ApplyHydraForClusters", NUM_MISSIONS)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ASkyguardGunner", NUM_MISSIONS)

    def test_contract_does_not_relock_in_flight_siblings(self) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        for token in IN_FLIGHT_SIBLINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, NUM_MISSIONS)
        self.assertNotIn("DeleteCampaignSlot", NUM_MISSIONS)
        self.assertNotIn("ValidateDefinition", NUM_MISSIONS)
        self.assertNotIn("LoadCampaignFromSlot", NUM_MISSIONS)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        self.assertEqual(
            require_declaration(locked_only, NUM_MISSIONS),
            NUM_MISSIONS,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, NUM_MISSIONS)
        self.assertNotIn("IndexOf", NUM_MISSIONS)
        self.assertNotIn("IdAt", NUM_MISSIONS)
        self.assertNotIn("LoadoutLabel", NUM_MISSIONS)
        self.assertNotIn("WeatherEnumLabel", NUM_MISSIONS)
        self.assertNotIn("IndexOf", locked_only)
        self.assertNotIn("IdAt", locked_only)
        self.assertNotIn("LoadoutLabel", locked_only)
        self.assertNotIn("WeatherEnumLabel", locked_only)

    def test_contract_parses_namespace_not_struct_or_cpp(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertNotIn("struct FSkyguardCampaignMissionSpec", body)
        self.assertNotIn("float BeatSeconds[7]", body)
        self.assertEqual(
            require_declaration(body, NUM_MISSIONS),
            NUM_MISSIONS,
        )
        self.assertNotIn("SkyguardCampaignRoster.cpp", body)
        self.assertNotIn("UE_ARRAY_COUNT", body)
        self.assertNotIn("TEXT(", body)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, NUM_MISSIONS)
            self.assertNotIn(token, body)
        self.assertNotIn("SkyguardCampaignRoster.cpp", body)
        self.assertNotIn("SkyguardCampaignRoster::NumMissions", body)
        self.assertNotIn("return UE_ARRAY_COUNT(GMissions);", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = namespace_body(origin_main_header())
        locked_only = f"{NUM_MISSIONS}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
            self.assertNotIn(token, NUM_MISSIONS)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
            self.assertNotIn(token, NUM_MISSIONS)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{NUM_MISSIONS}\n"
        body = namespace_body(origin_main_header())
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            "40.f, 80.f",
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, NUM_MISSIONS)
            self.assertNotIn(token, body)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(NUM_MISSIONS, "Rifle")
        self.assertNotEqual(NUM_MISSIONS, "Igla")
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", body)

    def test_declaration_bans_igla_yak_rifle(self) -> None:
        body = namespace_body(origin_main_header())
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"campaign roster NumMissions contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not leftover live copy",
            )
            self.assertNotIn(banned, NUM_MISSIONS.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        body = namespace_body(header)
        self.assertNotIn("D:\\Skyguard52", body)
        self.assertNotIn("D:/Skyguard52", NUM_MISSIONS)

    def test_contract_is_num_missions_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(
            require_declaration(body, NUM_MISSIONS),
            NUM_MISSIONS,
        )
        locked_only = f"{NUM_MISSIONS}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, NUM_MISSIONS)
        self.assertNotIn("IndexOf", locked_only)
        self.assertNotIn("IdAt", locked_only)
        self.assertNotIn("LoadoutLabel", locked_only)
        self.assertNotIn("WeatherEnumLabel", locked_only)
        self.assertNotIn("FSkyguardCampaignMissionSpec& Get", locked_only)
        for token in SPEC_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, NUM_MISSIONS)
        for token in BEAT_SECONDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, NUM_MISSIONS)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, NUM_MISSIONS)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, NUM_MISSIONS)
        for token in IN_FLIGHT_SIBLINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, NUM_MISSIONS)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, NUM_MISSIONS)
            self.assertNotIn(token, body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, NUM_MISSIONS)
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
        self.assertNotIn("return ", NUM_MISSIONS)
        self.assertNotIn("{", NUM_MISSIONS)
        self.assertNotIn("UE_ARRAY_COUNT", NUM_MISSIONS)
        self.assertNotEqual(NUM_MISSIONS, "Rifle")
        self.assertNotEqual(NUM_MISSIONS, "Igla")
        self.assertNotIn("ApplyHydraForClusters", body)
        self.assertNotIn("float BeatSeconds[7]", body)
        self.assertNotIn("Harbor Breaker proof clock", body)
        self.assertNotIn("struct FSkyguardCampaignMissionSpec", body)

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
