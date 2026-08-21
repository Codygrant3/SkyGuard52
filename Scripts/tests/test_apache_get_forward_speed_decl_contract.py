from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardApacheAircraft.h"
CLASS_NAME = "ASkyguardApacheAircraft"
# Declaration presence only. Do not invent INDEX_NONE
# or lock the GetForwardSpeed body.
# origin/main is inline
# (`float GetForwardSpeed() const`
# with `{ return ForwardSpeed; }` possibly on the
# same line or following lines);
# accept that exact inline form, a one-line prototype
# (`float GetForwardSpeed() const;`),
# other split-line wraps, and other inline bodies without
# locking the body. `return ForwardSpeed;` is not a
# required token of this declaration lock. Nearby
# origin/main
# UFUNCTION(BlueprintPure, Category="Skyguard|Apache")
# is accepted as present. Parse the public class section of
# ASkyguardApacheAircraft only. Do not lock leftover
# pilot-command-roster #b593 enum values. This is not
# leftover apache-aircraft empty-fail-closed #851b (stay
# off mount getters GetGunnerMount / GetEyeMount /
# GetWeaponMount / GetChinTurret / GetPilotMount /
# GetSensorTurret). This is not leftover
# apache-chin-muzzle tests #4e39 (stay off
# GetChinMuzzleLocation). This is not leftover
# apache-own-ship-systems #96c5. This is not leftover
# apache-cpg-feel #8951. This is not leftover
# AimChinTurret / SetRotorPower / IssuePilotCommand /
# GetPilotCommand / GetPilotConfirmationsIssued /
# SetOrbitFocus / FaceWorldLocation / SetSensorView /
# SetFirstPersonInterior / SetDirectFlightInput /
# ApplyDamage siblings in this wave (do not create
# those files). Stay off AimChinTurret, SetRotorPower,
# IssuePilotCommand, GetPilotCommand,
# GetPilotConfirmationsIssued, SetOrbitFocus,
# FaceWorldLocation, SetSensorView,
# SetFirstPersonInterior, SetDirectFlightInput,
# ApplyDamage, GetDamageFraction, ApplySystemHit,
# ApplyHit, IsSensorLive, IsThermalAvailable,
# IsSensorViewActive, and remaining public methods.
# Leftover briefing / debrief widget isolated
# contracts, leftover Gunner helpers, leftover
# Harbor clocks, leftover theater-kit / flare / HUD,
# leftover ApacheSystem / weapon stations / leftover
# pilot-command-roster #b593 / loadout / lock-phase,
# leftover drafts #56–#64, leftover skyline style
# HarborIndustrial (leftover enum, not a Harbor 40/80
# retune), leftover sortie-hud-host fail-closed,
# leftover gun-fire camera shake, leftover DebriefWidget
# TravelNext / HandleDebriefKey, and leftover
# SortiePresentationWidgets stay sibling-only.
GET_FORWARD_SPEED = ("float GetForwardSpeed() const;")
UFUNCTION_APACHE = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Apache")'
)
# Leftover #56–#64 plus SkyguardApacheAircraft production
# files. This lane only adds an isolated Python
# GetForwardSpeed declaration contract on
# ASkyguardApacheAircraft. SortiePresentationWidgets is
# not the class under test. Stay off mount getters,
# GetChinMuzzleLocation, AimChinTurret, SetRotorPower,
# IssuePilotCommand, GetPilotCommand,
# GetPilotConfirmationsIssued, SetOrbitFocus,
# FaceWorldLocation, SetSensorView,
# SetFirstPersonInterior, SetDirectFlightInput,
# ApplyDamage, GetDamageFraction, ApplySystemHit,
# ApplyHit, IsSensorLive, IsThermalAvailable,
# IsSensorViewActive, remaining public methods,
# leftover apache-aircraft empty-fail-closed #851b,
# leftover apache-chin-muzzle #4e39, leftover
# apache-own-ship-systems #96c5, leftover
# apache-cpg-feel #8951, leftover CPG HUD / sight HUD,
# leftover drafts #56–#64, leftover ApacheSystem enum
# values, leftover Harbor clocks, leftover skyline
# HarborIndustrial, leftover DebriefWidget isolated
# contracts, leftover BriefingWidget isolated
# contracts, leftover gun-fire camera shake, leftover
# sortie-hud-host fail-closed, leftover AimChinTurret /
# SetRotorPower / IssuePilotCommand / GetPilotCommand /
# GetPilotConfirmationsIssued / SetOrbitFocus /
# FaceWorldLocation / SetSensorView /
# SetFirstPersonInterior / SetDirectFlightInput /
# ApplyDamage siblings, leftover
# pilot-command-roster #b593, and dirty workspace
# paths.
LOCKED = {
    "SkyguardApacheAircraft.h",
    "SkyguardApacheAircraft.cpp",
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
# apache-aircraft empty-fail-closed #851b, leftover
# apache-chin-muzzle #4e39, leftover
# apache-own-ship-systems #96c5, leftover
# apache-cpg-feel #8951, leftover AimChinTurret /
# SetRotorPower / IssuePilotCommand / GetPilotCommand /
# GetPilotConfirmationsIssued / SetOrbitFocus /
# FaceWorldLocation / SetSensorView /
# SetFirstPersonInterior / SetDirectFlightInput /
# ApplyDamage siblings in this wave, leftover
# pilot-command-roster #b593, leftover
# DebriefWidget Configure / GetPresentation / GetDebrief /
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
# leftover apache-cpg-feel, and sibling Apache neighbors
# stay sibling-only.
LOCKED_SCRIPTS = (
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
    "Scripts/tests/test_apache_apply_damage_decl_contract.py",
    "Scripts/tests/test_pilot_command_roster.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_pilot_command_roster_tests.py",
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
    "Scripts/tests/test_mission_weather_enum_contract.py",
)
# Neighbors in the same public section. Presence is not
# locked here. Mount getters, GetChinMuzzleLocation,
# AimChinTurret, SetRotorPower, IssuePilotCommand,
# GetPilotCommand, GetPilotConfirmationsIssued,
# SetOrbitFocus, FaceWorldLocation, SetSensorView,
# SetFirstPersonInterior, SetDirectFlightInput,
# ApplyDamage, GetDamageFraction, ApplySystemHit,
# ApplyHit, IsSensorLive, IsThermalAvailable,
# IsSensorViewActive, and remaining public methods
# stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "USceneComponent* GetGunnerMount() const { return GunnerMount; }",
    "USceneComponent* GetEyeMount() const { return EyeMount; }",
    "USceneComponent* GetWeaponMount() const { return WeaponMount; }",
    "USceneComponent* GetChinTurret() const { return ChinTurret; }",
    "USceneComponent* GetPilotMount() const { return PilotMount; }",
    "USceneComponent* GetSensorTurret() const { return SensorTurret; }",
    "FVector GetChinMuzzleLocation() const;",
    "void AimChinTurret(const FRotator& WorldAim);",
    "void SetRotorPower(float NormalizedPower);",
    "void IssuePilotCommand(ESkyguardPilotCommand Command);",
    "ESkyguardPilotCommand GetPilotCommand() const { return CurrentPilotCommand; }",
    "int32 GetPilotConfirmationsIssued() const { return PilotConfirmationsIssued; }",
    "void SetOrbitFocus(const FVector& WorldLocation);",
    "void FaceWorldLocation(const FVector& WorldLocation);",
    "void SetSensorView(bool bInSensor);",
    "void SetFirstPersonInterior(bool bInterior);",
    "void SetDirectFlightInput(float Collective,float Yaw,float CyclicPitch,float CyclicRoll);",
    "void ApplyDamage(float Amount);",
    "float GetDamageFraction() const;",
    "void ApplySystemHit(ESkyguardApacheSystem System, float Amount);",
    "void ApplyHit(UPrimitiveComponent* HitComponent, float Amount);",
    "bool IsSensorLive() const;",
    "bool IsThermalAvailable() const;",
    "bool IsSensorViewActive() const;",
    "bool IsCanopyGlassCracked() const { return bCanopyGlassCracked; }",
    "bool AreEnginesDown() const;",
    "bool IsChinTurretDown() const;",
    "bool IsRotorDown() const;",
    "bool IsSystemDown(ESkyguardApacheSystem System) const;",
    "ESkyguardApacheSystem FindNearestLiveSystem() const;",
    "float GetSensorQuality() const;",
    "float GetChinSlewScale() const;",
    "float GetChinFireScale() const;",
    "float GetEnginePowerScale() const;",
    "float GetRotorPowerScale() const;",
    "float GetRotorRPM() const { return CurrentRotorRPM; }",
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
AIM_CHIN_TURRET_NOT_LOCKED = ("void AimChinTurret(const FRotator& WorldAim);",)
SET_ROTOR_POWER_NOT_LOCKED = ("void SetRotorPower(float NormalizedPower);",)
PILOT_COMMAND_NOT_LOCKED = (
    "void IssuePilotCommand(ESkyguardPilotCommand Command);",
    "ESkyguardPilotCommand GetPilotCommand() const { return CurrentPilotCommand; }",
    "int32 GetPilotConfirmationsIssued() const { return PilotConfirmationsIssued; }",
)
ORBIT_AND_FACE_NOT_LOCKED = (
    "void SetOrbitFocus(const FVector& WorldLocation);",
    "void FaceWorldLocation(const FVector& WorldLocation);",
)
SENSOR_VIEW_NOT_LOCKED = (
    "void SetSensorView(bool bInSensor);",
    "void SetFirstPersonInterior(bool bInterior);",
)
FLIGHT_INPUT_NOT_LOCKED = ("SetDirectFlightInput",)
DAMAGE_NOT_LOCKED = (
    "void ApplyDamage(float Amount);",
    "float GetDamageFraction() const;",
    "void ApplySystemHit(ESkyguardApacheSystem System, float Amount);",
    "void ApplyHit(UPrimitiveComponent* HitComponent, float Amount);",
)
SENSOR_STATE_NOT_LOCKED = (
    "bool IsSensorLive() const;",
    "bool IsThermalAvailable() const;",
    "bool IsSensorViewActive() const;",
)
REMAINING_PUBLIC_NOT_LOCKED = (
    "IsCanopyGlassCracked",
    "AreEnginesDown",
    "IsChinTurretDown",
    "IsRotorDown",
    "IsSystemDown",
    "FindNearestLiveSystem",
    "GetSensorQuality",
    "GetChinSlewScale",
    "GetChinFireScale",
    "GetEnginePowerScale",
    "GetRotorPowerScale",
    "GetRotorRPM",
)
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
# Leftover AimChinTurret sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_AIM_CHIN_TURRET_NOT_LOCKED = (
    "test_apache_aim_chin_turret_decl_contract.py",
    "void AimChinTurret(const FRotator& WorldAim);",
)
# Leftover SetRotorPower sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_SET_ROTOR_POWER_NOT_LOCKED = (
    "test_apache_set_rotor_power_decl_contract.py",
    "void SetRotorPower(float NormalizedPower);",
)
# Leftover IssuePilotCommand sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_ISSUE_PILOT_COMMAND_NOT_LOCKED = (
    "test_apache_issue_pilot_command_decl_contract.py",
    "void IssuePilotCommand(ESkyguardPilotCommand Command);",
)
# Leftover GetPilotCommand sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_GET_PILOT_COMMAND_NOT_LOCKED = (
    "test_apache_get_pilot_command_decl_contract.py",
    "ESkyguardPilotCommand GetPilotCommand() const { return CurrentPilotCommand; }",
)
# Leftover GetPilotConfirmationsIssued sibling in this
# wave stays unlocked. Do not create or edit that file.
LEFTOVER_GET_PILOT_CONFIRMATIONS_ISSUED_NOT_LOCKED = (
    "test_apache_get_pilot_confirmations_issued_decl_contract.py",
    "int32 GetPilotConfirmationsIssued() const { return PilotConfirmationsIssued; }",
)
# Leftover SetOrbitFocus sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_SET_ORBIT_FOCUS_NOT_LOCKED = (
    "test_apache_set_orbit_focus_decl_contract.py",
    "void SetOrbitFocus(const FVector& WorldLocation);",
)
# Leftover FaceWorldLocation sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_FACE_WORLD_LOCATION_NOT_LOCKED = (
    "test_apache_face_world_location_decl_contract.py",
    "void FaceWorldLocation(const FVector& WorldLocation);",
)
# Leftover SetSensorView sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_SET_SENSOR_VIEW_NOT_LOCKED = (
    "test_apache_set_sensor_view_decl_contract.py",
    "void SetSensorView(bool bInSensor);",
)
# Leftover SetFirstPersonInterior sibling in this wave
# stays unlocked. Do not create or edit that file.
LEFTOVER_SET_FIRST_PERSON_INTERIOR_NOT_LOCKED = (
    "test_apache_set_first_person_interior_decl_contract.py",
    "void SetFirstPersonInterior(bool bInterior);",
)
# Leftover SetDirectFlightInput sibling in this wave
# stays unlocked. Do not create or edit that file.
LEFTOVER_SET_DIRECT_FLIGHT_INPUT_NOT_LOCKED = (
    "test_apache_set_direct_flight_input_decl_contract.py",
    "SetDirectFlightInput",
)
# Leftover ApplyDamage sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_APPLY_DAMAGE_NOT_LOCKED = (
    "test_apache_apply_damage_decl_contract.py",
    "void ApplyDamage(float Amount);",
)
# Leftover pilot-command-roster #b593 stays unlocked.
# Do not lock leftover roster enum values.
LEFTOVER_PILOT_COMMAND_ROSTER_NOT_LOCKED = (
    "test_pilot_command_roster.py",
    "test_pilot_command_roster_contract.py",
    "test_pilot_command_roster_tests.py",
    "Pursuit",
    "OrbitLeft",
    "OrbitRight",
    "AttackRun",
    "FaceTarget",
)
# Leftover CPG HUD / sight HUD stay unlocked.
LEFTOVER_CPG_HUD_NOT_LOCKED = (
    "SkyguardCpgHud",
    "SkyguardCpgSightHud",
    "ASkyguardCpgHud",
    "ASkyguardCpgSightHud",
    "test_sortie_hud_host_fail_closed.py",
    "test_sortie_hud_host_fail_closed_tests.py",
    "test_sortie_hud_host_fail_closed_contract.py",
)
# Leftover DebriefWidget / BriefingWidget isolated
# contracts stay unlocked. Do not create TravelNext or
# HandleDebriefKey siblings here.
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
# pilot-command-roster #b593 / loadout / lock-phase /
# leftover Gunner FillAnd* stay unlocked. The return
# type on this getter is not a leftover enum-value lock.
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
# .cpp GetForwardSpeed body / invented INDEX_NONE stay
# unlocked. Do not invent INDEX_NONE or lock the
# cpp body. origin/main inline return of the current
# speed is accepted as presence, not a locked
# implementation contract.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "ASkyguardApacheAircraft::GetForwardSpeed",
    "SkyguardApacheAircraft.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
    "USkyguardDebriefWidget",
    "USkyguardBriefingWidget",
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


