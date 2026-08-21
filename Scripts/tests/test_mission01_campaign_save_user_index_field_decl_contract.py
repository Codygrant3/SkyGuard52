from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission01IntegrationDirector.h"
CLASS_NAME = "ASkyguardMission01IntegrationDirector"
# Field-declaration presence only. Do not invent
# INDEX_NONE or lock CampaignSaveUserIndex
# construction in the .cpp. This is a FIELD contract
# on ASkyguardMission01IntegrationDirector. Keep
# CampaignSaveUserIndex distinct from sibling
# director fields Briefing / AudioDirector / Root /
# RadioChatter / SortiePresentation /
# CampaignDefinition / MissionDefinition / Readiness /
# bAutoInitialize / bAllowBoundedActorSpawning /
# bAutoLaunchAfterBriefing / CampaignSaveSlotName. Do not
# lock leftover spawn-location fields on this class.
# Do not lock leftover GetAircraft. Do not lock
# leftover MissionBriefingComponent methods
# ConfigureFromMission / AdvanceBriefing /
# SetAssetsReady / AcknowledgeAndLaunch / CanLaunch /
# GetElapsedSeconds / GetBriefingState /
# GetMinimumWarmupSeconds / GetBriefingText /
# GetRadioChatter. Do not lock leftover
# briefing-widget GetPresentation / Configure /
# GetMissionTitle / GetBriefingText /
# AcknowledgeBriefing / LaunchSortie. Do not lock
# leftover USkyguardCampaignDefinition CampaignId /
# DisplayName / Missions / ValidateDefinition /
# GetPrimaryAssetId. Do not open
# SkyguardCampaignDefinition.h. Stay off leftover
# audio-director listener / telemetry / suppression /
# engine-state / bank-null / world-event fail-closed
# contracts. Stay off leftover radio-chatter
# empty-queue / empty-line fail-closed contracts.
# origin/main is a one-line field
# (`int32 CampaignSaveUserIndex = 0;`); accept
# that form and other one-line / split-line wraps.
# Nearby origin/main UPROPERTY is SPLIT-LINE:
# UPROPERTY(EditAnywhere, BlueprintReadWrite,
# Category="Skyguard|Mission01|Campaign",
# meta=(ClampMin="0")). Require ClampMin="0" as
# present nearby. Accept one-line and split-line
# UPROPERTY wraps. Parse the public class section
# of ASkyguardMission01IntegrationDirector only.
# Category is Skyguard|Mission01|Campaign, not
# Skyguard|Mission01 alone, not Mission02 / Boss /
# Destruction.
# Stay off leftover drafts #56–#64, leftover Harbor
# #6/#8/#9, leftover theater-kit #59, leftover
# isolated-test drafts #107–#582, leftover Apache
# MaxIntegrity / CurrentIntegrity, leftover Apache
# mount getters #851b / own-ship #96c5 / chin muzzle
# #4e39, leftover settings-apply-broadcast #1268,
# leftover patrol-ship empty fail-closed #5382,
# leftover RadarNode, leftover named boss methods,
# leftover LifelineHunter OpticalTracker / WeaponServo
# / CountermeasurePod / Engine fields, leftover
# briefing / debrief widget isolated contracts,
# leftover MissionBriefingComponent method decl
# contracts, leftover campaign-definition method
# decl contracts, leftover briefing-card /
# briefing-radio-row defaults, leftover briefing
# fail-closed tests, leftover environment-readiness
# defaults #6b9d / #b931, leftover skyline style
# HarborIndustrial (leftover enum, not a Harbor 40/80
# retune). Harbor interval retune tokens fail closed
# in this file and the locked declaration only. Do
# not scan Apache public section for those tokens.
# Incoming clock names may be scanned in the
# Mission01IntegrationDirector public section and
# must be absent. Pathfinder MinHeightFromOriginCm
# is the wrong header, not Harbor 40/80. LastFlight
# MinimumCivilianSeparationMeters = 550.f is
# Harbor-adjacent; do not treat as Harbor 40/80.
# LifelineHunter MinimumWeaponSeparationMeters =
# 450.f is Harbor-adjacent. Do not lock leftover
# ESkyguardMission02WaveState while leftover Harbor
# #6/#8/#9 remain open.
BRIEFING_FIELD = (
    "TObjectPtr<USkyguardMissionBriefingComponent> Briefing;"
)
UPROPERTY_CAMPAIGN = (
    "UPROPERTY(EditAnywhere, BlueprintReadWrite, "
    'Category="Skyguard|Mission01|Campaign",'
)
UPROPERTY_CAMPAIGN_META = 'meta=(ClampMin="0")'
CLAMP_MIN_ZERO = 'ClampMin="0"'
UPROPERTY_CAMPAIGN_SPLIT = (
    UPROPERTY_CAMPAIGN + "\n\t\t" + UPROPERTY_CAMPAIGN_META
)
UPROPERTY_CAMPAIGN_ONE_LINE = (
    UPROPERTY_CAMPAIGN + " " + UPROPERTY_CAMPAIGN_META
)
ROOT_FIELD = "TObjectPtr<USceneComponent> Root;"
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
CAMPAIGN_SAVE_USER_INDEX_FIELD = "int32 CampaignSaveUserIndex = 0;"
ALLOW_BOUNDED_ACTOR_SPAWNING_FIELD = (
    "bool bAllowBoundedActorSpawning = true;"
)
CAMPAIGN_SAVE_SLOT_NAME_FIELD = (
    'FString CampaignSaveSlotName = TEXT("Skyguard52Campaign");'
)
AUTO_INITIALIZE_FIELD = "bool bAutoInitialize = true;"
AUTO_LAUNCH_AFTER_BRIEFING_FIELD = (
    "bool bAutoLaunchAfterBriefing = true;"
)
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
# leftover theater-kit #59, leftover #107–#582, plus
# SkyguardMission01IntegrationDirector production
# files. This lane only adds an isolated Python
# CampaignSaveUserIndex field declaration
# contract on ASkyguardMission01IntegrationDirector.
LOCKED = {
    "SkyguardMission01IntegrationDirector.h",
    "SkyguardMission01IntegrationDirector.cpp",
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
# leftover Harbor #6/#8/#9, leftover theater-kit
# #59, leftover environment-readiness defaults
# #6b9d / #b931, leftover campaign-definition
# method decl contracts, leftover radio-chatter
# fail-closed contracts, sibling Briefing /
# AudioDirector / Root / RadioChatter /
# SortiePresentation / CampaignDefinition /
# MissionDefinition / Readiness / bAutoInitialize /
# bAllowBoundedActorSpawning / bAutoLaunchAfterBriefing /
# CampaignSaveSlotName field contracts stay sibling-only.
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
    "Scripts/tests/test_mission01_get_aircraft_decl_contract.py",
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
    "CampaignSaveSlotName",
    ROOT_FIELD,
    BRIEFING_FIELD,
    AUDIO_DIRECTOR_FIELD,
    RADIO_CHATTER_FIELD,
    SORTIE_PRESENTATION_FIELD,
    CAMPAIGN_DEFINITION_FIELD,
    MISSION_DEFINITION_FIELD,
    READINESS_FIELD,
    AUTO_INITIALIZE_FIELD,
    ALLOW_BOUNDED_ACTOR_SPAWNING_FIELD,
    AUTO_LAUNCH_AFTER_BRIEFING_FIELD,
    CAMPAIGN_SAVE_SLOT_NAME_FIELD,
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
CAMPAIGN_ID_FIELD = "FName CampaignId;"
DISPLAY_NAME_FIELD = "FText DisplayName;"
MISSIONS_FIELD = (
    "TArray<TSoftObjectPtr<USkyguardMissionDefinition>> Missions;"
)
VALIDATE_DEFINITION = (
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;"
)
GET_PRIMARY_ASSET_ID = "FPrimaryAssetId GetPrimaryAssetId() const override;"
LEFTOVER_CAMPAIGN_DEFINITION_METHODS_NOT_LOCKED = (
    CAMPAIGN_ID_FIELD,
    DISPLAY_NAME_FIELD,
    MISSIONS_FIELD,
    VALIDATE_DEFINITION,
    GET_PRIMARY_ASSET_ID,
    "CampaignId",
    "DisplayName",
    "ValidateDefinition",
    "GetPrimaryAssetId",
    "test_campaign_definition_campaign_id_decl_contract.py",
    "test_campaign_definition_display_name_decl_contract.py",
    "test_campaign_definition_missions_decl_contract.py",
    "test_validate_definition_decl_contract.py",
    "test_get_primary_asset_id_decl_contract.py",
    "SkyguardCampaignDefinition.h",
    "USkyguardCampaignDefinition::",
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
    "VisibleAnywhere",
    "BlueprintReadOnly",
    "VisibleDefaultsOnly",
    "EditDefaultsOnly",
    "SaveGame",
    "AllowPrivateAccess",
    'Category = "Campaign"',
    'Category = "Identity"',
)
INVENTED_FIELD_META = (
    "meta =",
    "ClampMax",
)
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "ASkyguardMission01IntegrationDirector::CampaignSaveUserIndex",
    "SkyguardMission01IntegrationDirector.cpp",
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
        "ASkyguardMission01IntegrationDirector();",
        ROOT_FIELD,
        BRIEFING_FIELD,
        AUDIO_DIRECTOR_FIELD,
        RADIO_CHATTER_FIELD,
        SORTIE_PRESENTATION_FIELD,
        CAMPAIGN_DEFINITION_FIELD,
        MISSION_DEFINITION_FIELD,
        AUTO_INITIALIZE_FIELD,
        ALLOW_BOUNDED_ACTOR_SPAWNING_FIELD,
        AUTO_LAUNCH_AFTER_BRIEFING_FIELD,
        CAMPAIGN_SAVE_SLOT_NAME_FIELD,
        CAMPAIGN_ID_FIELD,
        DISPLAY_NAME_FIELD,
        MISSIONS_FIELD,
        VALIDATE_DEFINITION,
        GET_PRIMARY_ASSET_ID,
        READINESS_FIELD,
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


class Mission01CampaignSaveUserIndexFieldDeclContractTests(unittest.TestCase):
    def test_mission01_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD), section)

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
            f"\t{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
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
            f"\t{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
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
            f"\t{ROOT_FIELD}\n"
            "private:\n"
            f"\t{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn("CampaignSaveUserIndex", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD))

    def test_missing_campaign_save_user_index_declaration_fails_closed(
        self,
    ) -> None:
        neighbors_only = (
            "\tASkyguardMission01IntegrationDirector();\n"
            f"\t{ROOT_FIELD}\n"
            f"\t{BRIEFING_FIELD}\n"
            f"\t{RADIO_CHATTER_FIELD}\n"
            f"\t{SORTIE_PRESENTATION_FIELD}\n"
            f"\t{AUDIO_DIRECTOR_FIELD}\n"
            f"\t{CAMPAIGN_DEFINITION_FIELD}\n"
            f"\t{MISSION_DEFINITION_FIELD}\n"
            f"\t{AUTO_INITIALIZE_FIELD}\n"
            f"\t{ALLOW_BOUNDED_ACTOR_SPAWNING_FIELD}\n"
            f"\t{AUTO_LAUNCH_AFTER_BRIEFING_FIELD}\n"
            f"\t{CAMPAIGN_SAVE_SLOT_NAME_FIELD}\n"
            f"\t{READINESS_FIELD}\n"
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
            require_declaration(neighbors_only, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn("CampaignSaveUserIndex", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        for macro_only in (
            f"\t{UPROPERTY_CAMPAIGN}\n",
            f"\t{UPROPERTY_CAMPAIGN_SPLIT}\n",
            f"\t{UPROPERTY_CAMPAIGN_ONE_LINE}\n",
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(macro_only, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertIn("CampaignSaveUserIndex", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_CAMPAIGN, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadWrite", section)
        self.assertIn('Category="Skyguard|Mission01|Campaign"', section)
        self.assertTrue(has_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD), section)
        self.assertNotIn("UPROPERTY", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("EditAnywhere", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("BlueprintReadWrite", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("Category", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("BlueprintPure", UPROPERTY_CAMPAIGN)
        self.assertNotIn("BlueprintCallable", UPROPERTY_CAMPAIGN)
        self.assertIn("Skyguard|Mission01|Campaign", UPROPERTY_CAMPAIGN)
        self.assertIn("|Campaign", UPROPERTY_CAMPAIGN)
        self.assertIn(CLAMP_MIN_ZERO, UPROPERTY_CAMPAIGN_META)
        self.assertIn(CLAMP_MIN_ZERO, UPROPERTY_CAMPAIGN_SPLIT)
        self.assertIn(CLAMP_MIN_ZERO, section)
        self.assertIn(UPROPERTY_CAMPAIGN_META, section)
        self.assertIn(UPROPERTY_CAMPAIGN_SPLIT, section)
        self.assertNotIn(CLAMP_MIN_ZERO, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn('Category="Skyguard|Mission01")', UPROPERTY_CAMPAIGN)
        self.assertNotIn("Mission02", UPROPERTY_CAMPAIGN)
        self.assertNotIn("Boss", UPROPERTY_CAMPAIGN)
        self.assertNotIn("Destruction", UPROPERTY_CAMPAIGN)
        self.assertNotIn("Mission07", UPROPERTY_CAMPAIGN)
        self.assertNotIn("Mission10", UPROPERTY_CAMPAIGN)
        self.assertNotIn("Encounter", UPROPERTY_CAMPAIGN)
        self.assertNotIn("Safety", UPROPERTY_CAMPAIGN)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_CAMPAIGN)
            self.assertNotIn(invented, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, UPROPERTY_CAMPAIGN)
            self.assertNotIn(invented, CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tASkyguardMission01IntegrationDirector();\n"
            f"\t{ROOT_FIELD}\n"
            f"\t{BRIEFING_FIELD}\n"
            f"\t{RADIO_CHATTER_FIELD}\n"
            f"\t{SORTIE_PRESENTATION_FIELD}\n"
            f"\t{AUDIO_DIRECTOR_FIELD}\n"
            f"\t{CAMPAIGN_DEFINITION_FIELD}\n"
            f"\t{MISSION_DEFINITION_FIELD}\n"
            f"\t{AUTO_INITIALIZE_FIELD}\n"
            f"\t{ALLOW_BOUNDED_ACTOR_SPAWNING_FIELD}\n"
            f"\t{AUTO_LAUNCH_AFTER_BRIEFING_FIELD}\n"
            f"\t{CAMPAIGN_SAVE_SLOT_NAME_FIELD}\n"
            f"\t{READINESS_FIELD}\n"
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
            require_declaration(other_helpers, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn("CampaignSaveUserIndex", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        unassigned = "\tint32 CampaignSaveUserIndex;\n"
        wrong_false = "\tint32 CampaignSaveUserIndex = 1;\n"
        as_int = "\tint32 CampaignSaveUserIndex = 1;\n"
        as_bool = "\tbool CampaignSaveUserIndex = 0;\n"
        as_uint8 = "\tuint8 CampaignSaveUserIndex = 0;\n"
        as_optional = "\tTOptional<int32> CampaignSaveUserIndex;\n"
        leftover_auto_init = f"\t{AUTO_INITIALIZE_FIELD}\n"
        leftover_allow_bounded = f"\t{ALLOW_BOUNDED_ACTOR_SPAWNING_FIELD}\n"
        leftover_auto_launch = f"\t{AUTO_LAUNCH_AFTER_BRIEFING_FIELD}\n"
        leftover_save_slot = f"\t{CAMPAIGN_SAVE_SLOT_NAME_FIELD}\n"
        leftover_root = f"\t{ROOT_FIELD}\n"
        leftover_briefing = f"\t{BRIEFING_FIELD}\n"
        leftover_radio = f"\t{RADIO_CHATTER_FIELD}\n"
        leftover_sortie = f"\t{SORTIE_PRESENTATION_FIELD}\n"
        leftover_campaign = f"\t{CAMPAIGN_DEFINITION_FIELD}\n"
        leftover_audio = f"\t{AUDIO_DIRECTOR_FIELD}\n"
        leftover_mission = f"\t{MISSION_DEFINITION_FIELD}\n"
        leftover_readiness = f"\t{READINESS_FIELD}\n"
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
            unassigned,
            wrong_false,
            as_int,
            as_bool,
            as_uint8,
            as_optional,
            leftover_auto_init,
            leftover_allow_bounded,
            leftover_auto_launch,
            leftover_save_slot,
            leftover_root,
            leftover_briefing,
            leftover_radio,
            leftover_sortie,
            leftover_campaign,
            leftover_audio,
            leftover_mission,
            leftover_readiness,
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
                require_declaration(region, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertIn("CampaignSaveUserIndex", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_campaign_save_user_index_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD),
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )
        self.assertTrue(has_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD))
        self.assertEqual(declaration_count(section, CAMPAIGN_SAVE_USER_INDEX_FIELD), 1)
        self.assertTrue(
            CAMPAIGN_SAVE_USER_INDEX_FIELD.startswith("int32 "),
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )
        self.assertTrue(CAMPAIGN_SAVE_USER_INDEX_FIELD.endswith(";"), CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn("CampaignSaveUserIndex", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn("= 0", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("bool ", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("TArray<", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("TObjectPtr", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("TSoftObjectPtr", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("false", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("INDEX_NONE", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("UFUNCTION", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("{", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("}", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("return ", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("Briefing", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("RadioChatter", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("SortiePresentation", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("AudioDirector", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("CampaignDefinition", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("MissionDefinition", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("Readiness", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("bAutoInitialize", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn(
            "bAllowBoundedActorSpawning",
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )
        self.assertNotIn(
            "bAutoLaunchAfterBriefing",
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )
        self.assertNotIn(
            "CampaignSaveSlotName",
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )
        self.assertNotIn("PathfinderSpawnLocation", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("GetAircraft", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("ConfigureFromMission", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("AdvanceBriefing", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("SetAssetsReady", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("AcknowledgeAndLaunch", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("CanLaunch", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("GetElapsedSeconds", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("GetBriefingState", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("GetMinimumWarmupSeconds", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("GetBriefingText", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("GetRadioChatter", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("GetPresentation", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("GetMissionTitle", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("AcknowledgeBriefing", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("LaunchSortie", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("HullCollider", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("OpticalTracker", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("WeaponServo", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("CountermeasurePod", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("MinHeightFromOriginCm", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("RadarNode", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("ESkyguardMission02WaveState", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("HarborIndustrial", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("MaxIntegrity", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("CurrentIntegrity", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        for name in leftover_live_copy_method_names():
            self.assertNotIn(name, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        for name in leftover_spawn_name_tokens():
            self.assertNotIn(name, CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tint32\n"
            "\tCampaignSaveUserIndex = 0;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tint32   CampaignSaveUserIndex = 0;\n"
            "private:\n"
            "};\n"
        )
        wrap_tab = (
            "public:\n"
            "\tint32\t"
            "CampaignSaveUserIndex = 0;\n"
            "};\n"
        )
        wrap_indent = (
            "public:\n"
            "\tint32\n"
            "\t\tCampaignSaveUserIndex = 0;\n"
            "};\n"
        )
        wrap_assign = (
            "public:\n"
            "\tint32 CampaignSaveUserIndex =\n"
            "\t0;\n"
            "};\n"
        )
        wrap_uproperty = (
            "public:\n"
            f"\t{UPROPERTY_CAMPAIGN}\n"
            f"\t{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_one_line = (
            "public:\n"
            f"\t{UPROPERTY_CAMPAIGN} {CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_category = (
            "public:\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadWrite,\n"
            '\t\tCategory="Skyguard|Mission01|Campaign",\n'
            '\t\tmeta=(ClampMin="0"))\n'
            f"\t{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_split_origin = (
            "public:\n"
            f"\t{UPROPERTY_CAMPAIGN_SPLIT}\n"
            f"\t{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_one_line_clamp = (
            "public:\n"
            f"\t{UPROPERTY_CAMPAIGN_ONE_LINE}\n"
            f"\t{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
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
        header_wrap_assign = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_assign}"
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
        header_wrap_uproperty_split_origin = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_uproperty_split_origin}"
        )
        header_wrap_uproperty_one_line_clamp = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_uproperty_one_line_clamp}"
        )
        for header in (
            header_wrap_type,
            header_wrap_spaces,
            header_wrap_tab,
            header_wrap_indent,
            header_wrap_assign,
            header_wrap_uproperty,
            header_wrap_uproperty_one_line,
            header_wrap_uproperty_category,
            header_wrap_uproperty_split_origin,
            header_wrap_uproperty_one_line_clamp,
        ):
            section = public_section(header)
            self.assertTrue(has_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD), section)
            self.assertEqual(
                require_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD),
                CAMPAIGN_SAVE_USER_INDEX_FIELD,
            )
            self.assertEqual(declaration_count(section, CAMPAIGN_SAVE_USER_INDEX_FIELD), 1)
        one_line = f"{{\npublic:\n\t{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n}}\n"
        self.assertTrue(has_declaration(one_line, CAMPAIGN_SAVE_USER_INDEX_FIELD))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD), section)
        self.assertEqual(
            require_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD),
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )
        self.assertIn(UPROPERTY_CAMPAIGN, section)
        self.assertIn(UPROPERTY_CAMPAIGN_META, section)
        self.assertIn(UPROPERTY_CAMPAIGN_SPLIT, section)
        self.assertIn(CLAMP_MIN_ZERO, section)

    def test_unassigned_campaign_save_user_index_does_not_satisfy(self) -> None:
        unassigned = "\tint32 CampaignSaveUserIndex;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(unassigned, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn("CampaignSaveUserIndex", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(unassigned, CAMPAIGN_SAVE_USER_INDEX_FIELD))

    def test_nonzero_campaign_save_user_index_does_not_satisfy(self) -> None:
        wrong_false = "\tint32 CampaignSaveUserIndex = 1;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(wrong_false, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn("CampaignSaveUserIndex", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(wrong_false, CAMPAIGN_SAVE_USER_INDEX_FIELD))

    def test_sibling_public_fields_do_not_satisfy(self) -> None:
        for region in (
            f"\t{ROOT_FIELD}\n",
            f"\t{BRIEFING_FIELD}\n",
            f"\t{RADIO_CHATTER_FIELD}\n",
            f"\t{SORTIE_PRESENTATION_FIELD}\n",
            f"\t{AUDIO_DIRECTOR_FIELD}\n",
            f"\t{CAMPAIGN_DEFINITION_FIELD}\n",
            f"\t{MISSION_DEFINITION_FIELD}\n",
            f"\t{AUTO_INITIALIZE_FIELD}\n",
            f"\t{ALLOW_BOUNDED_ACTOR_SPAWNING_FIELD}\n",
            f"\t{AUTO_LAUNCH_AFTER_BRIEFING_FIELD}\n",
            f"\t{CAMPAIGN_SAVE_SLOT_NAME_FIELD}\n",
            f"\t{READINESS_FIELD}\n",
            f"\t{PATHFINDER_SPAWN_LOCATION}\n",
            f"\t{PATHFINDER_SPAWN_ROTATION}\n",
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertIn("CampaignSaveUserIndex", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, CAMPAIGN_SAVE_USER_INDEX_FIELD))

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_CAMPAIGN)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_CAMPAIGN)
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_CAMPAIGN, section)
        self.assertIn(UPROPERTY_CAMPAIGN_META, section)
        self.assertIn(UPROPERTY_CAMPAIGN_SPLIT, section)
        self.assertIn(CLAMP_MIN_ZERO, section)
        self.assertNotIn(CLAMP_MIN_ZERO, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertTrue(has_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD), section)

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        self.assertNotIn("UFUNCTION", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(
            CAMPAIGN_SAVE_USER_INDEX_FIELD.startswith("UFUNCTION"),
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD), section)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_campaign_save_user_index_cpp_body(
        self,
    ) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        self.assertNotIn("{", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("}", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("return ", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn(
            "ASkyguardMission01IntegrationDirector::CampaignSaveUserIndex",
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )
        self.assertNotIn(
            "SkyguardMission01IntegrationDirector.cpp",
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )
        self.assertNotIn(
            "SkyguardMission01IntegrationDirector.cpp",
            locked_only,
        )
        self.assertNotIn("return false", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("return true", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("CreateDefaultSubobject", CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_relock_sibling_director_fields(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in SIBLING_DIRECTOR_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn("CampaignSaveUserIndex", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn("int32 ", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn("= 0", CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_relock_leftover_spawn_locations(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_SPAWN_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        for token in leftover_spawn_name_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_relock_leftover_get_aircraft(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        self.assertNotIn(GET_AIRCRAFT, locked_only)
        self.assertNotIn(GET_AIRCRAFT, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn(
            "Scripts/tests/test_mission01_get_aircraft_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_briefing_methods(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_BRIEFING_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_relock_leftover_briefing_widget(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_BRIEFING_WIDGET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_relock_leftover_briefing_defaults(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_BRIEFING_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_relock_leftover_audio_director_fail_closed(
        self,
    ) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_AUDIO_DIRECTOR_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
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
        self.assertNotIn("SkyguardCampaignDefinition.h", locked_only)
        self.assertNotIn("SetListenerPerspective", locked_only)
        self.assertNotIn("TriggerWorldEvent", locked_only)

    def test_contract_does_not_relock_leftover_harbor_scripts(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_HARBOR_SCRIPTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
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
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_ENVIRONMENT_READINESS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
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
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_MISSION02_WAVE_STATE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn(
            "ESkyguardMission02WaveState",
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_relock_leftover_lifeline_hunter(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_relock_leftover_apache(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_APACHE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_relock_leftover_patrol_ship(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_PATROL_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_relock_leftover_radar_node(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_scan_wrong_harbor_headers(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("MinHeightFromOriginCm", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("MaxIntegrity", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("CurrentIntegrity", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("SkyguardApacheAircraft.h", CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_open_leftover_campaign_definition_header(
        self,
    ) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        file_text = this_file_text()
        leftover_header = "SkyguardCampaignDefinition.h"
        self.assertNotIn(leftover_header, locked_only)
        self.assertNotIn(leftover_header, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn(f"origin/main:{leftover_header}", file_text)
        self.assertNotIn(
            f"git show origin/main:{leftover_header}",
            file_text,
        )
        self.assertNotIn(
            f"origin/main:Source/Skyguard52/{leftover_header}",
            file_text,
        )
        self.assertEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardMission01IntegrationDirector.h",
        )

    def test_contract_does_not_scan_apache_public_section_for_harbor(
        self,
    ) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        file_text = this_file_text()
        apache_header = "SkyguardApacheAircraft.h"
        self.assertNotIn(apache_header, locked_only)
        self.assertNotIn(apache_header, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("ASkyguardApacheAircraft", locked_only)
        self.assertNotIn("ASkyguardApacheAircraft", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn(f"origin/main:{apache_header}", file_text)
        self.assertNotIn(f"git show origin/main:{apache_header}", file_text)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_minimum_civilian_separation_is_not_harbor_40_80(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        section = public_section(origin_main_header())
        adjacent = "MinimumCivilianSeparationMeters = 550.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        for token in HARBOR_ADJACENT_CIVILIAN_SEPARATION:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        for token in HARBOR_ADJACENT_NOT_LOCKED:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("MinimumCivilianSeparationMeters", section)
        self.assertNotIn("550.f", section)

    def test_harbor_adjacent_fields_are_not_harbor_40_80(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        adjacent_civilian = "MinimumCivilianSeparationMeters = 550.f"
        adjacent_weapon = "MinimumWeaponSeparationMeters = 450.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent_civilian)
            self.assertNotEqual(token, adjacent_weapon)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        self.assertEqual(
            require_declaration(locked_only, CAMPAIGN_SAVE_USER_INDEX_FIELD),
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("Briefing", locked_only)
        self.assertNotIn("RadioChatter", locked_only)
        self.assertNotIn("SortiePresentation", locked_only)
        self.assertNotIn("AudioDirector", locked_only)
        self.assertNotIn("CampaignDefinition", locked_only)
        self.assertNotIn("MissionDefinition", locked_only)
        self.assertNotIn("Readiness", locked_only)
        self.assertNotIn("bAutoInitialize", locked_only)
        self.assertNotIn("bAllowBoundedActorSpawning", locked_only)
        self.assertNotIn("bAutoLaunchAfterBriefing", locked_only)
        self.assertNotIn("CampaignSaveSlotName", locked_only)
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
        self.assertNotIn("SkyguardCampaignDefinition.h", locked_only)
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
            require_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD),
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )
        self.assertEqual(declaration_count(section, CAMPAIGN_SAVE_USER_INDEX_FIELD), 1)
        self.assertNotIn(
            "SkyguardMission01IntegrationDirector.cpp",
            section,
        )
        self.assertNotIn(
            "ASkyguardMission01IntegrationDirector::CampaignSaveUserIndex",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn(
            "SkyguardMission01IntegrationDirector.cpp",
            section,
        )
        self.assertNotIn(
            "ASkyguardMission01IntegrationDirector::CampaignSaveUserIndex",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("}", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("return false", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("return true", CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        file_text = this_file_text()
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
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
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
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
                "mission01 CampaignSaveUserIndex field contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live cop" + "y",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, CAMPAIGN_SAVE_USER_INDEX_FIELD.lower())
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertNotIn(token, locked_only)

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                CAMPAIGN_SAVE_USER_INDEX_FIELD.lower(),
                "mission01 CampaignSaveUserIndex contains "
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
        self.assertNotIn(dirty_fwd, CAMPAIGN_SAVE_USER_INDEX_FIELD)

    def test_contract_is_campaign_save_user_index_field_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, CAMPAIGN_SAVE_USER_INDEX_FIELD),
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        leftover_groups = (
            SIBLING_DIRECTOR_FIELDS_NOT_LOCKED,
            LEFTOVER_BRIEFING_METHODS_NOT_LOCKED,
            LEFTOVER_BRIEFING_WIDGET_NOT_LOCKED,
            LEFTOVER_BRIEFING_DEFAULTS_NOT_LOCKED,
            LEFTOVER_AUDIO_DIRECTOR_FAIL_CLOSED_NOT_LOCKED,
            LEFTOVER_CAMPAIGN_DEFINITION_METHODS_NOT_LOCKED,
            LEFTOVER_RADIO_CHATTER_FAIL_CLOSED_NOT_LOCKED,
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
                self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, CAMPAIGN_SAVE_USER_INDEX_FIELD.lower())
            self.assertNotIn(banned, locked_only.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertNotIn("{", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertTrue(
            CAMPAIGN_SAVE_USER_INDEX_FIELD.startswith("int32 ")
        )
        self.assertIn(
            "CampaignSaveUserIndex",
            CAMPAIGN_SAVE_USER_INDEX_FIELD,
        )
        self.assertTrue(CAMPAIGN_SAVE_USER_INDEX_FIELD.endswith(";"))
        self.assertIn("= 0", CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn(UPROPERTY_CAMPAIGN, section)
        self.assertIn(UPROPERTY_CAMPAIGN_META, section)
        self.assertIn(UPROPERTY_CAMPAIGN_SPLIT, section)
        self.assertIn(CLAMP_MIN_ZERO, section)

    def test_sibling_director_fields_do_not_satisfy_campaign_save_user_index(
        self,
    ) -> None:
        for leftover in (
            ROOT_FIELD,
            BRIEFING_FIELD,
            RADIO_CHATTER_FIELD,
            SORTIE_PRESENTATION_FIELD,
            AUDIO_DIRECTOR_FIELD,
            CAMPAIGN_DEFINITION_FIELD,
            MISSION_DEFINITION_FIELD,
            AUTO_INITIALIZE_FIELD,
            ALLOW_BOUNDED_ACTOR_SPAWNING_FIELD,
            AUTO_LAUNCH_AFTER_BRIEFING_FIELD,
            CAMPAIGN_SAVE_SLOT_NAME_FIELD,
            READINESS_FIELD,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertIn("CampaignSaveUserIndex", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, CAMPAIGN_SAVE_USER_INDEX_FIELD))
            self.assertNotEqual(CAMPAIGN_SAVE_USER_INDEX_FIELD, leftover)
        self.assertIn(
            "Scripts/tests/test_mission01_root_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
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
        self.assertIn(
            "Scripts/tests/test_mission01_campaign_save_slot_name"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
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
                require_declaration(region, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertIn("CampaignSaveUserIndex", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, CAMPAIGN_SAVE_USER_INDEX_FIELD))

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
                require_declaration(region, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertIn("CampaignSaveUserIndex", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, CAMPAIGN_SAVE_USER_INDEX_FIELD))

    def test_leftover_live_copy_named_boss_methods_do_not_satisfy(self) -> None:
        for leftover in (
            leftover_apply_strike(),
            leftover_is_lock_eligible(),
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertIn("CampaignSaveUserIndex", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, CAMPAIGN_SAVE_USER_INDEX_FIELD))
        for name in leftover_live_copy_method_names():
            self.assertNotIn(name, CAMPAIGN_SAVE_USER_INDEX_FIELD)

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
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        self.assertNotIn("USkyguardBriefingWidget", locked_only)
        self.assertNotIn("GetPresentation", locked_only)
        self.assertNotIn("LaunchSortie", locked_only)

    def test_contract_does_not_relock_leftover_campaign_definition_methods(
        self,
    ) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_CAMPAIGN_DEFINITION_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn(
            "Scripts/tests/test_campaign_definition_campaign_id"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_campaign_definition_display_name"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_campaign_definition_missions"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_validate_definition_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("SkyguardCampaignDefinition.h", locked_only)
        self.assertNotIn("CampaignId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)

    def test_contract_does_not_relock_leftover_radio_chatter_fail_closed(
        self,
    ) -> None:
        locked_only = f"{CAMPAIGN_SAVE_USER_INDEX_FIELD}\n"
        for token in LEFTOVER_RADIO_CHATTER_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CAMPAIGN_SAVE_USER_INDEX_FIELD)
        self.assertIn(
            "Scripts/tests/test_radio_chatter_empty_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_radio_chatter_empty_queue_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_radio_chatter_empty_line_tests.py",
            LOCKED_SCRIPTS,
        )

    def test_leftover_campaign_definition_methods_do_not_satisfy(self) -> None:
        for leftover in (
            CAMPAIGN_ID_FIELD,
            DISPLAY_NAME_FIELD,
            MISSIONS_FIELD,
            VALIDATE_DEFINITION,
            GET_PRIMARY_ASSET_ID,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CAMPAIGN_SAVE_USER_INDEX_FIELD)
            self.assertIn("CampaignSaveUserIndex", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, CAMPAIGN_SAVE_USER_INDEX_FIELD))

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
