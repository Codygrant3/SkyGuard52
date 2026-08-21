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
# mission-record payload, a migration result, or lock the
# MissionRecords body in the .cpp.
# origin/main is one line
# (`TMap<FName, FSkyguardMissionSaveRecord> MissionRecords;`)
# with nearby UPROPERTY(EditAnywhere, BlueprintReadWrite) as
# present on origin/main; accept that form and other
# split-line wraps. Do not invent UPROPERTY metadata that
# is not in origin/main.
# Parse the public class section of
# USkyguardCampaignSaveGame only. Do not lock leftover
# FSkyguardMissionSaveRecord struct fields (#ac38).
MISSION_RECORDS = (
    "TMap<FName, FSkyguardMissionSaveRecord> MissionRecords;"
)
# Nearby UPROPERTY metadata as present on origin/main.
# Do not invent Category, meta, BlueprintReadOnly, or
# other specifiers that are not in origin/main.
UPROPERTY_NEARBY = "UPROPERTY(EditAnywhere, BlueprintReadWrite)"
# Leftover #56–#64 plus CampaignSaveGame production files.
# This lane only adds an isolated Python MissionRecords
# field declaration contract. Stay off CurrentSaveVersion
# #341, MinSupportedSaveVersion #342, leftover
# campaign-save empty-fail-closed, leftover
# mission-save-record defaults #ac38
# (FSkyguardMissionSaveRecord fields), MigrateCampaignSave
# #338, SaveVersion field #345, save-game CampaignId
# (in-flight sibling), SavedAtUtc (sibling this wave),
# leftover CPG debrief #284/#195/#130/#8ccd,
# FillResultCombatStats / FillAndFinalize / FillAndFail /
# ApplyHydraForClusters (leftover ASkyguardGunner*),
# leftover campaign-roster lookup #111, leftover Harbor
# #6/#8/#9, leftover theater-kit #59, leftover flare/HUD
# #57/#61/#62, leftover drafts #56–#64, leftover #147
# ApacheSystem, leftover #149 weapon stations, leftover
# #152 pilot commands, leftover #154 loadout / lock-phase,
# leftover settings invert-look / ApplySettings #134,
# leftover bind-hud-host, leftover objective-runtime
# fail-closed, leftover route-runtime fail-closed,
# leftover pilot #117/#120/#128/#129/#170, leftover
# gun-fire camera shake #8860, leftover mission-weather
# enum #96d2, Harbor IncomingRadar 40/80, leftover live
# copy, FSkyguardMission0NIntegrationReadiness
# (bYakRuntimeReady), and dirty D:\Skyguard52.
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
# record defaults, leftover campaign-roster lookup #111,
# leftover CPG debrief copy / snapshot / fail-closed,
# leftover campaign-subsystem save/load siblings,
# leftover theater-kit / Harbor / flare/HUD, leftover
# ApacheSystem / weapon stations / pilot commands /
# loadout, leftover settings invert-look, leftover
# bind-hud-host, leftover objective-runtime fail-closed,
# leftover route-runtime fail-closed, CurrentSaveVersion
# #341, MinSupportedSaveVersion #342, MigrateCampaignSave
# #338, SaveVersion field #345, campaign definition
# CampaignId / DisplayName, and leftover campaign-roster
# #111 stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
    "Scripts/tests/test_current_save_version_decl_contract.py",
    "Scripts/tests/test_min_supported_save_version_decl_contract.py",
    "Scripts/tests/test_migrate_campaign_save_decl_contract.py",
    "Scripts/tests/test_campaign_save_version_field_decl_contract.py",
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
    "Scripts/tests/test_retry_save_last_debrief_decl_contract.py",
    "Scripts/tests/test_get_last_debrief_decl_contract.py",
    "Scripts/tests/test_get_mission_records_decl_contract.py",
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
    "Scripts/tests/test_set_to_defaults_decl_contract.py",
    "Scripts/tests/test_validate_settings_decl_contract.py",
    "Scripts/tests/test_bind_hud_host_presentation_tests.py",
    "Scripts/tests/test_gun_fire_camera_shake_tests.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
)
# Neighbors in the same public section. Presence is not locked
# here. Leftover #ac38 FSkyguardMissionSaveRecord fields and
# leftover empty-fail-closed identity-migrate stay sibling-only.
# CurrentSaveVersion #341, MinSupportedSaveVersion #342,
# MigrateCampaignSave #338, SaveVersion field #345,
# save-game CampaignId (in-flight), and SavedAtUtc
# (sibling this wave) stay unlocked.
UNLOCKED_NEIGHBORS = (
    "static constexpr int32 MinSupportedSaveVersion = 1;",
    "static constexpr int32 CurrentSaveVersion = 2;",
    "static bool MigrateCampaignSave(USkyguardCampaignSaveGame& SaveGame);",
    "int32 SaveVersion = CurrentSaveVersion;",
    "FName CampaignId;",
    "FDateTime SavedAtUtc;",
)
CURRENT_SAVE_VERSION_NOT_LOCKED = (
    "static constexpr int32 CurrentSaveVersion = 2;",
)
MIN_SUPPORTED_NOT_LOCKED = (
    "static constexpr int32 MinSupportedSaveVersion = 1;",
)
MIGRATE_NOT_LOCKED = (
    "static bool MigrateCampaignSave(USkyguardCampaignSaveGame& SaveGame);",
)
SAVE_VERSION_FIELD_NOT_LOCKED = (
    "int32 SaveVersion = CurrentSaveVersion;",
)
SAVE_FIELDS_NOT_LOCKED = (
    "int32 SaveVersion = CurrentSaveVersion;",
    "FName CampaignId;",
    "FDateTime SavedAtUtc;",
)
GET_MISSION_RECORDS_NOT_LOCKED = (
    "const TMap<FName, FSkyguardMissionSaveRecord>& GetMissionRecords() const",
)
# Invented UPROPERTY metadata that is not on origin/main
# for this field.
INVENTED_UPROPERTY = (
    'Category = "Campaign|Save"',
    'Category="Campaign|Save"',
    "BlueprintReadOnly",
    "VisibleAnywhere",
    "SaveGame",
    "ClampMin",
    "ClampMax",
    "meta = (ClampMin",
)
# Leftover mission-save-record defaults #ac38 stay unlocked.
# Do not lock FSkyguardMissionSaveRecord struct fields.
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
# Leftover Gunner helpers stay unlocked.
FILL_AND_GUNNER_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
    "FillAndFinalize",
    "FillAndFail",
    "ApplyHydraForClusters",
)
# Leftover #147 / #149 / #152 / #154 / invert-look #134 stay
# unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "bInvertLook",
    "InvertLook",
    "FillResultCombatStats",
    "ASkyguardGunner",
    "FillAndFinalize",
    "FillAndFail",
)
# .cpp MissionRecords body / invented INDEX_NONE, migration
# result, or leftover struct payload stay unlocked. Do not
# invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "FSkyguardMigrationResult",
    "ESkyguardMigrationResult",
    "return MissionRecords",
    "USkyguardCampaignSaveGame::MissionRecords",
    "USkyguardCampaignSaveGame::MigrateCampaignSave",
    "SkyguardCampaignSaveGame.cpp",
    "already-v2",
    "Identity migrate",
    "NewObject",
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
CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*<\s*", "<", compact)
    compact = re.sub(r"\s*>\s*", "> ", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
    compact = re.sub(r"\s*&\s*", "& ", compact)
    compact = re.sub(r"\s*=\s*", " = ", compact)
    compact = re.sub(r"\s+", " ", compact).strip()
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


class CampaignSaveMissionRecordsDeclContractTests(unittest.TestCase):
    def test_campaign_save_game_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, MISSION_RECORDS), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedSaveGame "
                ": public USaveGame\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_struct_body_does_not_satisfy_class_lock(self) -> None:
        struct_only = (
            "USTRUCT(BlueprintType)\n"
            "struct FSkyguardMissionSaveRecord\n"
            "{\n"
            "\tGENERATED_BODY()\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadWrite)\n"
            "\tbool bCompleted = false;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            class_body(struct_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API UOtherCampaignSaveGame "
            ": public USaveGame\n"
            "{\n"
            "public:\n"
            f"\t{UPROPERTY_NEARBY}\n"
            f"\t{MISSION_RECORDS}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public USaveGame\n"
            "{\n"
            "private:\n"
            f"\t{UPROPERTY_NEARBY}\n"
            f"\t{MISSION_RECORDS}\n"
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
            "\tstatic constexpr int32 CurrentSaveVersion = 2;\n"
            "private:\n"
            f"\t{UPROPERTY_NEARBY}\n"
            f"\t{MISSION_RECORDS}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, MISSION_RECORDS)
        self.assertIn("MissionRecords", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, MISSION_RECORDS))

    def test_missing_mission_records_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tstatic constexpr int32 MinSupportedSaveVersion = 1;\n"
            "\tstatic constexpr int32 CurrentSaveVersion = 2;\n"
            "\tstatic bool MigrateCampaignSave("
            "USkyguardCampaignSaveGame& SaveGame);\n"
            "\tint32 SaveVersion = CurrentSaveVersion;\n"
            "\tFName CampaignId;\n"
            "\tFDateTime SavedAtUtc;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, MISSION_RECORDS)
        self.assertIn("MissionRecords", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_NEARBY}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, MISSION_RECORDS)
        self.assertIn("MissionRecords", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintCallable, Category = "Campaign|Save")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, MISSION_RECORDS)
        self.assertIn("MissionRecords", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_declaration_accepts_nearby_origin_main_uproperty(self) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, MISSION_RECORDS), section)
        self.assertEqual(
            require_declaration(section, MISSION_RECORDS),
            MISSION_RECORDS,
        )
        self.assertIn(UPROPERTY_NEARBY, section)
        nearby_then_field = (
            "public:\n"
            f"\t{UPROPERTY_NEARBY}\n"
            f"\t{MISSION_RECORDS}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public USaveGame\n{{\n{nearby_then_field}"
        )
        wrapped = public_section(header)
        self.assertTrue(has_declaration(wrapped, MISSION_RECORDS), wrapped)
        self.assertIn(UPROPERTY_NEARBY, wrapped)
        self.assertEqual(
            require_declaration(wrapped, MISSION_RECORDS),
            MISSION_RECORDS,
        )
        self.assertNotIn("UPROPERTY", MISSION_RECORDS)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        self.assertNotIn("UPROPERTY", MISSION_RECORDS)
        self.assertNotIn("UPROPERTY", locked_only)
        self.assertFalse(
            MISSION_RECORDS.startswith("UPROPERTY"),
            MISSION_RECORDS,
        )
        for token in INVENTED_UPROPERTY:
            self.assertNotIn(token, MISSION_RECORDS)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("UFUNCTION", MISSION_RECORDS)
        self.assertNotIn("UFUNCTION", locked_only)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, MISSION_RECORDS), section)
        self.assertEqual(
            require_declaration(section, MISSION_RECORDS),
            MISSION_RECORDS,
        )
        self.assertIn(UPROPERTY_NEARBY, section)
        for token in INVENTED_UPROPERTY:
            self.assertNotIn(token, MISSION_RECORDS)

    def test_neighbor_fields_do_not_satisfy(self) -> None:
        other_fields = (
            "\tstatic constexpr int32 MinSupportedSaveVersion = 1;\n"
            "\tstatic constexpr int32 CurrentSaveVersion = 2;\n"
            "\tstatic bool MigrateCampaignSave("
            "USkyguardCampaignSaveGame& SaveGame);\n"
            "\tint32 SaveVersion = CurrentSaveVersion;\n"
            "\tFName CampaignId;\n"
            "\tFDateTime SavedAtUtc;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_fields, MISSION_RECORDS)
        self.assertIn("MissionRecords", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        tarray = "\tTArray<FSkyguardMissionSaveRecord> MissionRecords;\n"
        string_key = (
            "\tTMap<FString, FSkyguardMissionSaveRecord> MissionRecords;\n"
        )
        wrong_value = "\tTMap<FName, FSkyguardMissionResult> MissionRecords;\n"
        bare_map = "\tTMap MissionRecords;\n"
        wrong_name = (
            "\tTMap<FName, FSkyguardMissionSaveRecord> Records;\n"
        )
        getter = (
            "\tconst TMap<FName, FSkyguardMissionSaveRecord>& "
            "GetMissionRecords() const;\n"
        )
        campaign_id = "\tFName CampaignId;\n"
        saved_at = "\tFDateTime SavedAtUtc;\n"
        save_version = "\tint32 SaveVersion = CurrentSaveVersion;\n"
        for region in (
            tarray,
            string_key,
            wrong_value,
            bare_map,
            wrong_name,
            getter,
            campaign_id,
            saved_at,
            save_version,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, MISSION_RECORDS)
            self.assertIn("MissionRecords", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_getter_declaration_does_not_satisfy_field_lock(self) -> None:
        getter = (
            "\tconst TMap<FName, FSkyguardMissionSaveRecord>& "
            "GetMissionRecords() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(getter, MISSION_RECORDS)
        self.assertIn("MissionRecords", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(getter, MISSION_RECORDS))

    def test_mission_records_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, MISSION_RECORDS),
            MISSION_RECORDS,
        )
        self.assertTrue(has_declaration(section, MISSION_RECORDS))
        self.assertEqual(declaration_count(section, MISSION_RECORDS), 1)
        self.assertTrue(
            MISSION_RECORDS.startswith("TMap<"),
            MISSION_RECORDS,
        )
        self.assertIn("FName", MISSION_RECORDS)
        self.assertIn("FSkyguardMissionSaveRecord", MISSION_RECORDS)
        self.assertIn("MissionRecords", MISSION_RECORDS)
        self.assertTrue(MISSION_RECORDS.endswith(";"), MISSION_RECORDS)
        self.assertNotIn("INDEX_NONE", MISSION_RECORDS)
        self.assertNotIn("UFUNCTION", MISSION_RECORDS)
        self.assertNotIn("UPROPERTY", MISSION_RECORDS)
        self.assertNotIn("{", MISSION_RECORDS)
        self.assertNotIn("}", MISSION_RECORDS)
        self.assertNotIn("return ", MISSION_RECORDS)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_name = (
            "public:\n"
            "\tTMap<FName, FSkyguardMissionSaveRecord>\n"
            "\tMissionRecords;\n"
            "private:\n"
            "};\n"
        )
        wrap_type = (
            "public:\n"
            "\tTMap<FName,\n"
            "\t\tFSkyguardMissionSaveRecord> MissionRecords;\n"
            "private:\n"
            "};\n"
        )
        wrap_template = (
            "public:\n"
            "\tTMap\n"
            "\t<FName, FSkyguardMissionSaveRecord> MissionRecords;\n"
            "};\n"
        )
        wrap_uproperty = (
            "public:\n"
            f"\t{UPROPERTY_NEARBY}\n"
            "\tTMap<FName, FSkyguardMissionSaveRecord>\n"
            "\tMissionRecords;\n"
            "};\n"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public USaveGame\n{{\n{wrap_name}"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public USaveGame\n{{\n{wrap_type}"
        )
        header_wrap_template = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public USaveGame\n{{\n{wrap_template}"
        )
        header_wrap_uproperty = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public USaveGame\n{{\n{wrap_uproperty}"
        )
        for header in (
            header_wrap_name,
            header_wrap_type,
            header_wrap_template,
            header_wrap_uproperty,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, MISSION_RECORDS),
                section,
            )
            self.assertEqual(
                require_declaration(section, MISSION_RECORDS),
                MISSION_RECORDS,
            )
            self.assertEqual(declaration_count(section, MISSION_RECORDS), 1)
        one_line = f"{{\npublic:\n\t{MISSION_RECORDS}\n}}\n"
        self.assertTrue(has_declaration(one_line, MISSION_RECORDS))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, MISSION_RECORDS), section)
        self.assertEqual(
            require_declaration(section, MISSION_RECORDS),
            MISSION_RECORDS,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", MISSION_RECORDS)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", MISSION_RECORDS)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_migration_result(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        self.assertNotIn("FSkyguardMigrationResult", MISSION_RECORDS)
        self.assertNotIn("ESkyguardMigrationResult", MISSION_RECORDS)
        self.assertNotIn("FSkyguardMigrationResult", locked_only)
        self.assertNotIn("ESkyguardMigrationResult", locked_only)
        self.assertNotIn("return ", MISSION_RECORDS)
        section = public_section(origin_main_header())
        self.assertNotIn("FSkyguardMigrationResult", section)
        self.assertNotIn("ESkyguardMigrationResult", section)

    def test_declaration_does_not_lock_struct_fields(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        for token in MISSION_SAVE_RECORD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSION_RECORDS)
        self.assertNotIn("BestScore", MISSION_RECORDS)
        self.assertNotIn("BestMedalTier", MISSION_RECORDS)
        self.assertNotIn("BestCompletionTimeSeconds", MISSION_RECORDS)
        self.assertNotIn("bCompleted", MISSION_RECORDS)
        self.assertNotIn("BestScore", locked_only)
        self.assertNotIn("BestMedalTier", locked_only)
        self.assertNotIn("BestCompletionTimeSeconds", locked_only)
        self.assertNotIn("bCompleted", locked_only)

    def test_contract_does_not_lock_mission_records_cpp_body(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        self.assertNotIn("{", MISSION_RECORDS)
        self.assertNotIn("}", MISSION_RECORDS)
        self.assertNotIn("return ", MISSION_RECORDS)
        self.assertNotIn(
            "USkyguardCampaignSaveGame::MissionRecords",
            MISSION_RECORDS,
        )
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", MISSION_RECORDS)
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", locked_only)
        self.assertNotIn("already-v2", MISSION_RECORDS)
        self.assertNotIn("Identity migrate", MISSION_RECORDS)
        self.assertNotIn("NewObject", MISSION_RECORDS)

    def test_contract_does_not_relock_current_save_version_constexpr(
        self,
    ) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        for neighbor in CURRENT_SAVE_VERSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSION_RECORDS)
        self.assertNotIn(
            "static constexpr int32 CurrentSaveVersion = 2;",
            MISSION_RECORDS,
        )
        self.assertNotIn(
            "static constexpr int32 CurrentSaveVersion = 2;",
            locked_only,
        )
        self.assertNotIn("CurrentSaveVersion", MISSION_RECORDS)
        self.assertNotIn("CurrentSaveVersion", locked_only)

    def test_contract_does_not_relock_min_supported_save_version(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        for neighbor in MIN_SUPPORTED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSION_RECORDS)
        self.assertNotIn("MinSupportedSaveVersion", MISSION_RECORDS)
        self.assertNotIn("MinSupportedSaveVersion", locked_only)

    def test_contract_does_not_relock_migrate_campaign_save(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        for neighbor in MIGRATE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSION_RECORDS)
        self.assertNotIn("MigrateCampaignSave", MISSION_RECORDS)
        self.assertNotIn("MigrateCampaignSave", locked_only)

    def test_contract_does_not_relock_save_version_field(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        for neighbor in SAVE_VERSION_FIELD_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSION_RECORDS)
        self.assertNotIn("SaveVersion", MISSION_RECORDS)
        self.assertNotIn("SaveVersion", locked_only)

    def test_contract_does_not_relock_save_fields(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        for neighbor in SAVE_FIELDS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSION_RECORDS)
        self.assertNotIn("CampaignId", MISSION_RECORDS)
        self.assertNotIn("SavedAtUtc", MISSION_RECORDS)
        self.assertNotIn("SaveVersion", MISSION_RECORDS)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("SavedAtUtc", locked_only)
        self.assertNotIn("SaveVersion", locked_only)

    def test_contract_does_not_relock_get_mission_records_getter(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        for neighbor in GET_MISSION_RECORDS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSION_RECORDS)
        self.assertNotIn("GetMissionRecords", MISSION_RECORDS)
        self.assertNotIn("GetMissionRecords", locked_only)

    def test_contract_does_not_relock_leftover_mission_save_record(
        self,
    ) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        section = public_section(origin_main_header())
        for token in MISSION_SAVE_RECORD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSION_RECORDS)
            self.assertNotIn(token, section)
        self.assertNotIn("BestScore", MISSION_RECORDS)
        self.assertNotIn("BestMedalTier", MISSION_RECORDS)
        self.assertNotIn("BestCompletionTimeSeconds", MISSION_RECORDS)
        self.assertNotIn("bCompleted", MISSION_RECORDS)
        self.assertNotIn("BestScore", locked_only)
        self.assertNotIn("BestMedalTier", locked_only)
        self.assertNotIn("BestCompletionTimeSeconds", locked_only)
        self.assertNotIn("bCompleted", locked_only)
        self.assertNotIn("BestScore", section)
        self.assertNotIn("bCompleted", section)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        section = public_section(origin_main_header())
        for token in EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSION_RECORDS)
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
        locked_only = f"{MISSION_RECORDS}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSION_RECORDS)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSION_RECORDS)
        self.assertNotIn("FillResultCombatStats", MISSION_RECORDS)
        self.assertNotIn("ASkyguardGunner", MISSION_RECORDS)
        self.assertNotIn("FillAndFinalize", MISSION_RECORDS)
        self.assertNotIn("FillAndFail", MISSION_RECORDS)
        self.assertNotIn("ApplyHydraForClusters", MISSION_RECORDS)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSION_RECORDS)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        self.assertEqual(
            require_declaration(locked_only, MISSION_RECORDS),
            MISSION_RECORDS,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSION_RECORDS)
        self.assertNotIn("MinSupportedSaveVersion", locked_only)
        self.assertNotIn("MigrateCampaignSave", locked_only)
        self.assertNotIn(
            "static constexpr int32 CurrentSaveVersion = 2;",
            locked_only,
        )
        self.assertNotIn("SaveVersion", locked_only)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("SavedAtUtc", locked_only)
        self.assertNotIn("GetMissionRecords", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("bInvertLook", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)

    def test_contract_parses_public_section_not_struct_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSaveGame::MissionRecords",
            section,
        )
        self.assertNotIn("bool bCompleted = false;", section)
        self.assertNotIn("int32 BestScore = 0;", section)
        self.assertNotIn("int32 BestMedalTier = 0;", section)
        self.assertNotIn("float BestCompletionTimeSeconds = 0.f;", section)
        self.assertEqual(
            require_declaration(section, MISSION_RECORDS),
            MISSION_RECORDS,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, MISSION_RECORDS)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSaveGame::MissionRecords",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", MISSION_RECORDS)
        self.assertNotIn("}", MISSION_RECORDS)
        self.assertNotIn("return ", MISSION_RECORDS)
        self.assertNotIn("already-v2", MISSION_RECORDS)
        self.assertNotIn("Identity migrate", MISSION_RECORDS)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{MISSION_RECORDS}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, MISSION_RECORDS)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, MISSION_RECORDS)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{MISSION_RECORDS}\n"
        section = public_section(origin_main_header())
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            "40.f, 80.f",
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSION_RECORDS)
            self.assertNotIn(token, section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(MISSION_RECORDS, "Rifle")
        self.assertNotEqual(MISSION_RECORDS, "Igla")
        self.assertNotIn("FireIgla", section)
        self.assertNotIn("FireRifle", section)
        self.assertNotIn("YakSpawnLocation", section)
        self.assertNotIn("bYakRuntimeReady", section)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_igla_yak_rifle(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"campaign MissionRecords contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, MISSION_RECORDS.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", MISSION_RECORDS)

    def test_contract_is_mission_records_field_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, MISSION_RECORDS),
            MISSION_RECORDS,
        )
        locked_only = f"{MISSION_RECORDS}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSION_RECORDS)
        self.assertNotIn("MinSupportedSaveVersion", locked_only)
        self.assertNotIn("MigrateCampaignSave", locked_only)
        self.assertNotIn(
            "static constexpr int32 CurrentSaveVersion = 2;",
            locked_only,
        )
        self.assertNotIn("SaveVersion", locked_only)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("SavedAtUtc", locked_only)
        self.assertNotIn("GetMissionRecords", locked_only)
        self.assertNotIn("BestScore", locked_only)
        self.assertNotIn("BestMedalTier", locked_only)
        self.assertNotIn("BestCompletionTimeSeconds", locked_only)
        self.assertNotIn("bCompleted", locked_only)
        self.assertNotIn("already-v2", locked_only)
        self.assertNotIn("Identity migrate", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("bInvertLook", locked_only)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertNotIn("UPROPERTY", locked_only)
        for token in INVENTED_UPROPERTY:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSION_RECORDS)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSION_RECORDS)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSION_RECORDS)
        for token in EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSION_RECORDS)
        for token in MISSION_SAVE_RECORD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSION_RECORDS)
        for token in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSION_RECORDS)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, MISSION_RECORDS)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, MISSION_RECORDS)
            self.assertNotIn(token, section)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", MISSION_RECORDS)
        self.assertNotIn("{", MISSION_RECORDS)
        self.assertNotIn("UFUNCTION", MISSION_RECORDS)
        self.assertNotEqual(MISSION_RECORDS, "Rifle")
        self.assertNotEqual(MISSION_RECORDS, "Igla")
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertTrue(
            MISSION_RECORDS.startswith("TMap<"),
            MISSION_RECORDS,
        )
        self.assertTrue(MISSION_RECORDS.endswith(";"), MISSION_RECORDS)
        self.assertIn("FSkyguardMissionSaveRecord", MISSION_RECORDS)
        self.assertIn("MissionRecords", MISSION_RECORDS)

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
