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
# a weather body, leftover ProfileId / TimeOfDayHours, or
# lock Weather in the .cpp. origin/main is one line
# (`FSkyguardWeatherProfile Weather;`); accept that form
# and other split-line wraps. Nearby UPROPERTY metadata
# is present on origin/main; do not invent metadata that
# is not in origin/main. Parse the public class section
# of USkyguardMissionDefinition only. Do not parse the
# FSkyguardWeatherProfile struct body. Leftover
# weather-profile defaults #7dd0 lock those struct
# fields, not this class field. Leftover mission-weather
# enum #96d2 stays sibling-only.
WEATHER = "FSkyguardWeatherProfile Weather;"
UPROPERTY_ENVIRONMENT = (
    'UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Environment")'
)
# Leftover #56–#64 plus MissionDefinition production files.
# This lane only adds an isolated Python Weather field
# declaration contract. Stay off MissionId #350,
# DisplayName #351, CampaignOrder #352, MissionMap #353,
# Route, Objectives, Waves (in-flight sibling), Boss
# (sibling this wave), Presentation, ScoreRules,
# PrerequisiteMissionIds, RequiredCampaignMedals,
# GetPrimaryAssetId, ValidateDefinition, and
# FindObjective on this class. Stay off leftover
# objective-definition defaults #b29f, leftover
# enemy-wave defaults #dc07, leftover boss-definition
# defaults #cc27, leftover weather-profile defaults
# #7dd0 (struct fields, not this class field), leftover
# mission-presentation defaults #157e, leftover
# mission-score-rules defaults #deae, leftover
# route-definition fields #dbff. Stay off leftover
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
# defaults, leftover weather-profile defaults, leftover
# campaign definition CampaignId / DisplayName /
# Missions, leftover CPG debrief, leftover
# objective-runtime / route-runtime fail-closed,
# leftover theater-kit / Harbor / flare / HUD, leftover
# ApacheSystem / weapon stations / pilot commands /
# loadout, leftover settings invert-look, leftover
# bind-hud-host, leftover pilot drafts, leftover
# gun-fire camera shake, leftover mission-weather enum,
# and in-flight MissionId / DisplayName / CampaignOrder /
# MissionMap / Route / Objectives / Waves / Boss stay
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
    "Scripts/tests/test_mission_definition_boss_decl_contract.py",
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_enemy_wave_defaults_contract.py",
    "Scripts/tests/test_boss_definition_defaults_contract.py",
    "Scripts/tests/test_weather_profile_defaults_contract.py",
    "Scripts/tests/test_mission_presentation_defaults_contract.py",
    "Scripts/tests/test_mission_score_rules_defaults_contract.py",
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
# Presentation / ScoreRules / PrerequisiteMissionIds /
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
    "FSkyguardMissionPresentation Presentation;",
    "FSkyguardMissionScoreRules ScoreRules;",
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
FIND_OBJECTIVE_NOT_LOCKED = (
    "const FSkyguardObjectiveDefinition* FindObjective(FName ObjectiveId) const;",
)
# USkyguardCampaignDefinition / USkyguardCampaignSaveGame
# identity fields stay unlocked. This lane is Weather on
# USkyguardMissionDefinition only.
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
# field. Leftover weather-profile defaults #7dd0 lock
# ProfileId / TimeOfDayHours on the struct, not this
# class field.
LEFTOVER_STRUCT_DEFAULTS_NOT_LOCKED = (
    "test_objective_definition_defaults_contract.py",
    "test_enemy_wave_defaults_contract.py",
    "test_boss_definition_defaults_contract.py",
    "test_weather_profile_defaults_contract.py",
    "test_mission_presentation_defaults_contract.py",
    "test_mission_score_rules_defaults_contract.py",
    "test_route_definition_fields_contract.py",
)
LEFTOVER_WEATHER_STRUCT_FIELDS_NOT_LOCKED = (
    "FName ProfileId;",
    "ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Clear;",
    "float TimeOfDayHours = 12.f;",
    "float WindSpeedMetersPerSecond = 5.f;",
    "float Precipitation = 0.f;",
    "float CloudCoverage = 0.25f;",
)
LEFTOVER_MISSION_WEATHER_ENUM_NOT_LOCKED = (
    "test_mission_weather_enum_contract.py",
    "ESkyguardMissionWeather::Clear",
    "ESkyguardMissionWeather::Overcast",
    "ESkyguardMissionWeather::Rain",
    "ESkyguardMissionWeather::Storm",
    "ESkyguardMissionWeather::NightClear",
    "ESkyguardMissionWeather::NightOvercast",
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
# EditAnywhere, BlueprintReadOnly, Category = "Environment".
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
# .cpp Weather body / invented INDEX_NONE stay unlocked.
# Do not invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "USkyguardMissionDefinition::Weather",
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


class MissionDefinitionWeatherDeclContractTests(unittest.TestCase):
    def test_mission_definition_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, WEATHER), section)

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
            f"\t{WEATHER}\n"
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

    def test_weather_profile_struct_does_not_satisfy_class(self) -> None:
        struct_only = (
            "USTRUCT(BlueprintType)\n"
            "struct FSkyguardWeatherProfile\n"
            "{\n"
            "\tGENERATED_BODY()\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadOnly)\n"
            "\tFName ProfileId;\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadOnly)\n"
            "\tESkyguardMissionWeather Weather = "
            "ESkyguardMissionWeather::Clear;\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadOnly)\n"
            "\tfloat TimeOfDayHours = 12.f;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(struct_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(struct_only, WEATHER)
        self.assertIn("Weather", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "private:\n"
            f"\t{WEATHER}\n"
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
            f"\t{WEATHER}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, WEATHER)
        self.assertIn("Weather", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, WEATHER))

    def test_missing_weather_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tFName MissionId;\n"
            "\tFText DisplayName;\n"
            "\tint32 CampaignOrder = 1;\n"
            "\tTSoftObjectPtr<UWorld> MissionMap;\n"
            "\tFSkyguardRouteDefinition Route;\n"
            "\tTArray<FSkyguardObjectiveDefinition> Objectives;\n"
            "\tTArray<FSkyguardEnemyWaveDefinition> Waves;\n"
            "\tFSkyguardBossDefinition Boss;\n"
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
            require_declaration(neighbors_only, WEATHER)
        self.assertIn("Weather", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_ENVIRONMENT}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, WEATHER)
        self.assertIn("Weather", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_ENVIRONMENT, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('Category = "Environment"', section)
        self.assertTrue(has_declaration(section, WEATHER), section)
        self.assertNotIn("UPROPERTY", WEATHER)
        self.assertNotIn("EditAnywhere", WEATHER)
        self.assertNotIn("BlueprintReadOnly", WEATHER)
        self.assertNotIn("Category", WEATHER)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_ENVIRONMENT)
            self.assertNotIn(invented, WEATHER)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, UPROPERTY_ENVIRONMENT)
            self.assertNotIn(invented, WEATHER)

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
            require_declaration(other_fields, WEATHER)
        self.assertIn("Weather", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        assigned = "\tFSkyguardWeatherProfile Weather = {};\n"
        name_type = "\tFName Weather;\n"
        text_type = "\tFText Weather;\n"
        int_type = "\tint32 Weather;\n"
        leftover_id = "\tFName ProfileId;\n"
        leftover_hours = "\tfloat TimeOfDayHours = 12.f;\n"
        leftover_enum = (
            "\tESkyguardMissionWeather Weather = "
            "ESkyguardMissionWeather::Clear;\n"
        )
        enum_type = "\tESkyguardMissionWeather Weather;\n"
        mission_id = "\tFName MissionId;\n"
        display_name = "\tFText DisplayName;\n"
        route = "\tFSkyguardRouteDefinition Route;\n"
        for region in (
            assigned,
            name_type,
            text_type,
            int_type,
            leftover_id,
            leftover_hours,
            leftover_enum,
            enum_type,
            mission_id,
            display_name,
            route,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, WEATHER)
            self.assertIn("Weather", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_weather_struct_fields_do_not_satisfy(self) -> None:
        leftover = (
            "\tFName ProfileId;\n"
            "\tESkyguardMissionWeather Weather = "
            "ESkyguardMissionWeather::Clear;\n"
            "\tfloat TimeOfDayHours = 12.f;\n"
            "\tfloat WindSpeedMetersPerSecond = 5.f;\n"
            "\tfloat Precipitation = 0.f;\n"
            "\tfloat CloudCoverage = 0.25f;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(leftover, WEATHER)
        self.assertIn("Weather", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(leftover, WEATHER))

    def test_assigned_weather_does_not_satisfy(self) -> None:
        assigned = "\tFSkyguardWeatherProfile Weather = {};\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(assigned, WEATHER)
        self.assertIn("Weather", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(assigned, WEATHER))

    def test_weather_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, WEATHER),
            WEATHER,
        )
        self.assertTrue(has_declaration(section, WEATHER))
        self.assertEqual(
            declaration_count(section, WEATHER),
            1,
        )
        self.assertTrue(
            WEATHER.endswith(";"),
            WEATHER,
        )
        self.assertTrue(
            WEATHER.startswith("FSkyguardWeatherProfile "),
            WEATHER,
        )
        self.assertIn("Weather", WEATHER)
        self.assertNotIn("=", WEATHER)
        self.assertNotIn("TEXT(", WEATHER)
        self.assertNotIn("INDEX_NONE", WEATHER)
        self.assertNotIn("NAME_None", WEATHER)
        self.assertNotIn("UFUNCTION", WEATHER)
        self.assertNotIn("{", WEATHER)
        self.assertNotIn("}", WEATHER)
        self.assertNotIn("return ", WEATHER)
        self.assertNotIn("ProfileId", WEATHER)
        self.assertNotIn("TimeOfDayHours", WEATHER)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_name = (
            "public:\n"
            "\tFSkyguardWeatherProfile\n"
            "\tWeather;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tFSkyguardWeatherProfile   Weather;\n"
            "private:\n"
            "};\n"
        )
        wrap_tab = (
            "public:\n"
            "\tFSkyguardWeatherProfile\tWeather;\n"
            "};\n"
        )
        wrap_indent = (
            "public:\n"
            "\tFSkyguardWeatherProfile\n"
            "\t\tWeather;\n"
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
                has_declaration(section, WEATHER),
                section,
            )
            self.assertEqual(
                require_declaration(section, WEATHER),
                WEATHER,
            )
            self.assertEqual(
                declaration_count(section, WEATHER),
                1,
            )
        one_line = f"{{\npublic:\n\t{WEATHER}\n}}\n"
        self.assertTrue(has_declaration(one_line, WEATHER))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, WEATHER), section)
        self.assertEqual(
            require_declaration(section, WEATHER),
            WEATHER,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{WEATHER}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", WEATHER)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", WEATHER)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{WEATHER}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, WEATHER)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_ENVIRONMENT)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, WEATHER)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_ENVIRONMENT)
        section = public_section(origin_main_header())
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, section)
        self.assertIn(UPROPERTY_ENVIRONMENT, section)

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{WEATHER}\n"
        self.assertNotIn("UFUNCTION", WEATHER)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(WEATHER.startswith("UFUNCTION"), WEATHER)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, WEATHER), section)
        self.assertEqual(
            require_declaration(section, WEATHER),
            WEATHER,
        )

    def test_contract_does_not_lock_weather_cpp_body(self) -> None:
        locked_only = f"{WEATHER}\n"
        self.assertNotIn("{", WEATHER)
        self.assertNotIn("}", WEATHER)
        self.assertNotIn("return ", WEATHER)
        self.assertNotIn(
            "USkyguardMissionDefinition::Weather",
            WEATHER,
        )
        self.assertNotIn(
            "SkyguardMissionDefinition.cpp",
            WEATHER,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", locked_only)
        self.assertNotIn("return false", WEATHER)
        self.assertNotIn("AddError", WEATHER)

    def test_contract_does_not_parse_weather_profile_struct_body(
        self,
    ) -> None:
        locked_only = f"{WEATHER}\n"
        self.assertEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardMissionDefinition.h",
        )
        self.assertNotEqual(HEADER_PATH, TYPES_HEADER_PATH)
        self.assertNotIn("SkyguardMissionTypes.h", HEADER_PATH)
        self.assertNotIn("FName ProfileId;", WEATHER)
        self.assertNotIn("FName ProfileId;", locked_only)
        self.assertNotIn("TimeOfDayHours", WEATHER)
        self.assertNotIn("TimeOfDayHours", locked_only)
        self.assertNotIn("WindSpeedMetersPerSecond", WEATHER)
        self.assertNotIn("Precipitation", WEATHER)
        self.assertNotIn("CloudCoverage", WEATHER)
        self.assertNotIn("ESkyguardMissionWeather", WEATHER)
        self.assertNotIn("GENERATED_BODY()", WEATHER)
        section = public_section(origin_main_header())
        self.assertNotIn("FName ProfileId;", section)
        self.assertNotIn("float TimeOfDayHours = 12.f;", section)
        self.assertNotIn("float WindSpeedMetersPerSecond = 5.f;", section)
        self.assertNotIn("float Precipitation = 0.f;", section)
        self.assertNotIn("float CloudCoverage = 0.25f;", section)
        self.assertTrue(has_declaration(section, WEATHER), section)

    def test_contract_does_not_relock_mission_id(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in MISSION_ID_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("MissionId", WEATHER)
        self.assertNotIn("MissionId", locked_only)
        self.assertNotIn("FName", WEATHER)

    def test_contract_does_not_relock_display_name(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in DISPLAY_NAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("DisplayName", WEATHER)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("FText", WEATHER)

    def test_contract_does_not_relock_campaign_order(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in CAMPAIGN_ORDER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("CampaignOrder", WEATHER)
        self.assertNotIn("CampaignOrder", locked_only)

    def test_contract_does_not_relock_mission_map(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in MISSION_MAP_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("MissionMap", WEATHER)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("TSoftObjectPtr", WEATHER)

    def test_contract_does_not_relock_route(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in ROUTE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("FSkyguardRouteDefinition", WEATHER)
        self.assertNotIn("FSkyguardRouteDefinition", locked_only)

    def test_contract_does_not_relock_objectives(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in OBJECTIVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("Objectives", WEATHER)
        self.assertNotIn("Objectives", locked_only)
        self.assertNotIn("FSkyguardObjectiveDefinition", WEATHER)

    def test_contract_does_not_relock_waves(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in WAVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("Waves", WEATHER)
        self.assertNotIn("Waves", locked_only)
        self.assertNotIn("FSkyguardEnemyWaveDefinition", WEATHER)

    def test_contract_does_not_relock_boss(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in BOSS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("FSkyguardBossDefinition", WEATHER)
        self.assertNotIn("FSkyguardBossDefinition", locked_only)

    def test_contract_does_not_relock_presentation(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in PRESENTATION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("FSkyguardMissionPresentation", WEATHER)
        self.assertNotIn("FSkyguardMissionPresentation", locked_only)

    def test_contract_does_not_relock_score_rules(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in SCORE_RULES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("FSkyguardMissionScoreRules", WEATHER)
        self.assertNotIn("FSkyguardMissionScoreRules", locked_only)

    def test_contract_does_not_relock_prerequisite_mission_ids(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in PREREQUISITE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("PrerequisiteMissionIds", WEATHER)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)

    def test_contract_does_not_relock_required_campaign_medals(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in MEDALS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("RequiredCampaignMedals", WEATHER)
        self.assertNotIn("RequiredCampaignMedals", locked_only)

    def test_contract_does_not_relock_primary_asset_id(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in PRIMARY_ASSET_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("GetPrimaryAssetId", WEATHER)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("FPrimaryAssetId", WEATHER)

    def test_contract_does_not_relock_validate_definition(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in VALIDATE_DEFINITION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("ValidateDefinition", WEATHER)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("OutErrors", WEATHER)
        self.assertNotIn("BlueprintCallable", WEATHER)

    def test_contract_does_not_relock_find_objective(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in FIND_OBJECTIVE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("FindObjective", WEATHER)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("ObjectiveId", WEATHER)

    def test_contract_does_not_relock_campaign_definition_fields(self) -> None:
        locked_only = f"{WEATHER}\n"
        section = public_section(origin_main_header())
        for token in DEFINITION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
            self.assertNotIn(token, section)
        self.assertNotIn("Skyguard52MainCampaign", WEATHER)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", WEATHER)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        for token in SAVE_GAME_CAMPAIGN_ID_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_struct_default_drafts(
        self,
    ) -> None:
        locked_only = f"{WEATHER}\n"
        for token in LEFTOVER_STRUCT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
        self.assertNotIn("defaults_contract", WEATHER)
        self.assertNotIn("defaults_contract", locked_only)
        self.assertNotIn("test_weather_profile_defaults_contract.py", WEATHER)
        self.assertNotIn(
            "test_weather_profile_defaults_contract.py",
            locked_only,
        )
        self.assertNotIn("test_route_definition_fields_contract.py", WEATHER)
        self.assertNotIn(
            "test_route_definition_fields_contract.py",
            locked_only,
        )

    def test_contract_does_not_relock_leftover_weather_struct_fields(
        self,
    ) -> None:
        locked_only = f"{WEATHER}\n"
        for token in LEFTOVER_WEATHER_STRUCT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
        self.assertNotIn("ProfileId", WEATHER)
        self.assertNotIn("ProfileId", locked_only)
        self.assertNotIn("TimeOfDayHours", WEATHER)
        self.assertNotIn("TimeOfDayHours", locked_only)
        self.assertNotIn("WindSpeedMetersPerSecond", WEATHER)
        self.assertNotIn("WindSpeedMetersPerSecond", locked_only)
        self.assertNotIn("Precipitation", WEATHER)
        self.assertNotIn("Precipitation", locked_only)
        self.assertNotIn("CloudCoverage", WEATHER)
        self.assertNotIn("CloudCoverage", locked_only)
        self.assertNotIn("ESkyguardMissionWeather", WEATHER)
        self.assertNotIn("ESkyguardMissionWeather", locked_only)

    def test_contract_does_not_relock_leftover_mission_weather_enum(
        self,
    ) -> None:
        locked_only = f"{WEATHER}\n"
        for token in LEFTOVER_MISSION_WEATHER_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
        self.assertNotIn("ESkyguardMissionWeather", WEATHER)
        self.assertNotIn("ESkyguardMissionWeather", locked_only)
        self.assertNotIn("test_mission_weather_enum_contract.py", WEATHER)
        self.assertNotIn(
            "test_mission_weather_enum_contract.py",
            locked_only,
        )

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{WEATHER}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
        self.assertNotIn("FillResultCombatStats", WEATHER)
        self.assertNotIn("ASkyguardGunner", WEATHER)
        self.assertNotIn("FillAndFinalize", WEATHER)
        self.assertNotIn("FillAndFail", WEATHER)
        self.assertNotIn("ApplyHydraForClusters", WEATHER)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{WEATHER}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{WEATHER}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{WEATHER}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{WEATHER}\n"
        self.assertEqual(
            require_declaration(locked_only, WEATHER),
            WEATHER,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
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
            require_declaration(section, WEATHER),
            WEATHER,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::Weather",
            section,
        )
        self.assertNotIn("FName ProfileId;", section)
        self.assertNotIn("float TimeOfDayHours = 12.f;", section)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, WEATHER)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::Weather",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", WEATHER)
        self.assertNotIn("}", WEATHER)
        self.assertNotIn("return false", WEATHER)
        self.assertNotIn("AddError", WEATHER)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{WEATHER}\n"
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, WEATHER)
            self.assertNotIn(token, locked_only)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{WEATHER}\n"
        section = public_section(origin_main_header())
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
            self.assertNotIn(token, section)
            self.assertNotIn(token, file_text)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "mission Weather contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, WEATHER.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, WEATHER)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"mission Weather contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, WEATHER.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, WEATHER)

    def test_contract_is_weather_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, WEATHER),
            WEATHER,
        )
        locked_only = f"{WEATHER}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WEATHER)
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
        self.assertNotIn("FName ProfileId;", locked_only)
        self.assertNotIn("float TimeOfDayHours = 12.f;", locked_only)
        self.assertNotIn("ESkyguardMissionWeather", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
        for token in LEFTOVER_WEATHER_STRUCT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
        for token in LEFTOVER_MISSION_WEATHER_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WEATHER)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, WEATHER)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, WEATHER)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, WEATHER)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, WEATHER.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", WEATHER)
        self.assertNotIn("{", WEATHER)
        self.assertNotIn("AddError", WEATHER)
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertEqual(WEATHER, "FSkyguardWeatherProfile Weather;")

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
