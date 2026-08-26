from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission02IntegrationDirector.h"
CLASS_NAME = "ASkyguardMission02IntegrationDirector"
# Declaration presence only. Do not invent
# INDEX_NONE or lock ConfigureMissionDefinition
# construction in the .cpp. This is leftover-safe
# Mission02 Integration ConfigureMissionDefinition
# METHOD on ASkyguardMission02IntegrationDirector.
# It is NOT leftover Mission10
# ConfigureMissionDefinition / branch
# cursor/mission10-configure-mission-definition-
# decl-contract-c332, NOT leftover Mission09
# ConfigureMissionDefinition #750 / branch
# cursor/mission09-configure-mission-definition-
# decl-contract-c332, NOT leftover Mission08
# ConfigureMissionDefinition #730 / branch
# cursor/mission08-configure-mission-definition-
# decl-contract-c332, NOT leftover Mission05
# ConfigureMissionDefinition #665, NOT leftover
# Mission07 / Mission06 / Mission04 / Mission03 /
# Mission01 ConfigureMissionDefinition, NOT leftover
# Mission02 InitializePlayableMission sibling /
# branch cursor/mission02-initialize-playable-
# mission-decl-contract-c332, NOT leftover merged
# Mission02 C++ bundle #102 /
# cursor/m02-director-api-tests-1c8b, NOT leftover
# BindRuntimeActors, NOT leftover retired-mount spawn
# fields, NOT leftover HandleDroneCityImpact, NOT
# leftover Harbor #6/#8/#9, NOT
# leftover Mission07 wave-state enum #74d8, NOT
# leftover Mission07 protected-target enum #18f2,
# NOT leftover Mission07 protected-target-runtime
# defaults #866c, NOT leftover search-sector enum
# #b4d4, NOT leftover search-track-runtime-defaults
# #8266, NOT leftover GetNightBeatKit /
# GetNightBeatKind / GetNightBeatIndex /
# TickNightBeatKit without UFUNCTION, NOT leftover
# Mission06 wave-state enum #fa65, NOT leftover
# airfield-target enum #14d2, NOT leftover
# airfield-target-runtime-defaults #6ad8, NOT
# leftover payload-window-runtime-defaults #f114,
# and NOT leftover HandleBossPhaseChanged without
# Blueprint category. Distinct from leftover
# briefing-widget / MissionBriefingComponent
# methods.
# not leftover Briefing / AudioDirector / Root /
# RadioChatter / SortiePresentation /
# CampaignDefinition / MissionDefinition /
# Readiness / bAutoInitialize /
# bAllowBoundedActorSpawning /
# bAutoLaunchAfterBriefing sibling director fields.
# Do not lock leftover spawn-location fields on
# this class. Do not lock leftover GetAircraft.
# Do not lock leftover BindRuntimeActors. Do not
# lock leftover HandleDroneCityImpact. Do not
# lock leftover HandleBossPhaseChanged. Do not
# lock leftover Mission10 route-phase enum #701a /
# leftover Mission10 protected-group enum #6f9d /
# leftover Mission10 protected-runtime-defaults
# #7898. Do not lock leftover GetDayBeatKit / GetDayBeatKind /
# GetDayBeatIndex / TickDayBeatKit without
# UFUNCTION. Do not lock sibling Integration /
# Waves / Payload / Targets / Objectives methods
# InitializePlayableMission /
# BindRuntimeActors / StartNextWave /
# NotifyThreatDestroyed / StartPayloadWindow /
# AdvancePayloadWindow / TryJamActivePayload /
# NotifyAirfieldTargetDamage /
# NotifyProtectedAssetFailed /
# HandleDroneCityImpact /
# SynchronizeRuntimeState / IsCorePlayableReady /
# GetReadiness / GetObjectiveRuntime /
# GetWaveState / GetRemainingThreatsInWave /
# GetPayloadWindow / GetTargetRuntime /
# GetSurvivingTargetCount /
# GetMissionId / ValidateMissionContract. Do not
# lock leftover Mission01
# GetGunner / GetPathfinder. Do not lock leftover
# MissionBriefingComponent methods
# ConfigureFromMission / AdvanceBriefing /
# SetAssetsReady / AcknowledgeAndLaunch / CanLaunch /
# GetElapsedSeconds / GetBriefingState /
# GetMinimumWarmupSeconds / GetBriefingText /
# GetRadioChatter. Do not lock leftover
# briefing-widget GetPresentation / Configure /
# GetMissionTitle / GetBriefingText /
# AcknowledgeBriefing / LaunchSortie. Stay off
# leftover briefing-widget isolated contracts,
# leftover MissionBriefingComponent method decl
# contracts, leftover Harbor #6/#8/#9, leftover
# Harbor Mission02, leftover theater-kit #59,
# leftover audio-director fail-closed contracts,
# leftover radio-chatter fail-closed contracts,
# leftover campaign-definition method contracts,
# leftover Mission01 ConfigureMissionDefinition,
# leftover Mission03 ConfigureMissionDefinition #629,
# leftover Mission04 ConfigureMissionDefinition #650,
# leftover Mission05 ConfigureMissionDefinition #665,
# leftover Mission10 ConfigureMissionDefinition,
# leftover Mission05 InitializePlayableMission #666,
# leftover Mission05 GetSurvivingTargetCount,
# leftover Mission04 wave-state enum #bb22,
# leftover Mission06 wave-state enum #fa65,
# leftover airfield-target enum #14d2, leftover
# airfield-target-runtime-defaults #6ad8, leftover
# payload-window-runtime-defaults #f114, leftover
# searchlight-track-runtime-defaults #7347
# (do not lock GetSearchlightRuntime).
# origin/main is a one-line method
# (`bool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission);`); accept that
# form, other one-line / split-line wraps, and an
# inline body without locking the body.
# Nearby origin/main
# UFUNCTION(BlueprintCallable,
# Category="Skyguard|Mission02|Integration")
# is required as present. Accept one-line and
# split-line UFUNCTION wraps. Parse the public
# class section of
# ASkyguardMission02IntegrationDirector only.
# Category is Skyguard|Mission02|Integration, not
# Mission01 / Mission10 / Mission03 / Mission04 /
# Mission05 / Mission06 / Mission07 / Waves / Search /
# Protection / Payload / Targets / Objectives /
# Hoist / Safety / Rescue / Boss / Destruction /
# Briefing, not Environment,
# not leftover briefing-widget, not leftover
# MissionBriefingComponent methods, not leftover
# Mission01 Integration, not leftover Mission03
# Integration, not leftover Mission04 Integration,
# not leftover Mission05 Integration #666, not
# leftover Mission06 Integration #685, not leftover
# Mission07 Integration, not leftover Harbor
# Mission02 Integration, not leftover Mission08
# Integration #729, not leftover Mission08
# Waves / Hoist / Safety / Protection, not leftover
# Mission09 Waves / Protection / Performance,
# not leftover Mission10 Waves / Safety /
# Protection / Objectives / Evacuation / Campaign.
# Stay off leftover drafts #56–#64, leftover Harbor
# #6/#8/#9, leftover theater-kit #59, leftover
# isolated-test drafts #107–#673, leftover #664,
# closed leftover drafts #658–#673, leftover open
# drafts #674–#767+, leftover Apache
# MaxIntegrity / CurrentIntegrity, leftover Apache
# mount getters #851b / own-ship #96c5 / chin muzzle
# #4e39, leftover settings-apply-broadcast #1268,
# leftover patrol-ship empty fail-closed #5382,
# leftover RadarNode, leftover named boss methods,
# leftover LifelineHunter OpticalTracker / WeaponServo
# / CountermeasurePod / Engine fields, leftover
# briefing / debrief widget isolated contracts,
# leftover briefing-card / briefing-radio-row
# defaults, leftover briefing fail-closed tests,
# leftover environment-readiness defaults #6b9d /
# #b931, leftover skyline style HarborIndustrial
# (leftover enum, not a Harbor 40/80 retune).
# Harbor interval retune tokens fail closed in this
# file and the locked declaration only. Do not scan
# Apache public section for those tokens. Incoming
# clock names must be absent from the
# Mission10IntegrationDirector public section. Pathfinder MinHeightFromOriginCm
# is the wrong header, not Harbor 40/80. LastFlight
# MinimumCivilianSeparationMeters = 550.f is
# Harbor-adjacent; do not treat as Harbor 40/80.
# LifelineHunter MinimumWeaponSeparationMeters =
# 450.f is Harbor-adjacent. Do not lock leftover
# ESkyguardMission02WaveState while leftover Harbor
# #6/#8/#9 remain open. Skip leftover #664
# cloud-env install. Do not reopen leftover
# drafts #536–#673. Do not reopen leftover
# #668/#669. Do not reopen closed-without-merge
# #658–#673. Do not reopen leftover Mission08
# InitializePlayableMission #729. Do not reopen
# leftover Mission09 InitializePlayableMission
# #751. Do not reopen leftover Mission10 route-
# phase enum #701a, leftover Mission10 protected-
# group enum #6f9d, leftover Mission10 protected-
# runtime-defaults #7898. Do not reopen
# leftover Mission09 wave-state enum #20fc / #238,
# leftover Mission09 protected-target enum #9246 /
# #228, leftover Mission09 protected-target-runtime
# defaults #bf28 / #225, leftover Mission09 pool-
# runtime-defaults #5426 / #243, leftover Mission09
# pool-budget-defaults #4537 / #242. Do not reopen
# open drafts #674–#767+.
INITIALIZE_PLAYABLE_MISSION = "bool InitializePlayableMission();"
UFUNCTION_INTEGRATION = (
    "UFUNCTION(BlueprintCallable, "
    'Category="Skyguard|Mission02|Integration")'
)
ROOT_FIELD = "TObjectPtr<USceneComponent> Root;"
BRIEFING_FIELD = (
    "TObjectPtr<USkyguardMissionBriefingComponent> Briefing;"
)
AUDIO_DIRECTOR_FIELD = (
    "TObjectPtr<USkyguardAudioDirectorComponent> AudioDirector;"
)
RADIO_CHATTER_FIELD = (
    "TObjectPtr<USkyguardRadioChatterComponent> RadioChatter;"
)
SORTIE_PRESENTATION_FIELD = (
    "TObjectPtr<USkyguardSortiePresentationComponent> "
    "SortiePresentation;"
)
CAMPAIGN_DEFINITION_FIELD = (
    "TSoftObjectPtr<USkyguardCampaignDefinition> "
    "CampaignDefinition;"
)
MISSION_DEFINITION_FIELD = (
    "TSoftObjectPtr<USkyguardMissionDefinition> "
    "MissionDefinition;"
)
READINESS_FIELD = (
    "FSkyguardMission02IntegrationReadiness Readiness;"
)
AUTO_INITIALIZE_FIELD = "bool bAutoInitialize = true;"
ALLOW_BOUNDED_SPAWNING_FIELD = (
    "bool bAllowBoundedActorSpawning = true;"
)
AUTO_LAUNCH_AFTER_BRIEFING_FIELD = (
    "bool bAutoLaunchAfterBriefing = true;"
)
PATHFINDER_SPAWN_LOCATION = "FVector PathfinderSpawnLocation;"
PATHFINDER_SPAWN_ROTATION = "FRotator PathfinderSpawnRotation;"
CONFIGURE_MISSION_DEFINITION = (
    "bool ConfigureMissionDefinition("
    "USkyguardMissionDefinition* Mission);"
)
NOTIFY_OBJECTIVE_PROGRESS = (
    "bool NotifyObjectiveProgress(FName ObjectiveId, int32 Amount = 1);"
)
NOTIFY_PROTECTED_ASSET_FAILED = "bool NotifyProtectedAssetFailed();"
HANDLE_DRONE_CITY_IMPACT = (
    "void HandleDroneCityImpact(ASkyguardDrone* Drone);"
)
BIND_CAMPAIGN_RUNTIME = (
    "bool BindCampaignRuntime("
    "USkyguardCampaignSubsystem* InCampaignRuntime);"
)
GET_POOL_RUNTIME = (
    "const FSkyguardMission09PoolRuntime& "
    "GetPoolRuntime() const"
)
GET_MISSION09_PROTECTED_TARGET = (
    "FSkyguardMission09ProtectedTargetRuntime GetProtectedTarget("
    "ESkyguardMission09ProtectedTarget Target) const;"
)
GET_MISSION09_WAVE_STATE = (
    "ESkyguardMission09WaveState GetWaveState() const"
)
IRON_RAIN_SPAWN_LOCATION = (
    "FVector IronRainSpawnLocation ="
)
NOTIFY_FUEL_TERMINAL_DAMAGE = (
    "bool NotifyFuelTerminalDamage(int32 Damage);"
)
GET_CURRENT_WAVE_INDEX = (
    "int32 GetCurrentWaveIndex() const { return CurrentWaveIndex; }"
)
GET_FUEL_TERMINAL_INTEGRITY = (
    "int32 GetFuelTerminalIntegrity() const { return FuelTerminalIntegrity; }"
)
GET_BREAKWATER = (
    "ASkyguardBreakwaterBoss* GetBreakwater() const { return Breakwater; }"
)
START_NEXT_WAVE = "bool StartNextWave();"
NOTIFY_THREAT_DESTROYED = (
    "bool NotifyThreatDestroyed(int32 Amount = 1);"
)
ADVANCE_CONVOY_BY_DISTANCE = (
    "bool AdvanceConvoyByDistance(float DistanceCentimeters);"
)
NOTIFY_CONVOY_DAMAGE = "bool NotifyConvoyDamage(int32 Damage);"
GET_WAVE_STATE = (
    "ESkyguardMission07WaveState GetWaveState() const"
)
GET_CONVOY_ROUTE_STATE = (
    "ESkyguardConvoyRouteState GetConvoyRouteState() const"
)
GET_DAY_BEAT_KIT = (
    "const FSkyguardDaySortieBeatKit& GetDayBeatKit() const;"
)
GET_NIGHT_BEAT_KIT = (
    "const FSkyguardNightSortieBeatKit& GetNightBeatKit() const;"
)
GET_NIGHT_BEAT_KIND = (
    "ESkyguardNightSortieBeatKind GetNightBeatKind() const;"
)
GET_NIGHT_BEAT_INDEX = (
    "int32 GetNightBeatIndex() const { return NightBeatIndex; }"
)
TICK_NIGHT_BEAT_KIT = "void TickNightBeatKit(float DeltaSeconds);"
CLASSIFY_FALSE_TRACK = "bool ClassifyFalseTrack(FName TrackId);"
CONFIRM_RADAR_GHOST_IDENTIFICATION = (
    "bool ConfirmRadarGhostIdentification("
    "bool bExhaustObserved, "
    "bool bShadowObserved, "
    "bool bEngineSoundObserved);"
)
NOTIFY_PROTECTED_TARGET_DAMAGE = (
    "bool NotifyProtectedTargetDamage("
    "ESkyguardMission07ProtectedTarget Target, "
    "int32 Damage);"
)
ADVANCE_REINFORCEMENT_TIMER = (
    "bool AdvanceReinforcementTimer(float DeltaSeconds);"
)
GET_SEARCH_SECTOR = (
    "ESkyguardSearchSector GetSearchSector() const { return SearchSector; }"
)
GET_CLASSIFIED_FALSE_TRACK_COUNT = (
    "int32 GetClassifiedFalseTrackCount() const;"
)
IS_HOSTILE_CONTACT_CONFIRMED = (
    "bool IsHostileContactConfirmed() const "
    "{ return bHostileContactConfirmed; }"
)
GET_PROTECTED_TARGET = (
    "FSkyguardMission07ProtectedTargetRuntime GetProtectedTarget("
    "ESkyguardMission07ProtectedTarget Target) const;"
)
GET_REINFORCEMENT_TIME_REMAINING = (
    "float GetReinforcementTimeRemaining() const"
)
RADAR_GHOST_SPAWN_LOCATION = "FVector RadarGhostSpawnLocation;"
RADAR_GHOST_SPAWN_ROTATION = "FRotator RadarGhostSpawnRotation;"

