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
# returned mission id, or lock the IdAt body in the .cpp.
# origin/main may wrap as `FName IdAt(` / `int32 Index);`;
# accept that form and other split-line wraps.
ID_AT = "FName IdAt(int32 Index);"
# Leftover #56–#64 plus CampaignRoster production sources.
# This lane only adds an isolated Python IdAt declaration
# contract. Stay off leftover campaign-roster lookup #111
# (IndexOf), NumMissions (sibling in-flight), Get (sibling
# in-flight this wave), LoadoutLabel, WeatherEnumLabel,
# FSkyguardCampaignMissionSpec fields, BeatSeconds, Harbor
# Breaker proof-clock comments, leftover Harbor 40/80,
# leftover campaign-save empty-fail-closed, leftover
# loadout #8/#114/#154, leftover CPG debrief,
# FillResultCombatStats / FillAndFinalize / FillAndFail /
# ApplyHydraForClusters leftover Gunner, leftover Harbor
# #6/#8/#9, leftover theater-kit #59, leftover flare/HUD
# #57/#61/#62, leftover drafts #56–#64, leftover #147
# ApacheSystem, leftover #149 weapon stations, leftover
# #152 pilot commands, settings invert-look #134, Harbor
# IncomingRadar 40/80, Yak/Igla/rifle live copy,
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
# loadout #8/#114/#154, leftover ApacheSystem #147 /
# weapon stations #149 / pilot commands #152, leftover
# settings invert-look #134, leftover Harbor / theater-kit,
# and in-flight NumMissions / Get siblings stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
    "Scripts/tests/test_campaign_roster_get_decl_contract.py",
    "Scripts/tests/test_campaign_roster_index_of_decl_contract.py",
    "Scripts/tests/test_campaign_roster_loadout_label_decl_contract.py",
    "Scripts/tests/test_campaign_roster_weather_enum_label_decl_contract.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
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
    "Scripts/tests/test_game_user_settings_getter_decl_contract.py",
    "Scripts/tests/test_set_invert_look_decl_contract.py",
    "Scripts/tests/test_invert_look_decl_contract.py",
    "Scripts/tests/test_validate_settings_decl_contract.py",
    "Scripts/tests/test_apply_and_save_settings_decl_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
# NumMissions is a sibling in-flight. Get is a sibling
# in-flight this wave. IndexOf is leftover lookup #111.
UNLOCKED_NEIGHBORS = (
    "int32 NumMissions();",
    "const FSkyguardCampaignMissionSpec& Get(int32 Index);",
    "int32 IndexOf(FName MissionId);",
    "const TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);",
    "const TCHAR* WeatherEnumLabel(ESkyguardMissionWeather Weather);",
)
INDEX_OF_NOT_LOCKED = ("int32 IndexOf(FName MissionId);",)
NUM_MISSIONS_NOT_LOCKED = ("int32 NumMissions();",)
GET_NOT_LOCKED = ("const FSkyguardCampaignMissionSpec& Get(int32 Index);",)
LABELS_NOT_LOCKED = (
    "const TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);",
    "const TCHAR* WeatherEnumLabel(ESkyguardMissionWeather Weather);",
)
# FSkyguardCampaignMissionSpec fields and Harbor Breaker
# proof-clock comments stay unlocked. Parse the namespace,
# not the struct.
SPEC_FIELDS_NOT_LOCKED = (
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
    "Harbor Breaker proof clock",
    "120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f",
)
# Leftover #111 lookup return values stay unlocked. Do not
# invent a returned mission id.
MISSION_IDS_NOT_LOCKED = (
    "M01_CoastalIntercept",
    "M02_HarborShield",
    "M10_EvacuationFinale",
    "UnknownRosterMission",
)
# Leftover CPG debrief copy / snapshot / fail-closed stay
# unlocked.
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
# Leftover FillResultCombatStats / FillAndFinalize /
# FillAndFail / ApplyHydraForClusters leftover Gunner,
# leftover #147 / #149 / #152 / #154, and settings
# invert-look #134 stay unlocked.
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
    "ASkyguardGunner",
    "SetInvertVerticalLook",
    "GetInvertVerticalLook",
    "bInvertVerticalLook",
    "InvertLook",
    "HandleInvertLookChanged",
)
# .cpp IdAt body / invented return values stay unlocked.
# Do not invent INDEX_NONE or a returned mission id.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return 0",
    "return -1",
    "return Get(Index).MissionId",
    "FMath::Clamp",
    "GMissions",
    "SkyguardCampaignRoster::IdAt",
    "SkyguardCampaignRoster.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "ASkyguardIglaMissile",
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


