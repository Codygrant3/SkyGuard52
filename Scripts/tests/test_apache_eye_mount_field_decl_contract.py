# THIS IS leftover-safe ASkyguardApacheAircraft EyeMount.
# origin/main form: one-line and split-line UPROPERTY wraps
# UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Apache")
# then BARE `TObjectPtr<USceneComponent> EyeMount;` (no initializer).
# Type is TObjectPtr<USceneComponent>, NOT UStaticMeshComponent.
# THIS IS leftover-safe isolated UPROPERTY with Category.
# Category IS `Skyguard|Apache`. VisibleAnywhere IS present.
# BlueprintReadOnly IS present. There is NO default.
# Fail-closed if the UPROPERTY or decl is missing
# or renamed, if Category is missing, or if specifiers
# drop to BlueprintReadWrite / EditAnywhere-only.
# Accept one-line and split-line UPROPERTY wraps.
# Parse ONLY class `ASkyguardApacheAircraft`.
# Start at `protected:` (or parse the class body but
# claim ONLY this UPROPERTY). Stop BEFORE `private:`.
# Stop BEFORE sibling WeaponMount as a claimed slot.
# Do not claim GunnerMount / PilotMount / WeaponMount /
# HellfireLeft / HellfireRight / SensorTurret /
# SensorBall / AircraftRoot / HullCollider / RotorPower.
# Do NOT parse leftover Apache UFUNCTION decls
# SetSensorView / GetRotorRPM / etc.
# Do NOT parse leftover analog
# apache-aircraft-empty-fail-closed (keep bulk in
# LOCKED_SCRIPTS).
# Do NOT parse leftover analog apache-hull-collider-field,
# leftover analog apache-mount-fail-closed, leftover
# analog apache-cpg-feel, leftover analog
# apache-own-ship-systems.
# Do NOT parse leftover ProtectAsset MaxIntegrity /
# CurrentIntegrity (different class).
# Do NOT parse leftover ArcadeLook UPROPERTY, leftover
# GuidedLockRules, leftover CampaignMissionSpec,
# leftover Harbor Breaker Approach/Contact/Shore,
# leftover ASkyguardGunshipSortieDirector, leftover
# analog campaign-roster-lookup-tests.
# Clone source leftover-safe TheaterKit WeatherIdentity
# wrap IS VisibleAnywhere BlueprintReadOnly — keep
# those specifiers — but RETARGET hard: Category is
# Skyguard|Apache NOT Skyguard|Theater. Better same-type
# retarget leftover-safe AircraftRoot
# `TObjectPtr<USceneComponent>`. LOCKED_DECL is
# `TObjectPtr<USceneComponent> EyeMount;` NOT
# `FName WeatherIdentity;` and NOT leftover
# `TObjectPtr<USceneComponent> AircraftRoot;`.
# Scene slots fail-closed if LOCKED_DECL is
# `TObjectPtr<UStaticMeshComponent>`.
# EyeMount fail-closed if LOCKED_DECL is leftover
# analog apache-mount-fail-closed, leftover
# SensorTurret, leftover SensorBall, leftover
# GunnerMount, leftover PilotMount, leftover
# WeaponMount, leftover AircraftRoot, leftover
# HellfireLeft, leftover HellfireRight.
# Fail-closed if this test still asserts
# FName WeatherIdentity / Category="Skyguard|Theater" /
# 160.f AS THE LOCKED DECL.
# Harbor fail-closed ONLY 40/80 split tokens.
# Ban retired live-copy tokens via split tokens
# (b + Ya + kRuntimeReady). Stay Apache CPG 30 mm /
# Hydra / Hellfire. Fail-closed on live Ig+la /
# Ri+fle / Ya+k appearing as contiguous tokens in
# THIS test file.

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardApacheAircraft.h"
CLASS_NAME = "ASkyguardApacheAircraft"
LOCKED_DECL = "TObjectPtr<USceneComponent> EyeMount;"
UPROPERTY_VISIBLE_READONLY = (
    "UPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
    'Category="Skyguard|Apache")'
)


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
    "Scripts/tests/test_add_objective_progress_decl_contract.py",
    "Scripts/tests/test_airfield_target_enum_contract.py",
    "Scripts/tests/test_airfield_target_runtime_defaults_contract.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_contract.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_tests.py",
    "Scripts/tests/test_apache_apply_damage_decl_contract.py",
    "Scripts/tests/test_apache_aircraft_root_field_decl_contract.py",
    "Scripts/tests/test_apache_gunner_mount_field_decl_contract.py",
    "Scripts/tests/test_apache_hellfire_left_field_decl_contract.py",
    "Scripts/tests/test_apache_hellfire_right_field_decl_contract.py",
    "Scripts/tests/test_apache_pilot_mount_field_decl_contract.py",
    "Scripts/tests/test_apache_sensor_ball_field_decl_contract.py",
    "Scripts/tests/test_apache_sensor_turret_field_decl_contract.py",
    "Scripts/tests/test_apache_silhouette_mesh_field_decl_contract.py",
    "Scripts/tests/test_apache_weapon_mount_field_decl_contract.py",
    "Scripts/tests/test_apache_chin_muzzle_contract.py",
    "Scripts/tests/test_apache_chin_muzzle_tests.py",
    "Scripts/tests/test_apache_cpg_feel_contract.py",
    "Scripts/tests/test_apache_current_integrity_field_decl_contract.py",
    "Scripts/tests/test_apache_get_damage_fraction_decl_contract.py",
    "Scripts/tests/test_apache_get_forward_speed_decl_contract.py",
    "Scripts/tests/test_apache_get_rotor_rpm_decl_contract.py",
    "Scripts/tests/test_apache_hull_collider_field_decl_contract.py",
    "Scripts/tests/test_apache_max_integrity_field_decl_contract.py",
    "Scripts/tests/test_apache_mount_fail_closed.py",
    "Scripts/tests/test_apache_mount_fail_closed_contract.py",
    "Scripts/tests/test_apache_mount_fail_closed_tests.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_tests.py",
    "Scripts/tests/test_apache_set_direct_flight_input_decl_contract.py",
    "Scripts/tests/test_apache_set_first_person_interior_decl_contract.py",
    "Scripts/tests/test_apache_set_sensor_view_decl_contract.py",
    "Scripts/tests/test_arcade_look_bloom_intensity_field_decl_contract.py",
    "Scripts/tests/test_arcade_look_contrast_field_decl_contract.py",
    "Scripts/tests/test_arcade_look_enabled_field_decl_contract.py",
    "Scripts/tests/test_arcade_look_fail_closed.py",
    "Scripts/tests/test_arcade_look_fail_closed_contract.py",
    "Scripts/tests/test_arcade_look_fail_closed_tests.py",
    "Scripts/tests/test_arcade_look_gain_field_decl_contract.py",
    "Scripts/tests/test_arcade_look_gamma_field_decl_contract.py",
    "Scripts/tests/test_arcade_look_grain_field_decl_contract.py",
    "Scripts/tests/test_arcade_look_saturation_field_decl_contract.py",
    "Scripts/tests/test_arcade_look_vignette_field_decl_contract.py",
    "Scripts/tests/test_arcade_look_world_mood_fail_closed.py",
    "Scripts/tests/test_arcade_look_world_mood_fail_closed_contract.py",
    "Scripts/tests/test_arcade_look_world_mood_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_bank_null_fail_closed.py",
    "Scripts/tests/test_audio_director_bank_null_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_bank_null_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_engine_state_fail_closed.py",
    "Scripts/tests/test_audio_director_engine_state_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_engine_state_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_listener_perspective_fail_closed.py",
    "Scripts/tests/test_audio_director_listener_perspective_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_listener_perspective_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_suppression_fail_closed.py",
    "Scripts/tests/test_audio_director_suppression_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_suppression_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_telemetry_fail_closed.py",
    "Scripts/tests/test_audio_director_telemetry_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_telemetry_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_world_event_fail_closed.py",
    "Scripts/tests/test_audio_director_world_event_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_world_event_fail_closed_tests.py",
    "Scripts/tests/test_audio_telemetry_defaults.py",
    "Scripts/tests/test_audio_telemetry_defaults_contract.py",
    "Scripts/tests/test_audio_telemetry_defaults_tests.py",
    "Scripts/tests/test_audio_telemetry_peak_active_voices_field_decl_contract.py",
    "Scripts/tests/test_audio_telemetry_played_events_field_decl_contract.py",
    "Scripts/tests/test_audio_telemetry_priority_evictions_field_decl_contract.py",
    "Scripts/tests/test_audio_telemetry_rejected_by_concurrency_field_decl_contract.py",
    "Scripts/tests/test_audio_telemetry_rejected_by_cooldown_field_decl_contract.py",
    "Scripts/tests/test_audio_telemetry_rejected_missing_asset_field_decl_contract.py",
    "Scripts/tests/test_audio_telemetry_requested_events_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_root_field_decl_contract.py",
    "Scripts/tests/test_boss_telemetry_pilot_commands_issued_field_decl_contract.py",
    "Scripts/tests/test_boss_telemetry_weak_points_destroyed_field_decl_contract.py",
    "Scripts/tests/test_briefing_acknowledge_and_launch_decl_contract.py",
    "Scripts/tests/test_briefing_advance_briefing_decl_contract.py",
    "Scripts/tests/test_briefing_can_launch_decl_contract.py",
    "Scripts/tests/test_briefing_card_body_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_card_id_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_briefing_card_priority_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_title_field_decl_contract.py",
    "Scripts/tests/test_briefing_configure_from_mission_decl_contract.py",
    "Scripts/tests/test_briefing_fail_closed.py",
    "Scripts/tests/test_briefing_fail_closed_contract.py",
    "Scripts/tests/test_briefing_fail_closed_tests.py",
    "Scripts/tests/test_briefing_get_briefing_state_decl_contract.py",
    "Scripts/tests/test_briefing_get_briefing_text_decl_contract.py",
    "Scripts/tests/test_briefing_get_elapsed_seconds_decl_contract.py",
    "Scripts/tests/test_briefing_get_minimum_warmup_seconds_decl_contract.py",
    "Scripts/tests/test_briefing_get_radio_chatter_decl_contract.py",
    "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
    "Scripts/tests/test_briefing_radio_row_line_id_field_decl_contract.py",
    "Scripts/tests/test_briefing_radio_row_speaker_field_decl_contract.py",
    "Scripts/tests/test_briefing_radio_row_subtitle_field_decl_contract.py",
    "Scripts/tests/test_briefing_set_assets_ready_decl_contract.py",
    "Scripts/tests/test_briefing_widget_acknowledge_briefing_decl_contract.py",
    "Scripts/tests/test_briefing_widget_configure_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_briefing_text_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_mission_title_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_presentation_decl_contract.py",
    "Scripts/tests/test_briefing_widget_launch_sortie_decl_contract.py",
    "Scripts/tests/test_campaign_definition_campaign_id_decl_contract.py",
    "Scripts/tests/test_campaign_definition_display_name_decl_contract.py",
    "Scripts/tests/test_campaign_definition_missions_decl_contract.py",
    "Scripts/tests/test_campaign_mission_spec_brief_field_decl_contract.py",
    "Scripts/tests/test_campaign_mission_spec_contact_kind_field_decl_contract.py",
    "Scripts/tests/test_campaign_mission_spec_shore_kind_field_decl_contract.py",
    "Scripts/tests/test_campaign_mission_spec_title_field_decl_contract.py",
    "Scripts/tests/test_campaign_mission_spec_weather_field_decl_contract.py",
    "Scripts/tests/test_campaign_roster_get_decl_contract.py",
    "Scripts/tests/test_campaign_roster_id_at_decl_contract.py",
    "Scripts/tests/test_campaign_roster_loadout_label_decl_contract.py",
    "Scripts/tests/test_campaign_roster_lookup.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
    "Scripts/tests/test_campaign_roster_weather_enum_label_decl_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_coastal_env_director_empty_fail_closed.py",
    "Scripts/tests/test_coastal_environment_director_empty_fail_closed.py",
    "Scripts/tests/test_convoy_route_state_enum_contract.py",
    "Scripts/tests/test_debrief_widget_configure_decl_contract.py",
    "Scripts/tests/test_debrief_widget_get_presentation_decl_contract.py",
    "Scripts/tests/test_environment_quality_enum_contract.py",
    "Scripts/tests/test_environment_readiness_bound_capability_count_field_decl_contract.py",
    "Scripts/tests/test_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_environment_readiness_shrub_instance_count_field_decl_contract.py",
    "Scripts/tests/test_environment_readiness_tree_instance_count_field_decl_contract.py",
    "Scripts/tests/test_environment_readiness_vfx_pool_size_field_decl_contract.py",
    "Scripts/tests/test_find_mission_decl_contract.py",
    "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
    "Scripts/tests/test_guided_lock_rules_helmet_acquire_degrees_field_decl_contract.py",
    "Scripts/tests/test_guided_lock_rules_helmet_lock_seconds_field_decl_contract.py",
    "Scripts/tests/test_guided_lock_rules_sensor_acquire_degrees_field_decl_contract.py",
    "Scripts/tests/test_guided_lock_rules_sensor_lock_seconds_field_decl_contract.py",
    "Scripts/tests/test_harbor_proof_play.py",
    "Scripts/tests/test_harbor_proof_source_tests.py",
    "Scripts/tests/test_hoist_window_runtime_defaults_contract.py",
    "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
    "Scripts/tests/test_how_to_fly_row_input_hint_field_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_instruction_field_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_step_id_field_decl_contract.py",
    "Scripts/tests/test_landscape_capture_config_defaults_contract.py",
    "Scripts/tests/test_landscape_capture_config_error_field_decl_contract.py",
    "Scripts/tests/test_landscape_capture_config_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_capture_config_view_mode_field_decl_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_error_field_decl_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_height_sample_error_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_height_centimeters_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_heightfield_source_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_query_location_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_valid_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_asset_compilation_queue_empty_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_defaults_contract.py",
    "Scripts/tests/test_landscape_material_compilation_error_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_generated_material_instance_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_shader_compilation_queue_empty_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_actor_hidden_in_game_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_actor_temporarily_hidden_in_editor_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_bounds_finite_and_nonzero_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_bounds_maximum_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_bounds_minimum_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_contract_camera_frustum_intersection_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_landscape_visible_audit_error_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_generated_material_instance_ready_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_governed_material_parent_match_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_hidden_in_game_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_landscape_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_registered_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_render_state_created_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_visible_component_count_field_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_debris_control_surface_field_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_debris_primary_sensor_field_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_debris_secondary_sensor_field_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_open_sensor_exposure_decl_contract.py",
    "Scripts/tests/test_loadout_spec_hull_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission01_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission01_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission01_authored_pcg_graph_field_decl_contract.py",
    "Scripts/tests/test_mission01_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission01_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission01_beach_material_field_decl_contract.py",
    "Scripts/tests/test_mission01_beach_tiles_field_decl_contract.py",
    "Scripts/tests/test_mission01_beach_width_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission01_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission01_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission01_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission01_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission01_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission01_coastal_haze_delay_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission01_coastal_haze_hold_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission01_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission01_district_length_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_enable_coastal_haze_transition_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_authored_structure_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_defaults_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_error_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_generated_pcg_component_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_generated_pcg_instance_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_generation_locked_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_contract_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_edge_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_node_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_node_setting_classes_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_landscape_component_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_landscape_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_landscape_guid_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_landscape_transform_exact_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_licensed_mesh_slots_empty_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_route_and_beach_generated_instances_zero_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_success_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_visible_audit_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_authored_landscape_surface_exposed_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_authored_pcg_graph_bound_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_authored_pcg_structure_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_beach_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_continuous_coastline_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_land_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_landscape_component_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_ocean_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_pcg_bounds_tagged_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_pcg_generation_authorized_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_production_landscape_bound_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_route_exclusion_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_root_field_decl_contract.py",
    "Scripts/tests/test_mission01_get_aircraft_decl_contract.py",
    "Scripts/tests/test_mission01_get_gunner_decl_contract.py",
    "Scripts/tests/test_mission01_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission01_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission01_get_pathfinder_decl_contract.py",
    "Scripts/tests/test_mission01_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission01_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission01_inland_extent_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_inland_vegetation_pcg_field_decl_contract.py",
    "Scripts/tests/test_mission01_is_authored_environment_ready_decl_contract.py",
    "Scripts/tests/test_mission01_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission01_land_material_field_decl_contract.py",
    "Scripts/tests/test_mission01_land_scatter_bounds_field_decl_contract.py",
    "Scripts/tests/test_mission01_land_tiles_field_decl_contract.py",
    "Scripts/tests/test_mission01_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission01_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_notify_objective_progress_decl_contract.py",
    "Scripts/tests/test_mission01_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission01_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_ocean_material_field_decl_contract.py",
    "Scripts/tests/test_mission01_ocean_tiles_field_decl_contract.py",
    "Scripts/tests/test_mission01_production_landscape_field_decl_contract.py",
    "Scripts/tests/test_mission01_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission01_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission01_rebuild_production_layout_decl_contract.py",
    "Scripts/tests/test_mission01_root_field_decl_contract.py",
    "Scripts/tests/test_mission01_route_corridor_half_width_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_route_exclusion_field_decl_contract.py",
    "Scripts/tests/test_mission01_route_length_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_sample_landscape_footprint_decl_contract.py",
    "Scripts/tests/test_mission01_sample_landscape_height_decl_contract.py",
    "Scripts/tests/test_mission01_seaward_extent_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_shoreline_land_offset_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission01_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission01_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission01_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission02_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission02_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission02_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission02_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission02_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission02_breakwater_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_breakwater_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission02_breakwater_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission02_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission02_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission02_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission02_get_aircraft_decl_contract.py",
    "Scripts/tests/test_mission02_get_breakwater_decl_contract.py",
    "Scripts/tests/test_mission02_get_current_wave_index_decl_contract.py",
    "Scripts/tests/test_mission02_get_fuel_terminal_integrity_decl_contract.py",
    "Scripts/tests/test_mission02_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission02_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission02_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission02_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission02_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission02_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission02_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission02_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission02_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_maximum_fuel_terminal_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission02_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission02_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission02_notify_fuel_terminal_damage_decl_contract.py",
    "Scripts/tests/test_mission02_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission02_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission02_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission02_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission02_radio_line_count_field_decl_contract.py",
    "Scripts/tests/test_mission02_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission02_root_field_decl_contract.py",
    "Scripts/tests/test_mission02_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission02_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission02_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission02_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission02_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission02_wave_state_enum_contract.py",
    "Scripts/tests/test_mission02_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission03_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission03_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission03_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission03_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission03_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission03_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission03_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission03_convoy_route_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_convoy_runtime_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission03_get_aircraft_decl_contract.py",
    "Scripts/tests/test_mission03_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission03_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission03_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission03_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission03_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission03_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission03_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission03_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_maximum_convoy_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission03_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission03_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission03_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission03_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission03_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission03_radio_line_count_field_decl_contract.py",
    "Scripts/tests/test_mission03_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission03_road_hunter_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_road_hunter_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission03_root_field_decl_contract.py",
    "Scripts/tests/test_mission03_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission03_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission03_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission03_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission03_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission03_wave_state_enum_contract.py",
    "Scripts/tests/test_mission03_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission04_advance_searchlight_track_decl_contract.py",
    "Scripts/tests/test_mission04_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission04_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission04_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission04_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission04_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission04_black_kite_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission04_black_kite_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission04_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission04_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission04_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission04_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission04_get_night_beat_kit_decl_contract.py",
    "Scripts/tests/test_mission04_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission04_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission04_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission04_get_searchlight_runtime_decl_contract.py",
    "Scripts/tests/test_mission04_get_substation_integrity_decl_contract.py",
    "Scripts/tests/test_mission04_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission04_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission04_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission04_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission04_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission04_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission04_maximum_substation_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission04_missed_track_damage_field_decl_contract.py",
    "Scripts/tests/test_mission04_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission04_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission04_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission04_notify_substation_damage_decl_contract.py",
    "Scripts/tests/test_mission04_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission04_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission04_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission04_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission04_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission04_required_track_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission04_root_field_decl_contract.py",
    "Scripts/tests/test_mission04_searchlight_port_field_decl_contract.py",
    "Scripts/tests/test_mission04_searchlight_starboard_field_decl_contract.py",
    "Scripts/tests/test_mission04_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission04_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission04_start_searchlight_window_decl_contract.py",
    "Scripts/tests/test_mission04_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission04_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission04_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission04_wave_state_enum_contract.py",
    "Scripts/tests/test_mission05_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission05_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission05_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission05_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission05_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission05_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission05_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission05_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission05_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission05_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission05_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission05_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission05_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission05_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission05_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission05_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission05_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission05_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission05_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission05_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission05_maximum_protected_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission05_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission05_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission05_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission05_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission05_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission05_protected_target_enum_contract.py",
    "Scripts/tests/test_mission05_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_mission05_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission05_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission05_root_field_decl_contract.py",
    "Scripts/tests/test_mission05_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission05_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission05_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission05_tempest_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission05_tempest_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission05_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission05_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission05_wave_state_enum_contract.py",
    "Scripts/tests/test_mission06_advance_payload_window_decl_contract.py",
    "Scripts/tests/test_mission06_airfield_target_runtime_destroyed_field_decl_contract.py",
    "Scripts/tests/test_mission06_airfield_target_runtime_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission06_airfield_target_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_mission06_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission06_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission06_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission06_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission06_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission06_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission06_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission06_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission06_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission06_get_payload_window_decl_contract.py",
    "Scripts/tests/test_mission06_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission06_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission06_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission06_get_target_runtime_decl_contract.py",
    "Scripts/tests/test_mission06_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission06_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission06_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission06_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_maximum_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission06_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission06_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission06_notify_airfield_target_damage_decl_contract.py",
    "Scripts/tests/test_mission06_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission06_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission06_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission06_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_payload_impact_damage_field_decl_contract.py",
    "Scripts/tests/test_mission06_payload_window_runtime_active_field_decl_contract.py",
    "Scripts/tests/test_mission06_payload_window_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_mission06_protected_target_count_field_decl_contract.py",
    "Scripts/tests/test_mission06_protected_targets_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission06_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission06_root_field_decl_contract.py",
    "Scripts/tests/test_mission06_runway_breaker_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_runway_breaker_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission06_runway_breaker_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission06_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission06_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission06_start_payload_window_decl_contract.py",
    "Scripts/tests/test_mission06_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission06_try_jam_active_payload_decl_contract.py",
    "Scripts/tests/test_mission06_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission06_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission06_wave_state_enum_contract.py",
    "Scripts/tests/test_mission06_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_advance_reinforcement_timer_decl_contract.py",
    "Scripts/tests/test_mission07_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission07_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission07_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission07_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission07_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission07_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission07_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission07_classify_false_track_decl_contract.py",
    "Scripts/tests/test_mission07_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission07_confirm_radar_ghost_identification_decl_contract.py",
    "Scripts/tests/test_mission07_get_classified_false_track_count_decl_contract.py",
    "Scripts/tests/test_mission07_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission07_get_night_beat_kit_decl_contract.py",
    "Scripts/tests/test_mission07_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission07_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission07_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission07_get_reinforcement_time_remaining_decl_contract.py",
    "Scripts/tests/test_mission07_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission07_get_search_sector_decl_contract.py",
    "Scripts/tests/test_mission07_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission07_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission07_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission07_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission07_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission07_is_hostile_contact_confirmed_decl_contract.py",
    "Scripts/tests/test_mission07_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_maximum_protected_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission07_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission07_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission07_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission07_notify_protected_target_damage_decl_contract.py",
    "Scripts/tests/test_mission07_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission07_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission07_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_protected_target_enum_contract.py",
    "Scripts/tests/test_mission07_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_mission07_protected_target_runtime_destroyed_field_decl_contract.py",
    "Scripts/tests/test_mission07_protected_target_runtime_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission07_protected_target_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_mission07_protected_targets_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_radar_ghost_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_radar_ghost_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission07_radar_ghost_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission07_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission07_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission07_reinforcement_deadline_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission07_root_field_decl_contract.py",
    "Scripts/tests/test_mission07_search_runtime_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_search_track_count_field_decl_contract.py",
    "Scripts/tests/test_mission07_search_track_runtime_sector_field_decl_contract.py",
    "Scripts/tests/test_mission07_search_track_runtime_track_id_field_decl_contract.py",
    "Scripts/tests/test_mission07_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission07_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission07_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission07_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission07_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission07_wave_state_enum_contract.py",
    "Scripts/tests/test_mission07_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_advance_hoist_window_decl_contract.py",
    "Scripts/tests/test_mission08_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission08_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission08_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission08_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission08_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission08_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission08_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission08_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission08_get_hoist_runtime_decl_contract.py",
    "Scripts/tests/test_mission08_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission08_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission08_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission08_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission08_get_rejected_weapon_releases_decl_contract.py",
    "Scripts/tests/test_mission08_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission08_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission08_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission08_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission08_hoist_cable_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission08_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission08_lifeline_hunter_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_lifeline_hunter_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission08_lifeline_hunter_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission08_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_maximum_protected_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission08_minimum_weapon_separation_meters_field_decl_contract.py",
    "Scripts/tests/test_mission08_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission08_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission08_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission08_notify_protected_target_damage_decl_contract.py",
    "Scripts/tests/test_mission08_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission08_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission08_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_target_count_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_target_enum_contract.py",
    "Scripts/tests/test_mission08_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_mission08_protected_target_runtime_destroyed_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_target_runtime_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_target_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_targets_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission08_rafts_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission08_required_covered_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission08_rescue_animation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_rescue_helicopter_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_rescue_vessel_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_root_field_decl_contract.py",
    "Scripts/tests/test_mission08_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission08_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_start_hoist_window_decl_contract.py",
    "Scripts/tests/test_mission08_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission08_survivors_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission08_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission08_validate_weapon_release_decl_contract.py",
    "Scripts/tests/test_mission08_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission08_wave_state_enum_contract.py",
    "Scripts/tests/test_mission08_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission09_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission09_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission09_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission09_bind_campaign_runtime_decl_contract.py",
    "Scripts/tests/test_mission09_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission09_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission09_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission09_escalating_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission09_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission09_get_pool_runtime_decl_contract.py",
    "Scripts/tests/test_mission09_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission09_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission09_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission09_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission09_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission09_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission09_iron_rain_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission09_major_bridge_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission09_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_max_active_decoys_field_decl_contract.py",
    "Scripts/tests/test_mission09_max_active_threats_field_decl_contract.py",
    "Scripts/tests/test_mission09_max_simultaneous_explosions_field_decl_contract.py",
    "Scripts/tests/test_mission09_maximum_protected_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission09_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission09_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission09_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission09_notify_protected_target_damage_decl_contract.py",
    "Scripts/tests/test_mission09_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission09_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission09_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_budget_defaults_contract.py",
    "Scripts/tests/test_mission09_pool_budget_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_budget_safe_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_capacity_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_active_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_available_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_defaults_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_peak_active_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_recycled_field_decl_contract.py",
    "Scripts/tests/test_mission09_power_station_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission09_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_target_count_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_target_enum_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_destroyed_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_targets_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission09_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission09_root_field_decl_contract.py",
    "Scripts/tests/test_mission09_skyline_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission09_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission09_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission09_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission09_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission09_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission09_wave_state_enum_contract.py",
    "Scripts/tests/test_mission10_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission10_ambulance_a_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_ambulance_b_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission10_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission10_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission10_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission10_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_bus_a_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_bus_b_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission10_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission10_evacuation_ship_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_ferry_terminal_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission10_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission10_get_protected_group_decl_contract.py",
    "Scripts/tests/test_mission10_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission10_get_rejected_weapon_releases_decl_contract.py",
    "Scripts/tests/test_mission10_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission10_get_route_phase_decl_contract.py",
    "Scripts/tests/test_mission10_get_surviving_protected_group_count_decl_contract.py",
    "Scripts/tests/test_mission10_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_highway_convoy_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission10_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission10_last_flight_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission10_last_flight_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission10_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_maximum_protected_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission10_minimum_weapon_separation_meters_field_decl_contract.py",
    "Scripts/tests/test_mission10_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission10_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission10_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission10_notify_protected_group_damage_decl_contract.py",
    "Scripts/tests/test_mission10_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission10_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission10_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_protected_group_enum_contract.py",
    "Scripts/tests/test_mission10_protected_runtime_defaults_contract.py",
    "Scripts/tests/test_mission10_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission10_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission10_root_field_decl_contract.py",
    "Scripts/tests/test_mission10_route_phase_enum_contract.py",
    "Scripts/tests/test_mission10_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission10_start_phase_wave_decl_contract.py",
    "Scripts/tests/test_mission10_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission10_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission10_validate_weapon_release_decl_contract.py",
    "Scripts/tests/test_mission10_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission_briefing_state_enum_contract.py",
    "Scripts/tests/test_mission_debrief_campaign_complete_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_defaults.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_defaults_tests.py",
    "Scripts/tests/test_mission_debrief_mission_display_name_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_narrative_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_new_best_medal_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_new_best_score_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_next_mission_display_name_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_next_mission_id_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_next_mission_map_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_next_mission_unlocked_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_progress_saved_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_result_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_state_field_decl_contract.py",
    "Scripts/tests/test_mission_map_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission_map_is_point_inside_flight_clearance_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_defaults_contract.py",
    "Scripts/tests/test_mission_map_readiness_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_landmarks_distinct_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_required_objectives_anchored_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_route_matches_definition_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_weather_matches_definition_field_decl_contract.py",
    "Scripts/tests/test_mission_map_rebuild_route_spline_decl_contract.py",
    "Scripts/tests/test_mission_map_validate_assembly_decl_contract.py",
    "Scripts/tests/test_mission_result_defaults.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_tests.py",
    "Scripts/tests/test_mission_result_final_score_field_decl_contract.py",
    "Scripts/tests/test_mission_result_medal_tier_field_decl_contract.py",
    "Scripts/tests/test_mission_skyline_style_enum_contract.py",
    "Scripts/tests/test_objective_progress_current_progress_field_decl_contract.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
    "Scripts/tests/test_objective_progress_objective_id_field_decl_contract.py",
    "Scripts/tests/test_objective_progress_state_field_decl_contract.py",
    "Scripts/tests/test_objective_runtime_fail_closed.py",
    "Scripts/tests/test_objective_runtime_fail_closed_contract.py",
    "Scripts/tests/test_objective_runtime_fail_closed_tests.py",
    "Scripts/tests/test_pathfinder_encounter_controller_field_decl_contract.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed_contract.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed_tests.py",
    "Scripts/tests/test_payload_window_runtime_defaults_contract.py",
    "Scripts/tests/test_protect_asset_apply_damage_decl_contract.py",
    "Scripts/tests/test_protect_asset_cargo_proxy.py",
    "Scripts/tests/test_protect_asset_cargo_proxy_contract.py",
    "Scripts/tests/test_protect_asset_cargo_proxy_tests.py",
    "Scripts/tests/test_protect_asset_current_integrity_field_decl_contract.py",
    "Scripts/tests/test_protect_asset_get_integrity_fraction_decl_contract.py",
    "Scripts/tests/test_protect_asset_is_destroyed_decl_contract.py",
    "Scripts/tests/test_protect_asset_max_integrity_field_decl_contract.py",
    "Scripts/tests/test_protect_asset_reset_integrity_decl_contract.py",
    "Scripts/tests/test_radar_ghost_radar_receiver_field_decl_contract.py",
    "Scripts/tests/test_radar_node_apply_damage_decl_contract.py",
    "Scripts/tests/test_radar_node_is_destroyed_decl_contract.py",
    "Scripts/tests/test_radar_node_max_health_field_decl_contract.py",
    "Scripts/tests/test_radar_node_presentation.py",
    "Scripts/tests/test_radar_node_presentation_contract.py",
    "Scripts/tests/test_radar_node_presentation_tests.py",
    "Scripts/tests/test_radar_node_reset_gameplay.py",
    "Scripts/tests/test_radar_node_reset_gameplay_contract.py",
    "Scripts/tests/test_radar_node_reset_gameplay_tests.py",
    "Scripts/tests/test_radar_node_reset_node_decl_contract.py",
    "Scripts/tests/test_radio_chatter_empty_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_fail_closed_contract.py",
    "Scripts/tests/test_radio_chatter_empty_fail_closed_tests.py",
    "Scripts/tests/test_radio_chatter_empty_line_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_line_fail_closed_contract.py",
    "Scripts/tests/test_radio_chatter_empty_line_fail_closed_tests.py",
    "Scripts/tests/test_radio_chatter_empty_line_tests.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed_contract.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed_tests.py",
    "Scripts/tests/test_radio_line_defaults_contract.py",
    "Scripts/tests/test_readable_escalation.py",
    "Scripts/tests/test_search_sector_enum_contract.py",
    "Scripts/tests/test_search_track_runtime_defaults_contract.py",
    "Scripts/tests/test_searchlight_track_runtime_defaults_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_sortie_debrief_loadouts.py",
    "Scripts/tests/test_sortie_director_empty_fail_closed.py",
    "Scripts/tests/test_sortie_presentation_fail_closed.py",
    "Scripts/tests/test_sortie_presentation_fail_closed_contract.py",
    "Scripts/tests/test_sortie_presentation_fail_closed_tests.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_theater_kit_root_field_decl_contract.py",
    "Scripts/tests/test_theater_kit_spec_weather_identity_field_decl_contract.py",
    "Scripts/tests/test_validate_definition_decl_contract.py",
) + leftover_live_copy_boss_scripts()

