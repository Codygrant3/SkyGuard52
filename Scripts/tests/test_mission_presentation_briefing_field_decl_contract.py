# THIS IS leftover-safe FSkyguardMissionPresentation Briefing.
# origin/main form: one-line and split-line UPROPERTY wraps
# UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (MultiLine = "true"))
# then BARE `FText Briefing;` (no initializer).
# MultiLine = "true" IS present. Category is NOT present.
# EditAnywhere IS present. BlueprintReadOnly IS present.
# Fail-closed if the UPROPERTY or decl is missing
# or renamed, if EditAnywhere is dropped, if specifiers
# drop to BlueprintReadWrite, if type is not FText,
# if an initializer is added, if MultiLine is missing
# or wrong, or if Category= is added.
# Accept one-line and split-line UPROPERTY wraps.
# Parse STRUCT `FSkyguardMissionPresentation` body ONLY after
# `struct FSkyguardMissionPresentation`. Stop at
# `struct FSkyguardMissionScoreRules`.
# Do NOT parse leftover `FSkyguardBossDefinition`.
# Do NOT parse leftover `FSkyguardBossWeakPointDefinition`.
# Do NOT parse leftover `FSkyguardWeatherProfile`.
# Do NOT parse leftover `FSkyguardObjectiveDefinition`.
# Do NOT parse leftover `FSkyguardObjectiveProgress`.
# Do NOT parse leftover `FSkyguardRouteDefinition`.
# Do NOT parse leftover `USkyguardMissionDefinition`
# (leftover presentation field decls).
# Do NOT parse leftover briefing-card / briefing-radio-row /
# how-to-fly-row / briefing-widget / briefing-fail-closed /
# sortie-presentation-fail-closed.
# Do NOT contract sibling fields RadioChatter /
# SuccessDebrief / FailureDebrief /
# MinimumBriefingWarmupSeconds.
# THIS IS NOT leftover mission-presentation-defaults
# (keep that file in LOCKED_SCRIPTS; isolated Briefing
# field decl does not relock the defaults bulk).
# THIS IS NOT leftover USkyguardMissionDefinition
# presentation field decls.
# THIS IS NOT leftover merged bulk
# test_campaign_theater_kit_contract.py (keep that file
# in LOCKED_SCRIPTS; isolated field decl does not relock
# the bulk).
# THIS IS NOT leftover mission-types-defaults-tests.
# Analog: leftover mission-presentation-defaults then
# isolated Briefing field decl.
# If a clone asserts FName / VisibleAnywhere /
# Category="Skyguard|Theater" / WeatherIdentity, retarget:
# type is FText, EditAnywhere, no Category, MultiLine true,
# bare Briefing.
# Do NOT parse enum class ESkyguardAudioEvent.
# Do NOT parse FSkyguardAudioEventDefinition.
# Do NOT parse ESkyguardBriefingPictogram.
# Do NOT parse ESkyguardBossWeapon.
# Do NOT parse ASkyguardPropSpinner.
# Do NOT parse ASkyguardGunshipSortieDirector.
# Do NOT parse ASkyguardPatrolShipBoss.
# Do NOT parse leftover retired mount class (split tokens).
# Do NOT parse ASkyguardGunner.
# Do NOT parse USkyguardBossWeakPointComponent.
# Harbor 40/80 fail-closed.
# Ban retired live-copy tokens via split tokens
# (b + Ya + kRuntimeReady). Stay Apache CPG 30 mm / Hydra /
# Hellfire. Fail-closed on live Ig+la / Ri+fle / Ya+k
# appearing as contiguous tokens in THIS test file.

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMissionTypes.h"
STRUCT_NAME = "FSkyguardMissionPresentation"
TARGET = "FText Briefing;"
TARGET_WRONG_EQ_NONE = "FText Briefing = FText::GetEmpty();"
TARGET_WRONG_FALSE = "FText Briefing = false;"
TARGET_WRONG_TRUE = "FText Briefing = true;"
TARGET_WRONG_ZERO = "FText Briefing = 0.f;"
TARGET_WRONG_FLOAT = "float Briefing;"
TARGET_WRONG_FNAME = "FName Briefing;"
TARGET_WRONG_HEALTH = "float Health = 160.f;"
TARGET_WRONG_CATEGORY = (
    'UPROPERTY(EditAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Campaign")'
)
LOCKED_DECL = TARGET
UPROPERTY_EDIT_READONLY_MULTILINE = (
    'UPROPERTY(EditAnywhere, BlueprintReadOnly, '
    'meta = (MultiLine = "true"))'
)
STOP_BEFORE_SCORE_RULES = "struct FSkyguardMissionScoreRules"
STOP_BEFORE_BOSS_DEFINITION = "struct FSkyguardBossDefinition"
STOP_BEFORE_BOSS_WEAK_POINT = "struct FSkyguardBossWeakPointDefinition"
STOP_BEFORE_WEATHER_PROFILE = "struct FSkyguardWeatherProfile"
STOP_BEFORE_OBJECTIVE_DEFINITION = "struct FSkyguardObjectiveDefinition"
STOP_BEFORE_OBJECTIVE_PROGRESS = "struct FSkyguardObjectiveProgress"
STOP_BEFORE_ROUTE_DEFINITION = "struct FSkyguardRouteDefinition"
STOP_BEFORE_MISSION_DEFINITION = "USkyguardMissionDefinition"
STOP_BEFORE_AUDIO_EVENT = "enum class ESkyguardAudioEvent"
STOP_BEFORE_PICTOGRAM = "enum class ESkyguardBriefingPictogram"
STOP_BEFORE_EVENT_DEF = "struct FSkyguardAudioEventDefinition"
STOP_BEFORE_BOSS_WEAPON = "enum class ESkyguardBossWeapon"
STOP_BEFORE_PROP_SPINNER = "ASkyguardPropSpinner"
STOP_BEFORE_SORTIE = "ASkyguardGunshipSortieDirector"
STOP_BEFORE_PATROL = "ASkyguardPatrolShipBoss"
STOP_BEFORE_GUNNER = "ASkyguardGunner"
STOP_BEFORE_WEAK_POINT = "USkyguardBossWeakPointComponent"
GET_OBJECTIVE_RUNTIME = "GetObjectiveRuntime"
ADD_OBJECTIVE_PROGRESS = "AddObjectiveProgress"
BIND_RUNTIME_ACTORS = "BindRuntimeActors"
HANDLE_DRONE_CITY_IMPACT = "HandleDroneCityImpact"
GET_STORM_RAIN_BEAT_KIT = "GetStormRainBeatKit"
SIBLING_RADIO_CHATTER = "RadioChatter"
SIBLING_SUCCESS_DEBRIEF = "SuccessDebrief"
SIBLING_FAILURE_DEBRIEF = "FailureDebrief"
SIBLING_MIN_WARMUP = "MinimumBriefingWarmupSeconds"
LEFTOVER_APACHE_CLASS = "ASkyguardApacheAircraft"
LEFTOVER_PROTECT_ASSET_CLASS = "ASkyguardProtectAsset"
LEFTOVER_RADAR_NODE_CLASS = "ASkyguardRadarNode"
LEFTOVER_THEATER_KIT_ACTOR = "ASkyguardCampaignTheaterKit"
LEFTOVER_THEATER_KIT_NAMESPACE = "SkyguardCampaignTheaterKit"
THIS_SCRIPT = (
    "Scripts/tests/test_mission_presentation_briefing"
    "_field_decl_contract.py"
)
LEFTOVER_THEATER_KIT_WEATHER_IDENTITY = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
    "_field_decl_contract.py"
)
LEFTOVER_MISSION_PRESENTATION_DEFAULTS = (
    "Scripts/tests/test_mission_presentation_defaults_contract.py"
)
LEFTOVER_MISSION_PRESENTATION_DEFAULTS_PY = (
    "Scripts/tests/test_mission_presentation_defaults.py"
)
LEFTOVER_MISSION_PRESENTATION_DEFAULTS_TESTS = (
    "Scripts/tests/test_mission_presentation_defaults_tests.py"
)
LEFTOVER_MISSION_TYPES_DEFAULTS_TESTS = (
    "Scripts/tests/test_mission_types_defaults_tests.py"
)
LEFTOVER_MISSION_TYPES_DEFAULTS_PY = (
    "Scripts/tests/test_mission_types_defaults.py"
)
LEFTOVER_MISSION_TYPES_DEFAULTS_CONTRACT = (
    "Scripts/tests/test_mission_types_defaults_contract.py"
)
LEFTOVER_MISSION_DEFINITION_PRESENTATION = (
    "Scripts/tests/test_mission_definition_presentation"
    "_decl_contract.py"
)

CLONE_HEALTH = (
    "Scripts/tests/test_radar_node_health"
    "_field_decl_contract.py"
)
LEFTOVER_THEATER_KIT_BULK = (
    "Scripts/tests/test_campaign_theater_kit_contract.py"
)
LEFTOVER_MESH_BIND_SLOT = (
    "Scripts/tests/test_mesh_bind_slot_fields_contract.py"
)

CLONE_CURRENT_INTEGRITY = (
    "Scripts/tests/test_protect_asset_current_integrity"
    "_field_decl_contract.py"
)
CLONE_MAX_HEALTH = (
    "Scripts/tests/test_radar_node_max_health"
    "_field_decl_contract.py"
)
CLONE_RADAR_IS_DESTROYED = (
    "Scripts/tests/test_radar_node_is_destroyed"
    "_decl_contract.py"
)
CLONE_RADAR_APPLY_DAMAGE = (
    "Scripts/tests/test_radar_node_apply_damage"
    "_decl_contract.py"
)
CLONE_RADAR_RESET_NODE = (
    "Scripts/tests/test_radar_node_reset_node"
    "_decl_contract.py"
)
CLONE_RESET_INTEGRITY = (
    "Scripts/tests/test_protect_asset_reset_integrity"
    "_decl_contract.py"
)
CLONE_PEAK_ACTIVE_VOICES = (
    "Scripts/tests/test_audio_telemetry_peak_active_voices"
    "_field_decl_contract.py"
)

LEFTOVER_PROTECT_ASSET_CARGO_PROXY = (
    "Scripts/tests/test_protect_asset_cargo_proxy.py"
)
LEFTOVER_PROTECT_ASSET_CARGO_PROXY_CONTRACT = (
    "Scripts/tests/test_protect_asset_cargo_proxy_contract.py"
)
LEFTOVER_PROTECT_ASSET_CARGO_PROXY_TESTS = (
    "Scripts/tests/test_protect_asset_cargo_proxy_tests.py"
)
LEFTOVER_RADAR_NODE_PRESENTATION = (
    "Scripts/tests/test_radar_node_presentation.py"
)
LEFTOVER_RADAR_NODE_PRESENTATION_TESTS = (
    "Scripts/tests/test_radar_node_presentation_tests.py"
)
LEFTOVER_RADAR_NODE_PRESENTATION_CONTRACT = (
    "Scripts/tests/test_radar_node_presentation_contract.py"
)
LEFTOVER_RADAR_NODE_RESET_GAMEPLAY = (
    "Scripts/tests/test_radar_node_reset_gameplay.py"
)
LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_TESTS = (
    "Scripts/tests/test_radar_node_reset_gameplay_tests.py"
)
LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_CONTRACT = (
    "Scripts/tests/test_radar_node_reset_gameplay_contract.py"
)

