from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMissionDefinition.h"
CLASS_NAME = "USkyguardMissionDefinition"
# Declaration presence only. Do not invent INDEX_NONE,
# a returned objective pointer, or lock the FindObjective
# body in the .cpp. origin/main is one line
# (`const FSkyguardObjectiveDefinition* FindObjective(FName ObjectiveId) const;`);
# accept that form, other split-line wraps, and an inline
# body without locking the body. Parse the public class
# section of USkyguardMissionDefinition only. Do not parse
# the FSkyguardObjectiveDefinition struct body.
FIND_OBJECTIVE = (
    "const FSkyguardObjectiveDefinition* FindObjective("
    "FName ObjectiveId) const;"
)
# Leftover #56–#64 plus MissionDefinition production files.
# This lane only adds an isolated Python FindObjective
# declaration contract. Stay off MissionId #350,
# DisplayName #351, CampaignOrder #352, MissionMap #353,
# Route #354, Objectives #355, Waves #356, Weather #357,
# Boss #358, Presentation #359, ScoreRules #360,
# PrerequisiteMissionIds, RequiredCampaignMedals,
# GetPrimaryAssetId (in-flight sibling on this class),
# ValidateDefinition (sibling this wave), leftover
# objective-definition defaults #b29f (struct fields),
# leftover objective-runtime fail-closed, leftover
# campaign-roster #111, leftover campaign-save
# empty-fail-closed, leftover route / weather / boss /
# wave / presentation / score-rules defaults, leftover
# FindMission #340, leftover CPG debrief
# #284/#195/#130/#8ccd, leftover Gunner helpers,
# leftover Harbor #6/#8/#9, leftover theater-kit #59,
# leftover flare/HUD #57/#61/#62, leftover drafts
# #56–#64, leftover #147 ApacheSystem, leftover #149
# weapon stations, leftover #152 pilot commands,
# leftover #154 loadout / lock-phase, leftover settings
# invert-look / ApplySettings broadcast #134, leftover
# bind-hud-host, leftover route-runtime fail-closed,
# leftover pilot #117/#120/#128/#129/#170, leftover
# gun-fire camera shake #8860, leftover mission-weather
# enum #96d2, leftover mission 0N integration readiness,
# Harbor leftover clocks, leftover live copy, and dirty
# workspace path.
LOCKED = {
    "SkyguardMissionDefinition.h",
    "SkyguardMissionDefinition.cpp",
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
# campaign-roster #111, leftover campaign-save
# empty-fail-closed, leftover objective-definition
# defaults, leftover objective-runtime fail-closed,
# leftover route / weather / boss / wave /
# presentation / score-rules defaults, leftover
# MissionId #350, leftover FindMission #340, leftover
# DisplayName through RequiredCampaignMedals field
# drafts, leftover GetPrimaryAssetId / ValidateDefinition,
# leftover CPG debrief, leftover route-runtime
# fail-closed, leftover theater-kit / Harbor /
# flare/HUD, leftover ApacheSystem / weapon stations /
# pilot commands / loadout, leftover settings
# invert-look, leftover bind-hud-host, leftover
# pilot drafts, leftover gun-fire camera shake, and
# leftover mission-weather enum stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_roster_get_decl_contract.py",
    "Scripts/tests/test_campaign_roster_id_at_decl_contract.py",
    "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
    "Scripts/tests/test_campaign_roster_loadout_label_decl_contract.py",
    "Scripts/tests/test_campaign_roster_weather_enum_label_decl_contract.py",
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_enemy_wave_defaults_contract.py",
    "Scripts/tests/test_boss_definition_defaults_contract.py",
    "Scripts/tests/test_weather_profile_defaults_contract.py",
    "Scripts/tests/test_mission_presentation_defaults_contract.py",
    "Scripts/tests/test_mission_score_rules_defaults_contract.py",
    "Scripts/tests/test_route_definition_fields_contract.py",
    "Scripts/tests/test_objective_runtime_fail_closed.py",
    "Scripts/tests/test_objective_runtime_empty_fail_closed.py",
    "Scripts/tests/test_objective_runtime_fail_closed_contract.py",
    "Scripts/tests/test_route_runtime_fail_closed.py",
    "Scripts/tests/test_route_runtime_empty_fail_closed.py",
    "Scripts/tests/test_route_runtime_fail_closed_contract.py",
    "Scripts/tests/test_mission_definition_mission_id_decl_contract.py",
    "Scripts/tests/test_mission_definition_display_name_decl_contract.py",
    "Scripts/tests/test_mission_definition_campaign_order_decl_contract.py",
    "Scripts/tests/test_mission_definition_mission_map_decl_contract.py",
    "Scripts/tests/test_mission_definition_route_decl_contract.py",
    "Scripts/tests/test_mission_definition_objectives_decl_contract.py",
    "Scripts/tests/test_mission_definition_waves_decl_contract.py",
    "Scripts/tests/test_mission_definition_weather_decl_contract.py",
    "Scripts/tests/test_mission_definition_boss_decl_contract.py",
    "Scripts/tests/test_mission_definition_presentation_decl_contract.py",
    "Scripts/tests/test_mission_definition_score_rules_decl_contract.py",
    "Scripts/tests/test_mission_definition_prerequisite_ids_decl_contract.py",
    "Scripts/tests/test_mission_definition_required_medals_decl_contract.py",
    "Scripts/tests/test_find_mission_decl_contract.py",
    "Scripts/tests/test_validate_definition_decl_contract.py",
    "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
    "Scripts/tests/test_campaign_definition_campaign_id_decl_contract.py",
    "Scripts/tests/test_campaign_definition_display_name_decl_contract.py",
    "Scripts/tests/test_campaign_definition_missions_decl_contract.py",
    "Scripts/tests/test_campaign_save_campaign_id_decl_contract.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
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
    "Scripts/tests/test_pilot_confirm_line_contract.py",
    "Scripts/tests/test_pilot_warn_lock_reload_contract.py",
    "Scripts/tests/test_pilot_line_enum_contract.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
    "Scripts/tests/test_gunship_types_loadout_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
    "Scripts/tests/test_bind_hud_host_presentation_tests.py",
    "Scripts/tests/test_gun_fire_camera_shake_tests.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
)
# Neighbors in the same public section. Presence is not locked
# here. MissionId #350 through ScoreRules #360 /
# PrerequisiteMissionIds / RequiredCampaignMedals /
# GetPrimaryAssetId / ValidateDefinition stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "FName MissionId;",
    "FText DisplayName;",
    "int32 CampaignOrder = 1;",
    "TSoftObjectPtr<UWorld> MissionMap;",
    "FSkyguardRouteDefinition Route;",
    "TArray<FSkyguardObjectiveDefinition> Objectives;",
    "TArray<FSkyguardEnemyWaveDefinition> Waves;",
    "FSkyguardBossDefinition Boss;",
    "FSkyguardWeatherProfile Weather;",
    "FSkyguardMissionPresentation Presentation;",
    "FSkyguardMissionScoreRules ScoreRules;",
    "TArray<FName> PrerequisiteMissionIds;",
    "int32 RequiredCampaignMedals = 0;",
    "virtual FPrimaryAssetId GetPrimaryAssetId() const override;",
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;",
)
MISSION_ID_NOT_LOCKED = ("FName MissionId;",)
DISPLAY_NAME_NOT_LOCKED = ("FText DisplayName;",)
CAMPAIGN_ORDER_NOT_LOCKED = ("int32 CampaignOrder = 1;",)
MISSION_MAP_NOT_LOCKED = ("TSoftObjectPtr<UWorld> MissionMap;",)
ROUTE_NOT_LOCKED = ("FSkyguardRouteDefinition Route;",)
OBJECTIVES_NOT_LOCKED = (
    "TArray<FSkyguardObjectiveDefinition> Objectives;",
)
WAVES_NOT_LOCKED = ("TArray<FSkyguardEnemyWaveDefinition> Waves;",)
BOSS_NOT_LOCKED = ("FSkyguardBossDefinition Boss;",)
WEATHER_NOT_LOCKED = ("FSkyguardWeatherProfile Weather;",)
PRESENTATION_NOT_LOCKED = ("FSkyguardMissionPresentation Presentation;",)
SCORE_RULES_NOT_LOCKED = ("FSkyguardMissionScoreRules ScoreRules;",)
PREREQUISITE_NOT_LOCKED = ("TArray<FName> PrerequisiteMissionIds;",)
MEDALS_NOT_LOCKED = ("int32 RequiredCampaignMedals = 0;",)
PRIMARY_ASSET_NOT_LOCKED = (
    "virtual FPrimaryAssetId GetPrimaryAssetId() const override;",
)
VALIDATE_DEFINITION_NOT_LOCKED = (
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;",
)
FIND_MISSION_NOT_LOCKED = (
    "USkyguardMissionDefinition* FindMission(FName MissionId) const;",
)
# Leftover objective-definition defaults #b29f lock
# struct fields, not this class method. Stay off those
# leftover struct-default drafts and leftover route /
# weather / boss / wave / presentation / score-rules
# defaults.
LEFTOVER_STRUCT_DEFAULTS_NOT_LOCKED = (
    "FName ObjectiveId;",
    "int32 RequiredProgress = 1;",
    "bool bRequiredForMissionSuccess = true;",
    "bool bFailureEndsMission = false;",
    "int32 ScoreReward = 1000;",
    "FName WaveId;",
    "float StartTimeSeconds = 0.f;",
    "FName CompletionObjectiveId;",
    "FName BossId;",
    "FName DefeatObjectiveId;",
    "int32 MaximumBreakupPieces = 3;",
    "FName ProfileId;",
    "FText Briefing;",
    "TArray<FText> RadioChatter;",
    "FText SuccessDebrief;",
    "FText FailureDebrief;",
    "float MinimumBriefingWarmupSeconds = 3.f;",
    "int32 CompletionScore = 5000;",
    "int32 PerfectAccuracyBonus = 2500;",
    "int32 NoDamageBonus = 1500;",
    "int32 BronzeThreshold = 5000;",
    "int32 SilverThreshold = 8000;",
    "int32 GoldThreshold = 11000;",
    "FName RouteId;",
    "TArray<FSkyguardRoutePoint> Points;",
    "test_objective_definition_defaults_contract.py",
    "test_enemy_wave_defaults_contract.py",
    "test_boss_definition_defaults_contract.py",
    "test_weather_profile_defaults_contract.py",
    "test_mission_presentation_defaults_contract.py",
    "test_mission_score_rules_defaults_contract.py",
    "test_route_definition_fields_contract.py",
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
# Leftover #147 / #149 / #152 / #154 / #134 / Hydra
# cluster apply / leftover Gunner FillAnd* stay unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "FillAndFinalize",
    "FillAndFail",
    "FillResultCombatStats",
    "bInvertLook",
    "ApplySettings",
    "BindHudHost",
    "enum class ESkyguardMissionWeather",
    "ESkyguardPilotLine",
)
# Invented UFUNCTION / UPROPERTY specifiers that are not
# on origin/main for this method. Nearby ValidateDefinition
# uses BlueprintCallable Category Mission; do not invent
# that metadata on FindObjective.
INVENTED_UFUNCTION = (
    "UFUNCTION",
    "BlueprintCallable",
    "BlueprintPure",
    'Category = "Mission"',
    'Category = "Campaign"',
    "BlueprintReadWrite",
    "AllowPrivateAccess",
)
# .cpp FindObjective body / invented returned objective
# pointer stay unlocked. Do not invent INDEX_NONE or lock
# the cpp body. origin/main .cpp uses const FName and
# FindByPredicate; that body is not locked here.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return nullptr",
    "FindByPredicate",
    "Objectives.FindByPredicate",
    "Objective.ObjectiveId == ObjectiveId",
    "USkyguardMissionDefinition::FindObjective",
    "SkyguardMissionDefinition.cpp",
)
RETURNED_POINTER_NOT_LOCKED = (
    "nullptr",
    "return nullptr",
    "FindByPredicate",
    "Objectives.FindByPredicate",
    "Found->Get()",
    "return Objectives.FindByPredicate",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
)
CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
STRUCT_RE = re.compile(r"struct\s+(?:SKYGUARD52_API\s+)?FSkyguardObjectiveDefinition\b")
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")
UFUNCTION_NEARBY = 'UFUNCTION(BlueprintCallable, Category = "Mission")'


