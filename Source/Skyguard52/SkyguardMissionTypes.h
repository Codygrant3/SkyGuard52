#pragma once

#include "CoreMinimal.h"
#include "SkyguardMissionTypes.generated.h"

class UWorld;

UENUM(BlueprintType)
enum class ESkyguardMissionObjectiveType : uint8
{
	DestroyTargets,
	ProtectAsset,
	ReachRoutePoint,
	Survive,
	ScanTargets,
	Rescue,
	BossPhase
};

UENUM(BlueprintType)
enum class ESkyguardMissionObjectiveState : uint8
{
	Inactive,
	Active,
	Completed,
	Failed
};

UENUM(BlueprintType)
enum class ESkyguardFormationType : uint8
{
	Line,
	Vee,
	EchelonLeft,
	EchelonRight,
	Trail,
	LooseSwarm
};

UENUM(BlueprintType)
enum class ESkyguardMissionWeather : uint8
{
	Clear,
	Overcast,
	Rain,
	Storm,
	NightClear,
	NightOvercast
};

USTRUCT(BlueprintType)
struct FSkyguardRoutePoint
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName PointId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FVector WorldLocation = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	float TargetAirspeedKph = 220.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	float LookAheadSeconds = 2.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	bool bAllowCombatOrbit = true;
};

USTRUCT(BlueprintType)
struct FSkyguardRouteDefinition
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName RouteId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	TArray<FSkyguardRoutePoint> Points;
};

USTRUCT(BlueprintType)
struct FSkyguardObjectiveDefinition
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName ObjectiveId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	ESkyguardMissionObjectiveType Type = ESkyguardMissionObjectiveType::DestroyTargets;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "1"))
	int32 RequiredProgress = 1;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	bool bRequiredForMissionSuccess = true;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	bool bFailureEndsMission = false;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0"))
	int32 ScoreReward = 1000;
};

USTRUCT(BlueprintType)
struct FSkyguardEnemyFormationDefinition
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName FormationId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	ESkyguardFormationType Formation = ESkyguardFormationType::Vee;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "1", ClampMax = "32"))
	int32 UnitCount = 3;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "100.0"))
	float SpacingCentimeters = 1200.f;
};

USTRUCT(BlueprintType)
struct FSkyguardEnemyWaveDefinition
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName WaveId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0.0"))
	float StartTimeSeconds = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	TArray<FSkyguardEnemyFormationDefinition> Formations;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName CompletionObjectiveId;
};

USTRUCT(BlueprintType)
struct FSkyguardBossWeakPointDefinition
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName WeakPointId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName RequiredWeapon;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName ExposesWeakPointId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "1.0"))
	float Integrity = 100.f;
};

USTRUCT(BlueprintType)
struct FSkyguardBossDefinition
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName BossId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FText Callsign;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	TArray<FSkyguardBossWeakPointDefinition> WeakPoints;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName DefeatObjectiveId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0", ClampMax = "12"))
	int32 MaximumBreakupPieces = 3;
};

USTRUCT(BlueprintType)
struct FSkyguardWeatherProfile
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName ProfileId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Clear;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0.0", ClampMax = "24.0"))
	float TimeOfDayHours = 12.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0.0"))
	float WindSpeedMetersPerSecond = 5.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float Precipitation = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float CloudCoverage = 0.25f;
};

USTRUCT(BlueprintType)
struct FSkyguardMissionPresentation
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (MultiLine = "true"))
	FText Briefing;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	TArray<FText> RadioChatter;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (MultiLine = "true"))
	FText SuccessDebrief;

	/** Used by USkyguardCampaignSubsystem::FailActiveMission for LastDebrief.Narrative. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (MultiLine = "true"))
	FText FailureDebrief;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0.0"))
	float MinimumBriefingWarmupSeconds = 3.f;
};

USTRUCT(BlueprintType)
struct FSkyguardMissionScoreRules
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0"))
	int32 CompletionScore = 5000;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0"))
	int32 PerfectAccuracyBonus = 2500;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "0"))
	int32 NoDamageBonus = 1500;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "1"))
	int32 BronzeThreshold = 5000;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "1"))
	int32 SilverThreshold = 8000;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, meta = (ClampMin = "1"))
	int32 GoldThreshold = 11000;
};

USTRUCT(BlueprintType)
struct FSkyguardObjectiveProgress
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FName ObjectiveId;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 CurrentProgress = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardMissionObjectiveState State = ESkyguardMissionObjectiveState::Inactive;
};

USTRUCT(BlueprintType)
struct FSkyguardMissionResult
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FName MissionId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	bool bMissionSucceeded = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 ShotsFired = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 Hits = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float AircraftDamageFraction = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float CompletionTimeSeconds = 0.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TArray<FName> CompletedObjectiveIds;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 FinalScore = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, meta = (ClampMin = "0", ClampMax = "3"))
	int32 MedalTier = 0;
};

UENUM(BlueprintType)
enum class ESkyguardMissionDebriefState : uint8
{
	Unavailable,
	Ready,
	Acknowledged
};

/**
 * Presentation-safe result of a completed sortie.
 *
 * UI code can render this structure without re-running scoring, progression,
 * save, or mission-selection logic.
 */
USTRUCT(BlueprintType)
struct FSkyguardMissionDebrief
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardMissionDebriefState State =
		ESkyguardMissionDebriefState::Unavailable;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FSkyguardMissionResult Result;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FText MissionDisplayName;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, meta = (MultiLine = "true"))
	FText Narrative;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bNewBestScore = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bNewBestMedal = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bProgressSaved = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FString SaveSlotName;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FName NextMissionId;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FText NextMissionDisplayName;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	TSoftObjectPtr<UWorld> NextMissionMap;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bNextMissionUnlocked = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bCampaignComplete = false;
};
