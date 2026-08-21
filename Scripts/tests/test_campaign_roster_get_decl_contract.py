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
# returned spec payload, or lock the Get body in the .cpp.
# origin/main is one line
# (`const FSkyguardCampaignMissionSpec& Get(int32 Index);`);
# accept that form and other split-line wraps.
GET_DECL = "const FSkyguardCampaignMissionSpec& Get(int32 Index);"
LOCKED_DECLARATION = GET_DECL
LOCKED_DECLARATIONS = (GET_DECL,)
# Leftover #56–#64 plus CampaignRoster production sources.
# This lane only adds an isolated Python Get declaration
# contract. Stay off leftover campaign-roster lookup #111
# (IndexOf), NumMissions (in-flight sibling), IdAt,
# LoadoutLabel, WeatherEnumLabel, FSkyguardCampaignMissionSpec
# fields / BeatSeconds / Harbor Breaker proof-clock comments,
# leftover campaign-save empty-fail-closed, leftover loadout
# #8/#114/#154, leftover CPG debrief, FillResultCombatStats /
# FillAndFinalize / FillAndFail / ApplyHydraForClusters
# leftover Gunner, leftover Harbor #6/#8/#9, leftover
# theater-kit #59, leftover flare/HUD #57/#61/#62, leftover
# drafts #56–#64, leftover #147 ApacheSystem, leftover #149
# weapon stations, leftover #152 pilot commands, leftover
# settings invert-look / ApplySettings broadcast #134, Harbor
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
# campaign-roster lookup #111, NumMissions (in-flight),
# leftover campaign-save empty-fail-closed, leftover loadout
# #8/#114/#154, leftover CPG debrief copy / snapshot /
# fail-closed, leftover Harbor / theater-kit / flare/HUD,
# leftover ApacheSystem / weapon stations / pilot commands,
# leftover settings invert-look / ApplySettings broadcast,
# and leftover drafts #56–#64 stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_loadout_slot_helpers_contract.py",
    "Scripts/tests/test_loadout_display_name_contract.py",
    "Scripts/tests/test_gunship_types_loadout_contract.py",
    "Scripts/tests/test_gunship_types_loadout_tests.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
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
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
# NumMissions is an in-flight sibling. IndexOf is leftover #111.
UNLOCKED_NEIGHBORS = (
    "int32 NumMissions();",
    "int32 IndexOf(FName MissionId);",
    "FName IdAt(int32 Index);",
    "const TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);",
    "const TCHAR* WeatherEnumLabel(ESkyguardMissionWeather Weather);",
)
NUM_MISSIONS_NOT_LOCKED = "int32 NumMissions();"
INDEX_OF_NOT_LOCKED = "int32 IndexOf(FName MissionId);"
ID_AT_NOT_LOCKED = "FName IdAt(int32 Index);"
LOADOUT_LABEL_NOT_LOCKED = (
    "const TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);"
)
WEATHER_ENUM_LABEL_NOT_LOCKED = (
    "const TCHAR* WeatherEnumLabel(ESkyguardMissionWeather Weather);"
)
# FSkyguardCampaignMissionSpec fields / BeatSeconds / Harbor
# Breaker proof-clock comments stay unlocked. Parse the
# namespace, not the struct.
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
# FillResultCombatStats / FillAndFinalize / FillAndFail /
# ApplyHydraForClusters leftover Gunner stay unlocked.
FILL_AND_GUNNER_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
    "FillAndFinalize",
    "FillAndFail",
    "ApplyHydraForClusters",
)
# Leftover #147 / #149 / #152 / #154 / #8 / #114 / #134 stay
# unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "FillAndFinalize",
    "FillAndFail",
    "bInvertLook",
    "ApplySettings",
)
# .cpp Get body / invented return values / spec payloads stay
# unlocked. Do not invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return GMissions",
    "FMath::Clamp",
    "GMissions",
    "SkyguardCampaignRoster::Get",
    "SkyguardCampaignRoster.cpp",
    "const int32 Index",
)
# Do not invent a returned spec payload.
SPEC_PAYLOAD_NOT_LOCKED = (
    "return GMissions",
    "GMissions[",
    "FMath::Clamp(Index",
    "TEXT(\"Harbor",
    "M01_CoastalIntercept",
    "M02_HarborShield",
    "M10_EvacuationFinale",
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


class CampaignRosterGetDeclContractTests(unittest.TestCase):
    def test_campaign_roster_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertTrue(has_declaration(body, GET_DECL), body)
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
            "\tfloat BeatSeconds[7] = {120.f, 240.f, 360.f, "
            "480.f, 600.f, 780.f, 900.f};\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            namespace_body(struct_only)
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_get_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "\tint32 NumMissions();\n"
            "\tint32 IndexOf(FName MissionId);\n"
            "\tFName IdAt(int32 Index);\n"
            "\tconst TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);\n"
            "\tconst TCHAR* WeatherEnumLabel("
            "ESkyguardMissionWeather Weather);\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, GET_DECL)
        self.assertIn("Get(int32 Index)", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_neighbors_do_not_satisfy_get(self) -> None:
        neighbors_only = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tint32 NumMissions();\n"
            "\tint32 IndexOf(FName MissionId);\n"
            "\tFName IdAt(int32 Index);\n"
            "\tconst TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);\n"
            "\tconst TCHAR* WeatherEnumLabel("
            "ESkyguardMissionWeather Weather);\n"
            "}\n"
        )
        body = namespace_body(neighbors_only)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(body, GET_DECL)
        self.assertIn("Get(int32 Index)", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(body, GET_DECL))
        self.assertIn("NumMissions", body)
        self.assertIn("IndexOf", body)
        self.assertIn("IdAt", body)
        self.assertIn("LoadoutLabel", body)
        self.assertIn("WeatherEnumLabel", body)

    def test_wrong_signature_does_not_satisfy(self) -> None:
        wrong = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tFSkyguardCampaignMissionSpec& Get(int32 Index);\n"
            "\tconst FSkyguardCampaignMissionSpec Get(int32 Index);\n"
            "\tconst FSkyguardCampaignMissionSpec& Get();\n"
            "\tconst FSkyguardCampaignMissionSpec& Get(FName MissionId);\n"
            "\tint32 Get(int32 Index);\n"
            "\tconst FSkyguardCampaignMissionSpec& Get("
            "const int32 Index);\n"
            "}\n"
        )
        body = namespace_body(wrong)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(body, GET_DECL)
        self.assertIn("Get(int32 Index)", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn("Get(", body)
        self.assertFalse(has_declaration(body, GET_DECL))
        self.assertFalse(GET_DECL.endswith("const;"), GET_DECL)
        self.assertNotEqual(
            GET_DECL,
            "const FSkyguardCampaignMissionSpec& Get(int32 Index) const;",
        )

    def test_get_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(require_declaration(body, GET_DECL), GET_DECL)
        self.assertEqual(LOCKED_DECLARATIONS, (GET_DECL,))
        self.assertEqual(LOCKED_DECLARATION, GET_DECL)
        self.assertTrue(has_declaration(body, GET_DECL))
        self.assertEqual(declaration_count(body, GET_DECL), 1)
        self.assertTrue(GET_DECL.endswith(";"), GET_DECL)
        self.assertTrue(
            GET_DECL.startswith("const FSkyguardCampaignMissionSpec& "),
            GET_DECL,
        )
        self.assertIn("Get(int32 Index)", GET_DECL)
        self.assertNotIn("INDEX_NONE", GET_DECL)
        self.assertNotIn("return ", GET_DECL)
        self.assertNotIn("{", GET_DECL)
        self.assertNotIn("}", GET_DECL)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "{\n"
            "\tconst FSkyguardCampaignMissionSpec&\n"
            "\tGet(int32 Index);\n"
            "}\n"
        )
        wrap_args = (
            "{\n"
            "\tconst FSkyguardCampaignMissionSpec& Get(\n"
            "\t\tint32 Index);\n"
            "}\n"
        )
        wrap_amp = (
            "{\n"
            "\tconst FSkyguardCampaignMissionSpec\n"
            "\t& Get(int32 Index);\n"
            "}\n"
        )
        wrap_name = (
            "{\n"
            "\tconst FSkyguardCampaignMissionSpec& Get(int32\n"
            "\t\tIndex);\n"
            "}\n"
        )
        for region in (wrap_type, wrap_args, wrap_amp, wrap_name):
            self.assertTrue(has_declaration(region, GET_DECL), region)
            self.assertEqual(
                require_declaration(region, GET_DECL),
                GET_DECL,
            )
            self.assertEqual(declaration_count(region, GET_DECL), 1)
        one_line = f"{{\n\t{GET_DECL}\n}}\n"
        self.assertTrue(has_declaration(one_line, GET_DECL))
        body = namespace_body(origin_main_header())
        self.assertTrue(has_declaration(body, GET_DECL), body)
        self.assertEqual(require_declaration(body, GET_DECL), GET_DECL)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{GET_DECL}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", GET_DECL)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", GET_DECL)
        body = namespace_body(origin_main_header())
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)

    def test_declaration_does_not_invent_returned_spec_payload(self) -> None:
        locked_only = f"{GET_DECL}\n"
        self.assertNotIn("return ", GET_DECL)
        self.assertNotIn("{", GET_DECL)
        self.assertNotIn("}", GET_DECL)
        for token in SPEC_PAYLOAD_NOT_LOCKED:
            self.assertNotIn(token, GET_DECL)
            self.assertNotIn(token, locked_only)
        body = namespace_body(origin_main_header())
        for token in SPEC_PAYLOAD_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn("return GMissions", body)
        self.assertNotIn("FMath::Clamp", body)
        self.assertNotIn("GMissions[", body)

    def test_contract_does_not_lock_get_cpp_body(self) -> None:
        locked_only = f"{GET_DECL}\n"
        self.assertNotIn("{", GET_DECL)
        self.assertNotIn("}", GET_DECL)
        self.assertNotIn("return ", GET_DECL)
        self.assertNotIn("SkyguardCampaignRoster::Get", GET_DECL)
        self.assertNotIn("SkyguardCampaignRoster.cpp", GET_DECL)
        self.assertNotIn("SkyguardCampaignRoster.cpp", locked_only)
        self.assertNotIn("FMath::Clamp", GET_DECL)
        self.assertNotIn("GMissions", GET_DECL)
        self.assertNotIn("const int32 Index", GET_DECL)
        self.assertNotIn("const int32 Index", locked_only)

    def test_contract_does_not_relock_num_missions(self) -> None:
        locked_only = f"{GET_DECL}\n"
        self.assertNotIn(NUM_MISSIONS_NOT_LOCKED, locked_only)
        self.assertNotIn(NUM_MISSIONS_NOT_LOCKED, GET_DECL)
        self.assertNotIn("NumMissions", GET_DECL)
        self.assertNotIn("NumMissions", locked_only)
        self.assertIn(
            "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_index_of(self) -> None:
        locked_only = f"{GET_DECL}\n"
        self.assertNotIn(INDEX_OF_NOT_LOCKED, locked_only)
        self.assertNotIn(INDEX_OF_NOT_LOCKED, GET_DECL)
        self.assertNotIn("IndexOf", GET_DECL)
        self.assertNotIn("IndexOf", locked_only)
        self.assertIn(
            "Scripts/tests/test_campaign_roster_lookup_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_campaign_roster_lookup_tests.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_id_at(self) -> None:
        locked_only = f"{GET_DECL}\n"
        self.assertNotIn(ID_AT_NOT_LOCKED, locked_only)
        self.assertNotIn(ID_AT_NOT_LOCKED, GET_DECL)
        self.assertNotIn("IdAt", GET_DECL)
        self.assertNotIn("IdAt", locked_only)

    def test_contract_does_not_relock_loadout_label(self) -> None:
        locked_only = f"{GET_DECL}\n"
        self.assertNotIn(LOADOUT_LABEL_NOT_LOCKED, locked_only)
        self.assertNotIn(LOADOUT_LABEL_NOT_LOCKED, GET_DECL)
        self.assertNotIn("LoadoutLabel", GET_DECL)
        self.assertNotIn("LoadoutLabel", locked_only)
        self.assertNotIn("ESkyguardLoadout", GET_DECL)
        self.assertNotIn("ESkyguardLoadout", locked_only)

    def test_contract_does_not_relock_weather_enum_label(self) -> None:
        locked_only = f"{GET_DECL}\n"
        self.assertNotIn(WEATHER_ENUM_LABEL_NOT_LOCKED, locked_only)
        self.assertNotIn(WEATHER_ENUM_LABEL_NOT_LOCKED, GET_DECL)
        self.assertNotIn("WeatherEnumLabel", GET_DECL)
        self.assertNotIn("WeatherEnumLabel", locked_only)

    def test_contract_does_not_relock_spec_fields_or_proof_clock(self) -> None:
        locked_only = f"{GET_DECL}\n"
        for token in SPEC_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_DECL)
        for token in HARBOR_PROOF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_DECL)
        self.assertNotIn("BeatSeconds", GET_DECL)
        self.assertNotIn("Harbor Breaker", GET_DECL)
        self.assertNotIn("proof clock", GET_DECL)
        self.assertNotIn("bNightIdentity", locked_only)
        self.assertNotIn("bStormRocketContract", locked_only)
        body = namespace_body(origin_main_header())
        for token in HARBOR_PROOF_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn("struct FSkyguardCampaignMissionSpec", body)

    def test_contract_does_not_relock_leftover_cpg_debrief(self) -> None:
        locked_only = f"{GET_DECL}\n"
        body = namespace_body(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_DECL)
            self.assertNotIn(token, body)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_fill_and_gunner(self) -> None:
        locked_only = f"{GET_DECL}\n"
        body = namespace_body(origin_main_header())
        for token in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_DECL)
            self.assertNotIn(token, body)
        self.assertNotIn("FillResultCombatStats", GET_DECL)
        self.assertNotIn("ASkyguardGunner", GET_DECL)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{GET_DECL}\n"
        body = namespace_body(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_DECL)
            if token != "ESkyguardLoadout":
                self.assertNotIn(token, body)
        self.assertNotIn("bInvertLook", GET_DECL)
        self.assertNotIn("ApplySettings", GET_DECL)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn("ESkyguardGunshipWeaponStation", locked_only)
        self.assertNotIn("ESkyguardPilotCommand", locked_only)
        self.assertNotIn("ESkyguardLoadout", GET_DECL)
        self.assertNotIn("ESkyguardLoadout", locked_only)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{GET_DECL}\n"
        self.assertEqual(
            require_declaration(locked_only, GET_DECL),
            GET_DECL,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_DECL)
        self.assertNotIn("NumMissions", locked_only)
        self.assertNotIn("IndexOf", locked_only)
        self.assertNotIn("IdAt", locked_only)
        self.assertNotIn("LoadoutLabel", locked_only)
        self.assertNotIn("WeatherEnumLabel", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("bInvertLook", locked_only)

    def test_contract_parses_namespace_not_struct_or_cpp(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertNotIn("struct FSkyguardCampaignMissionSpec", body)
        self.assertNotIn("float BeatSeconds[7]", body)
        self.assertNotIn("Harbor Breaker", body)
        self.assertEqual(require_declaration(body, GET_DECL), GET_DECL)
        self.assertNotIn("SkyguardCampaignRoster.cpp", body)
        self.assertNotIn("SkyguardCampaignRoster::Get", body)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_DECL)
            self.assertNotIn(token, body)
        self.assertNotIn("SkyguardCampaignRoster.cpp", body)
        self.assertNotIn("SkyguardCampaignRoster::Get", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("{", GET_DECL)
        self.assertNotIn("}", GET_DECL)
        self.assertNotIn("return ", GET_DECL)
        self.assertNotIn("FMath::Clamp", GET_DECL)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = namespace_body(origin_main_header())
        locked_only = f"{GET_DECL}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
            self.assertNotIn(token, GET_DECL)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
            self.assertNotIn(token, GET_DECL)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{GET_DECL}\n"
        body = namespace_body(origin_main_header())
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            "40.f, 80.f",
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_DECL)
            self.assertNotIn(token, body)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(GET_DECL, "Rifle")
        self.assertNotEqual(GET_DECL, "Igla")
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
                f"campaign roster Get contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, GET_DECL.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        body = namespace_body(header)
        self.assertNotIn("D:\\Skyguard52", body)
        self.assertNotIn("D:/Skyguard52", GET_DECL)

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
            "Scripts/tests/test_campaign_roster_get_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_is_get_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(require_declaration(body, GET_DECL), GET_DECL)
        locked_only = f"{GET_DECL}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_DECL)
        self.assertNotIn("NumMissions", locked_only)
        self.assertNotIn("IndexOf", locked_only)
        self.assertNotIn("IdAt", locked_only)
        self.assertNotIn("LoadoutLabel", locked_only)
        self.assertNotIn("WeatherEnumLabel", locked_only)
        for token in SPEC_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_DECL)
        for token in HARBOR_PROOF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_DECL)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_DECL)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_DECL)
        for token in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_DECL)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, GET_DECL)
            self.assertNotIn(token, body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_DECL)
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
        self.assertNotIn("return ", GET_DECL)
        self.assertNotIn("{", GET_DECL)
        self.assertNotIn("BeatSeconds", GET_DECL)
        self.assertNotIn("Harbor Breaker", body)
        self.assertNotEqual(GET_DECL, "Rifle")
        self.assertNotEqual(GET_DECL, "Igla")
        self.assertNotIn("ApplyHydraForClusters", body)
        self.assertNotIn("bInvertLook", body)

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
