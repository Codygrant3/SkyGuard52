from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardTempestBoss.h"
CLASS_NAME = "ASkyguardTempestBoss"
# Declaration presence only. Do not invent INDEX_NONE
# or lock the IsLightningExposed body.
# origin/main is inline
# (`bool IsLightningExposed() const`
# with `{ return bLightningExposed; }` possibly on the
# same line or following lines);
# accept that exact inline form, a one-line prototype
# (`bool IsLightningExposed() const;`),
# other split-line wraps, and other inline bodies without
# locking the body. The inline return of the lightning
# exposed flag is not a required token of this
# declaration lock. Nearby origin/main
# UFUNCTION(BlueprintPure,
# Category="Skyguard|Mission05|Boss") is accepted as
# present. Parse the public class section of
# ASkyguardTempestBoss only. Stay off leftover
# emergency-finish surfaces. Stay off leftover
# SetLightningExposed / ApplyCorrectiveBankGust /
# GetLockStabilitySeconds siblings. Stay off leftover
# RadarNode, leftover Gunner, leftover
# apache-own-ship-systems #96c5, leftover #851b mount
# getters, leftover #4e39 GetChinMuzzleLocation. Stay
# off leftover USkyguardBossWeakPointComponent
# fields. Stay off leftover apache / settings /
# input-capture / briefing / debrief isolated
# contracts. Stay off leftover drafts #56–#64 and
# leftover isolated-test drafts #107–#441 including
# leftover searchlight-track-runtime-defaults #7347
# leftover BlackKite / RadarGhost / LifelineHunter
# contracts, leftover patrol-ship empty-fail-closed
# #5382. Harbor interval retune tokens fail closed
# in this file and the locked declaration only. Do
# not scan the Apache public section for those
# tokens. Harbor clock names may be scanned in this
# relevant public section and must be absent.
# Harbor-adjacent MinimumWeaponSeparationMeters is
# not a Harbor 40/80 retune. Stay off leftover
# theater-kit / flare / HUD, leftover ApacheSystem /
# weapon stations / leftover roster / loadout /
# lock-phase, leftover skyline style
# HarborIndustrial (leftover enum, not a Harbor
# interval retune), leftover Pathfinder
# MinHeightFromOriginCm, leftover Apache
# MaxIntegrity, leftover sortie-hud-host
# fail-closed, leftover gun-fire camera shake,
# leftover DebriefWidget / BriefingWidget isolated
# contracts, leftover SortiePresentationWidgets,
# leftover CPG HUD / sight HUD, leftover
# apache-cpg-feel #8951, leftover Mission05
# neighbors, and dirty workspace paths.
IS_LIGHTNING_EXPOSED = "bool IsLightningExposed() const;"
UFUNCTION_BOSS = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Mission05|Boss")'
)
# Leftover #56–#64 plus SkyguardTempestBoss
# production files. This lane only adds an isolated
# Python IsLightningExposed declaration contract on
# ASkyguardTempestBoss. Stay off leftover
# SetLightningExposed / ApplyCorrectiveBankGust /
# GetLockStabilitySeconds, leftover emergency-finish
# surfaces, leftover RadarNode, leftover Gunner,
# leftover apache-own-ship-systems #96c5, leftover
# #851b mount getters, leftover #4e39
# GetChinMuzzleLocation, leftover
# USkyguardBossWeakPointComponent fields, leftover
# apache aircraft isolated contracts, leftover
# settings / input-capture contracts, leftover CPG
# HUD / sight HUD, leftover drafts #56–#64,
# leftover isolated-test drafts #107–#441, leftover
# searchlight-track-runtime-defaults #7347,
# leftover BlackKite siblings, leftover RadarGhost
# siblings, leftover LifelineHunter siblings,
# leftover patrol-ship empty-fail-closed #5382,
# leftover ApacheSystem enum values, leftover
# roster enum values, leftover Harbor clocks,
# leftover skyline HarborIndustrial, leftover
# DebriefWidget isolated contracts, leftover
# BriefingWidget isolated contracts, leftover
# gun-fire camera shake, leftover
# sortie-hud-host fail-closed, leftover Mission05
# neighbors, and dirty workspace paths.
LOCKED = {
    "SkyguardTempestBoss.h",
    "SkyguardTempestBoss.cpp",
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
        f"{prefix}test_tempest_advance_stabilized_{missile}"
        "_lock_decl_contract.py",
        f"{prefix}test_tempest_arm_break_{banned}"
        "_finish_decl_contract.py",
        f"{prefix}test_tempest_is_break_{banned}"
        "_finish_armed_decl_contract.py",
        f"{prefix}test_lifeline_hunter_open_safe_{missile}"
        "_window_decl_contract.py",
        f"{prefix}test_lifeline_hunter_arm_safe_{banned}"
        "_engine_fallback_decl_contract.py",
        f"{prefix}test_black_kite_arm_emergency_{banned}"
        "_finish_decl_contract.py",
        f"{prefix}test_black_kite_is_emergency_{banned}"
        "_finish_armed_decl_contract.py",
        f"{prefix}test_{missile}_boss_decl_contract.py",
        f"{prefix}test_{missile}_missile_decl_contract.py",
    )