CLONE_APPLY_DAMAGE = (
    "Scripts/tests/test_protect_asset_apply_damage"
    "_decl_contract.py"
)
CLONE_IS_DESTROYED = (
    "Scripts/tests/test_protect_asset_is_destroyed"
    "_decl_contract.py"
)
CLONE_GET_INTEGRITY_FRACTION = (
    "Scripts/tests/test_protect_asset_get_integrity_fraction"
    "_decl_contract.py"
)
CLONE_MAX_INTEGRITY = (
    "Scripts/tests/test_protect_asset_max_integrity"
    "_field_decl_contract.py"
)
CLONE_PLAYED_EVENTS = (
    "Scripts/tests/test_audio_telemetry_played_events"
    "_field_decl_contract.py"
)
CLONE_REQUESTED_EVENTS = (
    "Scripts/tests/test_audio_telemetry_requested_events"
    "_field_decl_contract.py"
)
CLONE_REJECTED_BY_COOLDOWN = (
    "Scripts/tests/test_audio_telemetry_rejected_by_cooldown"
    "_field_decl_contract.py"
)
CLONE_REJECTED_BY_CONCURRENCY = (
    "Scripts/tests/test_audio_telemetry_rejected_by_concurrency"
    "_field_decl_contract.py"
)
CLONE_REJECTED_MISSING_ASSET = (
    "Scripts/tests/test_audio_telemetry_rejected_missing_asset"
    "_field_decl_contract.py"
)
CLONE_PRIORITY_EVICTIONS = (
    "Scripts/tests/test_audio_telemetry_priority_evictions"
    "_field_decl_contract.py"
)
CLONE_WEAK_POINTS_DESTROYED = (
    "Scripts/tests/test_boss_telemetry_weak_points_destroyed"
    "_field_decl_contract.py"
)
CLONE_PILOT_COMMANDS_ISSUED = (
    "Scripts/tests/test_boss_telemetry_pilot_commands_issued"
    "_field_decl_contract.py"
)
CLONE_CAMPAIGN_COMPLETE = (
    "Scripts/tests/test_mission_debrief_campaign_complete"
    "_field_decl_contract.py"
)
CLONE_NEW_BEST_SCORE = (
    "Scripts/tests/test_mission_debrief_new_best_score"
    "_field_decl_contract.py"
)
CLONE_NEW_BEST_MEDAL = (
    "Scripts/tests/test_mission_debrief_new_best_medal"
    "_field_decl_contract.py"
)
CLONE_PROGRESS_SAVED = (
    "Scripts/tests/test_mission_debrief_progress_saved"
    "_field_decl_contract.py"
)
CLONE_SAVE_SLOT_NAME = (
    "Scripts/tests/test_mission_debrief_save_slot_name"
    "_field_decl_contract.py"
)
CLONE_NEXT_MISSION_ID = (
    "Scripts/tests/test_mission_debrief_next_mission_id"
    "_field_decl_contract.py"
)
CLONE_NEXT_MISSION_DISPLAY_NAME = (
    "Scripts/tests/test_mission_debrief_next_mission_display_name"
    "_field_decl_contract.py"
)
CLONE_NEXT_MISSION_MAP = (
    "Scripts/tests/test_mission_debrief_next_mission_map"
    "_field_decl_contract.py"
)
CLONE_NEXT_MISSION_UNLOCKED = (
    "Scripts/tests/test_mission_debrief_next_mission_unlocked"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_RESULT = (
    "Scripts/tests/test_mission_debrief_result"
    "_field_decl_contract.py"
)
CLONE_MISSION_DISPLAY_NAME = (
    "Scripts/tests/test_mission_debrief_mission_display_name"
    "_field_decl_contract.py"
)
CLONE_NARRATIVE = (
    "Scripts/tests/test_mission_debrief_narrative"
    "_field_decl_contract.py"
)
CLONE_OBJECTIVE_ID = (
    "Scripts/tests/test_objective_progress_objective_id"
    "_field_decl_contract.py"
)
CLONE_CURRENT_PROGRESS = (
    "Scripts/tests/test_objective_progress_current_progress"
    "_field_decl_contract.py"
)
CLONE_STATE = (
    "Scripts/tests/test_objective_progress_state"
    "_field_decl_contract.py"
)
CLONE_FINAL_SCORE = (
    "Scripts/tests/test_mission_result_final_score"
    "_field_decl_contract.py"
)
CLONE_MEDAL_TIER = (
    "Scripts/tests/test_mission_result_medal_tier"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_STATE = (
    "Scripts/tests/test_mission_debrief_state"
    "_field_decl_contract.py"
)
LEFTOVER_MISSION_RESULT_DEFAULTS = (
    "Scripts/tests/test_mission_result_defaults_contract.py"
)
LEFTOVER_MISSION_DEBRIEF_DEFAULTS = (
    "Scripts/tests/test_mission_debrief_defaults_contract.py"
)
LEFTOVER_OBJECTIVE_PROGRESS_DEFAULTS = (
    "Scripts/tests/test_objective_progress_defaults_contract.py"
)
LEFTOVER_ADD_OBJECTIVE_PROGRESS = (
    "Scripts/tests/test_add_objective_progress_decl_contract.py"
)
LEFTOVER_AUDIO_TELEMETRY_DEFAULTS = (
    "Scripts/tests/test_audio_telemetry_defaults_contract.py"
)
LEFTOVER_AUDIO_TELEMETRY_DEFAULTS_PY = (
    "Scripts/tests/test_audio_telemetry_defaults.py"
)
LEFTOVER_AUDIO_TELEMETRY_DEFAULTS_TESTS = (
    "Scripts/tests/test_audio_telemetry_defaults_tests.py"
)
LEFTOVER_AUDIO_DIRECTOR_TELEMETRY = (
    "Scripts/tests/test_audio_director_telemetry_fail_closed.py"
)
LEFTOVER_AUDIO_DIRECTOR_TELEMETRY_TESTS = (
    "Scripts/tests/test_audio_director_telemetry_fail_closed_tests.py"
)
LEFTOVER_AUDIO_DIRECTOR_TELEMETRY_CONTRACT = (
    "Scripts/tests/test_audio_director_telemetry_fail_closed_contract.py"
)
CLONE_HOW_TO_FLY_STEP_ID = (
    "Scripts/tests/test_how_to_fly_row_step_id_field_decl_contract.py"
)
CLONE_HOW_TO_FLY_INPUT_HINT = (
    "Scripts/tests/test_how_to_fly_row_input_hint_field_decl_contract.py"
)
CLONE_HOW_TO_FLY_INSTRUCTION = (
    "Scripts/tests/test_how_to_fly_row_instruction"
    "_field_decl_contract.py"
)
CLONE_CARD_ID = (
    "Scripts/tests/test_briefing_card_card_id_field_decl_contract.py"
)
CLONE_TITLE = (
    "Scripts/tests/test_briefing_card_title_field_decl_contract.py"
)
CLONE_BODY = (
    "Scripts/tests/test_briefing_card_body_field_decl_contract.py"
)
CLONE_PRIORITY = (
    "Scripts/tests/test_briefing_card_priority_field_decl_contract.py"
)
OTHER_TELEMETRY_FIELDS = (
    "RequestedEvents",
    "PlayedEvents",
    "RejectedByCooldown",
    "RejectedByConcurrency",
    "RejectedMissingAsset",
    "PriorityEvictions",
)

RESULT_NESTED_MEMBERS = (
    "FinalScore",
    "MedalTier",
    "MissionId",
    "bMissionSucceeded",
    "ShotsFired",
    "Hits",
    "AircraftDamageFraction",
    "CompletionTimeSeconds",
    "CompletedObjectiveIds",
)



LOCKED = {
    "SkyguardMission10IntegrationDirector.h",
    "SkyguardMission10IntegrationDirector.cpp",
    "SkyguardMission09IntegrationDirector.h",
    "SkyguardMission09IntegrationDirector.cpp",
    "SkyguardMission08IntegrationDirector.h",
    "SkyguardMission08IntegrationDirector.cpp",
    "SkyguardMission07IntegrationDirector.h",
    "SkyguardMission07IntegrationDirector.cpp",
    "SkyguardMission06IntegrationDirector.h",
    "SkyguardMission06IntegrationDirector.cpp",
    "SkyguardRadarNode.cpp",
    "SkyguardRadarNode.h",
    "SkyguardRadarNodeGameplayTests.cpp",
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
    "SkyguardProtectAssetTests.cpp",
    "SkyguardHarborProofTests.cpp",
    "SkyguardCampaignTheaterKitTests.cpp",
    "SkyguardMission01EnvironmentAuthoringLibrary.h",
    "SkyguardMissionBriefingComponent.h",
    "SkyguardSortiePresentationWidgets.h",
    "SkyguardCampaignSubsystem.h",
    "SkyguardCampaignSubsystem.cpp",
    "SkyguardMission01IntegrationDirector.h",
    "SkyguardMission01IntegrationDirector.cpp",
    "SkyguardMission02IntegrationDirector.h",
    "SkyguardMission02IntegrationDirector.cpp",
    "SkyguardMission03IntegrationDirector.h",
    "SkyguardMission03IntegrationDirector.cpp",
    "SkyguardMission04IntegrationDirector.h",
    "SkyguardMission04IntegrationDirector.cpp",
    "SkyguardMission05IntegrationDirector.h",
    "SkyguardMission05IntegrationDirector.cpp",
    "SkyguardMissionDirectorCampaignHelpers.h",
    "SkyguardMissionDirectorPresentationHelpers.h",
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



LOCKED_SCRIPTS = (
    "Scripts/tests/test_mission08_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission02_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission03_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission04_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission05_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission06_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission07_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission10_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission09_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission09_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission09_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_iron_rain_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_escalating_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_targets_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_budget_safe_field_decl_contract.py",
    "Scripts/tests/test_mission08_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission09_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission09_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission09_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission09_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission09_root_field_decl_contract.py",
    "Scripts/tests/test_mission09_skyline_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission09_major_bridge_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission09_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission09_power_station_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission09_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission09_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission09_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission09_readiness_field_decl_contract.py",
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
    "Scripts/tests/test_mission01_environment_readiness_ocean_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_beach_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_land_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_authored_landscape_surface_exposed_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_continuous_coastline_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_route_exclusion_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_landscape_component_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_production_landscape_bound_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_authored_pcg_graph_bound_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_pcg_bounds_tagged_field_decl_contract.py",
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
    "Scripts/tests/test_mission01_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission03_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission03_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission04_wave_state_enum_contract.py",
    "Scripts/tests/test_searchlight_track_runtime_defaults_contract.py",
    "Scripts/tests/test_search_track_runtime_defaults_contract.py",
    "Scripts/tests/test_mission04_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission04_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission03_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission04_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission04_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission04_start_searchlight_window_decl_contract.py",
    "Scripts/tests/test_mission04_advance_searchlight_track_decl_contract.py",
    "Scripts/tests/test_mission04_notify_substation_damage_decl_contract.py",
    "Scripts/tests/test_mission04_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission04_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission04_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission04_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission04_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission04_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission04_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission04_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission04_get_searchlight_runtime_decl_contract.py",
    "Scripts/tests/test_mission04_get_substation_integrity_decl_contract.py",
    "Scripts/tests/test_mission04_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission04_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission04_get_night_beat_kit_decl_contract.py",
    "Scripts/tests/test_mission01_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission02_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission02_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission02_get_aircraft_decl_contract.py",
    "Scripts/tests/test_mission02_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission03_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission03_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission03_get_aircraft_decl_contract.py",
    "Scripts/tests/test_mission03_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission03_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission03_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission03_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission03_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission03_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission03_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission03_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission01_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission01_notify_objective_progress_decl_contract.py",
    "Scripts/tests/test_mission01_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission01_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission01_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission01_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission01_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission01_get_gunner_decl_contract.py",
    "Scripts/tests/test_mission01_get_pathfinder_decl_contract.py",
    "Scripts/tests/test_mission01_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission01_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission01_bind_runtime_actors_decl_contract.py",
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
    "Scripts/tests/test_mission04_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission05_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission05_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission05_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission05_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission05_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission05_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission05_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission05_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission05_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission05_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission05_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission05_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission05_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission05_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission05_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission05_wave_state_enum_contract.py",
    "Scripts/tests/test_mission06_wave_state_enum_contract.py",
    "Scripts/tests/test_airfield_target_enum_contract.py",
    "Scripts/tests/test_airfield_target_runtime_defaults_contract.py",
    "Scripts/tests/test_payload_window_runtime_defaults_contract.py",
    "Scripts/tests/test_mission06_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission06_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission06_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission06_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission06_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission06_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission06_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission06_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission06_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission06_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission06_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission06_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission06_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission06_start_payload_window_decl_contract.py",
    "Scripts/tests/test_mission06_advance_payload_window_decl_contract.py",
    "Scripts/tests/test_mission06_try_jam_active_payload_decl_contract.py",
    "Scripts/tests/test_mission06_notify_airfield_target_damage_decl_contract.py",
    "Scripts/tests/test_mission06_get_payload_window_decl_contract.py",
    "Scripts/tests/test_mission06_get_target_runtime_decl_contract.py",
    "Scripts/tests/test_mission06_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission07_wave_state_enum_contract.py",
    "Scripts/tests/test_mission07_protected_target_enum_contract.py",
    "Scripts/tests/test_mission07_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_search_sector_enum_contract.py",
    "Scripts/tests/test_mission07_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission07_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission07_classify_false_track_decl_contract.py",
    "Scripts/tests/test_mission07_confirm_radar_ghost_identification_decl_contract.py",
    "Scripts/tests/test_mission07_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission07_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission07_notify_protected_target_damage_decl_contract.py",
    "Scripts/tests/test_mission07_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission07_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission07_advance_reinforcement_timer_decl_contract.py",
    "Scripts/tests/test_mission07_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission07_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission07_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission07_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission07_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission07_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission07_get_search_sector_decl_contract.py",
    "Scripts/tests/test_mission07_get_classified_false_track_count_decl_contract.py",
    "Scripts/tests/test_mission07_is_hostile_contact_confirmed_decl_contract.py",
    "Scripts/tests/test_mission07_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission07_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission07_get_reinforcement_time_remaining_decl_contract.py",
    "Scripts/tests/test_mission07_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission07_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission07_get_night_beat_kit_decl_contract.py",
    "Scripts/tests/test_mission07_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission08_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission08_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission08_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission08_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission08_start_hoist_window_decl_contract.py",
    "Scripts/tests/test_mission08_advance_hoist_window_decl_contract.py",
    "Scripts/tests/test_mission08_validate_weapon_release_decl_contract.py",
    "Scripts/tests/test_mission08_notify_protected_target_damage_decl_contract.py",
    "Scripts/tests/test_mission08_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission08_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission08_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission08_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission08_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission08_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission08_get_hoist_runtime_decl_contract.py",
    "Scripts/tests/test_mission08_get_rejected_weapon_releases_decl_contract.py",
    "Scripts/tests/test_mission08_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission08_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission08_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission08_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission08_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission08_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission08_wave_state_enum_contract.py",
    "Scripts/tests/test_mission08_protected_target_enum_contract.py",
    "Scripts/tests/test_mission08_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_hoist_window_runtime_defaults_contract.py",
    "Scripts/tests/test_mission08_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_route_matches_definition_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_required_objectives_anchored_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_landmarks_distinct_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_weather_matches_definition_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_defaults_contract.py",
    "Scripts/tests/test_mission_map_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission_map_validate_assembly_decl_contract.py",
    "Scripts/tests/test_mission_map_rebuild_route_spline_decl_contract.py",
    "Scripts/tests/test_mission_map_is_point_inside_flight_clearance_decl_contract.py",
    "Scripts/tests/test_mission05_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission06_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission09_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission09_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission09_bind_campaign_runtime_decl_contract.py",
    "Scripts/tests/test_mission09_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission09_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission09_notify_protected_target_damage_decl_contract.py",
    "Scripts/tests/test_mission09_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission09_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission09_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission09_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission09_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission09_get_pool_runtime_decl_contract.py",
    "Scripts/tests/test_mission09_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission05_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission09_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission09_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission09_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission09_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission09_wave_state_enum_contract.py",
    "Scripts/tests/test_mission09_protected_target_enum_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_defaults_contract.py",
    "Scripts/tests/test_mission09_pool_budget_defaults_contract.py",
    "Scripts/tests/test_mission09_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission10_route_phase_enum_contract.py",
    "Scripts/tests/test_mission10_protected_group_enum_contract.py",
    "Scripts/tests/test_mission10_protected_runtime_defaults_contract.py",
    "Scripts/tests/test_mission10_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission10_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission10_start_phase_wave_decl_contract.py",
    "Scripts/tests/test_mission10_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission10_validate_weapon_release_decl_contract.py",
    "Scripts/tests/test_mission10_notify_protected_group_damage_decl_contract.py",
    "Scripts/tests/test_mission10_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission10_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission10_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission10_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission10_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission10_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission10_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission10_get_route_phase_decl_contract.py",
    "Scripts/tests/test_mission10_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission10_get_surviving_protected_group_count_decl_contract.py",
    "Scripts/tests/test_mission10_get_rejected_weapon_releases_decl_contract.py",
    "Scripts/tests/test_mission10_get_protected_group_decl_contract.py",
    "Scripts/tests/test_mission10_root_field_decl_contract.py",
    "Scripts/tests/test_mission10_highway_convoy_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_bus_a_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_bus_b_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_ambulance_a_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_ambulance_b_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_ferry_terminal_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_evacuation_ship_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission10_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission10_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission10_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission10_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission10_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission10_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission10_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission10_last_flight_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission10_last_flight_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission10_minimum_weapon_separation_meters_field_decl_contract.py",
    "Scripts/tests/test_mission10_maximum_protected_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission10_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission10_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission02_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission03_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission04_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission05_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission07_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission08_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission09_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission02_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission02_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission02_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission02_get_breakwater_decl_contract.py",
    "Scripts/tests/test_mission02_get_fuel_terminal_integrity_decl_contract.py",
    "Scripts/tests/test_mission02_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission02_get_current_wave_index_decl_contract.py",
    "Scripts/tests/test_mission02_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission02_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission02_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission02_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission02_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission02_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission02_notify_fuel_terminal_damage_decl_contract.py",
    "Scripts/tests/test_mission02_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission02_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission02_root_field_decl_contract.py",
    "Scripts/tests/test_mission02_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission02_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission02_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission02_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission02_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission02_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission02_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission02_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission02_breakwater_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission02_breakwater_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission02_maximum_fuel_terminal_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission02_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission02_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_breakwater_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission02_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission02_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission02_radio_line_count_field_decl_contract.py",
    "Scripts/tests/test_mission03_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission03_maximum_convoy_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission03_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission03_root_field_decl_contract.py",
    "Scripts/tests/test_mission03_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission03_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission03_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission03_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission03_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission03_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission03_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission03_convoy_runtime_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission03_road_hunter_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_convoy_route_state_enum_contract.py",
    "Scripts/tests/test_mission03_wave_state_enum_contract.py",
    "Scripts/tests/test_radio_line_defaults_contract.py",
    "Scripts/tests/test_mission03_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission03_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_road_hunter_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_convoy_route_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission03_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission03_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission03_radio_line_count_field_decl_contract.py",
    "Scripts/tests/test_mission04_root_field_decl_contract.py",
    "Scripts/tests/test_mission04_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission04_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission04_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission04_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission04_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission04_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission04_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission04_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission04_searchlight_port_field_decl_contract.py",
    "Scripts/tests/test_mission04_searchlight_starboard_field_decl_contract.py",
    "Scripts/tests/test_mission04_black_kite_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission04_black_kite_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission04_required_track_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission04_missed_track_damage_field_decl_contract.py",
    "Scripts/tests/test_mission04_maximum_substation_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission04_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission05_root_field_decl_contract.py",
    "Scripts/tests/test_mission05_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission05_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission05_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission05_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission05_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission05_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission05_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission05_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission05_tempest_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission05_tempest_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission05_maximum_protected_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission05_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission05_wave_state_enum_contract.py",
    "Scripts/tests/test_mission05_protected_target_enum_contract.py",
    "Scripts/tests/test_mission05_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_mission06_root_field_decl_contract.py",
    "Scripts/tests/test_mission06_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission06_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission06_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission06_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission06_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission06_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission06_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission06_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission05_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission06_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission06_runway_breaker_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission06_runway_breaker_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission06_maximum_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission06_payload_impact_damage_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission06_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_runway_breaker_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission04_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission05_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission04_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission05_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission04_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission04_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission05_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_protected_targets_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission10_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission04_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission05_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission07_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission08_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission10_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission06_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission06_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission06_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission06_protected_target_count_field_decl_contract.py",
    "Scripts/tests/test_mission07_root_field_decl_contract.py",
    "Scripts/tests/test_mission07_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission07_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission07_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission07_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission07_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission07_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission07_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission07_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission07_radar_ghost_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission07_radar_ghost_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission07_maximum_protected_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission07_reinforcement_deadline_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission07_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission07_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission07_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_radar_ghost_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_protected_targets_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_search_runtime_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission07_search_track_count_field_decl_contract.py",
    "Scripts/tests/test_mission08_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission08_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_targets_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_target_count_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission01_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission04_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission05_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission10_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission08_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission08_maximum_protected_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission08_root_field_decl_contract.py",
    "Scripts/tests/test_mission08_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission08_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission08_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission08_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission08_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission08_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission08_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission08_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission08_rescue_helicopter_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_hoist_cable_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_survivors_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_rafts_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_rescue_vessel_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_lifeline_hunter_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission08_lifeline_hunter_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission08_required_covered_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission08_minimum_weapon_separation_meters_field_decl_contract.py",
    "Scripts/tests/test_mission08_rescue_animation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_lifeline_hunter_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_target_count_field_decl_contract.py",
    "Scripts/tests/test_mission09_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_budget_field_decl_contract.py",
    "Scripts/tests/test_mission09_maximum_protected_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission09_max_active_threats_field_decl_contract.py",
    "Scripts/tests/test_mission09_max_active_decoys_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_capacity_field_decl_contract.py",
    "Scripts/tests/test_mission09_max_active_threats_field_decl_contract.py",
    "Scripts/tests/test_mission09_max_active_decoys_field_decl_contract.py",
    "Scripts/tests/test_mission09_max_simultaneous_explosions_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_available_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_active_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_peak_active_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_recycled_field_decl_contract.py",
    "Scripts/tests/test_mission09_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_destroyed_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_target_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_target_runtime_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_target_runtime_destroyed_field_decl_contract.py",
    "Scripts/tests/test_mission07_search_track_runtime_track_id_field_decl_contract.py",
    "Scripts/tests/test_mission07_search_track_runtime_sector_field_decl_contract.py",
    "Scripts/tests/test_mission07_protected_target_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_mission07_protected_target_runtime_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission07_protected_target_runtime_destroyed_field_decl_contract.py",
    "Scripts/tests/test_mission06_airfield_target_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_mission06_airfield_target_runtime_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission06_airfield_target_runtime_destroyed_field_decl_contract.py",
    "Scripts/tests/test_mission06_payload_window_runtime_active_field_decl_contract.py",
    "Scripts/tests/test_mission06_payload_window_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_environment_readiness_bound_capability_count_field_decl_contract.py",
    "Scripts/tests/test_environment_readiness_tree_instance_count_field_decl_contract.py",
    "Scripts/tests/test_environment_readiness_shrub_instance_count_field_decl_contract.py",
    "Scripts/tests/test_environment_readiness_vfx_pool_size_field_decl_contract.py",
    "Scripts/tests/test_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_environment_quality_enum_contract.py",
    "Scripts/tests/test_coastal_env_director_empty_fail_closed.py",
    "Scripts/tests/test_coastal_environment_director_empty_fail_closed.py",
    "Scripts/tests/test_mission01_environment_readiness_ocean_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_beach_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_land_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_authored_landscape_surface_exposed_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_continuous_coastline_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_route_exclusion_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_landscape_component_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_production_landscape_bound_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_authored_pcg_graph_bound_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_pcg_bounds_tagged_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_mission01_is_authored_environment_ready_decl_contract.py",
    "Scripts/tests/test_mission01_sample_landscape_height_decl_contract.py",
    "Scripts/tests/test_mission01_sample_landscape_footprint_decl_contract.py",
    "Scripts/tests/test_mission01_rebuild_production_layout_decl_contract.py",
    "Scripts/tests/test_mission01_production_landscape_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_pcg_generation_authorized_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_valid_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_query_location_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_height_centimeters_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_heightfield_source_field_decl_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_landscape_capture_config_defaults_contract.py",
    "Scripts/tests/test_landscape_material_compilation_defaults_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_success_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_landscape_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_visible_audit_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_landscape_component_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_node_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_edge_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_node_setting_classes_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_landscape_guid_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_landscape_transform_exact_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_contract_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_authored_structure_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_authored_pcg_structure_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_defaults_contract.py",
    "Scripts/tests/test_landscape_visible_audit_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_actor_hidden_in_game_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_hidden_in_game_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_landscape_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_landscape_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_contract_camera_frustum_intersection_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_actor_hidden_in_game_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_actor_temporarily_hidden_in_editor_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_governed_material_parent_match_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_generated_material_instance_ready_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_hidden_in_game_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_visible_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_registered_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_render_state_created_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_capture_config_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_capture_config_defaults_contract.py",
    "Scripts/tests/test_landscape_visible_audit_bounds_finite_and_nonzero_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_bounds_minimum_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_bounds_maximum_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_error_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_asset_compilation_queue_empty_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_shader_compilation_queue_empty_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_generated_material_instance_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_capture_config_error_field_decl_contract.py",
    "Scripts/tests/test_landscape_capture_config_view_mode_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_licensed_mesh_slots_empty_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_error_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_generated_pcg_instance_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_route_and_beach_generated_instances_zero_field_decl_contract.py",
    "Scripts/tests/test_sortie_presentation_fail_closed.py",
    "Scripts/tests/test_sortie_presentation_fail_closed_tests.py",
    "Scripts/tests/test_sortie_presentation_fail_closed_contract.py",
    "Scripts/tests/test_briefing_card_priority_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_card_id_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_title_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_body_field_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_step_id_field_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_input_hint_field_decl_contract.py",
    "Scripts/tests/test_briefing_radio_row_line_id_field_decl_contract.py",
    "Scripts/tests/test_briefing_radio_row_speaker_field_decl_contract.py",
    "Scripts/tests/test_briefing_radio_row_subtitle_field_decl_contract.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
    "Scripts/tests/test_add_objective_progress_decl_contract.py",
    "Scripts/tests/test_objective_runtime_fail_closed.py",
    "Scripts/tests/test_objective_runtime_fail_closed_tests.py",
    "Scripts/tests/test_objective_runtime_fail_closed_contract.py",
    "Scripts/tests/test_objective_progress_objective_id_field_decl_contract.py",
    "Scripts/tests/test_objective_progress_current_progress_field_decl_contract.py",
    "Scripts/tests/test_objective_progress_state_field_decl_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_mission_result_final_score_field_decl_contract.py",
    "Scripts/tests/test_mission_result_medal_tier_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_state_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_result_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_mission_display_name_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_narrative_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_new_best_score_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_new_best_medal_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_progress_saved_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_next_mission_id_field_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_instruction_field_decl_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_error_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_error_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_error_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_generated_pcg_component_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_generation_locked_field_decl_contract.py",
    "Scripts/tests/test_mission_result_defaults_tests.py",
    "Scripts/tests/test_mission_result_defaults.py",
    "Scripts/tests/test_mission_debrief_defaults_tests.py",
    "Scripts/tests/test_mission_debrief_defaults.py",
    "Scripts/tests/test_mission_debrief_next_mission_display_name_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_next_mission_map_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_next_mission_unlocked_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_campaign_complete_field_decl_contract.py",
    "Scripts/tests/test_boss_telemetry_weak_points_destroyed_field_decl_contract.py",
    "Scripts/tests/test_boss_telemetry_pilot_commands_issued_field_decl_contract.py",
    "Scripts/tests/test_audio_telemetry_defaults_contract.py",
    "Scripts/tests/test_audio_telemetry_defaults.py",
    "Scripts/tests/test_audio_telemetry_defaults_tests.py",
    CLONE_PLAYED_EVENTS,
    CLONE_REQUESTED_EVENTS,
    CLONE_REJECTED_BY_COOLDOWN,
    CLONE_REJECTED_BY_CONCURRENCY,
    CLONE_REJECTED_MISSING_ASSET,
    CLONE_PRIORITY_EVICTIONS,
    CLONE_PEAK_ACTIVE_VOICES,
    LEFTOVER_PROTECT_ASSET_CARGO_PROXY,
    LEFTOVER_PROTECT_ASSET_CARGO_PROXY_CONTRACT,
    LEFTOVER_PROTECT_ASSET_CARGO_PROXY_TESTS,
    CLONE_APPLY_DAMAGE,
    CLONE_IS_DESTROYED,
    CLONE_GET_INTEGRITY_FRACTION,
    CLONE_MAX_INTEGRITY,
    CLONE_CURRENT_INTEGRITY,
    CLONE_MAX_HEALTH,
    CLONE_RADAR_IS_DESTROYED,
    CLONE_RADAR_APPLY_DAMAGE,
    CLONE_RADAR_RESET_NODE,
    CLONE_RESET_INTEGRITY,
    LEFTOVER_RADAR_NODE_PRESENTATION,
    LEFTOVER_RADAR_NODE_PRESENTATION_TESTS,
    LEFTOVER_RADAR_NODE_PRESENTATION_CONTRACT,
    LEFTOVER_RADAR_NODE_RESET_GAMEPLAY,
    LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_TESTS,
    LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_CONTRACT,
    "Scripts/tests/test_theater_kit_spec_weather_identity_field_decl_contract.py",
    "Scripts/tests/test_mission_presentation_defaults_contract.py",
    "Scripts/tests/test_mission_presentation_defaults.py",
    "Scripts/tests/test_mission_presentation_defaults_tests.py",
    "Scripts/tests/test_mission_types_defaults_tests.py",
    "Scripts/tests/test_mission_types_defaults.py",
    "Scripts/tests/test_mission_types_defaults_contract.py",
    "Scripts/tests/test_mission_definition_presentation_decl_contract.py",
    "Scripts/tests/test_mission_definition_mission_id_decl_contract.py",
    "Scripts/tests/test_mission_definition_display_name_decl_contract.py",
    "Scripts/tests/test_mission_definition_campaign_order_decl_contract.py",
    "Scripts/tests/test_mission_definition_mission_map_decl_contract.py",
    "Scripts/tests/test_mission_definition_route_decl_contract.py",
    "Scripts/tests/test_mission_definition_objectives_decl_contract.py",
    "Scripts/tests/test_mission_definition_waves_decl_contract.py",
    "Scripts/tests/test_mission_definition_weather_decl_contract.py",
    "Scripts/tests/test_mission_definition_boss_decl_contract.py",
    "Scripts/tests/test_mission_definition_score_rules_decl_contract.py",
    "Scripts/tests/test_mission_definition_prerequisite_ids_decl_contract.py",
    "Scripts/tests/test_mission_definition_required_medals_decl_contract.py",
    "Scripts/tests/test_mission_definition_get_primary_asset_id_decl_contract.py",
    "Scripts/tests/test_mission_definition_validate_definition_decl_contract.py",
    "Scripts/tests/test_mission_definition_find_objective_decl_contract.py",
) + leftover_live_copy_boss_scripts()




def leftover_retired_primary_hits_field() -> str:
    return "Ri" + "fleHits"


def leftover_retired_guided_hits_field() -> str:
    return "Ig" + "laHits"


def leftover_neighbor_hit_fields() -> tuple[str, ...]:
    return (
        leftover_retired_primary_hits_field(),
        leftover_retired_guided_hits_field(),
    )


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


def leftover_pictogram_values() -> tuple[str, ...]:
    return (
        "ESkyguardBriefingPictogram::" + "Ri" + "fle",
        "ESkyguardBriefingPictogram::" + "Ig" + "la",
    )


def leftover_live_case_tokens() -> tuple[str, ...]:
    return leftover_live_copy_title_tokens()


def leftover_live_copy_title_tokens() -> tuple[str, ...]:
    return ("Ig" + "la", "Ri" + "fle", "Ya" + "k")


def leftover_weapon_enum_body_tokens() -> tuple[str, ...]:
    return (
        "UMETA(DisplayName = \"" + "Ri" + "fle\")",
        "UMETA(DisplayName = \"" + "Ig" + "la\")",
    )


def leftover_audio_event_enum_tokens() -> tuple[str, ...]:
    return (
        "Ri" + "fleShot",
        "Ri" + "fleMechanical",
        "Ig" + "laSeekerSearch",
        "Ig" + "laLock",
        "Ig" + "laLaunch",
        "Ig" + "laImpact",
    )


STRUCT_RE = re.compile(
    rf"struct\s+(?:SKYGUARD52_API\s+)?{re.escape(STRUCT_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")
INVENTED_UPROPERTY = (
    "VisibleAnywhere",
    "BlueprintReadWrite",
    "BlueprintCallable",
    "BlueprintPure",
    "Transient",
    "BlueprintAuthorityOnly",
    "Category=",
    "Category =",
)
INVENTED_FIELD_META = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "CreateDefaultSubobject",
    "const float Amount",
    "{ return",
    "= true",
    "= false",
    "= 0.f",
    "= 160.f",
    "= NAME_None",
    "FText::GetEmpty()",
)


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_RADIO_CHATTER,
        SIBLING_SUCCESS_DEBRIEF,
        SIBLING_FAILURE_DEBRIEF,
        SIBLING_MIN_WARMUP,
    )


def leftover_neighbor_struct_tokens() -> tuple[str, ...]:
    return (
        STOP_BEFORE_SCORE_RULES,
        STOP_BEFORE_BOSS_DEFINITION,
        STOP_BEFORE_BOSS_WEAK_POINT,
        STOP_BEFORE_WEATHER_PROFILE,
        STOP_BEFORE_OBJECTIVE_DEFINITION,
        STOP_BEFORE_OBJECTIVE_PROGRESS,
        STOP_BEFORE_ROUTE_DEFINITION,
        STOP_BEFORE_MISSION_DEFINITION,
        "struct FSkyguardBriefingCard",
        "struct FSkyguardBriefingRadioRow",
        "struct FSkyguardHowToFlyRow",
        "class USkyguardBriefingWidget",
        "class USkyguardDebriefWidget",
        "class USkyguardSortiePresentationComponent",
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


def has_identifier(region: str, name: str) -> bool:
    return re.search(r"\b" + re.escape(name) + r"\b", region) is not None


def has_one_declaration(region: str, declaration: str) -> bool:
    if declaration in region:
        return True
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return True
    stem = declaration_stem(declaration)
    if not stem:
        return False
    pattern = re.compile(re.escape(stem) + r"\s*;")
    return pattern.search(compact_region) is not None


def has_declaration(region: str, declaration: str) -> bool:
    # Fail-closed on the authored bare `FText Briefing;`.
    # Do not accept `= FText::GetEmpty()` / `= false` /
    # `= true` / `= 0.f` / leftover float Health when
    # origin/main has a bare FText. Do not accept sibling
    # RadioChatter / SuccessDebrief / FailureDebrief /
    # MinimumBriefingWarmupSeconds fields.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if re.search(
        r"FText\s+Briefing\s*=",
        compact,
    ):
        return False
    if re.search(
        r"float\s+Briefing\b",
        compact,
    ):
        return False
    if re.search(
        r"FName\s+Briefing\b",
        compact,
    ):
        return False
    if re.search(
        r"int32\s+Briefing\b",
        compact,
    ):
        return False
    if re.search(
        r"bool\s+Briefing\b",
        compact,
    ):
        return False
    if re.search(
        r"FText\s+Briefing\s*;",
        compact,
    ) is None:
        return False
    return True


def count_one_declaration(region: str, declaration: str) -> int:
    if declaration in region:
        return region.count(declaration)
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return compact_region.count(compact_decl)
    stem = declaration_stem(declaration)
    if not stem:
        return 0
    pattern = re.compile(re.escape(stem) + r"\s*;")
    return len(pattern.findall(compact_region))


def declaration_count(region: str, declaration: str) -> int:
    if not has_declaration(region, declaration):
        return 0
    return count_one_declaration(region, declaration)


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


def struct_body(header: str) -> str:
    match = STRUCT_RE.search(header)
    if match is None:
        raise AssertionError(
            f"{STRUCT_NAME} is missing from origin/main:{HEADER_PATH}"
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
        f"{STRUCT_NAME} struct body is missing from origin/main:{HEADER_PATH}"
    )


def leaked_neighbor_tokens() -> tuple[str, ...]:
    return leftover_neighbor_struct_tokens() + (
        STOP_BEFORE_AUDIO_EVENT,
        STOP_BEFORE_PICTOGRAM,
        STOP_BEFORE_EVENT_DEF,
        STOP_BEFORE_BOSS_WEAPON,
        STOP_BEFORE_PROP_SPINNER,
        STOP_BEFORE_SORTIE,
        STOP_BEFORE_PATROL,
        leftover_retired_mount_class(),
        STOP_BEFORE_GUNNER,
        STOP_BEFORE_WEAK_POINT,
        GET_OBJECTIVE_RUNTIME,
        ADD_OBJECTIVE_PROGRESS,
        BIND_RUNTIME_ACTORS,
        HANDLE_DRONE_CITY_IMPACT,
        GET_STORM_RAIN_BEAT_KIT,
        "class USkyguardCampaignSubsystem",
        "class ASkyguardMission01IntegrationDirector",
        "class ASkyguardMission05IntegrationDirector",
        "class ASkyguardMission10IntegrationDirector",
        "struct FSkyguardLandscapeVisibleAudit",
        "struct FSkyguardLandscapeCaptureConfigurationResult",
        "struct FSkyguardLandscapeMaterialCompilationResult",
        "class USkyguardMission01EnvironmentAuthoringLibrary",
        "class ASkyguardMission01EnvironmentDirector",
        "struct FSkyguardMission01EnvironmentReadiness",
        "struct FSkyguardLandscapeFootprintSampleResult",
        "struct FSkyguardLandscapeHeightSample",
        "class ASkyguardPropSpinner",
        "enum class ESkyguardBriefingPictogram",
        "class USkyguardSortiePresentationComponent",
        "struct FSkyguardMissionResult",
        "struct FSkyguardMissionDebrief",
        "struct FSkyguardBossTelemetry",
        "struct FSkyguardAudioTelemetry",
        "ESkyguardAudioEvent::",
        f"class SKYGUARD52_API {LEFTOVER_APACHE_CLASS}",
        f"class {LEFTOVER_APACHE_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_RADAR_NODE_CLASS}",
        f"class {LEFTOVER_RADAR_NODE_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_THEATER_KIT_ACTOR}",
        f"class {LEFTOVER_THEATER_KIT_ACTOR}",
        f"namespace {LEFTOVER_THEATER_KIT_NAMESPACE}",
        "ApplyTheaterKitToWorld",
    )


def spec_section(header: str) -> str:
    body = struct_body(header)
    public = re.search(r"\bpublic\s*:", body)
    if public is None:
        if ACCESS_RE.search(body) is not None:
            raise AssertionError(
                f"{STRUCT_NAME} public section is missing from "
                f"origin/main:{HEADER_PATH}"
            )
        close = body.rfind("}")
        if close == -1:
            raise AssertionError(
                f"{STRUCT_NAME} public section is missing from "
                f"origin/main:{HEADER_PATH}"
            )
        section = body[1:close]
    else:
        start = public.end()
        rest = body[start:]
        next_access = ACCESS_RE.search(rest)
        if next_access is not None:
            section = rest[: next_access.start()]
        else:
            close = rest.rfind("}")
            if close == -1:
                raise AssertionError(
                    f"{STRUCT_NAME} public section is missing from "
                    f"origin/main:{HEADER_PATH}"
                )
            section = rest[:close]
    for token in leaked_neighbor_tokens():
        if token in section:
            raise AssertionError(
                f"{STRUCT_NAME} parse window includes {token}"
            )
    if STOP_BEFORE_SCORE_RULES in section:
        raise AssertionError(
            f"{STRUCT_NAME} parse window includes {STOP_BEFORE_SCORE_RULES}"
        )
    forty = "40" + ".f"
    eighty = "80" + ".f"
    for token in (forty, eighty):
        if token in section:
            raise AssertionError(
                f"{STRUCT_NAME} parse window includes harbor token {token}"
            )
    return section


def attached_uproperty_specifiers(section: str) -> str:
    compact = collapsed(section)
    cursor = 0
    while True:
        match = re.search(r"UPROPERTY\(", compact[cursor:])
        if match is None:
            break
        start = cursor + match.end()
        depth = 1
        index = start
        while index < len(compact) and depth:
            if compact[index] == "(":
                depth += 1
            elif compact[index] == ")":
                depth -= 1
            index += 1
        if depth == 0 and re.match(
            r"\s*FText\s+Briefing\b", compact[index:]
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for FText Briefing is missing from "
        f"origin/main:{HEADER_PATH} struct {STRUCT_NAME} body"
    )


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"struct {STRUCT_NAME} body"
        )
    return declaration


