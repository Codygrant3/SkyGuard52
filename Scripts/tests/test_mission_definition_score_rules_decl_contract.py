from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMissionDefinition.h"
TYPES_HEADER_PATH = "Source/Skyguard52/SkyguardMissionTypes.h"
CLASS_NAME = "USkyguardMissionDefinition"
# Declaration presence only. Do not invent INDEX_NONE,
# a score-rules body, leftover CompletionScore /
# PerfectAccuracyBonus, leftover mission-result
# defaults, or lock ScoreRules in the .cpp.
# origin/main is one line
# (`FSkyguardMissionScoreRules ScoreRules;`); accept
# that form and other split-line wraps. Nearby
# UPROPERTY metadata is present on origin/main; do not
# invent metadata that is not in origin/main. Parse the
# public class section of USkyguardMissionDefinition
# only. Do not parse the FSkyguardMissionScoreRules
# struct body. Leftover mission-score-rules defaults
# #deae lock those struct fields, not this class field.
# Leftover mission-result defaults #c4db stay
# sibling-only.
SCORE_RULES = "FSkyguardMissionScoreRules ScoreRules;"
UPROPERTY_SCORING = (
    'UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Scoring")'
)
# Leftover #56–#64 plus MissionDefinition production files.
# This lane only adds an isolated Python ScoreRules field
# declaration contract. Stay off MissionId #350,
# DisplayName #351, CampaignOrder #352, MissionMap #353,
# Route #354, Objectives #355, Waves #356, Weather, Boss
# (in-flight sibling), Presentation (in-flight sibling),
# PrerequisiteMissionIds, RequiredCampaignMedals,
# GetPrimaryAssetId, ValidateDefinition, and
# FindObjective on this class. Stay off leftover
# objective-definition defaults #b29f, leftover
# enemy-wave defaults #dc07, leftover boss-definition
# defaults #cc27, leftover weather-profile defaults
# #7dd0, leftover mission-presentation defaults #157e,
# leftover mission-score-rules defaults #deae (struct
# fields, not this class field), leftover
# route-definition fields #dbff, leftover
# mission-result defaults #c4db. Stay off leftover
# campaign-roster #111, leftover campaign-save
# empty-fail-closed, leftover campaign definition
# CampaignId / DisplayName / Missions, leftover CPG
# debrief #284/#195/#130/#8ccd, leftover Gunner helpers,
# leftover Harbor #6/#8/#9, leftover theater-kit #59,
# leftover flare/HUD #57/#61/#62, leftover drafts
# #56–#64, leftover #147 ApacheSystem, leftover #149
# weapon stations, leftover #152 pilot commands,
# leftover #154 loadout / lock-phase, leftover settings
# invert-look / ApplySettings broadcast #134, leftover
# bind-hud-host, leftover objective-runtime fail-closed,
# leftover route-runtime fail-closed, leftover pilot
# #117/#120/#128/#129/#170, leftover gun-fire camera
# shake #8860, leftover mission-weather enum #96d2,
# leftover mission 0N integration readiness, and dirty
# workspace paths.
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
# campaign-roster lookup, leftover campaign-save
# empty-fail-closed, leftover objective / route /
# mission-score / weather / boss / wave / presentation
# defaults, leftover mission-result defaults, leftover
# campaign definition CampaignId / DisplayName /
# Missions, leftover CPG debrief, leftover
# objective-runtime / route-runtime fail-closed,
# leftover theater-kit / Harbor / flare / HUD, leftover
# ApacheSystem / weapon stations / pilot commands /
# loadout, leftover settings invert-look, leftover
# bind-hud-host, leftover pilot drafts, leftover
# gun-fire camera shake, leftover mission-weather enum,
# and in-flight MissionId #350 / DisplayName /
# CampaignOrder / MissionMap / Route / Objectives /
# Waves / Weather / Boss / Presentation stay
# sibling-only.
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
    "Scripts/tests/test_campaign_definition_display_name_decl_contract.py",
    "Scripts/tests/test_campaign_definition_campaign_id_decl_contract.py",
    "Scripts/tests/test_campaign_definition_missions_decl_contract.py",
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
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_enemy_wave_defaults_contract.py",
    "Scripts/tests/test_boss_definition_defaults_contract.py",
    "Scripts/tests/test_weather_profile_defaults_contract.py",
    "Scripts/tests/test_mission_presentation_defaults_contract.py",
    "Scripts/tests/test_mission_score_rules_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_route_definition_fields_contract.py",
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
    "Scripts/tests/test_pilot_confirm_command_decl_contract.py",
    "Scripts/tests/test_pilot_confirm_line_contract.py",
    "Scripts/tests/test_pilot_get_last_called_line_decl_contract.py",
    "Scripts/tests/test_pilot_get_last_called_text_decl_contract.py",
    "Scripts/tests/test_pilot_make_radio_line_decl_contract.py",
    "Scripts/tests/test_pilot_line_text_for_event_decl_contract.py",
    "Scripts/tests/test_pilot_warn_lock_reload_contract.py",
    "Scripts/tests/test_pilot_voice_call_probe.py",
    "Scripts/tests/test_pilot_voice_duration_tests.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
    "Scripts/tests/test_gunship_types_loadout_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
    "Scripts/tests/test_bind_hud_host_presentation_tests.py",
    "Scripts/tests/test_gun_fire_camera_shake_tests.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
)
# Neighbors in the same public section. Presence is not locked
# here. MissionId #350 / DisplayName / CampaignOrder /
# MissionMap / Route / Objectives / Waves / Boss /
# Weather / Presentation / PrerequisiteMissionIds /
# RequiredCampaignMedals / GetPrimaryAssetId /
# ValidateDefinition / FindObjective stay sibling-only.
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
    "TArray<FName> PrerequisiteMissionIds;",
    "int32 RequiredCampaignMedals = 0;",
    "virtual FPrimaryAssetId GetPrimaryAssetId() const override;",
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;",
    "const FSkyguardObjectiveDefinition* FindObjective(FName ObjectiveId) const;",
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
PREREQUISITE_NOT_LOCKED = ("TArray<FName> PrerequisiteMissionIds;",)
MEDALS_NOT_LOCKED = ("int32 RequiredCampaignMedals = 0;",)
PRIMARY_ASSET_NOT_LOCKED = (
    "virtual FPrimaryAssetId GetPrimaryAssetId() const override;",
)
VALIDATE_DEFINITION_NOT_LOCKED = (
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;",
)
FIND_OBJECTIVE_NOT_LOCKED = (
    "const FSkyguardObjectiveDefinition* FindObjective(FName ObjectiveId) const;",
)
# USkyguardCampaignDefinition / USkyguardCampaignSaveGame
# identity fields stay unlocked. This lane is ScoreRules
# on USkyguardMissionDefinition only.
DEFINITION_NOT_LOCKED = (
    'FName CampaignId = TEXT("Skyguard52MainCampaign");',
    "USkyguardCampaignDefinition",
    "TArray<TObjectPtr<USkyguardMissionDefinition>> Missions",
)
SAVE_GAME_CAMPAIGN_ID_NOT_LOCKED = (
    "USkyguardCampaignSaveGame",
)
# Leftover struct-default drafts stay unlocked. Those
# leftover drafts lock struct defaults, not this class
# field. Leftover mission-score-rules defaults #deae
# lock CompletionScore / PerfectAccuracyBonus on the
# struct, not this class field. Leftover mission-result
# defaults #c4db lock result fields, not this class
# field.
LEFTOVER_STRUCT_DEFAULTS_NOT_LOCKED = (
    "test_objective_definition_defaults_contract.py",
    "test_enemy_wave_defaults_contract.py",
    "test_boss_definition_defaults_contract.py",
    "test_weather_profile_defaults_contract.py",
    "test_mission_presentation_defaults_contract.py",
    "test_mission_score_rules_defaults_contract.py",
    "test_mission_result_defaults_contract.py",
    "test_route_definition_fields_contract.py",
)
LEFTOVER_SCORE_RULES_STRUCT_FIELDS_NOT_LOCKED = (
    "int32 CompletionScore = 5000;",
    "int32 PerfectAccuracyBonus = 2500;",
    "int32 NoDamageBonus = 1500;",
    "int32 BronzeThreshold = 5000;",
    "int32 SilverThreshold = 8000;",
    "int32 GoldThreshold = 11000;",
)
LEFTOVER_MISSION_RESULT_NOT_LOCKED = (
    "test_mission_result_defaults_contract.py",
    "bool bMissionSucceeded = false;",
    "int32 ShotsFired = 0;",
    "int32 Hits = 0;",
    "float AircraftDamageFraction = 0.f;",
    "float CompletionTimeSeconds = 0.f;",
    "TArray<FName> CompletedObjectiveIds;",
    "int32 FinalScore = 0;",
    "int32 MedalTier = 0;",
)
FILL_AND_GUNNER_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
    "FillAndFinalize",
    "FillAndFail",
    "ApplyHydraForClusters",
)
# Leftover CPG debrief copy / snapshot defaults /
# fail-closed / empty-capture stay unlocked.
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
# Leftover ApacheSystem / weapon stations / pilot
# commands / loadout / lock-phase / invert-look /
# ApplySettings / leftover Gunner FillAnd* stay unlocked.
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
)
# Invented UPROPERTY specifiers that are not on origin/main
# for this field. Nearby origin/main metadata is
# EditAnywhere, BlueprintReadOnly, Category = "Scoring".
# Do not invent extra specifiers. Neighbor fields may use
# ClampMin meta; that is not locked here.
INVENTED_UPROPERTY = (
    "BlueprintReadWrite",
    "VisibleAnywhere",
    "VisibleDefaultsOnly",
    "EditDefaultsOnly",
    "SaveGame",
    'Category = "Campaign"',
    'Category = "Campaign|Id"',
    "AllowPrivateAccess",
)
INVENTED_FIELD_META = (
    "meta =",
)
# .cpp ScoreRules body / invented INDEX_NONE stay unlocked.
# Do not invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "USkyguardMissionDefinition::ScoreRules",
    "SkyguardMissionDefinition.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
)
CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")


