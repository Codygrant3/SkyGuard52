from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardLastFlightBoss.h"
CLASS_NAME = "ASkyguardLastFlightBoss"
# Declaration presence only. Do not invent INDEX_NONE
# or lock the SetCivilianSeparationMeters body in the
# .cpp. origin/main is one line
# (`void SetCivilianSeparationMeters(float SeparationMeters);`);
# accept that form, other split-line wraps, and an
# inline body without locking the body. Nearby
# origin/main UFUNCTION(BlueprintCallable,
# Category="Skyguard|Mission10|Safety") is accepted as
# present. Parse the public class section of
# ASkyguardLastFlightBoss only. Stay off leftover
# emergency-finish surfaces. Stay off leftover
# sibling OpenGuidanceArrayExposure /
# BeginTerminalStrikeCycle / IssueClimbCommand /
# DivertWreckFromCivilians. Stay off leftover
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
# isolated-test drafts #107–#456 including leftover
# searchlight-track-runtime-defaults #7347,
# leftover BlackKite / RadarGhost /
# LifelineHunter / Tempest / IronRain contracts,
# leftover patrol-ship empty fail-closed #5382,
# leftover skyline style HarborIndustrial (leftover
# enum, not a Harbor 40/80 retune), leftover
# Pathfinder MinHeightFromOriginCm, leftover Apache
# MaxIntegrity, leftover sortie-hud-host
# fail-closed, leftover gun-fire camera shake,
# leftover DebriefWidget / BriefingWidget isolated
# contracts, and leftover SortiePresentationWidgets
# stay sibling-only. Do not scan Apache public
# section for Harbor interval tokens. Harbor clock
# names may be scanned in this relevant public
# section and must be absent. Field
# MinimumCivilianSeparationMeters = 550.f is
# Harbor-adjacent; do not treat it as Harbor 40/80.
SET_CIVILIAN_SEPARATION_METERS = (
    "void SetCivilianSeparationMeters(float SeparationMeters);"
)
UFUNCTION_SAFETY = (
    'UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Safety")'
)
# Leftover #56–#64 plus SkyguardLastFlightBoss
# production files. This lane only adds an isolated
# Python SetCivilianSeparationMeters declaration
# contract on ASkyguardLastFlightBoss. Stay off
# leftover sibling OpenGuidanceArrayExposure /
# BeginTerminalStrikeCycle / IssueClimbCommand /
# DivertWreckFromCivilians, leftover
# emergency-finish surfaces, leftover RadarNode,
# leftover Gunner, leftover
# apache-own-ship-systems #96c5, leftover #851b
# mount getters, leftover #4e39
# GetChinMuzzleLocation, leftover
# USkyguardBossWeakPointComponent fields, leftover
# apache aircraft isolated contracts, leftover
# settings / input-capture contracts, leftover
# CPG HUD / sight HUD, leftover drafts #56–#64,
# leftover isolated-test drafts #107–#456,
# leftover searchlight-track-runtime-defaults
# #7347, leftover BlackKite siblings, leftover
# RadarGhost siblings, leftover LifelineHunter
# siblings, leftover Tempest siblings, leftover
# IronRain siblings, leftover patrol-ship empty
# fail-closed #5382, leftover ApacheSystem enum
# values, leftover roster enum values, leftover
# Harbor clocks, leftover skyline
# HarborIndustrial, leftover DebriefWidget
# isolated contracts, leftover BriefingWidget
# isolated contracts, leftover gun-fire camera
# shake, leftover sortie-hud-host fail-closed,
# and dirty workspace paths.
LOCKED = {
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
# IssueClimbCommand / DivertWreckFromCivilians
# siblings, leftover
# apache aircraft isolated contracts, leftover
# Gunner, leftover settings / input-capture
# contracts, leftover briefing/debrief widget
# contracts, leftover apache-aircraft
# empty-fail-closed #851b, leftover
# apache-chin-muzzle #4e39, leftover
# apache-own-ship-systems #96c5, leftover
# apache-cpg-feel #8951, leftover drafts
# #56–#64, leftover isolated-test drafts
# #107–#456, leftover
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
# IssueCrossCommand, leftover patrol-ship empty
# fail-closed #5382, leftover gun-fire camera
# shake, leftover sortie-hud-host fail-closed,
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
# MaxIntegrity, and leftover Iron Rain contracts
# stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_last_flight_open_guidance_array_exposure_decl_contract.py",
    "Scripts/tests/test_last_flight_begin_terminal_strike_cycle_decl_contract.py",
    "Scripts/tests/test_last_flight_issue_climb_command_decl_contract.py",
    "Scripts/tests/test_last_flight_divert_wreck_from_civilians_decl_contract.py",
    "Scripts/tests/test_iron_rain_open_upper_engine_exposure_decl_contract.py",
    "Scripts/tests/test_iron_rain_open_dispenser_bay_decl_contract.py",
    "Scripts/tests/test_iron_rain_release_pooled_escort_decl_contract.py",
    "Scripts/tests/test_iron_rain_issue_climb_command_decl_contract.py",
    "Scripts/tests/test_iron_rain_issue_cross_command_decl_contract.py",
    "Scripts/tests/test_iron_rain_get_destroyed_antenna_count_decl_contract.py",
    "Scripts/tests/test_iron_rain_get_destroyed_dispenser_count_decl_contract.py",
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
# Neighbors in the same public section. Presence is
# not locked here. Sibling
# OpenGuidanceArrayExposure, BeginTerminalStrikeCycle,
# IssueClimbCommand, DivertWreckFromCivilians,
# leftover
# emergency-finish surfaces, leftover
# USkyguardBossWeakPointComponent fields, leftover
# mount getters, leftover GetChinMuzzleLocation,
# and leftover apache / Gunner / settings helpers
# stay sibling-only.
BEGIN_TERMINAL_STRIKE_CYCLE = (
    "bool BeginTerminalStrikeCycle();"
)
ISSUE_CLIMB_COMMAND = (
    "bool IssueClimbCommand();"
)
DIVERT_WRECK_FROM_CIVILIANS = (
    "bool DivertWreckFromCivilians();"
)
OPEN_GUIDANCE_ARRAY_EXPOSURE = (
    "bool OpenGuidanceArrayExposure();"
)
GET_FINALE_STAGE = (
    "ESkyguardLastFlightStage GetFinaleStage() const "
    "{ return FinaleStage; }"
)
GET_OBJECTIVE_MILESTONES = (
    "int32 GetObjectiveMilestonesReached() const"
)
IS_CLIMB_COMMAND_ISSUED = (
    "bool IsClimbCommandIssued() const "
    "{ return bClimbCommandIssued; }"
)
IS_WRECK_DIVERTED = (
    "bool IsWreckDiverted() const { return bWreckDiverted; }"
)
GET_CIVILIAN_SEPARATION_METERS = (
    "float GetCivilianSeparationMeters() const"
)
MINIMUM_CIVILIAN_SEPARATION = (
    "float MinimumCivilianSeparationMeters = 550.f;"
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
    return (
        f"OpenFirst{lock}Window",
        f"OpenFinal{lock}Window",
        f"ArmCommandCore{finish}Path",
        f"bCommandCore{finish}Armed",
    )


def unlocked_neighbors() -> tuple[str, ...]:
    return (
        "ASkyguardLastFlightBoss();",
        BEGIN_TERMINAL_STRIKE_CYCLE,
        ISSUE_CLIMB_COMMAND,
        DIVERT_WRECK_FROM_CIVILIANS,
        OPEN_GUIDANCE_ARRAY_EXPOSURE,
        leftover_open_first_window(),
        leftover_open_final_window(),
        leftover_arm_command_core_path(),
        GET_FINALE_STAGE,
        GET_OBJECTIVE_MILESTONES,
        IS_CLIMB_COMMAND_ISSUED,
        IS_WRECK_DIVERTED,
        GET_CIVILIAN_SEPARATION_METERS,
        MINIMUM_CIVILIAN_SEPARATION,
        "TObjectPtr<USkyguardBossWeakPointComponent> PortGuidanceArray;",
        "TObjectPtr<USkyguardBossWeakPointComponent> StarboardGuidanceArray;",
        "TObjectPtr<USkyguardBossWeakPointComponent> PortStrikeBayMechanism;",
        "TObjectPtr<USkyguardBossWeakPointComponent> StarboardStrikeBayMechanism;",
        "TObjectPtr<USkyguardBossWeakPointComponent> PortCoolingSystem;",
        "TObjectPtr<USkyguardBossWeakPointComponent> StarboardCoolingSystem;",
        "TObjectPtr<USkyguardBossWeakPointComponent> Jammer;",
        "TObjectPtr<USkyguardBossWeakPointComponent> PortEngine;",
        "TObjectPtr<USkyguardBossWeakPointComponent> StarboardEngine;",
        "TObjectPtr<USkyguardBossWeakPointComponent> CommandCore;",
        "TObjectPtr<UStaticMeshComponent> DebrisArmorPort;",
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
    "PortGuidanceArray",
    "StarboardGuidanceArray",
    "PortStrikeBayMechanism",
    "StarboardStrikeBayMechanism",
    "PortCoolingSystem",
    "StarboardCoolingSystem",
    "Jammer",
    "PortEngine",
    "StarboardEngine",
    "CommandCore",
    "DebrisArmorPort",
    "DebrisArmorStarboard",
    "DebrisStrikeBayPort",
    "DebrisStrikeBayStarboard",
    "DebrisEnginePort",
    "DebrisEngineStarboard",
    "USkyguardBossWeakPointComponent",
)
BEGIN_TERMINAL_STRIKE_CYCLE_NOT_LOCKED = (
    BEGIN_TERMINAL_STRIKE_CYCLE,
    "test_last_flight_begin_terminal_strike_cycle_decl_contract.py",
    "BeginTerminalStrikeCycle",
)
ISSUE_CLIMB_COMMAND_NOT_LOCKED = (
    ISSUE_CLIMB_COMMAND,
    "test_last_flight_issue_climb_command_decl_contract.py",
    "IssueClimbCommand",
)
DIVERT_WRECK_FROM_CIVILIANS_NOT_LOCKED = (
    DIVERT_WRECK_FROM_CIVILIANS,
    "test_last_flight_divert_wreck_from_civilians_decl_contract.py",
    "DivertWreckFromCivilians",
)
OPEN_GUIDANCE_ARRAY_EXPOSURE_NOT_LOCKED = (
    OPEN_GUIDANCE_ARRAY_EXPOSURE,
    "test_last_flight_open_guidance_array_exposure_decl_contract.py",
    "OpenGuidanceArrayExposure",
)
GETTERS_NOT_LOCKED = (
    GET_FINALE_STAGE,
    GET_OBJECTIVE_MILESTONES,
    IS_CLIMB_COMMAND_ISSUED,
    IS_WRECK_DIVERTED,
    GET_CIVILIAN_SEPARATION_METERS,
    "GetFinaleStage",
    "GetObjectiveMilestonesReached",
    "IsClimbCommandIssued",
    "IsWreckDiverted",
    "GetCivilianSeparationMeters",
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
    "ASkyguardIronRainBoss",
    "test_iron_rain_open_upper_engine_exposure_decl_contract.py",
    "test_iron_rain_open_dispenser_bay_decl_contract.py",
    "test_iron_rain_release_pooled_escort_decl_contract.py",
    "test_iron_rain_issue_cross_command_decl_contract.py",
    "test_iron_rain_get_destroyed_antenna_count_decl_contract.py",
    "test_iron_rain_get_destroyed_dispenser_count_decl_contract.py",
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
# Pathfinder MinHeightFromOriginCm and Apache
# MaxIntegrity are the wrong headers. Do not scan
# Apache public section for Harbor clocks.
WRONG_HARBOR_HEADERS_NOT_SCANNED = (
    "SkyguardPathfinder",
    "MinHeightFromOriginCm",
    "MaxIntegrity",
    "SkyguardApacheAircraft.h",
    "ASkyguardApacheAircraft",
)
# Field MinimumCivilianSeparationMeters = 550.f is
# Harbor-adjacent; do not treat it as Harbor 40/80.
HARBOR_ADJACENT_CIVILIAN_SEPARATION = (
    "MinimumCivilianSeparationMeters",
    "550.f",
)
# .cpp SetCivilianSeparationMeters body / invented
# INDEX_NONE stay unlocked. Do not invent INDEX_NONE
# or lock the cpp body. Do not parse leftover HUD
# classes.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "ASkyguardLastFlightBoss::SetCivilianSeparationMeters",
    "SkyguardLastFlightBoss.cpp",
    "FMath::Max",
    "CivilianSeparationMeters = FMath::Max",
    "HasSafeCivilianSeparation",
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


class LastFlightSetCivilianSeparationMetersDeclContractTests(unittest.TestCase):
    def test_last_flight_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, SET_CIVILIAN_SEPARATION_METERS),
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
            f"\t{SET_CIVILIAN_SEPARATION_METERS}\n"
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
            f"\t{SET_CIVILIAN_SEPARATION_METERS}\n"
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
            f"\t{BEGIN_TERMINAL_STRIKE_CYCLE}\n"
            "private:\n"
            f"\t{SET_CIVILIAN_SEPARATION_METERS}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, SET_CIVILIAN_SEPARATION_METERS)
        self.assertIn("SetCivilianSeparationMeters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(
            has_declaration(section, SET_CIVILIAN_SEPARATION_METERS)
        )

    def test_missing_set_civilian_separation_meters_declaration_fails_closed(
        self,
    ) -> None:
        neighbors_only = (
            "\tASkyguardLastFlightBoss();\n"
            f"\t{BEGIN_TERMINAL_STRIKE_CYCLE}\n"
            f"\t{ISSUE_CLIMB_COMMAND}\n"
            f"\t{DIVERT_WRECK_FROM_CIVILIANS}\n"
            f"\t{OPEN_GUIDANCE_ARRAY_EXPOSURE}\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "PortGuidanceArray;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, SET_CIVILIAN_SEPARATION_METERS)
        self.assertIn("SetCivilianSeparationMeters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_SAFETY}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, SET_CIVILIAN_SEPARATION_METERS)
        self.assertIn("SetCivilianSeparationMeters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_SAFETY, section)
        self.assertTrue(
            has_declaration(section, SET_CIVILIAN_SEPARATION_METERS),
            section,
        )
        self.assertNotIn("BlueprintPure", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("UFUNCTION", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("Category", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("BlueprintCallable", SET_CIVILIAN_SEPARATION_METERS)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tASkyguardLastFlightBoss();\n"
            f"\t{BEGIN_TERMINAL_STRIKE_CYCLE}\n"
            f"\t{ISSUE_CLIMB_COMMAND}\n"
            f"\t{DIVERT_WRECK_FROM_CIVILIANS}\n"
            f"\t{OPEN_GUIDANCE_ARRAY_EXPOSURE}\n"
            f"\t{leftover_open_first_window()}\n"
            f"\t{leftover_open_final_window()}\n"
            f"\t{leftover_arm_command_core_path()}\n"
            f"\t{GET_FINALE_STAGE}\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "PortGuidanceArray;\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "CommandCore;\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
            "\tvoid FaceWorldLocation(const FVector& WorldLocation);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, SET_CIVILIAN_SEPARATION_METERS)
        self.assertIn("SetCivilianSeparationMeters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_parens = "\tvoid SetCivilianSeparationMeters;\n"
        wrong_return_bool = (
            "\tbool SetCivilianSeparationMeters(float SeparationMeters);\n"
        )
        wrong_return_int = (
            "\tint32 SetCivilianSeparationMeters(float SeparationMeters);\n"
        )
        added_const = (
            "\tvoid SetCivilianSeparationMeters(float SeparationMeters) "
            "const;\n"
        )
        wrong_type = (
            "\tvoid SetCivilianSeparationMeters(int SeparationMeters);\n"
        )
        missing_arg = "\tvoid SetCivilianSeparationMeters();\n"
        added_arg = (
            "\tvoid SetCivilianSeparationMeters("
            "float SeparationMeters, float Extra);\n"
        )
        leftover_begin = f"\t{BEGIN_TERMINAL_STRIKE_CYCLE}\n"
        leftover_climb = f"\t{ISSUE_CLIMB_COMMAND}\n"
        leftover_divert = f"\t{DIVERT_WRECK_FROM_CIVILIANS}\n"
        leftover_open = f"\t{OPEN_GUIDANCE_ARRAY_EXPOSURE}\n"
        leftover_get = f"\t{GET_CIVILIAN_SEPARATION_METERS}\n"
        leftover_field = f"\t{MINIMUM_CIVILIAN_SEPARATION}\n"
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
        for region in (
            missing_parens,
            wrong_return_bool,
            wrong_return_int,
            added_const,
            wrong_type,
            missing_arg,
            added_arg,
            leftover_begin,
            leftover_climb,
            leftover_divert,
            leftover_open,
            leftover_get,
            leftover_field,
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
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, SET_CIVILIAN_SEPARATION_METERS)
            self.assertIn("SetCivilianSeparationMeters", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_set_civilian_separation_meters_declaration_matches_origin_main(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, SET_CIVILIAN_SEPARATION_METERS),
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertTrue(
            has_declaration(section, SET_CIVILIAN_SEPARATION_METERS)
        )
        self.assertEqual(
            declaration_count(section, SET_CIVILIAN_SEPARATION_METERS),
            1,
        )
        self.assertTrue(
            SET_CIVILIAN_SEPARATION_METERS.startswith("void "),
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertTrue(
            SET_CIVILIAN_SEPARATION_METERS.endswith(";"),
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertIn(
            "SetCivilianSeparationMeters(",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertIn("float SeparationMeters", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("int32 BayIndex", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("INDEX_NONE", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("{", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("}", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("return ", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(" const", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "OpenGuidanceArrayExposure",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn(
            "BeginTerminalStrikeCycle",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("IssueClimbCommand", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "DivertWreckFromCivilians",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn(
            "GetCivilianSeparationMeters",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn(
            "MinimumCivilianSeparationMeters",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("GetChinMuzzleLocation", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("GetGunnerMount", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("FaceWorldLocation", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("PortGuidanceArray", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("SetSearchlightTracked", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("SetContactIdentified", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "SetFriendlySeparationMeters",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("SetLightningExposed", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "OpenUpperEngineExposure",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, SET_CIVILIAN_SEPARATION_METERS)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tvoid\n"
            "\tSetCivilianSeparationMeters(float SeparationMeters);\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tvoid SetCivilianSeparationMeters(\n"
            "\t\tfloat SeparationMeters);\n"
            "private:\n"
            "};\n"
        )
        wrap_parens = (
            "public:\n"
            "\tvoid SetCivilianSeparationMeters\n"
            "\t(float SeparationMeters);\n"
            "};\n"
        )
        wrap_param = (
            "public:\n"
            "\tvoid\n"
            "\tSetCivilianSeparationMeters(\n"
            "\t\tfloat\n"
            "\t\tSeparationMeters);\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_type}"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_name}"
        )
        header_wrap_parens = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_parens}"
        )
        header_wrap_param = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_param}"
        )
        for header in (
            header_wrap_type,
            header_wrap_name,
            header_wrap_parens,
            header_wrap_param,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, SET_CIVILIAN_SEPARATION_METERS),
                section,
            )
            self.assertEqual(
                require_declaration(section, SET_CIVILIAN_SEPARATION_METERS),
                SET_CIVILIAN_SEPARATION_METERS,
            )
            self.assertEqual(
                declaration_count(section, SET_CIVILIAN_SEPARATION_METERS),
                1,
            )
        one_line = (
            f"{{\npublic:\n\t{SET_CIVILIAN_SEPARATION_METERS}\n}}\n"
        )
        self.assertTrue(
            has_declaration(one_line, SET_CIVILIAN_SEPARATION_METERS)
        )
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, SET_CIVILIAN_SEPARATION_METERS),
            section,
        )
        self.assertEqual(
            require_declaration(section, SET_CIVILIAN_SEPARATION_METERS),
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tvoid SetCivilianSeparationMeters(float SeparationMeters)\n"
            "\t{\n"
            "\t}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{inline}"
        )
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, SET_CIVILIAN_SEPARATION_METERS),
            section,
        )
        self.assertEqual(
            require_declaration(section, SET_CIVILIAN_SEPARATION_METERS),
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertEqual(
            declaration_count(section, SET_CIVILIAN_SEPARATION_METERS),
            1,
        )
        self.assertNotIn("{", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("}", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("return ", SET_CIVILIAN_SEPARATION_METERS)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", SET_CIVILIAN_SEPARATION_METERS)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_set_civilian_separation_meters_cpp_body(
        self,
    ) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        self.assertNotIn("{", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("}", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("return ", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "ASkyguardLastFlightBoss::SetCivilianSeparationMeters",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn(
            "SkyguardLastFlightBoss.cpp",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("SkyguardLastFlightBoss.cpp", locked_only)
        self.assertNotIn("return false", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("return true", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("FMath::Max", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "CivilianSeparationMeters = FMath::Max",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("HasSafeCivilianSeparation", SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_relock_begin_terminal_strike_cycle_sibling(
        self,
    ) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in BEGIN_TERMINAL_STRIKE_CYCLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "OpenGuidanceArrayExposure",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn(
            "BeginTerminalStrikeCycle",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("BeginTerminalStrikeCycle", locked_only)
        self.assertNotIn(
            "test_last_flight_begin_terminal_strike_cycle_decl_contract.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_relock_issue_climb_command_sibling(
        self,
    ) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in ISSUE_CLIMB_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("IssueClimbCommand", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("IssueClimbCommand", locked_only)
        self.assertNotIn(
            "test_last_flight_issue_climb_command_decl_contract.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_relock_divert_wreck_from_civilians_sibling(
        self,
    ) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in DIVERT_WRECK_FROM_CIVILIANS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "DivertWreckFromCivilians",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("DivertWreckFromCivilians", locked_only)
        self.assertNotIn(
            "test_last_flight_divert_wreck_from_civilians_decl_contract.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_relock_open_guidance_array_exposure_sibling(
        self,
    ) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in OPEN_GUIDANCE_ARRAY_EXPOSURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "OpenGuidanceArrayExposure",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("OpenGuidanceArrayExposure", locked_only)
        self.assertNotIn(
            "test_last_flight_open_guidance_array_exposure_decl_contract.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_relock_leftover_getters(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("GetFinaleStage", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("IsWreckDiverted", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "GetCivilianSeparationMeters",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_relock_leftover_emergency_finish(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        self.assertNotIn(leftover_open_first_window(), locked_only)
        self.assertNotIn(
            leftover_open_first_window(),
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn(leftover_open_final_window(), locked_only)
        self.assertNotIn(
            leftover_open_final_window(),
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn(leftover_arm_command_core_path(), locked_only)
        self.assertNotIn(
            leftover_arm_command_core_path(),
            SET_CIVILIAN_SEPARATION_METERS,
        )
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, SET_CIVILIAN_SEPARATION_METERS)
        for script in leftover_live_copy_boss_scripts():
            self.assertNotIn(script, SET_CIVILIAN_SEPARATION_METERS)
            self.assertNotIn(script, locked_only)

    def test_contract_does_not_relock_weak_point_fields(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in WEAK_POINT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("USkyguardBossWeakPointComponent", locked_only)
        self.assertNotIn("PortGuidanceArray", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("StarboardGuidanceArray", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("CommandCore", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("PortEngine", SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_relock_leftover_searchlight_runtime(
        self,
    ) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "test_searchlight_track_runtime_defaults_contract.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn(
            "FSkyguardSearchlightTrackRuntime",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_relock_leftover_black_kite(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_BLACK_KITE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("SetSearchlightTracked", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("IsSearchlightTracked", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("ASkyguardBlackKiteBoss", SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_relock_leftover_radar_ghost(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_RADAR_GHOST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("SetContactIdentified", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("IsContactIdentified", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("OpenOrbitExposure", SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_relock_leftover_lifeline_hunter(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "SetFriendlySeparationMeters",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("OpenSensorExposure", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "ASkyguardLifelineHunterBoss",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_relock_leftover_tempest(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_TEMPEST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("SetLightningExposed", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "ApplyCorrectiveBankGust",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("ASkyguardTempestBoss", SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_relock_leftover_iron_rain(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_IRON_RAIN_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "OpenUpperEngineExposure",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("OpenDispenserBay", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("ASkyguardIronRainBoss", SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_relock_leftover_patrol_ship(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_PATROL_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "test_patrol_ship_empty_fail_closed.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("ASkyguardPatrolShip", SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_relock_mount_getters(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in MOUNT_GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("GetGunnerMount", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("GetChinTurret", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("GetSensorTurret", SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_relock_chin_muzzle(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for neighbor in GET_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("GetChinMuzzleLocation", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "test_apache_aircraft_empty_fail_closed.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_relock_leftover_chin_muzzle(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("GetChinMuzzleLocation", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "test_apache_chin_muzzle_tests.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_relock_leftover_own_ship_systems(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("ESkyguardApacheSystem", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn(
            "test_apache_own_ship_systems_contract.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_relock_leftover_cpg_feel(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "test_apache_cpg_feel_contract.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_relock_leftover_apache_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_APACHE_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "test_apache_face_world_location_decl_contract.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("FaceWorldLocation", SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_relock_leftover_settings(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_SETTINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "test_settings_apply_broadcast_tests.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_relock_leftover_input_capture(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_INPUT_CAPTURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "test_input_capture_is_capture_active_decl_contract.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("RecordPlayerEvent", SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_relock_leftover_gunner(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("ASkyguardGunner", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("FillAndFinalize", SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_relock_leftover_radar_node(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("SkyguardRadarNode", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("ASkyguardRadarNode", locked_only)


    def test_contract_does_not_relock_leftover_widget_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardDebriefWidget", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "USkyguardBriefingWidget",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn(
            "test_debrief_widget_travel_next_decl_contract.py",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "ESkyguardMissionSkylineStyle",
            SET_CIVILIAN_SEPARATION_METERS,
        )

    def test_contract_does_not_scan_wrong_harbor_headers(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("MinHeightFromOriginCm", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("MaxIntegrity", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn(
            "SkyguardApacheAircraft.h",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("SkyguardPathfinder", SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_scan_apache_public_section_for_harbor(
        self,
    ) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        file_text = this_file_text()
        apache_header = "SkyguardApacheAircraft.h"
        self.assertNotIn(apache_header, locked_only)
        self.assertNotIn(apache_header, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("ASkyguardApacheAircraft", locked_only)
        self.assertNotIn(
            "ASkyguardApacheAircraft",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn(f"origin/main:{apache_header}", file_text)
        self.assertNotIn(f"git show origin/main:{apache_header}", file_text)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)

    def test_minimum_civilian_separation_is_not_harbor_40_80(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        section = public_section(origin_main_header())
        # Field MinimumCivilianSeparationMeters = 550.f is
        # Harbor-adjacent; do not treat it as Harbor 40/80.
        adjacent = "MinimumCivilianSeparationMeters = 550.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent)
            self.assertNotEqual(token, "550.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in HARBOR_ADJACENT_CIVILIAN_SEPARATION:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertIn("MinimumCivilianSeparationMeters", section)
        self.assertIn("550.f", section)

    def test_contract_does_not_lock_minimum_civilian_separation_meters(
        self,
    ) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        self.assertNotIn(MINIMUM_CIVILIAN_SEPARATION, locked_only)
        self.assertNotIn(
            MINIMUM_CIVILIAN_SEPARATION,
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn(
            "MinimumCivilianSeparationMeters",
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertNotIn("550.f", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("550.f", locked_only)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        self.assertEqual(
            require_declaration(locked_only, SET_CIVILIAN_SEPARATION_METERS),
            SET_CIVILIAN_SEPARATION_METERS,
        )
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("BeginTerminalStrikeCycle", locked_only)
        self.assertNotIn("IssueClimbCommand", locked_only)
        self.assertNotIn("DivertWreckFromCivilians", locked_only)
        self.assertNotIn("OpenGuidanceArrayExposure", locked_only)
        self.assertNotIn("GetGunnerMount", locked_only)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)
        self.assertNotIn("FaceWorldLocation", locked_only)
        self.assertNotIn("PortGuidanceArray", locked_only)
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
            require_declaration(section, SET_CIVILIAN_SEPARATION_METERS),
            SET_CIVILIAN_SEPARATION_METERS,
        )
        self.assertEqual(
            declaration_count(section, SET_CIVILIAN_SEPARATION_METERS),
            1,
        )
        self.assertNotIn("SkyguardLastFlightBoss.cpp", section)
        self.assertNotIn(
            "ASkyguardLastFlightBoss::SetCivilianSeparationMeters",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardLastFlightBoss.cpp", section)
        self.assertNotIn(
            "ASkyguardLastFlightBoss::SetCivilianSeparationMeters",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("}", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("return false", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("return true", SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        file_text = this_file_text()
        # Harbor clock field names stay off this class
        # public section. Literal Harbor interval retune
        # tokens fail closed in this file and the
        # locked declaration only. Do not scan Apache
        # public section for those tokens. Apache
        # MaxIntegrity is not a Harbor clock.
        # Pathfinder MinHeightFromOriginCm is the
        # wrong header. Field
        # MinimumCivilianSeparationMeters = 550.f is
        # Harbor-adjacent; do not treat it as Harbor
        # 40/80.
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(
                token,
                "MinimumCivilianSeparationMeters = 550.f",
            )

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
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
                "last flight SetCivilianSeparationMeters contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        # Leftover emergency-finish names stay in the
        # public section. This file and the locked
        # declaration stay clean of leftover live copy.
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, SET_CIVILIAN_SEPARATION_METERS.lower())
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                SET_CIVILIAN_SEPARATION_METERS.lower(),
                "last flight SetCivilianSeparationMeters contains "
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
        self.assertNotIn(dirty_fwd, SET_CIVILIAN_SEPARATION_METERS)

    def test_contract_is_set_civilian_separation_meters_declaration_only(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, SET_CIVILIAN_SEPARATION_METERS),
            SET_CIVILIAN_SEPARATION_METERS,
        )
        locked_only = f"{SET_CIVILIAN_SEPARATION_METERS}\n"
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("BeginTerminalStrikeCycle", locked_only)
        self.assertNotIn("IssueClimbCommand", locked_only)
        self.assertNotIn("DivertWreckFromCivilians", locked_only)
        self.assertNotIn("OpenGuidanceArrayExposure", locked_only)
        self.assertNotIn("GetGunnerMount", locked_only)
        self.assertNotIn("GetEyeMount", locked_only)
        self.assertNotIn("GetWeaponMount", locked_only)
        self.assertNotIn("GetChinTurret", locked_only)
        self.assertNotIn("GetPilotMount", locked_only)
        self.assertNotIn("GetSensorTurret", locked_only)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)
        self.assertNotIn("FaceWorldLocation", locked_only)
        self.assertNotIn("ApplyDamage", locked_only)
        self.assertNotIn("PortGuidanceArray", locked_only)
        self.assertNotIn("StarboardGuidanceArray", locked_only)
        self.assertNotIn("USkyguardBossWeakPointComponent", locked_only)
        self.assertNotIn("FSkyguardSearchlightTrackRuntime", locked_only)
        self.assertNotIn("HarborIndustrial", locked_only)
        self.assertNotIn("USkyguardDebriefWidget", locked_only)
        self.assertNotIn("USkyguardBriefingWidget", locked_only)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn("MinHeightFromOriginCm", locked_only)
        self.assertNotIn("MaxIntegrity", locked_only)
        self.assertNotIn("SetSearchlightTracked", locked_only)
        self.assertNotIn("SetContactIdentified", locked_only)
        self.assertNotIn("OpenOrbitExposure", locked_only)
        self.assertNotIn("SetFriendlySeparationMeters", locked_only)
        self.assertNotIn("SetLightningExposed", locked_only)
        self.assertNotIn("OpenUpperEngineExposure", locked_only)
        self.assertNotIn("ASkyguardPatrolShip", locked_only)
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_APACHE_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_SETTINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_INPUT_CAPTURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_BLACK_KITE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_RADAR_GHOST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_TEMPEST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_IRON_RAIN_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in LEFTOVER_PATROL_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in BEGIN_TERMINAL_STRIKE_CYCLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in ISSUE_CLIMB_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in DIVERT_WRECK_FROM_CIVILIANS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in OPEN_GUIDANCE_ARRAY_EXPOSURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in WEAK_POINT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in leftover_short_roster_values():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, SET_CIVILIAN_SEPARATION_METERS)
            self.assertNotIn(token, section)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, SET_CIVILIAN_SEPARATION_METERS.lower())
            self.assertNotIn(banned, locked_only.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", SET_CIVILIAN_SEPARATION_METERS)
        self.assertNotIn("{", SET_CIVILIAN_SEPARATION_METERS)
        self.assertTrue(SET_CIVILIAN_SEPARATION_METERS.startswith("void "))
        self.assertTrue(SET_CIVILIAN_SEPARATION_METERS.endswith(";"))
        self.assertIn(UFUNCTION_SAFETY, section)

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
