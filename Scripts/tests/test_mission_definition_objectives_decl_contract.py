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
# an objectives default, or lock Objectives in the .cpp.
# origin/main is one line
# (`TArray<FSkyguardObjectiveDefinition> Objectives;`);
# accept that form and other split-line wraps. Nearby
# UPROPERTY metadata is present on origin/main; do not
# invent metadata that is not in origin/main.
# Parse the public class section of
# USkyguardMissionDefinition only. Do not parse
# FSkyguardObjectiveDefinition struct body. Leftover
# objective-definition defaults #b29f lock struct fields,
# not this class field.
OBJECTIVES = "TArray<FSkyguardObjectiveDefinition> Objectives;"
UPROPERTY_OBJECTIVES = (
    'UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Objectives")'
)
# Leftover #56–#64 plus MissionDefinition production files.
# This lane only adds an isolated Python Objectives field
# declaration contract. Stay off MissionId #350,
# DisplayName, CampaignOrder, MissionMap (in-flight
# sibling), Route (sibling this wave), Waves, Boss,
# Weather, Presentation, ScoreRules,
# PrerequisiteMissionIds, RequiredCampaignMedals,
# GetPrimaryAssetId, ValidateDefinition, and
# FindObjective on this class. Stay off leftover
# objective-definition defaults #b29f, leftover
# enemy-wave defaults #dc07, leftover boss-definition
# defaults #cc27, leftover weather-profile defaults
# #7dd0, leftover mission-presentation defaults #157e,
# leftover mission-score-rules defaults #deae, leftover
# route-definition fields #dbff, leftover campaign-
# definition fields, leftover campaign-roster #111,
# leftover campaign-save empty-fail-closed,
# leftover CPG debrief #284/#195/#130/#8ccd, leftover
# bind-hud-host, leftover objective-runtime fail-closed,
# leftover route-runtime fail-closed, leftover pilot
# #117/#120/#128/#129/#170, leftover gun-fire camera
# shake #8860, leftover mission-weather enum #96d2,
# FillResultCombatStats / FillAndFinalize / FillAndFail
# / ApplyHydraForClusters, leftover Harbor #6/#8/#9,
# leftover theater-kit #59, leftover flare/HUD
# #57/#61/#62, leftover drafts #56–#64, leftover #147
# ApacheSystem, leftover #149 weapon stations, leftover
# #152 pilot commands, leftover #154 loadout /
# lock-phase, leftover settings invert-look /
# ApplySettings broadcast #134, Harbor leftover clocks,
# leftover live copy, FSkyguardMission0NIntegrationReadiness
# leftover readiness flag, and dirty workspace path.
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
# empty-fail-closed, leftover objective / route /
# mission-score / weather / boss / wave / presentation
# defaults, leftover campaign-definition fields,
# in-flight mission-definition MissionId #350,
# DisplayName, CampaignOrder, leftover CPG debrief,
# leftover objective-runtime / route-runtime
# fail-closed, leftover theater-kit / Harbor /
# flare/HUD, leftover settings invert-look /
# ApplySettings broadcast, leftover bind-hud-host,
# leftover gun-fire camera shake, leftover
# mission-weather enum, leftover pilot siblings,
# leftover #147 / #149 / #152 / #154 stay
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
    "Scripts/tests/test_campaign_definition_campaign_id_decl_contract.py",
    "Scripts/tests/test_campaign_definition_display_name_decl_contract.py",
    "Scripts/tests/test_campaign_definition_missions_decl_contract.py",
    "Scripts/tests/test_mission_definition_mission_id_decl_contract.py",
    "Scripts/tests/test_mission_definition_display_name_decl_contract.py",
    "Scripts/tests/test_mission_definition_campaign_order_decl_contract.py",
    "Scripts/tests/test_mission_definition_mission_map_decl_contract.py",
    "Scripts/tests/test_mission_definition_route_decl_contract.py",
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_enemy_wave_defaults_contract.py",
    "Scripts/tests/test_boss_definition_defaults_contract.py",
    "Scripts/tests/test_weather_profile_defaults_contract.py",
    "Scripts/tests/test_mission_presentation_defaults_contract.py",
    "Scripts/tests/test_mission_score_rules_defaults_contract.py",
    "Scripts/tests/test_route_definition_fields_contract.py",
    "Scripts/tests/test_validate_definition_decl_contract.py",
    "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
    "Scripts/tests/test_find_mission_decl_contract.py",
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
# here. MissionId #350 / DisplayName / CampaignOrder /
# MissionMap / Route / Waves / Boss / Weather /
# Presentation / ScoreRules / PrerequisiteMissionIds /
# RequiredCampaignMedals / GetPrimaryAssetId /
# ValidateDefinition / FindObjective stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "FName MissionId;",
    "FText DisplayName;",
    "int32 CampaignOrder = 1;",
    "TSoftObjectPtr<UWorld> MissionMap;",
    "FSkyguardRouteDefinition Route;",
    "TArray<FSkyguardEnemyWaveDefinition> Waves;",
    "FSkyguardBossDefinition Boss;",
    "FSkyguardWeatherProfile Weather;",
    "FSkyguardMissionPresentation Presentation;",
    "FSkyguardMissionScoreRules ScoreRules;",
    "TArray<FName> PrerequisiteMissionIds;",
    "int32 RequiredCampaignMedals = 0;",
    "virtual FPrimaryAssetId GetPrimaryAssetId() const override;",
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;",
    "const FSkyguardObjectiveDefinition* FindObjective(FName ObjectiveId) const;",
)
MISSION_ID_NOT_LOCKED = (
    "FName MissionId;",
)
DISPLAY_NAME_NOT_LOCKED = (
    "FText DisplayName;",
)
CAMPAIGN_ORDER_NOT_LOCKED = (
    "int32 CampaignOrder = 1;",
)
MISSION_MAP_NOT_LOCKED = (
    "TSoftObjectPtr<UWorld> MissionMap;",
)
ROUTE_NOT_LOCKED = (
    "FSkyguardRouteDefinition Route;",
)
WAVES_NOT_LOCKED = (
    "TArray<FSkyguardEnemyWaveDefinition> Waves;",
)
BOSS_NOT_LOCKED = (
    "FSkyguardBossDefinition Boss;",
)
WEATHER_NOT_LOCKED = (
    "FSkyguardWeatherProfile Weather;",
)
PRESENTATION_NOT_LOCKED = (
    "FSkyguardMissionPresentation Presentation;",
)
SCORE_RULES_NOT_LOCKED = (
    "FSkyguardMissionScoreRules ScoreRules;",
)
PREREQUISITE_NOT_LOCKED = (
    "TArray<FName> PrerequisiteMissionIds;",
)
MEDALS_NOT_LOCKED = (
    "int32 RequiredCampaignMedals = 0;",
)
PRIMARY_ASSET_NOT_LOCKED = (
    "virtual FPrimaryAssetId GetPrimaryAssetId() const override;",
)
VALIDATE_DEFINITION_NOT_LOCKED = (
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;",
)
FIND_OBJECTIVE_NOT_LOCKED = (
    "const FSkyguardObjectiveDefinition* FindObjective(FName ObjectiveId) const;",
)
# Leftover objective-definition defaults #b29f lock
# struct fields on FSkyguardObjectiveDefinition, not
# this class field. Those leftover drafts stay
# unlocked, along with leftover wave / boss / weather /
# presentation / score / route defaults.
LEFTOVER_DEFAULTS_NOT_LOCKED = (
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
    "ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Clear;",
    "float TimeOfDayHours = 12.f;",
    "float WindSpeedMetersPerSecond = 5.f;",
    "float Precipitation = 0.f;",
    "float CloudCoverage = 0.25f;",
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
)
LEFTOVER_OBJECTIVE_DEFAULTS_NOT_LOCKED = (
    "test_objective_definition_defaults_contract.py",
    "FName ObjectiveId;",
    "int32 RequiredProgress = 1;",
    "bool bRequiredForMissionSuccess = true;",
    "bool bFailureEndsMission = false;",
    "int32 ScoreReward = 1000;",
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
    "bInvertLook",
    "ApplySettings",
    "BindHudHost",
    "enum class ESkyguardMissionWeather",
    "ESkyguardPilotLine",
)
# Invented UPROPERTY specifiers that are not on origin/main
# for this field. Nearby origin/main metadata is
# EditAnywhere, BlueprintReadOnly, Category = "Objectives".
# Do not invent extra specifiers. Neighbor fields may use
# ClampMin meta; that is not locked here.
INVENTED_UPROPERTY = (
    "BlueprintReadWrite",
    "VisibleAnywhere",
    "VisibleDefaultsOnly",
    "EditDefaultsOnly",
    "SaveGame",
    'Category = "Campaign"',
    'Category = "Objectives|List"',
    "AllowPrivateAccess",
    "Transient",
    "BlueprintSetter",
)
INVENTED_FIELD_META = (
    "meta =",
)
# Invented objectives defaults are not on origin/main.
# Do not invent an initializer or INDEX_NONE sentinel.
INVENTED_OBJECTIVES_DEFAULT = (
    "INDEX_NONE",
    "NAME_None",
    "{}",
    "TArray()",
)
# .cpp Objectives body / invented INDEX_NONE stay unlocked.
# Do not invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "USkyguardMissionDefinition::Objectives",
    "SkyguardMissionDefinition.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
)
CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")
STRUCT_RE = re.compile(
    r"struct\s+(?:SKYGUARD52_API\s+)?FSkyguardObjectiveDefinition\b"
)


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