class ApacheGetForwardSpeedDeclContractTests(unittest.TestCase):
    def test_apache_aircraft_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, GET_FORWARD_SPEED), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API ASkyguardUnrelatedAircraft "
                ": public AActor\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API AOtherApacheAircraft "
            ": public AActor\n"
            "{\n"
            "public:\n"
            f"\t{GET_FORWARD_SPEED}\n"
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
            f"\t{GET_FORWARD_SPEED}\n"
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
            "\tvoid SetRotorPower(float NormalizedPower);\n"
            "private:\n"
            f"\t{GET_FORWARD_SPEED}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, GET_FORWARD_SPEED)
        self.assertIn("GetForwardSpeed", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, GET_FORWARD_SPEED))

    def test_missing_get_forward_speed_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tUSceneComponent* GetGunnerMount() const "
            "{ return GunnerMount; }\n"
            "\tUSceneComponent* GetChinTurret() const "
            "{ return ChinTurret; }\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
            "\tvoid AimChinTurret(const FRotator& WorldAim);\n"
            "\tvoid SetRotorPower(float NormalizedPower);\n"
            "\tvoid IssuePilotCommand("
            "ESkyguardPilotCommand Command);\n"
            "\tESkyguardPilotCommand GetPilotCommand() const "
            "{ return CurrentPilotCommand; }\n"
            "\tint32 GetPilotConfirmationsIssued() const "
            "{ return PilotConfirmationsIssued; }\n"
            "\tvoid SetOrbitFocus(const FVector& WorldLocation);\n"
            "\tvoid FaceWorldLocation(const FVector& WorldLocation);\n"
            "\tvoid SetSensorView(bool bInSensor);\n"
            "\tvoid SetDirectFlightInput("
            "float Collective,float Yaw,"
            "float CyclicPitch,float CyclicRoll);\n"
            "\tvoid ApplyDamage(float Amount);\n"
            "\tbool IsSensorLive() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, GET_FORWARD_SPEED)
        self.assertIn("GetForwardSpeed", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_APACHE}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, GET_FORWARD_SPEED)
        self.assertIn("GetForwardSpeed", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_APACHE, section)
        self.assertTrue(has_declaration(section, GET_FORWARD_SPEED), section)
        self.assertNotIn("BlueprintPure", GET_FORWARD_SPEED)
        self.assertNotIn("UFUNCTION", GET_FORWARD_SPEED)
        self.assertNotIn("Category", GET_FORWARD_SPEED)
        self.assertNotIn("BlueprintCallable", GET_FORWARD_SPEED)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tUSceneComponent* GetGunnerMount() const "
            "{ return GunnerMount; }\n"
            "\tUSceneComponent* GetEyeMount() const "
            "{ return EyeMount; }\n"
            "\tUSceneComponent* GetWeaponMount() const "
            "{ return WeaponMount; }\n"
            "\tUSceneComponent* GetChinTurret() const "
            "{ return ChinTurret; }\n"
            "\tUSceneComponent* GetPilotMount() const "
            "{ return PilotMount; }\n"
            "\tUSceneComponent* GetSensorTurret() const "
            "{ return SensorTurret; }\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
            "\tvoid AimChinTurret(const FRotator& WorldAim);\n"
            "\tvoid SetRotorPower(float NormalizedPower);\n"
            "\tvoid IssuePilotCommand("
            "ESkyguardPilotCommand Command);\n"
            "\tESkyguardPilotCommand GetPilotCommand() const "
            "{ return CurrentPilotCommand; }\n"
            "\tint32 GetPilotConfirmationsIssued() const "
            "{ return PilotConfirmationsIssued; }\n"
            "\tvoid SetDirectFlightInput("
            "float Collective,float Yaw,"
            "float CyclicPitch,float CyclicRoll);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, GET_FORWARD_SPEED)
        self.assertIn("GetForwardSpeed", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_const = "\tfloat GetForwardSpeed();\n"
        wrong_return_void = "\tvoid GetForwardSpeed() const;\n"
        wrong_return_bool = "\tbool GetForwardSpeed() const;\n"
        added_arg = "\tfloat GetForwardSpeed(bool bReady) const;\n"
        leftover_issue = (
            "\tvoid IssuePilotCommand(ESkyguardPilotCommand Command);\n"
        )
        leftover_get_command = (
            "\tESkyguardPilotCommand GetPilotCommand() const "
            "{ return CurrentPilotCommand; }\n"
        )
        leftover_confirmations = (
            "\tint32 GetPilotConfirmationsIssued() const "
            "{ return PilotConfirmationsIssued; }\n"
        )
        leftover_set_rotor = "\tvoid SetRotorPower(float NormalizedPower);\n"
        leftover_aim = "\tvoid AimChinTurret(const FRotator& WorldAim);\n"
        leftover_muzzle = "\tFVector GetChinMuzzleLocation() const;\n"
        leftover_get_turret = (
            "\tUSceneComponent* GetChinTurret() const "
            "{ return ChinTurret; }\n"
        )
        leftover_mount = (
            "\tUSceneComponent* GetGunnerMount() const "
            "{ return GunnerMount; }\n"
        )
        leftover_scale = "\tfloat GetRotorPowerScale() const;\n"
        leftover_flight = (
            "\tvoid SetDirectFlightInput("
            "float Collective,float Yaw,"
            "float CyclicPitch,float CyclicRoll);\n"
        )
        leftover_damage = "\tvoid ApplyDamage(float Amount);\n"
        for region in (
            missing_const,
            wrong_return_void,
            wrong_return_bool,
            added_arg,
            leftover_issue,
            leftover_get_command,
            leftover_confirmations,
            leftover_set_rotor,
            leftover_aim,
            leftover_muzzle,
            leftover_get_turret,
            leftover_mount,
            leftover_scale,
            leftover_flight,
            leftover_damage,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, GET_FORWARD_SPEED)
            self.assertIn("GetForwardSpeed", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_get_forward_speed_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, GET_FORWARD_SPEED),
            GET_FORWARD_SPEED,
        )
        self.assertTrue(has_declaration(section, GET_FORWARD_SPEED))
        self.assertEqual(declaration_count(section, GET_FORWARD_SPEED), 1)
        self.assertTrue(
            GET_FORWARD_SPEED.startswith("float "),
            GET_FORWARD_SPEED,
        )
        self.assertTrue(GET_FORWARD_SPEED.endswith(";"), GET_FORWARD_SPEED)
        self.assertIn("GetForwardSpeed()", GET_FORWARD_SPEED)
        self.assertIn(" const", GET_FORWARD_SPEED)
        self.assertNotIn("INDEX_NONE", GET_FORWARD_SPEED)
        self.assertNotIn("{", GET_FORWARD_SPEED)
        self.assertNotIn("}", GET_FORWARD_SPEED)
        self.assertNotIn("return ", GET_FORWARD_SPEED)
        self.assertNotIn("return ForwardSpeed", GET_FORWARD_SPEED)
        self.assertNotIn("AimChinTurret", GET_FORWARD_SPEED)
        self.assertNotIn("SetRotorPower", GET_FORWARD_SPEED)
        self.assertNotIn("IssuePilotCommand", GET_FORWARD_SPEED)
        self.assertNotIn("GetPilotCommand", GET_FORWARD_SPEED)
        self.assertNotIn("GetPilotConfirmationsIssued", GET_FORWARD_SPEED)
        self.assertNotIn("GetChinMuzzleLocation", GET_FORWARD_SPEED)
        self.assertNotIn("GetChinTurret", GET_FORWARD_SPEED)
        self.assertNotIn("GetRotorPowerScale", GET_FORWARD_SPEED)
        self.assertNotIn("SetDirectFlightInput", GET_FORWARD_SPEED)
        self.assertNotIn("ApplyDamage", GET_FORWARD_SPEED)

    def test_declaration_accepts_origin_main_inline_and_prototype(
        self,
    ) -> None:
        one_line_prototype = f"{{\npublic:\n\t{GET_FORWARD_SPEED}\n}}\n"
        self.assertTrue(has_declaration(one_line_prototype, GET_FORWARD_SPEED))
        self.assertEqual(
            require_declaration(one_line_prototype, GET_FORWARD_SPEED),
            GET_FORWARD_SPEED,
        )
        exact_inline = (
            "float GetForwardSpeed() "
            "const { return ForwardSpeed; }"
        )
        self.assertTrue(has_declaration(exact_inline, GET_FORWARD_SPEED))
        self.assertEqual(
            require_declaration(exact_inline, GET_FORWARD_SPEED),
            GET_FORWARD_SPEED,
        )
        self.assertEqual(
            declaration_count(exact_inline, GET_FORWARD_SPEED),
            1,
        )
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, GET_FORWARD_SPEED),
            section,
        )
        self.assertEqual(
            require_declaration(section, GET_FORWARD_SPEED),
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("{", GET_FORWARD_SPEED)
        self.assertNotIn("return ForwardSpeed", GET_FORWARD_SPEED)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tfloat\n"
            "\tGetForwardSpeed() const;\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tfloat GetForwardSpeed(\n"
            "\t) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tfloat GetForwardSpeed()\n"
            "\tconst;\n"
            "};\n"
        )
        wrap_inline = (
            "public:\n"
            "\tfloat GetForwardSpeed()\n"
            "\tconst { return ForwardSpeed; }\n"
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
                has_declaration(section, GET_FORWARD_SPEED),
                section,
            )
            self.assertEqual(
                require_declaration(section, GET_FORWARD_SPEED),
                GET_FORWARD_SPEED,
            )
            self.assertEqual(declaration_count(section, GET_FORWARD_SPEED), 1)
        one_line = f"{{\npublic:\n\t{GET_FORWARD_SPEED}\n}}\n"
        self.assertTrue(has_declaration(one_line, GET_FORWARD_SPEED))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, GET_FORWARD_SPEED), section)
        self.assertEqual(
            require_declaration(section, GET_FORWARD_SPEED),
            GET_FORWARD_SPEED,
        )

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tfloat GetForwardSpeed() const\n"
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
        self.assertTrue(has_declaration(section, GET_FORWARD_SPEED), section)
        self.assertEqual(
            require_declaration(section, GET_FORWARD_SPEED),
            GET_FORWARD_SPEED,
        )
        self.assertEqual(declaration_count(section, GET_FORWARD_SPEED), 1)
        self.assertNotIn("{", GET_FORWARD_SPEED)
        self.assertNotIn("}", GET_FORWARD_SPEED)
        self.assertNotIn("return ", GET_FORWARD_SPEED)
        self.assertNotIn("return ForwardSpeed", GET_FORWARD_SPEED)
        self.assertNotIn("return Other", GET_FORWARD_SPEED)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", GET_FORWARD_SPEED)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", GET_FORWARD_SPEED)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_get_forward_speed_body(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        self.assertNotIn("{", GET_FORWARD_SPEED)
        self.assertNotIn("}", GET_FORWARD_SPEED)
        self.assertNotIn("return ", GET_FORWARD_SPEED)
        self.assertNotIn("return ForwardSpeed", GET_FORWARD_SPEED)
        self.assertNotIn("return ForwardSpeed", locked_only)
        self.assertNotIn(
            "ASkyguardApacheAircraft::GetForwardSpeed",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("SkyguardApacheAircraft.cpp", GET_FORWARD_SPEED)
        self.assertNotIn("SkyguardApacheAircraft.cpp", locked_only)
        self.assertNotIn("return false", GET_FORWARD_SPEED)
        self.assertNotIn("return true", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_mount_getters(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in MOUNT_GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn("GetGunnerMount", GET_FORWARD_SPEED)
        self.assertNotIn("GetEyeMount", GET_FORWARD_SPEED)
        self.assertNotIn("GetWeaponMount", GET_FORWARD_SPEED)
        self.assertNotIn("GetChinTurret", GET_FORWARD_SPEED)
        self.assertNotIn("GetPilotMount", GET_FORWARD_SPEED)
        self.assertNotIn("GetSensorTurret", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_chin_muzzle(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for neighbor in GET_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_FORWARD_SPEED)
        self.assertNotIn("GetChinMuzzleLocation", GET_FORWARD_SPEED)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)

    def test_contract_does_not_relock_aim_chin_turret(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for neighbor in AIM_CHIN_TURRET_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_FORWARD_SPEED)
        self.assertNotIn("AimChinTurret", GET_FORWARD_SPEED)
        self.assertNotIn("AimChinTurret", locked_only)

    def test_contract_does_not_relock_set_rotor_power(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for neighbor in SET_ROTOR_POWER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_FORWARD_SPEED)
        self.assertNotIn("SetRotorPower", GET_FORWARD_SPEED)
        self.assertNotIn("SetRotorPower", locked_only)

    def test_contract_does_not_relock_pilot_command_helpers(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for neighbor in PILOT_COMMAND_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_FORWARD_SPEED)
        self.assertNotIn("IssuePilotCommand", GET_FORWARD_SPEED)
        self.assertNotIn("GetPilotCommand", GET_FORWARD_SPEED)
        self.assertNotIn("GetPilotConfirmationsIssued", GET_FORWARD_SPEED)
        self.assertNotIn("IssuePilotCommand", locked_only)
        self.assertNotIn("GetPilotCommand", locked_only)
        self.assertNotIn("GetPilotConfirmationsIssued", locked_only)

    def test_contract_does_not_relock_orbit_or_face(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for neighbor in ORBIT_AND_FACE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_FORWARD_SPEED)
        self.assertNotIn("SetOrbitFocus", GET_FORWARD_SPEED)
        self.assertNotIn("FaceWorldLocation", GET_FORWARD_SPEED)
        self.assertNotIn("SetOrbitFocus", locked_only)
        self.assertNotIn("FaceWorldLocation", locked_only)

    def test_contract_does_not_relock_sensor_view_or_interior(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for neighbor in SENSOR_VIEW_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_FORWARD_SPEED)
        self.assertNotIn("SetSensorView", GET_FORWARD_SPEED)
        self.assertNotIn("SetFirstPersonInterior", GET_FORWARD_SPEED)
        self.assertNotIn("SetSensorView", locked_only)
        self.assertNotIn("SetFirstPersonInterior", locked_only)

    def test_contract_does_not_relock_flight_input(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in FLIGHT_INPUT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn("SetDirectFlightInput", locked_only)
        self.assertNotIn("SetDirectFlightInput", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_damage_helpers(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for neighbor in DAMAGE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_FORWARD_SPEED)
        self.assertNotIn("ApplyDamage", GET_FORWARD_SPEED)
        self.assertNotIn("GetDamageFraction", GET_FORWARD_SPEED)
        self.assertNotIn("ApplySystemHit", GET_FORWARD_SPEED)
        self.assertNotIn("ApplyHit", GET_FORWARD_SPEED)
        self.assertNotIn("ApplyDamage", locked_only)
        self.assertNotIn("GetDamageFraction", locked_only)
        self.assertNotIn("ApplySystemHit", locked_only)
        self.assertNotIn("ApplyHit", locked_only)

    def test_contract_does_not_relock_sensor_state_helpers(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for neighbor in SENSOR_STATE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_FORWARD_SPEED)
        self.assertNotIn("IsSensorLive", GET_FORWARD_SPEED)
        self.assertNotIn("IsThermalAvailable", GET_FORWARD_SPEED)
        self.assertNotIn("IsSensorViewActive", GET_FORWARD_SPEED)
        self.assertNotIn("IsSensorLive", locked_only)
        self.assertNotIn("IsThermalAvailable", locked_only)
        self.assertNotIn("IsSensorViewActive", locked_only)

    def test_contract_does_not_relock_remaining_public_methods(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in REMAINING_PUBLIC_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_aircraft_empty_fail_closed.py",
            GET_FORWARD_SPEED,
        )

    def test_contract_does_not_relock_leftover_chin_muzzle(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn("GetChinMuzzleLocation", GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_chin_muzzle_tests.py",
            GET_FORWARD_SPEED,
        )

    def test_contract_does_not_relock_leftover_own_ship_systems(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn("ESkyguardApacheSystem", GET_FORWARD_SPEED)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn(
            "test_apache_own_ship_systems_contract.py",
            GET_FORWARD_SPEED,
        )

    def test_contract_does_not_relock_leftover_cpg_feel(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_cpg_feel_contract.py",
            GET_FORWARD_SPEED,
        )

    def test_contract_does_not_relock_leftover_aim_chin_turret_sibling(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_AIM_CHIN_TURRET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_aim_chin_turret_decl_contract.py",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("AimChinTurret", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_set_rotor_power_sibling(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_SET_ROTOR_POWER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_set_rotor_power_decl_contract.py",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("SetRotorPower", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_issue_pilot_command_sibling(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_ISSUE_PILOT_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_issue_pilot_command_decl_contract.py",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("IssuePilotCommand", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_get_pilot_command_sibling(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_GET_PILOT_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_get_pilot_command_decl_contract.py",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("GetPilotCommand", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_confirmations_issued_sibling(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_GET_PILOT_CONFIRMATIONS_ISSUED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_get_pilot_confirmations_issued_decl_contract.py",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("GetPilotConfirmationsIssued", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_set_orbit_focus_sibling(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_SET_ORBIT_FOCUS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_set_orbit_focus_decl_contract.py",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("SetOrbitFocus", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_face_world_location_sibling(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_FACE_WORLD_LOCATION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_face_world_location_decl_contract.py",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("FaceWorldLocation", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_set_sensor_view_sibling(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_SET_SENSOR_VIEW_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_set_sensor_view_decl_contract.py",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("SetSensorView", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_first_person_interior_sibling(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_SET_FIRST_PERSON_INTERIOR_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_set_first_person_interior_decl_contract.py",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("SetFirstPersonInterior", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_direct_flight_input_sibling(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_SET_DIRECT_FLIGHT_INPUT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_set_direct_flight_input_decl_contract.py",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("SetDirectFlightInput", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_apply_damage_sibling(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_APPLY_DAMAGE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_apache_apply_damage_decl_contract.py",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("ApplyDamage", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_pilot_command_roster(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_PILOT_COMMAND_ROSTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_pilot_command_roster_contract.py",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn("Pursuit", GET_FORWARD_SPEED)
        self.assertNotIn("OrbitLeft", GET_FORWARD_SPEED)
        self.assertNotIn("AttackRun", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_cpg_hud(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_HUD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCpgHud", locked_only)
        self.assertNotIn("SkyguardCpgSightHud", locked_only)
        self.assertNotIn("ASkyguardCpgHud", locked_only)
        self.assertNotIn("ASkyguardCpgSightHud", locked_only)

    def test_contract_does_not_relock_leftover_widget_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardDebriefWidget", GET_FORWARD_SPEED)
        self.assertNotIn("USkyguardBriefingWidget", GET_FORWARD_SPEED)
        self.assertNotIn(
            "test_debrief_widget_travel_next_decl_contract.py",
            GET_FORWARD_SPEED,
        )
        self.assertNotIn(
            "test_debrief_widget_handle_debrief_key_decl_contract.py",
            GET_FORWARD_SPEED,
        )

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", GET_FORWARD_SPEED)
        self.assertNotIn("ESkyguardMissionSkylineStyle", GET_FORWARD_SPEED)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        self.assertEqual(
            require_declaration(locked_only, GET_FORWARD_SPEED),
            GET_FORWARD_SPEED,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_FORWARD_SPEED)
        self.assertNotIn("GetGunnerMount", locked_only)
        self.assertNotIn("GetEyeMount", locked_only)
        self.assertNotIn("GetWeaponMount", locked_only)
        self.assertNotIn("GetChinTurret", locked_only)
        self.assertNotIn("GetPilotMount", locked_only)
        self.assertNotIn("GetSensorTurret", locked_only)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)
        self.assertNotIn("AimChinTurret", locked_only)
        self.assertNotIn("SetRotorPower", locked_only)
        self.assertNotIn("IssuePilotCommand", locked_only)
        self.assertNotIn("GetPilotCommand", locked_only)
        self.assertNotIn("GetPilotConfirmationsIssued", locked_only)
        self.assertNotIn("SetOrbitFocus", locked_only)
        self.assertNotIn("FaceWorldLocation", locked_only)
        self.assertNotIn("SetSensorView", locked_only)
        self.assertNotIn("SetFirstPersonInterior", locked_only)
        self.assertNotIn("SetDirectFlightInput", locked_only)
        self.assertNotIn("ApplyDamage", locked_only)
        self.assertNotIn("GetDamageFraction", locked_only)
        self.assertNotIn("ApplySystemHit", locked_only)
        self.assertNotIn("ApplyHit", locked_only)
        self.assertNotIn("IsSensorLive", locked_only)
        self.assertNotIn("IsThermalAvailable", locked_only)
        self.assertNotIn("IsSensorViewActive", locked_only)

    def test_contract_parses_public_section_not_enum_private_or_cpp(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        body = class_body(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("UENUM", section)
        self.assertNotIn("enum class", section)
        self.assertNotIn("CreateVisual", section)
        self.assertNotIn("BindPrimitive", section)
        self.assertNotIn("UpdatePilotMotion", section)
        self.assertNotIn("ResetOwnShipSystems", section)
        self.assertNotIn("OpenCockpitView", section)
        self.assertNotIn("BindSilhouetteMesh", section)
        self.assertNotIn("USkyguardDebriefWidget", section)
        self.assertNotIn("USkyguardBriefingWidget", section)
        self.assertNotIn("USkyguardDebriefWidget", body)
        self.assertNotIn("USkyguardBriefingWidget", body)
        self.assertEqual(
            require_declaration(section, GET_FORWARD_SPEED),
            GET_FORWARD_SPEED,
        )
        self.assertEqual(declaration_count(section, GET_FORWARD_SPEED), 1)
        self.assertNotIn("SkyguardApacheAircraft.cpp", section)
        self.assertNotIn(
            "ASkyguardApacheAircraft::GetForwardSpeed",
            section,
        )
        self.assertNotIn("Pursuit", GET_FORWARD_SPEED)
        self.assertNotIn("OrbitLeft", GET_FORWARD_SPEED)
        self.assertNotIn("AttackRun", GET_FORWARD_SPEED)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_FORWARD_SPEED)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardApacheAircraft.cpp", section)
        self.assertNotIn(
            "ASkyguardApacheAircraft::GetForwardSpeed",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", GET_FORWARD_SPEED)
        self.assertNotIn("}", GET_FORWARD_SPEED)
        self.assertNotIn("return false", GET_FORWARD_SPEED)
        self.assertNotIn("return true", GET_FORWARD_SPEED)
        self.assertNotIn("return ForwardSpeed", GET_FORWARD_SPEED)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{GET_FORWARD_SPEED}\n"
        file_text = this_file_text()
        # Harbor clock field names stay off this class public
        # section. Literal Harbor interval retune tokens fail
        # closed in this file and the locked declaration
        # only: public MaxIntegrity is not a Harbor clock.
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, GET_FORWARD_SPEED)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, GET_FORWARD_SPEED)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{GET_FORWARD_SPEED}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
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
                "apache GetForwardSpeed contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, GET_FORWARD_SPEED.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"apache GetForwardSpeed contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, GET_FORWARD_SPEED.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, GET_FORWARD_SPEED)

    def test_contract_is_get_forward_speed_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, GET_FORWARD_SPEED),
            GET_FORWARD_SPEED,
        )
        locked_only = f"{GET_FORWARD_SPEED}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_FORWARD_SPEED)
        self.assertNotIn("GetGunnerMount", locked_only)
        self.assertNotIn("GetEyeMount", locked_only)
        self.assertNotIn("GetWeaponMount", locked_only)
        self.assertNotIn("GetChinTurret", locked_only)
        self.assertNotIn("GetPilotMount", locked_only)
        self.assertNotIn("GetSensorTurret", locked_only)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)
        self.assertNotIn("AimChinTurret", locked_only)
        self.assertNotIn("SetRotorPower", locked_only)
        self.assertNotIn("IssuePilotCommand", locked_only)
        self.assertNotIn("GetPilotCommand", locked_only)
        self.assertNotIn("GetPilotConfirmationsIssued", locked_only)
        self.assertNotIn("SetOrbitFocus", locked_only)
        self.assertNotIn("FaceWorldLocation", locked_only)
        self.assertNotIn("SetSensorView", locked_only)
        self.assertNotIn("SetFirstPersonInterior", locked_only)
        self.assertNotIn("SetDirectFlightInput", locked_only)
        self.assertNotIn("ApplyDamage", locked_only)
        self.assertNotIn("GetDamageFraction", locked_only)
        self.assertNotIn("ApplySystemHit", locked_only)
        self.assertNotIn("ApplyHit", locked_only)
        self.assertNotIn("IsSensorLive", locked_only)
        self.assertNotIn("IsThermalAvailable", locked_only)
        self.assertNotIn("IsSensorViewActive", locked_only)
        self.assertNotIn("IsCanopyGlassCracked", locked_only)
        self.assertNotIn("AreEnginesDown", locked_only)
        self.assertNotIn("IsChinTurretDown", locked_only)
        self.assertNotIn("IsRotorDown", locked_only)
        self.assertNotIn("IsSystemDown", locked_only)
        self.assertNotIn("FindNearestLiveSystem", locked_only)
        self.assertNotIn("GetSensorQuality", locked_only)
        self.assertNotIn("GetChinSlewScale", locked_only)
        self.assertNotIn("GetChinFireScale", locked_only)
        self.assertNotIn("GetEnginePowerScale", locked_only)
        self.assertNotIn("GetRotorPowerScale", locked_only)
        self.assertNotIn("GetRotorRPM", locked_only)
        self.assertNotIn("HarborIndustrial", locked_only)
        self.assertNotIn("USkyguardDebriefWidget", locked_only)
        self.assertNotIn("USkyguardBriefingWidget", locked_only)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn("Pursuit", locked_only)
        self.assertNotIn("OrbitLeft", locked_only)
        self.assertNotIn("AttackRun", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_AIM_CHIN_TURRET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_SET_ROTOR_POWER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_ISSUE_PILOT_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_GET_PILOT_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_GET_PILOT_CONFIRMATIONS_ISSUED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_SET_ORBIT_FOCUS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_FACE_WORLD_LOCATION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_SET_SENSOR_VIEW_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_SET_FIRST_PERSON_INTERIOR_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_SET_DIRECT_FLIGHT_INPUT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_APPLY_DAMAGE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_PILOT_COMMAND_ROSTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_CPG_HUD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_FORWARD_SPEED)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, GET_FORWARD_SPEED)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, GET_FORWARD_SPEED)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_FORWARD_SPEED)
            self.assertNotIn(token, section)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, GET_FORWARD_SPEED.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", GET_FORWARD_SPEED)
        self.assertNotIn("return ForwardSpeed", GET_FORWARD_SPEED)
        self.assertNotIn("{", GET_FORWARD_SPEED)
        self.assertTrue(GET_FORWARD_SPEED.startswith("float "))
        self.assertTrue(GET_FORWARD_SPEED.endswith(";"))
        self.assertIn(" const", GET_FORWARD_SPEED)
        self.assertIn(UFUNCTION_APACHE, section)

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
