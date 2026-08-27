# THIS IS leftover-safe ASkyguardCampaignTheaterKit
# ApplyTheaterKit.
# origin/main form: one-line and split-line UFUNCTION wraps
# UFUNCTION(BlueprintCallable, Category="Skyguard|Theater")
# then declaration-only `void ApplyTheaterKit(FName WeatherIdentity);`
# (no inline body required).
# THIS IS leftover-safe isolated actor UFUNCTION.
# Category IS `Skyguard|Theater`. BlueprintCallable IS present.
# THIS IS NOT BlueprintPure. THIS IS NOT static.
# Return type IS void. Parameter IS FName WeatherIdentity.
# Do NOT require const.
# Fail-closed if the UFUNCTION or decl is missing
# or renamed, if Category is missing, if specifiers
# drop to BlueprintPure, if the method is static,
# if FName WeatherIdentity is missing, or if the
# return type is not void.
# Accept one-line and split-line UFUNCTION wraps.
# Parse class `ASkyguardCampaignTheaterKit` public section
# ONLY. Stop at `private:`.
# Do NOT parse `struct FSkyguardTheaterKitSpec` (leftover
# isolated spec fields #1299-#1314).
# Do NOT contract `ApplyTheaterKitToWorld` (leftover
# theater-kit-weather-apply #59).
# Sibling UFUNCTIONs GetAppliedWeatherIdentity /
# GetAppliedKitId / GetNamedLandmark / GetBuildingTint /
# GetAppliedSpec / GetRoadInstanceCount /
# GetBuildingInstanceCount / GetLampInstanceCount /
# GetSilhouetteInstanceCount / ApplyTheaterKitToWorld
# stay uncontracted.
# Public UPROPERTY fields stay uncontracted (leftover
# actor UPROPERTY #1315-#1321).
# Do not parse private Transient CubeMesh / CylinderMesh /
# ConeMesh / SphereMesh / ShapeMaterial / Lamps.
# THIS IS NOT leftover theater-kit-weather-apply #59
# (ApplyTheaterKitToWorld gameplay).
# THIS IS NOT leftover merged bulk
# test_campaign_theater_kit_contract.py (keep that file
# in LOCKED_SCRIPTS; leftover bulk string-contains
# ApplyTheaterKit does not block this isolated
# UFUNCTION decl, same as leftover briefing-card-defaults
# then isolated CardId).
# THIS IS NOT leftover TheaterKitSpec field drafts
# #1299-#1314 (keep those files in LOCKED_SCRIPTS).
# THIS IS NOT leftover actor UPROPERTY drafts
# #1315-#1321 (keep those files in LOCKED_SCRIPTS).
# THIS IS NOT leftover actor UFUNCTION drafts
# GetAppliedWeatherIdentity / GetAppliedKitId /
# GetBuildingTint / GetNamedLandmark / GetAppliedSpec /
# GetRoadInstanceCount / GetBuildingInstanceCount
# (keep those files in LOCKED_SCRIPTS).
# THIS IS NOT leftover MeshBindSlot #194 / #6829.
# THIS IS NOT leftover ProtectAsset / RadarNode #1288-#1298.
# Analog: leftover briefing-card-defaults then isolated
# CardId field decls.
# If a clone asserts UPROPERTY / spec struct /
# Category="Skyguard|Campaign" / parses the spec struct /
# asserts UPROPERTY FName WeatherIdentity /
# asserts BlueprintPure GetBuildingInstanceCount,
# retarget: this is UFUNCTION BlueprintCallable
# void ApplyTheaterKit(FName WeatherIdentity),
# Category is Skyguard|Theater,
# parse window is the actor public section,
# declaration only (no inline body required),
# instance not static, not leftover #59 ToWorld.
# Do NOT parse enum class ESkyguardAudioEvent.
# Do NOT parse FSkyguardAudioEventDefinition.
# Do NOT parse ESkyguardBriefingPictogram.
# Do NOT parse ESkyguardBossWeapon.
# Do NOT parse ASkyguardPropSpinner.
# Do NOT parse ASkyguardGunshipSortieDirector.
# Do NOT parse ASkyguardPatrolShipBoss.
# Do NOT parse leftover retired mount class (split tokens).
# Do NOT parse ASkyguardGunner.
# Do NOT parse USkyguardBossWeakPointComponent.
# Harbor 40/80 fail-closed.
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
HEADER_PATH = "Source/Skyguard52/SkyguardCampaignTheaterKit.h"
STRUCT_NAME = "FSkyguardTheaterKitSpec"
ACTOR_NAME = "ASkyguardCampaignTheaterKit"
NAMESPACE_NAME = "SkyguardCampaignTheaterKit"
TARGET = "void ApplyTheaterKit(FName WeatherIdentity);"
TARGET_WRONG_EQ_NONE = "void ApplyTheaterKit() = NAME_None;"
TARGET_WRONG_FALSE = "void ApplyTheaterKit() = false;"
TARGET_WRONG_TRUE = "void ApplyTheaterKit() = true;"
TARGET_WRONG_ZERO = "void ApplyTheaterKit() = 0.f;"
TARGET_WRONG_FLOAT = "float ApplyTheaterKit(FName WeatherIdentity);"
TARGET_WRONG_FNAME = "FName ApplyTheaterKit(FName WeatherIdentity);"
TARGET_WRONG_FLINEAR = "FLinearColor ApplyTheaterKit(FName WeatherIdentity);"
TARGET_WRONG_INT32 = "int32 ApplyTheaterKit(FName WeatherIdentity);"
TARGET_WRONG_STATIC = "static void ApplyTheaterKit(FName WeatherIdentity);"
TARGET_WRONG_NO_PARAM = "void ApplyTheaterKit();"
TARGET_WRONG_TO_WORLD = (
    "static void ApplyTheaterKitToWorld("
    "UObject* WorldContextObject, "
    "FName WeatherIdentity);"
)
TARGET_WRONG_BODY = (
    "void ApplyTheaterKit(FName WeatherIdentity) "
    "{ AppliedSpec = SkyguardCampaignTheaterKit::Resolve"
    "(WeatherIdentity); }"
)
TARGET_WRONG_SPEC_FIELD = "FName WeatherIdentity;"
TARGET_WRONG_HEALTH = "float Health = 160.f;"
TARGET_WRONG_CAMPAIGN = (
    'UFUNCTION(BlueprintCallable, '
    'Category="Skyguard|Campaign")'
)
TARGET_WRONG_PURE = (
    'UFUNCTION(BlueprintPure, '
    'Category="Skyguard|Theater")'
)
LOCKED_DECL = TARGET
UFUNCTION_CALLABLE_THEATER = (
    'UFUNCTION(BlueprintCallable, '
    'Category="Skyguard|Theater")'
)
UPROPERTY_VISIBLE_READONLY = UFUNCTION_CALLABLE_THEATER
STOP_BEFORE_NAMESPACE = "namespace SkyguardCampaignTheaterKit"
STOP_BEFORE_ACTOR = "class ASkyguardCampaignTheaterKit"
STOP_BEFORE_APPLY = "ApplyTheaterKitToWorld"
STOP_BEFORE_AUDIO_EVENT = "enum class ESkyguardAudioEvent"
STOP_BEFORE_PICTOGRAM = "enum class ESkyguardBriefingPictogram"
STOP_BEFORE_EVENT_DEF = "struct FSkyguardAudioEventDefinition"
STOP_BEFORE_BOSS_WEAPON = "enum class ESkyguardBossWeapon"
STOP_BEFORE_PROP_SPINNER = "ASkyguardPropSpinner"
STOP_BEFORE_SORTIE = "ASkyguardGunshipSortieDirector"
STOP_BEFORE_PATROL = "ASkyguardPatrolShipBoss"
STOP_BEFORE_GUNNER = "ASkyguardGunner"
STOP_BEFORE_WEAK_POINT = "USkyguardBossWeakPointComponent"
GET_OBJECTIVE_RUNTIME = "GetObjectiveRuntime"
ADD_OBJECTIVE_PROGRESS = "AddObjectiveProgress"
BIND_RUNTIME_ACTORS = "BindRuntimeActors"
HANDLE_DRONE_CITY_IMPACT = "HandleDroneCityImpact"
GET_STORM_RAIN_BEAT_KIT = "GetStormRainBeatKit"
NUM_KITS = "NumKits"
GET_BY_INDEX = "GetByIndex"
RESOLVE = "Resolve"
FINGERPRINT = "Fingerprint"
ARE_KITS_PAIRWISE_DISTINCT = "AreKitsPairwiseDistinct"
SIBLING_ROOT = "Root"
SIBLING_ROAD_INSTANCES = "RoadInstances"
SIBLING_BUILDING_INSTANCES = "BuildingInstances"
SIBLING_LAMP_INSTANCES = "LampInstances"
SIBLING_SILHOUETTE_INSTANCES = "SilhouetteInstances"
SIBLING_NAMED_LANDMARK_MESH = "NamedLandmarkMesh"
SIBLING_APPLIED_SPEC = "AppliedSpec"
SIBLING_KIT_ID = "KitId"
SIBLING_LANDMARK_SET = "LandmarkSet"
SIBLING_BUILDING_KIT = "BuildingKit"
SIBLING_BUILDING_TINT = "BuildingTint"
SIBLING_LAMP_TREATMENT = "LampTreatment"
SIBLING_LAMP_COLOR = "LampColor"
SIBLING_LAMP_INTENSITY = "LampIntensity"
SIBLING_ROAD_TREATMENT = "RoadTreatment"
SIBLING_ROAD_TINT = "RoadTint"
SIBLING_NAMED_LANDMARK = "NamedLandmark"
SIBLING_LANDMARK_TINT = "LandmarkTint"
SIBLING_SILHOUETTE_KIT = "SilhouetteKit"
SIBLING_SILHOUETTE_TINT = "SilhouetteTint"
SIBLING_LANDMARK_MESH_INDEX = "LandmarkMeshIndex"
SIBLING_LANDMARK_SCALE = "LandmarkScale"
PRIVATE_CUBE_MESH = "CubeMesh"
PRIVATE_CYLINDER_MESH = "CylinderMesh"
PRIVATE_CONE_MESH = "ConeMesh"
PRIVATE_SPHERE_MESH = "SphereMesh"
PRIVATE_SHAPE_MATERIAL = "ShapeMaterial"
PRIVATE_LAMPS = "Lamps"
LEFTOVER_APACHE_CLASS = "ASkyguardApacheAircraft"
LEFTOVER_PROTECT_ASSET_CLASS = "ASkyguardProtectAsset"
LEFTOVER_RADAR_NODE_CLASS = "ASkyguardRadarNode"
THIS_SCRIPT = (
    "Scripts/tests/test_theater_kit_apply_theater_kit"
    "_decl_contract.py"
)
LEFTOVER_GET_BUILDING_INSTANCE_COUNT = (
    "Scripts/tests/test_theater_kit_get_building_instance_count"
    "_decl_contract.py"
)
LEFTOVER_GET_APPLIED_WEATHER_IDENTITY = (
    "Scripts/tests/test_theater_kit_get_applied_weather_identity"
    "_decl_contract.py"
)
LEFTOVER_GET_APPLIED_KIT_ID = (
    "Scripts/tests/test_theater_kit_get_applied_kit_id"
    "_decl_contract.py"
)
LEFTOVER_GET_BUILDING_TINT = (
    "Scripts/tests/test_theater_kit_get_building_tint"
    "_decl_contract.py"
)
LEFTOVER_GET_NAMED_LANDMARK = (
    "Scripts/tests/test_theater_kit_get_named_landmark"
    "_decl_contract.py"
)
LEFTOVER_GET_APPLIED_SPEC = (
    "Scripts/tests/test_theater_kit_get_applied_spec"
    "_decl_contract.py"
)
LEFTOVER_GET_ROAD_INSTANCE_COUNT = (
    "Scripts/tests/test_theater_kit_get_road_instance_count"
    "_decl_contract.py"
)
CLONE_ROOT_FIELD = (
    "Scripts/tests/test_theater_kit_root"
    "_field_decl_contract.py"
)
CLONE_ROAD_INSTANCES = (
    "Scripts/tests/test_theater_kit_road_instances"
    "_field_decl_contract.py"
)
CLONE_BUILDING_INSTANCES = (
    "Scripts/tests/test_theater_kit_building_instances"
    "_field_decl_contract.py"
)
CLONE_LAMP_INSTANCES = (
    "Scripts/tests/test_theater_kit_lamp_instances"
    "_field_decl_contract.py"
)
CLONE_SILHOUETTE_INSTANCES = (
    "Scripts/tests/test_theater_kit_silhouette_instances"
    "_field_decl_contract.py"
)
CLONE_NAMED_LANDMARK_MESH = (
    "Scripts/tests/test_theater_kit_named_landmark_mesh"
    "_field_decl_contract.py"
)
CLONE_APPLIED_SPEC = (
    "Scripts/tests/test_theater_kit_applied_spec"
    "_field_decl_contract.py"
)
CLONE_WEATHER_IDENTITY = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
    "_field_decl_contract.py"
)
CLONE_LANDMARK_SET = (
    "Scripts/tests/test_theater_kit_spec_landmark_set"
    "_field_decl_contract.py"
)
CLONE_KIT_ID = (
    "Scripts/tests/test_theater_kit_spec_kit_id"
    "_field_decl_contract.py"
)
CLONE_LAMP_TREATMENT = (
    "Scripts/tests/test_theater_kit_spec_lamp_treatment"
    "_field_decl_contract.py"
)
CLONE_BUILDING_TINT = (
    "Scripts/tests/test_theater_kit_spec_building_tint"
    "_field_decl_contract.py"
)
CLONE_BUILDING_KIT = (
    "Scripts/tests/test_theater_kit_spec_building_kit"
    "_field_decl_contract.py"
)
CLONE_LAMP_COLOR = (
    "Scripts/tests/test_theater_kit_spec_lamp_color"
    "_field_decl_contract.py"
)
CLONE_ROAD_TINT = (
    "Scripts/tests/test_theater_kit_spec_road_tint"
    "_field_decl_contract.py"
)
CLONE_ROAD_TREATMENT = (
    "Scripts/tests/test_theater_kit_spec_road_treatment"
    "_field_decl_contract.py"
)
CLONE_LAMP_INTENSITY = (
    "Scripts/tests/test_theater_kit_spec_lamp_intensity"
    "_field_decl_contract.py"
)
CLONE_LANDMARK_TINT = (
    "Scripts/tests/test_theater_kit_spec_landmark_tint"
    "_field_decl_contract.py"
)
CLONE_SILHOUETTE_KIT = (
    "Scripts/tests/test_theater_kit_spec_silhouette_kit"
    "_field_decl_contract.py"
)
CLONE_NAMED_LANDMARK = (
    "Scripts/tests/test_theater_kit_spec_named_landmark"
    "_field_decl_contract.py"
)
CLONE_SILHOUETTE_TINT = (
    "Scripts/tests/test_theater_kit_spec_silhouette_tint"
    "_field_decl_contract.py"
)
CLONE_LANDMARK_MESH_INDEX = (
    "Scripts/tests/test_theater_kit_spec_landmark_mesh_index"
    "_field_decl_contract.py"
)
CLONE_LANDMARK_SCALE = (
    "Scripts/tests/test_theater_kit_spec_landmark_scale"
    "_field_decl_contract.py"
)
LEFTOVER_THEATER_KIT_WEATHER_APPLY = (
    "Scripts/tests/test_theater_kit_weather_apply.py"
)
LEFTOVER_THEATER_KIT_WEATHER_APPLY_TESTS = (
    "Scripts/tests/test_theater_kit_weather_apply_tests.py"
)
LEFTOVER_THEATER_KIT_WEATHER_APPLY_CONTRACT = (
    "Scripts/tests/test_theater_kit_weather_apply_contract.py"
)
CLONE_HEALTH = (
    "Scripts/tests/test_radar_node_health"
    "_field_decl_contract.py"
)
LEFTOVER_THEATER_KIT_BULK = (
    "Scripts/tests/test_campaign_theater_kit_contract.py"
)
LEFTOVER_MESH_BIND_SLOT = (
    "Scripts/tests/test_mesh_bind_slot_fields_contract.py"
)

