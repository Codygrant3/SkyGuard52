from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardBlackKiteBoss.h"
CLASS_NAME = "ASkyguardBlackKiteBoss"
# Declaration presence only. Do not invent INDEX_NONE
# or lock the IsSearchlightTracked body.
# origin/main is inline
# (`bool IsSearchlightTracked() const`
# with `{ return bSearchlightTracked; }` possibly on the
# same line or following lines);
# accept that exact inline form, a one-line prototype
# (`bool IsSearchlightTracked() const;`),
# other split-line wraps, and other inline bodies without
# locking the body. The inline return of the searchlight
# flag is not a required token of this declaration lock.
# Nearby origin/main
# UFUNCTION(BlueprintPure, Category="Skyguard|Mission04|Boss")
# is accepted as present. Parse the public class section of
# ASkyguardBlackKiteBoss only. Stay off leftover
# emergency-finish surfaces (constructed at runtime).
# Stay off leftover searchlight-track-runtime-defaults
# #7347 (struct defaults lane, not this method). Stay
# off sibling SetSearchlightTracked (this wave). Stay
# off leftover RadarNode, leftover Gunner, leftover
# apache-own-ship-systems #96c5, leftover #851b mount
# getters GetGunnerMount / GetEyeMount / GetWeaponMount
# / GetChinTurret / GetPilotMount / GetSensorTurret,
# leftover #4e39 GetChinMuzzleLocation, leftover
# USkyguardBossWeakPointComponent fields
# PortNavigationVane / StarboardNavigationVane / Jammer
# / PowerBus, leftover apache aircraft isolated
# contracts, leftover settings / input-capture
# contracts, leftover briefing / debrief widget
# isolated contracts, leftover Harbor clocks, leftover
# theater-kit / flare / HUD, leftover drafts #56–#64,
# leftover isolated-test drafts #107–#431, leftover
# skyline style HarborIndustrial (leftover enum, not a
# Harbor 40/80 retune), leftover sortie-hud-host
# fail-closed, leftover gun-fire camera shake, leftover
# DebriefWidget TravelNext / HandleDebriefKey, leftover
# SortiePresentationWidgets, leftover CPG HUD / sight
# HUD, leftover apache-cpg-feel #8951, leftover
# apache-aircraft empty-fail-closed #851b, leftover
# apache-chin-muzzle #4e39, leftover
# pilot-command-roster #b593, leftover live-copy boss
# contracts, and dirty workspace paths.
IS_SEARCHLIGHT_TRACKED = "bool IsSearchlightTracked() const;"
UFUNCTION_BOSS = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Mission04|Boss")'
)
# Leftover #56–#64 plus SkyguardBlackKiteBoss production
# files. This lane only adds an isolated Python
# IsSearchlightTracked declaration contract on
# ASkyguardBlackKiteBoss. SortiePresentationWidgets is
# not the class under test. Stay off leftover
# emergency-finish surfaces, leftover
# searchlight-track-runtime-defaults #7347, leftover
# SetSearchlightTracked sibling, leftover RadarNode,
# leftover Gunner, leftover apache-own-ship-systems
# #96c5, leftover #851b mount getters, leftover #4e39
# GetChinMuzzleLocation, leftover
# USkyguardBossWeakPointComponent fields, leftover
# apache aircraft isolated contracts, leftover
# settings / input-capture contracts, leftover
# briefing / debrief widget isolated contracts,
# leftover drafts #56–#64, leftover isolated-test
# drafts #107–#431, leftover Harbor clocks, leftover
# skyline HarborIndustrial, leftover CPG HUD / sight
# HUD, leftover gun-fire camera shake, leftover
# sortie-hud-host fail-closed, leftover
# live-copy boss contracts, and dirty workspace paths.
LOCKED = {
    "SkyguardBlackKiteBoss.h",
    "SkyguardBlackKiteBoss.cpp",
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
# Isolated-test drafts stay off this lane. Leftover
# searchlight-track-runtime-defaults #7347, leftover
# live-copy boss contracts, leftover apache aircraft
# isolated contracts, leftover Gunner, leftover
# settings / input-capture contracts, leftover
# briefing / debrief widget isolated contracts,
# leftover apache-aircraft empty-fail-closed #851b,
# leftover apache-chin-muzzle #4e39, leftover
# apache-own-ship-systems #96c5, leftover
# apache-cpg-feel #8951, leftover
# pilot-command-roster #b593, leftover DebriefWidget
# Configure / GetPresentation / GetDebrief /
# GetDebriefNarrative / GetFinalScore /
# IsProgressSaved / GetPresentationState /
# AcknowledgeDebrief / RetrySave / TravelNext /
# HandleDebriefKey, leftover BriefingWidget isolated
# contracts, leftover gun-fire camera shake, leftover
# sortie-hud-host fail-closed, leftover CPG HUD / sight
# HUD, leftover briefing-fail-closed, leftover
# campaign-save empty-fail-closed, leftover
# objective-runtime / route-runtime fail-closed,
# leftover theater-kit / Harbor / flare / HUD, leftover
# ApacheSystem / weapon stations / leftover
# pilot-command-roster #b593 / loadout, leftover
# bind-hud-host, leftover Gunner helpers, leftover
# pilot drafts, leftover mission-weather enum, leftover
# mission-definition field / method contracts, leftover
# skyline HarborIndustrial, leftover
# SortiePresentationWidgets, leftover CPG debrief,
# leftover drafts #56–#64, leftover isolated-test
# drafts #107–#431, leftover SetSearchlightTracked
# sibling, leftover USkyguardBossWeakPointComponent
# fields, leftover RadarNode, leftover #851b mount
# getters, leftover #4e39 GetChinMuzzleLocation, and
# sibling Black Kite neighbors stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_searchlight_track_runtime_defaults_contract.py",
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
    "Scripts/tests/test_apache_are_engines_down_decl_contract.py",
    "Scripts/tests/test_apache_is_canopy_glass_cracked_decl_contract.py",
    "Scripts/tests/test_apache_is_rotor_down_decl_contract.py",
    "Scripts/tests/test_apache_is_chin_turret_down_decl_contract.py",
    "Scripts/tests/test_apache_get_sensor_quality_decl_contract.py",
    "Scripts/tests/test_apache_get_chin_slew_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_chin_fire_scale_decl_contract.py",
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
    "Scripts/tests/test_gunner_empty_fail_closed.py",
    "Scripts/tests/test_gunner_helpers.py",
    "Scripts/tests/test_gunner_campaign.py",
    "Scripts/tests/test_settings_get_invert_vertical_look_decl_contract.py",
    "Scripts/tests/test_settings_set_invert_vertical_look_decl_contract.py",
    "Scripts/tests/test_settings_get_master_volume_decl_contract.py",
    "Scripts/tests/test_settings_set_master_volume_decl_contract.py",
    "Scripts/tests/test_settings_get_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_settings_set_mouse_sensitivity_decl_contract.py",
    "Scripts/tests/test_settings_apply_and_save_settings_decl_contract.py",
    "Scripts/tests/test_settings_validate_settings_decl_contract.py",
    "Scripts/tests/test_settings_set_to_defaults_decl_contract.py",
    "Scripts/tests/test_settings_get_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_settings_set_camera_shake_scale_decl_contract.py",
    "Scripts/tests/test_game_user_settings_getter_decl_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
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
    "Scripts/tests/test_pilot_command_roster.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_pilot_command_roster_tests.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
)
# Neighbors in the same public section. Presence is not
# locked here. SetSearchlightTracked, leftover
# emergency-finish surfaces, leftover
# USkyguardBossWeakPointComponent fields, leftover
# debris meshes, leftover mount getters,
# GetChinMuzzleLocation, leftover apache-own-ship
# surfaces, leftover RadarNode, leftover Gunner, and
# leftover searchlight-track-runtime-defaults #7347
# stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "void SetSearchlightTracked(bool bTracked);",
    "TObjectPtr<USkyguardBossWeakPointComponent> PortNavigationVane;",
    "TObjectPtr<USkyguardBossWeakPointComponent> StarboardNavigationVane;",
    "TObjectPtr<USkyguardBossWeakPointComponent> Jammer;",
    "TObjectPtr<USkyguardBossWeakPointComponent> PowerBus;",
    "TObjectPtr<UStaticMeshComponent> DebrisPortVane;",
    "TObjectPtr<UStaticMeshComponent> DebrisStarboardVane;",
    "TObjectPtr<UStaticMeshComponent> DebrisJammer;",
    "USceneComponent* GetGunnerMount() const { return GunnerMount; }",
    "USceneComponent* GetEyeMount() const { return EyeMount; }",
    "USceneComponent* GetWeaponMount() const { return WeaponMount; }",
    "USceneComponent* GetChinTurret() const { return ChinTurret; }",
    "USceneComponent* GetPilotMount() const { return PilotMount; }",
    "USceneComponent* GetSensorTurret() const { return SensorTurret; }",
    "FVector GetChinMuzzleLocation() const;",
)
SET_SEARCHLIGHT_TRACKED_NOT_LOCKED = (
    "void SetSearchlightTracked(bool bTracked);",
)
WEAK_POINT_FIELDS_NOT_LOCKED = (
    "PortNavigationVane",
    "StarboardNavigationVane",
    "Jammer",
    "PowerBus",
    "USkyguardBossWeakPointComponent",
)
DEBRIS_FIELDS_NOT_LOCKED = (
    "DebrisPortVane",
    "DebrisStarboardVane",
    "DebrisJammer",
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
LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED = (
    "test_searchlight_track_runtime_defaults_contract.py",
    "FSkyguardSearchlightTrackRuntime",
)
LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED = (
    "test_apache_aircraft_empty_fail_closed.py",
    "test_apache_aircraft_empty_fail_closed_tests.py",
    "test_apache_aircraft_empty_fail_closed_contract.py",
)
LEFTOVER_CHIN_MUZZLE_NOT_LOCKED = (
    "test_apache_chin_muzzle_tests.py",
    "test_apache_chin_muzzle_contract.py",
    "GetChinMuzzleLocation",
)
LEFTOVER_OWN_SHIP_NOT_LOCKED = (
    "test_apache_own_ship_systems_contract.py",
    "test_apache_own_ship_systems_tests.py",
    "ESkyguardApacheSystem",
)
LEFTOVER_CPG_FEEL_NOT_LOCKED = (
    "test_apache_cpg_feel_contract.py",
    "test_apache_cpg_feel_tests.py",
    "test_apache_cpg_feel.py",
)
LEFTOVER_RADAR_NODE_NOT_LOCKED = (
    "SkyguardRadarNode.h",
    "SkyguardRadarNode.cpp",
)
LEFTOVER_GUNNER_NOT_LOCKED = (
    "SkyguardGunner.h",
    "SkyguardGunner.cpp",
    "SkyguardGunnerCampaign.cpp",
    "test_gunner_empty_fail_closed.py",
    "test_gunner_helpers.py",
    "test_gunner_campaign.py",
)
LEFTOVER_SETTINGS_INPUT_NOT_LOCKED = (
    "test_settings_get_invert_vertical_look_decl_contract.py",
    "test_settings_set_invert_vertical_look_decl_contract.py",
    "test_input_capture_is_capture_active_decl_contract.py",
    "test_input_capture_record_player_event_decl_contract.py",
    "test_input_capture_record_gameplay_event_decl_contract.py",
    "test_game_user_settings_getter_decl_contract.py",
    "test_settings_apply_broadcast_tests.py",
)
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
LEFTOVER_CPG_HUD_NOT_LOCKED = (
    "SkyguardCpgHud",
    "SkyguardCpgSightHud",
    "ASkyguardCpgHud",
    "ASkyguardCpgSightHud",
    "test_sortie_hud_host_fail_closed.py",
    "test_sortie_hud_host_fail_closed_tests.py",
    "test_sortie_hud_host_fail_closed_contract.py",
)
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
# .cpp IsSearchlightTracked body / invented INDEX_NONE
# stay unlocked. Do not invent INDEX_NONE or lock the
# cpp body. Do not parse leftover HUD classes.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "ASkyguardBlackKiteBoss::IsSearchlightTracked",
    "SkyguardBlackKiteBoss.cpp",
)
SIBLING_TYPES = (
    "FSkyguardSearchlightTrackRuntime",
    "USkyguardDebriefWidget",
    "USkyguardBriefingWidget",
    "ASkyguardApacheAircraft",
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


def leftover_emergency_finish_tokens() -> tuple[str, ...]:
    return (
        "ArmEmergency" + "Ri" + "fle" + "Finish",
        "IsEmergency" + "Ri" + "fle" + "FinishArmed",
    )


def leftover_live_copy_boss_scripts() -> tuple[str, ...]:
    live = "ri" + "fle"
    seeker = "ig" + "la"
    return (
        f"Scripts/tests/test_black_kite_arm_emergency_{live}_finish_decl_contract.py",
        f"Scripts/tests/test_black_kite_is_emergency_{live}_finish_armed_decl_contract.py",
        f"Scripts/tests/test_breakwater_arm_emergency_{live}_finish_decl_contract.py",
        f"Scripts/tests/test_road_hunter_arm_emergency_{live}_finish_decl_contract.py",
        f"Scripts/tests/test_runway_breaker_arm_emergency_{live}_finish_decl_contract.py",
        f"Scripts/tests/test_{seeker}_boss_empty_fail_closed.py",
        f"Scripts/tests/test_{seeker}_boss_decl_contract.py",
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


def all_locked_scripts() -> tuple[str, ...]:
    return LOCKED_SCRIPTS + leftover_live_copy_boss_scripts()


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


class BlackKiteIsSearchlightTrackedDeclContractTests(unittest.TestCase):
    def test_black_kite_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, IS_SEARCHLIGHT_TRACKED),
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
            "class SKYGUARD52_API AOtherBlackKiteBoss "
            ": public AActor\n"
            "{\n"
            "public:\n"
            f"\t{IS_SEARCHLIGHT_TRACKED}\n"
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
            f"\t{IS_SEARCHLIGHT_TRACKED}\n"
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
            "\tvoid SetSearchlightTracked(bool bTracked);\n"
            "private:\n"
            f"\t{IS_SEARCHLIGHT_TRACKED}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, IS_SEARCHLIGHT_TRACKED)
        self.assertIn("IsSearchlightTracked", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, IS_SEARCHLIGHT_TRACKED))

    def test_missing_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tvoid SetSearchlightTracked(bool bTracked);\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "PortNavigationVane;\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> Jammer;\n"
            "\tTObjectPtr<UStaticMeshComponent> DebrisPortVane;\n"
            "\tUSceneComponent* GetGunnerMount() const "
            "{ return GunnerMount; }\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, IS_SEARCHLIGHT_TRACKED)
        self.assertIn("IsSearchlightTracked", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_BOSS}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, IS_SEARCHLIGHT_TRACKED)
        self.assertIn("IsSearchlightTracked", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_BOSS, section)
        self.assertTrue(
            has_declaration(section, IS_SEARCHLIGHT_TRACKED),
            section,
        )
        self.assertNotIn("BlueprintPure", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("UFUNCTION", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("Category", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("BlueprintCallable", IS_SEARCHLIGHT_TRACKED)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tvoid SetSearchlightTracked(bool bTracked);\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "PortNavigationVane;\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "StarboardNavigationVane;\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> Jammer;\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> PowerBus;\n"
            "\tTObjectPtr<UStaticMeshComponent> DebrisPortVane;\n"
            "\tTObjectPtr<UStaticMeshComponent> DebrisStarboardVane;\n"
            "\tTObjectPtr<UStaticMeshComponent> DebrisJammer;\n"
            "\tUSceneComponent* GetGunnerMount() const "
            "{ return GunnerMount; }\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, IS_SEARCHLIGHT_TRACKED)
        self.assertIn("IsSearchlightTracked", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_parens = "\tbool IsSearchlightTracked const;\n"
        wrong_return_void = "\tvoid IsSearchlightTracked() const;\n"
        wrong_return_int = "\tint32 IsSearchlightTracked() const;\n"
        missing_const = "\tbool IsSearchlightTracked();\n"
        added_arg = "\tbool IsSearchlightTracked(bool bTracked) const;\n"
        leftover_set = "\tvoid SetSearchlightTracked(bool bTracked);\n"
        leftover_vane = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "PortNavigationVane;\n"
        )
        leftover_muzzle = "\tFVector GetChinMuzzleLocation() const;\n"
        leftover_mount = (
            "\tUSceneComponent* GetGunnerMount() const "
            "{ return GunnerMount; }\n"
        )
        leftover_runtime = (
            "\tFSkyguardSearchlightTrackRuntime SearchlightTrack;\n"
        )
        leftover_emergency = (
            "\tbool "
            + leftover_emergency_finish_tokens()[0]
            + "();\n"
        )
        leftover_armed = (
            "\tbool "
            + leftover_emergency_finish_tokens()[1]
            + "() const;\n"
        )
        for region in (
            missing_parens,
            wrong_return_void,
            wrong_return_int,
            missing_const,
            added_arg,
            leftover_set,
            leftover_vane,
            leftover_muzzle,
            leftover_mount,
            leftover_runtime,
            leftover_emergency,
            leftover_armed,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, IS_SEARCHLIGHT_TRACKED)
            self.assertIn("IsSearchlightTracked", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, IS_SEARCHLIGHT_TRACKED),
            IS_SEARCHLIGHT_TRACKED,
        )
        self.assertTrue(has_declaration(section, IS_SEARCHLIGHT_TRACKED))
        self.assertEqual(
            declaration_count(section, IS_SEARCHLIGHT_TRACKED),
            1,
        )
        self.assertTrue(
            IS_SEARCHLIGHT_TRACKED.startswith("bool "),
            IS_SEARCHLIGHT_TRACKED,
        )
        self.assertTrue(
            IS_SEARCHLIGHT_TRACKED.endswith(";"),
            IS_SEARCHLIGHT_TRACKED,
        )
        self.assertIn("IsSearchlightTracked()", IS_SEARCHLIGHT_TRACKED)
        self.assertIn(" const", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("INDEX_NONE", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("{", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("}", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return ", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return bSearchlightTracked", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("SetSearchlightTracked", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("GetChinMuzzleLocation", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("GetGunnerMount", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("PortNavigationVane", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("FSkyguardSearchlightTrackRuntime", IS_SEARCHLIGHT_TRACKED)
        for token in leftover_emergency_finish_tokens():
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)

    def test_declaration_accepts_origin_main_inline_and_prototype(self) -> None:
        one_line_prototype = (
            f"{{\npublic:\n\t{IS_SEARCHLIGHT_TRACKED}\n}}\n"
        )
        self.assertTrue(
            has_declaration(one_line_prototype, IS_SEARCHLIGHT_TRACKED)
        )
        self.assertEqual(
            require_declaration(one_line_prototype, IS_SEARCHLIGHT_TRACKED),
            IS_SEARCHLIGHT_TRACKED,
        )
        exact_inline = (
            "bool IsSearchlightTracked() "
            "const { return bSearchlightTracked; }"
        )
        self.assertTrue(has_declaration(exact_inline, IS_SEARCHLIGHT_TRACKED))
        self.assertEqual(
            require_declaration(exact_inline, IS_SEARCHLIGHT_TRACKED),
            IS_SEARCHLIGHT_TRACKED,
        )
        self.assertEqual(
            declaration_count(exact_inline, IS_SEARCHLIGHT_TRACKED),
            1,
        )
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, IS_SEARCHLIGHT_TRACKED),
            section,
        )
        self.assertEqual(
            require_declaration(section, IS_SEARCHLIGHT_TRACKED),
            IS_SEARCHLIGHT_TRACKED,
        )
        self.assertNotIn("{", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return bSearchlightTracked", IS_SEARCHLIGHT_TRACKED)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tbool\n"
            "\tIsSearchlightTracked() const;\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tbool IsSearchlightTracked(\n"
            "\t) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tbool IsSearchlightTracked()\n"
            "\tconst;\n"
            "};\n"
        )
        wrap_inline = (
            "public:\n"
            "\tbool IsSearchlightTracked()\n"
            "\tconst { return bSearchlightTracked; }\n"
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
                has_declaration(section, IS_SEARCHLIGHT_TRACKED),
                section,
            )
            self.assertEqual(
                require_declaration(section, IS_SEARCHLIGHT_TRACKED),
                IS_SEARCHLIGHT_TRACKED,
            )
            self.assertEqual(
                declaration_count(section, IS_SEARCHLIGHT_TRACKED),
                1,
            )
        one_line = f"{{\npublic:\n\t{IS_SEARCHLIGHT_TRACKED}\n}}\n"
        self.assertTrue(has_declaration(one_line, IS_SEARCHLIGHT_TRACKED))
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, IS_SEARCHLIGHT_TRACKED),
            section,
        )
        self.assertEqual(
            require_declaration(section, IS_SEARCHLIGHT_TRACKED),
            IS_SEARCHLIGHT_TRACKED,
        )

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tbool IsSearchlightTracked() const\n"
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
            has_declaration(section, IS_SEARCHLIGHT_TRACKED),
            section,
        )
        self.assertEqual(
            require_declaration(section, IS_SEARCHLIGHT_TRACKED),
            IS_SEARCHLIGHT_TRACKED,
        )
        self.assertEqual(
            declaration_count(section, IS_SEARCHLIGHT_TRACKED),
            1,
        )
        self.assertNotIn("{", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("}", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return ", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return bSearchlightTracked", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return Other", IS_SEARCHLIGHT_TRACKED)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", IS_SEARCHLIGHT_TRACKED)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_searchlight_cpp_body(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        self.assertNotIn("{", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("}", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return ", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return bSearchlightTracked", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return bSearchlightTracked", locked_only)
        self.assertNotIn(
            "ASkyguardBlackKiteBoss::IsSearchlightTracked",
            IS_SEARCHLIGHT_TRACKED,
        )
        self.assertNotIn("SkyguardBlackKiteBoss.cpp", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("SkyguardBlackKiteBoss.cpp", locked_only)
        self.assertNotIn("return false", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return true", IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_relock_set_searchlight_tracked(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for neighbor in SET_SEARCHLIGHT_TRACKED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("SetSearchlightTracked", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("SetSearchlightTracked", locked_only)

    def test_contract_does_not_relock_leftover_emergency_finish(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for token in leftover_emergency_finish_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_relock_leftover_searchlight_runtime(
        self,
    ) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for token in LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn(
            "test_searchlight_track_runtime_defaults_contract.py",
            IS_SEARCHLIGHT_TRACKED,
        )
        self.assertNotIn(
            "FSkyguardSearchlightTrackRuntime",
            IS_SEARCHLIGHT_TRACKED,
        )

    def test_contract_does_not_relock_weak_point_fields(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for token in WEAK_POINT_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in DEBRIS_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("PortNavigationVane", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("USkyguardBossWeakPointComponent", locked_only)

    def test_contract_does_not_relock_mount_getters(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for token in MOUNT_GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("GetGunnerMount", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("GetEyeMount", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("GetWeaponMount", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("GetChinTurret", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("GetPilotMount", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("GetSensorTurret", IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_relock_chin_muzzle(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for neighbor in GET_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("GetChinMuzzleLocation", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_relock_leftover_chin_muzzle(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_relock_leftover_own_ship_systems(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("ESkyguardApacheSystem", IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_relock_leftover_cpg_feel(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_relock_leftover_radar_node(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_relock_leftover_gunner(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_relock_leftover_settings_input(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for token in LEFTOVER_SETTINGS_INPUT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_relock_leftover_widget_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardDebriefWidget", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("USkyguardBriefingWidget", IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_relock_leftover_cpg_hud(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_HUD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("ESkyguardMissionSkylineStyle", IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        self.assertEqual(
            require_declaration(locked_only, IS_SEARCHLIGHT_TRACKED),
            IS_SEARCHLIGHT_TRACKED,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("SetSearchlightTracked", locked_only)
        self.assertNotIn("PortNavigationVane", locked_only)
        self.assertNotIn("GetGunnerMount", locked_only)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)
        for token in leftover_emergency_finish_tokens():
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
        self.assertEqual(
            require_declaration(section, IS_SEARCHLIGHT_TRACKED),
            IS_SEARCHLIGHT_TRACKED,
        )
        self.assertEqual(
            declaration_count(section, IS_SEARCHLIGHT_TRACKED),
            1,
        )
        self.assertNotIn("SkyguardBlackKiteBoss.cpp", section)
        self.assertNotIn(
            "ASkyguardBlackKiteBoss::IsSearchlightTracked",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBlackKiteBoss.cpp", section)
        self.assertNotIn(
            "ASkyguardBlackKiteBoss::IsSearchlightTracked",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("}", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return false", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return true", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return bSearchlightTracked", IS_SEARCHLIGHT_TRACKED)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        file_text = this_file_text()
        # Harbor clock field names stay off this class public
        # section. Literal Harbor interval retune tokens fail
        # closed in this file and the locked declaration
        # only: public MaxIntegrity is not a Harbor clock.
        # Pathfinder MinHeightFromOriginCm is the wrong
        # header; do not scan it.
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
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
                "Black Kite IsSearchlightTracked contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, IS_SEARCHLIGHT_TRACKED.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)
        # Leftover emergency-finish surfaces live in the
        # origin/main public section and stay unlocked.
        # Do not scan that section for leftover live-copy
        # tokens.

    def test_declaration_bans_retired_live_copy(self) -> None:
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                IS_SEARCHLIGHT_TRACKED.lower(),
                "Black Kite IsSearchlightTracked contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, IS_SEARCHLIGHT_TRACKED)

    def test_contract_is_searchlight_tracked_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, IS_SEARCHLIGHT_TRACKED),
            IS_SEARCHLIGHT_TRACKED,
        )
        locked_only = f"{IS_SEARCHLIGHT_TRACKED}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("SetSearchlightTracked", locked_only)
        self.assertNotIn("PortNavigationVane", locked_only)
        self.assertNotIn("StarboardNavigationVane", locked_only)
        self.assertNotIn("GetGunnerMount", locked_only)
        self.assertNotIn("GetEyeMount", locked_only)
        self.assertNotIn("GetWeaponMount", locked_only)
        self.assertNotIn("GetChinTurret", locked_only)
        self.assertNotIn("GetPilotMount", locked_only)
        self.assertNotIn("GetSensorTurret", locked_only)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)
        self.assertNotIn("HarborIndustrial", locked_only)
        self.assertNotIn("USkyguardDebriefWidget", locked_only)
        self.assertNotIn("USkyguardBriefingWidget", locked_only)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn("FSkyguardSearchlightTrackRuntime", locked_only)
        for token in leftover_emergency_finish_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in LEFTOVER_SETTINGS_INPUT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in LEFTOVER_CPG_HUD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in leftover_short_roster_values():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in leftover_live_copy_boss_scripts():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, IS_SEARCHLIGHT_TRACKED)
            self.assertNotIn(token, section)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, IS_SEARCHLIGHT_TRACKED.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("return bSearchlightTracked", IS_SEARCHLIGHT_TRACKED)
        self.assertNotIn("{", IS_SEARCHLIGHT_TRACKED)
        self.assertTrue(IS_SEARCHLIGHT_TRACKED.startswith("bool "))
        self.assertTrue(IS_SEARCHLIGHT_TRACKED.endswith(";"))
        self.assertIn(" const", IS_SEARCHLIGHT_TRACKED)
        self.assertIn(UFUNCTION_BOSS, section)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in all_locked_scripts():
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
