from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardCampaignSubsystem.h"
CLASS_NAME = "USkyguardCampaignSubsystem"
# Declaration presence only. Do not invent INDEX_NONE, a
# save-game payload, persistence result, or slot contents,
# or lock the SaveCampaignToSlot body in the .cpp.
# origin/main is split-line
# (`bool SaveCampaignToSlot(` /
# `const FString& SlotName = TEXT("Skyguard52Campaign"),` /
# `int32 UserIndex = 0) const;`);
# accept that form and other split-line wraps.
# origin/main also has
# UFUNCTION(BlueprintCallable, Category = "Campaign|Persistence")
# above the declaration; UFUNCTION alone does not satisfy.
# This lane does not lock leftover campaign-save
# empty-fail-closed, LoadCampaignFromSlot,
# DeleteCampaignSlot, RetrySaveLastDebrief, ApplySaveGame,
# GetMissionRecords, BuildSaveGame, or
# IsValidCampaignSlotName.
SAVE_CAMPAIGN = (
    "bool SaveCampaignToSlot("
    'const FString& SlotName = TEXT("Skyguard52Campaign"), '
    "int32 UserIndex = 0) const;"
)
# Leftover #56–#64 plus CampaignSubsystem production files.
# This lane only adds an isolated Python
# SaveCampaignToSlot declaration contract. Stay
# off LoadCampaignFromSlot / DeleteCampaignSlot /
# RetrySaveLastDebrief (sibling in-flight this wave),
# ApplySaveGame / GetMissionRecords (sibling drafts),
# BuildSaveGame (sibling in-flight),
# IsValidCampaignSlotName #306, leftover campaign-save
# empty-fail-closed, leftover campaign-roster lookup #111,
# LoadCampaignProgressAfterConfigure (#290), leftover
# CPG debrief #284/#195/#130/#8ccd, GetLastDebrief,
# FillResultCombatStats / FillAndFinalize / FillAndFail /
# ApplyHydraForClusters (leftover ASkyguardGunner*), leftover
# Harbor #6/#8/#9, leftover theater-kit #59, leftover
# flare/HUD #57/#61/#62, leftover drafts #56–#64, leftover
# #147 ApacheSystem, leftover #149 weapon stations,
# leftover #152 pilot commands, leftover #154 loadout /
# lock-phase, leftover settings invert-look /
# ApplySettings broadcast #134, Harbor IncomingRadar
# 40/80, leftover live copy, FSkyguardMission0NIntegrationReadiness
# (bYakRuntimeReady), and dirty D:\Skyguard52.
LOCKED = {
    "SkyguardCampaignSubsystem.h",
    "SkyguardCampaignSubsystem.cpp",
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
# broadcast, and newly drafted campaign-subsystem siblings
# stay sibling-only.
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
    "Scripts/tests/test_load_campaign_from_slot_decl_contract.py",
    "Scripts/tests/test_delete_campaign_slot_decl_contract.py",
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
# Neighbors in the same public section. Presence is not locked here.
# LoadCampaignFromSlot / DeleteCampaignSlot /
# RetrySaveLastDebrief are sibling in-flight this wave.
# ApplySaveGame / GetMissionRecords are sibling drafts.
# BuildSaveGame is sibling in-flight. IsValidCampaignSlotName
# #306 stays sibling-only. FillResultCombatStats takes leftover
# ASkyguardGunner*. Leftover CPG debrief #284/#195/#130/
# #8ccd stay sibling-only. Leftover campaign-save
# empty-fail-closed stays leftover.
UNLOCKED_NEIGHBORS = (
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
    "bool RetrySaveLastDebrief(",
    "bool AcknowledgeDebrief();",
    "const FSkyguardMissionDebrief& GetLastDebrief() const",
    "bool CanTravelToNextMission() const;",
    "FString GetNextMissionMapPackageName() const;",
    "bool TravelToNextMission(UObject* WorldContextObject);",
    "bool ApplySaveGame(const USkyguardCampaignSaveGame* SaveGame);",
    "USkyguardCampaignSaveGame* BuildSaveGame() const;",
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
)
GET_ACTIVE_MISSION_NOT_LOCKED = (
    "USkyguardMissionDefinition* GetActiveMission() const",
)
OBJECTIVES_NOT_LOCKED = (
    "bool AddObjectiveProgress(FName ObjectiveId, int32 Amount = 1);",
    "bool FailObjective(FName ObjectiveId);",
    "bool CompleteSurviveObjectiveIfIntact(FName ObjectiveId);",
)
ACTIVE_MISSION_HELPERS_NOT_LOCKED = (
    "bool CompleteActiveMission(FSkyguardMissionResult& InOutResult);",
    "bool FinalizeActiveMission(",
    "bool FailActiveMission(",
)
FILL_COMBAT_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
)
FILL_AND_NOT_LOCKED = (
    "FillAndFinalize",
    "FillAndFail",
)
ELAPSED_NOT_LOCKED = (
    "float GetActiveMissionElapsedSeconds(",
)
ACKNOWLEDGE_DEBRIEF_NOT_LOCKED = ("bool AcknowledgeDebrief();",)
DEBRIEF_NEIGHBORS_NOT_LOCKED = (
    "bool RetrySaveLastDebrief(",
    "const FSkyguardMissionDebrief& GetLastDebrief() const",
)
TRAVEL_NOT_LOCKED = (
    "bool CanTravelToNextMission() const;",
    "FString GetNextMissionMapPackageName() const;",
    "bool TravelToNextMission(UObject* WorldContextObject);",
)
RUNTIME_GETTERS_NOT_LOCKED = (
    "USkyguardObjectiveRuntime* GetObjectiveRuntime() const",
    "USkyguardRouteRuntime* GetRouteRuntime() const",
)
SAVE_GAME_SIBLINGS_NOT_LOCKED = (
    "bool ApplySaveGame(const USkyguardCampaignSaveGame* SaveGame);",
    "USkyguardCampaignSaveGame* BuildSaveGame() const;",
    "bool LoadCampaignFromSlot(",
    "bool DeleteCampaignSlot(",
    "bool RetrySaveLastDebrief(",
    "const TMap<FName, FSkyguardMissionSaveRecord>& GetMissionRecords() const",
    "static bool IsValidCampaignSlotName(const FString& SlotName);",
)
CONFIGURE_CAN_START_START_NOT_LOCKED = (
    "bool ConfigureCampaign(USkyguardCampaignDefinition* InCampaign);",
    "bool CanStartMission(FName MissionId) const;",
    "bool StartMission(FName MissionId);",
)
IS_MISSION_UNLOCKED_NOT_LOCKED = (
    "bool IsMissionUnlocked(FName MissionId) const;",
)
SCORE_MEDAL_NOT_LOCKED = (
    "static int32 CalculateMissionScore(",
    "static int32 CalculateMedalTier(",
)
# Leftover campaign-save empty-fail-closed (empty-file /
# fail-closed save behavior) stays unlocked.
LEFTOVER_CAMPAIGN_SAVE_EMPTY_NOT_LOCKED = (
    "empty-file",
    "EmptyFailClosed",
    "campaign_save_empty",
    "SkyguardCampaignSaveEmpty",
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
# .cpp SaveCampaignToSlot body / invented return values /
# invented save-game payload / persistence result / slot
# contents stay unlocked. Do not invent INDEX_NONE or lock
# the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return true",
    "return false",
    "return 0",
    "USkyguardCampaignSubsystem::SaveCampaignToSlot",
    "SkyguardCampaignSubsystem.cpp",
    "SaveGameToSlot",
    "LoadGameFromSlot",
    "DoesSaveGameExist",
    "DuplicateObject",
    "MigrateCampaignSave",
    "CurrentSaveVersion",
    "MissionRecords.Reset",
    "MissionRecords.Add",
    "ClearActiveMissionRuntime",
    "GetTransientPackage",
)
SAVE_PAYLOADS_AND_SLOT_NOT_LOCKED = (
    "DuplicateObject",
    "MigrateCampaignSave",
    "CurrentSaveVersion",
    "BestScore",
    "BestMedalTier",
    "BestCompletionTimeSeconds",
    "SaveGameToSlot",
    "LoadGameFromSlot",
    "DoesSaveGameExist",
    "LastDebrief.bProgressSaved",
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


class SaveCampaignToSlotDeclContractTests(unittest.TestCase):
    def test_campaign_subsystem_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, SAVE_CAMPAIGN), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedCampaign "
                ": public UGameInstanceSubsystem\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API UOtherCampaignSubsystem "
            ": public UGameInstanceSubsystem\n"
            "{\n"
            "public:\n"
            f"\t{SAVE_CAMPAIGN}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UGameInstanceSubsystem\n"
            "{\n"
            "private:\n"
            f"\t{SAVE_CAMPAIGN}\n"
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
            ": public UGameInstanceSubsystem\n"
            "{\n"
            "public:\n"
            "\tbool ApplySaveGame("
            "const USkyguardCampaignSaveGame* SaveGame);\n"
            "private:\n"
            f"\t{SAVE_CAMPAIGN}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, SAVE_CAMPAIGN)
        self.assertIn("SaveCampaignToSlot", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, SAVE_CAMPAIGN))

    def test_missing_save_campaign_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tbool ConfigureCampaign("
            "USkyguardCampaignDefinition* InCampaign);\n"
            "\tbool CanStartMission(FName MissionId) const;\n"
            "\tbool StartMission(FName MissionId);\n"
            "\tbool AddObjectiveProgress("
            "FName ObjectiveId, int32 Amount = 1);\n"
            "\tbool FailObjective(FName ObjectiveId);\n"
            "\tbool CompleteSurviveObjectiveIfIntact("
            "FName ObjectiveId);\n"
            "\tbool CompleteActiveMission("
            "FSkyguardMissionResult& InOutResult);\n"
            "\tbool FinalizeActiveMission(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
            "\tbool FailActiveMission(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
            "\tvoid FillResultCombatStats(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            "\t\tconst ASkyguardGunner* Gunner,\n"
            "\t\tconst UObject* WorldContextObject) const;\n"
            "\tfloat GetActiveMissionElapsedSeconds(\n"
            "\t\tconst UObject* WorldContextObject) const;\n"
            "\tbool RetrySaveLastDebrief(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
            "\tbool AcknowledgeDebrief();\n"
            "\tconst FSkyguardMissionDebrief& GetLastDebrief() const;\n"
            "\tbool CanTravelToNextMission() const;\n"
            "\tFString GetNextMissionMapPackageName() const;\n"
            "\tbool TravelToNextMission(UObject* WorldContextObject);\n"
            "\tbool ApplySaveGame("
            "const USkyguardCampaignSaveGame* SaveGame);\n"
            "\tUSkyguardCampaignSaveGame* BuildSaveGame() const;\n"
            "\tbool LoadCampaignFromSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
            "\tbool DeleteCampaignSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0) const;\n"
            "\tstatic bool IsValidCampaignSlotName("
            "const FString& SlotName);\n"
            "\tbool IsMissionUnlocked(FName MissionId) const;\n"
            "\tint32 GetEarnedCampaignMedals() const;\n"
            "\tUSkyguardMissionDefinition* GetActiveMission() const;\n"
            "\tUSkyguardObjectiveRuntime* GetObjectiveRuntime() const;\n"
            "\tUSkyguardRouteRuntime* GetRouteRuntime() const;\n"
            "\tconst TMap<FName, FSkyguardMissionSaveRecord>& "
            "GetMissionRecords() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, SAVE_CAMPAIGN)
        self.assertIn("SaveCampaignToSlot", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintCallable, Category = "Campaign|Persistence")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, SAVE_CAMPAIGN)
        self.assertIn("SaveCampaignToSlot", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_has_persistence_ufunction(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(
            'UFUNCTION(BlueprintCallable, Category = "Campaign|Persistence")',
            section,
        )
        self.assertTrue(has_declaration(section, SAVE_CAMPAIGN), section)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tbool ApplySaveGame("
            "const USkyguardCampaignSaveGame* SaveGame);\n"
            "\tUSkyguardCampaignSaveGame* BuildSaveGame() const;\n"
            "\tbool LoadCampaignFromSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
            "\tbool DeleteCampaignSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0) const;\n"
            "\tbool RetrySaveLastDebrief(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
            "\tstatic bool IsValidCampaignSlotName("
            "const FString& SlotName);\n"
            "\tconst TMap<FName, FSkyguardMissionSaveRecord>& "
            "GetMissionRecords() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, SAVE_CAMPAIGN)
        self.assertIn("SaveCampaignToSlot", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_defaults = (
            "\tbool SaveCampaignToSlot("
            "const FString& SlotName, int32 UserIndex) const;\n"
        )
        missing_user_index = (
            "\tbool SaveCampaignToSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign")) '
            "const;\n"
        )
        no_default_values = (
            "\tbool SaveCampaignToSlot(\n"
            "\t\tconst FString& SlotName,\n"
            "\t\tint32 UserIndex) const;\n"
        )
        wrong_slot = (
            "\tbool SaveCampaignToSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Campaign"),\n'
            "\t\tint32 UserIndex = 0) const;\n"
        )
        index_none = (
            "\tbool SaveCampaignToSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = INDEX_NONE) const;\n"
        )
        missing_const = (
            "\tbool SaveCampaignToSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
        )
        void_return = (
            "\tvoid SaveCampaignToSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0) const;\n"
        )
        for region in (
            missing_defaults,
            missing_user_index,
            no_default_values,
            wrong_slot,
            index_none,
            missing_const,
            void_return,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, SAVE_CAMPAIGN)
            self.assertIn("SaveCampaignToSlot", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_load_or_delete_slot_does_not_satisfy(self) -> None:
        load_only = (
            "\tbool LoadCampaignFromSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
        )
        delete_only = (
            "\tbool DeleteCampaignSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0) const;\n"
        )
        for region in (load_only, delete_only):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, SAVE_CAMPAIGN)
            self.assertIn("SaveCampaignToSlot", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, SAVE_CAMPAIGN))

    def test_retry_save_last_debrief_does_not_satisfy(self) -> None:
        retry_only = (
            "\tbool RetrySaveLastDebrief(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(retry_only, SAVE_CAMPAIGN)
        self.assertIn("SaveCampaignToSlot", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(retry_only, SAVE_CAMPAIGN))

    def test_save_campaign_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, SAVE_CAMPAIGN),
            SAVE_CAMPAIGN,
        )
        self.assertTrue(has_declaration(section, SAVE_CAMPAIGN))
        self.assertEqual(declaration_count(section, SAVE_CAMPAIGN), 1)
        self.assertTrue(SAVE_CAMPAIGN.startswith("bool "), SAVE_CAMPAIGN)
        self.assertTrue(SAVE_CAMPAIGN.endswith(") const;"), SAVE_CAMPAIGN)
        self.assertIn(
            'const FString& SlotName = TEXT("Skyguard52Campaign")',
            SAVE_CAMPAIGN,
        )
        self.assertIn("int32 UserIndex = 0", SAVE_CAMPAIGN)
        self.assertNotIn("INDEX_NONE", SAVE_CAMPAIGN)
        self.assertNotIn("{", SAVE_CAMPAIGN)
        self.assertNotIn("}", SAVE_CAMPAIGN)
        self.assertNotIn("return ", SAVE_CAMPAIGN)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_name = (
            "public:\n"
            "\tbool SaveCampaignToSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_type = (
            "public:\n"
            "\tbool\n"
            "\tSaveCampaignToSlot("
            'const FString& SlotName = TEXT("Skyguard52Campaign"), '
            "int32 UserIndex = 0) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_args = (
            "public:\n"
            "\tbool SaveCampaignToSlot(const FString&\n"
            '\t\tSlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32\n"
            "\t\tUserIndex = 0) const;\n"
            "};\n"
        )
        wrap_defaults = (
            "public:\n"
            "\tbool SaveCampaignToSlot(\n"
            "\t\tconst FString& SlotName =\n"
            '\t\tTEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex =\n"
            "\t\t0) const;\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tbool SaveCampaignToSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0)\n"
            "\t\tconst;\n"
            "};\n"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_name}"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_type}"
        )
        header_wrap_args = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_args}"
        )
        header_wrap_defaults = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_defaults}"
        )
        header_wrap_const = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_const}"
        )
        for header in (
            header_wrap_name,
            header_wrap_type,
            header_wrap_args,
            header_wrap_defaults,
            header_wrap_const,
        ):
            section = public_section(header)
            self.assertTrue(has_declaration(section, SAVE_CAMPAIGN), section)
            self.assertEqual(
                require_declaration(section, SAVE_CAMPAIGN),
                SAVE_CAMPAIGN,
            )
            self.assertEqual(declaration_count(section, SAVE_CAMPAIGN), 1)
        one_line = f"{{\npublic:\n\t{SAVE_CAMPAIGN}\n}}\n"
        self.assertTrue(has_declaration(one_line, SAVE_CAMPAIGN))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, SAVE_CAMPAIGN), section)
        self.assertEqual(
            require_declaration(section, SAVE_CAMPAIGN),
            SAVE_CAMPAIGN,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", SAVE_CAMPAIGN)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", SAVE_CAMPAIGN)
        self.assertNotIn("UserIndex = INDEX_NONE", SAVE_CAMPAIGN)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_save_payload_or_slot_contents(
        self,
    ) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        self.assertNotIn("return ", SAVE_CAMPAIGN)
        self.assertNotIn("return true", SAVE_CAMPAIGN)
        self.assertNotIn("return false", SAVE_CAMPAIGN)
        for token in SAVE_PAYLOADS_AND_SLOT_NOT_LOCKED:
            self.assertNotIn(token, SAVE_CAMPAIGN)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("SaveGameToSlot", SAVE_CAMPAIGN)
        self.assertNotIn("LoadGameFromSlot", SAVE_CAMPAIGN)
        self.assertNotIn("DoesSaveGameExist", SAVE_CAMPAIGN)
        self.assertNotIn("DuplicateObject", SAVE_CAMPAIGN)
        self.assertNotIn("MigrateCampaignSave", SAVE_CAMPAIGN)
        self.assertNotIn("CurrentSaveVersion", SAVE_CAMPAIGN)
        self.assertNotIn("BestScore", SAVE_CAMPAIGN)
        self.assertNotIn("BestMedalTier", SAVE_CAMPAIGN)
        self.assertNotIn("LastDebrief.bProgressSaved", SAVE_CAMPAIGN)

    def test_contract_does_not_lock_save_campaign_cpp_body(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        self.assertNotIn("{", SAVE_CAMPAIGN)
        self.assertNotIn("}", SAVE_CAMPAIGN)
        self.assertNotIn("return ", SAVE_CAMPAIGN)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::SaveCampaignToSlot",
            SAVE_CAMPAIGN,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", SAVE_CAMPAIGN)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", locked_only)
        self.assertNotIn("SaveGameToSlot", SAVE_CAMPAIGN)
        self.assertNotIn("LoadGameFromSlot", SAVE_CAMPAIGN)
        self.assertNotIn("DoesSaveGameExist", SAVE_CAMPAIGN)
        self.assertNotIn("ClearActiveMissionRuntime", SAVE_CAMPAIGN)

    def test_contract_does_not_relock_leftover_campaign_save_empty(
        self,
    ) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CAMPAIGN_SAVE_EMPTY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVE_CAMPAIGN)
            self.assertNotIn(token, section)
        self.assertNotIn("empty-file", locked_only)
        self.assertNotIn("EmptyFailClosed", SAVE_CAMPAIGN)
        self.assertNotIn("campaign_save_empty", locked_only)
        self.assertNotIn("SkyguardCampaignSaveEmpty", SAVE_CAMPAIGN)

    def test_contract_does_not_relock_get_active_mission(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in GET_ACTIVE_MISSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn(
            "USkyguardMissionDefinition* GetActiveMission() const",
            SAVE_CAMPAIGN,
        )
        self.assertNotIn(
            "USkyguardMissionDefinition* GetActiveMission() const",
            locked_only,
        )

    def test_contract_does_not_relock_configure_can_start_or_start(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in CONFIGURE_CAN_START_START_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn("ConfigureCampaign", SAVE_CAMPAIGN)
        self.assertNotIn("CanStartMission", SAVE_CAMPAIGN)
        self.assertNotIn("StartMission", SAVE_CAMPAIGN)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)

    def test_contract_does_not_relock_is_mission_unlocked(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in IS_MISSION_UNLOCKED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn("IsMissionUnlocked", SAVE_CAMPAIGN)
        self.assertNotIn("IsMissionUnlocked", locked_only)

    def test_contract_does_not_relock_objectives(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in OBJECTIVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn("AddObjectiveProgress", SAVE_CAMPAIGN)
        self.assertNotIn("FailObjective", SAVE_CAMPAIGN)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", SAVE_CAMPAIGN)
        self.assertNotIn("AddObjectiveProgress", locked_only)
        self.assertNotIn("FailObjective", locked_only)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", locked_only)

    def test_contract_does_not_relock_active_mission_helpers(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in ACTIVE_MISSION_HELPERS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn("CompleteActiveMission", SAVE_CAMPAIGN)
        self.assertNotIn("FinalizeActiveMission", SAVE_CAMPAIGN)
        self.assertNotIn("FailActiveMission", SAVE_CAMPAIGN)
        self.assertNotIn("CompleteActiveMission", locked_only)
        self.assertNotIn("FinalizeActiveMission", locked_only)
        self.assertNotIn("FailActiveMission", locked_only)

    def test_contract_does_not_relock_fill_result_combat_stats(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in FILL_COMBAT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn("FillResultCombatStats", SAVE_CAMPAIGN)
        self.assertNotIn("ASkyguardGunner", SAVE_CAMPAIGN)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)

    def test_contract_does_not_relock_fill_and_finalize_or_fail(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        section = public_section(origin_main_header())
        for token in FILL_AND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVE_CAMPAIGN)
            self.assertNotIn(token, section)
        self.assertNotIn("FillAndFinalize", SAVE_CAMPAIGN)
        self.assertNotIn("FillAndFail", SAVE_CAMPAIGN)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)

    def test_contract_does_not_relock_elapsed_seconds(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in ELAPSED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn("GetActiveMissionElapsedSeconds", SAVE_CAMPAIGN)
        self.assertNotIn("GetActiveMissionElapsedSeconds", locked_only)

    def test_contract_does_not_relock_acknowledge_debrief(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in ACKNOWLEDGE_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn("AcknowledgeDebrief", SAVE_CAMPAIGN)
        self.assertNotIn("AcknowledgeDebrief", locked_only)

    def test_contract_does_not_relock_debrief_neighbors(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in DEBRIEF_NEIGHBORS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn("RetrySaveLastDebrief", SAVE_CAMPAIGN)
        self.assertNotIn("GetLastDebrief", SAVE_CAMPAIGN)
        self.assertNotIn("RetrySaveLastDebrief", locked_only)
        self.assertNotIn("GetLastDebrief", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVE_CAMPAIGN)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_travel_helpers(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in TRAVEL_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn("CanTravelToNextMission", SAVE_CAMPAIGN)
        self.assertNotIn("GetNextMissionMapPackageName", SAVE_CAMPAIGN)
        self.assertNotIn("TravelToNextMission", SAVE_CAMPAIGN)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)

    def test_contract_does_not_relock_runtime_getters(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in RUNTIME_GETTERS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn("GetObjectiveRuntime", SAVE_CAMPAIGN)
        self.assertNotIn("GetRouteRuntime", SAVE_CAMPAIGN)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("GetRouteRuntime", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVE_CAMPAIGN)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_save_game_siblings(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in SAVE_GAME_SIBLINGS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn("ApplySaveGame", SAVE_CAMPAIGN)
        self.assertNotIn("BuildSaveGame", SAVE_CAMPAIGN)
        self.assertNotIn("LoadCampaignFromSlot", SAVE_CAMPAIGN)
        self.assertNotIn("DeleteCampaignSlot", SAVE_CAMPAIGN)
        self.assertNotIn("RetrySaveLastDebrief", SAVE_CAMPAIGN)
        self.assertNotIn("GetMissionRecords", SAVE_CAMPAIGN)
        self.assertNotIn("IsValidCampaignSlotName", SAVE_CAMPAIGN)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("BuildSaveGame", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("RetrySaveLastDebrief", locked_only)
        self.assertNotIn("GetMissionRecords", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)

    def test_contract_does_not_relock_score_or_medal_helpers(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in SCORE_MEDAL_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn("CalculateMissionScore", SAVE_CAMPAIGN)
        self.assertNotIn("CalculateMedalTier", SAVE_CAMPAIGN)
        self.assertNotIn("CalculateMissionScore", locked_only)
        self.assertNotIn("CalculateMedalTier", locked_only)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVE_CAMPAIGN)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        self.assertEqual(
            require_declaration(locked_only, SAVE_CAMPAIGN),
            SAVE_CAMPAIGN,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)
        self.assertNotIn("IsMissionUnlocked", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("GetEarnedCampaignMedals", locked_only)
        self.assertNotIn("GetLastDebrief", locked_only)
        self.assertNotIn("RetrySaveLastDebrief", locked_only)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("GetRouteRuntime", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("GetActiveMissionElapsedSeconds", locked_only)
        self.assertNotIn("CompleteActiveMission", locked_only)
        self.assertNotIn("FinalizeActiveMission", locked_only)
        self.assertNotIn("FailActiveMission", locked_only)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("BuildSaveGame", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("GetMissionRecords", locked_only)
        self.assertNotIn(
            "USkyguardMissionDefinition* GetActiveMission() const",
            locked_only,
        )
        self.assertNotIn("LoadCampaignProgressAfterConfigure", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("TObjectPtr<USkyguardCampaignDefinition>", section)
        self.assertNotIn("TObjectPtr<USkyguardMissionDefinition>", section)
        self.assertNotIn("MissionStartWorldTimeSeconds", section)
        self.assertNotIn("void BuildSuccessDebrief(", section)
        self.assertNotIn("void BuildFailureDebrief(", section)
        self.assertNotIn("void ClearActiveMissionRuntime();", section)
        self.assertEqual(
            require_declaration(section, SAVE_CAMPAIGN),
            SAVE_CAMPAIGN,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::SaveCampaignToSlot",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SAVE_CAMPAIGN)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::SaveCampaignToSlot",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", SAVE_CAMPAIGN)
        self.assertNotIn("}", SAVE_CAMPAIGN)
        self.assertNotIn("return true", SAVE_CAMPAIGN)
        self.assertNotIn("return false", SAVE_CAMPAIGN)
        self.assertNotIn("SaveGameToSlot", SAVE_CAMPAIGN)
        self.assertNotIn("DuplicateObject", SAVE_CAMPAIGN)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, SAVE_CAMPAIGN)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, SAVE_CAMPAIGN)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{SAVE_CAMPAIGN}\n"
        section = public_section(origin_main_header())
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            "40.f, 80.f",
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVE_CAMPAIGN)
            self.assertNotIn(token, section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(SAVE_CAMPAIGN, "Rifle")
        self.assertNotEqual(SAVE_CAMPAIGN, "Igla")
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
                f"campaign SaveCampaignToSlot contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, SAVE_CAMPAIGN.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", SAVE_CAMPAIGN)

    def test_contract_is_save_campaign_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, SAVE_CAMPAIGN),
            SAVE_CAMPAIGN,
        )
        locked_only = f"{SAVE_CAMPAIGN}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SAVE_CAMPAIGN)
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
        self.assertNotIn("GetActiveMissionElapsedSeconds", locked_only)
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
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)
        self.assertNotIn("GetMissionRecords", locked_only)
        self.assertNotIn("GetEarnedCampaignMedals", locked_only)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("GetRouteRuntime", locked_only)
        self.assertNotIn("CalculateMissionScore", locked_only)
        self.assertNotIn("CalculateMedalTier", locked_only)
        self.assertNotIn("LastDebrief.bProgressSaved", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVE_CAMPAIGN)
        for token in LEFTOVER_CAMPAIGN_SAVE_EMPTY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVE_CAMPAIGN)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVE_CAMPAIGN)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SAVE_CAMPAIGN)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, SAVE_CAMPAIGN)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SAVE_CAMPAIGN)
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
        self.assertNotIn("return ", SAVE_CAMPAIGN)
        self.assertNotIn("{", SAVE_CAMPAIGN)
        self.assertNotIn("return true", SAVE_CAMPAIGN)
        self.assertNotEqual(SAVE_CAMPAIGN, "Rifle")
        self.assertNotEqual(SAVE_CAMPAIGN, "Igla")
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertIn(
            'const FString& SlotName = TEXT("Skyguard52Campaign")',
            SAVE_CAMPAIGN,
        )
        self.assertIn("int32 UserIndex = 0", SAVE_CAMPAIGN)
        self.assertTrue(SAVE_CAMPAIGN.endswith(") const;"), SAVE_CAMPAIGN)

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
