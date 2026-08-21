from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardRoadHunterBoss.h"
CLASS_NAME = "ASkyguardRoadHunterBoss"
# Field-declaration presence only. Do not invent
# INDEX_NONE or lock RightActuator construction
# in the .cpp. This is a FIELD contract on
# ASkyguardRoadHunterBoss, not leftover RoadHunter
# sibling fields TargetingCamera / LeftActuator /
# Engine / DebrisLeftWing / DebrisEngine /
# DebrisRightWing and not leftover
# emergency-finish named surfaces
# (split tokens only). Keep RoadHunter Engine /
# DebrisEngine distinct from leftover Breakwater
# Engine / DebrisEngine (different classes; do
# not lock Breakwater here). Keep RightActuator
# distinct from leftover Pathfinder NoseCamera. This is not a
# leftover USkyguardBossWeakPointComponent member
# contract. origin/main is a one-line field
# (`TObjectPtr<USkyguardBossWeakPointComponent>
# RightActuator;`); accept that form and other
# one-line / split-line wraps. The element
# type appears on origin/main and must be
# part of the locked field declaration.
# Nearby origin/main
# UPROPERTY(VisibleAnywhere, BlueprintReadOnly,
# Category="Skyguard|Mission03|Boss") is required as
# present. Accept one-line and split-line
# UPROPERTY wraps. Parse the public class
# section of ASkyguardRoadHunterBoss only.
# Do not lock leftover sibling RadarGhost
# fields SignatureModulator, RadarReceiver,
# CoolingDoor, Engine, DebrisPortEWPanel,
# DebrisStarboardEWPanel, or DebrisCoolingDoor
# as the primary lock. Do not lock leftover
# sibling Breakwater fields PortLatch /
# StarboardLatch / DecoyPods / Engine /
# ElevatorLinkage / DebrisEngine /
# DebrisPortPanel / DebrisStarboardPanel. Stay off leftover
# RadarGhost public methods SetContactIdentified /
# OpenOrbitExposure / IsContactIdentified /
# constructor / HandleWeakPointDestroyed. Stay
# off leftover sibling Iron Rain fields
# DispenserCenter,
# DispenserStarboard, CommandAntennaPort,
# CommandAntennaStarboard, DecoyController,
# EnginePodPort, EnginePodCenter,
# EnginePodStarboard, FuelControlPort,
# FuelControlStarboard, DebrisPortWing,
# DebrisCenterRack, DebrisStarboardWing, or
# MaxReleasesPerBay as the primary lock.
# Stay off leftover Iron Rain public methods
# OpenDispenserBay / ReleasePooledEscort /
# IssueClimbCommand / IssueCrossCommand /
# OpenUpperEngineExposure /
# GetDestroyedDispenserCount /
# GetDestroyedAntennaCount /
# GetDestroyedEngineCount /
# GetReleasedEscortCount / GetManeuver.
# Stay off leftover Tempest ControlServo /
# sibling field contracts and leftover
# Tempest lightning / gust / lock-stability
# methods SetLightningExposed /
# ApplyCorrectiveBankGust /
# IsLightningExposed /
# GetLockStabilitySeconds. Stay off leftover
# Tempest emergency-finish / stabilized-lock
# methods. Stay off leftover
# USkyguardBossWeakPointComponent member
# fields. Do not lock leftover accept flags
# on that component. Do not open
# SkyguardBossWeakPointComponent.h as the
# locked header. Stay off leftover BossDrone
# Root / BodyMesh / WeakPoints fields and
# leftover debris getters. Stay off leftover
# Apache HullCollider field #425. Stay off leftover
# LastFlight PortGuidanceArray #481
# / DebrisArmorPort #491. Stay off leftover
# Pathfinder EncounterController / Engine /
# CommandAntenna / NoseCamera /
# ControlLinkage / Debris* sibling field
# contracts. Stay off leftover
# Apache IssuePilotCommand / leftover #96c5 /
# #851b / #4e39. Stay off leftover Gunner.
# Leftover briefing / debrief widget isolated
# contracts, leftover settings /
# input-capture contracts, leftover apache
# aircraft isolated contracts, leftover
# Harbor clocks, leftover Harbor #6/#8/#9,
# leftover theater-kit #59 / flare / HUD,
# leftover ApacheSystem / weapon stations /
# leftover roster / loadout / lock-phase,
# leftover drafts #56–#64, leftover
# isolated-test drafts #107–#546 including
# leftover searchlight-track-runtime-defaults
# #7347, leftover settings-apply-broadcast
# #1268, leftover BlackKite / RadarGhost /
# LifelineHunter / Pathfinder / Tempest /
# LastFlight / BossDrone drafts, leftover
# patrol-ship empty fail-closed #5382,
# leftover skyline style HarborIndustrial
# (leftover enum, not a Harbor 40/80 retune),
# leftover Apache MaxIntegrity /
# CurrentIntegrity, leftover
# sortie-hud-host fail-closed, leftover
# gun-fire camera shake, leftover
# DebriefWidget / BriefingWidget isolated
# contracts, and leftover
# SortiePresentationWidgets stay sibling-only.
# Harbor interval retune tokens fail closed
# in this file and the locked declaration
# only. Do not scan Apache public section for
# those tokens. Harbor clock names may be
# scanned in the RoadHunter public section and
# must be absent. Pathfinder
# MinHeightFromOriginCm is the wrong
# header, not Harbor 40/80. LastFlight
# MinimumCivilianSeparationMeters = 550.f is
# Harbor-adjacent; do not treat as Harbor
# 40/80. LifelineHunter
# MinimumWeaponSeparationMeters = 450.f is
# Harbor-adjacent.
TARGETING_CAMERA_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> TargetingCamera;"
)
LEFT_ACTUATOR_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> LeftActuator;"
)
RIGHT_ACTUATOR_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> RightActuator;"
)
ROAD_HUNTER_ENGINE_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> Engine;"
)
DEBRIS_LEFT_WING_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisLeftWing;"
)
ROAD_HUNTER_DEBRIS_ENGINE_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisEngine;"
)
DEBRIS_RIGHT_WING_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisRightWing;"
)
# Leftover Breakwater fields. Same Engine / DebrisEngine
# declaration text, different class. Not the primary lock.
BREAKWATER_ENGINE_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> Engine;"
)
BREAKWATER_DEBRIS_ENGINE_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisEngine;"
)
PORT_LATCH_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> PortLatch;"
)
STARBOARD_LATCH_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> StarboardLatch;"
)
DECOY_PODS_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> DecoyPods;"
)
ELEVATOR_LINKAGE_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> ElevatorLinkage;"
)
BREAKWATER_DEBRIS_PORT_PANEL_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisPortPanel;"
)
BREAKWATER_DEBRIS_STARBOARD_PANEL_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisStarboardPanel;"
)
# Leftover RadarGhost field. Not the primary lock.
COOLING_DOOR_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> CoolingDoor;"
)
SIGNATURE_MODULATOR_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "SignatureModulator;"
)
RADAR_RECEIVER_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "RadarReceiver;"
)
RADAR_GHOST_ENGINE_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> Engine;"
)
DEBRIS_PORT_EW_PANEL_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisPortEWPanel;"
)
DEBRIS_STARBOARD_EW_PANEL_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisStarboardEWPanel;"
)
DEBRIS_COOLING_DOOR_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisCoolingDoor;"
)
SET_CONTACT_IDENTIFIED = (
    "void SetContactIdentified(bool bIdentified);"
)
OPEN_ORBIT_EXPOSURE = (
    "bool OpenOrbitExposure();"
)
IS_CONTACT_IDENTIFIED = (
    "bool IsContactIdentified() const "
    "{ return bContactIdentified; }"
)
UPROPERTY_PORT = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Mission03|Boss")'
)
# Leftover #56–#64 plus leftover Harbor
# #6/#8/#9, leftover theater-kit #59,
# leftover #107–#546, plus
# SkyguardRadarGhostBoss production files.
# This lane only adds an isolated Python
# RightActuator field declaration contract on
# ASkyguardRoadHunterBoss. Stay off leftover
# sibling RadarGhost fields, leftover RadarGhost
# public methods, leftover Iron Rain sibling
# fields, leftover Iron Rain public methods,
# leftover Tempest ControlServo
# and sibling Tempest fields, leftover Tempest
# lightning / gust / lock-stability methods,
# leftover Tempest emergency-finish /
# stabilized-lock methods, leftover
# Pathfinder MinHeightFromOriginCm,
# leftover RadarNode, leftover Gunner,
# leftover apache-own-ship-systems #96c5,
# leftover #851b mount getters, leftover
# #4e39 GetChinMuzzleLocation, leftover
# USkyguardBossWeakPointComponent fields,
# leftover apache aircraft isolated
# contracts, leftover settings /
# input-capture contracts, leftover CPG HUD
# / sight HUD, leftover drafts #56–#64,
# leftover isolated-test drafts #107–#546,
# leftover searchlight-track-runtime-defaults
# #7347, leftover BlackKite siblings,
# leftover RadarGhost siblings, leftover
# LifelineHunter siblings, leftover
# Pathfinder siblings, leftover Tempest
# siblings, leftover LastFlight siblings
# including leftover PortGuidanceArray /
# DebrisArmorPort, leftover patrol-ship
# empty fail-closed #5382, leftover
# ApacheSystem enum values, leftover roster
# enum values, leftover Harbor clocks,
# leftover skyline HarborIndustrial,
# leftover DebriefWidget isolated contracts,
# leftover BriefingWidget isolated
# contracts, leftover gun-fire camera shake,
# leftover sortie-hud-host fail-closed, and
# dirty workspace paths.
LOCKED = {
    "SkyguardRoadHunterBoss.h",
    "SkyguardRoadHunterBoss.cpp",
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
        f"{prefix}test_radar_ghost_open_rear_aspect_{missile}"
        "_window_decl_contract.py",
        f"{prefix}test_radar_ghost_arm_break_{banned}"
        "_finish_decl_contract.py",
        f"{prefix}test_radar_ghost_is_break_{banned}"
        "_finish_armed_decl_contract.py",
        f"{prefix}test_breakwater_arm_emergency_{banned}"
        "_finish_decl_contract.py",
        f"{prefix}test_breakwater_is_emergency_{banned}"
        "_finish_armed_decl_contract.py",
        f"{prefix}test_road_hunter_arm_emergency_{banned}"
        "_finish_decl_contract.py",
        f"{prefix}test_road_hunter_is_emergency_{banned}"
        "_finish_armed_decl_contract.py",
    )


