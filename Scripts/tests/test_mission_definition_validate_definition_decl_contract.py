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
# validation error text, or lock the ValidateDefinition
# body in the .cpp.
# origin/main is one line
# (`bool ValidateDefinition(TArray<FText>& OutErrors) const;`);
# accept that form, other split-line wraps, and an inline
# body without locking the body. Nearby origin/main
# UFUNCTION(BlueprintCallable, Category = "Mission") is
# accepted as present. This is
# USkyguardMissionDefinition::ValidateDefinition, not
# USkyguardCampaignDefinition::ValidateDefinition (#331).
VALIDATE_DEFINITION = (
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;"
)
UFUNCTION_NEARBY = (
    'UFUNCTION(BlueprintCallable, Category = "Mission")'
)
# Leftover #56–#64 plus MissionDefinition production files.
# This lane only adds an isolated Python ValidateDefinition
# declaration contract. Stay off MissionId #350 through
# ScoreRules #360, PrerequisiteMissionIds,
# RequiredCampaignMedals, GetPrimaryAssetId (in-flight
# sibling on this class, not campaign-definition #339),
# and FindObjective (sibling this wave). Stay off leftover
# campaign-roster #111, leftover campaign-save
# empty-fail-closed, leftover objective-definition
# defaults, leftover enemy-wave defaults, leftover
# boss-definition defaults, leftover weather-profile
# defaults, leftover mission-presentation defaults,
# leftover mission-score-rules defaults, leftover
# route-definition fields, leftover campaign-definition
# ValidateDefinition #331, leftover CPG debrief
# #284/#195/#130/#8ccd, leftover bind-hud-host, leftover
# objective-runtime fail-closed, leftover route-runtime
# fail-closed, leftover pilot #117/#120/#128/#129/#170,
# leftover gun-fire camera shake #8860, leftover
# mission-weather enum #96d2, FillResultCombatStats /
# FillAndFinalize / FillAndFail / ApplyHydraForClusters,
# leftover Harbor #6/#8/#9, leftover theater-kit #59,
# leftover flare/HUD #57/#61/#62, leftover drafts
# #56–#64, leftover #147 ApacheSystem, leftover #149
# weapon stations, leftover #152 pilot commands,
# leftover #154 loadout / lock-phase, leftover settings
# invert-look / ApplySettings broadcast #134, Harbor
# leftover clocks, leftover live copy,
# FSkyguardMission0NIntegrationReadiness leftover
# readiness flag, and dirty workspace path.
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
# weather / boss / wave / presentation / score-rules
# defaults, leftover campaign-definition
# ValidateDefinition #331, leftover MissionId #350
# through ScoreRules field siblings, leftover
# PrerequisiteMissionIds / RequiredCampaignMedals /
# GetPrimaryAssetId / FindObjective siblings, leftover
# CPG debrief, leftover objective-runtime /
# route-runtime fail-closed, leftover theater-kit /
# Harbor / flare/HUD, leftover settings invert-look /
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
    "Scripts/tests/test_validate_definition_decl_contract.py",
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
    "Scripts/tests/test_mission_definition_prerequisite_ids_decl_contract.py",
    "Scripts/tests/test_mission_definition_required_medals_decl_contract.py",
    "Scripts/tests/test_mission_definition_get_primary_asset_id_decl_contract.py",
    "Scripts/tests/test_mission_definition_find_objective_decl_contract.py",
    "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
    "Scripts/tests/test_find_mission_decl_contract.py",
    "Scripts/tests/test_find_objective_decl_contract.py",
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_enemy_wave_defaults_contract.py",
    "Scripts/tests/test_boss_definition_defaults_contract.py",
    "Scripts/tests/test_weather_profile_defaults_contract.py",
    "Scripts/tests/test_mission_presentation_defaults_contract.py",
    "Scripts/tests/test_mission_score_rules_defaults_contract.py",
    "Scripts/tests/test_route_definition_fields_contract.py",
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
# MissionMap / Route / Objectives / Waves / Boss /
# Weather / Presentation / ScoreRules #360 /
# PrerequisiteMissionIds / RequiredCampaignMedals /
# GetPrimaryAssetId / FindObjective stay sibling-only.
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
OBJECTIVES_NOT_LOCKED = (
    "TArray<FSkyguardObjectiveDefinition> Objectives;",
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
FIND_OBJECTIVE_NOT_LOCKED = (
    "const FSkyguardObjectiveDefinition* FindObjective(FName ObjectiveId) const;",
)
# USkyguardCampaignDefinition::ValidateDefinition (#331)
# stays sibling-only. Same signature, different class.
CAMPAIGN_DEFINITION_NOT_LOCKED = (
    "USkyguardCampaignDefinition",
    "USkyguardMissionDefinition* FindMission(FName MissionId) const;",
    "TArray<TObjectPtr<USkyguardMissionDefinition>> Missions",
)
# Leftover struct-default drafts stay unlocked.
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
    "FillResultCombatStats",
    "bInvertLook",
    "ApplySettings",
    "BindHudHost",
    "enum class ESkyguardMissionWeather",
    "ESkyguardPilotLine",
)
# Invented UFUNCTION specifiers that are not on
# origin/main for this helper. Nearby origin/main
# metadata is BlueprintCallable, Category = "Mission".
# Do not invent extra specifiers.
INVENTED_UFUNCTION = (
    "BlueprintPure",
    "BlueprintAuthorityOnly",
    'Category = "Campaign"',
    'Category = "Mission|Validate"',
    "meta =",
)
# .cpp ValidateDefinition body / invented INDEX_NONE
# stay unlocked. Do not invent INDEX_NONE or lock the
# cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "OutErrors.Reset",
    "AddError",
    "USkyguardMissionDefinition::ValidateDefinition",
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


