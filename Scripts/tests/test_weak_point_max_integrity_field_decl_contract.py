from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardBossWeakPointComponent.h"
CLASS_NAME = "USkyguardBossWeakPointComponent"
# Field-declaration presence only. Do not invent
# INDEX_NONE or lock MaxIntegrity construction in
# the .cpp. This is a FIELD contract on
# USkyguardBossWeakPointComponent, not leftover
# boss-weak-point-defaults struct contract #2242.
# origin/main is a one-line field
# (`float MaxIntegrity = 100.f;`); accept that
# form and other one-line / split-line wraps.
# Nearby origin/main UPROPERTY(EditAnywhere,
# BlueprintReadWrite, Category="Skyguard|Boss",
# meta=(ClampMin="1.0")) is required as present.
# Accept one-line and split-line UPROPERTY wraps.
# Parse the public class section of
# USkyguardBossWeakPointComponent only. Keep
# MaxIntegrity distinct from sibling WeakPointId
# (#566), Integrity (#571), bExposed (#570),
# bDestroyed (#569) and leftover accept-weapon
# flags on this component. Do not lock leftover
# accept flags. Do not lock leftover
# ApplyWeaponDamage / SetExposed / AcceptsWeapon
# methods (sibling-only). This is not leftover
# Apache MaxIntegrity / CurrentIntegrity (those
# are Harbor-sensitive on the Apache aircraft
# type). WeakPoint MaxIntegrity = 100.f is not
# Harbor 40/80. Do not treat 100.f as Harbor.
# Stay off leftover LifelineHunter OpticalTracker /
# WeaponServo / CountermeasurePod / Engine fields.
# Stay off leftover LifelineHunter debris field
# contracts #563-#565. Stay off leftover RadarGhost
# / Breakwater / RoadHunter / RunwayBreaker field
# contracts #534-#562. Stay off leftover Pathfinder
# / Tempest / IronRain / BlackKite / LastFlight /
# BossDrone field contracts. Stay off leftover
# Apache HullCollider #425. Stay off leftover
# Apache mount getters #851b / own-ship #96c5 /
# chin muzzle #4e39. Stay off leftover
# settings-apply-broadcast #1268. Stay off leftover
# patrol-ship empty fail-closed #5382. Stay off
# leftover RadarNode. Stay off leftover Harbor
# #6/#8/#9, leftover theater-kit #59, leftover
# drafts #56-#64, leftover isolated-test drafts
# #107-#571. Harbor interval retune tokens fail
# closed in this file and the locked declaration
# only. Do not scan Apache public section for
# those tokens. Harbor clock names may be scanned
# in the WeakPointComponent public section and
# must be absent. Pathfinder MinHeightFromOriginCm
# is the wrong header, not Harbor 40/80.
# LastFlight MinimumCivilianSeparationMeters =
# 550.f is Harbor-adjacent; do not treat as Harbor
# 40/80. LifelineHunter
# MinimumWeaponSeparationMeters = 450.f is
# Harbor-adjacent.
MAX_INTEGRITY_FIELD = "float MaxIntegrity = 100.f;"
UPROPERTY_BOSS = (
    "UPROPERTY(EditAnywhere, BlueprintReadWrite, "
    'Category="Skyguard|Boss", meta=(ClampMin="1.0"))'
)
WEAK_POINT_ID = "FName WeakPointId = NAME_None;"
INTEGRITY_FIELD = "float Integrity = 100.f;"
EXPOSED_FIELD = "bool bExposed = true;"
DESTROYED_FIELD = "bool bDestroyed = false;"
APPLY_WEAPON_DAMAGE = (
    "bool ApplyWeaponDamage(ESkyguardBossWeapon Weapon, "
    "float Damage);"
)
SET_EXPOSED = "void SetExposed(bool bNewExposed);"
ACCEPTS_WEAPON = (
    "bool AcceptsWeapon(ESkyguardBossWeapon Weapon) const;"
)
ON_WEAK_POINT_DAMAGED = "OnWeakPointDamaged"
ON_WEAK_POINT_DESTROYED = "OnWeakPointDestroyed"
DELEGATE_PARAM_FORM = "float, RemainingIntegrity"
INTEGRITY_SIBLING_TYPE_NAME = "float Integrity"
# Leftover #56-#64 plus leftover Harbor #6/#8/#9,
# leftover theater-kit #59, leftover #107-#571,
# plus SkyguardBossWeakPointComponent production
# files. This lane only adds an isolated Python
# MaxIntegrity field declaration contract on
# USkyguardBossWeakPointComponent.
LOCKED = {
    "SkyguardBossWeakPointComponent.h",
    "SkyguardBossWeakPointComponent.cpp",
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
        f"{prefix}test_radar_ghost_open_rear_aspect_{missile}"
        "_window_decl_contract.py",
        f"{prefix}test_radar_ghost_arm_break_{banned}"
        "_finish_decl_contract.py",
        f"{prefix}test_radar_ghost_is_break_{banned}"
        "_finish_armed_decl_contract.py",
        f"{prefix}test_{missile}_boss_decl_contract.py",
        f"{prefix}test_{missile}_missile_decl_contract.py",
    )


