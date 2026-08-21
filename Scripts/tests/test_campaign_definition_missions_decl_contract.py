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
# a missions default, or lock Missions in the .cpp.
# origin/main is one line
# (`TArray<TObjectPtr<USkyguardMissionDefinition>> Missions;`);
# accept that form and other split-line wraps. Nearby
# UPROPERTY metadata is present on origin/main; do not
# invent metadata that is not in origin/main.
MISSIONS = (
    "TArray<TObjectPtr<USkyguardMissionDefinition>> Missions;"
)
UPROPERTY_CAMPAIGN = (
    'UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Campaign")'
)
# Leftover #56–#64 plus CampaignDefinition production files.
# This lane only adds an isolated Python Missions field
# declaration contract. Stay off CampaignId #343,
# DisplayName #344, ValidateDefinition #331,
# FindMission #340, GetPrimaryAssetId #339, leftover
# campaign-roster #111, leftover campaign-save
# empty-fail-closed, USkyguardCampaignSubsystem methods,
# LoadCampaignProgress #290, leftover CPG debrief
# #284/#195/#130/#8ccd, leftover bind-hud-host, leftover
# objective-runtime fail-closed, leftover route-runtime
# fail-closed, leftover pilot #117/#120/#128/#129/#170,
# leftover gun-fire camera shake #8860, leftover
# mission-weather enum #96d2, FillResultCombatStats /
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
# broadcast, leftover bind-hud-host, leftover gun-fire
# camera shake, leftover mission-weather enum, leftover
# pilot siblings, CampaignId #343, DisplayName #344,
# ValidateDefinition #331, FindMission #340,
# GetPrimaryAssetId #339, leftover mission-save-record
# defaults, and newly drafted campaign-subsystem siblings
# stay sibling-only.
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
    "Scripts/tests/test_campaign_definition_display_name_decl_contract.py",
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
    "Scripts/tests/test_bind_hud_host_presentation_tests.py",
    "Scripts/tests/test_gun_fire_camera_shake_tests.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
)
# Neighbors in the same public section. Presence is not locked
# here. CampaignId #343 / DisplayName #344 /
# ValidateDefinition #331 / FindMission #340 /
# GetPrimaryAssetId #339 stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "FName CampaignId",
    "FText DisplayName",
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
DISPLAY_NAME_NOT_LOCKED = (
    "FText DisplayName;",
)
# USkyguardCampaignSubsystem helpers stay unlocked. This lane
# is Missions on USkyguardCampaignDefinition only.
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
    'Category = "Campaign|Missions"',
    "AllowPrivateAccess",
    "meta =",
)
# Invented missions defaults are not on origin/main.
# Do not invent an initializer or INDEX_NONE sentinel.
INVENTED_MISSIONS_DEFAULT = (
    "INDEX_NONE",
    "NAME_None",
    "{}",
    "TArray()",
)
# .cpp Missions body / invented INDEX_NONE stay unlocked.
# Do not invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "USkyguardCampaignDefinition::Missions",
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
    compact = re.sub(r"\s*<\s*", "<", compact)
    compact = re.sub(r"\s*>\s*", ">", compact)
    compact = re.sub(r">([A-Za-z_])", r"> \1", compact)
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