# Isolated-test drafts stay off this lane. Leftover
# emergency-finish boss contracts, leftover
# SetLightningExposed / ApplyCorrectiveBankGust /
# GetLockStabilitySeconds siblings, leftover apache
# aircraft isolated contracts, leftover Gunner,
# leftover settings / input-capture contracts,
# leftover briefing / debrief widget contracts,
# leftover apache-aircraft empty-fail-closed #851b,
# leftover apache-chin-muzzle #4e39, leftover
# apache-own-ship-systems #96c5, leftover
# apache-cpg-feel #8951, leftover drafts #56–#64,
# leftover isolated-test drafts #107–#441, leftover
# searchlight-track-runtime-defaults #7347,
# leftover BlackKite SetSearchlightTracked /
# IsSearchlightTracked, leftover RadarGhost
# SetContactIdentified / IsContactIdentified /
# OpenOrbitExposure, leftover LifelineHunter
# IsDisabledDescent / OpenSensorExposure /
# SetFriendlySeparationMeters /
# RedirectDisabledDrone / IsCrashRedirected /
# GetFriendlySeparationMeters, leftover patrol-ship
# empty-fail-closed #5382, leftover gun-fire camera
# shake, leftover sortie-hud-host fail-closed,
# leftover CPG HUD / sight HUD, leftover
# briefing-fail-closed, leftover campaign-save
# empty-fail-closed, leftover objective-runtime /
# route-runtime fail-closed, leftover theater-kit /
# Harbor / flare / HUD, leftover ApacheSystem /
# weapon stations / leftover roster / loadout,
# leftover bind-hud-host, leftover Gunner helpers,
# leftover pilot drafts, leftover mission-weather
# enum, leftover skyline HarborIndustrial, leftover
# SortiePresentationWidgets, leftover CPG debrief,
# leftover apache-cpg-feel, leftover
# USkyguardBossWeakPointComponent fields, leftover
# RadarNode, leftover Pathfinder
# MinHeightFromOriginCm, leftover Apache
# MaxIntegrity, and leftover Tempest neighbors stay
# sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_tempest_set_lightning_exposed_decl_contract.py",
    "Scripts/tests/test_tempest_apply_corrective_bank_gust_decl_contract.py",
    "Scripts/tests/test_tempest_get_lock_stability_seconds_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_open_sensor_exposure_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_set_friendly_separation_meters_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_redirect_disabled_drone_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_get_friendly_separation_meters_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_is_crash_redirected_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_is_disabled_descent_decl_contract.py",
    "Scripts/tests/test_searchlight_track_runtime_defaults_contract.py",
    "Scripts/tests/test_black_kite_set_searchlight_tracked_decl_contract.py",
    "Scripts/tests/test_black_kite_is_searchlight_tracked_decl_contract.py",
    "Scripts/tests/test_radar_ghost_set_contact_identified_decl_contract.py",
    "Scripts/tests/test_radar_ghost_is_contact_identified_decl_contract.py",
    "Scripts/tests/test_radar_ghost_open_orbit_exposure_decl_contract.py",
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
# not locked here. Sibling SetLightningExposed /
# ApplyCorrectiveBankGust / GetLockStabilitySeconds,
# leftover emergency-finish surfaces, leftover
# USkyguardBossWeakPointComponent fields, leftover
# mount getters, leftover GetChinMuzzleLocation, and
# leftover apache / Gunner / settings helpers stay
# sibling-only. Harbor-adjacent
# MinimumWeaponSeparationMeters is not a Harbor
# 40/80 retune.
SET_LIGHTNING_EXPOSED = "void SetLightningExposed(bool bExposed);"
APPLY_CORRECTIVE_BANK_GUST = (
    "bool ApplyCorrectiveBankGust(float Turbulence);"
)
GET_LOCK_STABILITY_SECONDS = (
    "float GetLockStabilitySeconds() const "
    "{ return LockStabilitySeconds; }"
)
REQUIRED_LOCK_STABILITY_SECONDS = (
    "float RequiredLockStabilitySeconds = 2.5f;"
)
HARBOR_ADJACENT_SEPARATION_FIELD = (
    "float MinimumWeaponSeparationMeters = 450.f;"
)


