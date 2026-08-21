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
# combat-counter payload, or lock the FillResultCombatStats
# body in the .cpp. origin/main is split-line
# (`void FillResultCombatStats(` /
# `FSkyguardMissionResult& InOutResult,` /
# `const ASkyguardGunner* Gunner,` /
# `const UObject* WorldContextObject) const;`);
# accept that form and other split-line wraps.
# Nearby UFUNCTION Category Campaign|Sortie and WorldContext
# meta must be present. This is the campaign-subsystem
# UFUNCTION. Stay off leftover Gunner combat-fill helpers
# and leftover FillAndFinalize / FillAndFail /
# LoadCampaignProgressAfterConfigure in
# SkyguardMissionDirectorCampaignHelpers. Stay off leftover
# Gunner class contracts. Do not open or lock
# SkyguardGunner.h. The ASkyguardGunner* parameter type
# appears on origin/main and is part of this locked
# declaration.
FILL_RESULT = (
    "void FillResultCombatStats("
    "FSkyguardMissionResult& InOutResult, "
    "const ASkyguardGunner* Gunner, "
    "const UObject* WorldContextObject) const;"
)
UFUNCTION_CATEGORY = 'Category = "Campaign|Sortie"'
UFUNCTION_WORLD_CONTEXT = 'meta = (WorldContext = "WorldContextObject")'
UFUNCTION_CALLABLE = "BlueprintCallable"
# Leftover #56–#64 plus CampaignSubsystem production files.
# This lane only adds an isolated Python FillResultCombatStats
# declaration contract. Stay off leftover Gunner combat-fill
# helpers, leftover FillAndFinalize / FillAndFail /
# LoadCampaignProgressAfterConfigure, leftover Harbor #6/#8/#9,
# leftover theater-kit #59, leftover drafts #56–#64, leftover
# #107–#565, leftover Apache MaxIntegrity / CurrentIntegrity,
# leftover Apache mount getters #851b / own-ship #96c5 / chin
# muzzle #4e39, leftover settings-apply-broadcast #1268,
# leftover patrol-ship empty fail-closed #5382, leftover
# RadarNode, leftover live-mount-named boss methods, leftover
# campaign-save empty-fail-closed, leftover campaign-roster
# #111, leftover campaign-load-progress #adda, Harbor
# IncomingRadar 40/80, leftover live copy,
# FSkyguardMission0NIntegrationReadiness, and dirty
# D:\Skyguard52.
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
# Isolated-test drafts stay off this lane. Sibling isolated
# campaign-subsystem decl contracts, leftover campaign-save
# empty-fail-closed, leftover campaign-roster #111, leftover
# campaign-load-progress #adda, leftover CPG debrief copy /
# snapshot / fail-closed, leftover objective-runtime
# fail-closed, leftover route-runtime fail-closed, leftover
# theater-kit / Harbor / flare/HUD, leftover FillAndFinalize /
# FillAndFail, leftover settings invert-look / ApplySettings
# broadcast, and newly drafted campaign-subsystem siblings
# stay sibling-only (must remain absent from this PR diff).
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
    "Scripts/tests/test_configure_campaign_decl_contract.py",
    "Scripts/tests/test_can_start_mission_decl_contract.py",
    "Scripts/tests/test_start_mission_decl_contract.py",
    "Scripts/tests/test_add_objective_progress_decl_contract.py",
    "Scripts/tests/test_fail_objective_decl_contract.py",
    "Scripts/tests/test_complete_survive_objective_if_intact_decl_contract.py",
    "Scripts/tests/test_complete_active_mission_decl_contract.py",
    "Scripts/tests/test_finalize_active_mission_decl_contract.py",
    "Scripts/tests/test_fail_active_mission_decl_contract.py",
    "Scripts/tests/test_get_active_mission_elapsed_seconds_decl_contract.py",
    "Scripts/tests/test_retry_save_last_debrief_decl_contract.py",
    "Scripts/tests/test_acknowledge_debrief_decl_contract.py",
    "Scripts/tests/test_get_last_debrief_decl_contract.py",
    "Scripts/tests/test_can_travel_to_next_mission_decl_contract.py",
    "Scripts/tests/test_get_next_mission_map_package_name_decl_contract.py",
    "Scripts/tests/test_travel_to_next_mission_decl_contract.py",
    "Scripts/tests/test_apply_save_game_decl_contract.py",
    "Scripts/tests/test_build_save_game_decl_contract.py",
    "Scripts/tests/test_save_campaign_to_slot_decl_contract.py",
    "Scripts/tests/test_load_campaign_from_slot_decl_contract.py",
    "Scripts/tests/test_delete_campaign_slot_decl_contract.py",
    "Scripts/tests/test_is_valid_campaign_slot_name_decl_contract.py",
    "Scripts/tests/test_is_mission_unlocked_decl_contract.py",
    "Scripts/tests/test_get_earned_campaign_medals_decl_contract.py",
    "Scripts/tests/test_get_active_mission_decl_contract.py",
    "Scripts/tests/test_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_get_route_runtime_decl_contract.py",
    "Scripts/tests/test_get_mission_records_decl_contract.py",
    "Scripts/tests/test_calculate_mission_score_decl_contract.py",
    "Scripts/tests/test_calculate_medal_tier_decl_contract.py",
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
# here. Sibling campaign-subsystem methods stay sibling-only.
# Leftover FillAndFinalize / FillAndFail /
# LoadCampaignProgressAfterConfigure stay unlocked.
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
    "float GetActiveMissionElapsedSeconds(",
    "bool RetrySaveLastDebrief(",
    "bool AcknowledgeDebrief();",
    "const FSkyguardMissionDebrief& GetLastDebrief() const",
    "bool CanTravelToNextMission() const;",
    "FString GetNextMissionMapPackageName() const;",
    "bool TravelToNextMission(UObject* WorldContextObject);",
    "bool ApplySaveGame(const USkyguardCampaignSaveGame* SaveGame);",
    "USkyguardCampaignSaveGame* BuildSaveGame() const;",
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
    "const TMap<FName, FSkyguardMissionSaveRecord>& GetMissionRecords() const",
)
SAVE_GAME_NOT_LOCKED = (
    "bool ApplySaveGame(const USkyguardCampaignSaveGame* SaveGame);",
    "USkyguardCampaignSaveGame* BuildSaveGame() const;",
    "bool SaveCampaignToSlot(",
    "bool LoadCampaignFromSlot(",
    "bool DeleteCampaignSlot(",
    "static bool IsValidCampaignSlotName(const FString& SlotName);",
    "int32 GetEarnedCampaignMedals() const;",
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
# Leftover Gunner combat-fill helpers and leftover director
# helpers stay unlocked. Do not open SkyguardGunner.h or
# SkyguardMissionDirectorCampaignHelpers.
LEFTOVER_DIRECTOR_HELPERS_NOT_LOCKED = (
    "FillAndFinalize",
    "FillAndFail",
    "LoadCampaignProgressAfterConfigure",
    "SkyguardMissionDirectorCampaignHelpers",
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
# cluster apply / leftover Apache integrity stay unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "LoadCampaignProgressAfterConfigure",
    "SetInvertVerticalLook",
    "OnSettingsApplied",
    "MaxIntegrity",
    "CurrentIntegrity",
)
# Invented combat-stat payload / cpp body stay unlocked.
# Do not invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return 0.f",
    "return 0.0f",
    "GetTimeSeconds",
    "MissionStartWorldTimeSeconds",
    "ShotsFired =",
    "HitsLanded =",
    "USkyguardCampaignSubsystem::FillResultCombatStats",
    "SkyguardCampaignSubsystem.cpp",
    "FillAndFinalize",
    "FillAndFail",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bY" "akRuntimeReady",
    "ASkyguardI" "glaMissile",
)
BANNED = ("i" "gla", "y" "ak", "r" "ifle")
HARBOR_INCOMING = "IncomingRadar"
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
# Harbor 40/80 fail-closed tokens live in THIS file and the
# locked declaration only. Do not scan Apache public section
# for those tokens. IncomingRadar clock names may be scanned
# in the CampaignSubsystem public section and must be absent.
# Pathfinder MinHeightFromOriginCm = -80.f is the wrong
# header. LastFlight MinimumCivilianSeparationMeters = 550.f
# and LifelineHunter MinimumWeaponSeparationMeters = 450.f
# are Harbor-adjacent, not Harbor 40/80.
HARBOR_TUNING = ("40.f", "80.f")
PATHFINDER_NOT_HARBOR = "MinHeightFromOriginCm = -80.f"
LAST_FLIGHT_NOT_HARBOR = "MinimumCivilianSeparationMeters = 550.f"
LIFELINE_HUNTER_NOT_HARBOR = "MinimumWeaponSeparationMeters = 450.f"
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