def declaration_stem(declaration: str) -> str:
    compact = collapsed(declaration)
    if compact.endswith(";"):
        return compact[:-1].rstrip()
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
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return True
    stem = declaration_stem(declaration)
    index = 0
    while True:
        found = compact_region.find(stem, index)
        if found == -1:
            return False
        after = compact_region[found + len(stem) :].lstrip()
        if after.startswith(";") or after.startswith("{"):
            return True
        index = found + 1


def declaration_count(region: str, declaration: str) -> int:
    compact_region = collapsed(region)
    stem = declaration_stem(declaration)
    count = 0
    index = 0
    while True:
        found = compact_region.find(stem, index)
        if found == -1:
            return count
        after = compact_region[found + len(stem) :].lstrip()
        if after.startswith(";") or after.startswith("{"):
            count += 1
            index = found + max(len(stem), 1)
        else:
            index = found + 1


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"class {CLASS_NAME} public section"
        )
    return declaration


class MissionDefinitionValidateDefinitionDeclContractTests(unittest.TestCase):
    def test_mission_definition_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, VALIDATE_DEFINITION), section)

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
            f"\t{VALIDATE_DEFINITION}\n"
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
            f"\t{VALIDATE_DEFINITION}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(definition)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "private:\n"
            f"\t{VALIDATE_DEFINITION}\n"
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
            f"\t{VALIDATE_DEFINITION}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, VALIDATE_DEFINITION)
        self.assertIn("ValidateDefinition", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, VALIDATE_DEFINITION))

    def test_missing_validate_definition_declaration_fails_closed(self) -> None:
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
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, VALIDATE_DEFINITION)
        self.assertIn("ValidateDefinition", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_NEARBY}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, VALIDATE_DEFINITION)
        self.assertIn("ValidateDefinition", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_NEARBY, section)
        self.assertIn("BlueprintCallable", section)
        self.assertIn('Category = "Mission"', section)
        self.assertTrue(has_declaration(section, VALIDATE_DEFINITION), section)
        self.assertNotIn("BlueprintPure", VALIDATE_DEFINITION)
        self.assertNotIn("UFUNCTION", VALIDATE_DEFINITION)
        self.assertNotIn("Category", VALIDATE_DEFINITION)
        for invented in INVENTED_UFUNCTION:
            self.assertNotIn(invented, VALIDATE_DEFINITION)

    def test_declaration_accepts_nearby_origin_main_ufunction(self) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, VALIDATE_DEFINITION), section)
        self.assertEqual(
            require_declaration(section, VALIDATE_DEFINITION),
            VALIDATE_DEFINITION,
        )
        self.assertIn(UFUNCTION_NEARBY, section)
        nearby_then_decl = (
            "public:\n"
            f"\t{UFUNCTION_NEARBY}\n"
            f"\t{VALIDATE_DEFINITION}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{nearby_then_decl}"
        )
        wrapped = public_section(header)
        self.assertTrue(has_declaration(wrapped, VALIDATE_DEFINITION), wrapped)
        self.assertIn(UFUNCTION_NEARBY, wrapped)
        self.assertEqual(
            require_declaration(wrapped, VALIDATE_DEFINITION),
            VALIDATE_DEFINITION,
        )
        self.assertNotIn("UFUNCTION", VALIDATE_DEFINITION)

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
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, VALIDATE_DEFINITION)
        self.assertIn("ValidateDefinition", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_arg = "\tbool ValidateDefinition() const;\n"
        non_const = "\tbool ValidateDefinition(TArray<FText>& OutErrors);\n"
        wrong_return = (
            "\tvoid ValidateDefinition(TArray<FText>& OutErrors) const;\n"
        )
        missing_ref = (
            "\tbool ValidateDefinition(TArray<FText> OutErrors) const;\n"
        )
        wrong_array = (
            "\tbool ValidateDefinition(TArray<FString>& OutErrors) const;\n"
        )
        find_objective = (
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        for region in (
            missing_arg,
            non_const,
            wrong_return,
            missing_ref,
            wrong_array,
            find_objective,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, VALIDATE_DEFINITION)
            self.assertIn("ValidateDefinition", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_validate_definition_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, VALIDATE_DEFINITION),
            VALIDATE_DEFINITION,
        )
        self.assertTrue(has_declaration(section, VALIDATE_DEFINITION))
        self.assertEqual(
            declaration_count(section, VALIDATE_DEFINITION),
            1,
        )
        self.assertTrue(
            VALIDATE_DEFINITION.endswith("const;"),
            VALIDATE_DEFINITION,
        )
        self.assertTrue(
            VALIDATE_DEFINITION.startswith("bool "),
            VALIDATE_DEFINITION,
        )
        self.assertIn("TArray<FText>& OutErrors", VALIDATE_DEFINITION)
        self.assertNotIn("INDEX_NONE", VALIDATE_DEFINITION)
        self.assertNotIn("{", VALIDATE_DEFINITION)
        self.assertNotIn("}", VALIDATE_DEFINITION)
        self.assertNotIn("return ", VALIDATE_DEFINITION)
        self.assertNotIn("UFUNCTION", VALIDATE_DEFINITION)
        self.assertNotIn("static ", VALIDATE_DEFINITION)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_name = (
            "public:\n"
            "\tbool ValidateDefinition(\n"
            "\t\tTArray<FText>& OutErrors) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_type = (
            "public:\n"
            "\tbool\n"
            "\tValidateDefinition(TArray<FText>& OutErrors) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_arg = (
            "public:\n"
            "\tbool ValidateDefinition(TArray<FText>&\n"
            "\t\tOutErrors) const;\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tbool ValidateDefinition(TArray<FText>& OutErrors)\n"
            "\tconst;\n"
            "};\n"
        )
        wrap_ufunction = (
            "public:\n"
            f"\t{UFUNCTION_NEARBY}\n"
            "\tbool ValidateDefinition(\n"
            "\t\tTArray<FText>& OutErrors) const;\n"
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
        header_wrap_ufunction = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_ufunction}"
        )
        for header in (
            header_wrap_name,
            header_wrap_type,
            header_wrap_arg,
            header_wrap_const,
            header_wrap_ufunction,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, VALIDATE_DEFINITION),
                section,
            )
            self.assertEqual(
                require_declaration(section, VALIDATE_DEFINITION),
                VALIDATE_DEFINITION,
            )
            self.assertEqual(
                declaration_count(section, VALIDATE_DEFINITION),
                1,
            )
        one_line = f"{{\npublic:\n\t{VALIDATE_DEFINITION}\n}}\n"
        self.assertTrue(has_declaration(one_line, VALIDATE_DEFINITION))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, VALIDATE_DEFINITION), section)
        self.assertEqual(
            require_declaration(section, VALIDATE_DEFINITION),
            VALIDATE_DEFINITION,
        )

    def test_declaration_accepts_inline_body_without_locking_body(self) -> None:
        inline_true = (
            "public:\n"
            "\tbool ValidateDefinition(TArray<FText>& OutErrors) const "
            "{ return true; }\n"
            "};\n"
        )
        inline_wrap = (
            "public:\n"
            "\tbool ValidateDefinition(TArray<FText>& OutErrors) const\n"
            "\t{\n"
            "\t\tOutErrors.Reset();\n"
            "\t\treturn true;\n"
            "\t}\n"
            "};\n"
        )
        header_true = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{inline_true}"
        )
        header_wrap = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{inline_wrap}"
        )
        for header in (header_true, header_wrap):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, VALIDATE_DEFINITION),
                section,
            )
            self.assertEqual(
                require_declaration(section, VALIDATE_DEFINITION),
                VALIDATE_DEFINITION,
            )
            self.assertEqual(
                declaration_count(section, VALIDATE_DEFINITION),
                1,
            )
        self.assertNotIn("{", VALIDATE_DEFINITION)
        self.assertNotIn("}", VALIDATE_DEFINITION)
        self.assertNotIn("return ", VALIDATE_DEFINITION)
        self.assertNotIn("OutErrors.Reset", VALIDATE_DEFINITION)
        self.assertNotIn("AddError", VALIDATE_DEFINITION)
        self.assertTrue(VALIDATE_DEFINITION.endswith(";"), VALIDATE_DEFINITION)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", VALIDATE_DEFINITION)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", VALIDATE_DEFINITION)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_validation_error_text(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        self.assertNotIn("return ", VALIDATE_DEFINITION)
        self.assertNotIn("AddError", VALIDATE_DEFINITION)
        self.assertNotIn("OutErrors.Reset", VALIDATE_DEFINITION)
        self.assertNotIn("must be set", VALIDATE_DEFINITION)
        self.assertNotIn("must be unique", VALIDATE_DEFINITION)
        self.assertNotIn("at least one", VALIDATE_DEFINITION)
        self.assertNotIn("TEXT(", VALIDATE_DEFINITION)
        self.assertNotIn('"', VALIDATE_DEFINITION)
        self.assertNotIn("AddError", locked_only)
        self.assertNotIn("OutErrors.Reset", locked_only)
        self.assertNotIn("must be set", locked_only)
        section = public_section(origin_main_header())
        self.assertNotIn("AddError", section)
        self.assertNotIn("OutErrors.Reset", section)
        self.assertNotIn("must be set", section)
        self.assertNotIn("must be unique", section)

    def test_declaration_does_not_invent_ufunction_metadata(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for invented in INVENTED_UFUNCTION:
            self.assertNotIn(invented, VALIDATE_DEFINITION)
            self.assertNotIn(invented, locked_only)
        self.assertNotIn("UFUNCTION", VALIDATE_DEFINITION)
        self.assertNotIn("BlueprintPure", VALIDATE_DEFINITION)
        self.assertNotIn("BlueprintCallable", VALIDATE_DEFINITION)
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_NEARBY, section)
        self.assertTrue(has_declaration(section, VALIDATE_DEFINITION), section)

    def test_contract_does_not_lock_validate_definition_cpp_body(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        self.assertNotIn("{", VALIDATE_DEFINITION)
        self.assertNotIn("}", VALIDATE_DEFINITION)
        self.assertNotIn("return ", VALIDATE_DEFINITION)
        self.assertNotIn(
            "USkyguardMissionDefinition::ValidateDefinition",
            VALIDATE_DEFINITION,
        )
        self.assertNotIn(
            "SkyguardMissionDefinition.cpp",
            VALIDATE_DEFINITION,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", locked_only)
        self.assertNotIn("OutErrors.Reset", VALIDATE_DEFINITION)
        self.assertNotIn("AddError", VALIDATE_DEFINITION)
        self.assertNotIn("return false", VALIDATE_DEFINITION)
        self.assertNotIn("return true", VALIDATE_DEFINITION)

    def test_contract_does_not_relock_mission_id(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in MISSION_ID_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("MissionId", VALIDATE_DEFINITION)
        self.assertNotIn("MissionId", locked_only)

    def test_contract_does_not_relock_display_name(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in DISPLAY_NAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("DisplayName", VALIDATE_DEFINITION)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("FText DisplayName", VALIDATE_DEFINITION)

    def test_contract_does_not_relock_campaign_order(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in CAMPAIGN_ORDER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("CampaignOrder", VALIDATE_DEFINITION)
        self.assertNotIn("CampaignOrder", locked_only)

    def test_contract_does_not_relock_mission_map(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in MISSION_MAP_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("MissionMap", VALIDATE_DEFINITION)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("TSoftObjectPtr", VALIDATE_DEFINITION)

    def test_contract_does_not_relock_route(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in ROUTE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("FSkyguardRouteDefinition", VALIDATE_DEFINITION)
        self.assertNotIn("FSkyguardRouteDefinition", locked_only)

    def test_contract_does_not_relock_objectives(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in OBJECTIVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("Objectives", VALIDATE_DEFINITION)
        self.assertNotIn("Objectives", locked_only)
        self.assertNotIn("FSkyguardObjectiveDefinition", VALIDATE_DEFINITION)

    def test_contract_does_not_relock_waves(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in WAVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("Waves", VALIDATE_DEFINITION)
        self.assertNotIn("Waves", locked_only)
        self.assertNotIn("FSkyguardEnemyWaveDefinition", VALIDATE_DEFINITION)

    def test_contract_does_not_relock_boss(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in BOSS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("FSkyguardBossDefinition", VALIDATE_DEFINITION)
        self.assertNotIn("FSkyguardBossDefinition", locked_only)

    def test_contract_does_not_relock_weather(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in WEATHER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("FSkyguardWeatherProfile", VALIDATE_DEFINITION)
        self.assertNotIn("FSkyguardWeatherProfile", locked_only)

    def test_contract_does_not_relock_presentation(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in PRESENTATION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("FSkyguardMissionPresentation", VALIDATE_DEFINITION)
        self.assertNotIn("FSkyguardMissionPresentation", locked_only)

    def test_contract_does_not_relock_score_rules(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in SCORE_RULES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("FSkyguardMissionScoreRules", VALIDATE_DEFINITION)
        self.assertNotIn("FSkyguardMissionScoreRules", locked_only)

    def test_contract_does_not_relock_prerequisite_mission_ids(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in PREREQUISITE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("PrerequisiteMissionIds", VALIDATE_DEFINITION)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)

    def test_contract_does_not_relock_required_campaign_medals(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in MEDALS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("RequiredCampaignMedals", VALIDATE_DEFINITION)
        self.assertNotIn("RequiredCampaignMedals", locked_only)

    def test_contract_does_not_relock_primary_asset_id(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in PRIMARY_ASSET_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("GetPrimaryAssetId", VALIDATE_DEFINITION)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("FPrimaryAssetId", VALIDATE_DEFINITION)

    def test_contract_does_not_relock_find_objective(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in FIND_OBJECTIVE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("FindObjective", VALIDATE_DEFINITION)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("ObjectiveId", VALIDATE_DEFINITION)

    def test_contract_does_not_relock_campaign_definition_validate(
        self,
    ) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        section = public_section(origin_main_header())
        for token in CAMPAIGN_DEFINITION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, VALIDATE_DEFINITION)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardCampaignDefinition", VALIDATE_DEFINITION)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        self.assertNotIn("FindMission", VALIDATE_DEFINITION)
        self.assertNotIn("FindMission", locked_only)

    def test_contract_does_not_relock_leftover_struct_default_drafts(
        self,
    ) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for token in LEFTOVER_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, VALIDATE_DEFINITION)
        self.assertNotIn("defaults_contract", VALIDATE_DEFINITION)
        self.assertNotIn("defaults_contract", locked_only)

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("FillResultCombatStats", VALIDATE_DEFINITION)
        self.assertNotIn("ASkyguardGunner", VALIDATE_DEFINITION)
        self.assertNotIn("FillAndFinalize", VALIDATE_DEFINITION)
        self.assertNotIn("FillAndFail", VALIDATE_DEFINITION)
        self.assertNotIn("ApplyHydraForClusters", VALIDATE_DEFINITION)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, VALIDATE_DEFINITION)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, VALIDATE_DEFINITION)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, VALIDATE_DEFINITION)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{VALIDATE_DEFINITION}\n"
        self.assertEqual(
            require_declaration(locked_only, VALIDATE_DEFINITION),
            VALIDATE_DEFINITION,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("MissionId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("CampaignOrder", locked_only)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)
        self.assertNotIn("RequiredCampaignMedals", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("OutErrors.Reset", section)
        self.assertNotIn("AddError", section)
        self.assertEqual(
            require_declaration(section, VALIDATE_DEFINITION),
            VALIDATE_DEFINITION,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::ValidateDefinition",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, VALIDATE_DEFINITION)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::ValidateDefinition",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", VALIDATE_DEFINITION)
        self.assertNotIn("}", VALIDATE_DEFINITION)
        self.assertNotIn("return false", VALIDATE_DEFINITION)
        self.assertNotIn("AddError", VALIDATE_DEFINITION)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for token in harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, VALIDATE_DEFINITION)
            self.assertNotIn(token, locked_only)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        self_text = this_file_text()
        locked_only = f"{VALIDATE_DEFINITION}\n"
        section = public_section(origin_main_header())
        for token in harbor_tokens():
            self.assertNotIn(token, self_text)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, VALIDATE_DEFINITION)
            self.assertNotIn(token, section)

    def test_contract_does_not_require_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        for banned in banned_live_copy():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, VALIDATE_DEFINITION.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, VALIDATE_DEFINITION)
        self.assertNotEqual(VALIDATE_DEFINITION, "Rif" + "le")
        self.assertNotEqual(VALIDATE_DEFINITION, "Ig" + "la")

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in banned_live_copy():
            self.assertNotIn(
                banned,
                lowered,
                "mission ValidateDefinition contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, VALIDATE_DEFINITION.lower())

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
        for banned in banned_live_copy():
            self.assertNotIn(banned, comment_blob)
            self.assertNotIn(banned, string_blob)
            self.assertNotIn(banned, VALIDATE_DEFINITION.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_slash = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_slash, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_slash, VALIDATE_DEFINITION)

    def test_contract_is_validate_definition_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, VALIDATE_DEFINITION),
            VALIDATE_DEFINITION,
        )
        locked_only = f"{VALIDATE_DEFINITION}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, VALIDATE_DEFINITION)
        self.assertNotIn("MissionId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("CampaignOrder", locked_only)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)
        self.assertNotIn("RequiredCampaignMedals", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        self.assertNotIn("FindMission", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, VALIDATE_DEFINITION)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, VALIDATE_DEFINITION)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, VALIDATE_DEFINITION)
        for token in LEFTOVER_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, VALIDATE_DEFINITION)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, VALIDATE_DEFINITION)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, VALIDATE_DEFINITION)
            self.assertNotIn(token, section)
        for token in harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for banned in banned_live_copy():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, VALIDATE_DEFINITION.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", VALIDATE_DEFINITION)
        self.assertNotIn("{", VALIDATE_DEFINITION)
        self.assertNotIn("AddError", VALIDATE_DEFINITION)
        self.assertNotEqual(VALIDATE_DEFINITION, "Rif" + "le")
        self.assertNotEqual(VALIDATE_DEFINITION, "Ig" + "la")
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertEqual(
            VALIDATE_DEFINITION,
            "bool ValidateDefinition(TArray<FText>& OutErrors) const;",
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