def leftover_harbor_tokens() -> tuple[str, ...]:
    incoming = "Incoming" + "Radar"
    forty = "40" + ".f"
    eighty = "80" + ".f"
    return (
        incoming,
        incoming + "LiveIntervalSeconds",
        incoming + "DownIntervalSeconds",
        forty,
        eighty,
        forty + ", " + eighty,
    )


def leftover_live_copy_tokens() -> tuple[str, ...]:
    return ("ig" + "la", "ya" + "k", "ri" + "fle")


def leftover_readiness_tokens() -> tuple[str, ...]:
    return (
        "b" + "Ya" + "kRuntimeReady",
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


class MissionDefinitionScoreRulesDeclContractTests(unittest.TestCase):
    def test_mission_definition_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, SCORE_RULES), section)

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
            f"\t{SCORE_RULES}\n"
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
            '\tFName CampaignId = TEXT("Skyguard52MainCampaign");\n'
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(definition)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_save_game_class_does_not_satisfy(self) -> None:
        save_game = (
            "class SKYGUARD52_API USkyguardCampaignSaveGame "
            ": public USaveGame\n"
            "{\n"
            "public:\n"
            "\tFName CampaignId;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(save_game)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_score_rules_struct_does_not_satisfy_class(self) -> None:
        struct_only = (
            "USTRUCT(BlueprintType)\n"
            "struct FSkyguardMissionScoreRules\n"
            "{\n"
            "\tGENERATED_BODY()\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadOnly)\n"
            "\tint32 CompletionScore = 5000;\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadOnly)\n"
            "\tint32 PerfectAccuracyBonus = 2500;\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadOnly)\n"
            "\tint32 NoDamageBonus = 1500;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(struct_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(struct_only, SCORE_RULES)
        self.assertIn("ScoreRules", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "private:\n"
            f"\t{SCORE_RULES}\n"
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
            "\tFName MissionId;\n"
            "private:\n"
            f"\t{SCORE_RULES}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, SCORE_RULES)
        self.assertIn("ScoreRules", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, SCORE_RULES))

    def test_missing_score_rules_declaration_fails_closed(self) -> None:
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
            "\tTArray<FName> PrerequisiteMissionIds;\n"
            "\tint32 RequiredCampaignMedals = 0;\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() "
            "const override;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, SCORE_RULES)
        self.assertIn("ScoreRules", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_SCORING}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, SCORE_RULES)
        self.assertIn("ScoreRules", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_SCORING, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('Category = "Scoring"', section)
        self.assertTrue(has_declaration(section, SCORE_RULES), section)
        self.assertNotIn("UPROPERTY", SCORE_RULES)
        self.assertNotIn("EditAnywhere", SCORE_RULES)
        self.assertNotIn("BlueprintReadOnly", SCORE_RULES)
        self.assertNotIn("Category", SCORE_RULES)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_SCORING)
            self.assertNotIn(invented, SCORE_RULES)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, UPROPERTY_SCORING)
            self.assertNotIn(invented, SCORE_RULES)

    def test_neighbor_fields_do_not_satisfy(self) -> None:
        other_fields = (
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
            "\tTArray<FName> PrerequisiteMissionIds;\n"
            "\tint32 RequiredCampaignMedals = 0;\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() "
            "const override;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_fields, SCORE_RULES)
        self.assertIn("ScoreRules", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        assigned = "\tFSkyguardMissionScoreRules ScoreRules = {};\n"
        name_type = "\tFName ScoreRules;\n"
        text_type = "\tFText ScoreRules;\n"
        int_type = "\tint32 ScoreRules;\n"
        leftover_completion = "\tint32 CompletionScore = 5000;\n"
        leftover_perfect = "\tint32 PerfectAccuracyBonus = 2500;\n"
        leftover_result = "\tint32 FinalScore = 0;\n"
        score_rules_id = "\tFSkyguardMissionScoreRules ScoreRulesId;\n"
        mission_id = "\tFName MissionId;\n"
        display_name = "\tFText DisplayName;\n"
        weather = "\tFSkyguardWeatherProfile Weather;\n"
        for region in (
            assigned,
            name_type,
            text_type,
            int_type,
            leftover_completion,
            leftover_perfect,
            leftover_result,
            score_rules_id,
            mission_id,
            display_name,
            weather,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, SCORE_RULES)
            self.assertIn("ScoreRules", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_score_rules_struct_fields_do_not_satisfy(self) -> None:
        leftover = (
            "\tint32 CompletionScore = 5000;\n"
            "\tint32 PerfectAccuracyBonus = 2500;\n"
            "\tint32 NoDamageBonus = 1500;\n"
            "\tint32 BronzeThreshold = 5000;\n"
            "\tint32 SilverThreshold = 8000;\n"
            "\tint32 GoldThreshold = 11000;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(leftover, SCORE_RULES)
        self.assertIn("ScoreRules", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(leftover, SCORE_RULES))

    def test_leftover_mission_result_fields_do_not_satisfy(self) -> None:
        leftover = (
            "\tbool bMissionSucceeded = false;\n"
            "\tint32 ShotsFired = 0;\n"
            "\tint32 Hits = 0;\n"
            "\tfloat AircraftDamageFraction = 0.f;\n"
            "\tfloat CompletionTimeSeconds = 0.f;\n"
            "\tTArray<FName> CompletedObjectiveIds;\n"
            "\tint32 FinalScore = 0;\n"
            "\tint32 MedalTier = 0;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(leftover, SCORE_RULES)
        self.assertIn("ScoreRules", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(leftover, SCORE_RULES))

    def test_assigned_score_rules_does_not_satisfy(self) -> None:
        assigned = "\tFSkyguardMissionScoreRules ScoreRules = {};\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(assigned, SCORE_RULES)
        self.assertIn("ScoreRules", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(assigned, SCORE_RULES))

    def test_score_rules_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, SCORE_RULES),
            SCORE_RULES,
        )
        self.assertTrue(has_declaration(section, SCORE_RULES))
        self.assertEqual(
            declaration_count(section, SCORE_RULES),
            1,
        )
        self.assertTrue(
            SCORE_RULES.endswith(";"),
            SCORE_RULES,
        )
        self.assertTrue(
            SCORE_RULES.startswith("FSkyguardMissionScoreRules "),
            SCORE_RULES,
        )
        self.assertIn("ScoreRules", SCORE_RULES)
        self.assertNotIn("=", SCORE_RULES)
        self.assertNotIn("TEXT(", SCORE_RULES)
        self.assertNotIn("INDEX_NONE", SCORE_RULES)
        self.assertNotIn("NAME_None", SCORE_RULES)
        self.assertNotIn("UFUNCTION", SCORE_RULES)
        self.assertNotIn("{", SCORE_RULES)
        self.assertNotIn("}", SCORE_RULES)
        self.assertNotIn("return ", SCORE_RULES)
        self.assertNotIn("CompletionScore", SCORE_RULES)
        self.assertNotIn("PerfectAccuracyBonus", SCORE_RULES)
        self.assertNotIn("FinalScore", SCORE_RULES)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_name = (
            "public:\n"
            "\tFSkyguardMissionScoreRules\n"
            "\tScoreRules;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tFSkyguardMissionScoreRules   ScoreRules;\n"
            "private:\n"
            "};\n"
        )
        wrap_tab = (
            "public:\n"
            "\tFSkyguardMissionScoreRules\tScoreRules;\n"
            "};\n"
        )
        wrap_indent = (
            "public:\n"
            "\tFSkyguardMissionScoreRules\n"
            "\t\tScoreRules;\n"
            "};\n"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_name}"
        )
        header_wrap_spaces = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_spaces}"
        )
        header_wrap_tab = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_tab}"
        )
        header_wrap_indent = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_indent}"
        )
        for header in (
            header_wrap_name,
            header_wrap_spaces,
            header_wrap_tab,
            header_wrap_indent,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, SCORE_RULES),
                section,
            )
            self.assertEqual(
                require_declaration(section, SCORE_RULES),
                SCORE_RULES,
            )
            self.assertEqual(
                declaration_count(section, SCORE_RULES),
                1,
            )
        one_line = f"{{\npublic:\n\t{SCORE_RULES}\n}}\n"
        self.assertTrue(has_declaration(one_line, SCORE_RULES))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, SCORE_RULES), section)
        self.assertEqual(
            require_declaration(section, SCORE_RULES),
            SCORE_RULES,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", SCORE_RULES)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", SCORE_RULES)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, SCORE_RULES)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_SCORING)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, SCORE_RULES)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_SCORING)
        section = public_section(origin_main_header())
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, section)
        self.assertIn(UPROPERTY_SCORING, section)

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        self.assertNotIn("UFUNCTION", SCORE_RULES)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(SCORE_RULES.startswith("UFUNCTION"), SCORE_RULES)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, SCORE_RULES), section)
        self.assertEqual(
            require_declaration(section, SCORE_RULES),
            SCORE_RULES,
        )

    def test_contract_does_not_lock_score_rules_cpp_body(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        self.assertNotIn("{", SCORE_RULES)
        self.assertNotIn("}", SCORE_RULES)
        self.assertNotIn("return ", SCORE_RULES)
        self.assertNotIn(
            "USkyguardMissionDefinition::ScoreRules",
            SCORE_RULES,
        )
        self.assertNotIn(
            "SkyguardMissionDefinition.cpp",
            SCORE_RULES,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", locked_only)
        self.assertNotIn("return false", SCORE_RULES)
        self.assertNotIn("AddError", SCORE_RULES)

    def test_contract_does_not_parse_score_rules_struct_body(
        self,
    ) -> None:
        locked_only = f"{SCORE_RULES}\n"
        self.assertEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardMissionDefinition.h",
        )
        self.assertNotEqual(HEADER_PATH, TYPES_HEADER_PATH)
        self.assertNotIn("SkyguardMissionTypes.h", HEADER_PATH)
        self.assertNotIn("int32 CompletionScore = 5000;", SCORE_RULES)
        self.assertNotIn("int32 CompletionScore = 5000;", locked_only)
        self.assertNotIn("CompletionScore", SCORE_RULES)
        self.assertNotIn("CompletionScore", locked_only)
        self.assertNotIn("PerfectAccuracyBonus", SCORE_RULES)
        self.assertNotIn("NoDamageBonus", SCORE_RULES)
        self.assertNotIn("BronzeThreshold", SCORE_RULES)
        self.assertNotIn("SilverThreshold", SCORE_RULES)
        self.assertNotIn("GoldThreshold", SCORE_RULES)
        self.assertNotIn("GENERATED_BODY()", SCORE_RULES)
        section = public_section(origin_main_header())
        self.assertNotIn("int32 CompletionScore = 5000;", section)
        self.assertNotIn("int32 PerfectAccuracyBonus = 2500;", section)
        self.assertNotIn("int32 NoDamageBonus = 1500;", section)
        self.assertNotIn("int32 BronzeThreshold = 5000;", section)
        self.assertNotIn("int32 SilverThreshold = 8000;", section)
        self.assertNotIn("int32 GoldThreshold = 11000;", section)
        self.assertTrue(has_declaration(section, SCORE_RULES), section)

    def test_contract_does_not_relock_mission_id(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in MISSION_ID_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("MissionId", SCORE_RULES)
        self.assertNotIn("MissionId", locked_only)
        self.assertNotIn("FName", SCORE_RULES)

    def test_contract_does_not_relock_display_name(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in DISPLAY_NAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("DisplayName", SCORE_RULES)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("FText", SCORE_RULES)

    def test_contract_does_not_relock_campaign_order(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in CAMPAIGN_ORDER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("CampaignOrder", SCORE_RULES)
        self.assertNotIn("CampaignOrder", locked_only)

    def test_contract_does_not_relock_mission_map(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in MISSION_MAP_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("MissionMap", SCORE_RULES)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("TSoftObjectPtr", SCORE_RULES)

    def test_contract_does_not_relock_route(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in ROUTE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("FSkyguardRouteDefinition", SCORE_RULES)
        self.assertNotIn("FSkyguardRouteDefinition", locked_only)

    def test_contract_does_not_relock_objectives(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in OBJECTIVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("Objectives", SCORE_RULES)
        self.assertNotIn("Objectives", locked_only)
        self.assertNotIn("FSkyguardObjectiveDefinition", SCORE_RULES)

    def test_contract_does_not_relock_waves(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in WAVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("Waves", SCORE_RULES)
        self.assertNotIn("Waves", locked_only)
        self.assertNotIn("FSkyguardEnemyWaveDefinition", SCORE_RULES)

    def test_contract_does_not_relock_boss(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in BOSS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("FSkyguardBossDefinition", SCORE_RULES)
        self.assertNotIn("FSkyguardBossDefinition", locked_only)

    def test_contract_does_not_relock_weather(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in WEATHER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("FSkyguardWeatherProfile", SCORE_RULES)
        self.assertNotIn("FSkyguardWeatherProfile", locked_only)

    def test_contract_does_not_relock_presentation(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in PRESENTATION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("FSkyguardMissionPresentation", SCORE_RULES)
        self.assertNotIn("FSkyguardMissionPresentation", locked_only)

    def test_contract_does_not_relock_prerequisite_mission_ids(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in PREREQUISITE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("PrerequisiteMissionIds", SCORE_RULES)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)

    def test_contract_does_not_relock_required_campaign_medals(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in MEDALS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("RequiredCampaignMedals", SCORE_RULES)
        self.assertNotIn("RequiredCampaignMedals", locked_only)

    def test_contract_does_not_relock_primary_asset_id(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in PRIMARY_ASSET_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("GetPrimaryAssetId", SCORE_RULES)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("FPrimaryAssetId", SCORE_RULES)

    def test_contract_does_not_relock_validate_definition(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in VALIDATE_DEFINITION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("ValidateDefinition", SCORE_RULES)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("OutErrors", SCORE_RULES)
        self.assertNotIn("BlueprintCallable", SCORE_RULES)

    def test_contract_does_not_relock_find_objective(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in FIND_OBJECTIVE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("FindObjective", SCORE_RULES)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("ObjectiveId", SCORE_RULES)

    def test_contract_does_not_relock_campaign_definition_fields(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        section = public_section(origin_main_header())
        for token in DEFINITION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
            self.assertNotIn(token, section)
        self.assertNotIn("Skyguard52MainCampaign", SCORE_RULES)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", SCORE_RULES)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        for token in SAVE_GAME_CAMPAIGN_ID_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_struct_default_drafts(
        self,
    ) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for token in LEFTOVER_STRUCT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
        self.assertNotIn("defaults_contract", SCORE_RULES)
        self.assertNotIn("defaults_contract", locked_only)
        self.assertNotIn(
            "test_mission_score_rules_defaults_contract.py",
            SCORE_RULES,
        )
        self.assertNotIn(
            "test_mission_score_rules_defaults_contract.py",
            locked_only,
        )
        self.assertNotIn(
            "test_mission_result_defaults_contract.py",
            SCORE_RULES,
        )
        self.assertNotIn(
            "test_mission_result_defaults_contract.py",
            locked_only,
        )
        self.assertNotIn("test_route_definition_fields_contract.py", SCORE_RULES)
        self.assertNotIn(
            "test_route_definition_fields_contract.py",
            locked_only,
        )

    def test_contract_does_not_relock_leftover_score_rules_struct_fields(
        self,
    ) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for token in LEFTOVER_SCORE_RULES_STRUCT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
        self.assertNotIn("CompletionScore", SCORE_RULES)
        self.assertNotIn("CompletionScore", locked_only)
        self.assertNotIn("PerfectAccuracyBonus", SCORE_RULES)
        self.assertNotIn("PerfectAccuracyBonus", locked_only)
        self.assertNotIn("NoDamageBonus", SCORE_RULES)
        self.assertNotIn("NoDamageBonus", locked_only)
        self.assertNotIn("BronzeThreshold", SCORE_RULES)
        self.assertNotIn("BronzeThreshold", locked_only)
        self.assertNotIn("SilverThreshold", SCORE_RULES)
        self.assertNotIn("SilverThreshold", locked_only)
        self.assertNotIn("GoldThreshold", SCORE_RULES)
        self.assertNotIn("GoldThreshold", locked_only)

    def test_contract_does_not_relock_leftover_mission_result_defaults(
        self,
    ) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for token in LEFTOVER_MISSION_RESULT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
        self.assertNotIn("bMissionSucceeded", SCORE_RULES)
        self.assertNotIn("bMissionSucceeded", locked_only)
        self.assertNotIn("FinalScore", SCORE_RULES)
        self.assertNotIn("FinalScore", locked_only)
        self.assertNotIn("MedalTier", SCORE_RULES)
        self.assertNotIn("MedalTier", locked_only)
        self.assertNotIn(
            "test_mission_result_defaults_contract.py",
            SCORE_RULES,
        )
        self.assertNotIn(
            "test_mission_result_defaults_contract.py",
            locked_only,
        )

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("FillResultCombatStats", SCORE_RULES)
        self.assertNotIn("ASkyguardGunner", SCORE_RULES)
        self.assertNotIn("FillAndFinalize", SCORE_RULES)
        self.assertNotIn("FillAndFail", SCORE_RULES)
        self.assertNotIn("ApplyHydraForClusters", SCORE_RULES)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{SCORE_RULES}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{SCORE_RULES}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        self.assertEqual(
            require_declaration(locked_only, SCORE_RULES),
            SCORE_RULES,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("MissionId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("CampaignOrder", locked_only)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)
        self.assertNotIn("RequiredCampaignMedals", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("OutErrors.Reset", section)
        self.assertNotIn("AddError", section)
        self.assertEqual(
            require_declaration(section, SCORE_RULES),
            SCORE_RULES,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::ScoreRules",
            section,
        )
        self.assertNotIn("int32 CompletionScore = 5000;", section)
        self.assertNotIn("int32 PerfectAccuracyBonus = 2500;", section)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SCORE_RULES)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::ScoreRules",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", SCORE_RULES)
        self.assertNotIn("}", SCORE_RULES)
        self.assertNotIn("return false", SCORE_RULES)
        self.assertNotIn("AddError", SCORE_RULES)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{SCORE_RULES}\n"
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, SCORE_RULES)
            self.assertNotIn(token, locked_only)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{SCORE_RULES}\n"
        section = public_section(origin_main_header())
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
            self.assertNotIn(token, section)
            self.assertNotIn(token, file_text)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "mission ScoreRules contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, SCORE_RULES.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, SCORE_RULES)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"mission ScoreRules contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, SCORE_RULES.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, SCORE_RULES)

    def test_contract_is_score_rules_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, SCORE_RULES),
            SCORE_RULES,
        )
        locked_only = f"{SCORE_RULES}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SCORE_RULES)
        self.assertNotIn("MissionId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("CampaignOrder", locked_only)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)
        self.assertNotIn("RequiredCampaignMedals", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        self.assertNotIn("USkyguardCampaignSaveGame", locked_only)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)
        self.assertNotIn("int32 CompletionScore = 5000;", locked_only)
        self.assertNotIn("int32 PerfectAccuracyBonus = 2500;", locked_only)
        self.assertNotIn("int32 FinalScore = 0;", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
        for token in LEFTOVER_SCORE_RULES_STRUCT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
        for token in LEFTOVER_MISSION_RESULT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SCORE_RULES)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, SCORE_RULES)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, SCORE_RULES)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SCORE_RULES)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, SCORE_RULES.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", SCORE_RULES)
        self.assertNotIn("{", SCORE_RULES)
        self.assertNotIn("AddError", SCORE_RULES)
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertEqual(SCORE_RULES, "FSkyguardMissionScoreRules ScoreRules;")

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