LEFTOVER_THEATER_KIT_DECL = "FName WeatherIdentity;"
LEFTOVER_THEATER_KIT_WRAP = (
    "UPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
    'Category="Skyguard|Theater")'
)
LEFTOVER_THEATER_KIT_STRUCT = "FSkyguardTheaterKitSpec"
LEFTOVER_MAX_INTEGRITY_DECL = "float MaxIntegrity = 140.f;"
LEFTOVER_MAX_INTEGRITY_WRAP = (
    "UPROPERTY(EditAnywhere, BlueprintReadWrite, "
    'Category="Skyguard|Apache|Damage", '
    'meta=(ClampMin="1.0"))'
)
LEFTOVER_ARCADE_LOOK_CLASS = "USkyguardArcadeLookComponent"
LEFTOVER_ARCADE_LOOK_WRAP = (
    "UPROPERTY(EditAnywhere, BlueprintReadWrite, "
    'Category="Skyguard|Arcade")'
)
LEFTOVER_ARCADE_LOOK_DECL = "float Contrast = 1.18f;"
LEFTOVER_ARCADE_LOOK_ENABLED = "bool bEnabled = true;"
LEFTOVER_PROTECT_ASSET_CLASS = "ASkyguardProtectAsset"
LEFTOVER_PROTECT_ASSET_DECL = "float MaxIntegrity = 100.f;"
LEFTOVER_PROTECT_ASSET_WRAP = (
    "UPROPERTY(EditAnywhere, BlueprintReadWrite, "
    'Category="Skyguard|Campaign")'
)
LEFTOVER_LOADOUT_SPEC = "FSkyguardLoadoutSpec"
LEFTOVER_HULL_INTEGRITY = "float HullIntegrity = 140.f;"
LEFTOVER_CAMPAIGN_SPEC = "FSkyguardCampaignMissionSpec"
LEFTOVER_GUIDED_LOCK_HEADER = (
    "Source/Skyguard52/SkyguardGuidedLockRules.h"
)
LEFTOVER_GUIDED_LOCK_STRUCT = "FSkyguardGuidedLockRules"
LEFTOVER_NIGHT_KIT = "FSkyguardNightSortieBeatKit"
LEFTOVER_RADAR_NODE_CLASS = "ASkyguardRadarNode"
TARGET_WRONG_EQ_NONE = "TObjectPtr<USceneComponent> EyeMount = nullptr;"
TARGET_WRONG_FALSE = "TObjectPtr<USceneComponent> EyeMount = false;"
TARGET_WRONG_TRUE = "TObjectPtr<USceneComponent> EyeMount = true;"
TARGET_WRONG_ZERO = "TObjectPtr<USceneComponent> EyeMount = 0.f;"
TARGET_WRONG_FLOAT = "float EyeMount;"
TARGET_WRONG_FNAME = "FName EyeMount;"
TARGET_WRONG_INT = "int32 EyeMount = 0;"
TARGET_WRONG_BOOL = "bool EyeMount = true;"
TARGET_WRONG_HEALTH = "float Health = 160.f;"
TARGET_WRONG_MAX = "float MaxIntegrity = 140.f;"
TARGET_WRONG_CURRENT = "float CurrentIntegrity = 140.f;"
TARGET_WRONG_HULL = "TObjectPtr<UBoxComponent> HullCollider;"
TARGET_WRONG_SILHOUETTE = "TObjectPtr<UStaticMeshComponent> SilhouetteMesh;"
TARGET_WRONG_STATIC_MESH = "TObjectPtr<UStaticMeshComponent> EyeMount;"
TARGET_WRONG_AIRCRAFT_ROOT = "TObjectPtr<USceneComponent> AircraftRoot;"
TARGET_WRONG_GUNNER_MOUNT = "TObjectPtr<USceneComponent> GunnerMount;"
TARGET_WRONG_PILOT_MOUNT = "TObjectPtr<USceneComponent> PilotMount;"
TARGET_WRONG_WEAPON_MOUNT = "TObjectPtr<USceneComponent> WeaponMount;"
TARGET_WRONG_SENSOR_TURRET = "TObjectPtr<USceneComponent> SensorTurret;"
TARGET_WRONG_SENSOR_BALL = "TObjectPtr<UStaticMeshComponent> SensorBall;"
TARGET_WRONG_HELLFIRE_LEFT = "TObjectPtr<UStaticMeshComponent> HellfireLeft;"
TARGET_WRONG_HELLFIRE_RIGHT = "TObjectPtr<UStaticMeshComponent> HellfireRight;"
TARGET_WRONG_ROTOR = "float RotorPower = 0.88f;"
TARGET_WRONG_HOVER = "float HoverBobCentimeters = 10.f;"
TARGET_WRONG_CONTRAST = "float Contrast = 1.18f;"
TARGET_WRONG_ENABLED = "bool bEnabled = true;"
TARGET_WRONG_WEATHER_IDENTITY = "FName WeatherIdentity;"
TARGET_WRONG_WEATHER_IDENTITY_FLOAT = "float WeatherIdentity;"
TARGET_WRONG_THEATER_WRAP = (
    "UPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
    'Category="Skyguard|Theater")'
)
TARGET_WRONG_CAMPAIGN_WRAP = (
    "UPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
    'Category="Skyguard|Campaign")'
)
TARGET_WRONG_ARCADE_WRAP = (
    "UPROPERTY(EditAnywhere, BlueprintReadWrite, "
    'Category="Skyguard|Arcade")'
)
TARGET_WRONG_EDIT_WRAP = (
    "UPROPERTY(EditAnywhere, BlueprintReadWrite, "
    'Category="Skyguard|Apache")'
)
STOP_BEFORE_PRIVATE = "private:"
STOP_BEFORE_WEAPON = "WeaponMount"
STOP_BEFORE_SORTIE = "ASkyguardGunshipSortieDirector"
STOP_BEFORE_AUDIO_EVENT = "enum class ESkyguardAudioEvent"
STOP_BEFORE_PICTOGRAM = "enum class ESkyguardBriefingPictogram"
STOP_BEFORE_EVENT_DEF = "struct FSkyguardAudioEventDefinition"
STOP_BEFORE_BOSS_WEAPON = "enum class ESkyguardBossWeapon"
STOP_BEFORE_PROP_SPINNER = "ASkyguardPropSpinner"
STOP_BEFORE_PATROL = "ASkyguardPatrolShipBoss"
STOP_BEFORE_GUNNER = "ASkyguardGunner"
STOP_BEFORE_WEAK_POINT = "USkyguardBossWeakPointComponent"
SET_SENSOR_VIEW = "SetSensorView"
GET_EYE_MOUNT = "GetEyeMount"
GET_ROTOR_RPM = "GetRotorRPM"
SET_FIRST_PERSON = "SetFirstPersonInterior"
SET_DIRECT_FLIGHT = "SetDirectFlightInput"
APPLY_DAMAGE = "ApplyDamage"
GET_FORWARD_SPEED = "GetForwardSpeed"
GET_DAMAGE_FRACTION = "GetDamageFraction"
AIM_CHIN_TURRET = "AimChinTurret"
SET_ROTOR_POWER = "SetRotorPower"
ISSUE_PILOT_COMMAND = "IssuePilotCommand"
GET_PILOT_COMMAND = "GetPilotCommand"
GET_PILOT_CONFIRMATIONS = "GetPilotConfirmationsIssued"
SET_ORBIT_FOCUS = "SetOrbitFocus"
FACE_WORLD_LOCATION = "FaceWorldLocation"
APPLY_SYSTEM_HIT = "ApplySystemHit"
APPLY_HIT = "ApplyHit"
IS_SENSOR_LIVE = "IsSensorLive"
IS_THERMAL_AVAILABLE = "IsThermalAvailable"
IS_SENSOR_VIEW_ACTIVE = "IsSensorViewActive"
IS_CANOPY_GLASS_CRACKED = "IsCanopyGlassCracked"
ARE_ENGINES_DOWN = "AreEnginesDown"
IS_CHIN_TURRET_DOWN = "IsChinTurretDown"
IS_ROTOR_DOWN = "IsRotorDown"
IS_SYSTEM_DOWN = "IsSystemDown"
FIND_NEAREST_LIVE_SYSTEM = "FindNearestLiveSystem"
GET_SENSOR_QUALITY = "GetSensorQuality"
GET_CHIN_SLEW_SCALE = "GetChinSlewScale"
GET_CHIN_FIRE_SCALE = "GetChinFireScale"
GET_ENGINE_POWER_SCALE = "GetEnginePowerScale"
GET_ROTOR_POWER_SCALE = "GetRotorPowerScale"
SIBLING_SILHOUETTE_MESH = "SilhouetteMesh"
SIBLING_ROTOR_POWER = "RotorPower"
SIBLING_HOVER_BOB = "HoverBobCentimeters"
SIBLING_MAX_INTEGRITY = "MaxIntegrity"
SIBLING_CURRENT_INTEGRITY = "CurrentIntegrity"
SIBLING_HULL_COLLIDER = "HullCollider"
SIBLING_AIRCRAFT_ROOT = "AircraftRoot"
SIBLING_GUNNER_MOUNT = "GunnerMount"
SIBLING_PILOT_MOUNT = "PilotMount"
SIBLING_WEAPON_MOUNT = "WeaponMount"
SIBLING_SENSOR_TURRET = "SensorTurret"
SIBLING_SENSOR_BALL = "SensorBall"
SIBLING_HELLFIRE_LEFT = "HellfireLeft"
SIBLING_HELLFIRE_RIGHT = "HellfireRight"
LEFTOVER_CANNON_FIRE_RATE = "CannonFireRate"
LEFTOVER_CANNON_RECOIL_PITCH = "CannonRecoilPitch"
LEFTOVER_CANNON_DAMAGE = "CannonDamage"
LEFTOVER_HELMET_LOCK_SECONDS = "HelmetLockSeconds"
LEFTOVER_HELMET_ACQUIRE_DEGREES = "HelmetAcquireDegrees"
LEFTOVER_SENSOR_LOCK_SECONDS = "SensorLockSeconds"
LEFTOVER_SENSOR_ACQUIRE_DEGREES = "SensorAcquireDegrees"
THIS_SCRIPT = (
    "Scripts/tests/test_apache_eye_mount"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_EMPTY = (
    "Scripts/tests/test_apache_aircraft_empty_fail_closed.py"
)
LEFTOVER_APACHE_EMPTY_TESTS = (
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_tests.py"
)
LEFTOVER_APACHE_EMPTY_CONTRACT = (
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_contract.py"
)
LEFTOVER_APACHE_HULL_COLLIDER = (
    "Scripts/tests/test_apache_hull_collider"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_AIRCRAFT_ROOT = (
    "Scripts/tests/test_apache_aircraft_root"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_GUNNER_MOUNT = (
    "Scripts/tests/test_apache_gunner_mount"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_PILOT_MOUNT = (
    "Scripts/tests/test_apache_pilot_mount"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_WEAPON_MOUNT = (
    "Scripts/tests/test_apache_weapon_mount"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_SENSOR_TURRET = (
    "Scripts/tests/test_apache_sensor_turret"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_SENSOR_BALL = (
    "Scripts/tests/test_apache_sensor_ball"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_HELLFIRE_LEFT = (
    "Scripts/tests/test_apache_hellfire_left"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_HELLFIRE_RIGHT = (
    "Scripts/tests/test_apache_hellfire_right"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_SILHOUETTE_MESH = (
    "Scripts/tests/test_apache_silhouette_mesh"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_MOUNT = (
    "Scripts/tests/test_apache_mount_fail_closed.py"
)
LEFTOVER_APACHE_MOUNT_TESTS = (
    "Scripts/tests/test_apache_mount_fail_closed_tests.py"
)
LEFTOVER_APACHE_MOUNT_CONTRACT = (
    "Scripts/tests/test_apache_mount_fail_closed_contract.py"
)
LEFTOVER_APACHE_CPG_FEEL = (
    "Scripts/tests/test_apache_cpg_feel_contract.py"
)
LEFTOVER_APACHE_OWN_SHIP = (
    "Scripts/tests/test_apache_own_ship_systems_contract.py"
)
LEFTOVER_APACHE_OWN_SHIP_TESTS = (
    "Scripts/tests/test_apache_own_ship_systems_tests.py"
)
LEFTOVER_PROTECT_MAX_INTEGRITY = (
    "Scripts/tests/test_protect_asset_max_integrity"
    "_field_decl_contract.py"
)
LEFTOVER_PROTECT_CURRENT_INTEGRITY = (
    "Scripts/tests/test_protect_asset_current_integrity"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_HULL_INTEGRITY = (
    "Scripts/tests/test_loadout_spec_hull_integrity"
    "_field_decl_contract.py"
)
LEFTOVER_ARCADE_LOOK_FAIL_CLOSED = (
    "Scripts/tests/test_arcade_look_fail_closed.py"
)
LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_TESTS = (
    "Scripts/tests/test_arcade_look_fail_closed_tests.py"
)
LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_CONTRACT = (
    "Scripts/tests/test_arcade_look_fail_closed_contract.py"
)
LEFTOVER_ARCADE_LOOK_WORLD_MOOD = (
    "Scripts/tests/test_arcade_look_world_mood_fail_closed.py"
)
LEFTOVER_ARCADE_LOOK_ENABLED_SCRIPT = (
    "Scripts/tests/test_arcade_look_enabled"
    "_field_decl_contract.py"
)
LEFTOVER_ARCADE_LOOK_CONTRAST_SCRIPT = (
    "Scripts/tests/test_arcade_look_contrast"
    "_field_decl_contract.py"
)
LEFTOVER_THEATER_KIT_WEATHER_IDENTITY = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
    "_field_decl_contract.py"
)
LEFTOVER_THEATER_KIT_ROOT = (
    "Scripts/tests/test_theater_kit_root"
    "_field_decl_contract.py"
)
LEFTOVER_THEATER_KIT_BULK = (
    "Scripts/tests/test_campaign_theater_kit_contract.py"
)
LEFTOVER_CAMPAIGN_ROSTER_LOOKUP = (
    "Scripts/tests/test_campaign_roster_lookup_tests.py"
)
LEFTOVER_GUIDED_HELMET_LOCK = (
    "Scripts/tests/test_guided_lock_rules_helmet_lock_seconds"
    "_field_decl_contract.py"
)
LEFTOVER_GUIDED_SENSOR_LOCK = (
    "Scripts/tests/test_guided_lock_rules_sensor_lock_seconds"
    "_field_decl_contract.py"
)
LEFTOVER_GUIDED_HELMET_ACQUIRE = (
    "Scripts/tests/test_guided_lock_rules_helmet_acquire_degrees"
    "_field_decl_contract.py"
)
LEFTOVER_GUIDED_SENSOR_ACQUIRE = (
    "Scripts/tests/test_guided_lock_rules_sensor_acquire_degrees"
    "_field_decl_contract.py"
)
LEFTOVER_MAX_INTEGRITY_SCRIPT = (
    "Scripts/tests/test_apache_max_integrity"
    "_field_decl_contract.py"
)
SIBLING_CURRENT_SCRIPT = (
    "Scripts/tests/test_apache_current_integrity"
    "_field_decl_contract.py"
)
LEFTOVER_SET_SENSOR_VIEW = (
    "Scripts/tests/test_apache_set_sensor_view"
    "_decl_contract.py"
)
LEFTOVER_GET_ROTOR_RPM = (
    "Scripts/tests/test_apache_get_rotor_rpm"
    "_decl_contract.py"
)

LOCKED = (
    "SkyguardApacheAircraft.cpp",
    "SkyguardArcadeLookComponent.cpp",
    "SkyguardArcadeLookTests.cpp",
    "SkyguardGuidedLockRules.h",
    "SkyguardGuidedLockRules.cpp",
    "SkyguardCampaignTheaterKit.h",
    "SkyguardCampaignTheaterKit.cpp",
    "SkyguardProtectAsset.h",
    "SkyguardProtectAsset.cpp",
    "SkyguardProtectAssetTests.cpp",
    "SkyguardGunshipTypes.h",
    "SkyguardCampaignRoster.h",
    "SkyguardNightSortieBeatKit.h",
    "SkyguardMissionTypes.h",
    "SkyguardHarborProofTests.cpp",
    "SkyguardRadarNode.h",
    "SkyguardRadarNode.cpp",
)

CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")
EYE_MOUNT_DECL_RE = re.compile(
    r"TObjectPtr\s*<\s*USceneComponent\s*>\s*EyeMount\s*;"
)
EYE_MOUNT_INIT_RE = re.compile(
    r"TObjectPtr\s*<\s*USceneComponent\s*>\s*EyeMount\s*="
)
EYE_MOUNT_FLOAT_RE = re.compile(r"float\s+EyeMount\b")
INVENTED_DECL_TOKENS = (
    "EditAnywhere",
    "BlueprintReadWrite",
    "BlueprintCallable",
    "BlueprintPure",
    "Transient",
    "MultiLine",
    "BlueprintAuthorityOnly",
    "ClampMin",
    "ClampMax",
    "meta=",
    "UPROPERTY",
    "Category",
    "GENERATED_BODY",
    "USTRUCT",
    "UFUNCTION",
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
    "= false",
    "= true",
    "= 0.f",
    "= 160.f",
    "= 100.f",
    "= 140.f",
    "= 12.0f",
    "= 22.0f",
    "= 12.f",
    "= 5.5f",
    "= 0.25f",
    "= 1.18f",
    "= NAME_None",
    "= nullptr",
)


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
    # Harbor is ONLY the 40/80 split tokens. Do not treat
    # leftover analog 140.f as Harbor 40.f.
    forty = "40" + ".f"
    eighty = "80" + ".f"
    return leftover_harbor_clock_tokens() + (
        "= " + forty,
        "= " + eighty,
        forty + ", " + eighty,
    )


def leftover_live_copy_tokens() -> tuple[str, ...]:
    return ("ig" + "la", "ya" + "k", "ri" + "fle")


def leftover_readiness_tokens() -> tuple[str, ...]:
    return (
        "b" + "Ya" + "kRuntimeReady",
        "ASkyguard" + "Ig" + "la" + "Missile",
    )


def leftover_live_copy_title_tokens() -> tuple[str, ...]:
    return ("Ig" + "la", "Ri" + "fle", "Ya" + "k")


def leftover_live_case_tokens() -> tuple[str, ...]:
    return leftover_live_copy_title_tokens()


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def leftover_pictogram_values() -> tuple[str, ...]:
    return (
        "ESkyguardBriefingPictogram::" + "Ri" + "fle",
        "ESkyguardBriefingPictogram::" + "Ig" + "la",
    )


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_SILHOUETTE_MESH,
        SIBLING_ROTOR_POWER,
        SIBLING_HOVER_BOB,
        SIBLING_MAX_INTEGRITY,
        SIBLING_CURRENT_INTEGRITY,
        SIBLING_HULL_COLLIDER,
        SIBLING_AIRCRAFT_ROOT,
        SIBLING_GUNNER_MOUNT,
        SIBLING_PILOT_MOUNT,
        SIBLING_WEAPON_MOUNT,
        SIBLING_SENSOR_TURRET,
        SIBLING_SENSOR_BALL,
        SIBLING_HELLFIRE_LEFT,
        SIBLING_HELLFIRE_RIGHT,
    )


def leftover_ufunction_names() -> tuple[str, ...]:
    return (
        SET_SENSOR_VIEW,
        GET_EYE_MOUNT,
        GET_ROTOR_RPM,
        SET_FIRST_PERSON,
        SET_DIRECT_FLIGHT,
        APPLY_DAMAGE,
        GET_FORWARD_SPEED,
        GET_DAMAGE_FRACTION,
        AIM_CHIN_TURRET,
        SET_ROTOR_POWER,
        ISSUE_PILOT_COMMAND,
        GET_PILOT_COMMAND,
        GET_PILOT_CONFIRMATIONS,
        SET_ORBIT_FOCUS,
        FACE_WORLD_LOCATION,
        APPLY_SYSTEM_HIT,
        APPLY_HIT,
        IS_SENSOR_LIVE,
        IS_THERMAL_AVAILABLE,
        IS_SENSOR_VIEW_ACTIVE,
        IS_CANOPY_GLASS_CRACKED,
        ARE_ENGINES_DOWN,
        IS_CHIN_TURRET_DOWN,
        IS_ROTOR_DOWN,
        IS_SYSTEM_DOWN,
        FIND_NEAREST_LIVE_SYSTEM,
        GET_SENSOR_QUALITY,
        GET_CHIN_SLEW_SCALE,
        GET_CHIN_FIRE_SCALE,
        GET_ENGINE_POWER_SCALE,
        GET_ROTOR_POWER_SCALE,
    )


def leftover_analog_feel_fields() -> tuple[str, ...]:
    return (
        LEFTOVER_CANNON_FIRE_RATE,
        LEFTOVER_CANNON_RECOIL_PITCH,
        LEFTOVER_CANNON_DAMAGE,
    )


def leftover_guided_lock_fields() -> tuple[str, ...]:
    return (
        LEFTOVER_HELMET_LOCK_SECONDS,
        LEFTOVER_HELMET_ACQUIRE_DEGREES,
        LEFTOVER_SENSOR_LOCK_SECONDS,
        LEFTOVER_SENSOR_ACQUIRE_DEGREES,
    )


def this_file_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*<\s*", "<", compact)
    compact = re.sub(r"\s*>", ">", compact)
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
    # Fail-closed on the authored bare
    # `TObjectPtr<USceneComponent> EyeMount;`.
    # Do not accept `= nullptr` / leftover float /
    # leftover TheaterKit WeatherIdentity /
    # leftover MaxIntegrity = 140.f / leftover 160.f
    # Health when origin/main has a bare TObjectPtr.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if EYE_MOUNT_INIT_RE.search(compact):
        return False
    if EYE_MOUNT_FLOAT_RE.search(compact):
        return False
    if EYE_MOUNT_DECL_RE.search(compact) is None:
        return False
    if re.search(r"FName\s+EyeMount\b", compact):
        return False
    if re.search(r"int32\s+EyeMount\b", compact):
        return False
    if re.search(r"bool\s+EyeMount\b", compact):
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


def leaked_neighbor_tokens() -> tuple[str, ...]:
    return (
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
        LEFTOVER_THEATER_KIT_STRUCT,
        LEFTOVER_ARCADE_LOOK_CLASS,
        LEFTOVER_LOADOUT_SPEC,
        LEFTOVER_CAMPAIGN_SPEC,
        LEFTOVER_GUIDED_LOCK_STRUCT,
        LEFTOVER_NIGHT_KIT,
        LEFTOVER_GUIDED_LOCK_HEADER,
        "struct FSkyguardTheaterKitSpec",
        "struct FSkyguardCampaignMissionSpec",
        "struct FSkyguardGuidedLockRules",
        "struct FSkyguardLoadoutSpec",
        "class USkyguardArcadeLookComponent",
        f"class SKYGUARD52_API {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_RADAR_NODE_CLASS}",
        f"class {LEFTOVER_RADAR_NODE_CLASS}",
        "HullIntegrity",
        "WeatherIdentity",
        "HelmetLockSeconds",
        "SensorLockSeconds",
        "HelmetAcquireDegrees",
        "CannonFireRate",
        "CannonRecoilPitch",
        "CannonDamage",
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


def protected_section(header: str) -> str:
    body = class_body(header)
    protected = re.search(r"\bprotected\s*:", body)
    if protected is None:
        raise AssertionError(
            f"{CLASS_NAME} protected section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = protected.end()
    rest = body[start:]
    next_access = ACCESS_RE.search(rest)
    if next_access is not None:
        return rest[: next_access.start()]
    close = rest.rfind("}")
    if close == -1:
        raise AssertionError(
            f"{CLASS_NAME} protected section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    return rest[:close]


def spec_section(header: str) -> str:
    section = protected_section(header)
    first_prop = section.find("UPROPERTY")
    if first_prop == -1:
        raise AssertionError(
            f"{CLASS_NAME} protected UPROPERTY fields are missing from "
            f"origin/main:{HEADER_PATH}"
        )
    section = section[first_prop:]
    if STOP_BEFORE_PRIVATE in section:
        raise AssertionError(
            f"{CLASS_NAME} parse window includes private:"
        )
    for token in leaked_neighbor_tokens():
        if token in section:
            raise AssertionError(
                f"{CLASS_NAME} parse window includes {token}"
            )
    forty = "40" + ".f"
    eighty = "80" + ".f"
    if ("= " + forty) in section or ("= " + eighty) in section:
        raise AssertionError(
            f"{CLASS_NAME} parse window includes Harbor 40/80 tokens"
        )
    if (forty + ", " + eighty) in section:
        raise AssertionError(
            f"{CLASS_NAME} parse window includes Harbor 40/80 pair"
        )
    return section


def claimed_field_window(header: str) -> str:
    section = spec_section(header)
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
        after = compact[index:]
        field = re.match(
            r"\s*TObjectPtr<USceneComponent>\s*EyeMount\s*;",
            after,
        )
        if depth == 0 and field is not None:
            window = compact[cursor + match.start() : index + field.end()]
            for sibling in sibling_uncontracted_decls():
                if re.search(r"\b" + re.escape(sibling) + r"\b", window):
                    raise AssertionError(
                        f"claimed window includes sibling {sibling}"
                    )
            for leftover in leftover_ufunction_names():
                if leftover in window:
                    raise AssertionError(
                        f"claimed window includes leftover {leftover}"
                    )
            if LEFTOVER_THEATER_KIT_DECL in window:
                raise AssertionError(
                    "claimed window includes leftover TheaterKit "
                    "WeatherIdentity"
                )
            if STOP_BEFORE_PRIVATE in window:
                raise AssertionError(
                    "claimed window includes private:"
                )
            if STOP_BEFORE_WEAPON in window:
                raise AssertionError(
                    "claimed window includes sibling WeaponMount"
                )
            return window
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for TObjectPtr<USceneComponent> EyeMount; is "
        f"missing from origin/main:{HEADER_PATH} class {CLASS_NAME} "
        "protected UPROPERTY fields"
    )


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
            r"\s*TObjectPtr<USceneComponent>\s*EyeMount\b",
            compact[index:],
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for TObjectPtr<USceneComponent> EyeMount is "
        f"missing from origin/main:{HEADER_PATH} class {CLASS_NAME} "
        "protected UPROPERTY fields"
    )


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"class {CLASS_NAME} protected UPROPERTY fields"
        )
    return declaration


class ApacheEyeMountFieldDeclContractTests(unittest.TestCase):
    def test_apache_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertIn(f"class SKYGUARD52_API {CLASS_NAME}", header)
        self.assertEqual(CLASS_NAME, "ASkyguardApacheAircraft")
        self.assertNotEqual(CLASS_NAME, LEFTOVER_PROTECT_ASSET_CLASS)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_ARCADE_LOOK_CLASS)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_THEATER_KIT_STRUCT)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_LOADOUT_SPEC)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_CAMPAIGN_SPEC)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_GUIDED_LOCK_STRUCT)
        self.assertNotEqual(CLASS_NAME, STOP_BEFORE_SORTIE)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = spec_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(has_identifier(section, "EyeMount"), section)
        self.assertIn("UPROPERTY", section)
        claimed = claimed_field_window(header)
        self.assertTrue(has_declaration(claimed, LOCKED_DECL), claimed)
        self.assertNotIn(SIBLING_SILHOUETTE_MESH, claimed)
        self.assertNotIn(SIBLING_ROTOR_POWER, claimed)
        self.assertNotIn(SIBLING_HOVER_BOB, claimed)
        self.assertNotIn(SIBLING_MAX_INTEGRITY, claimed)
        self.assertNotIn(SIBLING_CURRENT_INTEGRITY, claimed)
        self.assertNotIn(SIBLING_HULL_COLLIDER, claimed)
        self.assertNotIn(SIBLING_AIRCRAFT_ROOT, claimed)
        self.assertNotIn(SIBLING_GUNNER_MOUNT, claimed)
        self.assertNotIn(SIBLING_PILOT_MOUNT, claimed)
        self.assertNotIn(SIBLING_WEAPON_MOUNT, claimed)
        self.assertNotIn(SIBLING_SENSOR_TURRET, claimed)
        self.assertNotIn(SIBLING_SENSOR_BALL, claimed)
        self.assertNotIn(SIBLING_HELLFIRE_LEFT, claimed)
        self.assertNotIn(SIBLING_HELLFIRE_RIGHT, claimed)
        self.assertNotIn(STOP_BEFORE_PRIVATE, claimed)
        self.assertNotIn(STOP_BEFORE_WEAPON, claimed)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class ASkyguardUnrelatedApacheAircraft\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_protect_asset_class_does_not_satisfy(self) -> None:
        other = (
            f"class {LEFTOVER_PROTECT_ASSET_CLASS}\n"
            "{\n"
            "protected:\n"
            f"\t{LEFTOVER_PROTECT_ASSET_WRAP}\n"
            f"\t{LEFTOVER_PROTECT_ASSET_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        mixed = (
            f"class {LEFTOVER_PROTECT_ASSET_CLASS}\n"
            "{\n"
            "protected:\n"
            f"\t{UPROPERTY_VISIBLE_READONLY}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(mixed)
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_other_type_does_not_satisfy(self) -> None:
        leftovers = (
            LEFTOVER_THEATER_KIT_STRUCT,
            LEFTOVER_ARCADE_LOOK_CLASS,
            LEFTOVER_LOADOUT_SPEC,
            LEFTOVER_CAMPAIGN_SPEC,
            LEFTOVER_GUIDED_LOCK_STRUCT,
            STOP_BEFORE_SORTIE,
        )
        for name in leftovers:
            kind = "class" if name.startswith(("A", "U")) else "struct"
            other = (
                f"{kind} {name}\n"
                "{\n"
                "protected:\n"
                f"\t{UPROPERTY_VISIBLE_READONLY}\n"
                f"\t{LOCKED_DECL}\n"
                "};\n"
            )
            with self.assertRaises(AssertionError) as raised:
                spec_section(other)
            self.assertIn(CLASS_NAME, str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_neighbor_class_declaration_does_not_satisfy(self) -> None:
        mixed = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            f"\t{UPROPERTY_VISIBLE_READONLY}\n"
            f"\t{TARGET_WRONG_SILHOUETTE}\n"
            "};\n"
            f"class {LEFTOVER_PROTECT_ASSET_CLASS}\n"
            "{\n"
            "protected:\n"
            f"\t{UPROPERTY_VISIBLE_READONLY}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        section = spec_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("EyeMount", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_eye_mount_declaration_fails_closed(self) -> None:
        empty = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            f"\t{UPROPERTY_VISIBLE_READONLY}\n"
            f"\t{TARGET_WRONG_SILHOUETTE}\n"
            "};\n"
        )
        section = spec_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("EyeMount", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_VISIBLE_READONLY}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("EyeMount", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotIn("WeatherIdentity", str(raised.exception))

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = spec_section(origin_main_header())
        self.assertIn("VisibleAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('Category="Skyguard|Apache"', section)
        self.assertIn("VisibleAnywhere", UPROPERTY_VISIBLE_READONLY)
        self.assertIn("BlueprintReadOnly", UPROPERTY_VISIBLE_READONLY)
        self.assertIn("Category", UPROPERTY_VISIBLE_READONLY)
        self.assertIn(
            'Category="Skyguard|Apache"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertNotIn("EditAnywhere", UPROPERTY_VISIBLE_READONLY)
        self.assertNotIn("BlueprintReadWrite", UPROPERTY_VISIBLE_READONLY)
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertNotIn(
            'Category="Skyguard|Arcade"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertNotIn(
            'Category="Skyguard|Campaign"',
            UPROPERTY_VISIBLE_READONLY,
        )
        specifiers = attached_uproperty_specifiers(section)
        self.assertIn("VisibleAnywhere", specifiers)
        self.assertIn("BlueprintReadOnly", specifiers)
        self.assertIn('Category="Skyguard|Apache"', specifiers)
        self.assertNotIn("EditAnywhere", specifiers)
        self.assertNotIn("BlueprintReadWrite", specifiers)
        self.assertNotIn('Category="Skyguard|Theater"', specifiers)
        self.assertNotIn('Category="Skyguard|Arcade"', specifiers)
        self.assertNotIn("MultiLine", specifiers)
        self.assertNotIn("ClampMin", specifiers)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertNotIn("UFUNCTION", LOCKED_DECL)
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        self.assertNotIn("ClampMin", LOCKED_DECL)
        self.assertNotIn("GENERATED_BODY", LOCKED_DECL)
        self.assertNotIn("USTRUCT", LOCKED_DECL)
        for invented in INVENTED_DECL_TOKENS:
            self.assertNotIn(invented, LOCKED_DECL)

    def test_locked_decl_is_not_leftover_theater_or_arcade(self) -> None:
        self.assertEqual(
            LOCKED_DECL,
            "TObjectPtr<USceneComponent> EyeMount;",
        )
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_AIRCRAFT_ROOT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_GUNNER_MOUNT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_PILOT_MOUNT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_WEAPON_MOUNT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SENSOR_TURRET)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SENSOR_BALL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_HELLFIRE_LEFT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_HELLFIRE_RIGHT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_STATIC_MESH)
        self.assertNotIn("UStaticMeshComponent", LOCKED_DECL)
        self.assertNotIn("apache-mount-fail-closed", LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_THEATER_KIT_DECL)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_MAX_INTEGRITY_DECL)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_ARCADE_LOOK_DECL)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_ARCADE_LOOK_ENABLED)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_PROTECT_ASSET_DECL)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_HULL_INTEGRITY)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_HEALTH)
        self.assertNotEqual(
            UPROPERTY_VISIBLE_READONLY,
            LEFTOVER_THEATER_KIT_WRAP,
        )
        self.assertNotEqual(
            UPROPERTY_VISIBLE_READONLY,
            LEFTOVER_ARCADE_LOOK_WRAP,
        )
        self.assertNotEqual(
            UPROPERTY_VISIBLE_READONLY,
            LEFTOVER_PROTECT_ASSET_WRAP,
        )
        self.assertNotEqual(
            UPROPERTY_VISIBLE_READONLY,
            LEFTOVER_MAX_INTEGRITY_WRAP,
        )
        self.assertIn("TObjectPtr<", LOCKED_DECL)
        self.assertIn("USceneComponent", LOCKED_DECL)
        self.assertIn("EyeMount", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("WeatherIdentity", LOCKED_DECL)
        self.assertNotIn("MaxIntegrity", LOCKED_DECL)
        self.assertNotIn("HullIntegrity", LOCKED_DECL)
        self.assertNotIn("160.f", LOCKED_DECL)
        self.assertNotIn("140.f", LOCKED_DECL)
        self.assertNotIn("=", LOCKED_DECL)
        self.assertIn("VisibleAnywhere", UPROPERTY_VISIBLE_READONLY)
        self.assertIn("BlueprintReadOnly", UPROPERTY_VISIBLE_READONLY)
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertIn(
            'Category="Skyguard|Apache"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertFalse(
            has_declaration(
                f"\t{LEFTOVER_THEATER_KIT_WRAP}\n"
                f"\t{LEFTOVER_THEATER_KIT_DECL}\n",
                LOCKED_DECL,
            )
        )
        self.assertFalse(
            has_declaration(
                f"\t{LEFTOVER_MAX_INTEGRITY_WRAP}\n"
                f"\t{LEFTOVER_MAX_INTEGRITY_DECL}\n",
                LOCKED_DECL,
            )
        )
        self.assertFalse(
            has_declaration(
                f"\t{TARGET_WRONG_HEALTH}\n",
                LOCKED_DECL,
            )
        )

    def test_locked_decl_requires_bare_pointer(self) -> None:
        self.assertNotIn("=", LOCKED_DECL)
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_EQ_NONE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FLOAT}\n", LOCKED_DECL)
        )
        origin = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIn(
            "TObjectPtr<USceneComponent> EyeMount;",
            compact_origin,
        )
        self.assertNotIn("EyeMount = nullptr", compact_origin)
        self.assertNotIn("EyeMount = NAME_None", compact_origin)
        self.assertNotIn("EyeMount = false", compact_origin)
        self.assertNotIn("EyeMount = true", compact_origin)
        self.assertNotIn("EyeMount = 0.f", compact_origin)
        self.assertNotIn("EyeMount = 160.f", compact_origin)

    def test_eye_mount_declaration_matches_origin_main(self) -> None:
        section = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(
            LOCKED_DECL.startswith("TObjectPtr<USceneComponent> EyeMount"),
            LOCKED_DECL,
        )
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertNotIn("=", LOCKED_DECL)
        self.assertNotIn("= 140.f", LOCKED_DECL)
        self.assertNotIn("= 100.f", LOCKED_DECL)
        self.assertNotIn("= 160.f", LOCKED_DECL)
        self.assertNotIn("= 0.f", LOCKED_DECL)
        self.assertNotIn("= false", LOCKED_DECL)
        self.assertNotIn("= true", LOCKED_DECL)
        self.assertNotIn("= NAME_None", LOCKED_DECL)
        self.assertNotIn("= nullptr", LOCKED_DECL)
        self.assertIn("TObjectPtr<", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("float ", LOCKED_DECL)
        self.assertNotIn("bool ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn("WeatherIdentity", LOCKED_DECL)
        self.assertNotIn("MaxIntegrity", LOCKED_DECL)
        self.assertNotIn("HullIntegrity", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        self.assertNotIn("GENERATED_BODY", LOCKED_DECL)
        self.assertNotIn("USTRUCT", LOCKED_DECL)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_EQ_NONE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FNAME}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_HEALTH}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_MAX}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_CURRENT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{LEFTOVER_THEATER_KIT_DECL}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_EQ_NONE}\n", LOCKED_DECL)
        self.assertIn("EyeMount", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tfloat " + leftover_retired_primary_hits_field()
            + " = 140.f;\n"
        )
        leftover_guided = (
            "\tfloat " + leftover_retired_guided_hits_field()
            + " = 140.f;\n"
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
            f"\t{TARGET_WRONG_INT}\n",
            f"\t{TARGET_WRONG_BOOL}\n",
            f"\t{TARGET_WRONG_HEALTH}\n",
            f"\t{TARGET_WRONG_MAX}\n",
            f"\t{TARGET_WRONG_CURRENT}\n",
            f"\t{TARGET_WRONG_HULL}\n",
            f"\t{TARGET_WRONG_SILHOUETTE}\n",
            f"\t{TARGET_WRONG_ROTOR}\n",
            f"\t{TARGET_WRONG_HOVER}\n",
            f"\t{TARGET_WRONG_CONTRAST}\n",
            f"\t{TARGET_WRONG_ENABLED}\n",
            f"\t{TARGET_WRONG_WEATHER_IDENTITY}\n",
            f"\t{TARGET_WRONG_WEATHER_IDENTITY_FLOAT}\n",
            leftover_primary,
            leftover_guided,
            "\tTObjectPtr<USceneComponent> EyeMounts;\n",
            "\tTObjectPtr<UStaticMeshComponent> EyeMount;\n",
            f"\t{TARGET_WRONG_STATIC_MESH}\n",
            f"\t{TARGET_WRONG_AIRCRAFT_ROOT}\n",
            f"\t{TARGET_WRONG_GUNNER_MOUNT}\n",
            f"\t{TARGET_WRONG_PILOT_MOUNT}\n",
            f"\t{TARGET_WRONG_WEAPON_MOUNT}\n",
            f"\t{TARGET_WRONG_SENSOR_TURRET}\n",
            f"\t{TARGET_WRONG_SENSOR_BALL}\n",
            f"\t{TARGET_WRONG_HELLFIRE_LEFT}\n",
            f"\t{TARGET_WRONG_HELLFIRE_RIGHT}\n",
            "\tTObjectPtr<USceneComponent> Root;\n",
            "\tFName WeatherIdentity;\n",
            "\tfloat EyeMount = " + forty + ";\n",
            "\tfloat EyeMount = " + eighty + ";\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("EyeMount", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_missing_category_or_visible_anywhere_fails_closed(self) -> None:
        no_category = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly)\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        section = spec_section(no_category)
        specifiers = attached_uproperty_specifiers(section)
        self.assertNotIn("Category", specifiers)
        origin = attached_uproperty_specifiers(
            spec_section(origin_main_header())
        )
        self.assertIn("Category", origin)
        self.assertIn('Category="Skyguard|Apache"', origin)
        self.assertIn("VisibleAnywhere", origin)
        self.assertIn("BlueprintReadOnly", origin)
        no_visible = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            "\tUPROPERTY(BlueprintReadOnly, "
            'Category="Skyguard|Apache")\n'
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        dropped = attached_uproperty_specifiers(
            spec_section(no_visible)
        )
        self.assertNotIn("VisibleAnywhere", dropped)
        self.assertIn("VisibleAnywhere", origin)
        leftover_wrap = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            f"\t{LEFTOVER_THEATER_KIT_WRAP}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        leftover_specs = attached_uproperty_specifiers(
            spec_section(leftover_wrap)
        )
        self.assertIn("VisibleAnywhere", leftover_specs)
        self.assertIn("BlueprintReadOnly", leftover_specs)
        self.assertIn('Category="Skyguard|Theater"', leftover_specs)
        self.assertNotIn('Category="Skyguard|Apache"', leftover_specs)
        edit_wrap = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            f"\t{TARGET_WRONG_EDIT_WRAP}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        edit_specs = attached_uproperty_specifiers(
            spec_section(edit_wrap)
        )
        self.assertIn("EditAnywhere", edit_specs)
        self.assertIn("BlueprintReadWrite", edit_specs)
        self.assertNotIn("VisibleAnywhere", edit_specs)
        self.assertNotIn("BlueprintReadOnly", edit_specs)
        arcade = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            f"\t{TARGET_WRONG_ARCADE_WRAP}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        arcade_specs = attached_uproperty_specifiers(
            spec_section(arcade)
        )
        self.assertIn('Category="Skyguard|Arcade"', arcade_specs)
        self.assertNotIn(
            'Category="Skyguard|Apache"',
            arcade_specs,
        )
        self.assertIn('Category="Skyguard|Apache"', origin)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wraps = (
            "\tTObjectPtr<USceneComponent>\n\tEyeMount;\n",
            "\tTObjectPtr<USceneComponent>   EyeMount;\n",
            "\tTObjectPtr<USceneComponent>\tEyeMount;\n",
            "\tTObjectPtr<\n\tUSceneComponent> EyeMount;\n",
            f"\t{LOCKED_DECL}\n",
            f"\t{UPROPERTY_VISIBLE_READONLY}\n\t{LOCKED_DECL}\n",
            f"\t{UPROPERTY_VISIBLE_READONLY} {LOCKED_DECL}\n",
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
            'Category="Skyguard|Apache")\n'
            f"\t{LOCKED_DECL}\n",
            "\tUPROPERTY(\n\t\tVisibleAnywhere, BlueprintReadOnly, "
            'Category="Skyguard|Apache")\n'
            f"\t{LOCKED_DECL}\n",
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly,\n"
            '\t\tCategory="Skyguard|Apache")\n'
            f"\t{LOCKED_DECL}\n",
        )
        for region in wraps:
            self.assertTrue(has_declaration(region, LOCKED_DECL), region)
        header = origin_main_header()
        section = spec_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertIn(
            collapsed(UPROPERTY_VISIBLE_READONLY),
            collapsed(section),
        )

    def test_does_not_contract_sibling_fields(self) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        section = spec_section(origin_main_header())
        self.assertTrue(has_identifier(section, SIBLING_SILHOUETTE_MESH))
        self.assertTrue(has_identifier(section, SIBLING_ROTOR_POWER))
        self.assertTrue(has_identifier(section, SIBLING_HOVER_BOB))
        self.assertTrue(has_identifier(section, SIBLING_AIRCRAFT_ROOT))
        self.assertTrue(has_identifier(section, SIBLING_GUNNER_MOUNT))
        self.assertTrue(has_identifier(section, SIBLING_PILOT_MOUNT))
        self.assertTrue(has_identifier(section, SIBLING_WEAPON_MOUNT))
        self.assertTrue(has_identifier(section, SIBLING_SENSOR_TURRET))
        self.assertTrue(has_identifier(section, SIBLING_SENSOR_BALL))
        self.assertTrue(has_identifier(section, SIBLING_HELLFIRE_LEFT))
        self.assertTrue(has_identifier(section, SIBLING_HELLFIRE_RIGHT))
        claimed = claimed_field_window(origin_main_header())
        for sibling in sibling_uncontracted_decls():
            self.assertFalse(
                has_identifier(claimed, sibling),
                sibling,
            )
        self.assertIn(STOP_BEFORE_WEAPON, section)
        self.assertNotIn(STOP_BEFORE_WEAPON, claimed)
        public = public_section(origin_main_header())
        self.assertIn(SIBLING_MAX_INTEGRITY, public)
        self.assertIn(SIBLING_CURRENT_INTEGRITY, public)
        self.assertIn(SIBLING_HULL_COLLIDER, public)
        self.assertNotIn(SIBLING_MAX_INTEGRITY, section)
        self.assertNotIn(SIBLING_CURRENT_INTEGRITY, section)
        self.assertNotIn(SIBLING_HULL_COLLIDER, section)

    def test_claimed_window_stops_before_weapon_mount(self) -> None:
        claimed = claimed_field_window(origin_main_header())
        self.assertIn("EyeMount", claimed)
        self.assertIn("TObjectPtr", claimed)
        self.assertIn("USceneComponent", claimed)
        self.assertIn("UPROPERTY", claimed)
        self.assertIn("VisibleAnywhere", claimed)
        self.assertIn("BlueprintReadOnly", claimed)
        self.assertIn('Category="Skyguard|Apache"', claimed)
        self.assertNotIn(SIBLING_SILHOUETTE_MESH, claimed)
        self.assertNotIn(SIBLING_ROTOR_POWER, claimed)
        self.assertNotIn(SIBLING_HOVER_BOB, claimed)
        self.assertNotIn(SIBLING_MAX_INTEGRITY, claimed)
        self.assertNotIn(SIBLING_CURRENT_INTEGRITY, claimed)
        self.assertNotIn(SIBLING_HULL_COLLIDER, claimed)
        self.assertNotIn(SIBLING_AIRCRAFT_ROOT, claimed)
        self.assertNotIn(SIBLING_GUNNER_MOUNT, claimed)
        self.assertNotIn(SIBLING_PILOT_MOUNT, claimed)
        self.assertNotIn(SIBLING_WEAPON_MOUNT, claimed)
        self.assertNotIn(SIBLING_SENSOR_TURRET, claimed)
        self.assertNotIn(SIBLING_SENSOR_BALL, claimed)
        self.assertNotIn(SIBLING_HELLFIRE_LEFT, claimed)
        self.assertNotIn(SIBLING_HELLFIRE_RIGHT, claimed)
        self.assertNotIn(STOP_BEFORE_PRIVATE, claimed)
        self.assertNotIn(STOP_BEFORE_WEAPON, claimed)
        mixed = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            f"\t{UPROPERTY_VISIBLE_READONLY}\n"
            f"\t{LOCKED_DECL}\n"
            f"\t{UPROPERTY_VISIBLE_READONLY}\n"
            f"\t{TARGET_WRONG_WEAPON_MOUNT}\n"
            "};\n"
        )
        window = claimed_field_window(mixed)
        self.assertTrue(has_declaration(window, LOCKED_DECL), window)
        self.assertNotIn(SIBLING_WEAPON_MOUNT, window)
        self.assertNotIn(SIBLING_SILHOUETTE_MESH, window)

    def test_parse_window_starts_at_protected_stops_before_private(self) -> None:
        header = origin_main_header()
        public = public_section(header)
        protected = protected_section(header)
        section = spec_section(header)
        self.assertNotIn(STOP_BEFORE_PRIVATE, protected)
        self.assertNotIn(STOP_BEFORE_PRIVATE, section)
        self.assertIn("EyeMount", class_body(header))
        self.assertIn("EyeMount", protected)
        self.assertIn("EyeMount", section)
        self.assertTrue(has_declaration(protected, LOCKED_DECL), protected)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertFalse(has_declaration(public, LOCKED_DECL), public)
        self.assertNotIn(LOCKED_DECL, public)
        self.assertIn(GET_EYE_MOUNT, public)
        self.assertNotIn(GET_EYE_MOUNT, section)
        self.assertIn(SIBLING_MAX_INTEGRITY, public)
        self.assertNotIn(SIBLING_MAX_INTEGRITY, section)
        mixed = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{LEFTOVER_MAX_INTEGRITY_WRAP}\n"
            f"\t{LEFTOVER_MAX_INTEGRITY_DECL}\n"
            "protected:\n"
            f"\t{UPROPERTY_VISIBLE_READONLY}\n"
            f"\t{LOCKED_DECL}\n"
            "private:\n"
            "\tfloat HiddenIntegrity = 140.f;\n"
            "};\n"
        )
        section = spec_section(mixed)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertNotIn("HiddenIntegrity", section)
        self.assertNotIn(STOP_BEFORE_PRIVATE, section)
        self.assertNotIn("MaxIntegrity", section)

    def test_does_not_parse_leftover_apache_ufunction_decls(self) -> None:
        header = origin_main_header()
        public = public_section(header)
        section = spec_section(header)
        claimed = claimed_field_window(header)
        self.assertIn("UFUNCTION", public)
        self.assertNotIn("UFUNCTION", section)
        self.assertNotIn("UFUNCTION", claimed)
        self.assertNotIn("UFUNCTION", LOCKED_DECL)
        for name in leftover_ufunction_names():
            self.assertIn(name, public)
            self.assertNotIn(name, section)
            self.assertNotIn(name, claimed)
            self.assertNotIn(name, LOCKED_DECL)
        self.assertIn(SET_SENSOR_VIEW, public)
        self.assertIn(GET_ROTOR_RPM, public)
        self.assertNotIn(SET_SENSOR_VIEW, claimed)
        self.assertNotIn(GET_ROTOR_RPM, claimed)

    def test_does_not_parse_leftover_protect_asset_integrity(self) -> None:
        self.assertNotEqual(CLASS_NAME, LEFTOVER_PROTECT_ASSET_CLASS)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_PROTECT_ASSET_DECL)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_MAX_INTEGRITY_DECL)
        self.assertNotEqual(
            UPROPERTY_VISIBLE_READONLY,
            LEFTOVER_PROTECT_ASSET_WRAP,
        )
        self.assertNotIn("= 140.f", LOCKED_DECL)
        self.assertNotIn("= 100.f", LOCKED_DECL)
        header = origin_main_header()
        section = spec_section(header)
        claimed = claimed_field_window(header)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, HEADER_PATH)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, section)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, claimed)
        self.assertNotIn("SkyguardProtectAsset.h", HEADER_PATH)
        with self.assertRaises(AssertionError):
            require_declaration(
                f"\t{LEFTOVER_PROTECT_ASSET_DECL}\n",
                LOCKED_DECL,
            )

    def test_does_not_parse_leftover_loadout_hull_integrity(self) -> None:
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_HULL_INTEGRITY)
        self.assertNotIn("HullIntegrity", LOCKED_DECL)
        self.assertIn("EyeMount", LOCKED_DECL)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, HEADER_PATH)
        header = origin_main_header()
        section = spec_section(header)
        claimed = claimed_field_window(header)
        self.assertNotIn("HullIntegrity", section)
        self.assertNotIn("HullIntegrity", claimed)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, section)
        with self.assertRaises(AssertionError):
            require_declaration(
                f"\t{LEFTOVER_HULL_INTEGRITY}\n",
                LOCKED_DECL,
            )

    def test_does_not_parse_leftover_arcade_look_or_guided_lock(self) -> None:
        self.assertNotEqual(HEADER_PATH, LEFTOVER_GUIDED_LOCK_HEADER)
        self.assertNotIn("ArcadeLook", HEADER_PATH)
        self.assertNotIn("GuidedLock", HEADER_PATH)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_ARCADE_LOOK_DECL)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_ARCADE_LOOK_ENABLED)
        header = origin_main_header()
        section = spec_section(header)
        claimed = claimed_field_window(header)
        self.assertNotIn(LEFTOVER_ARCADE_LOOK_CLASS, header)
        self.assertNotIn(LEFTOVER_GUIDED_LOCK_STRUCT, header)
        self.assertNotIn("bEnabled", claimed)
        self.assertNotIn("Contrast", claimed)
        for leftover in leftover_guided_lock_fields():
            self.assertNotIn(leftover, LOCKED_DECL)
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, claimed)
        for leftover in leftover_analog_feel_fields():
            self.assertNotIn(leftover, LOCKED_DECL)
            self.assertNotIn(leftover, section)

    def test_does_not_parse_neighbors(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = class_body(header)
        self.assertNotIn(LEFTOVER_THEATER_KIT_STRUCT, header)
        self.assertNotIn(LEFTOVER_THEATER_KIT_STRUCT, section)
        self.assertNotIn(STOP_BEFORE_SORTIE, header)
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, header)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, header)
        self.assertNotIn(leftover_retired_mount_class(), header)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, leaked)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, leaked)
        self.assertNotIn(LEFTOVER_CAMPAIGN_SPEC, leaked)
        self.assertNotIn(LEFTOVER_GUIDED_LOCK_STRUCT, leaked)
        self.assertNotIn(LEFTOVER_ARCADE_LOOK_CLASS, leaked)

    def test_declaration_does_not_invent_uproperty_on_locked_decl(self) -> None:
        self.assertIn("VisibleAnywhere", UPROPERTY_VISIBLE_READONLY)
        self.assertIn("BlueprintReadOnly", UPROPERTY_VISIBLE_READONLY)
        self.assertIn(
            'Category="Skyguard|Apache"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertNotIn(
            'Category="Skyguard|Arcade"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertNotIn("EditAnywhere", UPROPERTY_VISIBLE_READONLY)
        self.assertNotIn("BlueprintReadWrite", UPROPERTY_VISIBLE_READONLY)
        self.assertNotIn("MultiLine", UPROPERTY_VISIBLE_READONLY)
        self.assertNotIn("ClampMin", UPROPERTY_VISIBLE_READONLY)
        self.assertNotIn("ClampMax", UPROPERTY_VISIBLE_READONLY)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, LOCKED_DECL)
        for invented in INVENTED_DECL_TOKENS:
            self.assertNotIn(invented, LOCKED_DECL)

    def test_leftover_theater_kit_wrap_is_not_locked_wrap(self) -> None:
        self.assertNotEqual(
            UPROPERTY_VISIBLE_READONLY,
            LEFTOVER_THEATER_KIT_WRAP,
        )
        self.assertIn("VisibleAnywhere", LEFTOVER_THEATER_KIT_WRAP)
        self.assertIn("BlueprintReadOnly", LEFTOVER_THEATER_KIT_WRAP)
        self.assertIn(
            'Category="Skyguard|Theater"',
            LEFTOVER_THEATER_KIT_WRAP,
        )
        self.assertIn("VisibleAnywhere", UPROPERTY_VISIBLE_READONLY)
        self.assertIn("BlueprintReadOnly", UPROPERTY_VISIBLE_READONLY)
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertIn(
            'Category="Skyguard|Apache"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertEqual(LEFTOVER_THEATER_KIT_DECL, "FName WeatherIdentity;")
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_THEATER_KIT_DECL)
        self.assertNotIn("160.f", LOCKED_DECL)
        self.assertNotIn("WeatherIdentity", LOCKED_DECL)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        self.assertNotIn(".cpp", HEADER_PATH)
        self.assertTrue(HEADER_PATH.endswith(".h"))
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("SkyguardApacheAircraft.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardGuidedLockRules.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignTheaterKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardProtectAsset.h", HEADER_PATH)
        self.assertNotIn("SkyguardArcadeLookComponent.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipTypes.h", HEADER_PATH)
        self.assertEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardApacheAircraft.h",
        )

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
        claimed = claimed_field_window(header)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, claimed)
            self.assertNotIn(token, header)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "apache EyeMount field decl contract "
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
            "eye_mount_field_decl_contract.py"
        ))
        self.assertNotIn("SkyguardApacheAircraft.cpp", THIS_SCRIPT)
        self.assertIn(LEFTOVER_APACHE_EMPTY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_EMPTY_TESTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_EMPTY_CONTRACT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_HULL_COLLIDER, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_AIRCRAFT_ROOT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_GUNNER_MOUNT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_PILOT_MOUNT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_WEAPON_MOUNT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_SENSOR_TURRET, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_SENSOR_BALL, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_HELLFIRE_LEFT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_HELLFIRE_RIGHT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_SILHOUETTE_MESH, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_MOUNT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_CPG_FEEL, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_OWN_SHIP, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_PROTECT_MAX_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_PROTECT_CURRENT_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_HULL_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ARCADE_LOOK_ENABLED_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ARCADE_LOOK_CONTRAST_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_THEATER_KIT_WEATHER_IDENTITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_THEATER_KIT_ROOT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_CAMPAIGN_ROSTER_LOOKUP, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_MAX_INTEGRITY_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(SIBLING_CURRENT_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_SET_SENSOR_VIEW, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GET_ROTOR_RPM, LOCKED_SCRIPTS)

    def test_leftover_analogs_stay_locked(self) -> None:
        leftovers = (
            LEFTOVER_APACHE_EMPTY,
            LEFTOVER_APACHE_EMPTY_TESTS,
            LEFTOVER_APACHE_EMPTY_CONTRACT,
            LEFTOVER_APACHE_HULL_COLLIDER,
            LEFTOVER_APACHE_AIRCRAFT_ROOT,
            LEFTOVER_APACHE_GUNNER_MOUNT,
            LEFTOVER_APACHE_PILOT_MOUNT,
            LEFTOVER_APACHE_WEAPON_MOUNT,
            LEFTOVER_APACHE_SENSOR_TURRET,
            LEFTOVER_APACHE_SENSOR_BALL,
            LEFTOVER_APACHE_HELLFIRE_LEFT,
            LEFTOVER_APACHE_HELLFIRE_RIGHT,
            LEFTOVER_APACHE_SILHOUETTE_MESH,
            LEFTOVER_APACHE_MOUNT,
            LEFTOVER_APACHE_MOUNT_TESTS,
            LEFTOVER_APACHE_MOUNT_CONTRACT,
            LEFTOVER_APACHE_CPG_FEEL,
            LEFTOVER_APACHE_OWN_SHIP,
            LEFTOVER_APACHE_OWN_SHIP_TESTS,
            LEFTOVER_PROTECT_MAX_INTEGRITY,
            LEFTOVER_PROTECT_CURRENT_INTEGRITY,
            LEFTOVER_LOADOUT_HULL_INTEGRITY,
            LEFTOVER_ARCADE_LOOK_FAIL_CLOSED,
            LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_TESTS,
            LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_CONTRACT,
            LEFTOVER_ARCADE_LOOK_WORLD_MOOD,
            LEFTOVER_ARCADE_LOOK_ENABLED_SCRIPT,
            LEFTOVER_ARCADE_LOOK_CONTRAST_SCRIPT,
            LEFTOVER_THEATER_KIT_WEATHER_IDENTITY,
            LEFTOVER_THEATER_KIT_ROOT,
            LEFTOVER_THEATER_KIT_BULK,
            LEFTOVER_CAMPAIGN_ROSTER_LOOKUP,
            LEFTOVER_GUIDED_HELMET_LOCK,
            LEFTOVER_GUIDED_SENSOR_LOCK,
            LEFTOVER_GUIDED_HELMET_ACQUIRE,
            LEFTOVER_GUIDED_SENSOR_ACQUIRE,
            LEFTOVER_MAX_INTEGRITY_SCRIPT,
            SIBLING_CURRENT_SCRIPT,
            LEFTOVER_SET_SENSOR_VIEW,
            LEFTOVER_GET_ROTOR_RPM,
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

    def test_header_path_is_apache_aircraft_only(self) -> None:
        self.assertEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardApacheAircraft.h",
        )
        self.assertEqual(CLASS_NAME, "ASkyguardApacheAircraft")
        self.assertEqual(
            LOCKED_DECL,
            "TObjectPtr<USceneComponent> EyeMount;",
        )
        self.assertEqual(
            UPROPERTY_VISIBLE_READONLY,
            "UPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
            'Category="Skyguard|Apache")',
        )
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_AIRCRAFT_ROOT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_GUNNER_MOUNT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_PILOT_MOUNT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_WEAPON_MOUNT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SENSOR_TURRET)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SENSOR_BALL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_STATIC_MESH)
        self.assertNotIn("UStaticMeshComponent", LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, "FName WeatherIdentity;")
        self.assertNotEqual(
            UPROPERTY_VISIBLE_READONLY,
            "UPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
            'Category="Skyguard|Theater")',
        )
        self.assertNotIn("160.f", LOCKED_DECL)
        self.assertTrue(HEADER_PATH.endswith("SkyguardApacheAircraft.h"))
        self.assertNotIn("TheaterKit", HEADER_PATH)
        self.assertNotIn("ProtectAsset", HEADER_PATH)
        self.assertNotIn("ArcadeLook", HEADER_PATH)
        self.assertNotIn("GuidedLock", HEADER_PATH)
        self.assertNotIn("CampaignRoster", HEADER_PATH)

    def test_contract_is_target_field_declaration_only(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        claimed = claimed_field_window(header)
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertEqual(
            require_declaration(claimed, LOCKED_DECL),
            LOCKED_DECL,
        )
        locked_only = f"{LOCKED_DECL}\n"
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, locked_only)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, locked_only)
        for leftover in leftover_analog_feel_fields():
            self.assertNotIn(leftover, locked_only)
        for leftover in leftover_guided_lock_fields():
            self.assertNotIn(leftover, locked_only)
        self.assertNotIn("WeatherIdentity", locked_only)
        self.assertNotIn("HullIntegrity", locked_only)
        self.assertNotIn("MaxIntegrity", locked_only)
        self.assertNotIn("160.f", locked_only)
        self.assertNotIn("140.f", locked_only)
        self.assertNotIn('Category="Skyguard|Theater"', locked_only)
        self.assertNotIn("GENERATED_BODY", locked_only)
        self.assertNotIn("USTRUCT", locked_only)
        self.assertNotIn(SET_SENSOR_VIEW, locked_only)
        self.assertNotIn(GET_ROTOR_RPM, locked_only)
        self.assertNotIn(LEFTOVER_THEATER_KIT_STRUCT, locked_only)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, locked_only)
        self.assertNotIn(LEFTOVER_ARCADE_LOOK_CLASS, locked_only)
        self.assertNotIn(SIBLING_SILHOUETTE_MESH, claimed)
        self.assertNotIn(SIBLING_HULL_COLLIDER, claimed)
        self.assertNotIn(SIBLING_AIRCRAFT_ROOT, claimed)
        self.assertNotIn(SIBLING_GUNNER_MOUNT, claimed)
        self.assertNotIn(SIBLING_PILOT_MOUNT, claimed)
        self.assertNotIn(SIBLING_WEAPON_MOUNT, claimed)
        self.assertNotIn(SIBLING_SENSOR_TURRET, claimed)
        self.assertNotIn(SIBLING_SENSOR_BALL, claimed)
        self.assertNotIn(SIBLING_HELLFIRE_LEFT, claimed)
        self.assertNotIn(SIBLING_HELLFIRE_RIGHT, claimed)
        self.assertNotIn("UStaticMeshComponent", locked_only)
        self.assertNotIn(TARGET_WRONG_AIRCRAFT_ROOT, locked_only)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, locked_only)
            self.assertNotIn(leftover, section)


if __name__ == "__main__":
    unittest.main()
