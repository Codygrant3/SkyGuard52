from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardCampaignSubsystem.h"
CLASS_NAME = "USkyguardCampaignSubsystem"
# Declaration presence only. Do not invent INDEX_NONE, return
# values, or lock the FailObjective body in the .cpp.
# origin/main is semicolon-only:
# `bool FailObjective(FName ObjectiveId);`
# Accept that form and split-line forms without locking a body.
FAIL_OBJECTIVE_DECL = "bool FailObjective(FName ObjectiveId);"
# Leftover #56–#64 plus CampaignSubsystem production files.
# This lane only adds an isolated Python FailObjective
# declaration contract. Stay off AddObjectiveProgress
# (in-flight sibling), leftover objective-runtime
# fail-closed / leftover objective-runtime survive tests,
# leftover objective-progress defaults #ae90 / leftover
# objective-definition defaults #b29f, GetObjectiveRuntime
# (newly drafted sibling), leftover CPG debrief
# #284/#195/#130/#8ccd, FillResultCombatStats (takes
# leftover ASkyguardGunner*), leftover campaign-save
# empty-fail-closed drafts, leftover campaign-roster
# lookup #111, leftover LoadCampaignProgressAfterConfigure
# (#290), leftover Harbor #6/#8/#9, leftover theater-kit
# #59, leftover flare/HUD #57/#61/#62, leftover drafts
# #56–#64, leftover #147 ApacheSystem, leftover #149
# weapon stations, leftover #152 pilot commands, leftover
# #154 loadout / lock-phase, Harbor IncomingRadar 40/80,
# leftover live copy, FSkyguardMission0NIntegrationReadiness
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
# Isolated-test drafts stay off this lane. AddObjectiveProgress,
# leftover objective-runtime fail-closed / leftover
# objective-runtime survive tests, leftover
# objective-progress defaults #ae90 / leftover
# objective-definition defaults #b29f, GetObjectiveRuntime,
# leftover campaign-save empty-fail-closed, leftover
# campaign-roster lookup #111, leftover
# LoadCampaignProgressAfterConfigure (#290), leftover CPG
# debrief #284/#195/#130/#8ccd, leftover theater-kit #59,
# leftover Harbor #6/#8/#9, leftover flare/HUD #57/#61/#62,
# leftover #147 ApacheSystem, leftover #149 weapon stations,
# leftover #152 pilot commands, leftover #154 loadout /
# lock-phase, and in-flight campaign declaration siblings
# stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_objective_runtime_fail_closed.py",
    "Scripts/tests/test_objective_runtime_empty_fail_closed.py",
    "Scripts/tests/test_objective_runtime_fail_closed_contract.py",
    "Scripts/tests/test_objective_runtime_survive.py",
    "Scripts/tests/test_objective_runtime_survive_fail_closed.py",
    "Scripts/tests/test_objective_runtime_survive_tests.py",
    "Scripts/tests/test_complete_survive_objective_if_intact_decl_contract.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_add_objective_progress_decl_contract.py",
    "Scripts/tests/test_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
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
    "Scripts/tests/test_get_active_mission_decl_contract.py",
    "Scripts/tests/test_get_route_runtime_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_copy_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_campaign_sortie_flow_contract.py",
    "Scripts/tests/test_m09_campaign_handoff_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_gunship_weapon_stations_contract.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
    "Scripts/tests/test_gunship_types_loadout_tests.py",
)
# Neighbors in the same public section. Presence is not locked here.
# AddObjectiveProgress is an in-flight sibling.
# GetObjectiveRuntime is a newly drafted sibling.
# FillResultCombatStats takes leftover ASkyguardGunner*.
UNLOCKED_NEIGHBORS = (
    "bool ConfigureCampaign(USkyguardCampaignDefinition* InCampaign);",
    "bool CanStartMission(FName MissionId) const;",
    "bool StartMission(FName MissionId);",
    "bool AddObjectiveProgress(FName ObjectiveId, int32 Amount = 1);",
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
    "bool SaveCampaignToSlot(",
    "bool LoadCampaignFromSlot(",
    "bool DeleteCampaignSlot(",
    "static bool IsValidCampaignSlotName(const FString& SlotName);",
    "bool IsMissionUnlocked(FName MissionId) const;",
    "int32 GetEarnedCampaignMedals() const;",
    "USkyguardMissionDefinition* GetActiveMission() const",
    "USkyguardObjectiveRuntime* GetObjectiveRuntime() const",
    "USkyguardRouteRuntime* GetRouteRuntime() const",
    "const TMap<FName, FSkyguardMissionSaveRecord>& GetMissionRecords() const",
    "static int32 CalculateMissionScore(",
    "static int32 CalculateMedalTier(",
)
CONFIGURE_NOT_LOCKED = (
    "bool ConfigureCampaign(USkyguardCampaignDefinition* InCampaign);",
)
CAN_START_NOT_LOCKED = (
    "bool CanStartMission(FName MissionId) const;",
)
START_MISSION_NOT_LOCKED = (
    "bool StartMission(FName MissionId);",
)
ADD_OBJECTIVE_PROGRESS_NOT_LOCKED = (
    "bool AddObjectiveProgress(FName ObjectiveId, int32 Amount = 1);",
)
SURVIVE_NOT_LOCKED = (
    "bool CompleteSurviveObjectiveIfIntact(FName ObjectiveId);",
    "test_objective_runtime_survive.py",
    "test_objective_runtime_survive_fail_closed.py",
    "test_complete_survive_objective_if_intact_decl_contract.py",
)
GET_OBJECTIVE_RUNTIME_NOT_LOCKED = (
    "USkyguardObjectiveRuntime* GetObjectiveRuntime() const",
)
UNLOCK_AND_SLOT_NOT_LOCKED = (
    "bool IsMissionUnlocked(FName MissionId) const;",
    "static bool IsValidCampaignSlotName(const FString& SlotName);",
)
SCORE_AND_TIER_NOT_LOCKED = (
    "static int32 CalculateMissionScore(",
    "static int32 CalculateMedalTier(",
)
DEBRIEF_TRAVEL_NOT_LOCKED = (
    "bool AcknowledgeDebrief();",
    "bool CanTravelToNextMission() const;",
    "FString GetNextMissionMapPackageName() const;",
    "bool TravelToNextMission(UObject* WorldContextObject);",
)
FILL_COMBAT_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
)
RUNTIME_NEIGHBORS_NOT_LOCKED = (
    "USkyguardMissionDefinition* GetActiveMission() const",
    "USkyguardRouteRuntime* GetRouteRuntime() const",
)
# Leftover CPG debrief copy #284 / snapshot defaults #195 /
# fail-closed #8ccd / empty-capture #130 stay unlocked.
LEFTOVER_CPG_DEBRIEF_NOT_LOCKED = (
    "SkyguardBuildCpgDebriefCopy",
    "SkyguardCpgCopyHasBannedTerm",
    "SkyguardCaptureCpgDebrief",
    "FSkyguardCpgDebriefSnapshot",
)
# Leftover sibling tokens stay unlocked. Do not require them.
LEFTOVER_SIBLINGS_NOT_LOCKED = (
    "LoadCampaignProgressAfterConfigure",
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeapon",
    "ESkyguardPilotCommand",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "SkyguardCampaignRoster::IndexOf",
    "NumMissions",
)
# Leftover objective-runtime fail-closed / leftover
# objective-runtime survive tests stay unlocked. Do not
# require them and do not treat leftover
# SkyguardObjectiveRuntime.h as this lane's edit surface.
OBJECTIVE_RUNTIME_FAIL_CLOSED_NOT_LOCKED = (
    "SkyguardObjectiveRuntime.h",
    "SkyguardObjectiveRuntime.cpp",
    "test_objective_runtime_fail_closed.py",
    "test_objective_runtime_empty_fail_closed.py",
    "test_route_runtime_fail_closed.py",
)
# Leftover objective-progress defaults #ae90 / leftover
# objective-definition defaults #b29f stay unlocked.
OBJECTIVE_DEFAULTS_NOT_LOCKED = (
    "CurrentProgress = 0;",
    "RequiredProgress = 1;",
    "bFailureEndsMission = false;",
    "ESkyguardMissionObjectiveState::Inactive",
    "FSkyguardObjectiveDefinition",
    "FSkyguardObjectiveProgress",
    "test_objective_progress_defaults_contract.py",
    "test_objective_definition_defaults_contract.py",
)
# .cpp FailObjective body / invented return values stay
# unlocked. Do not invent INDEX_NONE or lock the .cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return nullptr",
    "return INDEX_NONE",
    "return false",
    "return true",
    "return 0",
    "return -1",
    "return ObjectiveRuntime",
    "ObjectiveRuntime &&",
    "ObjectiveRuntime->FailObjective",
    "const FName ObjectiveId",
    "USkyguardCampaignSubsystem::FailObjective",
    "SkyguardCampaignSubsystem.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "ApplyHydraForClusters",
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


