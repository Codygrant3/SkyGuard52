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
# values, or the CanStartMission body. Unknown-mission return
# stays unlocked; do not invent INDEX_NONE for it.
CAN_START_MISSION = "bool CanStartMission(FName MissionId) const;"
CAN_START_MISSION_NAME = "bool CanStartMission("
PARAMETER_LIST = ("FName MissionId",)
# Leftover #56–#64 plus CampaignSubsystem production files.
# This lane only adds an isolated Python CanStartMission
# declaration contract. Stay off leftover Harbor #6/#8/#9,
# leftover theater-kit #59, leftover flare/HUD #57/#61/#62,
# leftover drafts #56–#64, leftover #147 ApacheSystem,
# leftover #149 weapon stations, leftover #152 pilot
# commands, leftover #154 loadout/lock-phase, leftover
# campaign-save empty-fail-closed drafts, leftover
# campaign-roster lookup #111, LoadCampaignProgressAfterConfigure
# (#290), Yak/Igla live copy, and dirty D:\Skyguard52.
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
# lookup, leftover LoadCampaignProgressAfterConfigure, and
# leftover theater-kit / Harbor / flare/HUD stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
    "Scripts/tests/test_configure_campaign_decl_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_campaign_sortie_flow_contract.py",
    "Scripts/tests/test_m09_campaign_handoff_contract.py",
)
# Neighbors in the same public section. Presence is not locked here.
# ConfigureCampaign is an in-flight sibling. FillResultCombatStats
# takes leftover ASkyguardGunner*.
UNLOCKED_NEIGHBORS = (
    "bool ConfigureCampaign(USkyguardCampaignDefinition* InCampaign);",
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
    "bool TravelToNextMission(UObject* WorldContextObject);",
    "bool ApplySaveGame(const USkyguardCampaignSaveGame* SaveGame);",
    "USkyguardCampaignSaveGame* BuildSaveGame() const;",
    "bool SaveCampaignToSlot(",
    "bool LoadCampaignFromSlot(",
    "bool DeleteCampaignSlot(",
    "static bool IsValidCampaignSlotName(const FString& SlotName);",
)
CONFIGURE_NOT_LOCKED = (
    "bool ConfigureCampaign(USkyguardCampaignDefinition* InCampaign);",
)
START_AND_OBJECTIVES_NOT_LOCKED = (
    "bool StartMission(FName MissionId);",
    "bool AddObjectiveProgress(FName ObjectiveId, int32 Amount = 1);",
    "bool FailObjective(FName ObjectiveId);",
    "bool CompleteSurviveObjectiveIfIntact(FName ObjectiveId);",
)
ACTIVE_MISSION_NOT_LOCKED = (
    "bool CompleteActiveMission(FSkyguardMissionResult& InOutResult);",
    "bool FinalizeActiveMission(",
    "bool FailActiveMission(",
)
COMBAT_AND_DEBRIEF_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
    "float GetActiveMissionElapsedSeconds(",
    "bool RetrySaveLastDebrief(",
    "bool AcknowledgeDebrief();",
    "const FSkyguardMissionDebrief& GetLastDebrief() const",
)
TRAVEL_NOT_LOCKED = (
    "bool CanTravelToNextMission() const;",
    "FString GetNextMissionMapPackageName() const;",
    "bool TravelToNextMission(UObject* WorldContextObject);",
)
SAVE_GAME_NOT_LOCKED = (
    "bool ApplySaveGame(const USkyguardCampaignSaveGame* SaveGame);",
    "USkyguardCampaignSaveGame* BuildSaveGame() const;",
    "bool SaveCampaignToSlot(",
    "bool LoadCampaignFromSlot(",
    "bool DeleteCampaignSlot(",
    "static bool IsValidCampaignSlotName(const FString& SlotName);",
)
# Leftover #147 / #149 / #152 / #154 / #290 / Hydra cluster
# apply stay unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "LoadCampaignProgressAfterConfigure",
)
# .cpp CanStartMission body / invented return values stay unlocked.
# Do not invent INDEX_NONE as the unknown-mission return.
CPP_AND_INVENTED = (
    "return IsMissionUnlocked",
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return 0",
    "return -1",
    "const FName MissionId",
    "USkyguardCampaignSubsystem::CanStartMission",
    "SkyguardCampaignSubsystem.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "USkyguardCampaignSaveGame",
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


class CanStartMissionDeclContractTests(unittest.TestCase):
    def test_campaign_subsystem_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, CAN_START_MISSION), section)

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
            f"\t{CAN_START_MISSION}\n"
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
            f"\t{CAN_START_MISSION}\n"
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
            "\tbool ConfigureCampaign("
            "USkyguardCampaignDefinition* InCampaign);\n"
            "private:\n"
            f"\t{CAN_START_MISSION}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, CAN_START_MISSION)
        self.assertIn("CanStartMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertNotIn(CAN_START_MISSION, section)

    def test_missing_can_start_mission_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tbool ConfigureCampaign("
            "USkyguardCampaignDefinition* InCampaign);\n"
            "\tbool StartMission(FName MissionId);\n"
            "\tbool AddObjectiveProgress("
            "FName ObjectiveId, int32 Amount = 1);\n"
            "\tbool FailObjective(FName ObjectiveId);\n"
            "\tbool CompleteSurviveObjectiveIfIntact("
            "FName ObjectiveId);\n"
            "\tbool CompleteActiveMission("
            "FSkyguardMissionResult& InOutResult);\n"
            "\tvoid FillResultCombatStats(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            "\t\tconst ASkyguardGunner* Gunner,\n"
            "\t\tconst UObject* WorldContextObject) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, CAN_START_MISSION)
        self.assertIn("CanStartMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintPure, Category = "Campaign")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, CAN_START_MISSION)
        self.assertIn("CanStartMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_parameter_list_fails_closed(self) -> None:
        name_only = "\tbool CanStartMission() const;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(name_only, CAN_START_MISSION)
        self.assertIn("CanStartMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_can_start_mission_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, CAN_START_MISSION),
            CAN_START_MISSION,
        )
        self.assertTrue(has_declaration(section, CAN_START_MISSION))
        self.assertEqual(declaration_count(section, CAN_START_MISSION), 1)
        self.assertTrue(CAN_START_MISSION.endswith(";"), CAN_START_MISSION)
        self.assertIn(CAN_START_MISSION_NAME, CAN_START_MISSION)
        for parameter in PARAMETER_LIST:
            self.assertIn(parameter, CAN_START_MISSION)
            self.assertTrue(has_declaration(section, parameter), section)
        self.assertNotIn("INDEX_NONE", CAN_START_MISSION)
        self.assertNotIn("return ", CAN_START_MISSION)
        self.assertTrue(CAN_START_MISSION.startswith("bool "), CAN_START_MISSION)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tbool\n"
            "\tCanStartMission(FName MissionId) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_args = (
            "public:\n"
            "\tbool CanStartMission(\n"
            "\t\tFName MissionId) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tbool CanStartMission(FName MissionId)\n"
            "\tconst;\n"
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
        header_wrap_const = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_const}"
        )
        for header in (
            header_wrap_type,
            header_wrap_args,
            header_wrap_const,
        ):
            section = public_section(header)
            self.assertTrue(has_declaration(section, CAN_START_MISSION), section)
            self.assertEqual(
                require_declaration(section, CAN_START_MISSION),
                CAN_START_MISSION,
            )
            self.assertEqual(declaration_count(section, CAN_START_MISSION), 1)
        one_line = f"{{\npublic:\n\t{CAN_START_MISSION}\n}}\n"
        self.assertTrue(has_declaration(one_line, CAN_START_MISSION))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, CAN_START_MISSION), section)
        self.assertEqual(
            require_declaration(section, CAN_START_MISSION),
            CAN_START_MISSION,
        )
        for parameter in PARAMETER_LIST:
            self.assertTrue(has_declaration(wrap_args, parameter), wrap_args)
            self.assertTrue(has_declaration(section, parameter), section)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(CAN_START_MISSION.endswith(";"), CAN_START_MISSION)
        self.assertTrue(CAN_START_MISSION.startswith("bool "), CAN_START_MISSION)
        self.assertNotIn("return ", CAN_START_MISSION)
        self.assertNotIn("INDEX_NONE", CAN_START_MISSION)
        self.assertNotIn("NAME_None", CAN_START_MISSION)
        self.assertNotIn("{", CAN_START_MISSION)
        self.assertNotIn("}", CAN_START_MISSION)
        self.assertNotIn("const FName MissionId", CAN_START_MISSION)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("return IsMissionUnlocked", section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CAN_START_MISSION)

    def test_contract_does_not_invent_index_none_as_unknown_mission_return(
        self,
    ) -> None:
        locked_only = f"{CAN_START_MISSION}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", CAN_START_MISSION)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("return INDEX_NONE", CAN_START_MISSION)
        self.assertNotIn("unknown-mission", CAN_START_MISSION.lower())
        self.assertNotIn("return false", CAN_START_MISSION)
        self.assertNotIn("return true", CAN_START_MISSION)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)

    def test_contract_does_not_lock_can_start_mission_cpp_body(self) -> None:
        locked_only = f"{CAN_START_MISSION}\n"
        self.assertNotIn("return IsMissionUnlocked", locked_only)
        self.assertNotIn("return IsMissionUnlocked", CAN_START_MISSION)
        self.assertNotIn("const FName MissionId", CAN_START_MISSION)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::CanStartMission",
            CAN_START_MISSION,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", CAN_START_MISSION)
        self.assertNotIn("{", CAN_START_MISSION)
        self.assertNotIn("}", CAN_START_MISSION)
        section = public_section(origin_main_header())
        self.assertNotIn("return IsMissionUnlocked", section)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::CanStartMission",
            section,
        )

    def test_contract_does_not_relock_configure_campaign(self) -> None:
        locked_only = f"{CAN_START_MISSION}\n"
        for neighbor in CONFIGURE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAN_START_MISSION)
        self.assertNotIn("ConfigureCampaign", CAN_START_MISSION)
        self.assertNotIn("ConfigureCampaign", locked_only)

    def test_contract_does_not_relock_start_or_objectives(self) -> None:
        locked_only = f"{CAN_START_MISSION}\n"
        for neighbor in START_AND_OBJECTIVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAN_START_MISSION)
        self.assertNotIn("bool StartMission(FName MissionId);", CAN_START_MISSION)
        self.assertNotIn("AddObjectiveProgress", CAN_START_MISSION)
        self.assertNotIn("FailObjective", CAN_START_MISSION)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", CAN_START_MISSION)
        self.assertNotIn("bool StartMission(FName MissionId);", locked_only)
        self.assertNotIn("AddObjectiveProgress", locked_only)
        self.assertNotIn("FailObjective", locked_only)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", locked_only)

    def test_contract_does_not_relock_active_mission_helpers(self) -> None:
        locked_only = f"{CAN_START_MISSION}\n"
        for neighbor in ACTIVE_MISSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAN_START_MISSION)
        self.assertNotIn("CompleteActiveMission", CAN_START_MISSION)
        self.assertNotIn("FinalizeActiveMission", CAN_START_MISSION)
        self.assertNotIn("FailActiveMission", CAN_START_MISSION)
        self.assertNotIn("CompleteActiveMission", locked_only)
        self.assertNotIn("FinalizeActiveMission", locked_only)
        self.assertNotIn("FailActiveMission", locked_only)

    def test_contract_does_not_relock_combat_or_debrief(self) -> None:
        locked_only = f"{CAN_START_MISSION}\n"
        for neighbor in COMBAT_AND_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAN_START_MISSION)
        self.assertNotIn("FillResultCombatStats", CAN_START_MISSION)
        self.assertNotIn("ASkyguardGunner", CAN_START_MISSION)
        self.assertNotIn("GetActiveMissionElapsedSeconds", CAN_START_MISSION)
        self.assertNotIn("RetrySaveLastDebrief", CAN_START_MISSION)
        self.assertNotIn("AcknowledgeDebrief", CAN_START_MISSION)
        self.assertNotIn("GetLastDebrief", CAN_START_MISSION)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("GetActiveMissionElapsedSeconds", locked_only)
        self.assertNotIn("RetrySaveLastDebrief", locked_only)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("GetLastDebrief", locked_only)

    def test_contract_does_not_relock_travel_helpers(self) -> None:
        locked_only = f"{CAN_START_MISSION}\n"
        for neighbor in TRAVEL_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAN_START_MISSION)
        self.assertNotIn("CanTravelToNextMission", CAN_START_MISSION)
        self.assertNotIn("GetNextMissionMapPackageName", CAN_START_MISSION)
        self.assertNotIn("TravelToNextMission", CAN_START_MISSION)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)

    def test_contract_does_not_relock_save_game_helpers(self) -> None:
        locked_only = f"{CAN_START_MISSION}\n"
        for neighbor in SAVE_GAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAN_START_MISSION)
        self.assertNotIn("ApplySaveGame", CAN_START_MISSION)
        self.assertNotIn("BuildSaveGame", CAN_START_MISSION)
        self.assertNotIn("SaveCampaignToSlot", CAN_START_MISSION)
        self.assertNotIn("LoadCampaignFromSlot", CAN_START_MISSION)
        self.assertNotIn("DeleteCampaignSlot", CAN_START_MISSION)
        self.assertNotIn("IsValidCampaignSlotName", CAN_START_MISSION)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("BuildSaveGame", locked_only)
        self.assertNotIn("SaveCampaignToSlot", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{CAN_START_MISSION}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAN_START_MISSION)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{CAN_START_MISSION}\n"
        self.assertEqual(
            require_declaration(locked_only, CAN_START_MISSION),
            CAN_START_MISSION,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAN_START_MISSION)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("bool StartMission(FName MissionId);", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("LoadCampaignProgressAfterConfigure", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

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
            require_declaration(section, CAN_START_MISSION),
            CAN_START_MISSION,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn("return IsMissionUnlocked", section)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CAN_START_MISSION)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::CanStartMission",
            section,
        )
        self.assertNotIn("return IsMissionUnlocked", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", CAN_START_MISSION)
        self.assertNotIn("}", CAN_START_MISSION)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, CAN_START_MISSION)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, CAN_START_MISSION)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(CAN_START_MISSION, "Rifle")
        self.assertNotEqual(CAN_START_MISSION, "Igla")
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
                f"campaign CanStartMission contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, CAN_START_MISSION.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", CAN_START_MISSION)

    def test_contract_is_can_start_mission_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, CAN_START_MISSION),
            CAN_START_MISSION,
        )
        locked_only = f"{CAN_START_MISSION}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAN_START_MISSION)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("bool StartMission(FName MissionId);", locked_only)
        self.assertNotIn("AddObjectiveProgress", locked_only)
        self.assertNotIn("FailObjective", locked_only)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", locked_only)
        self.assertNotIn("CompleteActiveMission", locked_only)
        self.assertNotIn("FinalizeActiveMission", locked_only)
        self.assertNotIn("FailActiveMission", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("GetActiveMissionElapsedSeconds", locked_only)
        self.assertNotIn("RetrySaveLastDebrief", locked_only)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("GetLastDebrief", locked_only)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("BuildSaveGame", locked_only)
        self.assertNotIn("SaveCampaignToSlot", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAN_START_MISSION)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, CAN_START_MISSION)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CAN_START_MISSION)
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
        self.assertNotIn("return ", CAN_START_MISSION)
        self.assertNotIn("const FName MissionId", CAN_START_MISSION)
        self.assertNotEqual(CAN_START_MISSION, "Rifle")
        self.assertNotEqual(CAN_START_MISSION, "Igla")
        for parameter in PARAMETER_LIST:
            self.assertIn(parameter, CAN_START_MISSION)

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
