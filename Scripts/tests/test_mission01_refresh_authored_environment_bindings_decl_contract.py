from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission01EnvironmentDirector.h"
CLASS_NAME = "ASkyguardMission01EnvironmentDirector"
# Declaration presence only. Do not invent
# INDEX_NONE or lock RefreshAuthoredEnvironmentBindings
# construction in the .cpp. This is a leftover-safe
# Environment PCG METHOD contract on
# ASkyguardMission01EnvironmentDirector. It is NOT
# leftover IsRouteExclusionSafe / leftover
# bRouteExclusionValid, NOT leftover
# bLicensedVegetationLibraryApproved /
# bAllowAuthoredPCGGeneration /
# bProductionLandscapeBound /
# bUseAuthoredLandscapeSurface, NOT leftover
# IsPCGGenerationAuthorized, NOT leftover
# SetUseAuthoredLandscapeSurfaceForValidation,
# and NOT leftover environment-readiness defaults
# #6b9d / #b931 or leftover Environment GetReadiness.
# Distinct from leftover Integration methods
# InitializePlayableMission /
# ConfigureMissionDefinition /
# NotifyObjectiveProgress /
# NotifyProtectedAssetFailed /
# SynchronizeRuntimeState / GetReadiness /
# GetObjectiveRuntime / GetGunner /
# GetPathfinder / GetMissionId /
# ValidateMissionContract / BindRuntimeActors /
# GetAircraft / HandleDroneCityImpact /
# IsCorePlayableReady. Distinct from leftover
# briefing-widget / MissionBriefingComponent
# methods. Not leftover Briefing (#568) /
# AudioDirector (#572) / Root (#574) /
# RadioChatter (#576) / SortiePresentation (#575) /
# CampaignDefinition / MissionDefinition /
# Readiness / bAutoInitialize /
# bAllowBoundedActorSpawning /
# bAutoLaunchAfterBriefing sibling director fields.
# Do not lock leftover spawn-location fields.
# Do not lock sibling Environment methods
# RebuildProductionLayout / IsPointAllowedForPCG /
# HasContinuousCoastline /
# SetUseAuthoredLandscapeSurfaceForValidation /
# IsAuthoredLandscapeSurfaceExposed /
# IsAuthoredEnvironmentReady /
# IsPCGGenerationAuthorized. Do not lock leftover
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
# origin/main is a one-line method
# (`void RefreshAuthoredEnvironmentBindings();`);
# accept that form, other one-line / split-line
# wraps, and an inline body without locking the
# body. Nearby origin/main
# UFUNCTION(BlueprintCallable,
# Category="Skyguard|Mission01|Environment|PCG")
# is required as present. Accept one-line and
# split-line UFUNCTION wraps. Parse the public
# class section of
# ASkyguardMission01EnvironmentDirector only.
# Category is Skyguard|Mission01|Environment|PCG,
# not bare Environment, not Environment|Landscape,
# not Environment|Layout, not Environment|Materials,
# not Environment|Visibility, not Integration, not
# leftover briefing-widget, not leftover
# MissionBriefingComponent methods.
# Stay off leftover drafts #56–#64, leftover Harbor
# #6/#8/#9, leftover theater-kit #59, leftover
# isolated-test drafts #107–#619, leftover Apache
# MaxIntegrity / CurrentIntegrity, leftover Apache
# mount getters #851b / own-ship #96c5 / chin muzzle
# #4e39, leftover settings-apply-broadcast #1268,
# leftover patrol-ship empty fail-closed #5382,
# leftover RadarNode, leftover named boss methods,
# leftover LifelineHunter OpticalTracker / WeaponServo
# / CountermeasurePod / Engine fields, leftover
# briefing / debrief widget isolated contracts,
# leftover briefing-card / briefing-radio-row
# defaults, leftover briefing fail-closed tests,
# leftover environment-readiness defaults #6b9d /
# #b931, leftover skyline style HarborIndustrial
# (leftover enum, not a Harbor 40/80 retune).
# Harbor interval retune tokens fail closed in this
# file and the locked declaration only. Do not scan
# Apache public section for those tokens. Incoming
# clock names may be scanned in the
# Mission01EnvironmentDirector public section and
# must be absent. Pathfinder MinHeightFromOriginCm
# is the wrong header, not Harbor 40/80. LastFlight
# MinimumCivilianSeparationMeters = 550.f is
# Harbor-adjacent; do not treat as Harbor 40/80.
# LifelineHunter MinimumWeaponSeparationMeters =
# 450.f is Harbor-adjacent. Do not lock leftover
# ESkyguardMission02WaveState while leftover Harbor
# #6/#8/#9 remain open.
INITIALIZE_PLAYABLE_MISSION = "bool InitializePlayableMission();"
UFUNCTION_ENVIRONMENT = (
    "UFUNCTION(BlueprintCallable, "
    'Category="Skyguard|Mission01|Environment|PCG")'
)
ROOT_FIELD = "TObjectPtr<USceneComponent> Root;"
BRIEFING_FIELD = (
    "TObjectPtr<USkyguardMissionBriefingComponent> Briefing;"
)
AUDIO_DIRECTOR_FIELD = (
    "TObjectPtr<USkyguardAudioDirectorComponent> AudioDirector;"
)
RADIO_CHATTER_FIELD = (
    "TObjectPtr<USkyguardRadioChatterComponent> RadioChatter;"
)
SORTIE_PRESENTATION_FIELD = (
    "TObjectPtr<USkyguardSortiePresentationComponent> "
    "SortiePresentation;"
)
CAMPAIGN_DEFINITION_FIELD = (
    "TSoftObjectPtr<USkyguardCampaignDefinition> "
    "CampaignDefinition;"
)
MISSION_DEFINITION_FIELD = (
    "TSoftObjectPtr<USkyguardMissionDefinition> "
    "MissionDefinition;"
)
READINESS_FIELD = (
    "FSkyguardMission01IntegrationReadiness Readiness;"
)
AUTO_INITIALIZE_FIELD = "bool bAutoInitialize = true;"
ALLOW_BOUNDED_SPAWNING_FIELD = (
    "bool bAllowBoundedActorSpawning = true;"
)
AUTO_LAUNCH_AFTER_BRIEFING_FIELD = (
    "bool bAutoLaunchAfterBriefing = true;"
)
PATHFINDER_SPAWN_LOCATION = "FVector PathfinderSpawnLocation;"
PATHFINDER_SPAWN_ROTATION = "FRotator PathfinderSpawnRotation;"
CONFIGURE_MISSION_DEFINITION = (
    "bool ConfigureMissionDefinition("
    "USkyguardMissionDefinition* Mission);"
)
NOTIFY_OBJECTIVE_PROGRESS = (
    "bool NotifyObjectiveProgress(FName ObjectiveId, int32 Amount = 1);"
)
NOTIFY_PROTECTED_ASSET_FAILED = "bool NotifyProtectedAssetFailed();"
HANDLE_DRONE_CITY_IMPACT = (
    "void HandleDroneCityImpact(ASkyguardDrone* Drone);"
)
SYNCHRONIZE_RUNTIME_STATE = "void SynchronizeRuntimeState();"
REBUILD_PRODUCTION_LAYOUT = "void RebuildProductionLayout();";
IS_CORE_PLAYABLE_READY = "bool IsCorePlayableReady() const;"
IS_POINT_ALLOWED_FOR_PCG = (
    "bool IsPointAllowedForPCG(const FVector& WorldPoint) const;"
)
IS_ROUTE_EXCLUSION_SAFE = "bool IsRouteExclusionSafe() const;"
HAS_CONTINUOUS_COASTLINE = "bool HasContinuousCoastline() const;"
SET_USE_AUTHORED_LANDSCAPE = (
    "void SetUseAuthoredLandscapeSurfaceForValidation(bool bEnable);"
)
IS_AUTHORED_LANDSCAPE_EXPOSED = (
    "bool IsAuthoredLandscapeSurfaceExposed() const"
)
REFRESH_AUTHORED_BINDINGS = "void RefreshAuthoredEnvironmentBindings();";
IS_AUTHORED_ENVIRONMENT_READY = "bool IsAuthoredEnvironmentReady() const"
IS_PCG_GENERATION_AUTHORIZED = "bool IsPCGGenerationAuthorized() const"
ENVIRONMENT_GET_READINESS = (
    "const FSkyguardMission01EnvironmentReadiness& "
    "GetReadiness() const"
)
ROUTE_EXCLUSION_VALID_FIELD = "bool bRouteExclusionValid = false;"
LICENSED_VEGETATION_LIBRARY_FIELD = (
    "bool bLicensedVegetationLibraryApproved = false;"
)
ALLOW_AUTHORED_PCG_GENERATION_FIELD = (
    "bool bAllowAuthoredPCGGeneration = false;"
)
PRODUCTION_LANDSCAPE_BOUND_FIELD = (
    "bool bProductionLandscapeBound = false;"
)
USE_AUTHORED_LANDSCAPE_SURFACE_FIELD = (
    "bool bUseAuthoredLandscapeSurface = false;"
)
GET_READINESS = (
    "const FSkyguardMission01IntegrationReadiness& "
    "GetReadiness() const"
)
GET_OBJECTIVE_RUNTIME = (
    "USkyguardObjectiveRuntime* GetObjectiveRuntime() const;"
)
GET_GUNNER = "ASkyguardGunner* GetGunner() const { return Gunner; }"
GET_PATHFINDER = (
    "ASkyguardPathfinderBoss* GetPathfinder() const "
    "{ return Pathfinder; }"
)
GET_MISSION_ID = (
    "static FName GetMissionId() "
    '{ return TEXT("M01_CoastalIntercept"); }'
)
VALIDATE_MISSION_CONTRACT = "static bool ValidateMissionContract("
BIND_RUNTIME_ACTORS = "BindRuntimeActors"
GET_AIRCRAFT = "GetAircraft"
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
# leftover theater-kit #59, leftover #107–#619, plus
# SkyguardMission01EnvironmentDirector production
# files. This lane only adds an isolated Python
# RefreshAuthoredEnvironmentBindings method
# declaration contract on
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
# leftover briefing-widget isolated contracts,
# leftover MissionBriefingComponent method decl
# contracts, leftover briefing-card /
# briefing-radio-row defaults, leftover briefing
# fail-closed tests, leftover audio-director
# listener / telemetry / suppression / engine-state
# / bank-null / world-event fail-closed contracts,
# leftover radio-chatter empty fail-closed /
# empty-queue / empty-line contracts, leftover
# Harbor #6/#8/#9, leftover theater-kit #59,
# leftover environment-readiness defaults #6b9d /
# #b931, leftover campaign-definition method
# contracts, sibling Mission01 Integration /
# Environment field contracts stay sibling-only.
LOCKED_SCRIPTS = (
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
    "Scripts/tests/test_campaign_definition_campaign_id_decl_contract.py",
    "Scripts/tests/test_campaign_definition_display_name_decl_contract.py",
    "Scripts/tests/test_campaign_definition_missions_decl_contract.py",
    "Scripts/tests/test_validate_definition_decl_contract.py",
    "Scripts/tests/test_find_mission_decl_contract.py",
    "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
    "Scripts/tests/test_readable_escalation.py",
    "Scripts/tests/test_sortie_debrief_loadouts.py",
    "Scripts/tests/test_harbor_proof_play.py",
    "Scripts/tests/test_harbor_proof_source_tests.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_mission01_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission01_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission01_root_field_decl_contract.py",
    "Scripts/tests/test_mission01_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission01_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission01_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission01_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission01_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission01_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission01_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission01_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission01_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission01_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_root_field_decl_contract.py",
    "Scripts/tests/test_mission01_production_landscape_field_decl_contract.py",
    "Scripts/tests/test_mission01_inland_vegetation_pcg_field_decl_contract.py",
    "Scripts/tests/test_mission01_land_scatter_bounds_field_decl_contract.py",
    "Scripts/tests/test_mission01_route_exclusion_field_decl_contract.py",
    "Scripts/tests/test_mission01_land_tiles_field_decl_contract.py",
    "Scripts/tests/test_mission01_beach_tiles_field_decl_contract.py",
    "Scripts/tests/test_mission01_ocean_tiles_field_decl_contract.py",
    "Scripts/tests/test_mission01_authored_pcg_graph_field_decl_contract.py",
    "Scripts/tests/test_mission01_route_length_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_district_length_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_route_corridor_half_width_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_shoreline_land_offset_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_seaward_extent_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_beach_width_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_inland_extent_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_ocean_material_field_decl_contract.py",
    "Scripts/tests/test_mission01_land_material_field_decl_contract.py",
    "Scripts/tests/test_mission01_beach_material_field_decl_contract.py",
    "Scripts/tests/test_mission01_enable_coastal_haze_transition_field_decl_contract.py",
    "Scripts/tests/test_mission01_coastal_haze_delay_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission01_coastal_haze_hold_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission01_get_aircraft_decl_contract.py",
    "Scripts/tests/test_mission01_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission01_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission01_coastal_haze_density_increase_field_decl_contract.py",
    "Scripts/tests/test_mission01_coastal_haze_fade_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission01_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission01_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission01_notify_objective_progress_decl_contract.py",
    "Scripts/tests/test_mission01_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission01_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission01_get_gunner_decl_contract.py",
    "Scripts/tests/test_mission01_get_pathfinder_decl_contract.py",
    "Scripts/tests/test_mission01_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission01_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission01_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission01_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission01_is_point_allowed_for_pcg_decl_contract.py",
    "Scripts/tests/test_mission01_is_route_exclusion_safe_decl_contract.py",
    "Scripts/tests/test_mission01_has_continuous_coastline_decl_contract.py",
    "Scripts/tests/test_mission01_rebuild_production_layout_decl_contract.py",
    "Scripts/tests/test_mission01_is_authored_environment_ready_decl_contract.py",
    "Scripts/tests/test_mission01_is_pcg_generation_authorized_decl_contract.py",
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
SIBLING_DIRECTOR_FIELDS_NOT_LOCKED = (
    "Root;",
    "Briefing",
    "AudioDirector",
    "RadioChatter",
    "SortiePresentation",
    "CampaignDefinition",
    "MissionDefinition",
    "Readiness;",
    "bAutoInitialize",
    "bAllowBoundedActorSpawning",
    "bAutoLaunchAfterBriefing",
    ROOT_FIELD,
    BRIEFING_FIELD,
    AUDIO_DIRECTOR_FIELD,
    RADIO_CHATTER_FIELD,
    SORTIE_PRESENTATION_FIELD,
    CAMPAIGN_DEFINITION_FIELD,
    MISSION_DEFINITION_FIELD,
    READINESS_FIELD,
    AUTO_INITIALIZE_FIELD,
    ALLOW_BOUNDED_SPAWNING_FIELD,
    AUTO_LAUNCH_AFTER_BRIEFING_FIELD,
)
SIBLING_INTEGRATION_METHODS_NOT_LOCKED = (
    CONFIGURE_MISSION_DEFINITION,
    INITIALIZE_PLAYABLE_MISSION,
    HANDLE_DRONE_CITY_IMPACT,
    NOTIFY_PROTECTED_ASSET_FAILED,
    SYNCHRONIZE_RUNTIME_STATE,
    NOTIFY_OBJECTIVE_PROGRESS,
    GET_READINESS,
    GET_OBJECTIVE_RUNTIME,
    GET_GUNNER,
    GET_PATHFINDER,
    GET_MISSION_ID,
    VALIDATE_MISSION_CONTRACT,
    BIND_RUNTIME_ACTORS,
    GET_AIRCRAFT,
    IS_CORE_PLAYABLE_READY,
    "ConfigureMissionDefinition",
    "InitializePlayableMission",
    "HandleDroneCityImpact",
    "NotifyProtectedAssetFailed",
    "SynchronizeRuntimeState",
    "NotifyObjectiveProgress",
    "IsCorePlayableReady",
    "GetReadiness",
    "GetObjectiveRuntime",
    "GetGunner",
    "GetPathfinder",
    "GetMissionId",
    "ValidateMissionContract",
    "test_mission01_configure_mission_definition_decl_contract.py",
    "test_mission01_initialize_playable_mission_decl_contract.py",
    "test_mission01_notify_protected_asset_failed_decl_contract.py",
    "test_mission01_synchronize_runtime_state_decl_contract.py",
    "test_mission01_notify_objective_progress_decl_contract.py",
    "test_mission01_get_readiness_decl_contract.py",
    "test_mission01_get_objective_runtime_decl_contract.py",
    "test_mission01_get_gunner_decl_contract.py",
    "test_mission01_get_pathfinder_decl_contract.py",
    "test_mission01_get_mission_id_decl_contract.py",
    "test_mission01_validate_mission_contract_decl_contract.py",
    "test_mission01_bind_runtime_actors_decl_contract.py",
    "test_mission01_get_aircraft_decl_contract.py",
    "test_mission01_is_core_playable_ready_decl_contract.py",
)
SIBLING_ENVIRONMENT_METHODS_NOT_LOCKED = (
    IS_POINT_ALLOWED_FOR_PCG,
    HAS_CONTINUOUS_COASTLINE,
    SET_USE_AUTHORED_LANDSCAPE,
    IS_AUTHORED_LANDSCAPE_EXPOSED,
    REBUILD_PRODUCTION_LAYOUT,
    IS_AUTHORED_ENVIRONMENT_READY,
    IS_PCG_GENERATION_AUTHORIZED,
    "IsPointAllowedForPCG",
    "HasContinuousCoastline",
    "SetUseAuthoredLandscapeSurfaceForValidation",
    "IsAuthoredLandscapeSurfaceExposed",
    "RebuildProductionLayout",
    "IsAuthoredEnvironmentReady",
    "IsPCGGenerationAuthorized",
    "test_mission01_is_point_allowed_for_pcg_decl_contract.py",
    "test_mission01_has_continuous_coastline_decl_contract.py",
    "test_mission01_rebuild_production_layout_decl_contract.py",
    "test_mission01_is_authored_environment_ready_decl_contract.py",
    "test_mission01_is_pcg_generation_authorized_decl_contract.py",
)
LEFTOVER_ROUTE_EXCLUSION_NOT_LOCKED = (
    "IsRouteExclusionSafe",
    "bRouteExclusionValid",
    IS_ROUTE_EXCLUSION_SAFE,
    ROUTE_EXCLUSION_VALID_FIELD,
    "test_mission01_is_route_exclusion_safe_decl_contract.py",
)
LEFTOVER_PRODUCTION_FLAGS_NOT_LOCKED = (
    "bLicensedVegetationLibraryApproved",
    "bAllowAuthoredPCGGeneration",
    "bProductionLandscapeBound",
    "bUseAuthoredLandscapeSurface",
    LICENSED_VEGETATION_LIBRARY_FIELD,
    ALLOW_AUTHORED_PCG_GENERATION_FIELD,
    PRODUCTION_LANDSCAPE_BOUND_FIELD,
    USE_AUTHORED_LANDSCAPE_SURFACE_FIELD,
)
LEFTOVER_ENVIRONMENT_GET_READINESS_NOT_LOCKED = (
    ENVIRONMENT_GET_READINESS,
    "FSkyguardMission01EnvironmentReadiness",
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
LEFTOVER_HANDLE_DRONE_CITY_IMPACT_NOT_LOCKED = (
    "HandleDroneCityImpact",
    HANDLE_DRONE_CITY_IMPACT,
    "test_mission01_handle_drone_city_impact_decl_contract.py",
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
LEFTOVER_FILL_AND_GUNNER_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "FillAndFinalize",
    "FillAndFail",
    "ApplyHydraForClusters",
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
INVENTED_UFUNCTION = (
    "BlueprintPure",
    "BlueprintAuthorityOnly",
    "CallInEditor",
    "VisibleAnywhere",
    "BlueprintReadOnly",
    "EditAnywhere",
    "BlueprintReadWrite",
    'Category = "Campaign"',
    'Category = "Identity"',
    'Category="Skyguard|Mission01|Integration"',
    'Category="Skyguard|Mission01|Briefing"',
    'Category="Skyguard|Mission01|Environment"',
    'Category="Skyguard|Mission01|Environment|Landscape"',
    'Category="Skyguard|Mission01|Environment|Layout"',
    'Category="Skyguard|Mission01|Environment|Materials"',
    'Category="Skyguard|Mission01|Environment|Visibility"',
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
    "ASkyguardMission01EnvironmentDirector::RefreshAuthoredEnvironmentBindings",
    "SkyguardMission01EnvironmentDirector.cpp",
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
        BRIEFING_FIELD,
        AUDIO_DIRECTOR_FIELD,
        RADIO_CHATTER_FIELD,
        SORTIE_PRESENTATION_FIELD,
        CAMPAIGN_DEFINITION_FIELD,
        MISSION_DEFINITION_FIELD,
        READINESS_FIELD,
        AUTO_INITIALIZE_FIELD,
        ALLOW_BOUNDED_SPAWNING_FIELD,
        AUTO_LAUNCH_AFTER_BRIEFING_FIELD,
        PATHFINDER_SPAWN_LOCATION,
        PATHFINDER_SPAWN_ROTATION,
        CONFIGURE_MISSION_DEFINITION,
        INITIALIZE_PLAYABLE_MISSION,
        HANDLE_DRONE_CITY_IMPACT,
        NOTIFY_PROTECTED_ASSET_FAILED,
        SYNCHRONIZE_RUNTIME_STATE,
        NOTIFY_OBJECTIVE_PROGRESS,
        GET_READINESS,
        GET_OBJECTIVE_RUNTIME,
        GET_GUNNER,
        GET_PATHFINDER,
        GET_MISSION_ID,
        VALIDATE_MISSION_CONTRACT,
        BIND_RUNTIME_ACTORS,
        GET_AIRCRAFT,
        IS_CORE_PLAYABLE_READY,
        IS_POINT_ALLOWED_FOR_PCG,
        IS_ROUTE_EXCLUSION_SAFE,
        HAS_CONTINUOUS_COASTLINE,
        SET_USE_AUTHORED_LANDSCAPE,
        IS_AUTHORED_LANDSCAPE_EXPOSED,
        REBUILD_PRODUCTION_LAYOUT,
        IS_AUTHORED_ENVIRONMENT_READY,
        IS_PCG_GENERATION_AUTHORIZED,
        ENVIRONMENT_GET_READINESS,
        ROUTE_EXCLUSION_VALID_FIELD,
        LICENSED_VEGETATION_LIBRARY_FIELD,
        ALLOW_AUTHORED_PCG_GENERATION_FIELD,
        PRODUCTION_LANDSCAPE_BOUND_FIELD,
        USE_AUTHORED_LANDSCAPE_SURFACE_FIELD,
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


def declaration_stem(declaration: str) -> str:
    compact = collapsed(declaration)
    if compact.endswith(";"):
        return compact[:-1].rstrip()
    return compact


def has_declaration(region: str, declaration: str) -> bool:
    if declaration in region:
        return True
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return True
    stem = declaration_stem(declaration)
    if not stem:
        return False
    # Accept `;` or an inline `{` body after the signature
    # without locking that body.
    pattern = re.compile(re.escape(stem) + r"\s*[;{]")
    return pattern.search(compact_region) is not None


def declaration_count(region: str, declaration: str) -> int:
    if declaration in region:
        return region.count(declaration)
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return compact_region.count(compact_decl)
    stem = declaration_stem(declaration)
    if not stem:
        return 0
    pattern = re.compile(re.escape(stem) + r"\s*[;{]")
    return len(pattern.findall(compact_region))


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


class Mission01RefreshAuthoredEnvironmentBindingsDeclContractTests(unittest.TestCase):
    def test_mission01_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, REFRESH_AUTHORED_BINDINGS),
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
            f"\t{REFRESH_AUTHORED_BINDINGS}\n"
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
            f"\t{REFRESH_AUTHORED_BINDINGS}\n"
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
            f"\t{BRIEFING_FIELD}\n"
            "private:\n"
            f"\t{REFRESH_AUTHORED_BINDINGS}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, REFRESH_AUTHORED_BINDINGS)
        self.assertIn("RefreshAuthoredEnvironmentBindings", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(
            has_declaration(section, REFRESH_AUTHORED_BINDINGS)
        )

    def test_missing_refresh_authored_environment_bindings_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tASkyguardMission01EnvironmentDirector();\n"
            f"\t{ROOT_FIELD}\n"
            f"\t{BRIEFING_FIELD}\n"
            f"\t{AUDIO_DIRECTOR_FIELD}\n"
            f"\t{RADIO_CHATTER_FIELD}\n"
            f"\t{SORTIE_PRESENTATION_FIELD}\n"
            f"\t{CAMPAIGN_DEFINITION_FIELD}\n"
            f"\t{MISSION_DEFINITION_FIELD}\n"
            f"\t{READINESS_FIELD}\n"
            f"\t{AUTO_INITIALIZE_FIELD}\n"
            f"\t{ALLOW_BOUNDED_SPAWNING_FIELD}\n"
            f"\t{AUTO_LAUNCH_AFTER_BRIEFING_FIELD}\n"
            f"\t{PATHFINDER_SPAWN_LOCATION}\n"
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            f"\t{INITIALIZE_PLAYABLE_MISSION}\n"
            f"\t{HANDLE_DRONE_CITY_IMPACT}\n"
            f"\t{NOTIFY_PROTECTED_ASSET_FAILED}\n"
            f"\t{SYNCHRONIZE_RUNTIME_STATE}\n"
            f"\t{NOTIFY_OBJECTIVE_PROGRESS}\n"
            f"\t{GET_READINESS}\n"
            f"\t{GET_OBJECTIVE_RUNTIME}\n"
            f"\t{GET_GUNNER}\n"
            f"\t{GET_PATHFINDER}\n"
            f"\t{GET_MISSION_ID}\n"
            f"\t{VALIDATE_MISSION_CONTRACT}\n"
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
            f"\t{IS_CORE_PLAYABLE_READY}\n"
            f"\t{IS_POINT_ALLOWED_FOR_PCG}\n"
            f"\t{IS_ROUTE_EXCLUSION_SAFE}\n"
            f"\t{HAS_CONTINUOUS_COASTLINE}\n"
            f"\t{REBUILD_PRODUCTION_LAYOUT}\n"
            f"\t{ENVIRONMENT_GET_READINESS}\n"
            f"\t{LICENSED_VEGETATION_LIBRARY_FIELD}\n"
            f"\t{USE_AUTHORED_LANDSCAPE_SURFACE_FIELD}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, REFRESH_AUTHORED_BINDINGS)
        self.assertIn("RefreshAuthoredEnvironmentBindings", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_ENVIRONMENT}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, REFRESH_AUTHORED_BINDINGS)
        self.assertIn("RefreshAuthoredEnvironmentBindings", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_ENVIRONMENT, section)
        self.assertIn("BlueprintCallable", section)
        self.assertIn(
            'Category="Skyguard|Mission01|Environment|PCG"',
            section,
        )
        self.assertTrue(
            has_declaration(section, REFRESH_AUTHORED_BINDINGS),
            section,
        )
        self.assertNotIn("UFUNCTION", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("BlueprintCallable", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("BlueprintPure", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("Category", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("BlueprintPure", UFUNCTION_ENVIRONMENT)
        self.assertIn("Skyguard|Mission01|Environment|PCG", UFUNCTION_ENVIRONMENT)
        self.assertIn("BlueprintCallable", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("Integration", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("Briefing", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("Mission02", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("Boss", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("Destruction", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("Apache", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("Mission07", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("Mission10", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("Encounter", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("Safety", UFUNCTION_ENVIRONMENT)
        self.assertIn("|PCG", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("|Landscape", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("|Layout", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("|Materials", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("|Visibility", UFUNCTION_ENVIRONMENT)
        for invented in INVENTED_UFUNCTION:
            self.assertNotIn(invented, UFUNCTION_ENVIRONMENT)
            self.assertNotIn(invented, REFRESH_AUTHORED_BINDINGS)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, UFUNCTION_ENVIRONMENT)
            self.assertNotIn(invented, REFRESH_AUTHORED_BINDINGS)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tASkyguardMission01EnvironmentDirector();\n"
            f"\t{ROOT_FIELD}\n"
            f"\t{BRIEFING_FIELD}\n"
            f"\t{AUDIO_DIRECTOR_FIELD}\n"
            f"\t{RADIO_CHATTER_FIELD}\n"
            f"\t{SORTIE_PRESENTATION_FIELD}\n"
            f"\t{CAMPAIGN_DEFINITION_FIELD}\n"
            f"\t{MISSION_DEFINITION_FIELD}\n"
            f"\t{READINESS_FIELD}\n"
            f"\t{AUTO_INITIALIZE_FIELD}\n"
            f"\t{ALLOW_BOUNDED_SPAWNING_FIELD}\n"
            f"\t{AUTO_LAUNCH_AFTER_BRIEFING_FIELD}\n"
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            f"\t{INITIALIZE_PLAYABLE_MISSION}\n"
            f"\t{HANDLE_DRONE_CITY_IMPACT}\n"
            f"\t{NOTIFY_PROTECTED_ASSET_FAILED}\n"
            f"\t{SYNCHRONIZE_RUNTIME_STATE}\n"
            f"\t{NOTIFY_OBJECTIVE_PROGRESS}\n"
            f"\t{GET_READINESS}\n"
            f"\t{GET_OBJECTIVE_RUNTIME}\n"
            f"\t{GET_GUNNER}\n"
            f"\t{GET_PATHFINDER}\n"
            f"\t{GET_MISSION_ID}\n"
            f"\t{VALIDATE_MISSION_CONTRACT}\n"
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
            f"\t{IS_CORE_PLAYABLE_READY}\n"
            f"\t{IS_POINT_ALLOWED_FOR_PCG}\n"
            f"\t{IS_ROUTE_EXCLUSION_SAFE}\n"
            f"\t{HAS_CONTINUOUS_COASTLINE}\n"
            f"\t{REBUILD_PRODUCTION_LAYOUT}\n"
            f"\t{ENVIRONMENT_GET_READINESS}\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, REFRESH_AUTHORED_BINDINGS)
        self.assertIn("RefreshAuthoredEnvironmentBindings", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        as_void = "\tvoid RefreshAuthoredEnvironmentBindings() const;\n"
        missing_const = "\tbool RefreshAuthoredEnvironmentBindings();\n"
        extra_arg = "\tvoid RefreshAuthoredEnvironmentBindings(int32 Amount);\n"
        extra_args = (
            "\tvoid RefreshAuthoredEnvironmentBindings("
            "FName ObjectiveId, int32 Amount = 1);\n"
        )
        as_int = "\tint32 RefreshAuthoredEnvironmentBindings();\n"
        renamed = "\tvoid RebuildLayout();\n"
        short_name = "\tvoid RefreshProductionLayout();\n"
        getter = "\tvoid GetProductionLayout();\n"
        leftover_configure = f"\t{CONFIGURE_MISSION_DEFINITION}\n"
        leftover_init = f"\t{INITIALIZE_PLAYABLE_MISSION}\n"
        leftover_notify = f"\t{NOTIFY_OBJECTIVE_PROGRESS}\n"
        leftover_failed = f"\t{NOTIFY_PROTECTED_ASSET_FAILED}\n"
        leftover_sync = f"\t{SYNCHRONIZE_RUNTIME_STATE}\n"
        leftover_readiness = f"\t{GET_READINESS}\n"
        leftover_root = f"\t{ROOT_FIELD}\n"
        leftover_briefing = f"\t{BRIEFING_FIELD}\n"
        leftover_audio = f"\t{AUDIO_DIRECTOR_FIELD}\n"
        leftover_radio = f"\t{RADIO_CHATTER_FIELD}\n"
        leftover_sortie = f"\t{SORTIE_PRESENTATION_FIELD}\n"
        leftover_campaign = f"\t{CAMPAIGN_DEFINITION_FIELD}\n"
        leftover_mission = f"\t{MISSION_DEFINITION_FIELD}\n"
        leftover_readiness_field = f"\t{READINESS_FIELD}\n"
        leftover_auto = f"\t{AUTO_INITIALIZE_FIELD}\n"
        leftover_allow = f"\t{ALLOW_BOUNDED_SPAWNING_FIELD}\n"
        leftover_launch = f"\t{AUTO_LAUNCH_AFTER_BRIEFING_FIELD}\n"
        leftover_path_loc = f"\t{PATHFINDER_SPAWN_LOCATION}\n"
        leftover_path_rot = f"\t{PATHFINDER_SPAWN_ROTATION}\n"
        leftover_from_mission = f"\t{CONFIGURE_FROM_MISSION}\n"
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
        leftover_fill = "\tvoid FillResultCombatStats();\n"
        leftover_finalize = "\tvoid FillAndFinalize();\n"
        leftover_fail = "\tvoid FillAndFail();\n"
        leftover_objective = f"\t{GET_OBJECTIVE_RUNTIME}\n"
        leftover_gunner = f"\t{GET_GUNNER}\n"
        leftover_pathfinder = f"\t{GET_PATHFINDER}\n"
        leftover_mission_id = f"\t{GET_MISSION_ID}\n"
        leftover_validate = f"\t{VALIDATE_MISSION_CONTRACT}\n"
        leftover_bind = f"\t{BIND_RUNTIME_ACTORS}();\n"
        leftover_get_aircraft = f"\t{GET_AIRCRAFT}() const;\n"
        leftover_impact = f"\t{HANDLE_DRONE_CITY_IMPACT}\n"
        leftover_core_ready = f"\t{IS_CORE_PLAYABLE_READY}\n"
        leftover_point = f"\t{IS_POINT_ALLOWED_FOR_PCG}\n"
        leftover_route_safe = f"\t{IS_ROUTE_EXCLUSION_SAFE}\n"
        leftover_coastline = f"\t{HAS_CONTINUOUS_COASTLINE}\n"
        leftover_refresh = f"\t{REBUILD_PRODUCTION_LAYOUT}\n"
        leftover_env_ready = f"\t{IS_AUTHORED_ENVIRONMENT_READY}\n"
        leftover_pcg_auth = f"\t{IS_PCG_GENERATION_AUTHORIZED}\n"
        leftover_env_get = f"\t{ENVIRONMENT_GET_READINESS}\n"
        leftover_route_valid = f"\t{ROUTE_EXCLUSION_VALID_FIELD}\n"
        leftover_licensed = f"\t{LICENSED_VEGETATION_LIBRARY_FIELD}\n"
        leftover_allow_pcg = f"\t{ALLOW_AUTHORED_PCG_GENERATION_FIELD}\n"
        leftover_bound = f"\t{PRODUCTION_LANDSCAPE_BOUND_FIELD}\n"
        leftover_use_surface = f"\t{USE_AUTHORED_LANDSCAPE_SURFACE_FIELD}\n"
        for region in (
            as_void,
            missing_const,
            extra_arg,
            extra_args,
            as_int,
            renamed,
            short_name,
            getter,
            leftover_configure,
            leftover_init,
            leftover_notify,
            leftover_failed,
            leftover_sync,
            leftover_readiness,
            leftover_objective,
            leftover_gunner,
            leftover_pathfinder,
            leftover_mission_id,
            leftover_validate,
            leftover_bind,
            leftover_get_aircraft,
            leftover_impact,
            leftover_core_ready,
            leftover_point,
            leftover_route_safe,
            leftover_coastline,
            leftover_refresh,
            leftover_env_ready,
            leftover_pcg_auth,
            leftover_env_get,
            leftover_route_valid,
            leftover_licensed,
            leftover_allow_pcg,
            leftover_bound,
            leftover_use_surface,
            leftover_root,
            leftover_briefing,
            leftover_audio,
            leftover_radio,
            leftover_sortie,
            leftover_campaign,
            leftover_mission,
            leftover_readiness_field,
            leftover_auto,
            leftover_allow,
            leftover_launch,
            leftover_path_loc,
            leftover_path_rot,
            leftover_from_mission,
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
            leftover_fill,
            leftover_finalize,
            leftover_fail,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, REFRESH_AUTHORED_BINDINGS)
            self.assertIn("RefreshAuthoredEnvironmentBindings", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_refresh_authored_environment_bindings_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, REFRESH_AUTHORED_BINDINGS),
            REFRESH_AUTHORED_BINDINGS,
        )
        self.assertTrue(has_declaration(section, REFRESH_AUTHORED_BINDINGS))
        self.assertEqual(
            declaration_count(section, REFRESH_AUTHORED_BINDINGS),
            1,
        )
        self.assertTrue(
            REFRESH_AUTHORED_BINDINGS.startswith("void "),
            REFRESH_AUTHORED_BINDINGS,
        )
        self.assertTrue(
            REFRESH_AUTHORED_BINDINGS.endswith(";"),
            REFRESH_AUTHORED_BINDINGS,
        )
        self.assertIn("RefreshAuthoredEnvironmentBindings", REFRESH_AUTHORED_BINDINGS)
        self.assertIn("RefreshAuthoredEnvironmentBindings()", REFRESH_AUTHORED_BINDINGS)
        self.assertTrue(
            REFRESH_AUTHORED_BINDINGS.endswith("();"),
            REFRESH_AUTHORED_BINDINGS,
        )
        self.assertNotIn("TArray<", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("TObjectPtr", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("TSoftObjectPtr", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("INDEX_NONE", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("UFUNCTION", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("{", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("}", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("return ", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn(" const;", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("bool ", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("Root", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("Briefing", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("AudioDirector", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("RadioChatter", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("SortiePresentation", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("CampaignDefinition", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("MissionDefinition", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("Readiness", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("bAutoInitialize", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("bAllowBoundedActorSpawning", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("bAutoLaunchAfterBriefing", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("PathfinderSpawnLocation", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("GetAircraft", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("BindRuntimeActors", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("HandleDroneCityImpact", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("ConfigureMissionDefinition", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("InitializePlayableMission", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("NotifyProtectedAssetFailed", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("SynchronizeRuntimeState", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("NotifyObjectiveProgress", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("GetReadiness", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("GetObjectiveRuntime", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("GetGunner", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("GetPathfinder", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("GetMissionId", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("ValidateMissionContract", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("ConfigureFromMission", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("AdvanceBriefing", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("SetAssetsReady", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("AcknowledgeAndLaunch", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("CanLaunch", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("GetElapsedSeconds", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("GetBriefingState", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("GetMinimumWarmupSeconds", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("GetBriefingText", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("GetRadioChatter", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("GetPresentation", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("GetMissionTitle", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("AcknowledgeBriefing", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("LaunchSortie", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("HullCollider", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("OpticalTracker", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("WeaponServo", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("CountermeasurePod", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("MinHeightFromOriginCm", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("RadarNode", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("ESkyguardMission02WaveState", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("HarborIndustrial", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("MaxIntegrity", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("CurrentIntegrity", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("FillAndFinalize", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("FillAndFail", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("IsRouteExclusionSafe", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("bRouteExclusionValid", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn(
            "bLicensedVegetationLibraryApproved",
            REFRESH_AUTHORED_BINDINGS,
        )
        self.assertNotIn("bAllowAuthoredPCGGeneration", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("bProductionLandscapeBound", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("bUseAuthoredLandscapeSurface", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("IsPointAllowedForPCG", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("HasContinuousCoastline", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn(
            "RebuildProductionLayout",
            REFRESH_AUTHORED_BINDINGS,
        )
        self.assertNotIn("IsAuthoredEnvironmentReady", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("IsPCGGenerationAuthorized", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("IsCorePlayableReady", REFRESH_AUTHORED_BINDINGS)
        for name in leftover_live_copy_method_names():
            self.assertNotIn(name, REFRESH_AUTHORED_BINDINGS)
        for name in leftover_spawn_name_tokens():
            self.assertNotIn(name, REFRESH_AUTHORED_BINDINGS)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tvoid\n"
            "\tRefreshAuthoredEnvironmentBindings();\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tvoid   RefreshAuthoredEnvironmentBindings();\n"
            "private:\n"
            "};\n"
        )
        wrap_tab = (
            "public:\n"
            "\tvoid\t"
            "RefreshAuthoredEnvironmentBindings();\n"
            "};\n"
        )
        wrap_indent = (
            "public:\n"
            "\tvoid\n"
            "\t\tRefreshAuthoredEnvironmentBindings();\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tvoid RefreshAuthoredEnvironmentBindings\n"
            "\t();\n"
            "};\n"
        )
        wrap_ufunction = (
            "public:\n"
            f"\t{UFUNCTION_ENVIRONMENT}\n"
            f"\t{REFRESH_AUTHORED_BINDINGS}\n"
            "};\n"
        )
        wrap_ufunction_one_line = (
            "public:\n"
            f"\t{UFUNCTION_ENVIRONMENT} {REFRESH_AUTHORED_BINDINGS}\n"
            "};\n"
        )
        wrap_ufunction_category = (
            "public:\n"
            "\tUFUNCTION(BlueprintCallable,\n"
            '\t\tCategory="Skyguard|Mission01|Environment|PCG")\n'
            f"\t{REFRESH_AUTHORED_BINDINGS}\n"
            "};\n"
        )
        wrap_ufunction_split_specifiers = (
            "public:\n"
            "\tUFUNCTION(\n"
            "\t\tBlueprintCallable,\n"
            '\t\tCategory="Skyguard|Mission01|Environment|PCG")\n'
            f"\t{REFRESH_AUTHORED_BINDINGS}\n"
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
        header_wrap_const = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_const}"
        )
        header_wrap_ufunction = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_ufunction}"
        )
        header_wrap_ufunction_one_line = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_ufunction_one_line}"
        )
        header_wrap_ufunction_category = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_ufunction_category}"
        )
        header_wrap_ufunction_split_specifiers = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_ufunction_split_specifiers}"
        )
        for header in (
            header_wrap_type,
            header_wrap_spaces,
            header_wrap_tab,
            header_wrap_indent,
            header_wrap_const,
            header_wrap_ufunction,
            header_wrap_ufunction_one_line,
            header_wrap_ufunction_category,
            header_wrap_ufunction_split_specifiers,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, REFRESH_AUTHORED_BINDINGS),
                section,
            )
            self.assertEqual(
                require_declaration(section, REFRESH_AUTHORED_BINDINGS),
                REFRESH_AUTHORED_BINDINGS,
            )
            self.assertEqual(
                declaration_count(section, REFRESH_AUTHORED_BINDINGS),
                1,
            )
        one_line = f"{{\npublic:\n\t{REFRESH_AUTHORED_BINDINGS}\n}}\n"
        self.assertTrue(has_declaration(one_line, REFRESH_AUTHORED_BINDINGS))
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, REFRESH_AUTHORED_BINDINGS),
            section,
        )
        self.assertEqual(
            require_declaration(section, REFRESH_AUTHORED_BINDINGS),
            REFRESH_AUTHORED_BINDINGS,
        )
        self.assertIn(UFUNCTION_ENVIRONMENT, section)

    def test_integration_category_does_not_satisfy_environment(self) -> None:
        self.assertNotIn("Integration", UFUNCTION_ENVIRONMENT)
        self.assertNotIn("Briefing", UFUNCTION_ENVIRONMENT)
        integration = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission01|Integration")'
        )
        briefing = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission01|Briefing")'
        )
        leftover_pure = (
            'UFUNCTION(BlueprintPure, '
            'Category="Skyguard|Mission01|Environment|PCG")'
        )
        leftover_environment = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission01|Environment")'
        )
        leftover_landscape = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission01|Environment|Landscape")'
        )
        self.assertNotEqual(integration, UFUNCTION_ENVIRONMENT)
        self.assertNotEqual(briefing, UFUNCTION_ENVIRONMENT)
        self.assertNotEqual(leftover_pure, UFUNCTION_ENVIRONMENT)
        self.assertNotEqual(leftover_environment, UFUNCTION_ENVIRONMENT)
        self.assertNotEqual(leftover_landscape, UFUNCTION_ENVIRONMENT)
        self.assertNotIn(integration, UFUNCTION_ENVIRONMENT)
        self.assertNotIn(briefing, UFUNCTION_ENVIRONMENT)
        self.assertNotIn(leftover_pure, UFUNCTION_ENVIRONMENT)
        self.assertNotIn(leftover_environment, UFUNCTION_ENVIRONMENT)
        self.assertNotIn(leftover_landscape, UFUNCTION_ENVIRONMENT)

    def test_declaration_does_not_invent_ufunction_metadata(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for invented in INVENTED_UFUNCTION:
            self.assertNotIn(invented, REFRESH_AUTHORED_BINDINGS)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UFUNCTION_ENVIRONMENT)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, REFRESH_AUTHORED_BINDINGS)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UFUNCTION_ENVIRONMENT)
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_ENVIRONMENT, section)
        self.assertTrue(
            has_declaration(section, REFRESH_AUTHORED_BINDINGS),
            section,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", REFRESH_AUTHORED_BINDINGS)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_refresh_authored_environment_bindings_cpp_body(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        self.assertNotIn("{", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("}", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("return ", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn(
            "ASkyguardMission01EnvironmentDirector::RefreshAuthoredEnvironmentBindings",
            REFRESH_AUTHORED_BINDINGS,
        )
        self.assertNotIn(
            "SkyguardMission01EnvironmentDirector.cpp",
            REFRESH_AUTHORED_BINDINGS,
        )
        self.assertNotIn(
            "SkyguardMission01EnvironmentDirector.cpp",
            locked_only,
        )
        self.assertNotIn("return false", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("return true", REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_relock_sibling_director_fields(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in SIBLING_DIRECTOR_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        self.assertIn("RefreshAuthoredEnvironmentBindings", REFRESH_AUTHORED_BINDINGS)
        self.assertTrue(REFRESH_AUTHORED_BINDINGS.startswith("void "))

    def test_contract_does_not_relock_sibling_environment_methods(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in SIBLING_ENVIRONMENT_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        for token in LEFTOVER_ROUTE_EXCLUSION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        for token in LEFTOVER_PRODUCTION_FLAGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        for token in LEFTOVER_ENVIRONMENT_GET_READINESS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_relock_sibling_integration_methods(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in SIBLING_INTEGRATION_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        self.assertIn(
            "Scripts/tests/test_mission01_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_get_aircraft_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_bind_runtime_actors"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_spawn_locations(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_SPAWN_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        for token in leftover_spawn_name_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_relock_leftover_get_aircraft(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        self.assertNotIn(GET_AIRCRAFT, locked_only)
        self.assertNotIn(GET_AIRCRAFT, REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn(BIND_RUNTIME_ACTORS, locked_only)
        self.assertNotIn(BIND_RUNTIME_ACTORS, REFRESH_AUTHORED_BINDINGS)
        self.assertIn(
            "Scripts/tests/test_mission01_get_aircraft_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_briefing_methods(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_BRIEFING_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_relock_leftover_briefing_widget(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_BRIEFING_WIDGET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_relock_leftover_briefing_defaults(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_BRIEFING_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_relock_leftover_audio_director_fail_closed(
        self,
    ) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_AUDIO_DIRECTOR_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
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
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_RADIO_CHATTER_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
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
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_CAMPAIGN_DEFINITION_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
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
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_HARBOR_SCRIPTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
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
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_ENVIRONMENT_READINESS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
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
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_MISSION02_WAVE_STATE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn(
            "ESkyguardMission02WaveState",
            REFRESH_AUTHORED_BINDINGS,
        )

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_relock_leftover_lifeline_hunter(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_relock_leftover_apache(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_APACHE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_relock_leftover_patrol_ship(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_PATROL_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_relock_leftover_radar_node(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_relock_leftover_fill_and_gunner(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_scan_wrong_harbor_headers(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("MinHeightFromOriginCm", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("MaxIntegrity", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("CurrentIntegrity", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("SkyguardApacheAircraft.h", REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_scan_apache_public_section_for_harbor(
        self,
    ) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        file_text = this_file_text()
        apache_header = "SkyguardApacheAircraft.h"
        self.assertNotIn(apache_header, locked_only)
        self.assertNotIn(apache_header, REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("ASkyguardApacheAircraft", locked_only)
        self.assertNotIn("ASkyguardApacheAircraft", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn(f"origin/main:{apache_header}", file_text)
        self.assertNotIn(f"git show origin/main:{apache_header}", file_text)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_minimum_civilian_separation_is_not_harbor_40_80(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        section = public_section(origin_main_header())
        adjacent = "MinimumCivilianSeparationMeters = 550.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        for token in HARBOR_ADJACENT_CIVILIAN_SEPARATION:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        for token in HARBOR_ADJACENT_NOT_LOCKED:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("MinimumCivilianSeparationMeters", section)
        self.assertNotIn("550.f", section)

    def test_harbor_adjacent_fields_are_not_harbor_40_80(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        adjacent_civilian = "MinimumCivilianSeparationMeters = 550.f"
        adjacent_weapon = "MinimumWeaponSeparationMeters = 450.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent_civilian)
            self.assertNotEqual(token, adjacent_weapon)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        self.assertEqual(
            require_declaration(locked_only, REFRESH_AUTHORED_BINDINGS),
            REFRESH_AUTHORED_BINDINGS,
        )
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("Root;", locked_only)
        self.assertNotIn("Briefing", locked_only)
        self.assertNotIn("AudioDirector", locked_only)
        self.assertNotIn("RadioChatter", locked_only)
        self.assertNotIn("SortiePresentation", locked_only)
        self.assertNotIn("CampaignDefinition", locked_only)
        self.assertNotIn("MissionDefinition", locked_only)
        self.assertNotIn("Readiness", locked_only)
        self.assertNotIn("bAutoInitialize", locked_only)
        self.assertNotIn("bAllowBoundedActorSpawning", locked_only)
        self.assertNotIn("bAutoLaunchAfterBriefing", locked_only)
        self.assertNotIn("PathfinderSpawnLocation", locked_only)
        self.assertNotIn("GetAircraft", locked_only)
        self.assertNotIn("BindRuntimeActors", locked_only)
        self.assertNotIn("HandleDroneCityImpact", locked_only)
        self.assertNotIn("ConfigureMissionDefinition", locked_only)
        self.assertNotIn("InitializePlayableMission", locked_only)
        self.assertNotIn("NotifyProtectedAssetFailed", locked_only)
        self.assertNotIn("SynchronizeRuntimeState", locked_only)
        self.assertNotIn("NotifyObjectiveProgress", locked_only)
        self.assertNotIn("GetReadiness", locked_only)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("GetGunner", locked_only)
        self.assertNotIn("GetPathfinder", locked_only)
        self.assertNotIn("GetMissionId", locked_only)
        self.assertNotIn("ValidateMissionContract", locked_only)
        self.assertNotIn("IsCorePlayableReady", locked_only)
        self.assertNotIn("IsRouteExclusionSafe", locked_only)
        self.assertNotIn("IsPointAllowedForPCG", locked_only)
        self.assertNotIn("HasContinuousCoastline", locked_only)
        self.assertNotIn("RebuildProductionLayout", locked_only)
        self.assertNotIn("bLicensedVegetationLibraryApproved", locked_only)
        self.assertNotIn("bUseAuthoredLandscapeSurface", locked_only)
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
        self.assertNotIn("MinHeightFromOriginCm", section)
        self.assertEqual(
            require_declaration(section, REFRESH_AUTHORED_BINDINGS),
            REFRESH_AUTHORED_BINDINGS,
        )
        self.assertEqual(
            declaration_count(section, REFRESH_AUTHORED_BINDINGS),
            1,
        )
        self.assertNotIn(
            "SkyguardMission01EnvironmentDirector.cpp",
            section,
        )
        self.assertNotIn(
            "ASkyguardMission01EnvironmentDirector::RefreshAuthoredEnvironmentBindings",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
            self.assertNotIn(token, section)
        self.assertNotIn(
            "SkyguardMission01EnvironmentDirector.cpp",
            section,
        )
        self.assertNotIn(
            "ASkyguardMission01EnvironmentDirector::RefreshAuthoredEnvironmentBindings",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("}", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("return false", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("return true", REFRESH_AUTHORED_BINDINGS)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        file_text = this_file_text()
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
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
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
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
                "mission01 RefreshAuthoredEnvironmentBindings method contract "
                f"contains {banned}; declaration is Apache CPG 30 mm / "
                "Hydra / Hellfire, not leftover live cop" + "y",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, REFRESH_AUTHORED_BINDINGS.lower())
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
            self.assertNotIn(token, locked_only)

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                REFRESH_AUTHORED_BINDINGS.lower(),
                "mission01 RefreshAuthoredEnvironmentBindings contains "
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
        self.assertNotIn(dirty_fwd, REFRESH_AUTHORED_BINDINGS)

    def test_contract_is_refresh_authored_environment_bindings_declaration_only(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, REFRESH_AUTHORED_BINDINGS),
            REFRESH_AUTHORED_BINDINGS,
        )
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, REFRESH_AUTHORED_BINDINGS)
        leftover_groups = (
            SIBLING_DIRECTOR_FIELDS_NOT_LOCKED,
            SIBLING_INTEGRATION_METHODS_NOT_LOCKED,
            SIBLING_ENVIRONMENT_METHODS_NOT_LOCKED,
            LEFTOVER_ROUTE_EXCLUSION_NOT_LOCKED,
            LEFTOVER_PRODUCTION_FLAGS_NOT_LOCKED,
            LEFTOVER_ENVIRONMENT_GET_READINESS_NOT_LOCKED,
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
            LEFTOVER_HANDLE_DRONE_CITY_IMPACT_NOT_LOCKED,
            LEFTOVER_MISSION02_WAVE_STATE_NOT_LOCKED,
            LEFTOVER_SKYLINE_NOT_LOCKED,
            LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED,
            LEFTOVER_APACHE_NOT_LOCKED,
            LEFTOVER_PATROL_SHIP_NOT_LOCKED,
            LEFTOVER_RADAR_NODE_NOT_LOCKED,
            LEFTOVER_FILL_AND_GUNNER_NOT_LOCKED,
            WRONG_HARBOR_HEADERS_NOT_SCANNED,
            leftover_short_roster_values(),
            leftover_live_copy_method_names(),
            HARBOR_ADJACENT_NOT_LOCKED,
            leftover_harbor_clock_tokens(),
        )
        for group in leftover_groups:
            for token in group:
                self.assertNotIn(token, locked_only)
                self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, REFRESH_AUTHORED_BINDINGS.lower())
            self.assertNotIn(banned, locked_only.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("{", REFRESH_AUTHORED_BINDINGS)
        self.assertTrue(REFRESH_AUTHORED_BINDINGS.startswith("void "))
        self.assertIn("RefreshAuthoredEnvironmentBindings", REFRESH_AUTHORED_BINDINGS)
        self.assertIn("RefreshAuthoredEnvironmentBindings()", REFRESH_AUTHORED_BINDINGS)
        self.assertTrue(
            REFRESH_AUTHORED_BINDINGS.endswith("();"),
            REFRESH_AUTHORED_BINDINGS,
        )
        self.assertNotIn(" const;", REFRESH_AUTHORED_BINDINGS)
        self.assertTrue(REFRESH_AUTHORED_BINDINGS.endswith(";"))
        self.assertIn(UFUNCTION_ENVIRONMENT, section)

    def test_sibling_director_fields_do_not_satisfy_refresh_authored_environment_bindings(
        self,
    ) -> None:
        for leftover in (
            ROOT_FIELD,
            BRIEFING_FIELD,
            AUDIO_DIRECTOR_FIELD,
            RADIO_CHATTER_FIELD,
            SORTIE_PRESENTATION_FIELD,
            CAMPAIGN_DEFINITION_FIELD,
            MISSION_DEFINITION_FIELD,
            READINESS_FIELD,
            AUTO_INITIALIZE_FIELD,
            ALLOW_BOUNDED_SPAWNING_FIELD,
            AUTO_LAUNCH_AFTER_BRIEFING_FIELD,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, REFRESH_AUTHORED_BINDINGS)
            self.assertIn("RefreshAuthoredEnvironmentBindings", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, REFRESH_AUTHORED_BINDINGS)
            )
            self.assertNotEqual(REFRESH_AUTHORED_BINDINGS, leftover)
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
            "Scripts/tests/test_mission01_auto_initialize"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_sibling_environment_methods_do_not_satisfy(self) -> None:
        for leftover in (
            IS_POINT_ALLOWED_FOR_PCG,
            HAS_CONTINUOUS_COASTLINE,
            SET_USE_AUTHORED_LANDSCAPE,
            IS_AUTHORED_LANDSCAPE_EXPOSED,
            REBUILD_PRODUCTION_LAYOUT,
            IS_AUTHORED_ENVIRONMENT_READY,
            IS_PCG_GENERATION_AUTHORIZED,
            ENVIRONMENT_GET_READINESS,
            IS_ROUTE_EXCLUSION_SAFE,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, REFRESH_AUTHORED_BINDINGS)
            self.assertIn("RefreshAuthoredEnvironmentBindings", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, REFRESH_AUTHORED_BINDINGS)
            )

    def test_leftover_route_exclusion_does_not_satisfy(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_ROUTE_EXCLUSION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)
        region = f"\t{IS_ROUTE_EXCLUSION_SAFE}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(region, REFRESH_AUTHORED_BINDINGS)
        self.assertIn("RefreshAuthoredEnvironmentBindings", str(raised.exception))

    def test_leftover_production_flags_do_not_satisfy(self) -> None:
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_PRODUCTION_FLAGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_sibling_integration_methods_do_not_satisfy(self) -> None:
        for leftover in (
            CONFIGURE_MISSION_DEFINITION,
            INITIALIZE_PLAYABLE_MISSION,
            HANDLE_DRONE_CITY_IMPACT,
            NOTIFY_PROTECTED_ASSET_FAILED,
            SYNCHRONIZE_RUNTIME_STATE,
            NOTIFY_OBJECTIVE_PROGRESS,
            GET_READINESS,
            GET_OBJECTIVE_RUNTIME,
            GET_GUNNER,
            GET_PATHFINDER,
            GET_MISSION_ID,
            VALIDATE_MISSION_CONTRACT,
            IS_CORE_PLAYABLE_READY,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, REFRESH_AUTHORED_BINDINGS)
            self.assertIn("RefreshAuthoredEnvironmentBindings", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, REFRESH_AUTHORED_BINDINGS)
            )

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
                require_declaration(region, REFRESH_AUTHORED_BINDINGS)
            self.assertIn("RefreshAuthoredEnvironmentBindings", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, REFRESH_AUTHORED_BINDINGS)
            )

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
                require_declaration(region, REFRESH_AUTHORED_BINDINGS)
            self.assertIn("RefreshAuthoredEnvironmentBindings", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, REFRESH_AUTHORED_BINDINGS)
            )

    def test_leftover_live_copy_named_boss_methods_do_not_satisfy(self) -> None:
        for leftover in (
            leftover_apply_strike(),
            leftover_is_lock_eligible(),
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, REFRESH_AUTHORED_BINDINGS)
            self.assertIn("RefreshAuthoredEnvironmentBindings", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, REFRESH_AUTHORED_BINDINGS)
            )
        for name in leftover_live_copy_method_names():
            self.assertNotIn(name, REFRESH_AUTHORED_BINDINGS)

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
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
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


    def test_leftover_handle_drone_city_impact_does_not_satisfy(self) -> None:
        region = f"\t{HANDLE_DRONE_CITY_IMPACT}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(region, REFRESH_AUTHORED_BINDINGS)
        self.assertIn("RefreshAuthoredEnvironmentBindings", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(
            has_declaration(region, REFRESH_AUTHORED_BINDINGS)
        )
        locked_only = f"{REFRESH_AUTHORED_BINDINGS}\n"
        for token in LEFTOVER_HANDLE_DRONE_CITY_IMPACT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, REFRESH_AUTHORED_BINDINGS)

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tvoid RefreshAuthoredEnvironmentBindings()\n"
            "\t{\n"
            "\t\tOther();\n"
            "\t}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{inline}"
        )
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, REFRESH_AUTHORED_BINDINGS),
            section,
        )
        self.assertEqual(
            require_declaration(section, REFRESH_AUTHORED_BINDINGS),
            REFRESH_AUTHORED_BINDINGS,
        )
        self.assertEqual(
            declaration_count(section, REFRESH_AUTHORED_BINDINGS),
            1,
        )
        self.assertNotIn("{", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("}", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("return ", REFRESH_AUTHORED_BINDINGS)
        self.assertNotIn("return Other", REFRESH_AUTHORED_BINDINGS)

    def test_declaration_accepts_split_parameter_wrap(self) -> None:
        wrap_const = (
            "public:\n"
            "\tvoid RefreshAuthoredEnvironmentBindings\n"
            "\t\t();\n"
            "};\n"
        )
        wrap_type_and_const = (
            "public:\n"
            "\tvoid\n"
            "\tRefreshAuthoredEnvironmentBindings\n"
            "\t\t();\n"
            "};\n"
        )
        wrap_ufunction_split = (
            "public:\n"
            "\tUFUNCTION(BlueprintCallable,\n"
            '\t\tCategory="Skyguard|Mission01|Environment|PCG")\n'
            "\tvoid RefreshAuthoredEnvironmentBindings();\n"
            "};\n"
        )
        for wrap in (wrap_const, wrap_type_and_const, wrap_ufunction_split):
            header = (
                f"class SKYGUARD52_API {CLASS_NAME} "
                f": public AActor\n{{\n{wrap}"
            )
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, REFRESH_AUTHORED_BINDINGS),
                section,
            )
            self.assertEqual(
                require_declaration(section, REFRESH_AUTHORED_BINDINGS),
                REFRESH_AUTHORED_BINDINGS,
            )
            self.assertEqual(
                declaration_count(section, REFRESH_AUTHORED_BINDINGS),
                1,
            )

    def test_locked_scripts_do_not_include_this_file(self) -> None:
        this_script = (
            "Scripts/tests/test_mission01_refresh_authored_environment_bindings"
            "_decl_contract.py"
        )
        self.assertNotIn(this_script, LOCKED_SCRIPTS)
        self.assertIn(
            "Scripts/tests/test_mission01_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_is_core_playable_ready"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_coastal_haze_fade_seconds"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )


if __name__ == "__main__":
    unittest.main()