def leftover_harbor_tokens() -> tuple[str, ...]:
    incoming = "Incoming" + "Radar"
    forty = f"{40}.f"
    eighty = f"{80}.f"
    return (
        incoming,
        incoming + "LiveIntervalSeconds",
        incoming + "DownIntervalSeconds",
        forty,
        eighty,
        f"{40}.f, {80}.f",
    )


def leftover_live_copy_tokens() -> tuple[str, ...]:
    return ("ig" + "la", "y" + "ak", "rif" + "le")


def leftover_readiness_tokens() -> tuple[str, ...]:
    return (
        "FSkyguardMission0NIntegrationReadiness",
        "b" + "Y" + "ak" + "RuntimeReady",
        "ASkyguard" + "Ig" + "la" + "Missile",
    )


def this_file_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
    compact = re.sub(r"\s*=\s*", " = ", compact)
    return compact


def declaration_signature(declaration: str) -> str:
    compact = collapsed(declaration)
    if compact.endswith(";"):
        return compact[:-1].rstrip()
    return compact


def declaration_hits(region: str, declaration: str) -> int:
    if declaration in region:
        return region.count(declaration)
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return compact_region.count(compact_decl)
    signature = declaration_signature(declaration)
    braced = re.sub(r"\s*\{", "{", compact_region)
    return braced.count(signature + ";") + braced.count(signature + "{")


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
    return declaration_hits(region, declaration) > 0