class MissionDefinitionObjectivesDeclContractTests(unittest.TestCase):
    def test_mission_definition_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, OBJECTIVES), section)

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
            f"\t{OBJECTIVES}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
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
        self.assertFalse(has_declaration(struct_only, OBJECTIVES))

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "private:\n"
            f"\t{OBJECTIVES}\n"
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
            f"\t{OBJECTIVES}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, OBJECTIVES)
        self.assertIn("Objectives", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, OBJECTIVES))

    def test_missing_objectives_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tFName MissionId;\n"
            "\tFText DisplayName;\n"
            "\tint32 CampaignOrder = 1;\n"
            "\tTSoftObjectPtr<UWorld> MissionMap;\n"
            "\tFSkyguardRouteDefinition Route;\n"
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
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, OBJECTIVES)
        self.assertIn("Objectives", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_OBJECTIVES}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, OBJECTIVES)
        self.assertIn("Objectives", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintCallable, Category = "Mission")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, OBJECTIVES)
        self.assertIn("Objectives", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_OBJECTIVES, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('Category = "Objectives"', section)
        self.assertTrue(has_declaration(section, OBJECTIVES), section)
        self.assertNotIn("UPROPERTY", OBJECTIVES)
        self.assertNotIn("EditAnywhere", OBJECTIVES)
        self.assertNotIn("BlueprintReadOnly", OBJECTIVES)
        self.assertNotIn("Category", OBJECTIVES)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_OBJECTIVES)
            self.assertNotIn(invented, OBJECTIVES)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, UPROPERTY_OBJECTIVES)
            self.assertNotIn(invented, OBJECTIVES)

    def test_declaration_accepts_nearby_origin_main_uproperty(self) -> None:
        nearby = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "public:\n"
            f"\t{UPROPERTY_OBJECTIVES}\n"
            f"\t{OBJECTIVES}\n"
            "};\n"
        )
        section = public_section(nearby)
        self.assertIn(UPROPERTY_OBJECTIVES, section)
        self.assertEqual(
            require_declaration(section, OBJECTIVES),
            OBJECTIVES,
        )

    def test_neighbor_fields_do_not_satisfy(self) -> None:
        other_fields = (
            "\tFName MissionId;\n"
            "\tFText DisplayName;\n"
            "\tint32 CampaignOrder = 1;\n"
            "\tTSoftObjectPtr<UWorld> MissionMap;\n"
            "\tFSkyguardRouteDefinition Route;\n"
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
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_fields, OBJECTIVES)
        self.assertIn("Objectives", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_objective_definition_fields_do_not_satisfy(self) -> None:
        leftover_struct = (
            "\tFName ObjectiveId;\n"
            "\tFText DisplayName;\n"
            "\tint32 RequiredProgress = 1;\n"
            "\tbool bRequiredForMissionSuccess = true;\n"
            "\tbool bFailureEndsMission = false;\n"
            "\tint32 ScoreReward = 1000;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(leftover_struct, OBJECTIVES)
        self.assertIn("Objectives", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(leftover_struct, OBJECTIVES))

    def test_wrong_signature_does_not_satisfy(self) -> None:
        wrong_inner = (
            "\tTArray<FSkyguardEnemyWaveDefinition> Objectives;\n"
        )
        name_type = "\tFName Objectives;\n"
        map_type = (
            "\tTMap<FName, FSkyguardObjectiveDefinition> "
            "Objectives;\n"
        )
        scalar = "\tFSkyguardObjectiveDefinition Objectives;\n"
        wrong_name = (
            "\tTArray<FSkyguardObjectiveDefinition> ObjectiveList;\n"
        )
        assigned = (
            "\tTArray<FSkyguardObjectiveDefinition> "
            "Objectives = {};\n"
        )
        find_objective = (
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        waves = "\tTArray<FSkyguardEnemyWaveDefinition> Waves;\n"
        mission_id = "\tFName MissionId;\n"
        for region in (
            wrong_inner,
            name_type,
            map_type,
            scalar,
            wrong_name,
            assigned,
            find_objective,
            waves,
            mission_id,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, OBJECTIVES)
            self.assertIn("Objectives", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_invented_objectives_assignment_does_not_satisfy(self) -> None:
        assigned = (
            "\tTArray<FSkyguardObjectiveDefinition> "
            "Objectives = {};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(assigned, OBJECTIVES)
        self.assertIn("Objectives", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(assigned, OBJECTIVES))

    def test_wrong_type_does_not_satisfy(self) -> None:
        wrong = "\tTArray<FSkyguardEnemyWaveDefinition> Objectives;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(wrong, OBJECTIVES)
        self.assertIn("Objectives", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(wrong, OBJECTIVES))

    def test_find_objective_does_not_satisfy(self) -> None:
        find_objective = (
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(find_objective, OBJECTIVES)
        self.assertIn("Objectives", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(find_objective, OBJECTIVES))

    def test_objectives_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, OBJECTIVES),
            OBJECTIVES,
        )
        self.assertTrue(has_declaration(section, OBJECTIVES))
        self.assertEqual(
            declaration_count(section, OBJECTIVES),
            1,
        )
        self.assertTrue(
            OBJECTIVES.endswith(";"),
            OBJECTIVES,
        )
        self.assertTrue(
            OBJECTIVES.startswith("TArray<"),
            OBJECTIVES,
        )
        self.assertIn("Objectives", OBJECTIVES)
        self.assertIn("FSkyguardObjectiveDefinition", OBJECTIVES)
        self.assertNotIn("=", OBJECTIVES)
        self.assertNotIn("TEXT(", OBJECTIVES)
        self.assertNotIn("INDEX_NONE", OBJECTIVES)
        self.assertNotIn("NAME_None", OBJECTIVES)
        self.assertNotIn("UFUNCTION", OBJECTIVES)
        self.assertNotIn("{", OBJECTIVES)
        self.assertNotIn("}", OBJECTIVES)
        self.assertNotIn("return ", OBJECTIVES)

    def test_declaration_does_not_invent_objectives_default(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        self.assertNotIn("=", OBJECTIVES)
        self.assertNotIn("TEXT(", OBJECTIVES)
        for invented in INVENTED_OBJECTIVES_DEFAULT:
            self.assertNotIn(invented, OBJECTIVES)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, OBJECTIVES), section)
        self.assertNotIn("NAME_None", OBJECTIVES)
        self.assertNotIn("INDEX_NONE", OBJECTIVES)
        self.assertNotIn("{}", locked_only)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tTArray<FSkyguardObjectiveDefinition>\n"
            "\tObjectives;\n"
            "private:\n"
            "};\n"
        )
        wrap_tabs = (
            "public:\n"
            "\tTArray<FSkyguardObjectiveDefinition>\n"
            "\t\tObjectives;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tTArray<FSkyguardObjectiveDefinition>    "
            "Objectives;\n"
            "};\n"
        )
        wrap_leading = (
            "public:\n"
            "    TArray<FSkyguardObjectiveDefinition> "
            "Objectives;\n"
            "};\n"
        )
        wrap_template = (
            "public:\n"
            "\tTArray<\n"
            "\t\tFSkyguardObjectiveDefinition\n"
            "\t> Objectives;\n"
            "};\n"
        )
        wrap_spaces_in_template = (
            "public:\n"
            "\tTArray < FSkyguardObjectiveDefinition > "
            "Objectives;\n"
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
        header_wrap_spaces_in_template = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_spaces_in_template}"
        )
        for header in (
            header_wrap_type,
            header_wrap_tabs,
            header_wrap_spaces,
            header_wrap_leading,
            header_wrap_template,
            header_wrap_spaces_in_template,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, OBJECTIVES),
                section,
            )
            self.assertEqual(
                require_declaration(section, OBJECTIVES),
                OBJECTIVES,
            )
            self.assertEqual(
                declaration_count(section, OBJECTIVES),
                1,
            )
        one_line = f"{{\npublic:\n\t{OBJECTIVES}\n}}\n"
        self.assertTrue(has_declaration(one_line, OBJECTIVES))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, OBJECTIVES), section)
        self.assertEqual(
            require_declaration(section, OBJECTIVES),
            OBJECTIVES,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", OBJECTIVES)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", OBJECTIVES)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, OBJECTIVES)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_OBJECTIVES)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, OBJECTIVES)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_OBJECTIVES)
        section = public_section(origin_main_header())
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, section)
        self.assertIn(UPROPERTY_OBJECTIVES, section)

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        self.assertNotIn("UFUNCTION", OBJECTIVES)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(OBJECTIVES.startswith("UFUNCTION"), OBJECTIVES)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, OBJECTIVES), section)
        self.assertEqual(
            require_declaration(section, OBJECTIVES),
            OBJECTIVES,
        )

    def test_contract_does_not_lock_objectives_cpp_body(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        self.assertNotIn("{", OBJECTIVES)
        self.assertNotIn("}", OBJECTIVES)
        self.assertNotIn("return ", OBJECTIVES)
        self.assertNotIn(
            "USkyguardMissionDefinition::Objectives",
            OBJECTIVES,
        )
        self.assertNotIn(
            "SkyguardMissionDefinition.cpp",
            OBJECTIVES,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", locked_only)
        self.assertNotIn("return false", OBJECTIVES)
        self.assertNotIn("AddError", OBJECTIVES)

    def test_contract_does_not_relock_mission_id(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in MISSION_ID_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("MissionId", OBJECTIVES)
        self.assertNotIn("MissionId", locked_only)

    def test_contract_does_not_relock_display_name(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in DISPLAY_NAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("DisplayName", OBJECTIVES)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("FText", OBJECTIVES)

    def test_contract_does_not_relock_campaign_order(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in CAMPAIGN_ORDER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("CampaignOrder", OBJECTIVES)
        self.assertNotIn("CampaignOrder", locked_only)

    def test_contract_does_not_relock_mission_map(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in MISSION_MAP_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("MissionMap", OBJECTIVES)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("TSoftObjectPtr", OBJECTIVES)

    def test_contract_does_not_relock_route(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in ROUTE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("FSkyguardRouteDefinition", OBJECTIVES)
        self.assertNotIn("FSkyguardRouteDefinition", locked_only)

    def test_contract_does_not_relock_waves(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in WAVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("Waves", OBJECTIVES)
        self.assertNotIn("Waves", locked_only)
        self.assertNotIn("FSkyguardEnemyWaveDefinition", OBJECTIVES)

    def test_contract_does_not_relock_boss(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in BOSS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("FSkyguardBossDefinition", OBJECTIVES)
        self.assertNotIn("FSkyguardBossDefinition", locked_only)

    def test_contract_does_not_relock_weather(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in WEATHER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("FSkyguardWeatherProfile", OBJECTIVES)
        self.assertNotIn("FSkyguardWeatherProfile", locked_only)

    def test_contract_does_not_relock_presentation(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in PRESENTATION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("FSkyguardMissionPresentation", OBJECTIVES)
        self.assertNotIn("FSkyguardMissionPresentation", locked_only)

    def test_contract_does_not_relock_score_rules(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in SCORE_RULES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("FSkyguardMissionScoreRules", OBJECTIVES)
        self.assertNotIn("FSkyguardMissionScoreRules", locked_only)

    def test_contract_does_not_relock_prerequisite_mission_ids(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in PREREQUISITE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("PrerequisiteMissionIds", OBJECTIVES)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)

    def test_contract_does_not_relock_required_campaign_medals(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in MEDALS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("RequiredCampaignMedals", OBJECTIVES)
        self.assertNotIn("RequiredCampaignMedals", locked_only)

    def test_contract_does_not_relock_primary_asset_id(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in PRIMARY_ASSET_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("GetPrimaryAssetId", OBJECTIVES)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("FPrimaryAssetId", OBJECTIVES)

    def test_contract_does_not_relock_validate_definition(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in VALIDATE_DEFINITION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("ValidateDefinition", OBJECTIVES)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("OutErrors", OBJECTIVES)
        self.assertNotIn("BlueprintCallable", OBJECTIVES)

    def test_contract_does_not_relock_find_objective(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in FIND_OBJECTIVE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("FindObjective", OBJECTIVES)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("ObjectiveId", OBJECTIVES)

    def test_contract_does_not_relock_leftover_defaults(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for token in LEFTOVER_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, OBJECTIVES)
        self.assertNotIn("RequiredProgress", OBJECTIVES)
        self.assertNotIn("ScoreReward", OBJECTIVES)
        self.assertNotIn("ObjectiveId", OBJECTIVES)

    def test_contract_does_not_relock_leftover_objective_definition_defaults(
        self,
    ) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for token in LEFTOVER_OBJECTIVE_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, OBJECTIVES)
        self.assertNotIn("defaults_contract", OBJECTIVES)
        self.assertNotIn("defaults_contract", locked_only)
        self.assertNotIn("RequiredProgress", locked_only)
        self.assertNotIn("bRequiredForMissionSuccess", locked_only)
        self.assertNotIn("bFailureEndsMission", locked_only)
        self.assertNotIn("ScoreReward", locked_only)

    def test_contract_does_not_parse_objective_definition_struct_body(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNone(STRUCT_RE.search(header), header)
        self.assertIsNone(STRUCT_RE.search(section), section)
        self.assertNotIn("RequiredProgress", section)
        self.assertNotIn("bRequiredForMissionSuccess", section)
        self.assertNotIn("bFailureEndsMission", section)
        self.assertNotIn("ScoreReward", section)
        self.assertNotIn("SkyguardMissionTypes.h", OBJECTIVES)
        self.assertNotIn("SkyguardMissionTypes.h", section)
        self.assertEqual(HEADER_PATH, "Source/Skyguard52/SkyguardMissionDefinition.h")
        self.assertNotIn("MissionTypes", HEADER_PATH)
        self.assertTrue(has_declaration(section, OBJECTIVES), section)

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
        self.assertNotIn("FillResultCombatStats", OBJECTIVES)
        self.assertNotIn("ASkyguardGunner", OBJECTIVES)
        self.assertNotIn("FillAndFinalize", OBJECTIVES)
        self.assertNotIn("FillAndFail", OBJECTIVES)
        self.assertNotIn("ApplyHydraForClusters", OBJECTIVES)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{OBJECTIVES}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, OBJECTIVES)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{OBJECTIVES}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, OBJECTIVES)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, OBJECTIVES)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        self.assertEqual(
            require_declaration(locked_only, OBJECTIVES),
            OBJECTIVES,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
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
            require_declaration(section, OBJECTIVES),
            OBJECTIVES,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::Objectives",
            section,
        )
        self.assertIsNone(STRUCT_RE.search(section), section)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, OBJECTIVES)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::Objectives",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", OBJECTIVES)
        self.assertNotIn("}", OBJECTIVES)
        self.assertNotIn("return false", OBJECTIVES)
        self.assertNotIn("AddError", OBJECTIVES)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{OBJECTIVES}\n"
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, OBJECTIVES)
            self.assertNotIn(token, locked_only)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{OBJECTIVES}\n"
        section = public_section(origin_main_header())
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, OBJECTIVES)
            self.assertNotIn(token, section)
            self.assertNotIn(token, file_text)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "mission Objectives contract contains "
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
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, comment_blob)
            self.assertNotIn(banned, OBJECTIVES.lower())

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, OBJECTIVES.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, OBJECTIVES)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)
        self.assertNotEqual(OBJECTIVES, "Rif" + "le")
        self.assertNotEqual(OBJECTIVES, "Ig" + "la")

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"mission Objectives contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, OBJECTIVES.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, OBJECTIVES)

    def test_contract_is_objectives_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, OBJECTIVES),
            OBJECTIVES,
        )
        locked_only = f"{OBJECTIVES}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, OBJECTIVES)
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
        self.assertNotIn("RequiredProgress", locked_only)
        self.assertNotIn("ObjectiveId", locked_only)
        self.assertIsNone(STRUCT_RE.search(header), header)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, OBJECTIVES)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, OBJECTIVES)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, OBJECTIVES)
        for token in LEFTOVER_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, OBJECTIVES)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, OBJECTIVES)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, OBJECTIVES)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, OBJECTIVES)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, OBJECTIVES.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", OBJECTIVES)
        self.assertNotIn("{", OBJECTIVES)
        self.assertNotIn("AddError", OBJECTIVES)
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertEqual(
            OBJECTIVES,
            "TArray<FSkyguardObjectiveDefinition> Objectives;",
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
        self.assertNotIn(
            "Scripts/tests/test_mission_definition_objectives_decl_contract.py",
            LOCKED_SCRIPTS,
        )


if __name__ == "__main__":
    unittest.main()
