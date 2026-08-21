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
# values, or the IsValidCampaignSlotName body in the .cpp.
# Do not lock leftover campaign-save empty-fail-closed slot
# behavior.
SLOT_NAME_DECL = (
    "static bool IsValidCampaignSlotName(const FString& SlotName);"
)
SLOT_NAME_DECL_NAME = "static bool IsValidCampaignSlotName("
PARAMETER_LIST = ("const FString& SlotName",)
# Leftover #56–#64 plus CampaignSubsystem production files.
# This lane only adds an isolated Python IsValidCampaignSlotName
# declaration contract. Stay off ConfigureCampaign / CanStartMission
# (newly drafted siblings), StartMission (in-flight sibling),
# IsMissionUnlocked (in-flight sibling), leftover campaign-save
# empty-fail-closed drafts, leftover campaign-roster lookup #111,
# LoadCampaignProgressAfterConfigure (#290), leftover
# FillResultCombatStats ASkyguardGunner* path, leftover Harbor
# #6/#8/#9, leftover theater-kit #59, leftover flare/HUD
# #57/#61/#62, leftover drafts #56–#64, leftover #147
# ApacheSystem, leftover #149 weapon stations, leftover #152
# pilot commands, leftover #154 loadout/lock-phase, Harbor
# IncomingRadar 40/80, live copy, and dirty D:\Skyguard52.
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
# Isolated-test drafts stay off this lane. Leftover campaign-save
# empty-fail-closed, leftover campaign-roster lookup, leftover
# LoadCampaignProgressAfterConfigure (#290), leftover theater-kit
# #59, leftover Harbor #6/#8/#9, leftover flare/HUD #57/#61/#62,
# leftover #147 ApacheSystem, leftover #149 weapon stations,
# leftover #152 pilot commands, leftover #154 loadout/lock-phase,
# and newly drafted ConfigureCampaign / CanStartMission stay
# sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
    "Scripts/tests/test_configure_campaign_decl_contract.py",
    "Scripts/tests/test_can_start_mission_decl_contract.py",
    "Scripts/tests/test_start_mission_decl_contract.py",
    "Scripts/tests/test_is_mission_unlocked_decl_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_campaign_sortie_flow_contract.py",
    "Scripts/tests/test_m09_campaign_handoff_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_gunship_weapon_stations_contract.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
)
# Neighbors in the same public section. Presence is not locked here.
# ConfigureCampaign / CanStartMission are newly drafted siblings.
# StartMission / IsMissionUnlocked are in-flight siblings.
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
    "bool TravelToNextMission(UObject* WorldContextObject);",
    "bool ApplySaveGame(const USkyguardCampaignSaveGame* SaveGame);",
    "USkyguardCampaignSaveGame* BuildSaveGame() const;",
    "bool SaveCampaignToSlot(",
    "bool LoadCampaignFromSlot(",
    "bool DeleteCampaignSlot(",
    "bool IsMissionUnlocked(FName MissionId) const;",
    "int32 GetEarnedCampaignMedals() const;",
    "USkyguardMissionDefinition* GetActiveMission() const",
    "USkyguardObjectiveRuntime* GetObjectiveRuntime() const",
    "USkyguardRouteRuntime* GetRouteRuntime() const",
    "static int32 CalculateMissionScore(",
    "static int32 CalculateMedalTier(",
)
CONFIGURE_AND_CAN_START_NOT_LOCKED = (
    "bool ConfigureCampaign(USkyguardCampaignDefinition* InCampaign);",
    "bool CanStartMission(FName MissionId) const;",
)
START_AND_UNLOCKED_NOT_LOCKED = (
    "bool StartMission(FName MissionId);",
    "bool IsMissionUnlocked(FName MissionId) const;",
)
SAVE_SLOT_NOT_LOCKED = (
    "bool ApplySaveGame(const USkyguardCampaignSaveGame* SaveGame);",
    "USkyguardCampaignSaveGame* BuildSaveGame() const;",
    "bool SaveCampaignToSlot(",
    "bool LoadCampaignFromSlot(",
    "bool DeleteCampaignSlot(",
)
FILL_RESULT_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
)
# Leftover helpers live on other types / leftover drafts.
LOAD_PROGRESS_AND_FILL_NOT_LOCKED = (
    "LoadCampaignProgressAfterConfigure",
    "FillAndFinalize",
    "FillAndFail",
)
EMPTY_FAIL_CLOSED_NOT_LOCKED = (
    "MigrateCampaignSave",
    "CurrentSaveVersion",
    "already-v2",
    "Identity migrate",
    "NewObject MissionRecords",
)
LEFTOVER_APACHE_STATIONS_PILOT_LOADOUT = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeapon",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "FSkyguardLoadoutSpec",
    "ApplyHydraForClusters",
)
# .cpp IsValidCampaignSlotName body / invented return values
# stay unlocked. Do not invent INDEX_NONE.
CPP_AND_INVENTED = (
    "TrimStartAndEnd",
    "MakeValidFileName",
    "Trimmed.IsEmpty",
    "Trimmed.Len()",
    "INDEX_NONE",
    "NAME_None",
    "return false",
    "return true",
    "return INDEX_NONE",
    "return 0",
    "return -1",
    "USkyguardCampaignSubsystem::IsValidCampaignSlotName",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
    "FSkyguardSearchlightTrackRuntime",
    "namespace SkyguardApacheCpgFeel",
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


class IsValidCampaignSlotNameDeclContractTests(unittest.TestCase):
    def test_campaign_subsystem_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, SLOT_NAME_DECL), section)

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
            f"\t{SLOT_NAME_DECL}\n"
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
            f"\t{SLOT_NAME_DECL}\n"
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
            f"\t{SLOT_NAME_DECL}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, SLOT_NAME_DECL)
        self.assertIn("IsValidCampaignSlotName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertNotIn(SLOT_NAME_DECL, section)

    def test_missing_slot_name_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tbool ConfigureCampaign("
            "USkyguardCampaignDefinition* InCampaign);\n"
            "\tbool CanStartMission(FName MissionId) const;\n"
            "\tbool StartMission(FName MissionId);\n"
            "\tbool IsMissionUnlocked(FName MissionId) const;\n"
            "\tbool ApplySaveGame("
            "const USkyguardCampaignSaveGame* SaveGame);\n"
            "\tUSkyguardCampaignSaveGame* BuildSaveGame() const;\n"
            "\tbool SaveCampaignToSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0) const;\n"
            "\tbool LoadCampaignFromSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0);\n"
            "\tbool DeleteCampaignSlot(\n"
            '\t\tconst FString& SlotName = TEXT("Skyguard52Campaign"),\n'
            "\t\tint32 UserIndex = 0) const;\n"
            "\tvoid FillResultCombatStats(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            "\t\tconst ASkyguardGunner* Gunner,\n"
            "\t\tconst UObject* WorldContextObject) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, SLOT_NAME_DECL)
        self.assertIn("IsValidCampaignSlotName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintPure, Category = "Campaign|Persistence")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, SLOT_NAME_DECL)
        self.assertIn("IsValidCampaignSlotName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_parameter_list_fails_closed(self) -> None:
        name_only = "\tstatic bool IsValidCampaignSlotName();\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(name_only, SLOT_NAME_DECL)
        self.assertIn("IsValidCampaignSlotName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_static_fails_closed(self) -> None:
        instance_only = (
            "\tbool IsValidCampaignSlotName(const FString& SlotName);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(instance_only, SLOT_NAME_DECL)
        self.assertIn("IsValidCampaignSlotName", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_slot_name_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, SLOT_NAME_DECL),
            SLOT_NAME_DECL,
        )
        self.assertTrue(has_declaration(section, SLOT_NAME_DECL))
        self.assertEqual(declaration_count(section, SLOT_NAME_DECL), 1)
        self.assertTrue(SLOT_NAME_DECL.endswith(";"), SLOT_NAME_DECL)
        self.assertIn(SLOT_NAME_DECL_NAME, SLOT_NAME_DECL)
        for parameter in PARAMETER_LIST:
            self.assertIn(parameter, SLOT_NAME_DECL)
            self.assertTrue(has_declaration(section, parameter), section)
        self.assertNotIn("INDEX_NONE", SLOT_NAME_DECL)
        self.assertNotIn("return ", SLOT_NAME_DECL)
        self.assertTrue(SLOT_NAME_DECL.startswith("static bool "), SLOT_NAME_DECL)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tstatic bool\n"
            "\tIsValidCampaignSlotName(const FString& SlotName);\n"
            "private:\n"
            "};\n"
        )
        wrap_args = (
            "public:\n"
            "\tstatic bool IsValidCampaignSlotName(\n"
            "\t\tconst FString& SlotName);\n"
            "private:\n"
            "};\n"
        )
        wrap_static = (
            "public:\n"
            "\tstatic\n"
            "\tbool IsValidCampaignSlotName(const FString& SlotName);\n"
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
        header_wrap_static = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_static}"
        )
        for header in (
            header_wrap_type,
            header_wrap_args,
            header_wrap_static,
        ):
            section = public_section(header)
            self.assertTrue(has_declaration(section, SLOT_NAME_DECL), section)
            self.assertEqual(
                require_declaration(section, SLOT_NAME_DECL),
                SLOT_NAME_DECL,
            )
            self.assertEqual(declaration_count(section, SLOT_NAME_DECL), 1)
        one_line = f"{{\npublic:\n\t{SLOT_NAME_DECL}\n}}\n"
        self.assertTrue(has_declaration(one_line, SLOT_NAME_DECL))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, SLOT_NAME_DECL), section)
        self.assertEqual(
            require_declaration(section, SLOT_NAME_DECL),
            SLOT_NAME_DECL,
        )
        for parameter in PARAMETER_LIST:
            self.assertTrue(has_declaration(wrap_args, parameter), wrap_args)
            self.assertTrue(has_declaration(section, parameter), section)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(SLOT_NAME_DECL.endswith(";"), SLOT_NAME_DECL)
        self.assertTrue(SLOT_NAME_DECL.startswith("static bool "), SLOT_NAME_DECL)
        self.assertNotIn("return ", SLOT_NAME_DECL)
        self.assertNotIn("INDEX_NONE", SLOT_NAME_DECL)
        self.assertNotIn("NAME_None", SLOT_NAME_DECL)
        self.assertNotIn("{", SLOT_NAME_DECL)
        self.assertNotIn("}", SLOT_NAME_DECL)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("return false", SLOT_NAME_DECL)
        self.assertNotIn("return true", SLOT_NAME_DECL)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SLOT_NAME_DECL)

    def test_contract_does_not_lock_slot_name_cpp_body(self) -> None:
        locked_only = f"{SLOT_NAME_DECL}\n"
        self.assertNotIn("TrimStartAndEnd", locked_only)
        self.assertNotIn("MakeValidFileName", locked_only)
        self.assertNotIn("Trimmed.IsEmpty", locked_only)
        self.assertNotIn("Trimmed.Len()", locked_only)
        self.assertNotIn("TrimStartAndEnd", SLOT_NAME_DECL)
        self.assertNotIn("MakeValidFileName", SLOT_NAME_DECL)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::IsValidCampaignSlotName",
            SLOT_NAME_DECL,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", SLOT_NAME_DECL)
        self.assertNotIn("{", SLOT_NAME_DECL)
        self.assertNotIn("}", SLOT_NAME_DECL)
        section = public_section(origin_main_header())
        self.assertNotIn("TrimStartAndEnd", section)
        self.assertNotIn("MakeValidFileName", section)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::IsValidCampaignSlotName",
            section,
        )

    def test_contract_does_not_relock_configure_or_can_start(self) -> None:
        locked_only = f"{SLOT_NAME_DECL}\n"
        for neighbor in CONFIGURE_AND_CAN_START_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SLOT_NAME_DECL)
        self.assertNotIn("ConfigureCampaign", SLOT_NAME_DECL)
        self.assertNotIn("CanStartMission", SLOT_NAME_DECL)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)

    def test_contract_does_not_relock_start_or_is_mission_unlocked(self) -> None:
        locked_only = f"{SLOT_NAME_DECL}\n"
        for neighbor in START_AND_UNLOCKED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SLOT_NAME_DECL)
        self.assertNotIn("bool StartMission(FName MissionId);", SLOT_NAME_DECL)
        self.assertNotIn("IsMissionUnlocked", SLOT_NAME_DECL)
        self.assertNotIn("bool StartMission(FName MissionId);", locked_only)
        self.assertNotIn("IsMissionUnlocked", locked_only)

    def test_contract_does_not_relock_save_slot_helpers(self) -> None:
        locked_only = f"{SLOT_NAME_DECL}\n"
        for neighbor in SAVE_SLOT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SLOT_NAME_DECL)
        self.assertNotIn("ApplySaveGame", SLOT_NAME_DECL)
        self.assertNotIn("BuildSaveGame", SLOT_NAME_DECL)
        self.assertNotIn("SaveCampaignToSlot", SLOT_NAME_DECL)
        self.assertNotIn("LoadCampaignFromSlot", SLOT_NAME_DECL)
        self.assertNotIn("DeleteCampaignSlot", SLOT_NAME_DECL)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("BuildSaveGame", locked_only)
        self.assertNotIn("SaveCampaignToSlot", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)

    def test_contract_does_not_relock_fill_result_combat_stats(self) -> None:
        locked_only = f"{SLOT_NAME_DECL}\n"
        for neighbor in FILL_RESULT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SLOT_NAME_DECL)
        self.assertNotIn("FillResultCombatStats", SLOT_NAME_DECL)
        self.assertNotIn("ASkyguardGunner", SLOT_NAME_DECL)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)

    def test_contract_does_not_relock_load_progress_or_fill_and(self) -> None:
        locked_only = f"{SLOT_NAME_DECL}\n"
        section = public_section(origin_main_header())
        for token in LOAD_PROGRESS_AND_FILL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SLOT_NAME_DECL)
            self.assertNotIn(token, section)
        self.assertNotIn("LoadCampaignProgressAfterConfigure", SLOT_NAME_DECL)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)

    def test_contract_does_not_relock_leftover_campaign_save_empty_fail_closed(
        self,
    ) -> None:
        locked_only = f"{SLOT_NAME_DECL}\n"
        section = public_section(origin_main_header())
        for token in EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SLOT_NAME_DECL)
            self.assertNotIn(token, section)
        self.assertNotIn("MigrateCampaignSave", SLOT_NAME_DECL)
        self.assertNotIn("CurrentSaveVersion", locked_only)
        self.assertNotIn("Identity migrate", section)

    def test_contract_does_not_relock_leftover_apache_stations_pilot_loadout(
        self,
    ) -> None:
        locked_only = f"{SLOT_NAME_DECL}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_APACHE_STATIONS_PILOT_LOADOUT:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SLOT_NAME_DECL)
            self.assertNotIn(token, section)
        self.assertNotIn("ApplyHydraForClusters", SLOT_NAME_DECL)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("ApplyHydraForClusters", section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{SLOT_NAME_DECL}\n"
        self.assertEqual(
            require_declaration(locked_only, SLOT_NAME_DECL),
            SLOT_NAME_DECL,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SLOT_NAME_DECL)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("bool StartMission(FName MissionId);", locked_only)
        self.assertNotIn("IsMissionUnlocked", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("LoadCampaignProgressAfterConfigure", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("MissionStartWorldTimeSeconds", section)
        self.assertNotIn("BuildSuccessDebrief", section)
        self.assertNotIn("BuildFailureDebrief", section)
        self.assertNotIn("ClearActiveMissionRuntime", section)
        self.assertEqual(
            require_declaration(section, SLOT_NAME_DECL),
            SLOT_NAME_DECL,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn("TrimStartAndEnd", section)
        self.assertNotIn("MakeValidFileName", section)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SLOT_NAME_DECL)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::IsValidCampaignSlotName",
            section,
        )
        self.assertNotIn("TrimStartAndEnd", section)
        self.assertNotIn("MakeValidFileName", section)
        self.assertNotIn("return false", SLOT_NAME_DECL)
        self.assertNotIn("return true", SLOT_NAME_DECL)
        self.assertNotIn("{", SLOT_NAME_DECL)
        self.assertNotIn("}", SLOT_NAME_DECL)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, SLOT_NAME_DECL)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, SLOT_NAME_DECL)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(SLOT_NAME_DECL, "Rifle")
        self.assertNotEqual(SLOT_NAME_DECL, "Igla")
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
                f"Campaign IsValidCampaignSlotName contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, SLOT_NAME_DECL.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", SLOT_NAME_DECL)

    def test_contract_is_slot_name_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, SLOT_NAME_DECL),
            SLOT_NAME_DECL,
        )
        locked_only = f"{SLOT_NAME_DECL}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SLOT_NAME_DECL)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("bool StartMission(FName MissionId);", locked_only)
        self.assertNotIn("IsMissionUnlocked", locked_only)
        self.assertNotIn("AddObjectiveProgress", locked_only)
        self.assertNotIn("FailObjective", locked_only)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", locked_only)
        self.assertNotIn("CompleteActiveMission", locked_only)
        self.assertNotIn("FinalizeActiveMission", locked_only)
        self.assertNotIn("FailActiveMission", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
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
        for token in LOAD_PROGRESS_AND_FILL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SLOT_NAME_DECL)
            self.assertNotIn(token, section)
        for token in EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SLOT_NAME_DECL)
            self.assertNotIn(token, section)
        for token in LEFTOVER_APACHE_STATIONS_PILOT_LOADOUT:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SLOT_NAME_DECL)
            self.assertNotIn(token, section)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, section)
            self.assertNotIn(token, SLOT_NAME_DECL)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SLOT_NAME_DECL)
            self.assertNotIn(token, section)
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
        self.assertNotIn("return ", SLOT_NAME_DECL)
        self.assertNotIn("{", SLOT_NAME_DECL)
        self.assertNotEqual(SLOT_NAME_DECL, "Rifle")
        self.assertNotEqual(SLOT_NAME_DECL, "Igla")
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