class MissionPresentationBriefingFieldDeclContractTests(unittest.TestCase):
    def test_mission_presentation_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(STRUCT_NAME, header)
        self.assertIsNotNone(STRUCT_RE.search(header), header)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertNotEqual(STRUCT_NAME, STOP_BEFORE_MISSION_DEFINITION)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_APACHE_CLASS)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_PROTECT_ASSET_CLASS)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_RADAR_NODE_CLASS)
        self.assertNotEqual(STRUCT_NAME, "FSkyguardTheaterKitSpec")
        body = struct_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = spec_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(has_identifier(section, "Briefing"), section)
        self.assertIn("UPROPERTY", section)
        self.assertIn(STOP_BEFORE_SCORE_RULES, header)
        self.assertNotIn(STOP_BEFORE_SCORE_RULES, section)
        self.assertNotIn(STOP_BEFORE_SCORE_RULES, body)
        self.assertIn(STOP_BEFORE_WEATHER_PROFILE, header)
        self.assertNotIn(STOP_BEFORE_WEATHER_PROFILE, section)
        self.assertNotIn(STOP_BEFORE_WEATHER_PROFILE, body)
        self.assertIn(STOP_BEFORE_BOSS_DEFINITION, header)
        self.assertNotIn(STOP_BEFORE_BOSS_DEFINITION, section)
        self.assertNotIn(STOP_BEFORE_BOSS_DEFINITION, body)
        self.assertNotIn(STOP_BEFORE_MISSION_DEFINITION, header)
        self.assertNotIn(STOP_BEFORE_MISSION_DEFINITION, section)
        self.assertNotIn(LEFTOVER_THEATER_KIT_ACTOR, header)
        self.assertNotIn(LEFTOVER_THEATER_KIT_NAMESPACE, header)
        self.assertNotIn("ApplyTheaterKitToWorld", header)
        self.assertNotIn("WeatherIdentity", section)
        self.assertNotIn("WeatherIdentity", body)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(GET_OBJECTIVE_RUNTIME, section)
        self.assertNotIn(ADD_OBJECTIVE_PROGRESS, section)
        self.assertNotIn(BIND_RUNTIME_ACTORS, section)
        self.assertNotIn(HANDLE_DRONE_CITY_IMPACT, section)
        self.assertNotIn(GET_STORM_RAIN_BEAT_KIT, section)
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, section)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, section)
        self.assertNotIn(STOP_BEFORE_EVENT_DEF, section)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAPON, section)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, section)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, section)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, section)

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            struct_body(
                "struct FSkyguardUnrelatedMissionPresentation\n{\n};\n"
            )
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_type_does_not_satisfy(self) -> None:
        other = (
            f"struct {LEFTOVER_APACHE_CLASS}\n"
            "{\n"
            f"\t{UPROPERTY_EDIT_READONLY_MULTILINE}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(other)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        leftover_def = (
            f"class {STOP_BEFORE_MISSION_DEFINITION}\n"
            "{\n"
            "public:\n"
            '\tUPROPERTY(EditAnywhere, BlueprintReadOnly, '
            'Category = "Presentation")\n'
            "\tFSkyguardMissionPresentation Presentation;\n"
            f"\t{UPROPERTY_EDIT_READONLY_MULTILINE}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(leftover_def)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        radar = (
            f"class {LEFTOVER_RADAR_NODE_CLASS}\n"
            "{\n"
            "public:\n"
            f"\t{UPROPERTY_EDIT_READONLY_MULTILINE}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(radar)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_score_rules_or_leftover_definition_does_not_satisfy(self) -> None:
        mixed = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "\tGENERATED_BODY()\n"
            "};\n"
            f"{STOP_BEFORE_SCORE_RULES}\n"
            "{\n"
            f"\t{UPROPERTY_EDIT_READONLY_MULTILINE}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
            f"class {STOP_BEFORE_MISSION_DEFINITION}\n"
            "{\n"
            "public:\n"
            '\tUPROPERTY(EditAnywhere, BlueprintReadOnly, '
            'Category = "Presentation")\n'
            "\tFSkyguardMissionPresentation Presentation;\n"
            "};\n"
        )
        section = spec_section(mixed)
        self.assertFalse(has_identifier(section, "Briefing"), section)
        self.assertNotIn(STOP_BEFORE_SCORE_RULES, section)
        self.assertNotIn(STOP_BEFORE_MISSION_DEFINITION, section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Briefing", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_briefing_declaration_fails_closed(self) -> None:
        empty = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\tTArray<FText> {SIBLING_RADIO_CHATTER};\n"
            "};\n"
        )
        section = spec_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Briefing", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_EDIT_READONLY_MULTILINE}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("Briefing", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = spec_section(origin_main_header())
        self.assertIn(UPROPERTY_EDIT_READONLY_MULTILINE, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('MultiLine = "true"', section)
        self.assertIn("EditAnywhere", UPROPERTY_EDIT_READONLY_MULTILINE)
        self.assertIn("BlueprintReadOnly", UPROPERTY_EDIT_READONLY_MULTILINE)
        self.assertIn("MultiLine", UPROPERTY_EDIT_READONLY_MULTILINE)
        self.assertIn(
            'meta = (MultiLine = "true")',
            UPROPERTY_EDIT_READONLY_MULTILINE,
        )
        self.assertNotIn("VisibleAnywhere", UPROPERTY_EDIT_READONLY_MULTILINE)
        self.assertNotIn("BlueprintReadWrite", UPROPERTY_EDIT_READONLY_MULTILINE)
        self.assertNotIn("Category", UPROPERTY_EDIT_READONLY_MULTILINE)
        specifiers = attached_uproperty_specifiers(section)
        self.assertIn("EditAnywhere", specifiers)
        self.assertIn("BlueprintReadOnly", specifiers)
        self.assertIn("MultiLine", specifiers)
        self.assertIn('MultiLine = "true"', specifiers)
        self.assertNotIn("VisibleAnywhere", specifiers)
        self.assertNotIn("BlueprintReadWrite", specifiers)
        self.assertNotIn("Category", specifiers)
        self.assertNotIn("ClampMin", specifiers)
        self.assertNotIn("ClampMax", specifiers)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertNotIn("UFUNCTION", LOCKED_DECL)
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, LOCKED_DECL)

    def test_initializer_fails_closed_when_origin_is_bare(self) -> None:
        initialized = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{UPROPERTY_EDIT_READONLY_MULTILINE}\n"
            f"\t{TARGET_WRONG_EQ_NONE}\n"
            "};\n"
        )
        section = spec_section(initialized)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Briefing", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        origin = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIn("FText Briefing;", compact_origin)
        self.assertNotIn("Briefing = FText::GetEmpty()", compact_origin)
        self.assertNotIn("Briefing = false", compact_origin)
        self.assertNotIn("Briefing = true", compact_origin)
        self.assertNotIn("Briefing = 0.f", compact_origin)
        self.assertNotIn("Briefing = 160.f", compact_origin)

    def test_briefing_declaration_matches_origin_main(self) -> None:
        section = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(
            LOCKED_DECL.startswith("FText Briefing"),
            LOCKED_DECL,
        )
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertNotIn("=", LOCKED_DECL)
        self.assertNotIn("= FText::GetEmpty()", LOCKED_DECL)
        self.assertNotIn("= false", LOCKED_DECL)
        self.assertNotIn("= true", LOCKED_DECL)
        self.assertNotIn("= 0.f", LOCKED_DECL)
        self.assertNotIn("= 160.f", LOCKED_DECL)
        self.assertIn("FText ", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("float ", LOCKED_DECL)
        self.assertNotIn("bool ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn("FSkyguardMissionResult", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FALSE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TRUE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_EQ_NONE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_ZERO}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FLOAT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FNAME}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_HEALTH}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_EQ_NONE}\n", LOCKED_DECL)
        self.assertIn("Briefing", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_FALSE}\n", LOCKED_DECL)
        self.assertIn("Briefing", str(raised.exception))

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tFText " + leftover_retired_primary_hits_field() + ";\n"
        )
        leftover_guided = (
            "\tFText " + leftover_retired_guided_hits_field() + ";\n"
        )
        forty = "40" + ".f"
        eighty = "80" + ".f"
        wrongs = (
            f"\t{TARGET_WRONG_EQ_NONE}\n",
            f"\t{TARGET_WRONG_FALSE}\n",
            f"\t{TARGET_WRONG_TRUE}\n",
            f"\t{TARGET_WRONG_ZERO}\n",
            f"\t{TARGET_WRONG_FLOAT}\n",
            f"\t{TARGET_WRONG_FNAME}\n",
            f"\t{TARGET_WRONG_HEALTH}\n",
            leftover_primary,
            leftover_guided,
            f"\tTArray<FText> {SIBLING_RADIO_CHATTER};\n",
            f"\tFText {SIBLING_SUCCESS_DEBRIEF};\n",
            f"\tFText {SIBLING_FAILURE_DEBRIEF};\n",
            f"\tfloat {SIBLING_MIN_WARMUP} = 3.f;\n",
            "\tFText Briefings;\n",
            "\tint32 Briefing;\n",
            "\tbool Briefing;\n",
            "\tfloat Briefing = " + forty + ";\n",
            "\tfloat Briefing = " + eighty + ";\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("Briefing", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_missing_edit_anywhere_or_multiline_fails_closed(self) -> None:
        no_multiline = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadOnly)\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        section = spec_section(no_multiline)
        specifiers = attached_uproperty_specifiers(section)
        self.assertNotIn("MultiLine", specifiers)
        origin = attached_uproperty_specifiers(
            spec_section(origin_main_header())
        )
        self.assertIn("MultiLine", origin)
        self.assertIn('MultiLine = "true"', origin)
        self.assertIn("EditAnywhere", origin)
        self.assertIn("BlueprintReadOnly", origin)
        self.assertNotIn("Category", origin)
        no_edit = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "\tUPROPERTY(BlueprintReadOnly, "
            'meta = (MultiLine = "true"))\n'
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        dropped = attached_uproperty_specifiers(
            spec_section(no_edit)
        )
        self.assertNotIn("EditAnywhere", dropped)
        self.assertIn("EditAnywhere", origin)
        write_only = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadWrite, "
            'meta = (MultiLine = "true"))\n'
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        write_specs = attached_uproperty_specifiers(
            spec_section(write_only)
        )
        self.assertIn("EditAnywhere", write_specs)
        self.assertIn("BlueprintReadWrite", write_specs)
        self.assertNotIn("BlueprintReadOnly", write_specs)
        self.assertIn("BlueprintReadOnly", origin)
        added_category = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_CATEGORY}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        category_specs = attached_uproperty_specifiers(
            spec_section(added_category)
        )
        self.assertIn("Category", category_specs)
        self.assertNotIn("Category", origin)
        visible = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
            'Category="Skyguard|Theater")\n'
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        visible_specs = attached_uproperty_specifiers(
            spec_section(visible)
        )
        self.assertIn("VisibleAnywhere", visible_specs)
        self.assertIn("Category", visible_specs)
        self.assertNotIn("VisibleAnywhere", origin)
        self.assertNotIn("Category", origin)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wraps = (
            "\tFText\n\tBriefing;\n",
            "\tFText   Briefing;\n",
            "\tFText\tBriefing;\n",
            f"\t{LOCKED_DECL}\n",
            f"\t{UPROPERTY_EDIT_READONLY_MULTILINE}\n\t{LOCKED_DECL}\n",
            f"\t{UPROPERTY_EDIT_READONLY_MULTILINE} {LOCKED_DECL}\n",
            "\tUPROPERTY(EditAnywhere, BlueprintReadOnly, "
            'meta = (MultiLine = "true"))\n'
            f"\t{LOCKED_DECL}\n",
            "\tUPROPERTY(\n\t\tEditAnywhere, BlueprintReadOnly, "
            'meta = (MultiLine = "true"))\n'
            f"\t{LOCKED_DECL}\n",
            "\tUPROPERTY(EditAnywhere, BlueprintReadOnly,\n"
            '\t\tmeta = (MultiLine = "true"))\n'
            f"\t{LOCKED_DECL}\n",
        )
        for region in wraps:
            self.assertTrue(has_declaration(region, LOCKED_DECL), region)

    def test_does_not_contract_sibling_presentation_fields(self) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertNotIn(GET_OBJECTIVE_RUNTIME, LOCKED_DECL)
        self.assertNotIn(ADD_OBJECTIVE_PROGRESS, LOCKED_DECL)
        self.assertNotIn(BIND_RUNTIME_ACTORS, LOCKED_DECL)
        self.assertNotIn(HANDLE_DRONE_CITY_IMPACT, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, LOCKED_DECL)
        self.assertNotIn(STOP_BEFORE_SCORE_RULES, LOCKED_DECL)
        section = spec_section(origin_main_header())
        for sibling in sibling_uncontracted_decls():
            self.assertTrue(has_identifier(section, sibling), sibling)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, section)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, LOCKED_DECL)

    def test_does_not_parse_leftover_neighbors(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = struct_body(header)
        self.assertIn(STOP_BEFORE_SCORE_RULES, header)
        self.assertNotIn(STOP_BEFORE_SCORE_RULES, section)
        self.assertNotIn(STOP_BEFORE_SCORE_RULES, leaked)
        self.assertIn(STOP_BEFORE_WEATHER_PROFILE, header)
        self.assertNotIn(STOP_BEFORE_WEATHER_PROFILE, section)
        self.assertNotIn(STOP_BEFORE_WEATHER_PROFILE, leaked)
        self.assertIn(STOP_BEFORE_BOSS_DEFINITION, header)
        self.assertNotIn(STOP_BEFORE_BOSS_DEFINITION, section)
        self.assertNotIn(STOP_BEFORE_BOSS_DEFINITION, leaked)
        self.assertIn(STOP_BEFORE_BOSS_WEAK_POINT, header)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAK_POINT, section)
        self.assertIn(STOP_BEFORE_OBJECTIVE_DEFINITION, header)
        self.assertNotIn(STOP_BEFORE_OBJECTIVE_DEFINITION, section)
        self.assertIn(STOP_BEFORE_ROUTE_DEFINITION, header)
        self.assertNotIn(STOP_BEFORE_ROUTE_DEFINITION, section)
        self.assertIn(STOP_BEFORE_OBJECTIVE_PROGRESS, header)
        self.assertNotIn(STOP_BEFORE_OBJECTIVE_PROGRESS, section)
        self.assertNotIn(STOP_BEFORE_OBJECTIVE_PROGRESS, leaked)
        self.assertNotIn(STOP_BEFORE_MISSION_DEFINITION, header)
        self.assertNotIn(STOP_BEFORE_MISSION_DEFINITION, section)
        self.assertNotIn(STOP_BEFORE_MISSION_DEFINITION, leaked)
        self.assertNotIn("struct FSkyguardBriefingCard", header)
        self.assertNotIn("struct FSkyguardBriefingRadioRow", header)
        self.assertNotIn("struct FSkyguardHowToFlyRow", header)
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, header)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, header)
        self.assertNotIn(STOP_BEFORE_EVENT_DEF, header)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAPON, header)
        self.assertNotIn(STOP_BEFORE_PROP_SPINNER, header)
        self.assertNotIn(STOP_BEFORE_SORTIE, header)
        self.assertNotIn(STOP_BEFORE_PATROL, header)
        self.assertNotIn(leftover_retired_mount_class(), header)
        self.assertNotIn(STOP_BEFORE_GUNNER, header)
        self.assertNotIn(STOP_BEFORE_WEAK_POINT, header)
        self.assertNotIn(GET_OBJECTIVE_RUNTIME, header)
        self.assertNotIn(ADD_OBJECTIVE_PROGRESS, header)
        self.assertNotIn(BIND_RUNTIME_ACTORS, header)
        self.assertNotIn(HANDLE_DRONE_CITY_IMPACT, header)
        self.assertNotIn(GET_STORM_RAIN_BEAT_KIT, header)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, header)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, header)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, header)
        self.assertNotIn(LEFTOVER_THEATER_KIT_ACTOR, header)
        self.assertNotIn("WeatherIdentity", header)
        self.assertNotIn("VisibleAnywhere", section)
        self.assertNotIn('Category="Skyguard|Theater"', section)

    def test_parse_window_excludes_leftover_weapon_enum_body(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = struct_body(header)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, leaked)
            self.assertNotIn(leftover, header)
        for leftover in leftover_weapon_enum_body_tokens():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, leaked)
            self.assertNotIn(leftover, header)
        for leftover in leftover_audio_event_enum_tokens():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, leaked)
            self.assertNotIn(leftover, header)
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, section)
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, leaked)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, section)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, leaked)
        self.assertNotIn(STOP_BEFORE_EVENT_DEF, section)
        self.assertNotIn(STOP_BEFORE_EVENT_DEF, leaked)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAPON, section)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAPON, leaked)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, section)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, leaked)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other = (
            "\tFSkyguardMissionPresentation Presentation;\n"
            f"\tTArray<FText> {SIBLING_RADIO_CHATTER};\n"
            f"\tFText {SIBLING_SUCCESS_DEBRIEF};\n"
            f"\tFText {SIBLING_FAILURE_DEBRIEF};\n"
            f"\tfloat {SIBLING_MIN_WARMUP} = 3.f;\n"
            f"\t{TARGET_WRONG_HEALTH}\n"
            "\tUSkyguardObjectiveRuntime* GetObjectiveRuntime() const;\n"
            "\tbool AddObjectiveProgress(\n"
            "\t\tFName ObjectiveId,\n"
            "\t\tint32 MedalTier);\n"
            "\tvoid BindRuntimeActors();\n"
            "\tvoid HandleDroneCityImpact();\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other, LOCKED_DECL)
        self.assertIn("Briefing", str(raised.exception))

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        self.assertEqual(
            UPROPERTY_EDIT_READONLY_MULTILINE,
            'UPROPERTY(EditAnywhere, BlueprintReadOnly, '
            'meta = (MultiLine = "true"))',
        )
        self.assertIn("EditAnywhere", UPROPERTY_EDIT_READONLY_MULTILINE)
        self.assertIn("BlueprintReadOnly", UPROPERTY_EDIT_READONLY_MULTILINE)
        self.assertIn("MultiLine", UPROPERTY_EDIT_READONLY_MULTILINE)
        self.assertIn(
            'meta = (MultiLine = "true")',
            UPROPERTY_EDIT_READONLY_MULTILINE,
        )
        self.assertNotIn("VisibleAnywhere", UPROPERTY_EDIT_READONLY_MULTILINE)
        self.assertNotIn("BlueprintReadWrite", UPROPERTY_EDIT_READONLY_MULTILINE)
        self.assertNotIn("Category", UPROPERTY_EDIT_READONLY_MULTILINE)
        self.assertNotIn('Category="Skyguard|Theater"', UPROPERTY_EDIT_READONLY_MULTILINE)
        self.assertNotIn("ClampMin", UPROPERTY_EDIT_READONLY_MULTILINE)
        self.assertNotIn("ClampMax", UPROPERTY_EDIT_READONLY_MULTILINE)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, LOCKED_DECL)
            self.assertNotIn(invented, UPROPERTY_EDIT_READONLY_MULTILINE)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        self.assertNotIn(".cpp", HEADER_PATH)
        self.assertTrue(HEADER_PATH.endswith(".h"))
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("SkyguardMissionTypes.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardMissionDefinition.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignTheaterKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardRadarNode.h", HEADER_PATH)
        self.assertNotIn("SkyguardProtectAsset.h", HEADER_PATH)
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = spec_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, LOCKED_DECL)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{LOCKED_DECL}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOCKED_DECL)
            self.assertNotIn(token, file_text)
        header = origin_main_header()
        section = spec_section(header)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, header)
        forty = "40" + ".f"
        eighty = "80" + ".f"
        self.assertNotIn(forty, section)
        self.assertNotIn(eighty, section)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "mission-presentation Briefing field decl contract "
                f"contains {banned}; declaration is Apache CPG 30 mm / "
                "Hydra / Hellfire, not leftover live cop" + "y",
            )

    def test_this_file_bans_live_retired_tokens_case_sensitive(self) -> None:
        file_text = this_file_text()
        for banned in leftover_live_case_tokens():
            self.assertNotIn(banned, file_text)

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        locked_only = f"{LOCKED_DECL}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, LOCKED_DECL.lower())
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, LOCKED_DECL)
            self.assertNotIn(token, locked_only)
        self.assertNotIn(leftover_retired_mount_class(), LOCKED_DECL)

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{LOCKED_DECL}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, LOCKED_DECL.lower())
            self.assertNotIn(banned, locked_only.lower())

    def test_locked_scripts_do_not_include_this_file(self) -> None:
        self.assertNotIn(THIS_SCRIPT, LOCKED_SCRIPTS)
        self.assertTrue(Path(__file__).name.endswith(
            "briefing_field_decl_contract.py"
        ))
        self.assertNotIn("SkyguardMissionTypes.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardMissionDefinition.h", THIS_SCRIPT)
        self.assertIn(LEFTOVER_THEATER_KIT_BULK, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_THEATER_KIT_WEATHER_IDENTITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_MISSION_PRESENTATION_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_MISSION_PRESENTATION_DEFAULTS_PY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_MISSION_PRESENTATION_DEFAULTS_TESTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_MISSION_TYPES_DEFAULTS_TESTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_MISSION_TYPES_DEFAULTS_PY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_MISSION_TYPES_DEFAULTS_CONTRACT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_MISSION_DEFINITION_PRESENTATION, LOCKED_SCRIPTS)
        self.assertIn(CLONE_CURRENT_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_MAX_HEALTH, LOCKED_SCRIPTS)
        self.assertIn(CLONE_RESET_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_APPLY_DAMAGE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_IS_DESTROYED, LOCKED_SCRIPTS)
        self.assertIn(CLONE_GET_INTEGRITY_FRACTION, LOCKED_SCRIPTS)
        self.assertIn(CLONE_MAX_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_RADAR_IS_DESTROYED, LOCKED_SCRIPTS)
        self.assertIn(CLONE_RADAR_APPLY_DAMAGE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_RADAR_RESET_NODE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_PEAK_ACTIVE_VOICES, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_PROTECT_ASSET_CARGO_PROXY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_PROTECT_ASSET_CARGO_PROXY_CONTRACT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_PROTECT_ASSET_CARGO_PROXY_TESTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_RADAR_NODE_PRESENTATION, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_RADAR_NODE_PRESENTATION_TESTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_RADAR_NODE_PRESENTATION_CONTRACT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_RADAR_NODE_RESET_GAMEPLAY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_TESTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_CONTRACT, LOCKED_SCRIPTS)
        self.assertIn(CLONE_OBJECTIVE_ID, LOCKED_SCRIPTS)
        self.assertIn(CLONE_CURRENT_PROGRESS, LOCKED_SCRIPTS)
        self.assertIn(CLONE_STATE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_FINAL_SCORE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_MEDAL_TIER, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_STATE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_RESULT, LOCKED_SCRIPTS)
        self.assertIn(CLONE_MISSION_DISPLAY_NAME, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NARRATIVE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NEW_BEST_SCORE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NEW_BEST_MEDAL, LOCKED_SCRIPTS)
        self.assertIn(CLONE_PROGRESS_SAVED, LOCKED_SCRIPTS)
        self.assertIn(CLONE_SAVE_SLOT_NAME, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NEXT_MISSION_ID, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NEXT_MISSION_DISPLAY_NAME, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NEXT_MISSION_MAP, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NEXT_MISSION_UNLOCKED, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_MISSION_RESULT_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_MISSION_DEBRIEF_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_OBJECTIVE_PROGRESS_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ADD_OBJECTIVE_PROGRESS, LOCKED_SCRIPTS)
        self.assertIn(CLONE_HOW_TO_FLY_STEP_ID, LOCKED_SCRIPTS)
        self.assertIn(CLONE_HOW_TO_FLY_INPUT_HINT, LOCKED_SCRIPTS)
        self.assertIn(CLONE_HOW_TO_FLY_INSTRUCTION, LOCKED_SCRIPTS)
        self.assertIn(CLONE_CARD_ID, LOCKED_SCRIPTS)
        self.assertIn(CLONE_TITLE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_BODY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_PRIORITY, LOCKED_SCRIPTS)
        self.assertIn(
            "Scripts/tests/test_mission_result_defaults.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission_result_defaults_tests.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission_debrief_defaults.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission_debrief_defaults_tests.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_briefing_card_defaults_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_campaign_theater_kit_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission_types_defaults_tests.py",
            LOCKED_SCRIPTS,
        )

    def test_leftover_mission_presentation_defaults_stay_locked(self) -> None:
        leftovers = (
            LEFTOVER_MISSION_PRESENTATION_DEFAULTS,
            LEFTOVER_MISSION_PRESENTATION_DEFAULTS_PY,
            LEFTOVER_MISSION_PRESENTATION_DEFAULTS_TESTS,
            LEFTOVER_MISSION_TYPES_DEFAULTS_TESTS,
            LEFTOVER_MISSION_TYPES_DEFAULTS_PY,
            LEFTOVER_MISSION_TYPES_DEFAULTS_CONTRACT,
            LEFTOVER_MISSION_DEFINITION_PRESENTATION,
            "Scripts/tests/test_mission_definition_mission_id_decl_contract.py",
            "Scripts/tests/test_mission_definition_display_name_decl_contract.py",
            "Scripts/tests/test_mission_definition_campaign_order_decl_contract.py",
            "Scripts/tests/test_mission_definition_mission_map_decl_contract.py",
            "Scripts/tests/test_mission_definition_route_decl_contract.py",
            "Scripts/tests/test_mission_definition_objectives_decl_contract.py",
            "Scripts/tests/test_mission_definition_waves_decl_contract.py",
            "Scripts/tests/test_mission_definition_weather_decl_contract.py",
            "Scripts/tests/test_mission_definition_boss_decl_contract.py",
            "Scripts/tests/test_mission_definition_score_rules_decl_contract.py",
            "Scripts/tests/test_mission_definition_prerequisite_ids_decl_contract.py",
            "Scripts/tests/test_mission_definition_required_medals_decl_contract.py",
            "Scripts/tests/test_mission_definition_get_primary_asset_id_decl_contract.py",
            "Scripts/tests/test_mission_definition_validate_definition_decl_contract.py",
            "Scripts/tests/test_mission_definition_find_objective_decl_contract.py",
            LEFTOVER_THEATER_KIT_WEATHER_IDENTITY,
            LEFTOVER_MISSION_RESULT_DEFAULTS,
            LEFTOVER_MISSION_DEBRIEF_DEFAULTS,
            LEFTOVER_OBJECTIVE_PROGRESS_DEFAULTS,
            LEFTOVER_ADD_OBJECTIVE_PROGRESS,
            CLONE_CAMPAIGN_COMPLETE,
            CLONE_WEAK_POINTS_DESTROYED,
            CLONE_PILOT_COMMANDS_ISSUED,
            CLONE_PLAYED_EVENTS,
            CLONE_REQUESTED_EVENTS,
            CLONE_REJECTED_BY_COOLDOWN,
            CLONE_REJECTED_BY_CONCURRENCY,
            CLONE_REJECTED_MISSING_ASSET,
            CLONE_PRIORITY_EVICTIONS,
            CLONE_PEAK_ACTIVE_VOICES,
            LEFTOVER_AUDIO_TELEMETRY_DEFAULTS,
            LEFTOVER_AUDIO_TELEMETRY_DEFAULTS_PY,
            LEFTOVER_AUDIO_TELEMETRY_DEFAULTS_TESTS,
            LEFTOVER_AUDIO_DIRECTOR_TELEMETRY,
            LEFTOVER_AUDIO_DIRECTOR_TELEMETRY_TESTS,
            LEFTOVER_AUDIO_DIRECTOR_TELEMETRY_CONTRACT,
            LEFTOVER_PROTECT_ASSET_CARGO_PROXY,
            LEFTOVER_PROTECT_ASSET_CARGO_PROXY_CONTRACT,
            LEFTOVER_PROTECT_ASSET_CARGO_PROXY_TESTS,
            CLONE_IS_DESTROYED,
            CLONE_GET_INTEGRITY_FRACTION,
            CLONE_APPLY_DAMAGE,
            CLONE_RESET_INTEGRITY,
            CLONE_MAX_INTEGRITY,
            CLONE_CURRENT_INTEGRITY,
            CLONE_MAX_HEALTH,
            CLONE_RADAR_IS_DESTROYED,
            CLONE_RADAR_APPLY_DAMAGE,
            CLONE_RADAR_RESET_NODE,
            LEFTOVER_RADAR_NODE_PRESENTATION,
            LEFTOVER_RADAR_NODE_PRESENTATION_TESTS,
            LEFTOVER_RADAR_NODE_PRESENTATION_CONTRACT,
            LEFTOVER_RADAR_NODE_RESET_GAMEPLAY,
            LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_TESTS,
            LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_CONTRACT,
            CLONE_OBJECTIVE_ID,
            CLONE_CURRENT_PROGRESS,
            CLONE_STATE,
            CLONE_FINAL_SCORE,
            CLONE_MEDAL_TIER,
            CLONE_DEBRIEF_STATE,
            CLONE_DEBRIEF_RESULT,
            CLONE_MISSION_DISPLAY_NAME,
            CLONE_NARRATIVE,
            CLONE_NEW_BEST_SCORE,
            CLONE_NEW_BEST_MEDAL,
            CLONE_PROGRESS_SAVED,
            CLONE_SAVE_SLOT_NAME,
            CLONE_NEXT_MISSION_ID,
            CLONE_NEXT_MISSION_DISPLAY_NAME,
            CLONE_NEXT_MISSION_MAP,
            CLONE_NEXT_MISSION_UNLOCKED,
            LEFTOVER_THEATER_KIT_BULK,
            "Scripts/tests/test_briefing_card_defaults_contract.py",
            "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
            "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
            "Scripts/tests/test_briefing_card_priority_field_decl_contract.py",
            "Scripts/tests/test_briefing_card_card_id_field_decl_contract.py",
            "Scripts/tests/test_briefing_card_title_field_decl_contract.py",
            "Scripts/tests/test_briefing_card_body_field_decl_contract.py",
            "Scripts/tests/test_how_to_fly_row_step_id_field_decl_contract.py",
            "Scripts/tests/test_how_to_fly_row_input_hint_field_decl_contract.py",
            "Scripts/tests/test_how_to_fly_row_instruction_field_decl_contract.py",
            "Scripts/tests/test_briefing_radio_row_line_id_field_decl_contract.py",
            "Scripts/tests/test_briefing_radio_row_speaker_field_decl_contract.py",
            "Scripts/tests/test_briefing_radio_row_subtitle_field_decl_contract.py",
            "Scripts/tests/test_briefing_fail_closed.py",
            "Scripts/tests/test_briefing_fail_closed_tests.py",
            "Scripts/tests/test_briefing_fail_closed_contract.py",
            "Scripts/tests/test_sortie_presentation_fail_closed.py",
            "Scripts/tests/test_sortie_presentation_fail_closed_tests.py",
            "Scripts/tests/test_sortie_presentation_fail_closed_contract.py",
        )
        for script in leftovers:
            self.assertIn(script, LOCKED_SCRIPTS)
            self.assertNotEqual(script, THIS_SCRIPT)

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

    def test_contract_is_target_field_declaration_only(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        locked_only = f"{LOCKED_DECL}\n"
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, locked_only)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, locked_only)
        self.assertNotIn(GET_OBJECTIVE_RUNTIME, locked_only)
        self.assertNotIn(ADD_OBJECTIVE_PROGRESS, locked_only)
        self.assertNotIn("FSkyguardObjectiveProgress", locked_only)
        self.assertNotIn("ESkyguardAudioEvent", locked_only)
        self.assertNotIn("ESkyguardBriefingPictogram", locked_only)
        self.assertNotIn("FSkyguardAudioEventDefinition", locked_only)
        self.assertNotIn("FSkyguardAudioTelemetry", locked_only)
        self.assertNotIn("ESkyguardBossWeapon", locked_only)
        self.assertNotIn("ESkyguardBossPhase", locked_only)
        self.assertNotIn("ESkyguardPilotCommand", locked_only)
        self.assertNotIn("PeakActiveVoices", locked_only)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, locked_only)
        self.assertNotIn(STOP_BEFORE_SCORE_RULES, locked_only)
        self.assertNotIn(STOP_BEFORE_MISSION_DEFINITION, locked_only)
        self.assertNotIn("WeatherIdentity", locked_only)
        self.assertNotIn("VisibleAnywhere", locked_only)


if __name__ == "__main__":
    unittest.main()