START_PAYLOAD_WINDOW = (
    "bool StartPayloadWindow("
    "ESkyguardAirfieldTarget Target, "
    "float WindowSeconds);"
)
ADVANCE_PAYLOAD_WINDOW = "bool AdvancePayloadWindow(float DeltaSeconds);"
TRY_JAM_ACTIVE_PAYLOAD = "bool TryJamActivePayload();"
NOTIFY_AIRFIELD_TARGET_DAMAGE = (
    "bool NotifyAirfieldTargetDamage("
    "ESkyguardAirfieldTarget Target, "
    "int32 Damage);"
)
GET_PAYLOAD_WINDOW = (
    "const FSkyguardPayloadWindowRuntime& "
    "GetPayloadWindow() const"
)
GET_TARGET_RUNTIME = (
    "FSkyguardAirfieldTargetRuntime GetTargetRuntime("
    "ESkyguardAirfieldTarget Target) const;"
)
GET_SURVIVING_TARGET_COUNT = "int32 GetSurvivingTargetCount() const;"
GET_DAY_BEAT_KIND = "ESkyguardDaySortieBeatKind GetDayBeatKind() const;"
GET_DAY_BEAT_INDEX = (
    "int32 GetDayBeatIndex() const { return DayBeatIndex; }"
)
TICK_DAY_BEAT_KIT = "void TickDayBeatKit(float DeltaSeconds);"
HANDLE_BOSS_PHASE_CHANGED = (
    "void HandleBossPhaseChanged("
    "ESkyguardBossPhase PreviousPhase, "
    "ESkyguardBossPhase NewPhase);"
)
START_SEARCHLIGHT_WINDOW = (
    "bool StartSearchlightWindow(float WindowSeconds);"
)
ADVANCE_SEARCHLIGHT_TRACK = (
    "bool AdvanceSearchlightTrack(float DeltaSeconds, bool bBossInTrack);"
)
NOTIFY_SUBSTATION_DAMAGE = "bool NotifySubstationDamage(int32 Damage);"
GET_REMAINING_THREATS_IN_WAVE = (
    "int32 GetRemainingThreatsInWave() const { return RemainingThreatsInWave; }"
)
GET_SEARCHLIGHT_RUNTIME = (
    "const FSkyguardSearchlightTrackRuntime& "
    "GetSearchlightRuntime() const"
)
GET_SUBSTATION_INTEGRITY = (
    "int32 GetSubstationIntegrity() const { return SubstationIntegrity; }"
)
BLACK_KITE_SPAWN_LOCATION = "FVector BlackKiteSpawnLocation;"
BLACK_KITE_SPAWN_ROTATION = "FRotator BlackKiteSpawnRotation;"
SEARCHLIGHT_PORT_FIELD = (
    "TObjectPtr<USpotLightComponent> SearchlightPort;"
)
SEARCHLIGHT_STARBOARD_FIELD = (
    "TObjectPtr<USpotLightComponent> SearchlightStarboard;"
)
CONVOY_RUNTIME_ANCHOR = (
    "TObjectPtr<USceneComponent> ConvoyRuntimeAnchor;"
)
ROAD_HUNTER_SPAWN_LOCATION = "FVector RoadHunterSpawnLocation;"
ROAD_HUNTER_SPAWN_ROTATION = "FRotator RoadHunterSpawnRotation;"
SYNCHRONIZE_RUNTIME_STATE = "void SynchronizeRuntimeState();"
IS_CORE_PLAYABLE_READY = "bool IsCorePlayableReady() const;"
GET_READINESS = (
    "const FSkyguardMission02IntegrationReadiness& "
    "GetReadiness() const"
)
GET_OBJECTIVE_RUNTIME = (
    "USkyguardObjectiveRuntime* GetObjectiveRuntime() const;"
)
GET_GUNNER = "ASkyguardGunner* GetGunner() const { return Gunner; }"
GET_PATHFINDER = (
    "ASkyguardPathfinderBoss* GetPathfinder() const "
    "{ return Pathfinder; }"
)
GET_MISSION_ID = (
    "static FName GetMissionId() "
    '{ return TEXT("M07_SearchIntercept"); }'
)
VALIDATE_MISSION_CONTRACT = "static bool ValidateMissionContract("
BIND_RUNTIME_ACTORS = "BindRuntimeActors"
GET_AIRCRAFT = "GetAircraft"
START_HOIST_WINDOW = "bool StartHoistWindow(float WindowSeconds);"
ADVANCE_HOIST_WINDOW = (
    "bool AdvanceHoistWindow(float DeltaSeconds, bool bCoverMaintained);"
)
VALIDATE_WEAPON_RELEASE = (
    "bool ValidateWeaponRelease("
    "float FriendlySeparationMeters, "
    "bool bShotIntersectsFriendlyCorridor);"
)
GET_HOIST_RUNTIME = (
    "const FSkyguardHoistWindowRuntime& "
    "GetHoistRuntime() const"
)
GET_REJECTED_WEAPON_RELEASES = (
    "int32 GetRejectedWeaponReleases() const"
)
GET_STORM_RAIN_BEAT_KIT = (
    "static const FSkyguardStormRainBeatKit& GetStormRainBeatKit();"
)
APPLY_STORM_RAIN_PLAY_CONTRACT = (
    "bool ApplyStormRainPlayContract(ASkyguardGunner* InGunner) const;"
)
GET_STORM_RAIN_BEAT_KIND = (
    "ESkyguardStormRainBeatKind GetStormRainBeatKind() const;"
)
TICK_STORM_RAIN_BEAT_KIT = "void TickStormRainBeatKit(float ElapsedSeconds);"
LIFELINE_HUNTER_SPAWN_LOCATION = "FVector LifelineHunterSpawnLocation;"
LIFELINE_HUNTER_SPAWN_ROTATION = "FRotator LifelineHunterSpawnRotation;"
RESCUE_HELICOPTER_ANCHOR = (
    "TObjectPtr<USceneComponent> RescueHelicopterAnchor;"
)
HOIST_CABLE_ANCHOR = "TObjectPtr<USceneComponent> HoistCableAnchor;"
SURVIVORS_ANCHOR = "TObjectPtr<USceneComponent> SurvivorsAnchor;"
RAFTS_ANCHOR = "TObjectPtr<USceneComponent> RaftsAnchor;"
RESCUE_VESSEL_ANCHOR = "TObjectPtr<USceneComponent> RescueVesselAnchor;"
CONFIGURE_FROM_MISSION = (
    "bool ConfigureFromMission(USkyguardMissionDefinition* Mission);"
)
ADVANCE_BRIEFING = "void AdvanceBriefing(float DeltaSeconds);"
SET_ASSETS_READY = "void SetAssetsReady(bool bReady);"
ACKNOWLEDGE_AND_LAUNCH = "bool AcknowledgeAndLaunch();"
CAN_LAUNCH = "bool CanLaunch() const;"
GET_ELAPSED_SECONDS = (
    "float GetElapsedSeconds() const { return ElapsedSeconds; }"
)
GET_BRIEFING_STATE = (
    "ESkyguardMissionBriefingState GetBriefingState() const "
    "{ return State; }"
)
GET_MINIMUM_WARMUP_SECONDS = (
    "float GetMinimumWarmupSeconds() const "
    "{ return MinimumWarmupSeconds; }"
)
GET_BRIEFING_TEXT = (
    "FText GetBriefingText() const { return BriefingText; }"
)
GET_RADIO_CHATTER = (
    "TArray<FText> GetRadioChatter() const { return RadioChatter; }"
)
WIDGET_CONFIGURE = (
    "void Configure(USkyguardSortiePresentationComponent* "
    "InPresentation);"
)
WIDGET_GET_PRESENTATION = (
    "USkyguardSortiePresentationComponent* GetPresentation() const"
)
WIDGET_GET_MISSION_TITLE = "FText GetMissionTitle() const;"
WIDGET_GET_BRIEFING_TEXT = "FText GetBriefingText() const;"
WIDGET_ACKNOWLEDGE_BRIEFING = "bool AcknowledgeBriefing();"
WIDGET_LAUNCH_SORTIE = "bool LaunchSortie();"
HULL_COLLIDER_FIELD = "TObjectPtr<UBoxComponent> HullCollider;"
OPTICAL_TRACKER_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> OpticalTracker;"
)
WEAPON_SERVO_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> WeaponServo;"
)
COUNTERMEASURE_POD_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> CountermeasurePod;"
)
ENGINE_FIELD = (
    "TObjectPtr<USkyguardBossWeakPointComponent> Engine;"
)
MINIMUM_WEAPON_SEPARATION_FIELD = (
    "float MinimumWeaponSeparationMeters = 450.f;"
)
MINIMUM_CIVILIAN_SEPARATION = (
    "float MinimumCivilianSeparationMeters = 550.f;"
)
# Leftover #56–#64 plus leftover Harbor #6/#8/#9,
# leftover theater-kit #59, leftover #107–#673, plus
# leftover Mission05 InitializePlayableMission #666,
# leftover Mission04 InitializePlayableMission,
# leftover Mission06 InitializePlayableMission #685,
# leftover Mission07 InitializePlayableMission,
# leftover Mission08 wave-state enum #68fc / #237,
# leftover Mission08 protected-target enum #a66a / #229,
# leftover Mission08 protected-target-runtime-defaults
# #75e6 / #226, leftover hoist-window-runtime-defaults
# #ec79, leftover GetStormRainBeatKit /
# ApplyStormRainPlayContract / GetStormRainBeatKind /
# TickStormRainBeatKit without UFUNCTION, leftover
# Mission07 wave-state enum #74d8, leftover
# Mission07 protected-target enum #18f2, leftover
# Mission07 protected-target-runtime-defaults #866c,
# leftover search-sector enum #b4d4, leftover
# search-track-runtime-defaults #8266, leftover
# Mission06 wave-state enum #fa65, leftover
# airfield-target enum #14d2, leftover
# airfield-target-runtime-defaults #6ad8, leftover
# payload-window-runtime-defaults #f114, leftover
# BindRuntimeActors, plus leftover #56–#64
# subsystem production files. This lane only adds
# an isolated Python ConfigureMissionDefinition
# method declaration contract on
# ASkyguardMission02IntegrationDirector.
LOCKED = {
    "SkyguardMission02IntegrationDirector.h",
    "SkyguardMission02IntegrationDirector.cpp",
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
        f"{prefix}test_{missile}_boss_decl_contract.py",
        f"{prefix}test_{missile}_missile_decl_contract.py",
    )


