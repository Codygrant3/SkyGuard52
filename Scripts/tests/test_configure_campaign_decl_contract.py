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
# values, or the ConfigureCampaign body in the .cpp.
CONFIGURE_DECL = (
    "bool ConfigureCampaign(USkyguardCampaignDefinition* InCampaign);"
)
# Leftover #56–#64 plus CampaignSubsystem production files.
# This lane only adds an isolated Python ConfigureCampaign
# declaration contract. Stay off CanStartMission (in-flight
# sibling), leftover campaign-save empty-fail-closed drafts,
# leftover campaign-roster lookup #111, LoadCampaignProgressAfterConfigure
# (#290), leftover FillAndFinalize / FillAndFail Gunner paths,
# leftover Harbor #6/#8/#9, leftover theater-kit #59, leftover
# flare/HUD #57/#61/#62, leftover drafts #56–#64, leftover #147
# ApacheSystem, leftover #149 weapon stations, leftover #152
# pilot commands, leftover #154 loadout/lock-phase, Harbor
# IncomingRadar 40/80, Yak/Igla live copy, and dirty D:\Skyguard52.
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
# leftover #152 pilot commands, and leftover #154 loadout/lock-phase
# stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_load_progress_decl_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_campaign_sortie_flow_contract.py",
    "Scripts/tests/test_m09_campaign_handoff_contract.py",
    "Scripts/tests/test_can_start_mission_decl_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_gunship_weapon_stations_contract.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
)
# Neighbors in the same public section. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
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
    "static bool IsValidCampaignSlotName(const FString& SlotName);",
)
CAN_START_NOT_LOCKED = (
    "bool CanStartMission(FName MissionId) const;",
)
START_AND_OBJECTIVE_NOT_LOCKED = (
    "bool StartMission(FName MissionId);",
    "bool AddObjectiveProgress(FName ObjectiveId, int32 Amount = 1);",
    "bool FailObjective(FName ObjectiveId);",
    "bool CompleteSurviveObjectiveIfIntact(FName ObjectiveId);",
)
COMPLETE_FINALIZE_FAIL_NOT_LOCKED = (
    "bool CompleteActiveMission(FSkyguardMissionResult& InOutResult);",
    "bool FinalizeActiveMission(",
    "bool FailActiveMission(",
)
FILL_DEBRIEF_NOT_LOCKED = (
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
SAVE_SLOT_NOT_LOCKED = (
    "bool ApplySaveGame(const USkyguardCampaignSaveGame* SaveGame);",
    "USkyguardCampaignSaveGame* BuildSaveGame() const;",
    "bool SaveCampaignToSlot(",
    "bool LoadCampaignFromSlot(",
    "bool DeleteCampaignSlot(",
    "static bool IsValidCampaignSlotName(const FString& SlotName);",
)
# Leftover helpers live on other types / leftover drafts.
LOAD_PROGRESS_AND_FILL_NOT_LOCKED = (
    "LoadCampaignProgressAfterConfigure",
    "FillAndFinalize",
    "FillAndFail",
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
# .cpp ConfigureCampaign body / invented return values stay unlocked.
CPP_AND_INVENTED = (
    "ValidateDefinition",
    "MissionRecords.Reset",
    "ClearActiveMissionRuntime",
    "INDEX_NONE",
    "NAME_None",
    "return false",
    "return true",
    "return INDEX_NONE",
    "return 0",
    "return -1",
    "USkyguardCampaignSubsystem::ConfigureCampaign",
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


class ConfigureCampaignDeclContractTests(unittest.TestCase):
    def test_campaign_subsystem_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, CONFIGURE_DECL), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedSubsystem "
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
            f"\t{CONFIGURE_DECL}\n"
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
            f"\t{CONFIGURE_DECL}\n"
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
            "\tbool CanStartMission(FName MissionId) const;\n"
            "private:\n"
            f"\t{CONFIGURE_DECL}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, CONFIGURE_DECL)
        self.assertIn("ConfigureCampaign", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertNotIn(CONFIGURE_DECL, section)

    def test_missing_configure_campaign_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tbool CanStartMission(FName MissionId) const;\n"
            "\tbool StartMission(FName MissionId);\n"
            "\tbool AddObjectiveProgress(FName ObjectiveId, int32 Amount = 1);\n"
            "\tbool FailObjective(FName ObjectiveId);\n"
            "\tbool CompleteSurviveObjectiveIfIntact(FName ObjectiveId);\n"
            "\tbool CompleteActiveMission(FSkyguardMissionResult& InOutResult);\n"
            "\tbool FinalizeActiveMission(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            "\t\tconst FString& SlotName = TEXT(\"Skyguard52Campaign\"),\n"
            "\t\tint32 UserIndex = 0);\n"
            "\tbool FailActiveMission(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            "\t\tconst FString& SlotName = TEXT(\"Skyguard52Campaign\"),\n"
            "\t\tint32 UserIndex = 0);\n"
            "\tvoid FillResultCombatStats(\n"
            "\t\tFSkyguardMissionResult& InOutResult,\n"
            "\t\tconst ASkyguardGunner* Gunner,\n"
            "\t\tconst UObject* WorldContextObject) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, CONFIGURE_DECL)
        self.assertIn("ConfigureCampaign", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintCallable, Category = "Campaign")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, CONFIGURE_DECL)
        self.assertIn("ConfigureCampaign", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_parameter_list_fails_closed(self) -> None:
        name_only = "\tbool ConfigureCampaign();\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(name_only, CONFIGURE_DECL)
        self.assertIn("ConfigureCampaign", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_configure_campaign_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, CONFIGURE_DECL),
            CONFIGURE_DECL,
        )
        self.assertTrue(has_declaration(section, CONFIGURE_DECL))
        self.assertEqual(declaration_count(section, CONFIGURE_DECL), 1)
        self.assertTrue(CONFIGURE_DECL.endswith(";"), CONFIGURE_DECL)
        self.assertTrue(CONFIGURE_DECL.startswith("bool "), CONFIGURE_DECL)
        self.assertIn("USkyguardCampaignDefinition* InCampaign", CONFIGURE_DECL)
        self.assertNotIn("INDEX_NONE", CONFIGURE_DECL)
        self.assertNotIn("return ", CONFIGURE_DECL)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tbool\n"
            "\tConfigureCampaign(USkyguardCampaignDefinition* InCampaign);\n"
            "private:\n"
            "};\n"
        )
        wrap_args = (
            "public:\n"
            "\tbool ConfigureCampaign(\n"
            "\t\tUSkyguardCampaignDefinition* InCampaign);\n"
            "private:\n"
            "};\n"
        )
        wrap_star = (
            "public:\n"
            "\tbool ConfigureCampaign(\n"
            "\t\tUSkyguardCampaignDefinition * InCampaign);\n"
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
        header_wrap_star = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_star}"
        )
        for header in (
            header_wrap_type,
            header_wrap_args,
            header_wrap_star,
        ):
            section = public_section(header)
            self.assertTrue(has_declaration(section, CONFIGURE_DECL), section)
            self.assertEqual(
                require_declaration(section, CONFIGURE_DECL),
                CONFIGURE_DECL,
            )
            self.assertEqual(declaration_count(section, CONFIGURE_DECL), 1)
        one_line = f"{{\npublic:\n\t{CONFIGURE_DECL}\n}}\n"
        self.assertTrue(has_declaration(one_line, CONFIGURE_DECL))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, CONFIGURE_DECL), section)
        self.assertEqual(
            require_declaration(section, CONFIGURE_DECL),
            CONFIGURE_DECL,
        )

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(CONFIGURE_DECL.endswith(";"), CONFIGURE_DECL)
        self.assertNotIn("return ", CONFIGURE_DECL)
        self.assertNotIn("INDEX_NONE", CONFIGURE_DECL)
        self.assertNotIn("NAME_None", CONFIGURE_DECL)
        self.assertNotIn("{", CONFIGURE_DECL)
        self.assertNotIn("}", CONFIGURE_DECL)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("return 0", section)
        self.assertNotIn("return -1", section)
        self.assertNotIn("return false", section)
        self.assertNotIn("return true", section)
        self.assertNotIn("= INDEX_NONE", section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CONFIGURE_DECL)

    def test_contract_does_not_relock_can_start_mission(self) -> None:
        locked_only = f"{CONFIGURE_DECL}\n"
        self.assertEqual(
            require_declaration(locked_only, CONFIGURE_DECL),
            CONFIGURE_DECL,
        )
        for neighbor in CAN_START_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE_DECL)
        self.assertNotIn("CanStartMission", CONFIGURE_DECL)
        self.assertNotIn("CanStartMission", locked_only)

    def test_contract_does_not_relock_start_and_objective_helpers(self) -> None:
        locked_only = f"{CONFIGURE_DECL}\n"
        for neighbor in START_AND_OBJECTIVE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE_DECL)
        self.assertNotIn("StartMission", CONFIGURE_DECL)
        self.assertNotIn("AddObjectiveProgress", CONFIGURE_DECL)
        self.assertNotIn("FailObjective", CONFIGURE_DECL)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", CONFIGURE_DECL)
        self.assertNotIn("StartMission", locked_only)
        self.assertNotIn("AddObjectiveProgress", locked_only)
        self.assertNotIn("FailObjective", locked_only)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", locked_only)

    def test_contract_does_not_relock_complete_finalize_fail(self) -> None:
        locked_only = f"{CONFIGURE_DECL}\n"
        for neighbor in COMPLETE_FINALIZE_FAIL_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE_DECL)
        self.assertNotIn("CompleteActiveMission", CONFIGURE_DECL)
        self.assertNotIn("FinalizeActiveMission", CONFIGURE_DECL)
        self.assertNotIn("FailActiveMission", CONFIGURE_DECL)
        self.assertNotIn("CompleteActiveMission", locked_only)
        self.assertNotIn("FinalizeActiveMission", locked_only)
        self.assertNotIn("FailActiveMission", locked_only)

    def test_contract_does_not_relock_fill_result_or_debrief(self) -> None:
        locked_only = f"{CONFIGURE_DECL}\n"
        for neighbor in FILL_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE_DECL)
        self.assertNotIn("FillResultCombatStats", CONFIGURE_DECL)
        self.assertNotIn("ASkyguardGunner", CONFIGURE_DECL)
        self.assertNotIn("GetActiveMissionElapsedSeconds", CONFIGURE_DECL)
        self.assertNotIn("RetrySaveLastDebrief", CONFIGURE_DECL)
        self.assertNotIn("AcknowledgeDebrief", CONFIGURE_DECL)
        self.assertNotIn("GetLastDebrief", CONFIGURE_DECL)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("GetLastDebrief", locked_only)

    def test_contract_does_not_relock_travel_helpers(self) -> None:
        locked_only = f"{CONFIGURE_DECL}\n"
        for neighbor in TRAVEL_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE_DECL)
        self.assertNotIn("CanTravelToNextMission", CONFIGURE_DECL)
        self.assertNotIn("GetNextMissionMapPackageName", CONFIGURE_DECL)
        self.assertNotIn("TravelToNextMission", CONFIGURE_DECL)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)

    def test_contract_does_not_relock_save_slot_helpers(self) -> None:
        locked_only = f"{CONFIGURE_DECL}\n"
        for neighbor in SAVE_SLOT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE_DECL)
        self.assertNotIn("ApplySaveGame", CONFIGURE_DECL)
        self.assertNotIn("BuildSaveGame", CONFIGURE_DECL)
        self.assertNotIn("SaveCampaignToSlot", CONFIGURE_DECL)
        self.assertNotIn("LoadCampaignFromSlot", CONFIGURE_DECL)
        self.assertNotIn("DeleteCampaignSlot", CONFIGURE_DECL)
        self.assertNotIn("IsValidCampaignSlotName", CONFIGURE_DECL)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("BuildSaveGame", locked_only)
        self.assertNotIn("SaveCampaignToSlot", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)

    def test_contract_does_not_relock_load_progress_or_fill_and(self) -> None:
        locked_only = f"{CONFIGURE_DECL}\n"
        section = public_section(origin_main_header())
        for token in LOAD_PROGRESS_AND_FILL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_DECL)
            self.assertNotIn(token, section)
        self.assertNotIn("LoadCampaignProgressAfterConfigure", CONFIGURE_DECL)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)

    def test_contract_does_not_relock_leftover_apache_stations_pilot_loadout(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_DECL}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_APACHE_STATIONS_PILOT_LOADOUT:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_DECL)
            self.assertNotIn(token, section)
        self.assertNotIn("ApplyHydraForClusters", CONFIGURE_DECL)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("ApplyHydraForClusters", section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{CONFIGURE_DECL}\n"
        self.assertEqual(
            require_declaration(locked_only, CONFIGURE_DECL),
            CONFIGURE_DECL,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE_DECL)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("MissionStartWorldTimeSeconds", section)
        self.assertNotIn("BuildSuccessDebrief", section)
        self.assertNotIn("BuildFailureDebrief", section)
        self.assertNotIn("ClearActiveMissionRuntime", section)
        self.assertEqual(
            require_declaration(section, CONFIGURE_DECL),
            CONFIGURE_DECL,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn("ValidateDefinition", section)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CONFIGURE_DECL)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::ConfigureCampaign",
            section,
        )
        self.assertNotIn("ValidateDefinition", section)
        self.assertNotIn("MissionRecords.Reset", section)
        self.assertNotIn("ClearActiveMissionRuntime", section)
        self.assertNotIn("return false", CONFIGURE_DECL)
        self.assertNotIn("return true", CONFIGURE_DECL)
        self.assertNotIn("{", CONFIGURE_DECL)
        self.assertNotIn("}", CONFIGURE_DECL)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, CONFIGURE_DECL)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, CONFIGURE_DECL)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(CONFIGURE_DECL, "Rifle")
        self.assertNotEqual(CONFIGURE_DECL, "Igla")
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
                f"Campaign ConfigureCampaign contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, CONFIGURE_DECL.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", CONFIGURE_DECL)

    def test_contract_is_configure_campaign_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, CONFIGURE_DECL),
            CONFIGURE_DECL,
        )
        locked_only = f"{CONFIGURE_DECL}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE_DECL)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)
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
        self.assertNotIn("IsValidCampaignSlotName", locked_only)
        for token in LOAD_PROGRESS_AND_FILL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_DECL)
            self.assertNotIn(token, section)
        for token in LEFTOVER_APACHE_STATIONS_PILOT_LOADOUT:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_DECL)
            self.assertNotIn(token, section)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, section)
            self.assertNotIn(token, CONFIGURE_DECL)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CONFIGURE_DECL)
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
        self.assertNotIn("return ", CONFIGURE_DECL)
        self.assertNotIn("{", CONFIGURE_DECL)
        self.assertNotEqual(CONFIGURE_DECL, "Rifle")
        self.assertNotEqual(CONFIGURE_DECL, "Igla")
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