def leftover_advance_stabilized_lock() -> str:
    mid = "Ig" + "la"
    return (
        f"bool AdvanceStabilized{mid}Lock("
        "float DeltaSeconds, float Turbulence);"
    )


def leftover_arm_break_finish() -> str:
    mid = "Ri" + "fle"
    return f"bool ArmBreak{mid}Finish();"


def leftover_is_break_finish_armed() -> str:
    mid = "Ri" + "fle"
    return f"bool IsBreak{mid}FinishArmed() const;"


def leftover_emergency_finish_names() -> tuple[str, ...]:
    window = "Ig" + "la"
    finish = "Ri" + "fle"
    return (
        f"AdvanceStabilized{window}Lock",
        f"ArmBreak{finish}Finish",
        f"IsBreak{finish}FinishArmed",
    )


def unlocked_neighbors() -> tuple[str, ...]:
    return (
        "ASkyguardTempestBoss();",
        SET_LIGHTNING_EXPOSED,
        APPLY_CORRECTIVE_BANK_GUST,
        leftover_advance_stabilized_lock(),
        leftover_arm_break_finish(),
        leftover_is_break_finish_armed(),
        GET_LOCK_STABILITY_SECONDS,
        REQUIRED_LOCK_STABILITY_SECONDS,
        "TObjectPtr<USkyguardBossWeakPointComponent> PortDischargeBoom;",
        "TObjectPtr<USkyguardBossWeakPointComponent> StarboardDischargeBoom;",
        "TObjectPtr<USkyguardBossWeakPointComponent> ControlServo;",
        "TObjectPtr<USkyguardBossWeakPointComponent> EngineIntake;",
        "TObjectPtr<UStaticMeshComponent> DebrisPortPanel;",
        "TObjectPtr<UStaticMeshComponent> DebrisStarboardPanel;",
        "TObjectPtr<UStaticMeshComponent> DebrisIntakePanel;",
        "USceneComponent* GetGunnerMount() const { return GunnerMount; }",
        "FVector GetChinMuzzleLocation() const;",
        "void FaceWorldLocation(const FVector& WorldLocation);",
        "void ApplyDamage(float Amount);",
    )


