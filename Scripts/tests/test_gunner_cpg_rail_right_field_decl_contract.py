# THIS IS leftover-safe ASkyguardGunner CpgRailRight.
# origin/main form: one-line VisibleAnywhere BlueprintReadOnly wrap
# UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
# then BARE `TObjectPtr<UStaticMeshComponent> CpgRailRight;`
# (no initializer).
# THIS IS leftover-safe isolated UPROPERTY with Category.
# Category IS `Skyguard`. VisibleAnywhere IS present.
# BlueprintReadOnly IS present. There is NO default.
# Fail-closed if the UPROPERTY or decl is missing
# or renamed, if Category is missing, or if specifiers
# drop to BlueprintReadWrite / EditAnywhere-only.
# Accept one-line and split-line UPROPERTY wraps.
# Parse CLASS `ASkyguardGunner` protected UPROPERTY
# fields ONLY after `class ASkyguardGunner`.
# Start at `protected:`. Stop BEFORE `private:`.
# Stop BEFORE sibling CpgTedacText as a claimed slot.
# Do NOT claim CpgStation, CpgCockpit, CpgSeatBack,
# CpgSeatPan, CpgKneeLeft, CpgKneeRight, CpgCanopyBow,
# CpgDash, CpgTedac, CpgMpdLeft, CpgMpdRight, CpgEufd,
# CpgTedacBezel, CpgReticleH, CpgReticleV, CpgGripLeft,
# CpgGripRight, CpgConsoleRight, CpgRailLeft, CpgTedacText,
# CpgMpdLeftText, Boom, GunnerCamera, HandMesh.
# Do NOT claim leftover CpgGripRight / CpgGripLeft /
# CpgReticleV / CpgReticleH / CpgTedacBezel as this slot.
# Text slots come AFTER this mesh. Do not lock
# TObjectPtr<UTextRenderComponent> CpgTedacText as this slot.
# CpgRailRight fail-closed if leftover Apache Canopy
# or leftover Apache PilotCanopy — do not lock those.
# Fail-closed leftover Apache GunnerMount / PilotMount /
# EyeMount / WeaponMount.
# Do NOT parse leftover analog apache-aircraft-empty-fail-closed
# (keep bulk in LOCKED_SCRIPTS).
# Do NOT parse leftover Apache UFUNCTION decls.
# Do NOT parse leftover analog apache-hull-collider-field,
# leftover analog apache-mount-fail-closed, leftover analog
# apache-cpg-feel, leftover analog apache-own-ship-systems.
# Do NOT parse leftover analog ASkyguardApacheAircraft
# TObjectPtr mesh/scene UPROPERTY (exhausted through
# EyeMount). Keep those isolated sibling field decls
# in LOCKED_SCRIPTS.
# Do NOT parse leftover ArcadeLook UPROPERTY, leftover
# GuidedLockRules, leftover CampaignMissionSpec, leftover
# Harbor Breaker Approach/Contact/Shore, leftover
# TheaterKit Category Skyguard|Theater, leftover
# ASkyguardGunshipSortieDirector, leftover analog
# campaign-roster-lookup-tests, leftover campaign-roster
# function decls, leftover LoadoutSpec.
# Clone wrap IS VisibleAnywhere BlueprintReadOnly — keep
# those specifiers — but RETARGET hard: Category is
# Skyguard NOT Skyguard|Apache and NOT Skyguard|Theater.
# LOCKED_DECL is `TObjectPtr<UStaticMeshComponent> CpgRailRight;`
# NOT `FName WeatherIdentity;` and NOT
# `float CurrentIntegrity = 140.f`.
# Fail-closed if this test still asserts FName
# WeatherIdentity / Category="Skyguard|Theater" / 160.f
# AS THE LOCKED DECL.
# Fail-closed if locked wrap Category is Skyguard|Apache.
# Mesh slots fail-closed if LOCKED_DECL is
# `TObjectPtr<USceneComponent>` or
# `TObjectPtr<UTextRenderComponent>`.
# CpgRailRight fail-closed if LOCKED_DECL is leftover
# CpgGripRight / CpgGripLeft / CpgReticleV / CpgReticleH /
# CpgTedacBezel / CpgConsoleRight / CpgRailLeft /
# CpgTedacText / CpgEufd / CpgTedac / CpgDash /
# CpgKneeRight / CpgKneeLeft / CpgSeatBack / CpgCockpit /
# CpgStation / CpgSeatPan / CpgCanopyBow / CpgMpdLeft /
# CpgMpdRight / leftover Apache Canopy / leftover
# Apache PilotCanopy.
# Harbor leftover is only the split 40 / 80 float tokens.
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
HEADER_PATH = "Source/Skyguard52/SkyguardGunner.h"
CLASS_NAME = "ASkyguardGunner"
TARGET = "TObjectPtr<UStaticMeshComponent> CpgRailRight;"
TARGET_WRONG_INIT = "TObjectPtr<UStaticMeshComponent> CpgRailRight = nullptr;"
TARGET_WRONG_FALSE = "TObjectPtr<UStaticMeshComponent> CpgRailRight = false;"
TARGET_WRONG_TRUE = "TObjectPtr<UStaticMeshComponent> CpgRailRight = true;"
TARGET_WRONG_SKELETAL = "TObjectPtr<USkeletalMeshComponent> CpgRailRight;"
TARGET_WRONG_FNAME = "FName WeatherIdentity;"
TARGET_WRONG_HEALTH = "float Health = 160.f;"
TARGET_WRONG_SCENE = "TObjectPtr<USceneComponent> CpgRailRight;"
TARGET_WRONG_SEAT_PAN = "TObjectPtr<UStaticMeshComponent> CpgSeatPan;"
TARGET_WRONG_SEAT_BACK = "TObjectPtr<UStaticMeshComponent> CpgSeatBack;"
TARGET_WRONG_KNEE_LEFT = "TObjectPtr<UStaticMeshComponent> CpgKneeLeft;"
TARGET_WRONG_KNEE_RIGHT = "TObjectPtr<UStaticMeshComponent> CpgKneeRight;"
TARGET_WRONG_CANOPY_BOW = "TObjectPtr<UStaticMeshComponent> CpgCanopyBow;"
TARGET_WRONG_DASH = "TObjectPtr<UStaticMeshComponent> CpgDash;"
TARGET_WRONG_MPD_LEFT = "TObjectPtr<UStaticMeshComponent> CpgMpdLeft;"
TARGET_WRONG_MPD_RIGHT = "TObjectPtr<UStaticMeshComponent> CpgMpdRight;"
TARGET_WRONG_TEDAC = "TObjectPtr<UStaticMeshComponent> CpgTedac;"
TARGET_WRONG_TEDAC_BEZEL = "TObjectPtr<UStaticMeshComponent> CpgTedacBezel;"
TARGET_WRONG_EUFD = "TObjectPtr<UStaticMeshComponent> CpgEufd;"
TARGET_WRONG_RETICLE_H = "TObjectPtr<UStaticMeshComponent> CpgReticleH;"
TARGET_WRONG_GRIP_LEFT = "TObjectPtr<UStaticMeshComponent> CpgGripLeft;"
TARGET_WRONG_GRIP_RIGHT = "TObjectPtr<UStaticMeshComponent> CpgGripRight;"
TARGET_WRONG_RETICLE_V = "TObjectPtr<UStaticMeshComponent> CpgReticleV;"
TARGET_WRONG_CONSOLE_RIGHT = "TObjectPtr<UStaticMeshComponent> CpgConsoleRight;"
TARGET_WRONG_RAIL_LEFT = "TObjectPtr<UStaticMeshComponent> CpgRailLeft;"
TARGET_WRONG_TEXT = "TObjectPtr<UTextRenderComponent> CpgRailRight;"
TARGET_WRONG_TEDAC_TEXT = "TObjectPtr<UTextRenderComponent> CpgTedacText;"
TARGET_WRONG_MPD_LEFT_TEXT = "TObjectPtr<UTextRenderComponent> CpgMpdLeftText;"
TARGET_WRONG_HAND_MESH = "TObjectPtr<UStaticMeshComponent> HandMesh;"
TARGET_WRONG_EUFD_TEXT = "TObjectPtr<UTextRenderComponent> CpgEufdText;"
TARGET_WRONG_CANOPY = "TObjectPtr<UStaticMeshComponent> Canopy;"
TARGET_WRONG_PILOT_CANOPY = "TObjectPtr<UStaticMeshComponent> PilotCanopy;"
TARGET_WRONG_CPG_STATION = "TObjectPtr<USceneComponent> CpgStation;"
TARGET_WRONG_CPG_COCKPIT = "TObjectPtr<UStaticMeshComponent> CpgCockpit;"
TARGET_WRONG_SILHOUETTE = "TObjectPtr<UStaticMeshComponent> SilhouetteMesh;"
TARGET_WRONG_FUSELAGE = "TObjectPtr<UStaticMeshComponent> Fuselage;"
TARGET_WRONG_AIRCRAFT_ROOT = "TObjectPtr<USceneComponent> AircraftRoot;"
TARGET_WRONG_THEATER = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Theater")'
)
LOCKED_DECL = TARGET
UPROPERTY_VISIBLE_READONLY = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard")'
)
STOP_BEFORE_PRIVATE = "private:"
STOP_BEFORE_PROTECTED = "protected:"
STOP_BEFORE_MPD_LEFT = "CpgMpdLeft"
STOP_BEFORE_MPD_RIGHT = "CpgMpdRight"
STOP_BEFORE_EUFD = "CpgEufd"
STOP_BEFORE_RETICLE_H = "CpgReticleH"
STOP_BEFORE_GRIP_LEFT = "CpgGripLeft"
STOP_BEFORE_TEDAC_BEZEL = "CpgTedacBezel"
STOP_BEFORE_TEDAC_TEXT = "CpgTedacText"
STOP_BEFORE_FUSELAGE = "Fuselage"
STOP_BEFORE_AUDIO_EVENT = "enum class ESkyguardAudioEvent"
STOP_BEFORE_PICTOGRAM = "enum class ESkyguardBriefingPictogram"
STOP_BEFORE_EVENT_DEF = "struct FSkyguardAudioEventDefinition"
STOP_BEFORE_BOSS_WEAPON = "enum class ESkyguardBossWeapon"
STOP_BEFORE_PROP_SPINNER = "ASkyguardPropSpinner"
STOP_BEFORE_SORTIE = "ASkyguardGunshipSortieDirector"
STOP_BEFORE_PATROL = "ASkyguardPatrolShipBoss"
STOP_BEFORE_GUNNER = "ASkyguardGunner"
STOP_BEFORE_WEAK_POINT = "USkyguardBossWeakPointComponent"
STOP_BEFORE_THEATER_SPEC = "FSkyguardTheaterKitSpec"
STOP_BEFORE_THEATER_ACTOR = "ASkyguardCampaignTheaterKit"
STOP_BEFORE_ARCADE_LOOK = "USkyguardArcadeLookComponent"
STOP_BEFORE_GUIDED_LOCK = "FSkyguardGuidedLockRules"
STOP_BEFORE_MISSION_SPEC = "FSkyguardCampaignMissionSpec"
STOP_BEFORE_LOADOUT_SPEC = "FSkyguardLoadoutSpec"
STOP_BEFORE_ROSTER = "SkyguardCampaignRoster"
GET_OBJECTIVE_RUNTIME = "GetObjectiveRuntime"
ADD_OBJECTIVE_PROGRESS = "AddObjectiveProgress"
BIND_RUNTIME_ACTORS = "BindRuntimeActors"
HANDLE_DRONE_CITY_IMPACT = "HandleDroneCityImpact"
GET_STORM_RAIN_BEAT_KIT = "GetStormRainBeatKit"
SIBLING_CPG_STATION = "CpgStation"
SIBLING_CPG_COCKPIT = "CpgCockpit"
SIBLING_CPG_SEAT_BACK = "CpgSeatBack"
SIBLING_CPG_SEAT_PAN = "CpgSeatPan"
SIBLING_CPG_KNEE_LEFT = "CpgKneeLeft"
SIBLING_CPG_KNEE_RIGHT = "CpgKneeRight"
SIBLING_CPG_CANOPY_BOW = "CpgCanopyBow"
SIBLING_CPG_DASH = "CpgDash"
SIBLING_CPG_TEDAC = "CpgTedac"
SIBLING_BOOM = "Boom"
SIBLING_GUNNER_CAMERA = "GunnerCamera"
SIBLING_CPG_MPD_LEFT = "CpgMpdLeft"
SIBLING_CPG_MPD_RIGHT = "CpgMpdRight"
SIBLING_CPG_EUFD = "CpgEufd"
SIBLING_CPG_TEDAC_BEZEL = "CpgTedacBezel"
SIBLING_CPG_RETICLE_H = "CpgReticleH"
SIBLING_CPG_GRIP_LEFT = "CpgGripLeft"
SIBLING_CPG_GRIP_RIGHT = "CpgGripRight"
SIBLING_CPG_CONSOLE_RIGHT = "CpgConsoleRight"
SIBLING_CPG_RAIL_LEFT = "CpgRailLeft"
SIBLING_CPG_RETICLE_V = "CpgReticleV"
SIBLING_CPG_TEDAC_TEXT = "CpgTedacText"
SIBLING_CPG_MPD_LEFT_TEXT = "CpgMpdLeftText"
SIBLING_HAND_MESH = "HandMesh"
SIBLING_CPG_EUFD_TEXT = "CpgEufdText"
SIBLING_AIRCRAFT_ROOT = "AircraftRoot"
SIBLING_FUSELAGE = "Fuselage"
SIBLING_ROTOR_POWER = "RotorPower"
SIBLING_HOVER_BOB = "HoverBobCentimeters"
SIBLING_MAX_INTEGRITY = "MaxIntegrity"
SIBLING_CURRENT_INTEGRITY = "CurrentIntegrity"
SIBLING_HULL_COLLIDER = "HullCollider"
LEFTOVER_PROTECT_ASSET_CLASS = "ASkyguardProtectAsset"
LEFTOVER_RADAR_NODE_CLASS = "ASkyguardRadarNode"
LEFTOVER_THEATER_KIT_ACTOR = "ASkyguardCampaignTheaterKit"
THIS_SCRIPT = (
    "Scripts/tests/test_gunner_cpg_rail_right"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_SILHOUETTE_MESH = (
    "Scripts/tests/test_apache_silhouette_mesh"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_COCKPIT = (
    "Scripts/tests/test_gunner_cpg_cockpit"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_STATION = (
    "Scripts/tests/test_gunner_cpg_station"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_SEAT_BACK = (
    "Scripts/tests/test_gunner_cpg_seat_back"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_SEAT_PAN = (
    "Scripts/tests/test_gunner_cpg_seat_pan"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_KNEE_LEFT = (
    "Scripts/tests/test_gunner_cpg_knee_left"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_KNEE_RIGHT = (
    "Scripts/tests/test_gunner_cpg_knee_right"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_CANOPY_BOW = (
    "Scripts/tests/test_gunner_cpg_canopy_bow"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_DASH = (
    "Scripts/tests/test_gunner_cpg_dash"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_TEDAC = (
    "Scripts/tests/test_gunner_cpg_tedac"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_MPD_LEFT = (
    "Scripts/tests/test_gunner_cpg_mpd_left"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_MPD_RIGHT = (
    "Scripts/tests/test_gunner_cpg_mpd_right"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_EUFD = (
    "Scripts/tests/test_gunner_cpg_eufd"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_TEDAC_BEZEL = (
    "Scripts/tests/test_gunner_cpg_tedac_bezel"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_RETICLE_H = (
    "Scripts/tests/test_gunner_cpg_reticle_h"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_RETICLE_V = (
    "Scripts/tests/test_gunner_cpg_reticle_v"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_GRIP_LEFT = (
    "Scripts/tests/test_gunner_cpg_grip_left"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_GRIP_RIGHT = (
    "Scripts/tests/test_gunner_cpg_grip_right"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_CANOPY = (
    "Scripts/tests/test_apache_canopy"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_PILOT_CANOPY = (
    "Scripts/tests/test_apache_pilot_canopy"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_AIRCRAFT_CLASS = "ASkyguardApacheAircraft"
LEFTOVER_APACHE_CURRENT_INTEGRITY = (
    "Scripts/tests/test_apache_current_integrity"
    "_field_decl_contract.py"
)
LEFTOVER_APACHE_MAX_INTEGRITY = (
    "Scripts/tests/test_apache_max_integrity"
    "_field_decl_contract.py"
)
CLONE_CURRENT_INTEGRITY = (
    "Scripts/tests/test_protect_asset_current_integrity"
    "_field_decl_contract.py"
)
CLONE_MAX_INTEGRITY = (
    "Scripts/tests/test_protect_asset_max_integrity"
    "_field_decl_contract.py"
)
CLONE_MAX_HEALTH = (
    "Scripts/tests/test_radar_node_max_health"
    "_field_decl_contract.py"
)
CLONE_RESET_INTEGRITY = (
    "Scripts/tests/test_protect_asset_reset_integrity"
    "_decl_contract.py"
)
CLONE_APPLY_DAMAGE = (
    "Scripts/tests/test_protect_asset_apply_damage"
    "_decl_contract.py"
)
CLONE_IS_DESTROYED = (
    "Scripts/tests/test_protect_asset_is_destroyed"
    "_decl_contract.py"
)
CLONE_GET_INTEGRITY_FRACTION = (
    "Scripts/tests/test_protect_asset_get_integrity_fraction"
    "_decl_contract.py"
)
CLONE_RADAR_IS_DESTROYED = (
    "Scripts/tests/test_radar_node_is_destroyed"
    "_decl_contract.py"
)
CLONE_RADAR_APPLY_DAMAGE = (
    "Scripts/tests/test_radar_node_apply_damage"
    "_decl_contract.py"
)
CLONE_RADAR_RESET_NODE = (
    "Scripts/tests/test_radar_node_reset_node"
    "_decl_contract.py"
)
CLONE_PEAK_ACTIVE_VOICES = (
    "Scripts/tests/test_audio_telemetry_peak_active_voices"
    "_field_decl_contract.py"
)
CLONE_PLAYED_EVENTS = (
    "Scripts/tests/test_audio_telemetry_played_events"
    "_field_decl_contract.py"
)
CLONE_REQUESTED_EVENTS = (
    "Scripts/tests/test_audio_telemetry_requested_events"
    "_field_decl_contract.py"
)
CLONE_REJECTED_BY_COOLDOWN = (
    "Scripts/tests/test_audio_telemetry_rejected_by_cooldown"
    "_field_decl_contract.py"
)
CLONE_REJECTED_BY_CONCURRENCY = (
    "Scripts/tests/test_audio_telemetry_rejected_by_concurrency"
    "_field_decl_contract.py"
)
CLONE_REJECTED_MISSING_ASSET = (
    "Scripts/tests/test_audio_telemetry_rejected_missing_asset"
    "_field_decl_contract.py"
)
CLONE_PRIORITY_EVICTIONS = (
    "Scripts/tests/test_audio_telemetry_priority_evictions"
    "_field_decl_contract.py"
)
CLONE_WEAK_POINTS_DESTROYED = (
    "Scripts/tests/test_boss_telemetry_weak_points_destroyed"
    "_field_decl_contract.py"
)
CLONE_PILOT_COMMANDS_ISSUED = (
    "Scripts/tests/test_boss_telemetry_pilot_commands_issued"
    "_field_decl_contract.py"
)
CLONE_HOW_TO_FLY_STEP_ID = (
    "Scripts/tests/test_how_to_fly_row_step_id_field_decl_contract.py"
)
CLONE_HOW_TO_FLY_INPUT_HINT = (
    "Scripts/tests/test_how_to_fly_row_input_hint_field_decl_contract.py"
)
CLONE_HOW_TO_FLY_INSTRUCTION = (
    "Scripts/tests/test_how_to_fly_row_instruction"
    "_field_decl_contract.py"
)
CLONE_CARD_ID = (
    "Scripts/tests/test_briefing_card_card_id_field_decl_contract.py"
)
CLONE_TITLE = (
    "Scripts/tests/test_briefing_card_title_field_decl_contract.py"
)
CLONE_BODY = (
    "Scripts/tests/test_briefing_card_body_field_decl_contract.py"
)
CLONE_PRIORITY = (
    "Scripts/tests/test_briefing_card_priority_field_decl_contract.py"
)
CLONE_OBJECTIVE_ID = (
    "Scripts/tests/test_objective_progress_objective_id"
    "_field_decl_contract.py"
)
CLONE_CURRENT_PROGRESS = (
    "Scripts/tests/test_objective_progress_current_progress"
    "_field_decl_contract.py"
)
CLONE_STATE = (
    "Scripts/tests/test_objective_progress_state"
    "_field_decl_contract.py"
)
CLONE_FINAL_SCORE = (
    "Scripts/tests/test_mission_result_final_score"
    "_field_decl_contract.py"
)
CLONE_MEDAL_TIER = (
    "Scripts/tests/test_mission_result_medal_tier"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_STATE = (
    "Scripts/tests/test_mission_debrief_state"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_RESULT = (
    "Scripts/tests/test_mission_debrief_result"
    "_field_decl_contract.py"
)
CLONE_MISSION_DISPLAY_NAME = (
    "Scripts/tests/test_mission_debrief_mission_display_name"
    "_field_decl_contract.py"
)
CLONE_NARRATIVE = (
    "Scripts/tests/test_mission_debrief_narrative"
    "_field_decl_contract.py"
)
CLONE_NEW_BEST_SCORE = (
    "Scripts/tests/test_mission_debrief_new_best_score"
    "_field_decl_contract.py"
)
CLONE_NEW_BEST_MEDAL = (
    "Scripts/tests/test_mission_debrief_new_best_medal"
    "_field_decl_contract.py"
)
CLONE_PROGRESS_SAVED = (
    "Scripts/tests/test_mission_debrief_progress_saved"
    "_field_decl_contract.py"
)
CLONE_SAVE_SLOT_NAME = (
    "Scripts/tests/test_mission_debrief_save_slot_name"
    "_field_decl_contract.py"
)
CLONE_NEXT_MISSION_ID = (
    "Scripts/tests/test_mission_debrief_next_mission_id"
    "_field_decl_contract.py"
)
CLONE_NEXT_MISSION_DISPLAY_NAME = (
    "Scripts/tests/test_mission_debrief_next_mission_display_name"
    "_field_decl_contract.py"
)
CLONE_NEXT_MISSION_MAP = (
    "Scripts/tests/test_mission_debrief_next_mission_map"
    "_field_decl_contract.py"
)
CLONE_NEXT_MISSION_UNLOCKED = (
    "Scripts/tests/test_mission_debrief_next_mission_unlocked"
    "_field_decl_contract.py"
)
CLONE_CAMPAIGN_COMPLETE = (
    "Scripts/tests/test_mission_debrief_campaign_complete"
    "_field_decl_contract.py"
)
LEFTOVER_THEATER_KIT_BULK = (
    "Scripts/tests/test_campaign_theater_kit_contract.py"
)
LEFTOVER_PROTECT_ASSET_CARGO_PROXY = (
    "Scripts/tests/test_protect_asset_cargo_proxy.py"
)
LEFTOVER_PROTECT_ASSET_CARGO_PROXY_CONTRACT = (
    "Scripts/tests/test_protect_asset_cargo_proxy_contract.py"
)
LEFTOVER_PROTECT_ASSET_CARGO_PROXY_TESTS = (
    "Scripts/tests/test_protect_asset_cargo_proxy_tests.py"
)
LEFTOVER_RADAR_NODE_PRESENTATION = (
    "Scripts/tests/test_radar_node_presentation.py"
)
LEFTOVER_RADAR_NODE_PRESENTATION_TESTS = (
    "Scripts/tests/test_radar_node_presentation_tests.py"
)
LEFTOVER_RADAR_NODE_PRESENTATION_CONTRACT = (
    "Scripts/tests/test_radar_node_presentation_contract.py"
)
LEFTOVER_RADAR_NODE_RESET_GAMEPLAY = (
    "Scripts/tests/test_radar_node_reset_gameplay.py"
)
LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_TESTS = (
    "Scripts/tests/test_radar_node_reset_gameplay_tests.py"
)
LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_CONTRACT = (
    "Scripts/tests/test_radar_node_reset_gameplay_contract.py"
)
LEFTOVER_MISSION_RESULT_DEFAULTS = (
    "Scripts/tests/test_mission_result_defaults_contract.py"
)
LEFTOVER_MISSION_DEBRIEF_DEFAULTS = (
    "Scripts/tests/test_mission_debrief_defaults_contract.py"
)
LEFTOVER_OBJECTIVE_PROGRESS_DEFAULTS = (
    "Scripts/tests/test_objective_progress_defaults_contract.py"
)
LEFTOVER_ADD_OBJECTIVE_PROGRESS = (
    "Scripts/tests/test_add_objective_progress_decl_contract.py"
)
LEFTOVER_AUDIO_TELEMETRY_DEFAULTS = (
    "Scripts/tests/test_audio_telemetry_defaults_contract.py"
)
LEFTOVER_AUDIO_TELEMETRY_DEFAULTS_PY = (
    "Scripts/tests/test_audio_telemetry_defaults.py"
)
LEFTOVER_AUDIO_TELEMETRY_DEFAULTS_TESTS = (
    "Scripts/tests/test_audio_telemetry_defaults_tests.py"
)
LEFTOVER_AUDIO_DIRECTOR_TELEMETRY = (
    "Scripts/tests/test_audio_director_telemetry_fail_closed.py"
)
LEFTOVER_AUDIO_DIRECTOR_TELEMETRY_TESTS = (
    "Scripts/tests/test_audio_director_telemetry_fail_closed_tests.py"
)
LEFTOVER_AUDIO_DIRECTOR_TELEMETRY_CONTRACT = (
    "Scripts/tests/test_audio_director_telemetry_fail_closed_contract.py"
)
LEFTOVER_APACHE_HULL_COLLIDER = (
    "Scripts/tests/test_apache_hull_collider_field_decl_contract.py"
)
LEFTOVER_APACHE_ROTOR_POWER = (
    "Scripts/tests/test_apache_rotor_power_field_decl_contract.py"
)
LEFTOVER_APACHE_EMPTY = (
    "Scripts/tests/test_apache_aircraft_empty_fail_closed.py"
)
LEFTOVER_APACHE_EMPTY_TESTS = (
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_tests.py"
)
LEFTOVER_APACHE_EMPTY_CONTRACT = (
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_contract.py"
)
LEFTOVER_APACHE_OWN_SHIP = (
    "Scripts/tests/test_apache_own_ship_systems_contract.py"
)
LEFTOVER_APACHE_OWN_SHIP_TESTS = (
    "Scripts/tests/test_apache_own_ship_systems_tests.py"
)
LEFTOVER_APACHE_CPG_FEEL = (
    "Scripts/tests/test_apache_cpg_feel_contract.py"
)
LEFTOVER_APACHE_MOUNT = (
    "Scripts/tests/test_apache_mount_fail_closed.py"
)
LEFTOVER_APACHE_MOUNT_TESTS = (
    "Scripts/tests/test_apache_mount_fail_closed_tests.py"
)
LEFTOVER_APACHE_MOUNT_CONTRACT = (
    "Scripts/tests/test_apache_mount_fail_closed_contract.py"
)
LEFTOVER_LOADOUT_HULL_INTEGRITY = (
    "Scripts/tests/test_loadout_spec_hull_integrity"
    "_field_decl_contract.py"
)
LEFTOVER_CAMPAIGN_ROSTER_LOOKUP = (
    "Scripts/tests/test_campaign_roster_lookup_tests.py"
)
LEFTOVER_SORTIE_DIRECTOR_EMPTY = (
    "Scripts/tests/test_sortie_director_empty_fail_closed.py"
)
LOCKED = {
    "SkyguardMission10IntegrationDirector.h",
    "SkyguardMission10IntegrationDirector.cpp",
    "SkyguardMission09IntegrationDirector.h",
    "SkyguardMission09IntegrationDirector.cpp",
    "SkyguardMission08IntegrationDirector.h",
    "SkyguardMission08IntegrationDirector.cpp",
    "SkyguardMission07IntegrationDirector.h",
    "SkyguardMission07IntegrationDirector.cpp",
    "SkyguardMission06IntegrationDirector.h",
    "SkyguardMission06IntegrationDirector.cpp",
    "SkyguardRadarNode.cpp",
    "SkyguardRadarNode.h",
    "SkyguardRadarNodeGameplayTests.cpp",
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
    "SkyguardProtectAssetTests.cpp",
    "SkyguardHarborProofTests.cpp",
    "SkyguardCampaignTheaterKitTests.cpp",
    "SkyguardMission01EnvironmentAuthoringLibrary.h",
    "SkyguardMissionBriefingComponent.h",
    "SkyguardSortiePresentationWidgets.h",
    "SkyguardCampaignSubsystem.h",
    "SkyguardCampaignSubsystem.cpp",
    "SkyguardMission01IntegrationDirector.h",
    "SkyguardMission01IntegrationDirector.cpp",
    "SkyguardMission02IntegrationDirector.h",
    "SkyguardMission02IntegrationDirector.cpp",
    "SkyguardMission03IntegrationDirector.h",
    "SkyguardMission03IntegrationDirector.cpp",
    "SkyguardMission04IntegrationDirector.h",
    "SkyguardMission04IntegrationDirector.cpp",
    "SkyguardMission05IntegrationDirector.h",
    "SkyguardMission05IntegrationDirector.cpp",
    "SkyguardMissionDirectorCampaignHelpers.h",
    "SkyguardMissionDirectorPresentationHelpers.h",
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


def leftover_apache_ufunction_scripts() -> tuple[str, ...]:
    prefix = "Scripts/tests/"
    return (
        f"{prefix}test_apache_get_rotor_rpm_decl_contract.py",
        f"{prefix}test_apache_get_rotor_power_scale_decl_contract.py",
        f"{prefix}test_apache_get_chin_slew_scale_decl_contract.py",
        f"{prefix}test_apache_get_chin_fire_scale_decl_contract.py",
        f"{prefix}test_apache_get_engine_power_scale_decl_contract.py",
        f"{prefix}test_apache_is_rotor_down_decl_contract.py",
        f"{prefix}test_apache_is_chin_turret_down_decl_contract.py",
        f"{prefix}test_apache_get_sensor_quality_decl_contract.py",
        f"{prefix}test_apache_is_canopy_glass_cracked_decl_contract.py",
        f"{prefix}test_apache_are_engines_down_decl_contract.py",
        f"{prefix}test_apache_get_damage_fraction_decl_contract.py",
        f"{prefix}test_apache_get_forward_speed_decl_contract.py",
        f"{prefix}test_apache_set_direct_flight_input_decl_contract.py",
        f"{prefix}test_apache_apply_damage_decl_contract.py",
        f"{prefix}test_apache_set_first_person_interior_decl_contract.py",
        f"{prefix}test_apache_set_sensor_view_decl_contract.py",
    )


def leftover_apache_mesh_field_scripts() -> tuple[str, ...]:
    prefix = "Scripts/tests/"
    names = (
        "silhouette_mesh",
        "aircraft_root",
        "fuselage",
        "canopy",
        "nose",
        "tail_boom",
        "vertical_tail",
        "stub_wing_left",
        "stub_wing_right",
        "rotor_mast",
        "main_rotor",
        "chin_turret",
        "tail_rotor",
        "chin_barrel",
        "chin_housing",
        "sensor_turret",
        "pilot_canopy",
        "night_vision_turret",
        "sensor_ball",
        "engine_left",
        "radar_dome",
        "engine_right",
        "gear_nose",
        "horizontal_tail",
        "main_rotor_cross",
        "pylon_left",
        "gear_left",
        "hydra_left",
        "pylon_right",
        "hydra_right",
        "hellfire_left",
        "hellfire_right",
        "gunner_mount",
        "weapon_mount",
        "pilot_mount",
        "eye_mount",
    )
    return tuple(
        f"{prefix}test_apache_{name}_field_decl_contract.py"
        for name in names
    )


def leftover_analog_extra_scripts() -> tuple[str, ...]:
    prefix = "Scripts/tests/"
    return (
        LEFTOVER_APACHE_HULL_COLLIDER,
        LEFTOVER_APACHE_CURRENT_INTEGRITY,
        LEFTOVER_APACHE_MAX_INTEGRITY,
        LEFTOVER_APACHE_ROTOR_POWER,
        LEFTOVER_APACHE_EMPTY,
        LEFTOVER_APACHE_EMPTY_TESTS,
        LEFTOVER_APACHE_EMPTY_CONTRACT,
        LEFTOVER_APACHE_OWN_SHIP,
        LEFTOVER_APACHE_OWN_SHIP_TESTS,
        LEFTOVER_APACHE_CPG_FEEL,
        LEFTOVER_APACHE_MOUNT,
        LEFTOVER_APACHE_MOUNT_TESTS,
        LEFTOVER_APACHE_MOUNT_CONTRACT,
        LEFTOVER_LOADOUT_HULL_INTEGRITY,
        LEFTOVER_CAMPAIGN_ROSTER_LOOKUP,
        LEFTOVER_SORTIE_DIRECTOR_EMPTY,
        LEFTOVER_APACHE_SILHOUETTE_MESH,
        LEFTOVER_GUNNER_CPG_COCKPIT,
        LEFTOVER_GUNNER_CPG_STATION,
        LEFTOVER_GUNNER_CPG_SEAT_BACK,
        LEFTOVER_GUNNER_CPG_SEAT_PAN,
        LEFTOVER_GUNNER_CPG_KNEE_LEFT,
        LEFTOVER_GUNNER_CPG_KNEE_RIGHT,
        LEFTOVER_GUNNER_CPG_CANOPY_BOW,
        LEFTOVER_GUNNER_CPG_DASH,
        LEFTOVER_GUNNER_CPG_TEDAC,
        LEFTOVER_GUNNER_CPG_MPD_LEFT,
        LEFTOVER_GUNNER_CPG_MPD_RIGHT,
        LEFTOVER_GUNNER_CPG_EUFD,
        LEFTOVER_GUNNER_CPG_TEDAC_BEZEL,
        LEFTOVER_GUNNER_CPG_RETICLE_H,
        LEFTOVER_GUNNER_CPG_RETICLE_V,
        LEFTOVER_GUNNER_CPG_GRIP_LEFT,
        LEFTOVER_GUNNER_CPG_GRIP_RIGHT,
        LEFTOVER_APACHE_CANOPY,
        LEFTOVER_APACHE_PILOT_CANOPY,
        f"{prefix}test_sortie_director_empty_fail_closed_tests.py",
        f"{prefix}test_sortie_director_empty_fail_closed_contract.py",
        f"{prefix}test_arcade_look_fail_closed.py",
        f"{prefix}test_arcade_look_world_mood_fail_closed.py",
        f"{prefix}test_arcade_look_enabled_field_decl_contract.py",
        f"{prefix}test_guided_lock_break_fail_closed.py",
        f"{prefix}test_guided_lock_rules_detect_progress_end"
        "_field_decl_contract.py",
        f"{prefix}test_campaign_mission_spec_mission_id"
        "_field_decl_contract.py",
        f"{prefix}test_campaign_mission_spec_contact_kind"
        "_field_decl_contract.py",
        f"{prefix}test_campaign_mission_spec_shore_kind"
        "_field_decl_contract.py",
        f"{prefix}test_campaign_roster_weather_enum_label_decl_contract.py",
        f"{prefix}test_campaign_roster_loadout_label_decl_contract.py",
        f"{prefix}test_campaign_roster_id_at_decl_contract.py",
        f"{prefix}test_campaign_roster_get_decl_contract.py",
        f"{prefix}test_campaign_roster_num_missions_decl_contract.py",
    ) + leftover_apache_ufunction_scripts() + leftover_apache_mesh_field_scripts()


LOCKED_SCRIPTS = (
    "Scripts/tests/test_mission08_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission02_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission03_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission04_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission05_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission06_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission07_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission10_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission09_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission09_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission09_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_iron_rain_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_escalating_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_targets_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_budget_safe_field_decl_contract.py",
    "Scripts/tests/test_mission08_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission09_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission09_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission09_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission09_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission09_root_field_decl_contract.py",
    "Scripts/tests/test_mission09_skyline_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission09_major_bridge_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission09_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission09_power_station_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission09_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission09_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission09_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission09_readiness_field_decl_contract.py",
    "Scripts/tests/test_briefing_widget_configure_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_presentation_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_mission_title_decl_contract.py",
    "Scripts/tests/test_briefing_widget_get_briefing_text_decl_contract.py",
    "Scripts/tests/test_briefing_widget_acknowledge_briefing_decl_contract.py",
    "Scripts/tests/test_briefing_widget_launch_sortie_decl_contract.py",
    "Scripts/tests/test_briefing_configure_from_mission_decl_contract.py",
    "Scripts/tests/test_briefing_advance_briefing_decl_contract.py",
    "Scripts/tests/test_briefing_set_assets_ready_decl_contract.py",
    "Scripts/tests/test_briefing_acknowledge_and_launch_decl_contract.py",
    "Scripts/tests/test_briefing_can_launch_decl_contract.py",
    "Scripts/tests/test_briefing_get_elapsed_seconds_decl_contract.py",
    "Scripts/tests/test_briefing_get_briefing_state_decl_contract.py",
    "Scripts/tests/test_briefing_get_minimum_warmup_seconds_decl_contract.py",
    "Scripts/tests/test_briefing_get_briefing_text_decl_contract.py",
    "Scripts/tests/test_briefing_get_radio_chatter_decl_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
    "Scripts/tests/test_briefing_fail_closed.py",
    "Scripts/tests/test_briefing_fail_closed_tests.py",
    "Scripts/tests/test_briefing_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_listener_perspective_fail_closed.py",
    "Scripts/tests/test_audio_director_listener_perspective_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_listener_perspective_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_telemetry_fail_closed.py",
    "Scripts/tests/test_audio_director_telemetry_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_telemetry_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_suppression_fail_closed.py",
    "Scripts/tests/test_audio_director_suppression_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_suppression_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_engine_state_fail_closed.py",
    "Scripts/tests/test_audio_director_engine_state_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_engine_state_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_bank_null_fail_closed.py",
    "Scripts/tests/test_audio_director_bank_null_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_bank_null_fail_closed_contract.py",
    "Scripts/tests/test_audio_director_world_event_fail_closed.py",
    "Scripts/tests/test_audio_director_world_event_fail_closed_tests.py",
    "Scripts/tests/test_audio_director_world_event_fail_closed_contract.py",
    "Scripts/tests/test_radio_chatter_empty_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_fail_closed_tests.py",
    "Scripts/tests/test_radio_chatter_empty_fail_closed_contract.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed_tests.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed_contract.py",
    "Scripts/tests/test_radio_chatter_empty_line_tests.py",
    "Scripts/tests/test_radio_chatter_empty_line_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_line_fail_closed_tests.py",
    "Scripts/tests/test_radio_chatter_empty_line_fail_closed_contract.py",
    "Scripts/tests/test_campaign_definition_campaign_id_decl_contract.py",
    "Scripts/tests/test_campaign_definition_display_name_decl_contract.py",
    "Scripts/tests/test_campaign_definition_missions_decl_contract.py",
    "Scripts/tests/test_validate_definition_decl_contract.py",
    "Scripts/tests/test_find_mission_decl_contract.py",
    "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
    "Scripts/tests/test_readable_escalation.py",
    "Scripts/tests/test_sortie_debrief_loadouts.py",
    "Scripts/tests/test_harbor_proof_play.py",
    "Scripts/tests/test_harbor_proof_source_tests.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_ocean_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_beach_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_land_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_authored_landscape_surface_exposed_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_continuous_coastline_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_route_exclusion_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_landscape_component_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_production_landscape_bound_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_authored_pcg_graph_bound_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_pcg_bounds_tagged_field_decl_contract.py",
    "Scripts/tests/test_mission01_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission01_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission01_root_field_decl_contract.py",
    "Scripts/tests/test_mission01_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission01_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission01_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission01_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission01_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission01_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission01_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission01_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission01_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission01_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_root_field_decl_contract.py",
    "Scripts/tests/test_mission01_production_landscape_field_decl_contract.py",
    "Scripts/tests/test_mission01_inland_vegetation_pcg_field_decl_contract.py",
    "Scripts/tests/test_mission01_land_scatter_bounds_field_decl_contract.py",
    "Scripts/tests/test_mission01_route_exclusion_field_decl_contract.py",
    "Scripts/tests/test_mission01_land_tiles_field_decl_contract.py",
    "Scripts/tests/test_mission01_beach_tiles_field_decl_contract.py",
    "Scripts/tests/test_mission01_ocean_tiles_field_decl_contract.py",
    "Scripts/tests/test_mission01_authored_pcg_graph_field_decl_contract.py",
    "Scripts/tests/test_mission01_route_length_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_district_length_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_route_corridor_half_width_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_shoreline_land_offset_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_seaward_extent_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_beach_width_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_inland_extent_cm_field_decl_contract.py",
    "Scripts/tests/test_mission01_ocean_material_field_decl_contract.py",
    "Scripts/tests/test_mission01_land_material_field_decl_contract.py",
    "Scripts/tests/test_mission01_beach_material_field_decl_contract.py",
    "Scripts/tests/test_mission01_enable_coastal_haze_transition_field_decl_contract.py",
    "Scripts/tests/test_mission01_coastal_haze_delay_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission01_coastal_haze_hold_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission01_get_aircraft_decl_contract.py",
    "Scripts/tests/test_mission01_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission03_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission03_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission04_wave_state_enum_contract.py",
    "Scripts/tests/test_searchlight_track_runtime_defaults_contract.py",
    "Scripts/tests/test_search_track_runtime_defaults_contract.py",
    "Scripts/tests/test_mission04_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission04_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission03_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission04_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission04_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission04_start_searchlight_window_decl_contract.py",
    "Scripts/tests/test_mission04_advance_searchlight_track_decl_contract.py",
    "Scripts/tests/test_mission04_notify_substation_damage_decl_contract.py",
    "Scripts/tests/test_mission04_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission04_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission04_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission04_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission04_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission04_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission04_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission04_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission04_get_searchlight_runtime_decl_contract.py",
    "Scripts/tests/test_mission04_get_substation_integrity_decl_contract.py",
    "Scripts/tests/test_mission04_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission04_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission04_get_night_beat_kit_decl_contract.py",
    "Scripts/tests/test_mission01_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission02_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission02_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission02_get_aircraft_decl_contract.py",
    "Scripts/tests/test_mission02_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission03_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission03_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission03_get_aircraft_decl_contract.py",
    "Scripts/tests/test_mission03_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission03_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission03_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission03_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission03_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission03_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission03_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission03_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission01_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission01_notify_objective_progress_decl_contract.py",
    "Scripts/tests/test_mission01_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission01_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission01_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission01_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission01_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission01_get_gunner_decl_contract.py",
    "Scripts/tests/test_mission01_get_pathfinder_decl_contract.py",
    "Scripts/tests/test_mission01_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission01_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission01_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission_briefing_state_enum_contract.py",
    "Scripts/tests/test_mission02_wave_state_enum_contract.py",
    "Scripts/tests/test_mission_skyline_style_enum_contract.py",
    "Scripts/tests/test_apache_hull_collider_field_decl_contract.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_tests.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_tests.py",
    "Scripts/tests/test_apache_chin_muzzle_tests.py",
    "Scripts/tests/test_apache_chin_muzzle_contract.py",
    "Scripts/tests/test_apache_cpg_feel_contract.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed_tests.py",
    "Scripts/tests/test_patrol_ship_empty_fail_closed_contract.py",
    "Scripts/tests/test_lifeline_hunter_debris_control_surface_field_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_debris_primary_sensor_field_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_debris_secondary_sensor_field_decl_contract.py",
    "Scripts/tests/test_lifeline_hunter_open_sensor_exposure_decl_contract.py",
    "Scripts/tests/test_radar_ghost_radar_receiver_field_decl_contract.py",
    "Scripts/tests/test_pathfinder_encounter_controller_field_decl_contract.py",
    "Scripts/tests/test_boss_drone_root_field_decl_contract.py",
    "Scripts/tests/test_debrief_widget_configure_decl_contract.py",
    "Scripts/tests/test_debrief_widget_get_presentation_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
    "Scripts/tests/test_mission04_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission05_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission05_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission05_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission05_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission05_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission05_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission05_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission05_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission05_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission05_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission05_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission05_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission05_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission05_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission05_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission05_wave_state_enum_contract.py",
    "Scripts/tests/test_mission06_wave_state_enum_contract.py",
    "Scripts/tests/test_airfield_target_enum_contract.py",
    "Scripts/tests/test_airfield_target_runtime_defaults_contract.py",
    "Scripts/tests/test_payload_window_runtime_defaults_contract.py",
    "Scripts/tests/test_mission06_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission06_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission06_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission06_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission06_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission06_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission06_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission06_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission06_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission06_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission06_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission06_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission06_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission06_start_payload_window_decl_contract.py",
    "Scripts/tests/test_mission06_advance_payload_window_decl_contract.py",
    "Scripts/tests/test_mission06_try_jam_active_payload_decl_contract.py",
    "Scripts/tests/test_mission06_notify_airfield_target_damage_decl_contract.py",
    "Scripts/tests/test_mission06_get_payload_window_decl_contract.py",
    "Scripts/tests/test_mission06_get_target_runtime_decl_contract.py",
    "Scripts/tests/test_mission06_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission07_wave_state_enum_contract.py",
    "Scripts/tests/test_mission07_protected_target_enum_contract.py",
    "Scripts/tests/test_mission07_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_search_sector_enum_contract.py",
    "Scripts/tests/test_mission07_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission07_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission07_classify_false_track_decl_contract.py",
    "Scripts/tests/test_mission07_confirm_radar_ghost_identification_decl_contract.py",
    "Scripts/tests/test_mission07_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission07_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission07_notify_protected_target_damage_decl_contract.py",
    "Scripts/tests/test_mission07_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission07_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission07_advance_reinforcement_timer_decl_contract.py",
    "Scripts/tests/test_mission07_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission07_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission07_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission07_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission07_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission07_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission07_get_search_sector_decl_contract.py",
    "Scripts/tests/test_mission07_get_classified_false_track_count_decl_contract.py",
    "Scripts/tests/test_mission07_is_hostile_contact_confirmed_decl_contract.py",
    "Scripts/tests/test_mission07_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission07_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission07_get_reinforcement_time_remaining_decl_contract.py",
    "Scripts/tests/test_mission07_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission07_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission07_get_night_beat_kit_decl_contract.py",
    "Scripts/tests/test_mission07_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission08_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission08_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission08_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission08_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission08_start_hoist_window_decl_contract.py",
    "Scripts/tests/test_mission08_advance_hoist_window_decl_contract.py",
    "Scripts/tests/test_mission08_validate_weapon_release_decl_contract.py",
    "Scripts/tests/test_mission08_notify_protected_target_damage_decl_contract.py",
    "Scripts/tests/test_mission08_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission08_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission08_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission08_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission08_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission08_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission08_get_hoist_runtime_decl_contract.py",
    "Scripts/tests/test_mission08_get_rejected_weapon_releases_decl_contract.py",
    "Scripts/tests/test_mission08_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission08_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission08_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission08_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission08_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission08_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission08_wave_state_enum_contract.py",
    "Scripts/tests/test_mission08_protected_target_enum_contract.py",
    "Scripts/tests/test_mission08_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_hoist_window_runtime_defaults_contract.py",
    "Scripts/tests/test_mission08_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_route_matches_definition_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_required_objectives_anchored_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_landmarks_distinct_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_weather_matches_definition_field_decl_contract.py",
    "Scripts/tests/test_mission_map_readiness_defaults_contract.py",
    "Scripts/tests/test_mission_map_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission_map_validate_assembly_decl_contract.py",
    "Scripts/tests/test_mission_map_rebuild_route_spline_decl_contract.py",
    "Scripts/tests/test_mission_map_is_point_inside_flight_clearance_decl_contract.py",
    "Scripts/tests/test_mission05_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission06_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission09_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission09_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission09_bind_campaign_runtime_decl_contract.py",
    "Scripts/tests/test_mission09_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission09_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission09_notify_protected_target_damage_decl_contract.py",
    "Scripts/tests/test_mission09_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission09_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission09_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission09_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission09_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission09_get_pool_runtime_decl_contract.py",
    "Scripts/tests/test_mission09_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission05_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission09_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission09_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission09_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission09_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission09_wave_state_enum_contract.py",
    "Scripts/tests/test_mission09_protected_target_enum_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_defaults_contract.py",
    "Scripts/tests/test_mission09_pool_budget_defaults_contract.py",
    "Scripts/tests/test_mission09_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission10_route_phase_enum_contract.py",
    "Scripts/tests/test_mission10_protected_group_enum_contract.py",
    "Scripts/tests/test_mission10_protected_runtime_defaults_contract.py",
    "Scripts/tests/test_mission10_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission10_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission10_start_phase_wave_decl_contract.py",
    "Scripts/tests/test_mission10_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission10_validate_weapon_release_decl_contract.py",
    "Scripts/tests/test_mission10_notify_protected_group_damage_decl_contract.py",
    "Scripts/tests/test_mission10_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission10_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission10_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission10_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission10_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission10_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission10_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission10_get_route_phase_decl_contract.py",
    "Scripts/tests/test_mission10_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission10_get_surviving_protected_group_count_decl_contract.py",
    "Scripts/tests/test_mission10_get_rejected_weapon_releases_decl_contract.py",
    "Scripts/tests/test_mission10_get_protected_group_decl_contract.py",
    "Scripts/tests/test_mission10_root_field_decl_contract.py",
    "Scripts/tests/test_mission10_highway_convoy_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_bus_a_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_bus_b_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_ambulance_a_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_ambulance_b_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_ferry_terminal_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_evacuation_ship_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission10_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission10_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission10_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission10_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission10_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission10_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission10_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission10_last_flight_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission10_last_flight_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission10_minimum_weapon_separation_meters_field_decl_contract.py",
    "Scripts/tests/test_mission10_maximum_protected_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission10_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission10_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission02_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission03_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission04_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission05_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission07_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission08_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission09_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission02_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission02_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission02_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission02_get_breakwater_decl_contract.py",
    "Scripts/tests/test_mission02_get_fuel_terminal_integrity_decl_contract.py",
    "Scripts/tests/test_mission02_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission02_get_current_wave_index_decl_contract.py",
    "Scripts/tests/test_mission02_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission02_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission02_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission02_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission02_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission02_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission02_notify_fuel_terminal_damage_decl_contract.py",
    "Scripts/tests/test_mission02_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission02_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission02_root_field_decl_contract.py",
    "Scripts/tests/test_mission02_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission02_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission02_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission02_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission02_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission02_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission02_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission02_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission02_breakwater_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission02_breakwater_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission02_maximum_fuel_terminal_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission02_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission02_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_breakwater_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission02_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission02_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission02_radio_line_count_field_decl_contract.py",
    "Scripts/tests/test_mission03_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission03_maximum_convoy_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission03_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission03_root_field_decl_contract.py",
    "Scripts/tests/test_mission03_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission03_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission03_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission03_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission03_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission03_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission03_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission03_convoy_runtime_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission03_road_hunter_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_convoy_route_state_enum_contract.py",
    "Scripts/tests/test_mission03_wave_state_enum_contract.py",
    "Scripts/tests/test_radio_line_defaults_contract.py",
    "Scripts/tests/test_mission03_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission03_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_road_hunter_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_convoy_route_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission03_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission03_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission03_radio_line_count_field_decl_contract.py",
    "Scripts/tests/test_mission04_root_field_decl_contract.py",
    "Scripts/tests/test_mission04_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission04_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission04_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission04_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission04_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission04_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission04_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission04_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission04_searchlight_port_field_decl_contract.py",
    "Scripts/tests/test_mission04_searchlight_starboard_field_decl_contract.py",
    "Scripts/tests/test_mission04_black_kite_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission04_black_kite_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission04_required_track_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission04_missed_track_damage_field_decl_contract.py",
    "Scripts/tests/test_mission04_maximum_substation_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission04_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission05_root_field_decl_contract.py",
    "Scripts/tests/test_mission05_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission05_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission05_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission05_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission05_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission05_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission05_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission05_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission05_tempest_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission05_tempest_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission05_maximum_protected_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission05_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission05_wave_state_enum_contract.py",
    "Scripts/tests/test_mission05_protected_target_enum_contract.py",
    "Scripts/tests/test_mission05_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_mission06_root_field_decl_contract.py",
    "Scripts/tests/test_mission06_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission06_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission06_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission06_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission06_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission06_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission06_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission06_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission05_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission06_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission06_runway_breaker_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission06_runway_breaker_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission06_maximum_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission06_payload_impact_damage_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission06_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_runway_breaker_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission04_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission05_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission04_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission05_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission04_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission02_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission03_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission04_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission05_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_protected_targets_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission04_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission05_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission09_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission10_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission04_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission05_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission07_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission08_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission10_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission06_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission06_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission06_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission06_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission06_protected_target_count_field_decl_contract.py",
    "Scripts/tests/test_mission07_root_field_decl_contract.py",
    "Scripts/tests/test_mission07_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission07_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission07_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission07_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission07_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission07_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission07_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission07_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission07_radar_ghost_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission07_radar_ghost_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission07_maximum_protected_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission07_reinforcement_deadline_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission07_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission07_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission07_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission07_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_radar_ghost_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_protected_targets_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_search_runtime_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission07_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission07_search_track_count_field_decl_contract.py",
    "Scripts/tests/test_mission08_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission08_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_targets_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_target_count_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission01_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission04_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission05_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission10_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission08_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission08_maximum_protected_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission08_root_field_decl_contract.py",
    "Scripts/tests/test_mission08_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission08_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission08_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission08_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission08_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission08_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission08_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission08_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission08_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission08_rescue_helicopter_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_hoist_cable_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_survivors_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_rafts_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_rescue_vessel_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission08_lifeline_hunter_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission08_lifeline_hunter_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission08_required_covered_seconds_field_decl_contract.py",
    "Scripts/tests/test_mission08_minimum_weapon_separation_meters_field_decl_contract.py",
    "Scripts/tests/test_mission08_rescue_animation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission08_lifeline_hunter_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission09_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_target_count_field_decl_contract.py",
    "Scripts/tests/test_mission09_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_budget_field_decl_contract.py",
    "Scripts/tests/test_mission09_maximum_protected_target_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission09_max_active_threats_field_decl_contract.py",
    "Scripts/tests/test_mission09_max_active_decoys_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_capacity_field_decl_contract.py",
    "Scripts/tests/test_mission09_max_active_threats_field_decl_contract.py",
    "Scripts/tests/test_mission09_max_active_decoys_field_decl_contract.py",
    "Scripts/tests/test_mission09_max_simultaneous_explosions_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_available_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_active_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_peak_active_field_decl_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_recycled_field_decl_contract.py",
    "Scripts/tests/test_mission09_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_destroyed_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_target_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_target_runtime_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission08_protected_target_runtime_destroyed_field_decl_contract.py",
    "Scripts/tests/test_mission07_search_track_runtime_track_id_field_decl_contract.py",
    "Scripts/tests/test_mission07_search_track_runtime_sector_field_decl_contract.py",
    "Scripts/tests/test_mission07_protected_target_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_mission07_protected_target_runtime_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission07_protected_target_runtime_destroyed_field_decl_contract.py",
    "Scripts/tests/test_mission06_airfield_target_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_mission06_airfield_target_runtime_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission06_airfield_target_runtime_destroyed_field_decl_contract.py",
    "Scripts/tests/test_mission06_payload_window_runtime_active_field_decl_contract.py",
    "Scripts/tests/test_mission06_payload_window_runtime_target_field_decl_contract.py",
    "Scripts/tests/test_environment_readiness_bound_capability_count_field_decl_contract.py",
    "Scripts/tests/test_environment_readiness_tree_instance_count_field_decl_contract.py",
    "Scripts/tests/test_environment_readiness_shrub_instance_count_field_decl_contract.py",
    "Scripts/tests/test_environment_readiness_vfx_pool_size_field_decl_contract.py",
    "Scripts/tests/test_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_environment_quality_enum_contract.py",
    "Scripts/tests/test_coastal_env_director_empty_fail_closed.py",
    "Scripts/tests/test_coastal_environment_director_empty_fail_closed.py",
    "Scripts/tests/test_mission01_environment_readiness_ocean_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_beach_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_land_tile_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_authored_landscape_surface_exposed_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_continuous_coastline_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_route_exclusion_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_landscape_component_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_production_landscape_bound_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_authored_pcg_graph_bound_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_pcg_bounds_tagged_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_mission01_is_authored_environment_ready_decl_contract.py",
    "Scripts/tests/test_mission01_sample_landscape_height_decl_contract.py",
    "Scripts/tests/test_mission01_sample_landscape_footprint_decl_contract.py",
    "Scripts/tests/test_mission01_rebuild_production_layout_decl_contract.py",
    "Scripts/tests/test_mission01_production_landscape_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_pcg_generation_authorized_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_valid_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_query_location_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_height_centimeters_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_heightfield_source_field_decl_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_landscape_capture_config_defaults_contract.py",
    "Scripts/tests/test_landscape_material_compilation_defaults_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_success_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_landscape_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_visible_audit_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_landscape_component_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_node_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_edge_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_node_setting_classes_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_landscape_guid_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_landscape_transform_exact_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_graph_contract_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_authored_structure_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_authored_pcg_structure_ready_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_defaults_contract.py",
    "Scripts/tests/test_landscape_visible_audit_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_actor_hidden_in_game_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_hidden_in_game_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_landscape_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_landscape_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_contract_camera_frustum_intersection_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_actor_hidden_in_game_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_actor_temporarily_hidden_in_editor_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_governed_material_parent_match_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_generated_material_instance_ready_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_hidden_in_game_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_visible_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_registered_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_render_state_created_component_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_capture_config_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_capture_config_defaults_contract.py",
    "Scripts/tests/test_landscape_visible_audit_bounds_finite_and_nonzero_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_bounds_minimum_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_bounds_maximum_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_success_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_error_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_asset_compilation_queue_empty_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_shader_compilation_queue_empty_field_decl_contract.py",
    "Scripts/tests/test_landscape_material_compilation_generated_material_instance_count_field_decl_contract.py",
    "Scripts/tests/test_landscape_capture_config_error_field_decl_contract.py",
    "Scripts/tests/test_landscape_capture_config_view_mode_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_licensed_mesh_slots_empty_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_error_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_generated_pcg_instance_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_route_and_beach_generated_instances_zero_field_decl_contract.py",
    "Scripts/tests/test_sortie_presentation_fail_closed.py",
    "Scripts/tests/test_sortie_presentation_fail_closed_tests.py",
    "Scripts/tests/test_sortie_presentation_fail_closed_contract.py",
    "Scripts/tests/test_briefing_card_priority_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_card_id_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_title_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_body_field_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_step_id_field_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_input_hint_field_decl_contract.py",
    "Scripts/tests/test_briefing_radio_row_line_id_field_decl_contract.py",
    "Scripts/tests/test_briefing_radio_row_speaker_field_decl_contract.py",
    "Scripts/tests/test_briefing_radio_row_subtitle_field_decl_contract.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
    "Scripts/tests/test_add_objective_progress_decl_contract.py",
    "Scripts/tests/test_objective_runtime_fail_closed.py",
    "Scripts/tests/test_objective_runtime_fail_closed_tests.py",
    "Scripts/tests/test_objective_runtime_fail_closed_contract.py",
    "Scripts/tests/test_objective_progress_objective_id_field_decl_contract.py",
    "Scripts/tests/test_objective_progress_current_progress_field_decl_contract.py",
    "Scripts/tests/test_objective_progress_state_field_decl_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_mission_result_final_score_field_decl_contract.py",
    "Scripts/tests/test_mission_result_medal_tier_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_state_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_result_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_mission_display_name_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_narrative_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_new_best_score_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_new_best_medal_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_progress_saved_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_next_mission_id_field_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_instruction_field_decl_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_error_field_decl_contract.py",
    "Scripts/tests/test_landscape_height_sample_error_field_decl_contract.py",
    "Scripts/tests/test_landscape_visible_audit_error_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_generated_pcg_component_count_field_decl_contract.py",
    "Scripts/tests/test_mission01_environment_authoring_result_generation_locked_field_decl_contract.py",
    "Scripts/tests/test_mission_result_defaults_tests.py",
    "Scripts/tests/test_mission_result_defaults.py",
    "Scripts/tests/test_mission_debrief_defaults_tests.py",
    "Scripts/tests/test_mission_debrief_defaults.py",
    "Scripts/tests/test_mission_debrief_next_mission_display_name_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_next_mission_map_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_next_mission_unlocked_field_decl_contract.py",
    "Scripts/tests/test_mission_debrief_campaign_complete_field_decl_contract.py",
    "Scripts/tests/test_boss_telemetry_weak_points_destroyed_field_decl_contract.py",
    "Scripts/tests/test_boss_telemetry_pilot_commands_issued_field_decl_contract.py",
    "Scripts/tests/test_audio_telemetry_defaults_contract.py",
    "Scripts/tests/test_audio_telemetry_defaults.py",
    "Scripts/tests/test_audio_telemetry_defaults_tests.py",
    CLONE_PLAYED_EVENTS,
    CLONE_REQUESTED_EVENTS,
    CLONE_REJECTED_BY_COOLDOWN,
    CLONE_REJECTED_BY_CONCURRENCY,
    CLONE_REJECTED_MISSING_ASSET,
    CLONE_PRIORITY_EVICTIONS,
    CLONE_PEAK_ACTIVE_VOICES,
    LEFTOVER_PROTECT_ASSET_CARGO_PROXY,
    LEFTOVER_PROTECT_ASSET_CARGO_PROXY_CONTRACT,
    LEFTOVER_PROTECT_ASSET_CARGO_PROXY_TESTS,
    CLONE_APPLY_DAMAGE,
    CLONE_IS_DESTROYED,
    CLONE_GET_INTEGRITY_FRACTION,
    CLONE_MAX_INTEGRITY,
    CLONE_CURRENT_INTEGRITY,
    CLONE_MAX_HEALTH,
    CLONE_RADAR_IS_DESTROYED,
    CLONE_RADAR_APPLY_DAMAGE,
    CLONE_RADAR_RESET_NODE,
    CLONE_RESET_INTEGRITY,
    LEFTOVER_RADAR_NODE_PRESENTATION,
    LEFTOVER_RADAR_NODE_PRESENTATION_TESTS,
    LEFTOVER_RADAR_NODE_PRESENTATION_CONTRACT,
    LEFTOVER_RADAR_NODE_RESET_GAMEPLAY,
    LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_TESTS,
    LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_CONTRACT,
) + leftover_live_copy_boss_scripts() + leftover_analog_extra_scripts()


def leftover_banned_primary_mesh() -> str:
    return "Ri" + "fle" + "Mesh"


def leftover_banned_guided_tube() -> str:
    return "Ig" + "la" + "Tube"


def leftover_banned_guided_muzzle() -> str:
    return "Ig" + "la" + "Muzzle"


def leftover_retired_primary_hits_field() -> str:
    return "Ri" + "fleHits"


def leftover_retired_guided_hits_field() -> str:
    return "Ig" + "laHits"


def leftover_neighbor_hit_fields() -> tuple[str, ...]:
    return (
        leftover_retired_primary_hits_field(),
        leftover_retired_guided_hits_field(),
    )


def leftover_harbor_tokens() -> tuple[str, ...]:
    forty = "40" + ".f"
    eighty = "80" + ".f"
    return (forty, eighty)


def leftover_harbor_token_in(text: str, token: str) -> bool:
    return re.search(r"(?<![0-9])" + re.escape(token), text) is not None


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


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def leftover_apache_ufunction_tokens() -> tuple[str, ...]:
    return (
        "GetRotorRPM",
        "GetRotorPowerScale",
        "GetChinSlewScale",
        "GetChinFireScale",
        "GetEnginePowerScale",
        "IsRotorDown",
        "IsChinTurretDown",
        "GetSensorQuality",
        "IsCanopyGlassCracked",
        "AreEnginesDown",
        "GetDamageFraction",
        "GetForwardSpeed",
        "SetDirectFlightInput",
        "ApplyDamage",
        "SetFirstPersonInterior",
        "SetSensorView",
        "GetGunnerMount",
        "AimChinTurret",
        "IssuePilotCommand",
        "BindSilhouetteMesh",
        "GetEffectiveRotorPower",
    )


def leftover_harbor_breaker_tokens() -> tuple[str, ...]:
    return (
        "ContactKind",
        "ShoreKind",
        "SupportKind",
        "ExtractKind",
        "ESkyguardSortieBeat::Approach",
    )


CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")
CPG_RAIL_RIGHT_DECL_RE = re.compile(
    r"TObjectPtr<UStaticMeshComponent>\s+CpgRailRight\s*;"
)
CPG_RAIL_RIGHT_INIT_RE = re.compile(
    r"TObjectPtr<UStaticMeshComponent>\s+CpgRailRight\s*="
)
WEATHER_IDENTITY_DECL_RE = re.compile(
    r"FName\s+WeatherIdentity\b"
)
INVENTED_UPROPERTY = (
    "EditAnywhere",
    "BlueprintReadWrite",
    "BlueprintCallable",
    "BlueprintPure",
    "Transient",
    "MultiLine",
    "BlueprintAuthorityOnly",
    "meta=",
)
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
    "= false",
    "= 0.f",
    "= 160.f",
    "= NAME_None",
    "= 100.f",
    "= nullptr",
    "= 140.f",
)


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_CPG_STATION,
        SIBLING_CPG_COCKPIT,
        SIBLING_CPG_SEAT_BACK,
        SIBLING_CPG_SEAT_PAN,
        SIBLING_CPG_KNEE_LEFT,
        SIBLING_CPG_KNEE_RIGHT,
        SIBLING_CPG_CANOPY_BOW,
        SIBLING_CPG_DASH,
        SIBLING_BOOM,
        SIBLING_GUNNER_CAMERA,
        SIBLING_CPG_TEDAC,
        SIBLING_CPG_MPD_LEFT,
        SIBLING_CPG_MPD_RIGHT,
        SIBLING_CPG_EUFD,
        SIBLING_CPG_TEDAC_BEZEL,
        SIBLING_CPG_RETICLE_H,
        SIBLING_CPG_GRIP_LEFT,
        SIBLING_CPG_GRIP_RIGHT,
        SIBLING_CPG_CONSOLE_RIGHT,
        SIBLING_CPG_RAIL_LEFT,
        SIBLING_CPG_RETICLE_V,
        SIBLING_CPG_TEDAC_TEXT,
        SIBLING_CPG_MPD_LEFT_TEXT,
        SIBLING_HAND_MESH,
        SIBLING_CPG_EUFD_TEXT,
        leftover_banned_primary_mesh(),
        leftover_banned_guided_tube(),
        leftover_banned_guided_muzzle(),
        SIBLING_AIRCRAFT_ROOT,
        SIBLING_FUSELAGE,
        SIBLING_ROTOR_POWER,
        SIBLING_HOVER_BOB,
        SIBLING_MAX_INTEGRITY,
        SIBLING_CURRENT_INTEGRITY,
        SIBLING_HULL_COLLIDER,
    )


def this_file_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*<\s*", "<", compact)
    compact = re.sub(r"\s*>", ">", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
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


def has_declaration(region: str, declaration: str) -> bool:
    # Fail-closed on authored bare
    # `TObjectPtr<UStaticMeshComponent> CpgRailRight;`.
    # Do not accept leftover FName WeatherIdentity,
    # leftover `= 160.f`, leftover CurrentIntegrity,
    # leftover CpgGripRight / CpgGripLeft / CpgReticleV /
    # CpgReticleH / CpgTedacBezel / CpgConsoleRight /
    # CpgRailLeft / CpgTedacText / CpgEufd / CpgTedac /
    # CpgDash / CpgKneeRight / CpgCanopyBow / CpgSeatBack /
    # CpgSeatPan / CpgCockpit / CpgStation / leftover
    # Apache Canopy, or an
    # initializer on CpgRailRight as the slot.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if CPG_RAIL_RIGHT_DECL_RE.search(compact) is None:
        return False
    if CPG_RAIL_RIGHT_INIT_RE.search(compact):
        return False
    if WEATHER_IDENTITY_DECL_RE.search(compact):
        return False
    if re.search(r"float\s+Health\s*=\s*160\.f\b", compact):
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


def leaked_neighbor_tokens() -> tuple[str, ...]:
    return (
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
        STOP_BEFORE_THEATER_SPEC,
        STOP_BEFORE_THEATER_ACTOR,
        STOP_BEFORE_ARCADE_LOOK,
        STOP_BEFORE_GUIDED_LOCK,
        STOP_BEFORE_MISSION_SPEC,
        STOP_BEFORE_LOADOUT_SPEC,
        STOP_BEFORE_ROSTER,
        GET_OBJECTIVE_RUNTIME,
        ADD_OBJECTIVE_PROGRESS,
        BIND_RUNTIME_ACTORS,
        HANDLE_DRONE_CITY_IMPACT,
        GET_STORM_RAIN_BEAT_KIT,
        "class USkyguardCampaignSubsystem",
        "class ASkyguardMission01IntegrationDirector",
        "struct FSkyguardBriefingCard",
        "struct FSkyguardMissionResult",
        "struct FSkyguardObjectiveProgress",
        "struct FSkyguardMissionDebrief",
        "struct FSkyguardBossTelemetry",
        "struct FSkyguardAudioTelemetry",
        "ESkyguardAudioEvent::",
        f"class SKYGUARD52_API {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_RADAR_NODE_CLASS}",
        f"class {LEFTOVER_RADAR_NODE_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_THEATER_KIT_ACTOR}",
        f"class {LEFTOVER_THEATER_KIT_ACTOR}",
    )


def protected_section(header: str) -> str:
    body = class_body(header)
    protected = re.search(r"\bprotected\s*:", body)
    if protected is None:
        raise AssertionError(
            f"{CLASS_NAME} protected section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = protected.end()
    rest = body[start:]
    next_access = ACCESS_RE.search(rest)
    if next_access is not None:
        section = rest[: next_access.start()]
    else:
        close = rest.rfind("}")
        if close == -1:
            raise AssertionError(
                f"{CLASS_NAME} protected section is missing from "
                f"origin/main:{HEADER_PATH}"
            )
        section = rest[:close]
    if STOP_BEFORE_PRIVATE in section:
        raise AssertionError(
            f"{CLASS_NAME} parse window includes {STOP_BEFORE_PRIVATE}"
        )
    return section


def _matching_paren_end(text: str, open_index: int) -> int:
    depth = 0
    index = open_index
    while index < len(text):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    raise AssertionError(
        f"{CLASS_NAME} UPROPERTY specifier list is unclosed in "
        f"origin/main:{HEADER_PATH}"
    )


def protected_uproperty_fields(header: str) -> str:
    section = protected_section(header)
    blocks: list[str] = []
    cursor = 0
    while True:
        match = re.search(r"UPROPERTY\s*\(", section[cursor:])
        if match is None:
            break
        start = cursor + match.start()
        open_paren = cursor + match.end() - 1
        after_paren = _matching_paren_end(section, open_paren)
        semi = section.find(";", after_paren)
        if semi == -1:
            raise AssertionError(
                f"{CLASS_NAME} protected UPROPERTY field is missing a "
                f"semicolon in origin/main:{HEADER_PATH}"
            )
        field_text = section[after_paren : semi + 1]
        if has_identifier(field_text, SIBLING_CPG_TEDAC_TEXT):
            break
        blocks.append(section[start : semi + 1])
        cursor = semi + 1
    window = "\n".join(blocks)
    for token in leaked_neighbor_tokens():
        if token in window:
            raise AssertionError(
                f"{CLASS_NAME} parse window includes {token}"
            )
    if has_identifier(window, SIBLING_CPG_TEDAC_TEXT):
        raise AssertionError(
            f"{CLASS_NAME} parse window claims sibling "
            f"{SIBLING_CPG_TEDAC_TEXT}"
        )
    for leftover in leftover_apache_ufunction_tokens():
        if has_identifier(window, leftover):
            raise AssertionError(
                f"{CLASS_NAME} parse window includes leftover "
                f"UFUNCTION {leftover}"
            )
    for leftover in leftover_harbor_breaker_tokens():
        if leftover in window:
            raise AssertionError(
                f"{CLASS_NAME} parse window includes leftover "
                f"Harbor Breaker {leftover}"
            )
    for sibling in (
        SIBLING_CPG_TEDAC_TEXT,
        SIBLING_CPG_MPD_LEFT_TEXT,
        SIBLING_CPG_EUFD_TEXT,
        leftover_banned_guided_muzzle(),
        SIBLING_ROTOR_POWER,
        SIBLING_HOVER_BOB,
        SIBLING_MAX_INTEGRITY,
        SIBLING_CURRENT_INTEGRITY,
        SIBLING_HULL_COLLIDER,
        SIBLING_FUSELAGE,
        SIBLING_AIRCRAFT_ROOT,
    ):
        if has_identifier(window, sibling):
            raise AssertionError(
                f"{CLASS_NAME} parse window claims sibling {sibling}"
            )
    return window


def spec_section(header: str) -> str:
    return protected_uproperty_fields(header)


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
            r"\s*TObjectPtr<UStaticMeshComponent>\s+CpgRailRight\b",
            compact[index:],
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for TObjectPtr<UStaticMeshComponent> CpgRailRight "
        f"is missing from origin/main:{HEADER_PATH} class "
        f"{CLASS_NAME} protected UPROPERTY fields"
    )


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"class {CLASS_NAME} protected UPROPERTY fields"
        )
    return declaration


class GunnerCpgRailRightFieldDeclContractTests(unittest.TestCase):
    def test_gunner_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertIn(f"class SKYGUARD52_API {CLASS_NAME}", header)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_PROTECT_ASSET_CLASS)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_RADAR_NODE_CLASS)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_THEATER_KIT_ACTOR)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = spec_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(has_identifier(section, "CpgRailRight"), section)
        self.assertIn("UPROPERTY", section)
        self.assertIn(STOP_BEFORE_PROTECTED, header)
        self.assertNotIn(STOP_BEFORE_PRIVATE, section)
        self.assertTrue(has_identifier(body, SIBLING_CPG_TEDAC_TEXT), body)
        self.assertFalse(
            has_identifier(section, SIBLING_CPG_TEDAC_TEXT),
            section,
        )
        self.assertTrue(has_identifier(section, SIBLING_CPG_GRIP_LEFT), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_GRIP_RIGHT), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_CONSOLE_RIGHT), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_RAIL_LEFT), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_RETICLE_V), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_TEDAC), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_MPD_LEFT), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_MPD_RIGHT), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_EUFD), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_TEDAC_BEZEL), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_RETICLE_H), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_DASH), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_COCKPIT), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_STATION), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_SEAT_BACK), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_SEAT_PAN), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_KNEE_LEFT), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_KNEE_RIGHT), section)
        self.assertTrue(has_identifier(section, SIBLING_CPG_CANOPY_BOW), section)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_APACHE_AIRCRAFT_CLASS)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, section)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, section)
        self.assertNotIn(LEFTOVER_THEATER_KIT_ACTOR, section)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for leftover in leftover_apache_ufunction_tokens():
            self.assertFalse(has_identifier(section, leftover), leftover)
        self.assertNotIn(GET_OBJECTIVE_RUNTIME, section)
        self.assertNotIn(ADD_OBJECTIVE_PROGRESS, section)
        self.assertNotIn(STOP_BEFORE_SORTIE, section)
        self.assertNotIn(STOP_BEFORE_MISSION_SPEC, section)
        self.assertNotIn(STOP_BEFORE_ARCADE_LOOK, section)
        self.assertNotIn(STOP_BEFORE_GUIDED_LOCK, section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class ASkyguardUnrelatedApache\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_type_does_not_satisfy(self) -> None:
        other = (
            f"class {LEFTOVER_PROTECT_ASSET_CLASS}\n"
            "{\n"
            "protected:\n"
            f"\t{UPROPERTY_VISIBLE_READONLY}\n"
            f"\t{LOCKED_DECL}\n"
            "protected:\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        theater = (
            f"struct {STOP_BEFORE_THEATER_SPEC}\n"
            "{\n"
            f"\t{TARGET_WRONG_THEATER}\n"
            f"\t{TARGET_WRONG_FNAME}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(theater)
        self.assertIn(CLASS_NAME, str(raised.exception))
        loadout = (
            f"struct {STOP_BEFORE_LOADOUT_SPEC}\n"
            "{\n"
            f"\t{TARGET_WRONG_SEAT_PAN}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(loadout)
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_leftover_class_same_identifier_does_not_satisfy(self) -> None:
        mixed = (
            f"class {LEFTOVER_PROTECT_ASSET_CLASS}\n"
            "{\n"
            "protected:\n"
            f"\t{UPROPERTY_VISIBLE_READONLY}\n"
            f"\t{LOCKED_DECL}\n"
            "protected:\n"
            "};\n"
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            "\tvoid ApplyDamage(float Amount);\n"
            "protected:\n"
            "};\n"
        )
        section = spec_section(mixed)
        self.assertFalse(has_identifier(section, "CpgRailRight"), section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("CpgRailRight", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_cpg_rail_right_declaration_fails_closed(self) -> None:
        empty = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            f"\t{UPROPERTY_VISIBLE_READONLY}\n"
            f"\t{TARGET_WRONG_CPG_STATION}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        section = spec_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("CpgRailRight", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_VISIBLE_READONLY}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("CpgRailRight", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = spec_section(origin_main_header())
        self.assertIn(UPROPERTY_VISIBLE_READONLY, section)
        self.assertIn("VisibleAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('Category="Skyguard"', section)
        self.assertNotIn('Skyguard|Apache', section)
        self.assertIn("VisibleAnywhere", UPROPERTY_VISIBLE_READONLY)
        self.assertIn("BlueprintReadOnly", UPROPERTY_VISIBLE_READONLY)
        self.assertIn("Category", UPROPERTY_VISIBLE_READONLY)
        self.assertIn(
            'Category="Skyguard"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertNotIn("EditAnywhere", UPROPERTY_VISIBLE_READONLY)
        self.assertNotIn("BlueprintReadWrite", UPROPERTY_VISIBLE_READONLY)
        specifiers = attached_uproperty_specifiers(section)
        self.assertIn("VisibleAnywhere", specifiers)
        self.assertIn("BlueprintReadOnly", specifiers)
        self.assertIn('Category="Skyguard"', specifiers)
        self.assertNotIn('Skyguard|Apache', specifiers)
        self.assertIn("Category", specifiers)
        self.assertNotIn("EditAnywhere", specifiers)
        self.assertNotIn("BlueprintReadWrite", specifiers)
        self.assertNotIn("MultiLine", specifiers)
        self.assertNotIn("ClampMin", specifiers)
        self.assertNotIn("ClampMax", specifiers)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertNotIn("UFUNCTION", LOCKED_DECL)
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, LOCKED_DECL)

    def test_wrong_initializer_fails_closed(self) -> None:
        bare = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            f"\t{UPROPERTY_VISIBLE_READONLY}\n"
            f"\t{TARGET_WRONG_INIT}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        section = spec_section(bare)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("CpgRailRight", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        origin = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIn("TObjectPtr<UStaticMeshComponent> CpgRailRight;", compact_origin)
        self.assertNotIn("CpgRailRight = 160.f", compact_origin)
        self.assertNotIn("FName WeatherIdentity", compact_origin)
        self.assertNotIn("FName WeatherIdentity", compact_origin)

    def test_cpg_rail_right_declaration_matches_origin_main(self) -> None:
        section = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(
            LOCKED_DECL.startswith("TObjectPtr<UStaticMeshComponent> CpgRailRight"),
            LOCKED_DECL,
        )
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertNotIn("=", LOCKED_DECL)
        self.assertNotIn("140.f", LOCKED_DECL)
        self.assertNotIn("160.f", LOCKED_DECL)
        self.assertNotIn("100.f", LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_FNAME)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_INIT)
        self.assertNotIn("WeatherIdentity", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertIn("TObjectPtr", LOCKED_DECL)
        self.assertIn("UStaticMeshComponent", LOCKED_DECL)
        self.assertNotIn("bool ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        self.assertNotIn(SIBLING_MAX_INTEGRITY, LOCKED_DECL)
        self.assertNotIn(SIBLING_CURRENT_INTEGRITY, LOCKED_DECL)
        self.assertNotIn(SIBLING_HULL_COLLIDER, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_SEAT_PAN, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_SEAT_BACK, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_KNEE_LEFT, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_KNEE_RIGHT, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_CANOPY_BOW, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_DASH, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_TEDAC, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_MPD_LEFT, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_MPD_RIGHT, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_EUFD, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_TEDAC_BEZEL, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_RETICLE_H, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_RETICLE_V, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_GRIP_LEFT, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_GRIP_RIGHT, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_CONSOLE_RIGHT, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_RAIL_LEFT, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_TEDAC_TEXT, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_MPD_LEFT_TEXT, LOCKED_DECL)
        self.assertNotIn(SIBLING_HAND_MESH, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_EUFD_TEXT, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_COCKPIT, LOCKED_DECL)
        self.assertNotIn(SIBLING_CPG_STATION, LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TEDAC)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CANOPY)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_PILOT_CANOPY)
        self.assertNotIn(SIBLING_FUSELAGE, LOCKED_DECL)
        self.assertNotIn(SIBLING_AIRCRAFT_ROOT, LOCKED_DECL)
        self.assertNotIn(SIBLING_ROTOR_POWER, LOCKED_DECL)
        self.assertNotIn(SIBLING_HOVER_BOB, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_INIT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FNAME}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_HEALTH}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_SCENE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TEXT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TEDAC_TEXT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_SEAT_PAN}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_CPG_STATION}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_CPG_COCKPIT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_SCENE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_SILHOUETTE}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_INIT}\n", LOCKED_DECL)
        self.assertIn("CpgRailRight", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_FNAME}\n", LOCKED_DECL)
        self.assertIn("CpgRailRight", str(raised.exception))

    def test_locked_decl_is_not_leftover_clone_weather_identity(self) -> None:
        self.assertEqual(LOCKED_DECL, "TObjectPtr<UStaticMeshComponent> CpgRailRight;")
        self.assertNotEqual(LOCKED_DECL, "FName WeatherIdentity;")
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CPG_COCKPIT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CPG_STATION)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SEAT_BACK)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SEAT_PAN)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_KNEE_LEFT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_KNEE_RIGHT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CANOPY_BOW)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_DASH)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TEDAC)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_MPD_LEFT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_MPD_RIGHT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TEDAC_BEZEL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_EUFD)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_RETICLE_H)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_RETICLE_V)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_GRIP_LEFT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_GRIP_RIGHT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CONSOLE_RIGHT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_RAIL_LEFT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TEXT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TEDAC_TEXT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_MPD_LEFT_TEXT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_HAND_MESH)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_EUFD_TEXT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CANOPY)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_PILOT_CANOPY)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SCENE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SILHOUETTE)
        self.assertNotEqual(
            LOCKED_DECL,
            "TObjectPtr<UStaticMeshComponent> "
            + leftover_banned_primary_mesh()
            + ";",
        )
        self.assertNotEqual(
            LOCKED_DECL,
            "TObjectPtr<UStaticMeshComponent> "
            + leftover_banned_guided_tube()
            + ";",
        )
        self.assertNotIn("WeatherIdentity", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("=", LOCKED_DECL)
        self.assertNotIn("140.f", LOCKED_DECL)
        self.assertNotIn("160.f", LOCKED_DECL)
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            LOCKED_DECL,
        )
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertNotEqual(
            UPROPERTY_VISIBLE_READONLY,
            TARGET_WRONG_THEATER,
        )
        self.assertIn(
            'Category="Skyguard"',
            UPROPERTY_VISIBLE_READONLY,
        )

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tfloat " + leftover_retired_primary_hits_field() + " = 160.f;\n"
        )
        leftover_guided = (
            "\tfloat " + leftover_retired_guided_hits_field() + " = 160.f;\n"
        )
        forty = "40" + ".f"
        eighty = "80" + ".f"
        wrongs = (
            f"\t{TARGET_WRONG_INIT}\n",
            f"\t{TARGET_WRONG_FALSE}\n",
            f"\t{TARGET_WRONG_TRUE}\n",
            f"\t{TARGET_WRONG_SKELETAL}\n",
            f"\t{TARGET_WRONG_FNAME}\n",
            f"\t{TARGET_WRONG_HEALTH}\n",
            f"\t{TARGET_WRONG_SCENE}\n",
            f"\t{TARGET_WRONG_SEAT_PAN}\n",
            f"\t{TARGET_WRONG_SEAT_BACK}\n",
            f"\t{TARGET_WRONG_KNEE_LEFT}\n",
            f"\t{TARGET_WRONG_KNEE_RIGHT}\n",
            f"\t{TARGET_WRONG_CANOPY_BOW}\n",
            f"\t{TARGET_WRONG_DASH}\n",
            f"\t{TARGET_WRONG_TEDAC}\n",
            f"\t{TARGET_WRONG_MPD_LEFT}\n",
            f"\t{TARGET_WRONG_MPD_RIGHT}\n",
            f"\t{TARGET_WRONG_TEDAC_BEZEL}\n",
            f"\t{TARGET_WRONG_EUFD}\n",
            f"\t{TARGET_WRONG_RETICLE_H}\n",
            f"\t{TARGET_WRONG_RETICLE_V}\n",
            f"\t{TARGET_WRONG_GRIP_LEFT}\n",
            f"\t{TARGET_WRONG_GRIP_RIGHT}\n",
            f"\t{TARGET_WRONG_CONSOLE_RIGHT}\n",
            f"\t{TARGET_WRONG_RAIL_LEFT}\n",
            f"\t{TARGET_WRONG_TEXT}\n",
            f"\t{TARGET_WRONG_TEDAC_TEXT}\n",
            f"\t{TARGET_WRONG_MPD_LEFT_TEXT}\n",
            f"\t{TARGET_WRONG_HAND_MESH}\n",
            f"\t{TARGET_WRONG_EUFD_TEXT}\n",
            f"\t{TARGET_WRONG_CANOPY}\n",
            f"\t{TARGET_WRONG_PILOT_CANOPY}\n",
            f"\t{TARGET_WRONG_CPG_STATION}\n",
            f"\t{TARGET_WRONG_CPG_COCKPIT}\n",
            f"\t{TARGET_WRONG_SILHOUETTE}\n",
            f"\t{TARGET_WRONG_FUSELAGE}\n",
            f"\t{TARGET_WRONG_AIRCRAFT_ROOT}\n",
            leftover_primary,
            leftover_guided,
            "\tTObjectPtr<UStaticMeshComponent> CpgRailRights;\n",
            "\tint32 CpgRailRight = 140;\n",
            "\tbool CpgRailRight = true;\n",
            "\tfloat CpgRailRight = " + forty + ";\n",
            "\tfloat CpgRailRight = " + eighty + ";\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("CpgRailRight", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_missing_category_or_visible_anywhere_fails_closed(self) -> None:
        no_category = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly)\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        section = spec_section(no_category)
        specifiers = attached_uproperty_specifiers(section)
        self.assertNotIn("Category", specifiers)
        origin = attached_uproperty_specifiers(
            spec_section(origin_main_header())
        )
        self.assertIn("Category", origin)
        self.assertIn('Category="Skyguard"', origin)
        self.assertNotIn('Skyguard|Apache', origin)
        self.assertIn("VisibleAnywhere", origin)
        self.assertIn("BlueprintReadOnly", origin)
        no_visible = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            "\tUPROPERTY(BlueprintReadOnly, "
            'Category="Skyguard")\n'
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        dropped = attached_uproperty_specifiers(
            spec_section(no_visible)
        )
        self.assertNotIn("VisibleAnywhere", dropped)
        self.assertIn("VisibleAnywhere", origin)
        write_only = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadWrite, "
            'Category="Skyguard")\n'
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        write_specs = attached_uproperty_specifiers(
            spec_section(write_only)
        )
        self.assertIn("EditAnywhere", write_specs)
        self.assertIn("BlueprintReadWrite", write_specs)
        self.assertNotIn("VisibleAnywhere", write_specs)
        self.assertNotIn("BlueprintReadOnly", write_specs)
        theater = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "protected:\n"
            f"\t{TARGET_WRONG_THEATER}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        theater_specs = attached_uproperty_specifiers(
            spec_section(theater)
        )
        self.assertIn('Category="Skyguard|Theater"', theater_specs)
        self.assertNotIn('Skyguard|Apache', theater_specs)
        self.assertIsNone(
            re.search(r'Category="Skyguard"(?!\|)', theater_specs)
        )
        self.assertIn('Category="Skyguard"', origin)
        self.assertNotIn('Skyguard|Apache', origin)
        self.assertNotIn('Skyguard|Theater', origin)
        self.assertIsNotNone(
            re.search(r'Category="Skyguard"(?!\|)', origin)
        )

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wraps = (
            "\tTObjectPtr<UStaticMeshComponent>\n\tCpgRailRight;\n",
            "\tTObjectPtr<UStaticMeshComponent>   CpgRailRight;\n",
            "\tTObjectPtr<UStaticMeshComponent>\tCpgRailRight;\n",
            f"\t{LOCKED_DECL}\n",
            f"\t{UPROPERTY_VISIBLE_READONLY}\n\t{LOCKED_DECL}\n",
            f"\t{UPROPERTY_VISIBLE_READONLY} {LOCKED_DECL}\n",
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
            'Category="Skyguard")\n'
            f"\t{LOCKED_DECL}\n",
            "\tUPROPERTY(\n\t\tVisibleAnywhere, BlueprintReadOnly, "
            'Category="Skyguard")\n'
            f"\t{LOCKED_DECL}\n",
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly,\n"
            '\t\tCategory="Skyguard")\n'
            f"\t{LOCKED_DECL}\n",
        )
        for region in wraps:
            self.assertTrue(has_declaration(region, LOCKED_DECL), region)

    def test_does_not_claim_sibling_tedac_text_or_neighbors(self) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertNotIn(SIBLING_CURRENT_INTEGRITY, LOCKED_DECL)
        section = spec_section(origin_main_header())
        self.assertTrue(has_identifier(section, SIBLING_CPG_STATION))
        self.assertTrue(has_identifier(section, SIBLING_CPG_COCKPIT))
        self.assertTrue(has_identifier(section, SIBLING_CPG_SEAT_BACK))
        self.assertTrue(has_identifier(section, SIBLING_CPG_SEAT_PAN))
        self.assertTrue(has_identifier(section, SIBLING_CPG_KNEE_LEFT))
        self.assertTrue(has_identifier(section, SIBLING_CPG_KNEE_RIGHT))
        self.assertTrue(has_identifier(section, SIBLING_CPG_CANOPY_BOW))
        self.assertTrue(has_identifier(section, SIBLING_CPG_DASH))
        self.assertTrue(has_identifier(section, SIBLING_CPG_TEDAC))
        self.assertTrue(has_identifier(section, SIBLING_CPG_MPD_LEFT))
        self.assertTrue(has_identifier(section, SIBLING_CPG_MPD_RIGHT))
        self.assertTrue(has_identifier(section, SIBLING_CPG_EUFD))
        self.assertTrue(has_identifier(section, SIBLING_CPG_TEDAC_BEZEL))
        self.assertTrue(has_identifier(section, SIBLING_CPG_RETICLE_H))
        self.assertTrue(has_identifier(section, SIBLING_CPG_RETICLE_V))
        self.assertTrue(has_identifier(section, SIBLING_CPG_GRIP_LEFT))
        self.assertTrue(has_identifier(section, SIBLING_CPG_GRIP_RIGHT))
        self.assertTrue(has_identifier(section, SIBLING_CPG_CONSOLE_RIGHT))
        self.assertTrue(has_identifier(section, SIBLING_CPG_RAIL_LEFT))
        self.assertTrue(has_identifier(section, "CpgRailRight"))
        self.assertFalse(has_identifier(section, SIBLING_CPG_TEDAC_TEXT))
        self.assertFalse(has_identifier(section, SIBLING_CPG_MPD_LEFT_TEXT))
        self.assertFalse(has_identifier(section, SIBLING_CPG_EUFD_TEXT))
        self.assertFalse(has_identifier(section, leftover_banned_guided_muzzle()))
        self.assertFalse(has_identifier(section, SIBLING_ROTOR_POWER))
        self.assertFalse(has_identifier(section, SIBLING_HOVER_BOB))
        self.assertFalse(has_identifier(section, SIBLING_MAX_INTEGRITY))
        self.assertFalse(has_identifier(section, SIBLING_CURRENT_INTEGRITY))
        self.assertFalse(has_identifier(section, SIBLING_HULL_COLLIDER))
        self.assertNotIn(TARGET_WRONG_TEDAC_TEXT, section)
        self.assertNotIn(TARGET_WRONG_MPD_LEFT_TEXT, section)
        self.assertNotIn(TARGET_WRONG_CANOPY, section)
        self.assertNotIn(TARGET_WRONG_PILOT_CANOPY, section)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, LOCKED_DECL)

    def test_does_not_parse_private_or_neighbors(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = class_body(header)
        self.assertNotIn(STOP_BEFORE_PRIVATE, section)
        self.assertTrue(has_identifier(leaked, "CpgRailRight"))
        self.assertTrue(has_identifier(section, "CpgRailRight"))
        self.assertTrue(has_identifier(leaked, SIBLING_CPG_TEDAC))
        self.assertTrue(has_identifier(section, SIBLING_CPG_TEDAC))
        self.assertTrue(has_identifier(leaked, SIBLING_CPG_EUFD))
        self.assertTrue(has_identifier(section, SIBLING_CPG_EUFD))
        self.assertTrue(has_identifier(leaked, SIBLING_CPG_TEDAC_BEZEL))
        self.assertTrue(has_identifier(section, SIBLING_CPG_TEDAC_BEZEL))
        self.assertTrue(has_identifier(leaked, SIBLING_CPG_RETICLE_H))
        self.assertTrue(has_identifier(section, SIBLING_CPG_RETICLE_H))
        self.assertTrue(has_identifier(leaked, SIBLING_CPG_RETICLE_V))
        self.assertTrue(has_identifier(section, SIBLING_CPG_RETICLE_V))
        self.assertTrue(has_identifier(leaked, SIBLING_CPG_GRIP_LEFT))
        self.assertTrue(has_identifier(section, SIBLING_CPG_GRIP_LEFT))
        self.assertTrue(has_identifier(leaked, SIBLING_CPG_GRIP_RIGHT))
        self.assertTrue(has_identifier(section, SIBLING_CPG_GRIP_RIGHT))
        self.assertTrue(has_identifier(leaked, SIBLING_CPG_CONSOLE_RIGHT))
        self.assertTrue(has_identifier(section, SIBLING_CPG_CONSOLE_RIGHT))
        self.assertTrue(has_identifier(leaked, SIBLING_CPG_RAIL_LEFT))
        self.assertTrue(has_identifier(section, SIBLING_CPG_RAIL_LEFT))
        self.assertTrue(has_identifier(leaked, SIBLING_CPG_TEDAC_TEXT))
        self.assertFalse(has_identifier(section, SIBLING_CPG_TEDAC_TEXT))
        self.assertTrue(has_identifier(leaked, SIBLING_CPG_MPD_LEFT_TEXT))
        self.assertFalse(has_identifier(section, SIBLING_CPG_MPD_LEFT_TEXT))
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, header)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, header)
        self.assertNotIn(STOP_BEFORE_EVENT_DEF, header)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAPON, header)
        self.assertNotIn(STOP_BEFORE_SORTIE, header)
        self.assertNotIn(leftover_retired_mount_class(), header)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, header)
        self.assertNotIn(STOP_BEFORE_MISSION_SPEC, header)
        self.assertNotIn(STOP_BEFORE_ARCADE_LOOK, header)
        self.assertNotIn(STOP_BEFORE_GUIDED_LOCK, header)
        self.assertNotIn(STOP_BEFORE_LOADOUT_SPEC, header)
        self.assertNotIn(STOP_BEFORE_ROSTER, header)
        for leftover in leftover_harbor_breaker_tokens():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, header)

    def test_parse_window_excludes_leftover_weapon_enum_body(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
        for leftover in leftover_weapon_enum_body_tokens():
            self.assertNotIn(leftover, section)
        for leftover in leftover_audio_event_enum_tokens():
            self.assertNotIn(leftover, section)
        for leftover in leftover_apache_ufunction_tokens():
            self.assertFalse(has_identifier(section, leftover), leftover)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other = (
            f"\t{TARGET_WRONG_FNAME}\n"
            f"\t{TARGET_WRONG_SEAT_PAN}\n"
            f"\t{TARGET_WRONG_SEAT_BACK}\n"
            f"\t{TARGET_WRONG_CANOPY}\n"
            f"\t{TARGET_WRONG_PILOT_CANOPY}\n"
            f"\t{TARGET_WRONG_CPG_STATION}\n"
            f"\t{TARGET_WRONG_CPG_COCKPIT}\n"
            f"\t{TARGET_WRONG_HEALTH}\n"
            "\tUSkyguardObjectiveRuntime* GetObjectiveRuntime() const;\n"
            "\tbool AddObjectiveProgress(\n"
            "\t\tFName ObjectiveId,\n"
            "\t\tint32 MedalTier);\n"
            "\tvoid BindRuntimeActors();\n"
            "\tvoid HandleDroneCityImpact();\n"
            "\tvoid ApplyDamage(float Amount);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other, LOCKED_DECL)
        self.assertIn("CpgRailRight", str(raised.exception))

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        self.assertEqual(
            UPROPERTY_VISIBLE_READONLY,
            'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
            'Category="Skyguard")',
        )
        self.assertIn("VisibleAnywhere", UPROPERTY_VISIBLE_READONLY)
        self.assertIn("BlueprintReadOnly", UPROPERTY_VISIBLE_READONLY)
        self.assertIn("Category", UPROPERTY_VISIBLE_READONLY)
        self.assertIn(
            'Category="Skyguard"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertNotIn(
            'Category="Skyguard|Apache"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertNotIn(
            'Category="Skyguard|Campaign"',
            UPROPERTY_VISIBLE_READONLY,
        )
        self.assertNotIn("EditAnywhere", UPROPERTY_VISIBLE_READONLY)
        self.assertNotIn("BlueprintReadWrite", UPROPERTY_VISIBLE_READONLY)
        self.assertNotIn("MultiLine", UPROPERTY_VISIBLE_READONLY)
        self.assertNotIn("ClampMin", UPROPERTY_VISIBLE_READONLY)
        self.assertNotIn("ClampMax", UPROPERTY_VISIBLE_READONLY)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, LOCKED_DECL)
            self.assertNotIn(invented, UPROPERTY_VISIBLE_READONLY)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        self.assertNotIn(".cpp", HEADER_PATH)
        self.assertTrue(HEADER_PATH.endswith(".h"))
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("SkyguardGunner.cpp", THIS_SCRIPT)
        self.assertIn("SkyguardGunner.h", HEADER_PATH)
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)
        self.assertNotIn("SkyguardProtectAsset.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignTheaterKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipTypes.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignRoster.h", HEADER_PATH)
        self.assertNotIn("SkyguardArcadeLookComponent.h", HEADER_PATH)
        self.assertNotIn("SkyguardGuidedLockRules.h", HEADER_PATH)

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
            self.assertFalse(leftover_harbor_token_in(locked_only, token))
            self.assertFalse(leftover_harbor_token_in(LOCKED_DECL, token))
            self.assertFalse(leftover_harbor_token_in(file_text, token))
        header = origin_main_header()
        section = spec_section(header)
        for token in leftover_harbor_tokens():
            self.assertFalse(leftover_harbor_token_in(section, token))

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "gunner CpgRailRight field decl contract "
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
            "gunner_cpg_rail_right_field_decl_contract.py"
        ))
        self.assertNotIn("SkyguardGunner.cpp", THIS_SCRIPT)
        self.assertIn(LEFTOVER_APACHE_SILHOUETTE_MESH, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_COCKPIT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_STATION, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_SEAT_BACK, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_SEAT_PAN, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_KNEE_LEFT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_KNEE_RIGHT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_CANOPY_BOW, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_DASH, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_TEDAC, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_MPD_LEFT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_MPD_RIGHT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_EUFD, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_TEDAC_BEZEL, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_RETICLE_H, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_RETICLE_V, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_GRIP_LEFT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUNNER_CPG_GRIP_RIGHT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_CANOPY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_PILOT_CANOPY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_THEATER_KIT_BULK, LOCKED_SCRIPTS)
        self.assertIn(CLONE_CURRENT_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_MAX_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_HULL_COLLIDER, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_CURRENT_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_MAX_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_EMPTY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_EMPTY_CONTRACT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_OWN_SHIP, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_CPG_FEEL, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_MOUNT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_HULL_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_CAMPAIGN_ROSTER_LOOKUP, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_SORTIE_DIRECTOR_EMPTY, LOCKED_SCRIPTS)
        for leftover in leftover_apache_ufunction_scripts():
            self.assertIn(leftover, LOCKED_SCRIPTS)
        self.assertIn(CLONE_RESET_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_APPLY_DAMAGE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_IS_DESTROYED, LOCKED_SCRIPTS)
        self.assertIn(CLONE_GET_INTEGRITY_FRACTION, LOCKED_SCRIPTS)
        self.assertIn(CLONE_MAX_HEALTH, LOCKED_SCRIPTS)
        self.assertIn(CLONE_RADAR_IS_DESTROYED, LOCKED_SCRIPTS)
        self.assertIn(CLONE_PEAK_ACTIVE_VOICES, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_PROTECT_ASSET_CARGO_PROXY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_OBJECTIVE_ID, LOCKED_SCRIPTS)
        self.assertIn(CLONE_FINAL_SCORE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_MISSION_RESULT_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(CLONE_HOW_TO_FLY_STEP_ID, LOCKED_SCRIPTS)
        self.assertIn(CLONE_CARD_ID, LOCKED_SCRIPTS)
        self.assertIn(CLONE_TITLE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_BODY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_PRIORITY, LOCKED_SCRIPTS)

    def test_leftover_mission_result_defaults_stay_locked(self) -> None:
        leftovers = (
            LEFTOVER_MISSION_RESULT_DEFAULTS,
            LEFTOVER_MISSION_DEBRIEF_DEFAULTS,
            LEFTOVER_OBJECTIVE_PROGRESS_DEFAULTS,
            LEFTOVER_ADD_OBJECTIVE_PROGRESS,
            CLONE_CAMPAIGN_COMPLETE,
            CLONE_WEAK_POINTS_DESTROYED,
            CLONE_PILOT_COMMANDS_ISSUED,
            CLONE_PLAYED_EVENTS,
            CLONE_REQUESTED_EVENTS,
            CLONE_REJECTED_BY_COOLDOWN,
            CLONE_REJECTED_BY_CONCURRENCY,
            CLONE_REJECTED_MISSING_ASSET,
            CLONE_PRIORITY_EVICTIONS,
            CLONE_PEAK_ACTIVE_VOICES,
            LEFTOVER_AUDIO_TELEMETRY_DEFAULTS,
            LEFTOVER_AUDIO_TELEMETRY_DEFAULTS_PY,
            LEFTOVER_AUDIO_TELEMETRY_DEFAULTS_TESTS,
            LEFTOVER_AUDIO_DIRECTOR_TELEMETRY,
            LEFTOVER_AUDIO_DIRECTOR_TELEMETRY_TESTS,
            LEFTOVER_AUDIO_DIRECTOR_TELEMETRY_CONTRACT,
            LEFTOVER_PROTECT_ASSET_CARGO_PROXY,
            LEFTOVER_PROTECT_ASSET_CARGO_PROXY_CONTRACT,
            LEFTOVER_PROTECT_ASSET_CARGO_PROXY_TESTS,
            CLONE_IS_DESTROYED,
            CLONE_GET_INTEGRITY_FRACTION,
            CLONE_APPLY_DAMAGE,
            CLONE_RESET_INTEGRITY,
            CLONE_MAX_INTEGRITY,
            CLONE_CURRENT_INTEGRITY,
            CLONE_MAX_HEALTH,
            CLONE_RADAR_IS_DESTROYED,
            CLONE_RADAR_APPLY_DAMAGE,
            CLONE_RADAR_RESET_NODE,
            LEFTOVER_RADAR_NODE_PRESENTATION,
            LEFTOVER_RADAR_NODE_PRESENTATION_TESTS,
            LEFTOVER_RADAR_NODE_PRESENTATION_CONTRACT,
            LEFTOVER_RADAR_NODE_RESET_GAMEPLAY,
            LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_TESTS,
            LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_CONTRACT,
            CLONE_OBJECTIVE_ID,
            CLONE_CURRENT_PROGRESS,
            CLONE_STATE,
            CLONE_FINAL_SCORE,
            CLONE_MEDAL_TIER,
            CLONE_DEBRIEF_STATE,
            CLONE_DEBRIEF_RESULT,
            CLONE_MISSION_DISPLAY_NAME,
            CLONE_NARRATIVE,
            CLONE_NEW_BEST_SCORE,
            CLONE_NEW_BEST_MEDAL,
            CLONE_PROGRESS_SAVED,
            CLONE_SAVE_SLOT_NAME,
            CLONE_NEXT_MISSION_ID,
            CLONE_NEXT_MISSION_DISPLAY_NAME,
            CLONE_NEXT_MISSION_MAP,
            CLONE_NEXT_MISSION_UNLOCKED,
            LEFTOVER_THEATER_KIT_BULK,
            LEFTOVER_APACHE_SILHOUETTE_MESH,
            LEFTOVER_GUNNER_CPG_COCKPIT,
            LEFTOVER_GUNNER_CPG_STATION,
            LEFTOVER_GUNNER_CPG_SEAT_BACK,
            LEFTOVER_GUNNER_CPG_SEAT_PAN,
            LEFTOVER_GUNNER_CPG_KNEE_LEFT,
            LEFTOVER_GUNNER_CPG_KNEE_RIGHT,
            LEFTOVER_GUNNER_CPG_CANOPY_BOW,
            LEFTOVER_GUNNER_CPG_DASH,
            LEFTOVER_GUNNER_CPG_TEDAC,
            LEFTOVER_GUNNER_CPG_MPD_LEFT,
            LEFTOVER_GUNNER_CPG_MPD_RIGHT,
            LEFTOVER_GUNNER_CPG_EUFD,
            LEFTOVER_GUNNER_CPG_TEDAC_BEZEL,
            LEFTOVER_GUNNER_CPG_RETICLE_H,
            LEFTOVER_GUNNER_CPG_RETICLE_V,
            LEFTOVER_GUNNER_CPG_GRIP_LEFT,
            LEFTOVER_GUNNER_CPG_GRIP_RIGHT,
            LEFTOVER_APACHE_CANOPY,
            LEFTOVER_APACHE_PILOT_CANOPY,
            LEFTOVER_APACHE_HULL_COLLIDER,
            LEFTOVER_APACHE_CURRENT_INTEGRITY,
            LEFTOVER_APACHE_MAX_INTEGRITY,
            LEFTOVER_APACHE_EMPTY,
            LEFTOVER_APACHE_CPG_FEEL,
            LEFTOVER_APACHE_OWN_SHIP,
            LEFTOVER_APACHE_MOUNT,
            LEFTOVER_LOADOUT_HULL_INTEGRITY,
            LEFTOVER_CAMPAIGN_ROSTER_LOOKUP,
            LEFTOVER_SORTIE_DIRECTOR_EMPTY,
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
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, locked_only)
        self.assertNotIn(GET_OBJECTIVE_RUNTIME, locked_only)
        self.assertNotIn(ADD_OBJECTIVE_PROGRESS, locked_only)
        self.assertNotIn("FSkyguardObjectiveProgress", locked_only)
        self.assertNotIn("ESkyguardAudioEvent", locked_only)
        self.assertNotIn("ESkyguardBriefingPictogram", locked_only)
        self.assertNotIn("FSkyguardAudioEventDefinition", locked_only)
        self.assertNotIn("FSkyguardAudioTelemetry", locked_only)
        self.assertNotIn("ESkyguardBossWeapon", locked_only)
        self.assertNotIn("ESkyguardPilotCommand", locked_only)
        self.assertNotIn("PeakActiveVoices", locked_only)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_THEATER_KIT_ACTOR, locked_only)
        self.assertNotIn(STOP_BEFORE_SORTIE, locked_only)
        self.assertNotIn(STOP_BEFORE_MISSION_SPEC, locked_only)
        self.assertNotIn(STOP_BEFORE_ARCADE_LOOK, locked_only)
        self.assertNotIn(STOP_BEFORE_GUIDED_LOCK, locked_only)
        self.assertNotIn(SIBLING_HULL_COLLIDER, locked_only)
        self.assertNotIn(SIBLING_MAX_INTEGRITY, locked_only)
        self.assertNotIn(SIBLING_CURRENT_INTEGRITY, locked_only)
        self.assertNotIn(SIBLING_CPG_SEAT_PAN, locked_only)
        self.assertNotIn(SIBLING_CPG_SEAT_BACK, locked_only)
        self.assertNotIn(SIBLING_CPG_KNEE_LEFT, locked_only)
        self.assertNotIn(SIBLING_CPG_KNEE_RIGHT, locked_only)
        self.assertNotIn(SIBLING_CPG_CANOPY_BOW, locked_only)
        self.assertNotIn(SIBLING_CPG_DASH, locked_only)
        self.assertNotIn(SIBLING_CPG_TEDAC, locked_only)
        self.assertNotIn(SIBLING_CPG_MPD_LEFT, locked_only)
        self.assertNotIn(SIBLING_CPG_MPD_RIGHT, locked_only)
        self.assertNotIn(SIBLING_CPG_EUFD, locked_only)
        self.assertNotIn(SIBLING_CPG_TEDAC_BEZEL, locked_only)
        self.assertNotIn(SIBLING_CPG_RETICLE_H, locked_only)
        self.assertNotIn(SIBLING_CPG_RETICLE_V, locked_only)
        self.assertNotIn(SIBLING_CPG_GRIP_LEFT, locked_only)
        self.assertNotIn(SIBLING_CPG_GRIP_RIGHT, locked_only)
        self.assertNotIn(SIBLING_CPG_CONSOLE_RIGHT, locked_only)
        self.assertNotIn(SIBLING_CPG_RAIL_LEFT, locked_only)
        self.assertNotIn(SIBLING_CPG_TEDAC_TEXT, locked_only)
        self.assertNotIn(SIBLING_CPG_MPD_LEFT_TEXT, locked_only)
        self.assertNotIn(SIBLING_HAND_MESH, locked_only)
        self.assertNotIn(SIBLING_CPG_EUFD_TEXT, locked_only)
        self.assertNotIn(SIBLING_CPG_COCKPIT, locked_only)
        self.assertNotIn(SIBLING_CPG_STATION, locked_only)
        self.assertNotIn("Canopy;", locked_only)
        self.assertNotIn("PilotCanopy", locked_only)
        self.assertNotIn(SIBLING_FUSELAGE, locked_only)
        self.assertNotIn(SIBLING_AIRCRAFT_ROOT, locked_only)
        self.assertNotIn(SIBLING_ROTOR_POWER, locked_only)
        self.assertNotIn(SIBLING_HOVER_BOB, locked_only)
        self.assertNotIn(leftover_banned_primary_mesh(), locked_only)
        self.assertNotIn(leftover_banned_guided_tube(), locked_only)
        self.assertNotIn("WeatherIdentity", locked_only)
        for leftover in leftover_apache_ufunction_tokens():
            self.assertNotIn(leftover, locked_only)


if __name__ == "__main__":
    unittest.main()
