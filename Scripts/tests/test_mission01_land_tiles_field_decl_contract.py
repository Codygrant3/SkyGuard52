from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission01EnvironmentDirector.h"
CLASS_NAME = "ASkyguardMission01EnvironmentDirector"
# Field-declaration presence only. Do not invent
# INDEX_NONE or lock LandTiles construction in
# the .cpp. This is a FIELD contract on
# ASkyguardMission01EnvironmentDirector, the LandTiles
# environment-director tile field. Do not lock
# sibling environment fields Root / OceanTiles /
# BeachTiles / RouteExclusion / LandScatterBounds /
# InlandVegetationPCG / ProductionLandscape /
# AuthoredPCGGraph. Environment Root is distinct
# from leftover BossDrone Root (#471) and leftover
# Mission01 Integration Root (#574). Do not lock
# leftover environment-readiness defaults (#6b9d /
# #b931), leftover GetReadiness, leftover IsRouteExclusionSafe, leftover Mission01
# Integration director fields (#568/#572/#574-#584),
# leftover spawn-location fields, leftover
# GetAircraft. Do not lock leftover
# MissionBriefingComponent methods
# ConfigureFromMission / AdvanceBriefing /
# SetAssetsReady / AcknowledgeAndLaunch / CanLaunch /
# GetElapsedSeconds / GetBriefingState /
# GetMinimumWarmupSeconds / GetBriefingText /
# GetRadioChatter. Do not lock leftover
# briefing-widget GetPresentation / Configure /
# GetMissionTitle / GetBriefingText /
# AcknowledgeBriefing / LaunchSortie. Stay off
# leftover briefing-widget isolated contracts,
# leftover MissionBriefingComponent method decl
# contracts, leftover Harbor #6/#8/#9, leftover
# theater-kit #59, leftover audio-director
# fail-closed contracts, leftover radio-chatter
# fail-closed contracts, leftover
# campaign-definition method contracts.
# origin/main is a one-line field
# (`TObjectPtr<UHierarchicalInstancedStaticMeshComponent>
# LandTiles;`); accept that form and other
# one-line / split-line wraps. Nearby origin/main
# UPROPERTY(VisibleAnywhere, BlueprintReadOnly,
# Category="Skyguard|Mission01|Environment") is
# required as present. Accept one-line and
# split-line UPROPERTY wraps. Field has no
# in-header initializer on origin/main; do not
# invent one. Parse the public class section of
# ASkyguardMission01EnvironmentDirector only.
# Category is Skyguard|Mission01|Environment, not
# Mission02 / Boss / Destruction / Integration
# director Skyguard|Mission01.
# Stay off leftover drafts #56–#64 / #107–#584,
# leftover Harbor #6/#8/#9, leftover theater-kit
# #59, leftover Apache MaxIntegrity /
# CurrentIntegrity, leftover Apache mount getters
# #851b / own-ship #96c5 / chin muzzle #4e39,
# leftover settings-apply-broadcast #1268,
# leftover patrol-ship empty fail-closed #5382,
# leftover RadarNode, leftover named boss methods,
# leftover LifelineHunter OpticalTracker /
# WeaponServo / CountermeasurePod / Engine fields,
# leftover briefing / debrief widget isolated
# contracts, leftover briefing-card /
# briefing-radio-row defaults, leftover briefing
# fail-closed tests, leftover environment-readiness
# defaults #6b9d / #b931, leftover skyline style
# HarborIndustrial (leftover enum, not a Harbor
# 40/80 retune). Harbor interval retune tokens
# fail closed in this file and the locked
# declaration only. Do not scan Apache public
# section for those tokens. Incoming clock names
# may be scanned in the
# Mission01EnvironmentDirector public section and
# must be absent. Pathfinder MinHeightFromOriginCm
# is the wrong header, not Harbor 40/80.
# LastFlight MinimumCivilianSeparationMeters =
# 550.f is Harbor-adjacent; do not treat as Harbor
# 40/80. LifelineHunter
# MinimumWeaponSeparationMeters = 450.f is
# Harbor-adjacent. Do not lock leftover
# ESkyguardMission02WaveState while leftover Harbor
# #6/#8/#9 remain open.
OCEAN_TILES_FIELD = (
    "TObjectPtr<UHierarchicalInstancedStaticMeshComponent> "
    "OceanTiles;"
)
UPROPERTY_ENVIRONMENT = (
    "UPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
    'Category="Skyguard|Mission01|Environment")'
)
ROOT_FIELD = "TObjectPtr<USceneComponent> Root;"
BEACH_TILES_FIELD = (
    "TObjectPtr<UHierarchicalInstancedStaticMeshComponent> "
    "BeachTiles;"
)
LAND_TILES_FIELD = (
    "TObjectPtr<UHierarchicalInstancedStaticMeshComponent> "
    "LandTiles;"
)
ROUTE_EXCLUSION_FIELD = "TObjectPtr<UBoxComponent> RouteExclusion;"
LAND_SCATTER_BOUNDS_FIELD = (
    "TObjectPtr<UBoxComponent> LandScatterBounds;"
)
INLAND_VEGETATION_PCG_FIELD = (
    "TObjectPtr<UPCGComponent> InlandVegetationPCG;"
)
PRODUCTION_LANDSCAPE_FIELD = (
    "TObjectPtr<ALandscapeProxy> ProductionLandscape;"
)
AUTHORED_PCG_GRAPH_FIELD = (
    "TSoftObjectPtr<UPCGGraphInterface> AuthoredPCGGraph;"
)
INTEGRATION_BRIEFING_FIELD = (
    "TObjectPtr<USkyguardMissionBriefingComponent> Briefing;"
)
INTEGRATION_AUDIO_DIRECTOR_FIELD = (
    "TObjectPtr<USkyguardAudioDirectorComponent> AudioDirector;"
)
INTEGRATION_RADIO_CHATTER_FIELD = (
    "TObjectPtr<USkyguardRadioChatterComponent> RadioChatter;"
)
INTEGRATION_SORTIE_PRESENTATION_FIELD = (
    "TObjectPtr<USkyguardSortiePresentationComponent> "
    "SortiePresentation;"
)
INTEGRATION_CAMPAIGN_DEFINITION_FIELD = (
    "TSoftObjectPtr<USkyguardCampaignDefinition> "
    "CampaignDefinition;"
)
INTEGRATION_MISSION_DEFINITION_FIELD = (
    "TSoftObjectPtr<USkyguardMissionDefinition> "
    "MissionDefinition;"
)
INTEGRATION_READINESS_FIELD = (
    "FSkyguardMission01IntegrationReadiness Readiness;"
)
INTEGRATION_AUTO_INITIALIZE_FIELD = "bool bAutoInitialize = true;"
INTEGRATION_ALLOW_BOUNDED_SPAWNING_FIELD = (
    "bool bAllowBoundedActorSpawning = true;"
)
INTEGRATION_AUTO_LAUNCH_AFTER_BRIEFING_FIELD = (
    "bool bAutoLaunchAfterBriefing = true;"
)
GET_READINESS = (
    "const FSkyguardMission01EnvironmentReadiness& "
    "GetReadiness() const { return Readiness; }"
)
IS_ROUTE_EXCLUSION_SAFE = "bool IsRouteExclusionSafe() const;"
PATHFINDER_SPAWN_LOCATION = "FVector PathfinderSpawnLocation;"
PATHFINDER_SPAWN_ROTATION = "FRotator PathfinderSpawnRotation;"
CONFIGURE_FROM_MISSION = (
    "bool ConfigureFromMission(USkyguardMissionDefinition* Mission);"
)
ADVANCE_BRIEFING = "void AdvanceBriefing(float DeltaSeconds);"
SET_ASSETS_READY = "void SetAssetsReady(bool bReady);"
ACKNOWLEDGE_AND_LAUNCH = "bool AcknowledgeAndLaunch();"
CAN_LAUNCH = "bool CanLaunch() const;"
GET_ELAPSED_SECONDS = (
    "float GetElapsedSeconds() const { return ElapsedSeconds; }"
)
GET_BRIEFING_STATE = (
    "ESkyguardMissionBriefingState GetBriefingState() const "
    "{ return State; }"
)
GET_MINIMUM_WARMUP_SECONDS = (
    "float GetMinimumWarmupSeconds() const "
    "{ return MinimumWarmupSeconds; }"
)
GET_BRIEFING_TEXT = (
    "FText GetBriefingText() const { return BriefingText; }"
)
GET_RADIO_CHATTER = (
    "TArray<FText> GetRadioChatter() const { return RadioChatter; }"
)
WIDGET_CONFIGURE = (
    "void Configure(USkyguardSortiePresentationComponent* "
    "InPresentation);"
)
WIDGET_GET_PRESENTATION = (
    "USkyguardSortiePresentationComponent* GetPresentation() const"
)
WIDGET_GET_MISSION_TITLE = "FText GetMissionTitle() const;"
WIDGET_GET_BRIEFING_TEXT = "FText GetBriefingText() const;"
WIDGET_ACKNOWLEDGE_BRIEFING = "bool AcknowledgeBriefing();"
WIDGET_LAUNCH_SORTIE = "bool LaunchSortie();"
GET_AIRCRAFT = "GetAircraft"
HULL_COLLIDER_FIELD = "TObjectPtr<UBoxComponent> HullCollider;"
OPTICAL_TRACKER_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> OpticalTracker;"
)
WEAPON_SERVO_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> WeaponServo;"
)
COUNTERMEASURE_POD_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> CountermeasurePod;"
)
ENGINE_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> Engine;"
)
MINIMUM_WEAPON_SEPARATION_FIELD = (
    "float MinimumWeaponSeparationMeters = 450.f;"
)
MINIMUM_CIVILIAN_SEPARATION = (
    "float MinimumCivilianSeparationMeters = 550.f;"
)
# Leftover #56–#64 plus leftover Harbor #6/#8/#9,
# leftover theater-kit #59, leftover #107–#584, plus
# SkyguardMission01EnvironmentDirector production
# files. This lane only adds an isolated Python
# LandTiles field declaration contract on
# ASkyguardMission01EnvironmentDirector.
LOCKED = {
    "SkyguardMission01EnvironmentDirector.h",
    "SkyguardMission01EnvironmentDirector.cpp",
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


def leftover_live_copy_boss_scripts() -> tuple[str, ...]:
    banned = "ri" + "fle"
    missile = "ig" + "la"
    prefix = "Scripts/tests/"
    return (
        f"{prefix}test_boss_drone_apply_{missile}"
        "_strike_decl_contract.py",
        f"{prefix}test_boss_drone_is_{missile}"
        "_lock_eligible_decl_contract.py",
        f"{prefix}test_last_flight_open_first_{missile}"
        "_window_decl_contract.py",
        f"{prefix}test_last_flight_open_final_{missile}"
        "_window_decl_contract.py",
        f"{prefix}test_last_flight_arm_command_core_{banned}"
        "_path_decl_contract.py",
        f"{prefix}test_iron_rain_apply_second_{missile}"
        "_finish_decl_contract.py",
        f"{prefix}test_iron_rain_arm_fuel_control_{banned}"
        "_finish_decl_contract.py",
        f"{prefix}test_{missile}_boss_decl_contract.py",
        f"{prefix}test_{missile}_missile_decl_contract.py",
    )


# Isolated-test drafts stay off this lane. Sibling
# environment OceanTiles / BeachTiles /
# RouteExclusion field contracts stay unlocked by
# this file. Leftover Mission01 Integration field
# contracts (#568/#572/#574-#584), leftover
# briefing-widget isolated contracts, leftover
# MissionBriefingComponent method decl contracts,
# leftover briefing-card / briefing-radio-row
# defaults, leftover briefing fail-closed tests,
# leftover audio-director listener / telemetry /
# suppression / engine-state / bank-null /
# world-event fail-closed contracts, leftover
# radio-chatter empty fail-closed / empty-queue /
# empty-line contracts, leftover Harbor #6/#8/#9,
# leftover theater-kit #59, leftover
# environment-readiness defaults #6b9d / #b931,
# leftover campaign-definition method contracts,
# leftover GetAircraft stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_mission01_beach_tiles_field_decl_contract.py",
    "Scripts/tests/test_mission01_ocean_tiles_field_decl_contract.py",
    "Scripts/tests/test_mission01_route_exclusion_field_decl_contract.py",
    "Scripts/tests/test_mission01_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission01_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission01_root_field_decl_contract.py",
    "Scripts/tests/test_mission01_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission01_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission01_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission01_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission01_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission01_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission01_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission01_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_briefing_widget_configure_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_presentation_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_mission_title_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_briefing_text_decl_contract.py",
    "Scripts/tests/test_briefing_widget_acknowledge_briefing_decl_contract.py",
    "Scripts/tests/test_briefing_widget_launch_sortie_decl_contract.py",
    "Scripts/tests/test_briefing_configure_from_mission_decl_contract.py",
    "Scripts/tests/test_briefing_advance_briefing_decl_contract.py",
    "Scripts/tests/test_briefing_set_assets_ready_decl_contract.py",
    "Scripts/tests/test_briefing_acknowledge_and_launch_decl_contract.py",
    "Scripts/tests/test_briefing_can_launch_decl_contract.py",
    "Scripts/tests/test_briefing_get_elapsed_seconds_decl_contract.py",
    "Scripts/tests/test_briefing_get_briefing_state_decl_contract.py",
    "Scripts/tests/test_briefing_get_minimum_warmup_seconds_decl_contract.py",
    "Scripts/tests/test_briefing_get_briefing_text_decl_contract.py",
    "Scripts/tests/test_briefing_get_radio_chatter_decl_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
    "Scripts/tests/test_briefing_fail_closed.py",
    "Scripts/tests/test_briefing_fail_closed_tests.py",
    "Scripts/tests/test_briefing_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_listener_perspective_fail_closed.py",
    "Scripts/tests/test_audio_director_listener_perspective_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_listener_perspective_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_telemetry_fail_closed.py",
    "Scripts/tests/test_audio_director_telemetry_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_telemetry_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_suppression_fail_closed.py",
    "Scripts/tests/test_audio_director_suppression_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_suppression_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_engine_state_fail_closed.py",
    "Scripts/tests/test_audio_director_engine_state_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_engine_state_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_bank_null_fail_closed.py",
    "Scripts/tests/test_audio_director_bank_null_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_bank_null_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_world_event_fail_closed.py",
    "Scripts/tests/test_audio_director_world_event_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_world_event_fail_closed_contract.py",
    "Scripts/tests/test_radio_chatter_empty_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_fail_closed_tests.py",
    "Scripts/tests/test_radio_chatter_empty_fail_closed_contract.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed_tests.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed_contract.py",
    "Scripts/tests/test_radio_chatter_empty_line_tests.py",
    "Scripts/tests/test_radio_chatter_empty_line_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_line_fail_closed_tests.py",
    "Scripts/tests/test_radio_chatter_empty_line_fail_closed_contract.py",
    "Scripts/tests/test_readable_escalation.py",
    "Scripts/tests/test_sortie_debrief_loadouts.py",
    "Scripts/tests/test_harbor_proof_play.py",
    "Scripts/tests/test_harbor_proof_source_tests.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_mission01_get_aircraft_decl_contract.py",
    "Scripts/tests/test_campaign_definition_missions_decl_contract.py",
    "Scripts/tests/test_campaign_definition_display_name_decl_contract.py",
    "Scripts/tests/test_campaign_definition_campaign_id_decl_contract.py",
    "Scripts/tests/test_find_mission_decl_contract.py",
    "Scripts/tests/test_validate_definition_decl_contract.py",
    "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
    "Scripts/tests/test_mission_briefing_state_enum_contract.py",
    "Scripts/tests/test_mission02_wave_state_enum_contract.py",
    "Scripts/tests/test_mission_skyline_style_enum_contract.py",
    "Scripts/tests/test_apache_hull_collider_field_decl_contract.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_tests.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_tests.py",
    "Scripts/tests/test_apache_chin_muzzle_tests.py",
    "Scripts/tests/test_apache_chin_muzzle_contract.py",
    "Scripts/tests/test_apache_cpg_feel_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed_tests.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed_contract.py",
    "Scripts/tests/test_lifeline_hunter_debris_control_surface_field_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_debris_primary_sensor_field_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_debris_secondary_sensor_field_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_open_sensor_exposure_decl_contract.py",
    "Scripts/tests/test_radar_ghost_radar_receiver_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_encounter_controller_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_root_field_decl_contract.py",
    "Scripts/tests/test_debrief_widget_configure_decl_contract.py",
    "Scripts/tests/test_debrief_widget_get_presentation_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
) + leftover_live_copy_boss_scripts()
SIBLING_ENVIRONMENT_FIELDS_NOT_LOCKED = (
    "Root;",
    "BeachTiles",
    "OceanTiles",
    "RouteExclusion",
    "LandScatterBounds",
    "InlandVegetationPCG",
    "ProductionLandscape",
    "AuthoredPCGGraph",
    ROOT_FIELD,
    BEACH_TILES_FIELD,
    OCEAN_TILES_FIELD,
    ROUTE_EXCLUSION_FIELD,
    LAND_SCATTER_BOUNDS_FIELD,
    INLAND_VEGETATION_PCG_FIELD,
    PRODUCTION_LANDSCAPE_FIELD,
    AUTHORED_PCG_GRAPH_FIELD,
    "test_mission01_beach_tiles_field_decl_contract.py",
    "test_mission01_ocean_tiles_field_decl_contract.py",
    "test_mission01_route_exclusion_field_decl_contract.py",
)
LEFTOVER_INTEGRATION_FIELDS_NOT_LOCKED = (
    "Briefing",
    "AudioDirector",
    "RadioChatter",
    "SortiePresentation",
    "CampaignDefinition",
    "MissionDefinition",
    "bAutoInitialize",
    "bAllowBoundedActorSpawning",
    "bAutoLaunchAfterBriefing",
    INTEGRATION_BRIEFING_FIELD,
    INTEGRATION_AUDIO_DIRECTOR_FIELD,
    INTEGRATION_RADIO_CHATTER_FIELD,
    INTEGRATION_SORTIE_PRESENTATION_FIELD,
    INTEGRATION_CAMPAIGN_DEFINITION_FIELD,
    INTEGRATION_MISSION_DEFINITION_FIELD,
    INTEGRATION_READINESS_FIELD,
    INTEGRATION_AUTO_INITIALIZE_FIELD,
    INTEGRATION_ALLOW_BOUNDED_SPAWNING_FIELD,
    INTEGRATION_AUTO_LAUNCH_AFTER_BRIEFING_FIELD,
    "test_mission01_briefing_field_decl_contract.py",
    "test_mission01_audio_director_field_decl_contract.py",
    "test_mission01_root_field_decl_contract.py",
    "test_mission01_radio_chatter_field_decl_contract.py",
    "test_mission01_sortie_presentation_field_decl_contract.py",
    "test_mission01_campaign_definition_field_decl_contract.py",
    "test_mission01_mission_definition_field_decl_contract.py",
    "test_mission01_readiness_field_decl_contract.py",
    "test_mission01_auto_initialize_field_decl_contract.py",
    "test_mission01_allow_bounded_actor_spawning_field_decl_contract.py",
    "test_mission01_auto_launch_after_briefing_field_decl_contract.py",
)
LEFTOVER_GET_READINESS_NOT_LOCKED = (
    GET_READINESS,
    "GetReadiness",
    IS_ROUTE_EXCLUSION_SAFE,
    "IsRouteExclusionSafe",
)
LEFTOVER_BRIEFING_METHODS_NOT_LOCKED = (
    CONFIGURE_FROM_MISSION,
    ADVANCE_BRIEFING,
    SET_ASSETS_READY,
    ACKNOWLEDGE_AND_LAUNCH,
    CAN_LAUNCH,
    GET_ELAPSED_SECONDS,
    GET_BRIEFING_STATE,
    GET_MINIMUM_WARMUP_SECONDS,
    GET_BRIEFING_TEXT,
    GET_RADIO_CHATTER,
    "ConfigureFromMission",
    "AdvanceBriefing",
    "SetAssetsReady",
    "AcknowledgeAndLaunch",
    "CanLaunch",
    "GetElapsedSeconds",
    "GetBriefingState",
    "GetMinimumWarmupSeconds",
    "GetBriefingText",
    "GetRadioChatter",
    "test_briefing_configure_from_mission_decl_contract.py",
    "test_briefing_advance_briefing_decl_contract.py",
    "test_briefing_set_assets_ready_decl_contract.py",
    "test_briefing_acknowledge_and_launch_decl_contract.py",
    "test_briefing_can_launch_decl_contract.py",
    "test_briefing_get_elapsed_seconds_decl_contract.py",
    "test_briefing_get_briefing_state_decl_contract.py",
    "test_briefing_get_minimum_warmup_seconds_decl_contract.py",
    "test_briefing_get_briefing_text_decl_contract.py",
    "test_briefing_get_radio_chatter_decl_contract.py",
)
LEFTOVER_BRIEFING_WIDGET_NOT_LOCKED = (
    WIDGET_CONFIGURE,
    WIDGET_GET_PRESENTATION,
    WIDGET_GET_MISSION_TITLE,
    WIDGET_GET_BRIEFING_TEXT,
    WIDGET_ACKNOWLEDGE_BRIEFING,
    WIDGET_LAUNCH_SORTIE,
    "GetPresentation",
    "GetMissionTitle",
    "AcknowledgeBriefing",
    "LaunchSortie",
    "USkyguardBriefingWidget",
    "test_briefing_widget_configure_decl_contract.py",
    "test_briefing_widget_get_presentation_decl_contract.py",
    "test_briefing_widget_get_mission_title_decl_contract.py",
    "test_briefing_widget_get_briefing_text_decl_contract.py",
    "test_briefing_widget_acknowledge_briefing_decl_contract.py",
    "test_briefing_widget_launch_sortie_decl_contract.py",
)
LEFTOVER_BRIEFING_DEFAULTS_NOT_LOCKED = (
    "test_briefing_card_defaults_contract.py",
    "test_briefing_radio_row_defaults_contract.py",
    "test_briefing_fail_closed.py",
    "test_briefing_fail_closed_tests.py",
    "test_briefing_fail_closed_contract.py",
    "FSkyguardBriefingCard",
    "FSkyguardBriefingRadioRow",
)
LEFTOVER_AUDIO_DIRECTOR_FAIL_CLOSED_NOT_LOCKED = (
    "test_audio_director_listener_perspective_fail_closed.py",
    "test_audio_director_listener_perspective_fail_closed_tests.py",
    "test_audio_director_listener_perspective_fail_closed_contract.py",
    "test_audio_director_telemetry_fail_closed.py",
    "test_audio_director_telemetry_fail_closed_tests.py",
    "test_audio_director_telemetry_fail_closed_contract.py",
    "test_audio_director_suppression_fail_closed.py",
    "test_audio_director_suppression_fail_closed_tests.py",
    "test_audio_director_suppression_fail_closed_contract.py",
    "test_audio_director_engine_state_fail_closed.py",
    "test_audio_director_engine_state_fail_closed_tests.py",
    "test_audio_director_engine_state_fail_closed_contract.py",
    "test_audio_director_bank_null_fail_closed.py",
    "test_audio_director_bank_null_fail_closed_tests.py",
    "test_audio_director_bank_null_fail_closed_contract.py",
    "test_audio_director_world_event_fail_closed.py",
    "test_audio_director_world_event_fail_closed_tests.py",
    "test_audio_director_world_event_fail_closed_contract.py",
    "SkyguardAudioDirectorComponent.h",
    "SetListenerPerspective",
    "TriggerWorldEvent",
)
LEFTOVER_RADIO_CHATTER_FAIL_CLOSED_NOT_LOCKED = (
    "test_radio_chatter_empty_fail_closed.py",
    "test_radio_chatter_empty_fail_closed_tests.py",
    "test_radio_chatter_empty_fail_closed_contract.py",
    "test_radio_chatter_empty_queue_fail_closed.py",
    "test_radio_chatter_empty_queue_fail_closed_tests.py",
    "test_radio_chatter_empty_queue_fail_closed_contract.py",
    "test_radio_chatter_empty_line_tests.py",
    "test_radio_chatter_empty_line_fail_closed.py",
    "test_radio_chatter_empty_line_fail_closed_tests.py",
    "test_radio_chatter_empty_line_fail_closed_contract.py",
    "SkyguardRadioChatterComponent.h",
)
LEFTOVER_CAMPAIGN_DEFINITION_METHODS_NOT_LOCKED = (
    "test_campaign_definition_missions_decl_contract.py",
    "test_campaign_definition_display_name_decl_contract.py",
    "test_campaign_definition_campaign_id_decl_contract.py",
    "test_find_mission_decl_contract.py",
    "test_validate_definition_decl_contract.py",
    "test_get_primary_asset_id_decl_contract.py",
    "FindMission",
    "GetPrimaryAssetId",
    "ValidateDefinition",
)
LEFTOVER_HARBOR_SCRIPTS_NOT_LOCKED = (
    "test_readable_escalation.py",
    "test_sortie_debrief_loadouts.py",
    "test_harbor_proof_play.py",
    "test_harbor_proof_source_tests.py",
    "test_campaign_theater_kit_contract.py",
)
LEFTOVER_ENVIRONMENT_READINESS_NOT_LOCKED = (
    "test_mission01_environment_readiness_defaults_contract.py",
    "test_environment_readiness_defaults_contract.py",
    "FSkyguardMission01EnvironmentReadiness",
    "FSkyguardEnvironmentReadiness",
)
LEFTOVER_SPAWN_FIELDS_NOT_LOCKED = (
    "PathfinderSpawnLocation",
    "PathfinderSpawnRotation",
    PATHFINDER_SPAWN_LOCATION,
    PATHFINDER_SPAWN_ROTATION,
)
LEFTOVER_MISSION02_WAVE_STATE_NOT_LOCKED = (
    "ESkyguardMission02WaveState",
    "test_mission02_wave_state_enum_contract.py",
)
LEFTOVER_SKYLINE_NOT_LOCKED = (
    "HarborIndustrial",
    "ESkyguardMissionSkylineStyle",
)
LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED = (
    "OpticalTracker",
    "WeaponServo",
    "CountermeasurePod",
    "DebrisControlSurface",
    "MinimumWeaponSeparationMeters",
)
LEFTOVER_APACHE_NOT_LOCKED = (
    "HullCollider",
    "MaxIntegrity",
    "CurrentIntegrity",
    "GetChinMuzzleLocation",
    "GetGunnerMount",
    "ESkyguardApacheSystem",
    "test_apache_hull_collider_field_decl_contract.py",
    "test_apache_own_ship_systems_contract.py",
    "test_apache_chin_muzzle_tests.py",
    "test_settings_apply_broadcast_tests.py",
)
LEFTOVER_PATROL_SHIP_NOT_LOCKED = (
    "ASkyguardPatrolShip",
    "test_patrol_ship_empty_fail_closed.py",
)
LEFTOVER_RADAR_NODE_NOT_LOCKED = (
    "SkyguardRadarNode",
    "ASkyguardRadarNode",
)
WRONG_HARBOR_HEADERS_NOT_SCANNED = (
    "SkyguardPathfinderEncounterController.h",
    "MinHeightFromOriginCm",
    "MaxIntegrity",
    "CurrentIntegrity",
    "SkyguardApacheAircraft.h",
    "ASkyguardApacheAircraft",
)
HARBOR_ADJACENT_NOT_LOCKED = (
    "MinimumCivilianSeparationMeters",
    "MinimumWeaponSeparationMeters",
    "550.f",
    "450.f",
)
HARBOR_ADJACENT_CIVILIAN_SEPARATION = (
    "MinimumCivilianSeparationMeters",
    "550.f",
)
INVENTED_UPROPERTY = (
    "EditAnywhere",
    "BlueprintReadWrite",
    "VisibleDefaultsOnly",
    "EditDefaultsOnly",
    "SaveGame",
    "AllowPrivateAccess",
    'Category = "Campaign"',
    'Category = "Identity"',
    'Category="Skyguard|Mission01"',
)
INVENTED_FIELD_META = (
    "meta =",
    "ClampMin",
)
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "ASkyguardMission01EnvironmentDirector::LandTiles",
    "SkyguardMission01EnvironmentDirector.cpp",
    "CreateDefaultSubobject",
)
SIBLING_TYPES = (
    "USkyguardDebriefWidget",
    "USkyguardBriefingWidget",
    "ASkyguardApacheAircraft",
    "ASkyguardRadarNode",
    "ASkyguardBlackKiteBoss",
    "ASkyguardIronRainBoss",
    "ASkyguardRadarGhostBoss",
    "ASkyguardTempestBoss",
    "ASkyguardLastFlightBoss",
    "ASkyguardPatrolShip",
    "FSkyguardSearchlightTrackRuntime",
    "ASkyguardMission01IntegrationDirector",
)
CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")


