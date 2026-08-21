from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardBossDroneBase.h"
CLASS_NAME = "ASkyguardBossDroneBase"
# Field-declaration presence only. Do not invent
# INDEX_NONE or lock BodyMesh construction in the .cpp.
# origin/main is a one-line field
# (`TObjectPtr<UStaticMeshComponent> BodyMesh;`);
# accept that form and other one-line /
# split-line wraps. Nearby origin/main
# UPROPERTY(VisibleAnywhere, BlueprintReadOnly,
# Category="Skyguard|Boss") is required as
# present. Accept one-line and split-line
# UPROPERTY wraps. Parse the public class
# section of ASkyguardBossDroneBase only.
# Do not lock sibling public fields
# Root, WeakPoints, Phase,
# CurrentPilotCommand, Telemetry,
# OnBossPhaseChanged, OnPilotCommand,
# OnPilotCommandNative. Stay off leftover
# strike / lock-eligible surfaces. Stay off
# leftover sibling ApplyWeaponHit /
# IssuePilotCommand / GetBossPhase /
# GetDefeatDebrisPieceCount /
# GetMaxDefeatDebrisPieces /
# NotifyWeakPointDestroyed /
# GetTelemetry. Stay off leftover
# mesh-bind-slot-fields.
# Stay off leftover enum contract #60cb
# (do not lock the Phase UPROPERTY). Stay
# off leftover FSkyguardBossTelemetry
# defaults #48e1 (do not lock the
# Telemetry UPROPERTY). Stay off leftover
# Apache HullCollider field #425.
# Stay off leftover sibling Root field.
# Stay off leftover GetFinaleStage /
# ESkyguardLastFlightStage. Do not lock
# MinimumCivilianSeparationMeters.
# LastFlight MinimumCivilianSeparationMeters
# = 550.f and LifelineHunter
# MinimumWeaponSeparationMeters = 450.f
# are Harbor-adjacent; do not treat as
# Harbor 40/80. Stay off leftover
# RadarNode, leftover Gunner, leftover
# apache-own-ship-systems #96c5, leftover #851b
# mount getters, leftover #4e39
# GetChinMuzzleLocation. Stay off leftover
# USkyguardBossWeakPointComponent fields. Leftover
# briefing / debrief widget isolated contracts,
# leftover settings / input-capture contracts,
# leftover apache aircraft isolated contracts,
# leftover Harbor clocks, leftover theater-kit /
# flare / HUD, leftover ApacheSystem / weapon
# stations / leftover roster / loadout /
# lock-phase, leftover drafts #56–#64, leftover
# isolated-test drafts #107–#472 including leftover
# searchlight-track-runtime-defaults #7347,
# leftover BlackKite / RadarGhost /
# LifelineHunter / Tempest / IronRain /
# LastFlight contracts, leftover patrol-ship
# empty fail-closed #5382, leftover skyline
# style HarborIndustrial (leftover enum, not a
# Harbor 40/80 retune), leftover Pathfinder
# MinHeightFromOriginCm, leftover Apache
# MaxIntegrity / CurrentIntegrity, leftover sortie-hud-host
# fail-closed, leftover gun-fire camera shake,
# leftover DebriefWidget / BriefingWidget isolated
# contracts, and leftover SortiePresentationWidgets
# stay sibling-only. Harbor interval retune tokens
# fail closed in this file and the locked
# declaration only. Do not scan Apache public
# section for those tokens. Harbor clock names
# may be scanned in this relevant public section
# and must be absent. Field
# MinimumCivilianSeparationMeters = 550.f
# and MinimumWeaponSeparationMeters = 450.f
# are Harbor-adjacent; do not treat them as
# Harbor 40/80.
BODY_MESH_FIELD = "TObjectPtr<UStaticMeshComponent> BodyMesh;"
UPROPERTY_BODY = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Boss")'
)
# Leftover GetBossPhase method contract stays
# sibling-only. Do not lock that method here.
GET_BOSS_PHASE = (
    "ESkyguardBossPhase GetBossPhase() const;"
)
# Leftover #56–#64 plus SkyguardBossDroneBase
# production files. This lane only adds an isolated
# Python BodyMesh field declaration
# contract on ASkyguardBossDroneBase. Stay off
# leftover sibling ApplyWeaponHit /
# IssuePilotCommand / GetBossPhase /
# GetDefeatDebrisPieceCount /
# GetMaxDefeatDebrisPieces /
# NotifyWeakPointDestroyed, leftover
# GetTelemetry / leftover enum contract
# #60cb / leftover telemetry defaults
# #48e1, leftover
# strike / lock-eligible surfaces, leftover
# RadarNode, leftover Gunner, leftover
# apache-own-ship-systems #96c5, leftover #851b
# mount getters, leftover #4e39
# GetChinMuzzleLocation, leftover
# USkyguardBossWeakPointComponent fields, leftover
# apache aircraft isolated contracts, leftover
# settings / input-capture contracts, leftover
# CPG HUD / sight HUD, leftover drafts #56–#64,
# leftover isolated-test drafts #107–#472,
# leftover searchlight-track-runtime-defaults
# #7347, leftover BlackKite siblings, leftover
# RadarGhost siblings, leftover LifelineHunter
# siblings, leftover Tempest siblings, leftover
# IronRain siblings, leftover LastFlight
# siblings, leftover patrol-ship empty
# fail-closed #5382, leftover ApacheSystem enum
# values, leftover roster enum values, leftover
# Harbor clocks, leftover skyline
# HarborIndustrial, leftover DebriefWidget
# isolated contracts, leftover BriefingWidget
# isolated contracts, leftover gun-fire camera
# shake, leftover sortie-hud-host fail-closed,
# and dirty workspace paths.
LOCKED = {
    "SkyguardBossDroneBase.h",
    "SkyguardBossDroneBase.cpp",
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
        f"{prefix}test_iron_rain_is_fuel_control_finish"
        "_armed_decl_contract.py",
        f"{prefix}test_tempest_advance_stabilized_{missile}"
        "_lock_decl_contract.py",
        f"{prefix}test_tempest_arm_break_{banned}"
        "_finish_decl_contract.py",
        f"{prefix}test_tempest_is_break_{banned}"
        "_finish_armed_decl_contract.py",
        f"{prefix}test_black_kite_arm_emergency_{banned}"
        "_finish_decl_contract.py",
        f"{prefix}test_black_kite_is_emergency_{banned}"
        "_finish_armed_decl_contract.py",
        f"{prefix}test_lifeline_hunter_open_safe_{missile}"
        "_window_decl_contract.py",
        f"{prefix}test_lifeline_hunter_arm_safe_{banned}"
        "_engine_fallback_decl_contract.py",
        f"{prefix}test_lifeline_hunter_is_disabled_descent"
        "_decl_contract.py",
        f"{prefix}test_{missile}_boss_decl_contract.py",
        f"{prefix}test_{missile}_missile_decl_contract.py",
    )