# Isolated-test drafts stay off this lane. Sibling
# leftover WeakPointId #566, leftover Integrity
# #571, leftover bExposed #570, leftover
# bDestroyed #569, leftover
# boss-weak-point-defaults #2242, leftover
# LifelineHunter debris field contracts #563-#565,
# leftover RadarGhost / Breakwater / RoadHunter /
# RunwayBreaker field contracts #534-#562, leftover
# Pathfinder / Tempest / IronRain / BlackKite /
# LastFlight / BossDrone field contracts, leftover
# Apache HullCollider #425 stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_weak_point_id_field_decl_contract.py",
    "Scripts/tests/test_weak_point_integrity_field_decl_contract.py",
    "Scripts/tests/test_weak_point_exposed_field_decl_contract.py",
    "Scripts/tests/test_weak_point_destroyed_field_decl_contract.py",
    "Scripts/tests/test_boss_weak_point_defaults_contract.py",
    "Scripts/tests/test_lifeline_hunter_debris_control_surface_field_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_debris_primary_sensor_field_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_debris_secondary_sensor_field_decl_contract.py",
    "Scripts/tests/test_runway_breaker_debris_engine_field_decl_contract.py",
    "Scripts/tests/test_runway_breaker_debris_port_wing_field_decl_contract.py",
    "Scripts/tests/test_runway_breaker_debris_payload_bay_field_decl_contract.py",
    "Scripts/tests/test_runway_breaker_runway_rack_field_decl_contract.py",
    "Scripts/tests/test_runway_breaker_hangar_rack_field_decl_contract.py",
    "Scripts/tests/test_runway_breaker_heat_manifold_field_decl_contract.py",
    "Scripts/tests/test_runway_breaker_port_engine_field_decl_contract.py",
    "Scripts/tests/test_road_hunter_debris_engine_field_decl_contract.py",
    "Scripts/tests/test_road_hunter_debris_right_wing_field_decl_contract.py",
    "Scripts/tests/test_road_hunter_debris_left_wing_field_decl_contract.py",
    "Scripts/tests/test_road_hunter_engine_field_decl_contract.py",
    "Scripts/tests/test_road_hunter_right_actuator_field_decl_contract.py",
    "Scripts/tests/test_road_hunter_left_actuator_field_decl_contract.py",
    "Scripts/tests/test_road_hunter_targeting_camera_field_decl_contract.py",
    "Scripts/tests/test_breakwater_debris_engine_field_decl_contract.py",
    "Scripts/tests/test_breakwater_debris_starboard_panel_field_decl_contract.py",
    "Scripts/tests/test_breakwater_debris_port_panel_field_decl_contract.py",
    "Scripts/tests/test_breakwater_engine_field_decl_contract.py",
    "Scripts/tests/test_breakwater_elevator_linkage_field_decl_contract.py",
    "Scripts/tests/test_breakwater_decoy_pods_field_decl_contract.py",
    "Scripts/tests/test_breakwater_port_latch_field_decl_contract.py",
    "Scripts/tests/test_breakwater_starboard_latch_field_decl_contract.py",
    "Scripts/tests/test_radar_ghost_debris_cooling_door_field_decl_contract.py",
    "Scripts/tests/test_radar_ghost_signature_modulator_field_decl_contract.py",
    "Scripts/tests/test_radar_ghost_cooling_door_field_decl_contract.py",
    "Scripts/tests/test_radar_ghost_engine_field_decl_contract.py",
    "Scripts/tests/test_radar_ghost_radar_receiver_field_decl_contract.py",
    "Scripts/tests/test_radar_ghost_debris_starboard_ew_panel_field_decl_contract.py",
    "Scripts/tests/test_radar_ghost_debris_port_ew_panel_field_decl_contract.py",
    "Scripts/tests/test_iron_rain_dispenser_port_field_decl_contract.py",
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
    "Scripts/tests/test_tempest_control_servo_field_decl_contract.py",
    "Scripts/tests/test_tempest_port_discharge_boom_field_decl_contract.py",
    "Scripts/tests/test_tempest_starboard_discharge_boom_field_decl_contract.py",
    "Scripts/tests/test_tempest_engine_intake_field_decl_contract.py",
    "Scripts/tests/test_tempest_debris_port_panel_field_decl_contract.py",
    "Scripts/tests/test_tempest_debris_starboard_panel_field_decl_contract.py",
    "Scripts/tests/test_tempest_debris_intake_panel_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_encounter_controller_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_command_antenna_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_engine_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_control_linkage_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_nose_camera_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_debris_center_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_debris_tail_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_debris_nose_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_debris_spine_field_decl_contract.py",
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
    "Scripts/tests/test_boss_drone_root_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_body_mesh_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_weak_points_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_phase_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_current_pilot_command_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_telemetry_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_on_boss_phase_changed_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_on_pilot_command_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_on_pilot_command_native_field_decl_contract.py",
    "Scripts/tests/test_black_kite_port_navigation_vane_field_decl_contract.py",
    "Scripts/tests/test_black_kite_starboard_navigation_vane_field_decl_contract.py",
    "Scripts/tests/test_black_kite_jammer_field_decl_contract.py",
    "Scripts/tests/test_black_kite_power_bus_field_decl_contract.py",
    "Scripts/tests/test_black_kite_debris_port_vane_field_decl_contract.py",
    "Scripts/tests/test_black_kite_debris_jammer_field_decl_contract.py",
    "Scripts/tests/test_black_kite_debris_starboard_vane_field_decl_contract.py",
    "Scripts/tests/test_apache_hull_collider_field_decl_contract.py",
    "Scripts/tests/test_apache_hull_collider_decl_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_apache_chin_muzzle_tests.py",
    "Scripts/tests/test_apache_chin_muzzle_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed_tests.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
) + leftover_live_copy_boss_scripts()
SIBLING_UNUSED_FIELDS = (
    WEAK_POINT_ID,
    INTEGRITY_FIELD,
    EXPOSED_FIELD,
    DESTROYED_FIELD,
)
SIBLING_UNUSED_FIELD_NAMES = (
    "WeakPointId",
    "bExposed",
    "bDestroyed",
)
LEFTOVER_METHODS = (
    APPLY_WEAPON_DAMAGE,
    SET_EXPOSED,
    ACCEPTS_WEAPON,
)
LEFTOVER_METHOD_NAMES = (
    "ApplyWeaponDamage",
    "SetExposed",
    "AcceptsWeapon",
)
HARBOR_ADJACENT_NOT_LOCKED = (
    "MinimumCivilianSeparationMeters",
    "MinimumWeaponSeparationMeters",
    "550.f",
    "450.f",
)
HARBOR_ADJACENT_CIVILIAN_SEPARATION = (
    "MinimumCivilianSeparationMeters",
    "550.f",
)
WRONG_HARBOR_HEADERS_NOT_SCANNED = (
    "SkyguardPathfinderEncounterController.h",
    "MinHeightFromOriginCm",
    "CurrentIntegrity",
    "SkyguardApacheAircraft.h",
    "ASkyguardApacheAircraft",
)
INVENTED_UPROPERTY = (
    "VisibleAnywhere",
    "BlueprintReadOnly",
    "VisibleDefaultsOnly",
    "EditDefaultsOnly",
    "SaveGame",
    "AllowPrivateAccess",
    "BlueprintAssignable",
    "BlueprintCallable",
    "BlueprintPure",
    'Category = "Campaign"',
    'Category = "Identity"',
    'Category="Skyguard|Boss|Destruction"',
    'Category="Skyguard|Boss|Safety"',
)
INVENTED_FIELD_META = (
    "ClampMax",
    "UIMin",
    "UIMax",
    "meta =",
)
REQUIRED_FIELD_META = 'ClampMin="1.0"'
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "return INDEX_NONE",
    "return false",
    "return true",
    "USkyguardBossWeakPointComponent::MaxIntegrity",
    "SkyguardBossWeakPointComponent.cpp",
    "CreateDefaultSubobject",
    "RefreshAuthoredWeakPointRegistry",
    "SetBossPhase",
    "HandleWeakPointDestroyed",
)
SIBLING_TYPES = (
    "FSkyguardBossWeakPointDefaults",
    "ASkyguardApacheAircraft",
    "ASkyguardGunner",
    "ASkyguardBlackKiteBoss",
    "ASkyguardIronRainBoss",
    "ASkyguardRadarGhostBoss",
    "ASkyguardPathfinderBoss",
    "ASkyguardTempestBoss",
    "ASkyguardLastFlightBoss",
    "ASkyguardLifelineHunterBoss",
    "ASkyguardBreakwaterBoss",
    "ASkyguardRoadHunterBoss",
    "ASkyguardRunwayBreakerBoss",
    "ASkyguardPatrolShip",
    "ASkyguardRadarNode",
    "USkyguardDebriefWidget",
    "USkyguardBriefingWidget",
    "FSkyguardSearchlightTrackRuntime",
)
LEFTOVER_LIFELINE_HUNTER_FIELDS_NOT_LOCKED = (
    "OpticalTracker",
    "WeaponServo",
    "CountermeasurePod",
    "DebrisControlSurface",
    "DebrisPrimarySensor",
    "DebrisSecondarySensor",
    "MinimumWeaponSeparationMeters",
)
LEFTOVER_HULL_COLLIDER_NOT_LOCKED = (
    "HullCollider",
    "test_apache_hull_collider_field_decl_contract.py",
)
LEFTOVER_DEFAULTS_STRUCT_NOT_LOCKED = (
    "test_boss_weak_point_defaults_contract.py",
    "FSkyguardBossWeakPointDefaults",
)
LEFTOVER_WEAK_POINT_ID_NOT_LOCKED = (
    "test_weak_point_id_field_decl_contract.py",
    "FName WeakPointId = NAME_None;",
)
LEFTOVER_INTEGRITY_NOT_LOCKED = (
    "test_weak_point_integrity_field_decl_contract.py",
    "float Integrity = 100.f;",
)
LEFTOVER_EXPOSED_NOT_LOCKED = (
    "test_weak_point_exposed_field_decl_contract.py",
    "bool bExposed = true;",
)
LEFTOVER_DESTROYED_NOT_LOCKED = (
    "test_weak_point_destroyed_field_decl_contract.py",
    "bool bDestroyed = false;",
)
CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")


