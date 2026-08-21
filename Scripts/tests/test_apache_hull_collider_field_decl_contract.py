from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardApacheAircraft.h"
CLASS_NAME = "ASkyguardApacheAircraft"
# Field-declaration presence only. Do not invent INDEX_NONE
# or lock HullCollider construction in the .cpp.
# origin/main is a split-line UPROPERTY wrap plus
# (`TObjectPtr<UBoxComponent> HullCollider;`);
# accept that form and other one-line / split-line wraps.
# Nearby origin/main
# UPROPERTY(VisibleAnywhere, BlueprintReadOnly,
# Category="Skyguard|Apache|Damage")
# is accepted as present. Parse the public class section of
# ASkyguardApacheAircraft only. Do not lock
# MaxIntegrity or CurrentIntegrity (those defaults are
# Harbor-sensitive). Do not lock
# ESkyguardPilotCommand enum values. Do not lock
# ESkyguardApacheSystem enum values. This is not leftover
# apache-own-ship-systems #96c5 (that leftover locks
# ESkyguardApacheSystem enumerators, not this field;
# stay off ApplySystemHit / ApplyHit / IsSensorLive /
# IsThermalAvailable / IsSensorViewActive / IsSystemDown /
# FindNearestLiveSystem). This is not leftover
# apache-aircraft empty-fail-closed #851b (stay off
# mount getters GetGunnerMount / GetEyeMount /
# GetWeaponMount / GetChinTurret / GetPilotMount /
# GetSensorTurret). This is not leftover
# apache-chin-muzzle tests #4e39 (stay off
# GetChinMuzzleLocation). This is not leftover
# apache-cpg-feel #8951. This is not leftover
# pilot-command-roster #b593. This is a field-declaration
# lane, not a method. Stay off sibling Apache methods
# already drafted: AimChinTurret, SetRotorPower,
# IssuePilotCommand, GetPilotCommand,
# GetPilotConfirmationsIssued, SetOrbitFocus,
# FaceWorldLocation, SetSensorView,
# SetFirstPersonInterior, SetDirectFlightInput,
# GetForwardSpeed, ApplyDamage, GetDamageFraction,
# IsCanopyGlassCracked, AreEnginesDown, IsChinTurretDown,
# IsRotorDown, GetSensorQuality, GetChinSlewScale,
# GetChinFireScale, GetEnginePowerScale, GetRotorPowerScale
# (sibling this wave), GetRotorRPM (sibling this wave),
# and remaining unused neighbors. Leftover briefing /
# debrief widget isolated contracts, leftover Gunner
# helpers, leftover Harbor clocks, leftover theater-kit /
# flare / HUD, leftover ApacheSystem / weapon stations /
# leftover roster / loadout / lock-phase, leftover drafts
# #56–#64, leftover skyline style HarborIndustrial
# (leftover enum, not a Harbor 40/80 retune), leftover
# sortie-hud-host fail-closed, leftover gun-fire camera
# shake, leftover DebriefWidget TravelNext /
# HandleDebriefKey, leftover isolated-test drafts
# #107–#423, leftover Pathfinder MinHeightFromOriginCm
# (wrong header; do not scan it), and leftover
# SortiePresentationWidgets stay sibling-only.
HULL_COLLIDER = "TObjectPtr<UBoxComponent> HullCollider;"
UPROPERTY_HULL = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Apache|Damage")'
)
# Leftover #56–#64 plus SkyguardApacheAircraft production
# files. This lane only adds an isolated Python
# HullCollider field declaration contract on
# ASkyguardApacheAircraft. SortiePresentationWidgets is
# not the class under test. Stay off mount getters,
# GetChinMuzzleLocation, AimChinTurret, SetRotorPower,
# IssuePilotCommand, GetPilotCommand,
# GetPilotConfirmationsIssued, SetOrbitFocus,
# FaceWorldLocation, SetSensorView,
# SetFirstPersonInterior, SetDirectFlightInput,
# GetForwardSpeed, ApplyDamage, GetDamageFraction,
# IsCanopyGlassCracked, AreEnginesDown, ApplySystemHit,
# ApplyHit, IsSensorLive, IsThermalAvailable,
# IsSensorViewActive, remaining public methods,
# MaxIntegrity, CurrentIntegrity, leftover
# apache-aircraft empty-fail-closed #851b, leftover
# apache-chin-muzzle #4e39, leftover
# apache-own-ship-systems #96c5, leftover
# apache-cpg-feel #8951, leftover
# pilot-command-roster #b593, leftover CPG HUD /
# sight HUD, leftover drafts #56–#64, leftover
# ApacheSystem enum values, leftover roster enum
# values, leftover Harbor clocks, leftover skyline
# HarborIndustrial, leftover DebriefWidget isolated
# contracts, leftover BriefingWidget isolated
# contracts, leftover gun-fire camera shake, leftover
# sortie-hud-host fail-closed, leftover AimChinTurret
# sibling, leftover SetRotorPower sibling, leftover
# IssuePilotCommand sibling, leftover
# GetPilotCommand sibling, leftover
# GetPilotConfirmationsIssued sibling, leftover
# SetOrbitFocus sibling, leftover FaceWorldLocation
# sibling, leftover SetSensorView sibling, leftover
# SetFirstPersonInterior sibling, leftover
# SetDirectFlightInput sibling, leftover
# GetForwardSpeed sibling, leftover ApplyDamage
# sibling, leftover GetDamageFraction sibling,
# leftover IsCanopyGlassCracked sibling, leftover
# AreEnginesDown sibling, leftover IsChinTurretDown
# sibling, leftover IsRotorDown sibling, leftover
# GetSensorQuality sibling, leftover GetChinSlewScale
# sibling, leftover GetChinFireScale sibling, leftover
# GetEnginePowerScale sibling, leftover
# GetRotorPowerScale sibling this wave, leftover
# GetRotorRPM sibling this wave, leftover Pathfinder
# header, and dirty workspace paths.
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
# apache-cpg-feel #8951, leftover
# pilot-command-roster #b593, leftover AimChinTurret
# sibling, leftover SetRotorPower sibling, leftover
# IssuePilotCommand sibling in this wave, leftover
# GetPilotCommand sibling in this wave, leftover
# GetPilotConfirmationsIssued sibling in this wave,
# leftover SetOrbitFocus sibling in this wave,
# leftover FaceWorldLocation sibling in this wave,
# leftover SetSensorView sibling in this wave,
# leftover SetFirstPersonInterior sibling in this
# wave, leftover SetDirectFlightInput sibling in this
# wave, leftover GetForwardSpeed sibling in this wave,
# leftover ApplyDamage sibling in this wave, leftover
# GetDamageFraction sibling in this wave, leftover
# IsCanopyGlassCracked sibling in this wave, leftover
# AreEnginesDown sibling in this wave, leftover
# IsChinTurretDown sibling in this wave, leftover
# IsRotorDown sibling in this wave, leftover
# GetSensorQuality sibling in this wave, leftover
# GetChinSlewScale sibling in this wave, leftover
# GetChinFireScale sibling in this wave, leftover
# GetEnginePowerScale sibling in this wave, leftover
# GetRotorPowerScale sibling in this wave, leftover
# GetRotorRPM sibling in this wave, leftover
# DebriefWidget Configure / GetPresentation /
# GetDebrief / GetDebriefNarrative / GetFinalScore /
# IsProgressSaved / GetPresentationState /
# AcknowledgeDebrief / RetrySave / TravelNext /
# HandleDebriefKey, leftover BriefingWidget isolated
# contracts, leftover gun-fire camera shake, leftover
# sortie-hud-host fail-closed, leftover CPG HUD / sight
# HUD, leftover briefing-fail-closed, leftover
# campaign-save empty-fail-closed, leftover
# objective-runtime / route-runtime fail-closed,
# leftover theater-kit / Harbor / flare / HUD, leftover
# ApacheSystem / weapon stations / leftover roster /
# loadout, leftover bind-hud-host, leftover Gunner
# helpers, leftover pilot drafts, leftover
# mission-weather enum, leftover mission-definition
# field / method contracts, leftover skyline
# HarborIndustrial, leftover SortiePresentationWidgets,
# leftover CPG debrief, leftover apache-cpg-feel, and
# sibling Apache neighbors stay sibling-only.
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
    "Scripts/tests/test_apache_get_forward_speed_decl_contract.py",
    "Scripts/tests/test_apache_apply_damage_decl_contract.py",
    "Scripts/tests/test_apache_get_damage_fraction_decl_contract.py",
    "Scripts/tests/test_apache_is_canopy_glass_cracked_decl_contract.py",
    "Scripts/tests/test_apache_are_engines_down_decl_contract.py",
    "Scripts/tests/test_apache_is_chin_turret_down_decl_contract.py",
    "Scripts/tests/test_apache_is_rotor_down_decl_contract.py",
    "Scripts/tests/test_apache_get_sensor_quality_decl_contract.py",
    "Scripts/tests/test_apache_get_chin_slew_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_chin_fire_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_engine_power_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_rotor_power_scale_decl_contract.py",
    "Scripts/tests/test_apache_get_rotor_rpm_decl_contract.py",
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
# GetForwardSpeed, ApplyDamage, GetDamageFraction,
# ApplySystemHit, ApplyHit, IsSensorLive,
# IsThermalAvailable, IsSensorViewActive,
# IsCanopyGlassCracked, AreEnginesDown, remaining
# public methods, MaxIntegrity, and CurrentIntegrity
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
    "float GetForwardSpeed() const { return ForwardSpeed; }",
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
    "float MaxIntegrity",
    "float CurrentIntegrity",
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
ISSUE_PILOT_COMMAND_NOT_LOCKED = (
    "void IssuePilotCommand(ESkyguardPilotCommand Command);",
)
GET_PILOT_HELPERS_NOT_LOCKED = (
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
FLIGHT_INPUT_NOT_LOCKED = (
    "SetDirectFlightInput",
    "GetForwardSpeed",
)
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
INTEGRITY_FIELDS_NOT_LOCKED = (
    "MaxIntegrity",
    "CurrentIntegrity",
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
LEFTOVER_APACHE_SYSTEM_VALUES_NOT_LOCKED = (
    "Sensor",
    "Canopy",
    "Engines",
    "ChinTurret",
    "Rotor",
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
    "GetPilotCommand",
)
# Leftover GetPilotConfirmationsIssued sibling in this
# wave stays unlocked. Do not create or edit that file.
LEFTOVER_GET_PILOT_CONFIRMATIONS_NOT_LOCKED = (
    "test_apache_get_pilot_confirmations_issued_decl_contract.py",
    "GetPilotConfirmationsIssued",
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
# Leftover GetForwardSpeed sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_GET_FORWARD_SPEED_NOT_LOCKED = (
    "test_apache_get_forward_speed_decl_contract.py",
    "GetForwardSpeed",
)
# Leftover ApplyDamage sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_APPLY_DAMAGE_NOT_LOCKED = (
    "test_apache_apply_damage_decl_contract.py",
    "void ApplyDamage(float Amount);",
)
# Leftover GetDamageFraction sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_GET_DAMAGE_FRACTION_NOT_LOCKED = (
    "test_apache_get_damage_fraction_decl_contract.py",
    "float GetDamageFraction() const;",
)
# Leftover IsCanopyGlassCracked sibling in this wave
# stays unlocked. Do not create or edit that file.
LEFTOVER_IS_CANOPY_GLASS_CRACKED_NOT_LOCKED = (
    "test_apache_is_canopy_glass_cracked_decl_contract.py",
    "IsCanopyGlassCracked",
)
# Leftover AreEnginesDown sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_ARE_ENGINES_DOWN_NOT_LOCKED = (
    "test_apache_are_engines_down_decl_contract.py",
    "AreEnginesDown",
)
# Leftover IsChinTurretDown sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_IS_CHIN_TURRET_DOWN_NOT_LOCKED = (
    "test_apache_is_chin_turret_down_decl_contract.py",
    "IsChinTurretDown",
)
# Leftover IsRotorDown sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_IS_ROTOR_DOWN_NOT_LOCKED = (
    "test_apache_is_rotor_down_decl_contract.py",
    "IsRotorDown",
)
# Leftover GetSensorQuality sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_GET_SENSOR_QUALITY_NOT_LOCKED = (
    "test_apache_get_sensor_quality_decl_contract.py",
    "GetSensorQuality",
)
# Leftover GetChinSlewScale sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_GET_CHIN_SLEW_SCALE_NOT_LOCKED = (
    "test_apache_get_chin_slew_scale_decl_contract.py",
    "GetChinSlewScale",
)
# Leftover GetChinFireScale sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_GET_CHIN_FIRE_SCALE_NOT_LOCKED = (
    "test_apache_get_chin_fire_scale_decl_contract.py",
    "GetChinFireScale",
)
# Leftover GetEnginePowerScale sibling in this wave
# stays unlocked. Do not create or edit that file.
LEFTOVER_GET_ENGINE_POWER_SCALE_NOT_LOCKED = (
    "test_apache_get_engine_power_scale_decl_contract.py",
    "GetEnginePowerScale",
)
# Leftover GetRotorPowerScale sibling in this wave
# stays unlocked. Do not create or edit that file.
LEFTOVER_GET_ROTOR_POWER_SCALE_NOT_LOCKED = (
    "test_apache_get_rotor_power_scale_decl_contract.py",
    "GetRotorPowerScale",
)
# Leftover GetRotorRPM sibling in this wave stays
# unlocked. Do not create or edit that file.
LEFTOVER_GET_ROTOR_RPM_NOT_LOCKED = (
    "test_apache_get_rotor_rpm_decl_contract.py",
    "GetRotorRPM",
)
# Leftover pilot-command-roster #b593 stays unlocked.
# Do not lock leftover roster enum values.
LEFTOVER_PILOT_COMMAND_ROSTER_NOT_LOCKED = (
    "test_pilot_command_roster_contract.py",
    "test_pilot_command_roster_tests.py",
    "test_pilot_command_roster.py",
)
# Do not lock ESkyguardPilotCommand enum values.
LEFTOVER_PILOT_COMMAND_VALUES_NOT_LOCKED = (
    "Pursuit",
    "OrbitLeft",
    "OrbitRight",
    "Extend",
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
# roster type-name lock / loadout / lock-phase /
# leftover Gunner FillAnd* stay unlocked. The
# HullCollider field type is not a leftover roster
# value lock.
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
# Invented UPROPERTY specifiers that are not on origin/main
# for this field. Nearby origin/main metadata is
# VisibleAnywhere, BlueprintReadOnly,
# Category="Skyguard|Apache|Damage".
# Do not invent extra specifiers. Neighbor MaxIntegrity
# may use EditAnywhere / BlueprintReadWrite / ClampMin;
# those are not locked here.
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
# .cpp HullCollider body / invented INDEX_NONE stay
# unlocked. Do not invent INDEX_NONE or lock the
# cpp body. Do not parse leftover HUD classes.
# Pathfinder MinHeightFromOriginCm is the wrong header.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "ASkyguardApacheAircraft::HullCollider",
    "SkyguardApacheAircraft.cpp",
    "MinHeightFromOriginCm",
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
    compact = re.sub(r"\s*=\s*", " = ", compact)
    return compact


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


def has_declaration(region: str, declaration: str) -> bool:
    if declaration in region:
        return True
    return collapsed(declaration) in collapsed(region)


def declaration_count(region: str, declaration: str) -> int:
    if declaration in region:
        return region.count(declaration)
    return collapsed(region).count(collapsed(declaration))


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"class {CLASS_NAME} public section"
        )
    return declaration