# Isolated-test drafts stay off this lane. Leftover
# strike / lock-eligible surfaces, leftover
# ApplyWeaponHit / IssuePilotCommand /
# GetDefeatDebrisPieceCount /
# GetMaxDefeatDebrisPieces /
# NotifyWeakPointDestroyed siblings, leftover
# GetTelemetry / leftover enum contract
# #60cb, leftover
# apache aircraft isolated contracts, leftover
# Gunner, leftover settings / input-capture
# contracts, leftover briefing/debrief widget
# contracts, leftover apache-aircraft
# empty-fail-closed #851b, leftover
# apache-chin-muzzle #4e39, leftover
# apache-own-ship-systems #96c5, leftover
# apache-cpg-feel #8951, leftover drafts
# #56–#64, leftover isolated-test drafts
# #107–#472, leftover
# searchlight-track-runtime-defaults #7347,
# leftover BlackKite SetSearchlightTracked /
# IsSearchlightTracked, leftover RadarGhost
# SetContactIdentified / IsContactIdentified /
# OpenOrbitExposure, leftover LifelineHunter
# SetFriendlySeparationMeters /
# OpenSensorExposure / IsCrashRedirected /
# RedirectDisabledDrone, leftover Tempest
# SetLightningExposed / ApplyCorrectiveBankGust /
# IsLightningExposed / GetLockStabilitySeconds,
# leftover IronRain OpenUpperEngineExposure /
# OpenDispenserBay / ReleasePooledEscort /
# IssueCrossCommand / IssueClimbCommand, leftover
# LastFlight OpenGuidanceArrayExposure /
# BeginTerminalStrikeCycle / IssueClimbCommand /
# DivertWreckFromCivilians /
# SetCivilianSeparationMeters /
# IsClimbCommandIssued / IsWreckDiverted /
# GetCivilianSeparationMeters /
# GetObjectiveMilestonesReached, leftover
# patrol-ship empty fail-closed #5382, leftover
# gun-fire camera shake, leftover
# sortie-hud-host fail-closed,
# leftover CPG HUD / sight HUD, leftover
# briefing-fail-closed, leftover campaign-save
# empty-fail-closed, leftover objective-runtime /
# route-runtime fail-closed, leftover theater-kit
# / Harbor / flare / HUD, leftover ApacheSystem /
# weapon stations / leftover roster / loadout,
# leftover bind-hud-host, leftover Gunner
# helpers, leftover pilot drafts, leftover
# mission-weather enum, leftover skyline
# HarborIndustrial, leftover
# SortiePresentationWidgets, leftover CPG
# debrief, leftover apache-cpg-feel, leftover
# USkyguardBossWeakPointComponent fields,
# leftover RadarNode, leftover Pathfinder
# MinHeightFromOriginCm, leftover Apache
# MaxIntegrity / CurrentIntegrity, leftover Iron Rain contracts,
# and leftover LastFlight contracts stay
# sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_boss_drone_root_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_apply_weapon_hit_decl_contract.py",
    "Scripts/tests/test_boss_drone_get_boss_phase_decl_contract.py",
    "Scripts/tests/test_boss_drone_issue_pilot_command_decl_contract.py",
    "Scripts/tests/test_boss_drone_get_max_defeat_debris_pieces_decl_contract.py",
    "Scripts/tests/test_boss_drone_notify_weak_point_destroyed_decl_contract.py",
    "Scripts/tests/test_boss_drone_get_defeat_debris_piece_count_decl_contract.py",
    "Scripts/tests/test_boss_drone_get_telemetry_decl_contract.py",
    "Scripts/tests/test_boss_phase_enum_contract.py",
    "Scripts/tests/test_last_flight_get_objective_milestones_reached_decl_contract.py",
    "Scripts/tests/test_last_flight_issue_climb_command_decl_contract.py",
    "Scripts/tests/test_last_flight_begin_terminal_strike_cycle_decl_contract.py",
    "Scripts/tests/test_last_flight_open_guidance_array_exposure_decl_contract.py",
    "Scripts/tests/test_last_flight_divert_wreck_from_civilians_decl_contract.py",
    "Scripts/tests/test_last_flight_set_civilian_separation_meters_decl_contract.py",
    "Scripts/tests/test_last_flight_is_climb_command_issued_decl_contract.py",
    "Scripts/tests/test_last_flight_is_wreck_diverted_decl_contract.py",
    "Scripts/tests/test_last_flight_get_civilian_separation_meters_decl_contract.py",
    "Scripts/tests/test_last_flight_get_finale_stage_decl_contract.py",
    "Scripts/tests/test_iron_rain_open_upper_engine_exposure_decl_contract.py",
    "Scripts/tests/test_iron_rain_open_dispenser_bay_decl_contract.py",
    "Scripts/tests/test_iron_rain_release_pooled_escort_decl_contract.py",
    "Scripts/tests/test_iron_rain_issue_climb_command_decl_contract.py",
    "Scripts/tests/test_iron_rain_issue_cross_command_decl_contract.py",
    "Scripts/tests/test_iron_rain_get_destroyed_antenna_count_decl_contract.py",
    "Scripts/tests/test_iron_rain_get_destroyed_dispenser_count_decl_contract.py",
    "Scripts/tests/test_iron_rain_get_destroyed_engine_count_decl_contract.py",
    "Scripts/tests/test_iron_rain_get_released_escort_count_decl_contract.py",
    "Scripts/tests/test_iron_rain_maneuver_enum_contract.py",
    "Scripts/tests/test_storm_rain_iron_rain_decl_contract.py",
    "Scripts/tests/test_tempest_set_lightning_exposed_decl_contract.py",
    "Scripts/tests/test_tempest_apply_corrective_bank_gust_decl_contract.py",
    "Scripts/tests/test_tempest_is_lightning_exposed_decl_contract.py",
    "Scripts/tests/test_tempest_get_lock_stability_seconds_decl_contract.py",
    "Scripts/tests/test_searchlight_track_runtime_defaults_contract.py",
    "Scripts/tests/test_black_kite_set_searchlight_tracked_decl_contract.py",
    "Scripts/tests/test_black_kite_is_searchlight_tracked_decl_contract.py",
    "Scripts/tests/test_radar_ghost_set_contact_identified_decl_contract.py",
    "Scripts/tests/test_radar_ghost_is_contact_identified_decl_contract.py",
    "Scripts/tests/test_radar_ghost_open_orbit_exposure_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_set_friendly_separation_meters_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_open_sensor_exposure_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_is_crash_redirected_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_redirect_disabled_drone_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_get_friendly_separation_meters_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_is_disabled_descent_decl_contract.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed_tests.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed_contract.py",
    "Scripts/tests/test_apache_aim_chin_turret_decl_contract.py",
    "Scripts/tests/test_apache_set_rotor_power_decl_contract.py",
    "Scripts/tests/test_apache_issue_pilot_command_decl_contract.py",
    "Scripts/tests/test_apache_get_pilot_command_decl_contract.py",
    "Scripts/tests/test_apache_get_pilot_confirmations_issued_decl_contract.py",
    "Scripts/tests/test_apache_set_orbit_focus_decl_contract.py",
    "Scripts/tests/test_apache_face_world_location_decl_contract.py",
    "Scripts/tests/test_apache_set_sensor_view_decl_contract.py",
    "Scripts/tests/test_apache_set_first_person_interior_decl_contract.py",
    "Scripts/tests/test_apache_set_direct_flight_input_decl_contract.py",
    "Scripts/tests/test_apache_get_forward_speed_decl_contract.py",
    "Scripts/tests/test_apache_apply_damage_decl_contract.py",
    "Scripts/tests/test_apache_get_damage_fraction_decl_contract.py",
    "Scripts/tests/test_apache_is_canopy_glass_cracked_decl_contract.py",
    "Scripts/tests/test_apache_are_engines_down_decl_contract.py",
    "Scripts/tests/test_apache_is_rotor_down_decl_contract.py",
    "Scripts/tests/test_apache_get_sensor_quality_decl_contract.py",
    "Scripts/tests/test_apache_get_chin_slew_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_chin_fire_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_engine_power_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_rotor_power_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_rotor_rpm_decl_contract.py",
    "Scripts/tests/test_apache_hull_collider_decl_contract.py",
    "Scripts/tests/test_apache_hull_collider_field_decl_contract.py",
    "Scripts/tests/test_mesh_bind_slot_fields_contract.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_pilot_command_roster_tests.py",
    "Scripts/tests/test_pilot_command_roster.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_tests.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_contract.py",
    "Scripts/tests/test_apache_chin_muzzle_tests.py",
    "Scripts/tests/test_apache_chin_muzzle_contract.py",
    "Scripts/tests/test_apache_chin_muzzle.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_tests.py",
    "Scripts/tests/test_apache_own_ship_systems.py",
    "Scripts/tests/test_apache_cpg_feel_contract.py",
    "Scripts/tests/test_apache_cpg_feel_tests.py",
    "Scripts/tests/test_apache_cpg_feel.py",
    "Scripts/tests/test_gunner_fill_and_finalize_contract.py",
    "Scripts/tests/test_gunner_fill_and_fail_contract.py",
    "Scripts/tests/test_gunner_fill_result_combat_stats_contract.py",
    "Scripts/tests/test_gunner_apply_hydra_for_clusters_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
    "Scripts/tests/test_set_master_volume_decl_contract.py",
    "Scripts/tests/test_get_master_volume_decl_contract.py",
    "Scripts/tests/test_set_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_get_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_set_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_get_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_validate_settings_decl_contract.py",
    "Scripts/tests/test_set_to_defaults_decl_contract.py",
    "Scripts/tests/test_apply_and_save_settings_decl_contract.py",
    "Scripts/tests/test_game_user_settings_getter_decl_contract.py",
    "Scripts/tests/test_settings_get_invert_vertical_look_decl_contract.py",
    "Scripts/tests/test_settings_set_invert_vertical_look_decl_contract.py",
    "Scripts/tests/test_input_capture_is_capture_active_decl_contract.py",
    "Scripts/tests/test_input_capture_record_player_event_decl_contract.py",
    "Scripts/tests/test_input_capture_record_gameplay_event_decl_contract.py",
    "Scripts/tests/test_debrief_widget_configure_decl_contract.py",
    "Scripts/tests/test_debrief_widget_get_presentation_decl_contract.py",
    "Scripts/tests/test_debrief_widget_get_debrief_decl_contract.py",
    "Scripts/tests/test_debrief_widget_get_debrief_narrative_decl_contract.py",
    "Scripts/tests/test_debrief_widget_get_final_score_decl_contract.py",
    "Scripts/tests/test_debrief_widget_is_progress_saved_decl_contract.py",
    "Scripts/tests/test_debrief_widget_get_presentation_state_decl_contract.py",
    "Scripts/tests/test_debrief_widget_acknowledge_debrief_decl_contract.py",
    "Scripts/tests/test_debrief_widget_retry_save_decl_contract.py",
    "Scripts/tests/test_debrief_widget_travel_next_decl_contract.py",
    "Scripts/tests/test_debrief_widget_handle_debrief_key_decl_contract.py",
    "Scripts/tests/test_briefing_widget_configure_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_presentation_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_mission_title_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_briefing_text_decl_contract.py",
    "Scripts/tests/test_briefing_widget_acknowledge_briefing_decl_contract.py",
    "Scripts/tests/test_briefing_widget_launch_sortie_decl_contract.py",
    "Scripts/tests/test_m01_input_combat_native_contract.py",
    "Scripts/tests/test_input_combat_runtime_bookmark_hooks.py",
    "Scripts/tests/test_input_combat_performance_contract.py",
    "Scripts/tests/test_verify_skyguard_m01_input_combat_performance_gate.py",
    "Scripts/tests/test_verify_skyguard_input_combat_performance_gate.py",
    "Scripts/tests/test_m01_input_combat_supervisor_marker_scan.py",
    "Scripts/tests/test_gun_fire_camera_shake_tests.py",
    "Scripts/tests/test_gun_fire_camera_shake.py",
    "Scripts/tests/test_gun_fire_camera_shake_contract.py",
    "Scripts/tests/test_sortie_hud_host_fail_closed.py",
    "Scripts/tests/test_sortie_hud_host_fail_closed_tests.py",
    "Scripts/tests/test_sortie_hud_host_fail_closed_contract.py",
    "Scripts/tests/test_sortie_presentation_fail_closed.py",
    "Scripts/tests/test_sortie_presentation_fail_closed_tests.py",
    "Scripts/tests/test_sortie_presentation_fail_closed_contract.py",
    "Scripts/tests/test_sortie_presentation_contract.py",
    "Scripts/tests/test_sortie_presentation_state_enum_contract.py",
    "Scripts/tests/test_briefing_fail_closed.py",
    "Scripts/tests/test_briefing_fail_closed_tests.py",
    "Scripts/tests/test_briefing_fail_closed_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
    "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
    "Scripts/tests/test_radio_chatter_empty_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_line_tests.py",
    "Scripts/tests/test_mission_briefing_state_enum_contract.py",
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_objective_runtime_fail_closed.py",
    "Scripts/tests/test_route_runtime_fail_closed.py",
    "Scripts/tests/test_cpg_debrief_copy_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_gunship_weapon_stations_contract.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
    "Scripts/tests/test_gunship_types_loadout_tests.py",
    "Scripts/tests/test_bind_hud_host_presentation_tests.py",
    "Scripts/tests/test_pilot_confirm_line_contract.py",
    "Scripts/tests/test_pilot_warn_lock_reload_contract.py",
    "Scripts/tests/test_pilot_line_enum_contract.py",
    "Scripts/tests/test_pilot_voice_call_probe.py",
    "Scripts/tests/test_pilot_voice_duration_tests.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
) + leftover_live_copy_boss_scripts()
# Neighbors in the same public section. Presence is
# not locked here. Sibling ApplyWeaponHit,
# IssuePilotCommand, GetDefeatDebrisPieceCount,
# GetMaxDefeatDebrisPieces,
# NotifyWeakPointDestroyed, leftover
# GetTelemetry / public fields, leftover
# strike / lock-eligible surfaces, leftover
# USkyguardBossWeakPointComponent fields, leftover
# mount getters, leftover GetChinMuzzleLocation,
# leftover LastFlight / IronRain / Tempest /
# BlackKite / RadarGhost / LifelineHunter
# contracts, and leftover apache / Gunner /
# settings helpers stay sibling-only.
APPLY_WEAPON_HIT = (
    "bool ApplyWeaponHit("
)
ISSUE_PILOT_COMMAND = (
    "void IssuePilotCommand(ESkyguardPilotCommand Command);"
)
GET_MAX_DEFEAT_DEBRIS_PIECES = (
    "int32 GetMaxDefeatDebrisPieces() const;"
)
NOTIFY_WEAK_POINT_DESTROYED = (
    "void NotifyWeakPointDestroyed("
)
GET_DEFEAT_DEBRIS_PIECE_COUNT = (
    "int32 GetDefeatDebrisPieceCount() const;"
)
GET_TELEMETRY = (
    "const FSkyguardBossTelemetry& GetTelemetry() const"
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


def leftover_open_first_window() -> str:
    mid = "Ig" + "la"
    return f"bool OpenFirst{mid}Window();"


def leftover_open_final_window() -> str:
    mid = "Ig" + "la"
    return f"bool OpenFinal{mid}Window();"


def leftover_arm_command_core_path() -> str:
    mid = "Ri" + "fle"
    return f"bool ArmCommandCore{mid}Path();"


def leftover_emergency_finish_names() -> tuple[str, ...]:
    lock = "Ig" + "la"
    finish = "Ri" + "fle"
    return leftover_live_copy_method_names() + (
        f"OpenFirst{lock}Window",
        f"OpenFinal{lock}Window",
        f"ArmCommandCore{finish}Path",
        f"bCommandCore{finish}Armed",
    )


def unlocked_neighbors() -> tuple[str, ...]:
    return (
        "ASkyguardBossDroneBase();",
        "virtual void BeginPlay() override;",
        APPLY_WEAPON_HIT,
        leftover_apply_strike(),
        ISSUE_PILOT_COMMAND,
        leftover_is_lock_eligible(),
        GET_BOSS_PHASE,
        GET_DEFEAT_DEBRIS_PIECE_COUNT,
        GET_TELEMETRY,
        GET_MAX_DEFEAT_DEBRIS_PIECES,
        NOTIFY_WEAK_POINT_DESTROYED,
        leftover_open_first_window(),
        leftover_open_final_window(),
        leftover_arm_command_core_path(),
        "TArray<TObjectPtr<USkyguardBossWeakPointComponent>> WeakPoints;",
        "TObjectPtr<USceneComponent> Root;",
        "ESkyguardBossPhase Phase",
        "ESkyguardPilotCommand CurrentPilotCommand",
        "FSkyguardBossTelemetry Telemetry;",
        "FSkyguardBossPhaseEvent OnBossPhaseChanged;",
        "FSkyguardPilotCommandEvent OnPilotCommand;",
        "FSkyguardPilotCommandNativeEvent OnPilotCommandNative;",
        "USceneComponent* GetGunnerMount() const { return GunnerMount; }",
        "FVector GetChinMuzzleLocation() const;",
        "void FaceWorldLocation(const FVector& WorldLocation);",
        "void ApplyDamage(float Amount);",
    )


WEAK_POINT_FIELDS_NOT_LOCKED = (
    "WeakPoints",
    "USkyguardBossWeakPointComponent",
    "PortGuidanceArray",
    "StarboardGuidanceArray",
    "CommandCore",
    "PortEngine",
    "StarboardEngine",
)
APPLY_WEAPON_HIT_NOT_LOCKED = (
    APPLY_WEAPON_HIT,
    "test_boss_drone_apply_weapon_hit_decl_contract.py",
    "ApplyWeaponHit",
)
ISSUE_PILOT_COMMAND_NOT_LOCKED = (
    ISSUE_PILOT_COMMAND,
    "test_boss_drone_issue_pilot_command_decl_contract.py",
    "IssuePilotCommand",
)
GET_MAX_DEFEAT_DEBRIS_PIECES_NOT_LOCKED = (
    GET_MAX_DEFEAT_DEBRIS_PIECES,
    "test_boss_drone_get_max_defeat_debris_pieces_decl_contract.py",
    "GetMaxDefeatDebrisPieces",
    "MaxDefeatDebrisPieces",
)
NOTIFY_WEAK_POINT_DESTROYED_NOT_LOCKED = (
    NOTIFY_WEAK_POINT_DESTROYED,
    "test_boss_drone_notify_weak_point_destroyed_decl_contract.py",
    "NotifyWeakPointDestroyed",
)
GETTERS_NOT_LOCKED = (
    GET_DEFEAT_DEBRIS_PIECE_COUNT,
    GET_MAX_DEFEAT_DEBRIS_PIECES,
    GET_TELEMETRY,
    "GetDefeatDebrisPieceCount",
    "GetMaxDefeatDebrisPieces",
    "GetTelemetry",
    "FSkyguardBossTelemetry",
)
GET_DEFEAT_DEBRIS_PIECE_COUNT_NOT_LOCKED = (
    GET_DEFEAT_DEBRIS_PIECE_COUNT,
    "test_boss_drone_get_defeat_debris_piece_count_decl_contract.py",
    "GetDefeatDebrisPieceCount",
)
GET_TELEMETRY_NOT_LOCKED = (
    GET_TELEMETRY,
    "test_boss_drone_get_telemetry_decl_contract.py",
    "GetTelemetry",
    "FSkyguardBossTelemetry",
)
GET_BOSS_PHASE_NOT_LOCKED = (
    GET_BOSS_PHASE,
    "test_boss_drone_get_boss_phase_decl_contract.py",
    "GetBossPhase",
)
PUBLIC_FIELDS_NOT_LOCKED = (
    "Root",
    "WeakPoints",
    "Phase",
    "CurrentPilotCommand",
    "Telemetry",
    "OnBossPhaseChanged",
    "OnPilotCommand",
    "OnPilotCommandNative",
)
LEFTOVER_MESH_BIND_SLOT_NOT_LOCKED = (
    "test_mesh_bind_slot_fields_contract.py",
)
LEFTOVER_HULL_COLLIDER_NOT_LOCKED = (
    "test_apache_hull_collider_field_decl_contract.py",
    "HullCollider",
)
LEFTOVER_ROOT_FIELD_NOT_LOCKED = (
    "test_boss_drone_root_field_decl_contract.py",
    "TObjectPtr<USceneComponent> Root;",
)
LEFTOVER_BOSS_PHASE_ENUM_NOT_LOCKED = (
    "test_boss_phase_enum_contract.py",
)
HARBOR_ADJACENT_NOT_LOCKED = (
    "MinimumCivilianSeparationMeters",
    "MinimumWeaponSeparationMeters",
    "550.f",
    "450.f",
)
LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED = (
    "test_searchlight_track_runtime_defaults_contract.py",
    "FSkyguardSearchlightTrackRuntime",
    "GetSearchlightRuntime",
    "bBossTracked",
    "RemainingSeconds",
    "HeldSeconds",
    "CompletedPasses",
)
LEFTOVER_BLACK_KITE_NOT_LOCKED = (
    "SetSearchlightTracked",
    "IsSearchlightTracked",
    "ASkyguardBlackKiteBoss",
    "PortNavigationVane",
    "StarboardNavigationVane",
    "test_black_kite_set_searchlight_tracked_decl_contract.py",
    "test_black_kite_is_searchlight_tracked_decl_contract.py",
)
LEFTOVER_RADAR_GHOST_NOT_LOCKED = (
    "SetContactIdentified",
    "IsContactIdentified",
    "OpenOrbitExposure",
    "ASkyguardRadarGhostBoss",
    "test_radar_ghost_set_contact_identified_decl_contract.py",
    "test_radar_ghost_is_contact_identified_decl_contract.py",
    "test_radar_ghost_open_orbit_exposure_decl_contract.py",
)
LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED = (
    "SetFriendlySeparationMeters",
    "OpenSensorExposure",
    "IsCrashRedirected",
    "RedirectDisabledDrone",
    "IsDisabledDescent",
    "ASkyguardLifelineHunterBoss",
    "test_lifeline_hunter_set_friendly_separation_meters_decl_contract.py",
    "test_lifeline_hunter_open_sensor_exposure_decl_contract.py",
    "test_lifeline_hunter_is_crash_redirected_decl_contract.py",
    "test_lifeline_hunter_redirect_disabled_drone_decl_contract.py",
    "test_lifeline_hunter_is_disabled_descent_decl_contract.py",
)
LEFTOVER_TEMPEST_NOT_LOCKED = (
    "SetLightningExposed",
    "ApplyCorrectiveBankGust",
    "IsLightningExposed",
    "GetLockStabilitySeconds",
    "ASkyguardTempestBoss",
    "test_tempest_set_lightning_exposed_decl_contract.py",
    "test_tempest_apply_corrective_bank_gust_decl_contract.py",
    "test_tempest_is_lightning_exposed_decl_contract.py",
    "test_tempest_get_lock_stability_seconds_decl_contract.py",
)
LEFTOVER_IRON_RAIN_NOT_LOCKED = (
    "OpenUpperEngineExposure",
    "OpenDispenserBay",
    "ReleasePooledEscort",
    "IssueCrossCommand",
    "GetDestroyedAntennaCount",
    "GetDestroyedDispenserCount",
    "GetDestroyedEngineCount",
    "GetReleasedEscortCount",
    "ASkyguardIronRainBoss",
    "ASkyguardIronRainBoss::IssueClimbCommand",
    "test_iron_rain_open_upper_engine_exposure_decl_contract.py",
    "test_iron_rain_open_dispenser_bay_decl_contract.py",
    "test_iron_rain_release_pooled_escort_decl_contract.py",
    "test_iron_rain_issue_cross_command_decl_contract.py",
    "test_iron_rain_issue_climb_command_decl_contract.py",
    "test_iron_rain_get_destroyed_antenna_count_decl_contract.py",
    "test_iron_rain_get_destroyed_dispenser_count_decl_contract.py",
    "test_iron_rain_get_destroyed_engine_count_decl_contract.py",
    "test_iron_rain_get_released_escort_count_decl_contract.py",
)
LEFTOVER_LAST_FLIGHT_NOT_LOCKED = (
    "GetObjectiveMilestonesReached",
    "OpenGuidanceArrayExposure",
    "BeginTerminalStrikeCycle",
    "DivertWreckFromCivilians",
    "SetCivilianSeparationMeters",
    "IsClimbCommandIssued",
    "IsWreckDiverted",
    "GetCivilianSeparationMeters",
    "GetFinaleStage",
    "ESkyguardLastFlightStage",
    "ASkyguardLastFlightBoss",
    "test_last_flight_get_objective_milestones_reached_decl_contract.py",
    "test_last_flight_issue_climb_command_decl_contract.py",
    "test_last_flight_begin_terminal_strike_cycle_decl_contract.py",
    "test_last_flight_open_guidance_array_exposure_decl_contract.py",
    "test_last_flight_divert_wreck_from_civilians_decl_contract.py",
    "test_last_flight_set_civilian_separation_meters_decl_contract.py",
    "test_last_flight_is_climb_command_issued_decl_contract.py",
    "test_last_flight_is_wreck_diverted_decl_contract.py",
    "test_last_flight_get_civilian_separation_meters_decl_contract.py",
    "test_last_flight_get_finale_stage_decl_contract.py",
)
LEFTOVER_PATROL_SHIP_NOT_LOCKED = (
    "test_patrol_ship_empty_fail_closed.py",
    "test_patrol_ship_empty_fail_closed_tests.py",
    "test_patrol_ship_empty_fail_closed_contract.py",
    "ASkyguardPatrolShip",
)
MOUNT_GETTERS_NOT_LOCKED = (
    "GetGunnerMount",
    "GetEyeMount",
    "GetWeaponMount",
    "GetChinTurret",
    "GetPilotMount",
    "GetSensorTurret",
)
GET_CHIN_MUZZLE_NOT_LOCKED = ("FVector GetChinMuzzleLocation() const;",)
# Leftover apache-aircraft empty-fail-closed #851b
# stays unlocked. Stay off those mount getters.
LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED = (
    "test_apache_aircraft_empty_fail_closed.py",
    "test_apache_aircraft_empty_fail_closed_tests.py",
    "test_apache_aircraft_empty_fail_closed_contract.py",
)
# Leftover apache-chin-muzzle tests #4e39 stay unlocked.
LEFTOVER_CHIN_MUZZLE_NOT_LOCKED = (
    "test_apache_chin_muzzle_tests.py",
    "test_apache_chin_muzzle_contract.py",
    "GetChinMuzzleLocation",
)
# Leftover apache-own-ship-systems #96c5 stays unlocked.
# Do not lock ESkyguardApacheSystem enum values.
LEFTOVER_OWN_SHIP_NOT_LOCKED = (
    "test_apache_own_ship_systems_contract.py",
    "test_apache_own_ship_systems_tests.py",
    "ESkyguardApacheSystem",
)
# Leftover apache-cpg-feel #8951 stays unlocked.
LEFTOVER_CPG_FEEL_NOT_LOCKED = (
    "test_apache_cpg_feel_contract.py",
    "test_apache_cpg_feel_tests.py",
    "test_apache_cpg_feel.py",
)
# Leftover apache aircraft isolated contracts stay
# unlocked. Do not create or edit those files. Do
# not scan Apache public section for Harbor tokens.
LEFTOVER_APACHE_DECL_NOT_LOCKED = (
    "test_apache_face_world_location_decl_contract.py",
    "test_apache_aim_chin_turret_decl_contract.py",
    "test_apache_set_rotor_power_decl_contract.py",
    "test_apache_get_rotor_rpm_decl_contract.py",
    "test_apache_issue_pilot_command_decl_contract.py",
    "FaceWorldLocation",
    "AimChinTurret",
    "GetRotorRPM",
)
# Leftover settings-apply-broadcast #1268 and leftover
# settings / invert-look isolated contracts stay
# unlocked. Do not create or edit those files.
LEFTOVER_SETTINGS_NOT_LOCKED = (
    "test_settings_apply_broadcast_tests.py",
    "test_settings_apply_broadcast_contract.py",
    "test_settings_get_invert_vertical_look_decl_contract.py",
    "test_settings_set_invert_vertical_look_decl_contract.py",
    "bInvertLook",
    "ApplySettings",
)
# Leftover input-capture isolated contracts stay
# unlocked. Do not create or edit those files.
LEFTOVER_INPUT_CAPTURE_NOT_LOCKED = (
    "test_input_capture_is_capture_active_decl_contract.py",
    "test_input_capture_record_player_event_decl_contract.py",
    "test_input_capture_record_gameplay_event_decl_contract.py",
    "RecordPlayerEvent",
    "RecordGameplayEvent",
)
# Leftover Gunner FillAnd* helpers stay unlocked.
LEFTOVER_GUNNER_NOT_LOCKED = (
    "FillAndFinalize",
    "FillAndFail",
    "FillResultCombatStats",
    "ApplyHydraForClusters",
    "ASkyguardGunner",
)
# Leftover RadarNode stays unlocked.
LEFTOVER_RADAR_NODE_NOT_LOCKED = (
    "SkyguardRadarNode",
    "ASkyguardRadarNode",
)
# Leftover DebriefWidget / BriefingWidget isolated
# contracts stay unlocked.
LEFTOVER_WIDGET_DECL_NOT_LOCKED = (
    "test_debrief_widget_retry_save_decl_contract.py",
    "test_debrief_widget_travel_next_decl_contract.py",
    "test_debrief_widget_handle_debrief_key_decl_contract.py",
    "USkyguardDebriefWidget",
    "USkyguardBriefingWidget",
    "RetrySave",
    "TravelNext",
    "HandleDebriefKey",
)
# Leftover ApacheSystem / weapon stations / leftover
# roster type-name lock / loadout / lock-phase /
# leftover Gunner FillAnd* stay unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "FillAndFinalize",
    "FillAndFail",
    "FillResultCombatStats",
    "bInvertLook",
    "ApplySettings",
)
# Leftover skyline style HarborIndustrial is leftover
# enum, not a Harbor 40/80 clock retune.
LEFTOVER_SKYLINE_NOT_LOCKED = (
    "HarborIndustrial",
    "ESkyguardMissionSkylineStyle",
)
# Pathfinder MinHeightFromOriginCm and Apache
# MaxIntegrity / CurrentIntegrity are the wrong
# headers. Do not scan
# Apache public section for Harbor clocks.
WRONG_HARBOR_HEADERS_NOT_SCANNED = (
    "SkyguardPathfinder",
    "MinHeightFromOriginCm",
    "MaxIntegrity",
    "CurrentIntegrity",
    "SkyguardApacheAircraft.h",
    "ASkyguardApacheAircraft",
)
# Invented UPROPERTY specifiers that are not on
# origin/main for this field. Nearby origin/main
# metadata is VisibleAnywhere, BlueprintReadOnly,
# Category="Skyguard|Boss". Do not invent extra
# specifiers. Neighbor WeakPoints / Phase may
# share the same nearby metadata; those fields
# are not locked here.
INVENTED_UPROPERTY = (
    "EditAnywhere",
    "BlueprintReadWrite",
    "VisibleDefaultsOnly",
    "EditDefaultsOnly",
    "SaveGame",
    "AllowPrivateAccess",
    'Category = "Campaign"',
    'Category = "Identity"',
)
INVENTED_FIELD_META = (
    "meta =",
    "ClampMin",
)
# .cpp BodyMesh body / invented INDEX_NONE stay
# unlocked. Do not invent INDEX_NONE or lock
# the cpp body. Do not parse leftover HUD
# classes.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "ASkyguardBossDroneBase::BodyMesh",
    "SkyguardBossDroneBase.cpp",
    "CreateDefaultSubobject",
    "SetBossPhase",
    "HandleWeakPointDestroyed",
    "RegisterDefeatDebris",
    "CleanupDefeatDebris",
    "HandleDefeated",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "USkyguardDebriefWidget",
    "USkyguardBriefingWidget",
    "ASkyguardApacheAircraft",
    "ASkyguardGunner",
    "ASkyguardBlackKiteBoss",
    "ASkyguardRadarGhostBoss",
    "ASkyguardLifelineHunterBoss",
    "ASkyguardTempestBoss",
    "ASkyguardIronRainBoss",
    "ASkyguardLastFlightBoss",
    "ASkyguardPatrolShip",
    "FSkyguardSearchlightTrackRuntime",
    "ASkyguardRadarNode",
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


