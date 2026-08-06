#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardBossTypes.h"
#include "SkyguardMission02IntegrationDirector.generated.h"

class ASkyguardBreakwaterBoss;
class ASkyguardGunner;
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

UENUM(BlueprintType)
enum class ESkyguardMission02WaveState : uint8
{
	Briefing,
	AwaitingWave,
	WaveActive,
	BossEngaged,
	Completed,
	Failed
};

USTRUCT(BlueprintType)
struct FSkyguardMission02IntegrationReadiness
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
	bool bBreakwaterReady = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bObjectivesReady = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bWavesReady = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bBriefingReady = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bAudioReady = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bCampaignRuntimeStarted = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 ObjectiveCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 WaveCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 RadioLineCount = 0;
};

/**
 * Mission 2 playable-integration boundary.
 *
 * This director promotes the accepted Harbor Shield proxy assembly without
 * mutating it. It binds the governed DataAsset to deterministic waves,
 * fuel-terminal protection, pilot commands and Breakwater's two completion
 * routes.
 */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardMission02IntegrationDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardMission02IntegrationDirector();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission02|Integration")
	bool InitializePlayableMission();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission02|Integration")
	bool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission02|Integration")
	void BindRuntimeActors(
		ASkyguardMissionMapAssemblyDirector* InMapAssembly,
		ASkyguardYak52Aircraft* Aircraft,
		ASkyguardGunner* InGunner,
		ASkyguardBreakwaterBoss* InBreakwater);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission02|Waves")
	bool StartNextWave();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission02|Waves")
	bool NotifyThreatDestroyed(int32 Amount = 1);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission02|Objectives")
	bool NotifyFuelTerminalDamage(int32 Damage);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission02|Integration")
	void SynchronizeRuntimeState();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission02|Integration")
	bool IsCorePlayableReady() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission02|Integration")
	const FSkyguardMission02IntegrationReadiness& GetReadiness() const
	{
		return Readiness;
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission02|Integration")
	USkyguardObjectiveRuntime* GetObjectiveRuntime() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission02|Waves")
	ESkyguardMission02WaveState GetWaveState() const { return WaveState; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission02|Waves")
	int32 GetCurrentWaveIndex() const { return CurrentWaveIndex; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission02|Waves")
	int32 GetRemainingThreatsInWave() const { return RemainingThreatsInWave; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission02|Objectives")
	int32 GetFuelTerminalIntegrity() const { return FuelTerminalIntegrity; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission02|Integration")
	ASkyguardBreakwaterBoss* GetBreakwater() const { return Breakwater; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission02|Integration")
	static FName GetMissionId() { return TEXT("M02_HarborShield"); }

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission02|Integration")
	static bool ValidateMissionContract(
		const USkyguardMissionDefinition* Mission,
		TArray<FText>& OutErrors);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission02")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission02")
	TObjectPtr<USkyguardMissionBriefingComponent> Briefing;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission02")
	TObjectPtr<USkyguardAudioDirectorComponent> AudioDirector;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission02")
	TObjectPtr<USkyguardRadioChatterComponent> RadioChatter;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission02")
	TSoftObjectPtr<USkyguardCampaignDefinition> CampaignDefinition;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission02")
	TSoftObjectPtr<USkyguardMissionDefinition> MissionDefinition;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission02")
	bool bAutoInitialize = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission02")
	bool bAllowBoundedActorSpawning = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission02")
	bool bAutoLaunchAfterBriefing = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission02")
	FVector YakSpawnLocation = FVector(0.f, 26000.f, 5200.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission02")
	FRotator YakSpawnRotation = FRotator(0.f, 0.f, 0.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission02")
	FVector BreakwaterSpawnLocation = FVector(65000.f, -8000.f, 4300.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission02")
	FRotator BreakwaterSpawnRotation = FRotator(0.f, 180.f, 0.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission02", meta=(ClampMin="1"))
	int32 MaximumFuelTerminalIntegrity = 100;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission02")
	FSkyguardMission02IntegrationReadiness Readiness;

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
	TObjectPtr<ASkyguardBreakwaterBoss> Breakwater;

	ESkyguardMission02WaveState WaveState =
		ESkyguardMission02WaveState::Briefing;
	int32 CurrentWaveIndex = -1;
	int32 RemainingThreatsInWave = 0;
	int32 FuelTerminalIntegrity = 100;
	int32 ObservedGovernedWeakPointsDestroyed = 0;
	int32 ObservedArmorLatchesDestroyed = 0;
	bool bInitialized = false;
	bool bSortieLaunched = false;
	bool bMissionCompleted = false;

	bool NotifyObjectiveProgress(FName ObjectiveId, int32 Amount = 1);
	int32 CalculateWaveThreatCount(int32 WaveIndex) const;
	int32 CountGovernedBossProgress() const;
	int32 CountDestroyedArmorLatches() const;
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