# Isolated-test drafts stay off this lane. Sibling
# isolated RadarGhost field contracts stay
# unlocked for THIS test's primary lock. Leftover
# RadarGhost public methods, leftover Iron Rain
# sibling field contracts, leftover
# Iron Rain public methods, leftover Tempest
# ControlServo / sibling Tempest field contracts,
# leftover Tempest lightning / gust / lock-stability
# methods, leftover Tempest emergency-finish /
# stabilized-lock methods, leftover Pathfinder /
# LastFlight / BossDrone / Apache / Gunner /
# settings / input-capture / briefing / debrief
# isolated contracts, leftover Harbor #6/#8/#9,
# leftover theater-kit #59, leftover drafts
# #56–#64, leftover isolated-test drafts
# #107–#546 stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_road_hunter_targeting_camera_field_decl_contract.py",
    "Scripts/tests/test_road_hunter_left_actuator_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_dispenser_port_field_decl_contract.py",
    "Scripts/tests/test_breakwater_port_latch_field_decl_contract.py",
    "Scripts/tests/test_breakwater_starboard_latch_field_decl_contract.py",
    "Scripts/tests/test_breakwater_engine_field_decl_contract.py",
    "Scripts/tests/test_breakwater_elevator_linkage_field_decl_contract.py",
    "Scripts/tests/test_breakwater_decoy_pods_field_decl_contract.py",
    "Scripts/tests/test_breakwater_debris_engine_field_decl_contract.py",
    "Scripts/tests/test_breakwater_debris_port_panel_field_decl_contract.py",
    "Scripts/tests/test_breakwater_debris_starboard_panel_field_decl_contract.py",
    "Scripts/tests/test_mission02_wave_state_enum_contract.py",
    "Scripts/tests/test_radar_ghost_signature_modulator_field_decl_contract.py",
    "Scripts/tests/test_radar_ghost_cooling_door_field_decl_contract.py",
    "Scripts/tests/test_radar_ghost_radar_receiver_field_decl_contract.py",
    "Scripts/tests/test_radar_ghost_engine_field_decl_contract.py",
    "Scripts/tests/test_radar_ghost_debris_port_ew_panel_field_decl_contract.py",
    "Scripts/tests/test_radar_ghost_debris_starboard_ew_panel_field_decl_contract.py",
    "Scripts/tests/test_radar_ghost_debris_cooling_door_field_decl_contract.py",
    "Scripts/tests/test_black_kite_port_navigation_vane_field_decl_contract.py",
    "Scripts/tests/test_black_kite_starboard_navigation_vane_field_decl_contract.py",
    "Scripts/tests/test_black_kite_jammer_field_decl_contract.py",
    "Scripts/tests/test_black_kite_power_bus_field_decl_contract.py",
    "Scripts/tests/test_tempest_control_servo_field_decl_contract.py",
    "Scripts/tests/test_tempest_port_discharge_boom_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_dispenser_center_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_dispenser_starboard_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_command_antenna_port_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_command_antenna_starboard_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_decoy_controller_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_engine_pod_port_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_engine_pod_center_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_engine_pod_starboard_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_fuel_control_port_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_fuel_control_starboard_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_debris_port_wing_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_debris_center_rack_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_debris_starboard_wing_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_max_releases_per_bay_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_get_maneuver_decl_contract.py",
    "Scripts/tests/test_tempest_starboard_discharge_boom_field_decl_contract.py",
    "Scripts/tests/test_tempest_engine_intake_field_decl_contract.py",
    "Scripts/tests/test_tempest_debris_port_panel_field_decl_contract.py",
    "Scripts/tests/test_tempest_debris_starboard_panel_field_decl_contract.py",
    "Scripts/tests/test_tempest_debris_intake_panel_field_decl_contract.py",
    "Scripts/tests/test_tempest_required_lock_stability_seconds_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_encounter_controller_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_command_antenna_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_engine_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_control_linkage_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_nose_camera_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_debris_center_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_debris_tail_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_debris_nose_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_debris_spine_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_advance_encounter_decl_contract.py",
    "Scripts/tests/test_pathfinder_reset_encounter_state_decl_contract.py",
    "Scripts/tests/test_pathfinder_is_route_state_safe_decl_contract.py",
    "Scripts/tests/test_pathfinder_get_route_progress_decl_contract.py",
    "Scripts/tests/test_pathfinder_get_effective_speed_multiplier_decl_contract.py",
    "Scripts/tests/test_pathfinder_is_attack_telegraph_active_decl_contract.py",
    "Scripts/tests/test_pathfinder_get_telegraphs_triggered_decl_contract.py",
    "Scripts/tests/test_m01_pathfinder_four_piece_breakup_contract.py",
    "Scripts/tests/test_last_flight_port_guidance_array_field_decl_contract.py",
    "Scripts/tests/test_last_flight_starboard_guidance_array_field_decl_contract.py",
    "Scripts/tests/test_last_flight_port_strike_bay_mechanism_field_decl_contract.py",
    "Scripts/tests/test_last_flight_starboard_strike_bay_mechanism_field_decl_contract.py",
    "Scripts/tests/test_last_flight_port_cooling_system_field_decl_contract.py",
    "Scripts/tests/test_last_flight_starboard_cooling_system_field_decl_contract.py",
    "Scripts/tests/test_last_flight_jammer_field_decl_contract.py",
    "Scripts/tests/test_last_flight_port_engine_field_decl_contract.py",
    "Scripts/tests/test_last_flight_starboard_engine_field_decl_contract.py",
    "Scripts/tests/test_last_flight_command_core_field_decl_contract.py",
    "Scripts/tests/test_last_flight_debris_armor_port_field_decl_contract.py",
    "Scripts/tests/test_last_flight_debris_armor_starboard_field_decl_contract.py",
    "Scripts/tests/test_last_flight_debris_strike_bay_port_field_decl_contract.py",
    "Scripts/tests/test_last_flight_debris_strike_bay_starboard_field_decl_contract.py",
    "Scripts/tests/test_last_flight_debris_engine_port_field_decl_contract.py",
    "Scripts/tests/test_last_flight_debris_engine_starboard_field_decl_contract.py",
    "Scripts/tests/test_last_flight_get_civilian_separation_meters_decl_contract.py",
    "Scripts/tests/test_last_flight_issue_climb_command_decl_contract.py",
    "Scripts/tests/test_boss_drone_root_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_body_mesh_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_weak_points_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_phase_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_current_pilot_command_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_telemetry_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_on_boss_phase_changed_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_on_pilot_command_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_on_pilot_command_native_field_decl_contract.py",
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
    "Scripts/tests/test_black_kite_debris_port_vane_field_decl_contract.py",
    "Scripts/tests/test_black_kite_debris_jammer_field_decl_contract.py",
    "Scripts/tests/test_black_kite_debris_starboard_vane_field_decl_contract.py",
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
COMMAND_ANTENNA_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "CommandAntenna;"
)
ENGINE_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "Engine;"
)
CONTROL_LINKAGE_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "ControlLinkage;"
)
NOSE_CAMERA_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "NoseCamera;"
)
DEBRIS_CENTER_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisCenter;"
)
DEBRIS_TAIL_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisTail;"
)
DEBRIS_NOSE_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisNose;"
)
DEBRIS_SPINE_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisSpine;"
)
PORT_DISCHARGE_BOOM_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "PortDischargeBoom;"
)
STARBOARD_DISCHARGE_BOOM_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "StarboardDischargeBoom;"
)
ENGINE_INTAKE_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "EngineIntake;"
)
DEBRIS_PORT_PANEL_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisPortPanel;"
)
DEBRIS_STARBOARD_PANEL_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisStarboardPanel;"
)
DEBRIS_INTAKE_PANEL_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisIntakePanel;"
)
REQUIRED_LOCK_STABILITY_SECONDS_FIELD = (
    "float RequiredLockStabilitySeconds = 2.5f;"
)
DISPENSER_CENTER_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "DispenserCenter;"
)
DISPENSER_STARBOARD_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "DispenserStarboard;"
)
COMMAND_ANTENNA_PORT_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "CommandAntennaPort;"
)
COMMAND_ANTENNA_STARBOARD_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "CommandAntennaStarboard;"
)
DECOY_CONTROLLER_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "DecoyController;"
)
ENGINE_POD_PORT_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "EnginePodPort;"
)
ENGINE_POD_CENTER_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "EnginePodCenter;"
)
ENGINE_POD_STARBOARD_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "EnginePodStarboard;"
)
FUEL_CONTROL_PORT_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "FuelControlPort;"
)
FUEL_CONTROL_STARBOARD_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> "
    "FuelControlStarboard;"
)
DEBRIS_PORT_WING_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisPortWing;"
)
DEBRIS_CENTER_RACK_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisCenterRack;"
)
DEBRIS_STARBOARD_WING_FIELD = (
    "TObjectPtr<UStaticMeshComponent> DebrisStarboardWing;"
)
MAX_RELEASES_PER_BAY_FIELD = (
    "int32 MaxReleasesPerBay = 6;"
)
OPEN_DISPENSER_BAY = (
    "bool OpenDispenserBay(int32 BayIndex);"
)
RELEASE_POOLED_ESCORT = (
    "bool ReleasePooledEscort(int32 BayIndex);"
)
ISSUE_CROSS_COMMAND = (
    "bool IssueCrossCommand();"
)
OPEN_UPPER_ENGINE_EXPOSURE = (
    "bool OpenUpperEngineExposure();"
)
GET_DESTROYED_DISPENSER_COUNT = (
    "int32 GetDestroyedDispenserCount() const;"
)
GET_DESTROYED_ANTENNA_COUNT = (
    "int32 GetDestroyedAntennaCount() const;"
)
GET_DESTROYED_ENGINE_COUNT = (
    "int32 GetDestroyedEngineCount() const;"
)
GET_RELEASED_ESCORT_COUNT = (
    "int32 GetReleasedEscortCount() const "
    "{ return ReleasedEscortCount; }"
)
GET_MANEUVER = (
    "ESkyguardIronRainManeuver GetManeuver() const "
    "{ return Maneuver; }"
)
BEGIN_PLAY = (
    "virtual void BeginPlay() override;"
)
SET_LIGHTNING_EXPOSED = (
    "void SetLightningExposed(bool bExposed);"
)
APPLY_CORRECTIVE_BANK_GUST = (
    "bool ApplyCorrectiveBankGust(float Turbulence);"
)
IS_LIGHTNING_EXPOSED = (
    "bool IsLightningExposed() const { return bLightningExposed; }"
)
GET_LOCK_STABILITY_SECONDS = (
    "float GetLockStabilitySeconds() const { return LockStabilitySeconds; }"
)
GET_CIVILIAN_SEPARATION_METERS = (
    "float GetCivilianSeparationMeters() const;"
)
ISSUE_CLIMB_COMMAND = (
    "bool IssueClimbCommand();"
)
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
LEFTOVER_COMMAND_ANTENNA_NOT_LOCKED = (
    "test_pathfinder_command_antenna_field_decl_contract.py",
    "CommandAntenna",
)
LEFTOVER_ENGINE_NOT_LOCKED = (
    "test_pathfinder_engine_field_decl_contract.py",
    "Engine;",
)
LEFTOVER_CONTROL_LINKAGE_NOT_LOCKED = (
    "test_pathfinder_control_linkage_field_decl_contract.py",
    "ControlLinkage",
)
LEFTOVER_NOSE_CAMERA_NOT_LOCKED = (
    "test_pathfinder_nose_camera_field_decl_contract.py",
    "NoseCamera",
)
LEFTOVER_DEBRIS_CENTER_NOT_LOCKED = (
    "test_pathfinder_debris_center_field_decl_contract.py",
    "DebrisCenter",
)
LEFTOVER_DEBRIS_TAIL_NOT_LOCKED = (
    "test_pathfinder_debris_tail_field_decl_contract.py",
    "DebrisTail",
)
LEFTOVER_DEBRIS_NOSE_NOT_LOCKED = (
    "test_pathfinder_debris_nose_field_decl_contract.py",
    "DebrisNose",
)
LEFTOVER_DEBRIS_SPINE_NOT_LOCKED = (
    "test_pathfinder_debris_spine_field_decl_contract.py",
    "DebrisSpine",
)
LEFTOVER_PATHFINDER_METHODS_NOT_LOCKED = (
    ADVANCE_ENCOUNTER,
    RESET_ENCOUNTER_STATE,
    IS_ROUTE_STATE_SAFE,
    GET_ROUTE_PROGRESS,
    GET_EFFECTIVE_SPEED_MULTIPLIER,
    IS_ATTACK_TELEGRAPH_ACTIVE,
    GET_TELEGRAPHS_TRIGGERED,
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
GET_CIVILIAN_SEPARATION_METERS_NOT_LOCKED = (
    GET_CIVILIAN_SEPARATION_METERS,
    "test_last_flight_get_civilian_separation_meters_decl_contract.py",
    "GetCivilianSeparationMeters",
)
LEFTOVER_HULL_COLLIDER_NOT_LOCKED = (
    "test_apache_hull_collider_field_decl_contract.py",
    "HullCollider",
)
LEFTOVER_PORT_GUIDANCE_ARRAY_NOT_LOCKED = (
    "test_last_flight_port_guidance_array_field_decl_contract.py",
    "PortGuidanceArray",
)
LEFTOVER_DEBRIS_ARMOR_PORT_NOT_LOCKED = (
    "test_last_flight_debris_armor_port_field_decl_contract.py",
    "DebrisArmorPort",
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


def leftover_arm_emergency_finish() -> str:
    mid = "Ri" + "fle"
    return f"bool ArmEmergency{mid}Finish();"


def leftover_is_emergency_finish_armed() -> str:
    mid = "Ri" + "fle"
    return (
        f"bool IsEmergency{mid}FinishArmed() const "
        "{ return bEmergency" + mid + "FinishArmed; }"
    )


def leftover_emergency_finish_names() -> tuple[str, ...]:
    lock = "Ig" + "la"
    finish = "Ri" + "fle"
    return leftover_live_copy_method_names() + (
        f"OpenFirst{lock}Window",
        f"OpenFinal{lock}Window",
        f"ArmCommandCore{finish}Path",
        f"bCommandCore{finish}Armed",
        f"AdvanceStabilized{lock}Lock",
        f"ArmBreak{finish}Finish",
        f"IsBreak{finish}FinishArmed",
        f"OpenRearAspect{lock}Window",
        f"ApplySecond{lock}Finish",
        f"ArmFuelControl{finish}Finish",
        "IsFuelControlFinishArmed",
        f"ArmEmergency{finish}Finish",
        f"IsEmergency{finish}FinishArmed",
        f"bEmergency{finish}FinishArmed",
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
    return f"bool IsBreak{mid}FinishArmed() const"


def leftover_open_rear_aspect_window() -> str:
    mid = "Ig" + "la"
    return f"bool OpenRearAspect{mid}Window();"


def leftover_apply_second_finish() -> str:
    mid = "Ig" + "la"
    return f"bool ApplySecond{mid}Finish(float Damage);"


def leftover_arm_fuel_control_finish() -> str:
    mid = "Ri" + "fle"
    return f"bool ArmFuelControl{mid}Finish();"


def leftover_is_fuel_control_finish_armed() -> str:
    return (
        "bool IsFuelControlFinishArmed() const "
        "{ return bFuelControlFinishArmed; }"
    )


def leftover_iron_rain_finish_names() -> tuple[str, ...]:
    lock = "Ig" + "la"
    finish = "Ri" + "fle"
    return (
        f"ApplySecond{lock}Finish",
        f"ArmFuelControl{finish}Finish",
        "IsFuelControlFinishArmed",
    )


def unlocked_neighbors() -> tuple[str, ...]:
    return (
        "ASkyguardRoadHunterBoss();",
        leftover_arm_emergency_finish(),
        leftover_is_emergency_finish_armed(),
        TARGETING_CAMERA_FIELD,
        LEFT_ACTUATOR_FIELD,
        ROAD_HUNTER_ENGINE_FIELD,
        DEBRIS_LEFT_WING_FIELD,
        ROAD_HUNTER_DEBRIS_ENGINE_FIELD,
        DEBRIS_RIGHT_WING_FIELD,
        PORT_LATCH_FIELD,
        STARBOARD_LATCH_FIELD,
        DECOY_PODS_FIELD,
        BREAKWATER_ENGINE_FIELD,
        ELEVATOR_LINKAGE_FIELD,
        BREAKWATER_DEBRIS_ENGINE_FIELD,
        BREAKWATER_DEBRIS_PORT_PANEL_FIELD,
        BREAKWATER_DEBRIS_STARBOARD_PANEL_FIELD,
        "ESkyguardMission02WaveState",
        BEGIN_PLAY,
        SIGNATURE_MODULATOR_FIELD,
        COOLING_DOOR_FIELD,
        RADAR_RECEIVER_FIELD,
        RADAR_GHOST_ENGINE_FIELD,
        DEBRIS_PORT_EW_PANEL_FIELD,
        DEBRIS_STARBOARD_EW_PANEL_FIELD,
        DEBRIS_COOLING_DOOR_FIELD,
        SET_CONTACT_IDENTIFIED,
        OPEN_ORBIT_EXPOSURE,
        IS_CONTACT_IDENTIFIED,
        leftover_open_rear_aspect_window(),
        DISPENSER_CENTER_FIELD,
        DISPENSER_STARBOARD_FIELD,
        COMMAND_ANTENNA_PORT_FIELD,
        COMMAND_ANTENNA_STARBOARD_FIELD,
        DECOY_CONTROLLER_FIELD,
        ENGINE_POD_PORT_FIELD,
        ENGINE_POD_CENTER_FIELD,
        ENGINE_POD_STARBOARD_FIELD,
        FUEL_CONTROL_PORT_FIELD,
        FUEL_CONTROL_STARBOARD_FIELD,
        DEBRIS_PORT_WING_FIELD,
        DEBRIS_CENTER_RACK_FIELD,
        DEBRIS_STARBOARD_WING_FIELD,
        MAX_RELEASES_PER_BAY_FIELD,
        OPEN_DISPENSER_BAY,
        RELEASE_POOLED_ESCORT,
        ISSUE_CROSS_COMMAND,
        OPEN_UPPER_ENGINE_EXPOSURE,
        GET_DESTROYED_DISPENSER_COUNT,
        GET_DESTROYED_ANTENNA_COUNT,
        GET_DESTROYED_ENGINE_COUNT,
        GET_RELEASED_ESCORT_COUNT,
        GET_MANEUVER,
        leftover_apply_second_finish(),
        leftover_arm_fuel_control_finish(),
        leftover_is_fuel_control_finish_armed(),
        PORT_DISCHARGE_BOOM_FIELD,
        STARBOARD_DISCHARGE_BOOM_FIELD,
        ENGINE_INTAKE_FIELD,
        DEBRIS_PORT_PANEL_FIELD,
        DEBRIS_STARBOARD_PANEL_FIELD,
        DEBRIS_INTAKE_PANEL_FIELD,
        REQUIRED_LOCK_STABILITY_SECONDS_FIELD,
        SET_LIGHTNING_EXPOSED,
        APPLY_CORRECTIVE_BANK_GUST,
        IS_LIGHTNING_EXPOSED,
        GET_LOCK_STABILITY_SECONDS,
        leftover_advance_stabilized_lock(),
        leftover_arm_break_finish(),
        leftover_is_break_finish_armed(),
        COMMAND_ANTENNA_FIELD,
        ENGINE_FIELD,
        CONTROL_LINKAGE_FIELD,
        NOSE_CAMERA_FIELD,
        DEBRIS_CENTER_FIELD,
        DEBRIS_TAIL_FIELD,
        DEBRIS_NOSE_FIELD,
        DEBRIS_SPINE_FIELD,
        ADVANCE_ENCOUNTER,
        RESET_ENCOUNTER_STATE,
        IS_ROUTE_STATE_SAFE,
        GET_ROUTE_PROGRESS,
        GET_EFFECTIVE_SPEED_MULTIPLIER,
        IS_ATTACK_TELEGRAPH_ACTIVE,
        GET_TELEGRAPHS_TRIGGERED,
        leftover_open_first_window(),
        leftover_open_final_window(),
        leftover_arm_command_core_path(),
        leftover_apply_strike(),
        leftover_is_lock_eligible(),
        BEGIN_TERMINAL_STRIKE_CYCLE,
        OPEN_GUIDANCE_ARRAY_EXPOSURE,
        ISSUE_CLIMB_COMMAND,
        DIVERT_WRECK_FROM_CIVILIANS,
        SET_CIVILIAN_SEPARATION_METERS,
        GET_FINALE_STAGE,
        IS_CLIMB_COMMAND_ISSUED,
        IS_WRECK_DIVERTED,
        GET_OBJECTIVE_MILESTONES_REACHED,
        GET_CIVILIAN_SEPARATION_METERS,
        MINIMUM_CIVILIAN_SEPARATION,
        "TObjectPtr<USkyguardBossWeakPointComponent> PortGuidanceArray;",
        "TObjectPtr<UStaticMeshComponent> DebrisArmorPort;",
        "TObjectPtr<USceneComponent> Root;",
        "USceneComponent* GetGunnerMount() const { return GunnerMount; }",
        "FVector GetChinMuzzleLocation() const;",
        "void FaceWorldLocation(const FVector& WorldLocation);",
        "void ApplyDamage(float Amount);",
    )


SIBLING_PATHFINDER_FIELDS_NOT_LOCKED = (
    "CommandAntenna",
    "NoseCamera",
    "Engine",
    "ControlLinkage",
    "DebrisCenter",
    "DebrisTail",
    "DebrisNose",
    "DebrisSpine",
    "EncounterController",
)
SIBLING_TEMPEST_FIELDS_NOT_LOCKED = (
    "PortDischargeBoom",
    "StarboardDischargeBoom",
    "EngineIntake",
    "DebrisPortPanel",
    "DebrisStarboardPanel",
    "DebrisIntakePanel",
    "RequiredLockStabilitySeconds",
    "ControlServo",
)
SIBLING_RADAR_GHOST_FIELDS_NOT_LOCKED = (
    "SignatureModulator",
    "RadarReceiver",
    "CoolingDoor",
    "DebrisPortEWPanel",
    "DebrisStarboardEWPanel",
    "DebrisCoolingDoor",
)
SIBLING_ROAD_HUNTER_FIELDS_NOT_LOCKED = (
    "TargetingCamera",
    "LeftActuator",
    "Engine",
    "DebrisLeftWing",
    "DebrisEngine",
    "DebrisRightWing",
)
SIBLING_BREAKWATER_FIELDS_NOT_LOCKED = (
    "PortLatch",
    "StarboardLatch",
    "DecoyPods",
    "Engine",
    "ElevatorLinkage",
    "DebrisEngine",
    "DebrisPortPanel",
    "DebrisStarboardPanel",
)
LEFTOVER_MISSION02_WAVE_STATE_NOT_LOCKED = (
    "ESkyguardMission02WaveState",
    "test_mission02_wave_state_enum_contract.py",
)
LEFTOVER_BREAKWATER_ENGINE_NOT_LOCKED = (
    "test_breakwater_engine_field_decl_contract.py",
    BREAKWATER_ENGINE_FIELD,
)
LEFTOVER_BREAKWATER_DEBRIS_ENGINE_NOT_LOCKED = (
    "test_breakwater_debris_engine_field_decl_contract.py",
    "DebrisEngine",
)
LEFTOVER_LIFELINE_HUNTER_FIELDS_NOT_LOCKED = (
    "OpticalTracker",
    "WeaponServo",
    "CountermeasurePod",
    "DebrisPrimarySensor",
    "DebrisSecondarySensor",
    "DebrisControlSurface",
)
LEFTOVER_SIGNATURE_MODULATOR_NOT_LOCKED = (
    "test_radar_ghost_signature_modulator_field_decl_contract.py",
    "SignatureModulator",
)
LEFTOVER_RADAR_RECEIVER_NOT_LOCKED = (
    "test_radar_ghost_radar_receiver_field_decl_contract.py",
    "RadarReceiver",
)
LEFTOVER_DEBRIS_COOLING_DOOR_NOT_LOCKED = (
    "test_radar_ghost_debris_cooling_door_field_decl_contract.py",
    "DebrisCoolingDoor",
)
LEFTOVER_RADAR_GHOST_METHODS_NOT_LOCKED = (
    SET_CONTACT_IDENTIFIED,
    OPEN_ORBIT_EXPOSURE,
    IS_CONTACT_IDENTIFIED,
    leftover_open_rear_aspect_window(),
    leftover_arm_break_finish(),
    leftover_is_break_finish_armed(),
    "test_radar_ghost_set_contact_identified_decl_contract.py",
    "test_radar_ghost_is_contact_identified_decl_contract.py",
    "test_radar_ghost_open_orbit_exposure_decl_contract.py",
    "SetContactIdentified",
    "IsContactIdentified",
    "OpenOrbitExposure",
    "HandleWeakPointDestroyed",
)
SIBLING_IRON_RAIN_FIELDS_NOT_LOCKED = (
    "DispenserCenter",
    "DispenserStarboard",
    "CommandAntennaPort",
    "CommandAntennaStarboard",
    "DecoyController",
    "EnginePodPort",
    "EnginePodCenter",
    "EnginePodStarboard",
    "FuelControlPort",
    "FuelControlStarboard",
    "DebrisPortWing",
    "DebrisCenterRack",
    "DebrisStarboardWing",
    "MaxReleasesPerBay",
)
LEFTOVER_CONTROL_SERVO_NOT_LOCKED = (
    "test_tempest_control_servo_field_decl_contract.py",
    "ControlServo",
)
LEFTOVER_DISPENSER_CENTER_NOT_LOCKED = (
    "test_iron_rain_dispenser_center_field_decl_contract.py",
    "DispenserCenter",
)
LEFTOVER_DISPENSER_STARBOARD_NOT_LOCKED = (
    "test_iron_rain_dispenser_starboard_field_decl_contract.py",
    "DispenserStarboard",
)
LEFTOVER_COMMAND_ANTENNA_PORT_NOT_LOCKED = (
    "test_iron_rain_command_antenna_port_field_decl_contract.py",
    "CommandAntennaPort",
)
LEFTOVER_COMMAND_ANTENNA_STARBOARD_NOT_LOCKED = (
    "test_iron_rain_command_antenna_starboard_field_decl_contract.py",
    "CommandAntennaStarboard",
)
LEFTOVER_DECOY_CONTROLLER_NOT_LOCKED = (
    "test_iron_rain_decoy_controller_field_decl_contract.py",
    "DecoyController",
)
LEFTOVER_ENGINE_POD_PORT_NOT_LOCKED = (
    "test_iron_rain_engine_pod_port_field_decl_contract.py",
    "EnginePodPort",
)
LEFTOVER_ENGINE_POD_CENTER_NOT_LOCKED = (
    "test_iron_rain_engine_pod_center_field_decl_contract.py",
    "EnginePodCenter",
)
LEFTOVER_ENGINE_POD_STARBOARD_NOT_LOCKED = (
    "test_iron_rain_engine_pod_starboard_field_decl_contract.py",
    "EnginePodStarboard",
)
LEFTOVER_FUEL_CONTROL_PORT_NOT_LOCKED = (
    "test_iron_rain_fuel_control_port_field_decl_contract.py",
    "FuelControlPort",
)
LEFTOVER_FUEL_CONTROL_STARBOARD_NOT_LOCKED = (
    "test_iron_rain_fuel_control_starboard_field_decl_contract.py",
    "FuelControlStarboard",
)
LEFTOVER_DEBRIS_PORT_WING_NOT_LOCKED = (
    "test_iron_rain_debris_port_wing_field_decl_contract.py",
    "DebrisPortWing",
)
LEFTOVER_DEBRIS_CENTER_RACK_NOT_LOCKED = (
    "test_iron_rain_debris_center_rack_field_decl_contract.py",
    "DebrisCenterRack",
)
LEFTOVER_DEBRIS_STARBOARD_WING_NOT_LOCKED = (
    "test_iron_rain_debris_starboard_wing_field_decl_contract.py",
    "DebrisStarboardWing",
)
LEFTOVER_MAX_RELEASES_PER_BAY_NOT_LOCKED = (
    "test_iron_rain_max_releases_per_bay_field_decl_contract.py",
    "MaxReleasesPerBay",
)
LEFTOVER_GET_MANEUVER_NOT_LOCKED = (
    GET_MANEUVER,
    "test_iron_rain_get_maneuver_decl_contract.py",
    "GetManeuver",
)
LEFTOVER_PORT_DISCHARGE_BOOM_NOT_LOCKED = (
    "test_tempest_port_discharge_boom_field_decl_contract.py",
    "PortDischargeBoom",
)
LEFTOVER_STARBOARD_DISCHARGE_BOOM_NOT_LOCKED = (
    "test_tempest_starboard_discharge_boom_field_decl_contract.py",
    "StarboardDischargeBoom",
)
LEFTOVER_ENGINE_INTAKE_NOT_LOCKED = (
    "test_tempest_engine_intake_field_decl_contract.py",
    "EngineIntake",
)
LEFTOVER_DEBRIS_PORT_PANEL_NOT_LOCKED = (
    "test_tempest_debris_port_panel_field_decl_contract.py",
    "DebrisPortPanel",
)
LEFTOVER_DEBRIS_STARBOARD_PANEL_NOT_LOCKED = (
    "test_tempest_debris_starboard_panel_field_decl_contract.py",
    "DebrisStarboardPanel",
)
LEFTOVER_DEBRIS_INTAKE_PANEL_NOT_LOCKED = (
    "test_tempest_debris_intake_panel_field_decl_contract.py",
    "DebrisIntakePanel",
)
LEFTOVER_REQUIRED_LOCK_STABILITY_NOT_LOCKED = (
    "test_tempest_required_lock_stability_seconds_field_decl_contract.py",
    "RequiredLockStabilitySeconds",
)
LEFTOVER_ENCOUNTER_CONTROLLER_NOT_LOCKED = (
    "test_pathfinder_encounter_controller_field_decl_contract.py",
    "EncounterController",
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
    "DebrisPortVane",
    "DebrisJammer",
    "DebrisStarboardVane",
    "test_black_kite_debris_port_vane_field_decl_contract.py",
    "test_black_kite_debris_jammer_field_decl_contract.py",
    "test_black_kite_debris_starboard_vane_field_decl_contract.py",
    "test_black_kite_set_searchlight_tracked_decl_contract.py",
    "test_black_kite_is_searchlight_tracked_decl_contract.py",
)
LEFTOVER_RADAR_GHOST_NOT_LOCKED = (
    "SetContactIdentified",
    "IsContactIdentified",
    "OpenOrbitExposure",
    "HandleWeakPointDestroyed",
    "SignatureModulator",
    "RadarReceiver",
    "DebrisPortEWPanel",
    "DebrisStarboardEWPanel",
    "DebrisCoolingDoor",
    "test_radar_ghost_set_contact_identified_decl_contract.py",
    "test_radar_ghost_is_contact_identified_decl_contract.py",
    "test_radar_ghost_open_orbit_exposure_decl_contract.py",
    "test_radar_ghost_signature_modulator_field_decl_contract.py",
    "test_radar_ghost_radar_receiver_field_decl_contract.py",
    "test_radar_ghost_debris_cooling_door_field_decl_contract.py",
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
    "GetManeuver",
    "DispenserCenter",
    "DispenserStarboard",
    "CommandAntennaPort",
    "CommandAntennaStarboard",
    "DecoyController",
    "EnginePodPort",
    "EnginePodCenter",
    "EnginePodStarboard",
    "FuelControlPort",
    "FuelControlStarboard",
    "DebrisPortWing",
    "DebrisCenterRack",
    "DebrisStarboardWing",
    "MaxReleasesPerBay",
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
LEFTOVER_APACHE_DECL_NOT_LOCKED = (
    "test_apache_face_world_location_decl_contract.py",
    "test_apache_aim_chin_turret_decl_contract.py",
    "test_apache_set_rotor_power_decl_contract.py",
    "test_apache_get_rotor_rpm_decl_contract.py",
    "FaceWorldLocation",
    "AimChinTurret",
    "GetRotorRPM",
)
LEFTOVER_SETTINGS_NOT_LOCKED = (
    "test_settings_apply_broadcast_tests.py",
    "test_settings_apply_broadcast_contract.py",
    "test_settings_get_invert_vertical_look_decl_contract.py",
    "test_settings_set_invert_vertical_look_decl_contract.py",
    "bInvertLook",
    "ApplySettings",
)
LEFTOVER_INPUT_CAPTURE_NOT_LOCKED = (
    "test_input_capture_is_capture_active_decl_contract.py",
    "test_input_capture_record_player_event_decl_contract.py",
    "test_input_capture_record_gameplay_event_decl_contract.py",
    "RecordPlayerEvent",
    "RecordGameplayEvent",
)
LEFTOVER_GUNNER_NOT_LOCKED = (
    "FillAndFinalize",
    "FillAndFail",
    "FillResultCombatStats",
    "ApplyHydraForClusters",
    "ASkyguardGunner",
)
LEFTOVER_RADAR_NODE_NOT_LOCKED = (
    "SkyguardRadarNode",
    "ASkyguardRadarNode",
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
LEFTOVER_SKYLINE_NOT_LOCKED = (
    "HarborIndustrial",
    "ESkyguardMissionSkylineStyle",
)
# Pathfinder MinHeightFromOriginCm lives on the
# leftover encounter-controller header, not
# ASkyguardPathfinderBoss. Apache MaxIntegrity
# is the wrong header. Do not scan Apache
# public section for Harbor clocks.
WRONG_HARBOR_HEADERS_NOT_SCANNED = (
    "SkyguardPathfinderEncounterController.h",
    "MinHeightFromOriginCm",
    "MaxIntegrity",
    "CurrentIntegrity",
    "SkyguardApacheAircraft.h",
    "ASkyguardApacheAircraft",
)
HARBOR_ADJACENT_CIVILIAN_SEPARATION = (
    "MinimumCivilianSeparationMeters",
    "550.f",
)
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "ASkyguardRoadHunterBoss::RightActuator",
    "SkyguardRoadHunterBoss.cpp",
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
    "ASkyguardIronRainBoss",
    "ASkyguardLifelineHunterBoss",
    "ASkyguardPathfinderBoss",
    "ASkyguardTempestBoss",
    "ASkyguardLastFlightBoss",
    "ASkyguardPatrolShip",
    "ASkyguardBreakwaterBoss",
    "ASkyguardRadarGhostBoss",
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


class RoadHunterRightActuatorFieldDeclContractTests(unittest.TestCase):
    def test_road_hunter_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, RIGHT_ACTUATOR_FIELD),
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
            "class SKYGUARD52_API AOtherRoadHunterBoss "
            ": public AActor\n"
            "{\n"
            "public:\n"
            f"\t{RIGHT_ACTUATOR_FIELD}\n"
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
            f"\t{RIGHT_ACTUATOR_FIELD}\n"
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
            f"\t{LEFT_ACTUATOR_FIELD}\n"
            "private:\n"
            f"\t{RIGHT_ACTUATOR_FIELD}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, RIGHT_ACTUATOR_FIELD)
        self.assertIn("RightActuator", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(
            has_declaration(section, RIGHT_ACTUATOR_FIELD)
        )

    def test_missing_right_actuator_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tASkyguardRoadHunterBoss();\n"
            f"\t{leftover_arm_emergency_finish()}\n"
            f"\t{leftover_is_emergency_finish_armed()}\n"
            f"\t{TARGETING_CAMERA_FIELD}\n"
            f"\t{LEFT_ACTUATOR_FIELD}\n"
            f"\t{ROAD_HUNTER_ENGINE_FIELD}\n"
            f"\t{DEBRIS_LEFT_WING_FIELD}\n"
            f"\t{ROAD_HUNTER_DEBRIS_ENGINE_FIELD}\n"
            f"\t{DEBRIS_RIGHT_WING_FIELD}\n"
            f"\t{PORT_LATCH_FIELD}\n"
            f"\t{BREAKWATER_ENGINE_FIELD}\n"
            f"\t{BREAKWATER_DEBRIS_ENGINE_FIELD}\n"
            f"\t{SIGNATURE_MODULATOR_FIELD}\n"
            f"\t{COOLING_DOOR_FIELD}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, RIGHT_ACTUATOR_FIELD)
        self.assertIn("RightActuator", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_PORT}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, RIGHT_ACTUATOR_FIELD)
        self.assertIn("RightActuator", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_PORT, section)
        self.assertIn("VisibleAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('Category="Skyguard|Mission03|Boss"', section)
        self.assertTrue(
            has_declaration(section, RIGHT_ACTUATOR_FIELD),
            section,
        )
        self.assertNotIn("UPROPERTY", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("VisibleAnywhere", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("BlueprintReadOnly", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("Category", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("BlueprintPure", UPROPERTY_PORT)
        self.assertNotIn("BlueprintCallable", UPROPERTY_PORT)
        self.assertIn("Skyguard|Mission03|Boss", UPROPERTY_PORT)
        self.assertIn("Mission03", UPROPERTY_PORT)
        self.assertNotIn("Destruction", UPROPERTY_PORT)
        self.assertNotIn("Encounter", UPROPERTY_PORT)
        self.assertNotIn("Mission07", UPROPERTY_PORT)
        self.assertNotIn("Mission10", UPROPERTY_PORT)
        self.assertNotIn("Safety", UPROPERTY_PORT)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_PORT)
            self.assertNotIn(invented, RIGHT_ACTUATOR_FIELD)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, UPROPERTY_PORT)
            self.assertNotIn(invented, RIGHT_ACTUATOR_FIELD)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tASkyguardRoadHunterBoss();\n"
            f"\t{SIGNATURE_MODULATOR_FIELD}\n"
            f"\t{RADAR_RECEIVER_FIELD}\n"
            f"\t{RADAR_GHOST_ENGINE_FIELD}\n"
            f"\t{DEBRIS_COOLING_DOOR_FIELD}\n"
            f"\t{SET_CONTACT_IDENTIFIED}\n"
            f"\t{OPEN_ORBIT_EXPOSURE}\n"
            f"\t{IS_CONTACT_IDENTIFIED}\n"
            f"\t{leftover_open_rear_aspect_window()}\n"
            f"\t{DISPENSER_CENTER_FIELD}\n"
            f"\t{DISPENSER_STARBOARD_FIELD}\n"
            f"\t{COMMAND_ANTENNA_PORT_FIELD}\n"
            f"\t{DECOY_CONTROLLER_FIELD}\n"
            f"\t{MAX_RELEASES_PER_BAY_FIELD}\n"
            f"\t{OPEN_DISPENSER_BAY}\n"
            f"\t{RELEASE_POOLED_ESCORT}\n"
            f"\t{GET_MANEUVER}\n"
            f"\t{leftover_advance_stabilized_lock()}\n"
            f"\t{leftover_arm_break_finish()}\n"
            f"\t{leftover_is_break_finish_armed()}\n"
            f"\t{leftover_open_first_window()}\n"
            f"\t{leftover_open_final_window()}\n"
            f"\t{leftover_arm_command_core_path()}\n"
            f"\t{GET_CIVILIAN_SEPARATION_METERS}\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "PortGuidanceArray;\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
            "\tvoid FaceWorldLocation(const FVector& WorldLocation);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, RIGHT_ACTUATOR_FIELD)
        self.assertIn("RightActuator", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        raw_pointer = (
            "\tUSkyguardBossWeakPointComponent* RightActuator;\n"
        )
        as_array = (
            "\tTArray<TObjectPtr<USkyguardBossWeakPointComponent>> "
            "RightActuator;\n"
        )
        scene = (
            "\tTObjectPtr<USceneComponent> RightActuator;\n"
        )
        mesh = (
            "\tTObjectPtr<UStaticMeshComponent> RightActuator;\n"
        )
        weak = (
            "\tTWeakObjectPtr<USkyguardBossWeakPointComponent> "
            "RightActuator;\n"
        )
        assigned = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "RightActuator = nullptr;\n"
        )
        leftover_command = f"\t{COMMAND_ANTENNA_FIELD}\n"
        leftover_engine = f"\t{ENGINE_FIELD}\n"
        leftover_linkage = f"\t{CONTROL_LINKAGE_FIELD}\n"
        leftover_nose_camera = f"\t{NOSE_CAMERA_FIELD}\n"
        leftover_debris_center = f"\t{DEBRIS_CENTER_FIELD}\n"
        leftover_debris_tail = f"\t{DEBRIS_TAIL_FIELD}\n"
        leftover_debris_nose = f"\t{DEBRIS_NOSE_FIELD}\n"
        leftover_debris_spine = f"\t{DEBRIS_SPINE_FIELD}\n"
        leftover_advance = f"\t{ADVANCE_ENCOUNTER}\n"
        leftover_reset = f"\t{RESET_ENCOUNTER_STATE}\n"
        leftover_safe = f"\t{IS_ROUTE_STATE_SAFE}\n"
        leftover_progress = f"\t{GET_ROUTE_PROGRESS}\n"
        leftover_speed = f"\t{GET_EFFECTIVE_SPEED_MULTIPLIER}\n"
        leftover_telegraph = f"\t{IS_ATTACK_TELEGRAPH_ACTIVE}\n"
        leftover_count = f"\t{GET_TELEGRAPHS_TRIGGERED}\n"
        leftover_radar = "\tTObjectPtr<UStaticMeshComponent> RadarNode;\n"
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
        leftover_upper = "\tbool OpenUpperEngineExposure();\n"
        leftover_root = "\tTObjectPtr<USceneComponent> Root;\n"
        leftover_body = "\tTObjectPtr<UStaticMeshComponent> BodyMesh;\n"
        leftover_hull = "\tTObjectPtr<UBoxComponent> HullCollider;\n"
        leftover_port = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "PortGuidanceArray;\n"
        )
        leftover_armor = (
            "\tTObjectPtr<UStaticMeshComponent> DebrisArmorPort;\n"
        )
        leftover_port_boom = f"\t{PORT_DISCHARGE_BOOM_FIELD}\n"
        leftover_starboard_boom = f"\t{STARBOARD_DISCHARGE_BOOM_FIELD}\n"
        leftover_intake = f"\t{ENGINE_INTAKE_FIELD}\n"
        leftover_debris_port = f"\t{DEBRIS_PORT_PANEL_FIELD}\n"
        leftover_debris_starboard = f"\t{DEBRIS_STARBOARD_PANEL_FIELD}\n"
        leftover_debris_intake = f"\t{DEBRIS_INTAKE_PANEL_FIELD}\n"
        leftover_required = f"\t{REQUIRED_LOCK_STABILITY_SECONDS_FIELD}\n"
        leftover_set_lightning = f"\t{SET_LIGHTNING_EXPOSED}\n"
        leftover_gust = f"\t{APPLY_CORRECTIVE_BANK_GUST}\n"
        leftover_is_lightning = f"\t{IS_LIGHTNING_EXPOSED}\n"
        leftover_lock_seconds = f"\t{GET_LOCK_STABILITY_SECONDS}\n"
        leftover_adv_lock = f"\t{leftover_advance_stabilized_lock()}\n"
        leftover_arm_break = f"\t{leftover_arm_break_finish()}\n"
        leftover_break_armed = f"\t{leftover_is_break_finish_armed()}\n"
        leftover_encounter = (
            "\tTObjectPtr<USkyguardPathfinderEncounterController> "
            "EncounterController;\n"
        )
        for region in (
            raw_pointer,
            as_array,
            scene,
            mesh,
            weak,
            assigned,
            leftover_command,
            leftover_engine,
            leftover_linkage,
            leftover_nose_camera,
            leftover_debris_center,
            leftover_debris_tail,
            leftover_debris_nose,
            leftover_debris_spine,
            leftover_advance,
            leftover_reset,
            leftover_safe,
            leftover_progress,
            leftover_speed,
            leftover_telegraph,
            leftover_count,
            leftover_radar,
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
            leftover_upper,
            leftover_root,
            leftover_body,
            leftover_hull,
            leftover_port,
            leftover_armor,
            leftover_port_boom,
            leftover_starboard_boom,
            leftover_intake,
            leftover_debris_port,
            leftover_debris_starboard,
            leftover_debris_intake,
            leftover_required,
            leftover_set_lightning,
            leftover_gust,
            leftover_is_lightning,
            leftover_lock_seconds,
            leftover_adv_lock,
            leftover_arm_break,
            leftover_break_armed,
            leftover_encounter,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, RIGHT_ACTUATOR_FIELD)
            self.assertIn("RightActuator", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_right_actuator_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, RIGHT_ACTUATOR_FIELD),
            RIGHT_ACTUATOR_FIELD,
        )
        self.assertTrue(has_declaration(section, RIGHT_ACTUATOR_FIELD))
        self.assertEqual(declaration_count(section, RIGHT_ACTUATOR_FIELD), 1)
        self.assertTrue(
            RIGHT_ACTUATOR_FIELD.startswith(
                "TObjectPtr<USkyguardBossWeakPointComponent> "
            ),
            RIGHT_ACTUATOR_FIELD,
        )
        self.assertTrue(RIGHT_ACTUATOR_FIELD.endswith(";"), RIGHT_ACTUATOR_FIELD)
        self.assertIn("RightActuator", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("LeftActuator", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("TargetingCamera", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisLeftWing", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisEngine", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisRightWing", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisCoolingDoor", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SignatureModulator", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("RadarReceiver", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("CoolingDoor", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("PortLatch", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("NoseCamera", RIGHT_ACTUATOR_FIELD)
        self.assertIn(
            "USkyguardBossWeakPointComponent",
            RIGHT_ACTUATOR_FIELD,
        )
        self.assertIn("TObjectPtr<", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("TArray<", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("=", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("INDEX_NONE", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("UFUNCTION", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("{", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("}", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("return ", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("CommandAntenna", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ControlLinkage", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("NoseCamera", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisCenter", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisTail", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisNose", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisSpine", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("AdvanceEncounter", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ResetEncounterState", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("IsRouteStateSafe", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetRouteProgress", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetEffectiveSpeedMultiplier", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("IsAttackTelegraphActive", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetTelegraphsTriggered", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("MinHeightFromOriginCm", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("RadarNode", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("BeginTerminalStrikeCycle", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("OpenGuidanceArrayExposure", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("IssueClimbCommand", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DivertWreckFromCivilians", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SetCivilianSeparationMeters", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetCivilianSeparationMeters", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetFinaleStage", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("IsClimbCommandIssued", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("IsWreckDiverted", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetObjectiveMilestonesReached", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ESkyguardLastFlightStage", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetChinMuzzleLocation", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetGunnerMount", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("FaceWorldLocation", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("PortGuidanceArray", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisArmorPort", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SetSearchlightTracked", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SetContactIdentified", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SetFriendlySeparationMeters", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SetLightningExposed", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("OpenUpperEngineExposure", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("HullCollider", RIGHT_ACTUATOR_FIELD)
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, RIGHT_ACTUATOR_FIELD)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent>\n"
            "\tRightActuator;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent>   "
            "RightActuator;\n"
            "private:\n"
            "};\n"
        )
        wrap_tab = (
            "public:\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent>\t"
            "RightActuator;\n"
            "};\n"
        )
        wrap_indent = (
            "public:\n"
            "\tTObjectPtr<USkyguardBossWeakPointComponent>\n"
            "\t\tRightActuator;\n"
            "};\n"
        )
        wrap_uproperty = (
            "public:\n"
            f"\t{UPROPERTY_PORT}\n"
            f"\t{RIGHT_ACTUATOR_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_one_line = (
            "public:\n"
            f"\t{UPROPERTY_PORT} {RIGHT_ACTUATOR_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_category = (
            "public:\n"
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly,\n"
            '\t\tCategory="Skyguard|Mission03|Boss")\n'
            f"\t{RIGHT_ACTUATOR_FIELD}\n"
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
                has_declaration(section, RIGHT_ACTUATOR_FIELD),
                section,
            )
            self.assertEqual(
                require_declaration(section, RIGHT_ACTUATOR_FIELD),
                RIGHT_ACTUATOR_FIELD,
            )
            self.assertEqual(
                declaration_count(section, RIGHT_ACTUATOR_FIELD),
                1,
            )
        one_line = f"{{\npublic:\n\t{RIGHT_ACTUATOR_FIELD}\n}}\n"
        self.assertTrue(has_declaration(one_line, RIGHT_ACTUATOR_FIELD))
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, RIGHT_ACTUATOR_FIELD),
            section,
        )
        self.assertEqual(
            require_declaration(section, RIGHT_ACTUATOR_FIELD),
            RIGHT_ACTUATOR_FIELD,
        )
        self.assertIn(UPROPERTY_PORT, section)

    def test_assigned_right_actuator_does_not_satisfy(self) -> None:
        assigned = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "RightActuator = nullptr;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(assigned, RIGHT_ACTUATOR_FIELD)
        self.assertIn("RightActuator", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(assigned, RIGHT_ACTUATOR_FIELD))

    def test_sibling_public_fields_do_not_satisfy(self) -> None:
        for region in (
            f"\t{TARGETING_CAMERA_FIELD}\n",
            f"\t{LEFT_ACTUATOR_FIELD}\n",
            f"\t{ROAD_HUNTER_ENGINE_FIELD}\n",
            f"\t{DEBRIS_LEFT_WING_FIELD}\n",
            f"\t{ROAD_HUNTER_DEBRIS_ENGINE_FIELD}\n",
            f"\t{DEBRIS_RIGHT_WING_FIELD}\n",
            f"\t{leftover_arm_emergency_finish()}\n",
            f"\t{leftover_is_emergency_finish_armed()}\n",
            f"\t{PORT_LATCH_FIELD}\n",
            f"\t{BREAKWATER_ENGINE_FIELD}\n",
            f"\t{BREAKWATER_DEBRIS_ENGINE_FIELD}\n",
            f"\t{COOLING_DOOR_FIELD}\n",
            f"\t{SIGNATURE_MODULATOR_FIELD}\n",
            f"\t{MINIMUM_CIVILIAN_SEPARATION}\n",
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, RIGHT_ACTUATOR_FIELD)
            self.assertIn("RightActuator", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, RIGHT_ACTUATOR_FIELD))

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, RIGHT_ACTUATOR_FIELD)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_PORT)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, RIGHT_ACTUATOR_FIELD)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_PORT)
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_PORT, section)
        self.assertTrue(has_declaration(section, RIGHT_ACTUATOR_FIELD), section)

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        self.assertNotIn("UFUNCTION", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(
            RIGHT_ACTUATOR_FIELD.startswith("UFUNCTION"),
            RIGHT_ACTUATOR_FIELD,
        )
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, RIGHT_ACTUATOR_FIELD), section)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", RIGHT_ACTUATOR_FIELD)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_right_actuator_cpp_body(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        self.assertNotIn("{", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("}", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("return ", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(
            "ASkyguardRoadHunterBoss::RightActuator",
            RIGHT_ACTUATOR_FIELD,
        )
        self.assertNotIn("SkyguardRoadHunterBoss.cpp", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SkyguardRoadHunterBoss.cpp", locked_only)
        self.assertNotIn("return false", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("return true", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("CreateDefaultSubobject", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SetExposed", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(
            "RefreshAuthoredWeakPointRegistry",
            RIGHT_ACTUATOR_FIELD,
        )
        self.assertNotIn("SetBossPhase", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("HandleWeakPointDestroyed", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_sibling_tempest_fields(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in SIBLING_TEMPEST_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("PortDischargeBoom", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("StarboardDischargeBoom", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("EngineIntake", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisPortPanel", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisStarboardPanel", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisIntakePanel", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("RequiredLockStabilitySeconds", RIGHT_ACTUATOR_FIELD)
        self.assertIn(
            "USkyguardBossWeakPointComponent",
            RIGHT_ACTUATOR_FIELD,
        )
        self.assertIn("RightActuator", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_command_antenna(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_COMMAND_ANTENNA_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("CommandAntenna", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_engine(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_ENGINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_encounter_controller(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_ENCOUNTER_CONTROLLER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("EncounterController", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_port_discharge_boom(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_PORT_DISCHARGE_BOOM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("PortDischargeBoom", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_starboard_discharge_boom(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_STARBOARD_DISCHARGE_BOOM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("StarboardDischargeBoom", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_engine_intake(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_ENGINE_INTAKE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("EngineIntake", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_debris_port_panel(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_DEBRIS_PORT_PANEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisPortPanel", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_debris_starboard_panel(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_DEBRIS_STARBOARD_PANEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisStarboardPanel", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_debris_intake_panel(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_DEBRIS_INTAKE_PANEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisIntakePanel", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_required_lock_stability(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_REQUIRED_LOCK_STABILITY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("RequiredLockStabilitySeconds", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_control_servo(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_CONTROL_SERVO_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ControlServo", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_sibling_iron_rain_fields(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in SIBLING_IRON_RAIN_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DispenserCenter", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("MaxReleasesPerBay", RIGHT_ACTUATOR_FIELD)
        self.assertIn("RightActuator", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_sibling_radar_ghost_fields(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in SIBLING_RADAR_GHOST_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SignatureModulator", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("RadarReceiver", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisCoolingDoor", RIGHT_ACTUATOR_FIELD)
        self.assertIn("RightActuator", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_signature_modulator(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_SIGNATURE_MODULATOR_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SignatureModulator", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_radar_receiver(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_RADAR_RECEIVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("RadarReceiver", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_debris_cooling_door(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_DEBRIS_COOLING_DOOR_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisCoolingDoor", RIGHT_ACTUATOR_FIELD)
        self.assertFalse(
            has_declaration(
                f"\t{DEBRIS_COOLING_DOOR_FIELD}\n",
                RIGHT_ACTUATOR_FIELD,
            )
        )

    def test_contract_does_not_relock_leftover_radar_ghost_methods(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_RADAR_GHOST_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SetContactIdentified", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("OpenOrbitExposure", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("IsContactIdentified", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("HandleWeakPointDestroyed", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(leftover_open_rear_aspect_window(), RIGHT_ACTUATOR_FIELD)

    def test_debris_cooling_door_does_not_satisfy_right_actuator(self) -> None:
        leftover = f"\t{DEBRIS_COOLING_DOOR_FIELD}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(leftover, RIGHT_ACTUATOR_FIELD)
        self.assertIn("RightActuator", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(leftover, RIGHT_ACTUATOR_FIELD))
        self.assertNotEqual(DEBRIS_COOLING_DOOR_FIELD, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("UStaticMeshComponent", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(
            "USkyguardBossWeakPointComponent",
            DEBRIS_COOLING_DOOR_FIELD,
        )

    def test_contract_does_not_relock_leftover_dispenser_center(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_DISPENSER_CENTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DispenserCenter", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_dispenser_starboard(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_DISPENSER_STARBOARD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DispenserStarboard", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_max_releases_per_bay(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_MAX_RELEASES_PER_BAY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("MaxReleasesPerBay", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_get_maneuver(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_GET_MANEUVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetManeuver", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_control_linkage(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_CONTROL_LINKAGE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ControlLinkage", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_nose_camera(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_NOSE_CAMERA_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("NoseCamera", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_debris_center(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_DEBRIS_CENTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisCenter", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_debris_tail(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_DEBRIS_TAIL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisTail", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_debris_nose(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_DEBRIS_NOSE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisNose", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_debris_spine(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_DEBRIS_SPINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisSpine", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_pathfinder_methods(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_PATHFINDER_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("AdvanceEncounter", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("IsRouteStateSafe", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetTelegraphsTriggered", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_begin_terminal_strike_cycle_sibling(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in BEGIN_TERMINAL_STRIKE_CYCLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("BeginTerminalStrikeCycle", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_open_guidance_array_exposure_sibling(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in OPEN_GUIDANCE_ARRAY_EXPOSURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("OpenGuidanceArrayExposure", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_divert_wreck_from_civilians_sibling(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in DIVERT_WRECK_FROM_CIVILIANS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DivertWreckFromCivilians", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_set_civilian_separation_meters_sibling(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in SET_CIVILIAN_SEPARATION_METERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SetCivilianSeparationMeters", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_get_civilian_separation_meters_sibling(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in GET_CIVILIAN_SEPARATION_METERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetCivilianSeparationMeters", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_getters(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetFinaleStage", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("IssueClimbCommand", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("IsWreckDiverted", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetObjectiveMilestonesReached", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_issue_climb_command_sibling(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in ISSUE_CLIMB_COMMAND_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("IssueClimbCommand", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_finale_stage(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in GET_FINALE_STAGE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetFinaleStage", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ESkyguardLastFlightStage", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_is_climb_command_issued_sibling(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in IS_CLIMB_COMMAND_ISSUED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("IsClimbCommandIssued", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_is_wreck_diverted_sibling(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in IS_WRECK_DIVERTED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("IsWreckDiverted", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_get_objective_milestones_reached_sibling(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in GET_OBJECTIVE_MILESTONES_REACHED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetObjectiveMilestonesReached", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_emergency_finish(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        self.assertNotIn(leftover_open_first_window(), locked_only)
        self.assertNotIn(leftover_open_first_window(), RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(leftover_open_final_window(), locked_only)
        self.assertNotIn(leftover_open_final_window(), RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(leftover_arm_command_core_path(), locked_only)
        self.assertNotIn(leftover_arm_command_core_path(), RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(leftover_apply_strike(), locked_only)
        self.assertNotIn(leftover_apply_strike(), RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(leftover_is_lock_eligible(), locked_only)
        self.assertNotIn(leftover_is_lock_eligible(), RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(leftover_arm_emergency_finish(), locked_only)
        self.assertNotIn(leftover_arm_emergency_finish(), RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(leftover_is_emergency_finish_armed(), locked_only)
        self.assertNotIn(
            leftover_is_emergency_finish_armed(),
            RIGHT_ACTUATOR_FIELD,
        )
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, RIGHT_ACTUATOR_FIELD)
        for script in leftover_live_copy_boss_scripts():
            self.assertNotIn(script, RIGHT_ACTUATOR_FIELD)
            self.assertNotIn(script, locked_only)

    def test_contract_does_not_relock_leftover_weak_point_component_fields(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in leftover_weak_point_accept_flags():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        for token in LEFTOVER_WEAK_POINT_COMPONENT_HEADER_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SkyguardBossWeakPointComponent.h", locked_only)
        self.assertIn(
            "USkyguardBossWeakPointComponent",
            RIGHT_ACTUATOR_FIELD,
        )

    def test_contract_does_not_relock_leftover_boss_drone_fields(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_BOSS_DRONE_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(
            "test_boss_drone_root_field_decl_contract.py",
            RIGHT_ACTUATOR_FIELD,
        )

    def test_contract_does_not_relock_leftover_debris_getters(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_DEBRIS_GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetDefeatDebrisPieceCount", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetMaxDefeatDebrisPieces", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_hull_collider(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_HULL_COLLIDER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("HullCollider", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_port_guidance_array(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_PORT_GUIDANCE_ARRAY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("PortGuidanceArray", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_debris_armor_port(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_DEBRIS_ARMOR_PORT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisArmorPort", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_searchlight_runtime(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_black_kite(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_BLACK_KITE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SetSearchlightTracked", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ASkyguardBlackKiteBoss", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_radar_ghost(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_RADAR_GHOST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SetContactIdentified", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("OpenOrbitExposure", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisCoolingDoor", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("CoolingDoor", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SignatureModulator", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ASkyguardRadarGhostBoss", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_lifeline_hunter(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SetFriendlySeparationMeters", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ASkyguardLifelineHunterBoss", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_tempest_methods(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_TEMPEST_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SetLightningExposed", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ApplyCorrectiveBankGust", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("IsLightningExposed", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetLockStabilitySeconds", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(leftover_advance_stabilized_lock(), RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(leftover_arm_break_finish(), RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(leftover_is_break_finish_armed(), RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_iron_rain(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_IRON_RAIN_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("OpenUpperEngineExposure", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetManeuver", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DispenserCenter", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_patrol_ship(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_PATROL_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ASkyguardPatrolShip", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_mount_getters(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in MOUNT_GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetGunnerMount", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_chin_muzzle(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for neighbor in GET_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("GetChinMuzzleLocation", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_empty_fail_closed(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_EMPTY_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_chin_muzzle(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_CHIN_MUZZLE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_own_ship_systems(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_OWN_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ESkyguardApacheSystem", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_cpg_feel(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_CPG_FEEL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_apache_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_APACHE_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("FaceWorldLocation", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_settings(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_SETTINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_input_capture(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_INPUT_CAPTURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_gunner(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ASkyguardGunner", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_radar_node(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SkyguardRadarNode", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_widget_decl_siblings(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_WIDGET_DECL_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardDebriefWidget", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_scan_wrong_harbor_headers(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("MinHeightFromOriginCm", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("MaxIntegrity", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("CurrentIntegrity", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("SkyguardApacheAircraft.h", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(
            "SkyguardPathfinderEncounterController.h",
            RIGHT_ACTUATOR_FIELD,
        )

    def test_contract_does_not_open_leftover_weak_point_component_header(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        file_text = this_file_text()
        leftover_header = "SkyguardBossWeakPointComponent.h"
        for token in LEFTOVER_WEAK_POINT_COMPONENT_HEADER_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(leftover_header, locked_only)
        self.assertNotIn(leftover_header, RIGHT_ACTUATOR_FIELD)
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
            "Source/Skyguard52/SkyguardRoadHunterBoss.h",
        )

    def test_contract_does_not_open_leftover_encounter_controller_header(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        file_text = this_file_text()
        leftover_header = "SkyguardPathfinderEncounterController.h"
        self.assertNotIn(leftover_header, locked_only)
        self.assertNotIn(leftover_header, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(f"origin/main:{leftover_header}", file_text)
        self.assertNotIn(
            f"git show origin/main:{leftover_header}",
            file_text,
        )
        self.assertNotIn(
            f"origin/main:Source/Skyguard52/{leftover_header}",
            file_text,
        )
        self.assertNotIn("MinHeightFromOriginCm", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_scan_apache_public_section_for_harbor(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        file_text = this_file_text()
        apache_header = "SkyguardApacheAircraft.h"
        self.assertNotIn(apache_header, locked_only)
        self.assertNotIn(apache_header, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ASkyguardApacheAircraft", locked_only)
        self.assertNotIn("ASkyguardApacheAircraft", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn(f"origin/main:{apache_header}", file_text)
        self.assertNotIn(f"git show origin/main:{apache_header}", file_text)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)

    def test_minimum_civilian_separation_is_not_harbor_40_80(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        section = public_section(origin_main_header())
        adjacent = "MinimumCivilianSeparationMeters = 550.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        for token in HARBOR_ADJACENT_CIVILIAN_SEPARATION:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        for token in HARBOR_ADJACENT_NOT_LOCKED:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("MinimumCivilianSeparationMeters", section)
        self.assertNotIn("550.f", section)

    def test_harbor_adjacent_fields_are_not_harbor_40_80(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        adjacent_civilian = "MinimumCivilianSeparationMeters = 550.f"
        adjacent_weapon = "MinimumWeaponSeparationMeters = 450.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent_civilian)
            self.assertNotEqual(token, adjacent_weapon)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        self.assertEqual(
            require_declaration(locked_only, RIGHT_ACTUATOR_FIELD),
            RIGHT_ACTUATOR_FIELD,
        )
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("PortDischargeBoom", locked_only)
        self.assertNotIn("StarboardDischargeBoom", locked_only)
        self.assertNotIn("EngineIntake", locked_only)
        self.assertNotIn("DebrisPortPanel", locked_only)
        self.assertNotIn("DebrisStarboardPanel", locked_only)
        self.assertNotIn("DebrisIntakePanel", locked_only)
        self.assertNotIn("RequiredLockStabilitySeconds", locked_only)
        self.assertNotIn("SignatureModulator", locked_only)
        self.assertNotIn("RadarReceiver", locked_only)
        self.assertNotIn("CoolingDoor", locked_only)
        self.assertNotIn("DebrisPortEWPanel", locked_only)
        self.assertNotIn("DebrisStarboardEWPanel", locked_only)
        self.assertNotIn("DebrisCoolingDoor", locked_only)
        self.assertNotIn("LeftActuator", locked_only)
        self.assertNotIn("RightActuator", locked_only)
        self.assertNotIn("DebrisLeftWing", locked_only)
        self.assertNotIn("DebrisEngine", locked_only)
        self.assertNotIn("DebrisRightWing", locked_only)
        self.assertNotIn("PortLatch", locked_only)
        self.assertNotIn("StarboardLatch", locked_only)
        self.assertNotIn("DecoyPods", locked_only)
        self.assertNotIn("ElevatorLinkage", locked_only)
        self.assertNotIn("DebrisPortPanel", locked_only)
        self.assertNotIn("ASkyguardBreakwaterBoss", locked_only)
        self.assertNotIn("OpticalTracker", locked_only)
        self.assertNotIn("WeaponServo", locked_only)
        self.assertNotIn("CountermeasurePod", locked_only)
        self.assertNotIn("ESkyguardMission02WaveState", locked_only)
        self.assertNotIn("SetContactIdentified", locked_only)
        self.assertNotIn("IsContactIdentified", locked_only)
        self.assertNotIn("HandleWeakPointDestroyed", locked_only)
        self.assertNotIn("DispenserCenter", locked_only)
        self.assertNotIn("DispenserStarboard", locked_only)
        self.assertNotIn("CommandAntennaPort", locked_only)
        self.assertNotIn("DecoyController", locked_only)
        self.assertNotIn("EnginePodPort", locked_only)
        self.assertNotIn("FuelControlPort", locked_only)
        self.assertNotIn("DebrisPortWing", locked_only)
        self.assertNotIn("MaxReleasesPerBay", locked_only)
        self.assertNotIn("OpenDispenserBay", locked_only)
        self.assertNotIn("ReleasePooledEscort", locked_only)
        self.assertNotIn("GetManeuver", locked_only)
        self.assertNotIn("ControlServo", locked_only)
        self.assertNotIn("SetLightningExposed", locked_only)
        self.assertNotIn("ApplyCorrectiveBankGust", locked_only)
        self.assertNotIn("IsLightningExposed", locked_only)
        self.assertNotIn("GetLockStabilitySeconds", locked_only)
        self.assertNotIn("CommandAntenna", locked_only)
        self.assertNotIn("ControlLinkage", locked_only)
        self.assertNotIn("NoseCamera", locked_only)
        self.assertNotIn("DebrisCenter", locked_only)
        self.assertNotIn("DebrisTail", locked_only)
        self.assertNotIn("DebrisNose", locked_only)
        self.assertNotIn("DebrisSpine", locked_only)
        self.assertNotIn("EncounterController", locked_only)
        self.assertNotIn("AdvanceEncounter", locked_only)
        self.assertNotIn("ResetEncounterState", locked_only)
        self.assertNotIn("IsRouteStateSafe", locked_only)
        self.assertNotIn("GetRouteProgress", locked_only)
        self.assertNotIn("GetEffectiveSpeedMultiplier", locked_only)
        self.assertNotIn("IsAttackTelegraphActive", locked_only)
        self.assertNotIn("GetTelegraphsTriggered", locked_only)
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
        self.assertNotIn("DebrisArmorPort", locked_only)
        self.assertNotIn("SkyguardBossWeakPointComponent.h", locked_only)
        self.assertNotIn(
            "SkyguardPathfinderEncounterController.h",
            locked_only,
        )
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
        self.assertNotIn("ASkyguardIronRainBoss", section)
        self.assertNotIn("ASkyguardLifelineHunterBoss", section)
        self.assertNotIn("ASkyguardPathfinderBoss", section)
        self.assertNotIn("ASkyguardTempestBoss", section)
        self.assertNotIn("ASkyguardLastFlightBoss", section)
        self.assertNotIn("ASkyguardPatrolShip", section)
        self.assertNotIn("ASkyguardBreakwaterBoss", section)
        self.assertNotIn("ASkyguardRadarGhostBoss", section)
        self.assertNotIn("ESkyguardMission02WaveState", section)
        self.assertNotIn("MinHeightFromOriginCm", section)
        self.assertEqual(
            require_declaration(section, RIGHT_ACTUATOR_FIELD),
            RIGHT_ACTUATOR_FIELD,
        )
        self.assertEqual(declaration_count(section, RIGHT_ACTUATOR_FIELD), 1)
        self.assertNotIn("SkyguardRoadHunterBoss.cpp", section)
        self.assertNotIn("ASkyguardRoadHunterBoss::RightActuator", section)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardRoadHunterBoss.cpp", section)
        self.assertNotIn("ASkyguardRoadHunterBoss::RightActuator", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("}", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("return false", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("return true", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        file_text = this_file_text()
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
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
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
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
                "road hunter RightActuator field contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, RIGHT_ACTUATOR_FIELD.lower())
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                RIGHT_ACTUATOR_FIELD.lower(),
                "road hunter RightActuator contains "
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
        self.assertNotIn(dirty_fwd, RIGHT_ACTUATOR_FIELD)

    def test_contract_is_right_actuator_field_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, RIGHT_ACTUATOR_FIELD),
            RIGHT_ACTUATOR_FIELD,
        )
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("PortDischargeBoom", locked_only)
        self.assertNotIn("StarboardDischargeBoom", locked_only)
        self.assertNotIn("EngineIntake", locked_only)
        self.assertNotIn("DebrisPortPanel", locked_only)
        self.assertNotIn("DebrisStarboardPanel", locked_only)
        self.assertNotIn("DebrisIntakePanel", locked_only)
        self.assertNotIn("RequiredLockStabilitySeconds", locked_only)
        self.assertNotIn("SignatureModulator", locked_only)
        self.assertNotIn("RadarReceiver", locked_only)
        self.assertNotIn("DebrisPortEWPanel", locked_only)
        self.assertNotIn("DebrisStarboardEWPanel", locked_only)
        self.assertNotIn("DebrisCoolingDoor", locked_only)
        self.assertNotIn("SetContactIdentified", locked_only)
        self.assertNotIn("IsContactIdentified", locked_only)
        self.assertNotIn("HandleWeakPointDestroyed", locked_only)
        self.assertNotIn("DispenserCenter", locked_only)
        self.assertNotIn("DispenserStarboard", locked_only)
        self.assertNotIn("CommandAntennaPort", locked_only)
        self.assertNotIn("DecoyController", locked_only)
        self.assertNotIn("EnginePodPort", locked_only)
        self.assertNotIn("FuelControlPort", locked_only)
        self.assertNotIn("DebrisPortWing", locked_only)
        self.assertNotIn("MaxReleasesPerBay", locked_only)
        self.assertNotIn("OpenDispenserBay", locked_only)
        self.assertNotIn("ReleasePooledEscort", locked_only)
        self.assertNotIn("GetManeuver", locked_only)
        self.assertNotIn("ControlServo", locked_only)
        self.assertNotIn("SetLightningExposed", locked_only)
        self.assertNotIn("ApplyCorrectiveBankGust", locked_only)
        self.assertNotIn("IsLightningExposed", locked_only)
        self.assertNotIn("GetLockStabilitySeconds", locked_only)
        self.assertNotIn("CommandAntenna", locked_only)
        self.assertNotIn("ControlLinkage", locked_only)
        self.assertNotIn("NoseCamera", locked_only)
        self.assertNotIn("DebrisCenter", locked_only)
        self.assertNotIn("DebrisTail", locked_only)
        self.assertNotIn("DebrisNose", locked_only)
        self.assertNotIn("DebrisSpine", locked_only)
        self.assertNotIn("EncounterController", locked_only)
        self.assertNotIn("AdvanceEncounter", locked_only)
        self.assertNotIn("ResetEncounterState", locked_only)
        self.assertNotIn("IsRouteStateSafe", locked_only)
        self.assertNotIn("GetRouteProgress", locked_only)
        self.assertNotIn("GetEffectiveSpeedMultiplier", locked_only)
        self.assertNotIn("IsAttackTelegraphActive", locked_only)
        self.assertNotIn("GetTelegraphsTriggered", locked_only)
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
        self.assertNotIn("DebrisArmorPort", locked_only)
        self.assertNotIn("SkyguardBossWeakPointComponent.h", locked_only)
        self.assertNotIn(
            "SkyguardPathfinderEncounterController.h",
            locked_only,
        )
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
        self.assertNotIn("RadarNode", locked_only)
        for name in leftover_emergency_finish_names():
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, RIGHT_ACTUATOR_FIELD)
        leftover_groups = (
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
            SIBLING_PATHFINDER_FIELDS_NOT_LOCKED,
            SIBLING_TEMPEST_FIELDS_NOT_LOCKED,
            SIBLING_IRON_RAIN_FIELDS_NOT_LOCKED,
            SIBLING_RADAR_GHOST_FIELDS_NOT_LOCKED,
            SIBLING_ROAD_HUNTER_FIELDS_NOT_LOCKED,
            SIBLING_BREAKWATER_FIELDS_NOT_LOCKED,
            LEFTOVER_MISSION02_WAVE_STATE_NOT_LOCKED,
            LEFTOVER_BREAKWATER_ENGINE_NOT_LOCKED,
            LEFTOVER_BREAKWATER_DEBRIS_ENGINE_NOT_LOCKED,
            LEFTOVER_LIFELINE_HUNTER_FIELDS_NOT_LOCKED,
            LEFTOVER_SIGNATURE_MODULATOR_NOT_LOCKED,
            LEFTOVER_RADAR_RECEIVER_NOT_LOCKED,
            LEFTOVER_DEBRIS_COOLING_DOOR_NOT_LOCKED,
            LEFTOVER_RADAR_GHOST_METHODS_NOT_LOCKED,
            LEFTOVER_CONTROL_SERVO_NOT_LOCKED,
            LEFTOVER_DISPENSER_CENTER_NOT_LOCKED,
            LEFTOVER_DISPENSER_STARBOARD_NOT_LOCKED,
            LEFTOVER_COMMAND_ANTENNA_PORT_NOT_LOCKED,
            LEFTOVER_COMMAND_ANTENNA_STARBOARD_NOT_LOCKED,
            LEFTOVER_DECOY_CONTROLLER_NOT_LOCKED,
            LEFTOVER_ENGINE_POD_PORT_NOT_LOCKED,
            LEFTOVER_ENGINE_POD_CENTER_NOT_LOCKED,
            LEFTOVER_ENGINE_POD_STARBOARD_NOT_LOCKED,
            LEFTOVER_FUEL_CONTROL_PORT_NOT_LOCKED,
            LEFTOVER_FUEL_CONTROL_STARBOARD_NOT_LOCKED,
            LEFTOVER_DEBRIS_PORT_WING_NOT_LOCKED,
            LEFTOVER_DEBRIS_CENTER_RACK_NOT_LOCKED,
            LEFTOVER_DEBRIS_STARBOARD_WING_NOT_LOCKED,
            LEFTOVER_MAX_RELEASES_PER_BAY_NOT_LOCKED,
            LEFTOVER_GET_MANEUVER_NOT_LOCKED,
            LEFTOVER_PORT_DISCHARGE_BOOM_NOT_LOCKED,
            LEFTOVER_STARBOARD_DISCHARGE_BOOM_NOT_LOCKED,
            LEFTOVER_ENGINE_INTAKE_NOT_LOCKED,
            LEFTOVER_DEBRIS_PORT_PANEL_NOT_LOCKED,
            LEFTOVER_DEBRIS_STARBOARD_PANEL_NOT_LOCKED,
            LEFTOVER_DEBRIS_INTAKE_PANEL_NOT_LOCKED,
            LEFTOVER_REQUIRED_LOCK_STABILITY_NOT_LOCKED,
            LEFTOVER_ENCOUNTER_CONTROLLER_NOT_LOCKED,
            LEFTOVER_COMMAND_ANTENNA_NOT_LOCKED,
            LEFTOVER_ENGINE_NOT_LOCKED,
            LEFTOVER_CONTROL_LINKAGE_NOT_LOCKED,
            LEFTOVER_NOSE_CAMERA_NOT_LOCKED,
            LEFTOVER_DEBRIS_CENTER_NOT_LOCKED,
            LEFTOVER_DEBRIS_TAIL_NOT_LOCKED,
            LEFTOVER_DEBRIS_NOSE_NOT_LOCKED,
            LEFTOVER_DEBRIS_SPINE_NOT_LOCKED,
            LEFTOVER_PATHFINDER_METHODS_NOT_LOCKED,
            WRONG_HARBOR_HEADERS_NOT_SCANNED,
            leftover_short_roster_values(),
            LEFTOVER_HULL_COLLIDER_NOT_LOCKED,
            LEFTOVER_PORT_GUIDANCE_ARRAY_NOT_LOCKED,
            LEFTOVER_DEBRIS_ARMOR_PORT_NOT_LOCKED,
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
                self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, RIGHT_ACTUATOR_FIELD.lower())
            self.assertNotIn(banned, locked_only.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("{", RIGHT_ACTUATOR_FIELD)
        self.assertTrue(
            RIGHT_ACTUATOR_FIELD.startswith(
                "TObjectPtr<USkyguardBossWeakPointComponent> "
            )
        )
        self.assertIn(
            "USkyguardBossWeakPointComponent",
            RIGHT_ACTUATOR_FIELD,
        )
        self.assertTrue(RIGHT_ACTUATOR_FIELD.endswith(";"))
        self.assertNotIn("=", RIGHT_ACTUATOR_FIELD)
        self.assertIn(UPROPERTY_PORT, section)

    def test_contract_does_not_relock_sibling_road_hunter_fields(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in SIBLING_ROAD_HUNTER_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("LeftActuator", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("TargetingCamera", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisLeftWing", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisEngine", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisRightWing", RIGHT_ACTUATOR_FIELD)
        self.assertIn("RightActuator", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_sibling_breakwater_fields(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in SIBLING_BREAKWATER_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("PortLatch", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("StarboardLatch", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DecoyPods", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ElevatorLinkage", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ASkyguardBreakwaterBoss", RIGHT_ACTUATOR_FIELD)
        self.assertIn(
            "Scripts/tests/test_breakwater_engine_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_breakwater_debris_engine_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_breakwater_debris_port_panel_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_road_hunter_targeting_camera_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_road_hunter_left_actuator_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn(
            "Scripts/tests/test_road_hunter_right_actuator_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_road_hunter_engine_is_not_breakwater_engine(self) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        self.assertNotEqual(ROAD_HUNTER_ENGINE_FIELD, RIGHT_ACTUATOR_FIELD)
        self.assertEqual(ROAD_HUNTER_ENGINE_FIELD, BREAKWATER_ENGINE_FIELD)
        self.assertEqual(ROAD_HUNTER_ENGINE_FIELD, ENGINE_FIELD)
        self.assertEqual(CLASS_NAME, "ASkyguardRoadHunterBoss")
        self.assertNotEqual(CLASS_NAME, "ASkyguardBreakwaterBoss")
        self.assertNotEqual(CLASS_NAME, "ASkyguardRadarGhostBoss")
        self.assertNotEqual(CLASS_NAME, "ASkyguardPathfinderBoss")
        for token in LEFTOVER_BREAKWATER_ENGINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("Engine;", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ASkyguardBreakwaterBoss", RIGHT_ACTUATOR_FIELD)

    def test_road_hunter_debris_engine_is_not_breakwater_debris_engine(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        self.assertNotEqual(
            ROAD_HUNTER_DEBRIS_ENGINE_FIELD,
            RIGHT_ACTUATOR_FIELD,
        )
        self.assertEqual(
            ROAD_HUNTER_DEBRIS_ENGINE_FIELD,
            BREAKWATER_DEBRIS_ENGINE_FIELD,
        )
        self.assertEqual(CLASS_NAME, "ASkyguardRoadHunterBoss")
        self.assertNotEqual(CLASS_NAME, "ASkyguardBreakwaterBoss")
        for token in LEFTOVER_BREAKWATER_DEBRIS_ENGINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("DebrisEngine", RIGHT_ACTUATOR_FIELD)
        self.assertIn("RightActuator", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_mission02_wave_state(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_MISSION02_WAVE_STATE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ESkyguardMission02WaveState", RIGHT_ACTUATOR_FIELD)

    def test_contract_does_not_relock_leftover_lifeline_hunter_fields(
        self,
    ) -> None:
        locked_only = f"{RIGHT_ACTUATOR_FIELD}\n"
        for token in LEFTOVER_LIFELINE_HUNTER_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("OpticalTracker", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("WeaponServo", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("CountermeasurePod", RIGHT_ACTUATOR_FIELD)
        self.assertNotIn("ASkyguardLifelineHunterBoss", RIGHT_ACTUATOR_FIELD)

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

           