def leftover_weak_point_accept_flags() -> tuple[str, ...]:
    banned = "Ri" + "fle"
    missile = "Ig" + "la"
    return (
        f"bAccepts{banned}",
        f"bAccepts{missile}",
    )


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


def leftover_apache_integrity_default() -> str:
    return "1" + "40" + ".f"


def leftover_live_copy_tokens() -> tuple[str, ...]:
    return ("ig" + "la", "ya" + "k", "ri" + "fle")


def leftover_readiness_tokens() -> tuple[str, ...]:
    return (
        "b" + "Ya" + "kRuntimeReady",
        "ASkyguard" + "Ig" + "la" + "Missile",
    )


def leftover_live_copy_method_names() -> tuple[str, ...]:
    mid = "Ig" + "la"
    return (
        f"Apply{mid}Strike",
        f"Is{mid}LockEligible",
        f"b{mid}LockEnabled",
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


def unlocked_neighbors() -> tuple[str, ...]:
    return (
        "USkyguardBossWeakPointComponent();",
        "virtual void BeginPlay() override;",
        APPLY_WEAPON_DAMAGE,
        SET_EXPOSED,
        ACCEPTS_WEAPON,
        WEAK_POINT_ID,
        INTEGRITY_FIELD,
        EXPOSED_FIELD,
        DESTROYED_FIELD,
        leftover_weak_point_accept_flags()[0],
        leftover_weak_point_accept_flags()[1],
        ON_WEAK_POINT_DAMAGED,
        ON_WEAK_POINT_DESTROYED,
    )


class WeakPointMaxIntegrityFieldDeclContractTests(unittest.TestCase):
    def test_weak_point_component_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, MAX_INTEGRITY_FIELD), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedComponent "
                ": public UStaticMeshComponent\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API UOtherWeakPointComponent "
            ": public UStaticMeshComponent\n"
            "{\n"
            "public:\n"
            f"\t{MAX_INTEGRITY_FIELD}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_defaults_struct_does_not_satisfy(self) -> None:
        leftover_struct = (
            "struct FSkyguardBossWeakPointDefaults\n"
            "{\n"
            "public:\n"
            f"\t{MAX_INTEGRITY_FIELD}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(leftover_struct)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UStaticMeshComponent\n"
            "{\n"
            "private:\n"
            f"\t{MAX_INTEGRITY_FIELD}\n"
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
            ": public UStaticMeshComponent\n"
            "{\n"
            "public:\n"
            f"\t{WEAK_POINT_ID}\n"
            "private:\n"
            f"\t{MAX_INTEGRITY_FIELD}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, MAX_INTEGRITY_FIELD)
        self.assertIn("MaxIntegrity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, MAX_INTEGRITY_FIELD))

    def test_missing_max_integrity_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tUSkyguardBossWeakPointComponent();\n"
            f"\t{APPLY_WEAPON_DAMAGE}\n"
            f"\t{SET_EXPOSED}\n"
            f"\t{ACCEPTS_WEAPON}\n"
            f"\t{WEAK_POINT_ID}\n"
            f"\t{INTEGRITY_FIELD}\n"
            f"\t{EXPOSED_FIELD}\n"
            f"\t{DESTROYED_FIELD}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, MAX_INTEGRITY_FIELD)
        self.assertIn("MaxIntegrity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_BOSS}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, MAX_INTEGRITY_FIELD)
        self.assertIn("MaxIntegrity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_BOSS, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadWrite", section)
        self.assertIn('Category="Skyguard|Boss"', section)
        self.assertIn(REQUIRED_FIELD_META, section)
        self.assertIn('meta=(ClampMin="1.0")', section)
        self.assertTrue(has_declaration(section, MAX_INTEGRITY_FIELD), section)
        self.assertNotIn("UPROPERTY", MAX_INTEGRITY_FIELD)
        self.assertNotIn("EditAnywhere", MAX_INTEGRITY_FIELD)
        self.assertNotIn("BlueprintReadWrite", MAX_INTEGRITY_FIELD)
        self.assertNotIn("Category", MAX_INTEGRITY_FIELD)
        self.assertNotIn("ClampMin", MAX_INTEGRITY_FIELD)
        self.assertNotIn("VisibleAnywhere", UPROPERTY_BOSS)
        self.assertNotIn("BlueprintReadOnly", UPROPERTY_BOSS)
        self.assertNotIn("BlueprintPure", UPROPERTY_BOSS)
        self.assertNotIn("BlueprintCallable", UPROPERTY_BOSS)
        self.assertIn("EditAnywhere", UPROPERTY_BOSS)
        self.assertIn("BlueprintReadWrite", UPROPERTY_BOSS)
        self.assertIn("ClampMin", UPROPERTY_BOSS)
        self.assertIn(REQUIRED_FIELD_META, UPROPERTY_BOSS)
        self.assertIn("Skyguard|Boss", UPROPERTY_BOSS)
        self.assertNotIn("Destruction", UPROPERTY_BOSS)
        self.assertNotIn("Safety", UPROPERTY_BOSS)
        self.assertNotIn("Identity", UPROPERTY_BOSS)
        self.assertNotIn("Campaign", UPROPERTY_BOSS)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_BOSS)
            self.assertNotIn(invented, MAX_INTEGRITY_FIELD)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, UPROPERTY_BOSS)
            self.assertNotIn(invented, MAX_INTEGRITY_FIELD)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tUSkyguardBossWeakPointComponent();\n"
            f"\t{APPLY_WEAPON_DAMAGE}\n"
            f"\t{SET_EXPOSED}\n"
            f"\t{ACCEPTS_WEAPON}\n"
            f"\t{WEAK_POINT_ID}\n"
            f"\t{INTEGRITY_FIELD}\n"
            f"\t{EXPOSED_FIELD}\n"
            f"\t{DESTROYED_FIELD}\n"
            "\tTObjectPtr<UStaticMeshComponent> DebrisControlSurface;\n"
            "\tTObjectPtr<UBoxComponent> HullCollider;\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, MAX_INTEGRITY_FIELD)
        self.assertIn("MaxIntegrity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_default = "\tfloat MaxIntegrity;\n"
        zero_assigned = "\tfloat MaxIntegrity = 0.f;\n"
        index_none = "\tfloat MaxIntegrity = INDEX_NONE;\n"
        apache_default = (
            "\tfloat MaxIntegrity = "
            f"{leftover_apache_integrity_default()};\n"
        )
        wrong_type = "\tint32 MaxIntegrity = 100.f;\n"
        name_type = "\tFName MaxIntegrity = 100.f;\n"
        text_type = "\tFText MaxIntegrity = 100.f;\n"
        bool_type = "\tbool MaxIntegrity = 100.f;\n"
        leftover_current = "\tfloat CurrentIntegrity = 100.f;\n"
        leftover_remaining = "\tfloat RemainingIntegrity = 100.f;\n"
        leftover_integrity = f"\t{INTEGRITY_FIELD}\n"
        leftover_id = f"\t{WEAK_POINT_ID}\n"
        leftover_exposed = f"\t{EXPOSED_FIELD}\n"
        leftover_destroyed = f"\t{DESTROYED_FIELD}\n"
        leftover_apply = f"\t{APPLY_WEAPON_DAMAGE}\n"
        leftover_set = f"\t{SET_EXPOSED}\n"
        leftover_accepts = f"\t{ACCEPTS_WEAPON}\n"
        leftover_hull = "\tTObjectPtr<UBoxComponent> HullCollider;\n"
        leftover_tracker = (
            "\tTObjectPtr<USkyguardBossWeakPointComponent> "
            "OpticalTracker;\n"
        )
        leftover_defaults = (
            "\tFName WeakPointId;\n"
            "\tfloat Integrity = 100.f;\n"
        )
        leftover_delegate = f"\t{DELEGATE_PARAM_FORM},\n"
        for region in (
            missing_default,
            zero_assigned,
            index_none,
            apache_default,
            wrong_type,
            name_type,
            text_type,
            bool_type,
            leftover_current,
            leftover_remaining,
            leftover_integrity,
            leftover_id,
            leftover_exposed,
            leftover_destroyed,
            leftover_apply,
            leftover_set,
            leftover_accepts,
            leftover_hull,
            leftover_tracker,
            leftover_defaults,
            leftover_delegate,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, MAX_INTEGRITY_FIELD)
            self.assertIn("MaxIntegrity", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_max_integrity_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, MAX_INTEGRITY_FIELD),
            MAX_INTEGRITY_FIELD,
        )
        self.assertTrue(has_declaration(section, MAX_INTEGRITY_FIELD))
        self.assertEqual(declaration_count(section, MAX_INTEGRITY_FIELD), 1)
        self.assertTrue(
            MAX_INTEGRITY_FIELD.startswith("float "),
            MAX_INTEGRITY_FIELD,
        )
        self.assertTrue(MAX_INTEGRITY_FIELD.endswith(";"), MAX_INTEGRITY_FIELD)
        self.assertIn("MaxIntegrity", MAX_INTEGRITY_FIELD)
        self.assertIn("100.f", MAX_INTEGRITY_FIELD)
        self.assertIn(" = ", MAX_INTEGRITY_FIELD)
        self.assertNotIn("INDEX_NONE", MAX_INTEGRITY_FIELD)
        self.assertNotIn("NAME_None", MAX_INTEGRITY_FIELD)
        self.assertNotIn("TEXT(", MAX_INTEGRITY_FIELD)
        self.assertNotIn("UFUNCTION", MAX_INTEGRITY_FIELD)
        self.assertNotIn("{", MAX_INTEGRITY_FIELD)
        self.assertNotIn("}", MAX_INTEGRITY_FIELD)
        self.assertNotIn("return ", MAX_INTEGRITY_FIELD)
        self.assertNotIn("ApplyWeaponDamage", MAX_INTEGRITY_FIELD)
        self.assertNotIn("SetExposed", MAX_INTEGRITY_FIELD)
        self.assertNotIn("AcceptsWeapon", MAX_INTEGRITY_FIELD)
        self.assertNotIn(INTEGRITY_SIBLING_TYPE_NAME, MAX_INTEGRITY_FIELD)
        self.assertNotIn("WeakPointId", MAX_INTEGRITY_FIELD)
        self.assertNotIn("CurrentIntegrity", MAX_INTEGRITY_FIELD)
        self.assertNotIn("RemainingIntegrity", MAX_INTEGRITY_FIELD)
        self.assertNotIn("bExposed", MAX_INTEGRITY_FIELD)
        self.assertNotIn("bDestroyed", MAX_INTEGRITY_FIELD)
        self.assertNotIn("HullCollider", MAX_INTEGRITY_FIELD)
        self.assertNotIn("OpticalTracker", MAX_INTEGRITY_FIELD)
        self.assertNotIn("WeaponServo", MAX_INTEGRITY_FIELD)
        self.assertNotIn("CountermeasurePod", MAX_INTEGRITY_FIELD)
        self.assertNotEqual(MAX_INTEGRITY_FIELD, INTEGRITY_FIELD)
        for name in leftover_weak_point_accept_flags():
            self.assertNotIn(name, MAX_INTEGRITY_FIELD)
        for name in leftover_live_copy_method_names():
            self.assertNotIn(name, MAX_INTEGRITY_FIELD)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tfloat\n"
            "\tMaxIntegrity = 100.f;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tfloat   MaxIntegrity = 100.f;\n"
            "private:\n"
            "};\n"
        )
        wrap_tab = (
            "public:\n"
            "\tfloat\tMaxIntegrity = 100.f;\n"
            "};\n"
        )
        wrap_indent = (
            "public:\n"
            "\tfloat\n"
            "\t\tMaxIntegrity = 100.f;\n"
            "};\n"
        )
        wrap_equals = (
            "public:\n"
            "\tfloat MaxIntegrity=100.f;\n"
            "};\n"
        )
        wrap_uproperty = (
            "public:\n"
            f"\t{UPROPERTY_BOSS}\n"
            f"\t{MAX_INTEGRITY_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_one_line = (
            "public:\n"
            f"\t{UPROPERTY_BOSS} {MAX_INTEGRITY_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_category = (
            "public:\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadWrite,\n"
            '\t\tCategory="Skyguard|Boss", meta=(ClampMin="1.0"))\n'
            f"\t{MAX_INTEGRITY_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_meta = (
            "public:\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadWrite, "
            'Category="Skyguard|Boss",\n'
            '\t\tmeta=(ClampMin="1.0"))\n'
            f"\t{MAX_INTEGRITY_FIELD}\n"
            "};\n"
        )
        wrap_uproperty_spaces = (
            "public:\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadWrite, "
            'Category = "Skyguard|Boss", meta = (ClampMin = "1.0"))\n'
            f"\t{MAX_INTEGRITY_FIELD}\n"
            "};\n"
        )
        headers = []
        for wrap in (
            wrap_type,
            wrap_spaces,
            wrap_tab,
            wrap_indent,
            wrap_equals,
            wrap_uproperty,
            wrap_uproperty_one_line,
            wrap_uproperty_category,
            wrap_uproperty_meta,
            wrap_uproperty_spaces,
        ):
            headers.append(
                f"class SKYGUARD52_API {CLASS_NAME} "
                f": public UStaticMeshComponent\n{{\n{wrap}"
            )
        for header in headers:
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, MAX_INTEGRITY_FIELD),
                section,
            )
            self.assertEqual(
                require_declaration(section, MAX_INTEGRITY_FIELD),
                MAX_INTEGRITY_FIELD,
            )
            self.assertEqual(
                declaration_count(section, MAX_INTEGRITY_FIELD),
                1,
            )
        one_line = f"{{\npublic:\n\t{MAX_INTEGRITY_FIELD}\n}}\n"
        self.assertTrue(has_declaration(one_line, MAX_INTEGRITY_FIELD))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, MAX_INTEGRITY_FIELD), section)
        self.assertEqual(
            require_declaration(section, MAX_INTEGRITY_FIELD),
            MAX_INTEGRITY_FIELD,
        )
        self.assertIn(UPROPERTY_BOSS, section)
        self.assertIn(REQUIRED_FIELD_META, section)

    def test_zero_max_integrity_does_not_satisfy(self) -> None:
        assigned = "\tfloat MaxIntegrity = 0.f;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(assigned, MAX_INTEGRITY_FIELD)
        self.assertIn("MaxIntegrity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(assigned, MAX_INTEGRITY_FIELD))

    def test_uninitialized_max_integrity_does_not_satisfy(self) -> None:
        bare = "\tfloat MaxIntegrity;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(bare, MAX_INTEGRITY_FIELD)
        self.assertIn("MaxIntegrity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(bare, MAX_INTEGRITY_FIELD))

    def test_apache_max_integrity_default_does_not_satisfy(self) -> None:
        leftover_apache = (
            "\tfloat MaxIntegrity = "
            f"{leftover_apache_integrity_default()};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(leftover_apache, MAX_INTEGRITY_FIELD)
        self.assertIn("MaxIntegrity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(leftover_apache, MAX_INTEGRITY_FIELD))
        self.assertNotIn(
            leftover_apache_integrity_default(),
            MAX_INTEGRITY_FIELD,
        )

    def test_sibling_public_fields_do_not_satisfy(self) -> None:
        for region in (
            f"\t{WEAK_POINT_ID}\n",
            f"\t{INTEGRITY_FIELD}\n",
            f"\t{EXPOSED_FIELD}\n",
            f"\t{DESTROYED_FIELD}\n",
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, MAX_INTEGRITY_FIELD)
            self.assertIn("MaxIntegrity", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, MAX_INTEGRITY_FIELD))

    def test_leftover_accept_flags_do_not_satisfy(self) -> None:
        for name in leftover_weak_point_accept_flags():
            region = f"\tbool {name} = true;\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, MAX_INTEGRITY_FIELD)
            self.assertIn("MaxIntegrity", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, MAX_INTEGRITY_FIELD))
            self.assertNotIn(name, MAX_INTEGRITY_FIELD)

    def test_leftover_methods_do_not_satisfy(self) -> None:
        for leftover in LEFTOVER_METHODS:
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, MAX_INTEGRITY_FIELD)
            self.assertIn("MaxIntegrity", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(region, MAX_INTEGRITY_FIELD))
            self.assertNotIn(leftover, MAX_INTEGRITY_FIELD)

    def test_delegate_param_form_does_not_satisfy_field_lock(self) -> None:
        region = (
            "DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(\n"
            "\tFSkyguardWeakPointStateEvent,\n"
            "\tFName, WeakPointId,\n"
            "\tESkyguardBossWeapon, Weapon,\n"
            "\tfloat, RemainingIntegrity);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(region, MAX_INTEGRITY_FIELD)
        self.assertIn("MaxIntegrity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(region, MAX_INTEGRITY_FIELD))
        self.assertNotIn(DELEGATE_PARAM_FORM, MAX_INTEGRITY_FIELD)

    def test_integrity_sibling_does_not_satisfy(self) -> None:
        region = f"\t{INTEGRITY_FIELD}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(region, MAX_INTEGRITY_FIELD)
        self.assertIn("MaxIntegrity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(region, MAX_INTEGRITY_FIELD))
        self.assertNotIn(INTEGRITY_FIELD, MAX_INTEGRITY_FIELD)
        self.assertNotIn(INTEGRITY_SIBLING_TYPE_NAME, MAX_INTEGRITY_FIELD)

    def test_apache_current_integrity_does_not_satisfy(self) -> None:
        leftover_apache = "\tfloat CurrentIntegrity = 100.f;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(leftover_apache, MAX_INTEGRITY_FIELD)
        self.assertIn("MaxIntegrity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(leftover_apache, MAX_INTEGRITY_FIELD))
        self.assertNotIn("CurrentIntegrity", MAX_INTEGRITY_FIELD)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, MAX_INTEGRITY_FIELD)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_BOSS)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, MAX_INTEGRITY_FIELD)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_BOSS)
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_BOSS, section)
        self.assertIn(REQUIRED_FIELD_META, UPROPERTY_BOSS)
        self.assertTrue(has_declaration(section, MAX_INTEGRITY_FIELD), section)

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        self.assertNotIn("UFUNCTION", MAX_INTEGRITY_FIELD)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(
            MAX_INTEGRITY_FIELD.startswith("UFUNCTION"),
            MAX_INTEGRITY_FIELD,
        )
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, MAX_INTEGRITY_FIELD), section)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", MAX_INTEGRITY_FIELD)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertIn("100.f", MAX_INTEGRITY_FIELD)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)

    def test_contract_does_not_lock_max_integrity_cpp_body(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        self.assertNotIn("{", MAX_INTEGRITY_FIELD)
        self.assertNotIn("}", MAX_INTEGRITY_FIELD)
        self.assertNotIn("return ", MAX_INTEGRITY_FIELD)
        self.assertNotIn(
            "USkyguardBossWeakPointComponent::MaxIntegrity",
            MAX_INTEGRITY_FIELD,
        )
        self.assertNotIn(
            "SkyguardBossWeakPointComponent.cpp",
            MAX_INTEGRITY_FIELD,
        )
        self.assertNotIn("SkyguardBossWeakPointComponent.cpp", locked_only)
        self.assertNotIn("return false", MAX_INTEGRITY_FIELD)
        self.assertNotIn("return true", MAX_INTEGRITY_FIELD)
        self.assertNotIn("CreateDefaultSubobject", MAX_INTEGRITY_FIELD)
        self.assertNotIn("RefreshAuthoredWeakPointRegistry", MAX_INTEGRITY_FIELD)
        self.assertNotIn("SetBossPhase", MAX_INTEGRITY_FIELD)
        self.assertNotIn("HandleWeakPointDestroyed", MAX_INTEGRITY_FIELD)

    def test_contract_does_not_relock_sibling_unused_fields(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for leftover in SIBLING_UNUSED_FIELDS:
            self.assertNotIn(leftover, locked_only)
            self.assertNotIn(leftover, MAX_INTEGRITY_FIELD)
        for name in SIBLING_UNUSED_FIELD_NAMES:
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, MAX_INTEGRITY_FIELD)
        self.assertNotIn(INTEGRITY_SIBLING_TYPE_NAME, locked_only)
        self.assertNotIn(INTEGRITY_SIBLING_TYPE_NAME, MAX_INTEGRITY_FIELD)
        self.assertIn("MaxIntegrity", MAX_INTEGRITY_FIELD)

    def test_contract_does_not_relock_sibling_weak_point_id(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for token in LEFTOVER_WEAK_POINT_ID_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        self.assertIn(
            "Scripts/tests/test_weak_point_id_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("WeakPointId", MAX_INTEGRITY_FIELD)

    def test_contract_does_not_relock_sibling_integrity(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for token in LEFTOVER_INTEGRITY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        self.assertIn(
            "Scripts/tests/test_weak_point_integrity_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn(INTEGRITY_SIBLING_TYPE_NAME, MAX_INTEGRITY_FIELD)
        self.assertNotEqual(MAX_INTEGRITY_FIELD, INTEGRITY_FIELD)

    def test_contract_does_not_relock_sibling_exposed(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for token in LEFTOVER_EXPOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        self.assertIn(
            "Scripts/tests/test_weak_point_exposed_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("bExposed", MAX_INTEGRITY_FIELD)

    def test_contract_does_not_relock_sibling_destroyed(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for token in LEFTOVER_DESTROYED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        self.assertIn(
            "Scripts/tests/test_weak_point_destroyed_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("bDestroyed", MAX_INTEGRITY_FIELD)

    def test_contract_does_not_relock_leftover_accept_flags(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for name in leftover_weak_point_accept_flags():
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, MAX_INTEGRITY_FIELD)

    def test_contract_does_not_relock_leftover_methods(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for leftover in LEFTOVER_METHODS:
            self.assertNotIn(leftover, locked_only)
            self.assertNotIn(leftover, MAX_INTEGRITY_FIELD)
        for name in LEFTOVER_METHOD_NAMES:
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, MAX_INTEGRITY_FIELD)

    def test_contract_does_not_relock_leftover_defaults_struct(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for token in LEFTOVER_DEFAULTS_STRUCT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        self.assertIn(
            "Scripts/tests/test_boss_weak_point_defaults_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_lifeline_hunter_fields(
        self,
    ) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for token in LEFTOVER_LIFELINE_HUNTER_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        self.assertIn(
            "Scripts/tests/test_lifeline_hunter_debris_control_surface"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_lifeline_hunter_debris_primary_sensor"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_lifeline_hunter_debris_secondary_sensor"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_hull_collider(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for token in LEFTOVER_HULL_COLLIDER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        self.assertNotIn("HullCollider", MAX_INTEGRITY_FIELD)
        self.assertIn(
            "Scripts/tests/test_apache_hull_collider_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_radar_ghost_breakwater_road_hunter_scripts_stay_sibling_only(
        self,
    ) -> None:
        self.assertIn(
            "Scripts/tests/test_radar_ghost_engine_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_breakwater_engine_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_road_hunter_engine_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_runway_breaker_port_engine"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        self.assertNotIn("ASkyguardRadarGhostBoss", locked_only)
        self.assertNotIn("ASkyguardBreakwaterBoss", locked_only)
        self.assertNotIn("ASkyguardRoadHunterBoss", locked_only)
        self.assertNotIn("ASkyguardRunwayBreakerBoss", locked_only)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        self.assertEqual(
            require_declaration(locked_only, MAX_INTEGRITY_FIELD),
            MAX_INTEGRITY_FIELD,
        )
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MAX_INTEGRITY_FIELD)
        self.assertNotIn("ApplyWeaponDamage", locked_only)
        self.assertNotIn("SetExposed", locked_only)
        self.assertNotIn("AcceptsWeapon", locked_only)
        self.assertNotIn(INTEGRITY_SIBLING_TYPE_NAME, locked_only)
        self.assertNotIn("WeakPointId", locked_only)
        self.assertNotIn("CurrentIntegrity", locked_only)
        self.assertNotIn("bExposed", locked_only)
        self.assertNotIn("bDestroyed", locked_only)
        self.assertNotIn("HullCollider", locked_only)
        self.assertNotIn("OpticalTracker", locked_only)
        self.assertNotIn("WeaponServo", locked_only)
        self.assertNotIn("CountermeasurePod", locked_only)
        self.assertNotIn("DebrisControlSurface", locked_only)
        self.assertNotIn("FSkyguardBossWeakPointDefaults", locked_only)
        for name in leftover_weak_point_accept_flags():
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
        self.assertNotIn("ASkyguardApacheAircraft", section)
        self.assertNotIn("ASkyguardGunner", section)
        self.assertNotIn("ASkyguardRadarNode", section)
        self.assertNotIn("ASkyguardBlackKiteBoss", section)
        self.assertNotIn("ASkyguardIronRainBoss", section)
        self.assertNotIn("ASkyguardRadarGhostBoss", section)
        self.assertNotIn("ASkyguardPathfinderBoss", section)
        self.assertNotIn("ASkyguardTempestBoss", section)
        self.assertNotIn("ASkyguardLastFlightBoss", section)
        self.assertNotIn("ASkyguardLifelineHunterBoss", section)
        self.assertNotIn("ASkyguardPatrolShip", section)
        self.assertNotIn("MinHeightFromOriginCm", section)
        self.assertNotIn("CurrentIntegrity", section)
        self.assertEqual(
            require_declaration(section, MAX_INTEGRITY_FIELD),
            MAX_INTEGRITY_FIELD,
        )
        self.assertEqual(declaration_count(section, MAX_INTEGRITY_FIELD), 1)
        self.assertNotIn("SkyguardBossWeakPointComponent.cpp", section)
        self.assertNotIn(
            "USkyguardBossWeakPointComponent::MaxIntegrity",
            section,
        )
        self.assertNotIn(DELEGATE_PARAM_FORM, section)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBossWeakPointComponent.cpp", section)
        self.assertNotIn(
            "USkyguardBossWeakPointComponent::MaxIntegrity",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", MAX_INTEGRITY_FIELD)
        self.assertNotIn("}", MAX_INTEGRITY_FIELD)
        self.assertNotIn("return false", MAX_INTEGRITY_FIELD)
        self.assertNotIn("return true", MAX_INTEGRITY_FIELD)

    def test_contract_does_not_scan_wrong_harbor_headers(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        file_text = this_file_text()
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        self.assertNotIn("MinHeightFromOriginCm", MAX_INTEGRITY_FIELD)
        self.assertNotIn("CurrentIntegrity", MAX_INTEGRITY_FIELD)
        self.assertNotIn("SkyguardApacheAircraft.h", MAX_INTEGRITY_FIELD)
        leftover_header = "SkyguardPathfinderEncounterController.h"
        self.assertNotIn(leftover_header, locked_only)
        self.assertNotIn(leftover_header, MAX_INTEGRITY_FIELD)
        self.assertNotIn(f"origin/main:{leftover_header}", file_text)
        self.assertNotIn(
            f"git show origin/main:{leftover_header}",
            file_text,
        )
        self.assertNotIn(
            f"origin/main:Source/Skyguard52/{leftover_header}",
            file_text,
        )

    def test_contract_does_not_scan_apache_public_section_for_harbor(
        self,
    ) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        file_text = this_file_text()
        apache_header = "SkyguardApacheAircraft.h"
        self.assertNotIn(apache_header, locked_only)
        self.assertNotIn(apache_header, MAX_INTEGRITY_FIELD)
        self.assertNotIn("ASkyguardApacheAircraft", locked_only)
        self.assertNotIn("ASkyguardApacheAircraft", MAX_INTEGRITY_FIELD)
        self.assertNotIn(f"origin/main:{apache_header}", file_text)
        self.assertNotIn(f"git show origin/main:{apache_header}", file_text)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)

    def test_max_integrity_is_not_harbor_40_80(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        section = public_section(origin_main_header())
        sibling = INTEGRITY_FIELD
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, MAX_INTEGRITY_FIELD)
            self.assertNotEqual(token, sibling)
            self.assertNotEqual(token, "100.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        self.assertTrue(has_declaration(section, MAX_INTEGRITY_FIELD), section)
        self.assertTrue(has_declaration(section, sibling), section)
        self.assertNotIn(sibling, MAX_INTEGRITY_FIELD)
        self.assertIn("100.f", MAX_INTEGRITY_FIELD)
        self.assertNotIn("MaxIntegrity", leftover_harbor_tokens())
        self.assertNotIn("100.f", leftover_harbor_tokens())
        self.assertNotIn(INTEGRITY_SIBLING_TYPE_NAME, leftover_harbor_tokens())

    def test_minimum_civilian_separation_is_not_harbor_40_80(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        section = public_section(origin_main_header())
        adjacent = "MinimumCivilianSeparationMeters = 550.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        for token in HARBOR_ADJACENT_CIVILIAN_SEPARATION:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        for token in HARBOR_ADJACENT_NOT_LOCKED:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        self.assertNotIn("MinimumCivilianSeparationMeters", section)
        self.assertNotIn("550.f", section)

    def test_harbor_adjacent_fields_are_not_harbor_40_80(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        adjacent_civilian = "MinimumCivilianSeparationMeters = 550.f"
        adjacent_weapon = "MinimumWeaponSeparationMeters = 450.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent_civilian)
            self.assertNotEqual(token, adjacent_weapon)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        file_text = this_file_text()
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, file_text)
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotEqual(token, "100.f")
            self.assertNotEqual(
                token,
                "MinimumCivilianSeparationMeters = 550.f",
            )

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
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
                "weak point MaxIntegrity field contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, MAX_INTEGRITY_FIELD.lower())
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                MAX_INTEGRITY_FIELD.lower(),
                "weak point MaxIntegrity contains "
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
        self.assertNotIn(dirty_fwd, MAX_INTEGRITY_FIELD)

    def test_contract_is_max_integrity_field_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, MAX_INTEGRITY_FIELD),
            MAX_INTEGRITY_FIELD,
        )
        locked_only = f"{MAX_INTEGRITY_FIELD}\n"
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MAX_INTEGRITY_FIELD)
        leftover_groups = (
            SIBLING_UNUSED_FIELDS,
            SIBLING_UNUSED_FIELD_NAMES,
            LEFTOVER_METHODS,
            LEFTOVER_METHOD_NAMES,
            leftover_weak_point_accept_flags(),
            leftover_live_copy_method_names(),
            LEFTOVER_LIFELINE_HUNTER_FIELDS_NOT_LOCKED,
            LEFTOVER_HULL_COLLIDER_NOT_LOCKED,
            LEFTOVER_DEFAULTS_STRUCT_NOT_LOCKED,
            LEFTOVER_WEAK_POINT_ID_NOT_LOCKED,
            LEFTOVER_INTEGRITY_NOT_LOCKED,
            LEFTOVER_EXPOSED_NOT_LOCKED,
            LEFTOVER_DESTROYED_NOT_LOCKED,
            HARBOR_ADJACENT_NOT_LOCKED,
            leftover_harbor_clock_tokens(),
            WRONG_HARBOR_HEADERS_NOT_SCANNED,
        )
        for group in leftover_groups:
            for token in group:
                self.assertNotIn(token, locked_only)
                self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAX_INTEGRITY_FIELD)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, MAX_INTEGRITY_FIELD.lower())
            self.assertNotIn(banned, locked_only.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", MAX_INTEGRITY_FIELD)
        self.assertNotIn("{", MAX_INTEGRITY_FIELD)
        self.assertTrue(MAX_INTEGRITY_FIELD.startswith("float "))
        self.assertTrue(MAX_INTEGRITY_FIELD.endswith(";"))
        self.assertIn("100.f", MAX_INTEGRITY_FIELD)
        self.assertEqual(MAX_INTEGRITY_FIELD, "float MaxIntegrity = 100.f;")
        self.assertIn(UPROPERTY_BOSS, section)
        self.assertIn(REQUIRED_FIELD_META, UPROPERTY_BOSS)
        self.assertEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardBossWeakPointComponent.h",
        )
        self.assertEqual(CLASS_NAME, "USkyguardBossWeakPointComponent")

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
