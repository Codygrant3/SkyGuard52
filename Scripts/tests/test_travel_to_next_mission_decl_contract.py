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
# values, or the TravelToNextMission body in the .cpp.
TRAVEL_TO_NEXT_MISSION = (
    "bool TravelToNextMission(UObject* WorldContextObject);"
)
# Leftover #56–#64 plus CampaignSubsystem production files.
# This lane only adds an isolated Python TravelToNextMission
# declaration contract. Stay off CanTravelToNextMission /
# GetNextMissionMapPackageName (newly drafted siblings),
# GetActiveMission (in-flight sibling), GetObjectiveRuntime
# (in-flight sibling), AcknowledgeDebrief #308, leftover CPG
# debrief #284/#195/#130/#8ccd, FillResultCombatStats (takes
# leftover ASkyguardGunner*), leftover campaign-save
# empty-fail-closed drafts, leftover campaign-roster lookup
# #111, leftover LoadCampaignProgressAfterConfigure (#290),
# leftover Harbor #6/#8/#9, leftover theater-kit #59,
# leftover flare/HUD #57/#61/#62, leftover drafts #56–#64,
# leftover #147 ApacheSystem, leftover #149 weapon stations,
# leftover #152 pilot commands, leftover #154 loadout /
# lock-phase, leftover objective-runtime fail-closed /
# leftover route-runtime fail-closed, Harbor IncomingRadar
# 40/80, live-copy leftovers, FSkyguardMission0NIntegrationReadiness
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
# Isolated-test drafts stay off this lane. Leftover
# campaign-save empty-fail-closed, leftover campaign-roster
# lookup #111, leftover LoadCampaignProgressAfterConfigure
# (#290), leftover CPG debrief #284/#195/#130/#8ccd,
# leftover theater-kit #59, leftover Harbor #6/#8/#9,
# leftover flare/HUD #57/#61/#62, leftover #147
# ApacheSystem, leftover #149 weapon stations, leftover
# #152 pilot commands, leftover #154 loadout/lock-phase,
# leftover objective-runtime fail-closed, leftover
# route-runtime fail-closed, and newly drafted / in-flight
# campaign declaration siblings stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
    "Scripts/tests/test_can_travel_to_next_mission_decl_contract.py",
    "Scripts/tests/test_get_next_mission_map_package_name_decl_contract.py",
    "Scripts/tests/test_get_active_mission_decl_contract.py",
    "Scripts/tests/test_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_acknowledge_debrief_decl_contract.py",
    "Scripts/tests/test_configure_campaign_decl_contract.py",
    "Scripts/tests/test_can_start_mission_decl_contract.py",
    "Scripts/tests/test_start_mission_decl_contract.py",
    "Scripts/tests/test_is_mission_unlocked_decl_contract.py",
    "Scripts/tests/test_is_valid_campaign_slot_name_decl_contract.py",
    "Scripts/tests/test_get_earned_campaign_medals_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_copy_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed.py",
    "Scripts/tests/test_objective_runtime_fail_closed.py",
    "Scripts/tests/test_route_runtime_fail_closed.py",
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
# CanTravelToNextMission / GetNextMissionMapPackageName are
# newly drafted siblings. GetActiveMission / GetObjectiveRuntime
# are in-flight siblings. AcknowledgeDebrief is #308.
# FillResultCombatStats takes leftover ASkyguardGunner*.
UNLOCKED_NEIGHBORS = (
    "bool ConfigureCampaign(USkyguardCampaignDefinition* InCampaign);",
    "bool CanStartMission(FName MissionId) const;",
    "bool StartMission(FName MissionId);",
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
    "static int32 CalculateMissionScore(",
    "static int32 CalculateMedalTier(",
)
CAN_TRAVEL_NOT_LOCKED = (
    "bool CanTravelToNextMission() const;",
)
NEXT_MAP_NOT_LOCKED = (
    "FString GetNextMissionMapPackageName() const;",
)
ACTIVE_MISSION_NOT_LOCKED = (
    "USkyguardMissionDefinition* GetActiveMission() const",
)
OBJECTIVE_RUNTIME_NOT_LOCKED = (
    "USkyguardObjectiveRuntime* GetObjectiveRuntime() const",
)
ACKNOWLEDGE_NOT_LOCKED = (
    "bool AcknowledgeDebrief();",
)
FILL_COMBAT_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
)
DEBRIEF_LEFTOVER_NOT_LOCKED = (
    "SkyguardBuildCpgDebriefCopy",
    "FSkyguardCpgDebriefSnapshot",
    "const FSkyguardMissionDebrief& GetLastDebrief() const",
)
# Leftover sibling tokens stay unlocked. Do not require them.
LEFTOVER_SIBLINGS_NOT_LOCKED = (
    "LoadCampaignProgressAfterConfigure",
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "SkyguardCampaignRoster::IndexOf",
    "NumMissions",
    "SkyguardCampaignSaveGameEmptyFailClosedTests",
    "SkyguardCampaignRosterLookupTests",
    "SkyguardObjectiveRuntimeFailClosedTests",
    "SkyguardRouteRuntimeFailClosedTests",
)
# .cpp TravelToNextMission body / invented return values
# stay unlocked. Do not invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return 0",
    "return -1",
    "return false",
    "return true",
    "UGameplayStatics::OpenLevel",
    "OpenLevel(",
    "if (!WorldContextObject || !CanTravelToNextMission())",
    "FName(*GetNextMissionMapPackageName())",
    "USkyguardCampaignSubsystem::TravelToNextMission",
    "SkyguardCampaignSubsystem.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "ASkyguardIglaMissile",
    "ApplyHydraForClusters",
    "SkyguardBuildCpgDebriefCopy",
    "FSkyguardCpgDebriefSnapshot",
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