# Isolated-test drafts stay off this lane. Sibling
# leftover briefing-widget isolated contracts,
# leftover MissionBriefingComponent method decl
# contracts, leftover briefing-card /
# briefing-radio-row defaults, leftover briefing
# fail-closed tests, leftover audio-director
# listener / telemetry / suppression / engine-state
# / bank-null / world-event fail-closed contracts,
# leftover radio-chatter empty fail-closed /
# empty-queue / empty-line contracts, leftover
# Harbor #6/#8/#9, leftover theater-kit #59,
# leftover environment-readiness defaults #6b9d /
# #b931, leftover campaign-definition method
# contracts, leftover Mission01 InitializePlayableMission
# #608, leftover Mission03 InitializePlayableMission
# #628, leftover Harbor Mission02, leftover
# Mission04 wave-state enum #bb22, leftover
# searchlight-track-runtime-defaults #7347, sibling
# Mission01 Integration / Environment field
# contracts stay sibling-only.
LOCKED_SCRIPTS = (
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
    "Scripts/tests/test_mission07_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission07_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission07_notify_protected_target_damage_decl_contract.py",
    "Scripts/tests/test_mission07_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission07_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission07_advance_reinforcement_timer_decl_contract.py",
    "Scripts/tests/test_mission07_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission07_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission07_get_readiness_decl_contract.py",
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
    "Scripts/tests/test_mission07_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission08_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission08_bind_runtime_actors_decl_contract.py",
    "Scripts/tests/test_mission08_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission08_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission08_start_hoist_window_decl_contract.py",
    "Scripts/tests/test_mission08_advance_hoist_window_decl_contract.py",
    "Scripts/tests/test_mission08_validate_weapon_release_decl_contract.py",
    "Scripts/tests/test_mission08_notify_protected_target_damage_decl_contract.py",
    "Scripts/tests/test_mission08_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission08_handle_drone_city_impact_decl_contract.py",
    "Scripts/tests/test_mission08_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission08_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission08_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission08_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission08_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission08_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission08_get_hoist_runtime_decl_contract.py",
    "Scripts/tests/test_mission08_get_rejected_weapon_releases_decl_contract.py",
    "Scripts/tests/test_mission08_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission08_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission08_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission08_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission08_wave_state_enum_contract.py",
    "Scripts/tests/test_mission08_protected_target_enum_contract.py",
    "Scripts/tests/test_mission08_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_hoist_window_runtime_defaults_contract.py",
    "Scripts/tests/test_mission08_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission09_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission09_bind_campaign_runtime_decl_contract.py",
    "Scripts/tests/test_mission09_start_next_wave_decl_contract.py",
    "Scripts/tests/test_mission09_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission09_notify_protected_target_damage_decl_contract.py",
    "Scripts/tests/test_mission09_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission09_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission09_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission09_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission09_get_wave_state_decl_contract.py",
    "Scripts/tests/test_mission09_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission09_get_pool_runtime_decl_contract.py",
    "Scripts/tests/test_mission09_get_protected_target_decl_contract.py",
    "Scripts/tests/test_mission09_get_surviving_target_count_decl_contract.py",
    "Scripts/tests/test_mission09_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission09_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission09_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission09_wave_state_enum_contract.py",
    "Scripts/tests/test_mission09_protected_target_enum_contract.py",
    "Scripts/tests/test_mission09_protected_target_runtime_defaults_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_defaults_contract.py",
    "Scripts/tests/test_mission09_pool_budget_defaults_contract.py",
    "Scripts/tests/test_mission09_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission10_initialize_playable_mission_decl_contract.py",
    "Scripts/tests/test_mission10_route_phase_enum_contract.py",
    "Scripts/tests/test_mission10_protected_group_enum_contract.py",
    "Scripts/tests/test_mission10_protected_runtime_defaults_contract.py",
    "Scripts/tests/test_mission10_configure_mission_definition_decl_contract.py",
    "Scripts/tests/test_mission10_validate_mission_contract_decl_contract.py",
    "Scripts/tests/test_mission10_get_mission_id_decl_contract.py",
    "Scripts/tests/test_mission10_get_surviving_protected_group_count_decl_contract.py",
    "Scripts/tests/test_mission10_get_protected_group_decl_contract.py",
    "Scripts/tests/test_mission10_get_rejected_weapon_releases_decl_contract.py",
    "Scripts/tests/test_mission10_get_route_phase_decl_contract.py",
    "Scripts/tests/test_mission10_get_remaining_threats_in_wave_decl_contract.py",
    "Scripts/tests/test_mission10_get_objective_runtime_decl_contract.py",
    "Scripts/tests/test_mission10_is_core_playable_ready_decl_contract.py",
    "Scripts/tests/test_mission10_get_readiness_decl_contract.py",
    "Scripts/tests/test_mission10_synchronize_runtime_state_decl_contract.py",
    "Scripts/tests/test_mission10_notify_protected_asset_failed_decl_contract.py",
    "Scripts/tests/test_mission10_notify_protected_group_damage_decl_contract.py",
    "Scripts/tests/test_mission10_validate_weapon_release_decl_contract.py",
    "Scripts/tests/test_mission10_start_phase_wave_decl_contract.py",
    "Scripts/tests/test_mission10_notify_threat_destroyed_decl_contract.py",
    "Scripts/tests/test_mission10_root_field_decl_contract.py",
    "Scripts/tests/test_mission10_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission10_audio_director_field_decl_contract.py",
    "Scripts/tests/test_mission10_radio_chatter_field_decl_contract.py",
    "Scripts/tests/test_mission10_sortie_presentation_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_definition_field_decl_contract.py",
    "Scripts/tests/test_mission10_mission_definition_field_decl_contract.py",
    "Scripts/tests/test_mission10_readiness_field_decl_contract.py",
    "Scripts/tests/test_mission10_auto_initialize_field_decl_contract.py",
    "Scripts/tests/test_mission10_allow_bounded_actor_spawning_field_decl_contract.py",
    "Scripts/tests/test_mission10_auto_launch_after_briefing_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_save_slot_name_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_save_user_index_field_decl_contract.py",
    "Scripts/tests/test_mission10_last_flight_spawn_location_field_decl_contract.py",
    "Scripts/tests/test_mission10_last_flight_spawn_rotation_field_decl_contract.py",
    "Scripts/tests/test_mission10_minimum_weapon_separation_meters_field_decl_contract.py",
    "Scripts/tests/test_mission10_maximum_protected_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission10_protected_group_count_field_decl_contract.py",
    "Scripts/tests/test_mission10_objective_count_field_decl_contract.py",
    "Scripts/tests/test_mission10_wave_count_field_decl_contract.py",
    "Scripts/tests/test_mission10_protected_runtime_integrity_field_decl_contract.py",
    "Scripts/tests/test_mission10_protected_runtime_destroyed_field_decl_contract.py",
    "Scripts/tests/test_mission10_evacuation_ship_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_ferry_terminal_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_ambulance_a_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_ambulance_b_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_bus_a_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_bus_b_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_highway_convoy_anchor_field_decl_contract.py",
    "Scripts/tests/test_mission10_map_assembly_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_last_flight_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_gunner_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_objectives_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_phase_waves_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_protected_groups_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_briefing_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_audio_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_runtime_started_field_decl_contract.py",
    "Scripts/tests/test_mission10_sortie_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_evacuation_presentation_ready_field_decl_contract.py",
    "Scripts/tests/test_mission10_campaign_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission10_mission_definition_valid_field_decl_contract.py",
    "Scripts/tests/test_mission01_configure_mission_definition_decl_contract.py",
) + leftover_live_copy_boss_scripts()
SIBLING_DIRECTOR_FIELDS_NOT_LOCKED = (
    "Root;",
    "Briefing",
    "AudioDirector",
    "RadioChatter",
    "SortiePresentation",
    "CampaignDefinition",
    "Readiness;",
    "bAutoInitialize",
    "bAllowBoundedActorSpawning",
    "bAutoLaunchAfterBriefing",
    "ConvoyRuntimeAnchor",
    ROOT_FIELD,
    BRIEFING_FIELD,
    AUDIO_DIRECTOR_FIELD,
    RADIO_CHATTER_FIELD,
    SORTIE_PRESENTATION_FIELD,
    CAMPAIGN_DEFINITION_FIELD,
    MISSION_DEFINITION_FIELD,
    READINESS_FIELD,
    AUTO_INITIALIZE_FIELD,
    ALLOW_BOUNDED_SPAWNING_FIELD,
    AUTO_LAUNCH_AFTER_BRIEFING_FIELD,
    CONVOY_RUNTIME_ANCHOR,
    RESCUE_HELICOPTER_ANCHOR,
    HOIST_CABLE_ANCHOR,
    SURVIVORS_ANCHOR,
    RAFTS_ANCHOR,
    RESCUE_VESSEL_ANCHOR,
    "RescueHelicopterAnchor",
    "HoistCableAnchor",
    "SurvivorsAnchor",
    "RaftsAnchor",
    "RescueVesselAnchor",
)
SIBLING_INTEGRATION_METHODS_NOT_LOCKED = (
    INITIALIZE_PLAYABLE_MISSION,
    BIND_CAMPAIGN_RUNTIME,
    GET_POOL_RUNTIME,
    GET_MISSION09_PROTECTED_TARGET,
    GET_MISSION09_WAVE_STATE,
    NOTIFY_OBJECTIVE_PROGRESS,
    NOTIFY_PROTECTED_ASSET_FAILED,
    HANDLE_DRONE_CITY_IMPACT,
    SYNCHRONIZE_RUNTIME_STATE,
    IS_CORE_PLAYABLE_READY,
    GET_READINESS,
    GET_OBJECTIVE_RUNTIME,
    GET_GUNNER,
    GET_PATHFINDER,
    GET_MISSION_ID,
    VALIDATE_MISSION_CONTRACT,
    BIND_RUNTIME_ACTORS,
    GET_AIRCRAFT,
    START_NEXT_WAVE,
    NOTIFY_THREAT_DESTROYED,
    ADVANCE_CONVOY_BY_DISTANCE,
    NOTIFY_CONVOY_DAMAGE,
    GET_WAVE_STATE,
    GET_CONVOY_ROUTE_STATE,
    GET_DAY_BEAT_KIT,
    GET_NIGHT_BEAT_KIT,
    START_SEARCHLIGHT_WINDOW,
    ADVANCE_SEARCHLIGHT_TRACK,
    NOTIFY_SUBSTATION_DAMAGE,
    GET_REMAINING_THREATS_IN_WAVE,
    GET_SEARCHLIGHT_RUNTIME,
    GET_SUBSTATION_INTEGRITY,
    "InitializePlayableMission",
    "NotifyObjectiveProgress",
    "NotifyProtectedAssetFailed",
    "HandleDroneCityImpact",
    "SynchronizeRuntimeState",
    "IsCorePlayableReady",
    "GetReadiness",
    "GetObjectiveRuntime",
    "GetGunner",
    "GetPathfinder",
    "GetMissionId",
    "ValidateMissionContract",
    "StartNextWave",
    "NotifyThreatDestroyed",
    "AdvanceConvoyByDistance",
    "NotifyConvoyDamage",
    "GetWaveState",
    "GetConvoyRouteState",
    "GetDayBeatKit",
    "GetNightBeatKit",
    "StartSearchlightWindow",
    "AdvanceSearchlightTrack",
    "NotifySubstationDamage",
    "GetRemainingThreatsInWave",
    "GetSearchlightRuntime",
    "GetSubstationIntegrity",
    "test_mission01_configure_mission_definition_decl_contract.py",
    "test_mission10_configure_mission_definition_decl_contract.py",
    "test_mission01_notify_objective_progress_decl_contract.py",
    "test_mission01_notify_protected_asset_failed_decl_contract.py",
    "test_mission01_synchronize_runtime_state_decl_contract.py",
    "test_mission01_is_core_playable_ready_decl_contract.py",
    "test_mission01_get_readiness_decl_contract.py",
    "test_mission01_get_objective_runtime_decl_contract.py",
    "test_mission01_get_gunner_decl_contract.py",
    "test_mission01_get_pathfinder_decl_contract.py",
    "test_mission01_get_mission_id_decl_contract.py",
    "test_mission01_validate_mission_contract_decl_contract.py",
    "test_mission01_bind_runtime_actors_decl_contract.py",
    "test_mission01_get_aircraft_decl_contract.py",
    "test_mission01_initialize_playable_mission_decl_contract.py",
    "test_mission02_initialize_playable_mission_decl_contract.py",
    "test_mission03_initialize_playable_mission_decl_contract.py",
    "test_mission04_wave_state_enum_contract.py",
    "test_searchlight_track_runtime_defaults_contract.py",
    "test_mission04_configure_mission_definition_decl_contract.py",
    "test_mission04_bind_runtime_actors_decl_contract.py",
    "test_mission04_start_next_wave_decl_contract.py",
    "test_mission04_notify_threat_destroyed_decl_contract.py",
    "test_mission04_start_searchlight_window_decl_contract.py",
    "test_mission04_advance_searchlight_track_decl_contract.py",
    "test_mission04_notify_substation_damage_decl_contract.py",
    "test_mission04_notify_protected_asset_failed_decl_contract.py",
    "test_mission04_handle_drone_city_impact_decl_contract.py",
    "test_mission04_synchronize_runtime_state_decl_contract.py",
    "test_mission04_is_core_playable_ready_decl_contract.py",
    "test_mission04_get_readiness_decl_contract.py",
    "test_mission04_get_objective_runtime_decl_contract.py",
    "test_mission04_get_wave_state_decl_contract.py",
    "test_mission04_get_remaining_threats_in_wave_decl_contract.py",
    "test_mission04_get_searchlight_runtime_decl_contract.py",
    "test_mission04_get_substation_integrity_decl_contract.py",
    "test_mission04_get_mission_id_decl_contract.py",
    "test_mission04_validate_mission_contract_decl_contract.py",
    "test_mission04_get_night_beat_kit_decl_contract.py",
    "test_mission03_bind_runtime_actors_decl_contract.py",
    "test_mission03_get_aircraft_decl_contract.py",
    "test_mission03_handle_drone_city_impact_decl_contract.py",
    "test_mission03_validate_mission_contract_decl_contract.py",
    START_PAYLOAD_WINDOW,
    ADVANCE_PAYLOAD_WINDOW,
    TRY_JAM_ACTIVE_PAYLOAD,
    NOTIFY_AIRFIELD_TARGET_DAMAGE,
    GET_PAYLOAD_WINDOW,
    GET_TARGET_RUNTIME,
    GET_SURVIVING_TARGET_COUNT,
    GET_DAY_BEAT_KIND,
    GET_DAY_BEAT_INDEX,
    TICK_DAY_BEAT_KIT,
    HANDLE_BOSS_PHASE_CHANGED,
    "StartPayloadWindow",
    "AdvancePayloadWindow",
    "TryJamActivePayload",
    "NotifyAirfieldTargetDamage",
    "GetPayloadWindow",
    "GetTargetRuntime",
    "GetSurvivingTargetCount",
    "GetDayBeatKind",
    "GetDayBeatIndex",
    "TickDayBeatKit",
    "HandleBossPhaseChanged",
    "test_mission04_initialize_playable_mission_decl_contract.py",
    "test_mission05_initialize_playable_mission_decl_contract.py",
    "test_mission05_configure_mission_definition_decl_contract.py",
    "test_mission05_get_surviving_target_count_decl_contract.py",
    "test_mission06_wave_state_enum_contract.py",
    "test_airfield_target_enum_contract.py",
    "test_airfield_target_runtime_defaults_contract.py",
    "test_payload_window_runtime_defaults_contract.py",
    CLASSIFY_FALSE_TRACK,
    CONFIRM_RADAR_GHOST_IDENTIFICATION,
    NOTIFY_PROTECTED_TARGET_DAMAGE,
    ADVANCE_REINFORCEMENT_TIMER,
    GET_SEARCH_SECTOR,
    GET_CLASSIFIED_FALSE_TRACK_COUNT,
    IS_HOSTILE_CONTACT_CONFIRMED,
    GET_PROTECTED_TARGET,
    GET_REINFORCEMENT_TIME_REMAINING,
    GET_NIGHT_BEAT_KIND,
    GET_NIGHT_BEAT_INDEX,
    TICK_NIGHT_BEAT_KIT,
    "ClassifyFalseTrack",
    "ConfirmRadarGhostIdentification",
    "NotifyProtectedTargetDamage",
    "AdvanceReinforcementTimer",
    "GetSearchSector",
    "GetClassifiedFalseTrackCount",
    "IsHostileContactConfirmed",
    "GetProtectedTarget",
    "GetReinforcementTimeRemaining",
    "GetNightBeatKind",
    "GetNightBeatIndex",
    "TickNightBeatKit",
    "test_mission06_initialize_playable_mission_decl_contract.py",
    "test_mission07_wave_state_enum_contract.py",
    "test_mission07_protected_target_enum_contract.py",
    "test_mission07_protected_target_runtime_defaults_contract.py",
    "test_search_sector_enum_contract.py",
    "test_mission07_configure_mission_definition_decl_contract.py",
    "test_mission07_bind_runtime_actors_decl_contract.py",
    "test_mission07_classify_false_track_decl_contract.py",
    "test_mission07_confirm_radar_ghost_identification_decl_contract.py",
    "test_mission07_start_next_wave_decl_contract.py",
    "test_mission07_notify_threat_destroyed_decl_contract.py",
    "test_mission07_notify_protected_target_damage_decl_contract.py",
    "test_mission07_notify_protected_asset_failed_decl_contract.py",
    "test_mission07_handle_drone_city_impact_decl_contract.py",
    "test_mission07_advance_reinforcement_timer_decl_contract.py",
    "test_mission07_synchronize_runtime_state_decl_contract.py",
    "test_mission07_is_core_playable_ready_decl_contract.py",
    "test_mission07_get_readiness_decl_contract.py",
    "test_mission07_get_objective_runtime_decl_contract.py",
    "test_mission07_get_wave_state_decl_contract.py",
    "test_mission07_get_remaining_threats_in_wave_decl_contract.py",
    "test_mission07_get_search_sector_decl_contract.py",
    "test_mission07_get_classified_false_track_count_decl_contract.py",
    "test_mission07_is_hostile_contact_confirmed_decl_contract.py",
    "test_mission07_get_protected_target_decl_contract.py",
    "test_mission07_get_surviving_target_count_decl_contract.py",
    "test_mission07_get_reinforcement_time_remaining_decl_contract.py",
    "test_mission07_get_mission_id_decl_contract.py",
    "test_mission07_validate_mission_contract_decl_contract.py",
    "test_mission07_get_night_beat_kit_decl_contract.py",
    "test_mission07_initialize_playable_mission_decl_contract.py",
    START_HOIST_WINDOW,
    ADVANCE_HOIST_WINDOW,
    VALIDATE_WEAPON_RELEASE,
    GET_HOIST_RUNTIME,
    GET_REJECTED_WEAPON_RELEASES,
    GET_STORM_RAIN_BEAT_KIT,
    APPLY_STORM_RAIN_PLAY_CONTRACT,
    GET_STORM_RAIN_BEAT_KIND,
    TICK_STORM_RAIN_BEAT_KIT,
    "StartHoistWindow",
    "AdvanceHoistWindow",
    "ValidateWeaponRelease",
    "GetHoistRuntime",
    "GetRejectedWeaponReleases",
    "GetStormRainBeatKit",
    "ApplyStormRainPlayContract",
    "GetStormRainBeatKind",
    "TickStormRainBeatKit",
    "test_mission08_configure_mission_definition_decl_contract.py",
    "test_mission08_start_next_wave_decl_contract.py",
    "test_mission08_notify_threat_destroyed_decl_contract.py",
    "test_mission08_start_hoist_window_decl_contract.py",
    "test_mission08_advance_hoist_window_decl_contract.py",
    "test_hoist_window_runtime_defaults_contract.py",
    "test_mission08_wave_state_enum_contract.py",
    "test_mission08_protected_target_enum_contract.py",
    "test_mission08_protected_target_runtime_defaults_contract.py",
)
LEFTOVER_BRIEFING_METHODS_NOT_LOCKED = (
    CONFIGURE_FROM_MISSION,
    ADVANCE_BRIEFING,
    SET_ASSETS_READY,
    ACKNOWLEDGE_AND_LAUNCH,
    CAN_LAUNCH,
    GET_ELAPSED_SECONDS,
    GET_BRIEFING_STATE,
    GET_MINIMUM_WARMUP_SECONDS,
    GET_BRIEFING_TEXT,
    GET_RADIO_CHATTER,
    "ConfigureFromMission",
    "AdvanceBriefing",
    "SetAssetsReady",
    "AcknowledgeAndLaunch",
    "CanLaunch",
    "GetElapsedSeconds",
    "GetBriefingState",
    "GetMinimumWarmupSeconds",
    "GetBriefingText",
    "GetRadioChatter",
    "test_briefing_configure_from_mission_decl_contract.py",
    "test_briefing_advance_briefing_decl_contract.py",
    "test_briefing_set_assets_ready_decl_contract.py",
    "test_briefing_acknowledge_and_launch_decl_contract.py",
    "test_briefing_can_launch_decl_contract.py",
    "test_briefing_get_elapsed_seconds_decl_contract.py",
    "test_briefing_get_briefing_state_decl_contract.py",
    "test_briefing_get_minimum_warmup_seconds_decl_contract.py",
    "test_briefing_get_briefing_text_decl_contract.py",
    "test_briefing_get_radio_chatter_decl_contract.py",
)
LEFTOVER_BRIEFING_WIDGET_NOT_LOCKED = (
    WIDGET_CONFIGURE,
    WIDGET_GET_PRESENTATION,
    WIDGET_GET_MISSION_TITLE,
    WIDGET_GET_BRIEFING_TEXT,
    WIDGET_ACKNOWLEDGE_BRIEFING,
    WIDGET_LAUNCH_SORTIE,
    "GetPresentation",
    "GetMissionTitle",
    "AcknowledgeBriefing",
    "LaunchSortie",
    "USkyguardBriefingWidget",
    "test_briefing_widget_configure_decl_contract.py",
    "test_briefing_widget_get_presentation_decl_contract.py",
    "test_briefing_widget_get_mission_title_decl_contract.py",
    "test_briefing_widget_get_briefing_text_decl_contract.py",
    "test_briefing_widget_acknowledge_briefing_decl_contract.py",
    "test_briefing_widget_launch_sortie_decl_contract.py",
)
LEFTOVER_BRIEFING_DEFAULTS_NOT_LOCKED = (
    "test_briefing_card_defaults_contract.py",
    "test_briefing_radio_row_defaults_contract.py",
    "test_briefing_fail_closed.py",
    "test_briefing_fail_closed_tests.py",
    "test_briefing_fail_closed_contract.py",
    "FSkyguardBriefingCard",
    "FSkyguardBriefingRadioRow",
)
LEFTOVER_AUDIO_DIRECTOR_FAIL_CLOSED_NOT_LOCKED = (
    "test_audio_director_listener_perspective_fail_closed.py",
    "test_audio_director_listener_perspective_fail_closed_tests.py",
    "test_audio_director_listener_perspective_fail_closed_contract.py",
    "test_audio_director_telemetry_fail_closed.py",
    "test_audio_director_telemetry_fail_closed_tests.py",
    "test_audio_director_telemetry_fail_closed_contract.py",
    "test_audio_director_suppression_fail_closed.py",
    "test_audio_director_suppression_fail_closed_tests.py",
    "test_audio_director_suppression_fail_closed_contract.py",
    "test_audio_director_engine_state_fail_closed.py",
    "test_audio_director_engine_state_fail_closed_tests.py",
    "test_audio_director_engine_state_fail_closed_contract.py",
    "test_audio_director_bank_null_fail_closed.py",
    "test_audio_director_bank_null_fail_closed_tests.py",
    "test_audio_director_bank_null_fail_closed_contract.py",
    "test_audio_director_world_event_fail_closed.py",
    "test_audio_director_world_event_fail_closed_tests.py",
    "test_audio_director_world_event_fail_closed_contract.py",
    "SkyguardAudioDirectorComponent.h",
    "SetListenerPerspective",
    "TriggerWorldEvent",
)
LEFTOVER_RADIO_CHATTER_FAIL_CLOSED_NOT_LOCKED = (
    "test_radio_chatter_empty_fail_closed.py",
    "test_radio_chatter_empty_fail_closed_tests.py",
    "test_radio_chatter_empty_fail_closed_contract.py",
    "test_radio_chatter_empty_queue_fail_closed.py",
    "test_radio_chatter_empty_queue_fail_closed_tests.py",
    "test_radio_chatter_empty_queue_fail_closed_contract.py",
    "test_radio_chatter_empty_line_tests.py",
    "test_radio_chatter_empty_line_fail_closed.py",
    "test_radio_chatter_empty_line_fail_closed_tests.py",
    "test_radio_chatter_empty_line_fail_closed_contract.py",
    "SkyguardRadioChatterComponent.h",
)
LEFTOVER_CAMPAIGN_DEFINITION_METHODS_NOT_LOCKED = (
    "test_campaign_definition_missions_decl_contract.py",
    "test_campaign_definition_display_name_decl_contract.py",
    "test_campaign_definition_campaign_id_decl_contract.py",
    "test_find_mission_decl_contract.py",
    "test_validate_definition_decl_contract.py",
    "test_get_primary_asset_id_decl_contract.py",
    "FindMission",
    "GetPrimaryAssetId",
    "ValidateDefinition",
)
LEFTOVER_HARBOR_SCRIPTS_NOT_LOCKED = (
    "test_readable_escalation.py",
    "test_sortie_debrief_loadouts.py",
    "test_harbor_proof_play.py",
    "test_harbor_proof_source_tests.py",
    "test_campaign_theater_kit_contract.py",
)
LEFTOVER_ENVIRONMENT_READINESS_NOT_LOCKED = (
    "test_mission01_environment_readiness_defaults_contract.py",
    "test_environment_readiness_defaults_contract.py",
    "FSkyguardMission01EnvironmentReadiness",
    "FSkyguardEnvironmentReadiness",
)
LEFTOVER_SPAWN_FIELDS_NOT_LOCKED = (
    "PathfinderSpawnLocation",
    "PathfinderSpawnRotation",
    PATHFINDER_SPAWN_LOCATION,
    PATHFINDER_SPAWN_ROTATION,
    "RoadHunterSpawnLocation",
    "RoadHunterSpawnRotation",
    ROAD_HUNTER_SPAWN_LOCATION,
    ROAD_HUNTER_SPAWN_ROTATION,
    "BlackKiteSpawnLocation",
    "BlackKiteSpawnRotation",
    BLACK_KITE_SPAWN_LOCATION,
    BLACK_KITE_SPAWN_ROTATION,
    "RadarGhostSpawnLocation",
    "RadarGhostSpawnRotation",
    RADAR_GHOST_SPAWN_LOCATION,
    RADAR_GHOST_SPAWN_ROTATION,
    LIFELINE_HUNTER_SPAWN_LOCATION,
    LIFELINE_HUNTER_SPAWN_ROTATION,
    "LifelineHunterSpawnLocation",
    "LifelineHunterSpawnRotation",
    IRON_RAIN_SPAWN_LOCATION,
    "IronRainSpawnLocation",
)
LEFTOVER_HANDLE_DRONE_CITY_IMPACT_NOT_LOCKED = (
    "HandleDroneCityImpact",
    HANDLE_DRONE_CITY_IMPACT,
    "test_mission03_handle_drone_city_impact_decl_contract.py",
    "test_mission02_handle_drone_city_impact_decl_contract.py",
)
LEFTOVER_MISSION01_INITIALIZE_NOT_LOCKED = (
    "ASkyguardMission01IntegrationDirector",
    "SkyguardMission01IntegrationDirector.h",
    "test_mission01_initialize_playable_mission_decl_contract.py",
    'Category="Skyguard|Mission01|Integration"',
)
LEFTOVER_MISSION03_INITIALIZE_NOT_LOCKED = (
    "ASkyguardMission03IntegrationDirector",
    "SkyguardMission03IntegrationDirector.h",
    "test_mission03_initialize_playable_mission_decl_contract.py",
    'Category="Skyguard|Mission03|Integration"',
    'Category="Skyguard|Mission04|Integration"',
    'Category="Skyguard|Mission05|Integration"',
    'Category="Skyguard|Mission05|Protection"',
    'Category="Skyguard|Mission05|Waves"',
    'Category="Skyguard|Mission06|Waves"',
    'Category="Skyguard|Mission06|Payload"',
    'Category="Skyguard|Mission06|Targets"',
    'Category="Skyguard|Mission06|Objectives"',
    'Category="Skyguard|Mission06|Integration"',
    'Category="Skyguard|Mission07|Integration"',
    'Category="Skyguard|Mission08|Integration"',
    'Category="Skyguard|Mission09|Waves"',
    'Category="Skyguard|Mission09|Protection"',
    'Category="Skyguard|Mission09|Performance"',
    'Category="Skyguard|Mission09|Objectives"',
    'Category="Skyguard|Mission07|Waves"',
    'Category="Skyguard|Mission08|Waves"',
    'Category="Skyguard|Mission08|Hoist"',
    'Category="Skyguard|Mission08|Safety"',
    'Category="Skyguard|Mission08|Protection"',
    'Category="Skyguard|Mission08|Objectives"',
    'Category="Skyguard|Mission08|Rescue"',
    'Category="Skyguard|Mission08|Integration"',
    'Category="Skyguard|Mission09|Waves"',
    'Category="Skyguard|Mission09|Protection"',
    'Category="Skyguard|Mission09|Performance"',
    'Category="Skyguard|Mission09|Objectives"',
    'Category="Skyguard|Mission07|Search"',
    'Category="Skyguard|Mission07|Protection"',
    'Category="Skyguard|Mission07|Objectives"',
    'Category="Skyguard|Mission07|Boss"',
    'Category="Skyguard|Mission07|Integration"',
    'Category="Skyguard|Mission08|Waves"',
    'Category="Skyguard|Mission08|Hoist"',
    'Category="Skyguard|Mission08|Safety"',
    'Category="Skyguard|Mission08|Protection"',
    'Category="Skyguard|Mission08|Objectives"',
    'Category="Skyguard|Mission08|Rescue"',
    'Category="Skyguard|Mission09|Integration"',
    'Category="Skyguard|Mission10|Integration"',
    'Category="Skyguard|Mission10|Waves"',
    'Category="Skyguard|Mission10|Safety"',
    'Category="Skyguard|Mission10|Protection"',
    'Category="Skyguard|Mission10|Objectives"',
    'Category="Skyguard|Mission10|Evacuation"',
    'Category="Skyguard|Mission10|Campaign"',
)
LEFTOVER_MISSION04_WAVE_STATE_ENUM_NOT_LOCKED = (
    "AwaitingWave",
    "WaveActive",
    "BossEngaged",
    "Completed",
    "Failed",
    "test_mission04_wave_state_enum_contract.py",
)
LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED = (
    "GetSearchlightRuntime",
    GET_SEARCHLIGHT_RUNTIME,
    "FSkyguardSearchlightTrackRuntime",
    "test_searchlight_track_runtime_defaults_contract.py",
    "test_search_track_runtime_defaults_contract.py",
)
LEFTOVER_HARBOR_MISSION02_NOT_LOCKED = (
    "test_mission02_initialize_playable_mission_decl_contract.py",
    "test_mission02_bind_runtime_actors_decl_contract.py",
    "test_mission02_handle_drone_city_impact_decl_contract.py",
    "ESkyguardMission02WaveState",
    'Category="Skyguard|Mission02|Harbor"',
    'Category="Skyguard|Mission02|Waves"',
    'Category="Skyguard|Mission02|Objectives"',
    "cursor/m02-director-api-tests-1c8b",
    "NotifyFuelTerminalDamage",
    "GetFuelTerminalIntegrity",
    "GetCurrentWaveIndex",
    "GetBreakwater",
)
LEFTOVER_MISSION10_CONFIGURE_NOT_LOCKED = (
    "test_mission10_configure_mission_definition_decl_contract.py",
    "ASkyguardMission10IntegrationDirector",
    "SkyguardMission10IntegrationDirector.h",
    'Category="Skyguard|Mission10|Integration"',
    "cursor/mission10-configure-mission-definition-decl-contract-c332",
)
LEFTOVER_MISSION02_WAVE_STATE_NOT_LOCKED = (
    "ESkyguardMission02WaveState",
    "test_mission02_wave_state_enum_contract.py",
)
LEFTOVER_SKYLINE_NOT_LOCKED = (
    "HarborIndustrial",
    "ESkyguardMissionSkylineStyle",
)
LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED = (
    "OpticalTracker",
    "WeaponServo",
    "CountermeasurePod",
    "DebrisControlSurface",
    "MinimumWeaponSeparationMeters",
)
LEFTOVER_APACHE_NOT_LOCKED = (
    "HullCollider",
    "MaxIntegrity",
    "CurrentIntegrity",
    "GetChinMuzzleLocation",
    "GetGunnerMount",
    "ESkyguardApacheSystem",
    "test_apache_hull_collider_field_decl_contract.py",
    "test_apache_own_ship_systems_contract.py",
    "test_apache_chin_muzzle_tests.py",
    "test_settings_apply_broadcast_tests.py",
)
LEFTOVER_PATROL_SHIP_NOT_LOCKED = (
    "ASkyguardPatrolShip",
    "test_patrol_ship_empty_fail_closed.py",
)
LEFTOVER_RADAR_NODE_NOT_LOCKED = (
    "SkyguardRadarNode",
    "ASkyguardRadarNode",
)
LEFTOVER_FILL_AND_GUNNER_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "FillAndFinalize",
    "FillAndFail",
    "ApplyHydraForClusters",
)