class CampaignRosterIdAtDeclContractTests(unittest.TestCase):
    def test_campaign_roster_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertTrue(has_declaration(body, ID_AT), body)
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

    def test_missing_id_at_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "\tint32 NumMissions();\n"
            "\tconst FSkyguardCampaignMissionSpec& Get(int32 Index);\n"
            "\tint32 IndexOf(FName MissionId);\n"
            "\tconst TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);\n"
            "\tconst TCHAR* WeatherEnumLabel("
            "ESkyguardMissionWeather Weather);\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, ID_AT)
        self.assertIn("IdAt", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_wrong_signature_does_not_satisfy(self) -> None:
        wrongs = (
            "{\n\tint32 IdAt(int32 Index);\n}\n",
            "{\n\tFName IdAt(FName MissionId);\n}\n",
            "{\n\tFName IdAt();\n}\n",
            "{\n\tFName IndexOf(int32 Index);\n}\n",
            "{\n\tFName IdAt(int32 Index = INDEX_NONE);\n}\n",
        )
        for region in wrongs:
            self.assertFalse(has_declaration(region, ID_AT), region)
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, ID_AT)
            self.assertIn("missing", str(raised.exception).lower())

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        neighbors_only = (
            "{\n"
            "\tint32 NumMissions();\n"
            "\tconst FSkyguardCampaignMissionSpec& Get(int32 Index);\n"
            "\tint32 IndexOf(FName MissionId);\n"
            "\tconst TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);\n"
            "\tconst TCHAR* WeatherEnumLabel("
            "ESkyguardMissionWeather Weather);\n"
            "}\n"
        )
        self.assertFalse(has_declaration(neighbors_only, ID_AT), neighbors_only)
        with self.assertRaises(AssertionError):
            require_declaration(neighbors_only, ID_AT)

    def test_id_at_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(require_declaration(body, ID_AT), ID_AT)
        self.assertTrue(has_declaration(body, ID_AT))
        self.assertEqual(declaration_count(body, ID_AT), 1)
        self.assertTrue(ID_AT.endswith(";"), ID_AT)
        self.assertTrue(ID_AT.startswith("FName "), ID_AT)
        self.assertIn("int32 Index", ID_AT)
        self.assertNotIn("INDEX_NONE", ID_AT)
        self.assertNotIn("return ", ID_AT)
        self.assertNotIn("{", ID_AT)
        self.assertNotIn("}", ID_AT)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = "{\n\tFName\n\tIdAt(int32 Index);\n}\n"
        wrap_args = "{\n\tFName IdAt(\n\t\tint32 Index);\n}\n"
        wrap_arg_type = "{\n\tFName IdAt(int32\n\t\tIndex);\n}\n"
        self.assertTrue(has_declaration(wrap_type, ID_AT), wrap_type)
        self.assertTrue(has_declaration(wrap_args, ID_AT), wrap_args)
        self.assertTrue(has_declaration(wrap_arg_type, ID_AT), wrap_arg_type)
        self.assertEqual(require_declaration(wrap_type, ID_AT), ID_AT)
        self.assertEqual(require_declaration(wrap_args, ID_AT), ID_AT)
        self.assertEqual(require_declaration(wrap_arg_type, ID_AT), ID_AT)
        self.assertEqual(declaration_count(wrap_type, ID_AT), 1)
        self.assertEqual(declaration_count(wrap_args, ID_AT), 1)
        self.assertEqual(declaration_count(wrap_arg_type, ID_AT), 1)
        one_line = f"{{\n\t{ID_AT}\n}}\n"
        self.assertTrue(has_declaration(one_line, ID_AT))
        body = namespace_body(origin_main_header())
        self.assertTrue(has_declaration(body, ID_AT), body)
        self.assertEqual(require_declaration(body, ID_AT), ID_AT)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{ID_AT}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", ID_AT)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", ID_AT)
        body = namespace_body(origin_main_header())
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("= INDEX_NONE", ID_AT)

    def test_declaration_does_not_invent_returned_mission_id(self) -> None:
        locked_only = f"{ID_AT}\n"
        self.assertNotIn("return ", ID_AT)
        self.assertNotIn("return Get(Index).MissionId", ID_AT)
        self.assertNotIn("return Get(Index).MissionId", locked_only)
        for token in MISSION_IDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ID_AT)
        body = namespace_body(origin_main_header())
        for token in MISSION_IDS_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn("return Get(Index).MissionId", body)
        self.assertNotIn("GMissions", ID_AT)
        self.assertNotIn("{", ID_AT)
        self.assertNotIn("}", ID_AT)

    def test_contract_does_not_lock_id_at_cpp_body(self) -> None:
        locked_only = f"{ID_AT}\n"
        self.assertNotIn("{", ID_AT)
        self.assertNotIn("}", ID_AT)
        self.assertNotIn("return ", ID_AT)
        self.assertNotIn("SkyguardCampaignRoster::IdAt", ID_AT)
        self.assertNotIn("SkyguardCampaignRoster.cpp", ID_AT)
        self.assertNotIn("SkyguardCampaignRoster.cpp", locked_only)
        self.assertNotIn("return Get(Index).MissionId", ID_AT)
        self.assertNotIn("FMath::Clamp", ID_AT)
        self.assertNotIn("GMissions", ID_AT)
        self.assertNotIn("const int32", ID_AT)

    def test_contract_does_not_relock_index_of(self) -> None:
        locked_only = f"{ID_AT}\n"
        for neighbor in INDEX_OF_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ID_AT)
        self.assertNotIn("IndexOf", ID_AT)
        self.assertNotIn("IndexOf", locked_only)
        for token in MISSION_IDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ID_AT)

    def test_contract_does_not_relock_num_missions(self) -> None:
        locked_only = f"{ID_AT}\n"
        for neighbor in NUM_MISSIONS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ID_AT)
        self.assertNotIn("NumMissions", ID_AT)
        self.assertNotIn("NumMissions", locked_only)

    def test_contract_does_not_relock_get(self) -> None:
        locked_only = f"{ID_AT}\n"
        for neighbor in GET_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ID_AT)
        self.assertNotIn(
            "const FSkyguardCampaignMissionSpec& Get(int32 Index);",
            locked_only,
        )
        self.assertNotIn("FSkyguardCampaignMissionSpec& Get", ID_AT)

    def test_contract_does_not_relock_loadout_or_weather_labels(self) -> None:
        locked_only = f"{ID_AT}\n"
        for neighbor in LABELS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ID_AT)
        self.assertNotIn("LoadoutLabel", ID_AT)
        self.assertNotIn("WeatherEnumLabel", ID_AT)
        self.assertNotIn("LoadoutLabel", locked_only)
        self.assertNotIn("WeatherEnumLabel", locked_only)

    def test_contract_does_not_relock_mission_spec_fields(self) -> None:
        locked_only = f"{ID_AT}\n"
        for token in SPEC_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ID_AT)
        self.assertNotIn("BeatSeconds", ID_AT)
        self.assertNotIn("BeatSeconds", locked_only)
        self.assertNotIn("Harbor Breaker proof clock", locked_only)
        self.assertNotIn("bNightIdentity", locked_only)
        self.assertNotIn("bStormRocketContract", locked_only)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{ID_AT}\n"
        self.assertEqual(require_declaration(locked_only, ID_AT), ID_AT)
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ID_AT)
        self.assertNotIn("NumMissions", locked_only)
        self.assertNotIn("IndexOf", locked_only)
        self.assertNotIn("LoadoutLabel", locked_only)
        self.assertNotIn("WeatherEnumLabel", locked_only)
        self.assertNotIn(
            "const FSkyguardCampaignMissionSpec& Get(int32 Index);",
            locked_only,
        )

    def test_contract_parses_namespace_not_struct_or_cpp(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertNotIn("struct FSkyguardCampaignMissionSpec", body)
        self.assertNotIn("float BeatSeconds[7]", body)
        self.assertNotIn("Harbor Breaker proof clock", body)
        self.assertEqual(require_declaration(body, ID_AT), ID_AT)
        self.assertNotIn("SkyguardCampaignRoster.cpp", body)
        self.assertNotIn("SkyguardCampaignRoster::IdAt", body)
        self.assertNotIn("return Get(Index).MissionId", body)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, ID_AT)
            if token != "return 0":
                self.assertNotIn(token, body)
        self.assertNotIn("SkyguardCampaignRoster.cpp", body)
        self.assertNotIn("SkyguardCampaignRoster::IdAt", body)
        self.assertNotIn("return Get(Index).MissionId", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("{", ID_AT)
        self.assertNotIn("}", ID_AT)

    def test_contract_does_not_relock_leftover_cpg_debrief(self) -> None:
        locked_only = f"{ID_AT}\n"
        body = namespace_body(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ID_AT)
            self.assertNotIn(token, body)

    def test_contract_does_not_relock_leftover_campaign_save(self) -> None:
        locked_only = f"{ID_AT}\n"
        body = namespace_body(origin_main_header())
        for token in LEFTOVER_CAMPAIGN_SAVE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ID_AT)
            self.assertNotIn(token, body)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{ID_AT}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ID_AT)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("SetInvertVerticalLook", locked_only)
        self.assertNotIn("bInvertVerticalLook", locked_only)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = namespace_body(origin_main_header())
        locked_only = f"{ID_AT}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
            self.assertNotIn(token, ID_AT)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
            self.assertNotIn(token, ID_AT)
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
        locked_only = f"{ID_AT}\n"
        body = namespace_body(origin_main_header())
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            "40.f, 80.f",
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ID_AT)
            self.assertNotIn(token, body)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(ID_AT, "Rifle")
        self.assertNotEqual(ID_AT, "Igla")
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
                f"campaign roster IdAt contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not leftover live copy",
            )
            self.assertNotIn(banned, ID_AT.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        body = namespace_body(header)
        self.assertNotIn("D:\\Skyguard52", body)
        self.assertNotIn("D:/Skyguard52", ID_AT)

    def test_contract_is_id_at_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(require_declaration(body, ID_AT), ID_AT)
        locked_only = f"{ID_AT}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, ID_AT)
        self.assertNotIn("NumMissions", locked_only)
        self.assertNotIn("IndexOf", locked_only)
        self.assertNotIn("LoadoutLabel", locked_only)
        self.assertNotIn("WeatherEnumLabel", locked_only)
        self.assertNotIn(
            "const FSkyguardCampaignMissionSpec& Get(int32 Index);",
            locked_only,
        )
        for token in SPEC_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ID_AT)
        for token in MISSION_IDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ID_AT)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ID_AT)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ID_AT)
        for token in LEFTOVER_CAMPAIGN_SAVE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, ID_AT)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, ID_AT)
            self.assertNotIn(token, body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, ID_AT)
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
        self.assertNotIn("return ", ID_AT)
        self.assertNotIn("{", ID_AT)
        self.assertNotIn("BeatSeconds", locked_only)
        self.assertNotIn("Harbor Breaker proof clock", locked_only)
        self.assertNotEqual(ID_AT, "Rifle")
        self.assertNotEqual(ID_AT, "Igla")
        self.assertNotIn("ApplyHydraForClusters", body)
        self.assertNotIn("FillResultCombatStats", body)
        self.assertNotIn("bYakRuntimeReady", body)

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
