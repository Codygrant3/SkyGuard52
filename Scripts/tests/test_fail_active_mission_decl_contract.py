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
# failure-debrief payload, persistence result, score, medal,
# or slot-save behavior, or lock the FailActiveMission body
# in the .cpp. origin/main is split-line
# (`bool FailActiveMission(` /
# `FSkyguardMissionResult& InOutResult,` /
# `const FString& SlotName = TEXT("Skyguard52Campaign"),` /
# `int32 UserIndex = 0);`);
# accept that form and other split-line wraps.
FAIL_ACTIVE_MISSION_DECL = (
    "bool FailActiveMission("
    "FSkyguardMissionResult& InOutResult, "
    "const FString& SlotName = TEXT(\"Skyguard52Campaign\"), "
    "int32 UserIndex = 0);"
)
# Leftover #56–#64 plus CampaignSubsystem production files.
# This lane only adds an isolated Python FailActiveMission
# declaration contract. Stay off CompleteActiveMission /
# FinalizeActiveMission (in-flight siblings),
# FillResultCombatStats (takes leftover ASkyguardGunner*),
# FillAndFinalize / FillAndFail (leftover Gunner),
# GetActiveMissionElapsedSeconds (sibling), GetActiveMission
# / GetObjectiveRuntime / TravelToNextMission (siblings),
# AddObjectiveProgress #316 / FailObjective #315 /
# CompleteSurviveObjectiveIfIntact (sibling drafts), leftover
# objective-runtime fail-closed / leftover route-runtime
# fail-closed, leftover CPG debrief #284/#195/#130/#8ccd,
# leftover campaign-save empty-fail-closed drafts, leftover
# campaign-roster lookup #111, LoadCampaignProgressAfterConfigure
# (#290), leftover Harbor #6/#8/#9, leftover theater-kit #59,
# leftover flare/HUD #57/#61/#62, leftover drafts #56–#64,
# leftover #147 ApacheSystem, leftover #149 weapon stations,
# leftover #152 pilot commands, leftover #154 loadout /
# lock-phase, leftover settings invert-look / ApplySettings
# broadcast #134, Harbor IncomingRadar 40/80, leftover live
# copy, FSkyguardMission0NIntegrationReadiness
# (bYakRuntimeReady), dirty D:\Skyguard52, and
# ApplyHydraForClusters.
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
# Isolated-test drafts stay off this lane. CompleteActiveMission /
# FinalizeActiveMission, GetActiveMissionElapsedSeconds,
# leftover campaign-save empty-fail-closed, leftover
# campaign-roster lookup, leftover LoadCampaignProgressAfterConfigure,
# leftover CPG debrief copy / snapshot / fail-closed, leftover
# objective-runtime fail-closed, leftover route-runtime
# fail-closed, leftover theater-kit / Harbor / flare/HUD,
# leftover FillAndFinalize / FillAndFail, leftover settings
# invert-look / ApplySettings broadcast, and newly drafted
# campaign-subsystem siblings stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
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
    "Scripts/tests/test_complete_active_mission_decl_contract.py",
    "Scripts/tests/test_finalize_active_mission_decl_contract.py",
    "Scripts/tests/test_add_objective_progress_decl_contract.py",
    "Scripts/tests/test_fail_objective_decl_contract.py",
    "Scripts/tests/test_complete_survive_objective_if_intact_decl_contract.py",
    "Scripts/tests/test_objective_runtime_fail_closed.py",
    "Scripts/tests/test_objective_runtime_empty_fail_closed.py",
    "Scripts/tests/test_objective_runtime_fail_closed_contract.py",
    "Scripts/tests/test_objective_runtime_survive.py",
    "Scripts/tests/test_objective_runtime_survive_fail_closed.py",
    "Scripts/tests/test_objective_runtime_survive_tests.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_route_runtime_fail_closed.py",
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
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
)
# Neighbors in the same public section. Presence is not locked here.
# CompleteActiveMission / FinalizeActiveMission are in-flight
# siblings. FillResultCombatStats takes leftover
# ASkyguardGunner*. GetActiveMissionElapsedSeconds is a
# sibling. Leftover CPG debrief #284/#195/#130/#8ccd stay
# sibling-only.
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
    "bool SaveCampaignToSlot(",
    "bool LoadCampaignFromSlot(",
    "bool DeleteCampaignSlot(",
    "static bool IsValidCampaignSlotName(const FString& SlotName);",
    "int32 GetEarnedCampaignMedals() const;",
    "USkyguardMissionDefinition* GetActiveMission() const",
    "USkyguardObjectiveRuntime* GetObjectiveRuntime() const",
    "USkyguardRouteRuntime* GetRouteRuntime() const",
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
)
FILL_COMBAT_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
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
# cluster apply stay unlocked.
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
)
# Invented FailActiveMission payload / persistence / score /
# medal / slot-save stay unlocked. The nearby origin/main
# comment may mention FillResultCombatStats and
# FailureDebrief; do not lock those as this contract.
INVENTED_FAIL_PAYLOAD = (
    "BuildFailureDebrief",
    "BuildSuccessDebrief",
    "ClearActiveMissionRuntime",
    "bMissionSucceeded = false",
    "FinalScore = 0",
    "MedalTier = 0",
    "bProgressSaved = false",
    "FillAndFinalize",
    "FillAndFail",
    "(void)UserIndex",
)
# .cpp FailActiveMission body / invented return values stay
# unlocked. Do not invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "return 0",
    "return -1",
    "BuildFailureDebrief",
    "ClearActiveMissionRuntime",
    "bMissionSucceeded = false",
    "FinalScore = 0",
    "MedalTier = 0",
    "bProgressSaved = false",
    "(void)UserIndex",
    "USkyguardCampaignSubsystem::FailActiveMission",
    "SkyguardCampaignSubsystem.cpp",
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


