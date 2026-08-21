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
# a required-medals body, or lock RequiredCampaignMedals
# in the .cpp. origin/main is one line
# (`int32 RequiredCampaignMedals = 0;`); accept that
# form and other split-line wraps of the field and
# default. Nearby UPROPERTY metadata is present on
# origin/main; do not invent metadata that is not in
# origin/main.
REQUIRED_MEDALS = "int32 RequiredCampaignMedals = 0;"
UPROPERTY_NEARBY = (
    'UPROPERTY(EditAnywhere, BlueprintReadOnly, '
    'Category = "Progression", meta = (ClampMin = "0"))'
)
# Leftover #56–#64 plus MissionDefinition production files.
# This lane only adds an isolated Python
# RequiredCampaignMedals field declaration contract.
# Stay off PrerequisiteMissionIds (sibling this wave),
# MissionId #350, DisplayName #351, CampaignOrder #352,
# MissionMap #353, Route #354, Objectives #355,
# Waves #356, Weather #357, Boss, Presentation,
# ScoreRules (in-flight sibling), GetPrimaryAssetId,
# ValidateDefinition, FindObjective, leftover
# campaign-roster #111, leftover GetEarnedCampaignMedals
# #312, leftover objective-definition defaults #b29f,
# leftover enemy-wave defaults #dc07, leftover
# boss-definition defaults #cc27, leftover
# weather-profile defaults #7dd0, leftover
# mission-presentation defaults #157e, leftover
# mission-score-rules defaults #deae, leftover
# route-definition fields #dbff, leftover campaign-
# definition fields, leftover campaign-save
# empty-fail-closed, leftover CPG debrief
# #284/#195/#130/#8ccd, leftover bind-hud-host,
# leftover objective-runtime fail-closed, leftover
# route-runtime fail-closed, leftover pilot
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
# DisplayName #351, CampaignOrder #352, MissionMap
# #353, Route #354, Objectives #355, Waves #356,
# Weather #357, Boss, Presentation, ScoreRules,
# PrerequisiteMissionIds sibling this wave, leftover
# GetEarnedCampaignMedals #312, leftover CPG debrief,
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
    "Scripts/tests/test_mission_definition_objectives_decl_contract.py",
    "Scripts/tests/test_mission_definition_waves_decl_contract.py",
    "Scripts/tests/test_mission_definition_weather_decl_contract.py",
    "Scripts/tests/test_mission_definition_boss_decl_contract.py",
    "Scripts/tests/test_mission_definition_presentation_decl_contract.py",
    "Scripts/tests/test_mission_definition_score_rules_decl_contract.py",
    "Scripts/tests/test_mission_definition_prerequisite_mission_ids_decl_contract.py",
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
# here. MissionId #350 / DisplayName #351 / CampaignOrder
# #352 / MissionMap #353 / Route #354 / Objectives #355 /
# Waves #356 / Weather #357 / Boss / Presentation /
# ScoreRules / PrerequisiteMissionIds (sibling this wave)
# / GetPrimaryAssetId / ValidateDefinition /
# FindObjective stay sibling-only.
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
MISSION_FIELDS_NOT_LOCKED = (
    "TSoftObjectPtr<UWorld> MissionMap;",
    "FSkyguardRouteDefinition Route;",
    "TArray<FSkyguardObjectiveDefinition> Objectives;",
    "TArray<FSkyguardEnemyWaveDefinition> Waves;",
    "FSkyguardBossDefinition Boss;",
    "FSkyguardWeatherProfile Weather;",
    "FSkyguardMissionPresentation Presentation;",
    "FSkyguardMissionScoreRules ScoreRules;",
    "TArray<FName> PrerequisiteMissionIds;",
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
EARNED_MEDALS_NOT_LOCKED = (
    "GetEarnedCampaignMedals",
)
# Leftover objective-definition defaults #b29f, leftover
# enemy-wave defaults #dc07, leftover boss-definition
# defaults #cc27, leftover weather-profile defaults #7dd0,
# leftover mission-presentation defaults #157e, leftover
# mission-score-rules defaults #deae, leftover
# route-definition fields #dbff stay unlocked.
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
# EditAnywhere, BlueprintReadOnly, Category = "Progression",
# meta = (ClampMin = "0"). Do not invent extra specifiers.
INVENTED_UPROPERTY = (
    "BlueprintReadWrite",
    "VisibleAnywhere",
    "VisibleDefaultsOnly",
    "EditDefaultsOnly",
    "SaveGame",
    'Category = "Campaign"',
    'Category = "Progression|Medals"',
    "AllowPrivateAccess",
    "ClampMax",
    "Transient",
    "BlueprintSetter",
)
# .cpp RequiredCampaignMedals body / invented INDEX_NONE
# stay unlocked. Do not invent INDEX_NONE or lock the
# cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "USkyguardMissionDefinition::RequiredCampaignMedals",
    "SkyguardMissionDefinition.cpp",
)
CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")


