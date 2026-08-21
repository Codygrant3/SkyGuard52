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
# values, or lock a specific GetActiveMission body.
# origin/main is inline
# (`USkyguardMissionDefinition* GetActiveMission() const { return ActiveMission; }`);
# accept that body and split-line forms without locking a body.
GET_ACTIVE_MISSION = "USkyguardMissionDefinition* GetActiveMission() const"
INLINE_BODY_FORM = (
    "USkyguardMissionDefinition* GetActiveMission() const "
    "{ return ActiveMission; }"
)
# Leftover #56–#64 plus CampaignSubsystem production files.
# This lane only adds an isolated Python GetActiveMission
# declaration contract. Stay off GetObjectiveRuntime /
# GetRouteRuntime, TravelToNextMission, CanTravelToNextMission /
# GetNextMissionMapPackageName (in-flight siblings),
# AcknowledgeDebrief (newly drafted sibling), ConfigureCampaign
# #302, CanStartMission #303, StartMission #304,
# IsMissionUnlocked #305, leftover CPG debrief #284/#195/#130/
# #8ccd, FillResultCombatStats (takes leftover
# ASkyguardGunner*), leftover campaign-save empty-fail-closed
# drafts, leftover campaign-roster lookup #111,
# LoadCampaignProgressAfterConfigure (#290), leftover Harbor
# #6/#8/#9, leftover theater-kit #59, leftover flare/HUD
# #57/#61/#62, leftover drafts #56–#64, leftover #147
# ApacheSystem, leftover #149 weapon stations, leftover #152
# pilot commands, leftover #154 loadout / lock-phase, Harbor
# IncomingRadar 40/80, live-copy leftovers,
# FSkyguardMission0NIntegrationReadiness, dirty D:\Skyguard52,
# and ApplyHydraForClusters.
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
# lookup, leftover LoadCampaignProgressAfterConfigure, leftover
# CPG debrief copy / snapshot / fail-closed, leftover
# theater-kit / Harbor / flare/HUD, and newly drafted
# campaign-subsystem siblings stay sibling-only.
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
    "Scripts/tests/test_is_valid_campaign_slot_name_decl_contract.py",
    "Scripts/tests/test_get_earned_campaign_medals_decl_contract.py",
    "Scripts/tests/test_acknowledge_debrief_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_copy_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed_contract.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_campaign_sortie_flow_contract.py",
    "Scripts/tests/test_m09_campaign_handoff_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_gunship_weapon_stations_contract.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
)
# Neighbors in the same public section. Presence is not locked here.
# GetObjectiveRuntime / GetRouteRuntime stay unlocked.
# CanTravelToNextMission / GetNextMissionMapPackageName are
# in-flight siblings. AcknowledgeDebrief is a newly drafted
# sibling. ConfigureCampaign #302 / CanStartMission #303 /
# StartMission #304 / IsMissionUnlocked #305 stay sibling-only.
# FillResultCombatStats takes leftover ASkyguardGunner*.
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
    "bool SaveCampaignToSlot(",
    "bool LoadCampaignFromSlot(",
    "bool DeleteCampaignSlot(",
    "static bool IsValidCampaignSlotName(const FString& SlotName);",
    "int32 GetEarnedCampaignMedals() const;",
    "USkyguardObjectiveRuntime* GetObjectiveRuntime() const",
    "USkyguardRouteRuntime* GetRouteRuntime() const",
    "static int32 CalculateMissionScore(",
    "static int32 CalculateMedalTier(",
)
CONFIGURE_CAN_START_START_NOT_LOCKED = (
    "bool ConfigureCampaign(USkyguardCampaignDefinition* InCampaign);",
    "bool CanStartMission(FName MissionId) const;",
    "bool StartMission(FName MissionId);",
)
IS_MISSION_UNLOCKED_NOT_LOCKED = (
    "bool IsMissionUnlocked(FName MissionId) const;",
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
# Leftover CPG debrief copy #284 / snapshot defaults #195 /
# fail-closed #8ccd / empty-capture #130 stay unlocked.
LEFTOVER_CPG_DEBRIEF_NOT_LOCKED = (
    "SkyguardBuildCpgDebriefCopy",
    "SkyguardCpgCopyHasBannedTerm",
    "SkyguardCaptureCpgDebrief",
    "FSkyguardCpgDebriefSnapshot",
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
# Invented return values stay unlocked. Do not invent
# INDEX_NONE or lock a specific GetActiveMission body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return nullptr",
    "return 0",
    "return -1",
    "return false",
    "return true",
    "USkyguardCampaignSubsystem::GetActiveMission",
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


class GetActiveMissionDeclContractTests(unittest.TestCase):
    def test_campaign_subsystem_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, GET_ACTIVE_MISSION), section)

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
            f"\t{GET_ACTIVE_MISSION};\n"
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
            f"\t{GET_ACTIVE_MISSION};\n"
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
            "\tbool AcknowledgeDebrief();\n"
            "private:\n"
            f"\t{GET_ACTIVE_MISSION};\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, GET_ACTIVE_MISSION)
        self.assertIn("GetActiveMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertNotIn(GET_ACTIVE_MISSION, section)

    def test_missing_get_active_mission_declaration_fails_closed(self) -> None:
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
            "\tUSkyguardObjectiveRuntime* GetObjectiveRuntime() const;\n"
            "\tUSkyguardRouteRuntime* GetRouteRuntime() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, GET_ACTIVE_MISSION)
        self.assertIn("GetActiveMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintPure, Category = "Campaign")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, GET_ACTIVE_MISSION)
        self.assertIn("GetActiveMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_neighbor_getters_do_not_satisfy(self) -> None:
        other_getters = (
            "\tfloat GetActiveMissionElapsedSeconds(\n"
            "\t\tconst UObject* WorldContextObject) const;\n"
            "\tconst FSkyguardMissionDebrief& GetLastDebrief() const;\n"
            "\tint32 GetEarnedCampaignMedals() const;\n"
            "\tUSkyguardObjectiveRuntime* GetObjectiveRuntime() const "
            "{ return ObjectiveRuntime; }\n"
            "\tUSkyguardRouteRuntime* GetRouteRuntime() const "
            "{ return RouteRuntime; }\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_getters, GET_ACTIVE_MISSION)
        self.assertIn("GetActiveMission", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        non_const = "\tUSkyguardMissionDefinition* GetActiveMission();\n"
        parameterized = (
            "\tUSkyguardMissionDefinition* GetActiveMission("
            "FName MissionId) const;\n"
        )
        wrong_return = "\tint32 GetActiveMission() const;\n"
        for region in (non_const, parameterized, wrong_return):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, GET_ACTIVE_MISSION)
            self.assertIn("GetActiveMission", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_get_active_mission_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, GET_ACTIVE_MISSION),
            GET_ACTIVE_MISSION,
        )
        self.assertTrue(has_declaration(section, GET_ACTIVE_MISSION))
        self.assertEqual(declaration_count(section, GET_ACTIVE_MISSION), 1)
        self.assertTrue(GET_ACTIVE_MISSION.endswith("const"), GET_ACTIVE_MISSION)
        self.assertTrue(
            GET_ACTIVE_MISSION.startswith("USkyguardMissionDefinition* "),
            GET_ACTIVE_MISSION,
        )
        self.assertNotIn("INDEX_NONE", GET_ACTIVE_MISSION)
        self.assertNotIn("{", GET_ACTIVE_MISSION)
        self.assertNotIn("}", GET_ACTIVE_MISSION)
        self.assertNotIn("return ", GET_ACTIVE_MISSION)
        self.assertNotEqual(GET_ACTIVE_MISSION, INLINE_BODY_FORM)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tUSkyguardMissionDefinition*\n"
            "\tGetActiveMission() const;\n"
            "private:\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tUSkyguardMissionDefinition* GetActiveMission()\n"
            "\tconst;\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tUSkyguardMissionDefinition* GetActiveMission(\n"
            "\t) const;\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_type}"
        )
        header_wrap_const = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_const}"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UGameInstanceSubsystem\n{{\n{wrap_name}"
        )
        for header in (
            header_wrap_type,
            header_wrap_const,
            header_wrap_name,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, GET_ACTIVE_MISSION),
                section,
            )
            self.assertEqual(
                require_declaration(section, GET_ACTIVE_MISSION),
                GET_ACTIVE_MISSION,
            )
            self.assertEqual(declaration_count(section, GET_ACTIVE_MISSION), 1)
        one_line = f"{{\npublic:\n\t{GET_ACTIVE_MISSION};\n}}\n"
        self.assertTrue(has_declaration(one_line, GET_ACTIVE_MISSION))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, GET_ACTIVE_MISSION), section)
        self.assertEqual(
            require_declaration(section, GET_ACTIVE_MISSION),
            GET_ACTIVE_MISSION,
        )

    def test_declaration_accepts_inline_body_form(self) -> None:
        inline_header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UGameInstanceSubsystem\n"
            "{\n"
            "public:\n"
            f"\t{INLINE_BODY_FORM}\n"
            "};\n"
        )
        split_inline = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UGameInstanceSubsystem\n"
            "{\n"
            "public:\n"
            "\tUSkyguardMissionDefinition* GetActiveMission()\n"
            "\tconst\n"
            "\t{\n"
            "\t\treturn ActiveMission;\n"
            "\t}\n"
            "};\n"
        )
        semicolon_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UGameInstanceSubsystem\n"
            "{\n"
            "public:\n"
            "\tUSkyguardMissionDefinition* GetActiveMission() const;\n"
            "};\n"
        )
        for header in (inline_header, split_inline, semicolon_only):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, GET_ACTIVE_MISSION),
                section,
            )
            self.assertEqual(
                require_declaration(section, GET_ACTIVE_MISSION),
                GET_ACTIVE_MISSION,
            )
        self.assertTrue(has_declaration(INLINE_BODY_FORM, GET_ACTIVE_MISSION))
        self.assertNotIn("{", GET_ACTIVE_MISSION)
        self.assertNotIn("return ActiveMission", GET_ACTIVE_MISSION)
        self.assertNotEqual(GET_ACTIVE_MISSION, INLINE_BODY_FORM)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, GET_ACTIVE_MISSION), section)

    def test_declaration_does_not_require_inline_body(self) -> None:
        self.assertNotIn("{", GET_ACTIVE_MISSION)
        self.assertNotIn("}", GET_ACTIVE_MISSION)
        self.assertNotIn("return ActiveMission", GET_ACTIVE_MISSION)
        self.assertNotIn("return ", GET_ACTIVE_MISSION)
        semicolon_only = f"{GET_ACTIVE_MISSION};\n"
        self.assertEqual(
            require_declaration(semicolon_only, GET_ACTIVE_MISSION),
            GET_ACTIVE_MISSION,
        )
        self.assertNotIn(INLINE_BODY_FORM, GET_ACTIVE_MISSION)
        self.assertNotIn("INDEX_NONE", GET_ACTIVE_MISSION)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(GET_ACTIVE_MISSION.endswith("const"), GET_ACTIVE_MISSION)
        self.assertNotIn("return ", GET_ACTIVE_MISSION)
        self.assertNotIn("INDEX_NONE", GET_ACTIVE_MISSION)
        self.assertNotIn("NAME_None", GET_ACTIVE_MISSION)
        self.assertNotIn("{", GET_ACTIVE_MISSION)
        self.assertNotIn("}", GET_ACTIVE_MISSION)
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("return 0", section)
        self.assertNotIn("return -1", section)
        self.assertNotIn("return nullptr", section)
        self.assertNotIn("= INDEX_NONE", section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_ACTIVE_MISSION)
            self.assertNotIn(token, section)

    def test_contract_does_not_invent_index_none_as_unknown_mission_return(
        self,
    ) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", GET_ACTIVE_MISSION)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("return INDEX_NONE", GET_ACTIVE_MISSION)
        self.assertNotIn("unknown-mission", GET_ACTIVE_MISSION.lower())
        self.assertNotIn("return false", GET_ACTIVE_MISSION)
        self.assertNotIn("return true", GET_ACTIVE_MISSION)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)

    def test_contract_does_not_lock_get_active_mission_body(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        self.assertNotIn("{", GET_ACTIVE_MISSION)
        self.assertNotIn("}", GET_ACTIVE_MISSION)
        self.assertNotIn("return ActiveMission", GET_ACTIVE_MISSION)
        self.assertNotIn("return ActiveMission", locked_only)
        self.assertNotIn(INLINE_BODY_FORM, GET_ACTIVE_MISSION)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::GetActiveMission",
            GET_ACTIVE_MISSION,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", GET_ACTIVE_MISSION)
        self.assertNotEqual(GET_ACTIVE_MISSION, INLINE_BODY_FORM)

    def test_contract_does_not_relock_configure_can_start_or_start(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        for neighbor in CONFIGURE_CAN_START_START_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_ACTIVE_MISSION)
        self.assertNotIn("ConfigureCampaign", GET_ACTIVE_MISSION)
        self.assertNotIn("CanStartMission", GET_ACTIVE_MISSION)
        self.assertNotIn("StartMission", GET_ACTIVE_MISSION)
        self.assertNotIn("ConfigureCampaign", locked_only)
        self.assertNotIn("CanStartMission", locked_only)
        self.assertNotIn("StartMission", locked_only)

    def test_contract_does_not_relock_is_mission_unlocked(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        for neighbor in IS_MISSION_UNLOCKED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_ACTIVE_MISSION)
        self.assertNotIn("IsMissionUnlocked", GET_ACTIVE_MISSION)
        self.assertNotIn("IsMissionUnlocked", locked_only)

    def test_contract_does_not_relock_objectives(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        for neighbor in OBJECTIVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_ACTIVE_MISSION)
        self.assertNotIn("AddObjectiveProgress", GET_ACTIVE_MISSION)
        self.assertNotIn("FailObjective", GET_ACTIVE_MISSION)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", GET_ACTIVE_MISSION)
        self.assertNotIn("AddObjectiveProgress", locked_only)
        self.assertNotIn("FailObjective", locked_only)
        self.assertNotIn("CompleteSurviveObjectiveIfIntact", locked_only)

    def test_contract_does_not_relock_active_mission_helpers(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        for neighbor in ACTIVE_MISSION_HELPERS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_ACTIVE_MISSION)
        self.assertNotIn("CompleteActiveMission", GET_ACTIVE_MISSION)
        self.assertNotIn("FinalizeActiveMission", GET_ACTIVE_MISSION)
        self.assertNotIn("FailActiveMission", GET_ACTIVE_MISSION)
        self.assertNotIn("CompleteActiveMission", locked_only)
        self.assertNotIn("FinalizeActiveMission", locked_only)
        self.assertNotIn("FailActiveMission", locked_only)

    def test_contract_does_not_relock_fill_result_combat_stats(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        for neighbor in FILL_COMBAT_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_ACTIVE_MISSION)
        self.assertNotIn("FillResultCombatStats", GET_ACTIVE_MISSION)
        self.assertNotIn("ASkyguardGunner", GET_ACTIVE_MISSION)
        self.assertNotIn("GetActiveMissionElapsedSeconds", GET_ACTIVE_MISSION)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("GetActiveMissionElapsedSeconds", locked_only)

    def test_contract_does_not_relock_acknowledge_debrief(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        for neighbor in ACKNOWLEDGE_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_ACTIVE_MISSION)
        self.assertNotIn("AcknowledgeDebrief", GET_ACTIVE_MISSION)
        self.assertNotIn("AcknowledgeDebrief", locked_only)

    def test_contract_does_not_relock_debrief_neighbors(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        for neighbor in DEBRIEF_NEIGHBORS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_ACTIVE_MISSION)
        self.assertNotIn("RetrySaveLastDebrief", GET_ACTIVE_MISSION)
        self.assertNotIn("GetLastDebrief", GET_ACTIVE_MISSION)
        self.assertNotIn("RetrySaveLastDebrief", locked_only)
        self.assertNotIn("GetLastDebrief", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_ACTIVE_MISSION)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_travel_helpers(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        for neighbor in TRAVEL_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_ACTIVE_MISSION)
        self.assertNotIn("CanTravelToNextMission", GET_ACTIVE_MISSION)
        self.assertNotIn("GetNextMissionMapPackageName", GET_ACTIVE_MISSION)
        self.assertNotIn("TravelToNextMission", GET_ACTIVE_MISSION)
        self.assertNotIn("CanTravelToNextMission", locked_only)
        self.assertNotIn("GetNextMissionMapPackageName", locked_only)
        self.assertNotIn("TravelToNextMission", locked_only)

    def test_contract_does_not_relock_runtime_getters(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        for neighbor in RUNTIME_GETTERS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_ACTIVE_MISSION)
        self.assertNotIn("GetObjectiveRuntime", GET_ACTIVE_MISSION)
        self.assertNotIn("GetRouteRuntime", GET_ACTIVE_MISSION)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("GetRouteRuntime", locked_only)

    def test_contract_does_not_relock_save_game_helpers(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        for neighbor in SAVE_GAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_ACTIVE_MISSION)
        self.assertNotIn("ApplySaveGame", GET_ACTIVE_MISSION)
        self.assertNotIn("BuildSaveGame", GET_ACTIVE_MISSION)
        self.assertNotIn("SaveCampaignToSlot", GET_ACTIVE_MISSION)
        self.assertNotIn("LoadCampaignFromSlot", GET_ACTIVE_MISSION)
        self.assertNotIn("DeleteCampaignSlot", GET_ACTIVE_MISSION)
        self.assertNotIn("IsValidCampaignSlotName", GET_ACTIVE_MISSION)
        self.assertNotIn("GetEarnedCampaignMedals", GET_ACTIVE_MISSION)
        self.assertNotIn("ApplySaveGame", locked_only)
        self.assertNotIn("BuildSaveGame", locked_only)
        self.assertNotIn("SaveCampaignToSlot", locked_only)
        self.assertNotIn("LoadCampaignFromSlot", locked_only)
        self.assertNotIn("DeleteCampaignSlot", locked_only)
        self.assertNotIn("IsValidCampaignSlotName", locked_only)
        self.assertNotIn("GetEarnedCampaignMedals", locked_only)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_ACTIVE_MISSION)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        self.assertEqual(
            require_declaration(locked_only, GET_ACTIVE_MISSION),
            GET_ACTIVE_MISSION,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_ACTIVE_MISSION)
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
            require_declaration(section, GET_ACTIVE_MISSION),
            GET_ACTIVE_MISSION,
        )
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::GetActiveMission",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_ACTIVE_MISSION)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCampaignSubsystem.cpp", section)
        self.assertNotIn(
            "USkyguardCampaignSubsystem::GetActiveMission",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", GET_ACTIVE_MISSION)
        self.assertNotIn("}", GET_ACTIVE_MISSION)
        self.assertNotIn("return ActiveMission", GET_ACTIVE_MISSION)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, section)
            self.assertNotIn(token, GET_ACTIVE_MISSION)
            self.assertNotIn(token, locked_only)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, section)
            self.assertNotIn(token, GET_ACTIVE_MISSION)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("40.f, 80.f", section)
        self.assertNotIn("40.f, 80.f", locked_only)
        self.assertNotIn(HARBOR_INCOMING, section)
        self.assertNotIn(HARBOR_INCOMING, locked_only)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", section)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", section)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        section = public_section(origin_main_header())
        harbor_tokens = (
            HARBOR_INCOMING,
            *HARBOR_CLOCKS,
            *HARBOR_TUNING,
            "40.f, 80.f",
        )
        for token in harbor_tokens:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_ACTIVE_MISSION)
            self.assertNotIn(token, section)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        section = public_section(origin_main_header())
        self.assertNotIn("Rifle", section)
        self.assertNotIn("Igla", section)
        self.assertNotIn("Yak", section)
        self.assertNotEqual(GET_ACTIVE_MISSION, "Rifle")
        self.assertNotEqual(GET_ACTIVE_MISSION, "Igla")
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
                f"campaign GetActiveMission contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not leftover live copy",
            )
            self.assertNotIn(banned, GET_ACTIVE_MISSION.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        self.assertNotIn("D:\\Skyguard52", header)
        self.assertNotIn("D:/Skyguard52", header)
        section = public_section(header)
        self.assertNotIn("D:\\Skyguard52", section)
        self.assertNotIn("D:/Skyguard52", GET_ACTIVE_MISSION)

    def test_contract_is_get_active_mission_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, GET_ACTIVE_MISSION),
            GET_ACTIVE_MISSION,
        )
        locked_only = f"{GET_ACTIVE_MISSION}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_ACTIVE_MISSION)
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
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_ACTIVE_MISSION)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_ACTIVE_MISSION)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, GET_ACTIVE_MISSION)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_ACTIVE_MISSION)
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
        self.assertNotIn("return ", GET_ACTIVE_MISSION)
        self.assertNotIn("{", GET_ACTIVE_MISSION)
        self.assertNotIn("return ActiveMission", GET_ACTIVE_MISSION)
        self.assertNotEqual(GET_ACTIVE_MISSION, INLINE_BODY_FORM)
        self.assertNotEqual(GET_ACTIVE_MISSION, "Rifle")
        self.assertNotEqual(GET_ACTIVE_MISSION, "Igla")
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