class FillResultCombatStatsDeclContractTests(unittest.TestCase):
    def test_campaign_subsystem_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, FILL_RESULT), section)

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
            f"\t{FILL_RESULT}\n"
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
            f"\t{FILL_RESULT}\n"
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
            "\tUSkyguardMissionDefinition* GetActiveMission() const;\n"
            "private:\n"
            f"\t{FILL_RESULT}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, FILL_RESULT)
        self.assertIn("FillResultCombatStats", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, FILL_RESULT))

    def test_missing_fill_result_declaration_fails_closed(self) -> None:
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
            "\tfloat GetActiveMissionElapsedSeconds(\n"
            "\t\tconst UObject* WorldContextObject) const;\n"
            "\tbool AcknowledgeDebrief();\n"
            "\tconst FSkyguardMissionDebrief& GetLastDebrief() const;\n"
            "\tbool CanTravelToNextMission() const;\n"
            "\tFString GetNextMissionMapPackageName() const;\n"
            "\tbool TravelToNextMission(UObject* WorldContextObject);\n"
            "\tbool IsMissionUnlocked(FName MissionId) const;\n"
            "\tstatic bool IsValidCampaignSlotName("
            "const FString& SlotName);\n"
            "\tint32 GetEarnedCampaignMedals() const;\n"
            "\tUSkyguardMissionDefinition* GetActiveMission() const;\n"
            "\tUSkyguardObjectiveRuntime* GetObjectiveRuntime() const;\n"
            "\tUSkyguardRouteRuntime* GetRouteRuntime() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, FILL_RESULT)
        self.assertIn("FillResultCombatStats", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            f'\tUFUNCTION({UFUNCTION_CALLABLE}, {UFUNCTION_CATEGORY},\n'
            f"\t\t{UFUNCTION_WORLD_CONTEXT})\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, FILL_RESULT)
        self.assertIn("FillResultCombatStats", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_CATEGORY, section)
        self.assertIn(UFUNCTION_WORLD_CONTEXT, section)
        self.assertIn(UFUNCTION_CALLABLE, section)
        self.assertTrue(has_declaration(section, FILL_RESULT), section)
        index = section.find("void FillResultCombatStats")
        self.assertGreaterEqual(index, 0, section)
        nearby = section[max(0, index - 220) : index]
        self.assertIn(UFUNCTION_CATEGORY, nearby)
        self.assertIn(UFUNCTION_WORLD_CONTEXT, nearby)
        self.assertIn(UFUNCTION_CALLABLE, nearby)
        self.assertNotIn("UFUNCTION", FILL_RESULT)
        self.assertNotIn("Category", FILL_RESULT)
        self.assertNotIn("BlueprintPure", FILL_RESULT)
        self.assertNotIn("BlueprintCallable", FILL_RESULT)
        self.assertIn("WorldContextObject", FILL_RESULT)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
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
            "\tfloat GetActiveMissionElapsedSeconds(\n"
            "\t\tconst UObject* WorldContextObject) const;\n"
            "\tbool RetrySaveLastDebrief(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, FILL_RESULT)
        self.assertIn("FillResultCombatStats", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_director_helpers_do_not_satisfy(self) -> None:
        leftover_helpers = (
            "\tvoid FillAndFinalize("
            "FSkyguardMissionResult& InOutResult);\n"
            "\tvoid FillAndFail("
            "FSkyguardMissionResult& InOutResult);\n"
            "\tvoid LoadCampaignProgressAfterConfigure();\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(leftover_helpers, FILL_RESULT)
        self.assertIn("FillResultCombatStats", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_gunner = (
            "\tvoid FillResultCombatStats("
            "FSkyguardMissionResult& InOutResult, "
            "const UObject* WorldContextObject) const;\n"
        )
        missing_world = (
            "\tvoid FillResultCombatStats("
            "FSkyguardMissionResult& InOutResult, "
            "const ASkyguardGunner* Gunner) const;\n"
        )
        missing_result = (
            "\tvoid FillResultCombatStats("
            "const ASkyguardGunner* Gunner, "
            "const UObject* WorldContextObject) const;\n"
        )
        non_const = (
            "\tvoid FillResultCombatStats("
            "FSkyguardMissionResult& InOutResult, "
            "const ASkyguardGunner* Gunner, "
            "const UObject* WorldContextObject);\n"
        )
        wrong_return = (
            "\tbool FillResultCombatStats("
            "FSkyguardMissionResult& InOutResult, "
            "const ASkyguardGunner* Gunner, "
            "const UObject* WorldContextObject) const;\n"
        )
        mutable_gunner = (
            "\tvoid FillResultCombatStats("
            "FSkyguardMissionResult& InOutResult, "
            "ASkyguardGunner* Gunner, "
            "const UObject* WorldContextObject) const;\n"
        )
        mutable_world = (
            "\tvoid FillResultCombatStats("
            "FSkyguardMissionResult& InOutResult, "
            "const ASkyguardGunner* Gunner, "
            "UObject* WorldContextObject) const;\n"
        )
        missing_ref = (
            "\tvoid FillResultCombatStats("
            "FSkyguardMissionResult InOutResult, "
            "const ASkyguardGunner* Gunner, "
            "const UObject* WorldContextObject) const;\n"
        )
        for region in (
            missing_gunner,
            missing_world,
            missing_result,
            non_const,
            wrong_return,
            mutable_gunner,
            mutable_world,
            missing_ref,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, FILL_RESULT)
            self.assertIn("FillResultCombatStats", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_fill_result_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, FILL_RESULT),
            FILL_RESULT,
        )
        self.assertTrue(has_declaration(section, FILL_RESULT))
        self.assertEqual(declaration_count(section, FILL_RESULT), 1)
        self.assertTrue(FILL_RESULT.endswith("const;"), FILL_RESULT)
        self.assertTrue(FILL_RESULT.startswith("void "), FILL_RESULT)
        self.assertIn("FSkyguardMissionResult& InOutResult", FILL_RESULT)
        self.assertIn("const ASkyguardGunner* Gunner", FILL_RESULT)
        self.assertIn("const UObject* WorldContextObject", FILL_RESULT)
        self.assertNotIn("INDEX_NONE", FILL_RESULT)
        self.assertNotIn("{", FILL_RESULT)
        self.assertNotIn("}", FILL_RESULT)
        self.assertNotIn("return ", FILL_RESULT)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_name = (
            "public:\n"
            "\tvoid FillResultCombatStats(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            "\t\tconst ASkyguardGunner* Gunner,\n"
            "\t\tconst UObject* WorldContextObject) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_type = (
            "public:\n"
            "\tvoid\n"
            "\tFillResultCombatStats("
            "FSkyguardMissionResult& InOutResult, "
            "const ASkyguardGunner* Gunner, "
            "const UObject* WorldContextObject) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_args = (
            "public:\n"
            "\tvoid FillResultCombatStats(FSkyguardMissionResult&\n"
            "\t\tInOutResult,\n"
            "\t\tconst ASkyguardGunner*\n"
            "\t\tGunner,\n"
            "\t\tconst UObject*\n"
            "\t\tWorldContextObject) const;\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tvoid FillResultCombatStats(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            "\t\tconst ASkyguardGunner* Gunner,\n"
            "\t\tconst UObject* WorldContextObject)\n"
            "\tconst;\n"
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
        header_wrap_const = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_const}"
        )
        for header in (
            header_wrap_name,
            header_wrap_type,
            header_wrap_args,
            header_wrap_const,
        ):
            section = public_section(header)
            self.assertTrue(has_declaration(section, FILL_RESULT), section)
            self.assertEqual(
                require_declaration(section, FILL_RESULT),
                FILL_RESULT,
            )
            self.assertEqual(declaration_count(section, FILL_RESULT), 1)
        one_line = f"{{\npublic:\n\t{FILL_RESULT}\n}}\n"
        self.assertTrue(has_declaration(one_line, FILL_RESULT))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, FILL_RESULT), section)
        self.assertEqual(
            require_declaration(section, FILL_RESULT),
            FILL_RESULT,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", FILL_RESULT)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", FILL_RESULT)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_combat_stat_payload(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        self.assertNotIn("return ", FILL_RESULT)
        self.assertNotIn("ShotsFired =", FILL_RESULT)
        self.assertNotIn("HitsLanded =", FILL_RESULT)
        self.assertNotIn("GetTimeSeconds", FILL_RESULT)
        self.assertNotIn("MissionStartWorldTimeSeconds", FILL_RESULT)
        self.assertNotIn("ShotsFired =", locked_only)
        self.assertNotIn("GetTimeSeconds", locked_only)
        self.assertNotIn("MissionStartWorldTimeSeconds", locked_only)
        section = public_section(origin_main_header())
        self.assertNotIn("ShotsFired =", section)
        self.assertNotIn("GetTimeSeconds", section)
        self.assertNotIn("MissionStartWorldTimeSeconds", section)

    def test_contract_does_not_lock_fill_result_cpp_body(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        self.assertNotIn("{", FILL_RESULT)
        self.assertNotIn("}", FILL_RESULT)
        self.assertNotIn("return ", FILL_RESULT)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::FillResultCombatStats",
            FILL_RESULT,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", FILL_RESULT)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", locked_only)
        self.assertNotIn("GetTimeSeconds", FILL_RESULT)
        self.assertNotIn("MissionStartWorldTimeSeconds", FILL_RESULT)
        self.assertNotIn("WorldContextObject->GetWorld()", FILL_RESULT)

    def test_contract_does_not_open_gunner_or_director_headers(self) -> None:
        self.assertEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardCampaignSubsystem.h",
        )
        self.assertNotIn("SkyguardGunner.h", HEADER_PATH)
        self.assertNotIn(
            "SkyguardMissionDirectorCampaignHelpers.h",
            HEADER_PATH,
        )
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)
        locked_only = f"{FILL_RESULT}\n"
        self.assertNotIn("SkyguardGunner.h", locked_only)
        self.assertNotIn(
            "SkyguardMissionDirectorCampaignHelpers.h",
            locked_only,
        )
        self.assertNotIn("SkyguardGunner.h", FILL_RESULT)

    def test_contract_does_not_relock_get_active_mission(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        for neighbor in GET_ACTIVE_MISSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
        self.assertNotIn(
            "USkyguardMissionDefinition* GetActiveMission() const",
            FILL_RESULT,
        )
        self.assertNotIn(
            "USkyguardMissionDefinition* GetActiveMission() const",
            locked_only,
        )

    def test_contract_does_not_relock_configure_can_start_or_start(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        for neighbor in CONFIGURE_CAN_START_START_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
        self.assertNotIn("ConfigureCampaign", FILL_RESULT)
        self.assertNotIn("CanStartMission", FILL_RESULT)
        self.assertNotIn("StartMission", FILL_RESULT)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)

    def test_contract_does_not_relock_is_mission_unlocked(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        for neighbor in IS_MISSION_UNLOCKED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
        self.assertNotIn("IsMissionUnlocked", FILL_RESULT)
        self.assertNotIn("IsMissionUnlocked", locked_only)

    def test_contract_does_not_relock_objectives(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        for neighbor in OBJECTIVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
        self.assertNotIn("AddObjectiveProgress", FILL_RESULT)
        self.assertNotIn("FailObjective", FILL_RESULT)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", FILL_RESULT)
        self.assertNotIn("AddObjectiveProgress", locked_only)
        self.assertNotIn("FailObjective", locked_only)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", locked_only)

    def test_contract_does_not_relock_active_mission_helpers(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        for neighbor in ACTIVE_MISSION_HELPERS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
        self.assertNotIn("CompleteActiveMission", FILL_RESULT)
        self.assertNotIn("FinalizeActiveMission", FILL_RESULT)
        self.assertNotIn("FailActiveMission", FILL_RESULT)
        self.assertNotIn("CompleteActiveMission", locked_only)
        self.assertNotIn("FinalizeActiveMission", locked_only)
        self.assertNotIn("FailActiveMission", locked_only)

    def test_contract_does_not_relock_elapsed_seconds(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        for neighbor in ELAPSED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
        self.assertNotIn("GetActiveMissionElapsedSeconds", FILL_RESULT)
        self.assertNotIn("GetActiveMissionElapsedSeconds", locked_only)

    def test_contract_does_not_relock_acknowledge_debrief(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        for neighbor in ACKNOWLEDGE_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
        self.assertNotIn("AcknowledgeDebrief", FILL_RESULT)
        self.assertNotIn("AcknowledgeDebrief", locked_only)

    def test_contract_does_not_relock_debrief_neighbors(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        for neighbor in DEBRIEF_NEIGHBORS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
        self.assertNotIn("RetrySaveLastDebrief", FILL_RESULT)
        self.assertNotIn("GetLastDebrief", FILL_RESULT)
        self.assertNotIn("RetrySaveLastDebrief", locked_only)
        self.assertNotIn("GetLastDebrief", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FILL_RESULT)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_travel_helpers(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        for neighbor in TRAVEL_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
        self.assertNotIn("CanTravelToNextMission", FILL_RESULT)
        self.assertNotIn("GetNextMissionMapPackageName", FILL_RESULT)
        self.assertNotIn("TravelToNextMission", FILL_RESULT)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)

    def test_contract_does_not_relock_runtime_getters(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        for neighbor in RUNTIME_GETTERS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
        self.assertNotIn("GetObjectiveRuntime", FILL_RESULT)
        self.assertNotIn("GetRouteRuntime", FILL_RESULT)
        self.assertNotIn("GetMissionRecords", FILL_RESULT)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("GetRouteRuntime", locked_only)
        self.assertNotIn("GetMissionRecords", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{FILL_RESULT}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FILL_RESULT)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_save_game_helpers(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        for neighbor in SAVE_GAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
        self.assertNotIn("ApplySaveGame", FILL_RESULT)
        self.assertNotIn("BuildSaveGame", FILL_RESULT)
        self.assertNotIn("SaveCampaignToSlot", FILL_RESULT)
        self.assertNotIn("LoadCampaignFromSlot", FILL_RESULT)
        self.assertNotIn("DeleteCampaignSlot", FILL_RESULT)
        self.assertNotIn("IsValidCampaignSlotName", FILL_RESULT)
        self.assertNotIn("GetEarnedCampaignMedals", FILL_RESULT)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("BuildSaveGame", locked_only)
        self.assertNotIn("SaveCampaignToSlot", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)
        self.assertNotIn("GetEarnedCampaignMedals", locked_only)

    def test_contract_does_not_relock_score_or_medal(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        for neighbor in SCORE_MEDAL_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
        self.assertNotIn("CalculateMissionScore", FILL_RESULT)
        self.assertNotIn("CalculateMedalTier", FILL_RESULT)
        self.assertNotIn("CalculateMissionScore", locked_only)
        self.assertNotIn("CalculateMedalTier", locked_only)

    def test_contract_does_not_relock_leftover_director_helpers(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        for token in LEFTOVER_DIRECTOR_HELPERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FILL_RESULT)
        self.assertNotIn("FillAndFinalize", FILL_RESULT)
        self.assertNotIn("FillAndFail", FILL_RESULT)
        self.assertNotIn("LoadCampaignProgressAfterConfigure", FILL_RESULT)
        self.assertNotIn("SkyguardMissionDirectorCampaignHelpers", FILL_RESULT)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("LoadCampaignProgressAfterConfigure", locked_only)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FILL_RESULT)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{FILL_RESULT}\n"
        self.assertEqual(
            require_declaration(locked_only, FILL_RESULT),
            FILL_RESULT,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)
        self.assertNotIn("IsMissionUnlocked", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)
        self.assertNotIn("GetEarnedCampaignMedals", locked_only)
        self.assertNotIn("GetLastDebrief", locked_only)
        self.assertNotIn("RetrySaveLastDebrief", locked_only)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("GetRouteRuntime", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
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
            require_declaration(section, FILL_RESULT),
            FILL_RESULT,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::FillResultCombatStats",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, FILL_RESULT)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::FillResultCombatStats",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", FILL_RESULT)
        self.assertNotIn("}", FILL_RESULT)
        self.assertNotIn("return 0.f", FILL_RESULT)
        self.assertNotIn("GetTimeSeconds", FILL_RESULT)

    def test_incoming_radar_clocks_absent_from_campaign_public(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{FILL_RESULT}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, FILL_RESULT)
            self.assertNotIn(token, locked_only)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn(HARBOR_INCOMING, FILL_RESULT)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_harbor_40_80_tokens_fail_closed_in_this_file_and_declaration(
        self,
    ) -> None:
        this_file = Path(__file__).read_text(encoding="utf-8")
        locked_only = f"{FILL_RESULT}\n"
        for token in HARBOR_TUNING:
            self.assertIn(token, this_file)
            self.assertNotIn(token, FILL_RESULT)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", FILL_RESULT)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardApacheAircraft.h",
        )
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)

    def test_pathfinder_last_flight_lifeline_are_not_harbor_40_80(self) -> None:
        this_file = Path(__file__).read_text(encoding="utf-8")
        self.assertIn(PATHFINDER_NOT_HARBOR, this_file)
        self.assertIn(LAST_FLIGHT_NOT_HARBOR, this_file)
        self.assertIn(LIFELINE_HUNTER_NOT_HARBOR, this_file)
        self.assertNotIn("MinHeightFromOriginCm", FILL_RESULT)
        self.assertNotIn("MinimumCivilianSeparationMeters", FILL_RESULT)
        self.assertNotIn("MinimumWeaponSeparationMeters", FILL_RESULT)
        self.assertNotEqual(PATHFINDER_NOT_HARBOR, "40.f")
        self.assertNotEqual(PATHFINDER_NOT_HARBOR, "80.f")
        self.assertNotEqual(LAST_FLIGHT_NOT_HARBOR, "40.f")
        self.assertNotEqual(LIFELINE_HUNTER_NOT_HARBOR, "80.f")
        self.assertNotIn("550.f", FILL_RESULT)
        self.assertNotIn("450.f", FILL_RESULT)

    def test_contract_does_not_require_leftover_live_mount(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("R" "ifle", section)
        self.assertNotIn("I" "gla", section)
        self.assertNotIn("Y" "ak", section)
        self.assertNotEqual(FILL_RESULT, "R" "ifle")
        self.assertNotEqual(FILL_RESULT, "I" "gla")
        self.assertNotIn("FireI" "gla", section)
        self.assertNotIn("FireR" "ifle", section)
        self.assertNotIn("Y" "akSpawnLocation", section)
        self.assertNotIn("bY" "akRuntimeReady", section)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_leftover_live_mount_terms(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"campaign FillResultCombatStats contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, FILL_RESULT.lower())

    def test_this_file_splits_banned_live_mount_tokens(self) -> None:
        text = Path(__file__).read_text(encoding="utf-8").lower()
        for banned in BANNED:
            self.assertNotIn(banned, text)

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", FILL_RESULT)

    def test_locked_scripts_list_sibling_isolated_contracts(self) -> None:
        scripts = "\n".join(LOCKED_SCRIPTS)
        required = (
            "test_configure_campaign_decl_contract.py",
            "test_can_start_mission_decl_contract.py",
            "test_start_mission_decl_contract.py",
            "test_add_objective_progress_decl_contract.py",
            "test_fail_objective_decl_contract.py",
            "test_complete_survive_objective_if_intact_decl_contract.py",
            "test_complete_active_mission_decl_contract.py",
            "test_finalize_active_mission_decl_contract.py",
            "test_fail_active_mission_decl_contract.py",
            "test_get_active_mission_elapsed_seconds_decl_contract.py",
            "test_retry_save_last_debrief_decl_contract.py",
            "test_acknowledge_debrief_decl_contract.py",
            "test_get_last_debrief_decl_contract.py",
            "test_can_travel_to_next_mission_decl_contract.py",
            "test_get_next_mission_map_package_name_decl_contract.py",
            "test_travel_to_next_mission_decl_contract.py",
            "test_apply_save_game_decl_contract.py",
            "test_build_save_game_decl_contract.py",
            "test_save_campaign_to_slot_decl_contract.py",
            "test_load_campaign_from_slot_decl_contract.py",
            "test_delete_campaign_slot_decl_contract.py",
            "test_is_valid_campaign_slot_name_decl_contract.py",
            "test_is_mission_unlocked_decl_contract.py",
            "test_get_earned_campaign_medals_decl_contract.py",
            "test_get_active_mission_decl_contract.py",
            "test_get_objective_runtime_decl_contract.py",
            "test_get_route_runtime_decl_contract.py",
            "test_get_mission_records_decl_contract.py",
            "test_calculate_mission_score_decl_contract.py",
            "test_calculate_medal_tier_decl_contract.py",
            "test_campaign_save_empty_fail_closed.py",
            "test_campaign_roster_lookup_contract.py",
            "test_campaign_load_progress_decl_contract.py",
        )
        for name in required:
            self.assertIn(name, scripts)
        self.assertNotIn(
            "test_fill_result_combat_stats_decl_contract.py",
            scripts,
        )
        self.assertIn("SkyguardCampaignSubsystem.h", LOCKED)
        self.assertIn("SkyguardCampaignSubsystem.cpp", LOCKED)
        self.assertIn("SkyguardRadarNode.cpp", LOCKED)
        self.assertIn("SkyguardHarborProofTests.cpp", LOCKED)
        self.assertIn("SkyguardCampaignTheaterKitTests.cpp", LOCKED)
        self.assertIn("SkyguardGunner.h", LOCKED)
        self.assertIn("SkyguardGunner.cpp", LOCKED)

    def test_contract_is_fill_result_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, FILL_RESULT),
            FILL_RESULT,
        )
        locked_only = f"{FILL_RESULT}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FILL_RESULT)
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
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FILL_RESULT)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FILL_RESULT)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FILL_RESULT)
        for token in LEFTOVER_DIRECTOR_HELPERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FILL_RESULT)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, FILL_RESULT)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, FILL_RESULT)
            self.assertNotIn(token, section)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, FILL_RESULT)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("R" "ifle", section)
        self.assertNotIn("I" "gla", section)
        self.assertNotIn("Y" "ak", section)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", FILL_RESULT)
        self.assertNotIn("{", FILL_RESULT)
        self.assertNotEqual(FILL_RESULT, "R" "ifle")
        self.assertNotEqual(FILL_RESULT, "I" "gla")
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertIn("void FillResultCombatStats(", FILL_RESULT)
        self.assertIn("const ASkyguardGunner* Gunner", FILL_RESULT)
        self.assertIn("const UObject* WorldContextObject", FILL_RESULT)
        self.assertTrue(FILL_RESULT.endswith("const;"), FILL_RESULT)

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