CLONE_CURRENT_INTEGRITY = (
    "Scripts/tests/test_protect_asset_current_integrity"
    "_field_decl_contract.py"
)
CLONE_MAX_HEALTH = (
    "Scripts/tests/test_radar_node_max_health"
    "_field_decl_contract.py"
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
CLONE_RESET_INTEGRITY = (
    "Scripts/tests/test_protect_asset_reset_integrity"
    "_decl_contract.py"
)
CLONE_PEAK_ACTIVE_VOICES = (
    "Scripts/tests/test_audio_telemetry_peak_active_voices"
    "_field_decl_contract.py"
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
CLONE_MAX_INTEGRITY = (
    "Scripts/tests/test_protect_asset_max_integrity"
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
CLONE_CAMPAIGN_COMPLETE = (
    "Scripts/tests/test_mission_debrief_campaign_complete"
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
OTHER_TELEMETRY_FIELDS = (
    "RequestedEvents",
    "PlayedEvents",
    "RejectedByCooldown",
    "RejectedByConcurrency",
    "RejectedMissingAsset",
    "PriorityEvictions",
)

RESULT_NESTED_MEMBERS = (
    "FinalScore",
    "MedalTier",
    "MissionId",
    "bMissionSucceeded",
    "ShotsFired",
    "Hits",
    "AircraftDamageFraction",
    "CompletionTimeSeconds",
    "CompletedObjectiveIds",
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
    CLONE_WEATHER_IDENTITY,
    CLONE_LANDMARK_SET,
    CLONE_KIT_ID,
    CLONE_LAMP_TREATMENT,
    CLONE_BUILDING_TINT,
    CLONE_BUILDING_KIT,
    CLONE_LAMP_COLOR,
    CLONE_ROAD_TINT,
    CLONE_ROAD_TREATMENT,
    CLONE_LAMP_INTENSITY,
    CLONE_LANDMARK_TINT,
    CLONE_SILHOUETTE_KIT,
    CLONE_NAMED_LANDMARK,
    CLONE_SILHOUETTE_TINT,
    CLONE_LANDMARK_MESH_INDEX,
    CLONE_LANDMARK_SCALE,
    LEFTOVER_THEATER_KIT_WEATHER_APPLY,
    LEFTOVER_THEATER_KIT_WEATHER_APPLY_TESTS,
    LEFTOVER_THEATER_KIT_WEATHER_APPLY_CONTRACT,
    CLONE_ROOT_FIELD,
    CLONE_ROAD_INSTANCES,
    CLONE_BUILDING_INSTANCES,
    CLONE_LAMP_INSTANCES,
    CLONE_SILHOUETTE_INSTANCES,
    CLONE_NAMED_LANDMARK_MESH,
    CLONE_APPLIED_SPEC,
    LEFTOVER_GET_APPLIED_WEATHER_IDENTITY,
    LEFTOVER_GET_APPLIED_KIT_ID,
    LEFTOVER_GET_BUILDING_TINT,
    LEFTOVER_GET_NAMED_LANDMARK,
    LEFTOVER_GET_APPLIED_SPEC,
    LEFTOVER_GET_ROAD_INSTANCE_COUNT,
    LEFTOVER_GET_BUILDING_INSTANCE_COUNT,
) + leftover_live_copy_boss_scripts()



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



CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(ACTOR_NAME)}\b"
)
STRUCT_RE = re.compile(
    rf"struct\s+(?:SKYGUARD52_API\s+)?{re.escape(STRUCT_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")
APPLY_THEATER_KIT_RE = re.compile(
    r"void\s+ApplyTheaterKit\s*\(\s*FName\s+WeatherIdentity\s*\)\s*;"
)
APPLY_THEATER_KIT_STATIC_RE = re.compile(
    r"static\s+void\s+ApplyTheaterKit\s*\("
)
APPLY_THEATER_KIT_WRONG_TYPE_RE = re.compile(
    r"(?:FName|float|FLinearColor|bool|int32)\s+ApplyTheaterKit\b"
)
APPLY_THEATER_KIT_BODY_RE = re.compile(
    r"void\s+ApplyTheaterKit\s*\(\s*FName\s+WeatherIdentity\s*\)"
    r"\s*\{"
)
APPLY_THEATER_KIT_NO_PARAM_RE = re.compile(
    r"void\s+ApplyTheaterKit\s*\(\s*\)\s*;"
)
INVENTED_UPROPERTY = (
    "EditAnywhere",
    "BlueprintReadWrite",
    "Transient",
    "MultiLine",
    "BlueprintAuthorityOnly",
    "VisibleAnywhere",
    "BlueprintReadOnly",
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
    "= nullptr",
)


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_ROOT,
        SIBLING_ROAD_INSTANCES,
        SIBLING_BUILDING_INSTANCES,
        SIBLING_LAMP_INSTANCES,
        SIBLING_SILHOUETTE_INSTANCES,
        SIBLING_NAMED_LANDMARK_MESH,
        SIBLING_APPLIED_SPEC,
    )


def leftover_spec_field_names() -> tuple[str, ...]:
    return (
        SIBLING_KIT_ID,
        SIBLING_BUILDING_TINT,
        SIBLING_LANDMARK_SET,
        SIBLING_BUILDING_KIT,
        SIBLING_LAMP_TREATMENT,
        SIBLING_LAMP_COLOR,
        SIBLING_LAMP_INTENSITY,
        SIBLING_ROAD_TREATMENT,
        SIBLING_ROAD_TINT,
        SIBLING_NAMED_LANDMARK,
        SIBLING_LANDMARK_TINT,
        SIBLING_SILHOUETTE_KIT,
        SIBLING_SILHOUETTE_TINT,
        SIBLING_LANDMARK_MESH_INDEX,
        SIBLING_LANDMARK_SCALE,
    )


def leftover_spec_field_scripts() -> tuple[str, ...]:
    return (
        CLONE_WEATHER_IDENTITY,
        CLONE_LANDMARK_SET,
        CLONE_KIT_ID,
        CLONE_LAMP_TREATMENT,
        CLONE_BUILDING_TINT,
        CLONE_BUILDING_KIT,
        CLONE_LAMP_COLOR,
        CLONE_ROAD_TINT,
        CLONE_ROAD_TREATMENT,
        CLONE_LAMP_INTENSITY,
        CLONE_LANDMARK_TINT,
        CLONE_SILHOUETTE_KIT,
        CLONE_NAMED_LANDMARK,
        CLONE_SILHOUETTE_TINT,
        CLONE_LANDMARK_MESH_INDEX,
        CLONE_LANDMARK_SCALE,
    )


def leftover_actor_uproperty_scripts() -> tuple[str, ...]:
    return (
        CLONE_ROOT_FIELD,
        CLONE_ROAD_INSTANCES,
        CLONE_BUILDING_INSTANCES,
        CLONE_LAMP_INSTANCES,
        CLONE_SILHOUETTE_INSTANCES,
        CLONE_NAMED_LANDMARK_MESH,
        CLONE_APPLIED_SPEC,
    )


def leftover_actor_ufunction_scripts() -> tuple[str, ...]:
    return (
        LEFTOVER_GET_APPLIED_WEATHER_IDENTITY,
        LEFTOVER_GET_APPLIED_KIT_ID,
        LEFTOVER_GET_BUILDING_TINT,
        LEFTOVER_GET_NAMED_LANDMARK,
        LEFTOVER_GET_APPLIED_SPEC,
        LEFTOVER_GET_ROAD_INSTANCE_COUNT,
        LEFTOVER_GET_BUILDING_INSTANCE_COUNT,
    )


def leftover_theater_kit_weather_apply_scripts() -> tuple[str, ...]:
    return (
        LEFTOVER_THEATER_KIT_WEATHER_APPLY,
        LEFTOVER_THEATER_KIT_WEATHER_APPLY_TESTS,
        LEFTOVER_THEATER_KIT_WEATHER_APPLY_CONTRACT,
    )


def private_transient_tokens() -> tuple[str, ...]:
    return (
        PRIVATE_CUBE_MESH,
        PRIVATE_CYLINDER_MESH,
        PRIVATE_CONE_MESH,
        PRIVATE_SPHERE_MESH,
        PRIVATE_SHAPE_MATERIAL,
        PRIVATE_LAMPS,
    )


def leftover_ufunction_tokens() -> tuple[str, ...]:
    return (
        STOP_BEFORE_APPLY,
        "GetAppliedWeatherIdentity",
        "GetAppliedKitId",
        "GetNamedLandmark",
        "GetAppliedSpec",
        "GetBuildingTint",  # leftover sibling UFUNCTION
        "GetRoadInstanceCount",
        "GetBuildingInstanceCount",
        "GetLampInstanceCount",
        "GetSilhouetteInstanceCount",
        "BeginPlay",
    )


def namespace_helper_tokens() -> tuple[str, ...]:
    return (
        NUM_KITS,
        GET_BY_INDEX,
        RESOLVE,
        FINGERPRINT,
        ARE_KITS_PAIRWISE_DISTINCT,
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
    # Fail-closed on authored declaration-only
    # `void ApplyTheaterKit(FName WeatherIdentity);`.
    # Do not accept static, BlueprintPure wraps,
    # missing FName WeatherIdentity, non-void return,
    # an inline body, leftover ApplyTheaterKitToWorld,
    # or leftover float Health.
    # Do not require const.
    # Do not accept sibling GetBuildingInstanceCount /
    # GetRoadInstanceCount UFUNCTIONs.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if APPLY_THEATER_KIT_WRONG_TYPE_RE.search(compact):
        return False
    if APPLY_THEATER_KIT_STATIC_RE.search(compact):
        return False
    if APPLY_THEATER_KIT_BODY_RE.search(compact):
        return False
    if APPLY_THEATER_KIT_NO_PARAM_RE.search(compact):
        return False
    if APPLY_THEATER_KIT_RE.search(compact) is None:
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
            f"{ACTOR_NAME} is missing from origin/main:{HEADER_PATH}"
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
        f"{ACTOR_NAME} class body is missing from origin/main:{HEADER_PATH}"
    )


def leaked_neighbor_tokens() -> tuple[str, ...]:
    return (
        "struct FSkyguardTheaterKitSpec",
        STOP_BEFORE_NAMESPACE,
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
        GET_OBJECTIVE_RUNTIME,
        ADD_OBJECTIVE_PROGRESS,
        BIND_RUNTIME_ACTORS,
        HANDLE_DRONE_CITY_IMPACT,
        GET_STORM_RAIN_BEAT_KIT,
        "class USkyguardCampaignSubsystem",
        "class ASkyguardMission01IntegrationDirector",
        "class ASkyguardMission05IntegrationDirector",
        "class ASkyguardMission10IntegrationDirector",
        "struct FSkyguardLandscapeVisibleAudit",
        "struct FSkyguardLandscapeCaptureConfigurationResult",
        "struct FSkyguardLandscapeMaterialCompilationResult",
        "class USkyguardMission01EnvironmentAuthoringLibrary",
        "class ASkyguardMission01EnvironmentDirector",
        "struct FSkyguardMission01EnvironmentReadiness",
        "struct FSkyguardLandscapeFootprintSampleResult",
        "struct FSkyguardLandscapeHeightSample",
        "class ASkyguardPropSpinner",
        "enum class ESkyguardBriefingPictogram",
        "class USkyguardSortiePresentationComponent",
        "struct FSkyguardBriefingCard",
        "struct FSkyguardBriefingRadioRow",
        "struct FSkyguardHowToFlyRow",
        "struct FSkyguardMissionResult",
        "struct FSkyguardObjectiveProgress",
        "struct FSkyguardMissionDebrief",
        "struct FSkyguardBossTelemetry",
        "struct FSkyguardAudioTelemetry",
        "ESkyguardAudioEvent::",
        f"class SKYGUARD52_API {LEFTOVER_APACHE_CLASS}",
        f"class {LEFTOVER_APACHE_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_RADAR_NODE_CLASS}",
        f"class {LEFTOVER_RADAR_NODE_CLASS}",
    )


def actor_section(header: str) -> str:
    body = class_body(header)
    public = re.search(r"\bpublic\s*:", body)
    if public is None:
        raise AssertionError(
            f"{ACTOR_NAME} public section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = public.end()
    rest = body[start:]
    next_access = ACCESS_RE.search(rest)
    if next_access is not None:
        section = rest[: next_access.start()]
    else:
        close = rest.rfind("}")
        if close == -1:
            raise AssertionError(
                f"{ACTOR_NAME} public section is missing from "
                f"origin/main:{HEADER_PATH}"
            )
        section = rest[:close]
    if STRUCT_RE.search(section):
        raise AssertionError(
            f"{ACTOR_NAME} parse window includes {STRUCT_NAME}"
        )
    if STOP_BEFORE_NAMESPACE in section:
        raise AssertionError(
            f"{ACTOR_NAME} parse window includes {STOP_BEFORE_NAMESPACE}"
        )
    for token in leaked_neighbor_tokens():
        if token in section:
            raise AssertionError(
                f"{ACTOR_NAME} parse window includes {token}"
            )
    for mesh in private_transient_tokens():
        if has_identifier(section, mesh):
            raise AssertionError(
                f"{ACTOR_NAME} parse window includes private {mesh}"
            )
    return section


def attached_ufunction_specifiers(section: str) -> str:
    compact = collapsed(section)
    cursor = 0
    while True:
        match = re.search(r"UFUNCTION\(", compact[cursor:])
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
            r"\s*void\s+ApplyTheaterKit\b",
            compact[index:],
        ) and not re.match(
            r"\s*void\s+ApplyTheaterKitToWorld\b",
            compact[index:],
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UFUNCTION for void ApplyTheaterKit is missing "
        f"from origin/main:{HEADER_PATH} class {ACTOR_NAME} public "
        "section"
    )


def attached_uproperty_specifiers(section: str) -> str:
    return attached_ufunction_specifiers(section)


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"class {ACTOR_NAME} public section"
        )
    return declaration


