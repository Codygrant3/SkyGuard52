from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardCampaignDefinition.h"
CLASS_NAME = "USkyguardCampaignDefinition"
# Declaration presence only. Do not invent INDEX_NONE,
# display-name text, or lock DisplayName in the .cpp.
# origin/main is one line (`FText DisplayName;`);
# accept that form and other split-line wraps. Nearby
# UPROPERTY metadata is present on origin/main; do not
# invent metadata that is not in origin/main.
DISPLAY_NAME = "FText DisplayName;"
UPROPERTY_CAMPAIGN = (
    'UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Campaign")'
)
# Leftover #56–#64 plus CampaignDefinition production files.
# This lane only adds an isolated Python DisplayName field
# declaration contract. Stay off CampaignId (sibling draft
# this wave), Missions array, ValidateDefinition #331,
# FindMission #340, GetPrimaryAssetId #339, leftover
# campaign-roster #111, leftover campaign-save
# empty-fail-closed, USkyguardCampaignSubsystem methods,
# LoadCampaignProgress #290, leftover CPG debrief
# #284/#195/#130/#8ccd, FillResultCombatStats /
# FillAndFinalize / FillAndFail / ApplyHydraForClusters
# (leftover ASkyguardGunner*), leftover Harbor #6/#8/#9,
# leftover theater-kit #59, leftover flare/HUD #57/#61/#62,
# leftover drafts #56–#64, leftover #147 ApacheSystem,
# leftover #149 weapon stations, leftover #152 pilot
# commands, leftover #154 loadout / lock-phase, leftover
# settings invert-look / ApplySettings broadcast #134,
# Harbor IncomingRadar 40/80, leftover live copy,
# FSkyguardMission0NIntegrationReadiness (bYakRuntimeReady),
# and dirty D:\Skyguard52.
LOCKED = {
    "SkyguardCampaignDefinition.h",
    "SkyguardCampaignDefinition.cpp",
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
# campaign-save empty-fail-closed, leftover campaign-roster
# lookup, leftover LoadCampaignProgressAfterConfigure,
# leftover CPG debrief copy / snapshot / fail-closed,
# leftover objective-runtime fail-closed, leftover
# route-runtime fail-closed, leftover theater-kit / Harbor /
# flare/HUD, leftover settings invert-look / ApplySettings
# broadcast, CampaignId (sibling draft this wave),
# ValidateDefinition #331, FindMission #340,
# GetPrimaryAssetId #339, and newly drafted
# campaign-subsystem siblings stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_roster_get_decl_contract.py",
    "Scripts/tests/test_campaign_roster_id_at_decl_contract.py",
    "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
    "Scripts/tests/test_campaign_roster_loadout_label_decl_contract.py",
    "Scripts/tests/test_campaign_roster_weather_enum_label_decl_contract.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
    "Scripts/tests/test_campaign_definition_campaign_id_decl_contract.py",
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
    "Scripts/tests/test_apply_save_game_decl_contract.py",
    "Scripts/tests/test_build_save_game_decl_contract.py",
    "Scripts/tests/test_get_mission_records_decl_contract.py",
    "Scripts/tests/test_save_campaign_to_slot_decl_contract.py",
    "Scripts/tests/test_load_campaign_from_slot_decl_contract.py",
    "Scripts/tests/test_delete_campaign_slot_decl_contract.py",
    "Scripts/tests/test_retry_save_last_debrief_decl_contract.py",
    "Scripts/tests/test_get_last_debrief_decl_contract.py",
    "Scripts/tests/test_calculate_mission_score_decl_contract.py",
    "Scripts/tests/test_calculate_medal_tier_decl_contract.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
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
# Neighbors in the same public section. Presence is not locked
# here. CampaignId (sibling draft this wave) /
# ValidateDefinition #331 / FindMission #340 /
# GetPrimaryAssetId #339 / Missions stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "FName CampaignId",
    "TArray<TObjectPtr<USkyguardMissionDefinition>> Missions",
    "virtual FPrimaryAssetId GetPrimaryAssetId() const override;",
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;",
    "USkyguardMissionDefinition* FindMission(FName MissionId) const;",
)
VALIDATE_DEFINITION_NOT_LOCKED = (
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;",
)
FIND_MISSION_NOT_LOCKED = (
    "USkyguardMissionDefinition* FindMission(FName MissionId) const;",
)
PRIMARY_ASSET_NOT_LOCKED = (
    "virtual FPrimaryAssetId GetPrimaryAssetId() const override;",
)
CAMPAIGN_ID_NOT_LOCKED = (
    'FName CampaignId = TEXT("Skyguard52MainCampaign");',
)
MISSIONS_NOT_LOCKED = (
    "TArray<TObjectPtr<USkyguardMissionDefinition>> Missions",
)
# USkyguardCampaignSubsystem helpers stay unlocked. This lane
# is DisplayName on USkyguardCampaignDefinition only.
SUBSYSTEM_NOT_LOCKED = (
    "bool ConfigureCampaign(USkyguardCampaignDefinition* InCampaign);",
    "bool CanStartMission(FName MissionId) const;",
    "bool StartMission(FName MissionId);",
    "bool IsMissionUnlocked(FName MissionId) const;",
    "bool AddObjectiveProgress(FName ObjectiveId, int32 Amount = 1);",
    "bool FailObjective(FName ObjectiveId);",
    "bool CompleteSurviveObjectiveIfIntact(FName ObjectiveId);",
    "bool CompleteActiveMission(FSkyguardMissionResult& InOutResult);",
    "bool FinalizeActiveMission(",
    "bool FailActiveMission(",
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
    "float GetActiveMissionElapsedSeconds(",
    "bool AcknowledgeDebrief();",
    "const FSkyguardMissionDebrief& GetLastDebrief() const",
    "bool CanTravelToNextMission() const;",
    "FString GetNextMissionMapPackageName() const;",
    "bool TravelToNextMission(UObject* WorldContextObject);",
    "bool ApplySaveGame(const USkyguardCampaignSaveGame* SaveGame);",
    "USkyguardCampaignSaveGame* BuildSaveGame() const;",
    "bool RetrySaveLastDebrief(",
    "bool SaveCampaignToSlot(",
    "bool LoadCampaignFromSlot(",
    "bool DeleteCampaignSlot(",
    "static bool IsValidCampaignSlotName(const FString& SlotName);",
    "int32 GetEarnedCampaignMedals() const;",
    "USkyguardMissionDefinition* GetActiveMission() const",
    "USkyguardObjectiveRuntime* GetObjectiveRuntime() const",
    "USkyguardRouteRuntime* GetRouteRuntime() const",
    "const TMap<FName, FSkyguardMissionSaveRecord>& GetMissionRecords() const",
    "static int32 CalculateMissionScore(",
    "static int32 CalculateMedalTier(",
    "LoadCampaignProgressAfterConfigure",
)
SAVE_GAME_NOT_LOCKED = (
    "bool ApplySaveGame(const USkyguardCampaignSaveGame* SaveGame);",
    "USkyguardCampaignSaveGame* BuildSaveGame() const;",
    "bool RetrySaveLastDebrief(",
    "bool SaveCampaignToSlot(",
    "bool LoadCampaignFromSlot(",
    "bool DeleteCampaignSlot(",
    "const TMap<FName, FSkyguardMissionSaveRecord>& GetMissionRecords() const",
)
FILL_AND_GUNNER_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
    "FillAndFinalize",
    "FillAndFail",
    "ApplyHydraForClusters",
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
# Leftover #147 / #149 / #152 / #154 / #290 / #134 / Hydra
# cluster apply / leftover Gunner FillAnd* stay unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "LoadCampaignProgressAfterConfigure",
    "FillAndFinalize",
    "FillAndFail",
    "bInvertLook",
    "ApplySettings",
)
# Invented UPROPERTY specifiers that are not on origin/main
# for this field. Nearby origin/main metadata is
# EditAnywhere, BlueprintReadOnly, Category = "Campaign".
INVENTED_UPROPERTY = (
    "BlueprintReadWrite",
    "VisibleAnywhere",
    "VisibleDefaultsOnly",
    "EditDefaultsOnly",
    "SaveGame",
    'Category = "Campaign|Display"',
    "AllowPrivateAccess",
    "meta =",
)
# Invented display-name text is not on origin/main.
# Do not invent NSLOCTEXT / LOCTEXT / FromString copy.
INVENTED_DISPLAY_TEXT = (
    "NSLOCTEXT",
    "LOCTEXT",
    "INVTEXT",
    "FText::FromString",
    "FText::FromName",
)
# .cpp DisplayName body / invented INDEX_NONE stay unlocked.
# Do not invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "USkyguardCampaignDefinition::DisplayName",
    "SkyguardCampaignDefinition.cpp",
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


