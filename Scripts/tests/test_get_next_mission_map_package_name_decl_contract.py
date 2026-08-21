from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardCampaignSubsystem.h"
CLASS_NAME = "USkyguardCampaignSubsystem"
# Declaration presence only. Do not invent INDEX_NONE, a map
# package name return, or the GetNextMissionMapPackageName
# body in the .cpp.
GET_NEXT_MAP_DECL = "FString GetNextMissionMapPackageName() const;"
# Leftover #56–#64 plus CampaignSubsystem production files.
# This lane only adds an isolated Python
# GetNextMissionMapPackageName declaration contract. Stay
# off CanTravelToNextMission (in-flight sibling),
# TravelToNextMission / GetActiveMission, AcknowledgeDebrief
# (in-flight sibling), ConfigureCampaign #302,
# CanStartMission #303, StartMission #304,
# IsMissionUnlocked #305, leftover CPG debrief
# #284/#195/#130/#8ccd, leftover FillResultCombatStats
# ASkyguardGunner* path, leftover campaign-save
# empty-fail-closed drafts, leftover campaign-roster lookup
# #111, leftover LoadCampaignProgressAfterConfigure (#290),
# leftover Harbor #6/#8/#9, leftover theater-kit #59,
# leftover flare/HUD #57/#61/#62, leftover drafts #56–#64,
# leftover #147 ApacheSystem, leftover #149 weapon stations,
# leftover #152 pilot commands, leftover #154 loadout /
# lock-phase, Harbor IncomingRadar 40/80, Yak/Igla/rifle
# live copy, and dirty D:\Skyguard52.
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
# Isolated-test drafts stay off this lane. CanTravel /
# AcknowledgeDebrief, ConfigureCampaign / CanStartMission /
# StartMission / IsMissionUnlocked, leftover CPG debrief,
# leftover campaign-save empty-fail-closed, leftover
# campaign-roster lookup #111, leftover
# LoadCampaignProgressAfterConfigure (#290), leftover
# theater-kit #59, leftover Harbor #6/#8/#9, leftover
# flare/HUD #57/#61/#62, leftover #147 ApacheSystem,
# leftover #149 weapon stations, leftover #152 pilot
# commands, and leftover #154 loadout/lock-phase stay
# sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_can_travel_to_next_mission_decl_contract.py",
    "Scripts/tests/test_acknowledge_debrief_decl_contract.py",
    "Scripts/tests/test_configure_campaign_decl_contract.py",
    "Scripts/tests/test_can_start_mission_decl_contract.py",
    "Scripts/tests/test_start_mission_decl_contract.py",
    "Scripts/tests/test_is_mission_unlocked_decl_contract.py",
    "Scripts/tests/test_is_valid_campaign_slot_name_decl_contract.py",
    "Scripts/tests/test_get_earned_campaign_medals_decl_contract.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
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
    "static int32 CalculateMissionScore(",
    "static int32 CalculateMedalTier(",
)
CAN_TRAVEL_NOT_LOCKED = (
    "bool CanTravelToNextMission() const;",
)
TRAVEL_AND_ACTIVE_NOT_LOCKED = (
    "bool TravelToNextMission(UObject* WorldContextObject);",
    "USkyguardMissionDefinition* GetActiveMission() const",
)
ACKNOWLEDGE_NOT_LOCKED = (
    "bool AcknowledgeDebrief();",
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
UNLOCK_NOT_LOCKED = (
    "bool IsMissionUnlocked(FName MissionId) const;",
)
CPG_DEBRIEF_NOT_LOCKED = (
    "SkyguardBuildCpgDebriefCopy",
    "FSkyguardCpgDebriefSnapshot",
    "const FSkyguardMissionDebrief& GetLastDebrief() const",
)
FILL_COMBAT_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
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
# .cpp GetNextMissionMapPackageName body / invented map
# package name returns stay unlocked. Do not invent
# INDEX_NONE or a map package name return.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return FString()",
    "return LastDebrief.NextMissionMap",
    "GetLongPackageName",
    "ToSoftObjectPath",
    "IsNull()",
    'TEXT("/Game/',
    "Lvl_M01",
    "Lvl_M01_CoastalIntercept_Playable_v1",
    "USkyguardCampaignSubsystem::GetNextMissionMapPackageName",
    "SkyguardCampaignSubsystem.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "ASkyguardIglaMissile",
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


class GetNextMissionMapPackageNameDeclContractTests(unittest.TestCase):
    def test_campaign_subsystem_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, GET_NEXT_MAP_DECL), section)

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
            f"\t{GET_NEXT_MAP_DECL}\n"
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
            f"\t{GET_NEXT_MAP_DECL}\n"
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
            f"\t{GET_NEXT_MAP_DECL}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, GET_NEXT_MAP_DECL)
        self.assertIn("GetNextMissionMapPackageName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertNotIn(GET_NEXT_MAP_DECL, section)

    def test_missing_get_next_mission_map_package_name_declaration_fails_closed(
        self,
    ) -> None:
        neighbors_only = (
            "\tbool CanTravelToNextMission() const;\n"
            "\tbool TravelToNextMission(UObject* WorldContextObject);\n"
            "\tUSkyguardMissionDefinition* GetActiveMission() const;\n"
            "\tbool AcknowledgeDebrief();\n"
            "\tbool ConfigureCampaign("
            "USkyguardCampaignDefinition* InCampaign);\n"
            "\tbool CanStartMission(FName MissionId) const;\n"
            "\tbool StartMission(FName MissionId);\n"
            "\tbool IsMissionUnlocked(FName MissionId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, GET_NEXT_MAP_DECL)
        self.assertIn("GetNextMissionMapPackageName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintPure, Category = "Campaign|Sortie")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, GET_NEXT_MAP_DECL)
        self.assertIn("GetNextMissionMapPackageName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_get_next_mission_map_package_name_declaration_matches_origin_main(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, GET_NEXT_MAP_DECL),
            GET_NEXT_MAP_DECL,
        )
        self.assertTrue(has_declaration(section, GET_NEXT_MAP_DECL))
        self.assertEqual(declaration_count(section, GET_NEXT_MAP_DECL), 1)
        self.assertTrue(GET_NEXT_MAP_DECL.endswith(";"), GET_NEXT_MAP_DECL)
        self.assertTrue(
            GET_NEXT_MAP_DECL.startswith("FString "),
            GET_NEXT_MAP_DECL,
        )
        self.assertIn("() const;", GET_NEXT_MAP_DECL)
        self.assertNotIn("INDEX_NONE", GET_NEXT_MAP_DECL)
        self.assertNotIn("return ", GET_NEXT_MAP_DECL)
        self.assertNotIn("{", GET_NEXT_MAP_DECL)
        self.assertNotIn("}", GET_NEXT_MAP_DECL)
        self.assertNotIn("TEXT(", GET_NEXT_MAP_DECL)
        self.assertNotIn("/Game/", GET_NEXT_MAP_DECL)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tFString\n"
            "\tGetNextMissionMapPackageName() const;\n"
            "private:\n"
            "};\n"
        )
        wrap_args = (
            "public:\n"
            "\tFString GetNextMissionMapPackageName(\n"
            "\t) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tFString GetNextMissionMapPackageName()\n"
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
            self.assertTrue(
                has_declaration(section, GET_NEXT_MAP_DECL),
                section,
            )
            self.assertEqual(
                require_declaration(section, GET_NEXT_MAP_DECL),
                GET_NEXT_MAP_DECL,
            )
            self.assertEqual(
                declaration_count(section, GET_NEXT_MAP_DECL),
                1,
            )
        one_line = f"{{\npublic:\n\t{GET_NEXT_MAP_DECL}\n}}\n"
        self.assertTrue(has_declaration(one_line, GET_NEXT_MAP_DECL))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, GET_NEXT_MAP_DECL), section)
        self.assertEqual(
            require_declaration(section, GET_NEXT_MAP_DECL),
            GET_NEXT_MAP_DECL,
        )

    def test_declaration_does_not_invent_index_none_or_map_package_name(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(GET_NEXT_MAP_DECL.endswith(";"), GET_NEXT_MAP_DECL)
        self.assertNotIn("return ", GET_NEXT_MAP_DECL)
        self.assertNotIn("INDEX_NONE", GET_NEXT_MAP_DECL)
        self.assertNotIn("NAME_None", GET_NEXT_MAP_DECL)
        self.assertNotIn("{", GET_NEXT_MAP_DECL)
        self.assertNotIn("}", GET_NEXT_MAP_DECL)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("return FString()", GET_NEXT_MAP_DECL)
        self.assertNotIn("GetLongPackageName", GET_NEXT_MAP_DECL)
        self.assertNotIn("ToSoftObjectPath", GET_NEXT_MAP_DECL)
        self.assertNotIn("TEXT(", GET_NEXT_MAP_DECL)
        self.assertNotIn("/Game/", GET_NEXT_MAP_DECL)
        self.assertNotIn("Lvl_M01", GET_NEXT_MAP_DECL)
        self.assertNotIn("= INDEX_NONE", section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_NEXT_MAP_DECL)

    def test_contract_does_not_relock_can_travel_to_next_mission(self) -> None:
        locked_only = f"{GET_NEXT_MAP_DECL}\n"
        self.assertEqual(
            require_declaration(locked_only, GET_NEXT_MAP_DECL),
            GET_NEXT_MAP_DECL,
        )
        for neighbor in CAN_TRAVEL_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_NEXT_MAP_DECL)
        self.assertNotIn("CanTravelToNextMission", GET_NEXT_MAP_DECL)
        self.assertNotIn("CanTravelToNextMission", locked_only)

    def test_contract_does_not_relock_travel_or_active_mission(self) -> None:
        locked_only = f"{GET_NEXT_MAP_DECL}\n"
        for neighbor in TRAVEL_AND_ACTIVE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_NEXT_MAP_DECL)
        self.assertNotIn("TravelToNextMission", GET_NEXT_MAP_DECL)
        self.assertNotIn("GetActiveMission", GET_NEXT_MAP_DECL)
        self.assertNotIn("TravelToNextMission", locked_only)
        self.assertNotIn("GetActiveMission", locked_only)

    def test_contract_does_not_relock_acknowledge_debrief(self) -> None:
        locked_only = f"{GET_NEXT_MAP_DECL}\n"
        for neighbor in ACKNOWLEDGE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_NEXT_MAP_DECL)
        self.assertNotIn("AcknowledgeDebrief", GET_NEXT_MAP_DECL)
        self.assertNotIn("AcknowledgeDebrief", locked_only)

    def test_contract_does_not_relock_configure_campaign(self) -> None:
        locked_only = f"{GET_NEXT_MAP_DECL}\n"
        for neighbor in CONFIGURE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_NEXT_MAP_DECL)
        self.assertNotIn("ConfigureCampaign", GET_NEXT_MAP_DECL)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", GET_NEXT_MAP_DECL)

    def test_contract_does_not_relock_can_start_mission(self) -> None:
        locked_only = f"{GET_NEXT_MAP_DECL}\n"
        for neighbor in CAN_START_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_NEXT_MAP_DECL)
        self.assertNotIn("CanStartMission", GET_NEXT_MAP_DECL)
        self.assertNotIn("CanStartMission", locked_only)

    def test_contract_does_not_relock_start_mission(self) -> None:
        locked_only = f"{GET_NEXT_MAP_DECL}\n"
        for neighbor in START_MISSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_NEXT_MAP_DECL)
        self.assertNotIn("StartMission", GET_NEXT_MAP_DECL)
        self.assertNotIn("StartMission", locked_only)

    def test_contract_does_not_relock_is_mission_unlocked(self) -> None:
        locked_only = f"{GET_NEXT_MAP_DECL}\n"
        for neighbor in UNLOCK_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_NEXT_MAP_DECL)
        self.assertNotIn("IsMissionUnlocked", GET_NEXT_MAP_DECL)
        self.assertNotIn("IsMissionUnlocked", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief(self) -> None:
        locked_only = f"{GET_NEXT_MAP_DECL}\n"
        for neighbor in CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_NEXT_MAP_DECL)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", GET_NEXT_MAP_DECL)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", GET_NEXT_MAP_DECL)
        self.assertNotIn("GetLastDebrief", GET_NEXT_MAP_DECL)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)
        self.assertNotIn("GetLastDebrief", locked_only)

    def test_contract_does_not_relock_fill_result_combat_stats(self) -> None:
        locked_only = f"{GET_NEXT_MAP_DECL}\n"
        for neighbor in FILL_COMBAT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_NEXT_MAP_DECL)
        self.assertNotIn("FillResultCombatStats", GET_NEXT_MAP_DECL)
        self.assertNotIn("ASkyguardGunner", GET_NEXT_MAP_DECL)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{GET_NEXT_MAP_DECL}\n"
        for token in LEFTOVER_SIBLINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_NEXT_MAP_DECL)
        self.assertNotIn("LoadCampaignProgressAfterConfigure", locked_only)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn("ESkyguardGunshipWeapon", locked_only)
        self.assertNotIn("ESkyguardPilotCommand", locked_only)
        self.assertNotIn("ESkyguardGuidedLockPhase", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{GET_NEXT_MAP_DECL}\n"
        self.assertEqual(
            require_declaration(locked_only, GET_NEXT_MAP_DECL),
            GET_NEXT_MAP_DECL,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_NEXT_MAP_DECL)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)
        self.assertNotIn("GetActiveMission", locked_only)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)
        self.assertNotIn("IsMissionUnlocked", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("GetEarnedCampaignMedals", locked_only)

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
            require_declaration(section, GET_NEXT_MAP_DECL),
            GET_NEXT_MAP_DECL,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn("GetLongPackageName", section)
        self.assertNotIn("ToSoftObjectPath", section)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_NEXT_MAP_DECL)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::GetNextMissionMapPackageName",
            section,
        )
        self.assertNotIn("GetLongPackageName", section)
        self.assertNotIn("ToSoftObjectPath", section)
        self.assertNotIn("return FString()", GET_NEXT_MAP_DECL)
        self.assertNotIn("TEXT(", GET_NEXT_MAP_DECL)
        self.assertNotIn("/Game/", GET_NEXT_MAP_DECL)
        self.assertNotIn("INDEX_NONE", GET_NEXT_MAP_DECL)
        self.assertNotIn("{", GET_NEXT_MAP_DECL)
        self.assertNotIn("}", GET_NEXT_MAP_DECL)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, GET_NEXT_MAP_DECL)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, GET_NEXT_MAP_DECL)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(GET_NEXT_MAP_DECL, "Rifle")
        self.assertNotEqual(GET_NEXT_MAP_DECL, "Igla")
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
                f"GetNextMissionMapPackageName contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, GET_NEXT_MAP_DECL.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", GET_NEXT_MAP_DECL)

    def test_contract_is_get_next_mission_map_package_name_declaration_only(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, GET_NEXT_MAP_DECL),
            GET_NEXT_MAP_DECL,
        )
        locked_only = f"{GET_NEXT_MAP_DECL}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_NEXT_MAP_DECL)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)
        self.assertNotIn("GetActiveMission", locked_only)
        self.assertNotIn("AcknowledgeDebrief", locked_only)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)
        self.assertNotIn("IsMissionUnlocked", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)
        for token in LEFTOVER_SIBLINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_NEXT_MAP_DECL)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, section)
            self.assertNotIn(token, GET_NEXT_MAP_DECL)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_NEXT_MAP_DECL)
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
        self.assertNotIn("INDEX_NONE", GET_NEXT_MAP_DECL)
        self.assertNotIn("return ", GET_NEXT_MAP_DECL)
        self.assertNotIn("{", GET_NEXT_MAP_DECL)
        self.assertNotEqual(GET_NEXT_MAP_DECL, "Rifle")
        self.assertNotEqual(GET_NEXT_MAP_DECL, "Igla")
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