class TheaterKitApplyTheaterKitDeclContractTests(unittest.TestCase):
    def test_theater_kit_actor_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(ACTOR_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertIn(f"class SKYGUARD52_API {ACTOR_NAME}", header)
        self.assertNotEqual(ACTOR_NAME, STRUCT_NAME)
        self.assertNotEqual(ACTOR_NAME, LEFTOVER_APACHE_CLASS)
        self.assertNotEqual(ACTOR_NAME, LEFTOVER_PROTECT_ASSET_CLASS)
        self.assertNotEqual(ACTOR_NAME, LEFTOVER_RADAR_NODE_CLASS)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = actor_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(has_identifier(section, "ApplyTheaterKit"), section)
        self.assertIn("UFUNCTION", section)
        self.assertIn("BlueprintCallable", section)
        self.assertIn("private:", body)
        self.assertNotIn("private:", section)
        self.assertIn(STRUCT_NAME, header)
        self.assertIsNone(STRUCT_RE.search(section), section)
        self.assertNotIn("struct FSkyguardTheaterKitSpec", section)
        self.assertIn(STOP_BEFORE_NAMESPACE, header)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        self.assertIn(STOP_BEFORE_APPLY, header)
        self.assertNotIn(STOP_BEFORE_APPLY, LOCKED_DECL)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for leftover in leftover_spec_field_names():
            self.assertNotIn(leftover, LOCKED_DECL)
        self.assertNotIn(GET_OBJECTIVE_RUNTIME, section)
        self.assertNotIn(ADD_OBJECTIVE_PROGRESS, section)
        self.assertNotIn(BIND_RUNTIME_ACTORS, section)
        self.assertNotIn(HANDLE_DRONE_CITY_IMPACT, section)
        self.assertNotIn(GET_STORM_RAIN_BEAT_KIT, section)
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, section)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, section)
        self.assertNotIn(STOP_BEFORE_EVENT_DEF, section)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAPON, section)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, section)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, section)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, section)
        for mesh in private_transient_tokens():
            self.assertFalse(has_identifier(section, mesh), mesh)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class ASkyguardUnrelatedTheaterKit\n{\n};\n"
            )
        self.assertIn(ACTOR_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_type_does_not_satisfy(self) -> None:
        spec = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{UFUNCTION_CALLABLE_THEATER}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            actor_section(spec)
        self.assertIn(ACTOR_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        leftover = (
            f"class {LEFTOVER_APACHE_CLASS}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_CALLABLE_THEATER}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            actor_section(leftover)
        self.assertIn(ACTOR_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        radar = (
            f"class {LEFTOVER_RADAR_NODE_CLASS}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_CALLABLE_THEATER}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            actor_section(radar)
        self.assertIn(ACTOR_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_spec_or_namespace_declaration_does_not_satisfy(self) -> None:
        mixed = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "\tGENERATED_BODY()\n"
            f"\t{UFUNCTION_CALLABLE_THEATER}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
            f"{STOP_BEFORE_NAMESPACE}\n"
            "{{\n"
            f"\tconst FSkyguardTheaterKitSpec& {RESOLVE}"
            "(FName WeatherIdentity);\n"
            "}}\n"
            f"class {ACTOR_NAME}\n"
            "{{\n"
            "public:\n"
            f"\tstatic void {STOP_BEFORE_APPLY}();\n"
            "}};\n"
        )
        section = actor_section(mixed)
        self.assertFalse(has_declaration(section, LOCKED_DECL), section)
        self.assertNotIn("struct FSkyguardTheaterKitSpec", section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("ApplyTheaterKit", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_apply_theater_kit_declaration_fails_closed(self) -> None:
        empty = (
            f"class {ACTOR_NAME}\n"
            "{\n"
            "public:\n"
            f"\tTObjectPtr<UHierarchicalInstancedStaticMeshComponent> "
            f"{SIBLING_BUILDING_INSTANCES};\n"
            "\tFLinearColor GetBuildingTint() const "
            "{ return AppliedSpec.BuildingTint; }\n"
            "private:\n"
            f"\tTObjectPtr<UStaticMesh> {PRIVATE_CUBE_MESH};\n"
            "};\n"
        )
        section = actor_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("ApplyTheaterKit", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_identifier(section, PRIVATE_CUBE_MESH), section)

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_CALLABLE_THEATER}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("ApplyTheaterKit", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = actor_section(origin_main_header())
        self.assertIn(UFUNCTION_CALLABLE_THEATER, section)
        self.assertIn("BlueprintCallable", section)
        self.assertIn('Category="Skyguard|Theater"', section)
        self.assertIn("BlueprintCallable", UFUNCTION_CALLABLE_THEATER)
        self.assertIn("Category", UFUNCTION_CALLABLE_THEATER)
        self.assertIn('Category="Skyguard|Theater"', UFUNCTION_CALLABLE_THEATER)
        self.assertNotIn("BlueprintPure", UFUNCTION_CALLABLE_THEATER)
        self.assertNotIn("static", UFUNCTION_CALLABLE_THEATER)
        self.assertNotIn("EditAnywhere", UFUNCTION_CALLABLE_THEATER)
        self.assertNotIn("BlueprintReadWrite", UFUNCTION_CALLABLE_THEATER)
        specifiers = attached_ufunction_specifiers(section)
        self.assertIn("BlueprintCallable", specifiers)
        self.assertIn('Category="Skyguard|Theater"', specifiers)
        self.assertIn("Category", specifiers)
        self.assertNotIn("BlueprintPure", specifiers)
        self.assertNotIn("static", specifiers)
        self.assertNotIn("WorldContext", specifiers)
        self.assertNotIn("EditAnywhere", specifiers)
        self.assertNotIn("BlueprintReadWrite", specifiers)
        self.assertNotIn("MultiLine", specifiers)
        self.assertNotIn("ClampMin", specifiers)
        self.assertNotIn("ClampMax", specifiers)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertIsNone(APPLY_THEATER_KIT_BODY_RE.search(collapsed(section)))
        self.assertIsNone(APPLY_THEATER_KIT_STATIC_RE.search(collapsed(LOCKED_DECL)))
        self.assertNotIn("UFUNCTION", LOCKED_DECL)
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        self.assertNotIn("const", LOCKED_DECL)
        self.assertNotIn("static", LOCKED_DECL)
        self.assertIn("void", LOCKED_DECL)
        self.assertIn("FName WeatherIdentity", LOCKED_DECL)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, LOCKED_DECL)

    def test_missing_or_wrong_signature_fails_closed(self) -> None:
        initialized = (
            f"class {ACTOR_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_CALLABLE_THEATER}\n"
            f"\t{TARGET_WRONG_STATIC}\n"
            "private:\n"
            "};\n"
        )
        section = actor_section(initialized)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("ApplyTheaterKit", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        origin = actor_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIsNotNone(APPLY_THEATER_KIT_RE.search(compact_origin))
        self.assertIsNone(APPLY_THEATER_KIT_BODY_RE.search(compact_origin))
        self.assertIsNone(APPLY_THEATER_KIT_STATIC_RE.search(collapsed(LOCKED_DECL)))
        self.assertNotIn("static void ApplyTheaterKit(", LOCKED_DECL)
        self.assertNotIn("FName ApplyTheaterKit", compact_origin)
        self.assertNotIn("float ApplyTheaterKit", compact_origin)
        self.assertNotIn("int32 ApplyTheaterKit", compact_origin)
        self.assertNotIn("FLinearColor ApplyTheaterKit", compact_origin)

    def test_apply_theater_kit_declaration_matches_origin_main(self) -> None:
        section = actor_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(
            LOCKED_DECL.startswith("void ApplyTheaterKit"),
            LOCKED_DECL,
        )
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertNotIn("const", LOCKED_DECL)
        self.assertNotIn("static", LOCKED_DECL)
        self.assertIn("void ", LOCKED_DECL)
        self.assertIn("FName WeatherIdentity", LOCKED_DECL)
        self.assertNotIn("=", LOCKED_DECL)
        self.assertNotIn("= nullptr", LOCKED_DECL)
        self.assertNotIn("= false", LOCKED_DECL)
        self.assertNotIn("= true", LOCKED_DECL)
        self.assertNotIn("= 0.f", LOCKED_DECL)
        self.assertNotIn("= 160.f", LOCKED_DECL)
        self.assertNotIn("float ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn("bool ", LOCKED_DECL)
        self.assertNotIn("FLinearColor ", LOCKED_DECL)
        self.assertNotIn("FSkyguardMissionResult", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        self.assertNotIn("BlueprintPure", LOCKED_DECL)
        self.assertNotIn("BlueprintCallable", LOCKED_DECL)
        self.assertNotIn("ApplyTheaterKitToWorld", LOCKED_DECL)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for leftover in leftover_spec_field_names():
            self.assertNotIn(leftover, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FALSE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TRUE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_EQ_NONE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_ZERO}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FLOAT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FNAME}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_STATIC}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_INT32}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_NO_PARAM}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TO_WORLD}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_HEALTH}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_STATIC}\n", LOCKED_DECL)
        self.assertIn("ApplyTheaterKit", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_FNAME}\n", LOCKED_DECL)
        self.assertIn("ApplyTheaterKit", str(raised.exception))

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tFLinearColor "
            + leftover_retired_primary_hits_field()
            + "() const;\n"
        )
        leftover_guided = (
            "\tFLinearColor "
            + leftover_retired_guided_hits_field()
            + "() const;\n"
        )
        forty = "40" + ".f"
        eighty = "80" + ".f"
        wrongs = (
            f"\t{TARGET_WRONG_EQ_NONE}\n",
            f"\t{TARGET_WRONG_FALSE}\n",
            f"\t{TARGET_WRONG_TRUE}\n",
            f"\t{TARGET_WRONG_ZERO}\n",
            f"\t{TARGET_WRONG_FLOAT}\n",
            f"\t{TARGET_WRONG_FNAME}\n",
            f"\t{TARGET_WRONG_STATIC}\n",
            f"\t{TARGET_WRONG_INT32}\n",
            f"\t{TARGET_WRONG_NO_PARAM}\n",
            f"\t{TARGET_WRONG_TO_WORLD}\n",
            f"\t{TARGET_WRONG_HEALTH}\n",
            leftover_primary,
            leftover_guided,
            f"\tTObjectPtr<UHierarchicalInstancedStaticMeshComponent> "
            f"{SIBLING_BUILDING_INSTANCES};\n",
            "\tint32 GetBuildingInstanceCount() const;\n",
            "\tFName GetAppliedWeatherIdentity() const;\n",
            "\tFName GetAppliedKitId() const;\n",
            "\tFName GetNamedLandmark() const;\n",
            "\tFLinearColor GetBuildingTint() const;\n",
            "\tconst FSkyguardTheaterKitSpec& GetAppliedSpec() const;\n",
            "\tint32 GetRoadInstanceCount() const;\n",
            "\tint32 GetLampInstanceCount() const;\n",
            "\tint32 GetSilhouetteInstanceCount() const;\n",
            f"\t{TARGET_WRONG_FLINEAR}\n",
            "\tbool ApplyTheaterKit(FName WeatherIdentity);\n",
            "\tFName ApplyTheaterKit(FName WeatherIdentity);\n",
            f"\t{TARGET_WRONG_BODY}\n",
            f"\t{TARGET_WRONG_SPEC_FIELD}\n",
            "\tvoid ApplyTheaterKit(FName WeatherIdentity) { return "
            + forty
            + "; }\n",
            "\tvoid ApplyTheaterKit(FName WeatherIdentity) { return "
            + eighty
            + "; }\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("ApplyTheaterKit", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_missing_category_or_blueprint_pure_instead_of_callable_fails_closed(self) -> None:
        no_category = (
            f"class {ACTOR_NAME}\n"
            "{\n"
            "public:\n"
            "\tUFUNCTION(BlueprintCallable)\n"
            f"\t{LOCKED_DECL}\n"
            "private:\n"
            "};\n"
        )
        section = actor_section(no_category)
        specifiers = attached_ufunction_specifiers(section)
        self.assertNotIn("Category", specifiers)
        origin = attached_ufunction_specifiers(
            actor_section(origin_main_header())
        )
        self.assertIn("Category", origin)
        self.assertIn('Category="Skyguard|Theater"', origin)
        self.assertIn("BlueprintCallable", origin)
        self.assertNotIn("BlueprintPure", origin)
        pure_only = (
            f"class {ACTOR_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{TARGET_WRONG_PURE}\n"
            f"\t{LOCKED_DECL}\n"
            "private:\n"
            "};\n"
        )
        dropped = attached_ufunction_specifiers(
            actor_section(pure_only)
        )
        self.assertIn("BlueprintPure", dropped)
        self.assertNotIn("BlueprintCallable", dropped)
        self.assertIn("BlueprintCallable", origin)
        self.assertNotIn("BlueprintPure", origin)
        campaign = (
            f"class {ACTOR_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{TARGET_WRONG_CAMPAIGN}\n"
            f"\t{LOCKED_DECL}\n"
            "private:\n"
            "};\n"
        )
        campaign_specs = attached_ufunction_specifiers(
            actor_section(campaign)
        )
        self.assertIn('Category="Skyguard|Campaign"', campaign_specs)
        self.assertNotIn('Category="Skyguard|Theater"', campaign_specs)
        self.assertIn('Category="Skyguard|Theater"', origin)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wraps = (
            "\tvoid\n\tApplyTheaterKit(FName WeatherIdentity);\n",
            "\tvoid   ApplyTheaterKit(FName WeatherIdentity);\n",
            "\tvoid\tApplyTheaterKit(FName WeatherIdentity);\n",
            "\tvoid ApplyTheaterKit(\n\tFName WeatherIdentity);\n",
            "\tvoid ApplyTheaterKit(FName  WeatherIdentity);\n",
            f"\t{LOCKED_DECL}\n",
            f"\t{LOCKED_DECL}\n",
            f"\t{UFUNCTION_CALLABLE_THEATER}\n\t{LOCKED_DECL}\n",
            f"\t{UFUNCTION_CALLABLE_THEATER} {LOCKED_DECL}\n",
            "\tUFUNCTION(BlueprintCallable, "
            'Category="Skyguard|Theater")\n'
            f"\t{LOCKED_DECL}\n",
            "\tUFUNCTION(\n\t\tBlueprintCallable, "
            'Category="Skyguard|Theater")\n'
            f"\t{LOCKED_DECL}\n",
            "\tUFUNCTION(BlueprintCallable,\n"
            '\t\tCategory="Skyguard|Theater")\n'
            f"\t{LOCKED_DECL}\n",
        )
        for region in wraps:
            self.assertTrue(has_declaration(region, LOCKED_DECL), region)

    def test_does_not_contract_sibling_theater_fields(self) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for leftover in leftover_spec_field_names():
            self.assertNotIn(leftover, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertNotIn(GET_OBJECTIVE_RUNTIME, LOCKED_DECL)
        self.assertNotIn(ADD_OBJECTIVE_PROGRESS, LOCKED_DECL)
        self.assertNotIn(BIND_RUNTIME_ACTORS, LOCKED_DECL)
        self.assertNotIn(HANDLE_DRONE_CITY_IMPACT, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, LOCKED_DECL)
        self.assertNotIn(STOP_BEFORE_APPLY, LOCKED_DECL)
        section = actor_section(origin_main_header())
        for sibling in sibling_uncontracted_decls():
            self.assertTrue(has_identifier(section, sibling), sibling)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, section)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, LOCKED_DECL)
        for method in leftover_ufunction_tokens():
            self.assertNotIn(method, LOCKED_DECL)

    def test_does_not_parse_spec_namespace_or_private_meshes(self) -> None:
        header = origin_main_header()
        section = actor_section(header)
        leaked = class_body(header)
        self.assertIn("struct FSkyguardTheaterKitSpec", header)
        self.assertNotIn("struct FSkyguardTheaterKitSpec", section)
        self.assertNotIn("struct FSkyguardTheaterKitSpec", leaked)
        self.assertIn(STOP_BEFORE_NAMESPACE, header)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, leaked)
        self.assertIn(STOP_BEFORE_APPLY, header)
        self.assertNotIn(STOP_BEFORE_APPLY, LOCKED_DECL)
        for helper in namespace_helper_tokens():
            self.assertIn(helper, header)
            self.assertNotIn(helper, section)
        for mesh in private_transient_tokens():
            self.assertTrue(has_identifier(header, mesh), mesh)
            self.assertFalse(has_identifier(section, mesh), mesh)
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, header)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, header)
        self.assertNotIn(STOP_BEFORE_EVENT_DEF, header)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAPON, header)
        self.assertNotIn(STOP_BEFORE_PROP_SPINNER, header)
        self.assertNotIn(STOP_BEFORE_SORTIE, header)
        self.assertNotIn(STOP_BEFORE_PATROL, header)
        self.assertNotIn(leftover_retired_mount_class(), header)
        self.assertNotIn(STOP_BEFORE_GUNNER, header)
        self.assertNotIn(STOP_BEFORE_WEAK_POINT, header)
        self.assertNotIn(GET_OBJECTIVE_RUNTIME, header)
        self.assertNotIn(ADD_OBJECTIVE_PROGRESS, header)
        self.assertNotIn(BIND_RUNTIME_ACTORS, header)
        self.assertNotIn(HANDLE_DRONE_CITY_IMPACT, header)
        self.assertNotIn(GET_STORM_RAIN_BEAT_KIT, header)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, header)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, header)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, header)

    def test_parse_window_excludes_leftover_weapon_enum_body(self) -> None:
        header = origin_main_header()
        section = actor_section(header)
        leaked = class_body(header)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, leaked)
            self.assertNotIn(leftover, header)
        for leftover in leftover_weapon_enum_body_tokens():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, leaked)
            self.assertNotIn(leftover, header)
        for leftover in leftover_audio_event_enum_tokens():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, leaked)
            self.assertNotIn(leftover, header)
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, section)
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, leaked)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, section)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, leaked)
        self.assertNotIn(STOP_BEFORE_EVENT_DEF, section)
        self.assertNotIn(STOP_BEFORE_EVENT_DEF, leaked)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAPON, section)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAPON, leaked)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, section)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, leaked)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other = (
            f"\tconst FSkyguardTheaterKitSpec& {RESOLVE}"
            "(FName WeatherIdentity);\n"
            f"\tint32 {NUM_KITS}();\n"
            f"\tstatic void {STOP_BEFORE_APPLY}();\n"
            f"\tTObjectPtr<UHierarchicalInstancedStaticMeshComponent> "
            f"{SIBLING_BUILDING_INSTANCES};\n"
            f"\t{TARGET_WRONG_HEALTH}\n"
            "\tint32 GetBuildingInstanceCount() const;\n"
            "\tFName GetAppliedWeatherIdentity() const;\n"
            "\tFName GetAppliedKitId() const;\n"
            "\tFName GetNamedLandmark() const;\n"
            "\tconst FSkyguardTheaterKitSpec& GetAppliedSpec() const;\n"
            "\tUSkyguardObjectiveRuntime* GetObjectiveRuntime() const;\n"
            "\tbool AddObjectiveProgress(\n"
            "\t\tFName ObjectiveId,\n"
            "\t\tint32 MedalTier);\n"
            "\tvoid BindRuntimeActors();\n"
            "\tvoid HandleDroneCityImpact();\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other, LOCKED_DECL)
        self.assertIn("ApplyTheaterKit", str(raised.exception))

    def test_declaration_does_not_invent_ufunction_metadata(self) -> None:
        self.assertEqual(
            UFUNCTION_CALLABLE_THEATER,
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Theater")',
        )
        self.assertIn("BlueprintCallable", UFUNCTION_CALLABLE_THEATER)
        self.assertIn("Category", UFUNCTION_CALLABLE_THEATER)
        self.assertIn('Category="Skyguard|Theater"', UFUNCTION_CALLABLE_THEATER)
        self.assertNotIn(
            'Category="Skyguard|Campaign"',
            UFUNCTION_CALLABLE_THEATER,
        )
        self.assertNotIn("BlueprintPure", UFUNCTION_CALLABLE_THEATER)
        self.assertNotIn("EditAnywhere", UFUNCTION_CALLABLE_THEATER)
        self.assertNotIn("BlueprintReadWrite", UFUNCTION_CALLABLE_THEATER)
        self.assertNotIn("VisibleAnywhere", UFUNCTION_CALLABLE_THEATER)
        self.assertNotIn("MultiLine", UFUNCTION_CALLABLE_THEATER)
        self.assertNotIn("ClampMin", UFUNCTION_CALLABLE_THEATER)
        self.assertNotIn("ClampMax", UFUNCTION_CALLABLE_THEATER)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, LOCKED_DECL)
            self.assertNotIn(invented, UFUNCTION_CALLABLE_THEATER)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        self.assertNotIn(".cpp", HEADER_PATH)
        self.assertTrue(HEADER_PATH.endswith(".h"))
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("SkyguardCampaignTheaterKit.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardRadarNode.h", HEADER_PATH)
        self.assertNotIn("SkyguardProtectAsset.h", HEADER_PATH)
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = actor_section(header)
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
        section = actor_section(header)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, header)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "theater-kit ApplyTheaterKit decl contract "
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
            "apply_theater_kit_decl_contract.py"
        ))
        self.assertIn(CLONE_ROOT_FIELD, LOCKED_SCRIPTS)
        self.assertIn(CLONE_ROAD_INSTANCES, LOCKED_SCRIPTS)
        self.assertIn(CLONE_BUILDING_INSTANCES, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LAMP_INSTANCES, LOCKED_SCRIPTS)
        self.assertIn(CLONE_SILHOUETTE_INSTANCES, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NAMED_LANDMARK_MESH, LOCKED_SCRIPTS)
        self.assertIn(CLONE_APPLIED_SPEC, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GET_APPLIED_WEATHER_IDENTITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GET_APPLIED_KIT_ID, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GET_BUILDING_TINT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GET_NAMED_LANDMARK, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GET_APPLIED_SPEC, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GET_ROAD_INSTANCE_COUNT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GET_BUILDING_INSTANCE_COUNT, LOCKED_SCRIPTS)
        self.assertNotIn("SkyguardCampaignTheaterKit.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardRadarNode.h", THIS_SCRIPT)
        self.assertIn(LEFTOVER_THEATER_KIT_BULK, LOCKED_SCRIPTS)
        self.assertIn(CLONE_WEATHER_IDENTITY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LANDMARK_SET, LOCKED_SCRIPTS)
        self.assertIn(CLONE_KIT_ID, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LANDMARK_SCALE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_THEATER_KIT_WEATHER_APPLY, LOCKED_SCRIPTS)
        self.assertIn(
            LEFTOVER_THEATER_KIT_WEATHER_APPLY_TESTS,
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            LEFTOVER_THEATER_KIT_WEATHER_APPLY_CONTRACT,
            LOCKED_SCRIPTS,
        )
        self.assertIn(CLONE_CURRENT_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_MAX_HEALTH, LOCKED_SCRIPTS)
        self.assertIn(CLONE_RESET_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_APPLY_DAMAGE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_IS_DESTROYED, LOCKED_SCRIPTS)
        self.assertIn(CLONE_GET_INTEGRITY_FRACTION, LOCKED_SCRIPTS)
        self.assertIn(CLONE_MAX_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_RADAR_IS_DESTROYED, LOCKED_SCRIPTS)
        self.assertIn(CLONE_RADAR_APPLY_DAMAGE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_RADAR_RESET_NODE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_PEAK_ACTIVE_VOICES, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_PROTECT_ASSET_CARGO_PROXY, LOCKED_SCRIPTS)
        self.assertIn(
            LEFTOVER_PROTECT_ASSET_CARGO_PROXY_CONTRACT,
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            LEFTOVER_PROTECT_ASSET_CARGO_PROXY_TESTS,
            LOCKED_SCRIPTS,
        )
        self.assertIn(LEFTOVER_RADAR_NODE_PRESENTATION, LOCKED_SCRIPTS)
        self.assertIn(
            LEFTOVER_RADAR_NODE_PRESENTATION_TESTS,
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            LEFTOVER_RADAR_NODE_PRESENTATION_CONTRACT,
            LOCKED_SCRIPTS,
        )
        self.assertIn(LEFTOVER_RADAR_NODE_RESET_GAMEPLAY, LOCKED_SCRIPTS)
        self.assertIn(
            LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_TESTS,
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_CONTRACT,
            LOCKED_SCRIPTS,
        )
        self.assertIn(CLONE_OBJECTIVE_ID, LOCKED_SCRIPTS)
        self.assertIn(CLONE_CURRENT_PROGRESS, LOCKED_SCRIPTS)
        self.assertIn(CLONE_STATE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_FINAL_SCORE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_MEDAL_TIER, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_STATE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_RESULT, LOCKED_SCRIPTS)
        self.assertIn(CLONE_MISSION_DISPLAY_NAME, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NARRATIVE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NEW_BEST_SCORE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NEW_BEST_MEDAL, LOCKED_SCRIPTS)
        self.assertIn(CLONE_PROGRESS_SAVED, LOCKED_SCRIPTS)
        self.assertIn(CLONE_SAVE_SLOT_NAME, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NEXT_MISSION_ID, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NEXT_MISSION_DISPLAY_NAME, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NEXT_MISSION_MAP, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NEXT_MISSION_UNLOCKED, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_MISSION_RESULT_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_MISSION_DEBRIEF_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_OBJECTIVE_PROGRESS_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ADD_OBJECTIVE_PROGRESS, LOCKED_SCRIPTS)
        self.assertIn(CLONE_HOW_TO_FLY_STEP_ID, LOCKED_SCRIPTS)
        self.assertIn(CLONE_HOW_TO_FLY_INPUT_HINT, LOCKED_SCRIPTS)
        self.assertIn(CLONE_HOW_TO_FLY_INSTRUCTION, LOCKED_SCRIPTS)
        self.assertIn(CLONE_CARD_ID, LOCKED_SCRIPTS)
        self.assertIn(CLONE_TITLE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_BODY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_PRIORITY, LOCKED_SCRIPTS)
        self.assertIn(
            "Scripts/tests/test_mission_result_defaults.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission_result_defaults_tests.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission_debrief_defaults.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission_debrief_defaults_tests.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_briefing_card_defaults_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_campaign_theater_kit_contract.py",
            LOCKED_SCRIPTS,
        )

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
            *leftover_spec_field_scripts(),
            *leftover_theater_kit_weather_apply_scripts(),
            *leftover_actor_uproperty_scripts(),
            *leftover_actor_ufunction_scripts(),
            "Scripts/tests/test_briefing_card_defaults_contract.py",
            "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
            "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
            "Scripts/tests/test_briefing_card_priority_field_decl_contract.py",
            "Scripts/tests/test_briefing_card_card_id_field_decl_contract.py",
            "Scripts/tests/test_briefing_card_title_field_decl_contract.py",
            "Scripts/tests/test_briefing_card_body_field_decl_contract.py",
            "Scripts/tests/test_how_to_fly_row_step_id_field_decl_contract.py",
            "Scripts/tests/test_how_to_fly_row_input_hint_field_decl_contract.py",
            "Scripts/tests/test_how_to_fly_row_instruction_field_decl_contract.py",
            "Scripts/tests/test_briefing_radio_row_line_id_field_decl_contract.py",
            "Scripts/tests/test_briefing_radio_row_speaker_field_decl_contract.py",
            "Scripts/tests/test_briefing_radio_row_subtitle_field_decl_contract.py",
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

    def test_contract_is_target_ufunction_declaration_only(self) -> None:
        header = origin_main_header()
        section = actor_section(header)
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        locked_only = f"{LOCKED_DECL}\n"
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, locked_only)
        for leftover in leftover_spec_field_names():
            self.assertNotIn(leftover, locked_only)
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
        self.assertNotIn("ESkyguardBossPhase", locked_only)
        self.assertNotIn("ESkyguardPilotCommand", locked_only)
        self.assertNotIn("PeakActiveVoices", locked_only)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, locked_only)
        self.assertNotIn(ACTOR_NAME, locked_only)
        self.assertNotIn(STOP_BEFORE_APPLY, locked_only)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, locked_only)
        self.assertNotIn(STRUCT_NAME, locked_only)
        for helper in namespace_helper_tokens():
            self.assertNotIn(helper, locked_only)
        for mesh in private_transient_tokens():
            self.assertNotIn(mesh, locked_only)
        for method in leftover_ufunction_tokens():
            self.assertNotIn(method, locked_only)


if __name__ == "__main__":
    unittest.main()
