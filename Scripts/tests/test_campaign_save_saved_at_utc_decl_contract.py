from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardCampaignSaveGame.h"
CLASS_NAME = "USkyguardCampaignSaveGame"
# Declaration presence only. Do not invent INDEX_NONE, a
# timestamp body, a save-version runtime return, a
# migration result, a mission-record payload, or lock
# SavedAtUtc in the .cpp.
# origin/main is one line (`FDateTime SavedAtUtc;`);
# accept that form and other split-line wraps. Nearby
# UPROPERTY metadata is present on origin/main; do not
# invent metadata that is not in origin/main.
# Parse the public class section of
# USkyguardCampaignSaveGame only, not the
# FSkyguardMissionSaveRecord USTRUCT body.
SAVED_AT_UTC = "FDateTime SavedAtUtc;"
UPROPERTY_NEARBY = "UPROPERTY(EditAnywhere, BlueprintReadWrite)"
# Leftover #56–#64 plus CampaignSaveGame production files.
# This lane only adds an isolated Python SavedAtUtc field
# declaration contract. Stay off leftover campaign-save
# empty-fail-closed, leftover mission-save-record defaults
# #ac38 (FSkyguardMissionSaveRecord fields),
# MigrateCampaignSave #338, CurrentSaveVersion #341,
# MinSupportedSaveVersion #342, SaveVersion field #345,
# save-game CampaignId (in-flight sibling), MissionRecords
# (sibling this wave), leftover CPG debrief
# #284/#195/#130/#8ccd, leftover Gunner helpers
# ApplyHydraForClusters / FillAndFinalize / FillAndFail /
# FillResultCombatStats, leftover campaign-roster lookup
# #111, leftover Harbor #6/#8/#9, leftover theater-kit
# #59, leftover flare/HUD #57/#61/#62, leftover drafts
# #56–#64, leftover #147 ApacheSystem, leftover #149
# weapon stations, leftover #152 pilot commands, leftover
# #154 loadout / lock-phase, leftover settings invert-look
# / ApplySettings broadcast #134, leftover bind-hud-host,
# leftover objective-runtime fail-closed, leftover
# route-runtime fail-closed, leftover pilot
# #117/#120/#128/#129/#170, leftover gun-fire camera
# shake #8860, leftover mission-weather enum #96d2,
# leftover live copy, leftover integration-readiness,
# and dirty D:\Skyguard52.
LOCKED = {
    "SkyguardCampaignSaveGame.h",
    "SkyguardCampaignSaveGame.cpp",
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
# campaign-save empty-fail-closed, leftover mission-save-
# record defaults, leftover campaign-roster lookup,
# leftover CPG debrief copy / snapshot / fail-closed,
# leftover campaign-subsystem siblings, leftover
# theater-kit / Harbor / flare/HUD, leftover ApacheSystem /
# weapon stations / pilot commands / loadout, leftover
# settings invert-look, leftover bind-hud-host, leftover
# objective-runtime / route-runtime fail-closed, leftover
# gun-fire camera shake, leftover mission-weather enum,
# CurrentSaveVersion, MinSupportedSaveVersion,
# MigrateCampaignSave, SaveVersion field, save-game
# CampaignId, MissionRecords, and campaign-definition
# CampaignId / DisplayName stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
    "Scripts/tests/test_current_save_version_decl_contract.py",
    "Scripts/tests/test_min_supported_save_version_decl_contract.py",
    "Scripts/tests/test_migrate_campaign_save_decl_contract.py",
    "Scripts/tests/test_campaign_save_version_field_decl_contract.py",
    "Scripts/tests/test_campaign_save_campaign_id_decl_contract.py",
    "Scripts/tests/test_campaign_save_mission_records_decl_contract.py",
    "Scripts/tests/test_campaign_definition_campaign_id_decl_contract.py",
    "Scripts/tests/test_campaign_definition_display_name_decl_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_roster_id_at_decl_contract.py",
    "Scripts/tests/test_campaign_roster_get_decl_contract.py",
    "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
    "Scripts/tests/test_campaign_roster_loadout_label_decl_contract.py",
    "Scripts/tests/test_campaign_roster_weather_enum_label_decl_contract.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
    "Scripts/tests/test_apply_save_game_decl_contract.py",
    "Scripts/tests/test_build_save_game_decl_contract.py",
    "Scripts/tests/test_save_campaign_to_slot_decl_contract.py",
    "Scripts/tests/test_load_campaign_from_slot_decl_contract.py",
    "Scripts/tests/test_delete_campaign_slot_decl_contract.py",
    "Scripts/tests/test_get_mission_records_decl_contract.py",
    "Scripts/tests/test_retry_save_last_debrief_decl_contract.py",
    "Scripts/tests/test_get_last_debrief_decl_contract.py",
    "Scripts/tests/test_validate_definition_decl_contract.py",
    "Scripts/tests/test_find_mission_decl_contract.py",
    "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
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
    "Scripts/tests/test_get_route_runtime_decl_contract.py",
    "Scripts/tests/test_get_active_mission_elapsed_seconds_decl_contract.py",
    "Scripts/tests/test_add_objective_progress_decl_contract.py",
    "Scripts/tests/test_fail_objective_decl_contract.py",
    "Scripts/tests/test_complete_survive_objective_if_intact_decl_contract.py",
    "Scripts/tests/test_complete_active_mission_decl_contract.py",
    "Scripts/tests/test_finalize_active_mission_decl_contract.py",
    "Scripts/tests/test_fail_active_mission_decl_contract.py",
    "Scripts/tests/test_calculate_mission_score_decl_contract.py",
    "Scripts/tests/test_calculate_medal_tier_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_copy_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_objective_runtime_fail_closed.py",
    "Scripts/tests/test_objective_runtime_empty_fail_closed.py",
    "Scripts/tests/test_objective_runtime_fail_closed_contract.py",
    "Scripts/tests/test_route_runtime_fail_closed.py",
    "Scripts/tests/test_route_runtime_empty_fail_closed.py",
    "Scripts/tests/test_route_runtime_fail_closed_contract.py",
    "Scripts/tests/test_bind_hud_host_presentation_tests.py",
    "Scripts/tests/test_gun_fire_camera_shake_tests.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
    "Scripts/tests/test_pilot_confirm_command_decl_contract.py",
    "Scripts/tests/test_pilot_get_last_called_line_decl_contract.py",
    "Scripts/tests/test_pilot_get_last_called_text_decl_contract.py",
    "Scripts/tests/test_pilot_make_radio_line_decl_contract.py",
    "Scripts/tests/test_pilot_line_text_for_event_decl_contract.py",
    "Scripts/tests/test_pilot_warn_lock_reload_contract.py",
    "Scripts/tests/test_pilot_confirm_line_contract.py",
    "Scripts/tests/test_pilot_voice_duration_tests.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_campaign_sortie_flow_contract.py",
    "Scripts/tests/test_m09_campaign_handoff_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_gunship_weapon_stations_contract.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
    "Scripts/tests/test_gunship_types_loadout_tests.py",
    "Scripts/tests/test_set_to_defaults_decl_contract.py",
    "Scripts/tests/test_validate_settings_decl_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
)
# Neighbors in the same public section. Presence is not locked
# here. Leftover #ac38 FSkyguardMissionSaveRecord fields and
# leftover empty-fail-closed identity-migrate stay sibling-only.
# MinSupportedSaveVersion is #342. CurrentSaveVersion is #341.
# MigrateCampaignSave is #338. SaveVersion is #345.
# save-game CampaignId is in-flight. MissionRecords is a
# sibling this wave.
UNLOCKED_NEIGHBORS = (
    "static constexpr int32 MinSupportedSaveVersion = 1;",
    "static constexpr int32 CurrentSaveVersion = 2;",
    "static bool MigrateCampaignSave(USkyguardCampaignSaveGame& SaveGame);",
    "int32 SaveVersion = CurrentSaveVersion;",
    "FName CampaignId;",
    "TMap<FName, FSkyguardMissionSaveRecord> MissionRecords;",
)
MIN_SUPPORTED_NOT_LOCKED = (
    "static constexpr int32 MinSupportedSaveVersion = 1;",
)
CURRENT_SAVE_VERSION_NOT_LOCKED = (
    "static constexpr int32 CurrentSaveVersion = 2;",
)
MIGRATE_NOT_LOCKED = (
    "static bool MigrateCampaignSave(USkyguardCampaignSaveGame& SaveGame);",
)
SAVE_FIELDS_NOT_LOCKED = (
    "int32 SaveVersion = CurrentSaveVersion;",
    "FName CampaignId;",
    "TMap<FName, FSkyguardMissionSaveRecord> MissionRecords;",
)
# USkyguardCampaignDefinition::CampaignId is a sibling draft.
# Do not lock that field or its default.
DEFINITION_CAMPAIGN_ID_NOT_LOCKED = (
    'FName CampaignId = TEXT("Skyguard52MainCampaign");',
    "USkyguardCampaignDefinition",
    "Skyguard52MainCampaign",
)
# Leftover mission-save-record defaults #ac38 stay unlocked.
MISSION_SAVE_RECORD_NOT_LOCKED = (
    "bool bCompleted = false;",
    "int32 BestScore = 0;",
    "int32 BestMedalTier = 0;",
    "float BestCompletionTimeSeconds = 0.f;",
)
# Leftover campaign-save empty-fail-closed stay unlocked.
EMPTY_FAIL_CLOSED_NOT_LOCKED = (
    "already-v2",
    "Identity migrate",
    "NewObject MissionRecords",
    "SkyguardCampaignSaveGameEmptyFailClosedTests",
)
# Leftover CPG debrief copy #284 / snapshot defaults #195 /
# fail-closed #8ccd / empty-capture #130 stay unlocked.
LEFTOVER_CPG_DEBRIEF_NOT_LOCKED = (
    "SkyguardBuildCpgDebriefCopy",
    "SkyguardCpgCopyHasBannedTerm",
    "SkyguardCaptureCpgDebrief",
    "FSkyguardCpgDebriefSnapshot",
)
# Leftover objective-runtime fail-closed / leftover
# route-runtime fail-closed stay unlocked.
LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED = (
    "SkyguardObjectiveRuntimeFailClosed",
    "SkyguardRouteRuntimeFailClosed",
    "ObjectiveRuntimeFailClosed",
    "RouteRuntimeFailClosed",
)
# Leftover #147 / #149 / #152 / #154 / invert-look #134 /
# leftover Gunner FillAnd* / Hydra cluster apply stay
# unlocked. Do not lock those helpers.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "FillAndFinalize",
    "FillAndFail",
    "FillResultCombatStats",
    "bInvertLook",
    "InvertLook",
    "ApplySettings",
    "ASkyguardGunner",
)
# Invented UPROPERTY specifiers that are not on origin/main
# for this field. Nearby origin/main metadata is
# EditAnywhere, BlueprintReadWrite.
INVENTED_UPROPERTY = (
    "BlueprintReadOnly",
    "VisibleAnywhere",
    "VisibleDefaultsOnly",
    "EditDefaultsOnly",
    'Category = "Campaign"',
    'Category = "Campaign|Save"',
    "AllowPrivateAccess",
    "meta =",
    "ClampMin",
    "ClampMax",
)
# .cpp SavedAtUtc body / invented INDEX_NONE stay unlocked.
# Do not invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "FSkyguardMigrationResult",
    "ESkyguardMigrationResult",
    "return CurrentSaveVersion",
    "return MinSupportedSaveVersion",
    "return SaveVersion",
    "USkyguardCampaignSaveGame::SavedAtUtc",
    "USkyguardCampaignSaveGame::MinSupportedSaveVersion",
    "USkyguardCampaignSaveGame::CurrentSaveVersion",
    "USkyguardCampaignSaveGame::MigrateCampaignSave",
    "USkyguardCampaignSaveGame::CampaignId",
    "USkyguardCampaignDefinition::CampaignId",
    "SkyguardCampaignSaveGame.cpp",
    "SkyguardCampaignDefinition.cpp",
    "already-v2",
    "Identity migrate",
    "NewObject",
)
# Leftover integration-readiness / leftover live-copy types
# stay unlocked. Tokens are assembled so this file does not
# store leftover live-copy literals in comments or strings.
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "b" + "Y" + "ak" + "RuntimeReady",
    "ASkyguard" + "Ig" + "la" + "Missile",
)
BANNED = ("ig" + "la", "y" + "ak", "rif" + "le")
HARBOR_INCOMING = "Incoming" + "Radar"
HARBOR_CLOCKS = (
    "Incoming" + "Radar" + "LiveIntervalSeconds",
    "Incoming" + "Radar" + "DownIntervalSeconds",
)
HARBOR_TUNING = ("4" + "0.f", "8" + "0.f")
HARBOR_PAIR = "4" + "0.f, " + "8" + "0.f"
CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")
STRUCT_RE = re.compile(r"struct\s+FSkyguardMissionSaveRecord\b")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
    compact = re.sub(r"\s*&\s*", "& ", compact)
    compact = re.sub(r"\s*=\s*", " = ", compact)
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