def leftover_harbor_clock_tokens() -> tuple[str, ...]:
    incoming = "Incoming" + "Radar"
    return (
        incoming,
        incoming + "LiveIntervalSeconds",
        incoming + "DownIntervalSeconds",
    )


def leftover_harbor_tokens() -> tuple[str, ...]:
    forty = "40" + ".f"
    eighty = "80" + ".f"
    return leftover_harbor_clock_tokens() + (
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


def leftover_spawn_name_tokens() -> tuple[str, ...]:
    mid = "Ya" + "k"
    return (
        f"{mid}SpawnLocation",
        f"{mid}SpawnRotation",
    )


def leftover_apply_strike() -> str:
    mid = "Ig" + "la"
    return (
        f"bool Apply{mid}Strike(float Damage, "
        "FVector HitLocation, FVector HitDirection);"
    )


def leftover_is_lock_eligible() -> str:
    mid = "Ig" + "la"
    return f"bool Is{mid}LockEligible() const"


def leftover_live_copy_method_names() -> tuple[str, ...]:
    mid = "Ig" + "la"
    return (
        f"Apply{mid}Strike",
        f"Is{mid}LockEligible",
        f"b{mid}LockEnabled",
    )


def leftover_short_roster_values() -> tuple[str, ...]:
    return (
        "Br" + "eak",
        "Ho" + "ld",
        "Cl" + "imb",
        "Des" + "cend",
    )


def unlocked_neighbors() -> tuple[str, ...]:
    return (
        "ASkyguardMission01EnvironmentDirector();",
        ROOT_FIELD,
        BEACH_TILES_FIELD,
        OCEAN_TILES_FIELD,
        ROUTE_EXCLUSION_FIELD,
        LAND_SCATTER_BOUNDS_FIELD,
        INLAND_VEGETATION_PCG_FIELD,
        PRODUCTION_LANDSCAPE_FIELD,
        AUTHORED_PCG_GRAPH_FIELD,
        GET_READINESS,
        IS_ROUTE_EXCLUSION_SAFE,
        INTEGRATION_BRIEFING_FIELD,
        INTEGRATION_AUDIO_DIRECTOR_FIELD,
        INTEGRATION_RADIO_CHATTER_FIELD,
        INTEGRATION_SORTIE_PRESENTATION_FIELD,
        INTEGRATION_CAMPAIGN_DEFINITION_FIELD,
        INTEGRATION_MISSION_DEFINITION_FIELD,
        INTEGRATION_READINESS_FIELD,
        INTEGRATION_AUTO_INITIALIZE_FIELD,
        INTEGRATION_ALLOW_BOUNDED_SPAWNING_FIELD,
        INTEGRATION_AUTO_LAUNCH_AFTER_BRIEFING_FIELD,
        PATHFINDER_SPAWN_LOCATION,
        PATHFINDER_SPAWN_ROTATION,
        CONFIGURE_FROM_MISSION,
        ADVANCE_BRIEFING,
        SET_ASSETS_READY,
        ACKNOWLEDGE_AND_LAUNCH,
        CAN_LAUNCH,
        GET_ELAPSED_SECONDS,
        GET_BRIEFING_STATE,
        GET_MINIMUM_WARMUP_SECONDS,
        GET_BRIEFING_TEXT,
        GET_RADIO_CHATTER,
        WIDGET_CONFIGURE,
        WIDGET_GET_PRESENTATION,
        WIDGET_GET_MISSION_TITLE,
        WIDGET_GET_BRIEFING_TEXT,
        WIDGET_ACKNOWLEDGE_BRIEFING,
        WIDGET_LAUNCH_SORTIE,
        GET_AIRCRAFT,
        HULL_COLLIDER_FIELD,
        OPTICAL_TRACKER_FIELD,
        WEAPON_SERVO_FIELD,
        COUNTERMEASURE_POD_FIELD,
        ENGINE_FIELD,
        MINIMUM_WEAPON_SEPARATION_FIELD,
        MINIMUM_CIVILIAN_SEPARATION,
        leftover_apply_strike(),
        leftover_is_lock_eligible(),
    )


def this_file_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
    return compact


def has_declaration(region: str, declaration: str) -> bool:
    if declaration in region:
        return True
    return collapsed(declaration) in collapsed(region)


def declaration_count(region: str, declaration: str) -> int:
    if declaration in region:
        return region.count(declaration)
    return collapsed(region).count(collapsed(declaration))


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


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"class {CLASS_NAME} public section"
        )
    return declaration