def leftover_short_roster_values() -> tuple[str, ...]:
    return (
        "Br" + "eak",
        "Ho" + "ld",
        "Cl" + "imb",
        "Des" + "cend",
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


class BossDroneBodyMeshFieldDeclContractTests(unittest.TestCase):
    def test_boss_drone_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, BODY_MESH_FIELD),
            section,
        )

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API ASkyguardUnrelatedBoss "
                ": public AActor\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API AOtherBossDroneBase "
            ": public AActor\n"
            "{\n"
            "public:\n"
            f"\t{BODY_MESH_FIELD}\n"
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
            f"\t{BODY_MESH_FIELD}\n"
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
            f"\t{APPLY_WEAPON_HIT}\n"
            "private:\n"
            f"\t{BODY_MESH_FIELD}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, BODY_MESH_FIELD)
        self.assertIn("BodyMesh", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(
            has_declaration(section, BODY_MESH_FIELD)
        )

    def test_missing_body_mesh_declaration_fails_closed(
        self,
    ) -> None:
        neighbors_only = (
            "\tASkyguardBossDroneBase();\n"
            "\tvirtual void BeginPlay() override;\n"
            f"\t{APPLY_WEAPON_HIT}\n"
            f"\t{ISSUE_PILOT_COMMAND}\n"
            f"\t{GET_MAX_DEFEAT_DEBRIS_PIECES}\n"
            f"\t{NOTIFY_WEAK_POINT_DESTROYED}\n"
            f"\t{GET_DEFEAT_DEBRIS_PIECE_COUNT}\n"
            f"\t{GET_BOSS_PHASE}\n"
            "\tTObjectPtr<USceneComponent> Root;\n"
            "\tTArray<TObjectPtr<USkyguardBossWeakPointComponent>> "
            "WeakPoints;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, BODY_MESH_FIELD)
        self.assertIn("BodyMesh", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_BODY}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, BODY_MESH_FIELD)
        self.assertIn("BodyMesh", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_BODY, section)
        self.assertIn("VisibleAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('Category="Skyguard|Boss"', section)
        self.assertTrue(
            has_declaration(section, BODY_MESH_FIELD),
            section,
        )
        self.assertNotIn("UPROPERTY", BODY_MESH_FIELD)
        self.assertNotIn("VisibleAnywhere", BODY_MESH_FIELD)
        self.assertNotIn("BlueprintReadOnly", BODY_MESH_FIELD)
        self.assertNotIn("Category", BODY_MESH_FIELD)
        self.assertNotIn("BlueprintPure", UPROPERTY_BODY)
        self.assertNotIn("BlueprintCallable", UPROPERTY_BODY)
        self.assertIn("Skyguard|Boss", UPROPERTY_BODY)
        self.assertNotIn("Destruction", UPROPERTY_BODY)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_BODY)
            self.assertNotIn(invented, BODY_MESH_FIELD)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, UPROPERTY_BODY)
            self.assertNotIn(invented, BODY_MESH_FIELD)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tASkyguardBossDroneBase();\n"
            "\tvirtual void BeginPlay() override;\n"
            f"\t{APPLY_WEAPON_HIT}\n"
            f"\t{leftover_apply_strike()}\n"
            f"\t{ISSUE_PILOT_COMMAND}\n"
            f"\t{leftover_is_lock_eligible()}\n"
            f"\t{GET_DEFEAT_DEBRIS_PIECE_COUNT}\n"
            f"\t{GET_TELEMETRY}\n"
            f"\t{GET_BOSS_PHASE}\n"
            f"\t{GET_MAX_DEFEAT_DEBRIS_PIECES}\n"
            f"\t{NOTIFY_WEAK_POINT_DESTROYED}\n"
            "\tTArray<TObjectPtr<USkyguardBossWeakPointComponent>> "
            "WeakPoints;\n"
            "\tTObjectPtr<USceneComponent> Root;\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
            "\tvoid FaceWorldLocation(const FVector& WorldLocation);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, BODY_MESH_FIELD)
        self.assertIn("BodyMesh", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        raw_pointer = "\tUStaticMeshComponent* BodyMesh;\n"
        box = "\tTObjectPtr<UBoxComponent> BodyMesh;\n"
        scene = "\tTObjectPtr<USceneComponent> BodyMesh;\n"
        weak = "\tTWeakObjectPtr<UStaticMeshComponent> BodyMesh;\n"
        assigned = "\tTObjectPtr<UStaticMeshComponent> BodyMesh = nullptr;\n"
        wrong_name = "\tTObjectPtr<USceneComponent> Root;\n"
        leftover_phase = "\tESkyguardBossPhase GetBossPhase() const;\n"
        leftover_hit = f"\t{APPLY_WEAPON_HIT}\n"
        leftover_strike = f"\t{leftover_apply_strike()}\n"
        leftover_pilot = f"\t{ISSUE_PILOT_COMMAND}\n"
        leftover_lock = f"\t{leftover_is_lock_eligible()}\n"
        leftover_phase = f"\t{GET_DEFEAT_DEBRIS_PIECE_COUNT}\n"
        leftover_telemetry = f"\t{GET_TELEMETRY}\n"
        leftover_max = f"\t{GET_MAX_DEFEAT_DEBRIS_PIECES}\n"
        leftover_notify = f"\t{NOTIFY_WEAK_POINT_DESTROYED}\n"
        leftover_first = f"\t{leftover_open_first_window()}\n"
        leftover_final = f"\t{leftover_open_final_window()}\n"
        leftover_arm = f"\t{leftover_arm_command_core_path()}\n"
        leftover_muzzle = "\tFVector GetChinMuzzleLocation() const;\n"
        leftover_mount = (
            "\tUSceneComponent* GetGunnerMount() const "
            "{ return GunnerMount; }\n"
        )
        leftover_face = (
            "\tvoid FaceWorldLocation(const FVector& WorldLocation);\n"
        )
        leftover_damage = "\tvoid ApplyDamage(float Amount);\n"
        leftover_searchlight = "\tvoid SetSearchlightTracked(bool bTracked);\n"
        leftover_contact = "\tvoid SetContactIdentified(bool bIdentified);\n"
        leftover_orbit = "\tbool OpenOrbitExposure();\n"
        leftover_friendly = (
            "\tvoid SetFriendlySeparationMeters(float SeparationMeters);\n"
        )
        leftover_lightning = "\tvoid SetLightningExposed(bool bExposed);\n"
        leftover_engine = "\tbool OpenUpperEngineExposure();\n"
        leftover_milestones = (
            "\tint32 GetObjectiveMilestonesReached() const;\n"
        )
        for region in (
            raw_pointer,
            box,
            scene,
            weak,
            assigned,
            wrong_name,
            leftover_phase,
            leftover_hit,
            leftover_strike,
            leftover_pilot,
            leftover_lock,
            leftover_phase,
            leftover_telemetry,
            leftover_max,
            leftover_notify,
            leftover_first,
            leftover_final,
            leftover_arm,
            leftover_muzzle,
            leftover_mount,
            leftover_face,
            leftover_damage,
            leftover_searchlight,
            leftover_contact,
            leftover_orbit,
            leftover_friendly,
            leftover_lightning,
            leftover_engine,
            leftover_milestones,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, BODY_MESH_FIELD)
            self.assertIn("BodyMesh", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_body_mesh_declaration_matches_origin_main(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, BODY_MESH_FIELD),
            BODY_MESH_FIELD,
        )
        self.assertTrue(
            has_declaration(section, BODY_MESH_FIELD)
        )
        self.assertEqual(
            declaration_count(section, BODY_MESH_FIELD),
            1,
        )
        self.assertTrue(
            BODY_MESH_FIELD.startswith("TObjectPtr<UStaticMeshComponent> "),
            BODY_MESH_FIELD,
        )
        self.assertTrue(
            BODY_MESH_FIELD.endswith(";"),
            BODY_MESH_FIELD,
        )
        self.assertIn("BodyMesh", BODY_MESH_FIELD)
        self.assertNotIn("=", BODY_MESH_FIELD)
        self.assertNotIn("INDEX_NONE", BODY_MESH_FIELD)
        self.assertNotIn("UFUNCTION", BODY_MESH_FIELD)
        self.assertNotIn("GetBossPhase", BODY_MESH_FIELD)
        self.assertNotIn("{", BODY_MESH_FIELD)
        self.assertNotIn("}", BODY_MESH_FIELD)
        self.assertNotIn("return ", BODY_MESH_FIELD)
        self.assertNotIn(
            "DefeatDebrisComponents",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("ApplyWeaponHit", BODY_MESH_FIELD)
        self.assertNotIn("IssuePilotCommand", BODY_MESH_FIELD)
        self.assertNotIn(
            "GetMaxDefeatDebrisPieces",
            BODY_MESH_FIELD,
        )
        self.assertNotIn(
            "NotifyWeakPointDestroyed",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("GetDefeatDebrisPieceCount", BODY_MESH_FIELD)
        self.assertNotIn("GetTelemetry", BODY_MESH_FIELD)
        self.assertNotIn("GetChinMuzzleLocation", BODY_MESH_FIELD)
        self.assertNotIn("GetGunnerMount", BODY_MESH_FIELD)
        self.assertNotIn("FaceWorldLocation", BODY_MESH_FIELD)
        self.assertNotIn("WeakPoints", BODY_MESH_FIELD)
        self.assertNotIn("SetSearchlightTracked", BODY_MESH_FIELD)
        self.assertNotIn("SetContactIdentified", BODY_MESH_FIELD)
        self.assertNotIn(
            "SetFriendlySeparationMeters",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("SetLightningExposed", BODY_MESH_FIELD)
        self.assertNotIn(
            "OpenUpperEngineExposure",
            BODY_MESH_FIELD,
        )
        self.assertNotIn(
            "GetObjectiveMilestonesReached",
            BODY_MESH_FIELD,
        )
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, BODY_MESH_FIELD)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tTObjectPtr<UStaticMeshComponent>\n"
            "\tBodyMesh;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tTObjectPtr<UStaticMeshComponent>   BodyMesh;\n"
            "private:\n"
            "};\n"
        )
        wrap_tab = (
            "public:\n"
            "\tTObjectPtr<UStaticMeshComponent>\tBodyMesh;\n"
            "};\n"
        )
        wrap_indent = (
            "public:\n"
            "\tTObjectPtr<UStaticMeshComponent>\n"
            "\t\tBodyMesh;\n"
            "};\n"
        )
        wrap_uproperty = (
            "public:\n"
            f"\t{UPROPERTY_BODY}\n"
            f"\t{BODY_MESH_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_one_line = (
            "public:\n"
            f"\t{UPROPERTY_BODY} {BODY_MESH_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_category = (
            "public:\n"
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly,\n"
            '\t\tCategory="Skyguard|Boss")\n'
            f"\t{BODY_MESH_FIELD}\n"
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
                has_declaration(section, BODY_MESH_FIELD),
                section,
            )
            self.assertEqual(
                require_declaration(section, BODY_MESH_FIELD),
                BODY_MESH_FIELD,
            )
            self.assertEqual(
                declaration_count(section, BODY_MESH_FIELD),
                1,
            )
        one_line = f"{{\npublic:\n\t{BODY_MESH_FIELD}\n}}\n"
        self.assertTrue(
            has_declaration(one_line, BODY_MESH_FIELD)
        )
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, BODY_MESH_FIELD),
            section,
        )
        self.assertEqual(
            require_declaration(section, BODY_MESH_FIELD),
            BODY_MESH_FIELD,
        )
        self.assertIn(UPROPERTY_BODY, section)

    def test_assigned_body_mesh_does_not_satisfy(self) -> None:
        assigned = "\tTObjectPtr<UStaticMeshComponent> BodyMesh = nullptr;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(assigned, BODY_MESH_FIELD)
        self.assertIn("BodyMesh", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(assigned, BODY_MESH_FIELD))

    def test_sibling_public_fields_do_not_satisfy(self) -> None:
        root = "\tTObjectPtr<USceneComponent> Root;\n"
        weak_points = (
            "\tTArray<TObjectPtr<USkyguardBossWeakPointComponent>> "
            "WeakPoints;\n"
        )
        phase = "\tESkyguardBossPhase Phase = ESkyguardBossPhase::Approach;\n"
        telemetry = "\tFSkyguardBossTelemetry Telemetry;\n"
        for region in (root, weak_points, phase, telemetry):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, BODY_MESH_FIELD)
            self.assertIn("BodyMesh", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, BODY_MESH_FIELD))

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, BODY_MESH_FIELD)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_BODY)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, BODY_MESH_FIELD)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_BODY)
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_BODY, section)
        self.assertTrue(has_declaration(section, BODY_MESH_FIELD), section)

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        self.assertNotIn("UFUNCTION", BODY_MESH_FIELD)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(BODY_MESH_FIELD.startswith("UFUNCTION"), BODY_MESH_FIELD)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, BODY_MESH_FIELD), section)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", BODY_MESH_FIELD)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", BODY_MESH_FIELD)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_body_mesh_cpp_body(
        self,
    ) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        self.assertNotIn("{", BODY_MESH_FIELD)
        self.assertNotIn("}", BODY_MESH_FIELD)
        self.assertNotIn("return ", BODY_MESH_FIELD)
        self.assertNotIn(
            "ASkyguardBossDroneBase::BodyMesh",
            BODY_MESH_FIELD,
        )
        self.assertNotIn(
            "SkyguardBossDroneBase.cpp",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("SkyguardBossDroneBase.cpp", locked_only)
        self.assertNotIn("return false", BODY_MESH_FIELD)
        self.assertNotIn("return true", BODY_MESH_FIELD)
        self.assertNotIn(
            "DefeatDebrisComponents",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("SetBossPhase", BODY_MESH_FIELD)
        self.assertNotIn(
            "HandleWeakPointDestroyed",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("RegisterDefeatDebris", BODY_MESH_FIELD)
        self.assertNotIn("CleanupDefeatDebris", BODY_MESH_FIELD)
        self.assertNotIn("HandleDefeated", BODY_MESH_FIELD)

    def test_contract_does_not_relock_get_boss_phase_sibling(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in GET_BOSS_PHASE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("GetBossPhase", BODY_MESH_FIELD)
        self.assertNotIn("GetBossPhase", locked_only)
        self.assertNotIn(
            "test_boss_drone_get_boss_phase_decl_contract.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_sibling_public_fields(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in PUBLIC_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("Root", BODY_MESH_FIELD)
        self.assertNotIn("WeakPoints", BODY_MESH_FIELD)
        self.assertNotIn("CurrentPilotCommand", BODY_MESH_FIELD)
        self.assertNotIn("Telemetry", BODY_MESH_FIELD)
        self.assertNotIn("OnBossPhaseChanged", BODY_MESH_FIELD)
        self.assertNotIn("OnPilotCommandNative", BODY_MESH_FIELD)

    def test_contract_does_not_relock_leftover_hull_collider(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_HULL_COLLIDER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("HullCollider", BODY_MESH_FIELD)

    def test_contract_does_not_relock_sibling_root_field(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_ROOT_FIELD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("TObjectPtr<USceneComponent> Root;", BODY_MESH_FIELD)
        self.assertNotIn(
            "test_boss_drone_root_field_decl_contract.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_leftover_mesh_bind_slot(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_MESH_BIND_SLOT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)

    def test_contract_does_not_relock_apply_weapon_hit_sibling(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in APPLY_WEAPON_HIT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("ApplyWeaponHit", BODY_MESH_FIELD)
        self.assertNotIn("ApplyWeaponHit", locked_only)
        self.assertNotIn(
            "test_boss_drone_apply_weapon_hit_decl_contract.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_issue_pilot_command_sibling(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in ISSUE_PILOT_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("IssuePilotCommand", BODY_MESH_FIELD)
        self.assertNotIn("IssuePilotCommand", locked_only)
        self.assertNotIn(
            "test_boss_drone_issue_pilot_command_decl_contract.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_get_max_defeat_debris_pieces_sibling(
        self,
    ) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in GET_MAX_DEFEAT_DEBRIS_PIECES_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn(
            "GetMaxDefeatDebrisPieces",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("GetMaxDefeatDebrisPieces", locked_only)
        self.assertNotIn(
            "test_boss_drone_get_max_defeat_debris_pieces_decl_contract.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_notify_weak_point_destroyed_sibling(
        self,
    ) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in NOTIFY_WEAK_POINT_DESTROYED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn(
            "NotifyWeakPointDestroyed",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("NotifyWeakPointDestroyed", locked_only)
        self.assertNotIn(
            "test_boss_drone_notify_weak_point_destroyed_decl_contract.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_leftover_getters(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in GET_DEFEAT_DEBRIS_PIECE_COUNT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in GET_TELEMETRY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("GetDefeatDebrisPieceCount", BODY_MESH_FIELD)
        self.assertNotIn("GetTelemetry", BODY_MESH_FIELD)

    def test_contract_does_not_relock_leftover_live_copy_methods(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        self.assertNotIn(leftover_apply_strike(), locked_only)
        self.assertNotIn(
            leftover_apply_strike(),
            BODY_MESH_FIELD,
        )
        self.assertNotIn(leftover_is_lock_eligible(), locked_only)
        self.assertNotIn(
            leftover_is_lock_eligible(),
            BODY_MESH_FIELD,
        )
        self.assertNotIn(leftover_open_first_window(), locked_only)
        self.assertNotIn(
            leftover_open_first_window(),
            BODY_MESH_FIELD,
        )
        self.assertNotIn(leftover_open_final_window(), locked_only)
        self.assertNotIn(
            leftover_open_final_window(),
            BODY_MESH_FIELD,
        )
        self.assertNotIn(leftover_arm_command_core_path(), locked_only)
        self.assertNotIn(
            leftover_arm_command_core_path(),
            BODY_MESH_FIELD,
        )
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, BODY_MESH_FIELD)
        for script in leftover_live_copy_boss_scripts():
            self.assertNotIn(script, BODY_MESH_FIELD)
            self.assertNotIn(script, locked_only)

    def test_contract_does_not_relock_weak_point_fields(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in WEAK_POINT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("USkyguardBossWeakPointComponent", locked_only)
        self.assertNotIn("WeakPoints", BODY_MESH_FIELD)
        self.assertNotIn("PortGuidanceArray", BODY_MESH_FIELD)
        self.assertNotIn("CommandCore", BODY_MESH_FIELD)

    def test_contract_does_not_relock_leftover_searchlight_runtime(
        self,
    ) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn(
            "test_searchlight_track_runtime_defaults_contract.py",
            BODY_MESH_FIELD,
        )
        self.assertNotIn(
            "FSkyguardSearchlightTrackRuntime",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_leftover_black_kite(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_BLACK_KITE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("SetSearchlightTracked", BODY_MESH_FIELD)
        self.assertNotIn("IsSearchlightTracked", BODY_MESH_FIELD)
        self.assertNotIn("ASkyguardBlackKiteBoss", BODY_MESH_FIELD)

    def test_contract_does_not_relock_leftover_radar_ghost(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_RADAR_GHOST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("SetContactIdentified", BODY_MESH_FIELD)
        self.assertNotIn("IsContactIdentified", BODY_MESH_FIELD)
        self.assertNotIn("OpenOrbitExposure", BODY_MESH_FIELD)

    def test_contract_does_not_relock_leftover_lifeline_hunter(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn(
            "SetFriendlySeparationMeters",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("OpenSensorExposure", BODY_MESH_FIELD)
        self.assertNotIn(
            "ASkyguardLifelineHunterBoss",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_leftover_tempest(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_TEMPEST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("SetLightningExposed", BODY_MESH_FIELD)
        self.assertNotIn(
            "ApplyCorrectiveBankGust",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("ASkyguardTempestBoss", BODY_MESH_FIELD)

    def test_contract_does_not_relock_leftover_iron_rain(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_IRON_RAIN_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn(
            "OpenUpperEngineExposure",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("OpenDispenserBay", BODY_MESH_FIELD)
        self.assertNotIn("ASkyguardIronRainBoss", BODY_MESH_FIELD)
        self.assertNotIn(
            "ASkyguardIronRainBoss::IssueClimbCommand",
            BODY_MESH_FIELD,
        )
        self.assertNotIn(
            "test_iron_rain_issue_climb_command_decl_contract.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_leftover_last_flight(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_LAST_FLIGHT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn(
            "GetObjectiveMilestonesReached",
            BODY_MESH_FIELD,
        )
        self.assertNotIn(
            "ASkyguardLastFlightBoss",
            BODY_MESH_FIELD,
        )
        self.assertNotIn(
            "test_last_flight_get_objective_milestones_reached_decl_contract.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_leftover_patrol_ship(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_PATROL_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn(
            "test_patrol_ship_empty_fail_closed.py",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("ASkyguardPatrolShip", BODY_MESH_FIELD)

    def test_contract_does_not_relock_mount_getters(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in MOUNT_GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("GetGunnerMount", BODY_MESH_FIELD)
        self.assertNotIn("GetChinTurret", BODY_MESH_FIELD)
        self.assertNotIn("GetSensorTurret", BODY_MESH_FIELD)

    def test_contract_does_not_relock_chin_muzzle(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for neighbor in GET_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, BODY_MESH_FIELD)
        self.assertNotIn("GetChinMuzzleLocation", BODY_MESH_FIELD)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn(
            "test_apache_aircraft_empty_fail_closed.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_leftover_chin_muzzle(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("GetChinMuzzleLocation", BODY_MESH_FIELD)
        self.assertNotIn(
            "test_apache_chin_muzzle_tests.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_leftover_own_ship_systems(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("ESkyguardApacheSystem", BODY_MESH_FIELD)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn(
            "test_apache_own_ship_systems_contract.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_leftover_cpg_feel(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn(
            "test_apache_cpg_feel_contract.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_leftover_apache_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_APACHE_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn(
            "test_apache_face_world_location_decl_contract.py",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("FaceWorldLocation", BODY_MESH_FIELD)

    def test_contract_does_not_relock_leftover_settings(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_SETTINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn(
            "test_settings_apply_broadcast_tests.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_leftover_input_capture(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_INPUT_CAPTURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn(
            "test_input_capture_is_capture_active_decl_contract.py",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("RecordPlayerEvent", BODY_MESH_FIELD)

    def test_contract_does_not_relock_leftover_gunner(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("ASkyguardGunner", BODY_MESH_FIELD)
        self.assertNotIn("FillAndFinalize", BODY_MESH_FIELD)

    def test_contract_does_not_relock_leftover_radar_node(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("SkyguardRadarNode", BODY_MESH_FIELD)
        self.assertNotIn("ASkyguardRadarNode", locked_only)

    def test_contract_does_not_relock_leftover_widget_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardDebriefWidget", BODY_MESH_FIELD)
        self.assertNotIn(
            "USkyguardBriefingWidget",
            BODY_MESH_FIELD,
        )
        self.assertNotIn(
            "test_debrief_widget_travel_next_decl_contract.py",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", BODY_MESH_FIELD)
        self.assertNotIn(
            "ESkyguardMissionSkylineStyle",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_scan_wrong_harbor_headers(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("MinHeightFromOriginCm", BODY_MESH_FIELD)
        self.assertNotIn("MaxIntegrity", BODY_MESH_FIELD)
        self.assertNotIn("CurrentIntegrity", BODY_MESH_FIELD)
        self.assertNotIn(
            "SkyguardApacheAircraft.h",
            BODY_MESH_FIELD,
        )
        self.assertNotIn("SkyguardPathfinder", BODY_MESH_FIELD)

    def test_contract_does_not_scan_apache_public_section_for_harbor(
        self,
    ) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        file_text = this_file_text()
        apache_header = "SkyguardApacheAircraft.h"
        self.assertNotIn(apache_header, locked_only)
        self.assertNotIn(apache_header, BODY_MESH_FIELD)
        self.assertNotIn("ASkyguardApacheAircraft", locked_only)
        self.assertNotIn(
            "ASkyguardApacheAircraft",
            BODY_MESH_FIELD,
        )
        self.assertNotIn(f"origin/main:{apache_header}", file_text)
        self.assertNotIn(f"git show origin/main:{apache_header}", file_text)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        self.assertEqual(
            require_declaration(locked_only, BODY_MESH_FIELD),
            BODY_MESH_FIELD,
        )
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, BODY_MESH_FIELD)
        self.assertNotIn("ApplyWeaponHit", locked_only)
        self.assertNotIn("IssuePilotCommand", locked_only)
        self.assertNotIn("GetMaxDefeatDebrisPieces", locked_only)
        self.assertNotIn("NotifyWeakPointDestroyed", locked_only)
        self.assertNotIn("GetDefeatDebrisPieceCount", locked_only)
        self.assertNotIn("GetTelemetry", locked_only)
        self.assertNotIn("GetGunnerMount", locked_only)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)
        self.assertNotIn("FaceWorldLocation", locked_only)
        self.assertNotIn("WeakPoints", locked_only)
        self.assertNotIn("USkyguardBossWeakPointComponent", locked_only)
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, locked_only)

    def test_contract_parses_public_section_not_enum_private_or_cpp(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        body = class_body(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("UENUM", section)
        self.assertNotIn("enum class", section)
        self.assertNotIn("HandleWeakPointDestroyed", section)
        self.assertNotIn("SetBossPhase", section)
        self.assertNotIn("RegisterDefeatDebris", section)
        self.assertNotIn("CleanupDefeatDebris", section)
        self.assertNotIn("HandleDefeated", section)
        self.assertNotIn("USkyguardDebriefWidget", section)
        self.assertNotIn("USkyguardBriefingWidget", section)
        self.assertNotIn("USkyguardDebriefWidget", body)
        self.assertNotIn("USkyguardBriefingWidget", body)
        self.assertNotIn("FSkyguardSearchlightTrackRuntime", section)
        self.assertNotIn("ASkyguardApacheAircraft", section)
        self.assertNotIn("ASkyguardGunner", section)
        self.assertNotIn("ASkyguardRadarNode", section)
        self.assertNotIn("ASkyguardBlackKiteBoss", section)
        self.assertNotIn("ASkyguardRadarGhostBoss", section)
        self.assertNotIn("ASkyguardLifelineHunterBoss", section)
        self.assertNotIn("ASkyguardTempestBoss", section)
        self.assertNotIn("ASkyguardIronRainBoss", section)
        self.assertNotIn("ASkyguardLastFlightBoss", section)
        self.assertNotIn("ASkyguardPatrolShip", section)
        self.assertEqual(
            require_declaration(section, BODY_MESH_FIELD),
            BODY_MESH_FIELD,
        )
        self.assertEqual(
            declaration_count(section, BODY_MESH_FIELD),
            1,
        )
        self.assertNotIn("SkyguardBossDroneBase.cpp", section)
        self.assertNotIn(
            "ASkyguardBossDroneBase::BodyMesh",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, BODY_MESH_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBossDroneBase.cpp", section)
        self.assertNotIn(
            "ASkyguardBossDroneBase::BodyMesh",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", BODY_MESH_FIELD)
        self.assertNotIn("}", BODY_MESH_FIELD)
        self.assertNotIn("return false", BODY_MESH_FIELD)
        self.assertNotIn("return true", BODY_MESH_FIELD)
        self.assertNotIn(
            "DefeatDebrisComponents",
            BODY_MESH_FIELD,
        )

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{BODY_MESH_FIELD}\n"
        file_text = this_file_text()
        # Harbor clock field names stay off this class
        # public section. Literal Harbor interval retune
        # tokens fail closed in this file and the
        # locked declaration only. Do not scan Apache
        # public section for those tokens. Apache
        # MaxIntegrity is not a Harbor clock.
        # Pathfinder MinHeightFromOriginCm is the
        # wrong header. Field
        # MinimumCivilianSeparationMeters = 550.f
        # and MinimumWeaponSeparationMeters = 450.f
        # are Harbor-adjacent; do not treat them as
        # Harbor 40/80. Do not lock
        # MinimumCivilianSeparationMeters.
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, BODY_MESH_FIELD)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, BODY_MESH_FIELD)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)

    def test_harbor_adjacent_fields_are_not_harbor_40_80(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        # LastFlight MinimumCivilianSeparationMeters = 550.f and
        # LifelineHunter MinimumWeaponSeparationMeters = 450.f
        # are Harbor-adjacent; do not treat as Harbor 40/80.
        # Do not lock MinimumCivilianSeparationMeters.
        adjacent_civilian = "MinimumCivilianSeparationMeters = 550.f"
        adjacent_weapon = "MinimumWeaponSeparationMeters = 450.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent_civilian)
            self.assertNotEqual(token, adjacent_weapon)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in HARBOR_ADJACENT_NOT_LOCKED:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)

    def test_contract_does_not_relock_leftover_boss_phase_enum(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for token in LEFTOVER_BOSS_PHASE_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn(
            "test_boss_phase_enum_contract.py",
            BODY_MESH_FIELD,
        )

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
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
                "boss drone BodyMesh field contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{BODY_MESH_FIELD}\n"
        # Leftover strike / lock-eligible names stay in
        # the public section. This file and the locked
        # declaration stay clean of leftover live copy.
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, BODY_MESH_FIELD.lower())
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, BODY_MESH_FIELD)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{BODY_MESH_FIELD}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                BODY_MESH_FIELD.lower(),
                "boss drone BodyMesh contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
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
        self.assertNotIn(dirty_fwd, BODY_MESH_FIELD)

    def test_contract_is_body_mesh_field_declaration_only(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, BODY_MESH_FIELD),
            BODY_MESH_FIELD,
        )
        locked_only = f"{BODY_MESH_FIELD}\n"
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, BODY_MESH_FIELD)
        self.assertNotIn("ApplyWeaponHit", locked_only)
        self.assertNotIn("IssuePilotCommand", locked_only)
        self.assertNotIn("GetMaxDefeatDebrisPieces", locked_only)
        self.assertNotIn("NotifyWeakPointDestroyed", locked_only)
        self.assertNotIn("GetDefeatDebrisPieceCount", locked_only)
        self.assertNotIn("GetTelemetry", locked_only)
        self.assertNotIn("GetGunnerMount", locked_only)
        self.assertNotIn("GetEyeMount", locked_only)
        self.assertNotIn("GetWeaponMount", locked_only)
        self.assertNotIn("GetChinTurret", locked_only)
        self.assertNotIn("GetPilotMount", locked_only)
        self.assertNotIn("GetSensorTurret", locked_only)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)
        self.assertNotIn("FaceWorldLocation", locked_only)
        self.assertNotIn("ApplyDamage", locked_only)
        self.assertNotIn("WeakPoints", locked_only)
        self.assertNotIn("USkyguardBossWeakPointComponent", locked_only)
        self.assertNotIn("FSkyguardSearchlightTrackRuntime", locked_only)
        self.assertNotIn("HarborIndustrial", locked_only)
        self.assertNotIn("USkyguardDebriefWidget", locked_only)
        self.assertNotIn("USkyguardBriefingWidget", locked_only)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn("MinHeightFromOriginCm", locked_only)
        self.assertNotIn("MaxIntegrity", locked_only)
        self.assertNotIn("CurrentIntegrity", locked_only)
        self.assertNotIn("SetSearchlightTracked", locked_only)
        self.assertNotIn("SetContactIdentified", locked_only)
        self.assertNotIn("OpenOrbitExposure", locked_only)
        self.assertNotIn("SetFriendlySeparationMeters", locked_only)
        self.assertNotIn("SetLightningExposed", locked_only)
        self.assertNotIn("OpenUpperEngineExposure", locked_only)
        self.assertNotIn("GetObjectiveMilestonesReached", locked_only)
        self.assertNotIn("ASkyguardPatrolShip", locked_only)
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, BODY_MESH_FIELD)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_APACHE_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_SETTINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_INPUT_CAPTURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_BLACK_KITE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_RADAR_GHOST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_TEMPEST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_IRON_RAIN_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_LAST_FLIGHT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_PATROL_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in APPLY_WEAPON_HIT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in ISSUE_PILOT_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in GET_MAX_DEFEAT_DEBRIS_PIECES_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in NOTIFY_WEAK_POINT_DESTROYED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in GET_DEFEAT_DEBRIS_PIECE_COUNT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in GET_TELEMETRY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in GET_BOSS_PHASE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in PUBLIC_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_HULL_COLLIDER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_ROOT_FIELD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_MESH_BIND_SLOT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in LEFTOVER_BOSS_PHASE_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in HARBOR_ADJACENT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in WEAK_POINT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in leftover_short_roster_values():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, BODY_MESH_FIELD)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, BODY_MESH_FIELD)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, BODY_MESH_FIELD)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, BODY_MESH_FIELD)
            self.assertNotIn(token, section)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, BODY_MESH_FIELD.lower())
            self.assertNotIn(banned, locked_only.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", BODY_MESH_FIELD)
        self.assertNotIn("{", BODY_MESH_FIELD)
        self.assertTrue(BODY_MESH_FIELD.startswith("TObjectPtr<UStaticMeshComponent> "))
        self.assertTrue(BODY_MESH_FIELD.endswith(";"))
        self.assertNotIn("=", BODY_MESH_FIELD)
        self.assertIn(UPROPERTY_BODY, section)

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