LEFTOVER_MISSION04_INITIALIZE_NOT_LOCKED = (
    "ASkyguardMission04IntegrationDirector",
    "SkyguardMission04IntegrationDirector.h",
    "test_mission04_initialize_playable_mission_decl_contract.py",
    'Category="Skyguard|Mission04|Integration"',
)
LEFTOVER_MISSION05_INITIALIZE_NOT_LOCKED = (
    "ASkyguardMission05IntegrationDirector",
    "SkyguardMission05IntegrationDirector.h",
    "test_mission05_initialize_playable_mission_decl_contract.py",
    'Category="Skyguard|Mission05|Integration"',
)
LEFTOVER_MISSION05_CONFIGURE_NOT_LOCKED = (
    "test_mission05_configure_mission_definition_decl_contract.py",
    "ASkyguardMission05IntegrationDirector",
    "SkyguardMission05IntegrationDirector.h",
    'Category="Skyguard|Mission05|Integration"',
)
LEFTOVER_MISSION05_GET_SURVIVING_TARGET_COUNT_NOT_LOCKED = (
    "test_mission05_get_surviving_target_count_decl_contract.py",
    GET_SURVIVING_TARGET_COUNT,
    "GetSurvivingTargetCount",
    'Category="Skyguard|Mission05|Protection"',
)
LEFTOVER_MISSION06_WAVE_STATE_ENUM_NOT_LOCKED = (
    "ESkyguardMission06WaveState",
    "test_mission06_wave_state_enum_contract.py",
)
LEFTOVER_AIRFIELD_TARGET_NOT_LOCKED = (
    "ESkyguardAirfieldTarget",
    "test_airfield_target_enum_contract.py",
    "test_airfield_target_runtime_defaults_contract.py",
    "FSkyguardAirfieldTargetRuntime",
)
LEFTOVER_PAYLOAD_WINDOW_NOT_LOCKED = (
    "FSkyguardPayloadWindowRuntime",
    "test_payload_window_runtime_defaults_contract.py",
    START_PAYLOAD_WINDOW,
    ADVANCE_PAYLOAD_WINDOW,
    TRY_JAM_ACTIVE_PAYLOAD,
    GET_PAYLOAD_WINDOW,
    "StartPayloadWindow",
    "AdvancePayloadWindow",
    "TryJamActivePayload",
    "GetPayloadWindow",
)
LEFTOVER_DAY_BEAT_METHODS_NOT_LOCKED = (
    GET_DAY_BEAT_KIT,
    GET_DAY_BEAT_KIND,
    GET_DAY_BEAT_INDEX,
    TICK_DAY_BEAT_KIT,
    "GetDayBeatKit",
    "GetDayBeatKind",
    "GetDayBeatIndex",
    "TickDayBeatKit",
)
LEFTOVER_HANDLE_BOSS_PHASE_CHANGED_NOT_LOCKED = (
    "HandleBossPhaseChanged",
    HANDLE_BOSS_PHASE_CHANGED,
)
LEFTOVER_MISSION06_INITIALIZE_NOT_LOCKED = (
    "ASkyguardMission06IntegrationDirector",
    "SkyguardMission06IntegrationDirector.h",
    "test_mission06_initialize_playable_mission_decl_contract.py",
    'Category="Skyguard|Mission06|Integration"',
)
LEFTOVER_MISSION07_INITIALIZE_NOT_LOCKED = (
    "ASkyguardMission07IntegrationDirector",
    "SkyguardMission07IntegrationDirector.h",
    "test_mission07_initialize_playable_mission_decl_contract.py",
    'Category="Skyguard|Mission07|Integration"',
)
LEFTOVER_MISSION08_INITIALIZE_NOT_LOCKED = (
    "ASkyguardMission08IntegrationDirector",
    "SkyguardMission08IntegrationDirector.h",
    "test_mission08_initialize_playable_mission_decl_contract.py",
    'Category="Skyguard|Mission08|Integration"',
    "cursor/mission08-initialize-playable-mission-decl-contract-c332",
)