def banned_live_copy() -> tuple[str, ...]:
    return ("ig" + "la", "y" + "ak", "rif" + "le")


def leftover_readiness_tokens() -> tuple[str, ...]:
    return (
        "FSkyguardMission0NIntegrationReadiness",
        "b" + "Y" + "ak" + "RuntimeReady",
        "ASkyguard" + "Ig" + "la" + "Missile",
    )


def harbor_tokens() -> tuple[str, ...]:
    incoming = "Incoming" + "Radar"
    return (
        incoming,
        incoming + "LiveIntervalSeconds",
        incoming + "DownIntervalSeconds",
        f"{40}.f",
        f"{80}.f",
        f"{40}.f, {80}.f",
    )


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


class MissionDefinitionRequiredMedalsDeclContractTests(unittest.TestCase):
    def test_mission_definition_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, REQUIRED_MEDALS), section)

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
            f"\t{REQUIRED_MEDALS}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "private:\n"
            f"\t{REQUIRED_MEDALS}\n"
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
            f"\t{REQUIRED_MEDALS}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, REQUIRED_MEDALS)
        self.assertIn("RequiredCampaignMedals", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, REQUIRED_MEDALS))

    def test_missing_required_medals_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tFName MissionId;\n"
            "\tFText DisplayName;\n"
            "\tint32 CampaignOrder = 1;\n"
            "\tTSoftObjectPtr<UWorld> MissionMap;\n"
            "\tTArray<FName> PrerequisiteMissionIds;\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() "
            "const override;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, REQUIRED_MEDALS)
        self.assertIn("RequiredCampaignMedals", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_NEARBY}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, REQUIRED_MEDALS)
        self.assertIn("RequiredCampaignMedals", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = (
            '\tUFUNCTION(BlueprintCallable, Category = "Mission")\n'
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, REQUIRED_MEDALS)
        self.assertIn("RequiredCampaignMedals", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_NEARBY, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('Category = "Progression"', section)
        self.assertIn('meta = (ClampMin = "0")', section)
        self.assertTrue(has_declaration(section, REQUIRED_MEDALS), section)
        self.assertNotIn("UPROPERTY", REQUIRED_MEDALS)
        self.assertNotIn("EditAnywhere", REQUIRED_MEDALS)
        self.assertNotIn("BlueprintReadOnly", REQUIRED_MEDALS)
        self.assertNotIn("Category", REQUIRED_MEDALS)
        self.assertNotIn("ClampMin", REQUIRED_MEDALS)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_NEARBY)
            self.assertNotIn(invented, REQUIRED_MEDALS)

    def test_declaration_accepts_nearby_origin_main_uproperty(self) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, REQUIRED_MEDALS), section)
        self.assertEqual(
            require_declaration(section, REQUIRED_MEDALS),
            REQUIRED_MEDALS,
        )
        self.assertIn(UPROPERTY_NEARBY, section)
        nearby_then_field = (
            "public:\n"
            f"\t{UPROPERTY_NEARBY}\n"
            f"\t{REQUIRED_MEDALS}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{nearby_then_field}"
        )
        wrapped = public_section(header)
        self.assertTrue(has_declaration(wrapped, REQUIRED_MEDALS), wrapped)
        self.assertIn(UPROPERTY_NEARBY, wrapped)
        self.assertEqual(
            require_declaration(wrapped, REQUIRED_MEDALS),
            REQUIRED_MEDALS,
        )
        self.assertNotIn("UPROPERTY", REQUIRED_MEDALS)

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
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() "
            "const override;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, REQUIRED_MEDALS)
        self.assertIn("RequiredCampaignMedals", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_default = "\tint32 RequiredCampaignMedals;\n"
        one_default = "\tint32 RequiredCampaignMedals = 1;\n"
        two_default = "\tint32 RequiredCampaignMedals = 2;\n"
        ten_default = "\tint32 RequiredCampaignMedals = 10;\n"
        index_none = "\tint32 RequiredCampaignMedals = INDEX_NONE;\n"
        float_type = "\tfloat RequiredCampaignMedals = 0;\n"
        float_default = "\tint32 RequiredCampaignMedals = 0.f;\n"
        int64_type = "\tint64 RequiredCampaignMedals = 0;\n"
        bare_int = "\tint RequiredCampaignMedals = 0;\n"
        wrong_name = "\tint32 RequiredMedals = 0;\n"
        order = "\tint32 CampaignOrder = 0;\n"
        earned = "\tint32 EarnedCampaignMedals = 0;\n"
        for region in (
            missing_default,
            one_default,
            two_default,
            ten_default,
            index_none,
            float_type,
            float_default,
            int64_type,
            bare_int,
            wrong_name,
            order,
            earned,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, REQUIRED_MEDALS)
            self.assertIn("RequiredCampaignMedals", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_missing_default_does_not_satisfy(self) -> None:
        bare_field = "\tint32 RequiredCampaignMedals;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(bare_field, REQUIRED_MEDALS)
        self.assertIn("RequiredCampaignMedals", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(bare_field, REQUIRED_MEDALS))

    def test_wrong_default_does_not_satisfy(self) -> None:
        wrong = "\tint32 RequiredCampaignMedals = 1;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(wrong, REQUIRED_MEDALS)
        self.assertIn("RequiredCampaignMedals", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(wrong, REQUIRED_MEDALS))

    def test_required_medals_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, REQUIRED_MEDALS),
            REQUIRED_MEDALS,
        )
        self.assertTrue(has_declaration(section, REQUIRED_MEDALS))
        self.assertEqual(
            declaration_count(section, REQUIRED_MEDALS),
            1,
        )
        self.assertTrue(
            REQUIRED_MEDALS.endswith(";"),
            REQUIRED_MEDALS,
        )
        self.assertTrue(
            REQUIRED_MEDALS.startswith("int32 "),
            REQUIRED_MEDALS,
        )
        self.assertIn("RequiredCampaignMedals", REQUIRED_MEDALS)
        self.assertTrue(
            REQUIRED_MEDALS.endswith("= 0;"),
            REQUIRED_MEDALS,
        )
        self.assertIn("= 0", REQUIRED_MEDALS)
        self.assertNotIn("INDEX_NONE", REQUIRED_MEDALS)
        self.assertNotIn("NAME_None", REQUIRED_MEDALS)
        self.assertNotIn("{", REQUIRED_MEDALS)
        self.assertNotIn("}", REQUIRED_MEDALS)
        self.assertNotIn("return ", REQUIRED_MEDALS)
        self.assertNotIn("UPROPERTY", REQUIRED_MEDALS)
        self.assertNotIn("UFUNCTION", REQUIRED_MEDALS)

    def test_declaration_locks_origin_main_default(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        self.assertIn("= 0", REQUIRED_MEDALS)
        self.assertIn("RequiredCampaignMedals =", REQUIRED_MEDALS)
        self.assertIn("0;", locked_only)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, REQUIRED_MEDALS), section)
        self.assertIn("RequiredCampaignMedals = 0", collapsed(section))
        self.assertNotIn("INDEX_NONE", REQUIRED_MEDALS)
        self.assertNotIn("NAME_None", REQUIRED_MEDALS)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_name = (
            "public:\n"
            "\tint32\n"
            "\tRequiredCampaignMedals = 0;\n"
            "private:\n"
            "};\n"
        )
        wrap_assign = (
            "public:\n"
            "\tint32 RequiredCampaignMedals =\n"
            "\t\t0;\n"
            "private:\n"
            "};\n"
        )
        wrap_equals = (
            "public:\n"
            "\tint32 RequiredCampaignMedals\n"
            "\t= 0;\n"
            "};\n"
        )
        wrap_compact = (
            "public:\n"
            "\tint32 RequiredCampaignMedals=0;\n"
            "};\n"
        )
        wrap_uproperty = (
            "public:\n"
            f"\t{UPROPERTY_NEARBY}\n"
            "\tint32\n"
            "\tRequiredCampaignMedals = 0;\n"
            "};\n"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_name}"
        )
        header_wrap_assign = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_assign}"
        )
        header_wrap_equals = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_equals}"
        )
        header_wrap_compact = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_compact}"
        )
        header_wrap_uproperty = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_uproperty}"
        )
        for header in (
            header_wrap_name,
            header_wrap_assign,
            header_wrap_equals,
            header_wrap_compact,
            header_wrap_uproperty,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, REQUIRED_MEDALS),
                section,
            )
            self.assertEqual(
                require_declaration(section, REQUIRED_MEDALS),
                REQUIRED_MEDALS,
            )
            self.assertEqual(
                declaration_count(section, REQUIRED_MEDALS),
                1,
            )
        one_line = f"{{\npublic:\n\t{REQUIRED_MEDALS}\n}}\n"
        self.assertTrue(has_declaration(one_line, REQUIRED_MEDALS))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, REQUIRED_MEDALS), section)
        self.assertEqual(
            require_declaration(section, REQUIRED_MEDALS),
            REQUIRED_MEDALS,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", REQUIRED_MEDALS)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", REQUIRED_MEDALS)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        self.assertNotIn("UPROPERTY", REQUIRED_MEDALS)
        self.assertNotIn("UPROPERTY", locked_only)
        self.assertFalse(
            REQUIRED_MEDALS.startswith("UPROPERTY"),
            REQUIRED_MEDALS,
        )
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, REQUIRED_MEDALS)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_NEARBY)
        self.assertNotIn("UFUNCTION", REQUIRED_MEDALS)
        self.assertNotIn("UFUNCTION", locked_only)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, REQUIRED_MEDALS), section)
        self.assertIn(UPROPERTY_NEARBY, section)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, REQUIRED_MEDALS)
            self.assertNotIn(invented, section)

    def test_contract_does_not_lock_required_medals_cpp_body(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        self.assertNotIn("{", REQUIRED_MEDALS)
        self.assertNotIn("}", REQUIRED_MEDALS)
        self.assertNotIn("return ", REQUIRED_MEDALS)
        self.assertNotIn(
            "USkyguardMissionDefinition::RequiredCampaignMedals",
            REQUIRED_MEDALS,
        )
        self.assertNotIn(
            "SkyguardMissionDefinition.cpp",
            REQUIRED_MEDALS,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", locked_only)
        self.assertNotIn("return false", REQUIRED_MEDALS)
        self.assertNotIn("AddError", REQUIRED_MEDALS)

    def test_contract_does_not_relock_mission_id(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        for neighbor in MISSION_ID_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REQUIRED_MEDALS)
        self.assertNotIn("MissionId", REQUIRED_MEDALS)
        self.assertNotIn("MissionId", locked_only)

    def test_contract_does_not_relock_display_name(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        for neighbor in DISPLAY_NAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REQUIRED_MEDALS)
        self.assertNotIn("DisplayName", REQUIRED_MEDALS)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("FText", REQUIRED_MEDALS)

    def test_contract_does_not_relock_campaign_order(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        for neighbor in CAMPAIGN_ORDER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REQUIRED_MEDALS)
        self.assertNotIn("CampaignOrder", REQUIRED_MEDALS)
        self.assertNotIn("CampaignOrder", locked_only)

    def test_contract_does_not_relock_neighbor_mission_fields(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        for neighbor in MISSION_FIELDS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REQUIRED_MEDALS)
        self.assertNotIn("MissionMap", REQUIRED_MEDALS)
        self.assertNotIn("PrerequisiteMissionIds", REQUIRED_MEDALS)
        self.assertNotIn("CampaignOrder", REQUIRED_MEDALS)
        self.assertNotIn("FSkyguardRouteDefinition", REQUIRED_MEDALS)
        self.assertNotIn("FSkyguardObjectiveDefinition", REQUIRED_MEDALS)
        self.assertNotIn("FSkyguardEnemyWaveDefinition", REQUIRED_MEDALS)
        self.assertNotIn("FSkyguardBossDefinition", REQUIRED_MEDALS)
        self.assertNotIn("FSkyguardWeatherProfile", REQUIRED_MEDALS)
        self.assertNotIn("FSkyguardMissionPresentation", REQUIRED_MEDALS)
        self.assertNotIn("FSkyguardMissionScoreRules", REQUIRED_MEDALS)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)

    def test_contract_does_not_relock_validate_definition(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        for neighbor in VALIDATE_DEFINITION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REQUIRED_MEDALS)
        self.assertNotIn("ValidateDefinition", REQUIRED_MEDALS)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("OutErrors", REQUIRED_MEDALS)
        self.assertNotIn("BlueprintCallable", REQUIRED_MEDALS)

    def test_contract_does_not_relock_find_objective(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        for neighbor in FIND_OBJECTIVE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REQUIRED_MEDALS)
        self.assertNotIn("FindObjective", REQUIRED_MEDALS)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("ObjectiveId", REQUIRED_MEDALS)

    def test_contract_does_not_relock_primary_asset_id(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        for neighbor in PRIMARY_ASSET_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REQUIRED_MEDALS)
        self.assertNotIn("GetPrimaryAssetId", REQUIRED_MEDALS)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("FPrimaryAssetId", REQUIRED_MEDALS)

    def test_contract_does_not_relock_earned_campaign_medals(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        for neighbor in EARNED_MEDALS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REQUIRED_MEDALS)
        self.assertNotIn("GetEarnedCampaignMedals", REQUIRED_MEDALS)
        self.assertNotIn("GetEarnedCampaignMedals", locked_only)

    def test_contract_does_not_relock_leftover_defaults(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        for token in LEFTOVER_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REQUIRED_MEDALS)
        self.assertNotIn("RequiredProgress", REQUIRED_MEDALS)
        self.assertNotIn("CompletionScore", REQUIRED_MEDALS)
        self.assertNotIn("MaximumBreakupPieces", REQUIRED_MEDALS)
        self.assertNotIn("MinimumBriefingWarmupSeconds", REQUIRED_MEDALS)
        self.assertNotIn("TimeOfDayHours", REQUIRED_MEDALS)
        self.assertNotIn("StartTimeSeconds", REQUIRED_MEDALS)
        self.assertNotIn("RouteId", REQUIRED_MEDALS)

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REQUIRED_MEDALS)
        self.assertNotIn("FillResultCombatStats", REQUIRED_MEDALS)
        self.assertNotIn("ASkyguardGunner", REQUIRED_MEDALS)
        self.assertNotIn("FillAndFinalize", REQUIRED_MEDALS)
        self.assertNotIn("FillAndFail", REQUIRED_MEDALS)
        self.assertNotIn("ApplyHydraForClusters", REQUIRED_MEDALS)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REQUIRED_MEDALS)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REQUIRED_MEDALS)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REQUIRED_MEDALS)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{REQUIRED_MEDALS}\n"
        self.assertEqual(
            require_declaration(locked_only, REQUIRED_MEDALS),
            REQUIRED_MEDALS,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REQUIRED_MEDALS)
        self.assertNotIn("MissionId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("CampaignOrder", locked_only)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)
        self.assertNotIn("GetEarnedCampaignMedals", locked_only)
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
            require_declaration(section, REQUIRED_MEDALS),
            REQUIRED_MEDALS,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::RequiredCampaignMedals",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, REQUIRED_MEDALS)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::RequiredCampaignMedals",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", REQUIRED_MEDALS)
        self.assertNotIn("}", REQUIRED_MEDALS)
        self.assertNotIn("return false", REQUIRED_MEDALS)
        self.assertNotIn("AddError", REQUIRED_MEDALS)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{REQUIRED_MEDALS}\n"
        for token in harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, REQUIRED_MEDALS)
            self.assertNotIn(token, locked_only)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        self_text = Path(__file__).read_text(encoding="utf-8")
        locked_only = f"{REQUIRED_MEDALS}\n"
        section = public_section(origin_main_header())
        for token in harbor_tokens():
            self.assertNotIn(token, self_text)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REQUIRED_MEDALS)
            self.assertNotIn(token, section)

    def test_contract_does_not_require_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        for banned in banned_live_copy():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, REQUIRED_MEDALS.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, REQUIRED_MEDALS)
        self.assertNotEqual(REQUIRED_MEDALS, "Rif" + "le")
        self.assertNotEqual(REQUIRED_MEDALS, "Ig" + "la")

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in banned_live_copy():
            self.assertNotIn(
                banned,
                lowered,
                "mission RequiredCampaignMedals contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, REQUIRED_MEDALS.lower())

    def test_file_comments_and_strings_ban_retired_mount(self) -> None:
        self_text = Path(__file__).read_text(encoding="utf-8")
        comment_blob = "\n".join(
            line[line.index("#"):].lower()
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
        for banned in banned_live_copy():
            self.assertNotIn(banned, comment_blob)
            self.assertNotIn(banned, string_blob)
            self.assertNotIn(banned, REQUIRED_MEDALS.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_slash = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_slash, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_slash, REQUIRED_MEDALS)

    def test_contract_is_required_medals_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, REQUIRED_MEDALS),
            REQUIRED_MEDALS,
        )
        locked_only = f"{REQUIRED_MEDALS}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REQUIRED_MEDALS)
        self.assertNotIn("MissionId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("CampaignOrder", locked_only)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)
        self.assertNotIn("GetEarnedCampaignMedals", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REQUIRED_MEDALS)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REQUIRED_MEDALS)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REQUIRED_MEDALS)
        for token in LEFTOVER_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REQUIRED_MEDALS)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, REQUIRED_MEDALS)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, REQUIRED_MEDALS)
            self.assertNotIn(token, section)
        for token in harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for banned in banned_live_copy():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, REQUIRED_MEDALS.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", REQUIRED_MEDALS)
        self.assertNotIn("{", REQUIRED_MEDALS)
        self.assertNotIn("AddError", REQUIRED_MEDALS)
        self.assertNotEqual(REQUIRED_MEDALS, "Rif" + "le")
        self.assertNotEqual(REQUIRED_MEDALS, "Ig" + "la")
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertIn("= 0", REQUIRED_MEDALS)

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
