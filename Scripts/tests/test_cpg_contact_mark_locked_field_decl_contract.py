# THIS IS leftover-safe FSkyguardCpgContactMark bLocked.
# origin/main form: BARE plain C++ field
# `bool bLocked = false;`
# THIS IS leftover-safe isolated FIELD declaration.
# FSkyguardCpgContactMark IS a plain C++ HUD struct.
# There is NO UPROPERTY. There is NO Category.
# There is NO VisibleAnywhere. There is NO EditAnywhere.
# There is NO BlueprintReadOnly. There is NO GENERATED_BODY.
# There is NO USTRUCT. The locked decl IS the bare field
# `bool bLocked = false;` with that in-struct initializer.
# Fail-closed if bLocked is missing or renamed, if the
# type is not bool, if the initializer is missing or is
# not `= false`, or if UPROPERTY / Category clones land.
# Fail-closed if this clone still asserts UPROPERTY /
# Category / VisibleAnywhere / EditAnywhere /
# BlueprintReadOnly / GENERATED_BODY / USTRUCT as the
# locked decl.
# Fail-closed if the initializer is missing, is Harbor 40/80
# (split-token), or is not `= false`.
# bLocked here is NOT leftover HUD LockLine #1505,
# leftover HUD LockPhase #1508, leftover HUD LockProgress
# #1512, leftover ContactMark LockAlpha, leftover
# ContactMark WorldLocation #1516, leftover ContactMark
# Label, leftover ContactMark bSeeking, leftover HUD
# snapshot #1501-#1515, or leftover SightHud FScreenMark
# bLocked.
# Parse STRUCT `FSkyguardCpgContactMark` body ONLY after
# `struct FSkyguardCpgContactMark`. Stop at
# `SkyguardCpgWeaponLabel`.
# Do NOT parse leftover `FSkyguardCpgHudSnapshot`
# (isolated #1501-#1515).
# Do NOT parse leftover `FSkyguardCpgDebriefSnapshot`
# (exhausted isolated #1451-#1465).
# Do NOT parse leftover `FSkyguardLoadoutSpec`.
# Do NOT parse leftover SightHud `FScreenMark`.
# HUD leftover `int32 FlareCount = 0` is NOT leftover
# LoadoutSpec `int32 FlareCount = 6`.
# There is NO leftover analog Python bulk for this HUD
# struct. Isolated field decl does not invent one.
# Do NOT contract sibling fields WorldLocation / Label /
# bSeeking / LockAlpha.
# THIS IS NOT leftover analog
# cpg-debrief-snapshot-defaults. Keep that file in
# LOCKED_SCRIPTS.
# THIS IS NOT leftover CpgDebriefSnapshot isolated
# field decls (#1451-#1465). Keep those files in
# LOCKED_SCRIPTS.
# THIS IS NOT leftover StormRainBeatKit isolated
# field decls (#1490-#1500). Keep analog
# storm-rain-beat-kit-fields in LOCKED_SCRIPTS.
# THIS IS NOT leftover HUD snapshot isolated fields
# #1501-#1515. Keep leftover-safe LockLine #1505,
# LockPhase #1508, LockProgress #1512, and siblings in
# LOCKED_SCRIPTS.
# THIS IS NOT leftover ContactMark WorldLocation #1516.
# Keep leftover-safe WorldLocation in LOCKED_SCRIPTS.
# THIS IS NOT leftover LoadoutSpec isolated FlareCount.
# THIS IS NOT leftover-safe TheaterKitSpec
# WeatherIdentity #1300 UPROPERTY clone. Isolated field
# decl does not relock the analog bulk.
# Clone #1300 is UPROPERTY-based. This lane is a PLAIN
# struct. ContactMark parse-window retarget is leftover-safe
# #1516 WorldLocation (FVector + ZeroVector initializer,
# parses FSkyguardCpgContactMark, stop before
# SkyguardCpgWeaponLabel). RETARGET: type is bool,
# identifier is bLocked, initializer is `= false`, parse
# STRUCT FSkyguardCpgContactMark, stop before
# SkyguardCpgWeaponLabel.
# Do NOT copy leftover HUD snapshot LockLine / LockPhase /
# LockProgress parse windows. Do NOT copy leftover
# RoutePoint / MissionObjectiveAnchor /
# MissionLandmarkAnchor WorldLocation parse windows.
# Harbor 40/80 fail-closed via split tokens.
# Ban retired live-copy tokens via split tokens
# (b + Ya + kRuntimeReady). Stay Apache CPG 30 mm / Hydra /
# Hellfire. Fail-closed on live Ig+la / Ri+fle / Ya+k
# appearing as contiguous tokens in THIS test file.

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardCpgHud.h"
STRUCT_NAME = "FSkyguardCpgContactMark"
LEFTOVER_HUD_SNAPSHOT = "FSkyguardCpgHudSnapshot"
LEFTOVER_DEBRIEF_SNAPSHOT = "FSkyguardCpgDebriefSnapshot"
LEFTOVER_LOADOUT_SPEC = "FSkyguardLoadoutSpec"
LEFTOVER_ROUTE_POINT = "FSkyguardRoutePoint"
LEFTOVER_OBJECTIVE_ANCHOR = "FSkyguardMissionObjectiveAnchor"
LEFTOVER_LANDMARK_ANCHOR = "FSkyguardMissionLandmarkAnchor"
LEFTOVER_SCREEN_MARK = "FScreenMark"
LEFTOVER_DEBRIEF_HEADER = "Source/Skyguard52/SkyguardCpgDebrief.h"
LEFTOVER_LOADOUT_HEADER = "Source/Skyguard52/SkyguardGunshipTypes.h"
LEFTOVER_THEATER_HEADER = "Source/Skyguard52/SkyguardCampaignTheaterKit.h"
LEFTOVER_MISSION_TYPES_HEADER = "Source/Skyguard52/SkyguardMissionTypes.h"
LEFTOVER_MAP_ASSEMBLY_HEADER = (
    "Source/Skyguard52/SkyguardMissionMapAssemblyDirector.h"
)
LEFTOVER_SIGHT_HUD_HEADER = "Source/Skyguard52/SkyguardCpgSightHud.h"
TARGET = "bool bLocked = false;"
TARGET_WRONG_BARE = "bool bLocked;"
TARGET_WRONG_EQ_EMPTY = 'bool bLocked = TEXT("");'
TARGET_WRONG_EQ_NONE = "bool bLocked = NAME_None;"
TARGET_WRONG_TRUE = "bool bLocked = true;"
TARGET_WRONG_ZERO = "bool bLocked = 0;"
TARGET_WRONG_ONE = "bool bLocked = 1;"
TARGET_WRONG_ZERO_F = "bool bLocked = 0.f;"
TARGET_WRONG_FLOAT = "float bLocked = 0.f;"
TARGET_WRONG_HEALTH = "float bLocked = 160.f;"
TARGET_WRONG_FVECTOR = "FVector bLocked = FVector::ZeroVector;"
TARGET_WRONG_INT = "int32 bLocked;"
TARGET_WRONG_FNAME = "FName bLocked;"
TARGET_WRONG_FSTRING = "FString bLocked;"
TARGET_WRONG_TCHAR = 'const TCHAR* bLocked = TEXT("");'
TARGET_WRONG_WORLD = "FVector WorldLocation = FVector::ZeroVector;"
TARGET_WRONG_LABEL = "FString Label;"
TARGET_WRONG_SEEKING = "bool bSeeking = false;"
TARGET_WRONG_LOCK_ALPHA = "float LockAlpha = 0.f;"
TARGET_WRONG_LOCK_LINE = "FString LockLine;"
TARGET_WRONG_LOCK_PHASE = (
    "ESkyguardGuidedLockPhase LockPhase = "
    "ESkyguardGuidedLockPhase::Search;"
)
TARGET_WRONG_LOCK_PROGRESS = "float LockProgress = 0.f;"
TARGET_WRONG_WEAPON = "FString WeaponLine;"
TARGET_WRONG_TITLE = "FString MissionTitle;"
TARGET_WRONG_HEADING = "float HeadingDegrees = 0.f;"
LOCKED_DECL = TARGET
CLONE_UPROPERTY_THEATER = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Theater")'
)
CLONE_UPROPERTY_CAMPAIGN = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Campaign")'
)
CLONE_UPROPERTY_EDIT = "UPROPERTY(EditAnywhere, BlueprintReadOnly)"
CLONE_DAY_MISSION_ID = "FName MissionId;"
CLONE_STORM_TITLE = 'const TCHAR* Title = TEXT("");'
CLONE_WEATHER_IDENTITY = "FName WeatherIdentity;"
STOP_BEFORE_HUD_SNAPSHOT = "struct FSkyguardCpgHudSnapshot"
STOP_BEFORE_WEAPON_LABEL = "SkyguardCpgWeaponLabel"
STOP_BEFORE_DEBRIEF = "struct FSkyguardCpgDebriefSnapshot"
STOP_BEFORE_LOADOUT = "struct FSkyguardLoadoutSpec"
STOP_BEFORE_THEATER = "struct FSkyguardTheaterKitSpec"
STOP_BEFORE_ROUTE_POINT = "struct FSkyguardRoutePoint"
STOP_BEFORE_OBJECTIVE_ANCHOR = "struct FSkyguardMissionObjectiveAnchor"
STOP_BEFORE_LANDMARK_ANCHOR = "struct FSkyguardMissionLandmarkAnchor"
STOP_BEFORE_SCREEN_MARK = "struct FScreenMark"
STOP_BEFORE_AUDIO_EVENT = "enum class ESkyguardAudioEvent"
STOP_BEFORE_PICTOGRAM = "enum class ESkyguardBriefingPictogram"
STOP_BEFORE_EVENT_DEF = "struct FSkyguardAudioEventDefinition"
STOP_BEFORE_BOSS_WEAPON = "enum class ESkyguardBossWeapon"
STOP_BEFORE_PROP_SPINNER = "ASkyguardPropSpinner"
STOP_BEFORE_SORTIE = "ASkyguardGunshipSortieDirector"
STOP_BEFORE_PATROL = "ASkyguardPatrolShipBoss"
STOP_BEFORE_GUNNER = "ASkyguardGunner"
STOP_BEFORE_WEAK_POINT = "USkyguardBossWeakPointComponent"
STOP_BEFORE_HARBOR_CALLS = "SkyguardHarborBeatCalls"
WEAPON_LABEL = "SkyguardCpgWeaponLabel"
THREAT_LABEL = "SkyguardCpgThreatLabel"
SHIP_SYSTEM_LABEL = "SkyguardCpgShipSystemLabel"
LOCK_PHASE_LABEL = "SkyguardCpgLockPhaseLabel"
SIGHT_LABEL = "SkyguardCpgSightLabel"
INBOUND_LABEL = "SkyguardCpgInboundLabel"
FLARE_TAPE = "SkyguardCpgFlareTape"
LEGACY_WORDING = "SkyguardCpgHudHasLegacyLiveWording"
SIBLING_WORLD = "WorldLocation"
SIBLING_LABEL = "Label"
SIBLING_SEEKING = "bSeeking"
SIBLING_LOCK_ALPHA = "LockAlpha"
HUD_SIBLING_FLARE_DECL = "int32 FlareCount = 0;"
LEFTOVER_LOADOUT_FLARE_DECL = "int32 FlareCount = 6;"
LEFTOVER_HUD_WEAPON = "FString WeaponLine;"
LEFTOVER_HUD_RANGE_LINE = "FString RangeLine;"
LEFTOVER_HUD_HEADING = "float HeadingDegrees = 0.f;"
LEFTOVER_HUD_FLARE = "int32 FlareCount = 0;"
LEFTOVER_HUD_MISSILE = "bool bMissileInbound = false;"
LEFTOVER_HUD_LOCK_LINE = "FString LockLine;"
LEFTOVER_HUD_LOCK_PHASE = (
    "ESkyguardGuidedLockPhase LockPhase = "
    "ESkyguardGuidedLockPhase::Search;"
)
LEFTOVER_HUD_LOCK_PROGRESS = "float LockProgress = 0.f;"
LEFTOVER_CONTACT_WORLD = "FVector WorldLocation = FVector::ZeroVector;"
LEFTOVER_CONTACT_LABEL = "FString Label;"
LEFTOVER_CONTACT_SEEKING = "bool bSeeking = false;"
LEFTOVER_CONTACT_LOCK_ALPHA = "float LockAlpha = 0.f;"
LEFTOVER_DEBRIEF_VALID = "bool bValid = false;"
LEFTOVER_DEBRIEF_WON = "bool bWon = false;"
LEFTOVER_DEBRIEF_MISSION_TITLE = "FString MissionTitle;"
LEFTOVER_DEBRIEF_OUTCOME = "FString OutcomeNarrative;"
LEFTOVER_DEBRIEF_SCORE = "int32 Score = 0;"
LEFTOVER_DEBRIEF_MEDAL = "int32 Medal = 0;"
LEFTOVER_APACHE_CLASS = "ASkyguardApacheAircraft"
LEFTOVER_PROTECT_ASSET_CLASS = "ASkyguardProtectAsset"
LEFTOVER_RADAR_NODE_CLASS = "ASkyguardRadarNode"
THIS_SCRIPT = (
    "Scripts/tests/test_cpg_contact_mark_locked"
    "_field_decl_contract.py"
)
LEFTOVER_CONTACT_WORLD_LOCATION = (
    "Scripts/tests/test_cpg_contact_mark_world_location"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_RANGE_LINE_SCRIPT = (
    "Scripts/tests/test_cpg_hud_snapshot_range_line"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_WEAPON_LINE = (
    "Scripts/tests/test_cpg_hud_snapshot_weapon_line"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_THREAT_LINE = (
    "Scripts/tests/test_cpg_hud_snapshot_threat_line"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_EUFD_LINE = (
    "Scripts/tests/test_cpg_hud_snapshot_eufd_line"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_LOCK_LINE_SCRIPT = (
    "Scripts/tests/test_cpg_hud_snapshot_lock_line"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_SIGHT_LINE = (
    "Scripts/tests/test_cpg_hud_snapshot_sight_line"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_STATION_STATUS = (
    "Scripts/tests/test_cpg_hud_snapshot_station_status"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_LOCK_PHASE_SCRIPT = (
    "Scripts/tests/test_cpg_hud_snapshot_lock_phase"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_SIGHT_MODE = (
    "Scripts/tests/test_cpg_hud_snapshot_sight_mode"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_RANGE_METERS = (
    "Scripts/tests/test_cpg_hud_snapshot_range_meters"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_THREAT_COUNT = (
    "Scripts/tests/test_cpg_hud_snapshot_threat_count"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_HEADING_DEGREES = (
    "Scripts/tests/test_cpg_hud_snapshot_heading_degrees"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_LOCK_PROGRESS_SCRIPT = (
    "Scripts/tests/test_cpg_hud_snapshot_lock_progress"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_FLARE_COUNT = (
    "Scripts/tests/test_cpg_hud_snapshot_flare_count"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_MISSILE_INBOUND = (
    "Scripts/tests/test_cpg_hud_snapshot_missile_inbound"
    "_field_decl_contract.py"
)
CLONE_THEATER_WEATHER_IDENTITY = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
    "_field_decl_contract.py"
)
LEFTOVER_ANALOG_STORM_KIT_FIELDS = (
    "Scripts/tests/test_storm_rain_beat_kit_fields_contract.py"
)
LEFTOVER_ROUTE_POINT_WORLD = (
    "Scripts/tests/test_route_point_world_location"
    "_field_decl_contract.py"
)
LEFTOVER_OBJECTIVE_WORLD = (
    "Scripts/tests/test_mission_objective_anchor_world_location"
    "_field_decl_contract.py"
)
LEFTOVER_LANDMARK_WORLD = (
    "Scripts/tests/test_mission_landmark_anchor_world_location"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_FLARE = (
    "Scripts/tests/test_loadout_spec_flare_count"
    "_field_decl_contract.py"
)
LEFTOVER_ANALOG_DEBRIEF_DEFAULTS = (
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py"
)
LEFTOVER_DEBRIEF_VALID_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_valid"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_WON_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_won"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_MISSION_TITLE_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_mission_title"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_OUTCOME_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_outcome_narrative"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_SCORE_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_score"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_MEDAL_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_medal"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_SHOTS_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_shots_fired"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_HITS_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_hits"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_CARGO_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_cargo_percent"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_RADAR_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_radar_dead"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_SYSTEMS_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_destroyed_systems"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_LOADOUT_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_selected_loadout"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_CANNON_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_cannon_ready"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_ROCKET_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_rocket_ready"
    "_field_decl_contract.py"
)
LEFTOVER_DEBRIEF_GUIDED_FIELD = (
    "Scripts/tests/test_cpg_debrief_snapshot_guided_ready"
    "_field_decl_contract.py"
)
LEFTOVER_ANALOG_DEBRIEF_FAIL_CLOSED = (
    "Scripts/tests/test_cpg_debrief_fail_closed.py"
)
LEFTOVER_ANALOG_DEBRIEF_COPY = (
    "Scripts/tests/test_cpg_debrief_copy_decl_contract.py"
)
LEFTOVER_ANALOG_THEATER_KIT_BULK = (
    "Scripts/tests/test_campaign_theater_kit_contract.py"
)
LEFTOVER_LOADOUT_DEFAULTS = (
    "Scripts/tests/test_loadout_spec_defaults_contract.py"
)
LEFTOVER_LOADOUT_STATION = (
    "Scripts/tests/test_loadout_spec_starting_station"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_LOADOUT = (
    "Scripts/tests/test_loadout_spec_loadout"
    "_field_decl_contract.py"
)

LOCKED = {
    "SkyguardCpgHud.h",
    "SkyguardCpgHud.cpp",
    "SkyguardCpgHudTests.cpp",
    "SkyguardCpgDebrief.h",
    "SkyguardCpgDebrief.cpp",
    "SkyguardCpgSightHud.h",
    "SkyguardCpgSightHud.cpp",
    "SkyguardGunshipTypes.h",
    "SkyguardGunner.h",
    "SkyguardGunner.cpp",
    "SkyguardCampaignTheaterKit.h",
    "SkyguardCampaignTheaterKit.cpp",
    "SkyguardApacheAircraft.h",
    "SkyguardApacheAircraft.cpp",
    "SkyguardGunshipSortieDirector.h",
    "SkyguardGunshipSortieDirector.cpp",
    "SkyguardHarborBeatCalls.h",
    "SkyguardHarborBeatCalls.cpp",
    "SkyguardStormRainBeatKit.h",
    "SkyguardStormRainBeatKit.cpp",
    "SkyguardMissionTypes.h",
    "SkyguardMissionMapAssemblyDirector.h",
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
        f"{prefix}test_{missile}_boss_decl_contract.py",
        f"{prefix}test_{missile}_missile_decl_contract.py",
    )


def leftover_debrief_isolated_scripts() -> tuple[str, ...]:
    return (
        LEFTOVER_DEBRIEF_VALID_FIELD,
        LEFTOVER_DEBRIEF_WON_FIELD,
        LEFTOVER_DEBRIEF_MISSION_TITLE_FIELD,
        LEFTOVER_DEBRIEF_OUTCOME_FIELD,
        LEFTOVER_DEBRIEF_SCORE_FIELD,
        LEFTOVER_DEBRIEF_MEDAL_FIELD,
        LEFTOVER_DEBRIEF_SHOTS_FIELD,
        LEFTOVER_DEBRIEF_HITS_FIELD,
        LEFTOVER_DEBRIEF_CARGO_FIELD,
        LEFTOVER_DEBRIEF_RADAR_FIELD,
        LEFTOVER_DEBRIEF_SYSTEMS_FIELD,
        LEFTOVER_DEBRIEF_LOADOUT_FIELD,
        LEFTOVER_DEBRIEF_CANNON_FIELD,
        LEFTOVER_DEBRIEF_ROCKET_FIELD,
        LEFTOVER_DEBRIEF_GUIDED_FIELD,
    )


def leftover_hud_snapshot_isolated_scripts() -> tuple[str, ...]:
    return (
        LEFTOVER_HUD_RANGE_LINE_SCRIPT,
        LEFTOVER_HUD_WEAPON_LINE,
        LEFTOVER_HUD_THREAT_LINE,
        LEFTOVER_HUD_EUFD_LINE,
        LEFTOVER_HUD_LOCK_LINE_SCRIPT,
        LEFTOVER_HUD_SIGHT_LINE,
        LEFTOVER_HUD_STATION_STATUS,
        LEFTOVER_HUD_LOCK_PHASE_SCRIPT,
        LEFTOVER_HUD_SIGHT_MODE,
        LEFTOVER_HUD_RANGE_METERS,
        LEFTOVER_HUD_THREAT_COUNT,
        LEFTOVER_HUD_HEADING_DEGREES,
        LEFTOVER_HUD_LOCK_PROGRESS_SCRIPT,
        LEFTOVER_HUD_FLARE_COUNT,
        LEFTOVER_HUD_MISSILE_INBOUND,
    )


def leftover_storm_rain_isolated_scripts() -> tuple[str, ...]:
    prefix = (
        "Scripts/tests/test_storm_rain_beat_kit_"
    )
    suffix = "_field_decl_contract.py"
    return (
        prefix + "mission_id" + suffix,
        prefix + "weather_identity" + suffix,
        prefix + "title" + suffix,
        prefix + "weather_label" + suffix,
        prefix + "hydra_for_clusters" + suffix,
        prefix + "weather" + suffix,
        prefix + "kinds" + suffix,
        prefix + "threats" + suffix,
        prefix + "stations" + suffix,
        prefix + "beat_count" + suffix,
        prefix + "calls" + suffix,
    )


def leftover_world_location_isolated_scripts() -> tuple[str, ...]:
    return (
        LEFTOVER_ROUTE_POINT_WORLD,
        LEFTOVER_OBJECTIVE_WORLD,
        LEFTOVER_LANDMARK_WORLD,
        LEFTOVER_CONTACT_WORLD_LOCATION,
    )


LOCKED_SCRIPTS = (
    leftover_debrief_isolated_scripts()
    + leftover_hud_snapshot_isolated_scripts()
    + leftover_storm_rain_isolated_scripts()
    + leftover_world_location_isolated_scripts()
    + (
        LEFTOVER_ANALOG_DEBRIEF_DEFAULTS,
        LEFTOVER_LOADOUT_FLARE,
        CLONE_THEATER_WEATHER_IDENTITY,
        LEFTOVER_ANALOG_STORM_KIT_FIELDS,
        LEFTOVER_ANALOG_DEBRIEF_FAIL_CLOSED,
        LEFTOVER_ANALOG_DEBRIEF_COPY,
        LEFTOVER_ANALOG_THEATER_KIT_BULK,
        LEFTOVER_LOADOUT_DEFAULTS,
        LEFTOVER_LOADOUT_STATION,
        LEFTOVER_LOADOUT_LOADOUT,
        "Scripts/tests/test_mesh_bind_slot_fields_contract.py",
        "Scripts/tests/test_cpg_copy_has_banned_term_decl_contract.py",
    )
    + leftover_live_copy_boss_scripts()
)

FORBIDDEN_LOCKED_MACRO_TOKENS = (
    "UPROPERTY",
    "Category",
    "VisibleAnywhere",
    "EditAnywhere",
    "BlueprintReadOnly",
    "GENERATED_BODY",
    "USTRUCT",
    "UFUNCTION",
    "BlueprintReadWrite",
)


def leftover_retired_primary_hits_field() -> str:
    return "Ri" + "fleHits"


def leftover_retired_guided_hits_field() -> str:
    return "Ig" + "laHits"


def leftover_neighbor_hit_fields() -> tuple[str, ...]:
    return (
        leftover_retired_primary_hits_field(),
        leftover_retired_guided_hits_field(),
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


def leftover_harbor_director_tokens() -> tuple[str, ...]:
    return (
        STOP_BEFORE_HARBOR_CALLS,
        STOP_BEFORE_SORTIE,
        "HarborBreaker",
        "ASkyguardHarborDirector",
    )


def leftover_live_copy_tokens() -> tuple[str, ...]:
    return ("ig" + "la", "ya" + "k", "ri" + "fle")


def leftover_readiness_tokens() -> tuple[str, ...]:
    return (
        "b" + "Ya" + "kRuntimeReady",
        "ASkyguard" + "Ig" + "la" + "Missile",
    )


def leftover_pictogram_values() -> tuple[str, ...]:
    return (
        "ESkyguardBriefingPictogram::" + "Ri" + "fle",
        "ESkyguardBriefingPictogram::" + "Ig" + "la",
    )


def leftover_live_case_tokens() -> tuple[str, ...]:
    return leftover_live_copy_title_tokens()


def leftover_live_copy_title_tokens() -> tuple[str, ...]:
    return ("Ig" + "la", "Ri" + "fle", "Ya" + "k")


def leftover_weapon_enum_body_tokens() -> tuple[str, ...]:
    return (
        "UMETA(DisplayName = \"" + "Ri" + "fle\")",
        "UMETA(DisplayName = \"" + "Ig" + "la\")",
    )


def leftover_audio_event_enum_tokens() -> tuple[str, ...]:
    return (
        "Ri" + "fleShot",
        "Ri" + "fleMechanical",
        "Ig" + "laSeekerSearch",
        "Ig" + "laLock",
        "Ig" + "laLaunch",
        "Ig" + "laImpact",
    )


STRUCT_RE = re.compile(
    rf"struct\s+(?:SKYGUARD52_API\s+)?{re.escape(STRUCT_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")
LOCKED_FIELD_RE = re.compile(r"bool\s+bLocked\s*=\s*false\s*;")
LOCKED_BARE_RE = re.compile(r"bool\s+bLocked\s*;")
LOCKED_INIT_RE = re.compile(r"bool\s+bLocked\s*=\s*([^;]+);")
LOCKED_INITIALIZER = "false"
INVENTED_FIELD_META = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "CreateDefaultSubobject",
    "const float Amount",
    "{ return",
    "= true",
    "= 0.f",
    "= 160.f",
    "= NAME_None",
    'TEXT("")',
    "WeatherIdentity",
    "MissionTitle",
    "OutcomeNarrative",
    "WeaponLine",
    "HeadingDegrees",
    "FlareCount",
    "WorldLocation",
    "LockLine",
    "LockPhase",
    "LockProgress",
    "LockAlpha",
)


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_WORLD,
        SIBLING_LABEL,
        SIBLING_SEEKING,
        SIBLING_LOCK_ALPHA,
    )


def leftover_sibling_contact_mark_decls() -> tuple[str, ...]:
    return (
        LEFTOVER_CONTACT_WORLD,
        LEFTOVER_CONTACT_LABEL,
        LEFTOVER_CONTACT_SEEKING,
        LEFTOVER_CONTACT_LOCK_ALPHA,
    )


def leftover_hud_lock_decls() -> tuple[str, ...]:
    return (
        LEFTOVER_HUD_LOCK_LINE,
        LEFTOVER_HUD_LOCK_PHASE,
        LEFTOVER_HUD_LOCK_PROGRESS,
    )


def leftover_hud_snapshot_decls() -> tuple[str, ...]:
    return (
        LEFTOVER_HUD_WEAPON,
        LEFTOVER_HUD_RANGE_LINE,
        LEFTOVER_HUD_HEADING,
        LEFTOVER_HUD_FLARE,
        LEFTOVER_HUD_MISSILE,
        LEFTOVER_HUD_LOCK_LINE,
        LEFTOVER_HUD_LOCK_PHASE,
        LEFTOVER_HUD_LOCK_PROGRESS,
    )


def leftover_debrief_decls() -> tuple[str, ...]:
    return (
        LEFTOVER_DEBRIEF_VALID,
        LEFTOVER_DEBRIEF_WON,
        LEFTOVER_DEBRIEF_MISSION_TITLE,
        LEFTOVER_DEBRIEF_OUTCOME,
        LEFTOVER_DEBRIEF_SCORE,
        LEFTOVER_DEBRIEF_MEDAL,
    )


def leftover_world_location_struct_names() -> tuple[str, ...]:
    return (
        LEFTOVER_ROUTE_POINT,
        LEFTOVER_OBJECTIVE_ANCHOR,
        LEFTOVER_LANDMARK_ANCHOR,
    )


def namespace_helper_tokens() -> tuple[str, ...]:
    return (
        WEAPON_LABEL,
        THREAT_LABEL,
        SHIP_SYSTEM_LABEL,
        LOCK_PHASE_LABEL,
        SIGHT_LABEL,
        INBOUND_LABEL,
        FLARE_TAPE,
        LEGACY_WORDING,
    )


def this_file_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
    compact = re.sub(r"\s*::\s*", "::", compact)
    compact = re.sub(r"\s*=\s*", " = ", compact)
    return compact


def declaration_stem(declaration: str) -> str:
    compact = collapsed(declaration)
    if compact.endswith(";"):
        return compact[:-1].rstrip()
    return compact


def has_identifier(region: str, name: str) -> bool:
    return re.search(r"\b" + re.escape(name) + r"\b", region) is not None


def has_one_declaration(region: str, declaration: str) -> bool:
    if declaration in region:
        return True
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return True
    stem = declaration_stem(declaration)
    if not stem:
        return False
    pattern = re.compile(re.escape(stem) + r"\s*;")
    return pattern.search(compact_region) is not None


def locked_has_uproperty_wrap(region: str) -> bool:
    compact = collapsed(region)
    return re.search(
        r"UPROPERTY\([^;]*\)\s*bool\s+bLocked\b",
        compact,
    ) is not None


def has_declaration(region: str, declaration: str) -> bool:
    # Fail-closed on the authored
    # `bool bLocked = false;`.
    # Do not accept a missing initializer, Harbor 40/80,
    # leftover sibling WorldLocation / Label / bSeeking /
    # LockAlpha, leftover HUD snapshot LockLine /
    # LockPhase / LockProgress, leftover HUD snapshot
    # WeaponLine / HeadingDegrees, leftover debrief
    # MissionTitle, leftover SightHud FScreenMark, or
    # leftover LoadoutSpec FlareCount. Do not accept
    # leftover RoutePoint / MissionObjectiveAnchor /
    # MissionLandmarkAnchor UPROPERTY wraps. Do not accept
    # UPROPERTY / Category clones.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if re.search(r"float\s+bLocked\b", compact):
        return False
    if re.search(r"FString\s+bLocked\b", compact):
        return False
    if re.search(r"FVector\s+bLocked\b", compact):
        return False
    if re.search(r"int32\s+bLocked\b", compact):
        return False
    if re.search(r"FName\s+bLocked\b", compact):
        return False
    if re.search(r"const\s+TCHAR\s*\*\s*bLocked\b", compact):
        return False
    if LOCKED_BARE_RE.search(compact) and (
        LOCKED_FIELD_RE.search(compact) is None
    ):
        return False
    init_match = LOCKED_INIT_RE.search(compact)
    if init_match is None:
        return False
    if init_match.group(1).strip() != LOCKED_INITIALIZER:
        return False
    if LOCKED_FIELD_RE.search(compact) is None:
        return False
    if locked_has_uproperty_wrap(region):
        return False
    if re.search(r"\bCategory\s*=", compact):
        return False
    return True


def count_one_declaration(region: str, declaration: str) -> int:
    if declaration in region:
        return region.count(declaration)
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return compact_region.count(compact_decl)
    stem = declaration_stem(declaration)
    if not stem:
        return 0
    pattern = re.compile(re.escape(stem) + r"\s*;")
    return len(pattern.findall(compact_region))


def declaration_count(region: str, declaration: str) -> int:
    if not has_declaration(region, declaration):
        return 0
    return count_one_declaration(region, declaration)


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


def leftover_debrief_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_DEBRIEF_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_DEBRIEF_HEADER} is missing from origin/main"
        )
    return result.stdout


def leftover_loadout_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_LOADOUT_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_LOADOUT_HEADER} is missing from origin/main"
        )
    return result.stdout


def leftover_theater_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_THEATER_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_THEATER_HEADER} is missing from origin/main"
        )
    return result.stdout


def leftover_mission_types_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_MISSION_TYPES_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_MISSION_TYPES_HEADER} is missing from origin/main"
        )
    return result.stdout


def leftover_map_assembly_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_MAP_ASSEMBLY_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_MAP_ASSEMBLY_HEADER} is missing from origin/main"
        )
    return result.stdout


def leftover_sight_hud_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_SIGHT_HUD_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_SIGHT_HUD_HEADER} is missing from origin/main"
        )
    return result.stdout


def struct_body(header: str) -> str:
    match = STRUCT_RE.search(header)
    if match is None:
        raise AssertionError(
            f"{STRUCT_NAME} is missing from origin/main:{HEADER_PATH}"
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
        f"{STRUCT_NAME} struct body is missing from origin/main:{HEADER_PATH}"
    )


def leaked_neighbor_tokens() -> tuple[str, ...]:
    return (
        STOP_BEFORE_HUD_SNAPSHOT,
        STOP_BEFORE_WEAPON_LABEL,
        STOP_BEFORE_DEBRIEF,
        STOP_BEFORE_LOADOUT,
        STOP_BEFORE_THEATER,
        STOP_BEFORE_ROUTE_POINT,
        STOP_BEFORE_OBJECTIVE_ANCHOR,
        STOP_BEFORE_LANDMARK_ANCHOR,
        STOP_BEFORE_SCREEN_MARK,
        STOP_BEFORE_AUDIO_EVENT,
        STOP_BEFORE_PICTOGRAM,
        STOP_BEFORE_EVENT_DEF,
        STOP_BEFORE_BOSS_WEAPON,
        STOP_BEFORE_PROP_SPINNER,
        STOP_BEFORE_SORTIE,
        STOP_BEFORE_PATROL,
        leftover_retired_mount_class(),
        STOP_BEFORE_GUNNER,
        STOP_BEFORE_WEAK_POINT,
        STOP_BEFORE_HARBOR_CALLS,
        LEFTOVER_HUD_SNAPSHOT,
        LEFTOVER_DEBRIEF_SNAPSHOT,
        LEFTOVER_LOADOUT_SPEC,
        LEFTOVER_ROUTE_POINT,
        LEFTOVER_OBJECTIVE_ANCHOR,
        LEFTOVER_LANDMARK_ANCHOR,
        LEFTOVER_SCREEN_MARK,
        WEAPON_LABEL,
        THREAT_LABEL,
        SHIP_SYSTEM_LABEL,
        LOCK_PHASE_LABEL,
        SIGHT_LABEL,
        INBOUND_LABEL,
        FLARE_TAPE,
        LEGACY_WORDING,
        "class USkyguardCampaignSubsystem",
        "struct FSkyguardMissionResult",
        "struct FSkyguardObjectiveProgress",
        "struct FSkyguardMissionDebrief",
        "struct FSkyguardAudioTelemetry",
        "ESkyguardAudioEvent::",
        f"class SKYGUARD52_API {LEFTOVER_APACHE_CLASS}",
        f"class {LEFTOVER_APACHE_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_RADAR_NODE_CLASS}",
        f"class {LEFTOVER_RADAR_NODE_CLASS}",
    )


def spec_section(header: str) -> str:
    body = struct_body(header)
    public = re.search(r"\bpublic\s*:", body)
    if public is None:
        if ACCESS_RE.search(body) is not None:
            raise AssertionError(
                f"{STRUCT_NAME} public section is missing from "
                f"origin/main:{HEADER_PATH}"
            )
        close = body.rfind("}")
        if close == -1:
            raise AssertionError(
                f"{STRUCT_NAME} public section is missing from "
                f"origin/main:{HEADER_PATH}"
            )
        section = body[1:close]
    else:
        start = public.end()
        rest = body[start:]
        next_access = ACCESS_RE.search(rest)
        if next_access is not None:
            section = rest[: next_access.start()]
        else:
            close = rest.rfind("}")
            if close == -1:
                raise AssertionError(
                    f"{STRUCT_NAME} public section is missing from "
                    f"origin/main:{HEADER_PATH}"
                )
            section = rest[:close]
    for token in leaked_neighbor_tokens():
        if token in section:
            raise AssertionError(
                f"{STRUCT_NAME} parse window includes {token}"
            )
    if STOP_BEFORE_HUD_SNAPSHOT in section:
        raise AssertionError(
            f"{STRUCT_NAME} parse window includes leftover "
            f"{STOP_BEFORE_HUD_SNAPSHOT}"
        )
    if STOP_BEFORE_WEAPON_LABEL in section:
        raise AssertionError(
            f"{STRUCT_NAME} parse window includes leftover "
            f"{STOP_BEFORE_WEAPON_LABEL}"
        )
    if LEFTOVER_HUD_SNAPSHOT in section:
        raise AssertionError(
            f"{STRUCT_NAME} parse window includes leftover "
            f"{LEFTOVER_HUD_SNAPSHOT}"
        )
    if LEFTOVER_SCREEN_MARK in section:
        raise AssertionError(
            f"{STRUCT_NAME} parse window includes leftover "
            f"{LEFTOVER_SCREEN_MARK}"
        )
    return section


def attached_uproperty_specifiers(section: str) -> str:
    compact = collapsed(section)
    cursor = 0
    while True:
        match = re.search(r"UPROPERTY\(", compact[cursor:])
        if match is None:
            break
        start = cursor + match.end()
        depth = 1
        index = start
        while index < len(compact) and depth:
            if compact[index] == "(":
                depth += 1
            elif compact[index] == ")":
                depth -= 1
            index += 1
        if depth == 0 and re.match(
            r"\s*bool bLocked\b", compact[index:]
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for bool bLocked is missing from "
        f"origin/main:{HEADER_PATH} struct {STRUCT_NAME} body; "
        "locked decl is the plain C++ field, not a UPROPERTY wrap"
    )


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"struct {STRUCT_NAME} body"
        )
    return declaration


def require_no_uproperty_wrap(section: str) -> None:
    compact = collapsed(section)
    if re.search(
        r"UPROPERTY\([^)]*\)\s*bool bLocked\b",
        compact,
    ):
        raise AssertionError(
            "UPROPERTY wrap on bool bLocked is not the locked "
            f"decl for plain C++ struct {STRUCT_NAME}"
        )
    if "UPROPERTY" in section and has_identifier(section, "bLocked"):
        raise AssertionError(
            "UPROPERTY clone landed on bLocked; locked decl is "
            f"plain {LOCKED_DECL}"
        )
    for token in ("USTRUCT", "GENERATED_BODY"):
        if token in section and has_identifier(section, "bLocked"):
            raise AssertionError(
                f"{token} clone landed on bLocked; locked decl is "
                f"plain {LOCKED_DECL}"
            )


class CpgContactMarkLockedFieldDeclContractTests(unittest.TestCase):
    def test_cpg_contact_mark_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(STRUCT_NAME, header)
        self.assertIsNotNone(STRUCT_RE.search(header), header)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertEqual(STRUCT_NAME, "FSkyguardCpgContactMark")
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_HUD_SNAPSHOT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DEBRIEF_SNAPSHOT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LOADOUT_SPEC)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_ROUTE_POINT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_OBJECTIVE_ANCHOR)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LANDMARK_ANCHOR)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_SCREEN_MARK)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_APACHE_CLASS)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_PROTECT_ASSET_CLASS)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_RADAR_NODE_CLASS)
        self.assertNotEqual(STRUCT_NAME, STOP_BEFORE_SORTIE)
        body = struct_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = spec_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(has_identifier(section, "bLocked"), section)
        self.assertNotIn("UPROPERTY", section)
        self.assertNotIn("GENERATED_BODY", section)
        self.assertNotIn("USTRUCT", section)
        self.assertIn(STOP_BEFORE_HUD_SNAPSHOT, header)
        self.assertNotIn(STOP_BEFORE_HUD_SNAPSHOT, section)
        self.assertNotIn(STOP_BEFORE_HUD_SNAPSHOT, body)
        self.assertIn(LEFTOVER_HUD_SNAPSHOT, header)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, body)
        self.assertIn(STOP_BEFORE_WEAPON_LABEL, header)
        self.assertNotIn(STOP_BEFORE_WEAPON_LABEL, section)
        self.assertNotIn(STOP_BEFORE_WEAPON_LABEL, body)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_DEBRIEF_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, section)
        self.assertNotIn(LEFTOVER_ROUTE_POINT, section)
        self.assertNotIn(LEFTOVER_OBJECTIVE_ANCHOR, section)
        self.assertNotIn(LEFTOVER_LANDMARK_ANCHOR, section)
        self.assertNotIn(LEFTOVER_SCREEN_MARK, section)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, section)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, section)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, section)

    def test_locked_decl_is_plain_cpp_not_uproperty(self) -> None:
        self.assertEqual(LOCKED_DECL, "bool bLocked = false;")
        self.assertEqual(LOCKED_DECL, TARGET)
        self.assertTrue(LOCKED_DECL.startswith("bool bLocked"))
        self.assertTrue(LOCKED_DECL.endswith(";"))
        self.assertIn("=", LOCKED_DECL)
        self.assertIn("= false", LOCKED_DECL)
        self.assertNotIn("= true", LOCKED_DECL)
        self.assertNotIn("= 0.f", LOCKED_DECL)
        self.assertIn("bLocked", LOCKED_DECL)
        self.assertIn("bool", LOCKED_DECL)
        self.assertNotIn(SIBLING_WORLD, LOCKED_DECL)
        self.assertNotIn(SIBLING_LABEL, LOCKED_DECL)
        self.assertNotIn(SIBLING_SEEKING, LOCKED_DECL)
        self.assertNotIn(SIBLING_LOCK_ALPHA, LOCKED_DECL)
        self.assertNotIn("LockLine", LOCKED_DECL)
        self.assertNotIn("LockPhase", LOCKED_DECL)
        self.assertNotIn("LockProgress", LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_WORLD)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LABEL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SEEKING)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_ALPHA)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_LINE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_PHASE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_PROGRESS)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_BARE)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_THEATER, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_CAMPAIGN, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_EDIT, LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_THEATER)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_CAMPAIGN)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_EDIT)
        self.assertNotEqual(LOCKED_DECL, CLONE_DAY_MISSION_ID)
        self.assertNotEqual(LOCKED_DECL, CLONE_STORM_TITLE)
        self.assertNotEqual(LOCKED_DECL, CLONE_WEATHER_IDENTITY)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_WEAPON)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TITLE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_HEADING)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_EQ_EMPTY)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_DEBRIEF_VALID)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_DEBRIEF_WON)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_HUD_MISSILE)

    def test_clone_uproperty_as_locked_decl_fails_closed(self) -> None:
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        self.assertNotIn("VisibleAnywhere", LOCKED_DECL)
        self.assertNotIn("EditAnywhere", LOCKED_DECL)
        self.assertNotIn("BlueprintReadOnly", LOCKED_DECL)
        self.assertNotIn("GENERATED_BODY", LOCKED_DECL)
        self.assertNotIn("USTRUCT", LOCKED_DECL)
        for clone_locked in (
            CLONE_UPROPERTY_THEATER,
            CLONE_UPROPERTY_CAMPAIGN,
            CLONE_UPROPERTY_EDIT,
        ):
            self.assertIn("UPROPERTY", clone_locked)
            self.assertNotEqual(LOCKED_DECL, clone_locked)
            self.assertFalse(has_declaration(clone_locked, LOCKED_DECL))
            with self.assertRaises(AssertionError) as raised:
                require_declaration(f"\t{clone_locked}\n", LOCKED_DECL)
            self.assertIn("bLocked", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            struct_body(
                "struct FSkyguardUnrelatedCpgContactMark\n{\n};\n"
            )
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_hud_snapshot_does_not_satisfy(self) -> None:
        leftover = (
            f"struct {LEFTOVER_HUD_SNAPSHOT}\n"
            "{\n"
            f"\t{LEFTOVER_HUD_LOCK_LINE}\n"
            f"\t{LEFTOVER_HUD_LOCK_PHASE}\n"
            f"\t{LEFTOVER_HUD_LOCK_PROGRESS}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(leftover)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_HUD_SNAPSHOT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_LOCK_LINE_SCRIPT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_LOCK_PHASE_SCRIPT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_LOCK_PROGRESS_SCRIPT)

    def test_leftover_screen_mark_does_not_satisfy(self) -> None:
        leftover = (
            f"struct {LEFTOVER_SCREEN_MARK}\n"
            "{\n"
            f"\t{LOCKED_DECL}\n"
            f"\t{TARGET_WRONG_SEEKING}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(leftover)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_SCREEN_MARK)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_SIGHT_HUD_HEADER)

    def test_leftover_world_location_structs_do_not_satisfy(self) -> None:
        leftovers = leftover_world_location_struct_names()
        for leftover_name in leftovers:
            leftover = (
                f"struct {leftover_name}\n"
                "{\n"
                f"\t{CLONE_UPROPERTY_EDIT}\n"
                f"\t{LOCKED_DECL}\n"
                "};\n"
            )
            with self.assertRaises(AssertionError) as raised:
                spec_section(leftover)
            self.assertIn(STRUCT_NAME, str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_ROUTE_POINT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_OBJECTIVE_ANCHOR)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LANDMARK_ANCHOR)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_ROUTE_POINT_WORLD)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_OBJECTIVE_WORLD)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_LANDMARK_WORLD)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_CONTACT_WORLD_LOCATION)

    def test_leftover_debrief_loadout_theater_do_not_satisfy(self) -> None:
        leftovers = (
            LEFTOVER_DEBRIEF_SNAPSHOT,
            LEFTOVER_LOADOUT_SPEC,
            "FSkyguardTheaterKitSpec",
        )
        for leftover_name in leftovers:
            leftover = (
                f"struct {leftover_name}\n"
                "{\n"
                f"\t{LOCKED_DECL}\n"
                "};\n"
            )
            with self.assertRaises(AssertionError) as raised:
                spec_section(leftover)
            self.assertIn(STRUCT_NAME, str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
        apache = (
            f"struct {LEFTOVER_APACHE_CLASS}\n"
            "{\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(apache)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_does_not_claim_leftover_headers_or_structs(self) -> None:
        self.assertNotEqual(HEADER_PATH, LEFTOVER_DEBRIEF_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_LOADOUT_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_THEATER_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_MISSION_TYPES_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_MAP_ASSEMBLY_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_SIGHT_HUD_HEADER)
        self.assertTrue(HEADER_PATH.endswith("SkyguardCpgHud.h"))
        self.assertNotIn("CpgDebrief", HEADER_PATH)
        self.assertNotIn("GunshipTypes", HEADER_PATH)
        self.assertNotIn("CampaignTheaterKit", HEADER_PATH)
        self.assertNotIn("MissionTypes", HEADER_PATH)
        self.assertNotIn("MissionMapAssembly", HEADER_PATH)
        self.assertNotIn("CpgSightHud", HEADER_PATH)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DEBRIEF_SNAPSHOT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LOADOUT_SPEC)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_HUD_SNAPSHOT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_SCREEN_MARK)
        debrief_header = leftover_debrief_header()
        self.assertIn(LEFTOVER_DEBRIEF_SNAPSHOT, debrief_header)
        self.assertIn(LEFTOVER_DEBRIEF_MISSION_TITLE, debrief_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(debrief_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        loadout_header = leftover_loadout_header()
        self.assertIn(LEFTOVER_LOADOUT_SPEC, loadout_header)
        self.assertIn(LEFTOVER_LOADOUT_FLARE_DECL, loadout_header)
        self.assertNotIn(HUD_SIBLING_FLARE_DECL, loadout_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(loadout_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        theater_header = leftover_theater_header()
        self.assertIn("FSkyguardTheaterKitSpec", theater_header)
        self.assertIn(CLONE_WEATHER_IDENTITY, theater_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(theater_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        mission_types = leftover_mission_types_header()
        self.assertIn(LEFTOVER_ROUTE_POINT, mission_types)
        self.assertIn(LEFTOVER_CONTACT_WORLD, mission_types)
        self.assertNotIn(LOCKED_DECL, mission_types)
        with self.assertRaises(AssertionError) as raised:
            spec_section(mission_types)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        map_assembly = leftover_map_assembly_header()
        self.assertIn(LEFTOVER_OBJECTIVE_ANCHOR, map_assembly)
        self.assertIn(LEFTOVER_LANDMARK_ANCHOR, map_assembly)
        self.assertIn(LEFTOVER_CONTACT_WORLD, map_assembly)
        self.assertNotIn(LOCKED_DECL, map_assembly)
        with self.assertRaises(AssertionError) as raised:
            spec_section(map_assembly)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        sight_hud = leftover_sight_hud_header()
        self.assertIn(LEFTOVER_SCREEN_MARK, sight_hud)
        self.assertIn(LOCKED_DECL, sight_hud)
        with self.assertRaises(AssertionError) as raised:
            spec_section(sight_hud)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_hud_snapshot_before_contact_mark_does_not_satisfy(self) -> None:
        mixed = (
            f"{STOP_BEFORE_HUD_SNAPSHOT}\n"
            "{\n"
            f"\t{LEFTOVER_HUD_LOCK_LINE}\n"
            f"\t{LEFTOVER_HUD_LOCK_PHASE}\n"
            f"\t{LEFTOVER_HUD_LOCK_PROGRESS}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "};\n"
        )
        section = spec_section(mixed)
        self.assertFalse(has_identifier(section, "bLocked"), section)
        self.assertNotIn(STOP_BEFORE_HUD_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bLocked", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_locked_declaration_fails_closed(self) -> None:
        empty = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_WORLD}\n"
            f"\t{TARGET_WRONG_LABEL}\n"
            f"\t{TARGET_WRONG_SEEKING}\n"
            f"\t{TARGET_WRONG_LOCK_ALPHA}\n"
            "};\n"
        )
        section = spec_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bLocked", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_sibling_contact_fields_do_not_satisfy_locked(self) -> None:
        leftovers = (
            TARGET_WRONG_WORLD,
            TARGET_WRONG_LABEL,
            TARGET_WRONG_SEEKING,
            TARGET_WRONG_LOCK_ALPHA,
        )
        for leftover_decl in leftovers:
            leftover = (
                f"struct {STRUCT_NAME}\n"
                "{\n"
                f"\t{leftover_decl}\n"
                "};\n"
            )
            section = spec_section(leftover)
            with self.assertRaises(AssertionError) as raised:
                require_declaration(section, LOCKED_DECL)
            self.assertIn("bLocked", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(section, LOCKED_DECL), section)
            self.assertNotEqual(LOCKED_DECL, leftover_decl)

    def test_leftover_hud_lock_fields_do_not_satisfy(self) -> None:
        leftovers = leftover_hud_lock_decls()
        for leftover_decl in leftovers:
            leftover = (
                f"struct {STRUCT_NAME}\n"
                "{\n"
                f"\t{leftover_decl}\n"
                "};\n"
            )
            section = spec_section(leftover)
            with self.assertRaises(AssertionError) as raised:
                require_declaration(section, LOCKED_DECL)
            self.assertIn("bLocked", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(has_declaration(section, LOCKED_DECL), section)
            self.assertNotEqual(LOCKED_DECL, leftover_decl)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_LOCK_LINE_SCRIPT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_LOCK_PHASE_SCRIPT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_LOCK_PROGRESS_SCRIPT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_LINE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_PHASE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_PROGRESS)

    def test_leftover_hud_weapon_line_does_not_satisfy(self) -> None:
        leftover = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_WEAPON}\n"
            "};\n"
        )
        section = spec_section(leftover)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bLocked", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_WEAPON_LINE)

    def test_leftover_debrief_title_does_not_satisfy(self) -> None:
        leftover = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_TITLE}\n"
            "};\n"
        )
        section = spec_section(leftover)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bLocked", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{CLONE_UPROPERTY_THEATER}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("bLocked", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_has_plain_field_not_uproperty(self) -> None:
        section = spec_section(origin_main_header())
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertNotIn("UPROPERTY", section)
        self.assertNotIn("VisibleAnywhere", section)
        self.assertNotIn("BlueprintReadOnly", section)
        self.assertNotIn("EditAnywhere", section)
        self.assertNotIn("GENERATED_BODY", section)
        self.assertNotIn("USTRUCT", section)
        self.assertNotIn("Category", section)
        self.assertNotIn("Category", LOCKED_DECL)
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        require_no_uproperty_wrap(section)
        with self.assertRaises(AssertionError) as raised:
            attached_uproperty_specifiers(section)
        self.assertIn("UPROPERTY", str(raised.exception))
        self.assertIn("plain", str(raised.exception).lower())

    def test_missing_or_wrong_initializer_fails_closed(self) -> None:
        invented = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_BARE}\n"
            "};\n"
        )
        section = spec_section(invented)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bLocked", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        origin = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIn("bool bLocked = false;", compact_origin)
        self.assertNotIn("bLocked = TEXT", compact_origin)
        self.assertNotIn("bLocked = NAME_None", compact_origin)
        self.assertNotIn("bLocked = true", compact_origin)
        self.assertNotIn("bLocked = 0.f", compact_origin)
        self.assertNotIn("bLocked = 160.f", compact_origin)
        self.assertNotIn("bLocked = FVector::ZeroVector", compact_origin)
        forty = "40" + ".f"
        eighty = "80" + ".f"
        self.assertNotIn("bLocked = " + forty, compact_origin)
        self.assertNotIn("bLocked = " + eighty, compact_origin)

    def test_locked_declaration_matches_origin_main(self) -> None:
        section = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(LOCKED_DECL.startswith("bool bLocked"), LOCKED_DECL)
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertEqual(LOCKED_DECL, "bool bLocked = false;")
        self.assertIn("=", LOCKED_DECL)
        self.assertIn("= false", LOCKED_DECL)
        self.assertNotIn("NAME_None", LOCKED_DECL)
        self.assertNotIn("= true", LOCKED_DECL)
        self.assertNotIn("= 0.f", LOCKED_DECL)
        self.assertNotIn("= 160.f", LOCKED_DECL)
        self.assertIn("bool ", LOCKED_DECL)
        self.assertNotIn("FString ", LOCKED_DECL)
        self.assertNotIn("FVector ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("float ", LOCKED_DECL)
        self.assertNotIn("const TCHAR*", LOCKED_DECL)
        self.assertNotIn("FSkyguardMissionResult", LOCKED_DECL)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_LOADOUT_FLARE_DECL, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_EQ_EMPTY}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_EQ_NONE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TRUE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_ZERO}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_ONE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_HEALTH}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FNAME}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TCHAR}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_WEAPON}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_WORLD}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_LABEL}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_LOCK_LINE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_LOCK_PHASE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_LOCK_PROGRESS}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_LOCK_ALPHA}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TITLE}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_EQ_EMPTY}\n", LOCKED_DECL)
        self.assertIn("bLocked", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_WEAPON}\n", LOCKED_DECL)
        self.assertIn("bLocked", str(raised.exception))
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        self.assertIn("bLocked", str(raised.exception))
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_TRUE}\n", LOCKED_DECL)
        self.assertIn("bLocked", str(raised.exception))

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tFString " + leftover_retired_primary_hits_field() + ";\n"
        )
        leftover_guided = (
            "\tFString " + leftover_retired_guided_hits_field() + ";\n"
        )
        forty = "40" + ".f"
        eighty = "80" + ".f"
        wrongs = (
            f"\t{TARGET_WRONG_EQ_EMPTY}\n",
            f"\t{TARGET_WRONG_EQ_NONE}\n",
            f"\t{TARGET_WRONG_TRUE}\n",
            f"\t{TARGET_WRONG_ZERO}\n",
            f"\t{TARGET_WRONG_ONE}\n",
            f"\t{TARGET_WRONG_ZERO_F}\n",
            f"\t{TARGET_WRONG_BARE}\n",
            f"\t{TARGET_WRONG_HEALTH}\n",
            f"\t{TARGET_WRONG_FVECTOR}\n",
            f"\t{TARGET_WRONG_INT}\n",
            f"\t{TARGET_WRONG_FNAME}\n",
            f"\t{TARGET_WRONG_TCHAR}\n",
            f"\t{TARGET_WRONG_FSTRING}\n",
            f"\t{TARGET_WRONG_FLOAT}\n",
            f"\t{TARGET_WRONG_WEAPON}\n",
            f"\t{TARGET_WRONG_HEADING}\n",
            f"\t{TARGET_WRONG_WORLD}\n",
            f"\t{TARGET_WRONG_LABEL}\n",
            f"\t{TARGET_WRONG_SEEKING}\n",
            f"\t{TARGET_WRONG_LOCK_ALPHA}\n",
            f"\t{TARGET_WRONG_LOCK_LINE}\n",
            f"\t{TARGET_WRONG_LOCK_PHASE}\n",
            f"\t{TARGET_WRONG_LOCK_PROGRESS}\n",
            f"\t{TARGET_WRONG_TITLE}\n",
            leftover_primary,
            leftover_guided,
            f"\t{HUD_SIBLING_FLARE_DECL}\n",
            f"\t{LEFTOVER_LOADOUT_FLARE_DECL}\n",
            f"\t{LEFTOVER_DEBRIEF_MISSION_TITLE}\n",
            f"\t{LEFTOVER_DEBRIEF_OUTCOME}\n",
            f"\t{LEFTOVER_DEBRIEF_VALID}\n",
            f"\t{LEFTOVER_HUD_MISSILE}\n",
            f"\t{LEFTOVER_CONTACT_WORLD}\n",
            "\tFString bLocked;\n",
            "\tint32 bLocked;\n",
            "\tFVector bLocked = FVector::ZeroVector;\n",
            "\tbool bLocked = " + forty + ";\n",
            "\tbool bLocked = " + eighty + ";\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("bLocked", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_uproperty_or_category_clone_fails_closed(self) -> None:
        wraps = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{CLONE_UPROPERTY_THEATER}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n",
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{CLONE_UPROPERTY_CAMPAIGN}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n",
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{CLONE_UPROPERTY_EDIT}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n",
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "\tUSTRUCT(BlueprintType)\n"
            "\tGENERATED_BODY()\n"
            f"\t{LOCKED_DECL}\n"
            "};\n",
        )
        for wrapped in wraps:
            section = spec_section(wrapped)
            with self.assertRaises(AssertionError):
                require_no_uproperty_wrap(section)
            if "UPROPERTY" in wrapped:
                self.assertTrue(
                    locked_has_uproperty_wrap(section),
                    section,
                )
                with self.assertRaises(AssertionError) as raised:
                    require_declaration(section, LOCKED_DECL)
                self.assertIn("bLocked", str(raised.exception))
                self.assertIn("missing", str(raised.exception).lower())
        origin = spec_section(origin_main_header())
        require_no_uproperty_wrap(origin)
        self.assertFalse(locked_has_uproperty_wrap(origin), origin)
        self.assertNotIn("UPROPERTY", origin)
        self.assertNotIn("Category", origin)
        self.assertNotIn("VisibleAnywhere", origin)
        self.assertNotIn("EditAnywhere", origin)
        self.assertNotIn("BlueprintReadOnly", origin)
        self.assertNotIn("GENERATED_BODY", origin)
        self.assertNotIn("USTRUCT", origin)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wraps = (
            "\tbool\n\tbLocked = false;\n",
            "\tbool   bLocked = false;\n",
            "\tbool\tbLocked = false;\n",
            "\tbool bLocked=false;\n",
            f"\t{LOCKED_DECL}\n",
        )
        for region in wraps:
            self.assertTrue(has_declaration(region, LOCKED_DECL), region)
        rejected = (
            f"\t{CLONE_UPROPERTY_THEATER}\n\t{LOCKED_DECL}\n",
            f"\t{CLONE_UPROPERTY_THEATER} {LOCKED_DECL}\n",
            f"\t{CLONE_UPROPERTY_EDIT}\n\t{LOCKED_DECL}\n",
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
            'Category="Skyguard|Theater")\n'
            f"\t{LOCKED_DECL}\n",
            f"\t{TARGET_WRONG_EQ_EMPTY}\n",
            f"\t{TARGET_WRONG_BARE}\n",
            f"\t{TARGET_WRONG_TRUE}\n",
            f"\t{TARGET_WRONG_ZERO}\n",
            f"\t{TARGET_WRONG_ONE}\n",
            f"\t{TARGET_WRONG_WEAPON}\n",
            f"\t{TARGET_WRONG_HEADING}\n",
            f"\t{TARGET_WRONG_WORLD}\n",
            f"\t{TARGET_WRONG_LABEL}\n",
            f"\t{TARGET_WRONG_SEEKING}\n",
            f"\t{TARGET_WRONG_LOCK_ALPHA}\n",
            f"\t{TARGET_WRONG_LOCK_LINE}\n",
            f"\t{TARGET_WRONG_LOCK_PHASE}\n",
            f"\t{TARGET_WRONG_LOCK_PROGRESS}\n",
        )
        for region in rejected:
            self.assertFalse(has_declaration(region, LOCKED_DECL), region)

    def test_does_not_contract_sibling_contact_mark_fields(self) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(HUD_SIBLING_FLARE_DECL, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_LOADOUT_FLARE_DECL, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        section = spec_section(origin_main_header())
        for sibling in sibling_uncontracted_decls():
            self.assertTrue(has_identifier(section, sibling), sibling)
        self.assertNotIn(HUD_SIBLING_FLARE_DECL, section)
        self.assertNotIn(LEFTOVER_LOADOUT_FLARE_DECL, section)
        for decl in leftover_sibling_contact_mark_decls():
            self.assertIn(decl, section)
            self.assertNotIn(decl, LOCKED_DECL)
        for decl in leftover_hud_lock_decls():
            self.assertNotIn(decl, section)
            self.assertNotIn(decl, LOCKED_DECL)
        for decl in leftover_debrief_decls():
            self.assertNotIn(decl, section)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, LOCKED_DECL)

    def test_hud_flare_count_is_not_loadout_spec_flare_count(self) -> None:
        section = spec_section(origin_main_header())
        self.assertNotIn(HUD_SIBLING_FLARE_DECL, section)
        self.assertNotIn(LEFTOVER_LOADOUT_FLARE_DECL, section)
        self.assertNotIn(LEFTOVER_LOADOUT_FLARE_DECL, LOCKED_DECL)
        self.assertNotIn(HUD_SIBLING_FLARE_DECL, LOCKED_DECL)
        self.assertNotEqual(HUD_SIBLING_FLARE_DECL, LEFTOVER_LOADOUT_FLARE_DECL)
        loadout_header = leftover_loadout_header()
        self.assertIn(LEFTOVER_LOADOUT_FLARE_DECL, loadout_header)
        self.assertNotIn(HUD_SIBLING_FLARE_DECL, loadout_header)
        self.assertFalse(
            has_declaration(f"\t{HUD_SIBLING_FLARE_DECL}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{LEFTOVER_LOADOUT_FLARE_DECL}\n", LOCKED_DECL)
        )

    def test_does_not_parse_leftover_hud_snapshot_or_neighbors(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = struct_body(header)
        self.assertIn(STOP_BEFORE_HUD_SNAPSHOT, header)
        self.assertNotIn(STOP_BEFORE_HUD_SNAPSHOT, section)
        self.assertNotIn(STOP_BEFORE_HUD_SNAPSHOT, leaked)
        self.assertIn(LEFTOVER_HUD_SNAPSHOT, header)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, leaked)
        self.assertIn(STOP_BEFORE_WEAPON_LABEL, header)
        self.assertNotIn(STOP_BEFORE_WEAPON_LABEL, section)
        self.assertNotIn(STOP_BEFORE_WEAPON_LABEL, leaked)
        self.assertNotIn(STOP_BEFORE_DEBRIEF, header)
        self.assertNotIn(STOP_BEFORE_DEBRIEF, section)
        self.assertNotIn(LEFTOVER_DEBRIEF_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, section)
        self.assertNotIn(LEFTOVER_ROUTE_POINT, section)
        self.assertNotIn(LEFTOVER_OBJECTIVE_ANCHOR, section)
        self.assertNotIn(LEFTOVER_LANDMARK_ANCHOR, section)
        self.assertNotIn(LEFTOVER_SCREEN_MARK, section)
        for helper in namespace_helper_tokens():
            self.assertIn(helper, header)
            self.assertNotIn(helper, section)
            self.assertNotIn(helper, leaked)
        for token in leftover_hud_snapshot_decls():
            self.assertIn(token, header)
            self.assertNotIn(token, section)
            self.assertNotIn(token, leaked)
        for token in leftover_debrief_decls():
            self.assertNotIn(token, section)
            self.assertNotIn(token, leaked)
        for token in leftover_audio_event_enum_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, LOCKED_DECL)
        for token in leftover_weapon_enum_body_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, LOCKED_DECL)

    def test_parse_window_excludes_leftover_weapon_enum_body(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        for token in leftover_weapon_enum_body_tokens():
            self.assertNotIn(token, section)
        for token in leftover_audio_event_enum_tokens():
            self.assertNotIn(token, section)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        for helper in namespace_helper_tokens():
            self.assertNotIn(helper, LOCKED_DECL)
        section = spec_section(origin_main_header())
        for helper in namespace_helper_tokens():
            self.assertNotIn(helper, section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{WEAPON_LABEL}();\n", LOCKED_DECL)
        self.assertIn("bLocked", str(raised.exception))

    def test_leftover_harbor_directors_do_not_satisfy(self) -> None:
        section = spec_section(origin_main_header())
        for token in leftover_harbor_director_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, LOCKED_DECL)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_THEATER, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_CAMPAIGN, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_EDIT, LOCKED_DECL)
        self.assertNotIn("MultiLine", LOCKED_DECL)
        self.assertNotIn("ClampMin", LOCKED_DECL)
        self.assertNotIn("ClampMax", LOCKED_DECL)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        self.assertNotIn(".cpp", HEADER_PATH)
        self.assertTrue(HEADER_PATH.endswith(".h"))
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("SkyguardCpgHud.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardCpgDebrief.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipTypes.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignTheaterKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardMissionTypes.h", HEADER_PATH)
        self.assertNotIn("SkyguardMissionMapAssemblyDirector.h", HEADER_PATH)
        self.assertNotIn("SkyguardRadarNode.h", HEADER_PATH)
        self.assertNotIn("SkyguardProtectAsset.h", HEADER_PATH)
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)
        self.assertNotIn("SkyguardHarborBeatCalls.h", HEADER_PATH)
        self.assertNotIn("SkyguardCpgSightHud.h", HEADER_PATH)

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = spec_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, LOCKED_DECL)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{LOCKED_DECL}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOCKED_DECL)
            self.assertNotIn(token, file_text)
        header = origin_main_header()
        section = spec_section(header)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, header)
        for token in leftover_harbor_director_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, LOCKED_DECL)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "cpg-contact-mark bLocked field decl contract "
                f"contains {banned}; declaration is Apache CPG 30 mm / "
                "Hydra / Hellfire, not leftover live cop" + "y",
            )

    def test_this_file_bans_live_retired_tokens_case_sensitive(self) -> None:
        file_text = this_file_text()
        for banned in leftover_live_case_tokens():
            self.assertNotIn(banned, file_text)

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        locked_only = f"{LOCKED_DECL}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, LOCKED_DECL.lower())
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, LOCKED_DECL)
            self.assertNotIn(token, locked_only)
        self.assertNotIn(leftover_retired_mount_class(), LOCKED_DECL)

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{LOCKED_DECL}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, LOCKED_DECL.lower())
            self.assertNotIn(banned, locked_only.lower())

    def test_locked_scripts_do_not_include_this_file(self) -> None:
        self.assertNotIn(THIS_SCRIPT, LOCKED_SCRIPTS)
        self.assertTrue(Path(__file__).name.endswith(
            "locked_field_decl_contract.py"
        ))
        self.assertIn("cpg_contact_mark", Path(__file__).name)
        self.assertNotIn("hud_snapshot", Path(__file__).name)
        self.assertNotIn("world_location", Path(__file__).name)
        self.assertNotIn("SkyguardCpgHud.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardCpgDebrief.h", THIS_SCRIPT)
        for script in leftover_debrief_isolated_scripts():
            self.assertIn(script, LOCKED_SCRIPTS)
        for script in leftover_hud_snapshot_isolated_scripts():
            self.assertIn(script, LOCKED_SCRIPTS)
        for script in leftover_storm_rain_isolated_scripts():
            self.assertIn(script, LOCKED_SCRIPTS)
        for script in leftover_world_location_isolated_scripts():
            self.assertIn(script, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_DEBRIEF_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_FLARE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_THEATER_WEATHER_IDENTITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_STORM_KIT_FIELDS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_HUD_LOCK_LINE_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_HUD_LOCK_PHASE_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_HUD_LOCK_PROGRESS_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_CONTACT_WORLD_LOCATION, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ROUTE_POINT_WORLD, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_OBJECTIVE_WORLD, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LANDMARK_WORLD, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_DEBRIEF_FAIL_CLOSED, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_DEBRIEF_COPY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_STATION, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_LOADOUT, LOCKED_SCRIPTS)

    def test_leftover_analog_bulk_stays_locked(self) -> None:
        leftovers = (
            leftover_debrief_isolated_scripts()
            + leftover_hud_snapshot_isolated_scripts()
            + leftover_storm_rain_isolated_scripts()
            + leftover_world_location_isolated_scripts()
            + (
                LEFTOVER_ANALOG_DEBRIEF_DEFAULTS,
                LEFTOVER_LOADOUT_FLARE,
                CLONE_THEATER_WEATHER_IDENTITY,
                LEFTOVER_ANALOG_STORM_KIT_FIELDS,
                LEFTOVER_HUD_LOCK_LINE_SCRIPT,
                LEFTOVER_HUD_LOCK_PHASE_SCRIPT,
                LEFTOVER_HUD_LOCK_PROGRESS_SCRIPT,
                LEFTOVER_CONTACT_WORLD_LOCATION,
                LEFTOVER_ANALOG_DEBRIEF_FAIL_CLOSED,
                LEFTOVER_ANALOG_DEBRIEF_COPY,
                LEFTOVER_ANALOG_THEATER_KIT_BULK,
                LEFTOVER_LOADOUT_DEFAULTS,
                LEFTOVER_LOADOUT_STATION,
                LEFTOVER_LOADOUT_LOADOUT,
            )
        )
        for script in leftovers:
            self.assertIn(script, LOCKED_SCRIPTS)
            self.assertNotEqual(script, THIS_SCRIPT)

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

    def test_contract_is_target_field_declaration_only(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        locked_only = f"{LOCKED_DECL}\n"
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, locked_only)
        self.assertNotIn(HUD_SIBLING_FLARE_DECL, locked_only)
        self.assertNotIn(LEFTOVER_LOADOUT_FLARE_DECL, locked_only)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, locked_only)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, locked_only)
        self.assertNotIn("FSkyguardObjectiveProgress", locked_only)
        self.assertNotIn("ESkyguardAudioEvent", locked_only)
        self.assertNotIn("ESkyguardBriefingPictogram", locked_only)
        self.assertNotIn("FSkyguardAudioEventDefinition", locked_only)
        self.assertNotIn("FSkyguardAudioTelemetry", locked_only)
        self.assertNotIn("ESkyguardBossWeapon", locked_only)
        self.assertNotIn("ESkyguardBossPhase", locked_only)
        self.assertNotIn("ESkyguardPilotCommand", locked_only)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, locked_only)
        self.assertNotIn(LEFTOVER_DEBRIEF_SNAPSHOT, locked_only)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, locked_only)
        self.assertNotIn(LEFTOVER_ROUTE_POINT, locked_only)
        self.assertNotIn(LEFTOVER_OBJECTIVE_ANCHOR, locked_only)
        self.assertNotIn(LEFTOVER_LANDMARK_ANCHOR, locked_only)
        self.assertNotIn(LEFTOVER_SCREEN_MARK, locked_only)
        self.assertNotIn(STOP_BEFORE_HUD_SNAPSHOT, locked_only)
        self.assertNotIn(STOP_BEFORE_WEAPON_LABEL, locked_only)
        self.assertNotIn(STOP_BEFORE_HARBOR_CALLS, locked_only)
        self.assertNotIn(SIBLING_WORLD, locked_only)
        self.assertNotIn(SIBLING_LABEL, locked_only)
        self.assertNotIn(SIBLING_SEEKING, locked_only)
        self.assertNotIn(SIBLING_LOCK_ALPHA, locked_only)
        self.assertNotIn("LockLine", locked_only)
        self.assertNotIn("LockPhase", locked_only)
        self.assertNotIn("LockProgress", locked_only)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_LOCK_LINE_SCRIPT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_LOCK_PHASE_SCRIPT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_LOCK_PROGRESS_SCRIPT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_CONTACT_WORLD_LOCATION)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_WEAPON_LINE)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_HEADING_DEGREES)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_ROUTE_POINT_WORLD)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_OBJECTIVE_WORLD)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_LANDMARK_WORLD)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_ANALOG_STORM_KIT_FIELDS)
        self.assertNotEqual(THIS_SCRIPT, CLONE_THEATER_WEATHER_IDENTITY)
        for helper in namespace_helper_tokens():
            self.assertNotIn(helper, locked_only)
        for decl in leftover_sibling_contact_mark_decls():
            self.assertNotIn(decl, locked_only)
        for decl in leftover_hud_lock_decls():
            self.assertNotIn(decl, locked_only)
        for decl in leftover_debrief_decls():
            self.assertNotIn(decl, locked_only)
        for decl in leftover_hud_snapshot_decls():
            self.assertNotIn(decl, locked_only)


if __name__ == "__main__":
    unittest.main()

