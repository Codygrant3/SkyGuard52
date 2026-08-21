from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardPathfinderBoss.h"
CLASS_NAME = "ASkyguardPathfinderBoss"
# Field-declaration presence only. Do not invent
# INDEX_NONE or lock CommandAntenna
# construction in the .cpp. This is a FIELD
# contract on ASkyguardPathfinderBoss, not a
# leftover USkyguardBossWeakPointComponent
# member contract and not leftover Pathfinder
# encounter-controller methods. origin/main
# is a one-line field
# (`TObjectPtr<USkyguardBossWeakPointComponent>
# CommandAntenna;`); accept that form and
# other one-line / split-line wraps. The
# element type appears on origin/main and must
# be part of the locked field declaration.
# Nearby origin/main
# UPROPERTY(VisibleAnywhere, BlueprintReadOnly,
# Category="Skyguard|Boss") is
# required as present. Accept one-line and
# split-line UPROPERTY wraps. Parse the public
# class section of ASkyguardPathfinderBoss
# only. Do not lock leftover sibling Pathfinder
# fields NoseCamera, Engine, ControlLinkage,
# DebrisNose, DebrisCenter, DebrisTail,
# DebrisSpine, EncounterController as the
# primary lock. Do not lock leftover Pathfinder
# encounter-controller methods. Do not lock
# leftover MinimumCivilianSeparationMeters.
# Stay off leftover sibling LastFlight fields
# PortGuidanceArray,
# StarboardGuidanceArray,
# PortStrikeBayMechanism,
# StarboardStrikeBayMechanism,
# PortCoolingSystem,
# StarboardCoolingSystem,
# Jammer, PortEngine, StarboardEngine,
# CommandCore. Do not lock leftover
# sibling debris fields
# DebrisArmorStarboard, DebrisStrikeBayPort,
# DebrisStrikeBayStarboard, DebrisEnginePort,
# DebrisEngineStarboard as the primary lock. Stay off leftover
# sibling OpenGuidanceArrayExposure /
# BeginTerminalStrikeCycle / IssueClimbCommand /
# DivertWreckFromCivilians /
# SetCivilianSeparationMeters /
# GetObjectiveMilestonesReached /
# IsClimbCommandIssued / IsWreckDiverted /
# GetCivilianSeparationMeters. Stay off leftover
# GetFinaleStage / ESkyguardLastFlightStage.
# Stay off leftover emergency-finish surfaces.
# Stay off leftover BossDrone Root / BodyMesh /
# WeakPoints fields and leftover debris
# getters. Stay off leftover Apache
# HullCollider field #425. Stay off leftover
# Apache IssuePilotCommand / leftover #96c5 /
# #851b / #4e39. Stay off leftover
# RadarNode, leftover Gunner. Stay off leftover
# USkyguardBossWeakPointComponent member
# fields. Do not lock leftover accept flags
# on that component. Do not open
# SkyguardBossWeakPointComponent.h as the
# locked header. Leftover briefing / debrief
# widget isolated contracts, leftover
# settings / input-capture contracts,
# leftover apache aircraft isolated contracts,
# leftover Harbor clocks, leftover Harbor
# #6/#8/#9, leftover theater-kit #59 /
# flare / HUD, leftover ApacheSystem / weapon
# stations / leftover roster / loadout /
# lock-phase, leftover drafts #56–#64, leftover
# isolated-test drafts #107–#500 including leftover
# searchlight-track-runtime-defaults #7347,
# leftover settings-apply-broadcast #1268,
# leftover BlackKite / RadarGhost /
# LifelineHunter / Tempest / IronRain /
# BossDrone drafts, leftover patrol-ship
# empty fail-closed #5382, leftover skyline
# style HarborIndustrial (leftover enum, not a
# Harbor 40/80 retune), leftover Pathfinder
# MinHeightFromOriginCm (wrong header, not
# Harbor 40/80), leftover Apache
# MaxIntegrity / CurrentIntegrity, leftover
# sortie-hud-host fail-closed, leftover
# gun-fire camera shake, leftover
# DebriefWidget / BriefingWidget isolated
# contracts, and leftover
# SortiePresentationWidgets stay sibling-only.
# Harbor interval retune tokens fail closed
# in this file and the locked declaration
# only. Do not scan Apache public section for
# those tokens. Harbor clock names may be
# scanned in this relevant public section and
# must be absent. LastFlight
# MinimumCivilianSeparationMeters = 550.f is
# Harbor-adjacent; do not treat as Harbor
# 40/80. LifelineHunter
# MinimumWeaponSeparationMeters = 450.f is
# Harbor-adjacent.
COMMAND_ANTENNA_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "CommandAntenna;"
)
UPROPERTY_ANTENNA = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Boss")'
)
GET_CIVILIAN_SEPARATION_METERS = (
    "float GetCivilianSeparationMeters() const;"
)
ISSUE_CLIMB_COMMAND = (
    "bool IssueClimbCommand();"
)
# Leftover #56–#64 plus leftover Harbor #6/#8/#9,
# leftover theater-kit #59, leftover
# SkyguardPathfinderBoss production files. This
# lane only adds an isolated Python CommandAntenna
# field declaration contract on
# ASkyguardPathfinderBoss. Stay off leftover
# sibling Pathfinder fields and leftover
# Pathfinder encounter-controller methods. Stay off
# leftover sibling OpenGuidanceArrayExposure /
# BeginTerminalStrikeCycle / IssueClimbCommand /
# DivertWreckFromCivilians /
# SetCivilianSeparationMeters /
# IsClimbCommandIssued / IsWreckDiverted /
# GetObjectiveMilestonesReached, leftover
# GetFinaleStage / ESkyguardLastFlightStage, leftover
# emergency-finish surfaces, leftover RadarNode,
# leftover Gunner, leftover
# apache-own-ship-systems #96c5, leftover #851b
# mount getters, leftover #4e39
# GetChinMuzzleLocation, leftover
# USkyguardBossWeakPointComponent fields, leftover
# apache aircraft isolated contracts, leftover
# settings / input-capture contracts, leftover
# CPG HUD / sight HUD, leftover drafts #56–#64,
# leftover isolated-test drafts #107–#500,
# leftover searchlight-track-runtime-defaults
# #7347, leftover BlackKite siblings, leftover
# RadarGhost siblings, leftover LifelineHunter
# siblings, leftover Tempest siblings, leftover
# IronRain siblings including leftover IronRain
# IssueClimbCommand, leftover patrol-ship empty
# fail-closed #5382, leftover ApacheSystem enum
# values, leftover roster enum values, leftover
# Harbor clocks, leftover skyline
# HarborIndustrial, leftover DebriefWidget
# isolated contracts, leftover BriefingWidget
# isolated contracts, leftover gun-fire camera
# shake, leftover sortie-hud-host fail-closed,
# and dirty workspace paths.
LOCKED = {
    "SkyguardPathfinderBoss.h",
    "SkyguardPathfinderBoss.cpp",
    "SkyguardPathfinderEncounterController.h",
    "SkyguardPathfinderEncounterController.cpp",
    "SkyguardLastFlightBoss.h",
    "SkyguardLastFlightBoss.cpp",
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
# emergency-finish boss contracts, leftover
# OpenGuidanceArrayExposure / BeginTerminalStrikeCycle /
# IssueClimbCommand / DivertWreckFromCivilians /
# SetCivilianSeparationMeters /
# IsClimbCommandIssued / IsWreckDiverted /
# GetObjectiveMilestonesReached siblings, leftover
# GetFinaleStage / ESkyguardLastFlightStage, leftover
# apache aircraft isolated contracts, leftover
# Gunner, leftover settings / input-capture
# contracts, leftover briefing/debrief widget
# contracts, leftover apache-aircraft
# empty-fail-closed #851b, leftover
# apache-chin-muzzle #4e39, leftover
# apache-own-ship-systems #96c5, leftover
# apache-cpg-feel #8951, leftover drafts
# #56–#64, leftover isolated-test drafts
# #107–#500, leftover
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
# MinHeightFromOriginCm (wrong header, not
# Harbor 40/80), leftover Apache
# MaxIntegrity, and leftover Iron Rain contracts
# stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_pathfinder_nose_camera_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_engine_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_control_linkage_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_debris_nose_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_debris_center_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_debris_tail_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_debris_spine_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_encounter_controller_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_advance_encounter_decl_contract.py",
    "Scripts/tests/test_pathfinder_reset_encounter_state_decl_contract.py",
    "Scripts/tests/test_pathfinder_is_route_state_safe_decl_contract.py",
    "Scripts/tests/test_pathfinder_get_route_progress_decl_contract.py",
    "Scripts/tests/test_pathfinder_get_effective_speed_multiplier_decl_contract.py",
    "Scripts/tests/test_pathfinder_is_attack_telegraph_active_decl_contract.py",
    "Scripts/tests/test_pathfinder_get_telegraphs_triggered_decl_contract.py",
    "Scripts/tests/test_last_flight_debris_armor_port_field_decl_contract.py",
    "Scripts/tests/test_last_flight_port_guidance_array_field_decl_contract.py",
    "Scripts/tests/test_last_flight_starboard_guidance_array_field_decl_contract.py",
    "Scripts/tests/test_last_flight_port_strike_bay_mechanism_field_decl_contract.py",
    "Scripts/tests/test_last_flight_starboard_strike_bay_mechanism_field_decl_contract.py",
    "Scripts/tests/test_last_flight_port_cooling_system_field_decl_contract.py",
    "Scripts/tests/test_last_flight_starboard_cooling_system_field_decl_contract.py",
    "Scripts/tests/test_last_flight_jammer_field_decl_contract.py",
    "Scripts/tests/test_last_flight_port_engine_field_decl_contract.py",
    "Scripts/tests/test_last_flight_starboard_engine_field_decl_contract.py",
    "Scripts/tests/test_last_flight_get_civilian_separation_meters_decl_contract.py",
    "Scripts/tests/test_last_flight_issue_climb_command_decl_contract.py",
    "Scripts/tests/test_boss_drone_root_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_body_mesh_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_weak_points_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_phase_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_current_pilot_command_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_telemetry_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_on_boss_phase_changed_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_apply_weapon_hit_decl_contract.py",
    "Scripts/tests/test_boss_drone_get_boss_phase_decl_contract.py",
    "Scripts/tests/test_boss_drone_issue_pilot_command_decl_contract.py",
    "Scripts/tests/test_boss_drone_get_max_defeat_debris_pieces_decl_contract.py",
    "Scripts/tests/test_boss_drone_notify_weak_point_destroyed_decl_contract.py",
    "Scripts/tests/test_boss_drone_get_defeat_debris_piece_count_decl_contract.py",
    "Scripts/tests/test_boss_drone_get_telemetry_decl_contract.py",
    "Scripts/tests/test_boss_phase_enum_contract.py",
    "Scripts/tests/test_mesh_bind_slot_fields_contract.py",
    "Scripts/tests/test_last_flight_begin_terminal_strike_cycle_decl_contract.py",
    "Scripts/tests/test_last_flight_open_guidance_array_exposure_decl_contract.py",
    "Scripts/tests/test_last_flight_divert_wreck_from_civilians_decl_contract.py",
    "Scripts/tests/test_last_flight_set_civilian_separation_meters_decl_contract.py",
    "Scripts/tests/test_last_flight_is_climb_command_issued_decl_contract.py",
    "Scripts/tests/test_last_flight_is_wreck_diverted_decl_contract.py",
    "Scripts/tests/test_last_flight_get_objective_milestones_reached_decl_contract.py",
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
NOSE_CAMERA_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "NoseCamera;"
)
ENGINE_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "Engine;"
)
CONTROL_LINKAGE_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "ControlLinkage;"
)
DEBRIS_NOSE_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisNose;"
)
DEBRIS_CENTER_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisCenter;"
)
DEBRIS_TAIL_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisTail;"
)
DEBRIS_SPINE_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisSpine;"
)
ENCOUNTER_CONTROLLER_FIELD = (
    "TObjectPtr<USkyguardPathfinderEncounterController> "
    "EncounterController;"
)
ADVANCE_ENCOUNTER = (
    "void AdvanceEncounter(float DeltaSeconds);"
)
RESET_ENCOUNTER_STATE = (
    "void ResetEncounterState(const FTransform& NewRouteOrigin);"
)
IS_ROUTE_STATE_SAFE = (
    "bool IsRouteStateSafe() const;"
)
GET_ROUTE_PROGRESS = (
    "float GetRouteProgress() const;"
)
GET_EFFECTIVE_SPEED_MULTIPLIER = (
    "float GetEffectiveSpeedMultiplier() const;"
)
IS_ATTACK_TELEGRAPH_ACTIVE = (
    "bool IsAttackTelegraphActive() const;"
)
GET_TELEGRAPHS_TRIGGERED = (
    "int32 GetTelegraphsTriggered() const;"
)
# Sibling Pathfinder boss fields stay unlocked for
# THIS test's primary lock.
# Neighbors in the same public section. Presence is
# not locked here. Sibling
# OpenGuidanceArrayExposure, BeginTerminalStrikeCycle,
# IssueClimbCommand, DivertWreckFromCivilians,
# SetCivilianSeparationMeters, IsClimbCommandIssued,
# IsWreckDiverted, GetObjectiveMilestonesReached,
# leftover GetFinaleStage / ESkyguardLastFlightStage,
# leftover
# emergency-finish surfaces, leftover
# USkyguardBossWeakPointComponent fields, leftover
# mount getters, leftover GetChinMuzzleLocation,
# and leftover apache / Gunner / settings helpers
# stay sibling-only.
BEGIN_TERMINAL_STRIKE_CYCLE = (
    "bool BeginTerminalStrikeCycle();"
)
OPEN_GUIDANCE_ARRAY_EXPOSURE = (
    "bool OpenGuidanceArrayExposure();"
)
DIVERT_WRECK_FROM_CIVILIANS = (
    "bool DivertWreckFromCivilians();"
)
SET_CIVILIAN_SEPARATION_METERS = (
    "void SetCivilianSeparationMeters(float SeparationMeters);"
)
GET_FINALE_STAGE = (
    "ESkyguardLastFlightStage GetFinaleStage() const "
    "{ return FinaleStage; }"
)
IS_CLIMB_COMMAND_ISSUED = (
    "bool IsClimbCommandIssued() const "
    "{ return bClimbCommandIssued; }"
)
IS_WRECK_DIVERTED = (
    "bool IsWreckDiverted() const { return bWreckDiverted; }"
)
GET_OBJECTIVE_MILESTONES_REACHED = (
    "int32 GetObjectiveMilestonesReached() const"
)
MINIMUM_CIVILIAN_SEPARATION = (
    "float MinimumCivilianSeparationMeters = 550.f;"
)
GET_CIVILIAN_SEPARATION_METERS_NOT_LOCKED = (
    GET_CIVILIAN_SEPARATION_METERS,
    "test_last_flight_get_civilian_separation_meters_decl_contract.py",
    "GetCivilianSeparationMeters",
)
LEFTOVER_HULL_COLLIDER_NOT_LOCKED = (
    "test_apache_hull_collider_field_decl_contract.py",
    "HullCollider",
)
LEFTOVER_PATHFINDER_SIBLING_FIELDS_NOT_LOCKED = (
    "test_pathfinder_nose_camera_field_decl_contract.py",
    "test_pathfinder_engine_field_decl_contract.py",
    "test_pathfinder_control_linkage_field_decl_contract.py",
    "test_pathfinder_debris_nose_field_decl_contract.py",
    "test_pathfinder_debris_center_field_decl_contract.py",
    "test_pathfinder_debris_tail_field_decl_contract.py",
    "test_pathfinder_debris_spine_field_decl_contract.py",
    "test_pathfinder_encounter_controller_field_decl_contract.py",
    "NoseCamera",
    "ControlLinkage",
    "DebrisNose",
    "DebrisCenter",
    "DebrisTail",
    "DebrisSpine",
    "EncounterController",
)
LEFTOVER_PATHFINDER_ENCOUNTER_METHODS_NOT_LOCKED = (
    "test_pathfinder_advance_encounter_decl_contract.py",
    "test_pathfinder_reset_encounter_state_decl_contract.py",
    "test_pathfinder_is_route_state_safe_decl_contract.py",
    "test_pathfinder_get_route_progress_decl_contract.py",
    "test_pathfinder_get_effective_speed_multiplier_decl_contract.py",
    "test_pathfinder_is_attack_telegraph_active_decl_contract.py",
    "test_pathfinder_get_telegraphs_triggered_decl_contract.py",
    "AdvanceEncounter",
    "ResetEncounterState",
    "IsRouteStateSafe",
    "GetRouteProgress",
    "GetEffectiveSpeedMultiplier",
    "IsAttackTelegraphActive",
    "GetTelegraphsTriggered",
)
LEFTOVER_LAST_FLIGHT_DEBRIS_ARMOR_PORT_NOT_LOCKED = (
    "test_last_flight_debris_armor_port_field_decl_contract.py",
    "DebrisArmorPort",
)
LEFTOVER_PORT_GUIDANCE_ARRAY_NOT_LOCKED = (
    "test_last_flight_port_guidance_array_field_decl_contract.py",
    "PortGuidanceArray",
)
LEFTOVER_STARBOARD_GUIDANCE_ARRAY_NOT_LOCKED = (
    "test_last_flight_starboard_guidance_array_field_decl_contract.py",
    "StarboardGuidanceArray",
)
LEFTOVER_PORT_STRIKE_BAY_MECHANISM_NOT_LOCKED = (
    "test_last_flight_port_strike_bay_mechanism_field_decl_contract.py",
    "PortStrikeBayMechanism",
)
LEFTOVER_STARBOARD_STRIKE_BAY_MECHANISM_NOT_LOCKED = (
    "test_last_flight_starboard_strike_bay_mechanism_field_decl_contract.py",
    "StarboardStrikeBayMechanism",
)
LEFTOVER_PORT_COOLING_SYSTEM_NOT_LOCKED = (
    "test_last_flight_port_cooling_system_field_decl_contract.py",
    "PortCoolingSystem",
)
LEFTOVER_STARBOARD_COOLING_SYSTEM_NOT_LOCKED = (
    "test_last_flight_starboard_cooling_system_field_decl_contract.py",
    "StarboardCoolingSystem",
)
LEFTOVER_JAMMER_NOT_LOCKED = (
    "test_last_flight_jammer_field_decl_contract.py",
    "Jammer",
)
LEFTOVER_PORT_ENGINE_NOT_LOCKED = (
    "test_last_flight_port_engine_field_decl_contract.py",
    "PortEngine",
)
LEFTOVER_STARBOARD_ENGINE_NOT_LOCKED = (
    "StarboardEngine",
)
LEFTOVER_SIBLING_DEBRIS_NOT_LOCKED = (
    "DebrisArmorStarboard",
    "DebrisStrikeBayPort",
    "DebrisStrikeBayStarboard",
    "DebrisEnginePort",
    "DebrisEngineStarboard",
)
LEFTOVER_BOSS_DRONE_FIELDS_NOT_LOCKED = (
    "test_boss_drone_root_field_decl_contract.py",
    "test_boss_drone_body_mesh_field_decl_contract.py",
    "test_boss_drone_weak_points_field_decl_contract.py",
    "test_boss_drone_phase_field_decl_contract.py",
    "test_boss_drone_current_pilot_command_field_decl_contract.py",
    "test_boss_drone_telemetry_field_decl_contract.py",
    "test_boss_drone_on_boss_phase_changed_field_decl_contract.py",
    "TObjectPtr<USceneComponent> Root;",
    "TObjectPtr<UStaticMeshComponent> BodyMesh;",
    "TArray<TObjectPtr<USkyguardBossWeakPointComponent>> WeakPoints;",
)
LEFTOVER_DEBRIS_GETTERS_NOT_LOCKED = (
    "test_boss_drone_get_defeat_debris_piece_count_decl_contract.py",
    "test_boss_drone_get_max_defeat_debris_pieces_decl_contract.py",
    "GetDefeatDebrisPieceCount",
    "GetMaxDefeatDebrisPieces",
)
LEFTOVER_WEAK_POINT_COMPONENT_HEADER_NOT_SCANNED = (
    "SkyguardBossWeakPointComponent.h",
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
)
INVENTED_FIELD_META = (
    "meta =",
    "ClampMin",
)
HARBOR_ADJACENT_NOT_LOCKED = (
    "MinimumCivilianSeparationMeters",
    "MinimumWeaponSeparationMeters",
    "550.f",
    "450.f",
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


def leftover_weak_point_accept_flags() -> tuple[str, ...]:
    banned = "Ri" + "fle"
    missile = "Ig" + "la"
    return (
        f"bAccepts{banned}",
        f"bAccepts{missile}",
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
        "ASkyguardPathfinderBoss();",
        NOSE_CAMERA_FIELD,
        ENGINE_FIELD,
        CONTROL_LINKAGE_FIELD,
        DEBRIS_NOSE_FIELD,
        DEBRIS_CENTER_FIELD,
        DEBRIS_TAIL_FIELD,
        DEBRIS_SPINE_FIELD,
        ENCOUNTER_CONTROLLER_FIELD,
        ADVANCE_ENCOUNTER,
        RESET_ENCOUNTER_STATE,
        IS_ROUTE_STATE_SAFE,
        GET_ROUTE_PROGRESS,
        GET_EFFECTIVE_SPEED_MULTIPLIER,
        IS_ATTACK_TELEGRAPH_ACTIVE,
        GET_TELEGRAPHS_TRIGGERED,
        BEGIN_TERMINAL_STRIKE_CYCLE,
        OPEN_GUIDANCE_ARRAY_EXPOSURE,
        ISSUE_CLIMB_COMMAND,
        DIVERT_WRECK_FROM_CIVILIANS,
        SET_CIVILIAN_SEPARATION_METERS,
        leftover_open_first_window(),
        leftover_open_final_window(),
        leftover_arm_command_core_path(),
        leftover_apply_strike(),
        leftover_is_lock_eligible(),
        GET_FINALE_STAGE,
        IS_CLIMB_COMMAND_ISSUED,
        IS_WRECK_DIVERTED,
        GET_OBJECTIVE_MILESTONES_REACHED,
        GET_CIVILIAN_SEPARATION_METERS,
        MINIMUM_CIVILIAN_SEPARATION,
        "TObjectPtr<USkyguardBossWeakPointComponent> StarboardGuidanceArray;",
        "TObjectPtr<USkyguardBossWeakPointComponent> PortGuidanceArray;",
        "TObjectPtr<USkyguardBossWeakPointComponent> StarboardStrikeBayMechanism;",
        "TObjectPtr<USkyguardBossWeakPointComponent> PortStrikeBayMechanism;",
        "TObjectPtr<USkyguardBossWeakPointComponent> StarboardCoolingSystem;",
        "TObjectPtr<USkyguardBossWeakPointComponent> PortCoolingSystem;",
        "TObjectPtr<USkyguardBossWeakPointComponent> PortEngine;",
        "TObjectPtr<USkyguardBossWeakPointComponent> StarboardEngine;",
        "TObjectPtr<USkyguardBossWeakPointComponent> CommandCore;",
        "TObjectPtr<USkyguardBossWeakPointComponent> Jammer;",
        "TObjectPtr<UStaticMeshComponent> DebrisArmorStarboard;",
        "TObjectPtr<UStaticMeshComponent> DebrisStrikeBayPort;",
        "TObjectPtr<UStaticMeshComponent> DebrisStrikeBayStarboard;",
        "TObjectPtr<UStaticMeshComponent> DebrisEnginePort;",
        "TObjectPtr<UStaticMeshComponent> DebrisEngineStarboard;",
        "USceneComponent* GetGunnerMount() const { return GunnerMount; }",
        "FVector GetChinMuzzleLocation() const;",
        "void FaceWorldLocation(const FVector& WorldLocation);",
        "void ApplyDamage(float Amount);",
    )


WEAK_POINT_FIELDS_NOT_LOCKED = (
    "StarboardGuidanceArray",
    "PortGuidanceArray",
    "StarboardStrikeBayMechanism",
    "PortStrikeBayMechanism",
    "StarboardCoolingSystem",
    "PortCoolingSystem",
    "PortEngine",
    "StarboardEngine",
    "CommandCore",
    "Jammer",
    "DebrisArmorStarboard",
    "DebrisStrikeBayPort",
    "DebrisStrikeBayStarboard",
    "DebrisEnginePort",
    "DebrisEngineStarboard",
)
BEGIN_TERMINAL_STRIKE_CYCLE_NOT_LOCKED = (
    BEGIN_TERMINAL_STRIKE_CYCLE,
    "test_last_flight_begin_terminal_strike_cycle_decl_contract.py",
    "BeginTerminalStrikeCycle",
)
OPEN_GUIDANCE_ARRAY_EXPOSURE_NOT_LOCKED = (
    OPEN_GUIDANCE_ARRAY_EXPOSURE,
    "test_last_flight_open_guidance_array_exposure_decl_contract.py",
    "OpenGuidanceArrayExposure",
)
DIVERT_WRECK_FROM_CIVILIANS_NOT_LOCKED = (
    DIVERT_WRECK_FROM_CIVILIANS,
    "test_last_flight_divert_wreck_from_civilians_decl_contract.py",
    "DivertWreckFromCivilians",
)
SET_CIVILIAN_SEPARATION_METERS_NOT_LOCKED = (
    SET_CIVILIAN_SEPARATION_METERS,
    "test_last_flight_set_civilian_separation_meters_decl_contract.py",
    "SetCivilianSeparationMeters",
)
GETTERS_NOT_LOCKED = (
    GET_FINALE_STAGE,
    IS_CLIMB_COMMAND_ISSUED,
    IS_WRECK_DIVERTED,
    GET_OBJECTIVE_MILESTONES_REACHED,
    "GetFinaleStage",
    "ESkyguardLastFlightStage",
    "IsClimbCommandIssued",
    "IsWreckDiverted",
    "GetObjectiveMilestonesReached",
)
ISSUE_CLIMB_COMMAND_NOT_LOCKED = (
    ISSUE_CLIMB_COMMAND,
    "test_last_flight_issue_climb_command_decl_contract.py",
    "IssueClimbCommand",
)
GET_FINALE_STAGE_NOT_LOCKED = (
    GET_FINALE_STAGE,
    "test_last_flight_get_finale_stage_decl_contract.py",
    "GetFinaleStage",
    "ESkyguardLastFlightStage",
)
IS_CLIMB_COMMAND_ISSUED_NOT_LOCKED = (
    IS_CLIMB_COMMAND_ISSUED,
    "test_last_flight_is_climb_command_issued_decl_contract.py",
    "IsClimbCommandIssued",
)
IS_WRECK_DIVERTED_NOT_LOCKED = (
    IS_WRECK_DIVERTED,
    "test_last_flight_is_wreck_diverted_decl_contract.py",
    "IsWreckDiverted",
)
GET_OBJECTIVE_MILESTONES_REACHED_NOT_LOCKED = (
    GET_OBJECTIVE_MILESTONES_REACHED,
    "test_last_flight_get_objective_milestones_reached_decl_contract.py",
    "GetObjectiveMilestonesReached",
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
# Pathfinder MinHeightFromOriginCm lives on the
# encounter-controller header, not this boss
# public section. That value is the wrong header,
# not Harbor 40/80. Apache MaxIntegrity is also
# the wrong header. Do not scan Apache public
# section for Harbor clocks.
WRONG_HARBOR_HEADERS_NOT_SCANNED = (
    "SkyguardPathfinderEncounterController.h",
    "MinHeightFromOriginCm",
    "MaxIntegrity",
    "CurrentIntegrity",
    "SkyguardApacheAircraft.h",
    "ASkyguardApacheAircraft",
)
# Field MinimumCivilianSeparationMeters = 550.f is
# Harbor-adjacent; do not treat it as Harbor 40/80.
HARBOR_ADJACENT_CIVILIAN_SEPARATION = (
    "MinimumCivilianSeparationMeters",
    "550.f",
)
# .cpp IssueClimbCommand body / invented
# INDEX_NONE stay unlocked. Do not invent INDEX_NONE
# or lock the cpp body. Do not parse leftover HUD
# classes.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "ASkyguardPathfinderBoss::CommandAntenna",
    "SkyguardPathfinderBoss.cpp",
    "SetExposed",
    "RefreshAuthoredWeakPointRegistry",
    "SetBossPhase",
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


class PathfinderCommandAntennaFieldDeclContractTests(unittest.TestCase):
    def test_pathfinder_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, COMMAND_ANTENNA_FIELD),
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
            "class SKYGUARD52_API AOtherLastFlightBoss "
            ": public AActor\n"
            "{\n"
            "public:\n"
            f"\t{COMMAND_ANTENNA_FIELD}\n"
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
            f"\t{COMMAND_ANTENNA_FIELD}\n"
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
            f"\t{NOSE_CAMERA_FIELD}\n"
            "private:\n"
            f"\t{COMMAND_ANTENNA_FIELD}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, COMMAND_ANTENNA_FIELD)
        self.assertIn("CommandAntenna", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(
            has_declaration(section, COMMAND_ANTENNA_FIELD)
        )

    def test_missing_command_antenna_declaration_fails_closed(
        self,
    ) -> None:
        neighbors_only = (
            "\tASkyguardPathfinderBoss();\n"
            f"\t{NOSE_CAMERA_FIELD}\n"
            f"\t{ENGINE_FIELD}\n"
            f"\t{CONTROL_LINKAGE_FIELD}\n"
            f"\t{DEBRIS_NOSE_FIELD}\n"
            f"\t{DEBRIS_CENTER_FIELD}\n"
            f"\t{DEBRIS_TAIL_FIELD}\n"
            f"\t{DEBRIS_SPINE_FIELD}\n"
            f"\t{ENCOUNTER_CONTROLLER_FIELD}\n"
            f"\t{ADVANCE_ENCOUNTER}\n"
            f"\t{GET_ROUTE_PROGRESS}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, COMMAND_ANTENNA_FIELD)
        self.assertIn("CommandAntenna", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_ANTENNA}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, COMMAND_ANTENNA_FIELD)
        self.assertIn("CommandAntenna", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_ANTENNA, section)
        self.assertIn("VisibleAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('Category="Skyguard|Boss"', section)
        self.assertTrue(
            has_declaration(section, COMMAND_ANTENNA_FIELD),
            section,
        )
        self.assertNotIn("UPROPERTY", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("VisibleAnywhere", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("BlueprintReadOnly", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("Category", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("BlueprintPure", UPROPERTY_ANTENNA)
        self.assertNotIn("BlueprintCallable", UPROPERTY_ANTENNA)
        self.assertIn("Skyguard|Boss", UPROPERTY_ANTENNA)
        self.assertNotIn("Destruction", UPROPERTY_ANTENNA)
        self.assertNotIn("Encounter", UPROPERTY_ANTENNA)
        self.assertNotIn("Mission10", UPROPERTY_ANTENNA)
        self.assertNotIn("Safety", UPROPERTY_ANTENNA)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_ANTENNA)
            self.assertNotIn(invented, COMMAND_ANTENNA_FIELD)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, UPROPERTY_ANTENNA)
            self.assertNotIn(invented, COMMAND_ANTENNA_FIELD)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tASkyguardPathfinderBoss();\n"
            f"\t{NOSE_CAMERA_FIELD}\n"
            f"\t{ENGINE_FIELD}\n"
            f"\t{CONTROL_LINKAGE_FIELD}\n"
            f"\t{DEBRIS_NOSE_FIELD}\n"
            f"\t{ENCOUNTER_CONTROLLER_FIELD}\n"
            f"\t{ADVANCE_ENCOUNTER}\n"
            f"\t{GET_ROUTE_PROGRESS}\n"
            f"\t{BEGIN_TERMINAL_STRIKE_CYCLE}\n"
            f"\t{leftover_open_first_window()}\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "CommandCore;\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
            "\tvoid FaceWorldLocation(const FVector& WorldLocation);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, COMMAND_ANTENNA_FIELD)
        self.assertIn("CommandAntenna", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        raw_pointer = (
            "\tUSkyguardBossWeakPointComponent* CommandAntenna;\n"
        )
        as_array = (
            "\tTArray<TObjectPtr<USkyguardBossWeakPointComponent>> "
            "CommandAntenna;\n"
        )
        scene = (
            "\tTObjectPtr<USceneComponent> CommandAntenna;\n"
        )
        weak = (
            "\tTWeakObjectPtr<USkyguardBossWeakPointComponent> "
            "CommandAntenna;\n"
        )
        assigned = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "CommandAntenna = nullptr;\n"
        )
        leftover_jammer_field = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "Jammer;\n"
        )
        wrong_name = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "StarboardGuidanceArray;\n"
        )
        leftover_port_guidance = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "PortGuidanceArray;\n"
        )
        leftover_starboard = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "StarboardGuidanceArray;\n"
        )
        leftover_starboard_strike = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "StarboardStrikeBayMechanism;\n"
        )
        leftover_port_strike = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "PortStrikeBayMechanism;\n"
        )
        leftover_port_cooling = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "PortCoolingSystem;\n"
        )
        leftover_starboard_cooling = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "StarboardCoolingSystem;\n"
        )
        leftover_begin = f"\t{BEGIN_TERMINAL_STRIKE_CYCLE}\n"
        leftover_guidance = f"\t{OPEN_GUIDANCE_ARRAY_EXPOSURE}\n"
        leftover_climb = f"\t{ISSUE_CLIMB_COMMAND}\n"
        leftover_divert = f"\t{DIVERT_WRECK_FROM_CIVILIANS}\n"
        leftover_set = f"\t{SET_CIVILIAN_SEPARATION_METERS}\n"
        leftover_get = f"\t{GET_CIVILIAN_SEPARATION_METERS}\n"
        leftover_first = f"\t{leftover_open_first_window()}\n"
        leftover_final = f"\t{leftover_open_final_window()}\n"
        leftover_arm = f"\t{leftover_arm_command_core_path()}\n"
        leftover_strike = f"\t{leftover_apply_strike()}\n"
        leftover_lock = f"\t{leftover_is_lock_eligible()}\n"
        leftover_finale = f"\t{GET_FINALE_STAGE}\n"
        leftover_issued = f"\t{IS_CLIMB_COMMAND_ISSUED}\n"
        leftover_diverted = f"\t{IS_WRECK_DIVERTED}\n"
        leftover_sep = f"\t{GET_OBJECTIVE_MILESTONES_REACHED}\n"
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
        leftover_root = "\tTObjectPtr<USceneComponent> Root;\n"
        leftover_body = "\tTObjectPtr<UStaticMeshComponent> BodyMesh;\n"
        leftover_hull = "\tTObjectPtr<UBoxComponent> HullCollider;\n"
        for region in (
            raw_pointer,
            as_array,
            scene,
            weak,
            assigned,
            wrong_name,
            leftover_port_guidance,
            leftover_starboard,
            leftover_starboard_strike,
            leftover_port_strike,
            leftover_port_cooling,
            leftover_starboard_cooling,
            leftover_jammer_field,
            leftover_begin,
            leftover_guidance,
            leftover_climb,
            leftover_divert,
            leftover_set,
            leftover_get,
            leftover_first,
            leftover_final,
            leftover_arm,
            leftover_strike,
            leftover_lock,
            leftover_finale,
            leftover_issued,
            leftover_diverted,
            leftover_sep,
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
            leftover_root,
            leftover_body,
            leftover_hull,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, COMMAND_ANTENNA_FIELD)
            self.assertIn("CommandAntenna", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_command_antenna_declaration_matches_origin_main(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, COMMAND_ANTENNA_FIELD),
            COMMAND_ANTENNA_FIELD,
        )
        self.assertTrue(
            has_declaration(section, COMMAND_ANTENNA_FIELD)
        )
        self.assertEqual(
            declaration_count(section, COMMAND_ANTENNA_FIELD),
            1,
        )
        self.assertTrue(
            COMMAND_ANTENNA_FIELD.startswith(
                "TObjectPtr<USkyguardBossWeakPointComponent> "
            ),
            COMMAND_ANTENNA_FIELD,
        )
        self.assertTrue(
            COMMAND_ANTENNA_FIELD.endswith(";"),
            COMMAND_ANTENNA_FIELD,
        )
        self.assertIn("CommandAntenna", COMMAND_ANTENNA_FIELD)
        self.assertIn(
            "USkyguardBossWeakPointComponent",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn(
            "UStaticMeshComponent",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertIn("TObjectPtr<", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("TArray<", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("=", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("INDEX_NONE", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("UFUNCTION", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("{", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("}", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("return ", COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "BeginTerminalStrikeCycle",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn("OpenGuidanceArrayExposure", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("IssueClimbCommand", COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "DivertWreckFromCivilians",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn(
            "SetCivilianSeparationMeters",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn("GetCivilianSeparationMeters", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("GetFinaleStage", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("IsClimbCommandIssued", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("IsWreckDiverted", COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "GetObjectiveMilestonesReached",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn(
            "ESkyguardLastFlightStage",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn("GetChinMuzzleLocation", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("GetGunnerMount", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("FaceWorldLocation", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("StarboardGuidanceArray", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("CommandCore", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("SetSearchlightTracked", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("SetContactIdentified", COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "SetFriendlySeparationMeters",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn("SetLightningExposed", COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "OpenUpperEngineExposure",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn("HullCollider", COMMAND_ANTENNA_FIELD)
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, COMMAND_ANTENNA_FIELD)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent>\n"
            "\tCommandAntenna;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent>   "
            "CommandAntenna;\n"
            "private:\n"
            "};\n"
        )
        wrap_tab = (
            "public:\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent>\t"
            "CommandAntenna;\n"
            "};\n"
        )
        wrap_indent = (
            "public:\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent>\n"
            "\t\tCommandAntenna;\n"
            "};\n"
        )
        wrap_uproperty = (
            "public:\n"
            f"\t{UPROPERTY_ANTENNA}\n"
            f"\t{COMMAND_ANTENNA_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_one_line = (
            "public:\n"
            f"\t{UPROPERTY_ANTENNA} {COMMAND_ANTENNA_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_category = (
            "public:\n"
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly,\n"
            '\t\tCategory="Skyguard|Boss")\n'
            f"\t{COMMAND_ANTENNA_FIELD}\n"
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
                has_declaration(section, COMMAND_ANTENNA_FIELD),
                section,
            )
            self.assertEqual(
                require_declaration(section, COMMAND_ANTENNA_FIELD),
                COMMAND_ANTENNA_FIELD,
            )
            self.assertEqual(
                declaration_count(section, COMMAND_ANTENNA_FIELD),
                1,
            )
        one_line = f"{{\npublic:\n\t{COMMAND_ANTENNA_FIELD}\n}}\n"
        self.assertTrue(
            has_declaration(one_line, COMMAND_ANTENNA_FIELD)
        )
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, COMMAND_ANTENNA_FIELD),
            section,
        )
        self.assertEqual(
            require_declaration(section, COMMAND_ANTENNA_FIELD),
            COMMAND_ANTENNA_FIELD,
        )
        self.assertIn(UPROPERTY_ANTENNA, section)

    def test_assigned_command_antenna_does_not_satisfy(self) -> None:
        assigned = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "CommandAntenna = nullptr;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(assigned, COMMAND_ANTENNA_FIELD)
        self.assertIn("CommandAntenna", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(assigned, COMMAND_ANTENNA_FIELD))

    def test_sibling_public_fields_do_not_satisfy(self) -> None:
        nose = f"\t{NOSE_CAMERA_FIELD}\n"
        engine = f"\t{ENGINE_FIELD}\n"
        linkage = f"\t{CONTROL_LINKAGE_FIELD}\n"
        debris_nose = f"\t{DEBRIS_NOSE_FIELD}\n"
        debris_center = f"\t{DEBRIS_CENTER_FIELD}\n"
        debris_tail = f"\t{DEBRIS_TAIL_FIELD}\n"
        debris_spine = f"\t{DEBRIS_SPINE_FIELD}\n"
        encounter = f"\t{ENCOUNTER_CONTROLLER_FIELD}\n"
        leftover_last_flight = (
            "\tTObjectPtr<UStaticMeshComponent> "
            "DebrisArmorPort;\n"
        )
        leftover_core = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "CommandCore;\n"
        )
        civilian = f"\t{MINIMUM_CIVILIAN_SEPARATION}\n"
        for region in (
            nose,
            engine,
            linkage,
            debris_nose,
            debris_center,
            debris_tail,
            debris_spine,
            encounter,
            leftover_last_flight,
            leftover_core,
            civilian,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, COMMAND_ANTENNA_FIELD)
            self.assertIn("CommandAntenna", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, COMMAND_ANTENNA_FIELD))

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, COMMAND_ANTENNA_FIELD)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_ANTENNA)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, COMMAND_ANTENNA_FIELD)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_ANTENNA)
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_ANTENNA, section)
        self.assertTrue(has_declaration(section, COMMAND_ANTENNA_FIELD), section)

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        self.assertNotIn("UFUNCTION", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(
            COMMAND_ANTENNA_FIELD.startswith("UFUNCTION"),
            COMMAND_ANTENNA_FIELD,
        )
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, COMMAND_ANTENNA_FIELD), section)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", COMMAND_ANTENNA_FIELD)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_command_antenna_cpp_body(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        self.assertNotIn("{", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("}", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("return ", COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "ASkyguardPathfinderBoss::CommandAntenna",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn(
            "SkyguardPathfinderBoss.cpp",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn("SkyguardPathfinderBoss.cpp", locked_only)
        self.assertNotIn("return false", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("return true", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("CreateDefaultSubobject", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("SetExposed", COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "RefreshAuthoredWeakPointRegistry",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn("SetBossPhase", COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "HandleWeakPointDestroyed",
            COMMAND_ANTENNA_FIELD,
        )

    def test_contract_does_not_relock_begin_terminal_strike_cycle_sibling(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in BEGIN_TERMINAL_STRIKE_CYCLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("BeginTerminalStrikeCycle", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("BeginTerminalStrikeCycle", locked_only)

    def test_contract_does_not_relock_open_guidance_array_exposure_sibling(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in OPEN_GUIDANCE_ARRAY_EXPOSURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("OpenGuidanceArrayExposure", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_divert_wreck_from_civilians_sibling(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in DIVERT_WRECK_FROM_CIVILIANS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("DivertWreckFromCivilians", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_set_civilian_separation_meters_sibling(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in SET_CIVILIAN_SEPARATION_METERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("SetCivilianSeparationMeters", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_get_civilian_separation_meters_sibling(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in GET_CIVILIAN_SEPARATION_METERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("GetCivilianSeparationMeters", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_getters(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("GetFinaleStage", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("IssueClimbCommand", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("IsWreckDiverted", COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "GetObjectiveMilestonesReached",
            COMMAND_ANTENNA_FIELD,
        )

    def test_contract_does_not_relock_issue_climb_command_sibling(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in ISSUE_CLIMB_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("IssueClimbCommand", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_finale_stage(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in GET_FINALE_STAGE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("GetFinaleStage", COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "ESkyguardLastFlightStage",
            COMMAND_ANTENNA_FIELD,
        )

    def test_contract_does_not_relock_is_climb_command_issued_sibling(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in IS_CLIMB_COMMAND_ISSUED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("IsClimbCommandIssued", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_is_wreck_diverted_sibling(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in IS_WRECK_DIVERTED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("IsWreckDiverted", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_get_objective_milestones_reached_sibling(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in GET_OBJECTIVE_MILESTONES_REACHED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "GetObjectiveMilestonesReached",
            COMMAND_ANTENNA_FIELD,
        )

    def test_contract_does_not_relock_leftover_emergency_finish(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        self.assertNotIn(leftover_open_first_window(), locked_only)
        self.assertNotIn(
            leftover_open_first_window(),
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn(leftover_open_final_window(), locked_only)
        self.assertNotIn(
            leftover_open_final_window(),
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn(leftover_arm_command_core_path(), locked_only)
        self.assertNotIn(
            leftover_arm_command_core_path(),
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn(leftover_apply_strike(), locked_only)
        self.assertNotIn(leftover_apply_strike(), COMMAND_ANTENNA_FIELD)
        self.assertNotIn(leftover_is_lock_eligible(), locked_only)
        self.assertNotIn(leftover_is_lock_eligible(), COMMAND_ANTENNA_FIELD)
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, COMMAND_ANTENNA_FIELD)
        for script in leftover_live_copy_boss_scripts():
            self.assertNotIn(script, COMMAND_ANTENNA_FIELD)
            self.assertNotIn(script, locked_only)

    def test_contract_does_not_relock_sibling_pathfinder_fields(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_PATHFINDER_SIBLING_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("NoseCamera", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("ControlLinkage", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("DebrisNose", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("DebrisCenter", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("DebrisTail", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("DebrisSpine", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("EncounterController", COMMAND_ANTENNA_FIELD)
        self.assertIn("CommandAntenna", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_pathfinder_encounter_methods(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_PATHFINDER_ENCOUNTER_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("AdvanceEncounter", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("ResetEncounterState", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("GetRouteProgress", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("IsAttackTelegraphActive", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_last_flight_debris_armor_port(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_LAST_FLIGHT_DEBRIS_ARMOR_PORT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("DebrisArmorPort", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_sibling_last_flight_fields(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in WEAK_POINT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("PortGuidanceArray", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("StarboardGuidanceArray", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("PortStrikeBayMechanism", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("StarboardStrikeBayMechanism", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("PortCoolingSystem", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("StarboardCoolingSystem", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("CommandCore", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("PortEngine", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("Jammer", COMMAND_ANTENNA_FIELD)
        self.assertIn(
            "USkyguardBossWeakPointComponent",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn(
            "UStaticMeshComponent",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertIn("CommandAntenna", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("NoseCamera", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("ControlLinkage", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("DebrisNose", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("EncounterController", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_weak_point_component_fields(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in leftover_weak_point_accept_flags():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        for token in LEFTOVER_WEAK_POINT_COMPONENT_HEADER_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("SkyguardBossWeakPointComponent.h", locked_only)
        self.assertIn(
            "USkyguardBossWeakPointComponent",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn(
            "UStaticMeshComponent",
            COMMAND_ANTENNA_FIELD,
        )

    def test_contract_does_not_relock_leftover_boss_drone_fields(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_BOSS_DRONE_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "test_boss_drone_root_field_decl_contract.py",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn(
            "test_boss_drone_weak_points_field_decl_contract.py",
            COMMAND_ANTENNA_FIELD,
        )

    def test_contract_does_not_relock_leftover_debris_getters(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_DEBRIS_GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("GetDefeatDebrisPieceCount", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("GetMaxDefeatDebrisPieces", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_hull_collider(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_HULL_COLLIDER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("HullCollider", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_port_guidance_array(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_PORT_GUIDANCE_ARRAY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("PortGuidanceArray", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_starboard_guidance_array(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_STARBOARD_GUIDANCE_ARRAY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("StarboardGuidanceArray", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_port_strike_bay_mechanism(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_PORT_STRIKE_BAY_MECHANISM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("PortStrikeBayMechanism", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_starboard_strike_bay_mechanism(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_STARBOARD_STRIKE_BAY_MECHANISM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("StarboardStrikeBayMechanism", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_port_cooling_system(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_PORT_COOLING_SYSTEM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("PortCoolingSystem", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_starboard_cooling_system(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_STARBOARD_COOLING_SYSTEM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("StarboardCoolingSystem", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_jammer(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_JAMMER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("Jammer", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_port_engine(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_PORT_ENGINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("PortEngine", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_starboard_engine(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_STARBOARD_ENGINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("StarboardEngine", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_sibling_debris_fields(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_SIBLING_DEBRIS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("DebrisArmorStarboard", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("DebrisStrikeBayPort", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("DebrisStrikeBayStarboard", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("DebrisEnginePort", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("DebrisEngineStarboard", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_searchlight_runtime(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "test_searchlight_track_runtime_defaults_contract.py",
            COMMAND_ANTENNA_FIELD,
        )

    def test_contract_does_not_relock_leftover_black_kite(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_BLACK_KITE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("SetSearchlightTracked", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("ASkyguardBlackKiteBoss", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_radar_ghost(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_RADAR_GHOST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("SetContactIdentified", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("OpenOrbitExposure", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_lifeline_hunter(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "SetFriendlySeparationMeters",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn(
            "ASkyguardLifelineHunterBoss",
            COMMAND_ANTENNA_FIELD,
        )

    def test_contract_does_not_relock_leftover_tempest(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_TEMPEST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("SetLightningExposed", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("ASkyguardTempestBoss", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_iron_rain(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_IRON_RAIN_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "OpenUpperEngineExposure",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn("ASkyguardIronRainBoss", COMMAND_ANTENNA_FIELD)
        self.assertNotIn(
            "ASkyguardIronRainBoss::IssueClimbCommand",
            COMMAND_ANTENNA_FIELD,
        )

    def test_contract_does_not_relock_leftover_patrol_ship(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_PATROL_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("ASkyguardPatrolShip", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_mount_getters(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in MOUNT_GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("GetGunnerMount", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_chin_muzzle(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for neighbor in GET_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("GetChinMuzzleLocation", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_chin_muzzle(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_own_ship_systems(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("ESkyguardApacheSystem", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_cpg_feel(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_apache_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_APACHE_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("FaceWorldLocation", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_settings(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_SETTINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_input_capture(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_INPUT_CAPTURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_gunner(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("ASkyguardGunner", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_radar_node(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("SkyguardRadarNode", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_widget_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardDebriefWidget", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_scan_wrong_harbor_headers(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("MinHeightFromOriginCm", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("MaxIntegrity", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("CurrentIntegrity", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("SkyguardApacheAircraft.h", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_open_leftover_weak_point_component_header(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        file_text = this_file_text()
        leftover_header = "SkyguardBossWeakPointComponent.h"
        for token in LEFTOVER_WEAK_POINT_COMPONENT_HEADER_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn(leftover_header, locked_only)
        self.assertNotIn(leftover_header, COMMAND_ANTENNA_FIELD)
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
            "Source/Skyguard52/SkyguardPathfinderBoss.h",
        )

    def test_contract_does_not_scan_apache_public_section_for_harbor(
        self,
    ) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        file_text = this_file_text()
        apache_header = "SkyguardApacheAircraft.h"
        self.assertNotIn(apache_header, locked_only)
        self.assertNotIn(apache_header, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("ASkyguardApacheAircraft", locked_only)
        self.assertNotIn(
            "ASkyguardApacheAircraft",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn(f"origin/main:{apache_header}", file_text)
        self.assertNotIn(f"git show origin/main:{apache_header}", file_text)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)

    def test_minimum_civilian_separation_is_not_harbor_40_80(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        section = public_section(origin_main_header())
        adjacent = "MinimumCivilianSeparationMeters = 550.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        for token in HARBOR_ADJACENT_CIVILIAN_SEPARATION:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        for token in HARBOR_ADJACENT_NOT_LOCKED:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("MinimumCivilianSeparationMeters", section)
        self.assertNotIn("550.f", COMMAND_ANTENNA_FIELD)

    def test_harbor_adjacent_fields_are_not_harbor_40_80(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        adjacent_civilian = "MinimumCivilianSeparationMeters = 550.f"
        adjacent_weapon = "MinimumWeaponSeparationMeters = 450.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent_civilian)
            self.assertNotEqual(token, adjacent_weapon)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        self.assertEqual(
            require_declaration(locked_only, COMMAND_ANTENNA_FIELD),
            COMMAND_ANTENNA_FIELD,
        )
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("BeginTerminalStrikeCycle", locked_only)
        self.assertNotIn("OpenGuidanceArrayExposure", locked_only)
        self.assertNotIn("IssueClimbCommand", locked_only)
        self.assertNotIn("DivertWreckFromCivilians", locked_only)
        self.assertNotIn("SetCivilianSeparationMeters", locked_only)
        self.assertNotIn("GetCivilianSeparationMeters", locked_only)
        self.assertNotIn("GetFinaleStage", locked_only)
        self.assertNotIn("IsClimbCommandIssued", locked_only)
        self.assertNotIn("IsWreckDiverted", locked_only)
        self.assertNotIn("GetObjectiveMilestonesReached", locked_only)
        self.assertNotIn("GetGunnerMount", locked_only)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)
        self.assertNotIn("FaceWorldLocation", locked_only)
        self.assertNotIn("PortGuidanceArray", locked_only)
        self.assertNotIn("StarboardGuidanceArray", locked_only)
        self.assertNotIn("PortStrikeBayMechanism", locked_only)
        self.assertNotIn("StarboardStrikeBayMechanism", locked_only)
        self.assertNotIn("PortCoolingSystem", locked_only)
        self.assertNotIn("StarboardCoolingSystem", locked_only)
        self.assertNotIn("Jammer", locked_only)
        self.assertNotIn("PortEngine", locked_only)
        self.assertNotIn("StarboardEngine", locked_only)
        self.assertNotIn("DebrisArmorStarboard", locked_only)
        self.assertNotIn("DebrisStrikeBayPort", locked_only)
        self.assertNotIn("DebrisStrikeBayStarboard", locked_only)
        self.assertNotIn("DebrisEnginePort", locked_only)
        self.assertNotIn("DebrisEngineStarboard", locked_only)
        self.assertNotIn("SkyguardBossWeakPointComponent.h", locked_only)
        self.assertNotIn("NoseCamera", locked_only)
        self.assertNotIn("ControlLinkage", locked_only)
        self.assertNotIn("DebrisNose", locked_only)
        self.assertNotIn("DebrisCenter", locked_only)
        self.assertNotIn("DebrisTail", locked_only)
        self.assertNotIn("DebrisSpine", locked_only)
        self.assertNotIn("EncounterController", locked_only)
        self.assertNotIn("AdvanceEncounter", locked_only)
        self.assertNotIn("ResetEncounterState", locked_only)
        self.assertNotIn("GetRouteProgress", locked_only)
        self.assertNotIn("DebrisArmorPort", locked_only)
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
        self.assertNotIn("ASkyguardPatrolShip", section)
        self.assertEqual(
            require_declaration(section, COMMAND_ANTENNA_FIELD),
            COMMAND_ANTENNA_FIELD,
        )
        self.assertEqual(
            declaration_count(section, COMMAND_ANTENNA_FIELD),
            1,
        )
        self.assertNotIn("SkyguardPathfinderBoss.cpp", section)
        self.assertNotIn(
            "ASkyguardPathfinderBoss::CommandAntenna",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardPathfinderBoss.cpp", section)
        self.assertNotIn(
            "ASkyguardPathfinderBoss::CommandAntenna",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("}", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("return false", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("return true", COMMAND_ANTENNA_FIELD)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        file_text = this_file_text()
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
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
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
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
                "pathfinder CommandAntenna field contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, COMMAND_ANTENNA_FIELD.lower())
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                COMMAND_ANTENNA_FIELD.lower(),
                "pathfinder CommandAntenna contains "
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
        self.assertNotIn(dirty_fwd, COMMAND_ANTENNA_FIELD)

    def test_contract_is_command_antenna_field_declaration_only(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, COMMAND_ANTENNA_FIELD),
            COMMAND_ANTENNA_FIELD,
        )
        locked_only = f"{COMMAND_ANTENNA_FIELD}\n"
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, COMMAND_ANTENNA_FIELD)
        self.assertNotIn("BeginTerminalStrikeCycle", locked_only)
        self.assertNotIn("OpenGuidanceArrayExposure", locked_only)
        self.assertNotIn("IssueClimbCommand", locked_only)
        self.assertNotIn("DivertWreckFromCivilians", locked_only)
        self.assertNotIn("SetCivilianSeparationMeters", locked_only)
        self.assertNotIn("GetCivilianSeparationMeters", locked_only)
        self.assertNotIn("GetFinaleStage", locked_only)
        self.assertNotIn("IsClimbCommandIssued", locked_only)
        self.assertNotIn("IsWreckDiverted", locked_only)
        self.assertNotIn("GetObjectiveMilestonesReached", locked_only)
        self.assertNotIn("GetGunnerMount", locked_only)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)
        self.assertNotIn("FaceWorldLocation", locked_only)
        self.assertNotIn("ApplyDamage", locked_only)
        self.assertNotIn("PortGuidanceArray", locked_only)
        self.assertNotIn("StarboardGuidanceArray", locked_only)
        self.assertNotIn("PortStrikeBayMechanism", locked_only)
        self.assertNotIn("StarboardStrikeBayMechanism", locked_only)
        self.assertNotIn("PortCoolingSystem", locked_only)
        self.assertNotIn("StarboardCoolingSystem", locked_only)
        self.assertNotIn("Jammer", locked_only)
        self.assertNotIn("PortEngine", locked_only)
        self.assertNotIn("StarboardEngine", locked_only)
        self.assertNotIn("DebrisArmorStarboard", locked_only)
        self.assertNotIn("DebrisStrikeBayPort", locked_only)
        self.assertNotIn("DebrisStrikeBayStarboard", locked_only)
        self.assertNotIn("DebrisEnginePort", locked_only)
        self.assertNotIn("DebrisEngineStarboard", locked_only)
        self.assertNotIn("SkyguardBossWeakPointComponent.h", locked_only)
        self.assertNotIn("NoseCamera", locked_only)
        self.assertNotIn("ControlLinkage", locked_only)
        self.assertNotIn("DebrisNose", locked_only)
        self.assertNotIn("EncounterController", locked_only)
        self.assertNotIn("AdvanceEncounter", locked_only)
        self.assertNotIn("ResetEncounterState", locked_only)
        self.assertNotIn("DebrisArmorPort", locked_only)
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
        self.assertNotIn("ASkyguardPatrolShip", locked_only)
        self.assertNotIn("HullCollider", locked_only)
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, COMMAND_ANTENNA_FIELD)
        leftover_groups = (
            LEFTOVER_PATHFINDER_SIBLING_FIELDS_NOT_LOCKED,
            LEFTOVER_PATHFINDER_ENCOUNTER_METHODS_NOT_LOCKED,
            LEFTOVER_LAST_FLIGHT_DEBRIS_ARMOR_PORT_NOT_LOCKED,
            LEFTOVER_NOT_LOCKED,
            LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED,
            LEFTOVER_CHIN_MUZZLE_NOT_LOCKED,
            LEFTOVER_OWN_SHIP_NOT_LOCKED,
            LEFTOVER_CPG_FEEL_NOT_LOCKED,
            LEFTOVER_APACHE_DECL_NOT_LOCKED,
            LEFTOVER_SETTINGS_NOT_LOCKED,
            LEFTOVER_INPUT_CAPTURE_NOT_LOCKED,
            LEFTOVER_GUNNER_NOT_LOCKED,
            LEFTOVER_RADAR_NODE_NOT_LOCKED,
            LEFTOVER_WIDGET_DECL_NOT_LOCKED,
            LEFTOVER_SKYLINE_NOT_LOCKED,
            LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED,
            LEFTOVER_BLACK_KITE_NOT_LOCKED,
            LEFTOVER_RADAR_GHOST_NOT_LOCKED,
            LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED,
            LEFTOVER_TEMPEST_NOT_LOCKED,
            LEFTOVER_IRON_RAIN_NOT_LOCKED,
            LEFTOVER_PATROL_SHIP_NOT_LOCKED,
            ISSUE_CLIMB_COMMAND_NOT_LOCKED,
            GET_FINALE_STAGE_NOT_LOCKED,
            IS_CLIMB_COMMAND_ISSUED_NOT_LOCKED,
            IS_WRECK_DIVERTED_NOT_LOCKED,
            GET_OBJECTIVE_MILESTONES_REACHED_NOT_LOCKED,
            BEGIN_TERMINAL_STRIKE_CYCLE_NOT_LOCKED,
            OPEN_GUIDANCE_ARRAY_EXPOSURE_NOT_LOCKED,
            DIVERT_WRECK_FROM_CIVILIANS_NOT_LOCKED,
            SET_CIVILIAN_SEPARATION_METERS_NOT_LOCKED,
            GET_CIVILIAN_SEPARATION_METERS_NOT_LOCKED,
            GETTERS_NOT_LOCKED,
            WEAK_POINT_FIELDS_NOT_LOCKED,
            WRONG_HARBOR_HEADERS_NOT_SCANNED,
            leftover_short_roster_values(),
            LEFTOVER_HULL_COLLIDER_NOT_LOCKED,
            LEFTOVER_PORT_GUIDANCE_ARRAY_NOT_LOCKED,
            LEFTOVER_STARBOARD_GUIDANCE_ARRAY_NOT_LOCKED,
            LEFTOVER_PORT_STRIKE_BAY_MECHANISM_NOT_LOCKED,
            LEFTOVER_STARBOARD_STRIKE_BAY_MECHANISM_NOT_LOCKED,
            LEFTOVER_PORT_COOLING_SYSTEM_NOT_LOCKED,
            LEFTOVER_STARBOARD_COOLING_SYSTEM_NOT_LOCKED,
            LEFTOVER_JAMMER_NOT_LOCKED,
            LEFTOVER_PORT_ENGINE_NOT_LOCKED,
            LEFTOVER_STARBOARD_ENGINE_NOT_LOCKED,
            LEFTOVER_SIBLING_DEBRIS_NOT_LOCKED,
            LEFTOVER_BOSS_DRONE_FIELDS_NOT_LOCKED,
            LEFTOVER_DEBRIS_GETTERS_NOT_LOCKED,
            leftover_weak_point_accept_flags(),
            LEFTOVER_WEAK_POINT_COMPONENT_HEADER_NOT_SCANNED,
            HARBOR_ADJACENT_NOT_LOCKED,
            leftover_harbor_clock_tokens(),
        )
        for group in leftover_groups:
            for token in group:
                self.assertNotIn(token, locked_only)
                self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, COMMAND_ANTENNA_FIELD)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, COMMAND_ANTENNA_FIELD.lower())
            self.assertNotIn(banned, locked_only.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", COMMAND_ANTENNA_FIELD)
        self.assertNotIn("{", COMMAND_ANTENNA_FIELD)
        self.assertTrue(
            COMMAND_ANTENNA_FIELD.startswith(
                "TObjectPtr<USkyguardBossWeakPointComponent> "
            )
        )
        self.assertIn(
            "USkyguardBossWeakPointComponent",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertNotIn(
            "UStaticMeshComponent",
            COMMAND_ANTENNA_FIELD,
        )
        self.assertTrue(COMMAND_ANTENNA_FIELD.endswith(";"))
        self.assertNotIn("=", COMMAND_ANTENNA_FIELD)
        self.assertIn(UPROPERTY_ANTENNA, section)

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
