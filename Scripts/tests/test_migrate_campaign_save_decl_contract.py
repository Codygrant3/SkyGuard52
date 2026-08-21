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
# migration result, a save-version number as a runtime
# return, a mission-record payload, or lock the
# MigrateCampaignSave body in the .cpp.
# origin/main is one line
# (`static bool MigrateCampaignSave(USkyguardCampaignSaveGame& SaveGame);`);
# accept that form and other split-line wraps.
# origin/main has no UFUNCTION on this method; do not invent
# UFUNCTION metadata.
MIGRATE = (
    "static bool MigrateCampaignSave("
    "USkyguardCampaignSaveGame& SaveGame);"
)
# Leftover #56–#64 plus CampaignSaveGame production files.
# This lane only adds an isolated Python MigrateCampaignSave
# declaration contract. Stay off leftover campaign-save
# empty-fail-closed, leftover mission-save-record defaults
# #ac38 (FSkyguardMissionSaveRecord fields), leftover
# MinSupportedSaveVersion / CurrentSaveVersion constexpr
# locks unless used only to confirm the class exists,
# leftover CPG debrief #284/#195/#130/#8ccd,
# FillResultCombatStats (takes leftover ASkyguardGunner*),
# leftover campaign-roster lookup #111, leftover Harbor
# #6/#8/#9, leftover theater-kit #59, leftover flare/HUD
# #57/#61/#62, leftover drafts #56–#64, leftover #147
# ApacheSystem, leftover #149 weapon stations, leftover
# #152 pilot commands, leftover #154 loadout / lock-phase,
# settings invert-look #134, Harbor IncomingRadar 40/80,
# live copy, FSkyguardMission0NIntegrationReadiness
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
# record defaults, leftover campaign-roster lookup,
# leftover CPG debrief copy / snapshot / fail-closed,
# leftover campaign-subsystem siblings, leftover
# theater-kit / Harbor / flare/HUD, leftover ApacheSystem /
# weapon stations / pilot commands / loadout, and leftover
# settings invert-look stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_roster_id_at_decl_contract.py",
    "Scripts/tests/test_campaign_roster_get_decl_contract.py",
    "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
    "Scripts/tests/test_campaign_roster_loadout_label_decl_contract.py",
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
    "Scripts/tests/test_set_to_defaults_decl_contract.py",
    "Scripts/tests/test_validate_settings_decl_contract.py",
)
# Neighbors in the same public section. Presence is not locked
# here. Leftover #ac38 FSkyguardMissionSaveRecord fields and
# leftover empty-fail-closed identity-migrate stay sibling-only.
# MinSupportedSaveVersion / CurrentSaveVersion are not the
# lock target.
UNLOCKED_NEIGHBORS = (
    "static constexpr int32 MinSupportedSaveVersion = 1;",
    "static constexpr int32 CurrentSaveVersion = 2;",
    "int32 SaveVersion = CurrentSaveVersion;",
    "FName CampaignId;",
    "TMap<FName, FSkyguardMissionSaveRecord> MissionRecords;",
    "FDateTime SavedAtUtc;",
)
VERSION_FIELDS_NOT_LOCKED = (
    "static constexpr int32 MinSupportedSaveVersion = 1;",
    "static constexpr int32 CurrentSaveVersion = 2;",
    "int32 SaveVersion = CurrentSaveVersion;",
)
SAVE_FIELDS_NOT_LOCKED = (
    "FName CampaignId;",
    "TMap<FName, FSkyguardMissionSaveRecord> MissionRecords;",
    "FDateTime SavedAtUtc;",
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
# .cpp MigrateCampaignSave body / invented migration result,
# save-version runtime return, or mission-record payload stay
# unlocked. Do not invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "FSkyguardMigrationResult",
    "ESkyguardMigrationResult",
    "return CurrentSaveVersion",
    "return MinSupportedSaveVersion",
    "return SaveVersion",
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
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
    compact = re.sub(r"\s*&\s*", "& ", compact)
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


class MigrateCampaignSaveDeclContractTests(unittest.TestCase):
    def test_campaign_save_game_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, MIGRATE), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedSaveGame "
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
            f"\t{MIGRATE}\n"
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
            f"\t{MIGRATE}\n"
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
            f"\t{MIGRATE}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, MIGRATE)
        self.assertIn("MigrateCampaignSave", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, MIGRATE))

    def test_missing_migrate_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tstatic constexpr int32 MinSupportedSaveVersion = 1;\n"
            "\tstatic constexpr int32 CurrentSaveVersion = 2;\n"
            "\tint32 SaveVersion = CurrentSaveVersion;\n"
            "\tFName CampaignId;\n"
            "\tTMap<FName, FSkyguardMissionSaveRecord> MissionRecords;\n"
            "\tFDateTime SavedAtUtc;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, MIGRATE)
        self.assertIn("MigrateCampaignSave", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintCallable, Category = "Campaign|Save")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, MIGRATE)
        self.assertIn("MigrateCampaignSave", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{MIGRATE}\n"
        self.assertNotIn("UFUNCTION", MIGRATE)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(MIGRATE.startswith("UFUNCTION"), MIGRATE)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, MIGRATE), section)
        self.assertEqual(require_declaration(section, MIGRATE), MIGRATE)

    def test_neighbor_fields_do_not_satisfy(self) -> None:
        other_fields = (
            "\tstatic constexpr int32 MinSupportedSaveVersion = 1;\n"
            "\tstatic constexpr int32 CurrentSaveVersion = 2;\n"
            "\tint32 SaveVersion = CurrentSaveVersion;\n"
            "\tFName CampaignId;\n"
            "\tTMap<FName, FSkyguardMissionSaveRecord> MissionRecords;\n"
            "\tFDateTime SavedAtUtc;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_fields, MIGRATE)
        self.assertIn("MigrateCampaignSave", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_static = (
            "\tbool MigrateCampaignSave("
            "USkyguardCampaignSaveGame& SaveGame);\n"
        )
        missing_arg = "\tstatic bool MigrateCampaignSave();\n"
        wrong_return = (
            "\tstatic int32 MigrateCampaignSave("
            "USkyguardCampaignSaveGame& SaveGame);\n"
        )
        void_return = (
            "\tstatic void MigrateCampaignSave("
            "USkyguardCampaignSaveGame& SaveGame);\n"
        )
        pointer_arg = (
            "\tstatic bool MigrateCampaignSave("
            "USkyguardCampaignSaveGame* SaveGame);\n"
        )
        const_ref = (
            "\tstatic bool MigrateCampaignSave("
            "const USkyguardCampaignSaveGame& SaveGame);\n"
        )
        const_method = (
            "\tstatic bool MigrateCampaignSave("
            "USkyguardCampaignSaveGame& SaveGame) const;\n"
        )
        for region in (
            missing_static,
            missing_arg,
            wrong_return,
            void_return,
            pointer_arg,
            const_ref,
            const_method,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, MIGRATE)
            self.assertIn("MigrateCampaignSave", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_migrate_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, MIGRATE),
            MIGRATE,
        )
        self.assertTrue(has_declaration(section, MIGRATE))
        self.assertEqual(declaration_count(section, MIGRATE), 1)
        self.assertTrue(MIGRATE.startswith("static bool "), MIGRATE)
        self.assertIn("MigrateCampaignSave(", MIGRATE)
        self.assertIn("USkyguardCampaignSaveGame& SaveGame", MIGRATE)
        self.assertTrue(MIGRATE.endswith(";"), MIGRATE)
        self.assertNotIn("INDEX_NONE", MIGRATE)
        self.assertNotIn("UFUNCTION", MIGRATE)
        self.assertNotIn("{", MIGRATE)
        self.assertNotIn("}", MIGRATE)
        self.assertNotIn("return ", MIGRATE)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_name = (
            "public:\n"
            "\tstatic bool MigrateCampaignSave(\n"
            "\t\tUSkyguardCampaignSaveGame& SaveGame);\n"
            "private:\n"
            "};\n"
        )
        wrap_type = (
            "public:\n"
            "\tstatic bool\n"
            "\tMigrateCampaignSave("
            "USkyguardCampaignSaveGame& SaveGame);\n"
            "private:\n"
            "};\n"
        )
        wrap_arg = (
            "public:\n"
            "\tstatic bool MigrateCampaignSave(USkyguardCampaignSaveGame&\n"
            "\t\tSaveGame);\n"
            "};\n"
        )
        wrap_static = (
            "public:\n"
            "\tstatic\n"
            "\tbool MigrateCampaignSave("
            "USkyguardCampaignSaveGame& SaveGame);\n"
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
        header_wrap_arg = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public USaveGame\n{{\n{wrap_arg}"
        )
        header_wrap_static = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public USaveGame\n{{\n{wrap_static}"
        )
        for header in (
            header_wrap_name,
            header_wrap_type,
            header_wrap_arg,
            header_wrap_static,
        ):
            section = public_section(header)
            self.assertTrue(has_declaration(section, MIGRATE), section)
            self.assertEqual(
                require_declaration(section, MIGRATE),
                MIGRATE,
            )
            self.assertEqual(declaration_count(section, MIGRATE), 1)
        one_line = f"{{\npublic:\n\t{MIGRATE}\n}}\n"
        self.assertTrue(has_declaration(one_line, MIGRATE))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, MIGRATE), section)
        self.assertEqual(
            require_declaration(section, MIGRATE),
            MIGRATE,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{MIGRATE}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", MIGRATE)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", MIGRATE)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_migration_result(self) -> None:
        locked_only = f"{MIGRATE}\n"
        self.assertNotIn("FSkyguardMigrationResult", MIGRATE)
        self.assertNotIn("ESkyguardMigrationResult", MIGRATE)
        self.assertNotIn("FSkyguardMigrationResult", locked_only)
        self.assertNotIn("ESkyguardMigrationResult", locked_only)
        self.assertNotIn("return ", MIGRATE)
        section = public_section(origin_main_header())
        self.assertNotIn("FSkyguardMigrationResult", section)
        self.assertNotIn("ESkyguardMigrationResult", section)

    def test_declaration_does_not_invent_save_version_runtime_return(
        self,
    ) -> None:
        locked_only = f"{MIGRATE}\n"
        self.assertNotIn("return CurrentSaveVersion", MIGRATE)
        self.assertNotIn("return MinSupportedSaveVersion", MIGRATE)
        self.assertNotIn("return SaveVersion", MIGRATE)
        self.assertNotIn("return CurrentSaveVersion", locked_only)
        self.assertNotIn("return MinSupportedSaveVersion", locked_only)
        self.assertNotIn("return SaveVersion", locked_only)
        self.assertNotIn("return ", MIGRATE)
        self.assertFalse(MIGRATE.startswith("static int32 "), MIGRATE)
        section = public_section(origin_main_header())
        self.assertNotIn("return CurrentSaveVersion", section)
        self.assertNotIn("return MinSupportedSaveVersion", section)
        self.assertNotIn("return SaveVersion", section)

    def test_declaration_does_not_invent_mission_record_payload(self) -> None:
        locked_only = f"{MIGRATE}\n"
        for token in MISSION_SAVE_RECORD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MIGRATE)
        self.assertNotIn("BestScore", MIGRATE)
        self.assertNotIn("BestMedalTier", MIGRATE)
        self.assertNotIn("BestCompletionTimeSeconds", MIGRATE)
        self.assertNotIn("bCompleted", MIGRATE)
        self.assertNotIn("BestScore", locked_only)
        self.assertNotIn("BestMedalTier", locked_only)
        self.assertNotIn("BestCompletionTimeSeconds", locked_only)
        self.assertNotIn("bCompleted", locked_only)

    def test_contract_does_not_lock_migrate_cpp_body(self) -> None:
        locked_only = f"{MIGRATE}\n"
        self.assertNotIn("{", MIGRATE)
        self.assertNotIn("}", MIGRATE)
        self.assertNotIn("return ", MIGRATE)
        self.assertNotIn(
            "USkyguardCampaignSaveGame::MigrateCampaignSave",
            MIGRATE,
        )
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", MIGRATE)
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", locked_only)
        self.assertNotIn("already-v2", MIGRATE)
        self.assertNotIn("Identity migrate", MIGRATE)
        self.assertNotIn("NewObject", MIGRATE)

    def test_contract_does_not_relock_version_constexpr_fields(self) -> None:
        locked_only = f"{MIGRATE}\n"
        for neighbor in VERSION_FIELDS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MIGRATE)
        self.assertNotIn("MinSupportedSaveVersion", MIGRATE)
        self.assertNotIn("CurrentSaveVersion", MIGRATE)
        self.assertNotIn("SaveVersion", MIGRATE)
        self.assertNotIn("MinSupportedSaveVersion", locked_only)
        self.assertNotIn("CurrentSaveVersion", locked_only)
        self.assertNotIn("SaveVersion", locked_only)

    def test_contract_does_not_relock_save_fields(self) -> None:
        locked_only = f"{MIGRATE}\n"
        for neighbor in SAVE_FIELDS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MIGRATE)
        self.assertNotIn("CampaignId", MIGRATE)
        self.assertNotIn("MissionRecords", MIGRATE)
        self.assertNotIn("SavedAtUtc", MIGRATE)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("MissionRecords", locked_only)
        self.assertNotIn("SavedAtUtc", locked_only)

    def test_contract_does_not_relock_leftover_mission_save_record(
        self,
    ) -> None:
        locked_only = f"{MIGRATE}\n"
        for token in MISSION_SAVE_RECORD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MIGRATE)
        self.assertNotIn("FSkyguardMissionSaveRecord", MIGRATE)
        self.assertNotIn("FSkyguardMissionSaveRecord", locked_only)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{MIGRATE}\n"
        section = public_section(origin_main_header())
        for token in EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MIGRATE)
            self.assertNotIn(token, section)
        self.assertNotIn("already-v2", locked_only)
        self.assertNotIn("Identity migrate", locked_only)
        self.assertNotIn("NewObject MissionRecords", locked_only)
        self.assertNotIn(
            "SkyguardCampaignSaveGameEmptyFailClosedTests",
            locked_only,
        )

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(self) -> None:
        locked_only = f"{MIGRATE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MIGRATE)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{MIGRATE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MIGRATE)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{MIGRATE}\n"
        self.assertEqual(
            require_declaration(locked_only, MIGRATE),
            MIGRATE,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MIGRATE)
        self.assertNotIn("MinSupportedSaveVersion", locked_only)
        self.assertNotIn("CurrentSaveVersion", locked_only)
        self.assertNotIn("SaveVersion", locked_only)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("MissionRecords", locked_only)
        self.assertNotIn("SavedAtUtc", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("bInvertLook", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSaveGame::MigrateCampaignSave",
            section,
        )
        self.assertEqual(
            require_declaration(section, MIGRATE),
            MIGRATE,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, MIGRATE)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCampaignSaveGame.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSaveGame::MigrateCampaignSave",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", MIGRATE)
        self.assertNotIn("}", MIGRATE)
        self.assertNotIn("return ", MIGRATE)
        self.assertNotIn("already-v2", MIGRATE)
        self.assertNotIn("Identity migrate", MIGRATE)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{MIGRATE}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, MIGRATE)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, MIGRATE)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{MIGRATE}\n"
        section = public_section(origin_main_header())
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            "40.f, 80.f",
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MIGRATE)
            self.assertNotIn(token, section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(MIGRATE, "Rifle")
        self.assertNotEqual(MIGRATE, "Igla")
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
                f"campaign MigrateCampaignSave contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, MIGRATE.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", MIGRATE)

    def test_contract_is_migrate_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, MIGRATE),
            MIGRATE,
        )
        locked_only = f"{MIGRATE}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MIGRATE)
        self.assertNotIn("MinSupportedSaveVersion", locked_only)
        self.assertNotIn("CurrentSaveVersion", locked_only)
        self.assertNotIn("SaveVersion", locked_only)
        self.assertNotIn("CampaignId", locked_only)
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
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MIGRATE)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MIGRATE)
        for token in EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MIGRATE)
        for token in MISSION_SAVE_RECORD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MIGRATE)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, MIGRATE)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, MIGRATE)
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
        self.assertNotIn("return ", MIGRATE)
        self.assertNotIn("{", MIGRATE)
        self.assertNotIn("UFUNCTION", MIGRATE)
        self.assertNotEqual(MIGRATE, "Rifle")
        self.assertNotEqual(MIGRATE, "Igla")
        self.assertNotIn("ApplyHydraForClusters", section)

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
