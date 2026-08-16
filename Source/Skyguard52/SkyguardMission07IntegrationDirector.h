#pragma once

class ASkyguardDrone;

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardBossTypes.h"
#include "SkyguardNightSortieBeatKit.h"
#include "SkyguardMission07IntegrationDirector.generated.h"

class ASkyguardGunner;
class ASkyguardMissionMapAssemblyDirector;
class ASkyguardRadarGhostBoss;
class ASkyguardYak52Aircraft;
class USceneComponent;
class USkyguardAudioDirectorComponent;
class USkyguardCampaignDefinition;
class USkyguardCampaignSubsystem;
class USkyguardMissionBriefingComponent;
class USkyguardMissionDefinition;
class USkyguardObjectiveRuntime;
class USkyguardRadioChatterComponent;
class USkyguardSortiePresentationComponent;

UENUM(BlueprintType)
enum class ESkyguardMission07WaveState : uint8
{
	Briefing,
	Searching,
	AwaitingWave,
	WaveActive,
	BossEngaged,
	Completed,
	Failed
};

UENUM(BlueprintType)
enum class ESkyguardSearchSector : uint8
{
	SectorA,
	SectorB,
	Intercept
};

UENUM(BlueprintType)
enum class ESkyguardMission07ProtectedTarget : uint8
{
	NavigationStation,
	FishingFleet
};

USTRUCT(BlueprintType)
struct FSkyguardSearchTrackRuntime
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FName TrackId = NAME_None;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardSearchSector Sector = ESkyguardSearchSector::SectorA;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bClassifiedFalse = false;
};

USTRUCT(BlueprintType)
struct FSkyguardMission07ProtectedTargetRuntime
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardMission07ProtectedTarget Target =
		ESkyguardMission07ProtectedTarget::NavigationStation;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 Integrity = 100;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bDestroyed = false;
};

USTRUCT(BlueprintType)
struct FSkyguardMission07IntegrationReadiness
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bMissionDefinitionValid = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bCampaignDefinitionValid = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bMapAssemblyReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bYakRuntimeReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bGunnerReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bRadarGhostReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bObjectivesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bWavesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bSearchRuntimeReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bProtectedTargetsReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bBriefingReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bAudioReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bSortiePresentationReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bCampaignRuntimeStarted = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 ObjectiveCount = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 WaveCount = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 SearchTrackCount = 0;
};