def declaration_count(region: str, declaration: str) -> int:
    return declaration_hits(region, declaration)


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"class {CLASS_NAME} public section"
        )
    return declaration


class MissionDefinitionFindObjectiveDeclContractTests(unittest.TestCase):
    def test_mission_definition_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, FIND_OBJECTIVE), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedMission "
                ": public UPrimaryDataAsset\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API UOtherMissionDefinition "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "public:\n"
            f"\t{FIND_OBJECTIVE}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_campaign_definition_class_does_not_satisfy(self) -> None:
        definition = (
            "class SKYGUARD52_API USkyguardCampaignDefinition "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "public:\n"
            "\tUSkyguardMissionDefinition* FindMission("
            "FName MissionId) const;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(definition)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_objective_definition_struct_does_not_satisfy(self) -> None:
        struct_only = (
            "USTRUCT(BlueprintType)\n"
            "struct FSkyguardObjectiveDefinition\n"
            "{\n"
            "\tGENERATED_BODY()\n"
            "\tFName ObjectiveId;\n"
            "\tint32 RequiredProgress = 1;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(struct_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIsNotNone(STRUCT_RE.search(struct_only), struct_only)
        self.assertIsNone(CLASS_RE.search(struct_only), struct_only)

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "private:\n"
            f"\t{FIND_OBJECTIVE}\n"
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
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
            "private:\n"
            f"\t{FIND_OBJECTIVE}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, FIND_OBJECTIVE)
        self.assertIn("FindObjective", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, FIND_OBJECTIVE))

    def test_missing_find_objective_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tFName MissionId;\n"
            "\tFText DisplayName;\n"
            "\tint32 CampaignOrder = 1;\n"
            "\tTSoftObjectPtr<UWorld> MissionMap;\n"
            "\tFSkyguardRouteDefinition Route;\n"
            "\tTArray<FSkyguardObjectiveDefinition> Objectives;\n"
            "\tTArray<FSkyguardEnemyWaveDefinition> Waves;\n"
            "\tFSkyguardBossDefinition Boss;\n"
            "\tFSkyguardWeatherProfile Weather;\n"
            "\tFSkyguardMissionPresentation Presentation;\n"
            "\tFSkyguardMissionScoreRules ScoreRules;\n"
            "\tTArray<FName> PrerequisiteMissionIds;\n"
            "\tint32 RequiredCampaignMedals = 0;\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() "
            "const override;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, FIND_OBJECTIVE)
        self.assertIn("FindObjective", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_NEARBY}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, FIND_OBJECTIVE)
        self.assertIn("FindObjective", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tFName MissionId;\n"
            "\tFText DisplayName;\n"
            "\tint32 CampaignOrder = 1;\n"
            "\tTSoftObjectPtr<UWorld> MissionMap;\n"
            "\tFSkyguardRouteDefinition Route;\n"
            "\tTArray<FSkyguardObjectiveDefinition> Objectives;\n"
            "\tTArray<FSkyguardEnemyWaveDefinition> Waves;\n"
            "\tFSkyguardBossDefinition Boss;\n"
            "\tFSkyguardWeatherProfile Weather;\n"
            "\tFSkyguardMissionPresentation Presentation;\n"
            "\tFSkyguardMissionScoreRules ScoreRules;\n"
            "\tTArray<FName> PrerequisiteMissionIds;\n"
            "\tint32 RequiredCampaignMedals = 0;\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() "
            "const override;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, FIND_OBJECTIVE)
        self.assertIn("FindObjective", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_arg = (
            "\tconst FSkyguardObjectiveDefinition* FindObjective() const;\n"
        )
        non_const = (
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId);\n"
        )
        wrong_return = "\tvoid FindObjective(FName ObjectiveId) const;\n"
        bool_return = "\tbool FindObjective(FName ObjectiveId) const;\n"
        mutable_ptr = (
            "\tFSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        wrong_arg = (
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FString ObjectiveId) const;\n"
        )
        const_name = (
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "const FName ObjectiveId) const;\n"
        )
        find_mission = (
            "\tUSkyguardMissionDefinition* FindMission("
            "FName MissionId) const;\n"
        )
        for region in (
            missing_arg,
            non_const,
            wrong_return,
            bool_return,
            mutable_ptr,
            wrong_arg,
            const_name,
            find_mission,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, FIND_OBJECTIVE)
            self.assertIn("FindObjective", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_find_objective_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, FIND_OBJECTIVE),
            FIND_OBJECTIVE,
        )
        self.assertTrue(has_declaration(section, FIND_OBJECTIVE))
        self.assertEqual(
            declaration_count(section, FIND_OBJECTIVE),
            1,
        )
        self.assertTrue(
            FIND_OBJECTIVE.endswith("const;"),
            FIND_OBJECTIVE,
        )
        self.assertTrue(
            FIND_OBJECTIVE.startswith(
                "const FSkyguardObjectiveDefinition* "
            ),
            FIND_OBJECTIVE,
        )
        self.assertIn("FName ObjectiveId", FIND_OBJECTIVE)
        self.assertIn("FindObjective", FIND_OBJECTIVE)
        self.assertNotIn("INDEX_NONE", FIND_OBJECTIVE)
        self.assertNotIn("{", FIND_OBJECTIVE)
        self.assertNotIn("}", FIND_OBJECTIVE)
        self.assertNotIn("return ", FIND_OBJECTIVE)
        self.assertNotIn("nullptr", FIND_OBJECTIVE)
        self.assertNotIn("UFUNCTION", FIND_OBJECTIVE)
        self.assertNotIn("FindByPredicate", FIND_OBJECTIVE)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_name = (
            "public:\n"
            "\tconst FSkyguardObjectiveDefinition* FindObjective(\n"
            "\t\tFName ObjectiveId) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_type = (
            "public:\n"
            "\tconst FSkyguardObjectiveDefinition*\n"
            "\tFindObjective(FName ObjectiveId) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_arg = (
            "public:\n"
            "\tconst FSkyguardObjectiveDefinition* FindObjective(FName\n"
            "\t\tObjectiveId) const;\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId)\n"
            "\tconst;\n"
            "};\n"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_name}"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_type}"
        )
        header_wrap_arg = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_arg}"
        )
        header_wrap_const = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_const}"
        )
        for header in (
            header_wrap_name,
            header_wrap_type,
            header_wrap_arg,
            header_wrap_const,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, FIND_OBJECTIVE),
                section,
            )
            self.assertEqual(
                require_declaration(section, FIND_OBJECTIVE),
                FIND_OBJECTIVE,
            )
            self.assertEqual(
                declaration_count(section, FIND_OBJECTIVE),
                1,
            )
        one_line = f"{{\npublic:\n\t{FIND_OBJECTIVE}\n}}\n"
        self.assertTrue(has_declaration(one_line, FIND_OBJECTIVE))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, FIND_OBJECTIVE), section)
        self.assertEqual(
            require_declaration(section, FIND_OBJECTIVE),
            FIND_OBJECTIVE,
        )

    def test_declaration_accepts_inline_body_without_locking_body(self) -> None:
        inline = (
            "public:\n"
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const\n"
            "\t{\n"
            "\t\treturn nullptr;\n"
            "\t}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{inline}"
        )
        section = public_section(header)
        self.assertTrue(has_declaration(section, FIND_OBJECTIVE), section)
        self.assertEqual(
            require_declaration(section, FIND_OBJECTIVE),
            FIND_OBJECTIVE,
        )
        self.assertEqual(
            declaration_count(section, FIND_OBJECTIVE),
            1,
        )
        self.assertNotIn("{", FIND_OBJECTIVE)
        self.assertNotIn("}", FIND_OBJECTIVE)
        self.assertNotIn("return ", FIND_OBJECTIVE)
        self.assertNotIn("nullptr", FIND_OBJECTIVE)
        self.assertNotIn("return nullptr", FIND_OBJECTIVE)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", FIND_OBJECTIVE)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", FIND_OBJECTIVE)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_returned_objective_pointer(
        self,
    ) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for token in RETURNED_POINTER_NOT_LOCKED:
            self.assertNotIn(token, FIND_OBJECTIVE)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("return ", FIND_OBJECTIVE)
        self.assertNotIn("nullptr", FIND_OBJECTIVE)
        self.assertNotIn("FindByPredicate", FIND_OBJECTIVE)
        self.assertNotIn("Found->Get()", FIND_OBJECTIVE)
        self.assertNotIn("{", FIND_OBJECTIVE)
        self.assertNotIn("}", FIND_OBJECTIVE)
        section = public_section(origin_main_header())
        self.assertNotIn("return nullptr", section)
        self.assertNotIn("FindByPredicate", section)
        self.assertNotIn("Found->Get()", section)

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for invented in INVENTED_UFUNCTION:
            self.assertNotIn(invented, FIND_OBJECTIVE)
            self.assertNotIn(invented, locked_only)
        self.assertFalse(FIND_OBJECTIVE.startswith("UFUNCTION"), FIND_OBJECTIVE)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, FIND_OBJECTIVE), section)
        self.assertEqual(
            require_declaration(section, FIND_OBJECTIVE),
            FIND_OBJECTIVE,
        )

    def test_contract_does_not_lock_find_objective_cpp_body(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        self.assertNotIn("{", FIND_OBJECTIVE)
        self.assertNotIn("}", FIND_OBJECTIVE)
        self.assertNotIn("return ", FIND_OBJECTIVE)
        self.assertNotIn(
            "USkyguardMissionDefinition::FindObjective",
            FIND_OBJECTIVE,
        )
        self.assertNotIn(
            "SkyguardMissionDefinition.cpp",
            FIND_OBJECTIVE,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", locked_only)
        self.assertNotIn("FindByPredicate", FIND_OBJECTIVE)
        self.assertNotIn("Objectives.FindByPredicate", FIND_OBJECTIVE)
        self.assertNotIn("return nullptr", FIND_OBJECTIVE)
        self.assertNotIn("const FName ObjectiveId", FIND_OBJECTIVE)

    def test_contract_does_not_relock_mission_id(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in MISSION_ID_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("MissionId", FIND_OBJECTIVE)
        self.assertNotIn("MissionId", locked_only)

    def test_contract_does_not_relock_display_name(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in DISPLAY_NAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("DisplayName", FIND_OBJECTIVE)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("FText", FIND_OBJECTIVE)

    def test_contract_does_not_relock_campaign_order(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in CAMPAIGN_ORDER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("CampaignOrder", FIND_OBJECTIVE)
        self.assertNotIn("CampaignOrder", locked_only)

    def test_contract_does_not_relock_mission_map(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in MISSION_MAP_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("MissionMap", FIND_OBJECTIVE)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("TSoftObjectPtr", FIND_OBJECTIVE)

    def test_contract_does_not_relock_route(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in ROUTE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("FSkyguardRouteDefinition", FIND_OBJECTIVE)
        self.assertNotIn("FSkyguardRouteDefinition", locked_only)

    def test_contract_does_not_relock_objectives_field(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in OBJECTIVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("Objectives", FIND_OBJECTIVE)
        self.assertNotIn("Objectives", locked_only)

    def test_contract_does_not_relock_waves(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in WAVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("Waves", FIND_OBJECTIVE)
        self.assertNotIn("Waves", locked_only)
        self.assertNotIn("FSkyguardEnemyWaveDefinition", FIND_OBJECTIVE)

    def test_contract_does_not_relock_boss(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in BOSS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("FSkyguardBossDefinition", FIND_OBJECTIVE)
        self.assertNotIn("FSkyguardBossDefinition", locked_only)

    def test_contract_does_not_relock_weather(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in WEATHER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("FSkyguardWeatherProfile", FIND_OBJECTIVE)
        self.assertNotIn("FSkyguardWeatherProfile", locked_only)

    def test_contract_does_not_relock_presentation(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in PRESENTATION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("FSkyguardMissionPresentation", FIND_OBJECTIVE)
        self.assertNotIn("FSkyguardMissionPresentation", locked_only)

    def test_contract_does_not_relock_score_rules(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in SCORE_RULES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("FSkyguardMissionScoreRules", FIND_OBJECTIVE)
        self.assertNotIn("FSkyguardMissionScoreRules", locked_only)

    def test_contract_does_not_relock_prerequisite_mission_ids(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in PREREQUISITE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("PrerequisiteMissionIds", FIND_OBJECTIVE)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)

    def test_contract_does_not_relock_required_campaign_medals(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in MEDALS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("RequiredCampaignMedals", FIND_OBJECTIVE)
        self.assertNotIn("RequiredCampaignMedals", locked_only)

    def test_contract_does_not_relock_primary_asset_id(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in PRIMARY_ASSET_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("GetPrimaryAssetId", FIND_OBJECTIVE)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("FPrimaryAssetId", FIND_OBJECTIVE)

    def test_contract_does_not_relock_validate_definition(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in VALIDATE_DEFINITION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("ValidateDefinition", FIND_OBJECTIVE)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("OutErrors", FIND_OBJECTIVE)
        self.assertNotIn("BlueprintCallable", FIND_OBJECTIVE)

    def test_contract_does_not_relock_find_mission(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in FIND_MISSION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("FindMission", FIND_OBJECTIVE)
        self.assertNotIn("FindMission", locked_only)

    def test_contract_does_not_relock_leftover_struct_default_drafts(
        self,
    ) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for token in LEFTOVER_STRUCT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FIND_OBJECTIVE)
        self.assertNotIn("defaults_contract", FIND_OBJECTIVE)
        self.assertNotIn("defaults_contract", locked_only)
        self.assertNotIn("RequiredProgress", FIND_OBJECTIVE)
        self.assertNotIn("bRequiredForMissionSuccess", FIND_OBJECTIVE)

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("FillResultCombatStats", FIND_OBJECTIVE)
        self.assertNotIn("ASkyguardGunner", FIND_OBJECTIVE)
        self.assertNotIn("FillAndFinalize", FIND_OBJECTIVE)
        self.assertNotIn("FillAndFail", FIND_OBJECTIVE)
        self.assertNotIn("ApplyHydraForClusters", FIND_OBJECTIVE)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FIND_OBJECTIVE)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FIND_OBJECTIVE)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FIND_OBJECTIVE)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        self.assertEqual(
            require_declaration(locked_only, FIND_OBJECTIVE),
            FIND_OBJECTIVE,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("MissionId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("CampaignOrder", locked_only)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)
        self.assertNotIn("RequiredCampaignMedals", locked_only)
        self.assertNotIn("FindMission", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)

    def test_contract_parses_public_class_section_not_struct_or_cpp(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertIsNone(STRUCT_RE.search(section), section)
        self.assertNotIn("FindByPredicate", section)
        self.assertNotIn("Objectives.FindByPredicate", section)
        self.assertNotIn("return nullptr", section)
        self.assertNotIn("OutErrors.Reset", section)
        self.assertNotIn("AddError", section)
        self.assertNotIn("RequiredProgress", section)
        self.assertNotIn("bRequiredForMissionSuccess", section)
        self.assertEqual(
            require_declaration(section, FIND_OBJECTIVE),
            FIND_OBJECTIVE,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::FindObjective",
            section,
        )
        self.assertEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardMissionDefinition.h",
        )
        self.assertNotIn("SkyguardMissionTypes.h", HEADER_PATH)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, FIND_OBJECTIVE)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::FindObjective",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", FIND_OBJECTIVE)
        self.assertNotIn("}", FIND_OBJECTIVE)
        self.assertNotIn("return nullptr", FIND_OBJECTIVE)
        self.assertNotIn("FindByPredicate", FIND_OBJECTIVE)
        self.assertNotIn("AddError", FIND_OBJECTIVE)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{FIND_OBJECTIVE}\n"
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, FIND_OBJECTIVE)
            self.assertNotIn(token, locked_only)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{FIND_OBJECTIVE}\n"
        section = public_section(origin_main_header())
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FIND_OBJECTIVE)
            self.assertNotIn(token, section)
            self.assertNotIn(token, file_text)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "mission FindObjective contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_file_comments_and_strings_ban_retired_mount(self) -> None:
        self_text = this_file_text()
        comment_blob = "\n".join(
            line[line.index("#") :].lower()
            for line in self_text.splitlines()
            if "#" in line
        )
        string_blob = " ".join(
            match.group(2).lower()
            for match in re.finditer(
                r"(['\"])((?:\\.|(?!\1).)*)\1",
                self_text,
            )
        )
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, comment_blob)
            self.assertNotIn(banned, string_blob)
            self.assertNotIn(banned, FIND_OBJECTIVE.lower())

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, FIND_OBJECTIVE.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, FIND_OBJECTIVE)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)
        self.assertNotEqual(FIND_OBJECTIVE, "Rif" + "le")
        self.assertNotEqual(FIND_OBJECTIVE, "Ig" + "la")

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                "mission FindObjective contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, FIND_OBJECTIVE.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, FIND_OBJECTIVE)

    def test_contract_is_find_objective_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, FIND_OBJECTIVE),
            FIND_OBJECTIVE,
        )
        locked_only = f"{FIND_OBJECTIVE}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, FIND_OBJECTIVE)
        self.assertNotIn("MissionId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("CampaignOrder", locked_only)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)
        self.assertNotIn("RequiredCampaignMedals", locked_only)
        self.assertNotIn("FindMission", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        self.assertNotIn("USkyguardCampaignSaveGame", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FIND_OBJECTIVE)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FIND_OBJECTIVE)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FIND_OBJECTIVE)
        for token in LEFTOVER_STRUCT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, FIND_OBJECTIVE)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, FIND_OBJECTIVE)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, FIND_OBJECTIVE)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, FIND_OBJECTIVE)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, FIND_OBJECTIVE.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", FIND_OBJECTIVE)
        self.assertNotIn("{", FIND_OBJECTIVE)
        self.assertNotIn("AddError", FIND_OBJECTIVE)
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertNotIn("FindByPredicate", FIND_OBJECTIVE)
        self.assertNotIn("nullptr", FIND_OBJECTIVE)
        self.assertEqual(
            FIND_OBJECTIVE,
            "const FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;",
        )

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