class TravelToNextMissionDeclContractTests(unittest.TestCase):
    def test_campaign_subsystem_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, TRAVEL_TO_NEXT_MISSION), section)

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
            f"\t{TRAVEL_TO_NEXT_MISSION}\n"
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
            f"\t{TRAVEL_TO_NEXT_MISSION}\n"
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
            "\tbool CanTravelToNextMission() const;\n"
            "private:\n"
            f"\t{TRAVEL_TO_NEXT_MISSION}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, TRAVEL_TO_NEXT_MISSION)
        self.assertIn("TravelToNextMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertNotIn(TRAVEL_TO_NEXT_MISSION, section)

    def test_missing_travel_to_next_mission_declaration_fails_closed(
        self,
    ) -> None:
        neighbors_only = (
            "\tbool ConfigureCampaign("
            "USkyguardCampaignDefinition* InCampaign);\n"
            "\tbool CanStartMission(FName MissionId) const;\n"
            "\tbool StartMission(FName MissionId);\n"
            "\tbool AcknowledgeDebrief();\n"
            "\tbool CanTravelToNextMission() const;\n"
            "\tFString GetNextMissionMapPackageName() const;\n"
            "\tbool IsMissionUnlocked(FName MissionId) const;\n"
            "\tUSkyguardMissionDefinition* GetActiveMission() const "
            "{ return ActiveMission; }\n"
            "\tUSkyguardObjectiveRuntime* GetObjectiveRuntime() const "
            "{ return ObjectiveRuntime; }\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, TRAVEL_TO_NEXT_MISSION)
        self.assertIn("TravelToNextMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintCallable, Category = "Campaign|Sortie",\n'
            '\t\tmeta = (WorldContext = "WorldContextObject"))\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, TRAVEL_TO_NEXT_MISSION)
        self.assertIn("TravelToNextMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_travel_to_next_mission_declaration_matches_origin_main(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, TRAVEL_TO_NEXT_MISSION),
            TRAVEL_TO_NEXT_MISSION,
        )
        self.assertTrue(has_declaration(section, TRAVEL_TO_NEXT_MISSION))
        self.assertEqual(declaration_count(section, TRAVEL_TO_NEXT_MISSION), 1)
        self.assertTrue(
            TRAVEL_TO_NEXT_MISSION.endswith(";"),
            TRAVEL_TO_NEXT_MISSION,
        )
        self.assertTrue(
            TRAVEL_TO_NEXT_MISSION.startswith("bool "),
            TRAVEL_TO_NEXT_MISSION,
        )
        self.assertIn(
            "(UObject* WorldContextObject);",
            TRAVEL_TO_NEXT_MISSION,
        )
        self.assertNotIn("INDEX_NONE", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("return ", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("{", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("}", TRAVEL_TO_NEXT_MISSION)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tbool\n"
            "\tTravelToNextMission(UObject* WorldContextObject);\n"
            "private:\n"
            "};\n"
        )
        wrap_args = (
            "public:\n"
            "\tbool TravelToNextMission(\n"
            "\tUObject* WorldContextObject);\n"
            "private:\n"
            "};\n"
        )
        wrap_pointer = (
            "public:\n"
            "\tbool TravelToNextMission(UObject*\n"
            "\tWorldContextObject);\n"
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
        header_wrap_pointer = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_pointer}"
        )
        for header in (
            header_wrap_type,
            header_wrap_args,
            header_wrap_pointer,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, TRAVEL_TO_NEXT_MISSION),
                section,
            )
            self.assertEqual(
                require_declaration(section, TRAVEL_TO_NEXT_MISSION),
                TRAVEL_TO_NEXT_MISSION,
            )
            self.assertEqual(
                declaration_count(section, TRAVEL_TO_NEXT_MISSION),
                1,
            )
        one_line = f"{{\npublic:\n\t{TRAVEL_TO_NEXT_MISSION}\n}}\n"
        self.assertTrue(has_declaration(one_line, TRAVEL_TO_NEXT_MISSION))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, TRAVEL_TO_NEXT_MISSION), section)
        self.assertEqual(
            require_declaration(section, TRAVEL_TO_NEXT_MISSION),
            TRAVEL_TO_NEXT_MISSION,
        )

    def test_declaration_does_not_invent_index_none_or_cpp_body(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(
            TRAVEL_TO_NEXT_MISSION.endswith(";"),
            TRAVEL_TO_NEXT_MISSION,
        )
        self.assertNotIn("return ", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("INDEX_NONE", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("NAME_None", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("{", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("}", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("return 0", section)
        self.assertNotIn("return -1", section)
        self.assertNotIn("UGameplayStatics::OpenLevel", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("OpenLevel(", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("= INDEX_NONE", section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, TRAVEL_TO_NEXT_MISSION)

    def test_contract_does_not_relock_can_travel_to_next_mission(self) -> None:
        locked_only = f"{TRAVEL_TO_NEXT_MISSION}\n"
        self.assertEqual(
            require_declaration(locked_only, TRAVEL_TO_NEXT_MISSION),
            TRAVEL_TO_NEXT_MISSION,
        )
        for neighbor in CAN_TRAVEL_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("CanTravelToNextMission", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("CanTravelToNextMission", locked_only)

    def test_contract_does_not_relock_next_map_package_name(self) -> None:
        locked_only = f"{TRAVEL_TO_NEXT_MISSION}\n"
        for neighbor in NEXT_MAP_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn(
            "GetNextMissionMapPackageName",
            TRAVEL_TO_NEXT_MISSION,
        )
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)

    def test_contract_does_not_relock_active_mission(self) -> None:
        locked_only = f"{TRAVEL_TO_NEXT_MISSION}\n"
        for neighbor in ACTIVE_MISSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("GetActiveMission", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("GetActiveMission", locked_only)

    def test_contract_does_not_relock_objective_runtime(self) -> None:
        locked_only = f"{TRAVEL_TO_NEXT_MISSION}\n"
        for neighbor in OBJECTIVE_RUNTIME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("GetObjectiveRuntime", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("GetRouteRuntime", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("GetRouteRuntime", locked_only)

    def test_contract_does_not_relock_acknowledge_debrief(self) -> None:
        locked_only = f"{TRAVEL_TO_NEXT_MISSION}\n"
        for neighbor in ACKNOWLEDGE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("AcknowledgeDebrief", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("AcknowledgeDebrief", locked_only)

    def test_contract_does_not_relock_fill_result_combat_stats(self) -> None:
        locked_only = f"{TRAVEL_TO_NEXT_MISSION}\n"
        for neighbor in FILL_COMBAT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("FillResultCombatStats", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("ASkyguardGunner", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief(self) -> None:
        locked_only = f"{TRAVEL_TO_NEXT_MISSION}\n"
        for token in DEBRIEF_LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)
        self.assertNotIn("GetLastDebrief", locked_only)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{TRAVEL_TO_NEXT_MISSION}\n"
        for token in LEFTOVER_SIBLINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("LoadCampaignProgressAfterConfigure", locked_only)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn("ESkyguardGunshipWeaponStation", locked_only)
        self.assertNotIn("ESkyguardPilotCommand", locked_only)
        self.assertNotIn("ESkyguardLoadout", locked_only)
        self.assertNotIn("ESkyguardGuidedLockPhase", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("SkyguardObjectiveRuntimeFailClosedTests", locked_only)
        self.assertNotIn("SkyguardRouteRuntimeFailClosedTests", locked_only)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{TRAVEL_TO_NEXT_MISSION}\n"
        self.assertEqual(
            require_declaration(locked_only, TRAVEL_TO_NEXT_MISSION),
            TRAVEL_TO_NEXT_MISSION,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)
        self.assertNotIn("IsMissionUnlocked", locked_only)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("GetActiveMission", locked_only)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("LoadCampaignProgressAfterConfigure", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("UPROPERTY(Transient)", section)
        self.assertNotIn("MissionStartWorldTimeSeconds", section)
        self.assertNotIn("ClearActiveMissionRuntime", section)
        self.assertNotIn("BuildSuccessDebrief", section)
        self.assertNotIn("BuildFailureDebrief", section)
        self.assertEqual(
            require_declaration(section, TRAVEL_TO_NEXT_MISSION),
            TRAVEL_TO_NEXT_MISSION,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn("UGameplayStatics::OpenLevel", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::TravelToNextMission",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::TravelToNextMission",
            section,
        )
        self.assertNotIn("UGameplayStatics::OpenLevel", section)
        self.assertNotIn("OpenLevel(", section)
        self.assertNotIn(
            "if (!WorldContextObject || !CanTravelToNextMission())",
            TRAVEL_TO_NEXT_MISSION,
        )
        self.assertNotIn(
            "FName(*GetNextMissionMapPackageName())",
            TRAVEL_TO_NEXT_MISSION,
        )
        self.assertNotIn("INDEX_NONE", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("{", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("}", TRAVEL_TO_NEXT_MISSION)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, TRAVEL_TO_NEXT_MISSION)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(TRAVEL_TO_NEXT_MISSION, "Rifle")
        self.assertNotEqual(TRAVEL_TO_NEXT_MISSION, "Igla")
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
                f"TravelToNextMission contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, TRAVEL_TO_NEXT_MISSION.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", TRAVEL_TO_NEXT_MISSION)

    def test_contract_is_travel_to_next_mission_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, TRAVEL_TO_NEXT_MISSION),
            TRAVEL_TO_NEXT_MISSION,
        )
        locked_only = f"{TRAVEL_TO_NEXT_MISSION}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)
        self.assertNotIn("IsMissionUnlocked", locked_only)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("GetActiveMission", locked_only)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)
        self.assertNotIn("SkyguardObjectiveRuntimeFailClosedTests", locked_only)
        self.assertNotIn("SkyguardRouteRuntimeFailClosedTests", locked_only)
        for token in LEFTOVER_SIBLINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, TRAVEL_TO_NEXT_MISSION)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, section)
            self.assertNotIn(token, TRAVEL_TO_NEXT_MISSION)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, TRAVEL_TO_NEXT_MISSION)
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
        self.assertNotIn("INDEX_NONE", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("return ", TRAVEL_TO_NEXT_MISSION)
        self.assertNotIn("{", TRAVEL_TO_NEXT_MISSION)
        self.assertNotEqual(TRAVEL_TO_NEXT_MISSION, "Rifle")
        self.assertNotEqual(TRAVEL_TO_NEXT_MISSION, "Igla")
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