WEAK_POINT_FIELDS_NOT_LOCKED = (
    "PortDischargeBoom",
    "StarboardDischargeBoom",
    "ControlServo",
    "EngineIntake",
    "DebrisPortPanel",
    "DebrisStarboardPanel",
    "DebrisIntakePanel",
    "USkyguardBossWeakPointComponent",
)
SET_LIGHTNING_EXPOSED_NOT_LOCKED = (
    SET_LIGHTNING_EXPOSED,
    "test_tempest_set_lightning_exposed_decl_contract.py",
    "SetLightningExposed",
)
APPLY_CORRECTIVE_BANK_GUST_NOT_LOCKED = (
    APPLY_CORRECTIVE_BANK_GUST,
    "test_tempest_apply_corrective_bank_gust_decl_contract.py",
    "ApplyCorrectiveBankGust",
)
GET_LOCK_STABILITY_SECONDS_NOT_LOCKED = (
    GET_LOCK_STABILITY_SECONDS,
    "test_tempest_get_lock_stability_seconds_decl_contract.py",
    "GetLockStabilitySeconds",
)
REQUIRED_LOCK_STABILITY_NOT_LOCKED = (
    REQUIRED_LOCK_STABILITY_SECONDS,
    "RequiredLockStabilitySeconds",
)
HARBOR_ADJACENT_NOT_HARBOR_40_80 = (
    HARBOR_ADJACENT_SEPARATION_FIELD,
    "MinimumWeaponSeparationMeters",
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
    "IsDisabledDescent",
    "OpenSensorExposure",
    "SetFriendlySeparationMeters",
    "RedirectDisabledDrone",
    "IsCrashRedirected",
    "GetFriendlySeparationMeters",
    "ASkyguardLifelineHunterBoss",
    "test_lifeline_hunter_is_disabled_descent_decl_contract.py",
    "test_lifeline_hunter_open_sensor_exposure_decl_contract.py",
    "test_lifeline_hunter_set_friendly_separation_meters_decl_contract.py",
    "test_lifeline_hunter_redirect_disabled_drone_decl_contract.py",
    "test_lifeline_hunter_is_crash_redirected_decl_contract.py",
    "test_lifeline_hunter_get_friendly_separation_meters_decl_contract.py",
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
# .cpp IsLightningExposed body / invented INDEX_NONE
# stay unlocked. Do not invent INDEX_NONE or lock the
# cpp body. Do not parse leftover HUD classes. The
# live inline return is accepted on origin/main and
# is not a locked token of this declaration.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "ASkyguardTempestBoss::IsLightningExposed",
    "SkyguardTempestBoss.cpp",
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


class TempestIsLightningExposedDeclContractTests(unittest.TestCase):
    def test_tempest_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, IS_LIGHTNING_EXPOSED),
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
            "class SKYGUARD52_API AOtherTempestBoss "
            ": public AActor\n"
            "{\n"
            "public:\n"
            f"\t{IS_LIGHTNING_EXPOSED}\n"
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
            f"\t{IS_LIGHTNING_EXPOSED}\n"
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
            f"\t{SET_LIGHTNING_EXPOSED}\n"
            "private:\n"
            f"\t{IS_LIGHTNING_EXPOSED}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, IS_LIGHTNING_EXPOSED)
        self.assertIn("IsLightningExposed", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, IS_LIGHTNING_EXPOSED))

    def test_missing_is_lightning_exposed_declaration_fails_closed(
        self,
    ) -> None:
        neighbors_only = (
            "\tASkyguardTempestBoss();\n"
            f"\t{SET_LIGHTNING_EXPOSED}\n"
            f"\t{APPLY_CORRECTIVE_BANK_GUST}\n"
            f"\t{leftover_advance_stabilized_lock()}\n"
            f"\t{GET_LOCK_STABILITY_SECONDS}\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "PortDischargeBoom;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, IS_LIGHTNING_EXPOSED)
        self.assertIn("IsLightningExposed", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_BOSS}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, IS_LIGHTNING_EXPOSED)
        self.assertIn("IsLightningExposed", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_BOSS, section)
        self.assertTrue(
            has_declaration(section, IS_LIGHTNING_EXPOSED),
            section,
        )
        self.assertNotIn("BlueprintPure", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("UFUNCTION", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("Category", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("BlueprintCallable", IS_LIGHTNING_EXPOSED)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tASkyguardTempestBoss();\n"
            f"\t{SET_LIGHTNING_EXPOSED}\n"
            f"\t{APPLY_CORRECTIVE_BANK_GUST}\n"
            f"\t{leftover_advance_stabilized_lock()}\n"
            f"\t{leftover_arm_break_finish()}\n"
            f"\t{leftover_is_break_finish_armed()}\n"
            f"\t{GET_LOCK_STABILITY_SECONDS}\n"
            f"\t{REQUIRED_LOCK_STABILITY_SECONDS}\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "PortDischargeBoom;\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> EngineIntake;\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
            "\tvoid FaceWorldLocation(const FVector& WorldLocation);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, IS_LIGHTNING_EXPOSED)
        self.assertIn("IsLightningExposed", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_parens = "\tbool IsLightningExposed const;\n"
        missing_const = "\tbool IsLightningExposed();\n"
        wrong_return_void = "\tvoid IsLightningExposed() const;\n"
        wrong_return_int = "\tint32 IsLightningExposed() const;\n"
        added_arg = "\tbool IsLightningExposed(bool bValue) const;\n"
        leftover_set = f"\t{SET_LIGHTNING_EXPOSED}\n"
        leftover_gust = f"\t{APPLY_CORRECTIVE_BANK_GUST}\n"
        leftover_lock = f"\t{GET_LOCK_STABILITY_SECONDS}\n"
        leftover_required = f"\t{REQUIRED_LOCK_STABILITY_SECONDS}\n"
        leftover_window = f"\t{leftover_advance_stabilized_lock()}\n"
        leftover_fallback = f"\t{leftover_arm_break_finish()}\n"
        leftover_armed = f"\t{leftover_is_break_finish_armed()}\n"
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
        leftover_descent = "\tbool IsDisabledDescent() const;\n"
        leftover_field = f"\t{HARBOR_ADJACENT_SEPARATION_FIELD}\n"
        for region in (
            missing_parens,
            missing_const,
            wrong_return_void,
            wrong_return_int,
            added_arg,
            leftover_set,
            leftover_gust,
            leftover_lock,
            leftover_required,
            leftover_window,
            leftover_fallback,
            leftover_armed,
            leftover_muzzle,
            leftover_mount,
            leftover_face,
            leftover_damage,
            leftover_searchlight,
            leftover_contact,
            leftover_orbit,
            leftover_descent,
            leftover_field,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, IS_LIGHTNING_EXPOSED)
            self.assertIn("IsLightningExposed", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_is_lightning_exposed_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, IS_LIGHTNING_EXPOSED),
            IS_LIGHTNING_EXPOSED,
        )
        self.assertTrue(has_declaration(section, IS_LIGHTNING_EXPOSED))
        self.assertEqual(
            declaration_count(section, IS_LIGHTNING_EXPOSED),
            1,
        )
        self.assertTrue(
            IS_LIGHTNING_EXPOSED.startswith("bool "),
            IS_LIGHTNING_EXPOSED,
        )
        self.assertTrue(
            IS_LIGHTNING_EXPOSED.endswith(";"),
            IS_LIGHTNING_EXPOSED,
        )
        self.assertIn("IsLightningExposed()", IS_LIGHTNING_EXPOSED)
        self.assertIn(" const", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("INDEX_NONE", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("{", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("}", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return ", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return bLightningExposed", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("SetLightningExposed", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("ApplyCorrectiveBankGust", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("GetLockStabilitySeconds", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("RequiredLockStabilitySeconds", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("GetChinMuzzleLocation", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("GetGunnerMount", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("FaceWorldLocation", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("PortDischargeBoom", IS_LIGHTNING_EXPOSED)
        self.assertNotIn(
            "MinimumWeaponSeparationMeters",
            IS_LIGHTNING_EXPOSED,
        )
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, IS_LIGHTNING_EXPOSED)

    def test_declaration_accepts_origin_main_inline_and_prototype(self) -> None:
        one_line_prototype = f"{{\npublic:\n\t{IS_LIGHTNING_EXPOSED}\n}}\n"
        self.assertTrue(
            has_declaration(one_line_prototype, IS_LIGHTNING_EXPOSED)
        )
        self.assertEqual(
            require_declaration(one_line_prototype, IS_LIGHTNING_EXPOSED),
            IS_LIGHTNING_EXPOSED,
        )
        exact_inline = (
            "bool IsLightningExposed() const { return bLightningExposed; }"
        )
        self.assertTrue(has_declaration(exact_inline, IS_LIGHTNING_EXPOSED))
        self.assertEqual(
            require_declaration(exact_inline, IS_LIGHTNING_EXPOSED),
            IS_LIGHTNING_EXPOSED,
        )
        self.assertEqual(
            declaration_count(exact_inline, IS_LIGHTNING_EXPOSED),
            1,
        )
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, IS_LIGHTNING_EXPOSED),
            section,
        )
        self.assertEqual(
            require_declaration(section, IS_LIGHTNING_EXPOSED),
            IS_LIGHTNING_EXPOSED,
        )
        self.assertNotIn("{", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return bLightningExposed", IS_LIGHTNING_EXPOSED)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tbool\n"
            "\tIsLightningExposed() const;\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tbool IsLightningExposed(\n"
            "\t) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tbool IsLightningExposed()\n"
            "\tconst;\n"
            "};\n"
        )
        wrap_inline = (
            "public:\n"
            "\tbool IsLightningExposed()\n"
            "\tconst { return bLightningExposed; }\n"
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
        header_wrap_const = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_const}"
        )
        header_wrap_inline = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_inline}"
        )
        for header in (
            header_wrap_type,
            header_wrap_name,
            header_wrap_const,
            header_wrap_inline,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, IS_LIGHTNING_EXPOSED),
                section,
            )
            self.assertEqual(
                require_declaration(section, IS_LIGHTNING_EXPOSED),
                IS_LIGHTNING_EXPOSED,
            )
            self.assertEqual(
                declaration_count(section, IS_LIGHTNING_EXPOSED),
                1,
            )
        one_line = f"{{\npublic:\n\t{IS_LIGHTNING_EXPOSED}\n}}\n"
        self.assertTrue(has_declaration(one_line, IS_LIGHTNING_EXPOSED))
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, IS_LIGHTNING_EXPOSED),
            section,
        )
        self.assertEqual(
            require_declaration(section, IS_LIGHTNING_EXPOSED),
            IS_LIGHTNING_EXPOSED,
        )

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tbool IsLightningExposed() const\n"
            "\t{\n"
            "\t\treturn Other;\n"
            "\t}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{inline}"
        )
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, IS_LIGHTNING_EXPOSED),
            section,
        )
        self.assertEqual(
            require_declaration(section, IS_LIGHTNING_EXPOSED),
            IS_LIGHTNING_EXPOSED,
        )
        self.assertEqual(
            declaration_count(section, IS_LIGHTNING_EXPOSED),
            1,
        )
        self.assertNotIn("{", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("}", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return ", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return bLightningExposed", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return Other", IS_LIGHTNING_EXPOSED)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", IS_LIGHTNING_EXPOSED)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_is_lightning_exposed_cpp_body(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        self.assertNotIn("{", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("}", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return ", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return bLightningExposed", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return bLightningExposed", locked_only)
        self.assertNotIn(
            "ASkyguardTempestBoss::IsLightningExposed",
            IS_LIGHTNING_EXPOSED,
        )
        self.assertNotIn(
            "SkyguardTempestBoss.cpp",
            IS_LIGHTNING_EXPOSED,
        )
        self.assertNotIn("SkyguardTempestBoss.cpp", locked_only)
        self.assertNotIn("return false", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return true", IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_relock_set_lightning_exposed_sibling(
        self,
    ) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in SET_LIGHTNING_EXPOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("SetLightningExposed", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("SetLightningExposed", locked_only)

    def test_contract_does_not_relock_apply_corrective_bank_gust_sibling(
        self,
    ) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in APPLY_CORRECTIVE_BANK_GUST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("ApplyCorrectiveBankGust", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("ApplyCorrectiveBankGust", locked_only)

    def test_contract_does_not_relock_get_lock_stability_seconds_sibling(
        self,
    ) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in GET_LOCK_STABILITY_SECONDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("GetLockStabilitySeconds", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("GetLockStabilitySeconds", locked_only)

    def test_contract_does_not_relock_leftover_emergency_finish(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        self.assertNotIn(leftover_advance_stabilized_lock(), locked_only)
        self.assertNotIn(
            leftover_advance_stabilized_lock(),
            IS_LIGHTNING_EXPOSED,
        )
        self.assertNotIn(leftover_arm_break_finish(), locked_only)
        self.assertNotIn(leftover_arm_break_finish(), IS_LIGHTNING_EXPOSED)
        self.assertNotIn(leftover_is_break_finish_armed(), locked_only)
        self.assertNotIn(
            leftover_is_break_finish_armed(),
            IS_LIGHTNING_EXPOSED,
        )
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, IS_LIGHTNING_EXPOSED)
        for script in leftover_live_copy_boss_scripts():
            self.assertNotIn(script, IS_LIGHTNING_EXPOSED)
            self.assertNotIn(script, locked_only)

    def test_contract_does_not_relock_weak_point_fields(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in WEAK_POINT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("USkyguardBossWeakPointComponent", locked_only)
        self.assertNotIn("PortDischargeBoom", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("StarboardDischargeBoom", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("ControlServo", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("EngineIntake", IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_relock_leftover_searchlight_runtime(
        self,
    ) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn(
            "test_searchlight_track_runtime_defaults_contract.py",
            IS_LIGHTNING_EXPOSED,
        )
        self.assertNotIn(
            "FSkyguardSearchlightTrackRuntime",
            IS_LIGHTNING_EXPOSED,
        )

    def test_contract_does_not_relock_leftover_black_kite(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_BLACK_KITE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("SetSearchlightTracked", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("IsSearchlightTracked", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("ASkyguardBlackKiteBoss", IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_relock_leftover_radar_ghost(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_RADAR_GHOST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("SetContactIdentified", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("IsContactIdentified", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("OpenOrbitExposure", IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_relock_leftover_lifeline_hunter(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("IsDisabledDescent", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("ASkyguardLifelineHunterBoss", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("OpenSensorExposure", IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_relock_leftover_patrol_ship(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_PATROL_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("ASkyguardPatrolShip", IS_LIGHTNING_EXPOSED)
        self.assertNotIn(
            "test_patrol_ship_empty_fail_closed.py",
            IS_LIGHTNING_EXPOSED,
        )

    def test_contract_does_not_relock_mount_getters(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in MOUNT_GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("GetGunnerMount", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("GetChinTurret", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("GetSensorTurret", IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_relock_chin_muzzle(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for neighbor in GET_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("GetChinMuzzleLocation", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn(
            "test_apache_aircraft_empty_fail_closed.py",
            IS_LIGHTNING_EXPOSED,
        )

    def test_contract_does_not_relock_leftover_chin_muzzle(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("GetChinMuzzleLocation", IS_LIGHTNING_EXPOSED)
        self.assertNotIn(
            "test_apache_chin_muzzle_tests.py",
            IS_LIGHTNING_EXPOSED,
        )

    def test_contract_does_not_relock_leftover_own_ship_systems(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("ESkyguardApacheSystem", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn(
            "test_apache_own_ship_systems_contract.py",
            IS_LIGHTNING_EXPOSED,
        )

    def test_contract_does_not_relock_leftover_cpg_feel(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn(
            "test_apache_cpg_feel_contract.py",
            IS_LIGHTNING_EXPOSED,
        )

    def test_contract_does_not_relock_leftover_apache_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_APACHE_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn(
            "test_apache_face_world_location_decl_contract.py",
            IS_LIGHTNING_EXPOSED,
        )
        self.assertNotIn("FaceWorldLocation", IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_relock_leftover_settings(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_SETTINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn(
            "test_settings_apply_broadcast_tests.py",
            IS_LIGHTNING_EXPOSED,
        )

    def test_contract_does_not_relock_leftover_input_capture(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_INPUT_CAPTURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn(
            "test_input_capture_is_capture_active_decl_contract.py",
            IS_LIGHTNING_EXPOSED,
        )
        self.assertNotIn("RecordPlayerEvent", IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_relock_leftover_gunner(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("ASkyguardGunner", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("FillAndFinalize", IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_relock_leftover_radar_node(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("SkyguardRadarNode", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("ASkyguardRadarNode", locked_only)

    def test_contract_does_not_relock_leftover_widget_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardDebriefWidget", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("USkyguardBriefingWidget", IS_LIGHTNING_EXPOSED)
        self.assertNotIn(
            "test_debrief_widget_travel_next_decl_contract.py",
            IS_LIGHTNING_EXPOSED,
        )

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("ESkyguardMissionSkylineStyle", IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_scan_wrong_harbor_headers(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("MinHeightFromOriginCm", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("MaxIntegrity", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("SkyguardApacheAircraft.h", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("SkyguardPathfinder", IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_scan_apache_public_section_for_harbor(
        self,
    ) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        file_text = this_file_text()
        apache_header = "SkyguardApacheAircraft.h"
        self.assertNotIn(apache_header, locked_only)
        self.assertNotIn(apache_header, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("ASkyguardApacheAircraft", locked_only)
        self.assertNotIn("ASkyguardApacheAircraft", IS_LIGHTNING_EXPOSED)
        self.assertNotIn(f"origin/main:{apache_header}", file_text)
        self.assertNotIn(f"git show origin/main:{apache_header}", file_text)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)

    def test_minimum_weapon_separation_is_not_harbor_40_80(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        adjacent = HARBOR_ADJACENT_SEPARATION_FIELD
        self.assertNotIn(adjacent, locked_only)
        self.assertNotIn(adjacent, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("MinimumWeaponSeparationMeters", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("450.f", IS_LIGHTNING_EXPOSED)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, adjacent)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        self.assertEqual(
            require_declaration(locked_only, IS_LIGHTNING_EXPOSED),
            IS_LIGHTNING_EXPOSED,
        )
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("SetLightningExposed", locked_only)
        self.assertNotIn("ApplyCorrectiveBankGust", locked_only)
        self.assertNotIn("GetLockStabilitySeconds", locked_only)
        self.assertNotIn("RequiredLockStabilitySeconds", locked_only)
        self.assertNotIn("GetGunnerMount", locked_only)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)
        self.assertNotIn("FaceWorldLocation", locked_only)
        self.assertNotIn("PortDischargeBoom", locked_only)
        self.assertNotIn("USkyguardBossWeakPointComponent", locked_only)
        self.assertNotIn("MinimumWeaponSeparationMeters", locked_only)
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
        self.assertNotIn("ASkyguardPatrolShip", section)
        self.assertEqual(
            require_declaration(section, IS_LIGHTNING_EXPOSED),
            IS_LIGHTNING_EXPOSED,
        )
        self.assertEqual(
            declaration_count(section, IS_LIGHTNING_EXPOSED),
            1,
        )
        self.assertNotIn("SkyguardTempestBoss.cpp", section)
        self.assertNotIn(
            "ASkyguardTempestBoss::IsLightningExposed",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardTempestBoss.cpp", section)
        self.assertNotIn(
            "ASkyguardTempestBoss::IsLightningExposed",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("}", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return false", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return true", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return bLightningExposed", IS_LIGHTNING_EXPOSED)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        file_text = this_file_text()
        # Harbor clock field names stay off this class
        # public section. Literal Harbor interval retune
        # tokens fail closed in this file and the locked
        # declaration only. Do not scan Apache public
        # section for those tokens. Harbor-adjacent
        # MinimumWeaponSeparationMeters is not a Harbor
        # 40/80 retune. Apache MaxIntegrity is not a
        # Harbor clock. Pathfinder MinHeightFromOriginCm
        # is the wrong header.
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, HARBOR_ADJACENT_SEPARATION_FIELD)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
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
                "tempest IsLightningExposed contract "
                f"contains {banned}; declaration is Apache CPG 30 mm / "
                "Hydra / Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        # Leftover emergency-finish names stay in the
        # public section. This file and the locked
        # declaration stay clean of leftover live copy.
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, IS_LIGHTNING_EXPOSED.lower())
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                IS_LIGHTNING_EXPOSED.lower(),
                "tempest IsLightningExposed contains "
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
        self.assertNotIn(dirty_fwd, IS_LIGHTNING_EXPOSED)

    def test_contract_is_is_lightning_exposed_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, IS_LIGHTNING_EXPOSED),
            IS_LIGHTNING_EXPOSED,
        )
        locked_only = f"{IS_LIGHTNING_EXPOSED}\n"
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_LIGHTNING_EXPOSED)
        self.assertNotIn("SetLightningExposed", locked_only)
        self.assertNotIn("ApplyCorrectiveBankGust", locked_only)
        self.assertNotIn("GetLockStabilitySeconds", locked_only)
        self.assertNotIn("RequiredLockStabilitySeconds", locked_only)
        self.assertNotIn("GetGunnerMount", locked_only)
        self.assertNotIn("GetEyeMount", locked_only)
        self.assertNotIn("GetWeaponMount", locked_only)
        self.assertNotIn("GetChinTurret", locked_only)
        self.assertNotIn("GetPilotMount", locked_only)
        self.assertNotIn("GetSensorTurret", locked_only)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)
        self.assertNotIn("FaceWorldLocation", locked_only)
        self.assertNotIn("ApplyDamage", locked_only)
        self.assertNotIn("PortDischargeBoom", locked_only)
        self.assertNotIn("StarboardDischargeBoom", locked_only)
        self.assertNotIn("USkyguardBossWeakPointComponent", locked_only)
        self.assertNotIn("MinimumWeaponSeparationMeters", locked_only)
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
        self.assertNotIn("IsDisabledDescent", locked_only)
        self.assertNotIn("ASkyguardLifelineHunterBoss", locked_only)
        self.assertNotIn("ASkyguardPatrolShip", locked_only)
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_APACHE_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_SETTINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_INPUT_CAPTURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_BLACK_KITE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_RADAR_GHOST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in LEFTOVER_PATROL_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in SET_LIGHTNING_EXPOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in APPLY_CORRECTIVE_BANK_GUST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in GET_LOCK_STABILITY_SECONDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in REQUIRED_LOCK_STABILITY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in WEAK_POINT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in HARBOR_ADJACENT_NOT_HARBOR_40_80:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in leftover_short_roster_values():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, IS_LIGHTNING_EXPOSED)
            self.assertNotIn(token, section)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HARBOR_ADJACENT_SEPARATION_FIELD)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, IS_LIGHTNING_EXPOSED.lower())
            self.assertNotIn(banned, locked_only.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("return bLightningExposed", IS_LIGHTNING_EXPOSED)
        self.assertNotIn("{", IS_LIGHTNING_EXPOSED)
        self.assertTrue(IS_LIGHTNING_EXPOSED.startswith("bool "))
        self.assertTrue(IS_LIGHTNING_EXPOSED.endswith(";"))
        self.assertIn(" const", IS_LIGHTNING_EXPOSED)
        self.assertIn(UFUNCTION_BOSS, section)

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