/** Mission 7 two-sector search, identification and intercept boundary. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardMission07IntegrationDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardMission07IntegrationDirector();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Integration")
	bool InitializePlayableMission();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Integration")
	bool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Integration")
	void BindRuntimeActors(
		ASkyguardMissionMapAssemblyDirector* InMapAssembly,
		ASkyguardYak52Aircraft* Aircraft,
		ASkyguardGunner* InGunner,
		ASkyguardRadarGhostBoss* InRadarGhost);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Search")
	bool ClassifyFalseTrack(FName TrackId);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Search")
	bool ConfirmRadarGhostIdentification(
		bool bExhaustObserved,
		bool bShadowObserved,
		bool bEngineSoundObserved);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Waves")
	bool StartNextWave();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Waves")
	bool NotifyThreatDestroyed(int32 Amount = 1);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Protection")
	bool NotifyProtectedTargetDamage(
		ESkyguardMission07ProtectedTarget Target,
		int32 Damage);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Objectives")
	bool NotifyProtectedAssetFailed();

	void HandleDroneCityImpact(ASkyguardDrone* Drone);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Boss")
	bool AdvanceReinforcementTimer(float DeltaSeconds);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Integration")
	void SynchronizeRuntimeState();
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Integration")
	bool IsCorePlayableReady() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Integration")
	const FSkyguardMission07IntegrationReadiness& GetReadiness() const
	{
		return Readiness;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Integration")
	USkyguardObjectiveRuntime* GetObjectiveRuntime() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Waves")
	ESkyguardMission07WaveState GetWaveState() const { return WaveState; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Waves")
	int32 GetRemainingThreatsInWave() const { return RemainingThreatsInWave; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Search")
	ESkyguardSearchSector GetSearchSector() const { return SearchSector; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Search")
	int32 GetClassifiedFalseTrackCount() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Search")
	bool IsHostileContactConfirmed() const { return bHostileContactConfirmed; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Protection")
	FSkyguardMission07ProtectedTargetRuntime GetProtectedTarget(
		ESkyguardMission07ProtectedTarget Target) const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Protection")
	int32 GetSurvivingTargetCount() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Boss")
	float GetReinforcementTimeRemaining() const
	{
		return ReinforcementTimeRemaining;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Integration")
	static FName GetMissionId() { return TEXT("M07_SearchIntercept"); }
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Integration")
	static bool ValidateMissionContract(
		const USkyguardMissionDefinition* Mission,
		TArray<FText>& OutErrors);

	const FSkyguardNightSortieBeatKit& GetNightBeatKit() const;
	ESkyguardNightSortieBeatKind GetNightBeatKind() const;
	int32 GetNightBeatIndex() const { return NightBeatIndex; }
	void TickNightBeatKit(float DeltaSeconds);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission07")
	TObjectPtr<USceneComponent> Root;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission07")
	TObjectPtr<USkyguardMissionBriefingComponent> Briefing;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission07")
	TObjectPtr<USkyguardAudioDirectorComponent> AudioDirector;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission07")
	TObjectPtr<USkyguardRadioChatterComponent> RadioChatter;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission07")
	TObjectPtr<USkyguardSortiePresentationComponent> SortiePresentation;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission07")
	TSoftObjectPtr<USkyguardCampaignDefinition> CampaignDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission07")
	TSoftObjectPtr<USkyguardMissionDefinition> MissionDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission07")
	bool bAutoInitialize = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission07")
	bool bAllowBoundedActorSpawning = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission07")
	bool bAutoLaunchAfterBriefing = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission07|Campaign")
	FString CampaignSaveSlotName = TEXT("Skyguard52Campaign");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission07|Campaign",
		meta=(ClampMin="0"))
	int32 CampaignSaveUserIndex = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission07")
	FVector YakSpawnLocation = FVector(0.f, -24000.f, 7600.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission07")
	FRotator YakSpawnRotation = FRotator(0.f, 18.f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission07")
	FVector RadarGhostSpawnLocation = FVector(73000.f, 32000.f, 7200.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission07")
	FRotator RadarGhostSpawnRotation = FRotator(0.f, 205.f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission07", meta=(ClampMin="1"))
	int32 MaximumProtectedTargetIntegrity = 100;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission07", meta=(ClampMin="1.0"))
	float ReinforcementDeadlineSeconds = 45.f;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission07")
	FSkyguardMission07IntegrationReadiness Readiness;

private:
	UPROPERTY(Transient)
	TObjectPtr<USkyguardMissionDefinition> ResolvedMission;
	UPROPERTY(Transient)
	TObjectPtr<USkyguardCampaignDefinition> ResolvedCampaign;
	UPROPERTY(Transient)
	TObjectPtr<USkyguardCampaignSubsystem> CampaignRuntime;
	UPROPERTY(Transient)
	TObjectPtr<USkyguardObjectiveRuntime> LocalObjectiveRuntime;
	UPROPERTY(Transient)
	TObjectPtr<ASkyguardMissionMapAssemblyDirector> MapAssembly;
	UPROPERTY(Transient)
	TObjectPtr<ASkyguardYak52Aircraft> YakAircraft;
	UPROPERTY(Transient)
	TObjectPtr<ASkyguardGunner> Gunner;
	UPROPERTY(Transient)
	TObjectPtr<ASkyguardRadarGhostBoss> RadarGhost;
	UPROPERTY(Transient)
	TArray<FSkyguardSearchTrackRuntime> SearchTracks;
	UPROPERTY(Transient)
	TArray<FSkyguardMission07ProtectedTargetRuntime> ProtectedTargets;

	ESkyguardMission07WaveState WaveState =
		ESkyguardMission07WaveState::Briefing;
	ESkyguardSearchSector SearchSector = ESkyguardSearchSector::SectorA;
	int32 CurrentWaveIndex = -1;
	int32 RemainingThreatsInWave = 0;
	int32 ObservedBossWeakPointsDestroyed = 0;
	float ReinforcementTimeRemaining = 45.f;
	int32 NightBeatIndex = 0;
	float NightBeatElapsed = 0.f;
	bool bHostileContactConfirmed = false;
	bool bInitialized = false;
	bool bSortieLaunched = false;
	bool bMissionCompleted = false;
	void ApplyNightThermalContract();

	bool NotifyObjectiveProgress(FName ObjectiveId, int32 Amount = 1);
	int32 CalculateWaveThreatCount(int32 WaveIndex) const;
	FSkyguardMission07ProtectedTargetRuntime* FindProtectedTarget(
		ESkyguardMission07ProtectedTarget Target);
	const FSkyguardMission07ProtectedTargetRuntime* FindProtectedTarget(
		ESkyguardMission07ProtectedTarget Target) const;
	void ResolveOrSpawnActors();
	void ConfigurePresentation();
	void UpdateReadiness();
	void TryLaunchSortie();
	void CompleteMissionIfReady();

	UFUNCTION()
	void HandleBossPhaseChanged(
		ESkyguardBossPhase PreviousPhase,
		ESkyguardBossPhase NewPhase);
	void HandlePilotCommand(ESkyguardPilotCommand Command);
};
