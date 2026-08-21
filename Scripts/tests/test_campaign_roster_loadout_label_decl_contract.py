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
# returned label string, or lock the LoadoutLabel body
# in the .cpp. origin/main is one line
# (`const TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);`);
# accept that form and other split-line wraps.
LOADOUT_LABEL = "const TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);"
# Leftover #56–#64 plus CampaignRoster production sources.
# This lane only adds an isolated Python LoadoutLabel
# declaration contract. Stay off leftover campaign-roster
# lookup #111 (IndexOf), leftover NumMissions sibling draft
# this wave, leftover Get / IdAt siblings in-flight,
# leftover WeatherEnumLabel, leftover campaign-save
# empty-fail-closed, LoadCampaignProgressAfterConfigure
# (#290), leftover loadout #8/#114/#154 files, leftover
# gunship loadout/lock-phase, leftover weather enum
# contracts, leftover CPG debrief #284/#195/#130/#8ccd,
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
# this wave. Do not lock NumMissions, Get, IdAt, IndexOf,
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
# campaign-roster lookup, leftover NumMissions sibling,
# leftover Get / IdAt siblings, leftover campaign-save
# empty-fail-closed, leftover LoadCampaignProgressAfterConfigure,
# leftover CPG debrief copy / snapshot / fail-closed,
# leftover loadout #8/#114/#154 / lock-phase / weather enum,
# leftover theater-kit / Harbor / flare/HUD, leftover
# settings invert-look / ApplySettings broadcast, leftover
# ApacheSystem / weapon stations / pilot commands, and
# in-flight DeleteCampaignSlot / ValidateDefinition /
# LoadCampaignFromSlot siblings stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
    "Scripts/tests/test_campaign_roster_get_decl_contract.py",
    "Scripts/tests/test_campaign_roster_id_at_decl_contract.py",
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
    "Scripts/tests/test_resolve_loadout_decl_contract.py",
    "Scripts/tests/test_loadout_display_name_contract.py",
    "Scripts/tests/test_loadout_slot_helpers_contract.py",
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
# leftover campaign-roster lookup #111 owns IndexOf.
# NumMissions is a sibling draft this wave. Get / IdAt are
# siblings in-flight. WeatherEnumLabel stays unlocked.
UNLOCKED_NEIGHBORS = (
    "int32 NumMissions();",
    "const FSkyguardCampaignMissionSpec& Get(int32 Index);",
    "int32 IndexOf(FName MissionId);",
    "FName IdAt(int32 Index);",
    "const TCHAR* WeatherEnumLabel(ESkyguardMissionWeather Weather);",
)
NUM_MISSIONS_NOT_LOCKED = "int32 NumMissions();"
INDEX_OF_NOT_LOCKED = "int32 IndexOf(FName MissionId);"
GET_NOT_LOCKED = "const FSkyguardCampaignMissionSpec& Get(int32 Index);"
ID_AT_NOT_LOCKED = "FName IdAt(int32 Index);"
WEATHER_ENUM_LABEL_NOT_LOCKED = (
    "const TCHAR* WeatherEnumLabel(ESkyguardMissionWeather Weather);"
)
# Leftover loadout #8/#114/#154 files stay unlocked. Do not
# lock leftover gunship loadout / lock-phase helpers.
LEFTOVER_LOADOUT_FILES = (
    "SkyguardCpgDebriefLoadoutTests.cpp",
    "SkyguardGunshipTypesLoadoutTests.cpp",
    "SkyguardCpgLoadoutSlot34Tests.cpp",
    "SkyguardCpgDebrief.cpp",
    "SkyguardCpgDebrief.h",
    "SkyguardGunshipTypes.cpp",
    "SkyguardGunshipTypes.h",
    "SkyguardSortiePresentationComponent.cpp",
    "SkyguardSortiePresentationComponent.h",
    "SkyguardSortiePresentationWidgets.cpp",
    "SkyguardSortiePresentationWidgets.h",
    "SkyguardGunshipSortieDirector.cpp",
    "SkyguardGunshipSortieDirector.h",
)
LEFTOVER_LOADOUT_LOCK_PHASE_NOT_LOCKED = (
    "enum class ESkyguardLoadout",
    "enum class ESkyguardGuidedLockPhase",
    "FSkyguardLoadoutSpec",
    "SkyguardResolveLoadout",
    "SkyguardLoadoutFromSlot",
    "SkyguardLoadoutSlot",
    "SkyguardLoadoutDisplayName",
    "ESkyguardGuidedLockPhase",
)
# .cpp TEXT payloads / invented returned labels stay
# unlocked. Do not invent the actual label strings.
LABEL_STRINGS_NOT_LOCKED = (
    "Anti-Armor",
    "Rocket Heavy",
    "Intercept",
    "Balanced",
    'return TEXT("',
    "TEXT(",
    "TEXT(\"Anti-Armor\")",
    "TEXT(\"Rocket Heavy\")",
    "TEXT(\"Intercept\")",
    "TEXT(\"Balanced\")",
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
# Leftover #147 / #149 / #152 / #290 / Hydra cluster
# apply / leftover Gunner FillAnd* stay unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardPilotCommand",
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
# .cpp LoadoutLabel body / invented returned label strings
# stay unlocked. Do not invent INDEX_NONE or lock the
# cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return 0",
    "return -1",
    "return TEXT(",
    "switch (Loadout)",
    "default:",
    "GMissions",
    "SkyguardCampaignRoster::LoadoutLabel",
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


class CampaignRosterLoadoutLabelDeclContractTests(unittest.TestCase):
    def test_campaign_roster_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertTrue(has_declaration(body, LOADOUT_LABEL), body)
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

    def test_missing_loadout_label_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "\tint32 NumMissions();\n"
            "\tconst FSkyguardCampaignMissionSpec& Get(int32 Index);\n"
            "\tint32 IndexOf(FName MissionId);\n"
            "\tFName IdAt(int32 Index);\n"
            "\tconst TCHAR* WeatherEnumLabel("
            "ESkyguardMissionWeather Weather);\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, LOADOUT_LABEL)
        self.assertIn("LoadoutLabel", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        neighbors_only = (
            "{\n"
            "\tint32 NumMissions();\n"
            "\tconst FSkyguardCampaignMissionSpec& Get(int32 Index);\n"
            "\tint32 IndexOf(FName MissionId);\n"
            "\tFName IdAt(int32 Index);\n"
            "\tconst TCHAR* WeatherEnumLabel("
            "ESkyguardMissionWeather Weather);\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, LOADOUT_LABEL)
        self.assertIn("LoadoutLabel", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_arg = "{\n\tconst TCHAR* LoadoutLabel();\n}\n"
        wrong_arg = "{\n\tconst TCHAR* LoadoutLabel(int32 Loadout);\n}\n"
        wrong_return = (
            "{\n\tFString LoadoutLabel(ESkyguardLoadout Loadout);\n}\n"
        )
        const_method = (
            "{\n\tconst TCHAR* LoadoutLabel("
            "ESkyguardLoadout Loadout) const;\n}\n"
        )
        named_get = (
            "{\n\tconst TCHAR* GetLoadoutLabel("
            "ESkyguardLoadout Loadout);\n}\n"
        )
        for region in (
            missing_arg,
            wrong_arg,
            wrong_return,
            const_method,
            named_get,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOADOUT_LABEL)
            self.assertIn("LoadoutLabel", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_loadout_label_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(body, LOADOUT_LABEL),
            LOADOUT_LABEL,
        )
        self.assertTrue(has_declaration(body, LOADOUT_LABEL))
        self.assertEqual(declaration_count(body, LOADOUT_LABEL), 1)
        self.assertTrue(LOADOUT_LABEL.endswith(";"), LOADOUT_LABEL)
        self.assertTrue(LOADOUT_LABEL.startswith("const TCHAR* "), LOADOUT_LABEL)
        self.assertNotIn("INDEX_NONE", LOADOUT_LABEL)
        self.assertNotIn("return ", LOADOUT_LABEL)
        self.assertNotIn("{", LOADOUT_LABEL)
        self.assertNotIn("}", LOADOUT_LABEL)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "{\n"
            "\tconst TCHAR*\n"
            "\tLoadoutLabel(ESkyguardLoadout Loadout);\n"
            "}\n"
        )
        wrap_args = (
            "{\n"
            "\tconst TCHAR* LoadoutLabel(\n"
            "\tESkyguardLoadout Loadout);\n"
            "}\n"
        )
        wrap_name = (
            "{\n"
            "\tconst TCHAR*\n"
            "\tLoadoutLabel(\n"
            "\tESkyguardLoadout Loadout);\n"
            "}\n"
        )
        self.assertTrue(has_declaration(wrap_type, LOADOUT_LABEL), wrap_type)
        self.assertTrue(has_declaration(wrap_args, LOADOUT_LABEL), wrap_args)
        self.assertTrue(has_declaration(wrap_name, LOADOUT_LABEL), wrap_name)
        self.assertEqual(
            require_declaration(wrap_type, LOADOUT_LABEL),
            LOADOUT_LABEL,
        )
        self.assertEqual(
            require_declaration(wrap_args, LOADOUT_LABEL),
            LOADOUT_LABEL,
        )
        self.assertEqual(
            require_declaration(wrap_name, LOADOUT_LABEL),
            LOADOUT_LABEL,
        )
        self.assertEqual(declaration_count(wrap_type, LOADOUT_LABEL), 1)
        self.assertEqual(declaration_count(wrap_args, LOADOUT_LABEL), 1)
        self.assertEqual(declaration_count(wrap_name, LOADOUT_LABEL), 1)
        one_line = f"{{\n\t{LOADOUT_LABEL}\n}}\n"
        self.assertTrue(has_declaration(one_line, LOADOUT_LABEL))
        body = namespace_body(origin_main_header())
        self.assertTrue(has_declaration(body, LOADOUT_LABEL), body)
        self.assertEqual(
            require_declaration(body, LOADOUT_LABEL),
            LOADOUT_LABEL,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", LOADOUT_LABEL)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", LOADOUT_LABEL)
        body = namespace_body(origin_main_header())
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)

    def test_declaration_does_not_invent_returned_label_string(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        self.assertNotIn("return ", LOADOUT_LABEL)
        self.assertNotIn("return TEXT(", LOADOUT_LABEL)
        self.assertNotIn("TEXT(", LOADOUT_LABEL)
        for token in LABEL_STRINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        body = namespace_body(origin_main_header())
        self.assertNotIn("return ", body)
        self.assertNotIn("TEXT(", body)
        self.assertNotIn("Anti-Armor", body)
        self.assertNotIn("Rocket Heavy", body)

    def test_contract_does_not_lock_loadout_label_cpp_body(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        self.assertNotIn("{", LOADOUT_LABEL)
        self.assertNotIn("}", LOADOUT_LABEL)
        self.assertNotIn("return ", LOADOUT_LABEL)
        self.assertNotIn(
            "SkyguardCampaignRoster::LoadoutLabel",
            LOADOUT_LABEL,
        )
        self.assertNotIn("SkyguardCampaignRoster.cpp", LOADOUT_LABEL)
        self.assertNotIn("SkyguardCampaignRoster.cpp", locked_only)
        self.assertNotIn("switch (Loadout)", LOADOUT_LABEL)
        self.assertNotIn("switch (Loadout)", locked_only)
        self.assertNotIn("return TEXT(", LOADOUT_LABEL)
        self.assertNotIn("default:", LOADOUT_LABEL)
        self.assertNotIn("GMissions", LOADOUT_LABEL)

    def test_contract_does_not_relock_num_missions(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        self.assertEqual(
            require_declaration(locked_only, LOADOUT_LABEL),
            LOADOUT_LABEL,
        )
        self.assertNotIn(NUM_MISSIONS_NOT_LOCKED, locked_only)
        self.assertNotIn(NUM_MISSIONS_NOT_LOCKED, LOADOUT_LABEL)
        self.assertNotIn("NumMissions", LOADOUT_LABEL)
        self.assertNotIn("NumMissions", locked_only)

    def test_contract_does_not_relock_index_of(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        self.assertEqual(
            require_declaration(locked_only, LOADOUT_LABEL),
            LOADOUT_LABEL,
        )
        self.assertNotIn(INDEX_OF_NOT_LOCKED, locked_only)
        self.assertNotIn(INDEX_OF_NOT_LOCKED, LOADOUT_LABEL)
        self.assertNotIn("IndexOf", LOADOUT_LABEL)
        self.assertNotIn("IndexOf", locked_only)

    def test_contract_does_not_relock_get(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        self.assertNotIn(GET_NOT_LOCKED, locked_only)
        self.assertNotIn(GET_NOT_LOCKED, LOADOUT_LABEL)
        self.assertNotIn("FSkyguardCampaignMissionSpec& Get", LOADOUT_LABEL)
        self.assertNotIn("FSkyguardCampaignMissionSpec& Get", locked_only)

    def test_contract_does_not_relock_id_at(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        self.assertNotIn(ID_AT_NOT_LOCKED, locked_only)
        self.assertNotIn(ID_AT_NOT_LOCKED, LOADOUT_LABEL)
        self.assertNotIn("IdAt", LOADOUT_LABEL)
        self.assertNotIn("IdAt", locked_only)

    def test_contract_does_not_relock_weather_enum_label(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        self.assertNotIn(WEATHER_ENUM_LABEL_NOT_LOCKED, locked_only)
        self.assertNotIn(WEATHER_ENUM_LABEL_NOT_LOCKED, LOADOUT_LABEL)
        self.assertNotIn("WeatherEnumLabel", LOADOUT_LABEL)
        self.assertNotIn("WeatherEnumLabel", locked_only)
        self.assertNotIn("ESkyguardMissionWeather", LOADOUT_LABEL)
        self.assertNotIn("ESkyguardMissionWeather", locked_only)

    def test_contract_does_not_relock_leftover_loadout_files(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        for name in LEFTOVER_LOADOUT_FILES:
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, LOADOUT_LABEL)
        self.assertNotIn("SkyguardGunshipTypesLoadoutTests.cpp", LOADOUT_LABEL)
        self.assertNotIn("SkyguardCpgDebriefLoadoutTests.cpp", locked_only)
        self.assertNotIn("test_gunship_loadout_lock_phase_contract.py", locked_only)
        self.assertNotIn("test_gunship_types_loadout_tests.py", LOADOUT_LABEL)

    def test_contract_does_not_relock_leftover_loadout_lock_phase(
        self,
    ) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        for token in LEFTOVER_LOADOUT_LOCK_PHASE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        self.assertNotIn("enum class ESkyguardLoadout", LOADOUT_LABEL)
        self.assertNotIn("ESkyguardGuidedLockPhase", locked_only)
        self.assertNotIn("SkyguardResolveLoadout", LOADOUT_LABEL)
        self.assertNotIn("SkyguardLoadoutDisplayName", locked_only)
        self.assertNotIn("FSkyguardLoadoutSpec", LOADOUT_LABEL)

    def test_contract_does_not_relock_spec_fields(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        for token in SPEC_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        for token in BEAT_SECONDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        body = namespace_body(origin_main_header())
        self.assertNotIn("float BeatSeconds[7]", body)
        self.assertNotIn("Harbor Breaker proof clock", body)
        self.assertNotIn("struct FSkyguardCampaignMissionSpec", body)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        self.assertNotIn("ApplyHydraForClusters", LOADOUT_LABEL)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ASkyguardGunner", LOADOUT_LABEL)

    def test_contract_does_not_relock_in_flight_siblings(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        for token in IN_FLIGHT_SIBLINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        self.assertNotIn("DeleteCampaignSlot", LOADOUT_LABEL)
        self.assertNotIn("ValidateDefinition", LOADOUT_LABEL)
        self.assertNotIn("LoadCampaignFromSlot", LOADOUT_LABEL)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        self.assertEqual(
            require_declaration(locked_only, LOADOUT_LABEL),
            LOADOUT_LABEL,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, LOADOUT_LABEL)
        self.assertNotIn("NumMissions", LOADOUT_LABEL)
        self.assertNotIn("IndexOf", LOADOUT_LABEL)
        self.assertNotIn("IdAt", LOADOUT_LABEL)
        self.assertNotIn("WeatherEnumLabel", LOADOUT_LABEL)
        self.assertNotIn("NumMissions", locked_only)
        self.assertNotIn("IndexOf", locked_only)
        self.assertNotIn("IdAt", locked_only)
        self.assertNotIn("WeatherEnumLabel", locked_only)

    def test_contract_parses_namespace_not_struct_or_cpp(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertNotIn("struct FSkyguardCampaignMissionSpec", body)
        self.assertNotIn("float BeatSeconds[7]", body)
        self.assertEqual(
            require_declaration(body, LOADOUT_LABEL),
            LOADOUT_LABEL,
        )
        self.assertNotIn("SkyguardCampaignRoster.cpp", body)
        self.assertNotIn("TEXT(", body)
        self.assertNotIn("switch (Loadout)", body)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, LOADOUT_LABEL)
            self.assertNotIn(token, body)
        self.assertNotIn("SkyguardCampaignRoster.cpp", body)
        self.assertNotIn("SkyguardCampaignRoster::LoadoutLabel", body)
        self.assertNotIn("return TEXT(\"Anti-Armor\");", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = namespace_body(origin_main_header())
        locked_only = f"{LOADOUT_LABEL}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
            self.assertNotIn(token, LOADOUT_LABEL)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
            self.assertNotIn(token, LOADOUT_LABEL)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{LOADOUT_LABEL}\n"
        body = namespace_body(origin_main_header())
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            "40.f, 80.f",
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
            self.assertNotIn(token, body)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(LOADOUT_LABEL, "Rifle")
        self.assertNotEqual(LOADOUT_LABEL, "Igla")
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
                f"campaign roster LoadoutLabel contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not leftover live copy",
            )
            self.assertNotIn(banned, LOADOUT_LABEL.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        body = namespace_body(header)
        self.assertNotIn("D:\\Skyguard52", body)
        self.assertNotIn("D:/Skyguard52", LOADOUT_LABEL)

    def test_contract_is_loadout_label_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(
            require_declaration(body, LOADOUT_LABEL),
            LOADOUT_LABEL,
        )
        locked_only = f"{LOADOUT_LABEL}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, LOADOUT_LABEL)
        self.assertNotIn("NumMissions", locked_only)
        self.assertNotIn("IndexOf", locked_only)
        self.assertNotIn("IdAt", locked_only)
        self.assertNotIn("WeatherEnumLabel", locked_only)
        self.assertNotIn("FSkyguardCampaignMissionSpec& Get", locked_only)
        for token in SPEC_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        for token in BEAT_SECONDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        for token in IN_FLIGHT_SIBLINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        for token in LEFTOVER_LOADOUT_LOCK_PHASE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        for token in LABEL_STRINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        for token in LEFTOVER_LOADOUT_FILES:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOADOUT_LABEL)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, LOADOUT_LABEL)
            self.assertNotIn(token, body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, LOADOUT_LABEL)
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
        self.assertNotIn("return ", LOADOUT_LABEL)
        self.assertNotIn("{", LOADOUT_LABEL)
        self.assertNotIn("TEXT(", LOADOUT_LABEL)
        self.assertNotEqual(LOADOUT_LABEL, "Rifle")
        self.assertNotEqual(LOADOUT_LABEL, "Igla")
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