class FailActiveMissionDeclContractTests(unittest.TestCase):
    def test_campaign_subsystem_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, FAIL_ACTIVE_MISSION_DECL),
            section,
        )

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
            f"\t{FAIL_ACTIVE_MISSION_DECL}\n"
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
            f"\t{FAIL_ACTIVE_MISSION_DECL}\n"
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
            f"\t{FAIL_ACTIVE_MISSION_DECL}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, FAIL_ACTIVE_MISSION_DECL)
        self.assertIn("FailActiveMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, FAIL_ACTIVE_MISSION_DECL))

    def test_missing_fail_active_mission_declaration_fails_closed(self) -> None:
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
            "\tvoid FillResultCombatStats(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            "\t\tconst ASkyguardGunner* Gunner,\n"
            "\t\tconst UObject* WorldContextObject) const;\n"
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
            require_declaration(neighbors_only, FAIL_ACTIVE_MISSION_DECL)
        self.assertIn("FailActiveMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintCallable, Category = "Campaign|Sortie")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, FAIL_ACTIVE_MISSION_DECL)
        self.assertIn("FailActiveMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tbool CompleteActiveMission("
            "FSkyguardMissionResult& InOutResult);\n"
            "\tbool FinalizeActiveMission(\n"
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
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, FAIL_ACTIVE_MISSION_DECL)
        self.assertIn("FailActiveMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_defaults = (
            "\tbool FailActiveMission("
            "FSkyguardMissionResult& InOutResult);\n"
        )
        no_slot_default = (
            "\tbool FailActiveMission(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            "\t\tconst FString& SlotName,\n"
            "\t\tint32 UserIndex = 0);\n"
        )
        no_user_default = (
            "\tbool FailActiveMission(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex);\n"
        )
        wrong_slot = (
            "\tbool FailActiveMission(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            '\t\tconst FString& SlotName = TEXT("OtherCampaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
        )
        wrong_user = (
            "\tbool FailActiveMission(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 1);\n"
        )
        wrong_return = (
            "\tvoid FailActiveMission(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
        )
        const_method = (
            "\tbool FailActiveMission(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0) const;\n"
        )
        const_user_index = (
            "\tbool FailActiveMission(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tconst int32 UserIndex = 0);\n"
        )
        for region in (
            missing_defaults,
            no_slot_default,
            no_user_default,
            wrong_slot,
            wrong_user,
            wrong_return,
            const_method,
            const_user_index,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, FAIL_ACTIVE_MISSION_DECL)
            self.assertIn("FailActiveMission", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_fail_active_mission_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, FAIL_ACTIVE_MISSION_DECL),
            FAIL_ACTIVE_MISSION_DECL,
        )
        self.assertTrue(has_declaration(section, FAIL_ACTIVE_MISSION_DECL))
        self.assertEqual(
            declaration_count(section, FAIL_ACTIVE_MISSION_DECL),
            1,
        )
        self.assertTrue(
            FAIL_ACTIVE_MISSION_DECL.endswith(";"),
            FAIL_ACTIVE_MISSION_DECL,
        )
        self.assertTrue(
            FAIL_ACTIVE_MISSION_DECL.startswith("bool "),
            FAIL_ACTIVE_MISSION_DECL,
        )
        self.assertIn("FSkyguardMissionResult& InOutResult", FAIL_ACTIVE_MISSION_DECL)
        self.assertIn(
            'const FString& SlotName = TEXT("Skyguard52Campaign")',
            FAIL_ACTIVE_MISSION_DECL,
        )
        self.assertIn("int32 UserIndex = 0", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("INDEX_NONE", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("{", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("}", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("return ", FAIL_ACTIVE_MISSION_DECL)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_name = (
            "public:\n"
            "\tbool FailActiveMission(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
            "private:\n"
            "};\n"
        )
        wrap_type = (
            "public:\n"
            "\tbool\n"
            "\tFailActiveMission("
            "FSkyguardMissionResult& InOutResult, "
            'const FString& SlotName = TEXT("Skyguard52Campaign"), '
            "int32 UserIndex = 0);\n"
            "private:\n"
            "};\n"
        )
        wrap_args = (
            "public:\n"
            "\tbool FailActiveMission(FSkyguardMissionResult&\n"
            "\t\tInOutResult,\n"
            "\t\tconst FString&\n"
            '\t\tSlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32\n"
            "\t\tUserIndex = 0);\n"
            "};\n"
        )
        wrap_defaults = (
            "public:\n"
            "\tbool FailActiveMission(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            "\t\tconst FString& SlotName =\n"
            '\t\tTEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex =\n"
            "\t\t0);\n"
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
        for header in (
            header_wrap_name,
            header_wrap_type,
            header_wrap_args,
            header_wrap_defaults,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, FAIL_ACTIVE_MISSION_DECL),
                section,
            )
            self.assertEqual(
                require_declaration(section, FAIL_ACTIVE_MISSION_DECL),
                FAIL_ACTIVE_MISSION_DECL,
            )
            self.assertEqual(
                declaration_count(section, FAIL_ACTIVE_MISSION_DECL),
                1,
            )
        one_line = f"{{\npublic:\n\t{FAIL_ACTIVE_MISSION_DECL}\n}}\n"
        self.assertTrue(has_declaration(one_line, FAIL_ACTIVE_MISSION_DECL))
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, FAIL_ACTIVE_MISSION_DECL),
            section,
        )
        self.assertEqual(
            require_declaration(section, FAIL_ACTIVE_MISSION_DECL),
            FAIL_ACTIVE_MISSION_DECL,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", FAIL_ACTIVE_MISSION_DECL)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_failure_debrief_payload(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for token in INVENTED_FAIL_PAYLOAD:
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("BuildFailureDebrief", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("bMissionSucceeded = false", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("FillAndFail", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("FillAndFinalize", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("FillResultCombatStats", FAIL_ACTIVE_MISSION_DECL)

    def test_declaration_does_not_invent_persistence_score_medal_or_slot_save(
        self,
    ) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        self.assertNotIn("SaveCampaignToSlot", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("LoadCampaignFromSlot", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("bProgressSaved", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("FinalScore", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("MedalTier", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("CalculateMissionScore", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("CalculateMedalTier", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("GetEarnedCampaignMedals", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("SaveCampaignToSlot", locked_only)
        self.assertNotIn("bProgressSaved", locked_only)
        self.assertNotIn("FinalScore", locked_only)
        self.assertNotIn("MedalTier", locked_only)
        self.assertNotIn("CalculateMissionScore", locked_only)
        self.assertNotIn("CalculateMedalTier", locked_only)

    def test_contract_does_not_lock_fail_active_mission_cpp_body(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        self.assertNotIn("{", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("}", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("return ", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::FailActiveMission",
            FAIL_ACTIVE_MISSION_DECL,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", locked_only)
        self.assertNotIn("BuildFailureDebrief", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("ClearActiveMissionRuntime", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("(void)UserIndex", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("if (!ActiveMission)", FAIL_ACTIVE_MISSION_DECL)

    def test_contract_does_not_relock_get_active_mission(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for neighbor in GET_ACTIVE_MISSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn(
            "USkyguardMissionDefinition* GetActiveMission() const",
            FAIL_ACTIVE_MISSION_DECL,
        )
        self.assertNotIn(
            "USkyguardMissionDefinition* GetActiveMission() const",
            locked_only,
        )

    def test_contract_does_not_relock_configure_can_start_or_start(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for neighbor in CONFIGURE_CAN_START_START_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("ConfigureCampaign", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("CanStartMission", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("StartMission", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)

    def test_contract_does_not_relock_is_mission_unlocked(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for neighbor in IS_MISSION_UNLOCKED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("IsMissionUnlocked", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("IsMissionUnlocked", locked_only)

    def test_contract_does_not_relock_objectives(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for neighbor in OBJECTIVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("AddObjectiveProgress", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("FailObjective", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("AddObjectiveProgress", locked_only)
        self.assertNotIn("FailObjective", locked_only)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", locked_only)

    def test_contract_does_not_relock_active_mission_helpers(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for neighbor in ACTIVE_MISSION_HELPERS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("CompleteActiveMission", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("FinalizeActiveMission", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("CompleteActiveMission", locked_only)
        self.assertNotIn("FinalizeActiveMission", locked_only)

    def test_contract_does_not_relock_fill_result_combat_stats(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for neighbor in FILL_COMBAT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("FillResultCombatStats", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("ASkyguardGunner", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("FillAndFinalize", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("FillAndFail", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)

    def test_contract_does_not_relock_elapsed_seconds(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for neighbor in ELAPSED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("GetActiveMissionElapsedSeconds", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("GetActiveMissionElapsedSeconds", locked_only)

    def test_contract_does_not_relock_acknowledge_debrief(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for neighbor in ACKNOWLEDGE_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("AcknowledgeDebrief", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("AcknowledgeDebrief", locked_only)

    def test_contract_does_not_relock_debrief_neighbors(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for neighbor in DEBRIEF_NEIGHBORS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("RetrySaveLastDebrief", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("GetLastDebrief", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("RetrySaveLastDebrief", locked_only)
        self.assertNotIn("GetLastDebrief", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_travel_helpers(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for neighbor in TRAVEL_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("CanTravelToNextMission", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("GetNextMissionMapPackageName", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("TravelToNextMission", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)

    def test_contract_does_not_relock_runtime_getters(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for neighbor in RUNTIME_GETTERS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("GetObjectiveRuntime", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("GetRouteRuntime", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("GetRouteRuntime", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_save_game_helpers(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for neighbor in SAVE_GAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("ApplySaveGame", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("BuildSaveGame", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("SaveCampaignToSlot", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("LoadCampaignFromSlot", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("DeleteCampaignSlot", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("IsValidCampaignSlotName", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("GetEarnedCampaignMedals", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("BuildSaveGame", locked_only)
        self.assertNotIn("SaveCampaignToSlot", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)
        self.assertNotIn("GetEarnedCampaignMedals", locked_only)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        self.assertEqual(
            require_declaration(locked_only, FAIL_ACTIVE_MISSION_DECL),
            FAIL_ACTIVE_MISSION_DECL,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
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
        self.assertNotIn("CompleteActiveMission", locked_only)
        self.assertNotIn("FinalizeActiveMission", locked_only)
        self.assertNotIn("GetActiveMissionElapsedSeconds", locked_only)
        self.assertNotIn(
            "USkyguardMissionDefinition* GetActiveMission() const",
            locked_only,
        )
        self.assertNotIn("LoadCampaignProgressAfterConfigure", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)

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
            require_declaration(section, FAIL_ACTIVE_MISSION_DECL),
            FAIL_ACTIVE_MISSION_DECL,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::FailActiveMission",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::FailActiveMission",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("}", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("return false", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("return true", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("BuildFailureDebrief", FAIL_ACTIVE_MISSION_DECL)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        section = public_section(origin_main_header())
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            "40.f, 80.f",
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
            self.assertNotIn(token, section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(FAIL_ACTIVE_MISSION_DECL, "Rifle")
        self.assertNotEqual(FAIL_ACTIVE_MISSION_DECL, "Igla")
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
                f"campaign FailActiveMission contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, FAIL_ACTIVE_MISSION_DECL.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", FAIL_ACTIVE_MISSION_DECL)

    def test_locked_scripts_list_sibling_isolated_contracts(self) -> None:
        scripts = "\n".join(LOCKED_SCRIPTS)
        self.assertIn(
            "test_get_active_mission_elapsed_seconds_decl_contract.py",
            scripts,
        )
        self.assertIn("test_fail_objective_decl_contract.py", scripts)
        self.assertIn("test_add_objective_progress_decl_contract.py", scripts)
        self.assertIn(
            "test_complete_survive_objective_if_intact_decl_contract.py",
            scripts,
        )
        self.assertIn("test_complete_active_mission_decl_contract.py", scripts)
        self.assertIn("test_finalize_active_mission_decl_contract.py", scripts)
        self.assertIn("test_get_active_mission_decl_contract.py", scripts)
        self.assertIn("test_objective_runtime_fail_closed.py", scripts)
        self.assertIn("test_route_runtime_fail_closed.py", scripts)
        self.assertIn("test_campaign_save_empty_fail_closed.py", scripts)
        self.assertIn("test_cpg_debrief_fail_closed.py", scripts)
        self.assertIn("SkyguardCampaignSubsystem.h", LOCKED)
        self.assertIn("SkyguardCampaignSubsystem.cpp", LOCKED)
        self.assertIn("SkyguardRadarNode.cpp", LOCKED)
        self.assertIn("SkyguardHarborProofTests.cpp", LOCKED)
        self.assertIn("SkyguardCampaignTheaterKitTests.cpp", LOCKED)

    def test_contract_is_fail_active_mission_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, FAIL_ACTIVE_MISSION_DECL),
            FAIL_ACTIVE_MISSION_DECL,
        )
        locked_only = f"{FAIL_ACTIVE_MISSION_DECL}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)
        self.assertNotIn("IsMissionUnlocked", locked_only)
        self.assertNotIn("AddObjectiveProgress", locked_only)
        self.assertNotIn("FailObjective", locked_only)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", locked_only)
        self.assertNotIn("CompleteActiveMission", locked_only)
        self.assertNotIn("FinalizeActiveMission", locked_only)
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
        self.assertNotIn("SaveCampaignToSlot", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)
        self.assertNotIn("GetEarnedCampaignMedals", locked_only)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("GetRouteRuntime", locked_only)
        self.assertNotIn("CalculateMissionScore", locked_only)
        self.assertNotIn("CalculateMedalTier", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
        for token in INVENTED_FAIL_PAYLOAD:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, FAIL_ACTIVE_MISSION_DECL)
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
        self.assertNotIn("return ", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotIn("{", FAIL_ACTIVE_MISSION_DECL)
        self.assertNotEqual(FAIL_ACTIVE_MISSION_DECL, "Rifle")
        self.assertNotEqual(FAIL_ACTIVE_MISSION_DECL, "Igla")
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertIn(
            'TEXT("Skyguard52Campaign")',
            FAIL_ACTIVE_MISSION_DECL,
        )
        self.assertIn("int32 UserIndex = 0", FAIL_ACTIVE_MISSION_DECL)

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