class FailObjectiveDeclContractTests(unittest.TestCase):
    def test_campaign_subsystem_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, FAIL_OBJECTIVE_DECL), section)

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
            f"\t{FAIL_OBJECTIVE_DECL}\n"
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
            f"\t{FAIL_OBJECTIVE_DECL}\n"
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
            "\tbool AddObjectiveProgress("
            "FName ObjectiveId, int32 Amount = 1);\n"
            "private:\n"
            f"\t{FAIL_OBJECTIVE_DECL}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, FAIL_OBJECTIVE_DECL)
        self.assertIn("FailObjective", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertNotIn(FAIL_OBJECTIVE_DECL, section)

    def test_missing_fail_objective_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tbool AddObjectiveProgress("
            "FName ObjectiveId, int32 Amount = 1);\n"
            "\tbool CompleteSurviveObjectiveIfIntact("
            "FName ObjectiveId);\n"
            "\tUSkyguardObjectiveRuntime* GetObjectiveRuntime() "
            "const { return ObjectiveRuntime; }\n"
            "\tvoid FillResultCombatStats(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            "\t\tconst ASkyguardGunner* Gunner,\n"
            "\t\tconst UObject* WorldContextObject) const;\n"
            "\tbool AcknowledgeDebrief();\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, FAIL_OBJECTIVE_DECL)
        self.assertIn("FailObjective", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintCallable, Category = "Campaign")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, FAIL_OBJECTIVE_DECL)
        self.assertIn("FailObjective", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tbool AddObjectiveProgress("
            "FName ObjectiveId, int32 Amount = 1);\n"
            "\tbool CompleteSurviveObjectiveIfIntact("
            "FName ObjectiveId);\n"
            "\tUSkyguardObjectiveRuntime* GetObjectiveRuntime() "
            "const { return ObjectiveRuntime; }\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, FAIL_OBJECTIVE_DECL)
        self.assertIn("FailObjective", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_fail_objective_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, FAIL_OBJECTIVE_DECL),
            FAIL_OBJECTIVE_DECL,
        )
        self.assertTrue(has_declaration(section, FAIL_OBJECTIVE_DECL))
        self.assertEqual(declaration_count(section, FAIL_OBJECTIVE_DECL), 1)
        self.assertTrue(FAIL_OBJECTIVE_DECL.endswith(";"), FAIL_OBJECTIVE_DECL)
        self.assertTrue(
            FAIL_OBJECTIVE_DECL.startswith("bool "),
            FAIL_OBJECTIVE_DECL,
        )
        self.assertIn("(FName ObjectiveId)", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("INDEX_NONE", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("return ", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("const", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("{", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("}", FAIL_OBJECTIVE_DECL)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tbool\n"
            "\tFailObjective(FName ObjectiveId);\n"
            "private:\n"
            "};\n"
        )
        wrap_args = (
            "public:\n"
            "\tbool FailObjective(\n"
            "\t\tFName ObjectiveId);\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tbool FailObjective(\n"
            "\tFName\n"
            "\tObjectiveId);\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_type}"
        )
        header_wrap_args = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_args}"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_name}"
        )
        for header in (
            header_wrap_type,
            header_wrap_args,
            header_wrap_name,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, FAIL_OBJECTIVE_DECL),
                section,
            )
            self.assertEqual(
                require_declaration(section, FAIL_OBJECTIVE_DECL),
                FAIL_OBJECTIVE_DECL,
            )
            self.assertEqual(declaration_count(section, FAIL_OBJECTIVE_DECL), 1)
        one_line = f"{{\npublic:\n\t{FAIL_OBJECTIVE_DECL}\n}}\n"
        self.assertTrue(has_declaration(one_line, FAIL_OBJECTIVE_DECL))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, FAIL_OBJECTIVE_DECL), section)
        self.assertEqual(
            require_declaration(section, FAIL_OBJECTIVE_DECL),
            FAIL_OBJECTIVE_DECL,
        )

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(FAIL_OBJECTIVE_DECL.endswith(";"), FAIL_OBJECTIVE_DECL)
        self.assertNotIn("return ", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("INDEX_NONE", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("NAME_None", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("{", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("}", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("return 0", section)
        self.assertNotIn("return -1", section)
        self.assertNotIn("return false", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("return true", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("= INDEX_NONE", section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)

    def test_contract_does_not_relock_add_objective_progress(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        self.assertEqual(
            require_declaration(locked_only, FAIL_OBJECTIVE_DECL),
            FAIL_OBJECTIVE_DECL,
        )
        for neighbor in ADD_OBJECTIVE_PROGRESS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("AddObjectiveProgress", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("AddObjectiveProgress", locked_only)
        self.assertNotIn("Amount = 1", FAIL_OBJECTIVE_DECL)

    def test_contract_does_not_relock_survive_helpers(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for neighbor in SURVIVE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", locked_only)

    def test_contract_does_not_relock_get_objective_runtime(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for neighbor in GET_OBJECTIVE_RUNTIME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("GetObjectiveRuntime", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("USkyguardObjectiveRuntime*", FAIL_OBJECTIVE_DECL)

    def test_contract_does_not_relock_configure_campaign(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for neighbor in CONFIGURE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("ConfigureCampaign", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", FAIL_OBJECTIVE_DECL)

    def test_contract_does_not_relock_can_start_mission(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for neighbor in CAN_START_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("CanStartMission", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("CanStartMission", locked_only)

    def test_contract_does_not_relock_start_mission(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for neighbor in START_MISSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("StartMission", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("StartMission", locked_only)

    def test_contract_does_not_relock_unlock_or_slot_helpers(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for neighbor in UNLOCK_AND_SLOT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("IsMissionUnlocked", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("IsValidCampaignSlotName", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("IsMissionUnlocked", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)

    def test_contract_does_not_relock_score_or_medal_tier(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for neighbor in SCORE_AND_TIER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("CalculateMissionScore", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("CalculateMedalTier", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("GetEarnedCampaignMedals", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("CalculateMissionScore", locked_only)
        self.assertNotIn("CalculateMedalTier", locked_only)

    def test_contract_does_not_relock_debrief_or_travel(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for neighbor in DEBRIEF_TRAVEL_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("AcknowledgeDebrief", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("CanTravelToNextMission", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("GetNextMissionMapPackageName", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("TravelToNextMission", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)

    def test_contract_does_not_relock_fill_result_combat_stats(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for neighbor in FILL_COMBAT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("FillResultCombatStats", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("ASkyguardGunner", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)

    def test_contract_does_not_relock_get_route_or_active_mission(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for neighbor in RUNTIME_NEIGHBORS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("GetActiveMission", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("GetRouteRuntime", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("GetActiveMission", locked_only)
        self.assertNotIn("GetRouteRuntime", locked_only)

    def test_contract_does_not_relock_leftover_objective_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for token in OBJECTIVE_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("SkyguardObjectiveRuntime.h", LOCKED)
        self.assertNotIn("SkyguardObjectiveRuntime.cpp", LOCKED)
        self.assertNotIn("SkyguardObjectiveRuntime.h", locked_only)
        self.assertNotIn("SkyguardRouteRuntime.h", locked_only)

    def test_contract_does_not_relock_leftover_objective_defaults(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for token in OBJECTIVE_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("CurrentProgress", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("RequiredProgress", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("bFailureEndsMission", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("FSkyguardObjectiveDefinition", locked_only)
        self.assertNotIn("FSkyguardObjectiveProgress", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for token in LEFTOVER_SIBLINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("LoadCampaignProgressAfterConfigure", locked_only)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn("ESkyguardGunshipWeapon", locked_only)
        self.assertNotIn("ESkyguardPilotCommand", locked_only)
        self.assertNotIn("ESkyguardGuidedLockPhase", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        self.assertEqual(
            require_declaration(locked_only, FAIL_OBJECTIVE_DECL),
            FAIL_OBJECTIVE_DECL,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("AddObjectiveProgress", locked_only)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", locked_only)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)
        self.assertNotIn("IsMissionUnlocked", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)
        self.assertNotIn("CalculateMissionScore", locked_only)
        self.assertNotIn("CalculateMedalTier", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)
        self.assertNotIn("GetActiveMission", locked_only)
        self.assertNotIn("GetRouteRuntime", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("UPROPERTY(Transient)", section)
        self.assertNotIn("MissionStartWorldTimeSeconds", section)
        self.assertNotIn("ClearActiveMissionRuntime", section)
        self.assertNotIn("BuildSuccessDebrief", section)
        self.assertNotIn("BuildFailureDebrief", section)
        self.assertNotIn("TObjectPtr<USkyguardObjectiveRuntime>", section)
        self.assertEqual(
            require_declaration(section, FAIL_OBJECTIVE_DECL),
            FAIL_OBJECTIVE_DECL,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::FailObjective",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::FailObjective",
            section,
        )
        self.assertNotIn("ObjectiveRuntime->FailObjective", section)
        self.assertNotIn("ObjectiveRuntime &&", section)
        self.assertNotIn("return false", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("return true", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("return INDEX_NONE", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("INDEX_NONE", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("{", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("}", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("const FName ObjectiveId", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("const FName ObjectiveId", section)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_contract_does_not_require_banned_live_copy(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(FAIL_OBJECTIVE_DECL, "Rifle")
        self.assertNotEqual(FAIL_OBJECTIVE_DECL, "Igla")
        self.assertNotIn("FireIgla", section)
        self.assertNotIn("FireRifle", section)
        self.assertNotIn("YakSpawnLocation", section)
        self.assertNotIn("bYakRuntimeReady", section)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_live_copy_terms(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FailObjective contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not leftover live copy",
            )
            self.assertNotIn(banned, FAIL_OBJECTIVE_DECL.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", FAIL_OBJECTIVE_DECL)

    def test_contract_is_fail_objective_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, FAIL_OBJECTIVE_DECL),
            FAIL_OBJECTIVE_DECL,
        )
        locked_only = f"{FAIL_OBJECTIVE_DECL}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FAIL_OBJECTIVE_DECL)
        self.assertNotIn("AddObjectiveProgress", locked_only)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", locked_only)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)
        self.assertNotIn("IsMissionUnlocked", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)
        self.assertNotIn("CalculateMissionScore", locked_only)
        self.assertNotIn("CalculateMedalTier", locked_only)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)
        self.assertNotIn("GetActiveMission", locked_only)
        self.assertNotIn("GetRouteRuntime", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        for token in LEFTOVER_SIBLINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
        for token in OBJECTIVE_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
        for token in OBJECTIVE_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
        for token in SURVIVE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, section)
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, FAIL_OBJECTIVE_DECL)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("INDEX_NONE", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("return ", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("{", FAIL_OBJECTIVE_DECL)
        self.assertNotIn("SkyguardObjectiveRuntime.h", LOCKED)
        self.assertNotEqual(FAIL_OBJECTIVE_DECL, "Rifle")
        self.assertNotEqual(FAIL_OBJECTIVE_DECL, "Igla")
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertNotIn("bYakRuntimeReady", section)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)
        self.assertNotIn("ObjectiveRuntime->FailObjective", section)
        self.assertNotIn("const FName ObjectiveId", FAIL_OBJECTIVE_DECL)

    def test_locked_scripts_list_leftover_objective_and_roster_siblings(
        self,
    ) -> None:
        scripts = "\n".join(LOCKED_SCRIPTS)
        self.assertIn("test_objective_runtime_fail_closed.py", scripts)
        self.assertIn("test_objective_runtime_survive.py", scripts)
        self.assertIn("test_objective_progress_defaults_contract.py", scripts)
        self.assertIn("test_objective_definition_defaults_contract.py", scripts)
        self.assertIn("test_get_objective_runtime_decl_contract.py", scripts)
        self.assertIn("test_add_objective_progress_decl_contract.py", scripts)
        self.assertIn("test_campaign_save_empty_fail_closed.py", scripts)
        self.assertIn("test_campaign_roster_lookup_contract.py", scripts)
        self.assertIn("test_campaign_roster_lookup_tests.py", scripts)
        self.assertIn("test_campaign_roster_contract.py", scripts)
        self.assertIn("test_campaign_load_progress_decl_contract.py", scripts)

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