class CampaignDefinitionDisplayNameDeclContractTests(unittest.TestCase):
    def test_campaign_definition_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, DISPLAY_NAME), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedCampaign "
                ": public UPrimaryDataAsset\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API UOtherCampaignDefinition "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "public:\n"
            f"\t{DISPLAY_NAME}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "private:\n"
            f"\t{DISPLAY_NAME}\n"
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
            ": public UPrimaryDataAsset\n"
            "{\n"
            "public:\n"
            '\tFName CampaignId = TEXT("Skyguard52MainCampaign");\n'
            "private:\n"
            f"\t{DISPLAY_NAME}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, DISPLAY_NAME)
        self.assertIn("DisplayName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, DISPLAY_NAME))

    def test_missing_display_name_declaration_fails_closed(self) -> None:
        neighbors_only = (
            '\tFName CampaignId = TEXT("Skyguard52MainCampaign");\n'
            "\tTArray<TObjectPtr<USkyguardMissionDefinition>> Missions;\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() "
            "const override;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
            "\tUSkyguardMissionDefinition* FindMission("
            "FName MissionId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, DISPLAY_NAME)
        self.assertIn("DisplayName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_CAMPAIGN}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, DISPLAY_NAME)
        self.assertIn("DisplayName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_CAMPAIGN, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('Category = "Campaign"', section)
        self.assertTrue(has_declaration(section, DISPLAY_NAME), section)
        self.assertNotIn("UPROPERTY", DISPLAY_NAME)
        self.assertNotIn("EditAnywhere", DISPLAY_NAME)
        self.assertNotIn("BlueprintReadOnly", DISPLAY_NAME)
        self.assertNotIn("Category", DISPLAY_NAME)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_CAMPAIGN)
            self.assertNotIn(invented, DISPLAY_NAME)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            '\tFName CampaignId = TEXT("Skyguard52MainCampaign");\n'
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() "
            "const override;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
            "\tUSkyguardMissionDefinition* FindMission("
            "FName MissionId) const;\n"
            "\tTArray<TObjectPtr<USkyguardMissionDefinition>> Missions;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, DISPLAY_NAME)
        self.assertIn("DisplayName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        name_type = "\tFName DisplayName;\n"
        string_type = "\tFString DisplayName;\n"
        wrong_name = "\tFText CampaignName;\n"
        assigned_ns = (
            '\tFText DisplayName = NSLOCTEXT("Skyguard", '
            '"Campaign", "Skyguard");\n'
        )
        assigned_from_string = (
            "\tFText DisplayName = FText::FromString("
            'TEXT("Skyguard"));\n'
        )
        campaign_id = (
            '\tFName CampaignId = TEXT("Skyguard52MainCampaign");\n'
        )
        for region in (
            name_type,
            string_type,
            wrong_name,
            assigned_ns,
            assigned_from_string,
            campaign_id,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, DISPLAY_NAME)
            self.assertIn("DisplayName", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_invented_display_name_assignment_does_not_satisfy(self) -> None:
        assigned = (
            '\tFText DisplayName = NSLOCTEXT("Skyguard", '
            '"Display", "Skyguard 52");\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(assigned, DISPLAY_NAME)
        self.assertIn("DisplayName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(assigned, DISPLAY_NAME))

    def test_wrong_type_does_not_satisfy(self) -> None:
        wrong = "\tFName DisplayName;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(wrong, DISPLAY_NAME)
        self.assertIn("DisplayName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(wrong, DISPLAY_NAME))

    def test_display_name_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, DISPLAY_NAME),
            DISPLAY_NAME,
        )
        self.assertTrue(has_declaration(section, DISPLAY_NAME))
        self.assertEqual(
            declaration_count(section, DISPLAY_NAME),
            1,
        )
        self.assertTrue(
            DISPLAY_NAME.endswith(";"),
            DISPLAY_NAME,
        )
        self.assertTrue(
            DISPLAY_NAME.startswith("FText "),
            DISPLAY_NAME,
        )
        self.assertIn("DisplayName", DISPLAY_NAME)
        self.assertNotIn("=", DISPLAY_NAME)
        self.assertNotIn("INDEX_NONE", DISPLAY_NAME)
        self.assertNotIn("NAME_None", DISPLAY_NAME)
        self.assertNotIn("{", DISPLAY_NAME)
        self.assertNotIn("}", DISPLAY_NAME)
        self.assertNotIn("return ", DISPLAY_NAME)

    def test_declaration_does_not_invent_display_name_text(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        self.assertNotIn("=", DISPLAY_NAME)
        self.assertNotIn("TEXT(", DISPLAY_NAME)
        self.assertNotIn("Skyguard52MainCampaign", DISPLAY_NAME)
        for invented in INVENTED_DISPLAY_TEXT:
            self.assertNotIn(invented, DISPLAY_NAME)
            self.assertNotIn(invented, locked_only)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, DISPLAY_NAME), section)
        for invented in INVENTED_DISPLAY_TEXT:
            self.assertNotIn(invented, section)
        self.assertNotIn("NAME_None", DISPLAY_NAME)
        self.assertNotIn("INDEX_NONE", DISPLAY_NAME)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tFText\n"
            "\tDisplayName;\n"
            "private:\n"
            "};\n"
        )
        wrap_semi = (
            "public:\n"
            "\tFText DisplayName\n"
            "\t;\n"
            "private:\n"
            "};\n"
        )
        wrap_both = (
            "public:\n"
            "\tFText\n"
            "\tDisplayName\n"
            "\t;\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tFText    DisplayName   ;\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_type}"
        )
        header_wrap_semi = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_semi}"
        )
        header_wrap_both = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_both}"
        )
        header_wrap_spaces = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_spaces}"
        )
        for header in (
            header_wrap_type,
            header_wrap_semi,
            header_wrap_both,
            header_wrap_spaces,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, DISPLAY_NAME),
                section,
            )
            self.assertEqual(
                require_declaration(section, DISPLAY_NAME),
                DISPLAY_NAME,
            )
            self.assertEqual(
                declaration_count(section, DISPLAY_NAME),
                1,
            )
        one_line = f"{{\npublic:\n\t{DISPLAY_NAME}\n}}\n"
        self.assertTrue(has_declaration(one_line, DISPLAY_NAME))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, DISPLAY_NAME), section)
        self.assertEqual(
            require_declaration(section, DISPLAY_NAME),
            DISPLAY_NAME,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", DISPLAY_NAME)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", DISPLAY_NAME)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, DISPLAY_NAME)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_CAMPAIGN)
        section = public_section(origin_main_header())
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, section)
        self.assertIn(UPROPERTY_CAMPAIGN, section)

    def test_contract_does_not_lock_display_name_cpp_body(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        self.assertNotIn("{", DISPLAY_NAME)
        self.assertNotIn("}", DISPLAY_NAME)
        self.assertNotIn("return ", DISPLAY_NAME)
        self.assertNotIn(
            "USkyguardCampaignDefinition::DisplayName",
            DISPLAY_NAME,
        )
        self.assertNotIn(
            "SkyguardCampaignDefinition.cpp",
            DISPLAY_NAME,
        )
        self.assertNotIn("SkyguardCampaignDefinition.cpp", locked_only)
        self.assertNotIn("return false", DISPLAY_NAME)
        self.assertNotIn("AddError", DISPLAY_NAME)

    def test_contract_does_not_relock_campaign_id(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        for neighbor in CAMPAIGN_ID_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, DISPLAY_NAME)
        self.assertNotIn("CampaignId", DISPLAY_NAME)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("Skyguard52MainCampaign", DISPLAY_NAME)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)
        self.assertNotIn("FName", DISPLAY_NAME)

    def test_contract_does_not_relock_missions(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        for neighbor in MISSIONS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, DISPLAY_NAME)
        self.assertNotIn("Missions", DISPLAY_NAME)
        self.assertNotIn("Missions", locked_only)
        self.assertNotIn("TArray", DISPLAY_NAME)
        self.assertNotIn("TObjectPtr", DISPLAY_NAME)

    def test_contract_does_not_relock_validate_definition(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        for neighbor in VALIDATE_DEFINITION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, DISPLAY_NAME)
        self.assertNotIn("ValidateDefinition", DISPLAY_NAME)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("OutErrors", DISPLAY_NAME)
        self.assertNotIn("BlueprintCallable", DISPLAY_NAME)

    def test_contract_does_not_relock_find_mission(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        for neighbor in FIND_MISSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, DISPLAY_NAME)
        self.assertNotIn("FindMission", DISPLAY_NAME)
        self.assertNotIn("FindMission", locked_only)
        self.assertNotIn("BlueprintPure", DISPLAY_NAME)

    def test_contract_does_not_relock_primary_asset_id(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        for neighbor in PRIMARY_ASSET_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, DISPLAY_NAME)
        self.assertNotIn("GetPrimaryAssetId", DISPLAY_NAME)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("FPrimaryAssetId", DISPLAY_NAME)

    def test_contract_does_not_relock_campaign_subsystem_methods(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        section = public_section(origin_main_header())
        for neighbor in SUBSYSTEM_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, DISPLAY_NAME)
            self.assertNotIn(neighbor, section)
        self.assertNotIn("ConfigureCampaign", DISPLAY_NAME)
        self.assertNotIn("CanStartMission", DISPLAY_NAME)
        self.assertNotIn("StartMission", DISPLAY_NAME)
        self.assertNotIn("GetActiveMission", DISPLAY_NAME)
        self.assertNotIn("USkyguardCampaignSubsystem", DISPLAY_NAME)
        self.assertNotIn("USkyguardCampaignSubsystem", locked_only)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("StartMission", locked_only)

    def test_contract_does_not_relock_save_game_helpers(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        for neighbor in SAVE_GAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, DISPLAY_NAME)
        self.assertNotIn("ApplySaveGame", DISPLAY_NAME)
        self.assertNotIn("BuildSaveGame", DISPLAY_NAME)
        self.assertNotIn("RetrySaveLastDebrief", DISPLAY_NAME)
        self.assertNotIn("SaveCampaignToSlot", DISPLAY_NAME)
        self.assertNotIn("LoadCampaignFromSlot", DISPLAY_NAME)
        self.assertNotIn("DeleteCampaignSlot", DISPLAY_NAME)
        self.assertNotIn("GetMissionRecords", DISPLAY_NAME)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("BuildSaveGame", locked_only)
        self.assertNotIn("RetrySaveLastDebrief", locked_only)
        self.assertNotIn("SaveCampaignToSlot", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("GetMissionRecords", locked_only)

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, DISPLAY_NAME)
        self.assertNotIn("FillResultCombatStats", DISPLAY_NAME)
        self.assertNotIn("ASkyguardGunner", DISPLAY_NAME)
        self.assertNotIn("FillAndFinalize", DISPLAY_NAME)
        self.assertNotIn("FillAndFail", DISPLAY_NAME)
        self.assertNotIn("ApplyHydraForClusters", DISPLAY_NAME)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, DISPLAY_NAME)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, DISPLAY_NAME)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, DISPLAY_NAME)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        self.assertEqual(
            require_declaration(locked_only, DISPLAY_NAME),
            DISPLAY_NAME,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, DISPLAY_NAME)
        self.assertNotIn("FindMission", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("Missions", locked_only)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("BuildSaveGame", locked_only)
        self.assertNotIn("RetrySaveLastDebrief", locked_only)
        self.assertNotIn("GetMissionRecords", locked_only)
        self.assertNotIn("LoadCampaignProgressAfterConfigure", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("OutErrors.Reset", section)
        self.assertNotIn("AddError", section)
        self.assertNotIn("MissionOrderById", section)
        self.assertNotIn("UsedOrders", section)
        self.assertEqual(
            require_declaration(section, DISPLAY_NAME),
            DISPLAY_NAME,
        )
        self.assertNotIn("SkyguardCampaignDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignDefinition::DisplayName",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, DISPLAY_NAME)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCampaignDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignDefinition::DisplayName",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", DISPLAY_NAME)
        self.assertNotIn("}", DISPLAY_NAME)
        self.assertNotIn("return false", DISPLAY_NAME)
        self.assertNotIn("AddError", DISPLAY_NAME)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{DISPLAY_NAME}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, DISPLAY_NAME)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, DISPLAY_NAME)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{DISPLAY_NAME}\n"
        section = public_section(origin_main_header())
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            "40.f, 80.f",
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, DISPLAY_NAME)
            self.assertNotIn(token, section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(DISPLAY_NAME, "Rifle")
        self.assertNotEqual(DISPLAY_NAME, "Igla")
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
                f"campaign DisplayName contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, DISPLAY_NAME.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", DISPLAY_NAME)

    def test_contract_is_display_name_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, DISPLAY_NAME),
            DISPLAY_NAME,
        )
        locked_only = f"{DISPLAY_NAME}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, DISPLAY_NAME)
        self.assertNotIn("FindMission", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("Missions", locked_only)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)
        self.assertNotIn("IsMissionUnlocked", locked_only)
        self.assertNotIn("AddObjectiveProgress", locked_only)
        self.assertNotIn("FailObjective", locked_only)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", locked_only)
        self.assertNotIn("CompleteActiveMission", locked_only)
        self.assertNotIn("FinalizeActiveMission", locked_only)
        self.assertNotIn("FailActiveMission", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn(
            "USkyguardMissionDefinition* GetActiveMission() const",
            locked_only,
        )
        self.assertNotIn("RetrySaveLastDebrief", locked_only)
        self.assertNotIn("GetLastDebrief", locked_only)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("BuildSaveGame", locked_only)
        self.assertNotIn("SaveCampaignToSlot", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)
        self.assertNotIn("GetEarnedCampaignMedals", locked_only)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("GetRouteRuntime", locked_only)
        self.assertNotIn("GetMissionRecords", locked_only)
        self.assertNotIn("CalculateMissionScore", locked_only)
        self.assertNotIn("CalculateMedalTier", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, DISPLAY_NAME)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, DISPLAY_NAME)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, DISPLAY_NAME)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, DISPLAY_NAME)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, DISPLAY_NAME)
            self.assertNotIn(token, section)
        for token in INVENTED_DISPLAY_TEXT:
            self.assertNotIn(token, DISPLAY_NAME)
            self.assertNotIn(token, locked_only)
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
        self.assertNotIn("return ", DISPLAY_NAME)
        self.assertNotIn("{", DISPLAY_NAME)
        self.assertNotIn("AddError", DISPLAY_NAME)
        self.assertNotEqual(DISPLAY_NAME, "Rifle")
        self.assertNotEqual(DISPLAY_NAME, "Igla")
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertNotIn("USkyguardCampaignSubsystem", locked_only)
        self.assertNotIn("=", DISPLAY_NAME)
        self.assertNotIn("CampaignId", DISPLAY_NAME)

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
