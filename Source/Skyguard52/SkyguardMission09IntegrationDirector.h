#pragma once

class ASkyguardDrone;

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardBossTypes.h"
#include "SkyguardMission09IntegrationDirector.generated.h"

class ASkyguardGunner;
class ASkyguardIronRainBoss;
class ASkyguardMissionMapAssemblyDirector;
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
enum class ESkyguardMission09WaveState : uint8
{
	Briefing,
	AwaitingWave,
	WaveActive,
	BossEngaged,
	Completed,
	Failed
};

UENUM(BlueprintType)
enum class ESkyguardMission09ProtectedTarget : uint8
{
	MetropolitanSkyline,
	CoastalPowerStation,
	MajorBridge
};

USTRUCT(BlueprintType)
struct FSkyguardMission09ProtectedTargetRuntime
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardMission09ProtectedTarget Target =
		ESkyguardMission09ProtectedTarget::MetropolitanSkyline;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 Integrity = 100;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bDestroyed = false;
};

USTRUCT(BlueprintType)
struct FSkyguardMission09PoolBudget
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="1", ClampMax="32"))
	int32 MaxActiveThreats = 24;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="1", ClampMax="96"))
	int32 PoolCapacity = 48;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="0", ClampMax="24"))
	int32 MaxActiveDecoys = 12;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta=(ClampMin="1", ClampMax="12"))
	int32 MaxSimultaneousExplosions = 6;
};

USTRUCT(BlueprintType)
struct FSkyguardMission09PoolRuntime
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 Available = 48;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 Active = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 PeakActive = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 Recycled = 0;
};

USTRUCT(BlueprintType)
struct FSkyguardMission09IntegrationReadiness
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bMissionDefinitionValid = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bCampaignDefinitionValid = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bCampaignRuntimeStarted = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bMapAssemblyReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bYakRuntimeReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bGunnerReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bIronRainReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bObjectivesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bEscalatingWavesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bProtectedTargetsReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bPoolBudgetSafe = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bPresentationReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bSortiePresentationReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 ObjectiveCount = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 WaveCount = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 ProtectedTargetCount = 0;
};

/** Mission 9 dense-city saturation, infrastructure and Iron Rain boundary. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardMission09IntegrationDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardMission09IntegrationDirector();
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Integration")
	bool InitializePlayableMission();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Integration")
	bool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Integration")
	bool BindCampaignRuntime(USkyguardCampaignSubsystem* InCampaignRuntime);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Integration")
	void BindRuntimeActors(
		ASkyguardMissionMapAssemblyDirector* InAssembly,
		ASkyguardYak52Aircraft* InYak,
		ASkyguardGunner* InGunner,
		ASkyguardIronRainBoss* InIronRain);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Waves")
	bool StartNextWave();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Waves")
	bool NotifyThreatDestroyed(int32 Amount = 1);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Protection")
	bool NotifyProtectedTargetDamage(
		ESkyguardMission09ProtectedTarget Target,
		int32 Damage);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Objectives")
	bool NotifyProtectedAssetFailed();

	void HandleDroneCityImpact(ASkyguardDrone* Drone);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Integration")
	void SynchronizeRuntimeState();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Integration")
	bool IsCorePlayableReady() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Integration")
	const FSkyguardMission09IntegrationReadiness& GetReadiness() const { return Readiness; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Waves")
	ESkyguardMission09WaveState GetWaveState() const { return WaveState; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Waves")
	int32 GetRemainingThreatsInWave() const { return RemainingThreatsInWave; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Performance")
	const FSkyguardMission09PoolRuntime& GetPoolRuntime() const { return PoolRuntime; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Protection")
	FSkyguardMission09ProtectedTargetRuntime GetProtectedTarget(
		ESkyguardMission09ProtectedTarget Target) const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Protection")
	int32 GetSurvivingTargetCount() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Integration")
	USkyguardObjectiveRuntime* GetObjectiveRuntime() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Integration")
	static FName GetMissionId() { return TEXT("M09_SaturationAttack"); }
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Integration")
	static bool ValidateMissionContract(
		const USkyguardMissionDefinition* Mission,
		TArray<FText>& OutErrors);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09")
	TObjectPtr<USceneComponent> Root;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09")
	TObjectPtr<USceneComponent> SkylineAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09")
	TObjectPtr<USceneComponent> PowerStationAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09")
	TObjectPtr<USceneComponent> MajorBridgeAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09")
	TObjectPtr<USkyguardMissionBriefingComponent> Briefing;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09")
	TObjectPtr<USkyguardAudioDirectorComponent> AudioDirector;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09")
	TObjectPtr<USkyguardRadioChatterComponent> RadioChatter;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09")
	TObjectPtr<USkyguardSortiePresentationComponent> SortiePresentation;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission09")
	TSoftObjectPtr<USkyguardCampaignDefinition> CampaignDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission09")
	TSoftObjectPtr<USkyguardMissionDefinition> MissionDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission09")
	bool bAutoInitialize = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission09")
	bool bAllowBoundedActorSpawning = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission09|Campaign")
	FString CampaignSaveSlotName = TEXT("Skyguard52Campaign");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission09|Campaign",
		meta=(ClampMin="0"))
	int32 CampaignSaveUserIndex = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission09")
	FVector YakSpawnLocation = FVector(0.f, -10000.f, 8800.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission09")
	FVector IronRainSpawnLocation = FVector(72000.f, 8000.f, 7600.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission09")
	int32 MaximumProtectedTargetIntegrity = 100;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission09|Performance")
	FSkyguardMission09PoolBudget PoolBudget;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09")
	FSkyguardMission09IntegrationReadiness Readiness;

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
	TObjectPtr<ASkyguardIronRainBoss> IronRain;
	UPROPERTY(Transient)
	TArray<FSkyguardMission09ProtectedTargetRuntime> ProtectedTargets;
	UPROPERTY(Transient)
	FSkyguardMission09PoolRuntime PoolRuntime;

	ESkyguardMission09WaveState WaveState = ESkyguardMission09WaveState::Briefing;
	int32 CurrentWaveIndex = -1;
	int32 RemainingThreatsInWave = 0;
	int32 ObservedDispenserMilestones = 0;
	int32 ObservedBossMilestones = 0;
	bool bMissionCompleted = false;

	bool NotifyObjectiveProgress(FName ObjectiveId, int32 Amount = 1);
	void FailObjective(FName ObjectiveId);
	int32 CalculateWaveThreatCount(int32 WaveIndex) const;
	bool ReservePooledThreats(int32 Count);
	void RecycleThreats(int32 Count);
	void UpdateReadiness();
	void CompleteMissionIfReady();
	FSkyguardMission09ProtectedTargetRuntime* FindProtectedTarget(
		ESkyguardMission09ProtectedTarget Target);
	const FSkyguardMission09ProtectedTargetRuntime* FindProtectedTarget(
		ESkyguardMission09ProtectedTarget Target) const;

	UFUNCTION()
	void HandleBossPhaseChanged(
		ESkyguardBossPhase PreviousPhase,
		ESkyguardBossPhase NewPhase);
	void HandlePilotCommand(ESkyguardPilotCommand Command);
};
