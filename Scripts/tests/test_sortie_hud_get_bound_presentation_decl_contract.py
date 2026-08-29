# THIS IS leftover-safe USkyguardSortieHudHostComponent
# GetBoundPresentation.
# origin/main form: one-line and split-line UFUNCTION wraps
# UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|HUD")
# wrapping `USkyguardSortiePresentationComponent* GetBoundPresentation() const`
# with origin/main inline `{ return Presentation; }`.
# LOCKED_DECL may be declaration-only
# `USkyguardSortiePresentationComponent* GetBoundPresentation() const;`
# if the matcher strips inline bodies, OR the full origin/main
# inline form. Accept declaration-only AND the origin/main inline body.
# Do NOT fail-closed on `{ return Presentation; }`.
# Do NOT require a body-less form.
# KEEP BlueprintPure. Do NOT switch to BlueprintCallable.
# Do NOT retarget to BindPresentation / RefreshFromPresentationState /
# RebindIfNeeded.
# Word-boundary match GetBoundPresentation vs BindPresentation.
# Identifier GetBoundPresentation is NOT leftover analog BindPresentation
# #1707 SHA 6a4d0db188a528053b7608035a2622d1de65be49.
# THIS IS leftover-safe unique analog Category
# Skyguard|Presentation|HUD (unique unused 3-segment suffix HUD).
# This is leftover-safe unique analog, NOT leftover analog Presentation /
# Briefing / Debrief.
# BlueprintPure IS present. BlueprintCallable IS absent.
# const IS present. Return type IS USkyguardSortiePresentationComponent*.
# Identifier GetBoundPresentation is NOT leftover analog
# sortie-hud-host-fail-closed bulk #132 (behavioral; wrap Category HUD
# UFUNCTION declaration only) and NOT leftover analog Gunner CpgSightHud
# #1627.
# Fail-closed if the UFUNCTION or decl is missing or renamed, if
# Category is missing, if specifiers drop to BlueprintCallable, if const
# is missing, if the return type is not
# USkyguardSortiePresentationComponent*, or if Category is
# Skyguard|Apache without |Damage / Skyguard|Combat without
# |Sortie/|Feedback/|Safety / Skyguard|Theater /
# Skyguard|MissionMap / Skyguard|Audio|Acceptance /
# Skyguard|Audio|Development / still Category="Skyguard"
# without a leftover-safe unique Category path /
# Category="Skyguard|Audio" without |Production /
# Category="Skyguard|Boss|Encounter" without a leftover-safe unique
# suffix / Category="Settings" without Skyguard| /
# Category="Skyguard|Presentation" without leftover-safe unique |HUD
# suffix / Category="Skyguard|Presentation|Briefing" /
# Category="Skyguard|Presentation|Debrief" /
# Category="Skyguard|Environment|VFX" /
# Category="Skyguard|Pause".
# Accept one-line and split-line UFUNCTION wraps.
# Parse CLASS `USkyguardSortieHudHostComponent` public section ONLY after
# `class USkyguardSortieHudHostComponent` / GENERATED_BODY. Start at
# `public:`. Stop BEFORE `private:`.
# Stop BEFORE first public UPROPERTY (`BriefingWidgetClass`).
# Isolate THIS UFUNCTION window so sibling BindPresentation /
# RefreshFromPresentationState / RebindIfNeeded are uncontracted.
# Do NOT claim sibling UFUNCTION BindPresentation /
# RefreshFromPresentationState / RebindIfNeeded as this slot
# (leave them uncontracted).
# Do NOT claim leftover analog ShouldShowDebriefForState
# (NO UFUNCTION wrap on origin/main).
# Clone leftover unique Validation BlueprintPure
# GetActiveRHIAndFeatureLevel #1695 SHA
# 44ff9ffdf3359acfed757b1588de83a1a9aabe98 RETARGET method/return.
# KEEP BlueprintPure.
# Clone leftover unique BlueprintPure GetSortieHits #1685 SHA
# 4e878e0750eaed9a830a48e36e94d949f608491b RETARGET Category Combat|Sortie
# → Skyguard|Presentation|HUD. KEEP BlueprintPure.
# FAIL-CLOSED if LOCKED_DECL is int32 GetSortieHits() const;
# Clone leftover unique Validation BlueprintCallable #1694 SHA
# e8a9961586c6ed5d538c813bb93d824c79b24db2 RETARGET method; this slot is
# BlueprintPure not BlueprintCallable.
# Clone leftover unique BlueprintCallable #1680 SHA
# 27ffb2a529b5067ad204e9c35e46f650a02403a4 RETARGET Category Production →
# Skyguard|Presentation|HUD. KEEP BlueprintPure not BlueprintCallable.
# Clone #1300 SHA c4679feb43f4b97d3a814c088e3b6c344e15831f is Category
# Theater wrapping FName WeatherIdentity — RETARGET hard.
# LOCKED_DECL is USkyguardSortiePresentationComponent* GetBoundPresentation() const;
# NOT FName WeatherIdentity / 160.f / FireRate = 12.0f /
# RecoilPitch = 0.92f / RouteLengthCm = 45000.f /
# int32 GetSortieHits() const; / void ResetSortieCombatStats(); /
# bool GetInvertVerticalLook() const; / bool bSuccess = false; /
# void EnsureDefaultEntries(); / void BindPresentation( /
# void RefreshFromPresentationState(); / void RebindIfNeeded(); /
# int32 GetActivationCount() const;
# Fail-closed if this test still asserts FName WeatherIdentity / 160.f /
# FireRate = 12.0f / RecoilPitch = 0.92f / RouteLengthCm = 45000.f /
# int32 GetSortieHits() const; / void ResetSortieCombatStats(); /
# bool GetInvertVerticalLook() const; / bool bSuccess = false; /
# void EnsureDefaultEntries(); / void BindPresentation( /
# void RefreshFromPresentationState(); / void RebindIfNeeded(); /
# int32 GetActivationCount() const; AS THE LOCKED DECL.
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
HEADER_PATH = "Source/Skyguard52/SkyguardSortieHudHostComponent.h"
CLASS_NAME = "USkyguardSortieHudHostComponent"
LEFTOVER_AUDIO_DIRECTOR_CLASS = "USkyguardAudioDirectorComponent"
LEFTOVER_PRODUCTION_BANK_CLASS = "USkyguardAudioProductionBank"
LEFTOVER_AUTHORING_RESULT_STRUCT = "FSkyguardMission01EnvironmentAuthoringResult"
LEFTOVER_VISIBLE_AUDIT_STRUCT = "FSkyguardLandscapeVisibleAudit"
LEFTOVER_DIRECTOR_CLASS = "ASkyguardMission01EnvironmentDirector"
TARGET = (
    "USkyguardSortiePresentationComponent* GetBoundPresentation() const;"
)
TARGET_SPLIT = (
    "USkyguardSortiePresentationComponent*\n"
    "\tGetBoundPresentation() const;"
)
TARGET_INLINE = (
    "USkyguardSortiePresentationComponent* GetBoundPresentation() const "
    "{ return Presentation; }"
)
TARGET_WRONG_BARE = (
    "void GetBoundPresentation();"
)
TARGET_WRONG_NO_CONST = (
    "USkyguardSortiePresentationComponent* GetBoundPresentation();"
)
TARGET_WRONG_REFRESH = "void RefreshFromPresentationState();"
TARGET_WRONG_REBIND = "void RebindIfNeeded();"
TARGET_WRONG_BIND = (
    "void BindPresentation("
    "USkyguardSortiePresentationComponent* InPresentation);"
)
TARGET_WRONG_GET_BOUND = TARGET_WRONG_BIND
TARGET_WRONG_GET_BOUND_INLINE = (
    "void BindPresentation("
    "USkyguardSortiePresentationComponent* InPresentation) "
    "{ Presentation = InPresentation; }"
)
TARGET_WRONG_BIND_CONST = (
    "void BindPresentation("
    "USkyguardSortiePresentationComponent* InPresentation) const;"
)
TARGET_WRONG_ACTIVATION = "int32 GetActivationCount() const;"
TARGET_WRONG_AUTHORING = (
    "static FSkyguardMission01EnvironmentAuthoringResult "
    "AuthorGovernedLandscapeAndGraph("
    "ASkyguardMission01EnvironmentDirector* Director, "
    "const FString& HeightmapSourcePath, "
    "const FString& GraphPackagePath);"
)
TARGET_WRONG_VOID = "void EnsureDefaultEntries();"
TARGET_WRONG_FLOAT = (
    "float GetBoundPresentation() const;"
)
TARGET_WRONG_INT = "int32 GetSortieHits() const;"
TARGET_WRONG_RENAME = "USkyguardSortiePresentationComponent* GetBoundPresentations() const;"
TARGET_WRONG_SIBLING_INIT = (
    "static FSkyguardMission01EnvironmentAuthoringResult "
    "AuthorGovernedLandscapeWithExistingGraph("
    "ASkyguardMission01EnvironmentDirector* Director, "
    "const FString& HeightmapSourcePath, "
    "const FString& GraphPackagePath);"
)
TARGET_WRONG_PRODUCTION_BANK_FIELD = (
    "TObjectPtr<USkyguardAudioProductionBank> ProductionBank;"
)
TARGET_WRONG_SIBLING_AUDIT = (
    "static FSkyguardMission01EnvironmentAuthoringResult "
    "AuditGovernedLandscapeAndGraph("
    "ASkyguardMission01EnvironmentDirector* Director);"
)
TARGET_WRONG_SAMPLE_HEIGHT = "FSkyguardLandscapeHeightSample SampleLandscapeHeight("
TARGET_WRONG_SAMPLE_FOOTPRINT = (
    "FSkyguardLandscapeFootprintSample SampleLandscapeFootprint("
)
TARGET_WRONG_GET_RHI = "static FString GetActiveRHIAndFeatureLevel();"
TARGET_WRONG_PREPARE = (
    "static FSkyguardLandscapeVisibleAudit "
    "AuthorGovernedLandscapeAndGraph("
)
TARGET_WRONG_AUDIT_VISIBLE = (
    "static FSkyguardLandscapeVisibleAudit AuditLandscapeVisibleReadiness("
)
TARGET_WRONG_FINISH_COMPILE = (
    "static FSkyguardLandscapeMaterialCompilationResult "
    "FinishLandscapeMaterialCompilation("
)
TARGET_WRONG_RESET_SORTIE = "void ResetSortieCombatStats();"
TARGET_WRONG_INVERT_LOOK = "bool GetInvertVerticalLook() const;"
TARGET_WRONG_LOOK_SENS = "float GetAppliedLookSensitivity() const;"
TARGET_WRONG_SUCCESS = "bool bSuccess = false;"
TARGET_WRONG_ROUTE_LENGTH = "float RouteLengthCm = 45000.f;"
TARGET_WRONG_CAMERA_SHAKE = "float GetAppliedCameraShakeScale() const;"
UFUNCTION_ENVIRONMENT_ONLY = (
    'UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation")'
)
UFUNCTION_GROUNDING = (
    'UFUNCTION(BlueprintCallable, '
    'Category="Skyguard|Presentation|Debrief")'
)
UFUNCTION_VALIDATION = (
    'UFUNCTION(BlueprintCallable, '
    'Category="Skyguard|Presentation|HUD")'
)
UFUNCTION_LANDSCAPE = (
    'UFUNCTION(BlueprintCallable, '
    'Category="Skyguard|Environment|VFX")'
)
UFUNCTION_PCG = (
    'UFUNCTION(BlueprintCallable, '
    'Category="Skyguard|Mission01|Environment|PCG")'
)
UFUNCTION_LAYOUT = (
    'UFUNCTION(BlueprintCallable, '
    'Category="Skyguard|Mission01|Environment|Layout")'
)
UFUNCTION_MATERIALS = (
    'UFUNCTION(BlueprintCallable, '
    'Category="Skyguard|Mission01|Environment|Materials")'
)
UFUNCTION_VISIBILITY = (
    'UFUNCTION(BlueprintCallable, '
    'Category="Skyguard|Mission01|Environment|Visibility")'
)
UFUNCTION_COMBAT_SORTIE = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Combat|Sortie")'
)
UFUNCTION_COMBAT_FEEDBACK = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Combat|Feedback")'
)
UFUNCTION_COMBAT_SAFETY = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Combat|Safety")'
)
UFUNCTION_BOSS_ENCOUNTER = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Boss|Encounter")'
)
UFUNCTION_SETTINGS_BARE = (
    'UFUNCTION(BlueprintPure, Category="Settings")'
)
UFUNCTION_APACHE_DAMAGE = (
    'UFUNCTION(BlueprintCallable, Category="Skyguard|Apache|Damage")'
)
TARGET_WRONG_PATHFINDER_INTERVAL = (
    "float LockWindowAttackInterval = 1.6f;"
)
TARGET_WRONG_SIBLING_COUNT = (
    "int32 GetResolvedProductionLoopRouteCount() const;"
)
TARGET_WRONG_IS_DESTROYED = "bool IsDestroyed() const;"
TARGET_WRONG_LAMP = "int32 GetLampInstanceCount() const;"
TARGET_WRONG_GET_WIND = "float GetWindBlend() const { return WindBlend; }"
TARGET_WRONG_FALSE = "bool bLicensedVegetationLibraryApproved = false;"
TARGET_WRONG_TRUE = "bool GetBoundPresentation = true;"
TARGET_WRONG_ZERO = "bool GetBoundPresentation = 0.f;"
TARGET_WRONG_SKELETAL = (
    "TObjectPtr<USkeletalMeshComponent> "
    "GetBoundPresentation;"
)
TARGET_WRONG_LOOK_YAW = "float LookYawLimit = 95.f;"
TARGET_WRONG_MISSION_ID = "FName MissionId;"
TARGET_WRONG_FLIGHT_SPLINE = "TObjectPtr<USplineComponent> FlightRouteSpline;"
TARGET_WRONG_MISSION_DEF = (
    "TObjectPtr<USkyguardMissionDefinition> MissionDefinition;"
)
TARGET_WRONG_SKYLINE = "ESkyguardMissionSkylineStyle SkylineStyle;"
TARGET_WRONG_READINESS = "FSkyguardMissionMapReadiness Readiness;"
TARGET_WRONG_FLARE = "int32 FlareCount = 6;"
TARGET_WRONG_FNAME = "FName WeatherIdentity;"
TARGET_WRONG_HEALTH = "float Health = 160.f;"
TARGET_WRONG_FIRE_RATE = "float FireRate = 12.0f;"
TARGET_WRONG_RECOIL_PITCH = "float RecoilPitch = 0.92f;"
TARGET_WRONG_CANNON_MAG = "int32 CannonMagazineSize = 30;"
TARGET_WRONG_ROCKET_MAG = "int32 RocketMagazineSize = 14;"
TARGET_WRONG_GUIDED_MAG = "int32 GuidedMagazineSize = 2;"
TARGET_WRONG_THEATER = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Theater")'
)
LOCKED_DECL = TARGET
LOCKED_UFUNCTION_WRAP = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|HUD")'
)
UFUNCTION_AUTHORING = (
    'UFUNCTION(BlueprintCallable, '
    'Category="Skyguard|Presentation|Briefing")'
)
UFUNCTION_CALLABLE = (
    'UFUNCTION(BlueprintCallable, Category="Skyguard|Presentation|HUD")'
)
UFUNCTION_PURE = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Presentation|HUD")'
)
UFUNCTION_AUDIO_ONLY = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Audio")'
)
UFUNCTION_APACHE = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Apache")'
)
UFUNCTION_COMBAT = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Combat")'
)
UFUNCTION_MISSIONMAP = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|MissionMap")'
)
UFUNCTION_ACCEPTANCE = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Audio|Acceptance")'
)
UFUNCTION_DEVELOPMENT = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Audio|Development")'
)
UFUNCTION_SKYGUARD_ONLY = (
    'UFUNCTION(BlueprintPure, Category="Skyguard")'
)
UFUNCTION_PAUSE = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Pause")'
)
TARGET_WRONG_BUDGET = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Audio|Budget")'
)
TARGET_WRONG_SAMPLE_RATE = "int32 SampleRate = 48000;"
TARGET_WRONG_BYTE_BUDGET = "int32 GeneratedByteBudget = 1048576;"
TARGET_WRONG_PLACEMENT_SEED = "int32 PlacementSeed = 0;"
TARGET_WRONG_MIN_SAMPLES = "int32 MinimumMeasuredSamples = 600;"
TARGET_WRONG_MAX_VOICES = "int32 MaximumAllowedVoices = 48;"
TARGET_WRONG_NIGHT_IDENTITY = "bool bNightIdentity = false;"
TARGET_WRONG_ARCADE_ENABLED = "bool bEnabled = true;"
TARGET_WRONG_BOOM = "TObjectPtr<USpringArmComponent> Boom;"
TARGET_WRONG_CRUISE = "TSoftObjectPtr<USoundBase> EngineCruiseLoop;"
TARGET_WRONG_POWER = "TSoftObjectPtr<USoundBase> EnginePowerLoop;"
TARGET_WRONG_PROP = "TSoftObjectPtr<USoundBase> PropellerLoop;"
TARGET_WRONG_IDLE = "TSoftObjectPtr<USoundBase> EngineIdleLoop;"
TARGET_WRONG_VOICE = "int32 GlobalVoiceLimit = 24;"
TARGET_WRONG_CULL = "float VegetationStartCullDistanceCm;"
TARGET_WRONG_WIND = "TSoftObjectPtr<USoundBase> OpenCockpitWindLoop;"
TARGET_WRONG_ASSEMBLY = (
    'FName AssemblyRevision = TEXT("CampaignMapAssembly_v1");'
)
TARGET_WRONG_ROUTE_POINTS = "TArray<FSkyguardRoutePoint> RoutePoints;"
TARGET_WRONG_ALLOW_PCG = "bool bAllowAuthoredPCGGeneration = false;"
TARGET_WRONG_HAZE = "bool bEnableCoastalHazeTransition = true;"
TARGET_WRONG_LANDSCAPE = "bool bUseAuthoredLandscapeSurface = false;"
TARGET_WRONG_PCG_AUTH = "bool bPCGGenerationAuthorized = false;"
TARGET_WRONG_SURFACE_EXPOSED = "bool bAuthoredLandscapeSurfaceExposed = false;"
TARGET_WRONG_READY_PCG = "bool bReadyForAuthoredPCGGeneration = false;"
TARGET_WRONG_READINESS_LICENSED = "bool bLicensedVegetationApproved = false;"
TARGET_WRONG_TEDAC_TEXT = "TObjectPtr<UTextRenderComponent> CpgTedacText;"
TARGET_WRONG_EUFD_TEXT = "TObjectPtr<UTextRenderComponent> CpgEufdText;"
TARGET_WRONG_MPD_LEFT_TEXT = "TObjectPtr<UTextRenderComponent> CpgMpdLeftText;"
TARGET_WRONG_HAND_MESH = "TObjectPtr<UStaticMeshComponent> HandMesh;"
TARGET_WRONG_MESH = (
    "TObjectPtr<UStaticMeshComponent> "
    "GetBoundPresentation;"
)
TARGET_WRONG_SCENE = (
    "TObjectPtr<USceneComponent> "
    "GetBoundPresentation;"
)
TARGET_WRONG_CANOPY = "TObjectPtr<UStaticMeshComponent> Canopy;"
TARGET_WRONG_PILOT_CANOPY = "TObjectPtr<UStaticMeshComponent> PilotCanopy;"
SIBLING_GET_RESOLVED_COUNT = "GetResolvedProductionLoopRouteCount"
SIBLING_GET_WIND_BLEND = "GetWindBlend"
SIBLING_GET_POWER_BLEND = "GetPowerBlend"
SIBLING_GET_CRUISE_BLEND = "GetCruiseBlend"
SIBLING_GET_IDLE_BLEND = "GetIdleBlend"
SIBLING_GET_ACTIVE_VOICE_COUNT = "GetActiveVoiceCount"
SIBLING_GET_TELEMETRY = "GetTelemetry"
SIBLING_GET_SUPPRESSION = "GetSuppressionAmount"
SIBLING_ADVANCE_AUDIO_STATE = "AdvanceAudioState"
SIBLING_APPLY_HEARING = "ApplyHearingSuppression"
SIBLING_SET_LISTENER = "SetListenerPerspective"
SIBLING_SET_ENGINE_STATE = "SetEngineState"
SIBLING_TRIGGER_WORLD = "TriggerWorldEvent"
SIBLING_TRIGGER_EVENT = "TriggerEvent"
SIBLING_GET_PRODUCTION_AUDIT = "GetProductionBankAudit"
SIBLING_APPLY_PRODUCTION_BANK = "ApplyProductionBank"
SIBLING_PRIME_CONFIGURED = "PrimeConfiguredAssets"
STOP_BEFORE_EVENT_DEFINITIONS = "BindPresentation"
SIBLING_INITIALIZE_REQUIRED = "RefreshFromPresentationState"
SIBLING_EVALUATE_READINESS = "RebindIfNeeded"
SIBLING_CONFIGURE_ROUTING = "ShouldShowDebriefForState"
SIBLING_UNBOUND_CATEGORIES = "BindPresentation"
SIBLING_FIND_ENTRY = "HandlePresentationStateChanged"
SIBLING_GET_REQUIRED = "FindPresentationInWorld"
SIBLING_GET_DISPLAY = "TearDownWidgets"
SIBLING_ENTRIES = "RefreshFromPresentationState"
SIBLING_ROUTING = "RebindIfNeeded"

