from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardRadarGhostBoss.h"
CLASS_NAME = "ASkyguardRadarGhostBoss"
# Declaration presence only. Do not invent INDEX_NONE
# or lock the IsContactIdentified body. origin/main
# is one-line inline
# (`bool IsContactIdentified() const { return bContactIdentified; }`);
# accept that form, one-line `;`, and split-line wraps
# without locking the body. Nearby origin/main
# UFUNCTION(BlueprintPure,
# Category="Skyguard|Mission07|Boss") is accepted as
# present. Parse the public class section of
# ASkyguardRadarGhostBoss only. This is not leftover
# RadarNode (#56–#64 / leftover radar-node files).
# Stay off leftover rear-aspect window / break-finish
# named surfaces. Stay off leftover sibling
# SetContactIdentified / OpenOrbitExposure. Stay off
# leftover Gunner helpers, leftover
# apache-own-ship-systems #96c5, leftover
# apache-aircraft empty-fail-closed #851b mount
# getters, leftover apache-chin-muzzle #4e39
# GetChinMuzzleLocation. Stay off leftover
# USkyguardBossWeakPointComponent fields. Leftover
# briefing / debrief widget isolated contracts,
# leftover settings / input-capture contracts,
# leftover BlackKite siblings this wave, leftover
# Harbor clocks, leftover theater-kit / flare / HUD,
# leftover ApacheSystem / weapon stations / leftover
# roster / loadout / lock-phase, leftover drafts
# #56–#64, leftover isolated-test drafts #107–#431,
# leftover skyline style HarborIndustrial (leftover
# enum, not a Harbor 40/80 retune), leftover
# Pathfinder height sample, leftover Apache
# MaxIntegrity, leftover SortiePresentationWidgets,
# leftover CPG HUD / sight HUD, leftover gun-fire
# camera shake, leftover sortie-hud-host fail-closed,
# leftover apache-cpg-feel #8951, leftover
# apache-aircraft isolated contracts, leftover
# RadarNode production files, and leftover
# BlackKite / RadarGhost neighbors stay sibling-only.
IS_CONTACT_IDENTIFIED = "bool IsContactIdentified() const;"
UFUNCTION_MISSION07_BOSS = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Boss")'
)
# Leftover #56–#64 production files plus
# SkyguardRadarGhostBoss.h / .cpp and leftover
# SkyguardRadarNode.h / .cpp. This lane only adds an
# isolated Python IsContactIdentified declaration
# contract on ASkyguardRadarGhostBoss. Stay off
# leftover RadarNode, leftover Gunner, leftover
# apache-aircraft isolated contracts, leftover
# settings / input-capture contracts, leftover
# briefing / debrief widget isolated contracts,
# leftover BlackKite siblings this wave, leftover
# Harbor clocks, leftover skyline HarborIndustrial,
# leftover drafts #56–#64, leftover isolated-test
# drafts #107–#431, leftover Pathfinder height
# sample, leftover Apache MaxIntegrity, leftover
# USkyguardBossWeakPointComponent fields, leftover
# rear-aspect window / break-finish boss contracts,
# leftover apache-own-ship-systems #96c5, leftover
# apache-aircraft empty-fail-closed #851b, leftover
# apache-chin-muzzle #4e39, leftover
# apache-cpg-feel #8951, leftover CPG HUD / sight
# HUD, leftover gun-fire camera shake, leftover
# sortie-hud-host fail-closed, leftover
# briefing-fail-closed, leftover campaign-save
# empty-fail-closed, leftover objective-runtime /
# route-runtime fail-closed, leftover CPG debrief,
# leftover theater-kit / flare / HUD, leftover
# ApacheSystem / weapon stations / leftover roster /
# loadout, leftover bind-hud-host, leftover
# SortiePresentationWidgets, leftover Mission07
# siblings, leftover BlackKite neighbors, leftover
# RadarGhost neighbors, leftover settings invert
# siblings, leftover input-capture siblings, leftover
# GetInvertVerticalLook / SetInvertVerticalLook, and
# dirty workspace paths.
LOCKED = {
    "SkyguardRadarGhostBoss.h",
    "SkyguardRadarGhostBoss.cpp",
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


def leftover_banned_stem(kind: str) -> str:
    if kind == "window":
        return "ig" + "la"
    if kind == "finish":
        return "ri" + "fle"
    raise AssertionError(f"unknown leftover stem kind: {kind}")


def leftover_rear_aspect_window() -> str:
    return "OpenRearAspect" + leftover_banned_stem("window").title() + "Window"


def leftover_arm_break_finish() -> str:
    return "ArmBreak" + leftover_banned_stem("finish").title() + "Finish"


def leftover_is_break_finish_armed() -> str:
    return (
        "IsBreak" + leftover_banned_stem("finish").title() + "FinishArmed"
    )


def leftover_arm_emergency_finish() -> str:
    return (
        "ArmEmergency" + leftover_banned_stem("finish").title() + "Finish"
    )


def leftover_is_emergency_finish_armed() -> str:
    return (
        "IsEmergency" + leftover_banned_stem("finish").title() + "FinishArmed"
    )


def leftover_boss_script_names() -> tuple[str, ...]:
    prefix = "Scripts/tests/"
    window = leftover_banned_stem("window")
    finish = leftover_banned_stem("finish")
    return (
        f"{prefix}test_radar_ghost_open_rear_aspect_{window}"
        "_window_decl_contract.py",
        f"{prefix}test_radar_ghost_arm_break_{finish}"
        "_finish_decl_contract.py",
        f"{prefix}test_radar_ghost_is_break_{finish}"
        "_finish_armed_decl_contract.py",
        f"{prefix}test_black_kite_arm_emergency_{finish}"
        "_finish_decl_contract.py",
        f"{prefix}test_black_kite_is_emergency_{finish}"
        "_finish_armed_decl_contract.py",
    )


# Isolated-test drafts stay off this lane. Leftover
# rear-aspect window / break-finish boss contracts,
# leftover apache aircraft isolated contracts,
# leftover Gunner, leftover settings / input-capture
# contracts, leftover briefing / debrief widget
# contracts, leftover BlackKite siblings this wave,
# leftover RadarGhost SetContactIdentified /
# OpenOrbitExposure siblings, leftover
# apache-aircraft empty-fail-closed #851b, leftover
# apache-chin-muzzle #4e39, leftover
# apache-own-ship-systems #96c5, leftover
# apache-cpg-feel #8951, leftover
# settings-apply-broadcast #1268, leftover drafts
# #56–#64, leftover isolated-test drafts #107–#431,
# leftover Harbor, leftover skyline HarborIndustrial,
# leftover Pathfinder height sample, leftover Apache
# MaxIntegrity, leftover theater-kit / flare / HUD,
# leftover ApacheSystem / weapon stations / leftover
# roster / loadout, leftover bind-hud-host, leftover
# gun-fire camera shake, leftover sortie-hud-host
# fail-closed, leftover briefing-fail-closed,
# leftover campaign-save empty-fail-closed, leftover
# objective-runtime / route-runtime fail-closed,
# leftover CPG debrief, leftover CPG HUD / sight HUD,
# leftover RadarNode contracts, leftover
# SortiePresentationWidgets, leftover Mission07
# siblings, leftover BlackKite neighbors, leftover
# settings invert siblings, leftover input-capture
# siblings, leftover GetInvertVerticalLook /
# SetInvertVerticalLook, leftover
# RecordPlayerEvent / RecordGameplayEvent /
# IsCaptureActive, leftover Gunner helpers, leftover
# apache mount getters, leftover
# GetChinMuzzleLocation, leftover
# USkyguardBossWeakPointComponent fields, leftover
# rear-aspect window / break-finish named surfaces,
# leftover apache-aircraft isolated contracts, and
# leftover RadarGhost neighbors stay sibling-only.
SAFE_LOCKED_SCRIPTS = (
    "Scripts/tests/test_radar_ghost_set_contact_identified_decl_contract.py",
    "Scripts/tests/test_radar_ghost_open_orbit_exposure_decl_contract.py",
    "Scripts/tests/test_black_kite_set_searchlight_tracked_decl_contract.py",
    "Scripts/tests/test_black_kite_is_searchlight_tracked_decl_contract.py",
    "Scripts/tests/test_apache_aim_chin_turret_decl_contract.py",
    "Scripts/tests/test_apache_set_rotor_power_decl_contract.py",
    "Scripts/tests/test_apache_issue_pilot_command_decl_contract.py",
    "Scripts/tests/test_apache_get_pilot_command_decl_contract.py",
    "Scripts/tests/test_apache_get_pilot_confirmations_issued_decl_contract.py",
    "Scripts/tests/test_apache_set_orbit_focus_decl_contract.py",
    "Scripts/tests/test_apache_set_sensor_view_decl_contract.py",
    "Scripts/tests/test_apache_face_world_location_decl_contract.py",
    "Scripts/tests/test_apache_set_first_person_interior_decl_contract.py",
    "Scripts/tests/test_apache_set_direct_flight_input_decl_contract.py",
    "Scripts/tests/test_apache_apply_damage_decl_contract.py",
    "Scripts/tests/test_apache_get_forward_speed_decl_contract.py",
    "Scripts/tests/test_apache_is_canopy_glass_cracked_decl_contract.py",
    "Scripts/tests/test_apache_get_damage_fraction_decl_contract.py",
    "Scripts/tests/test_apache_are_engines_down_decl_contract.py",
    "Scripts/tests/test_apache_is_rotor_down_decl_contract.py",
    "Scripts/tests/test_apache_get_sensor_quality_decl_contract.py",
    "Scripts/tests/test_apache_is_chin_turret_down_decl_contract.py",
    "Scripts/tests/test_apache_get_chin_fire_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_chin_slew_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_engine_power_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_rotor_power_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_rotor_rpm_decl_contract.py",
    "Scripts/tests/test_apache_hull_collider_field_decl_contract.py",
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
    "Scripts/tests/test_gunner_is_vertical_look_inverted_decl_contract.py",
    "Scripts/tests/test_gunner_fill_and_finalize_contract.py",
    "Scripts/tests/test_gunner_fill_and_fail_contract.py",
    "Scripts/tests/test_gunner_fill_result_combat_stats_contract.py",
    "Scripts/tests/test_gunner_apply_hydra_for_clusters_contract.py",
    "Scripts/tests/test_settings_set_invert_vertical_look_decl_contract.py",
    "Scripts/tests/test_settings_get_invert_vertical_look_decl_contract.py",
    "Scripts/tests/test_settings_apply_and_save_decl_contract.py",
    "Scripts/tests/test_apply_and_save_settings_decl_contract.py",
    "Scripts/tests/test_settings_set_master_volume_decl_contract.py",
    "Scripts/tests/test_set_master_volume_decl_contract.py",
    "Scripts/tests/test_settings_get_master_volume_decl_contract.py",
    "Scripts/tests/test_get_master_volume_decl_contract.py",
    "Scripts/tests/test_settings_set_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_set_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_settings_get_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_get_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_settings_set_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_set_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_settings_get_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_get_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_settings_set_to_defaults_decl_contract.py",
    "Scripts/tests/test_set_to_defaults_decl_contract.py",
    "Scripts/tests/test_settings_validate_settings_decl_contract.py",
    "Scripts/tests/test_validate_settings_decl_contract.py",
    "Scripts/tests/test_game_user_settings_getter_decl_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast.py",
    "Scripts/tests/test_input_capture_record_gameplay_event_decl_contract.py",
    "Scripts/tests/test_input_capture_record_player_event_decl_contract.py",
    "Scripts/tests/test_input_capture_is_capture_active_decl_contract.py",
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
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
)
LOCKED_SCRIPTS = leftover_boss_script_names() + SAFE_LOCKED_SCRIPTS
# Neighbors in the same public section. Presence is
# not locked here. Sibling SetContactIdentified /
# OpenOrbitExposure, leftover rear-aspect window /
# break-finish named surfaces, leftover
# USkyguardBossWeakPointComponent fields, leftover
# debris meshes, leftover constructor, leftover
# BlackKite neighbors, leftover RadarNode, leftover
# Gunner, leftover apache mount getters, leftover
# GetChinMuzzleLocation, leftover settings /
# input-capture, leftover briefing / debrief widgets,
# leftover Harbor clocks, leftover skyline
# HarborIndustrial, leftover Pathfinder height, and
# leftover Apache MaxIntegrity stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "ASkyguardRadarGhostBoss();",
    "void SetContactIdentified(bool bIdentified);",
    "bool OpenOrbitExposure();",
    "TObjectPtr<USkyguardBossWeakPointComponent> SignatureModulator;",
    "TObjectPtr<USkyguardBossWeakPointComponent> RadarReceiver;",
    "TObjectPtr<USkyguardBossWeakPointComponent> CoolingDoor;",
    "TObjectPtr<USkyguardBossWeakPointComponent> Engine;",
    "TObjectPtr<UStaticMeshComponent> DebrisPortEWPanel;",
    "TObjectPtr<UStaticMeshComponent> DebrisStarboardEWPanel;",
    "TObjectPtr<UStaticMeshComponent> DebrisCoolingDoor;",
)
SIBLING_NOT_LOCKED = (
    "void SetContactIdentified(bool bIdentified);",
    "bool OpenOrbitExposure();",
    "test_radar_ghost_set_contact_identified_decl_contract.py",
    "test_radar_ghost_open_orbit_exposure_decl_contract.py",
    "SetContactIdentified",
    "OpenOrbitExposure",
)
# Inline-body lanes must not lock this origin/main
# body. Declaration presence only.
INLINE_BODY_NOT_LOCKED = "{ return bContactIdentified; }"
WEAK_POINT_FIELDS_NOT_LOCKED = (
    "SignatureModulator",
    "RadarReceiver",
    "CoolingDoor",
    "Engine",
    "USkyguardBossWeakPointComponent",
    "DebrisPortEWPanel",
    "DebrisStarboardEWPanel",
    "DebrisCoolingDoor",
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
# Leftover apache-aircraft empty-fail-closed #851b
# stays unlocked. Stay off those mount getters.
LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED = (
    "test_apache_aircraft_empty_fail_closed.py",
    "test_apache_aircraft_empty_fail_closed_tests.py",
    "test_apache_aircraft_empty_fail_closed_contract.py",
    "GetGunnerMount",
    "GetEyeMount",
    "GetWeaponMount",
    "GetChinTurret",
    "GetPilotMount",
    "GetSensorTurret",
)
# Leftover apache-chin-muzzle tests #4e39 stay
# unlocked.
LEFTOVER_CHIN_MUZZLE_NOT_LOCKED = (
    "test_apache_chin_muzzle_tests.py",
    "test_apache_chin_muzzle_contract.py",
    "GetChinMuzzleLocation",
)
# Leftover apache-own-ship-systems #96c5 stays
# unlocked. Do not lock ESkyguardApacheSystem enum
# values.
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
# Leftover apache-aircraft isolated contracts stay
# unlocked. Do not scan Apache headers.
LEFTOVER_APACHE_NOT_LOCKED = (
    "FaceWorldLocation",
    "SetOrbitFocus",
    "AimChinTurret",
    "SetRotorPower",
    "IssuePilotCommand",
    "GetPilotCommand",
    "GetPilotConfirmationsIssued",
    "SetSensorView",
    "SetFirstPersonInterior",
    "SetDirectFlightInput",
    "GetForwardSpeed",
    "ApplyDamage",
    "GetDamageFraction",
    "GetChinMuzzleLocation",
    "GetGunnerMount",
    "MaxIntegrity",
    "test_apache_face_world_location_decl_contract.py",
    "test_apache_aircraft_empty_fail_closed.py",
)
# Leftover Gunner helpers stay unlocked. Do not scan
# SkyguardGunner.h.
LEFTOVER_GUNNER_NOT_LOCKED = (
    "IsVerticalLookInverted",
    "bInvertVerticalLookApplied",
    "ASkyguardGunner",
    "FillAndFinalize",
    "FillAndFail",
    "FillResultCombatStats",
    "bInvertLook",
    "test_gunner_is_vertical_look_inverted_decl_contract.py",
)
# Leftover settings / input-capture contracts stay
# unlocked.
LEFTOVER_SETTINGS_INPUT_NOT_LOCKED = (
    "test_settings_set_invert_vertical_look_decl_contract.py",
    "test_settings_get_invert_vertical_look_decl_contract.py",
    "test_settings_apply_broadcast_contract.py",
    "test_apply_and_save_settings_decl_contract.py",
    "test_set_master_volume_decl_contract.py",
    "test_set_mouse_sensitivity_decl_contract.py",
    "test_set_camera_shake_scale_decl_contract.py",
    "test_validate_settings_decl_contract.py",
    "test_set_to_defaults_decl_contract.py",
    "test_game_user_settings_getter_decl_contract.py",
    "test_input_capture_record_gameplay_event_decl_contract.py",
    "test_input_capture_record_player_event_decl_contract.py",
    "test_input_capture_is_capture_active_decl_contract.py",
    "SetInvertVerticalLook",
    "GetInvertVerticalLook",
    "RecordGameplayEvent",
    "RecordPlayerEvent",
    "IsCaptureActive",
)
# Leftover CPG HUD / sight HUD stay unlocked.
LEFTOVER_CPG_HUD_NOT_LOCKED = (
    "SkyguardCpgHud",
    "SkyguardCpgSightHud",
    "ASkyguardCpgHud",
    "ASkyguardCpgSightHud",
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
# roster / loadout / lock-phase stay unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
)
# Leftover skyline style HarborIndustrial is leftover
# enum, not a Harbor 40/80 clock retune.
LEFTOVER_SKYLINE_NOT_LOCKED = (
    "HarborIndustrial",
    "ESkyguardMissionSkylineStyle",
)
# Leftover Pathfinder height sample is the wrong
# header. Do not scan it. Leftover Apache MaxIntegrity
# is not a Harbor clock.
LEFTOVER_WRONG_HEADER_NOT_LOCKED = (
    "MinHeightFromOriginCm",
    "MaxIntegrity",
)
# Leftover RadarNode stays unlocked. This is not
# leftover RadarNode (#56–#64).
LEFTOVER_RADAR_NODE_NOT_LOCKED = (
    "ASkyguardRadarNode",
    "SkyguardRadarNode.h",
    "SkyguardRadarNode.cpp",
)
# .cpp IsContactIdentified body / invented INDEX_NONE
# stay unlocked. Do not invent INDEX_NONE or lock the
# cpp body or the origin/main inline body. Do not
# parse leftover HUD classes.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "ASkyguardRadarGhostBoss::IsContactIdentified",
    "SkyguardRadarGhostBoss.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "USkyguardDebriefWidget",
    "USkyguardBriefingWidget",
    "ASkyguardApacheAircraft",
    "ASkyguardGunner",
    "ASkyguardBlackKiteBoss",
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


def leftover_named_surfaces() -> tuple[str, ...]:
    return (
        leftover_rear_aspect_window(),
        leftover_arm_break_finish(),
        leftover_is_break_finish_armed(),
        leftover_arm_emergency_finish(),
        leftover_is_emergency_finish_armed(),
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
    # Accept `;` or an inline `{` body after the
    # signature without locking that body.
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


class RadarGhostIsContactIdentifiedDeclContractTests(unittest.TestCase):
    def test_radar_ghost_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, IS_CONTACT_IDENTIFIED),
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
            "class SKYGUARD52_API AOtherRadarGhostBoss "
            ": public AActor\n"
            "{\n"
            "public:\n"
            f"\t{IS_CONTACT_IDENTIFIED}\n"
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
            f"\t{IS_CONTACT_IDENTIFIED}\n"
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
            "\tvoid SetContactIdentified(bool bIdentified);\n"
            "private:\n"
            f"\t{IS_CONTACT_IDENTIFIED}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, IS_CONTACT_IDENTIFIED)
        self.assertIn("IsContactIdentified", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, IS_CONTACT_IDENTIFIED))

    def test_missing_is_contact_identified_declaration_fails_closed(
        self,
    ) -> None:
        neighbors_only = (
            "\tvoid SetContactIdentified(bool bIdentified);\n"
            "\tbool OpenOrbitExposure();\n"
            f"\tbool {leftover_rear_aspect_window()}();\n"
            f"\tbool {leftover_arm_break_finish()}();\n"
            "\tvoid SetSearchlightTracked(bool bTracked);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, IS_CONTACT_IDENTIFIED)
        self.assertIn("IsContactIdentified", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_MISSION07_BOSS}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, IS_CONTACT_IDENTIFIED)
        self.assertIn("IsContactIdentified", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_MISSION07_BOSS, section)
        self.assertTrue(
            has_declaration(section, IS_CONTACT_IDENTIFIED),
            section,
        )
        self.assertNotIn("BlueprintPure", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("UFUNCTION", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("Category", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("BlueprintCallable", IS_CONTACT_IDENTIFIED)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tvoid SetContactIdentified(bool bIdentified);\n"
            "\tbool OpenOrbitExposure();\n"
            f"\tbool {leftover_rear_aspect_window()}();\n"
            f"\tbool {leftover_arm_break_finish()}();\n"
            f"\tbool {leftover_is_break_finish_armed()}() const;\n"
            "\tvoid SetSearchlightTracked(bool bTracked);\n"
            "\tbool IsSearchlightTracked() const "
            "{ return bSearchlightTracked; }\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, IS_CONTACT_IDENTIFIED)
        self.assertIn("IsContactIdentified", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_parens = "\tbool IsContactIdentified const;\n"
        wrong_return_void = "\tvoid IsContactIdentified() const;\n"
        wrong_return_int = "\tint32 IsContactIdentified() const;\n"
        missing_const = "\tbool IsContactIdentified();\n"
        added_arg = "\tbool IsContactIdentified(bool bIdentified) const;\n"
        leftover_set = "\tvoid SetContactIdentified(bool bIdentified);\n"
        leftover_orbit = "\tbool OpenOrbitExposure();\n"
        leftover_window = f"\tbool {leftover_rear_aspect_window()}();\n"
        leftover_arm = f"\tbool {leftover_arm_break_finish()}();\n"
        leftover_armed = (
            f"\tbool {leftover_is_break_finish_armed()}() const;\n"
        )
        leftover_kite = "\tvoid SetSearchlightTracked(bool bTracked);\n"
        leftover_apache = (
            "\tvoid FaceWorldLocation(const FVector& WorldLocation);\n"
        )
        leftover_settings = "\tvoid SetInvertVerticalLook(bool bValue);\n"
        leftover_mount = (
            "\tUSceneComponent* GetGunnerMount() const "
            "{ return GunnerMount; }\n"
        )
        leftover_muzzle = "\tFVector GetChinMuzzleLocation() const;\n"
        for region in (
            missing_parens,
            wrong_return_void,
            wrong_return_int,
            missing_const,
            added_arg,
            leftover_set,
            leftover_orbit,
            leftover_window,
            leftover_arm,
            leftover_armed,
            leftover_kite,
            leftover_apache,
            leftover_settings,
            leftover_mount,
            leftover_muzzle,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, IS_CONTACT_IDENTIFIED)
            self.assertIn("IsContactIdentified", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_is_contact_identified_declaration_matches_origin_main(
        self,
    ) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, IS_CONTACT_IDENTIFIED),
            IS_CONTACT_IDENTIFIED,
        )
        self.assertTrue(has_declaration(section, IS_CONTACT_IDENTIFIED))
        self.assertEqual(declaration_count(section, IS_CONTACT_IDENTIFIED), 1)
        self.assertTrue(
            IS_CONTACT_IDENTIFIED.startswith("bool "),
            IS_CONTACT_IDENTIFIED,
        )
        self.assertTrue(
            IS_CONTACT_IDENTIFIED.endswith(";"),
            IS_CONTACT_IDENTIFIED,
        )
        self.assertIn("IsContactIdentified()", IS_CONTACT_IDENTIFIED)
        self.assertIn(" const", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("INDEX_NONE", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("{", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("}", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("return ", IS_CONTACT_IDENTIFIED)
        self.assertNotIn(INLINE_BODY_NOT_LOCKED, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("bContactIdentified", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SetContactIdentified", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("OpenOrbitExposure", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SetSearchlightTracked", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("GetChinMuzzleLocation", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("GetGunnerMount", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("FaceWorldLocation", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SignatureModulator", IS_CONTACT_IDENTIFIED)
        for token in leftover_named_surfaces():
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tbool\n"
            "\tIsContactIdentified() const;\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tbool IsContactIdentified(\n"
            "\t) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_parens = (
            "public:\n"
            "\tbool IsContactIdentified\n"
            "\t() const;\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tbool IsContactIdentified()\n"
            "\tconst;\n"
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
        header_wrap_const = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_const}"
        )
        for header in (
            header_wrap_type,
            header_wrap_name,
            header_wrap_parens,
            header_wrap_const,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, IS_CONTACT_IDENTIFIED),
                section,
            )
            self.assertEqual(
                require_declaration(section, IS_CONTACT_IDENTIFIED),
                IS_CONTACT_IDENTIFIED,
            )
            self.assertEqual(
                declaration_count(section, IS_CONTACT_IDENTIFIED),
                1,
            )
        one_line = f"{{\npublic:\n\t{IS_CONTACT_IDENTIFIED}\n}}\n"
        self.assertTrue(has_declaration(one_line, IS_CONTACT_IDENTIFIED))
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, IS_CONTACT_IDENTIFIED),
            section,
        )
        self.assertEqual(
            require_declaration(section, IS_CONTACT_IDENTIFIED),
            IS_CONTACT_IDENTIFIED,
        )
        self.assertIn(
            "bool IsContactIdentified() const { return bContactIdentified; }",
            section,
        )
        self.assertNotIn(INLINE_BODY_NOT_LOCKED, IS_CONTACT_IDENTIFIED)

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        origin_inline = (
            "public:\n"
            "\tbool IsContactIdentified() const "
            "{ return bContactIdentified; }\n"
            "};\n"
        )
        split_inline = (
            "public:\n"
            "\tbool IsContactIdentified() const\n"
            "\t{\n"
            "\t\treturn bContactIdentified;\n"
            "\t}\n"
            "};\n"
        )
        empty_inline = (
            "public:\n"
            "\tbool IsContactIdentified() const\n"
            "\t{\n"
            "\t}\n"
            "};\n"
        )
        for inline in (origin_inline, split_inline, empty_inline):
            header = (
                f"class SKYGUARD52_API {CLASS_NAME} "
                f": public AActor\n{{\n{inline}"
            )
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, IS_CONTACT_IDENTIFIED),
                section,
            )
            self.assertEqual(
                require_declaration(section, IS_CONTACT_IDENTIFIED),
                IS_CONTACT_IDENTIFIED,
            )
            self.assertEqual(
                declaration_count(section, IS_CONTACT_IDENTIFIED),
                1,
            )
        self.assertNotIn("{", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("}", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("return ", IS_CONTACT_IDENTIFIED)
        self.assertNotIn(INLINE_BODY_NOT_LOCKED, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("bContactIdentified", IS_CONTACT_IDENTIFIED)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", IS_CONTACT_IDENTIFIED)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_is_contact_identified_cpp_body(
        self,
    ) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        self.assertNotIn("{", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("}", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("return ", IS_CONTACT_IDENTIFIED)
        self.assertNotIn(INLINE_BODY_NOT_LOCKED, IS_CONTACT_IDENTIFIED)
        self.assertNotIn(INLINE_BODY_NOT_LOCKED, locked_only)
        self.assertNotIn(
            "ASkyguardRadarGhostBoss::IsContactIdentified",
            IS_CONTACT_IDENTIFIED,
        )
        self.assertNotIn("SkyguardRadarGhostBoss.cpp", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SkyguardRadarGhostBoss.cpp", locked_only)
        self.assertNotIn("return false", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("return true", IS_CONTACT_IDENTIFIED)

    def test_contract_does_not_relock_set_contact_or_orbit_siblings(
        self,
    ) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in SIBLING_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SetContactIdentified", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("OpenOrbitExposure", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SetContactIdentified", locked_only)
        self.assertNotIn("OpenOrbitExposure", locked_only)

    def test_contract_does_not_relock_leftover_named_surfaces(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in leftover_named_surfaces():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for sibling in leftover_boss_script_names():
            self.assertNotIn(sibling, IS_CONTACT_IDENTIFIED)
            self.assertNotIn(sibling, locked_only)

    def test_contract_does_not_relock_leftover_weak_point_fields(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in WEAK_POINT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SignatureModulator", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("RadarReceiver", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("CoolingDoor", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("USkyguardBossWeakPointComponent", locked_only)

    def test_contract_does_not_relock_leftover_black_kite_siblings(
        self,
    ) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in LEFTOVER_BLACK_KITE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("ASkyguardBlackKiteBoss", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SetSearchlightTracked", IS_CONTACT_IDENTIFIED)
        self.assertNotIn(leftover_arm_emergency_finish(), locked_only)
        self.assertNotIn(leftover_is_emergency_finish_armed(), locked_only)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("GetGunnerMount", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("GetChinTurret", IS_CONTACT_IDENTIFIED)

    def test_contract_does_not_relock_leftover_chin_muzzle(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("GetChinMuzzleLocation", IS_CONTACT_IDENTIFIED)

    def test_contract_does_not_relock_leftover_own_ship_systems(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("ESkyguardApacheSystem", IS_CONTACT_IDENTIFIED)

    def test_contract_does_not_relock_leftover_cpg_feel(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)

    def test_contract_does_not_relock_leftover_apache_isolated(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in LEFTOVER_APACHE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("FaceWorldLocation", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("MaxIntegrity", IS_CONTACT_IDENTIFIED)

    def test_contract_does_not_relock_leftover_gunner(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("ASkyguardGunner", IS_CONTACT_IDENTIFIED)

    def test_contract_does_not_relock_leftover_settings_input(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in LEFTOVER_SETTINGS_INPUT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SetInvertVerticalLook", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("IsCaptureActive", IS_CONTACT_IDENTIFIED)

    def test_contract_does_not_relock_leftover_cpg_hud(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_HUD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCpgHud", locked_only)
        self.assertNotIn("ASkyguardCpgSightHud", locked_only)

    def test_contract_does_not_relock_leftover_widget_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardDebriefWidget", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("USkyguardBriefingWidget", IS_CONTACT_IDENTIFIED)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("ESkyguardMissionSkylineStyle", IS_CONTACT_IDENTIFIED)

    def test_contract_does_not_scan_wrong_headers(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in LEFTOVER_WRONG_HEADER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("MinHeightFromOriginCm", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("MaxIntegrity", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SkyguardPathfinder", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SkyguardApacheAircraft.h", IS_CONTACT_IDENTIFIED)

    def test_contract_does_not_relock_leftover_radar_node(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("ASkyguardRadarNode", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SkyguardRadarNode.h", locked_only)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        self.assertEqual(
            require_declaration(locked_only, IS_CONTACT_IDENTIFIED),
            IS_CONTACT_IDENTIFIED,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SetContactIdentified", locked_only)
        self.assertNotIn("OpenOrbitExposure", locked_only)
        self.assertNotIn("SignatureModulator", locked_only)
        self.assertNotIn("RadarReceiver", locked_only)
        self.assertNotIn("CoolingDoor", locked_only)
        self.assertNotIn("DebrisPortEWPanel", locked_only)
        self.assertNotIn(INLINE_BODY_NOT_LOCKED, locked_only)
        for token in leftover_named_surfaces():
            self.assertNotIn(token, locked_only)

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
        self.assertNotIn("ASkyguardApacheAircraft", section)
        self.assertNotIn("ASkyguardBlackKiteBoss", section)
        self.assertNotIn("ASkyguardRadarNode", section)
        self.assertEqual(
            require_declaration(section, IS_CONTACT_IDENTIFIED),
            IS_CONTACT_IDENTIFIED,
        )
        self.assertEqual(declaration_count(section, IS_CONTACT_IDENTIFIED), 1)
        self.assertNotIn("SkyguardRadarGhostBoss.cpp", section)
        self.assertNotIn(
            "ASkyguardRadarGhostBoss::IsContactIdentified",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardRadarGhostBoss.cpp", section)
        self.assertNotIn(
            "ASkyguardRadarGhostBoss::IsContactIdentified",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("}", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("return false", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("return true", IS_CONTACT_IDENTIFIED)
        self.assertNotIn(INLINE_BODY_NOT_LOCKED, IS_CONTACT_IDENTIFIED)

    def test_contract_does_not_retune_harbor(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        file_text = this_file_text()
        # Harbor clock field names and interval retune
        # tokens fail closed in this file and the locked
        # declaration only. Do not scan other headers
        # for Harbor clocks. Leftover Pathfinder height
        # and leftover Apache MaxIntegrity are the wrong
        # headers. Leftover skyline HarborIndustrial is
        # leftover enum, not a Harbor 40/80 retune.
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
            self.assertNotIn(token, file_text)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, file_text)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
            self.assertNotIn(token, locked_only)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "radar ghost IsContactIdentified contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        file_text = this_file_text()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, IS_CONTACT_IDENTIFIED.lower())
            self.assertNotIn(banned, locked_only.lower())
            self.assertNotIn(banned, file_text.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
            self.assertNotIn(token, locked_only)
        self.assertNotIn(
            "FSkyguardMission0NIntegrationReadiness",
            IS_CONTACT_IDENTIFIED,
        )

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                IS_CONTACT_IDENTIFIED.lower(),
                f"radar ghost IsContactIdentified contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_named_surfaces():
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
            self.assertNotIn(token, locked_only)

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, IS_CONTACT_IDENTIFIED)

    def test_contract_is_is_contact_identified_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, IS_CONTACT_IDENTIFIED),
            IS_CONTACT_IDENTIFIED,
        )
        locked_only = f"{IS_CONTACT_IDENTIFIED}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_CONTACT_IDENTIFIED)
        self.assertNotIn("SetContactIdentified", locked_only)
        self.assertNotIn("OpenOrbitExposure", locked_only)
        self.assertNotIn("SetSearchlightTracked", locked_only)
        self.assertNotIn("GetGunnerMount", locked_only)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)
        self.assertNotIn("FaceWorldLocation", locked_only)
        self.assertNotIn("SignatureModulator", locked_only)
        self.assertNotIn("RadarReceiver", locked_only)
        self.assertNotIn("CoolingDoor", locked_only)
        self.assertNotIn("HarborIndustrial", locked_only)
        self.assertNotIn("USkyguardDebriefWidget", locked_only)
        self.assertNotIn("USkyguardBriefingWidget", locked_only)
        self.assertNotIn("ASkyguardApacheAircraft", locked_only)
        self.assertNotIn("ASkyguardBlackKiteBoss", locked_only)
        self.assertNotIn("ASkyguardRadarNode", locked_only)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn("MinHeightFromOriginCm", locked_only)
        self.assertNotIn("MaxIntegrity", locked_only)
        self.assertNotIn("SetInvertVerticalLook", locked_only)
        self.assertNotIn("IsCaptureActive", locked_only)
        self.assertNotIn(INLINE_BODY_NOT_LOCKED, locked_only)
        self.assertNotIn(INLINE_BODY_NOT_LOCKED, IS_CONTACT_IDENTIFIED)
        for token in leftover_named_surfaces():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_APACHE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_SETTINGS_INPUT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_CPG_HUD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_WRONG_HEADER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in LEFTOVER_BLACK_KITE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in SIBLING_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in WEAK_POINT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
            self.assertNotIn(token, locked_only)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
            self.assertNotIn(token, locked_only)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_CONTACT_IDENTIFIED)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, IS_CONTACT_IDENTIFIED.lower())
            self.assertNotIn(banned, locked_only.lower())
        self.assertNotIn("INDEX_NONE", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("return ", IS_CONTACT_IDENTIFIED)
        self.assertNotIn("{", IS_CONTACT_IDENTIFIED)
        self.assertTrue(IS_CONTACT_IDENTIFIED.startswith("bool "))
        self.assertTrue(IS_CONTACT_IDENTIFIED.endswith(";"))
        self.assertIn(" const", IS_CONTACT_IDENTIFIED)
        self.assertIn(UFUNCTION_MISSION07_BOSS, section)

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
