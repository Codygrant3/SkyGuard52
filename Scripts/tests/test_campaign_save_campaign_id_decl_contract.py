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
# campaign-id body, a save-version runtime return, a
# migration result, a mission-record payload, or lock
# CampaignId in the .cpp.
# origin/main is one line (`FName CampaignId;`);
# accept that form and other split-line wraps. Nearby
# UPROPERTY metadata is present on origin/main; do not
# invent metadata that is not in origin/main.
# This is USkyguardCampaignSaveGame::CampaignId, not
# USkyguardCampaignDefinition::CampaignId.
CAMPAIGN_ID = "FName CampaignId;"
UPROPERTY_CAMPAIGN = "UPROPERTY(EditAnywhere, BlueprintReadWrite)"
# Leftover #56–#64 plus CampaignSaveGame production files.
# This lane only adds an isolated Python CampaignId field
# declaration contract. Stay off leftover campaign-save
# empty-fail-closed, leftover mission-save-record defaults
# #ac38 (FSkyguardMissionSaveRecord fields),
# MigrateCampaignSave #338, CurrentSaveVersion #341,
# MinSupportedSaveVersion (sibling draft this wave),
# SaveVersion field (sibling in-flight), MissionRecords,
# SavedAtUtc, USkyguardCampaignDefinition::CampaignId
# (sibling draft this wave), leftover CPG debrief
# #284/#195/#130/#8ccd, FillResultCombatStats (takes
# leftover ASkyguardGunner*), leftover campaign-roster
# lookup #111, leftover Harbor #6/#8/#9, leftover
# theater-kit #59, leftover flare/HUD #57/#61/#62,
# leftover drafts #56–#64, leftover #147 ApacheSystem,
# leftover #149 weapon stations, leftover #152 pilot
# commands, leftover #154 loadout / lock-phase, leftover
# settings invert-look / ApplySettings broadcast #134,
# Harbor IncomingRadar 40/80, leftover live copy,
# FSkyguardMission0NIntegrationReadiness (bYakRuntimeReady),
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
# settings invert-look, MinSupportedSaveVersion,
# CurrentSaveVersion, MigrateCampaignSave, SaveVersion,
# and USkyguardCampaignDefinition::CampaignId stay
# sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
    "Scripts/tests/test_migrate_campaign_save_decl_contract.py",
    "Scripts/tests/test_current_save_version_decl_contract.py",
    "Scripts/tests/test_min_supported_save_version_decl_contract.py",
    "Scripts/tests/test_save_version_decl_contract.py",
    "Scripts/tests/test_campaign_definition_campaign_id_decl_contract.py",
    "Scripts/tests/test_validate_definition_decl_contract.py",
    "Scripts/tests/test_find_mission_decl_contract.py",
    "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
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
    "Scripts/tests/test_gunship_types_loadout_tests.py",
    "Scripts/tests/test_set_to_defaults_decl_contract.py",
    "Scripts/tests/test_validate_settings_decl_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
)
# Neighbors in the same public section. Presence is not locked
# here. Leftover #ac38 FSkyguardMissionSaveRecord fields and
# leftover empty-fail-closed identity-migrate stay sibling-only.
# MinSupportedSaveVersion is a sibling draft this wave.
# CurrentSaveVersion is #341. MigrateCampaignSave is #338.
# SaveVersion is a sibling in-flight. MissionRecords and
# SavedAtUtc stay unlocked.
UNLOCKED_NEIGHBORS = (
    "static constexpr int32 MinSupportedSaveVersion = 1;",
    "static constexpr int32 CurrentSaveVersion = 2;",
    "static bool MigrateCampaignSave(USkyguardCampaignSaveGame& SaveGame);",
    "int32 SaveVersion = CurrentSaveVersion;",
    "TMap<FName, FSkyguardMissionSaveRecord> MissionRecords;",
    "FDateTime SavedAtUtc;",
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
    "TMap<FName, FSkyguardMissionSaveRecord> MissionRecords;",
    "FDateTime SavedAtUtc;",
)
# USkyguardCampaignDefinition::CampaignId is a sibling draft
# this wave. Do not lock that field or its default.
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
    'Category = "Campaign|Id"',
    "AllowPrivateAccess",
    "meta =",
)
# .cpp CampaignId body / invented INDEX_NONE stay unlocked.
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
    "USkyguardCampaignSaveGame::CampaignId",
    "USkyguardCampaignSaveGame::MinSupportedSaveVersion",
    "USkyguardCampaignSaveGame::CurrentSaveVersion",
    "USkyguardCampaignSaveGame::MigrateCampaignSave",
    "USkyguardCampaignDefinition::CampaignId",
    "SkyguardCampaignSaveGame.cpp",
    "SkyguardCampaignDefinition.cpp",
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