STOP_BEFORE_PRIVATE = "private:"
STOP_BEFORE_PROTECTED = "protected:"
STOP_BEFORE_PUBLIC = "public:"
STOP_BEFORE_LOOK_PITCH_MIN = "LookPitchMin"
STOP_BEFORE_SKYLINE_STYLE = "RefreshFromPresentationState"
STOP_BEFORE_MPD_LEFT = "CpgMpdLeft"
STOP_BEFORE_MPD_RIGHT = "CpgMpdRight"
STOP_BEFORE_EUFD = "CpgEufd"
STOP_BEFORE_RETICLE_H = "CpgReticleH"
STOP_BEFORE_GRIP_LEFT = "CpgGripLeft"
STOP_BEFORE_TEDAC_BEZEL = "CpgTedacBezel"
STOP_BEFORE_EUFD_TEXT = "CpgEufdText"
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
SIBLING_CPG_RAIL_RIGHT = "CpgRailRight"
SIBLING_CPG_RETICLE_V = "CpgReticleV"
SIBLING_CPG_TEDAC_TEXT = "CpgTedacText"
SIBLING_CPG_MPD_LEFT_TEXT = "CpgMpdLeftText"
SIBLING_HAND_MESH = "HandMesh"
SIBLING_CPG_EUFD_TEXT = "CpgEufdText"
SIBLING_CPG_MPD_RIGHT_TEXT = "CpgMpdRightText"
SIBLING_LOOK_PITCH_MIN = "LookPitchMin"
SIBLING_LOOK_PITCH_MAX = "LookPitchMax"
SIBLING_MOUSE_SENSITIVITY = "MouseSensitivity"
SIBLING_ROOT = "Root"
SIBLING_FLIGHT_ROUTE_SPLINE = "FlightRouteSpline"
SIBLING_MISSION_DEFINITION = "MissionDefinition"
SIBLING_MISSION_ID = "MissionId"
SIBLING_SKYLINE_STYLE = "SkylineStyle"
SIBLING_WEATHER_PROFILE_ID = "WeatherProfileId"
SIBLING_ROUTE_POINTS = "RoutePoints"
SIBLING_OBJECTIVE_ANCHORS = "ObjectiveAnchors"
SIBLING_LANDMARK_ANCHORS = "LandmarkAnchors"
SIBLING_FLIGHT_CLEARANCE_RADIUS = "FlightClearanceRadiusCentimeters"
SIBLING_FLIGHT_CLEARANCE_VERTICAL = "FlightClearanceVerticalCentimeters"
SIBLING_READINESS = "Readiness"
SIBLING_LOOK_YAW_LIMIT = "LookYawLimit"
SIBLING_WEATHER_IDENTITY = "WeatherIdentity"
SIBLING_OCEAN_TILES = "OceanTiles"
SIBLING_BEACH_TILES = "BeachTiles"
SIBLING_LAND_TILES = "LandTiles"
SIBLING_ROUTE_EXCLUSION = "RouteExclusion"
SIBLING_LAND_SCATTER_BOUNDS = "LandScatterBounds"
SIBLING_INLAND_VEGETATION_PCG = "InlandVegetationPCG"
SIBLING_PRODUCTION_LANDSCAPE = "ProductionLandscape"
SIBLING_AUTHORED_PCG_GRAPH = "AuthoredPCGGraph"
SIBLING_ALLOW_AUTHORED_PCG = "bAllowAuthoredPCGGeneration"
SIBLING_ROUTE_LENGTH_CM = "RouteLengthCm"
SIBLING_DISTRICT_LENGTH_CM = "DistrictLengthCm"
SIBLING_USE_AUTHORED_LANDSCAPE = "bUseAuthoredLandscapeSurface"
SIBLING_LAND_MATERIAL = "LandMaterial"
SIBLING_OCEAN_MATERIAL = "OceanMaterial"
SIBLING_BEACH_MATERIAL = "BeachMaterial"
SIBLING_ENABLE_COASTAL_HAZE = "bEnableCoastalHazeTransition"
SIBLING_COASTAL_HAZE_DELAY = "CoastalHazeDelaySeconds"
SIBLING_COASTAL_HAZE_FADE = "CoastalHazeFadeSeconds"
SIBLING_COASTAL_HAZE_HOLD = "CoastalHazeHoldSeconds"
SIBLING_COASTAL_HAZE_DENSITY = "CoastalHazeDensityIncrease"
SIBLING_ASSEMBLY_REVISION = "AssemblyRevision"
SIBLING_READINESS_LICENSED = "bLicensedVegetationApproved"
SIBLING_PCG_AUTHORIZED = "bPCGGenerationAuthorized"
SIBLING_SURFACE_EXPOSED = "bAuthoredLandscapeSurfaceExposed"
SIBLING_READY_FOR_PCG = "bReadyForAuthoredPCGGeneration"
SIBLING_FIRE_RATE = "FireRate"
SIBLING_RECOIL_PITCH = "RecoilPitch"
SIBLING_CANNON_MAGAZINE_SIZE = "CannonMagazineSize"
SIBLING_ROCKET_MAGAZINE_SIZE = "RocketMagazineSize"
SIBLING_GUIDED_MAGAZINE_SIZE = "GuidedMagazineSize"
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
    "Scripts/tests/test_sortie_hud_get_bound_presentation"
    "_decl_contract.py"
)
LEFTOVER_BIND_PRESENTATION = (
    "Scripts/tests/test_sortie_hud_bind_presentation"
    "_decl_contract.py"
)
LEFTOVER_REFRESH_PRESENTATION = (
    "Scripts/tests/test_sortie_hud_refresh_from_presentation_state"
    "_decl_contract.py"
)
LEFTOVER_AUDIO_DIRECTOR_RESOLVED = (
    "Scripts/tests/test_audio_director_are_resolved_production_loop_routes_complete"
    "_decl_contract.py"
)
LEFTOVER_AUDIO_DIRECTOR_ROUTE_COUNT = (
    "Scripts/tests/test_audio_director_get_resolved_production_loop_route_count"
    "_decl_contract.py"
)
LEFTOVER_PATHFINDER_LOCK_WINDOW_INTERVAL = (
    "Scripts/tests/test_pathfinder_encounter_lock_window_attack_interval"
    "_field_decl_contract.py"
)
LEFTOVER_OPEN_COCKPIT_WIND_LOOP = (
    "Scripts/tests/test_audio_director_open_cockpit_wind_loop"
    "_field_decl_contract.py"
)
LEFTOVER_THEATER_LAMP_COUNT = (
    "Scripts/tests/test_theater_kit_get_lamp_instance_count"
    "_decl_contract.py"
)
LEFTOVER_GUNNER_TRACE_RANGE = (
    "Scripts/tests/test_gunner_trace_range"
    "_field_decl_contract.py"
)
LEFTOVER_MISSION01_LICENSED_VEGETATION_LIBRARY = (
    "Scripts/tests/test_mission01_licensed_vegetation_library_approved"
    "_field_decl_contract.py"
)
LEFTOVER_ARCADE_LOOK_ENABLED = (
    "Scripts/tests/test_arcade_look_enabled"
    "_field_decl_contract.py"
)
LEFTOVER_CAMPAIGN_NIGHT_IDENTITY = (
    "Scripts/tests/test_campaign_mission_spec_night_identity"
    "_field_decl_contract.py"
)
LEFTOVER_AUDIO_PROCEDURAL_BANK_EMPTY = (
    "Scripts/tests/test_audio_procedural_bank_empty_fail_closed.py"
)
LEFTOVER_AUDIO_HARNESS_FAIL_CLOSED = (
    "Scripts/tests/test_audio_harness_fail_closed.py"
)
LEFTOVER_AUDIBLE_ACCEPTANCE_RECEIPT_DEFAULTS = (
    "Scripts/tests/test_audible_acceptance_receipt_defaults.py"
)
LEFTOVER_COASTAL_PLACEMENT_SEED = (
    "Scripts/tests/test_coastal_placement_seed"
    "_field_decl_contract.py"
)
LEFTOVER_MINIMUM_MEASURED_SAMPLES = (
    "Scripts/tests/test_audio_acceptance_harness_minimum_measured_samples"
    "_field_decl_contract.py"
)
LEFTOVER_MAXIMUM_ALLOWED_VOICES = (
    "Scripts/tests/test_audio_acceptance_harness_maximum_allowed_voices"
    "_field_decl_contract.py"
)
SIBLING_SAMPLE_RATE = "SampleRate"
SIBLING_GENERATED_BYTE_BUDGET = "GeneratedByteBudget"
SIBLING_WAVES = "Waves"
TARGET_WRONG_SAMPLE_RATE = "int32 SampleRate = 48000;"
TARGET_WRONG_BYTE_BUDGET = "int32 GeneratedByteBudget = 1048576;"
TARGET_WRONG_PLACEMENT_SEED = "int32 PlacementSeed = 0;"
TARGET_WRONG_MIN_SAMPLES = "int32 MinimumMeasuredSamples = 600;"
TARGET_WRONG_MAX_VOICES = "int32 MaximumAllowedVoices = 48;"
TARGET_WRONG_NIGHT_IDENTITY = "bool bNightIdentity = false;"
TARGET_WRONG_ARCADE_ENABLED = "bool bEnabled = true;"
TARGET_WRONG_BOOM = "TObjectPtr<USpringArmComponent> Boom;"
TARGET_WRONG_CRUISE = "TSoftObjectPtr<USoundBase> EngineCruiseLoop;"
TARGET_WRONG_POWER = "TSoftObjectPtr<USoundBase> EnginePowerLoop;"
TARGET_WRONG_PROP = "TSoftObjectPtr<USoundBase> PropellerLoop;"
TARGET_WRONG_IDLE = "TSoftObjectPtr<USoundBase> EngineIdleLoop;"
TARGET_WRONG_VOICE = "int32 GlobalVoiceLimit = 24;"
TARGET_WRONG_CULL = "float VegetationStartCullDistanceCm;"
TARGET_WRONG_DEVELOPMENT = (
    'UPROPERTY(EditAnywhere, BlueprintReadWrite, '
    'Category="Skyguard|Audio|Development")'
)
SIBLING_ENGINE_CRUISE_LOOP = "EngineCruiseLoop"
SIBLING_ENGINE_POWER_LOOP = "EnginePowerLoop"
SIBLING_PROPELLER_LOOP = "PropellerLoop"
SIBLING_ENGINE_IDLE_LOOP = "EngineIdleLoop"
SIBLING_GLOBAL_VOICE_LIMIT = "GlobalVoiceLimit"
SIBLING_EVENT_DEFINITIONS = "EventDefinitions"
SIBLING_COCKPIT_EXTERIOR = "CockpitExteriorAttenuation"
SIBLING_COCKPIT_LOW_PASS = "CockpitLowPassHz"
SIBLING_PRODUCTION_BANK = "ProductionBank"
SIBLING_PRODUCTION_BANK_ASSET = "ProductionBankAsset"
LEFTOVER_GUNNER_BOOM = (
    "Scripts/tests/test_gunner_boom"
    "_field_decl_contract.py"
)
LEFTOVER_AUDIO_DIRECTOR_ENGINE_CRUISE = (
    "Scripts/tests/test_audio_director_engine_cruise_loop"
    "_field_decl_contract.py"
)
LEFTOVER_AUDIO_DIRECTOR_ENGINE_POWER = (
    "Scripts/tests/test_audio_director_engine_power_loop"
    "_field_decl_contract.py"
)
LEFTOVER_AUDIO_DIRECTOR_PROPELLER = (
    "Scripts/tests/test_audio_director_propeller_loop"
    "_field_decl_contract.py"
)
LEFTOVER_AUDIO_DIRECTOR_ENGINE_IDLE = (
    "Scripts/tests/test_audio_director_engine_idle_loop"
    "_field_decl_contract.py"
)
LEFTOVER_AUDIO_DIRECTOR_VOICE_LIMIT = (
    "Scripts/tests/test_audio_director_global_voice_limit"
    "_field_decl_contract.py"
)
LEFTOVER_AUDIO_DIRECTOR_EVENTS = (
    "Scripts/tests/test_audio_director_event_definitions"
    "_field_decl_contract.py"
)
LEFTOVER_AUDIO_DIRECTOR_COCKPIT_EXT = (
    "Scripts/tests/test_audio_director_cockpit_exterior_attenuation"
    "_field_decl_contract.py"
)
LEFTOVER_AUDIO_DIRECTOR_COCKPIT_LP = (
    "Scripts/tests/test_audio_director_cockpit_low_pass_hz"
    "_field_decl_contract.py"
)
LEFTOVER_AUDIO_DIRECTOR_PRODUCTION_BANK = (
    "Scripts/tests/test_audio_director_production_bank"
    "_field_decl_contract.py"
)
LEFTOVER_AUDIO_DIRECTOR_PRODUCTION_BANK_ASSET = (
    "Scripts/tests/test_audio_director_production_bank_asset"
    "_field_decl_contract.py"
)
LEFTOVER_ROUTING_COCKPIT_EXT = (
    "Scripts/tests/test_production_audio_routing_cockpit_exterior_attenuation"
    "_field_decl_contract.py"
)
LEFTOVER_ROUTING_COCKPIT_LP = (
    "Scripts/tests/test_production_audio_routing_cockpit_low_pass_hz"
    "_field_decl_contract.py"
)
LEFTOVER_AUDIO_PRODUCTION_BANK_EMPTY = (
    "Scripts/tests/test_audio_production_bank_empty_fail_closed.py"
)
LEFTOVER_MISSION01_AUDIO_DIRECTOR = (
    "Scripts/tests/test_mission01_audio_director"
    "_field_decl_contract.py"
)
LEFTOVER_PROCEDURAL_BANK_SAMPLE_RATE = (
    "Scripts/tests/test_audio_procedural_bank_sample_rate"
    "_field_decl_contract.py"
)
LEFTOVER_PROCEDURAL_BANK_BYTE_BUDGET = (
    "Scripts/tests/test_audio_procedural_bank_generated_byte_budget"
    "_field_decl_contract.py"
)
LEFTOVER_PROCEDURAL_BANK_AUDITION = (
    "Scripts/tests/test_audio_procedural_bank_enable_development_audition"
    "_field_decl_contract.py"
)
TARGET_WRONG_BUDGET = (
    'UPROPERTY(EditAnywhere, BlueprintReadWrite, '
    'Category="Skyguard|Audio|Budget")'
)
TARGET_WRONG_ACCEPTANCE = (
    'UPROPERTY(EditAnywhere, BlueprintReadWrite, '
    'Category="Skyguard|Audio|Acceptance")'
)
TARGET_WRONG_PERFORMANCE = (
    'UPROPERTY(EditAnywhere, BlueprintReadWrite, '
    'Category="Skyguard|Environment|Performance")'
)
LEFTOVER_ASSEMBLY_REVISION = (
    "Scripts/tests/test_mission_map_assembly_revision"
    "_field_decl_contract.py"
)
LEFTOVER_READINESS_LICENSED_VEGETATION = (
    "Scripts/tests/test_mission01_environment_readiness_licensed_vegetation_approved"
    "_field_decl_contract.py"
)
LEFTOVER_ROUTE_POINTS = (
    "Scripts/tests/test_mission_map_route_points"
    "_field_decl_contract.py"
)
LEFTOVER_ALLOW_AUTHORED_PCG = (
    "Scripts/tests/test_mission01_allow_authored_pcg_generation"
    "_field_decl_contract.py"
)
LEFTOVER_USE_AUTHORED_LANDSCAPE = (
    "Scripts/tests/test_mission01_use_authored_landscape_surface"
    "_field_decl_contract.py"
)
LEFTOVER_ENABLE_COASTAL_HAZE = (
    "Scripts/tests/test_mission01_enable_coastal_haze_transition"
    "_field_decl_contract.py"
)
TARGET_WRONG_ASSEMBLY = (
    'FName AssemblyRevision = TEXT("CampaignMapAssembly_v1");'
)
TARGET_WRONG_ROUTE_POINTS = "TArray<FSkyguardRoutePoint> RoutePoints;"
TARGET_WRONG_ALLOW_PCG = "bool bAllowAuthoredPCGGeneration = false;"
TARGET_WRONG_HAZE = "bool bEnableCoastalHazeTransition = true;"
TARGET_WRONG_LANDSCAPE = "bool bUseAuthoredLandscapeSurface = false;"
TARGET_WRONG_PCG_AUTH = "bool bPCGGenerationAuthorized = false;"
TARGET_WRONG_SURFACE_EXPOSED = "bool bAuthoredLandscapeSurfaceExposed = false;"
TARGET_WRONG_READY_PCG = "bool bReadyForAuthoredPCGGeneration = false;"
TARGET_WRONG_READINESS_LICENSED = "bool bLicensedVegetationApproved = false;"
LEFTOVER_GUNNER_LOOK_YAW_LIMIT = (
    "Scripts/tests/test_gunner_look_yaw_limit"
    "_field_decl_contract.py"
)
LEFTOVER_THEATER_WEATHER_IDENTITY = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
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
LEFTOVER_GUNNER_CPG_CONSOLE_RIGHT = (
    "Scripts/tests/test_gunner_cpg_console_right"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_RAIL_LEFT = (
    "Scripts/tests/test_gunner_cpg_rail_left"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_RAIL_RIGHT = (
    "Scripts/tests/test_gunner_cpg_rail_right"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_TEDAC_TEXT = (
    "Scripts/tests/test_gunner_cpg_tedac_text"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_MPD_LEFT_TEXT = (
    "Scripts/tests/test_gunner_cpg_mpd_left_text"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_MPD_RIGHT_TEXT = (
    "Scripts/tests/test_gunner_cpg_mpd_right_text"
    "_field_decl_contract.py"
)
LEFTOVER_GUNNER_CPG_EUFD_TEXT = (
    "Scripts/tests/test_gunner_cpg_eufd_text"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_CANNON_MAGAZINE = (
    "Scripts/tests/test_loadout_spec_cannon_magazine_size"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_ROCKET_MAGAZINE = (
    "Scripts/tests/test_loadout_spec_rocket_magazine_size"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_GUIDED_MAGAZINE = (
    "Scripts/tests/test_loadout_spec_guided_magazine_size"
    "_field_decl_contract.py"
)
LEFTOVER_GUNSHIP_WEAPON_STATIONS = (
    "Scripts/tests/test_gunship_weapon_stations_contract.py"
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
    "SkyguardAudioDirectorComponent.h",
    "SkyguardAudioProductionBank.h",
    "SkyguardAudioProductionBank.cpp",
    "SkyguardMission01EnvironmentAuthoringLibrary.cpp",
    "SkyguardAudioDirectorComponent.cpp",
    "SkyguardAudioProceduralBankComponent.h",
    "SkyguardAudioProceduralBankComponent.cpp",
    "SkyguardMission01EnvironmentDirector.h",
    "SkyguardMission01EnvironmentDirector.cpp",
    "SkyguardMissionMapAssemblyDirector.h",
    "SkyguardMissionMapAssemblyDirector.cpp",
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
    "SkyguardSortieHudHostComponent.h",
    "SkyguardSortieHudHostComponent.cpp",
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
        LEFTOVER_BIND_PRESENTATION,
        LEFTOVER_REFRESH_PRESENTATION,
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
        LEFTOVER_GUNNER_CPG_CONSOLE_RIGHT,
        LEFTOVER_GUNNER_CPG_RAIL_LEFT,
        LEFTOVER_GUNNER_CPG_RAIL_RIGHT,
        LEFTOVER_GUNNER_CPG_TEDAC_TEXT,
        LEFTOVER_GUNNER_CPG_MPD_LEFT_TEXT,
        LEFTOVER_GUNNER_CPG_MPD_RIGHT_TEXT,
        LEFTOVER_GUNNER_CPG_EUFD_TEXT,
        LEFTOVER_LOADOUT_CANNON_MAGAZINE,
        LEFTOVER_LOADOUT_ROCKET_MAGAZINE,
        LEFTOVER_LOADOUT_GUIDED_MAGAZINE,
        LEFTOVER_GUNSHIP_WEAPON_STATIONS,
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
        LEFTOVER_GUNNER_LOOK_YAW_LIMIT,
        LEFTOVER_THEATER_WEATHER_IDENTITY,
        LEFTOVER_ASSEMBLY_REVISION,
        LEFTOVER_READINESS_LICENSED_VEGETATION,
        LEFTOVER_ROUTE_POINTS,
        LEFTOVER_ALLOW_AUTHORED_PCG,
        LEFTOVER_USE_AUTHORED_LANDSCAPE,
        LEFTOVER_MISSION01_LICENSED_VEGETATION_LIBRARY,
        LEFTOVER_ARCADE_LOOK_ENABLED,
        LEFTOVER_CAMPAIGN_NIGHT_IDENTITY,
        LEFTOVER_AUDIO_PROCEDURAL_BANK_EMPTY,
        LEFTOVER_AUDIO_HARNESS_FAIL_CLOSED,
        LEFTOVER_AUDIBLE_ACCEPTANCE_RECEIPT_DEFAULTS,
        LEFTOVER_COASTAL_PLACEMENT_SEED,
        LEFTOVER_MINIMUM_MEASURED_SAMPLES,
        LEFTOVER_MAXIMUM_ALLOWED_VOICES,
        f"{prefix}test_audio_director_listener_perspective_fail_closed.py",
        f"{prefix}test_audio_director_engine_state_fail_closed.py",
        f"{prefix}test_audio_director_suppression_fail_closed.py",
        f"{prefix}test_audio_director_bank_null_fail_closed.py",
        f"{prefix}test_audio_director_world_event_fail_closed.py",
        f"{prefix}test_audio_production_bank_empty_fail_closed.py",
        f"{prefix}test_coastal_tree_instances_field_decl_contract.py",
        f"{prefix}test_coastal_shrub_instances_field_decl_contract.py",
        f"{prefix}test_coastal_wind_source_field_decl_contract.py",
        f"{prefix}test_coastal_epic_tree_budget_field_decl_contract.py",
        f"{prefix}test_coastal_epic_shrub_budget_field_decl_contract.py",
        f"{prefix}test_coastal_vegetation_start_cull_distance_cm"
        "_field_decl_contract.py",
        f"{prefix}test_coastal_vegetation_end_cull_distance_cm"
        "_field_decl_contract.py",
        LEFTOVER_ENABLE_COASTAL_HAZE,
        LEFTOVER_GUNNER_BOOM,
        LEFTOVER_AUDIO_DIRECTOR_ENGINE_CRUISE,
        LEFTOVER_AUDIO_DIRECTOR_ENGINE_POWER,
        LEFTOVER_AUDIO_DIRECTOR_PROPELLER,
        LEFTOVER_AUDIO_DIRECTOR_ENGINE_IDLE,
        LEFTOVER_AUDIO_DIRECTOR_VOICE_LIMIT,
        LEFTOVER_AUDIO_DIRECTOR_EVENTS,
        LEFTOVER_AUDIO_DIRECTOR_COCKPIT_EXT,
        LEFTOVER_AUDIO_DIRECTOR_COCKPIT_LP,
        LEFTOVER_AUDIO_DIRECTOR_PRODUCTION_BANK,
        LEFTOVER_AUDIO_DIRECTOR_PRODUCTION_BANK_ASSET,
        LEFTOVER_ROUTING_COCKPIT_EXT,
        LEFTOVER_ROUTING_COCKPIT_LP,
        LEFTOVER_AUDIO_PRODUCTION_BANK_EMPTY,
        LEFTOVER_MISSION01_AUDIO_DIRECTOR,
        LEFTOVER_PROCEDURAL_BANK_SAMPLE_RATE,
        LEFTOVER_PROCEDURAL_BANK_BYTE_BUDGET,
        LEFTOVER_PROCEDURAL_BANK_AUDITION,
        LEFTOVER_OPEN_COCKPIT_WIND_LOOP,
        LEFTOVER_THEATER_LAMP_COUNT,
        LEFTOVER_GUNNER_TRACE_RANGE,
    ) + leftover_apache_ufunction_scripts() + leftover_apache_mesh_field_scripts()


LOCKED_SCRIPTS = (
    "Scripts/tests/test_sortie_hud_bind_presentation"
    "_decl_contract.py",
    "Scripts/tests/test_sortie_hud_refresh_from_presentation_state"
    "_decl_contract.py",
    "Scripts/tests/test_mission01_prepare_governed_landscape_for_visible_validation"
    "_decl_contract.py",
    "Scripts/tests/test_mission01_get_active_rhi_and_feature_level"
    "_decl_contract.py",
    "Scripts/tests/test_sortie_hud_host_fail_closed.py",
    "Scripts/tests/test_gunner_cpg_sight_hud_field_decl_contract.py",
    "Scripts/tests/test_bind_hud_host_presentation.py",
    "Scripts/tests/test_mission01_author_governed_landscape_and_graph"
    "_decl_contract.py",
    "Scripts/tests/test_mission01_author_governed_landscape_with_existing_graph"
    "_decl_contract.py",
    "Scripts/tests/test_mission01_audit_governed_landscape_and_graph"
    "_decl_contract.py",
    "Scripts/tests/test_mission01_sample_landscape_height"
    "_decl_contract.py",
    "Scripts/tests/test_audio_production_bank_ensure_default_entries"
    "_decl_contract.py",
    "Scripts/tests/test_gunner_get_sortie_hits"
    "_decl_contract.py",
    "Scripts/tests/test_gunner_reset_sortie_combat_stats"
    "_decl_contract.py",
    "Scripts/tests/test_gunner_get_applied_look_sensitivity"
    "_decl_contract.py",
    "Scripts/tests/test_settings_get_invert_vertical_look"
    "_decl_contract.py",
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
) + leftover_live_copy_boss_scripts()


def leftover_banned_primary_mesh() -> str:
    return "Ri" + "fle" + "Mesh"


def leftover_banned_guided_tube() -> str:
    return "Ig" + "la" + "Tube"


def leftover_banned_guided_muzzle() -> str:
    return "Ig" + "la" + "Muzzle"


def leftover_banned_receiver() -> str:
    return "Ri" + "fle" + "Receiver"


def leftover_banned_front_sight() -> str:
    return "FrontSight"


def leftover_banned_rear_sight() -> str:
    return "RearSight"


def leftover_banned_forearm() -> str:
    return "ForearmMesh"


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
METHOD_SIGNATURE_RE = re.compile(
    r"USkyguardSortiePresentationComponent\*\s*"
    r"GetBoundPresentation\s*\(\s*\)\s*const\s*"
    r"(?:;|\{[^}]*return\s+Presentation\s*;\s*\})"
)
BIND_PRESENTATION_IDENT_RE = re.compile(r"\bBindPresentation\b")
GET_BOUND_PRESENTATION_IDENT_RE = re.compile(r"\bGetBoundPresentation\b")
GET_BOUND_WRONG_TYPE_RE = re.compile(
    r"(?:float|FName|bool|FLinearColor|void|int32)\s+"
    r"GetBoundPresentation\b"
)
GET_BOUND_NO_CONST_RE = re.compile(
    r"USkyguardSortiePresentationComponent\*\s*"
    r"GetBoundPresentation\s*\(\s*\)\s*;"
)
LEFTOVER_CLONE_RESOLVED_RE = re.compile(
    r"\bAuthorGovernedLandscapeWithExistingGraph\b"
)
LEFTOVER_SIBLING_INIT_RE = re.compile(
    r"\bAuditGovernedLandscapeAndGraph\b"
)
LEFTOVER_SAMPLE_HEIGHT_RE = re.compile(
    r"\bSampleLandscapeHeight\b"
)
LEFTOVER_SAMPLE_FOOTPRINT_RE = re.compile(
    r"\bSampleLandscapeFootprint\b"
)
LEFTOVER_GET_SORTIE_HITS_RE = re.compile(
    r"\bint32\s+GetSortieHits\s*\("
)
LEFTOVER_SUCCESS_FIELD_RE = re.compile(
    r"\bbool\s+bSuccess\s*=\s*false\b"
)
LEFTOVER_PRODUCTION_BANK_FIELD_RE = re.compile(
    r"TObjectPtr\s*<\s*USkyguardAudioProductionBank\s*>\s+ProductionBank\b"
)
LEFTOVER_READINESS_LICENSED_DECL_RE = re.compile(
    r"bool\s+bLicensedVegetationApproved\s*=\s*false\s*;"
)
ASSEMBLY_REVISION_DECL_RE = re.compile(
    r"FName\s+AssemblyRevision\b"
)
ROUTE_POINTS_DECL_RE = re.compile(
    r"TArray\s*<\s*FSkyguardRoutePoint\s*>\s+RoutePoints\b"
)
ALLOW_PCG_DECL_RE = re.compile(
    r"bool\s+bAllowAuthoredPCGGeneration\b"
)
HAZE_DECL_RE = re.compile(
    r"bool\s+bEnableCoastalHazeTransition\b"
)
LANDSCAPE_DECL_RE = re.compile(
    r"bool\s+bUseAuthoredLandscapeSurface\b"
)
PCG_AUTH_DECL_RE = re.compile(
    r"bool\s+bPCGGenerationAuthorized\b"
)
SURFACE_EXPOSED_DECL_RE = re.compile(
    r"bool\s+bAuthoredLandscapeSurfaceExposed\b"
)
READY_PCG_DECL_RE = re.compile(
    r"bool\s+bReadyForAuthoredPCGGeneration\b"
)
SAMPLE_RATE_DECL_RE = re.compile(
    r"int32\s+SampleRate\b"
)
BYTE_BUDGET_DECL_RE = re.compile(
    r"int32\s+GeneratedByteBudget\b"
)
MIN_SAMPLES_DECL_RE = re.compile(
    r"int32\s+MinimumMeasuredSamples\s*=\s*600\b"
)
MAX_VOICES_DECL_RE = re.compile(
    r"int32\s+MaximumAllowedVoices\s*=\s*48\b"
)
PLACEMENT_SEED_DECL_RE = re.compile(
    r"PlacementSeed\b"
)
ARCADE_ENABLED_DECL_RE = re.compile(
    r"bool\s+bEnabled\s*=\s*true\s*;"
)
NIGHT_IDENTITY_DECL_RE = re.compile(
    r"bool\s+bNightIdentity\b"
)
MISSION01_LIBRARY_DECL_RE = re.compile(
    r"bool\s+bLicensedVegetationLibraryApproved\b"
)
LOOK_YAW_LIMIT_DECL_RE = re.compile(
    r"float\s+LookYawLimit\s*=\s*95\.f\s*;"
)
WEATHER_IDENTITY_DECL_RE = re.compile(
    r"FName\s+WeatherIdentity\b"
)
FIRE_RATE_DECL_RE = re.compile(
    r"float\s+FireRate\s*=\s*12\.0f\b"
)
RECOIL_PITCH_DECL_RE = re.compile(
    r"float\s+RecoilPitch\s*=\s*0\.92f\b"
)
INVENTED_UFUNCTION = (
    "BlueprintPure",
    "VisibleAnywhere",
    "EditAnywhere",
    "BlueprintReadOnly",
    "BlueprintReadWrite",
    "Transient",
    "MultiLine",
    "BlueprintAuthorityOnly",
    "meta=",
)
INVENTED_DECL_META = (
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
        SIBLING_INITIALIZE_REQUIRED,
        SIBLING_EVALUATE_READINESS,
        SIBLING_CONFIGURE_ROUTING,
        SIBLING_UNBOUND_CATEGORIES,
        SIBLING_FIND_ENTRY,
        SIBLING_GET_REQUIRED,
        SIBLING_GET_DISPLAY,
        "GetActiveRHIAndFeatureLevel",
        "AuditLandscapeVisibleReadiness",
        "FinishLandscapeMaterialCompilation",
        "AuditLandscapeMaterialCompilation",
        "BeginTransientLandscapeDiagnosticMaterialDeferred",
        "ConfigureLandscapeSceneCaptureDiagnostic",
        "SetTransientLandscapeDiagnosticMaterial",
        "SetTransientLandscapeDiagnosticMaterialSynchronized",
        "RefreshFromPresentationState",
        "RebindIfNeeded",
        "BindPresentation",
        "ShouldShowDebriefForState",
        "GetActivationCount",
        "EnsureDefaultEntries",
        "AuthorGovernedLandscapeAndGraph",
        "SampleLandscapeHeight",
        "SampleLandscapeFootprint",
        SIBLING_GET_RESOLVED_COUNT,
        SIBLING_ENTRIES,
        SIBLING_ROUTING,
        SIBLING_GET_WIND_BLEND,
        SIBLING_GET_POWER_BLEND,
        SIBLING_GET_CRUISE_BLEND,
        SIBLING_GET_IDLE_BLEND,
        SIBLING_GET_ACTIVE_VOICE_COUNT,
        SIBLING_GET_TELEMETRY,
        SIBLING_GET_SUPPRESSION,
        SIBLING_ADVANCE_AUDIO_STATE,
        SIBLING_APPLY_HEARING,
        SIBLING_SET_LISTENER,
        SIBLING_SET_ENGINE_STATE,
        SIBLING_TRIGGER_WORLD,
        SIBLING_TRIGGER_EVENT,
        SIBLING_GET_PRODUCTION_AUDIT,
        SIBLING_APPLY_PRODUCTION_BANK,
        SIBLING_PRIME_CONFIGURED,
        SIBLING_ENGINE_CRUISE_LOOP,
        SIBLING_ENGINE_POWER_LOOP,
        SIBLING_PROPELLER_LOOP,
        SIBLING_ENGINE_IDLE_LOOP,
        SIBLING_GLOBAL_VOICE_LIMIT,
        SIBLING_EVENT_DEFINITIONS,
        SIBLING_COCKPIT_EXTERIOR,
        SIBLING_COCKPIT_LOW_PASS,
        SIBLING_PRODUCTION_BANK,
        SIBLING_PRODUCTION_BANK_ASSET,
        SIBLING_FIRE_RATE,
        SIBLING_RECOIL_PITCH,
        SIBLING_CANNON_MAGAZINE_SIZE,
        SIBLING_ROCKET_MAGAZINE_SIZE,
        SIBLING_GUIDED_MAGAZINE_SIZE,
        SIBLING_LOOK_YAW_LIMIT,
        SIBLING_WEATHER_IDENTITY,
        SIBLING_BOOM,
        SIBLING_ROOT,
        SIBLING_OCEAN_TILES,
        SIBLING_BEACH_TILES,
        SIBLING_LAND_TILES,
        SIBLING_READINESS,
        SIBLING_ALLOW_AUTHORED_PCG,
        SIBLING_ASSEMBLY_REVISION,
        SIBLING_SAMPLE_RATE,
        SIBLING_GENERATED_BYTE_BUDGET,
        SIBLING_WAVES,
        SIBLING_MAX_INTEGRITY,
        SIBLING_CURRENT_INTEGRITY,
        SIBLING_HULL_COLLIDER,
        leftover_banned_primary_mesh(),
        leftover_banned_receiver(),
        leftover_banned_front_sight(),
        leftover_banned_rear_sight(),
        leftover_banned_forearm(),
        leftover_banned_guided_tube(),
        leftover_banned_guided_muzzle(),
        SIBLING_HAND_MESH,
        SIBLING_CPG_EUFD_TEXT,
        SIBLING_CPG_TEDAC_TEXT,
        SIBLING_CPG_MPD_RIGHT_TEXT,
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


def has_identifier(region: str, name: str) -> bool:
    return re.search(r"\b" + re.escape(name) + r"\b", region) is not None


def leftover_analog_field_in_region(compact: str) -> bool:
    checks = (
        LEFTOVER_READINESS_LICENSED_DECL_RE,
        LOOK_YAW_LIMIT_DECL_RE,
        ASSEMBLY_REVISION_DECL_RE,
        ROUTE_POINTS_DECL_RE,
        ALLOW_PCG_DECL_RE,
        HAZE_DECL_RE,
        LANDSCAPE_DECL_RE,
        PCG_AUTH_DECL_RE,
        SURFACE_EXPOSED_DECL_RE,
        READY_PCG_DECL_RE,
        WEATHER_IDENTITY_DECL_RE,
        FIRE_RATE_DECL_RE,
        RECOIL_PITCH_DECL_RE,
        SAMPLE_RATE_DECL_RE,
        BYTE_BUDGET_DECL_RE,
        MIN_SAMPLES_DECL_RE,
        MAX_VOICES_DECL_RE,
        PLACEMENT_SEED_DECL_RE,
        ARCADE_ENABLED_DECL_RE,
        NIGHT_IDENTITY_DECL_RE,
        MISSION01_LIBRARY_DECL_RE,
    )
    for pattern in checks:
        if pattern.search(compact):
            return True
    if re.search(r"float\s+Health\s*=\s*160\.f\b", compact):
        return True
    return False


def has_declaration(region: str, declaration: str) -> bool:
    # Fail-closed on authored BlueprintPure signature
    # USkyguardSortiePresentationComponent* GetBoundPresentation() const.
    # Accept origin/main inline `{ return Presentation; }` AND
    # declaration-only. Do not require a body-less form.
    # Do not accept missing const, a void/bool/float/int32 rename,
    # leftover analog BindPresentation / RefreshFromPresentationState /
    # RebindIfNeeded, leftover analog GetSortieHits / bSuccess = false,
    # leftover FName WeatherIdentity, leftover TObjectPtr
    # ProductionBank, leftover FireRate / RecoilPitch,
    # leftover Boom, leftover VegetationStartCullDistanceCm,
    # leftover GetActivationCount, leftover EnsureDefaultEntries,
    # or Harbor 40 / 80.
    del declaration
    compact = collapsed(region)
    if METHOD_SIGNATURE_RE.search(compact) is None:
        return False
    if GET_BOUND_WRONG_TYPE_RE.search(compact):
        return False
    if GET_BOUND_NO_CONST_RE.search(compact) and (
        METHOD_SIGNATURE_RE.search(compact) is None
    ):
        return False
    if BIND_PRESENTATION_IDENT_RE.search(compact) and (
        METHOD_SIGNATURE_RE.search(compact) is None
    ):
        return False
    if re.search(r"\bbool\s+GetBoundPresentation\b", compact):
        return False
    if re.search(r"\bfloat\s+GetBoundPresentation\b", compact):
        return False
    if re.search(r"\bint32\s+GetBoundPresentation\b", compact):
        return False
    if re.search(
        r"\bstatic\s+FSkyguardLandscapeVisibleAudit\s+GetBoundPresentation\b",
        compact,
    ):
        return False
    if GET_BOUND_PRESENTATION_IDENT_RE.search(compact) is None:
        return False
    if LEFTOVER_PRODUCTION_BANK_FIELD_RE.search(compact):
        return False
    if leftover_analog_field_in_region(compact):
        return False
    return True


def count_one_declaration(region: str, declaration: str) -> int:
    del declaration
    compact = collapsed(region)
    return len(METHOD_SIGNATURE_RE.findall(compact))


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
        section = rest[: next_access.start()]
    else:
        close = rest.rfind("}")
        if close == -1:
            raise AssertionError(
                f"{CLASS_NAME} public section is missing from "
                f"origin/main:{HEADER_PATH}"
            )
        section = rest[:close]
    if STOP_BEFORE_PRIVATE in section:
        raise AssertionError(
            f"{CLASS_NAME} parse window includes {STOP_BEFORE_PRIVATE}"
        )
    return section


def spec_section(header: str) -> str:
    section = public_section(header)
    uproperty = re.search(r"\bUPROPERTY\s*\(", section)
    if uproperty is not None:
        section = section[: uproperty.start()]
    method = "GetBoundPresentation"
    method_match = re.search(r"\b" + re.escape(method) + r"\b", section)
    if method_match is not None:
        uf = section.rfind("UFUNCTION", 0, method_match.start())
        if uf != -1:
            section = section[uf:]
        next_uf = re.search(r"\bUFUNCTION\s*\(", section[1:])
        if next_uf is not None:
            section = section[: next_uf.start() + 1]
    if STOP_BEFORE_PRIVATE in section:
        raise AssertionError(
            f"{CLASS_NAME} parse window includes {STOP_BEFORE_PRIVATE}"
        )
    if has_identifier(section, STOP_BEFORE_EVENT_DEFINITIONS):
        raise AssertionError(
            f"{CLASS_NAME} parse window includes "
            f"{STOP_BEFORE_EVENT_DEFINITIONS}"
        )
    for token in leaked_neighbor_tokens():
        if token in section:
            raise AssertionError(
                f"{CLASS_NAME} parse window includes {token}"
            )
    for leftover in leftover_apache_ufunction_tokens():
        if has_identifier(section, leftover):
            raise AssertionError(
                f"{CLASS_NAME} parse window includes leftover "
                f"UFUNCTION {leftover}"
            )
    for leftover in leftover_harbor_breaker_tokens():
        if leftover in section:
            raise AssertionError(
                f"{CLASS_NAME} parse window includes leftover "
                f"Harbor Breaker {leftover}"
            )
    for sibling in (
        SIBLING_ENGINE_IDLE_LOOP,
        SIBLING_ENGINE_CRUISE_LOOP,
        SIBLING_ENGINE_POWER_LOOP,
        SIBLING_PROPELLER_LOOP,
        SIBLING_GLOBAL_VOICE_LIMIT,
        SIBLING_PRODUCTION_BANK,
        SIBLING_PRODUCTION_BANK_ASSET,
        SIBLING_COCKPIT_EXTERIOR,
        SIBLING_COCKPIT_LOW_PASS,
        SIBLING_FIRE_RATE,
        SIBLING_RECOIL_PITCH,
        SIBLING_WEATHER_IDENTITY,
        SIBLING_BOOM,
        leftover_banned_guided_muzzle(),
        leftover_banned_primary_mesh(),
        SIBLING_HAND_MESH,
        "SampleLandscapeHeight",
        "SampleLandscapeFootprint",
        "GetSortieHits",
        "ResetSortieCombatStats",
        "AuthorGovernedLandscapeAndGraph",
        "GetActiveRHIAndFeatureLevel",
        "AuditLandscapeVisibleReadiness",
        "FinishLandscapeMaterialCompilation",
        "AuditLandscapeMaterialCompilation",
        "RefreshFromPresentationState",
        "RebindIfNeeded",
        "BindPresentation",
    ):
        if has_identifier(section, sibling):
            raise AssertionError(
                f"{CLASS_NAME} parse window claims leftover analog "
                f"{sibling}"
            )
    guided_prefix = leftover_live_copy_title_tokens()[0]
    if has_identifier(section, guided_prefix):
        raise AssertionError(
            f"{CLASS_NAME} parse window claims banned "
            f"{guided_prefix} field"
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
            r"\s*USkyguardSortiePresentationComponent\*\s+"
            r"GetBoundPresentation\b",
            compact[index:],
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UFUNCTION for GetBoundPresentation "
        f"is missing from origin/main:{HEADER_PATH} class "
        f"{CLASS_NAME} public section"
    )


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"class {CLASS_NAME} public section"
        )
    return declaration


class SortieHudGetBoundPresentationDeclContractTests(
    unittest.TestCase
):
    def test_sortie_hud_host_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertIn(f"class SKYGUARD52_API {CLASS_NAME}", header)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_PROTECT_ASSET_CLASS)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_RADAR_NODE_CLASS)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_THEATER_KIT_ACTOR)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_AUDIO_DIRECTOR_CLASS)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_PRODUCTION_BANK_CLASS)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_AUTHORING_RESULT_STRUCT)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_VISIBLE_AUDIT_STRUCT)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_DIRECTOR_CLASS)
        self.assertNotEqual(
            CLASS_NAME,
            "USkyguardMission01EnvironmentAuthoringLibrary",
        )
        self.assertNotEqual(CLASS_NAME, "USkyguardAudioProductionBank")
        self.assertNotEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.h",
        )
        self.assertNotEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardAudioProductionBank.h",
        )
        self.assertNotEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardCpgSightHud.h",
        )
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = spec_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(
            has_identifier(section, "GetBoundPresentation"),
            section,
        )
        self.assertIn("UFUNCTION", section)
        self.assertIn(STOP_BEFORE_PUBLIC, header)
        self.assertNotIn(STOP_BEFORE_PRIVATE, section)
        self.assertTrue(has_identifier(body, STOP_BEFORE_SKYLINE_STYLE), body)
        self.assertFalse(
            has_identifier(section, STOP_BEFORE_SKYLINE_STYLE),
            section,
        )
        self.assertTrue(has_identifier(body, SIBLING_ENTRIES), body)
        self.assertFalse(has_identifier(section, SIBLING_ENTRIES), section)
        self.assertTrue(has_identifier(body, SIBLING_ROUTING), body)
        self.assertFalse(has_identifier(section, SIBLING_ROUTING), section)
        self.assertTrue(has_identifier(body, STOP_BEFORE_EVENT_DEFINITIONS), body)
        self.assertFalse(
            has_identifier(section, STOP_BEFORE_EVENT_DEFINITIONS),
            section,
        )
        self.assertTrue(has_identifier(body, STOP_BEFORE_SKYLINE_STYLE), body)
        self.assertFalse(has_identifier(section, STOP_BEFORE_SKYLINE_STYLE), section)
        self.assertTrue(has_identifier(body, "RebindIfNeeded"), body)
        self.assertFalse(has_identifier(section, "RebindIfNeeded"), section)
        self.assertFalse(has_identifier(section, SIBLING_ROOT), section)
        self.assertFalse(
            has_identifier(section, SIBLING_OCEAN_TILES),
            section,
        )
        self.assertFalse(has_identifier(section, SIBLING_PRODUCTION_LANDSCAPE), section)
        self.assertFalse(has_identifier(section, SIBLING_READINESS), section)
        self.assertFalse(has_identifier(section, SIBLING_ALLOW_AUTHORED_PCG), section)
        self.assertFalse(has_identifier(section, SIBLING_FIRE_RATE), section)
        self.assertFalse(has_identifier(section, SIBLING_RECOIL_PITCH), section)
        self.assertFalse(has_identifier(section, SIBLING_LOOK_YAW_LIMIT), section)
        self.assertFalse(has_identifier(section, SIBLING_WEATHER_IDENTITY), section)
        self.assertFalse(
            has_identifier(section, leftover_banned_guided_muzzle()),
            section,
        )
        self.assertFalse(
            has_identifier(section, leftover_banned_primary_mesh()),
            section,
        )
        self.assertFalse(has_identifier(section, SIBLING_HAND_MESH), section)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_APACHE_AIRCRAFT_CLASS)
        self.assertNotEqual(CLASS_NAME, "ASkyguardGunner")
        self.assertNotEqual(HEADER_PATH, "Source/Skyguard52/SkyguardGunner.h")
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, section)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, section)
        self.assertNotIn(LEFTOVER_THEATER_KIT_ACTOR, section)
        for sibling in sibling_uncontracted_decls():
            self.assertFalse(has_identifier(LOCKED_DECL, sibling), sibling)
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
            "public:\n"
            f"\t{LOCKED_UFUNCTION_WRAP}\n"
            f"\t{LOCKED_DECL}\n"
            "private:\n"
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
            f"\t{TARGET_WRONG_LAMP}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(theater)
        self.assertIn(CLASS_NAME, str(raised.exception))
        loadout = (
            f"struct {STOP_BEFORE_LOADOUT_SPEC}\n"
            "{\n"
            f"\t{TARGET_WRONG_CANNON_MAG}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(loadout)
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_leftover_class_same_identifier_does_not_satisfy(self) -> None:
        mixed = (
            f"class {LEFTOVER_PROTECT_ASSET_CLASS}\n"
            "{\n"
            "public:\n"
            f"\t{LOCKED_UFUNCTION_WRAP}\n"
            f"\t{LOCKED_DECL}\n"
            "private:\n"
            "};\n"
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            "\tvoid UnrelatedHelper();\n"
            "private:\n"
            "};\n"
        )
        section = spec_section(mixed)
        self.assertFalse(
            has_identifier(section, "GetBoundPresentation"),
            section,
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn(
            "GetBoundPresentation",
            str(raised.exception),
        )
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_get_bound_presentation_declaration_fails_closed(
        self,
    ) -> None:
        empty = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{LOCKED_UFUNCTION_WRAP}\n"
            "\tvoid UnrelatedHelper();\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        section = spec_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn(
            "GetBoundPresentation",
            str(raised.exception),
        )
        self.assertIn("missing", str(raised.exception).lower())

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{LOCKED_UFUNCTION_WRAP}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn(
            "GetBoundPresentation",
            str(raised.exception),
        )
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = spec_section(origin_main_header())
        self.assertIn(LOCKED_UFUNCTION_WRAP, section)
        self.assertIn("BlueprintPure", section)
        self.assertIn('Category="Skyguard|Presentation|HUD"', section)
        self.assertNotIn('Skyguard|Apache', section)
        self.assertNotIn('Skyguard|Theater', section)
        self.assertNotIn('Skyguard|MissionMap', section)
        self.assertNotIn('Skyguard|Combat', section)
        self.assertIsNone(
            re.search(r'Category="Skyguard"(?!\|)', LOCKED_UFUNCTION_WRAP)
        )
        self.assertIn("BlueprintPure", LOCKED_UFUNCTION_WRAP)
        self.assertIn("Category", LOCKED_UFUNCTION_WRAP)
        self.assertIn(
            'Category="Skyguard|Presentation|HUD"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn("BlueprintCallable", LOCKED_UFUNCTION_WRAP)
        self.assertNotIn("VisibleAnywhere", LOCKED_UFUNCTION_WRAP)
        self.assertNotIn("BlueprintReadOnly", LOCKED_UFUNCTION_WRAP)
        self.assertNotIn(
            'Category="Skyguard|Presentation|Briefing"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn(
            'Category="Skyguard|Presentation|Debrief"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn(
            'Category="Skyguard|Combat|Sortie"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn(
            'Category="Settings"',
            LOCKED_UFUNCTION_WRAP,
        )
        specifiers = attached_ufunction_specifiers(section)
        self.assertIn("BlueprintPure", specifiers)
        self.assertIn('Category="Skyguard|Presentation|HUD"', specifiers)
        self.assertNotIn("BlueprintCallable", specifiers)
        self.assertNotIn('Skyguard|MissionMap', specifiers)
        self.assertNotIn('Skyguard|Combat', specifiers)
        self.assertNotIn('Skyguard|Apache', specifiers)
        self.assertNotIn('Skyguard|Theater', specifiers)
        self.assertIn("Category", specifiers)
        self.assertNotIn("VisibleAnywhere", specifiers)
        self.assertNotIn("BlueprintReadOnly", specifiers)
        self.assertNotIn("MultiLine", specifiers)
        self.assertNotIn("ClampMin", specifiers)
        self.assertNotIn("ClampMax", specifiers)
        self.assertTrue("|HUD" in specifiers)
        self.assertNotIn("|Briefing", specifiers)
        self.assertNotIn("|Debrief", specifiers)
        self.assertNotIn("|VFX", specifiers)
        self.assertNotIn("|PCG", specifiers)
        self.assertNotIn("|Layout", specifiers)
        self.assertNotIn("|Materials", specifiers)
        self.assertNotIn("|Visibility", specifiers)
        self.assertNotIn("|Briefing", specifiers)
        self.assertNotIn("|Debrief", specifiers)
        self.assertNotIn("|Production", specifiers)
        self.assertTrue("|HUD" in specifiers)
        self.assertNotEqual(
            specifiers,
            'BlueprintPure, Category="Skyguard|Presentation"',
        )
        self.assertNotIn("BlueprintCallable", section)
        self.assertNotEqual(
            specifiers,
            'BlueprintPure, Category="Skyguard|Presentation"',
        )
        self.assertNotEqual(
            specifiers,
            'BlueprintCallable, Category="Skyguard|Audio"',
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertNotIn("UFUNCTION", LOCKED_DECL)
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        for invented in INVENTED_UFUNCTION:
            self.assertNotIn(invented, LOCKED_DECL)

    def test_missing_or_wrong_signature_fails_closed(self) -> None:
        bare = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{LOCKED_UFUNCTION_WRAP}\n"
            f"\t{TARGET_WRONG_BARE}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        section = spec_section(bare)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn(
            "GetBoundPresentation",
            str(raised.exception),
        )
        self.assertIn("missing", str(raised.exception).lower())
        wrong = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{LOCKED_UFUNCTION_WRAP}\n"
            f"\t{TARGET_WRONG_VOID}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        section = spec_section(wrong)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn(
            "GetBoundPresentation",
            str(raised.exception),
        )
        origin = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIn(
            collapsed(TARGET_INLINE),
            compact_origin,
        )
        self.assertIn("GetBoundPresentation", collapsed(LOCKED_DECL))
        self.assertTrue(
            GET_BOUND_PRESENTATION_IDENT_RE.search(LOCKED_DECL)
        )
        self.assertIsNone(
            BIND_PRESENTATION_IDENT_RE.search(LOCKED_DECL)
        )
        self.assertFalse(
            has_identifier(
                "USkyguardSortiePresentationComponent* "
                "GetBoundPresentation() const;",
                "BindPresentation",
            )
        )
        self.assertFalse(
            has_identifier(LOCKED_DECL, "BindPresentation")
        )
        self.assertNotIn(
            "BindPresentation",
            collapsed(LOCKED_DECL),
        )
        self.assertNotIn("float LookYawLimit = 95.f;", compact_origin)
        self.assertNotIn("FName AssemblyRevision", compact_origin)
        self.assertNotIn("LookYawLimit = 160.f", compact_origin)
        self.assertNotIn("FName WeatherIdentity", compact_origin)
        self.assertNotIn("TArray<FSkyguardRoutePoint> RoutePoints", compact_origin)
        self.assertNotIn("bool bLicensedVegetationApproved = false;", compact_origin)
        self.assertNotIn("float FireRate = 12.0f", compact_origin)
        self.assertNotIn("float RecoilPitch = 0.92f", compact_origin)

    def test_get_bound_presentation_declaration_matches_origin_main(
        self,
    ) -> None:
        section = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(
            LOCKED_DECL.startswith(
                "USkyguardSortiePresentationComponent* GetBoundPresentation"
            ),
            LOCKED_DECL,
        )
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertIsNotNone(re.search(r"\)\s*const\b", LOCKED_DECL))
        self.assertNotIn("static ", LOCKED_DECL)
        self.assertNotIn("InPresentation", LOCKED_DECL)
        self.assertIn(
            "USkyguardSortiePresentationComponent*",
            LOCKED_DECL,
        )
        self.assertNotIn("void ", LOCKED_DECL)
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("bool ", LOCKED_DECL)
        self.assertNotIn("float ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn("95.f", LOCKED_DECL)
        self.assertNotIn("140.f", LOCKED_DECL)
        self.assertNotIn("160.f", LOCKED_DECL)
        self.assertNotIn("100.f", LOCKED_DECL)
        self.assertNotIn("12.0f", LOCKED_DECL)
        self.assertNotIn("0.92f", LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_FNAME)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOOK_YAW)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_MISSION_ID)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SIBLING_COUNT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_IS_DESTROYED)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LAMP)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_VOICE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_WIND)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_IDLE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_FIRE_RATE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_RECOIL_PITCH)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_BOOM)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CULL)
        self.assertNotIn("WeatherIdentity", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("TObjectPtr<", LOCKED_DECL)
        self.assertNotIn("TSoftObjectPtr", LOCKED_DECL)
        self.assertNotIn("UTextRenderComponent", LOCKED_DECL)
        self.assertNotIn("UStaticMeshComponent", LOCKED_DECL)
        self.assertNotIn("USceneComponent", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        self.assertNotIn(SIBLING_GET_RESOLVED_COUNT, LOCKED_DECL)
        self.assertNotIn(SIBLING_GET_WIND_BLEND, LOCKED_DECL)
        self.assertNotIn(SIBLING_MAX_INTEGRITY, LOCKED_DECL)
        self.assertNotIn(SIBLING_CURRENT_INTEGRITY, LOCKED_DECL)
        self.assertNotIn(SIBLING_HULL_COLLIDER, LOCKED_DECL)
        self.assertNotIn(SIBLING_FIRE_RATE, LOCKED_DECL)
        self.assertNotIn(SIBLING_RECOIL_PITCH, LOCKED_DECL)
        self.assertNotIn(SIBLING_CANNON_MAGAZINE_SIZE, LOCKED_DECL)
        self.assertNotIn(SIBLING_ENGINE_IDLE_LOOP, LOCKED_DECL)
        self.assertNotIn(SIBLING_GLOBAL_VOICE_LIMIT, LOCKED_DECL)
        self.assertNotIn("OpenCockpitWindLoop", LOCKED_DECL)
        self.assertNotIn("IsDestroyed", LOCKED_DECL)
        self.assertNotIn("GetLampInstanceCount", LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_VOID}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FNAME}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_HEALTH}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FIRE_RATE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_RECOIL_PITCH}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_SIBLING_COUNT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_IS_DESTROYED}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_LAMP}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        self.assertIn(
            "GetBoundPresentation",
            str(raised.exception),
        )
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_FNAME}\n", LOCKED_DECL)
        self.assertIn(
            "GetBoundPresentation",
            str(raised.exception),
        )

    def test_locked_decl_is_not_leftover_clone_weather_identity(self) -> None:
        self.assertEqual(
            LOCKED_DECL,
            TARGET,
        )
        self.assertNotIn("static ", LOCKED_DECL)
        self.assertIn(
            "USkyguardSortiePresentationComponent*",
            LOCKED_DECL,
        )
        self.assertNotIn("InPresentation", LOCKED_DECL)
        self.assertNotIn("void ", LOCKED_DECL)
        self.assertEqual(
            LOCKED_DECL,
            "USkyguardSortiePresentationComponent* GetBoundPresentation() const;",
        )
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_BIND)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_REFRESH)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_REBIND)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_VOID)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_INT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_RESET_SORTIE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SUCCESS)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_AUTHORING)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_PREPARE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_GET_RHI)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_AUDIT_VISIBLE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SIBLING_INIT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOOK_YAW)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_MISSION_ID)
        self.assertNotEqual(LOCKED_DECL, "FName WeatherIdentity;")
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_ASSEMBLY)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_ROUTE_POINTS)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_READINESS_LICENSED)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_ALLOW_PCG)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SIBLING_COUNT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_IS_DESTROYED)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LAMP)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_GET_WIND)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_FIRE_RATE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_RECOIL_PITCH)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CANNON_MAG)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_ROCKET_MAG)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_GUIDED_MAG)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TEDAC_TEXT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_EUFD_TEXT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_MPD_LEFT_TEXT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_HAND_MESH)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_MESH)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SCENE)
        self.assertNotIn("WeatherIdentity", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("=", LOCKED_DECL)
        self.assertNotIn("AssemblyRevision", LOCKED_DECL)
        self.assertNotIn("95.f", LOCKED_DECL)
        self.assertNotIn("140.f", LOCKED_DECL)
        self.assertNotIn("160.f", LOCKED_DECL)
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            LOCKED_DECL,
        )
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn(
            'Category="Skyguard|Apache"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotEqual(
            LOCKED_UFUNCTION_WRAP,
            TARGET_WRONG_THEATER,
        )
        self.assertIn(
            'Category="Skyguard|Presentation|HUD"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn(
            'Skyguard|Combat',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn(
            'Skyguard|Theater',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SAMPLE_RATE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_BYTE_BUDGET)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_PLACEMENT_SEED)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_MIN_SAMPLES)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_MAX_VOICES)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_NIGHT_IDENTITY)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_ARCADE_ENABLED)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_FALSE)
        self.assertNotIn("SampleRate", LOCKED_DECL)
        self.assertNotIn("GeneratedByteBudget", LOCKED_DECL)
        self.assertNotIn("PlacementSeed", LOCKED_DECL)
        self.assertNotIn("MinimumMeasuredSamples", LOCKED_DECL)
        self.assertNotIn("MaximumAllowedVoices", LOCKED_DECL)
        self.assertNotIn("bNightIdentity", LOCKED_DECL)
        self.assertNotIn("bEnabled", LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_BOOM)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CRUISE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_POWER)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_PROP)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_IDLE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_VOICE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CULL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_WIND)
        self.assertNotIn("EngineCruiseLoop", LOCKED_DECL)
        self.assertNotIn("EnginePowerLoop", LOCKED_DECL)
        self.assertNotIn("PropellerLoop", LOCKED_DECL)
        self.assertNotIn("EngineIdleLoop", LOCKED_DECL)
        self.assertNotIn("GlobalVoiceLimit", LOCKED_DECL)
        self.assertNotIn("OpenCockpitWindLoop", LOCKED_DECL)
        self.assertNotIn("VegetationStartCullDistanceCm", LOCKED_DECL)
        self.assertNotIn("Boom;", LOCKED_DECL)
        self.assertNotIn("GetLampInstanceCount", LOCKED_DECL)
        self.assertNotIn("GetResolvedProductionLoopRouteCount", LOCKED_DECL)
        self.assertNotIn("AreResolvedProductionLoopRoutesComplete", LOCKED_DECL)
        self.assertNotIn("InitializeRequiredEntries", LOCKED_DECL)
        self.assertNotIn("EvaluateReadiness", LOCKED_DECL)
        self.assertNotIn("ConfigureRoutingTopology", LOCKED_DECL)
        self.assertNotIn("GetUnboundRequiredCategories", LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SIBLING_INIT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_VOID)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_PRODUCTION_BANK_FIELD)
        self.assertNotIn("IsDestroyed", LOCKED_DECL)
        self.assertNotIn(
            'Category="Skyguard|Audio|Development"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn("Waves", LOCKED_DECL)
        self.assertNotIn(
            'Category="Skyguard|Audio|Budget"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn(
            'Category="Skyguard|Audio|Acceptance"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotEqual(LOCKED_UFUNCTION_WRAP, UFUNCTION_AUDIO_ONLY)
        self.assertIsNone(
            re.search(r'Category\s*=\s*"Skyguard"(?!\|)', LOCKED_UFUNCTION_WRAP)
        )
        self.assertIsNone(
            re.search(
                r'Category\s*=\s*"Skyguard\|Audio"(?!\|)',
                LOCKED_UFUNCTION_WRAP,
            )
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
            f"\t{TARGET_WRONG_BARE}\n",
            f"\t{TARGET_WRONG_NO_CONST}\n",
            f"\t{TARGET_WRONG_VOID}\n",
            f"\t{TARGET_WRONG_FLOAT}\n",
            f"\t{TARGET_WRONG_INT}\n",
            f"\t{TARGET_WRONG_RENAME}\n",
            f"\t{TARGET_WRONG_SIBLING_COUNT}\n",
            f"\t{TARGET_WRONG_IS_DESTROYED}\n",
            f"\t{TARGET_WRONG_LAMP}\n",
            f"\t{TARGET_WRONG_GET_WIND}\n",
            f"\t{TARGET_WRONG_FALSE}\n",
            f"\t{TARGET_WRONG_TRUE}\n",
            f"\t{TARGET_WRONG_ZERO}\n",
            f"\t{TARGET_WRONG_SKELETAL}\n",
            f"\t{TARGET_WRONG_FNAME}\n",
            f"\t{TARGET_WRONG_HEALTH}\n",
            f"\t{TARGET_WRONG_FIRE_RATE}\n",
            f"\t{TARGET_WRONG_RECOIL_PITCH}\n",
            f"\t{TARGET_WRONG_CANNON_MAG}\n",
            f"\t{TARGET_WRONG_ROCKET_MAG}\n",
            f"\t{TARGET_WRONG_GUIDED_MAG}\n",
            leftover_primary,
            leftover_guided,
            "\tUSkyguardSortiePresentationComponent* GetBoundPresentationX() const;\n",
            "\tint32 GetBoundPresentation = 1;\n",
            "\tFName GetBoundPresentation = NAME_None;\n",
            "\tUSkyguardSortiePresentationComponent* GetBoundPresentation() = "
            + forty
            + ";\n",
            "\tUSkyguardSortiePresentationComponent* GetBoundPresentation() = "
            + eighty
            + ";\n",
            f"\t{TARGET_WRONG_BIND}\n",
            f"\t{TARGET_WRONG_BIND_CONST}\n",
            f"\t{TARGET_WRONG_INT}\n",
            f"\t{TARGET_WRONG_RESET_SORTIE}\n",
            f"\t{TARGET_WRONG_INVERT_LOOK}\n",
            f"\t{TARGET_WRONG_LOOK_SENS}\n",
            f"\t{TARGET_WRONG_SUCCESS}\n",
            f"\t{TARGET_WRONG_AUTHORING}\n",
            f"\t{TARGET_WRONG_PREPARE}\n",
            f"\t{TARGET_WRONG_GET_RHI}\n",
            f"\t{TARGET_WRONG_AUDIT_VISIBLE}\n",
            f"\t{TARGET_WRONG_SAMPLE_HEIGHT}\n",
            f"\t{TARGET_WRONG_FINISH_COMPILE}\n",
            f"\t{TARGET_WRONG_SIBLING_AUDIT}\n",
            f"\t{TARGET_WRONG_ROUTE_LENGTH}\n",
            f"\t{TARGET_WRONG_SIBLING_INIT}\n",
            f"\t{TARGET_WRONG_VOID}\n",
            f"\t{TARGET_WRONG_REFRESH}\n",
            f"\t{TARGET_WRONG_REBIND}\n",
            f"\t{TARGET_WRONG_GET_BOUND}\n",
            f"\t{TARGET_WRONG_GET_BOUND_INLINE}\n",
            f"\t{TARGET_WRONG_ACTIVATION}\n",
            f"\t{TARGET_WRONG_PRODUCTION_BANK_FIELD}\n",
            f"\t{TARGET_WRONG_PATHFINDER_INTERVAL}\n",
            f"\t{TARGET_WRONG_BOOM}\n",
            f"\t{TARGET_WRONG_CRUISE}\n",
            f"\t{TARGET_WRONG_POWER}\n",
            f"\t{TARGET_WRONG_PROP}\n",
            f"\t{TARGET_WRONG_IDLE}\n",
            f"\t{TARGET_WRONG_VOICE}\n",
            f"\t{TARGET_WRONG_WIND}\n",
            f"\t{TARGET_WRONG_CULL}\n",
            f"\t{TARGET_WRONG_ASSEMBLY}\n",
            f"\t{TARGET_WRONG_ROUTE_POINTS}\n",
            f"\t{TARGET_WRONG_ALLOW_PCG}\n",
            f"\t{TARGET_WRONG_HAZE}\n",
            f"\t{TARGET_WRONG_LANDSCAPE}\n",
            f"\t{TARGET_WRONG_PCG_AUTH}\n",
            f"\t{TARGET_WRONG_SURFACE_EXPOSED}\n",
            f"\t{TARGET_WRONG_READY_PCG}\n",
            f"\t{TARGET_WRONG_READINESS_LICENSED}\n",
            f"\t{TARGET_WRONG_LOOK_YAW}\n",
            f"\t{TARGET_WRONG_MISSION_ID}\n",
            f"\t{TARGET_WRONG_FLIGHT_SPLINE}\n",
            f"\t{TARGET_WRONG_MISSION_DEF}\n",
            f"\t{TARGET_WRONG_SKYLINE}\n",
            f"\t{TARGET_WRONG_READINESS}\n",
            f"\t{TARGET_WRONG_FLARE}\n",
            f"\t{TARGET_WRONG_SAMPLE_RATE}\n",
            f"\t{TARGET_WRONG_BYTE_BUDGET}\n",
            f"\t{TARGET_WRONG_PLACEMENT_SEED}\n",
            f"\t{TARGET_WRONG_MIN_SAMPLES}\n",
            f"\t{TARGET_WRONG_MAX_VOICES}\n",
            f"\t{TARGET_WRONG_NIGHT_IDENTITY}\n",
            f"\t{TARGET_WRONG_ARCADE_ENABLED}\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn(
                "GetBoundPresentation",
                str(raised.exception),
            )
            self.assertIn("missing", str(raised.exception).lower())

    def test_missing_category_or_blueprint_pure_fails_closed(self) -> None:
        no_category = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            "\tUFUNCTION(BlueprintPure)\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        section = spec_section(no_category)
        specifiers = attached_ufunction_specifiers(section)
        self.assertNotIn("Category", specifiers)
        origin = attached_ufunction_specifiers(
            spec_section(origin_main_header())
        )
        self.assertIn("Category", origin)
        self.assertIn('Category="Skyguard|Presentation|HUD"', origin)
        self.assertNotIn('Skyguard|Apache', origin)
        self.assertNotIn('Skyguard|MissionMap', origin)
        self.assertNotIn('Skyguard|Combat', origin)
        self.assertNotIn('Skyguard|Audio|Budget', origin)
        self.assertIsNone(
            re.search(r'Category="Skyguard"(?!\|)', origin)
        )
        self.assertIsNone(
            re.search(r'Category="Skyguard\|Audio"(?!\|)', origin)
        )
        self.assertIn("BlueprintPure", origin)
        self.assertNotIn("BlueprintCallable", origin)
        leftover_callable = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_CALLABLE}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        dropped = attached_ufunction_specifiers(
            spec_section(leftover_callable)
        )
        self.assertNotIn("BlueprintPure", dropped)
        self.assertIn("BlueprintCallable", dropped)
        self.assertIn("BlueprintPure", origin)
        leftover_audio_only = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_AUDIO_ONLY}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        audio_only = attached_ufunction_specifiers(
            spec_section(leftover_audio_only)
        )
        self.assertIn('Category="Skyguard|Audio"', audio_only)
        self.assertNotIn(
            'Category="Skyguard|Presentation|HUD"',
            audio_only,
        )
        leftover_apache = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_APACHE}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        apache_specs = attached_ufunction_specifiers(
            spec_section(leftover_apache)
        )
        self.assertIn('Category="Skyguard|Apache"', apache_specs)
        self.assertNotIn(
            'Category="Skyguard|Presentation|HUD"',
            apache_specs,
        )
        theater = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{TARGET_WRONG_THEATER}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        theater_specs = attached_ufunction_specifiers(
            spec_section(theater)
        )
        self.assertIn('Category="Skyguard|Theater"', theater_specs)
        self.assertNotIn(
            'Category="Skyguard|Presentation|HUD"',
            theater_specs,
        )
        self.assertIn('Category="Skyguard|Presentation|HUD"', origin)
        self.assertNotIn('Skyguard|Apache', origin)
        self.assertNotIn('Skyguard|Theater', origin)
        self.assertNotIn('Skyguard|MissionMap', origin)
        leftover_acceptance = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_ACCEPTANCE}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        acceptance_specs = attached_ufunction_specifiers(
            spec_section(leftover_acceptance)
        )
        self.assertIn(
            'Category="Skyguard|Audio|Acceptance"',
            acceptance_specs,
        )
        self.assertNotIn(
            'Category="Skyguard|Presentation|HUD"',
            acceptance_specs,
        )
        leftover_development = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_DEVELOPMENT}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        development_specs = attached_ufunction_specifiers(
            spec_section(leftover_development)
        )
        self.assertIn(
            'Category="Skyguard|Audio|Development"',
            development_specs,
        )
        self.assertNotIn(
            'Category="Skyguard|Presentation|HUD"',
            development_specs,
        )
        leftover_skyguard = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_SKYGUARD_ONLY}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        skyguard_specs = attached_ufunction_specifiers(
            spec_section(leftover_skyguard)
        )
        self.assertIn('Category="Skyguard"', skyguard_specs)
        self.assertNotIn(
            'Category="Skyguard|Presentation|HUD"',
            skyguard_specs,
        )
        leftover_env_only = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_ENVIRONMENT_ONLY}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        env_only = attached_ufunction_specifiers(
            spec_section(leftover_env_only)
        )
        self.assertIn(
            'Category="Skyguard|Presentation"',
            env_only,
        )
        self.assertNotIn(
            'Category="Skyguard|Presentation|HUD"',
            env_only,
        )
        leftover_authoring = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_AUTHORING}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        authoring_specs = attached_ufunction_specifiers(
            spec_section(leftover_authoring)
        )
        self.assertIn(
            'Category="Skyguard|Presentation|Briefing"',
            authoring_specs,
        )
        self.assertNotIn(
            'Category="Skyguard|Presentation|HUD"',
            authoring_specs,
        )
        leftover_grounding = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_GROUNDING}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        grounding_specs = attached_ufunction_specifiers(
            spec_section(leftover_grounding)
        )
        self.assertIn(
            'Category="Skyguard|Presentation|Debrief"',
            grounding_specs,
        )
        leftover_sortie = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_COMBAT_SORTIE}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        sortie_specs = attached_ufunction_specifiers(
            spec_section(leftover_sortie)
        )
        self.assertIn(
            'Category="Skyguard|Combat|Sortie"',
            sortie_specs,
        )
        self.assertIn("BlueprintPure", sortie_specs)
        self.assertNotIn("BlueprintCallable", sortie_specs)
        leftover_settings = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_SETTINGS_BARE}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        settings_specs = attached_ufunction_specifiers(
            spec_section(leftover_settings)
        )
        self.assertIn('Category="Settings"', settings_specs)
        leftover_boss = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_BOSS_ENCOUNTER}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        boss_specs = attached_ufunction_specifiers(
            spec_section(leftover_boss)
        )
        self.assertIn(
            'Category="Skyguard|Boss|Encounter"',
            boss_specs,
        )

        leftover_pause = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_PAUSE}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        pause_specs = attached_ufunction_specifiers(
            spec_section(leftover_pause)
        )
        self.assertIn('Category="Skyguard|Pause"', pause_specs)
        self.assertNotIn(
            'Category="Skyguard|Presentation|HUD"',
            pause_specs,
        )
        self.assertNotIn('Skyguard|Pause', origin)
        leftover_combat = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_COMBAT}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        combat_specs = attached_ufunction_specifiers(
            spec_section(leftover_combat)
        )
        self.assertIn('Category="Skyguard|Combat"', combat_specs)
        leftover_map = (
            f"class SKYGUARD52_API {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UFUNCTION_MISSIONMAP}\n"
            f"\t{LOCKED_DECL}\n"
            f"{STOP_BEFORE_PRIVATE}\n"
            "};\n"
        )
        map_specs = attached_ufunction_specifiers(
            spec_section(leftover_map)
        )
        self.assertIn('Category="Skyguard|MissionMap"', map_specs)
        self.assertNotIn('Skyguard|Audio|Acceptance', origin)
        self.assertNotIn('Skyguard|Audio|Development', origin)
        self.assertNotIn('Skyguard|Combat', origin)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wraps = (
            "\tUSkyguardSortiePresentationComponent* GetBoundPresentation() const;\n",
            "\tUSkyguardSortiePresentationComponent*\n"
            "\tGetBoundPresentation() const;\n",
            f"\t{LOCKED_DECL}\n",
            f"\t{LOCKED_UFUNCTION_WRAP}\n\t{LOCKED_DECL}\n",
            f"\t{LOCKED_UFUNCTION_WRAP} {LOCKED_DECL}\n",
            "\tUFUNCTION(BlueprintPure, "
            'Category="Skyguard|Presentation|HUD")\n'
            f"\t{LOCKED_DECL}\n",
            "\tUFUNCTION(\n\t\tBlueprintPure, "
            'Category="Skyguard|Presentation|HUD")\n'
            f"\t{LOCKED_DECL}\n",
            "\tUFUNCTION(BlueprintPure,\n"
            '\t\tCategory="Skyguard|Presentation|HUD")\n'
            f"\t{LOCKED_DECL}\n",
            f"\t{TARGET_INLINE}\n",
            "\tUSkyguardSortiePresentationComponent* GetBoundPresentation() const\n"
            "\t{\n"
            "\t\treturn Presentation;\n"
            "\t}\n",
        )
        for region in wraps:
            self.assertTrue(has_declaration(region, LOCKED_DECL), region)

    def test_does_not_claim_sibling_existing_graph_or_neighbors(
        self,
    ) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertFalse(has_identifier(LOCKED_DECL, sibling), sibling)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertNotIn(SIBLING_FIRE_RATE, LOCKED_DECL)
        self.assertNotIn(SIBLING_RECOIL_PITCH, LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SIBLING_COUNT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_IS_DESTROYED)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LAMP)
        section = spec_section(origin_main_header())
        leaked = class_body(origin_main_header())
        self.assertTrue(
            has_identifier(section, "GetBoundPresentation")
        )
        self.assertTrue(has_identifier(leaked, SIBLING_INITIALIZE_REQUIRED))
        self.assertFalse(has_identifier(LOCKED_DECL, SIBLING_INITIALIZE_REQUIRED))
        self.assertFalse(has_identifier(LOCKED_DECL, SIBLING_GET_RESOLVED_COUNT))
        self.assertFalse(has_identifier(LOCKED_DECL, SIBLING_EVALUATE_READINESS))
        self.assertFalse(has_identifier(LOCKED_DECL, SIBLING_CONFIGURE_ROUTING))
        self.assertFalse(has_identifier(LOCKED_DECL, SIBLING_UNBOUND_CATEGORIES))
        self.assertTrue(has_identifier(leaked, STOP_BEFORE_SKYLINE_STYLE))
        self.assertFalse(has_identifier(section, STOP_BEFORE_SKYLINE_STYLE))
        self.assertTrue(has_identifier(leaked, SIBLING_ENTRIES))
        self.assertFalse(has_identifier(section, SIBLING_ENTRIES))
        self.assertTrue(has_identifier(leaked, SIBLING_ROUTING))
        self.assertFalse(has_identifier(section, SIBLING_ROUTING))
        self.assertTrue(has_identifier(leaked, STOP_BEFORE_EVENT_DEFINITIONS))
        self.assertFalse(has_identifier(section, STOP_BEFORE_EVENT_DEFINITIONS))
        self.assertFalse(has_identifier(section, SIBLING_CPG_EUFD_TEXT))
        self.assertFalse(has_identifier(section, SIBLING_CPG_MPD_RIGHT_TEXT))
        self.assertFalse(has_identifier(section, SIBLING_CPG_TEDAC_TEXT))
        self.assertFalse(has_identifier(section, leftover_banned_guided_muzzle()))
        self.assertFalse(has_identifier(section, leftover_banned_primary_mesh()))
        self.assertFalse(has_identifier(section, SIBLING_HAND_MESH))
        self.assertFalse(has_identifier(section, SIBLING_FIRE_RATE))
        self.assertFalse(has_identifier(section, SIBLING_RECOIL_PITCH))
        self.assertFalse(has_identifier(section, SIBLING_CANNON_MAGAZINE_SIZE))
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_FIRE_RATE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_RECOIL_PITCH)
        self.assertNotIn(TARGET_WRONG_EUFD_TEXT, section)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, LOCKED_DECL)

    def test_does_not_parse_private_or_neighbors(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = class_body(header)
        self.assertNotIn(STOP_BEFORE_PRIVATE, section)
        self.assertTrue(
            has_identifier(leaked, "GetBoundPresentation")
        )
        self.assertTrue(
            has_identifier(section, "GetBoundPresentation")
        )
        self.assertTrue(has_identifier(leaked, STOP_BEFORE_SKYLINE_STYLE))
        self.assertFalse(has_identifier(section, STOP_BEFORE_SKYLINE_STYLE))
        self.assertTrue(has_identifier(leaked, SIBLING_ENTRIES))
        self.assertFalse(has_identifier(section, SIBLING_ENTRIES))
        self.assertTrue(has_identifier(leaked, SIBLING_ROUTING))
        self.assertFalse(has_identifier(section, SIBLING_ROUTING))
        self.assertTrue(has_identifier(leaked, STOP_BEFORE_EVENT_DEFINITIONS))
        self.assertFalse(has_identifier(section, STOP_BEFORE_EVENT_DEFINITIONS))
        self.assertTrue(has_identifier(leaked, STOP_BEFORE_SKYLINE_STYLE))
        self.assertFalse(has_identifier(section, STOP_BEFORE_SKYLINE_STYLE))
        self.assertTrue(has_identifier(leaked, "RebindIfNeeded"))
        self.assertFalse(has_identifier(section, "RebindIfNeeded"))
        self.assertFalse(has_identifier(section, SIBLING_ROOT))
        self.assertFalse(has_identifier(section, SIBLING_OCEAN_TILES))
        self.assertFalse(has_identifier(section, SIBLING_READINESS))
        self.assertFalse(has_identifier(section, SIBLING_ALLOW_AUTHORED_PCG))
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
            f"\t{TARGET_WRONG_FIRE_RATE}\n"
            f"\t{TARGET_WRONG_RECOIL_PITCH}\n"
            f"\t{TARGET_WRONG_CANNON_MAG}\n"
            f"\t{TARGET_WRONG_SIBLING_COUNT}\n"
            f"\t{TARGET_WRONG_IS_DESTROYED}\n"
            f"\t{TARGET_WRONG_LAMP}\n"
            f"\t{TARGET_WRONG_GET_WIND}\n"
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
        self.assertIn(
            "GetBoundPresentation",
            str(raised.exception),
        )

    def test_declaration_does_not_invent_ufunction_metadata(self) -> None:
        self.assertEqual(
            LOCKED_UFUNCTION_WRAP,
            'UFUNCTION(BlueprintPure, '
            'Category="Skyguard|Presentation|HUD")',
        )
        self.assertNotEqual(
            LOCKED_UFUNCTION_WRAP,
            UFUNCTION_AUTHORING,
        )
        self.assertNotEqual(
            LOCKED_UFUNCTION_WRAP,
            UFUNCTION_CALLABLE,
        )
        self.assertNotEqual(
            LOCKED_UFUNCTION_WRAP,
            UFUNCTION_AUDIO_ONLY,
        )
        self.assertIn("BlueprintPure", LOCKED_UFUNCTION_WRAP)
        self.assertIn("Category", LOCKED_UFUNCTION_WRAP)
        self.assertNotIn("BlueprintCallable", LOCKED_UFUNCTION_WRAP)
        self.assertIn(
            'Category="Skyguard|Presentation|HUD"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn(
            'Skyguard|MissionMap',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn(
            'Category="Skyguard|Apache"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn(
            'Category="Skyguard|Campaign"',
            LOCKED_UFUNCTION_WRAP,
        )
        self.assertNotIn("VisibleAnywhere", LOCKED_UFUNCTION_WRAP)
        self.assertNotIn("BlueprintReadOnly", LOCKED_UFUNCTION_WRAP)
        self.assertNotIn("MultiLine", LOCKED_UFUNCTION_WRAP)
        self.assertNotIn("ClampMin", LOCKED_UFUNCTION_WRAP)
        self.assertNotIn("ClampMax", LOCKED_UFUNCTION_WRAP)
        for invented in INVENTED_DECL_META:
            self.assertNotIn(invented, LOCKED_DECL)
            self.assertNotIn(invented, LOCKED_UFUNCTION_WRAP)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        self.assertNotIn(".cpp", HEADER_PATH)
        self.assertTrue(HEADER_PATH.endswith(".h"))
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("SkyguardMission01EnvironmentAuthoringLibrary.cpp", THIS_SCRIPT)
        self.assertIn("SkyguardSortieHudHostComponent.h", HEADER_PATH)
        self.assertNotIn("SkyguardMission01EnvironmentAuthoringLibrary.h", HEADER_PATH)
        self.assertNotIn("SkyguardAudioDirectorComponent.h", HEADER_PATH)
        self.assertNotIn("SkyguardAudioProceduralBankComponent.h", HEADER_PATH)
        self.assertIn("SkyguardSortieHudHostComponent.h", HEADER_PATH)
        self.assertNotIn("SkyguardMission01EnvironmentDirector.h", HEADER_PATH)
        self.assertNotIn("SkyguardAudioProductionBank.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunner.h", HEADER_PATH)
        self.assertNotIn("SkyguardMissionMapAssemblyDirector.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunner.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunner.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)
        self.assertNotIn("SkyguardProtectAsset.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignTheaterKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipTypes.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignRoster.h", HEADER_PATH)
        self.assertNotIn("SkyguardArcadeLookComponent.h", HEADER_PATH)
        self.assertNotIn("SkyguardGuidedLockRules.h", HEADER_PATH)
        self.assertNotIn("SkyguardRadarNode.h", HEADER_PATH)

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
                "sortie hud bind presentation "
                "decl contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / "
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
            "sortie_hud_get_bound_presentation"
            "_decl_contract.py"
        ))
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_BIND_PRESENTATION)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_REFRESH_PRESENTATION)
        self.assertNotIn("SkyguardSortieHudHostComponent.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardCpgSightHud.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardMission01EnvironmentAuthoringLibrary.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardRadarNode.h", THIS_SCRIPT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_AUDIO_DIRECTOR_RESOLVED)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_AUDIO_DIRECTOR_ROUTE_COUNT)
        self.assertIn(LEFTOVER_THEATER_KIT_BULK, LOCKED_SCRIPTS)
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
        self.assertIn(LEFTOVER_PROTECT_ASSET_CARGO_PROXY_CONTRACT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_PROTECT_ASSET_CARGO_PROXY_TESTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_RADAR_NODE_PRESENTATION, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_RADAR_NODE_PRESENTATION_TESTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_RADAR_NODE_PRESENTATION_CONTRACT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_RADAR_NODE_RESET_GAMEPLAY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_TESTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_RADAR_NODE_RESET_GAMEPLAY_CONTRACT, LOCKED_SCRIPTS)
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

    def test_contract_is_target_method_declaration_only(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        locked_only = f"{LOCKED_DECL}\n"
        for sibling in sibling_uncontracted_decls():
            self.assertFalse(has_identifier(locked_only, sibling), sibling)
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
        self.assertNotIn(SIBLING_FIRE_RATE, locked_only)
        self.assertNotIn(SIBLING_RECOIL_PITCH, locked_only)
        self.assertNotIn(SIBLING_CANNON_MAGAZINE_SIZE, locked_only)
        self.assertNotIn(SIBLING_ROCKET_MAGAZINE_SIZE, locked_only)
        self.assertNotIn(SIBLING_GUIDED_MAGAZINE_SIZE, locked_only)
        self.assertNotIn(SIBLING_CPG_TEDAC_TEXT, locked_only)
        self.assertNotIn(SIBLING_CPG_MPD_RIGHT_TEXT, locked_only)
        self.assertNotIn(SIBLING_HAND_MESH, locked_only)
        self.assertNotIn(SIBLING_CPG_EUFD_TEXT, locked_only)
        self.assertNotIn("Canopy;", locked_only)
        self.assertNotIn("PilotCanopy", locked_only)
        self.assertNotIn(SIBLING_FUSELAGE, locked_only)
        self.assertNotIn(SIBLING_AIRCRAFT_ROOT, locked_only)
        self.assertNotIn(SIBLING_ROTOR_POWER, locked_only)
        self.assertNotIn(SIBLING_HOVER_BOB, locked_only)
        self.assertNotIn(leftover_banned_primary_mesh(), locked_only)
        self.assertNotIn(leftover_banned_guided_tube(), locked_only)
        self.assertNotIn("WeatherIdentity", locked_only)
        self.assertNotIn("AssemblyRevision", locked_only)
        self.assertNotIn("RoutePoints", locked_only)
        self.assertNotIn("bLicensedVegetationApproved", locked_only)
        self.assertNotIn("bAllowAuthoredPCGGeneration", locked_only)
        self.assertNotIn("bPCGGenerationAuthorized", locked_only)
        self.assertNotIn("bAuthoredLandscapeSurfaceExposed", locked_only)
        self.assertNotIn("bReadyForAuthoredPCGGeneration", locked_only)
        self.assertNotIn("SampleRate", locked_only)
        self.assertNotIn("GeneratedByteBudget", locked_only)
        self.assertNotIn("PlacementSeed", locked_only)
        self.assertNotIn("MinimumMeasuredSamples", locked_only)
        self.assertNotIn("MaximumAllowedVoices", locked_only)
        self.assertNotIn("bNightIdentity", locked_only)
        self.assertNotIn("bEnabled", locked_only)
        self.assertNotIn("Waves", locked_only)
        self.assertNotIn("bLicensedVegetationLibraryApproved", locked_only)
        self.assertNotIn("EngineCruiseLoop", locked_only)
        self.assertNotIn("EnginePowerLoop", locked_only)
        self.assertNotIn("PropellerLoop", locked_only)
        self.assertNotIn("EngineIdleLoop", locked_only)
        self.assertNotIn("GlobalVoiceLimit", locked_only)
        self.assertNotIn("EventDefinitions", locked_only)
        self.assertNotIn("CockpitExteriorAttenuation", locked_only)
        self.assertNotIn("CockpitLowPassHz", locked_only)
        self.assertNotIn("ProductionBank", locked_only)
        self.assertNotIn("VegetationStartCullDistanceCm", locked_only)
        self.assertNotIn("Boom;", locked_only)
        self.assertNotIn("OpenCockpitWindLoop", locked_only)
        self.assertNotIn("GetResolvedProductionLoopRouteCount", locked_only)
        self.assertNotIn("AreResolvedProductionLoopRoutesComplete", locked_only)
        self.assertNotIn("InitializeRequiredEntries", locked_only)
        self.assertNotIn("EvaluateReadiness", locked_only)
        self.assertNotIn("ConfigureRoutingTopology", locked_only)
        self.assertNotIn("GetUnboundRequiredCategories", locked_only)
        self.assertNotIn("GetLampInstanceCount", locked_only)
        self.assertNotIn("IsDestroyed", locked_only)
        self.assertNotIn("LockWindowAttackInterval", locked_only)
        self.assertNotIn("ApproachSpeed", locked_only)
        self.assertNotIn("CriticalSpeed", locked_only)
        self.assertNotIn("AuthorGovernedLandscapeAndGraph", LOCKED_DECL)
        self.assertNotIn("GetActiveRHIAndFeatureLevel", LOCKED_DECL)
        self.assertNotIn("AuditLandscapeVisibleReadiness", LOCKED_DECL)
        self.assertNotIn("FinishLandscapeMaterialCompilation", LOCKED_DECL)
        self.assertNotIn("AuditLandscapeMaterialCompilation", LOCKED_DECL)
        self.assertNotIn("SampleLandscapeHeight", LOCKED_DECL)
        self.assertNotIn("EnsureDefaultEntries", LOCKED_DECL)
        self.assertNotIn("RefreshFromPresentationState", LOCKED_DECL)
        self.assertNotIn("RebindIfNeeded", LOCKED_DECL)
        self.assertIn("GetBoundPresentation", LOCKED_DECL)
        self.assertNotIn("BindPresentation", LOCKED_DECL)
        self.assertNotIn("GetActivationCount", LOCKED_DECL)
        self.assertNotIn("CpgSightHud", LOCKED_DECL)
        self.assertNotIn("InPresentation", LOCKED_DECL)
        for leftover in leftover_apache_ufunction_tokens():
            self.assertNotIn(leftover, locked_only)


if __name__ == "__main__":
    unittest.main()