class ApacheHullColliderFieldDeclContractTests(unittest.TestCase):
    def test_apache_aircraft_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, HULL_COLLIDER), section)

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
            f"\t{HULL_COLLIDER}\n"
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
            f"\t{HULL_COLLIDER}\n"
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
            "\tfloat GetDamageFraction() const;\n"
            "private:\n"
            f"\t{HULL_COLLIDER}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, HULL_COLLIDER)
        self.assertIn("HullCollider", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, HULL_COLLIDER))

    def test_missing_hull_collider_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tUSceneComponent* GetGunnerMount() const "
            "{ return GunnerMount; }\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
            "\tvoid AimChinTurret(const FRotator& WorldAim);\n"
            "\tvoid ApplyDamage(float Amount);\n"
            "\tfloat GetDamageFraction() const;\n"
            "\tvoid ApplySystemHit(ESkyguardApacheSystem System, "
            "float Amount);\n"
            "\tbool IsSensorLive() const;\n"
            "\tfloat GetChinSlewScale() const;\n"
            "\tfloat GetChinFireScale() const;\n"
            "\tfloat GetEnginePowerScale() const;\n"
            "\tfloat MaxIntegrity;\n"
            "\tfloat CurrentIntegrity;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, HULL_COLLIDER)
        self.assertIn("HullCollider", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_HULL}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, HULL_COLLIDER)
        self.assertIn("HullCollider", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_HULL, section)
        self.assertIn("VisibleAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('Category="Skyguard|Apache|Damage"', section)
        self.assertTrue(has_declaration(section, HULL_COLLIDER), section)
        self.assertNotIn("UPROPERTY", HULL_COLLIDER)
        self.assertNotIn("VisibleAnywhere", HULL_COLLIDER)
        self.assertNotIn("BlueprintReadOnly", HULL_COLLIDER)
        self.assertNotIn("Category", HULL_COLLIDER)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_HULL)
            self.assertNotIn(invented, HULL_COLLIDER)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, UPROPERTY_HULL)
            self.assertNotIn(invented, HULL_COLLIDER)

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
            "\tvoid ApplyDamage(float Amount);\n"
            "\tfloat GetDamageFraction() const;\n"
            "\tfloat GetChinSlewScale() const;\n"
            "\tfloat GetChinFireScale() const;\n"
            "\tfloat GetEnginePowerScale() const;\n"
            "\tfloat GetRotorPowerScale() const;\n"
            "\tfloat MaxIntegrity;\n"
            "\tfloat CurrentIntegrity;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, HULL_COLLIDER)
        self.assertIn("HullCollider", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        raw_pointer = "\tUBoxComponent* HullCollider;\n"
        sphere = "\tTObjectPtr<USphereComponent> HullCollider;\n"
        capsule = "\tTObjectPtr<UCapsuleComponent> HullCollider;\n"
        scene = "\tTObjectPtr<USceneComponent> HullCollider;\n"
        weak = "\tTWeakObjectPtr<UBoxComponent> HullCollider;\n"
        assigned = "\tTObjectPtr<UBoxComponent> HullCollider = nullptr;\n"
        wrong_name = "\tTObjectPtr<UBoxComponent> AircraftRoot;\n"
        max_integrity = "\tfloat MaxIntegrity;\n"
        current_integrity = "\tfloat CurrentIntegrity;\n"
        leftover_damage = "\tvoid ApplyDamage(float Amount);\n"
        leftover_fraction = "\tfloat GetDamageFraction() const;\n"
        leftover_system = (
            "\tvoid ApplySystemHit(ESkyguardApacheSystem System, "
            "float Amount);\n"
        )
        leftover_hit = (
            "\tvoid ApplyHit(UPrimitiveComponent* HitComponent, "
            "float Amount);\n"
        )
        leftover_slew = "\tfloat GetChinSlewScale() const;\n"
        leftover_fire = "\tfloat GetChinFireScale() const;\n"
        leftover_engine = "\tfloat GetEnginePowerScale() const;\n"
        leftover_rotor = "\tfloat GetRotorPowerScale() const;\n"
        leftover_rpm = "\tfloat GetRotorRPM() const { return CurrentRotorRPM; }\n"
        leftover_muzzle = "\tFVector GetChinMuzzleLocation() const;\n"
        leftover_mount = (
            "\tUSceneComponent* GetGunnerMount() const "
            "{ return GunnerMount; }\n"
        )
        for region in (
            raw_pointer,
            sphere,
            capsule,
            scene,
            weak,
            assigned,
            wrong_name,
            max_integrity,
            current_integrity,
            leftover_damage,
            leftover_fraction,
            leftover_system,
            leftover_hit,
            leftover_slew,
            leftover_fire,
            leftover_engine,
            leftover_rotor,
            leftover_rpm,
            leftover_muzzle,
            leftover_mount,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, HULL_COLLIDER)
            self.assertIn("HullCollider", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_assigned_hull_collider_does_not_satisfy(self) -> None:
        assigned = "\tTObjectPtr<UBoxComponent> HullCollider = nullptr;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(assigned, HULL_COLLIDER)
        self.assertIn("HullCollider", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(assigned, HULL_COLLIDER))

    def test_integrity_fields_do_not_satisfy(self) -> None:
        max_integrity = "\tfloat MaxIntegrity;\n"
        current_integrity = "\tfloat CurrentIntegrity;\n"
        for region in (max_integrity, current_integrity):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, HULL_COLLIDER)
            self.assertIn("HullCollider", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, HULL_COLLIDER))

    def test_hull_collider_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, HULL_COLLIDER),
            HULL_COLLIDER,
        )
        self.assertTrue(has_declaration(section, HULL_COLLIDER))
        self.assertEqual(declaration_count(section, HULL_COLLIDER), 1)
        self.assertTrue(
            HULL_COLLIDER.startswith("TObjectPtr<UBoxComponent> "),
            HULL_COLLIDER,
        )
        self.assertTrue(HULL_COLLIDER.endswith(";"), HULL_COLLIDER)
        self.assertIn("HullCollider", HULL_COLLIDER)
        self.assertNotIn("=", HULL_COLLIDER)
        self.assertNotIn("INDEX_NONE", HULL_COLLIDER)
        self.assertNotIn("NAME_None", HULL_COLLIDER)
        self.assertNotIn("UFUNCTION", HULL_COLLIDER)
        self.assertNotIn("{", HULL_COLLIDER)
        self.assertNotIn("}", HULL_COLLIDER)
        self.assertNotIn("return ", HULL_COLLIDER)
        self.assertNotIn("MaxIntegrity", HULL_COLLIDER)
        self.assertNotIn("CurrentIntegrity", HULL_COLLIDER)
        self.assertNotIn("GetChinSlewScale", HULL_COLLIDER)
        self.assertNotIn("GetChinFireScale", HULL_COLLIDER)
        self.assertNotIn("GetEnginePowerScale", HULL_COLLIDER)
        self.assertNotIn("GetRotorPowerScale", HULL_COLLIDER)
        self.assertNotIn("GetRotorRPM", HULL_COLLIDER)
        self.assertNotIn("GetChinMuzzleLocation", HULL_COLLIDER)
        self.assertNotIn("ApplySystemHit", HULL_COLLIDER)
        self.assertNotIn("ApplyHit", HULL_COLLIDER)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tTObjectPtr<UBoxComponent>\n"
            "\tHullCollider;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tTObjectPtr<UBoxComponent>   HullCollider;\n"
            "private:\n"
            "};\n"
        )
        wrap_tab = (
            "public:\n"
            "\tTObjectPtr<UBoxComponent>\tHullCollider;\n"
            "};\n"
        )
        wrap_indent = (
            "public:\n"
            "\tTObjectPtr<UBoxComponent>\n"
            "\t\tHullCollider;\n"
            "};\n"
        )
        wrap_uproperty = (
            "public:\n"
            f"\t{UPROPERTY_HULL}\n"
            f"\t{HULL_COLLIDER}\n"
            "};\n"
        )
        wrap_uproperty_one_line = (
            "public:\n"
            f"\t{UPROPERTY_HULL} {HULL_COLLIDER}\n"
            "};\n"
        )
        wrap_uproperty_category = (
            "public:\n"
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly,\n"
            '\t\tCategory="Skyguard|Apache|Damage")\n'
            f"\t{HULL_COLLIDER}\n"
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
                has_declaration(section, HULL_COLLIDER),
                section,
            )
            self.assertEqual(
                require_declaration(section, HULL_COLLIDER),
                HULL_COLLIDER,
            )
            self.assertEqual(
                declaration_count(section, HULL_COLLIDER),
                1,
            )
        one_line = f"{{\npublic:\n\t{HULL_COLLIDER}\n}}\n"
        self.assertTrue(has_declaration(one_line, HULL_COLLIDER))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, HULL_COLLIDER), section)
        self.assertEqual(
            require_declaration(section, HULL_COLLIDER),
            HULL_COLLIDER,
        )
        self.assertIn(UPROPERTY_HULL, section)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", HULL_COLLIDER)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", HULL_COLLIDER)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, HULL_COLLIDER)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_HULL)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, HULL_COLLIDER)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_HULL)
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_HULL, section)
        self.assertTrue(has_declaration(section, HULL_COLLIDER), section)

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        self.assertNotIn("UFUNCTION", HULL_COLLIDER)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(HULL_COLLIDER.startswith("UFUNCTION"), HULL_COLLIDER)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, HULL_COLLIDER), section)
        self.assertEqual(
            require_declaration(section, HULL_COLLIDER),
            HULL_COLLIDER,
        )

    def test_contract_does_not_lock_hull_collider_cpp_body(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        self.assertNotIn("{", HULL_COLLIDER)
        self.assertNotIn("}", HULL_COLLIDER)
        self.assertNotIn("return ", HULL_COLLIDER)
        self.assertNotIn(
            "ASkyguardApacheAircraft::HullCollider",
            HULL_COLLIDER,
        )
        self.assertNotIn("SkyguardApacheAircraft.cpp", HULL_COLLIDER)
        self.assertNotIn("SkyguardApacheAircraft.cpp", locked_only)
        self.assertNotIn("CreateDefaultSubobject", HULL_COLLIDER)
        self.assertNotIn("return false", HULL_COLLIDER)
        self.assertNotIn("return true", HULL_COLLIDER)

    def test_contract_does_not_lock_integrity_fields(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in INTEGRITY_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn("MaxIntegrity", HULL_COLLIDER)
        self.assertNotIn("CurrentIntegrity", HULL_COLLIDER)
        self.assertNotIn("MaxIntegrity", locked_only)
        self.assertNotIn("CurrentIntegrity", locked_only)
        self.assertNotIn("ClampMin", HULL_COLLIDER)

    def test_contract_does_not_scan_pathfinder_header(self) -> None:
        self.assertEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardApacheAircraft.h",
        )
        self.assertNotIn("Pathfinder", HEADER_PATH)
        self.assertNotIn("MinHeightFromOriginCm", HEADER_PATH)
        self.assertNotIn("MinHeightFromOriginCm", HULL_COLLIDER)
        self.assertNotIn("MinHeightFromOriginCm", UPROPERTY_HULL)

    def test_contract_does_not_relock_mount_getters(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in MOUNT_GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn("GetGunnerMount", HULL_COLLIDER)
        self.assertNotIn("GetEyeMount", HULL_COLLIDER)
        self.assertNotIn("GetWeaponMount", HULL_COLLIDER)
        self.assertNotIn("GetChinTurret", HULL_COLLIDER)
        self.assertNotIn("GetPilotMount", HULL_COLLIDER)
        self.assertNotIn("GetSensorTurret", HULL_COLLIDER)

    def test_contract_does_not_relock_chin_muzzle(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for neighbor in GET_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, HULL_COLLIDER)
        self.assertNotIn("GetChinMuzzleLocation", HULL_COLLIDER)
        self.assertNotIn("GetChinMuzzleLocation", locked_only)

    def test_contract_does_not_relock_aim_chin_turret(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for neighbor in AIM_CHIN_TURRET_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, HULL_COLLIDER)
        self.assertNotIn("AimChinTurret", HULL_COLLIDER)
        self.assertNotIn("AimChinTurret", locked_only)

    def test_contract_does_not_relock_set_rotor_power(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for neighbor in SET_ROTOR_POWER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, HULL_COLLIDER)
        self.assertNotIn("SetRotorPower", HULL_COLLIDER)
        self.assertNotIn("SetRotorPower", locked_only)

    def test_contract_does_not_relock_issue_pilot_command(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for neighbor in ISSUE_PILOT_COMMAND_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, HULL_COLLIDER)
        self.assertNotIn("IssuePilotCommand", HULL_COLLIDER)
        self.assertNotIn("IssuePilotCommand", locked_only)

    def test_contract_does_not_relock_get_pilot_helpers(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for neighbor in GET_PILOT_HELPERS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, HULL_COLLIDER)
        self.assertNotIn("GetPilotCommand", HULL_COLLIDER)
        self.assertNotIn("GetPilotConfirmationsIssued", HULL_COLLIDER)
        self.assertNotIn("GetPilotCommand", locked_only)
        self.assertNotIn("GetPilotConfirmationsIssued", locked_only)

    def test_contract_does_not_relock_orbit_or_face(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for neighbor in ORBIT_AND_FACE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, HULL_COLLIDER)
        self.assertNotIn("SetOrbitFocus", HULL_COLLIDER)
        self.assertNotIn("FaceWorldLocation", HULL_COLLIDER)
        self.assertNotIn("SetOrbitFocus", locked_only)
        self.assertNotIn("FaceWorldLocation", locked_only)

    def test_contract_does_not_relock_sensor_view_or_interior(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for neighbor in SENSOR_VIEW_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, HULL_COLLIDER)
        self.assertNotIn("SetSensorView", HULL_COLLIDER)
        self.assertNotIn("SetFirstPersonInterior", HULL_COLLIDER)
        self.assertNotIn("SetSensorView", locked_only)
        self.assertNotIn("SetFirstPersonInterior", locked_only)

    def test_contract_does_not_relock_flight_input(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in FLIGHT_INPUT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn("SetDirectFlightInput", locked_only)
        self.assertNotIn("GetForwardSpeed", locked_only)

    def test_contract_does_not_relock_damage_helpers(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for neighbor in DAMAGE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, HULL_COLLIDER)
        self.assertNotIn("ApplyDamage", HULL_COLLIDER)
        self.assertNotIn("GetDamageFraction", HULL_COLLIDER)
        self.assertNotIn("ApplySystemHit", HULL_COLLIDER)
        self.assertNotIn("ApplyHit", HULL_COLLIDER)
        self.assertNotIn("ApplyDamage", locked_only)
        self.assertNotIn("GetDamageFraction", locked_only)
        self.assertNotIn("ApplySystemHit", locked_only)
        self.assertNotIn("ApplyHit", locked_only)

    def test_contract_does_not_relock_sensor_state_helpers(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for neighbor in SENSOR_STATE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, HULL_COLLIDER)
        self.assertNotIn("IsSensorLive", HULL_COLLIDER)
        self.assertNotIn("IsThermalAvailable", HULL_COLLIDER)
        self.assertNotIn("IsSensorViewActive", HULL_COLLIDER)
        self.assertNotIn("IsSensorLive", locked_only)
        self.assertNotIn("IsThermalAvailable", locked_only)
        self.assertNotIn("IsSensorViewActive", locked_only)

    def test_contract_does_not_relock_remaining_public_methods(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in REMAINING_PUBLIC_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_aircraft_empty_fail_closed.py",
            HULL_COLLIDER,
        )

    def test_contract_does_not_relock_leftover_chin_muzzle(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn("GetChinMuzzleLocation", HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_chin_muzzle_tests.py",
            HULL_COLLIDER,
        )

    def test_contract_does_not_relock_leftover_own_ship_systems(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn("ESkyguardApacheSystem", HULL_COLLIDER)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        self.assertNotIn(
            "test_apache_own_ship_systems_contract.py",
            HULL_COLLIDER,
        )

    def test_contract_does_not_lock_apache_system_enum_values(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_APACHE_SYSTEM_VALUES_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn("ESkyguardApacheSystem", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_cpg_feel(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_cpg_feel_contract.py",
            HULL_COLLIDER,
        )

    def test_contract_does_not_relock_leftover_aim_chin_turret_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_AIM_CHIN_TURRET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_aim_chin_turret_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("AimChinTurret", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_set_rotor_power_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_SET_ROTOR_POWER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_set_rotor_power_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("SetRotorPower", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_issue_pilot_command_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_ISSUE_PILOT_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_issue_pilot_command_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("IssuePilotCommand", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_get_pilot_command_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_GET_PILOT_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_get_pilot_command_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("GetPilotCommand", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_get_pilot_confirmations_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_GET_PILOT_CONFIRMATIONS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_get_pilot_confirmations_issued_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("GetPilotConfirmationsIssued", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_set_orbit_focus_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_SET_ORBIT_FOCUS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_set_orbit_focus_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("SetOrbitFocus", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_face_world_location_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_FACE_WORLD_LOCATION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_face_world_location_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("FaceWorldLocation", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_set_sensor_view_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_SET_SENSOR_VIEW_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_set_sensor_view_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("SetSensorView", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_first_person_interior_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_SET_FIRST_PERSON_INTERIOR_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_set_first_person_interior_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("SetFirstPersonInterior", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_direct_flight_input_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_SET_DIRECT_FLIGHT_INPUT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_set_direct_flight_input_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("SetDirectFlightInput", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_get_forward_speed_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_GET_FORWARD_SPEED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_get_forward_speed_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("GetForwardSpeed", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_apply_damage_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_APPLY_DAMAGE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_apply_damage_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("ApplyDamage", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_get_damage_fraction_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_GET_DAMAGE_FRACTION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_get_damage_fraction_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("GetDamageFraction", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_is_canopy_glass_cracked_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_IS_CANOPY_GLASS_CRACKED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_is_canopy_glass_cracked_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("IsCanopyGlassCracked", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_are_engines_down_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_ARE_ENGINES_DOWN_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_are_engines_down_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("AreEnginesDown", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_is_chin_turret_down_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_IS_CHIN_TURRET_DOWN_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_is_chin_turret_down_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("IsChinTurretDown", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_is_rotor_down_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_IS_ROTOR_DOWN_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_is_rotor_down_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("IsRotorDown", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_get_sensor_quality_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_GET_SENSOR_QUALITY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_get_sensor_quality_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("GetSensorQuality", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_get_chin_slew_scale_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_GET_CHIN_SLEW_SCALE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_get_chin_slew_scale_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("GetChinSlewScale", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_get_chin_fire_scale_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_GET_CHIN_FIRE_SCALE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_get_chin_fire_scale_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("GetChinFireScale", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_get_engine_power_scale_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_GET_ENGINE_POWER_SCALE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_get_engine_power_scale_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("GetEnginePowerScale", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_get_rotor_power_scale_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_GET_ROTOR_POWER_SCALE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_get_rotor_power_scale_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("GetRotorPowerScale", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_get_rotor_rpm_sibling(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_GET_ROTOR_RPM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_apache_get_rotor_rpm_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn("GetRotorRPM", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_pilot_command_roster(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_PILOT_COMMAND_ROSTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn(
            "test_pilot_command_roster_contract.py",
            HULL_COLLIDER,
        )

    def test_contract_does_not_lock_pilot_command_enum_values(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_PILOT_COMMAND_VALUES_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in leftover_short_roster_values():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn("Pursuit", HULL_COLLIDER)
        self.assertNotIn("OrbitLeft", HULL_COLLIDER)
        self.assertNotIn("AttackRun", HULL_COLLIDER)
        self.assertNotIn("FaceTarget", HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_cpg_hud(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_HUD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardCpgHud", locked_only)
        self.assertNotIn("SkyguardCpgSightHud", locked_only)
        self.assertNotIn("ASkyguardCpgHud", locked_only)
        self.assertNotIn("ASkyguardCpgSightHud", locked_only)

    def test_contract_does_not_relock_leftover_widget_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardDebriefWidget", HULL_COLLIDER)
        self.assertNotIn("USkyguardBriefingWidget", HULL_COLLIDER)
        self.assertNotIn(
            "test_debrief_widget_travel_next_decl_contract.py",
            HULL_COLLIDER,
        )
        self.assertNotIn(
            "test_debrief_widget_handle_debrief_key_decl_contract.py",
            HULL_COLLIDER,
        )

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", HULL_COLLIDER)
        self.assertNotIn("ESkyguardMissionSkylineStyle", HULL_COLLIDER)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        self.assertEqual(
            require_declaration(locked_only, HULL_COLLIDER),
            HULL_COLLIDER,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, HULL_COLLIDER)
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
        self.assertNotIn("GetForwardSpeed", locked_only)
        self.assertNotIn("ApplyDamage", locked_only)
        self.assertNotIn("GetDamageFraction", locked_only)
        self.assertNotIn("ApplySystemHit", locked_only)
        self.assertNotIn("ApplyHit", locked_only)
        self.assertNotIn("IsSensorLive", locked_only)
        self.assertNotIn("IsThermalAvailable", locked_only)
        self.assertNotIn("IsSensorViewActive", locked_only)
        self.assertNotIn("GetChinSlewScale", locked_only)
        self.assertNotIn("GetChinFireScale", locked_only)
        self.assertNotIn("GetEnginePowerScale", locked_only)
        self.assertNotIn("GetRotorPowerScale", locked_only)
        self.assertNotIn("GetRotorRPM", locked_only)
        self.assertNotIn("MaxIntegrity", locked_only)
        self.assertNotIn("CurrentIntegrity", locked_only)

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
        self.assertNotIn("MinHeightFromOriginCm", section)
        self.assertEqual(
            require_declaration(section, HULL_COLLIDER),
            HULL_COLLIDER,
        )
        self.assertEqual(declaration_count(section, HULL_COLLIDER), 1)
        self.assertNotIn("SkyguardApacheAircraft.cpp", section)
        self.assertNotIn(
            "ASkyguardApacheAircraft::HullCollider",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, HULL_COLLIDER)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardApacheAircraft.cpp", section)
        self.assertNotIn(
            "ASkyguardApacheAircraft::HullCollider",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", HULL_COLLIDER)
        self.assertNotIn("}", HULL_COLLIDER)
        self.assertNotIn("return false", HULL_COLLIDER)
        self.assertNotIn("return true", HULL_COLLIDER)
        self.assertNotIn("CreateDefaultSubobject", HULL_COLLIDER)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{HULL_COLLIDER}\n"
        file_text = this_file_text()
        # Harbor clock field names stay off this class public
        # section. Literal Harbor interval retune tokens fail
        # closed in this file and the locked declaration
        # only: public MaxIntegrity is not a Harbor clock.
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, HULL_COLLIDER)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, HULL_COLLIDER)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{HULL_COLLIDER}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
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
                "apache HullCollider contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, HULL_COLLIDER.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, HULL_COLLIDER)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"apache HullCollider contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, HULL_COLLIDER.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, HULL_COLLIDER)

    def test_contract_is_hull_collider_field_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, HULL_COLLIDER),
            HULL_COLLIDER,
        )
        locked_only = f"{HULL_COLLIDER}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, HULL_COLLIDER)
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
        self.assertNotIn("GetForwardSpeed", locked_only)
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
        self.assertNotIn("MaxIntegrity", locked_only)
        self.assertNotIn("CurrentIntegrity", locked_only)
        self.assertNotIn("HarborIndustrial", locked_only)
        self.assertNotIn("USkyguardDebriefWidget", locked_only)
        self.assertNotIn("USkyguardBriefingWidget", locked_only)
        self.assertNotIn("ESkyguardApacheSystem", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_APACHE_SYSTEM_VALUES_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_AIM_CHIN_TURRET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_SET_ROTOR_POWER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_ISSUE_PILOT_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_GET_PILOT_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_GET_PILOT_CONFIRMATIONS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_SET_ORBIT_FOCUS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_FACE_WORLD_LOCATION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_SET_SENSOR_VIEW_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_SET_FIRST_PERSON_INTERIOR_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_SET_DIRECT_FLIGHT_INPUT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_GET_FORWARD_SPEED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_APPLY_DAMAGE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_GET_DAMAGE_FRACTION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_IS_CANOPY_GLASS_CRACKED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_ARE_ENGINES_DOWN_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_IS_CHIN_TURRET_DOWN_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_IS_ROTOR_DOWN_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_GET_SENSOR_QUALITY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_GET_CHIN_SLEW_SCALE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_GET_CHIN_FIRE_SCALE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_GET_ENGINE_POWER_SCALE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_GET_ROTOR_POWER_SCALE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_GET_ROTOR_RPM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in INTEGRITY_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_PILOT_COMMAND_ROSTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_PILOT_COMMAND_VALUES_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in leftover_short_roster_values():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_CPG_HUD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, HULL_COLLIDER)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, HULL_COLLIDER)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, HULL_COLLIDER)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, HULL_COLLIDER)
            self.assertNotIn(token, section)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, HULL_COLLIDER.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", HULL_COLLIDER)
        self.assertNotIn("{", HULL_COLLIDER)
        self.assertTrue(HULL_COLLIDER.startswith("TObjectPtr<UBoxComponent> "))
        self.assertTrue(HULL_COLLIDER.endswith(";"))
        self.assertIn(UPROPERTY_HULL, section)

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