class CampaignSaveCampaignIdDeclContractTests(unittest.TestCase):
    def test_campaign_save_game_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, CAMPAIGN_ID), section)

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
            f"\t{CAMPAIGN_ID}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_definition_class_does_not_satisfy(self) -> None:
        definition = (
            "class SKYGUARD52_API USkyguardCampaignDefinition "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "public:\n"
            '\tFName CampaignId = TEXT("Skyguard52MainCampaign");\n'
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(definition)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public USaveGame\n"
            "{\n"
            "private:\n"
            f"\t{CAMPAIGN_ID}\n"
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
            "\tint32 SaveVersion = CurrentSaveVersion;\n"
            "private:\n"
            f"\t{CAMPAIGN_ID}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, CAMPAIGN_ID)
        self.assertIn("CampaignId", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, CAMPAIGN_ID))

    def test_missing_campaign_id_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tstatic constexpr int32 MinSupportedSaveVersion = 1;\n"
            "\tstatic constexpr int32 CurrentSaveVersion = 2;\n"
            "\tstatic bool MigrateCampaignSave("
            "USkyguardCampaignSaveGame& SaveGame);\n"
            "\tint32 SaveVersion = CurrentSaveVersion;\n"
            "\tTMap<FName, FSkyguardMissionSaveRecord> MissionRecords;\n"
            "\tFDateTime SavedAtUtc;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, CAMPAIGN_ID)
        self.assertIn("CampaignId", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_CAMPAIGN}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, CAMPAIGN_ID)
        self.assertIn("CampaignId", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_CAMPAIGN, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadWrite", section)
        self.assertTrue(has_declaration(section, CAMPAIGN_ID), section)
        self.assertNotIn("UPROPERTY", CAMPAIGN_ID)
        self.assertNotIn("EditAnywhere", CAMPAIGN_ID)
        self.assertNotIn("BlueprintReadWrite", CAMPAIGN_ID)
        self.assertNotIn("Category", CAMPAIGN_ID)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_CAMPAIGN)
            self.assertNotIn(invented, CAMPAIGN_ID)

    def test_neighbor_fields_do_not_satisfy(self) -> None:
        other_fields = (
            "\tstatic constexpr int32 MinSupportedSaveVersion = 1;\n"
            "\tstatic constexpr int32 CurrentSaveVersion = 2;\n"
            "\tstatic bool MigrateCampaignSave("
            "USkyguardCampaignSaveGame& SaveGame);\n"
            "\tint32 SaveVersion = CurrentSaveVersion;\n"
            "\tTMap<FName, FSkyguardMissionSaveRecord> MissionRecords;\n"
            "\tFDateTime SavedAtUtc;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_fields, CAMPAIGN_ID)
        self.assertIn("CampaignId", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        name_none = "\tFName CampaignId = NAME_None;\n"
        definition_default = (
            '\tFName CampaignId = TEXT("Skyguard52MainCampaign");\n'
        )
        wrong_default = '\tFName CampaignId = TEXT("OtherCampaign");\n'
        wrong_type = "\tFString CampaignId;\n"
        text_type = "\tFText CampaignId;\n"
        int_type = "\tint32 CampaignId;\n"
        wrong_name = "\tFName MissionId;\n"
        const_field = "\tconst FName CampaignId;\n"
        for region in (
            name_none,
            definition_default,
            wrong_default,
            wrong_type,
            text_type,
            int_type,
            wrong_name,
            const_field,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CAMPAIGN_ID)
            self.assertIn("CampaignId", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_definition_campaign_id_does_not_satisfy(self) -> None:
        definition_field = (
            '\tFName CampaignId = TEXT("Skyguard52MainCampaign");\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(definition_field, CAMPAIGN_ID)
        self.assertIn("CampaignId", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(definition_field, CAMPAIGN_ID))

    def test_campaign_id_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, CAMPAIGN_ID),
            CAMPAIGN_ID,
        )
        self.assertTrue(has_declaration(section, CAMPAIGN_ID))
        self.assertEqual(
            declaration_count(section, CAMPAIGN_ID),
            1,
        )
        self.assertTrue(
            CAMPAIGN_ID.endswith(";"),
            CAMPAIGN_ID,
        )
        self.assertTrue(
            CAMPAIGN_ID.startswith("FName "),
            CAMPAIGN_ID,
        )
        self.assertIn("CampaignId", CAMPAIGN_ID)
        self.assertNotIn("=", CAMPAIGN_ID)
        self.assertNotIn("TEXT(", CAMPAIGN_ID)
        self.assertNotIn("Skyguard52MainCampaign", CAMPAIGN_ID)
        self.assertNotIn("INDEX_NONE", CAMPAIGN_ID)
        self.assertNotIn("NAME_None", CAMPAIGN_ID)
        self.assertNotIn("UFUNCTION", CAMPAIGN_ID)
        self.assertNotIn("{", CAMPAIGN_ID)
        self.assertNotIn("}", CAMPAIGN_ID)
        self.assertNotIn("return ", CAMPAIGN_ID)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_name = (
            "public:\n"
            "\tFName\n"
            "\tCampaignId;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tFName   CampaignId;\n"
            "private:\n"
            "};\n"
        )
        wrap_tab = (
            "public:\n"
            "\tFName\tCampaignId;\n"
            "};\n"
        )
        wrap_indent = (
            "public:\n"
            "\tFName\n"
            "\t\tCampaignId;\n"
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
        for header in (
            header_wrap_name,
            header_wrap_spaces,
            header_wrap_tab,
            header_wrap_indent,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, CAMPAIGN_ID),
                section,
            )
            self.assertEqual(
                require_declaration(section, CAMPAIGN_ID),
                CAMPAIGN_ID,
            )
            self.assertEqual(
                declaration_count(section, CAMPAIGN_ID),
                1,
            )
        one_line = f"{{\npublic:\n\t{CAMPAIGN_ID}\n}}\n"
        self.assertTrue(has_declaration(one_line, CAMPAIGN_ID))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, CAMPAIGN_ID), section)
        self.assertEqual(
            require_declaration(section, CAMPAIGN_ID),
            CAMPAIGN_ID,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", CAMPAIGN_ID)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", CAMPAIGN_ID)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, CAMPAIGN_ID)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_CAMPAIGN)
        section = public_section(origin_main_header())
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, section)
        self.assertIn(UPROPERTY_CAMPAIGN, section)

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        self.assertNotIn("UFUNCTION", CAMPAIGN_ID)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(CAMPAIGN_ID.startswith("UFUNCTION"), CAMPAIGN_ID)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, CAMPAIGN_ID), section)
        self.assertEqual(
            require_declaration(section, CAMPAIGN_ID),
            CAMPAIGN_ID,
        )

    def test_declaration_does_not_invent_migration_result(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        self.assertNotIn("FSkyguardMigrationResult", CAMPAIGN_ID)
        self.assertNotIn("ESkyguardMigrationResult", CAMPAIGN_ID)
        self.assertNotIn("FSkyguardMigrationResult", locked_only)
        self.assertNotIn("ESkyguardMigrationResult", locked_only)
        self.assertNotIn("return ", CAMPAIGN_ID)
        section = public_section(origin_main_header())
        self.assertNotIn("FSkyguardMigrationResult", section)
        self.assertNotIn("ESkyguardMigrationResult", section)

    def test_declaration_does_not_invent_save_version_runtime_return(
        self,
    ) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        self.assertNotIn("return CurrentSaveVersion", CAMPAIGN_ID)
        self.assertNotIn("return MinSupportedSaveVersion", CAMPAIGN_ID)
        self.assertNotIn("return SaveVersion", CAMPAIGN_ID)
        self.assertNotIn("return CurrentSaveVersion", locked_only)
        self.assertNotIn("return MinSupportedSaveVersion", locked_only)
        self.assertNotIn("return SaveVersion", locked_only)
        self.assertNotIn("return ", CAMPAIGN_ID)
        section = public_section(origin_main_header())
        self.assertNotIn("return CurrentSaveVersion", section)
        self.assertNotIn("return MinSupportedSaveVersion", section)
        self.assertNotIn("return SaveVersion", section)

    def test_declaration_does_not_invent_mission_record_payload(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        for token in MISSION_SAVE_RECORD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_ID)
        self.assertNotIn("BestScore", CAMPAIGN_ID)
        self.assertNotIn("BestMedalTier", CAMPAIGN_ID)
        self.assertNotIn("BestCompletionTimeSeconds", CAMPAIGN_ID)
        self.assertNotIn("bCompleted", CAMPAIGN_ID)
        self.assertNotIn("BestScore", locked_only)
        self.assertNotIn("BestMedalTier", locked_only)
        self.assertNotIn("BestCompletionTimeSeconds", locked_only)
        self.assertNotIn("bCompleted", locked_only)

    def test_contract_does_not_lock_campaign_id_cpp_body(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        self.assertNotIn("{", CAMPAIGN_ID)
        self.assertNotIn("}", CAMPAIGN_ID)
        self.assertNotIn("return ", CAMPAIGN_ID)
        self.assertNotIn(
            "USkyguardCampaignSaveGame::CampaignId",
            CAMPAIGN_ID,
        )
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", CAMPAIGN_ID)
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", locked_only)
        self.assertNotIn("already-v2", CAMPAIGN_ID)
        self.assertNotIn("Identity migrate", CAMPAIGN_ID)
        self.assertNotIn("NewObject", CAMPAIGN_ID)

    def test_contract_does_not_relock_min_supported_save_version(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        for neighbor in MIN_SUPPORTED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAMPAIGN_ID)
        self.assertNotIn("MinSupportedSaveVersion", CAMPAIGN_ID)
        self.assertNotIn("MinSupportedSaveVersion", locked_only)
        self.assertNotIn("= 1;", CAMPAIGN_ID)
        self.assertNotIn("= 1;", locked_only)

    def test_contract_does_not_relock_current_save_version(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        for neighbor in CURRENT_SAVE_VERSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAMPAIGN_ID)
        self.assertNotIn("CurrentSaveVersion", CAMPAIGN_ID)
        self.assertNotIn("CurrentSaveVersion", locked_only)
        self.assertNotIn("= 2;", CAMPAIGN_ID)
        self.assertNotIn("= 2;", locked_only)

    def test_contract_does_not_relock_migrate_campaign_save(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        for neighbor in MIGRATE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAMPAIGN_ID)
        self.assertNotIn("MigrateCampaignSave", CAMPAIGN_ID)
        self.assertNotIn("MigrateCampaignSave", locked_only)

    def test_contract_does_not_relock_save_fields(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        for neighbor in SAVE_FIELDS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAMPAIGN_ID)
        self.assertNotIn("SaveVersion", CAMPAIGN_ID)
        self.assertNotIn("SaveVersion", locked_only)
        self.assertNotIn("MissionRecords", CAMPAIGN_ID)
        self.assertNotIn("MissionRecords", locked_only)
        self.assertNotIn("SavedAtUtc", CAMPAIGN_ID)
        self.assertNotIn("SavedAtUtc", locked_only)
        self.assertNotIn("int32 SaveVersion = CurrentSaveVersion;", locked_only)
        self.assertNotIn("FSkyguardMissionSaveRecord", locked_only)

    def test_contract_does_not_relock_definition_campaign_id(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        section = public_section(origin_main_header())
        for token in DEFINITION_CAMPAIGN_ID_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_ID)
            self.assertNotIn(token, section)
        self.assertNotIn("Skyguard52MainCampaign", CAMPAIGN_ID)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", CAMPAIGN_ID)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        self.assertNotIn("TEXT(", CAMPAIGN_ID)
        self.assertNotIn("TEXT(", locked_only)

    def test_contract_does_not_relock_leftover_mission_save_record(
        self,
    ) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        for token in MISSION_SAVE_RECORD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_ID)
        self.assertNotIn("BestScore", locked_only)
        self.assertNotIn("BestMedalTier", locked_only)
        self.assertNotIn("BestCompletionTimeSeconds", locked_only)
        self.assertNotIn("bCompleted", locked_only)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        for token in EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_ID)
        self.assertNotIn("already-v2", locked_only)
        self.assertNotIn("Identity migrate", locked_only)
        self.assertNotIn("NewObject MissionRecords", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_ID)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_ID)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        self.assertEqual(
            require_declaration(locked_only, CAMPAIGN_ID),
            CAMPAIGN_ID,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAMPAIGN_ID)
        self.assertNotIn("MinSupportedSaveVersion", locked_only)
        self.assertNotIn("CurrentSaveVersion", locked_only)
        self.assertNotIn("MigrateCampaignSave", locked_only)
        self.assertNotIn("int32 SaveVersion = CurrentSaveVersion;", locked_only)
        self.assertNotIn("MissionRecords", locked_only)
        self.assertNotIn("SavedAtUtc", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("bInvertLook", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSaveGame::CampaignId",
            section,
        )
        self.assertEqual(
            require_declaration(section, CAMPAIGN_ID),
            CAMPAIGN_ID,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CAMPAIGN_ID)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSaveGame::CampaignId",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", CAMPAIGN_ID)
        self.assertNotIn("}", CAMPAIGN_ID)
        self.assertNotIn("return ", CAMPAIGN_ID)
        self.assertNotIn("already-v2", CAMPAIGN_ID)
        self.assertNotIn("Identity migrate", CAMPAIGN_ID)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{CAMPAIGN_ID}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, CAMPAIGN_ID)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, CAMPAIGN_ID)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{CAMPAIGN_ID}\n"
        section = public_section(origin_main_header())
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            "40.f, 80.f",
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_ID)
            self.assertNotIn(token, section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(CAMPAIGN_ID, "Rifle")
        self.assertNotEqual(CAMPAIGN_ID, "Igla")
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
                f"campaign CampaignId contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, CAMPAIGN_ID.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", CAMPAIGN_ID)

    def test_contract_is_campaign_id_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, CAMPAIGN_ID),
            CAMPAIGN_ID,
        )
        locked_only = f"{CAMPAIGN_ID}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAMPAIGN_ID)
        self.assertNotIn("MinSupportedSaveVersion", locked_only)
        self.assertNotIn("CurrentSaveVersion", locked_only)
        self.assertNotIn("MigrateCampaignSave", locked_only)
        self.assertNotIn("int32 SaveVersion = CurrentSaveVersion;", locked_only)
        self.assertNotIn("MissionRecords", locked_only)
        self.assertNotIn("SavedAtUtc", locked_only)
        self.assertNotIn("FSkyguardMissionSaveRecord", locked_only)
        self.assertNotIn("BestScore", locked_only)
        self.assertNotIn("BestMedalTier", locked_only)
        self.assertNotIn("BestCompletionTimeSeconds", locked_only)
        self.assertNotIn("bCompleted", locked_only)
        self.assertNotIn("already-v2", locked_only)
        self.assertNotIn("Identity migrate", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("bInvertLook", locked_only)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)
        self.assertNotIn("TEXT(", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_ID)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_ID)
        for token in EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_ID)
        for token in MISSION_SAVE_RECORD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_ID)
        for token in DEFINITION_CAMPAIGN_ID_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_ID)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, CAMPAIGN_ID)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CAMPAIGN_ID)
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
        self.assertNotIn("return ", CAMPAIGN_ID)
        self.assertNotIn("{", CAMPAIGN_ID)
        self.assertNotIn("UFUNCTION", CAMPAIGN_ID)
        self.assertNotEqual(CAMPAIGN_ID, "Rifle")
        self.assertNotEqual(CAMPAIGN_ID, "Igla")
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertNotIn("=", CAMPAIGN_ID)
        self.assertTrue(CAMPAIGN_ID.startswith("FName "), CAMPAIGN_ID)
        self.assertTrue(CAMPAIGN_ID.endswith(";"), CAMPAIGN_ID)

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