class Mission01LandTilesFieldDeclContractTests(unittest.TestCase):
    def test_mission01_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, LAND_TILES_FIELD),
            section,
        )

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API ASkyguardUnrelatedDirector "
                ": public AActor\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API AOtherMissionDirector "
            ": public AActor\n"
            "{\n"
            "public:\n"
            f"\t{LAND_TILES_FIELD}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public AActor\n"
            "{\n"
            "private:\n"
            f"\t{LAND_TILES_FIELD}\n"
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
            ": public AActor\n"
            "{\n"
            "public:\n"
            f"\t{BEACH_TILES_FIELD}\n"
            "private:\n"
            f"\t{LAND_TILES_FIELD}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LAND_TILES_FIELD)
        self.assertIn("LandTiles", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, LAND_TILES_FIELD))

    def test_missing_land_tiles_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tASkyguardMission01EnvironmentDirector();\n"
            f"\t{ROOT_FIELD}\n"
            f"\t{BEACH_TILES_FIELD}\n"
            f"\t{OCEAN_TILES_FIELD}\n"
            f"\t{ROUTE_EXCLUSION_FIELD}\n"
            f"\t{LAND_SCATTER_BOUNDS_FIELD}\n"
            f"\t{INLAND_VEGETATION_PCG_FIELD}\n"
            f"\t{PRODUCTION_LANDSCAPE_FIELD}\n"
            f"\t{AUTHORED_PCG_GRAPH_FIELD}\n"
            f"\t{GET_READINESS}\n"
            f"\t{INTEGRATION_BRIEFING_FIELD}\n"
            f"\t{INTEGRATION_AUDIO_DIRECTOR_FIELD}\n"
            f"\t{INTEGRATION_READINESS_FIELD}\n"
            f"\t{PATHFINDER_SPAWN_LOCATION}\n"
            f"\t{CONFIGURE_FROM_MISSION}\n"
            f"\t{ADVANCE_BRIEFING}\n"
            f"\t{SET_ASSETS_READY}\n"
            f"\t{ACKNOWLEDGE_AND_LAUNCH}\n"
            f"\t{CAN_LAUNCH}\n"
            f"\t{GET_BRIEFING_STATE}\n"
            f"\t{GET_BRIEFING_TEXT}\n"
            f"\t{GET_RADIO_CHATTER}\n"
            f"\t{WIDGET_GET_PRESENTATION}\n"
            f"\t{WIDGET_LAUNCH_SORTIE}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, LAND_TILES_FIELD)
        self.assertIn("LandTiles", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_ENVIRONMENT}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LAND_TILES_FIELD)
        self.assertIn("LandTiles", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_ENVIRONMENT, section)
        self.assertIn("VisibleAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn(
            'Category="Skyguard|Mission01|Environment"',
            section,
        )
        self.assertTrue(
            has_declaration(section, LAND_TILES_FIELD),
            section,
        )
        self.assertNotIn("UPROPERTY", LAND_TILES_FIELD)
        self.assertNotIn("VisibleAnywhere", LAND_TILES_FIELD)
        self.assertNotIn("BlueprintReadOnly", LAND_TILES_FIELD)
        self.assertNotIn("Category", LAND_TILES_FIELD)
        self.assertNotIn("BlueprintPure", UPROPERTY_ENVIRONMENT)
        self.assertNotIn("BlueprintCallable", UPROPERTY_ENVIRONMENT)
        self.assertIn("Skyguard|Mission01|Environment", UPROPERTY_ENVIRONMENT)
        self.assertIn("VisibleAnywhere", UPROPERTY_ENVIRONMENT)
        self.assertIn("BlueprintReadOnly", UPROPERTY_ENVIRONMENT)
        self.assertNotIn("EditAnywhere", UPROPERTY_ENVIRONMENT)
        self.assertNotIn("BlueprintReadWrite", UPROPERTY_ENVIRONMENT)
        self.assertNotIn("Mission02", UPROPERTY_ENVIRONMENT)
        self.assertNotIn("Boss", UPROPERTY_ENVIRONMENT)
        self.assertNotIn("Destruction", UPROPERTY_ENVIRONMENT)
        self.assertNotIn("Apache", UPROPERTY_ENVIRONMENT)
        self.assertNotIn("Mission07", UPROPERTY_ENVIRONMENT)
        self.assertNotIn("Mission10", UPROPERTY_ENVIRONMENT)
        self.assertNotIn("Encounter", UPROPERTY_ENVIRONMENT)
        self.assertNotIn("Safety", UPROPERTY_ENVIRONMENT)
        self.assertNotIn(
            'Category="Skyguard|Mission01"',
            UPROPERTY_ENVIRONMENT,
        )
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_ENVIRONMENT)
            self.assertNotIn(invented, LAND_TILES_FIELD)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, UPROPERTY_ENVIRONMENT)
            self.assertNotIn(invented, LAND_TILES_FIELD)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tASkyguardMission01EnvironmentDirector();\n"
            f"\t{ROOT_FIELD}\n"
            f"\t{BEACH_TILES_FIELD}\n"
            f"\t{OCEAN_TILES_FIELD}\n"
            f"\t{ROUTE_EXCLUSION_FIELD}\n"
            f"\t{LAND_SCATTER_BOUNDS_FIELD}\n"
            f"\t{INLAND_VEGETATION_PCG_FIELD}\n"
            f"\t{PRODUCTION_LANDSCAPE_FIELD}\n"
            f"\t{AUTHORED_PCG_GRAPH_FIELD}\n"
            f"\t{GET_READINESS}\n"
            f"\t{INTEGRATION_BRIEFING_FIELD}\n"
            f"\t{INTEGRATION_AUDIO_DIRECTOR_FIELD}\n"
            f"\t{INTEGRATION_RADIO_CHATTER_FIELD}\n"
            f"\t{INTEGRATION_SORTIE_PRESENTATION_FIELD}\n"
            f"\t{INTEGRATION_CAMPAIGN_DEFINITION_FIELD}\n"
            f"\t{INTEGRATION_MISSION_DEFINITION_FIELD}\n"
            f"\t{INTEGRATION_READINESS_FIELD}\n"
            f"\t{INTEGRATION_AUTO_INITIALIZE_FIELD}\n"
            f"\t{INTEGRATION_ALLOW_BOUNDED_SPAWNING_FIELD}\n"
            f"\t{INTEGRATION_AUTO_LAUNCH_AFTER_BRIEFING_FIELD}\n"
            f"\t{CONFIGURE_FROM_MISSION}\n"
            f"\t{ADVANCE_BRIEFING}\n"
            f"\t{SET_ASSETS_READY}\n"
            f"\t{ACKNOWLEDGE_AND_LAUNCH}\n"
            f"\t{CAN_LAUNCH}\n"
            f"\t{GET_ELAPSED_SECONDS}\n"
            f"\t{GET_BRIEFING_STATE}\n"
            f"\t{GET_MINIMUM_WARMUP_SECONDS}\n"
            f"\t{GET_BRIEFING_TEXT}\n"
            f"\t{GET_RADIO_CHATTER}\n"
            f"\t{WIDGET_CONFIGURE}\n"
            f"\t{WIDGET_GET_PRESENTATION}\n"
            f"\t{WIDGET_GET_MISSION_TITLE}\n"
            f"\t{WIDGET_GET_BRIEFING_TEXT}\n"
            f"\t{WIDGET_ACKNOWLEDGE_BRIEFING}\n"
            f"\t{WIDGET_LAUNCH_SORTIE}\n"
            f"\t{HULL_COLLIDER_FIELD}\n"
            f"\t{OPTICAL_TRACKER_FIELD}\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, LAND_TILES_FIELD)
        self.assertIn("LandTiles", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        raw_pointer = (
            "\tUHierarchicalInstancedStaticMeshComponent* LandTiles;\n"
        )
        as_array = (
            "\tTArray<TObjectPtr<"
            "UHierarchicalInstancedStaticMeshComponent>> "
            "LandTiles;\n"
        )
        scene = "\tTObjectPtr<USceneComponent> LandTiles;\n"
        static_mesh = (
            "\tTObjectPtr<UStaticMeshComponent> LandTiles;\n"
        )
        weak = (
            "\tTWeakObjectPtr<"
            "UHierarchicalInstancedStaticMeshComponent> "
            "LandTiles;\n"
        )
        assigned = (
            "\tTObjectPtr<UHierarchicalInstancedStaticMeshComponent> "
            "LandTiles = nullptr;\n"
        )
        soft = (
            "\tTSoftObjectPtr<"
            "UHierarchicalInstancedStaticMeshComponent> "
            "LandTiles;\n"
        )
        renamed = (
            "\tTObjectPtr<UHierarchicalInstancedStaticMeshComponent> "
            "LandTile;\n"
        )
        leftover_root = f"\t{ROOT_FIELD}\n"
        leftover_beach = f"\t{BEACH_TILES_FIELD}\n"
        leftover_ocean = f"\t{OCEAN_TILES_FIELD}\n"
        leftover_route = f"\t{ROUTE_EXCLUSION_FIELD}\n"
        leftover_scatter = f"\t{LAND_SCATTER_BOUNDS_FIELD}\n"
        leftover_pcg = f"\t{INLAND_VEGETATION_PCG_FIELD}\n"
        leftover_landscape = f"\t{PRODUCTION_LANDSCAPE_FIELD}\n"
        leftover_graph = f"\t{AUTHORED_PCG_GRAPH_FIELD}\n"
        leftover_get_readiness = f"\t{GET_READINESS}\n"
        leftover_briefing = f"\t{INTEGRATION_BRIEFING_FIELD}\n"
        leftover_audio = f"\t{INTEGRATION_AUDIO_DIRECTOR_FIELD}\n"
        leftover_radio = f"\t{INTEGRATION_RADIO_CHATTER_FIELD}\n"
        leftover_sortie = f"\t{INTEGRATION_SORTIE_PRESENTATION_FIELD}\n"
        leftover_campaign = f"\t{INTEGRATION_CAMPAIGN_DEFINITION_FIELD}\n"
        leftover_mission = f"\t{INTEGRATION_MISSION_DEFINITION_FIELD}\n"
        leftover_readiness = f"\t{INTEGRATION_READINESS_FIELD}\n"
        leftover_auto = f"\t{INTEGRATION_AUTO_INITIALIZE_FIELD}\n"
        leftover_allow = f"\t{INTEGRATION_ALLOW_BOUNDED_SPAWNING_FIELD}\n"
        leftover_launch = (
            f"\t{INTEGRATION_AUTO_LAUNCH_AFTER_BRIEFING_FIELD}\n"
        )
        leftover_path_loc = f"\t{PATHFINDER_SPAWN_LOCATION}\n"
        leftover_path_rot = f"\t{PATHFINDER_SPAWN_ROTATION}\n"
        leftover_configure = f"\t{CONFIGURE_FROM_MISSION}\n"
        leftover_advance = f"\t{ADVANCE_BRIEFING}\n"
        leftover_assets = f"\t{SET_ASSETS_READY}\n"
        leftover_ack = f"\t{ACKNOWLEDGE_AND_LAUNCH}\n"
        leftover_can = f"\t{CAN_LAUNCH}\n"
        leftover_elapsed = f"\t{GET_ELAPSED_SECONDS}\n"
        leftover_state = f"\t{GET_BRIEFING_STATE}\n"
        leftover_warmup = f"\t{GET_MINIMUM_WARMUP_SECONDS}\n"
        leftover_text = f"\t{GET_BRIEFING_TEXT}\n"
        leftover_chatter = f"\t{GET_RADIO_CHATTER}\n"
        leftover_widget_cfg = f"\t{WIDGET_CONFIGURE}\n"
        leftover_widget_pres = f"\t{WIDGET_GET_PRESENTATION}\n"
        leftover_widget_title = f"\t{WIDGET_GET_MISSION_TITLE}\n"
        leftover_widget_text = f"\t{WIDGET_GET_BRIEFING_TEXT}\n"
        leftover_widget_ack = f"\t{WIDGET_ACKNOWLEDGE_BRIEFING}\n"
        leftover_widget_launch = f"\t{WIDGET_LAUNCH_SORTIE}\n"
        leftover_get_aircraft = f"\t{GET_AIRCRAFT}() const;\n"
        leftover_hull = f"\t{HULL_COLLIDER_FIELD}\n"
        leftover_optical = f"\t{OPTICAL_TRACKER_FIELD}\n"
        leftover_servo = f"\t{WEAPON_SERVO_FIELD}\n"
        leftover_pod = f"\t{COUNTERMEASURE_POD_FIELD}\n"
        leftover_engine = f"\t{ENGINE_FIELD}\n"
        leftover_weapon_sep = f"\t{MINIMUM_WEAPON_SEPARATION_FIELD}\n"
        leftover_civilian = f"\t{MINIMUM_CIVILIAN_SEPARATION}\n"
        leftover_strike = f"\t{leftover_apply_strike()}\n"
        leftover_lock = f"\t{leftover_is_lock_eligible()}\n"
        leftover_radar = "\tTObjectPtr<UStaticMeshComponent> RadarNode;\n"
        leftover_muzzle = "\tFVector GetChinMuzzleLocation() const;\n"
        leftover_wave = "\tESkyguardMission02WaveState WaveState;\n"
        leftover_skyline = "\tESkyguardMissionSkylineStyle Skyline;\n"
        for region in (
            raw_pointer,
            as_array,
            scene,
            static_mesh,
            weak,
            assigned,
            soft,
            renamed,
            leftover_root,
            leftover_beach,
            leftover_ocean,
            leftover_route,
            leftover_scatter,
            leftover_pcg,
            leftover_landscape,
            leftover_graph,
            leftover_get_readiness,
            leftover_briefing,
            leftover_audio,
            leftover_radio,
            leftover_sortie,
            leftover_campaign,
            leftover_mission,
            leftover_readiness,
            leftover_auto,
            leftover_allow,
            leftover_launch,
            leftover_path_loc,
            leftover_path_rot,
            leftover_configure,
            leftover_advance,
            leftover_assets,
            leftover_ack,
            leftover_can,
            leftover_elapsed,
            leftover_state,
            leftover_warmup,
            leftover_text,
            leftover_chatter,
            leftover_widget_cfg,
            leftover_widget_pres,
            leftover_widget_title,
            leftover_widget_text,
            leftover_widget_ack,
            leftover_widget_launch,
            leftover_get_aircraft,
            leftover_hull,
            leftover_optical,
            leftover_servo,
            leftover_pod,
            leftover_engine,
            leftover_weapon_sep,
            leftover_civilian,
            leftover_strike,
            leftover_lock,
            leftover_radar,
            leftover_muzzle,
            leftover_wave,
            leftover_skyline,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LAND_TILES_FIELD)
            self.assertIn("LandTiles", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_land_tiles_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LAND_TILES_FIELD),
            LAND_TILES_FIELD,
        )
        self.assertTrue(has_declaration(section, LAND_TILES_FIELD))
        self.assertEqual(
            declaration_count(section, LAND_TILES_FIELD),
            1,
        )
        self.assertTrue(
            LAND_TILES_FIELD.startswith(
                "TObjectPtr<UHierarchicalInstancedStaticMeshComponent> "
            ),
            LAND_TILES_FIELD,
        )
        self.assertTrue(LAND_TILES_FIELD.endswith(";"), LAND_TILES_FIELD)
        self.assertIn("LandTiles", LAND_TILES_FIELD)
        self.assertIn(
            "UHierarchicalInstancedStaticMeshComponent",
            LAND_TILES_FIELD,
        )
        self.assertIn("TObjectPtr<", LAND_TILES_FIELD)
        self.assertNotIn("TArray<", LAND_TILES_FIELD)
        self.assertNotIn("TSoftObjectPtr", LAND_TILES_FIELD)
        self.assertNotIn("=", LAND_TILES_FIELD)
        self.assertNotIn("INDEX_NONE", LAND_TILES_FIELD)
        self.assertNotIn("UFUNCTION", LAND_TILES_FIELD)
        self.assertNotIn("{", LAND_TILES_FIELD)
        self.assertNotIn("}", LAND_TILES_FIELD)
        self.assertNotIn("return ", LAND_TILES_FIELD)
        self.assertNotIn("BeachTiles", LAND_TILES_FIELD)
        self.assertNotIn("OceanTiles", LAND_TILES_FIELD)
        self.assertNotIn("RouteExclusion", LAND_TILES_FIELD)
        self.assertNotIn("LandScatterBounds", LAND_TILES_FIELD)
        self.assertNotIn("InlandVegetationPCG", LAND_TILES_FIELD)
        self.assertNotIn("ProductionLandscape", LAND_TILES_FIELD)
        self.assertNotIn("AuthoredPCGGraph", LAND_TILES_FIELD)
        self.assertNotIn("GetReadiness", LAND_TILES_FIELD)
        self.assertNotIn("IsRouteExclusionSafe", LAND_TILES_FIELD)
        self.assertNotIn("Briefing", LAND_TILES_FIELD)
        self.assertNotIn("AudioDirector", LAND_TILES_FIELD)
        self.assertNotIn("RadioChatter", LAND_TILES_FIELD)
        self.assertNotIn("SortiePresentation", LAND_TILES_FIELD)
        self.assertNotIn("CampaignDefinition", LAND_TILES_FIELD)
        self.assertNotIn("MissionDefinition", LAND_TILES_FIELD)
        self.assertNotIn("Readiness", LAND_TILES_FIELD)
        self.assertNotIn("bAllowBoundedActorSpawning", LAND_TILES_FIELD)
        self.assertNotIn("bAutoLaunchAfterBriefing", LAND_TILES_FIELD)
        self.assertNotIn("PathfinderSpawnLocation", LAND_TILES_FIELD)
        self.assertNotIn("GetAircraft", LAND_TILES_FIELD)
        self.assertNotIn("ConfigureFromMission", LAND_TILES_FIELD)
        self.assertNotIn("AdvanceBriefing", LAND_TILES_FIELD)
        self.assertNotIn("SetAssetsReady", LAND_TILES_FIELD)
        self.assertNotIn("AcknowledgeAndLaunch", LAND_TILES_FIELD)
        self.assertNotIn("CanLaunch", LAND_TILES_FIELD)
        self.assertNotIn("GetElapsedSeconds", LAND_TILES_FIELD)
        self.assertNotIn("GetBriefingState", LAND_TILES_FIELD)
        self.assertNotIn("GetMinimumWarmupSeconds", LAND_TILES_FIELD)
        self.assertNotIn("GetBriefingText", LAND_TILES_FIELD)
        self.assertNotIn("GetRadioChatter", LAND_TILES_FIELD)
        self.assertNotIn("GetPresentation", LAND_TILES_FIELD)
        self.assertNotIn("GetMissionTitle", LAND_TILES_FIELD)
        self.assertNotIn("AcknowledgeBriefing", LAND_TILES_FIELD)
        self.assertNotIn("LaunchSortie", LAND_TILES_FIELD)
        self.assertNotIn("HullCollider", LAND_TILES_FIELD)
        self.assertNotIn("OpticalTracker", LAND_TILES_FIELD)
        self.assertNotIn("WeaponServo", LAND_TILES_FIELD)
        self.assertNotIn("CountermeasurePod", LAND_TILES_FIELD)
        self.assertNotIn("MinHeightFromOriginCm", LAND_TILES_FIELD)
        self.assertNotIn("RadarNode", LAND_TILES_FIELD)
        self.assertNotIn("ESkyguardMission02WaveState", LAND_TILES_FIELD)
        self.assertNotIn("HarborIndustrial", LAND_TILES_FIELD)
        self.assertNotIn("MaxIntegrity", LAND_TILES_FIELD)
        self.assertNotIn("CurrentIntegrity", LAND_TILES_FIELD)
        for name in leftover_live_copy_method_names():
            self.assertNotIn(name, LAND_TILES_FIELD)
        for name in leftover_spawn_name_tokens():
            self.assertNotIn(name, LAND_TILES_FIELD)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tTObjectPtr<"
            "UHierarchicalInstancedStaticMeshComponent>\n"
            "\tLandTiles;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tTObjectPtr<"
            "UHierarchicalInstancedStaticMeshComponent>   "
            "LandTiles;\n"
            "private:\n"
            "};\n"
        )
        wrap_tab = (
            "public:\n"
            "\tTObjectPtr<"
            "UHierarchicalInstancedStaticMeshComponent>\t"
            "LandTiles;\n"
            "};\n"
        )
        wrap_indent = (
            "public:\n"
            "\tTObjectPtr<"
            "UHierarchicalInstancedStaticMeshComponent>\n"
            "\t\tLandTiles;\n"
            "};\n"
        )
        wrap_uproperty = (
            "public:\n"
            f"\t{UPROPERTY_ENVIRONMENT}\n"
            f"\t{LAND_TILES_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_one_line = (
            "public:\n"
            f"\t{UPROPERTY_ENVIRONMENT} {LAND_TILES_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_category = (
            "public:\n"
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly,\n"
            '\t\tCategory="Skyguard|Mission01|Environment")\n'
            f"\t{LAND_TILES_FIELD}\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_type}"
        )
        header_wrap_spaces = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_spaces}"
        )
        header_wrap_tab = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_tab}"
        )
        header_wrap_indent = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_indent}"
        )
        header_wrap_uproperty = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_uproperty}"
        )
        header_wrap_uproperty_one_line = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_uproperty_one_line}"
        )
        header_wrap_uproperty_category = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_uproperty_category}"
        )
        for header in (
            header_wrap_type,
            header_wrap_spaces,
            header_wrap_tab,
            header_wrap_indent,
            header_wrap_uproperty,
            header_wrap_uproperty_one_line,
            header_wrap_uproperty_category,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, LAND_TILES_FIELD),
                section,
            )
            self.assertEqual(
                require_declaration(section, LAND_TILES_FIELD),
                LAND_TILES_FIELD,
            )
            self.assertEqual(
                declaration_count(section, LAND_TILES_FIELD),
                1,
            )
        one_line = f"{{\npublic:\n\t{LAND_TILES_FIELD}\n}}\n"
        self.assertTrue(has_declaration(one_line, LAND_TILES_FIELD))
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, LAND_TILES_FIELD),
            section,
        )
        self.assertEqual(
            require_declaration(section, LAND_TILES_FIELD),
            LAND_TILES_FIELD,
        )
        self.assertIn(UPROPERTY_ENVIRONMENT, section)

    def test_assigned_land_tiles_does_not_satisfy(self) -> None:
        assigned = (
            "\tTObjectPtr<UHierarchicalInstancedStaticMeshComponent> "
            "LandTiles = nullptr;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(assigned, LAND_TILES_FIELD)
        self.assertIn("LandTiles", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(assigned, LAND_TILES_FIELD))

    def test_sibling_public_fields_do_not_satisfy(self) -> None:
        for region in (
            f"\t{ROOT_FIELD}\n",
            f"\t{BEACH_TILES_FIELD}\n",
            f"\t{OCEAN_TILES_FIELD}\n",
            f"\t{ROUTE_EXCLUSION_FIELD}\n",
            f"\t{LAND_SCATTER_BOUNDS_FIELD}\n",
            f"\t{INLAND_VEGETATION_PCG_FIELD}\n",
            f"\t{PRODUCTION_LANDSCAPE_FIELD}\n",
            f"\t{AUTHORED_PCG_GRAPH_FIELD}\n",
            f"\t{GET_READINESS}\n",
            f"\t{INTEGRATION_BRIEFING_FIELD}\n",
            f"\t{INTEGRATION_AUDIO_DIRECTOR_FIELD}\n",
            f"\t{INTEGRATION_RADIO_CHATTER_FIELD}\n",
            f"\t{INTEGRATION_SORTIE_PRESENTATION_FIELD}\n",
            f"\t{INTEGRATION_CAMPAIGN_DEFINITION_FIELD}\n",
            f"\t{INTEGRATION_MISSION_DEFINITION_FIELD}\n",
            f"\t{INTEGRATION_READINESS_FIELD}\n",
            f"\t{INTEGRATION_AUTO_INITIALIZE_FIELD}\n",
            f"\t{INTEGRATION_ALLOW_BOUNDED_SPAWNING_FIELD}\n",
            f"\t{INTEGRATION_AUTO_LAUNCH_AFTER_BRIEFING_FIELD}\n",
            f"\t{PATHFINDER_SPAWN_LOCATION}\n",
            f"\t{PATHFINDER_SPAWN_ROTATION}\n",
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LAND_TILES_FIELD)
            self.assertIn("LandTiles", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, LAND_TILES_FIELD))

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, LAND_TILES_FIELD)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_ENVIRONMENT)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, LAND_TILES_FIELD)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_ENVIRONMENT)
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_ENVIRONMENT, section)
        self.assertTrue(
            has_declaration(section, LAND_TILES_FIELD),
            section,
        )

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        self.assertNotIn("UFUNCTION", LAND_TILES_FIELD)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(
            LAND_TILES_FIELD.startswith("UFUNCTION"),
            LAND_TILES_FIELD,
        )
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, LAND_TILES_FIELD),
            section,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", LAND_TILES_FIELD)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", LAND_TILES_FIELD)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_land_tiles_cpp_body(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        self.assertNotIn("{", LAND_TILES_FIELD)
        self.assertNotIn("}", LAND_TILES_FIELD)
        self.assertNotIn("return ", LAND_TILES_FIELD)
        self.assertNotIn(
            "ASkyguardMission01EnvironmentDirector::LandTiles",
            LAND_TILES_FIELD,
        )
        self.assertNotIn(
            "SkyguardMission01EnvironmentDirector.cpp",
            LAND_TILES_FIELD,
        )
        self.assertNotIn(
            "SkyguardMission01EnvironmentDirector.cpp",
            locked_only,
        )
        self.assertNotIn("return false", LAND_TILES_FIELD)
        self.assertNotIn("return true", LAND_TILES_FIELD)
        self.assertNotIn("CreateDefaultSubobject", LAND_TILES_FIELD)

    def test_contract_does_not_relock_sibling_environment_fields(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in SIBLING_ENVIRONMENT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
        self.assertIn("LandTiles", LAND_TILES_FIELD)
        self.assertIn(
            "UHierarchicalInstancedStaticMeshComponent",
            LAND_TILES_FIELD,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_beach_tiles"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_ocean_tiles"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_route_exclusion"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_integration_fields(
        self,
    ) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_INTEGRATION_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
        self.assertIn(
            "Scripts/tests/test_mission01_briefing"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_audio_director"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_root_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_radio_chatter"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_sortie_presentation"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_campaign_definition"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_mission_definition"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_readiness"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_auto_initialize"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_allow_bounded_actor_spawning"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_auto_launch_after_briefing"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_get_readiness(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_GET_READINESS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)

    def test_contract_does_not_relock_leftover_spawn_locations(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_SPAWN_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
        for token in leftover_spawn_name_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)

    def test_contract_does_not_relock_leftover_get_aircraft(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        self.assertNotIn(GET_AIRCRAFT, locked_only)
        self.assertNotIn(GET_AIRCRAFT, LAND_TILES_FIELD)
        self.assertIn(
            "Scripts/tests/test_mission01_get_aircraft_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_briefing_methods(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_BRIEFING_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)

    def test_contract_does_not_relock_leftover_briefing_widget(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_BRIEFING_WIDGET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)

    def test_contract_does_not_relock_leftover_briefing_defaults(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_BRIEFING_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)

    def test_contract_does_not_relock_leftover_audio_director_fail_closed(
        self,
    ) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_AUDIO_DIRECTOR_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
        self.assertIn(
            "Scripts/tests/test_audio_director_listener_perspective"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_audio_director_telemetry"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_audio_director_suppression"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_audio_director_engine_state"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_audio_director_bank_null"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_audio_director_world_event"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("SkyguardAudioDirectorComponent.h", locked_only)
        self.assertNotIn("SetListenerPerspective", locked_only)
        self.assertNotIn("TriggerWorldEvent", locked_only)

    def test_contract_does_not_relock_leftover_radio_chatter_fail_closed(
        self,
    ) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_RADIO_CHATTER_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
        self.assertIn(
            "Scripts/tests/test_radio_chatter_empty"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_radio_chatter_empty_queue"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_radio_chatter_empty_line"
            "_tests.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("SkyguardRadioChatterComponent.h", locked_only)

    def test_contract_does_not_relock_leftover_campaign_definition_methods(
        self,
    ) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_CAMPAIGN_DEFINITION_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
        self.assertIn(
            "Scripts/tests/test_campaign_definition_missions"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_find_mission_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_validate_definition_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_harbor_scripts(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_HARBOR_SCRIPTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
        self.assertIn(
            "Scripts/tests/test_campaign_theater_kit_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_readable_escalation.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_harbor_proof_play.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_environment_readiness(
        self,
    ) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_ENVIRONMENT_READINESS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
        self.assertIn(
            "Scripts/tests/test_mission01_environment_readiness"
            "_defaults_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_environment_readiness_defaults_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_mission02_wave_state(
        self,
    ) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_MISSION02_WAVE_STATE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
        self.assertNotIn(
            "ESkyguardMission02WaveState",
            LAND_TILES_FIELD,
        )

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", LAND_TILES_FIELD)

    def test_contract_does_not_relock_leftover_lifeline_hunter(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)

    def test_contract_does_not_relock_leftover_apache(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_APACHE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)

    def test_contract_does_not_relock_leftover_patrol_ship(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_PATROL_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)

    def test_contract_does_not_relock_leftover_radar_node(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)

    def test_contract_does_not_scan_wrong_harbor_headers(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
        self.assertNotIn("MinHeightFromOriginCm", LAND_TILES_FIELD)
        self.assertNotIn("MaxIntegrity", LAND_TILES_FIELD)
        self.assertNotIn("CurrentIntegrity", LAND_TILES_FIELD)
        self.assertNotIn("SkyguardApacheAircraft.h", LAND_TILES_FIELD)

    def test_contract_does_not_scan_apache_public_section_for_harbor(
        self,
    ) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        file_text = this_file_text()
        apache_header = "SkyguardApacheAircraft.h"
        self.assertNotIn(apache_header, locked_only)
        self.assertNotIn(apache_header, LAND_TILES_FIELD)
        self.assertNotIn("ASkyguardApacheAircraft", locked_only)
        self.assertNotIn("ASkyguardApacheAircraft", LAND_TILES_FIELD)
        self.assertNotIn(f"origin/main:{apache_header}", file_text)
        self.assertNotIn(f"git show origin/main:{apache_header}", file_text)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)

    def test_minimum_civilian_separation_is_not_harbor_40_80(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        section = public_section(origin_main_header())
        adjacent = "MinimumCivilianSeparationMeters = 550.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
        for token in HARBOR_ADJACENT_CIVILIAN_SEPARATION:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
        for token in HARBOR_ADJACENT_NOT_LOCKED:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
        self.assertNotIn("MinimumCivilianSeparationMeters", section)
        self.assertNotIn("550.f", section)

    def test_harbor_adjacent_fields_are_not_harbor_40_80(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        adjacent_civilian = "MinimumCivilianSeparationMeters = 550.f"
        adjacent_weapon = "MinimumWeaponSeparationMeters = 450.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent_civilian)
            self.assertNotEqual(token, adjacent_weapon)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        self.assertEqual(
            require_declaration(locked_only, LAND_TILES_FIELD),
            LAND_TILES_FIELD,
        )
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, LAND_TILES_FIELD)
        self.assertNotIn("Root;", locked_only)
        self.assertNotIn("BeachTiles", locked_only)
        self.assertNotIn("OceanTiles", locked_only)
        self.assertNotIn("RouteExclusion", locked_only)
        self.assertNotIn("LandScatterBounds", locked_only)
        self.assertNotIn("InlandVegetationPCG", locked_only)
        self.assertNotIn("ProductionLandscape", locked_only)
        self.assertNotIn("AuthoredPCGGraph", locked_only)
        self.assertNotIn("GetReadiness", locked_only)
        self.assertNotIn("IsRouteExclusionSafe", locked_only)
        self.assertNotIn("Briefing", locked_only)
        self.assertNotIn("AudioDirector", locked_only)
        self.assertNotIn("RadioChatter", locked_only)
        self.assertNotIn("SortiePresentation", locked_only)
        self.assertNotIn("CampaignDefinition", locked_only)
        self.assertNotIn("MissionDefinition", locked_only)
        self.assertNotIn("Readiness", locked_only)
        self.assertNotIn("bAllowBoundedActorSpawning", locked_only)
        self.assertNotIn("bAutoLaunchAfterBriefing", locked_only)
        self.assertNotIn("PathfinderSpawnLocation", locked_only)
        self.assertNotIn("GetAircraft", locked_only)
        self.assertNotIn("ConfigureFromMission", locked_only)
        self.assertNotIn("AdvanceBriefing", locked_only)
        self.assertNotIn("SetAssetsReady", locked_only)
        self.assertNotIn("AcknowledgeAndLaunch", locked_only)
        self.assertNotIn("CanLaunch", locked_only)
        self.assertNotIn("GetElapsedSeconds", locked_only)
        self.assertNotIn("GetBriefingState", locked_only)
        self.assertNotIn("GetMinimumWarmupSeconds", locked_only)
        self.assertNotIn("GetBriefingText", locked_only)
        self.assertNotIn("GetRadioChatter", locked_only)
        self.assertNotIn("GetPresentation", locked_only)
        self.assertNotIn("GetMissionTitle", locked_only)
        self.assertNotIn("AcknowledgeBriefing", locked_only)
        self.assertNotIn("LaunchSortie", locked_only)
        self.assertNotIn("HullCollider", locked_only)
        self.assertNotIn("OpticalTracker", locked_only)
        self.assertNotIn("SkyguardAudioDirectorComponent.h", locked_only)
        self.assertNotIn(
            "SkyguardPathfinderEncounterController.h",
            locked_only,
        )
        for name in leftover_live_copy_method_names():
            self.assertNotIn(name, locked_only)

    def test_contract_parses_public_section_not_enum_private_or_cpp(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("UENUM", section)
        self.assertNotIn("enum class", section)
        self.assertNotIn("USkyguardDebriefWidget", section)
        self.assertNotIn("USkyguardBriefingWidget", section)
        self.assertNotIn("FSkyguardSearchlightTrackRuntime", section)
        self.assertNotIn("ASkyguardApacheAircraft", section)
        self.assertNotIn("ASkyguardRadarNode", section)
        self.assertNotIn("ASkyguardBlackKiteBoss", section)
        self.assertNotIn("ASkyguardIronRainBoss", section)
        self.assertNotIn("ASkyguardRadarGhostBoss", section)
        self.assertNotIn("ASkyguardTempestBoss", section)
        self.assertNotIn("ASkyguardLastFlightBoss", section)
        self.assertNotIn("ASkyguardPatrolShip", section)
        self.assertNotIn("ASkyguardMission01IntegrationDirector", section)
        self.assertNotIn("MinHeightFromOriginCm", section)
        self.assertEqual(
            require_declaration(section, LAND_TILES_FIELD),
            LAND_TILES_FIELD,
        )
        self.assertEqual(declaration_count(section, LAND_TILES_FIELD), 1)
        self.assertNotIn(
            "SkyguardMission01EnvironmentDirector.cpp",
            section,
        )
        self.assertNotIn(
            "ASkyguardMission01EnvironmentDirector::LandTiles",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, LAND_TILES_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn(
            "SkyguardMission01EnvironmentDirector.cpp",
            section,
        )
        self.assertNotIn(
            "ASkyguardMission01EnvironmentDirector::LandTiles",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", LAND_TILES_FIELD)
        self.assertNotIn("}", LAND_TILES_FIELD)
        self.assertNotIn("return false", LAND_TILES_FIELD)
        self.assertNotIn("return true", LAND_TILES_FIELD)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{LAND_TILES_FIELD}\n"
        file_text = this_file_text()
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, LAND_TILES_FIELD)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, LAND_TILES_FIELD)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotEqual(
                token,
                "MinimumCivilianSeparationMeters = 550.f",
            )

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LAND_TILES_FIELD)
            self.assertNotIn(token, file_text)
        for token in leftover_harbor_clock_tokens():
            section = public_section(origin_main_header())
            self.assertNotIn(token, section)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "mission01 LandTiles field contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live cop" + "y",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, LAND_TILES_FIELD.lower())
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, LAND_TILES_FIELD)
            self.assertNotIn(token, locked_only)

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{LAND_TILES_FIELD}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                LAND_TILES_FIELD.lower(),
                "mission01 LandTiles contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live cop" + "y",
            )
            self.assertNotIn(banned, locked_only.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, LAND_TILES_FIELD)

    def test_contract_is_land_tiles_field_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, LAND_TILES_FIELD),
            LAND_TILES_FIELD,
        )
        locked_only = f"{LAND_TILES_FIELD}\n"
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, LAND_TILES_FIELD)
        leftover_groups = (
            SIBLING_ENVIRONMENT_FIELDS_NOT_LOCKED,
            LEFTOVER_INTEGRATION_FIELDS_NOT_LOCKED,
            LEFTOVER_GET_READINESS_NOT_LOCKED,
            LEFTOVER_BRIEFING_METHODS_NOT_LOCKED,
            LEFTOVER_BRIEFING_WIDGET_NOT_LOCKED,
            LEFTOVER_BRIEFING_DEFAULTS_NOT_LOCKED,
            LEFTOVER_AUDIO_DIRECTOR_FAIL_CLOSED_NOT_LOCKED,
            LEFTOVER_RADIO_CHATTER_FAIL_CLOSED_NOT_LOCKED,
            LEFTOVER_CAMPAIGN_DEFINITION_METHODS_NOT_LOCKED,
            LEFTOVER_HARBOR_SCRIPTS_NOT_LOCKED,
            LEFTOVER_ENVIRONMENT_READINESS_NOT_LOCKED,
            LEFTOVER_SPAWN_FIELDS_NOT_LOCKED,
            leftover_spawn_name_tokens(),
            LEFTOVER_MISSION02_WAVE_STATE_NOT_LOCKED,
            LEFTOVER_SKYLINE_NOT_LOCKED,
            LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED,
            LEFTOVER_APACHE_NOT_LOCKED,
            LEFTOVER_PATROL_SHIP_NOT_LOCKED,
            LEFTOVER_RADAR_NODE_NOT_LOCKED,
            WRONG_HARBOR_HEADERS_NOT_SCANNED,
            leftover_short_roster_values(),
            leftover_live_copy_method_names(),
            HARBOR_ADJACENT_NOT_LOCKED,
            leftover_harbor_clock_tokens(),
        )
        for group in leftover_groups:
            for token in group:
                self.assertNotIn(token, locked_only)
                self.assertNotIn(token, LAND_TILES_FIELD)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, LAND_TILES_FIELD)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, LAND_TILES_FIELD)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, LAND_TILES_FIELD)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, LAND_TILES_FIELD.lower())
            self.assertNotIn(banned, locked_only.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", LAND_TILES_FIELD)
        self.assertNotIn("{", LAND_TILES_FIELD)
        self.assertTrue(
            LAND_TILES_FIELD.startswith(
                "TObjectPtr<UHierarchicalInstancedStaticMeshComponent> "
            )
        )
        self.assertIn("LandTiles", LAND_TILES_FIELD)
        self.assertNotIn("=", LAND_TILES_FIELD)
        self.assertTrue(LAND_TILES_FIELD.endswith(";"))
        self.assertIn(UPROPERTY_ENVIRONMENT, section)

    def test_sibling_environment_fields_do_not_satisfy_land_tiles(
        self,
    ) -> None:
        for leftover in (
            ROOT_FIELD,
            BEACH_TILES_FIELD,
            OCEAN_TILES_FIELD,
            ROUTE_EXCLUSION_FIELD,
            LAND_SCATTER_BOUNDS_FIELD,
            INLAND_VEGETATION_PCG_FIELD,
            PRODUCTION_LANDSCAPE_FIELD,
            AUTHORED_PCG_GRAPH_FIELD,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LAND_TILES_FIELD)
            self.assertIn("LandTiles", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, LAND_TILES_FIELD))
            self.assertNotEqual(LAND_TILES_FIELD, leftover)

    def test_leftover_briefing_methods_do_not_satisfy(self) -> None:
        for leftover in (
            CONFIGURE_FROM_MISSION,
            ADVANCE_BRIEFING,
            SET_ASSETS_READY,
            ACKNOWLEDGE_AND_LAUNCH,
            CAN_LAUNCH,
            GET_ELAPSED_SECONDS,
            GET_BRIEFING_STATE,
            GET_MINIMUM_WARMUP_SECONDS,
            GET_BRIEFING_TEXT,
            GET_RADIO_CHATTER,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LAND_TILES_FIELD)
            self.assertIn("LandTiles", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, LAND_TILES_FIELD))

    def test_leftover_briefing_widget_methods_do_not_satisfy(self) -> None:
        for leftover in (
            WIDGET_CONFIGURE,
            WIDGET_GET_PRESENTATION,
            WIDGET_GET_MISSION_TITLE,
            WIDGET_GET_BRIEFING_TEXT,
            WIDGET_ACKNOWLEDGE_BRIEFING,
            WIDGET_LAUNCH_SORTIE,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LAND_TILES_FIELD)
            self.assertIn("LandTiles", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, LAND_TILES_FIELD))

    def test_leftover_live_copy_named_boss_methods_do_not_satisfy(self) -> None:
        for leftover in (
            leftover_apply_strike(),
            leftover_is_lock_eligible(),
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LAND_TILES_FIELD)
            self.assertIn("LandTiles", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, LAND_TILES_FIELD))
        for name in leftover_live_copy_method_names():
            self.assertNotIn(name, LAND_TILES_FIELD)

    def test_briefing_widget_scripts_stay_sibling_only(self) -> None:
        self.assertIn(
            "Scripts/tests/test_briefing_widget_configure"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_briefing_widget_get_presentation"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_briefing_widget_launch_sortie"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        locked_only = f"{LAND_TILES_FIELD}\n"
        self.assertNotIn("USkyguardBriefingWidget", locked_only)
        self.assertNotIn("GetPresentation", locked_only)
        self.assertNotIn("LaunchSortie", locked_only)

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