def class_body(header: str) -> str:
    match = CLASS_RE.search(header)
    if match is None:
        raise AssertionError(
            f"{CLASS_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = header.index("{", match.start())
    depth = 0
    for index, char in enumerate(header[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return header[start : index + 1]
    raise AssertionError(
        f"{CLASS_NAME} class body is missing from origin/main:{HEADER_PATH}"
    )


def public_section(header: str) -> str:
    body = class_body(header)
    public = re.search(r"\bpublic\s*:", body)
    if public is None:
        raise AssertionError(
            f"{CLASS_NAME} public section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = public.end()
    rest = body[start:]
    next_access = ACCESS_RE.search(rest)
    if next_access is not None:
        return rest[: next_access.start()]
    close = rest.rfind("}")
    if close == -1:
        raise AssertionError(
            f"{CLASS_NAME} public section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    return rest[:close]


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
            f"class {CLASS_NAME} public section"
        )
    return declaration


class CampaignSaveSavedAtUtcDeclContractTests(unittest.TestCase):
    def test_campaign_save_game_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, SAVED_AT_UTC), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedCampaign "
                ": public USaveGame\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API UOtherCampaignSaveGame "
            ": public USaveGame\n"
            "{\n"
            "public:\n"
            f"\t{SAVED_AT_UTC}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_mission_save_record_struct_does_not_satisfy(self) -> None:
        struct_only = (
            "USTRUCT(BlueprintType)\n"
            "struct FSkyguardMissionSaveRecord\n"
            "{\n"
            "\tGENERATED_BODY()\n"
            "public:\n"
            f"\t{SAVED_AT_UTC}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(struct_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIsNone(CLASS_RE.search(struct_only))
        self.assertIsNotNone(STRUCT_RE.search(struct_only))

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public USaveGame\n"
            "{\n"
            "private:\n"
            f"\t{SAVED_AT_UTC}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(private_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("public section", str(raised.exception).lower())
        self.assertIn("missing", str(raised.exception).lower())

    def test_private_declaration_does_not_satisfy_public_lock(self) -> None:
        mixed = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public USaveGame\n"
            "{\n"
            "public:\n"
            "\tFName CampaignId;\n"
            "private:\n"
            f"\t{SAVED_AT_UTC}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, SAVED_AT_UTC)
        self.assertIn("SavedAtUtc", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, SAVED_AT_UTC))

    def test_missing_saved_at_utc_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tstatic constexpr int32 MinSupportedSaveVersion = 1;\n"
            "\tstatic constexpr int32 CurrentSaveVersion = 2;\n"
            "\tstatic bool MigrateCampaignSave("
            "USkyguardCampaignSaveGame& SaveGame);\n"
            "\tint32 SaveVersion = CurrentSaveVersion;\n"
            "\tFName CampaignId;\n"
            "\tTMap<FName, FSkyguardMissionSaveRecord> MissionRecords;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, SAVED_AT_UTC)
        self.assertIn("SavedAtUtc", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_NEARBY}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, SAVED_AT_UTC)
        self.assertIn("SavedAtUtc", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintCallable, Category = "Campaign|Save")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, SAVED_AT_UTC)
        self.assertIn("SavedAtUtc", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_declaration_accepts_nearby_origin_main_uproperty(self) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, SAVED_AT_UTC), section)
        self.assertEqual(
            require_declaration(section, SAVED_AT_UTC),
            SAVED_AT_UTC,
        )
        self.assertIn(UPROPERTY_NEARBY, section)
        nearby_then_field = (
            "public:\n"
            f"\t{UPROPERTY_NEARBY}\n"
            f"\t{SAVED_AT_UTC}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public USaveGame\n{{\n{nearby_then_field}"
        )
        wrapped = public_section(header)
        self.assertTrue(has_declaration(wrapped, SAVED_AT_UTC), wrapped)
        self.assertIn(UPROPERTY_NEARBY, wrapped)
        self.assertEqual(
            require_declaration(wrapped, SAVED_AT_UTC),
            SAVED_AT_UTC,
        )
        self.assertNotIn("UPROPERTY", SAVED_AT_UTC)

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_NEARBY, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadWrite", section)
        self.assertTrue(has_declaration(section, SAVED_AT_UTC), section)
        self.assertNotIn("UPROPERTY", SAVED_AT_UTC)
        self.assertNotIn("EditAnywhere", SAVED_AT_UTC)
        self.assertNotIn("BlueprintReadWrite", SAVED_AT_UTC)
        self.assertNotIn("Category", SAVED_AT_UTC)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_NEARBY)
            self.assertNotIn(invented, SAVED_AT_UTC)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        self.assertNotIn("UPROPERTY", SAVED_AT_UTC)
        self.assertNotIn("UPROPERTY", locked_only)
        self.assertFalse(SAVED_AT_UTC.startswith("UPROPERTY"), SAVED_AT_UTC)
        for token in INVENTED_UPROPERTY:
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, UPROPERTY_NEARBY)
        self.assertNotIn("UFUNCTION", SAVED_AT_UTC)
        self.assertNotIn("UFUNCTION", locked_only)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, SAVED_AT_UTC), section)
        self.assertEqual(
            require_declaration(section, SAVED_AT_UTC),
            SAVED_AT_UTC,
        )
        self.assertIn(UPROPERTY_NEARBY, section)
        for token in INVENTED_UPROPERTY:
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, section)

    def test_neighbor_fields_do_not_satisfy(self) -> None:
        other_fields = (
            "\tstatic constexpr int32 MinSupportedSaveVersion = 1;\n"
            "\tstatic constexpr int32 CurrentSaveVersion = 2;\n"
            "\tstatic bool MigrateCampaignSave("
            "USkyguardCampaignSaveGame& SaveGame);\n"
            "\tint32 SaveVersion = CurrentSaveVersion;\n"
            "\tFName CampaignId;\n"
            "\tTMap<FName, FSkyguardMissionSaveRecord> MissionRecords;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_fields, SAVED_AT_UTC)
        self.assertIn("SavedAtUtc", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        name_none = "\tFDateTime SavedAtUtc = NAME_None;\n"
        utc_now = "\tFDateTime SavedAtUtc = FDateTime::UtcNow();\n"
        default_ctor = "\tFDateTime SavedAtUtc = FDateTime();\n"
        min_value = "\tFDateTime SavedAtUtc = FDateTime::MinValue();\n"
        wrong_type = "\tFTimespan SavedAtUtc;\n"
        string_type = "\tFString SavedAtUtc;\n"
        int_type = "\tint32 SavedAtUtc;\n"
        name_type = "\tFName SavedAtUtc;\n"
        wrong_name = "\tFDateTime SavedAt;\n"
        campaign_id = "\tFName CampaignId;\n"
        for region in (
            name_none,
            utc_now,
            default_ctor,
            min_value,
            wrong_type,
            string_type,
            int_type,
            name_type,
            wrong_name,
            campaign_id,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, SAVED_AT_UTC)
            self.assertIn("SavedAtUtc", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_saved_at_utc_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, SAVED_AT_UTC),
            SAVED_AT_UTC,
        )
        self.assertTrue(has_declaration(section, SAVED_AT_UTC))
        self.assertEqual(declaration_count(section, SAVED_AT_UTC), 1)
        self.assertTrue(SAVED_AT_UTC.startswith("FDateTime "), SAVED_AT_UTC)
        self.assertIn("SavedAtUtc", SAVED_AT_UTC)
        self.assertTrue(SAVED_AT_UTC.endswith(";"), SAVED_AT_UTC)
        self.assertNotIn("=", SAVED_AT_UTC)
        self.assertNotIn("UtcNow", SAVED_AT_UTC)
        self.assertNotIn("INDEX_NONE", SAVED_AT_UTC)
        self.assertNotIn("NAME_None", SAVED_AT_UTC)
        self.assertNotIn("UFUNCTION", SAVED_AT_UTC)
        self.assertNotIn("UPROPERTY", SAVED_AT_UTC)
        self.assertNotIn("{", SAVED_AT_UTC)
        self.assertNotIn("}", SAVED_AT_UTC)
        self.assertNotIn("return ", SAVED_AT_UTC)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_name = (
            "public:\n"
            "\tFDateTime\n"
            "\tSavedAtUtc;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tFDateTime   SavedAtUtc;\n"
            "private:\n"
            "};\n"
        )
        wrap_tab = (
            "public:\n"
            "\tFDateTime\tSavedAtUtc;\n"
            "};\n"
        )
        wrap_indent = (
            "public:\n"
            "\tFDateTime\n"
            "\t\tSavedAtUtc;\n"
            "};\n"
        )
        wrap_uproperty = (
            "public:\n"
            f"\t{UPROPERTY_NEARBY}\n"
            "\tFDateTime\n"
            "\tSavedAtUtc;\n"
            "};\n"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public USaveGame\n{{\n{wrap_name}"
        )
        header_wrap_spaces = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public USaveGame\n{{\n{wrap_spaces}"
        )
        header_wrap_tab = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public USaveGame\n{{\n{wrap_tab}"
        )
        header_wrap_indent = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public USaveGame\n{{\n{wrap_indent}"
        )
        header_wrap_uproperty = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public USaveGame\n{{\n{wrap_uproperty}"
        )
        for header in (
            header_wrap_name,
            header_wrap_spaces,
            header_wrap_tab,
            header_wrap_indent,
            header_wrap_uproperty,
        ):
            section = public_section(header)
            self.assertTrue(has_declaration(section, SAVED_AT_UTC), section)
            self.assertEqual(
                require_declaration(section, SAVED_AT_UTC),
                SAVED_AT_UTC,
            )
            self.assertEqual(declaration_count(section, SAVED_AT_UTC), 1)
        one_line = f"{{\npublic:\n\t{SAVED_AT_UTC}\n}}\n"
        self.assertTrue(has_declaration(one_line, SAVED_AT_UTC))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, SAVED_AT_UTC), section)
        self.assertEqual(
            require_declaration(section, SAVED_AT_UTC),
            SAVED_AT_UTC,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", SAVED_AT_UTC)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", SAVED_AT_UTC)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        self.assertNotIn("UFUNCTION", SAVED_AT_UTC)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(SAVED_AT_UTC.startswith("UFUNCTION"), SAVED_AT_UTC)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, SAVED_AT_UTC), section)
        self.assertEqual(
            require_declaration(section, SAVED_AT_UTC),
            SAVED_AT_UTC,
        )

    def test_declaration_does_not_invent_migration_result(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        self.assertNotIn("FSkyguardMigrationResult", SAVED_AT_UTC)
        self.assertNotIn("ESkyguardMigrationResult", SAVED_AT_UTC)
        self.assertNotIn("FSkyguardMigrationResult", locked_only)
        self.assertNotIn("ESkyguardMigrationResult", locked_only)
        self.assertNotIn("return ", SAVED_AT_UTC)
        section = public_section(origin_main_header())
        self.assertNotIn("FSkyguardMigrationResult", section)
        self.assertNotIn("ESkyguardMigrationResult", section)

    def test_declaration_does_not_invent_save_version_runtime_return(
        self,
    ) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        self.assertNotIn("return CurrentSaveVersion", SAVED_AT_UTC)
        self.assertNotIn("return MinSupportedSaveVersion", SAVED_AT_UTC)
        self.assertNotIn("return SaveVersion", SAVED_AT_UTC)
        self.assertNotIn("return CurrentSaveVersion", locked_only)
        self.assertNotIn("return MinSupportedSaveVersion", locked_only)
        self.assertNotIn("return SaveVersion", locked_only)
        self.assertNotIn("return ", SAVED_AT_UTC)
        section = public_section(origin_main_header())
        self.assertNotIn("return CurrentSaveVersion", section)
        self.assertNotIn("return MinSupportedSaveVersion", section)
        self.assertNotIn("return SaveVersion", section)

    def test_declaration_does_not_invent_mission_record_payload(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        for token in MISSION_SAVE_RECORD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
        self.assertNotIn("BestScore", SAVED_AT_UTC)
        self.assertNotIn("BestMedalTier", SAVED_AT_UTC)
        self.assertNotIn("BestCompletionTimeSeconds", SAVED_AT_UTC)
        self.assertNotIn("bCompleted", SAVED_AT_UTC)
        self.assertNotIn("BestScore", locked_only)
        self.assertNotIn("BestMedalTier", locked_only)
        self.assertNotIn("BestCompletionTimeSeconds", locked_only)
        self.assertNotIn("bCompleted", locked_only)

    def test_contract_does_not_lock_saved_at_utc_cpp_body(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        self.assertNotIn("{", SAVED_AT_UTC)
        self.assertNotIn("}", SAVED_AT_UTC)
        self.assertNotIn("return ", SAVED_AT_UTC)
        self.assertNotIn(
            "USkyguardCampaignSaveGame::SavedAtUtc",
            SAVED_AT_UTC,
        )
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", SAVED_AT_UTC)
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", locked_only)
        self.assertNotIn("already-v2", SAVED_AT_UTC)
        self.assertNotIn("Identity migrate", SAVED_AT_UTC)
        self.assertNotIn("NewObject", SAVED_AT_UTC)

    def test_contract_does_not_relock_min_supported_save_version(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        for neighbor in MIN_SUPPORTED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVED_AT_UTC)
        self.assertNotIn("MinSupportedSaveVersion", SAVED_AT_UTC)
        self.assertNotIn("MinSupportedSaveVersion", locked_only)
        self.assertNotIn("= 1;", SAVED_AT_UTC)
        self.assertNotIn("= 1;", locked_only)

    def test_contract_does_not_relock_current_save_version(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        for neighbor in CURRENT_SAVE_VERSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVED_AT_UTC)
        self.assertNotIn("CurrentSaveVersion", SAVED_AT_UTC)
        self.assertNotIn("CurrentSaveVersion", locked_only)
        self.assertNotIn("= 2;", SAVED_AT_UTC)
        self.assertNotIn("= 2;", locked_only)

    def test_contract_does_not_relock_migrate_campaign_save(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        for neighbor in MIGRATE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVED_AT_UTC)
        self.assertNotIn("MigrateCampaignSave", SAVED_AT_UTC)
        self.assertNotIn("MigrateCampaignSave", locked_only)

    def test_contract_does_not_relock_save_fields(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        for neighbor in SAVE_FIELDS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVED_AT_UTC)
        self.assertNotIn("SaveVersion", SAVED_AT_UTC)
        self.assertNotIn("SaveVersion", locked_only)
        self.assertNotIn("CampaignId", SAVED_AT_UTC)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("MissionRecords", SAVED_AT_UTC)
        self.assertNotIn("MissionRecords", locked_only)
        self.assertNotIn("int32 SaveVersion = CurrentSaveVersion;", locked_only)
        self.assertNotIn("FSkyguardMissionSaveRecord", locked_only)

    def test_contract_does_not_relock_definition_campaign_id(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        section = public_section(origin_main_header())
        for token in DEFINITION_CAMPAIGN_ID_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, section)
        self.assertNotIn("Skyguard52MainCampaign", SAVED_AT_UTC)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", SAVED_AT_UTC)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        self.assertNotIn("TEXT(", SAVED_AT_UTC)
        self.assertNotIn("TEXT(", locked_only)

    def test_contract_does_not_relock_leftover_mission_save_record(
        self,
    ) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        for token in MISSION_SAVE_RECORD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
        self.assertNotIn("BestScore", locked_only)
        self.assertNotIn("BestMedalTier", locked_only)
        self.assertNotIn("BestCompletionTimeSeconds", locked_only)
        self.assertNotIn("bCompleted", locked_only)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        section = public_section(origin_main_header())
        for token in EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, section)
        self.assertNotIn("already-v2", locked_only)
        self.assertNotIn("Identity migrate", locked_only)
        self.assertNotIn("NewObject MissionRecords", locked_only)
        self.assertNotIn(
            "SkyguardCampaignSaveGameEmptyFailClosedTests",
            locked_only,
        )

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_gunner_helpers(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        section = public_section(origin_main_header())
        for token in (
            "ApplyHydraForClusters",
            "FillAndFinalize",
            "FillAndFail",
            "FillResultCombatStats",
        ):
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        self.assertEqual(
            require_declaration(locked_only, SAVED_AT_UTC),
            SAVED_AT_UTC,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVED_AT_UTC)
        self.assertNotIn("MinSupportedSaveVersion", locked_only)
        self.assertNotIn("CurrentSaveVersion", locked_only)
        self.assertNotIn("MigrateCampaignSave", locked_only)
        self.assertNotIn("int32 SaveVersion = CurrentSaveVersion;", locked_only)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("MissionRecords", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("bInvertLook", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)

    def test_contract_parses_public_section_not_struct_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertIsNotNone(STRUCT_RE.search(header), header)
        self.assertNotIn("bool bCompleted = false;", section)
        self.assertNotIn("int32 BestScore = 0;", section)
        self.assertNotIn("int32 BestMedalTier = 0;", section)
        self.assertNotIn("float BestCompletionTimeSeconds = 0.f;", section)
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSaveGame::SavedAtUtc",
            section,
        )
        self.assertEqual(
            require_declaration(section, SAVED_AT_UTC),
            SAVED_AT_UTC,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSaveGame::SavedAtUtc",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", SAVED_AT_UTC)
        self.assertNotIn("}", SAVED_AT_UTC)
        self.assertNotIn("return ", SAVED_AT_UTC)
        self.assertNotIn("already-v2", SAVED_AT_UTC)
        self.assertNotIn("Identity migrate", SAVED_AT_UTC)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{SAVED_AT_UTC}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, locked_only)
        self.assertNotIn(HARBOR_PAIR, section)
        self.assertNotIn(HARBOR_PAIR, locked_only)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn(HARBOR_CLOCKS[0], section)
        self.assertNotIn(HARBOR_CLOCKS[1], section)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{SAVED_AT_UTC}\n"
        section = public_section(origin_main_header())
        source = Path(__file__).read_text(encoding="utf-8")
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            HARBOR_PAIR,
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, section)
            self.assertNotIn(token, source)

    def test_contract_does_not_require_leftover_live_copy(self) -> None:
        section = public_section(origin_main_header())
        retired_a = "Rif" + "le"
        retired_b = "Ig" + "la"
        retired_c = "Y" + "ak"
        self.assertNotIn(retired_a, section)
        self.assertNotIn(retired_b, section)
        self.assertNotIn(retired_c, section)
        self.assertNotEqual(SAVED_AT_UTC, retired_a)
        self.assertNotEqual(SAVED_AT_UTC, retired_b)
        self.assertNotIn("Fire" + retired_b, section)
        self.assertNotIn("Fire" + retired_a, section)
        self.assertNotIn(retired_c + "SpawnLocation", section)
        self.assertNotIn("b" + retired_c + "RuntimeReady", section)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_leftover_live_copy(self) -> None:
        section = public_section(origin_main_header())
        source = Path(__file__).read_text(encoding="utf-8")
        lowered = section.lower()
        source_lower = source.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"campaign SavedAtUtc contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, SAVED_AT_UTC.lower())
            self.assertNotIn(banned, source_lower)

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", SAVED_AT_UTC)

    def test_contract_is_saved_at_utc_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, SAVED_AT_UTC),
            SAVED_AT_UTC,
        )
        locked_only = f"{SAVED_AT_UTC}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVED_AT_UTC)
        self.assertNotIn("MinSupportedSaveVersion", locked_only)
        self.assertNotIn("CurrentSaveVersion", locked_only)
        self.assertNotIn("MigrateCampaignSave", locked_only)
        self.assertNotIn("int32 SaveVersion = CurrentSaveVersion;", locked_only)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("MissionRecords", locked_only)
        self.assertNotIn("FSkyguardMissionSaveRecord", locked_only)
        self.assertNotIn("BestScore", locked_only)
        self.assertNotIn("BestMedalTier", locked_only)
        self.assertNotIn("BestCompletionTimeSeconds", locked_only)
        self.assertNotIn("bCompleted", locked_only)
        self.assertNotIn("already-v2", locked_only)
        self.assertNotIn("Identity migrate", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("bInvertLook", locked_only)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertNotIn("UPROPERTY", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)
        self.assertNotIn("TEXT(", locked_only)
        for token in INVENTED_UPROPERTY:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
        for token in EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
        for token in MISSION_SAVE_RECORD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
        for token in DEFINITION_CAMPAIGN_ID_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVED_AT_UTC)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SAVED_AT_UTC)
            self.assertNotIn(token, section)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        self.assertNotIn(HARBOR_PAIR, section)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        retired_a = "Rif" + "le"
        retired_b = "Ig" + "la"
        retired_c = "Y" + "ak"
        self.assertNotIn(retired_a, section)
        self.assertNotIn(retired_b, section)
        self.assertNotIn(retired_c, section)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", SAVED_AT_UTC)
        self.assertNotIn("{", SAVED_AT_UTC)
        self.assertNotIn("UFUNCTION", SAVED_AT_UTC)
        self.assertNotEqual(SAVED_AT_UTC, retired_a)
        self.assertNotEqual(SAVED_AT_UTC, retired_b)
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertNotIn("=", SAVED_AT_UTC)
        self.assertTrue(SAVED_AT_UTC.startswith("FDateTime "), SAVED_AT_UTC)
        self.assertTrue(SAVED_AT_UTC.endswith(";"), SAVED_AT_UTC)

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