LEFTOVER_MISSION09_INITIALIZE_NOT_LOCKED = (
    "ASkyguardMission09IntegrationDirector",
    "SkyguardMission09IntegrationDirector.h",
    "test_mission09_initialize_playable_mission_decl_contract.py",
    'Category="Skyguard|Mission09|Integration"',
    "cursor/mission09-initialize-playable-mission-decl-contract-c332",
)
LEFTOVER_MISSION06_CONFIGURE_NOT_LOCKED = (
    "test_mission06_configure_mission_definition_decl_contract.py",
    "ASkyguardMission06IntegrationDirector",
    "SkyguardMission06IntegrationDirector.h",
    'Category="Skyguard|Mission06|Integration"',
)
LEFTOVER_MISSION07_CONFIGURE_NOT_LOCKED = (
    "test_mission07_configure_mission_definition_decl_contract.py",
    "ASkyguardMission07IntegrationDirector",
    "SkyguardMission07IntegrationDirector.h",
    'Category="Skyguard|Mission07|Integration"',
)
LEFTOVER_MISSION08_CONFIGURE_NOT_LOCKED = (
    "test_mission08_configure_mission_definition_decl_contract.py",
    "ASkyguardMission08IntegrationDirector",
    "SkyguardMission08IntegrationDirector.h",
    'Category="Skyguard|Mission08|Integration"',
    "cursor/mission08-configure-mission-definition-decl-contract-c332",
)
LEFTOVER_MISSION09_CONFIGURE_NOT_LOCKED = (
    "test_mission09_configure_mission_definition_decl_contract.py",
    "ASkyguardMission09IntegrationDirector",
    "SkyguardMission09IntegrationDirector.h",
    'Category="Skyguard|Mission09|Integration"',
    "cursor/mission09-configure-mission-definition-decl-contract-c332",
)
LEFTOVER_MISSION10_INITIALIZE_NOT_LOCKED = (
    "test_mission10_initialize_playable_mission_decl_contract.py",
    INITIALIZE_PLAYABLE_MISSION,
    "InitializePlayableMission",
    "cursor/mission10-initialize-playable-mission-decl-contract-c332",
)
GET_MISSION10_ROUTE_PHASE = (
    "ESkyguardMission10RoutePhase GetRoutePhase() const"
)
NOTIFY_PROTECTED_GROUP_DAMAGE = (
    "bool NotifyProtectedGroupDamage("
    "ESkyguardMission10ProtectedGroup Group, "
    "int32 Damage);"
)
GET_MISSION10_PROTECTED_GROUP = (
    "FSkyguardMission10ProtectedRuntime GetProtectedGroup("
    "ESkyguardMission10ProtectedGroup Group) const;"
)
GET_SURVIVING_PROTECTED_GROUP_COUNT = (
    "int32 GetSurvivingProtectedGroupCount() const;"
)
START_PHASE_WAVE = "bool StartPhaseWave();"
LEFTOVER_MISSION10_ROUTE_PHASE_ENUM_NOT_LOCKED = (
    "ESkyguardMission10RoutePhase",
    "test_mission10_route_phase_enum_contract.py",
)
LEFTOVER_MISSION10_PROTECTED_GROUP_ENUM_NOT_LOCKED = (
    "ESkyguardMission10ProtectedGroup",
    "test_mission10_protected_group_enum_contract.py",
)
LEFTOVER_MISSION10_PROTECTED_RUNTIME_NOT_LOCKED = (
    "FSkyguardMission10ProtectedRuntime",
    "test_mission10_protected_runtime_defaults_contract.py",
)
LEFTOVER_MISSION10_SIBLING_METHODS_NOT_LOCKED = (
    INITIALIZE_PLAYABLE_MISSION,
    START_PHASE_WAVE,
    NOTIFY_THREAT_DESTROYED,
    "ValidateWeaponRelease",
    NOTIFY_PROTECTED_GROUP_DAMAGE,
    NOTIFY_PROTECTED_ASSET_FAILED,
    SYNCHRONIZE_RUNTIME_STATE,
    IS_CORE_PLAYABLE_READY,
    GET_READINESS,
    GET_MISSION10_ROUTE_PHASE,
    GET_REMAINING_THREATS_IN_WAVE,
    GET_REJECTED_WEAPON_RELEASES,
    GET_MISSION10_PROTECTED_GROUP,
    GET_SURVIVING_PROTECTED_GROUP_COUNT,
    GET_OBJECTIVE_RUNTIME,
    GET_MISSION_ID,
    VALIDATE_MISSION_CONTRACT,
    BIND_RUNTIME_ACTORS,
    HANDLE_DRONE_CITY_IMPACT,
    GET_DAY_BEAT_KIT,
    "InitializePlayableMission",
    "StartPhaseWave",
    "NotifyThreatDestroyed",
    "NotifyProtectedGroupDamage",
    "NotifyProtectedAssetFailed",
    "SynchronizeRuntimeState",
    "IsCorePlayableReady",
    "GetReadiness",
    "GetRoutePhase",
    "GetRemainingThreatsInWave",
    "GetRejectedWeaponReleases",
    "GetProtectedGroup",
    "GetSurvivingProtectedGroupCount",
    "GetObjectiveRuntime",
    "GetMissionId",
    "ValidateMissionContract",
    "BindRuntimeActors",
    "HandleDroneCityImpact",
    "GetDayBeatKit",
)
LEFTOVER_MISSION09_WAVE_STATE_ENUM_NOT_LOCKED = (
    "ESkyguardMission09WaveState",
    "test_mission09_wave_state_enum_contract.py",
)
LEFTOVER_MISSION09_PROTECTED_TARGET_NOT_LOCKED = (
    "ESkyguardMission09ProtectedTarget",
    "FSkyguardMission09ProtectedTargetRuntime",
    "test_mission09_protected_target_enum_contract.py",
    "test_mission09_protected_target_runtime_defaults_contract.py",
)
LEFTOVER_MISSION09_POOL_RUNTIME_NOT_LOCKED = (
    "FSkyguardMission09PoolRuntime",
    GET_POOL_RUNTIME,
    "GetPoolRuntime",
    "test_mission09_pool_runtime_defaults_contract.py",
)
LEFTOVER_MISSION09_POOL_BUDGET_NOT_LOCKED = (
    "FSkyguardMission09PoolBudget",
    "test_mission09_pool_budget_defaults_contract.py",
)
LEFTOVER_MISSION09_SIBLING_METHODS_NOT_LOCKED = (
    INITIALIZE_PLAYABLE_MISSION,
    BIND_CAMPAIGN_RUNTIME,
    START_NEXT_WAVE,
    NOTIFY_THREAT_DESTROYED,
    NOTIFY_PROTECTED_TARGET_DAMAGE,
    NOTIFY_PROTECTED_ASSET_FAILED,
    SYNCHRONIZE_RUNTIME_STATE,
    IS_CORE_PLAYABLE_READY,
    GET_READINESS,
    GET_MISSION09_WAVE_STATE,
    GET_REMAINING_THREATS_IN_WAVE,
    GET_POOL_RUNTIME,
    GET_MISSION09_PROTECTED_TARGET,
    GET_SURVIVING_TARGET_COUNT,
    GET_OBJECTIVE_RUNTIME,
    GET_MISSION_ID,
    VALIDATE_MISSION_CONTRACT,
    "InitializePlayableMission",
    "BindCampaignRuntime",
    "StartNextWave",
    "NotifyThreatDestroyed",
    "NotifyProtectedTargetDamage",
    "NotifyProtectedAssetFailed",
    "SynchronizeRuntimeState",
    "IsCorePlayableReady",
    "GetReadiness",
    "GetWaveState",
    "GetRemainingThreatsInWave",
    "GetPoolRuntime",
    "GetProtectedTarget",
    "GetSurvivingTargetCount",
    "GetObjectiveRuntime",
    "GetMissionId",
    "ValidateMissionContract",
    "test_mission09_configure_mission_definition_decl_contract.py",
    "test_mission09_bind_campaign_runtime_decl_contract.py",
    "test_mission09_start_next_wave_decl_contract.py",
    "test_mission09_notify_threat_destroyed_decl_contract.py",
    "test_mission09_notify_protected_target_damage_decl_contract.py",
    "test_mission09_notify_protected_asset_failed_decl_contract.py",
    "test_mission09_synchronize_runtime_state_decl_contract.py",
    "test_mission09_is_core_playable_ready_decl_contract.py",
    "test_mission09_get_readiness_decl_contract.py",
    "test_mission09_get_wave_state_decl_contract.py",
    "test_mission09_get_remaining_threats_in_wave_decl_contract.py",
    "test_mission09_get_pool_runtime_decl_contract.py",
    "test_mission09_get_protected_target_decl_contract.py",
    "test_mission09_get_surviving_target_count_decl_contract.py",
    "test_mission09_get_objective_runtime_decl_contract.py",
    "test_mission09_get_mission_id_decl_contract.py",
    "test_mission09_validate_mission_contract_decl_contract.py",
)
LEFTOVER_MISSION08_WAVE_STATE_ENUM_NOT_LOCKED = (
    "ESkyguardMission08WaveState",
    "test_mission08_wave_state_enum_contract.py",
)
LEFTOVER_MISSION08_PROTECTED_TARGET_NOT_LOCKED = (
    "ESkyguardMission08ProtectedTarget",
    "FSkyguardMission08ProtectedTargetRuntime",
    "test_mission08_protected_target_enum_contract.py",
    "test_mission08_protected_target_runtime_defaults_contract.py",
)
LEFTOVER_HOIST_WINDOW_NOT_LOCKED = (
    "FSkyguardHoistWindowRuntime",
    "test_hoist_window_runtime_defaults_contract.py",
    START_HOIST_WINDOW,
    ADVANCE_HOIST_WINDOW,
    GET_HOIST_RUNTIME,
    "StartHoistWindow",
    "AdvanceHoistWindow",
    "GetHoistRuntime",
)
LEFTOVER_STORM_RAIN_BEAT_METHODS_NOT_LOCKED = (
    GET_STORM_RAIN_BEAT_KIT,
    APPLY_STORM_RAIN_PLAY_CONTRACT,
    GET_STORM_RAIN_BEAT_KIND,
    TICK_STORM_RAIN_BEAT_KIT,
    "GetStormRainBeatKit",
    "ApplyStormRainPlayContract",
    "GetStormRainBeatKind",
    "TickStormRainBeatKit",
)
LEFTOVER_MISSION08_SIBLING_METHODS_NOT_LOCKED = (
    START_HOIST_WINDOW,
    ADVANCE_HOIST_WINDOW,
    VALIDATE_WEAPON_RELEASE,
    GET_HOIST_RUNTIME,
    GET_REJECTED_WEAPON_RELEASES,
    "StartHoistWindow",
    "AdvanceHoistWindow",
    "ValidateWeaponRelease",
    "GetHoistRuntime",
    "GetRejectedWeaponReleases",
    "test_mission08_configure_mission_definition_decl_contract.py",
    "test_mission08_start_next_wave_decl_contract.py",
    "test_mission08_notify_threat_destroyed_decl_contract.py",
    "test_mission08_start_hoist_window_decl_contract.py",
    "test_mission08_advance_hoist_window_decl_contract.py",
    "test_mission08_validate_weapon_release_decl_contract.py",
    "test_mission08_notify_protected_target_damage_decl_contract.py",
    "test_mission08_notify_protected_asset_failed_decl_contract.py",
    "test_mission08_synchronize_runtime_state_decl_contract.py",
    "test_mission08_is_core_playable_ready_decl_contract.py",
    "test_mission08_get_readiness_decl_contract.py",
    "test_mission08_get_objective_runtime_decl_contract.py",
    "test_mission08_get_wave_state_decl_contract.py",
    "test_mission08_get_remaining_threats_in_wave_decl_contract.py",
    "test_mission08_get_hoist_runtime_decl_contract.py",
    "test_mission08_get_rejected_weapon_releases_decl_contract.py",
    "test_mission08_get_protected_target_decl_contract.py",
    "test_mission08_get_surviving_target_count_decl_contract.py",
    "test_mission08_get_mission_id_decl_contract.py",
    "test_mission08_validate_mission_contract_decl_contract.py",
)
LEFTOVER_MISSION07_WAVE_STATE_ENUM_NOT_LOCKED = (
    "ESkyguardMission07WaveState",
    "test_mission07_wave_state_enum_contract.py",
)
LEFTOVER_MISSION07_PROTECTED_TARGET_NOT_LOCKED = (
    "ESkyguardMission07ProtectedTarget",
    "FSkyguardMission07ProtectedTargetRuntime",
    "test_mission07_protected_target_enum_contract.py",
    "test_mission07_protected_target_runtime_defaults_contract.py",
)
LEFTOVER_SEARCH_SECTOR_NOT_LOCKED = (
    "ESkyguardSearchSector",
    "GetSearchSector",
    GET_SEARCH_SECTOR,
    "test_search_sector_enum_contract.py",
)
LEFTOVER_SEARCH_TRACK_NOT_LOCKED = (
    "FSkyguardSearchTrackRuntime",
    "test_search_track_runtime_defaults_contract.py",
)
LEFTOVER_NIGHT_BEAT_METHODS_NOT_LOCKED = (
    GET_NIGHT_BEAT_KIT,
    GET_NIGHT_BEAT_KIND,
    GET_NIGHT_BEAT_INDEX,
    TICK_NIGHT_BEAT_KIT,
    "GetNightBeatKit",
    "GetNightBeatKind",
    "GetNightBeatIndex",
    "TickNightBeatKit",
)
LEFTOVER_MISSION07_SIBLING_METHODS_NOT_LOCKED = (
    CLASSIFY_FALSE_TRACK,
    CONFIRM_RADAR_GHOST_IDENTIFICATION,
    NOTIFY_PROTECTED_TARGET_DAMAGE,
    ADVANCE_REINFORCEMENT_TIMER,
    GET_CLASSIFIED_FALSE_TRACK_COUNT,
    IS_HOSTILE_CONTACT_CONFIRMED,
    GET_PROTECTED_TARGET,
    GET_REINFORCEMENT_TIME_REMAINING,
    "ClassifyFalseTrack",
    "ConfirmRadarGhostIdentification",
    "NotifyProtectedTargetDamage",
    "AdvanceReinforcementTimer",
    "GetClassifiedFalseTrackCount",
    "IsHostileContactConfirmed",
    "GetProtectedTarget",
    "GetReinforcementTimeRemaining",
)
WRONG_HARBOR_HEADERS_NOT_SCANNED = (
    "SkyguardPathfinderEncounterController.h",
    "MinHeightFromOriginCm",
    "MaxIntegrity",
    "CurrentIntegrity",
    "SkyguardApacheAircraft.h",
    "ASkyguardApacheAircraft",
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
INVENTED_UFUNCTION = (
    "BlueprintPure",
    "BlueprintAuthorityOnly",
    "CallInEditor",
    "VisibleAnywhere",
    "BlueprintReadOnly",
    "EditAnywhere",
    "BlueprintReadWrite",
    'Category = "Campaign"',
    'Category = "Identity"',
    'Category="Skyguard|Mission01|Environment"',
    'Category="Skyguard|Mission01|Briefing"',
    'Category="Skyguard|Mission01|Integration"',
    'Category="Skyguard|Mission10|Integration"',
    'Category="Skyguard|Mission02|Harbor"',
    'Category="Skyguard|Mission02|Waves"',
    'Category="Skyguard|Mission02|Objectives"',
    'Category="Skyguard|Mission03|Integration"',
    'Category="Skyguard|Mission04|Integration"',
    'Category="Skyguard|Mission05|Integration"',
    'Category="Skyguard|Mission05|Protection"',
    'Category="Skyguard|Mission05|Waves"',
    'Category="Skyguard|Mission06|Waves"',
    'Category="Skyguard|Mission06|Payload"',
    'Category="Skyguard|Mission06|Targets"',
    'Category="Skyguard|Mission06|Objectives"',
    'Category="Skyguard|Mission06|Integration"',
    'Category="Skyguard|Mission07|Integration"',
    'Category="Skyguard|Mission07|Waves"',
    'Category="Skyguard|Mission08|Waves"',
    'Category="Skyguard|Mission08|Hoist"',
    'Category="Skyguard|Mission08|Safety"',
    'Category="Skyguard|Mission08|Protection"',
    'Category="Skyguard|Mission08|Objectives"',
    'Category="Skyguard|Mission08|Rescue"',
    'Category="Skyguard|Mission07|Search"',
    'Category="Skyguard|Mission07|Protection"',
    'Category="Skyguard|Mission07|Objectives"',
    'Category="Skyguard|Mission07|Boss"',
    'Category="Skyguard|Mission09|Integration"',
    'Category="Skyguard|Mission09|Waves"',
    'Category="Skyguard|Mission09|Protection"',
    'Category="Skyguard|Mission09|Performance"',
    'Category="Skyguard|Mission09|Objectives"',
    'Category="Skyguard|Mission10|Integration"',
    'Category="Skyguard|Mission10|Waves"',
    'Category="Skyguard|Mission10|Safety"',
    'Category="Skyguard|Mission10|Protection"',
    'Category="Skyguard|Mission10|Objectives"',
    'Category="Skyguard|Mission10|Evacuation"',
    'Category="Skyguard|Mission10|Campaign"',
)
INVENTED_FIELD_META = (
    "meta =",
    "ClampMin",
)
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "ASkyguardMission02IntegrationDirector::ConfigureMissionDefinition",
    "SkyguardMission02IntegrationDirector.cpp",
    "ASkyguardMission10IntegrationDirector::ConfigureMissionDefinition",
    "SkyguardMission10IntegrationDirector.cpp",
    "ASkyguardMission09IntegrationDirector::ConfigureMissionDefinition",
    "SkyguardMission09IntegrationDirector.cpp",
    "ASkyguardMission08IntegrationDirector::ConfigureMissionDefinition",
    "SkyguardMission08IntegrationDirector.cpp",
)
SIBLING_TYPES = (
    "USkyguardDebriefWidget",
    "USkyguardBriefingWidget",
    "ASkyguardApacheAircraft",
    "ASkyguardRadarNode",
    "ASkyguardBlackKiteBoss",
    "ASkyguardIronRainBoss",
    "ASkyguardRadarGhostBoss",
    "ASkyguardTempestBoss",
    "ASkyguardLastFlightBoss",
    "ASkyguardPatrolShip",
    "FSkyguardSearchlightTrackRuntime",
    "ASkyguardMission01IntegrationDirector",
    "ASkyguardMission03IntegrationDirector",
    "ASkyguardMission04IntegrationDirector",
    "ASkyguardMission05IntegrationDirector",
    "ASkyguardMission06IntegrationDirector",
    "ASkyguardMission07IntegrationDirector",
    "ASkyguardMission08IntegrationDirector",
    "ASkyguardMission09IntegrationDirector",
    "ASkyguardMission10IntegrationDirector",
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


def leftover_spawn_name_tokens() -> tuple[str, ...]:
    mid = "Ya" + "k"
    return (
        f"{mid}SpawnLocation",
        f"{mid}SpawnRotation",
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
    banned = "Ri" + "fle"
    return (
        f"Apply{mid}Strike",
        f"Is{mid}LockEligible",
        f"b{mid}LockEnabled",
        f"OpenSafe{mid}Window",
        f"ArmSafe{banned}EngineFallback",
    )


def leftover_short_roster_values() -> tuple[str, ...]:
    return (
        "Br" + "eak",
        "Ho" + "ld",
        "Cl" + "imb",
        "Des" + "cend",
    )


def unlocked_neighbors() -> tuple[str, ...]:
    return (
        "ASkyguardMission02IntegrationDirector();",
        ROOT_FIELD,
        BRIEFING_FIELD,
        AUDIO_DIRECTOR_FIELD,
        RADIO_CHATTER_FIELD,
        SORTIE_PRESENTATION_FIELD,
        CAMPAIGN_DEFINITION_FIELD,
        MISSION_DEFINITION_FIELD,
        READINESS_FIELD,
        AUTO_INITIALIZE_FIELD,
        ALLOW_BOUNDED_SPAWNING_FIELD,
        AUTO_LAUNCH_AFTER_BRIEFING_FIELD,
        PATHFINDER_SPAWN_LOCATION,
        PATHFINDER_SPAWN_ROTATION,
        ROAD_HUNTER_SPAWN_LOCATION,
        ROAD_HUNTER_SPAWN_ROTATION,
        CONVOY_RUNTIME_ANCHOR,
        INITIALIZE_PLAYABLE_MISSION,
        BIND_CAMPAIGN_RUNTIME,
        GET_POOL_RUNTIME,
        GET_MISSION09_PROTECTED_TARGET,
        GET_MISSION09_WAVE_STATE,
        IRON_RAIN_SPAWN_LOCATION,
        NOTIFY_OBJECTIVE_PROGRESS,
        NOTIFY_PROTECTED_ASSET_FAILED,
        HANDLE_DRONE_CITY_IMPACT,
        START_NEXT_WAVE,
        NOTIFY_FUEL_TERMINAL_DAMAGE,
        GET_CURRENT_WAVE_INDEX,
        GET_FUEL_TERMINAL_INTEGRITY,
        GET_BREAKWATER,
        NOTIFY_THREAT_DESTROYED,
        ADVANCE_CONVOY_BY_DISTANCE,
        NOTIFY_CONVOY_DAMAGE,
        GET_WAVE_STATE,
        GET_CONVOY_ROUTE_STATE,
        GET_DAY_BEAT_KIT,
        GET_NIGHT_BEAT_KIT,
        START_SEARCHLIGHT_WINDOW,
        ADVANCE_SEARCHLIGHT_TRACK,
        NOTIFY_SUBSTATION_DAMAGE,
        GET_REMAINING_THREATS_IN_WAVE,
        GET_SEARCHLIGHT_RUNTIME,
        GET_SUBSTATION_INTEGRITY,
        BLACK_KITE_SPAWN_LOCATION,
        BLACK_KITE_SPAWN_ROTATION,
        SEARCHLIGHT_PORT_FIELD,
        SEARCHLIGHT_STARBOARD_FIELD,
        SYNCHRONIZE_RUNTIME_STATE,
        IS_CORE_PLAYABLE_READY,
        GET_READINESS,
        GET_OBJECTIVE_RUNTIME,
        GET_GUNNER,
        GET_PATHFINDER,
        GET_MISSION_ID,
        VALIDATE_MISSION_CONTRACT,
        BIND_RUNTIME_ACTORS,
        GET_AIRCRAFT,
        CONFIGURE_FROM_MISSION,
        ADVANCE_BRIEFING,
        SET_ASSETS_READY,
        ACKNOWLEDGE_AND_LAUNCH,
        CAN_LAUNCH,
        GET_ELAPSED_SECONDS,
        GET_BRIEFING_STATE,
        GET_MINIMUM_WARMUP_SECONDS,
        GET_BRIEFING_TEXT,
        GET_RADIO_CHATTER,
        WIDGET_CONFIGURE,
        WIDGET_GET_PRESENTATION,
        WIDGET_GET_MISSION_TITLE,
        WIDGET_GET_BRIEFING_TEXT,
        WIDGET_ACKNOWLEDGE_BRIEFING,
        WIDGET_LAUNCH_SORTIE,
        HULL_COLLIDER_FIELD,
        OPTICAL_TRACKER_FIELD,
        WEAPON_SERVO_FIELD,
        COUNTERMEASURE_POD_FIELD,
        ENGINE_FIELD,
        MINIMUM_WEAPON_SEPARATION_FIELD,
        MINIMUM_CIVILIAN_SEPARATION,
        leftover_apply_strike(),
        leftover_is_lock_eligible(),
        START_PHASE_WAVE,
        NOTIFY_PROTECTED_GROUP_DAMAGE,
        GET_MISSION10_ROUTE_PHASE,
        GET_MISSION10_PROTECTED_GROUP,
        GET_SURVIVING_PROTECTED_GROUP_COUNT,
        START_PAYLOAD_WINDOW,
        ADVANCE_PAYLOAD_WINDOW,
        TRY_JAM_ACTIVE_PAYLOAD,
        NOTIFY_AIRFIELD_TARGET_DAMAGE,
        GET_PAYLOAD_WINDOW,
        GET_TARGET_RUNTIME,
        GET_SURVIVING_TARGET_COUNT,
        GET_DAY_BEAT_KIND,
        GET_DAY_BEAT_INDEX,
        TICK_DAY_BEAT_KIT,
        HANDLE_BOSS_PHASE_CHANGED,
        CLASSIFY_FALSE_TRACK,
        CONFIRM_RADAR_GHOST_IDENTIFICATION,
        NOTIFY_PROTECTED_TARGET_DAMAGE,
        ADVANCE_REINFORCEMENT_TIMER,
        GET_SEARCH_SECTOR,
        GET_CLASSIFIED_FALSE_TRACK_COUNT,
        IS_HOSTILE_CONTACT_CONFIRMED,
        GET_PROTECTED_TARGET,
        GET_REINFORCEMENT_TIME_REMAINING,
        GET_NIGHT_BEAT_KIND,
        GET_NIGHT_BEAT_INDEX,
        TICK_NIGHT_BEAT_KIT,
        RADAR_GHOST_SPAWN_LOCATION,
        RADAR_GHOST_SPAWN_ROTATION,
        START_HOIST_WINDOW,
        ADVANCE_HOIST_WINDOW,
        VALIDATE_WEAPON_RELEASE,
        GET_HOIST_RUNTIME,
        GET_REJECTED_WEAPON_RELEASES,
        GET_STORM_RAIN_BEAT_KIT,
        APPLY_STORM_RAIN_PLAY_CONTRACT,
        GET_STORM_RAIN_BEAT_KIND,
        TICK_STORM_RAIN_BEAT_KIT,
        LIFELINE_HUNTER_SPAWN_LOCATION,
        LIFELINE_HUNTER_SPAWN_ROTATION,
        RESCUE_HELICOPTER_ANCHOR,
        HOIST_CABLE_ANCHOR,
        SURVIVORS_ANCHOR,
        RAFTS_ANCHOR,
        RESCUE_VESSEL_ANCHOR,
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


class Mission02ConfigureMissionDefinitionDeclContractTests(unittest.TestCase):
    def test_mission02_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(
            has_declaration(section, CONFIGURE_MISSION_DEFINITION),
            section,
        )

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API ASkyguardUnrelatedDirector "
                ": public AActor\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API AOtherMissionDirector "
            ": public AActor\n"
            "{\n"
            "public:\n"
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
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
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
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
            f"\t{BRIEFING_FIELD}\n"
            "private:\n"
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, CONFIGURE_MISSION_DEFINITION)
        self.assertIn("ConfigureMissionDefinition", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(
            has_declaration(section, CONFIGURE_MISSION_DEFINITION)
        )

    def test_missing_configure_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tASkyguardMission02IntegrationDirector();\n"
            f"\t{ROOT_FIELD}\n"
            f"\t{BRIEFING_FIELD}\n"
            f"\t{AUDIO_DIRECTOR_FIELD}\n"
            f"\t{RADIO_CHATTER_FIELD}\n"
            f"\t{SORTIE_PRESENTATION_FIELD}\n"
            f"\t{CAMPAIGN_DEFINITION_FIELD}\n"
            f"\t{MISSION_DEFINITION_FIELD}\n"
            f"\t{READINESS_FIELD}\n"
            f"\t{AUTO_INITIALIZE_FIELD}\n"
            f"\t{ALLOW_BOUNDED_SPAWNING_FIELD}\n"
            f"\t{AUTO_LAUNCH_AFTER_BRIEFING_FIELD}\n"
            f"\t{PATHFINDER_SPAWN_LOCATION}\n"
            f"\t{INITIALIZE_PLAYABLE_MISSION}\n"
            f"\t{NOTIFY_OBJECTIVE_PROGRESS}\n"
            f"\t{NOTIFY_PROTECTED_ASSET_FAILED}\n"
            f"\t{SYNCHRONIZE_RUNTIME_STATE}\n"
            f"\t{IS_CORE_PLAYABLE_READY}\n"
            f"\t{GET_READINESS}\n"
            f"\t{GET_OBJECTIVE_RUNTIME}\n"
            f"\t{GET_GUNNER}\n"
            f"\t{GET_PATHFINDER}\n"
            f"\t{GET_MISSION_ID}\n"
            f"\t{VALIDATE_MISSION_CONTRACT}\n"
            f"\t{CONFIGURE_FROM_MISSION}\n"
            f"\t{ADVANCE_BRIEFING}\n"
            f"\t{SET_ASSETS_READY}\n"
            f"\t{ACKNOWLEDGE_AND_LAUNCH}\n"
            f"\t{CAN_LAUNCH}\n"
            f"\t{GET_BRIEFING_STATE}\n"
            f"\t{GET_BRIEFING_TEXT}\n"
            f"\t{GET_RADIO_CHATTER}\n"
            f"\t{WIDGET_GET_PRESENTATION}\n"
            f"\t{WIDGET_LAUNCH_SORTIE}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, CONFIGURE_MISSION_DEFINITION)
        self.assertIn("ConfigureMissionDefinition", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_INTEGRATION}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, CONFIGURE_MISSION_DEFINITION)
        self.assertIn("ConfigureMissionDefinition", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_INTEGRATION, section)
        self.assertIn("BlueprintCallable", section)
        self.assertIn(
            'Category="Skyguard|Mission02|Integration"',
            section,
        )
        self.assertTrue(
            has_declaration(section, CONFIGURE_MISSION_DEFINITION),
            section,
        )
        self.assertNotIn("UFUNCTION", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("BlueprintCallable", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("Category", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("BlueprintPure", UFUNCTION_INTEGRATION)
        self.assertIn("Skyguard|Mission02|Integration", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission01", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission03", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission04", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission05", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission06", UFUNCTION_INTEGRATION)
        self.assertNotIn("Waves", UFUNCTION_INTEGRATION)
        self.assertNotIn("Search", UFUNCTION_INTEGRATION)
        self.assertNotIn("Protection", UFUNCTION_INTEGRATION)
        self.assertNotIn("Payload", UFUNCTION_INTEGRATION)
        self.assertNotIn("Targets", UFUNCTION_INTEGRATION)
        self.assertNotIn("Objectives", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission07", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission08", UFUNCTION_INTEGRATION)
        self.assertNotIn("Hoist", UFUNCTION_INTEGRATION)
        self.assertNotIn("Performance", UFUNCTION_INTEGRATION)
        self.assertNotIn("Safety", UFUNCTION_INTEGRATION)
        self.assertNotIn("Rescue", UFUNCTION_INTEGRATION)
        self.assertIn("BlueprintCallable", UFUNCTION_INTEGRATION)
        self.assertNotIn("Environment", UFUNCTION_INTEGRATION)
        self.assertNotIn("Briefing", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission10", UFUNCTION_INTEGRATION)
        self.assertNotIn("Boss", UFUNCTION_INTEGRATION)
        self.assertNotIn("Destruction", UFUNCTION_INTEGRATION)
        self.assertNotIn("Apache", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission06", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission07", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission09", UFUNCTION_INTEGRATION)
        self.assertNotIn("Evacuation", UFUNCTION_INTEGRATION)
        self.assertNotIn("Campaign", UFUNCTION_INTEGRATION)
        self.assertNotIn("Encounter", UFUNCTION_INTEGRATION)
        self.assertNotIn("Safety", UFUNCTION_INTEGRATION)
        self.assertNotIn("Hoist", UFUNCTION_INTEGRATION)
        self.assertNotIn("Rescue", UFUNCTION_INTEGRATION)
        for invented in INVENTED_UFUNCTION:
            self.assertNotIn(invented, UFUNCTION_INTEGRATION)
            self.assertNotIn(invented, CONFIGURE_MISSION_DEFINITION)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, UFUNCTION_INTEGRATION)
            self.assertNotIn(invented, CONFIGURE_MISSION_DEFINITION)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tASkyguardMission02IntegrationDirector();\n"
            f"\t{ROOT_FIELD}\n"
            f"\t{BRIEFING_FIELD}\n"
            f"\t{AUDIO_DIRECTOR_FIELD}\n"
            f"\t{RADIO_CHATTER_FIELD}\n"
            f"\t{SORTIE_PRESENTATION_FIELD}\n"
            f"\t{CAMPAIGN_DEFINITION_FIELD}\n"
            f"\t{MISSION_DEFINITION_FIELD}\n"
            f"\t{READINESS_FIELD}\n"
            f"\t{AUTO_INITIALIZE_FIELD}\n"
            f"\t{ALLOW_BOUNDED_SPAWNING_FIELD}\n"
            f"\t{AUTO_LAUNCH_AFTER_BRIEFING_FIELD}\n"
            f"\t{INITIALIZE_PLAYABLE_MISSION}\n"
            f"\t{NOTIFY_OBJECTIVE_PROGRESS}\n"
            f"\t{NOTIFY_PROTECTED_ASSET_FAILED}\n"
            f"\t{SYNCHRONIZE_RUNTIME_STATE}\n"
            f"\t{IS_CORE_PLAYABLE_READY}\n"
            f"\t{GET_READINESS}\n"
            f"\t{GET_OBJECTIVE_RUNTIME}\n"
            f"\t{GET_GUNNER}\n"
            f"\t{GET_PATHFINDER}\n"
            f"\t{GET_MISSION_ID}\n"
            f"\t{VALIDATE_MISSION_CONTRACT}\n"
            f"\t{CONFIGURE_FROM_MISSION}\n"
            f"\t{ADVANCE_BRIEFING}\n"
            f"\t{SET_ASSETS_READY}\n"
            f"\t{ACKNOWLEDGE_AND_LAUNCH}\n"
            f"\t{CAN_LAUNCH}\n"
            f"\t{GET_ELAPSED_SECONDS}\n"
            f"\t{GET_BRIEFING_STATE}\n"
            f"\t{GET_MINIMUM_WARMUP_SECONDS}\n"
            f"\t{GET_BRIEFING_TEXT}\n"
            f"\t{GET_RADIO_CHATTER}\n"
            f"\t{WIDGET_CONFIGURE}\n"
            f"\t{WIDGET_GET_PRESENTATION}\n"
            f"\t{WIDGET_GET_MISSION_TITLE}\n"
            f"\t{WIDGET_GET_BRIEFING_TEXT}\n"
            f"\t{WIDGET_ACKNOWLEDGE_BRIEFING}\n"
            f"\t{WIDGET_LAUNCH_SORTIE}\n"
            f"\t{HULL_COLLIDER_FIELD}\n"
            f"\t{OPTICAL_TRACKER_FIELD}\n"
            "\tFVector GetChinMuzzleLocation() const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, CONFIGURE_MISSION_DEFINITION)
        self.assertIn("ConfigureMissionDefinition", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_arg = "\tbool ConfigureMissionDefinition();\n"
        as_void = (
            "\tvoid ConfigureMissionDefinition("
            "USkyguardMissionDefinition* Mission);\n"
        )
        as_const = (
            "\tbool ConfigureMissionDefinition("
            "USkyguardMissionDefinition* Mission) const;\n"
        )
        const_ptr = (
            "\tbool ConfigureMissionDefinition("
            "const USkyguardMissionDefinition* Mission);\n"
        )
        by_ref = (
            "\tbool ConfigureMissionDefinition("
            "USkyguardMissionDefinition& Mission);\n"
        )
        leftover_initialize = f"\t{INITIALIZE_PLAYABLE_MISSION}\n"
        leftover_notify = f"\t{NOTIFY_OBJECTIVE_PROGRESS}\n"
        leftover_failed = f"\t{NOTIFY_PROTECTED_ASSET_FAILED}\n"
        leftover_sync = f"\t{SYNCHRONIZE_RUNTIME_STATE}\n"
        leftover_ready = f"\t{IS_CORE_PLAYABLE_READY}\n"
        leftover_readiness = f"\t{GET_READINESS}\n"
        leftover_objective = f"\t{GET_OBJECTIVE_RUNTIME}\n"
        leftover_gunner = f"\t{GET_GUNNER}\n"
        leftover_pathfinder = f"\t{GET_PATHFINDER}\n"
        leftover_mission_id = f"\t{GET_MISSION_ID}\n"
        leftover_validate = f"\t{VALIDATE_MISSION_CONTRACT}\n"
        leftover_bind = f"\t{BIND_RUNTIME_ACTORS}();\n"
        leftover_get_aircraft = f"\t{GET_AIRCRAFT}() const;\n"
        leftover_impact = f"\t{HANDLE_DRONE_CITY_IMPACT}\n"
        leftover_wave_start = f"\t{START_NEXT_WAVE}\n"
        leftover_threat = f"\t{NOTIFY_THREAT_DESTROYED}\n"
        leftover_convoy = f"\t{ADVANCE_CONVOY_BY_DISTANCE}\n"
        leftover_convoy_dmg = f"\t{NOTIFY_CONVOY_DAMAGE}\n"
        leftover_wave_state = f"\t{GET_WAVE_STATE}\n"
        leftover_convoy_state = f"\t{GET_CONVOY_ROUTE_STATE}\n"
        leftover_day_kit = f"\t{GET_DAY_BEAT_KIT}\n"
        leftover_night_kit = f"\t{GET_NIGHT_BEAT_KIT}\n"
        leftover_search_window = f"\t{START_SEARCHLIGHT_WINDOW}\n"
        leftover_search_track = f"\t{ADVANCE_SEARCHLIGHT_TRACK}\n"
        leftover_substation = f"\t{NOTIFY_SUBSTATION_DAMAGE}\n"
        leftover_remaining = f"\t{GET_REMAINING_THREATS_IN_WAVE}\n"
        leftover_search_runtime = f"\t{GET_SEARCHLIGHT_RUNTIME}\n"
        leftover_integrity = f"\t{GET_SUBSTATION_INTEGRITY}\n"
        leftover_kite_loc = f"\t{BLACK_KITE_SPAWN_LOCATION}\n"
        leftover_kite_rot = f"\t{BLACK_KITE_SPAWN_ROTATION}\n"
        leftover_anchor = f"\t{CONVOY_RUNTIME_ANCHOR}\n"
        leftover_road_loc = f"\t{ROAD_HUNTER_SPAWN_LOCATION}\n"
        leftover_road_rot = f"\t{ROAD_HUNTER_SPAWN_ROTATION}\n"
        leftover_root = f"\t{ROOT_FIELD}\n"
        leftover_briefing = f"\t{BRIEFING_FIELD}\n"
        leftover_audio = f"\t{AUDIO_DIRECTOR_FIELD}\n"
        leftover_radio = f"\t{RADIO_CHATTER_FIELD}\n"
        leftover_sortie = f"\t{SORTIE_PRESENTATION_FIELD}\n"
        leftover_campaign = f"\t{CAMPAIGN_DEFINITION_FIELD}\n"
        leftover_mission = f"\t{MISSION_DEFINITION_FIELD}\n"
        leftover_readiness_field = f"\t{READINESS_FIELD}\n"
        leftover_auto = f"\t{AUTO_INITIALIZE_FIELD}\n"
        leftover_allow = f"\t{ALLOW_BOUNDED_SPAWNING_FIELD}\n"
        leftover_launch = f"\t{AUTO_LAUNCH_AFTER_BRIEFING_FIELD}\n"
        leftover_path_loc = f"\t{PATHFINDER_SPAWN_LOCATION}\n"
        leftover_path_rot = f"\t{PATHFINDER_SPAWN_ROTATION}\n"
        leftover_from_mission = f"\t{CONFIGURE_FROM_MISSION}\n"
        leftover_advance = f"\t{ADVANCE_BRIEFING}\n"
        leftover_assets = f"\t{SET_ASSETS_READY}\n"
        leftover_ack = f"\t{ACKNOWLEDGE_AND_LAUNCH}\n"
        leftover_can = f"\t{CAN_LAUNCH}\n"
        leftover_elapsed = f"\t{GET_ELAPSED_SECONDS}\n"
        leftover_state = f"\t{GET_BRIEFING_STATE}\n"
        leftover_warmup = f"\t{GET_MINIMUM_WARMUP_SECONDS}\n"
        leftover_text = f"\t{GET_BRIEFING_TEXT}\n"
        leftover_chatter = f"\t{GET_RADIO_CHATTER}\n"
        leftover_widget_cfg = f"\t{WIDGET_CONFIGURE}\n"
        leftover_widget_pres = f"\t{WIDGET_GET_PRESENTATION}\n"
        leftover_widget_title = f"\t{WIDGET_GET_MISSION_TITLE}\n"
        leftover_widget_text = f"\t{WIDGET_GET_BRIEFING_TEXT}\n"
        leftover_widget_ack = f"\t{WIDGET_ACKNOWLEDGE_BRIEFING}\n"
        leftover_widget_launch = f"\t{WIDGET_LAUNCH_SORTIE}\n"
        leftover_hull = f"\t{HULL_COLLIDER_FIELD}\n"
        leftover_optical = f"\t{OPTICAL_TRACKER_FIELD}\n"
        leftover_servo = f"\t{WEAPON_SERVO_FIELD}\n"
        leftover_pod = f"\t{COUNTERMEASURE_POD_FIELD}\n"
        leftover_engine = f"\t{ENGINE_FIELD}\n"
        leftover_weapon_sep = f"\t{MINIMUM_WEAPON_SEPARATION_FIELD}\n"
        leftover_civilian = f"\t{MINIMUM_CIVILIAN_SEPARATION}\n"
        leftover_strike = f"\t{leftover_apply_strike()}\n"
        leftover_lock = f"\t{leftover_is_lock_eligible()}\n"
        leftover_radar = "\tTObjectPtr<UStaticMeshComponent> RadarNode;\n"
        leftover_muzzle = "\tFVector GetChinMuzzleLocation() const;\n"
        leftover_wave = "\tESkyguardMission02WaveState WaveState;\n"
        leftover_skyline = "\tESkyguardMissionSkylineStyle Skyline;\n"
        leftover_fill = "\tvoid FillResultCombatStats();\n"
        leftover_finalize = "\tvoid FillAndFinalize();\n"
        leftover_fail = "\tvoid FillAndFail();\n"
        for region in (
            missing_arg,
            as_void,
            as_const,
            const_ptr,
            by_ref,
            leftover_initialize,
            leftover_notify,
            leftover_failed,
            leftover_sync,
            leftover_ready,
            leftover_readiness,
            leftover_objective,
            leftover_gunner,
            leftover_pathfinder,
            leftover_mission_id,
            leftover_validate,
            leftover_bind,
            leftover_get_aircraft,
            leftover_impact,
            leftover_wave_start,
            leftover_threat,
            leftover_convoy,
            leftover_convoy_dmg,
            leftover_wave_state,
            leftover_convoy_state,
            leftover_day_kit,
            leftover_night_kit,
            leftover_search_window,
            leftover_search_track,
            leftover_substation,
            leftover_remaining,
            leftover_search_runtime,
            leftover_integrity,
            leftover_kite_loc,
            leftover_kite_rot,
            leftover_anchor,
            leftover_road_loc,
            leftover_road_rot,
            leftover_root,
            leftover_briefing,
            leftover_audio,
            leftover_radio,
            leftover_sortie,
            leftover_campaign,
            leftover_mission,
            leftover_readiness_field,
            leftover_auto,
            leftover_allow,
            leftover_launch,
            leftover_path_loc,
            leftover_path_rot,
            leftover_from_mission,
            leftover_advance,
            leftover_assets,
            leftover_ack,
            leftover_can,
            leftover_elapsed,
            leftover_state,
            leftover_warmup,
            leftover_text,
            leftover_chatter,
            leftover_widget_cfg,
            leftover_widget_pres,
            leftover_widget_title,
            leftover_widget_text,
            leftover_widget_ack,
            leftover_widget_launch,
            leftover_hull,
            leftover_optical,
            leftover_servo,
            leftover_pod,
            leftover_engine,
            leftover_weapon_sep,
            leftover_civilian,
            leftover_strike,
            leftover_lock,
            leftover_radar,
            leftover_muzzle,
            leftover_wave,
            leftover_skyline,
            leftover_fill,
            leftover_finalize,
            leftover_fail,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CONFIGURE_MISSION_DEFINITION)
            self.assertIn("ConfigureMissionDefinition", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_configure_mission_definition_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, CONFIGURE_MISSION_DEFINITION),
            CONFIGURE_MISSION_DEFINITION,
        )
        self.assertTrue(has_declaration(section, CONFIGURE_MISSION_DEFINITION))
        self.assertEqual(
            declaration_count(section, CONFIGURE_MISSION_DEFINITION),
            1,
        )
        self.assertTrue(
            CONFIGURE_MISSION_DEFINITION.startswith("bool "),
            CONFIGURE_MISSION_DEFINITION,
        )
        self.assertTrue(
            CONFIGURE_MISSION_DEFINITION.endswith(";"),
            CONFIGURE_MISSION_DEFINITION,
        )
        self.assertIn("ConfigureMissionDefinition", CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "USkyguardMissionDefinition* Mission",
            CONFIGURE_MISSION_DEFINITION,
        )
        self.assertNotIn("TArray<", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("TObjectPtr", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("TSoftObjectPtr", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("INDEX_NONE", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("UFUNCTION", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("{", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("}", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("return ", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("const;", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("Root", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("Briefing", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("AudioDirector", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("RadioChatter", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("SortiePresentation", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("CampaignDefinition", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("Readiness", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("bAutoInitialize", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("bAllowBoundedActorSpawning", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("bAutoLaunchAfterBriefing", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("PathfinderSpawnLocation", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetAircraft", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("BindRuntimeActors", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("HandleDroneCityImpact", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("StartNextWave", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("NotifyThreatDestroyed", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("AdvanceConvoyByDistance", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("NotifyConvoyDamage", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetWaveState", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetConvoyRouteState", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetDayBeatKit", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetNightBeatKit", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("StartSearchlightWindow", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("AdvanceSearchlightTrack", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("NotifySubstationDamage", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetRemainingThreatsInWave", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetSearchlightRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetSubstationIntegrity", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("StartPayloadWindow", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("AdvancePayloadWindow", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("TryJamActivePayload", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("NotifyAirfieldTargetDamage", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetPayloadWindow", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetTargetRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetSurvivingTargetCount", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetDayBeatKind", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetDayBeatIndex", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("TickDayBeatKit", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("HandleBossPhaseChanged", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardMission04IntegrationDirector", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardMission05IntegrationDirector", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardMission06IntegrationDirector", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ESkyguardMission06WaveState", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ESkyguardMission07WaveState", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardMission07IntegrationDirector", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardMission08IntegrationDirector", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ESkyguardMission08WaveState", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ESkyguardMission09WaveState", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ESkyguardMission09ProtectedTarget", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("FSkyguardMission09ProtectedTargetRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("FSkyguardMission09PoolRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("FSkyguardMission09PoolBudget", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("BindCampaignRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetPoolRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("IronRainSpawnLocation", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ESkyguardMission08ProtectedTarget", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("FSkyguardMission08ProtectedTargetRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("FSkyguardHoistWindowRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("StartHoistWindow", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("AdvanceHoistWindow", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ValidateWeaponRelease", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetHoistRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetRejectedWeaponReleases", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetStormRainBeatKit", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ApplyStormRainPlayContract", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetStormRainBeatKind", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("TickStormRainBeatKit", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("RescueHelicopterAnchor", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("LifelineHunterSpawnLocation", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ESkyguardMission07ProtectedTarget", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("FSkyguardMission07ProtectedTargetRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ESkyguardSearchSector", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("FSkyguardSearchTrackRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ClassifyFalseTrack", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ConfirmRadarGhostIdentification", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("NotifyProtectedTargetDamage", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("AdvanceReinforcementTimer", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetSearchSector", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetClassifiedFalseTrackCount", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("IsHostileContactConfirmed", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetProtectedTarget", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetReinforcementTimeRemaining", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetNightBeatKind", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetNightBeatIndex", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("TickNightBeatKit", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ESkyguardAirfieldTarget", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("FSkyguardPayloadWindowRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardMission03IntegrationDirector", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ConvoyRuntimeAnchor", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("RoadHunterSpawnLocation", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardMission01IntegrationDirector", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardMission10IntegrationDirector", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("InitializePlayableMission", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("NotifyObjectiveProgress", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("NotifyProtectedAssetFailed", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("SynchronizeRuntimeState", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("IsCorePlayableReady", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetReadiness", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetObjectiveRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetGunner", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetPathfinder", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetMissionId", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ValidateMissionContract", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ConfigureFromMission", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("AdvanceBriefing", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("SetAssetsReady", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("AcknowledgeAndLaunch", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("CanLaunch", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetElapsedSeconds", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetBriefingState", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetMinimumWarmupSeconds", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetBriefingText", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetRadioChatter", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetPresentation", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetMissionTitle", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("AcknowledgeBriefing", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("LaunchSortie", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("HullCollider", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("OpticalTracker", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("WeaponServo", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("CountermeasurePod", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("MinHeightFromOriginCm", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("RadarNode", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ESkyguardMission02WaveState", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("HarborIndustrial", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("MaxIntegrity", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("CurrentIntegrity", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("FillAndFinalize", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("FillAndFail", CONFIGURE_MISSION_DEFINITION)
        for name in leftover_live_copy_method_names():
            self.assertNotIn(name, CONFIGURE_MISSION_DEFINITION)
        for name in leftover_spawn_name_tokens():
            self.assertNotIn(name, CONFIGURE_MISSION_DEFINITION)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tbool\n"
            "\tConfigureMissionDefinition(USkyguardMissionDefinition* Mission);\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tbool   ConfigureMissionDefinition(USkyguardMissionDefinition* Mission);\n"
            "private:\n"
            "};\n"
        )
        wrap_tab = (
            "public:\n"
            "\tbool\t"
            "ConfigureMissionDefinition(USkyguardMissionDefinition* Mission);\n"
            "};\n"
        )
        wrap_indent = (
            "public:\n"
            "\tbool\n"
            "\t\tConfigureMissionDefinition(USkyguardMissionDefinition* Mission);\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tbool ConfigureMissionDefinition(\n"
            "\t\tUSkyguardMissionDefinition* Mission);\n"
            "};\n"
        )
        wrap_ufunction = (
            "public:\n"
            f"\t{UFUNCTION_INTEGRATION}\n"
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            "};\n"
        )
        wrap_ufunction_one_line = (
            "public:\n"
            f"\t{UFUNCTION_INTEGRATION} {CONFIGURE_MISSION_DEFINITION}\n"
            "};\n"
        )
        wrap_ufunction_category = (
            "public:\n"
            "\tUFUNCTION(BlueprintCallable,\n"
            '\t\tCategory="Skyguard|Mission02|Integration")\n'
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            "};\n"
        )
        wrap_ufunction_split_specifiers = (
            "public:\n"
            "\tUFUNCTION(\n"
            "\t\tBlueprintCallable,\n"
            '\t\tCategory="Skyguard|Mission02|Integration")\n'
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
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
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_name}"
        )
        header_wrap_ufunction = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_ufunction}"
        )
        header_wrap_ufunction_one_line = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_ufunction_one_line}"
        )
        header_wrap_ufunction_category = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_ufunction_category}"
        )
        header_wrap_ufunction_split_specifiers = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public AActor\n{{\n{wrap_ufunction_split_specifiers}"
        )
        for header in (
            header_wrap_type,
            header_wrap_spaces,
            header_wrap_tab,
            header_wrap_indent,
            header_wrap_name,
            header_wrap_ufunction,
            header_wrap_ufunction_one_line,
            header_wrap_ufunction_category,
            header_wrap_ufunction_split_specifiers,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, CONFIGURE_MISSION_DEFINITION),
                section,
            )
            self.assertEqual(
                require_declaration(section, CONFIGURE_MISSION_DEFINITION),
                CONFIGURE_MISSION_DEFINITION,
            )
            self.assertEqual(
                declaration_count(section, CONFIGURE_MISSION_DEFINITION),
                1,
            )
        one_line = f"{{\npublic:\n\t{CONFIGURE_MISSION_DEFINITION}\n}}\n"
        self.assertTrue(has_declaration(one_line, CONFIGURE_MISSION_DEFINITION))
        section = public_section(origin_main_header())
        self.assertTrue(
            has_declaration(section, CONFIGURE_MISSION_DEFINITION),
            section,
        )
        self.assertEqual(
            require_declaration(section, CONFIGURE_MISSION_DEFINITION),
            CONFIGURE_MISSION_DEFINITION,
        )
        self.assertIn(UFUNCTION_INTEGRATION, section)

    def test_environment_category_does_not_satisfy_integration(self) -> None:
        self.assertNotIn("Environment", UFUNCTION_INTEGRATION)
        self.assertNotIn("Briefing", UFUNCTION_INTEGRATION)
        environment = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission01|Environment")'
        )
        briefing = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission01|Briefing")'
        )
        self.assertNotEqual(environment, UFUNCTION_INTEGRATION)
        self.assertNotEqual(briefing, UFUNCTION_INTEGRATION)
        self.assertNotIn(environment, UFUNCTION_INTEGRATION)
        self.assertNotIn(briefing, UFUNCTION_INTEGRATION)
        leftover_m01 = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission01|Integration")'
        )
        leftover_m10 = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission10|Integration")'
        )
        leftover_harbor = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission02|Harbor")'
        )
        leftover_m03 = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission03|Integration")'
        )
        leftover_m04 = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission04|Integration")'
        )
        leftover_m05 = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission05|Integration")'
        )
        leftover_m06 = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission06|Integration")'
        )
        leftover_m07 = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission07|Integration")'
        )
        leftover_m08 = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission08|Integration")'
        )
        leftover_m09 = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission09|Integration")'
        )
        leftover_m10_waves = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission10|Waves")'
        )
        leftover_m10_safety = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission10|Safety")'
        )
        leftover_m10_protection = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission10|Protection")'
        )
        leftover_m09_waves = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission09|Waves")'
        )
        leftover_m09_pool = (
            'UFUNCTION(BlueprintPure, '
            'Category="Skyguard|Mission09|Performance")'
        )
        leftover_hoist = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission08|Hoist")'
        )
        leftover_safety = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission08|Safety")'
        )
        leftover_waves = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission06|Waves")'
        )
        leftover_payload = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission06|Payload")'
        )
        leftover_targets = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission06|Targets")'
        )
        leftover_objectives = (
            'UFUNCTION(BlueprintCallable, '
            'Category="Skyguard|Mission06|Objectives")'
        )
        self.assertNotEqual(leftover_m01, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_m10, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_harbor, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_m03, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_m04, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_m05, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_m06, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_m07, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_m08, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_m09, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_m09_waves, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_m10_waves, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_m10_safety, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_m10_protection, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_m09_pool, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_hoist, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_safety, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_waves, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_payload, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_targets, UFUNCTION_INTEGRATION)
        self.assertNotEqual(leftover_objectives, UFUNCTION_INTEGRATION)
        self.assertNotIn(leftover_m01, UFUNCTION_INTEGRATION)
        self.assertNotIn(leftover_m10, UFUNCTION_INTEGRATION)
        self.assertNotIn(leftover_harbor, UFUNCTION_INTEGRATION)
        self.assertNotIn(leftover_m03, UFUNCTION_INTEGRATION)
        self.assertNotIn(leftover_m04, UFUNCTION_INTEGRATION)
        self.assertNotIn(leftover_m05, UFUNCTION_INTEGRATION)
        self.assertNotIn(leftover_m06, UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission01", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission03", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission04", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission05", UFUNCTION_INTEGRATION)
        self.assertNotIn("Mission08", UFUNCTION_INTEGRATION)
        self.assertNotIn("Waves", UFUNCTION_INTEGRATION)
        self.assertNotIn("Performance", UFUNCTION_INTEGRATION)
        self.assertNotIn("Search", UFUNCTION_INTEGRATION)
        self.assertNotIn("Protection", UFUNCTION_INTEGRATION)
        self.assertNotIn("Payload", UFUNCTION_INTEGRATION)
        self.assertNotIn("Targets", UFUNCTION_INTEGRATION)
        self.assertNotIn("Objectives", UFUNCTION_INTEGRATION)

    def test_declaration_does_not_invent_ufunction_metadata(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for invented in INVENTED_UFUNCTION:
            self.assertNotIn(invented, CONFIGURE_MISSION_DEFINITION)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UFUNCTION_INTEGRATION)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, CONFIGURE_MISSION_DEFINITION)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UFUNCTION_INTEGRATION)
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_INTEGRATION, section)
        self.assertTrue(
            has_declaration(section, CONFIGURE_MISSION_DEFINITION),
            section,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", CONFIGURE_MISSION_DEFINITION)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_configure_mission_definition_cpp_body(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        self.assertNotIn("{", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("}", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("return ", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn(
            "ASkyguardMission02IntegrationDirector::ConfigureMissionDefinition",
            CONFIGURE_MISSION_DEFINITION,
        )
        self.assertNotIn(
            "SkyguardMission02IntegrationDirector.cpp",
            CONFIGURE_MISSION_DEFINITION,
        )
        self.assertNotIn(
            "SkyguardMission02IntegrationDirector.cpp",
            locked_only,
        )
        self.assertNotIn("return false", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("return true", CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_sibling_director_fields(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in SIBLING_DIRECTOR_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn("ConfigureMissionDefinition", CONFIGURE_MISSION_DEFINITION)
        self.assertTrue(CONFIGURE_MISSION_DEFINITION.startswith("bool "))

    def test_contract_does_not_relock_sibling_integration_methods(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in SIBLING_INTEGRATION_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission01_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_get_aircraft_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_bind_runtime_actors"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission02_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission03_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission03_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission04_wave_state_enum_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_searchlight_track_runtime_defaults"
            "_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission03_handle_drone_city_impact"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission03_bind_runtime_actors"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_spawn_locations(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_SPAWN_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        for token in leftover_spawn_name_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_leftover_get_aircraft(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        self.assertNotIn(GET_AIRCRAFT, locked_only)
        self.assertNotIn(GET_AIRCRAFT, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn(BIND_RUNTIME_ACTORS, locked_only)
        self.assertNotIn(BIND_RUNTIME_ACTORS, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission01_get_aircraft_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_briefing_methods(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_BRIEFING_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_leftover_briefing_widget(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_BRIEFING_WIDGET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_leftover_briefing_defaults(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_BRIEFING_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_leftover_audio_director_fail_closed(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_AUDIO_DIRECTOR_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_audio_director_listener_perspective"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_audio_director_telemetry"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_audio_director_suppression"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_audio_director_engine_state"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_audio_director_bank_null"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_audio_director_world_event"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("SkyguardAudioDirectorComponent.h", locked_only)
        self.assertNotIn("SetListenerPerspective", locked_only)
        self.assertNotIn("TriggerWorldEvent", locked_only)

    def test_contract_does_not_relock_leftover_radio_chatter_fail_closed(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_RADIO_CHATTER_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_radio_chatter_empty"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_radio_chatter_empty_queue"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_radio_chatter_empty_line"
            "_tests.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("SkyguardRadioChatterComponent.h", locked_only)

    def test_contract_does_not_relock_leftover_campaign_definition_methods(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_CAMPAIGN_DEFINITION_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_campaign_definition_missions"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_find_mission_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_validate_definition_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_harbor_scripts(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_HARBOR_SCRIPTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_campaign_theater_kit_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_readable_escalation.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_harbor_proof_play.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_environment_readiness(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_ENVIRONMENT_READINESS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission01_environment_readiness"
            "_defaults_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_environment_readiness_defaults_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_mission02_wave_state(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION02_WAVE_STATE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn(
            "ESkyguardMission02WaveState",
            CONFIGURE_MISSION_DEFINITION,
        )

    def test_contract_does_not_relock_leftover_mission04_wave_state_enum(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION04_WAVE_STATE_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission04_wave_state_enum_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_searchlight_runtime(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetSearchlightRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_searchlight_track_runtime_defaults"
            "_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_skyline_harbor_industrial(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_SKYLINE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
            self.assertNotIn(token, section)
        self.assertNotIn("HarborIndustrial", CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_leftover_lifeline_hunter(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_leftover_apache(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_APACHE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_leftover_patrol_ship(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_PATROL_SHIP_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_leftover_radar_node(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_RADAR_NODE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_leftover_fill_and_gunner(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_scan_wrong_harbor_headers(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in WRONG_HARBOR_HEADERS_NOT_SCANNED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("MinHeightFromOriginCm", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("MaxIntegrity", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("CurrentIntegrity", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("SkyguardApacheAircraft.h", CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_scan_apache_public_section_for_harbor(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        file_text = this_file_text()
        apache_header = "SkyguardApacheAircraft.h"
        self.assertNotIn(apache_header, locked_only)
        self.assertNotIn(apache_header, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardApacheAircraft", locked_only)
        self.assertNotIn("ASkyguardApacheAircraft", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn(f"origin/main:{apache_header}", file_text)
        self.assertNotIn(f"git show origin/main:{apache_header}", file_text)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_minimum_civilian_separation_is_not_harbor_40_80(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        section = public_section(origin_main_header())
        adjacent = "MinimumCivilianSeparationMeters = 550.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        for token in HARBOR_ADJACENT_CIVILIAN_SEPARATION:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        for token in HARBOR_ADJACENT_NOT_LOCKED:
            self.assertNotIn(token, leftover_harbor_tokens())
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("MinimumCivilianSeparationMeters", section)
        # Leftover Mission10 MinimumWeaponSeparationMeters = 550.f
        # is Harbor-adjacent, not Harbor 40/80, and is not locked.
        self.assertNotIn("550.f", CONFIGURE_MISSION_DEFINITION)

    def test_harbor_adjacent_fields_are_not_harbor_40_80(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        adjacent_civilian = "MinimumCivilianSeparationMeters = 550.f"
        adjacent_weapon = "MinimumWeaponSeparationMeters = 450.f"
        for token in leftover_harbor_tokens():
            self.assertNotEqual(token, adjacent_civilian)
            self.assertNotEqual(token, adjacent_weapon)
            self.assertNotEqual(token, "550.f")
            self.assertNotEqual(token, "450.f")
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        self.assertEqual(
            require_declaration(locked_only, CONFIGURE_MISSION_DEFINITION),
            CONFIGURE_MISSION_DEFINITION,
        )
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("Root;", locked_only)
        self.assertNotIn("Briefing", locked_only)
        self.assertNotIn("AudioDirector", locked_only)
        self.assertNotIn("RadioChatter", locked_only)
        self.assertNotIn("SortiePresentation", locked_only)
        self.assertNotIn("CampaignDefinition", locked_only)
        self.assertNotIn("Readiness", locked_only)
        self.assertNotIn("bAutoInitialize", locked_only)
        self.assertNotIn("bAllowBoundedActorSpawning", locked_only)
        self.assertNotIn("bAutoLaunchAfterBriefing", locked_only)
        self.assertNotIn("PathfinderSpawnLocation", locked_only)
        self.assertNotIn("GetAircraft", locked_only)
        self.assertNotIn("BindRuntimeActors", locked_only)
        self.assertNotIn("InitializePlayableMission", locked_only)
        self.assertNotIn("NotifyObjectiveProgress", locked_only)
        self.assertNotIn("NotifyProtectedAssetFailed", locked_only)
        self.assertNotIn("SynchronizeRuntimeState", locked_only)
        self.assertNotIn("IsCorePlayableReady", locked_only)
        self.assertNotIn("GetReadiness", locked_only)
        self.assertNotIn("GetObjectiveRuntime", locked_only)
        self.assertNotIn("GetGunner", locked_only)
        self.assertNotIn("GetPathfinder", locked_only)
        self.assertNotIn("GetMissionId", locked_only)
        self.assertNotIn("ValidateMissionContract", locked_only)
        self.assertNotIn("ConfigureFromMission", locked_only)
        self.assertNotIn("AdvanceBriefing", locked_only)
        self.assertNotIn("SetAssetsReady", locked_only)
        self.assertNotIn("AcknowledgeAndLaunch", locked_only)
        self.assertNotIn("CanLaunch", locked_only)
        self.assertNotIn("GetElapsedSeconds", locked_only)
        self.assertNotIn("GetBriefingState", locked_only)
        self.assertNotIn("GetMinimumWarmupSeconds", locked_only)
        self.assertNotIn("GetBriefingText", locked_only)
        self.assertNotIn("GetRadioChatter", locked_only)
        self.assertNotIn("GetPresentation", locked_only)
        self.assertNotIn("GetMissionTitle", locked_only)
        self.assertNotIn("AcknowledgeBriefing", locked_only)
        self.assertNotIn("LaunchSortie", locked_only)
        self.assertNotIn("HullCollider", locked_only)
        self.assertNotIn("OpticalTracker", locked_only)
        self.assertNotIn("SkyguardAudioDirectorComponent.h", locked_only)
        self.assertNotIn(
            "SkyguardPathfinderEncounterController.h",
            locked_only,
        )
        for name in leftover_live_copy_method_names():
            self.assertNotIn(name, locked_only)

    def test_contract_parses_public_section_not_enum_private_or_cpp(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("UENUM", section)
        self.assertNotIn("enum class", section)
        self.assertNotIn("USkyguardDebriefWidget", section)
        self.assertNotIn("USkyguardBriefingWidget", section)
        self.assertNotIn("FSkyguardSearchlightTrackRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardApacheAircraft", section)
        self.assertNotIn("ASkyguardRadarNode", section)
        self.assertNotIn("ASkyguardBlackKiteBoss", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardIronRainBoss", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardRadarGhostBoss", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardTempestBoss", section)
        self.assertNotIn("ASkyguardLastFlightBoss", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("ASkyguardPatrolShip", section)
        self.assertNotIn("MinHeightFromOriginCm", section)
        self.assertEqual(
            require_declaration(section, CONFIGURE_MISSION_DEFINITION),
            CONFIGURE_MISSION_DEFINITION,
        )
        self.assertEqual(
            declaration_count(section, CONFIGURE_MISSION_DEFINITION),
            1,
        )
        self.assertNotIn(
            "SkyguardMission02IntegrationDirector.cpp",
            section,
        )
        self.assertNotIn(
            "ASkyguardMission02IntegrationDirector::ConfigureMissionDefinition",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
            self.assertNotIn(token, section)
        self.assertNotIn(
            "SkyguardMission08IntegrationDirector.cpp",
            section,
        )
        self.assertNotIn(
            "ASkyguardMission08IntegrationDirector::ConfigureMissionDefinition",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("}", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("return false", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("return true", CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        file_text = this_file_text()
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
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
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
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
                "mission02 ConfigureMissionDefinition method contract "
                f"contains {banned}; declaration is Apache CPG 30 mm / "
                "Hydra / Hellfire, not leftover live cop" + "y",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, CONFIGURE_MISSION_DEFINITION.lower())
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
            self.assertNotIn(token, locked_only)

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                CONFIGURE_MISSION_DEFINITION.lower(),
                "mission02 ConfigureMissionDefinition contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live cop" + "y",
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
        self.assertNotIn(dirty_fwd, CONFIGURE_MISSION_DEFINITION)

    def test_contract_is_configure_mission_definition_declaration_only(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, CONFIGURE_MISSION_DEFINITION),
            CONFIGURE_MISSION_DEFINITION,
        )
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for neighbor in unlocked_neighbors():
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, CONFIGURE_MISSION_DEFINITION)
        leftover_groups = (
            SIBLING_DIRECTOR_FIELDS_NOT_LOCKED,
            SIBLING_INTEGRATION_METHODS_NOT_LOCKED,
            LEFTOVER_BRIEFING_METHODS_NOT_LOCKED,
            LEFTOVER_BRIEFING_WIDGET_NOT_LOCKED,
            LEFTOVER_BRIEFING_DEFAULTS_NOT_LOCKED,
            LEFTOVER_AUDIO_DIRECTOR_FAIL_CLOSED_NOT_LOCKED,
            LEFTOVER_RADIO_CHATTER_FAIL_CLOSED_NOT_LOCKED,
            LEFTOVER_CAMPAIGN_DEFINITION_METHODS_NOT_LOCKED,
            LEFTOVER_HARBOR_SCRIPTS_NOT_LOCKED,
            LEFTOVER_ENVIRONMENT_READINESS_NOT_LOCKED,
            LEFTOVER_SPAWN_FIELDS_NOT_LOCKED,
            leftover_spawn_name_tokens(),
            LEFTOVER_HANDLE_DRONE_CITY_IMPACT_NOT_LOCKED,
            LEFTOVER_MISSION01_INITIALIZE_NOT_LOCKED,
            LEFTOVER_MISSION03_INITIALIZE_NOT_LOCKED,
            LEFTOVER_MISSION04_INITIALIZE_NOT_LOCKED,
            LEFTOVER_MISSION05_INITIALIZE_NOT_LOCKED,
            LEFTOVER_MISSION06_INITIALIZE_NOT_LOCKED,
            LEFTOVER_MISSION07_INITIALIZE_NOT_LOCKED,
            LEFTOVER_MISSION08_INITIALIZE_NOT_LOCKED,
            LEFTOVER_MISSION09_INITIALIZE_NOT_LOCKED,
            LEFTOVER_MISSION10_INITIALIZE_NOT_LOCKED,
            LEFTOVER_MISSION05_CONFIGURE_NOT_LOCKED,
            LEFTOVER_MISSION06_CONFIGURE_NOT_LOCKED,
            LEFTOVER_MISSION07_CONFIGURE_NOT_LOCKED,
            LEFTOVER_MISSION08_CONFIGURE_NOT_LOCKED,
            LEFTOVER_MISSION09_CONFIGURE_NOT_LOCKED,
            LEFTOVER_MISSION10_ROUTE_PHASE_ENUM_NOT_LOCKED,
            LEFTOVER_MISSION10_PROTECTED_GROUP_ENUM_NOT_LOCKED,
            LEFTOVER_MISSION10_PROTECTED_RUNTIME_NOT_LOCKED,
            LEFTOVER_MISSION10_SIBLING_METHODS_NOT_LOCKED,
            LEFTOVER_MISSION07_WAVE_STATE_ENUM_NOT_LOCKED,
            LEFTOVER_MISSION08_WAVE_STATE_ENUM_NOT_LOCKED,
            LEFTOVER_MISSION08_PROTECTED_TARGET_NOT_LOCKED,
            LEFTOVER_HOIST_WINDOW_NOT_LOCKED,
            LEFTOVER_STORM_RAIN_BEAT_METHODS_NOT_LOCKED,
            LEFTOVER_MISSION08_SIBLING_METHODS_NOT_LOCKED,
            LEFTOVER_MISSION09_WAVE_STATE_ENUM_NOT_LOCKED,
            LEFTOVER_MISSION09_PROTECTED_TARGET_NOT_LOCKED,
            LEFTOVER_MISSION09_POOL_RUNTIME_NOT_LOCKED,
            LEFTOVER_MISSION09_POOL_BUDGET_NOT_LOCKED,
            LEFTOVER_MISSION09_SIBLING_METHODS_NOT_LOCKED,
            LEFTOVER_MISSION07_PROTECTED_TARGET_NOT_LOCKED,
            LEFTOVER_SEARCH_SECTOR_NOT_LOCKED,
            LEFTOVER_SEARCH_TRACK_NOT_LOCKED,
            LEFTOVER_NIGHT_BEAT_METHODS_NOT_LOCKED,
            LEFTOVER_MISSION07_SIBLING_METHODS_NOT_LOCKED,
            LEFTOVER_MISSION05_CONFIGURE_NOT_LOCKED,
            LEFTOVER_MISSION05_GET_SURVIVING_TARGET_COUNT_NOT_LOCKED,
            LEFTOVER_MISSION06_WAVE_STATE_ENUM_NOT_LOCKED,
            LEFTOVER_AIRFIELD_TARGET_NOT_LOCKED,
            LEFTOVER_PAYLOAD_WINDOW_NOT_LOCKED,
            LEFTOVER_DAY_BEAT_METHODS_NOT_LOCKED,
            LEFTOVER_HANDLE_BOSS_PHASE_CHANGED_NOT_LOCKED,
            LEFTOVER_MISSION04_WAVE_STATE_ENUM_NOT_LOCKED,
            LEFTOVER_SEARCHLIGHT_RUNTIME_NOT_LOCKED,
            LEFTOVER_HARBOR_MISSION02_NOT_LOCKED,
            LEFTOVER_MISSION10_CONFIGURE_NOT_LOCKED,
            LEFTOVER_MISSION02_WAVE_STATE_NOT_LOCKED,
            LEFTOVER_SKYLINE_NOT_LOCKED,
            LEFTOVER_LIFELINE_HUNTER_NOT_LOCKED,
            LEFTOVER_APACHE_NOT_LOCKED,
            LEFTOVER_PATROL_SHIP_NOT_LOCKED,
            LEFTOVER_RADAR_NODE_NOT_LOCKED,
            LEFTOVER_FILL_AND_GUNNER_NOT_LOCKED,
            WRONG_HARBOR_HEADERS_NOT_SCANNED,
            leftover_short_roster_values(),
            leftover_live_copy_method_names(),
            HARBOR_ADJACENT_NOT_LOCKED,
            leftover_harbor_clock_tokens(),
        )
        for group in leftover_groups:
            for token in group:
                self.assertNotIn(token, locked_only)
                self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, CONFIGURE_MISSION_DEFINITION.lower())
            self.assertNotIn(banned, locked_only.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("{", CONFIGURE_MISSION_DEFINITION)
        self.assertTrue(CONFIGURE_MISSION_DEFINITION.startswith("bool "))
        self.assertIn("ConfigureMissionDefinition", CONFIGURE_MISSION_DEFINITION)
        self.assertTrue(CONFIGURE_MISSION_DEFINITION.endswith(";"))
        self.assertIn(UFUNCTION_INTEGRATION, section)

    def test_sibling_director_fields_do_not_satisfy_configure(
        self,
    ) -> None:
        for leftover in (
            ROOT_FIELD,
            BRIEFING_FIELD,
            AUDIO_DIRECTOR_FIELD,
            RADIO_CHATTER_FIELD,
            SORTIE_PRESENTATION_FIELD,
            CAMPAIGN_DEFINITION_FIELD,
            MISSION_DEFINITION_FIELD,
            READINESS_FIELD,
            AUTO_INITIALIZE_FIELD,
            ALLOW_BOUNDED_SPAWNING_FIELD,
            AUTO_LAUNCH_AFTER_BRIEFING_FIELD,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CONFIGURE_MISSION_DEFINITION)
            self.assertIn("ConfigureMissionDefinition", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, CONFIGURE_MISSION_DEFINITION)
            )
            self.assertNotEqual(CONFIGURE_MISSION_DEFINITION, leftover)
        self.assertIn(
            "Scripts/tests/test_mission01_briefing"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_audio_director"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_root_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_radio_chatter"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_sortie_presentation"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_campaign_definition"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_auto_initialize"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_sibling_integration_methods_do_not_satisfy(self) -> None:
        for leftover in (
            INITIALIZE_PLAYABLE_MISSION,
            BIND_CAMPAIGN_RUNTIME,
            GET_POOL_RUNTIME,
            GET_MISSION09_PROTECTED_TARGET,
            GET_MISSION09_WAVE_STATE,
            NOTIFY_OBJECTIVE_PROGRESS,
            NOTIFY_PROTECTED_ASSET_FAILED,
            SYNCHRONIZE_RUNTIME_STATE,
            IS_CORE_PLAYABLE_READY,
            GET_READINESS,
            GET_OBJECTIVE_RUNTIME,
            GET_GUNNER,
            GET_PATHFINDER,
            GET_MISSION_ID,
            VALIDATE_MISSION_CONTRACT,
            START_SEARCHLIGHT_WINDOW,
            ADVANCE_SEARCHLIGHT_TRACK,
            NOTIFY_SUBSTATION_DAMAGE,
            GET_REMAINING_THREATS_IN_WAVE,
            GET_SEARCHLIGHT_RUNTIME,
            GET_SUBSTATION_INTEGRITY,
            GET_NIGHT_BEAT_KIT,
            GET_NIGHT_BEAT_KIND,
            GET_NIGHT_BEAT_INDEX,
            TICK_NIGHT_BEAT_KIT,
            GET_WAVE_STATE,
            START_NEXT_WAVE,
            NOTIFY_THREAT_DESTROYED,
            CLASSIFY_FALSE_TRACK,
            CONFIRM_RADAR_GHOST_IDENTIFICATION,
            NOTIFY_PROTECTED_TARGET_DAMAGE,
            ADVANCE_REINFORCEMENT_TIMER,
            GET_SEARCH_SECTOR,
            GET_CLASSIFIED_FALSE_TRACK_COUNT,
            IS_HOSTILE_CONTACT_CONFIRMED,
            GET_PROTECTED_TARGET,
            GET_REINFORCEMENT_TIME_REMAINING,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CONFIGURE_MISSION_DEFINITION)
            self.assertIn("ConfigureMissionDefinition", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, CONFIGURE_MISSION_DEFINITION)
            )

    def test_leftover_briefing_methods_do_not_satisfy(self) -> None:
        for leftover in (
            CONFIGURE_FROM_MISSION,
            ADVANCE_BRIEFING,
            SET_ASSETS_READY,
            ACKNOWLEDGE_AND_LAUNCH,
            CAN_LAUNCH,
            GET_ELAPSED_SECONDS,
            GET_BRIEFING_STATE,
            GET_MINIMUM_WARMUP_SECONDS,
            GET_BRIEFING_TEXT,
            GET_RADIO_CHATTER,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CONFIGURE_MISSION_DEFINITION)
            self.assertIn("ConfigureMissionDefinition", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, CONFIGURE_MISSION_DEFINITION)
            )

    def test_leftover_briefing_widget_methods_do_not_satisfy(self) -> None:
        for leftover in (
            WIDGET_CONFIGURE,
            WIDGET_GET_PRESENTATION,
            WIDGET_GET_MISSION_TITLE,
            WIDGET_GET_BRIEFING_TEXT,
            WIDGET_ACKNOWLEDGE_BRIEFING,
            WIDGET_LAUNCH_SORTIE,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CONFIGURE_MISSION_DEFINITION)
            self.assertIn("ConfigureMissionDefinition", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, CONFIGURE_MISSION_DEFINITION)
            )

    def test_leftover_live_copy_named_boss_methods_do_not_satisfy(self) -> None:
        for leftover in (
            leftover_apply_strike(),
            leftover_is_lock_eligible(),
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CONFIGURE_MISSION_DEFINITION)
            self.assertIn("ConfigureMissionDefinition", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, CONFIGURE_MISSION_DEFINITION)
            )
        for name in leftover_live_copy_method_names():
            self.assertNotIn(name, CONFIGURE_MISSION_DEFINITION)

    def test_briefing_widget_scripts_stay_sibling_only(self) -> None:
        self.assertIn(
            "Scripts/tests/test_briefing_widget_configure"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_briefing_widget_get_presentation"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_briefing_widget_launch_sortie"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        self.assertNotIn("USkyguardBriefingWidget", locked_only)
        self.assertNotIn("GetPresentation", locked_only)
        self.assertNotIn("LaunchSortie", locked_only)

    def test_leftover_mission01_configure_does_not_satisfy(self) -> None:
        leftover = (
            "class SKYGUARD52_API ASkyguardMission01IntegrationDirector "
            ": public AActor\n"
            "{\n"
            "public:\n"
            "\tUFUNCTION(BlueprintCallable, "
            'Category="Skyguard|Mission01|Integration")\n'
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(leftover)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(
            "Scripts/tests/test_mission01_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        for token in LEFTOVER_MISSION01_INITIALIZE_NOT_LOCKED:
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_leftover_mission03_configure_does_not_satisfy(self) -> None:
        leftover = (
            "class SKYGUARD52_API ASkyguardMission03IntegrationDirector "
            ": public AActor\n"
            "{\n"
            "public:\n"
            "\tUFUNCTION(BlueprintCallable, "
            'Category="Skyguard|Mission03|Integration")\n'
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(leftover)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(
            "Scripts/tests/test_mission03_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        for token in LEFTOVER_MISSION03_INITIALIZE_NOT_LOCKED:
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_leftover_mission10_configure_does_not_satisfy(
        self,
    ) -> None:
        leftover = (
            "class SKYGUARD52_API ASkyguardMission10IntegrationDirector "
            ": public AActor\n"
            "{\n"
            "public:\n"
            "\tUFUNCTION(BlueprintCallable, "
            'Category="Skyguard|Mission10|Integration")\n'
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(leftover)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(
            "Scripts/tests/test_mission10_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission02_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        for token in LEFTOVER_MISSION10_CONFIGURE_NOT_LOCKED:
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        for token in LEFTOVER_HARBOR_MISSION02_NOT_LOCKED:
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_leftover_handle_drone_city_impact_does_not_satisfy(self) -> None:
        region = f"\t{HANDLE_DRONE_CITY_IMPACT}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(region, CONFIGURE_MISSION_DEFINITION)
        self.assertIn("ConfigureMissionDefinition", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(region, CONFIGURE_MISSION_DEFINITION))
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_HANDLE_DRONE_CITY_IMPACT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tbool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission)\n"
            "\t{\n"
            "\t\treturn false;\n"
            "\t}\n"
            "};\n"
        )
        origin_inline = (
            "public:\n"
            "\tbool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission)\n"
            "\t{\n"
            "\t\treturn true;\n"
            "\t}\n"
            "};\n"
        )
        one_line_inline = (
            "public:\n"
            "\tbool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission) { return false; }\n"
            "};\n"
        )
        for wrap in (inline, origin_inline, one_line_inline):
            header = (
                f"class SKYGUARD52_API {CLASS_NAME} "
                f": public AActor\n{{\n{wrap}"
            )
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, CONFIGURE_MISSION_DEFINITION),
                section,
            )
            self.assertEqual(
                require_declaration(section, CONFIGURE_MISSION_DEFINITION),
                CONFIGURE_MISSION_DEFINITION,
            )
            self.assertEqual(
                declaration_count(section, CONFIGURE_MISSION_DEFINITION),
                1,
            )
        self.assertNotIn("{", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("}", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("return ", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("return false", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("return true", CONFIGURE_MISSION_DEFINITION)


    def test_leftover_mission04_configure_does_not_satisfy(self) -> None:
        leftover = (
            "class SKYGUARD52_API ASkyguardMission04IntegrationDirector "
            ": public AActor\n"
            "{\n"
            "public:\n"
            "\tUFUNCTION(BlueprintCallable, "
            'Category="Skyguard|Mission04|Integration")\n'
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(leftover)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(
            "Scripts/tests/test_mission04_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission04_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        for token in LEFTOVER_MISSION04_INITIALIZE_NOT_LOCKED:
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)

    def test_leftover_mission05_configure_does_not_satisfy(self) -> None:
        leftover = (
            "class SKYGUARD52_API ASkyguardMission05IntegrationDirector "
            ": public AActor\n"
            "{\n"
            "public:\n"
            "\tUFUNCTION(BlueprintCallable, "
            'Category="Skyguard|Mission05|Integration")\n'
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(leftover)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(
            "Scripts/tests/test_mission05_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission05_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission06_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission06_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission07_wave_state_enum_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission07_protected_target_enum"
            "_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission07_protected_target_runtime"
            "_defaults_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_search_sector_enum_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_search_track_runtime_defaults"
            "_contract.py",
            LOCKED_SCRIPTS,
        )
        for token in LEFTOVER_MISSION05_INITIALIZE_NOT_LOCKED:
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("Mission05", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_mission05_configure(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION05_CONFIGURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission05_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("InitializePlayableMission", CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_leftover_mission05_surviving_count(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION05_GET_SURVIVING_TARGET_COUNT_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission05_get_surviving_target_count"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("GetSurvivingTargetCount", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("Protection", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_mission06_wave_state_enum(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION06_WAVE_STATE_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission06_wave_state_enum_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Waves", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_airfield_target(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_AIRFIELD_TARGET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_airfield_target_enum_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_airfield_target_runtime_defaults"
            "_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Targets", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_payload_window(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_PAYLOAD_WINDOW_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_payload_window_runtime_defaults"
            "_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Payload", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_day_beat_methods(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_DAY_BEAT_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("UFUNCTION", GET_DAY_BEAT_KIT)
        self.assertNotIn("UFUNCTION", GET_DAY_BEAT_KIND)
        self.assertNotIn("UFUNCTION", TICK_DAY_BEAT_KIT)

    def test_contract_does_not_relock_leftover_handle_boss_phase_changed(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_HANDLE_BOSS_PHASE_CHANGED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("HandleBossPhaseChanged", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("HandleBossPhaseChanged", UFUNCTION_INTEGRATION)

    def test_sibling_payload_and_target_methods_do_not_satisfy(self) -> None:
        for leftover in (
            START_PAYLOAD_WINDOW,
            ADVANCE_PAYLOAD_WINDOW,
            TRY_JAM_ACTIVE_PAYLOAD,
            NOTIFY_AIRFIELD_TARGET_DAMAGE,
            GET_PAYLOAD_WINDOW,
            GET_TARGET_RUNTIME,
            GET_SURVIVING_TARGET_COUNT,
            GET_DAY_BEAT_KIND,
            GET_DAY_BEAT_INDEX,
            TICK_DAY_BEAT_KIT,
            HANDLE_BOSS_PHASE_CHANGED,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CONFIGURE_MISSION_DEFINITION)
            self.assertIn("ConfigureMissionDefinition", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, CONFIGURE_MISSION_DEFINITION)
            )

    def test_locked_scripts_do_not_include_this_file(self) -> None:
        this_script = (
            "Scripts/tests/test_mission02_configure_mission_definition"
            "_decl_contract.py"
        )
        self.assertNotIn(this_script, LOCKED_SCRIPTS)
        self.assertTrue(
            Path(__file__).name.endswith(
                "test_mission02_configure_mission_definition"
                "_decl_contract.py"
            )
        )
        self.assertIn(
            "Scripts/tests/test_mission10_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission10_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission01_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission03_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission04_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission06_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission07_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission08_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission09_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission10_briefing_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission10_protected_group_count"
            "_field_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission05_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission05_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission05_get_surviving_target_count"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission04_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_briefing_widget_configure"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_audio_director_listener_perspective"
            "_fail_closed.py",
            LOCKED_SCRIPTS,
        )

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

    def test_leftover_mission06_configure_does_not_satisfy(self) -> None:
        leftover = (
            "class SKYGUARD52_API ASkyguardMission06IntegrationDirector "
            ": public AActor\n"
            "{\n"
            "public:\n"
            "\tUFUNCTION(BlueprintCallable, "
            'Category="Skyguard|Mission06|Integration")\n'
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(leftover)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(
            "Scripts/tests/test_mission06_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        for token in LEFTOVER_MISSION06_INITIALIZE_NOT_LOCKED:
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("Mission06", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_mission07_wave_state_enum(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION07_WAVE_STATE_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission07_wave_state_enum_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Waves", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_mission07_protected_target(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION07_PROTECTED_TARGET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission07_protected_target_enum"
            "_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission07_protected_target_runtime"
            "_defaults_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Protection", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_search_sector(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_SEARCH_SECTOR_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_search_sector_enum_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Search", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_search_track(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_SEARCH_TRACK_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_search_track_runtime_defaults"
            "_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_leftover_night_beat_methods(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_NIGHT_BEAT_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("UFUNCTION", GET_NIGHT_BEAT_KIT)
        self.assertNotIn("UFUNCTION", GET_NIGHT_BEAT_KIND)
        self.assertNotIn("UFUNCTION", GET_NIGHT_BEAT_INDEX)
        self.assertNotIn("UFUNCTION", TICK_NIGHT_BEAT_KIT)

    def test_sibling_mission07_search_protection_methods_do_not_satisfy(
        self,
    ) -> None:
        for leftover in LEFTOVER_MISSION07_SIBLING_METHODS_NOT_LOCKED:
            if leftover.startswith("test_"):
                continue
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CONFIGURE_MISSION_DEFINITION)
            self.assertIn("ConfigureMissionDefinition", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, CONFIGURE_MISSION_DEFINITION)
            )

    def test_leftover_mission07_configure_does_not_satisfy(self) -> None:
        leftover = (
            "class SKYGUARD52_API ASkyguardMission07IntegrationDirector "
            ": public AActor\n"
            "{\n"
            "public:\n"
            "\tUFUNCTION(BlueprintCallable, "
            'Category="Skyguard|Mission07|Integration")\n'
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(leftover)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(
            "Scripts/tests/test_mission07_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission07_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        for token in LEFTOVER_MISSION07_INITIALIZE_NOT_LOCKED:
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("Mission07", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_mission08_wave_state_enum(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION08_WAVE_STATE_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission08_wave_state_enum_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Waves", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_mission08_protected_target(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION08_PROTECTED_TARGET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission08_protected_target_enum"
            "_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission08_protected_target_runtime"
            "_defaults_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Protection", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_hoist_window(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_HOIST_WINDOW_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_hoist_window_runtime_defaults"
            "_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission08_start_hoist_window"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Hoist", UFUNCTION_INTEGRATION)
        self.assertNotIn("StartHoistWindow", CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_leftover_storm_rain_beat_methods(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_STORM_RAIN_BEAT_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("UFUNCTION", GET_STORM_RAIN_BEAT_KIT)
        self.assertNotIn("UFUNCTION", APPLY_STORM_RAIN_PLAY_CONTRACT)
        self.assertNotIn("UFUNCTION", GET_STORM_RAIN_BEAT_KIND)
        self.assertNotIn("UFUNCTION", TICK_STORM_RAIN_BEAT_KIT)

    def test_sibling_mission08_hoist_safety_methods_do_not_satisfy(
        self,
    ) -> None:
        for leftover in (
            START_HOIST_WINDOW,
            ADVANCE_HOIST_WINDOW,
            VALIDATE_WEAPON_RELEASE,
            GET_HOIST_RUNTIME,
            GET_REJECTED_WEAPON_RELEASES,
            GET_STORM_RAIN_BEAT_KIT,
            APPLY_STORM_RAIN_PLAY_CONTRACT,
            GET_STORM_RAIN_BEAT_KIND,
            TICK_STORM_RAIN_BEAT_KIT,
            INITIALIZE_PLAYABLE_MISSION,
            START_NEXT_WAVE,
            NOTIFY_THREAT_DESTROYED,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CONFIGURE_MISSION_DEFINITION)
            self.assertIn("ConfigureMissionDefinition", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, CONFIGURE_MISSION_DEFINITION)
            )
        self.assertIn(
            "Scripts/tests/test_mission08_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission08_start_next_wave"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission08_notify_threat_destroyed"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION08_SIBLING_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("Safety", UFUNCTION_INTEGRATION)
        self.assertNotIn("Hoist", UFUNCTION_INTEGRATION)
        self.assertNotIn("Rescue", UFUNCTION_INTEGRATION)


    def test_leftover_mission08_configure_does_not_satisfy(self) -> None:
        leftover = (
            "class SKYGUARD52_API ASkyguardMission08IntegrationDirector "
            ": public AActor\n"
            "{\n"
            "public:\n"
            "\tUFUNCTION(BlueprintCallable, "
            'Category="Skyguard|Mission08|Integration")\n'
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(leftover)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(
            "Scripts/tests/test_mission08_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission08_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        for token in LEFTOVER_MISSION08_INITIALIZE_NOT_LOCKED:
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("Mission08", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_mission09_wave_state_enum(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION09_WAVE_STATE_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission09_wave_state_enum_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Waves", UFUNCTION_INTEGRATION)
        self.assertNotIn(
            "ESkyguardMission09WaveState",
            CONFIGURE_MISSION_DEFINITION,
        )

    def test_contract_does_not_relock_leftover_mission09_protected_target(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION09_PROTECTED_TARGET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission09_protected_target_enum"
            "_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission09_protected_target_runtime"
            "_defaults_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Protection", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_mission09_pool(self) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION09_POOL_RUNTIME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        for token in LEFTOVER_MISSION09_POOL_BUDGET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission09_pool_runtime_defaults"
            "_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission09_pool_budget_defaults"
            "_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Performance", UFUNCTION_INTEGRATION)
        self.assertNotIn("GetPoolRuntime", CONFIGURE_MISSION_DEFINITION)

    def test_sibling_mission09_methods_do_not_satisfy(self) -> None:
        for leftover in (
            INITIALIZE_PLAYABLE_MISSION,
            BIND_CAMPAIGN_RUNTIME,
            START_NEXT_WAVE,
            NOTIFY_THREAT_DESTROYED,
            NOTIFY_PROTECTED_TARGET_DAMAGE,
            NOTIFY_PROTECTED_ASSET_FAILED,
            SYNCHRONIZE_RUNTIME_STATE,
            IS_CORE_PLAYABLE_READY,
            GET_READINESS,
            GET_MISSION09_WAVE_STATE,
            GET_REMAINING_THREATS_IN_WAVE,
            GET_POOL_RUNTIME,
            GET_MISSION09_PROTECTED_TARGET,
            GET_SURVIVING_TARGET_COUNT,
            GET_OBJECTIVE_RUNTIME,
            GET_MISSION_ID,
            VALIDATE_MISSION_CONTRACT,
            BIND_RUNTIME_ACTORS,
            HANDLE_DRONE_CITY_IMPACT,
            GET_DAY_BEAT_KIT,
            GET_DAY_BEAT_KIND,
            GET_DAY_BEAT_INDEX,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CONFIGURE_MISSION_DEFINITION)
            self.assertIn("ConfigureMissionDefinition", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, CONFIGURE_MISSION_DEFINITION)
            )
        self.assertIn(
            "Scripts/tests/test_mission09_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission09_bind_campaign_runtime"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission09_get_pool_runtime"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission09_is_core_playable_ready"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION09_SIBLING_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("BindCampaignRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetPoolRuntime", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn(BIND_RUNTIME_ACTORS, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("UFUNCTION", GET_DAY_BEAT_KIT)
        self.assertNotIn("UFUNCTION", GET_DAY_BEAT_KIND)
        self.assertNotIn("UFUNCTION", GET_DAY_BEAT_INDEX)


    def test_leftover_mission09_configure_does_not_satisfy(self) -> None:
        leftover = (
            "class SKYGUARD52_API ASkyguardMission09IntegrationDirector "
            ": public AActor\n"
            "{\n"
            "public:\n"
            "\tUFUNCTION(BlueprintCallable, "
            'Category="Skyguard|Mission09|Integration")\n'
            f"\t{CONFIGURE_MISSION_DEFINITION}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(leftover)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(
            "Scripts/tests/test_mission09_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission09_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        for token in LEFTOVER_MISSION09_INITIALIZE_NOT_LOCKED:
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("Mission09", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_mission10_route_phase_enum(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION10_ROUTE_PHASE_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission10_route_phase_enum_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission10_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Waves", UFUNCTION_INTEGRATION)
        self.assertNotIn(
            "ESkyguardMission10RoutePhase",
            CONFIGURE_MISSION_DEFINITION,
        )
        self.assertNotIn("GetRoutePhase", CONFIGURE_MISSION_DEFINITION)

    def test_contract_does_not_relock_leftover_mission10_protected_group(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION10_PROTECTED_GROUP_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        for token in LEFTOVER_MISSION10_PROTECTED_RUNTIME_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission10_protected_group_enum"
            "_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertIn(
            "Scripts/tests/test_mission10_protected_runtime_defaults"
            "_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("Protection", UFUNCTION_INTEGRATION)
        self.assertNotIn("GetProtectedGroup", CONFIGURE_MISSION_DEFINITION)

    def test_leftover_mission10_sibling_methods_do_not_satisfy(self) -> None:
        for leftover in (
            INITIALIZE_PLAYABLE_MISSION,
            START_PHASE_WAVE,
            NOTIFY_THREAT_DESTROYED,
            VALIDATE_WEAPON_RELEASE,
            NOTIFY_PROTECTED_GROUP_DAMAGE,
            NOTIFY_PROTECTED_ASSET_FAILED,
            SYNCHRONIZE_RUNTIME_STATE,
            IS_CORE_PLAYABLE_READY,
            GET_READINESS,
            GET_MISSION10_ROUTE_PHASE,
            GET_REMAINING_THREATS_IN_WAVE,
            GET_REJECTED_WEAPON_RELEASES,
            GET_MISSION10_PROTECTED_GROUP,
            GET_SURVIVING_PROTECTED_GROUP_COUNT,
            GET_OBJECTIVE_RUNTIME,
            GET_MISSION_ID,
            VALIDATE_MISSION_CONTRACT,
            BIND_RUNTIME_ACTORS,
            HANDLE_DRONE_CITY_IMPACT,
            GET_DAY_BEAT_KIT,
        ):
            region = f"\t{leftover}\n"
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, CONFIGURE_MISSION_DEFINITION)
            self.assertIn("ConfigureMissionDefinition", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertFalse(
                has_declaration(region, CONFIGURE_MISSION_DEFINITION)
            )
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION10_SIBLING_METHODS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn(BIND_RUNTIME_ACTORS, CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("HandleDroneCityImpact", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("UFUNCTION", GET_DAY_BEAT_KIT)
        self.assertNotIn("StartPhaseWave", CONFIGURE_MISSION_DEFINITION)
        self.assertNotIn("GetRoutePhase", CONFIGURE_MISSION_DEFINITION)


    def test_contract_does_not_relock_leftover_mission09_configure(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION09_CONFIGURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission09_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn(
            "cursor/mission09-configure-mission-definition-decl-contract-c332",
            CONFIGURE_MISSION_DEFINITION,
        )
        self.assertNotIn("Mission09", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_mission08_configure(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION08_CONFIGURE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission08_configure_mission_definition"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn(
            "cursor/mission08-configure-mission-definition-decl-contract-c332",
            CONFIGURE_MISSION_DEFINITION,
        )
        self.assertNotIn("Mission08", UFUNCTION_INTEGRATION)

    def test_contract_does_not_relock_leftover_mission10_initialize(
        self,
    ) -> None:
        locked_only = f"{CONFIGURE_MISSION_DEFINITION}\n"
        for token in LEFTOVER_MISSION10_INITIALIZE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, CONFIGURE_MISSION_DEFINITION)
        self.assertIn(
            "Scripts/tests/test_mission10_initialize_playable_mission"
            "_decl_contract.py",
            LOCKED_SCRIPTS,
        )
        self.assertNotIn("InitializePlayableMission", CONFIGURE_MISSION_DEFINITION)




if __name__ == "__main__":
    unittest.main()