class CampaignDefinitionMissionsDeclContractTests(unittest.TestCase):
    def test_campaign_definition_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, MISSIONS), section)

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
            f"\t{MISSIONS}\n"
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
            f"\t{MISSIONS}\n"
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
            "\tFText DisplayName;\n"
            "private:\n"
            f"\t{MISSIONS}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, MISSIONS)
        self.assertIn("Missions", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, MISSIONS))

    def test_missing_missions_declaration_fails_closed(self) -> None:
        neighbors_only = (
            '\tFName CampaignId = TEXT("Skyguard52MainCampaign");\n'
            "\tFText DisplayName;\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() "
            "const override;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
            "\tUSkyguardMissionDefinition* FindMission("
            "FName MissionId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, MISSIONS)
        self.assertIn("Missions", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_CAMPAIGN}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, MISSIONS)
        self.assertIn("Missions", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_CAMPAIGN, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('Category = "Campaign"', section)
        self.assertTrue(has_declaration(section, MISSIONS), section)
        self.assertNotIn("UPROPERTY", MISSIONS)
        self.assertNotIn("EditAnywhere", MISSIONS)
        self.assertNotIn("BlueprintReadOnly", MISSIONS)
        self.assertNotIn("Category", MISSIONS)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_CAMPAIGN)
            self.assertNotIn(invented, MISSIONS)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            '\tFName CampaignId = TEXT("Skyguard52MainCampaign");\n'
            "\tFText DisplayName;\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() "
            "const override;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
            "\tUSkyguardMissionDefinition* FindMission("
            "FName MissionId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, MISSIONS)
        self.assertIn("Missions", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        raw_pointer = (
            "\tTArray<USkyguardMissionDefinition*> Missions;\n"
        )
        soft_ptr = (
            "\tTArray<TSoftObjectPtr<USkyguardMissionDefinition>> "
            "Missions;\n"
        )
        wrong_inner = (
            "\tTArray<TObjectPtr<USkyguardCampaignDefinition>> "
            "Missions;\n"
        )
        wrong_name = (
            "\tTArray<TObjectPtr<USkyguardMissionDefinition>> "
            "MissionList;\n"
        )
        map_type = (
            "\tTMap<FName, TObjectPtr<USkyguardMissionDefinition>> "
            "Missions;\n"
        )
        name_type = "\tFName Missions;\n"
        assigned = (
            "\tTArray<TObjectPtr<USkyguardMissionDefinition>> "
            "Missions = {};\n"
        )
        campaign_id = (
            '\tFName CampaignId = TEXT("Skyguard52MainCampaign");\n'
        )
        display_name = "\tFText DisplayName;\n"
        for region in (
            raw_pointer,
            soft_ptr,
            wrong_inner,
            wrong_name,
            map_type,
            name_type,
            assigned,
            campaign_id,
            display_name,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, MISSIONS)
            self.assertIn("Missions", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_invented_missions_assignment_does_not_satisfy(self) -> None:
        assigned = (
            "\tTArray<TObjectPtr<USkyguardMissionDefinition>> "
            "Missions = {};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(assigned, MISSIONS)
        self.assertIn("Missions", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(assigned, MISSIONS))

    def test_wrong_type_does_not_satisfy(self) -> None:
        wrong = "\tTArray<USkyguardMissionDefinition*> Missions;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(wrong, MISSIONS)
        self.assertIn("Missions", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(wrong, MISSIONS))

    def test_missions_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, MISSIONS),
            MISSIONS,
        )
        self.assertTrue(has_declaration(section, MISSIONS))
        self.assertEqual(
            declaration_count(section, MISSIONS),
            1,
        )
        self.assertTrue(
            MISSIONS.endswith(";"),
            MISSIONS,
        )
        self.assertTrue(
            MISSIONS.startswith("TArray<"),
            MISSIONS,
        )
        self.assertIn("Missions", MISSIONS)
        self.assertIn("TObjectPtr", MISSIONS)
        self.assertIn("USkyguardMissionDefinition", MISSIONS)
        self.assertNotIn("=", MISSIONS)
        self.assertNotIn("INDEX_NONE", MISSIONS)
        self.assertNotIn("NAME_None", MISSIONS)
        self.assertNotIn("{", MISSIONS)
        self.assertNotIn("}", MISSIONS)
        self.assertNotIn("return ", MISSIONS)

    def test_declaration_does_not_invent_missions_default(self) -> None:
        locked_only = f"{MISSIONS}\n"
        self.assertNotIn("=", MISSIONS)
        self.assertNotIn("TEXT(", MISSIONS)
        self.assertNotIn("Skyguard52MainCampaign", MISSIONS)
        for invented in INVENTED_MISSIONS_DEFAULT:
            self.assertNotIn(invented, MISSIONS)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, MISSIONS), section)
        self.assertNotIn("NAME_None", MISSIONS)
        self.assertNotIn("INDEX_NONE", MISSIONS)
        self.assertNotIn("{}", locked_only)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tTArray<TObjectPtr<USkyguardMissionDefinition>>\n"
            "\tMissions;\n"
            "private:\n"
            "};\n"
        )
        wrap_tabs = (
            "public:\n"
            "\tTArray<TObjectPtr<USkyguardMissionDefinition>>\n"
            "\t\tMissions;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tTArray<TObjectPtr<USkyguardMissionDefinition>>    "
            "Missions;\n"
            "};\n"
        )
        wrap_leading = (
            "public:\n"
            "    TArray<TObjectPtr<USkyguardMissionDefinition>> "
            "Missions;\n"
            "};\n"
        )
        wrap_template = (
            "public:\n"
            "\tTArray<\n"
            "\t\tTObjectPtr<USkyguardMissionDefinition>\n"
            "\t> Missions;\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_type}"
        )
        header_wrap_tabs = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_tabs}"
        )
        header_wrap_spaces = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_spaces}"
        )
        header_wrap_leading = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_leading}"
        )
        header_wrap_template = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_template}"
        )
        for header in (
            header_wrap_type,
            header_wrap_tabs,
            header_wrap_spaces,
            header_wrap_leading,
            header_wrap_template,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, MISSIONS),
                section,
            )
            self.assertEqual(
                require_declaration(section, MISSIONS),
                MISSIONS,
            )
            self.assertEqual(
                declaration_count(section, MISSIONS),
                1,
            )
        one_line = f"{{\npublic:\n\t{MISSIONS}\n}}\n"
        self.assertTrue(has_declaration(one_line, MISSIONS))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, MISSIONS), section)
        self.assertEqual(
            require_declaration(section, MISSIONS),
            MISSIONS,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{MISSIONS}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", MISSIONS)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", MISSIONS)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{MISSIONS}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, MISSIONS)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_CAMPAIGN)
        section = public_section(origin_main_header())
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, section)
        self.assertIn(UPROPERTY_CAMPAIGN, section)

    def test_contract_does_not_lock_missions_cpp_body(self) -> None:
        locked_only = f"{MISSIONS}\n"
        self.assertNotIn("{", MISSIONS)
        self.assertNotIn("}", MISSIONS)
        self.assertNotIn("return ", MISSIONS)
        self.assertNotIn(
            "USkyguardCampaignDefinition::Missions",
            MISSIONS,
        )
        self.assertNotIn(
            "SkyguardCampaignDefinition.cpp",
            MISSIONS,
        )
        self.assertNotIn("SkyguardCampaignDefinition.cpp", locked_only)
        self.assertNotIn("return false", MISSIONS)
        self.assertNotIn("AddError", MISSIONS)

    def test_contract_does_not_relock_campaign_id(self) -> None:
        locked_only = f"{MISSIONS}\n"
        for neighbor in CAMPAIGN_ID_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSIONS)
        self.assertNotIn("CampaignId", MISSIONS)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("Skyguard52MainCampaign", MISSIONS)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)
        self.assertNotIn("FName", MISSIONS)

    def test_contract_does_not_relock_display_name(self) -> None:
        locked_only = f"{MISSIONS}\n"
        for neighbor in DISPLAY_NAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSIONS)
        self.assertNotIn("DisplayName", MISSIONS)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("FText", MISSIONS)

    def test_contract_does_not_relock_validate_definition(self) -> None:
        locked_only = f"{MISSIONS}\n"
        for neighbor in VALIDATE_DEFINITION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSIONS)
        self.assertNotIn("ValidateDefinition", MISSIONS)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("OutErrors", MISSIONS)
        self.assertNotIn("BlueprintCallable", MISSIONS)

    def test_contract_does_not_relock_find_mission(self) -> None:
        locked_only = f"{MISSIONS}\n"
        for neighbor in FIND_MISSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSIONS)
        self.assertNotIn("FindMission", MISSIONS)
        self.assertNotIn("FindMission", locked_only)
        self.assertNotIn("BlueprintPure", MISSIONS)

    def test_contract_does_not_relock_primary_asset_id(self) -> None:
        locked_only = f"{MISSIONS}\n"
        for neighbor in PRIMARY_ASSET_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSIONS)
        self.assertNotIn("GetPrimaryAssetId", MISSIONS)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("FPrimaryAssetId", MISSIONS)

    def test_contract_does_not_relock_campaign_subsystem_methods(self) -> None:
        locked_only = f"{MISSIONS}\n"
        section = public_section(origin_main_header())
        for neighbor in SUBSYSTEM_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSIONS)
            self.assertNotIn(neighbor, section)
        self.assertNotIn("ConfigureCampaign", MISSIONS)
        self.assertNotIn("CanStartMission", MISSIONS)
        self.assertNotIn("StartMission", MISSIONS)
        self.assertNotIn("GetActiveMission", MISSIONS)
        self.assertNotIn("USkyguardCampaignSubsystem", MISSIONS)
        self.assertNotIn("USkyguardCampaignSubsystem", locked_only)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("StartMission", locked_only)

    def test_contract_does_not_relock_save_game_helpers(self) -> None:
        locked_only = f"{MISSIONS}\n"
        for neighbor in SAVE_GAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSIONS)
        self.assertNotIn("ApplySaveGame", MISSIONS)
        self.assertNotIn("BuildSaveGame", MISSIONS)
        self.assertNotIn("RetrySaveLastDebrief", MISSIONS)
        self.assertNotIn("SaveCampaignToSlot", MISSIONS)
        self.assertNotIn("LoadCampaignFromSlot", MISSIONS)
        self.assertNotIn("DeleteCampaignSlot", MISSIONS)
        self.assertNotIn("GetMissionRecords", MISSIONS)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("BuildSaveGame", locked_only)
        self.assertNotIn("RetrySaveLastDebrief", locked_only)
        self.assertNotIn("SaveCampaignToSlot", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("GetMissionRecords", locked_only)

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{MISSIONS}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSIONS)
        self.assertNotIn("FillResultCombatStats", MISSIONS)
        self.assertNotIn("ASkyguardGunner", MISSIONS)
        self.assertNotIn("FillAndFinalize", MISSIONS)
        self.assertNotIn("FillAndFail", MISSIONS)
        self.assertNotIn("ApplyHydraForClusters", MISSIONS)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{MISSIONS}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSIONS)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{MISSIONS}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSIONS)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{MISSIONS}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSIONS)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{MISSIONS}\n"
        self.assertEqual(
            require_declaration(locked_only, MISSIONS),
            MISSIONS,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSIONS)
        self.assertNotIn("FindMission", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
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
            require_declaration(section, MISSIONS),
            MISSIONS,
        )
        self.assertNotIn("SkyguardCampaignDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignDefinition::Missions",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, MISSIONS)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCampaignDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignDefinition::Missions",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", MISSIONS)
        self.assertNotIn("}", MISSIONS)
        self.assertNotIn("return false", MISSIONS)
        self.assertNotIn("AddError", MISSIONS)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{MISSIONS}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, MISSIONS)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, MISSIONS)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{MISSIONS}\n"
        section = public_section(origin_main_header())
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            "40.f, 80.f",
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSIONS)
            self.assertNotIn(token, section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(MISSIONS, "Rifle")
        self.assertNotEqual(MISSIONS, "Igla")
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
                f"campaign Missions contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, MISSIONS.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", MISSIONS)

    def test_contract_is_missions_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, MISSIONS),
            MISSIONS,
        )
        locked_only = f"{MISSIONS}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MISSIONS)
        self.assertNotIn("FindMission", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
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
            self.assertNotIn(token, MISSIONS)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSIONS)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MISSIONS)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, MISSIONS)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, MISSIONS)
            self.assertNotIn(token, section)
        for token in INVENTED_MISSIONS_DEFAULT:
            self.assertNotIn(token, MISSIONS)
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
        self.assertNotIn("return ", MISSIONS)
        self.assertNotIn("{", MISSIONS)
        self.assertNotIn("AddError", MISSIONS)
        self.assertNotEqual(MISSIONS, "Rifle")
        self.assertNotEqual(MISSIONS, "Igla")
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertNotIn("USkyguardCampaignSubsystem", locked_only)
        self.assertNotIn("=", MISSIONS)
        self.assertNotIn("CampaignId", MISSIONS)
        self.assertNotIn("DisplayName", MISSIONS)

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
