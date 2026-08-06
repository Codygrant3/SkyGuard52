#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardBossTypes.h"
#include "SkyguardMission06IntegrationDirector.generated.h"

class ASkyguardGunner;
class ASkyguardMissionMapAssemblyDirector;
class ASkyguardRunwayBreakerBoss;
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
enum class ESkyguardMission06WaveState : uint8
{
	Briefing,
	AwaitingWave,
	WaveActive,
	BossEngaged,
	Completed,
	Failed
};

UENUM(BlueprintType)
enum class ESkyguardAirfieldTarget : uint8
{
	Runway,
	Hangars,
	ParkedAircraft
};

USTRUCT(BlueprintType)
struct FSkyguardAirfieldTargetRuntime
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardAirfieldTarget Target = ESkyguardAirfieldTarget::Runway;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 Integrity = 100;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bDestroyed = false;
};

USTRUCT(BlueprintType)
struct FSkyguardPayloadWindowRuntime
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bActive = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardAirfieldTarget Target = ESkyguardAirfieldTarget::Runway;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float RemainingSeconds = 0.f;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bJammed = false;
};

USTRUCT(BlueprintType)
struct FSkyguardMission06IntegrationReadiness
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
	bool bRunwayBreakerReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bObjectivesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bWavesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bProtectedTargetsReady = false;
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
	int32 ProtectedTargetCount = 0;
};

/** Mission 6 multi-target airfield-defense playable-integration boundary. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardMission06IntegrationDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardMission06IntegrationDirector();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission06|Integration")
	bool InitializePlayableMission();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission06|Integration")
	bool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission06|Integration")
	void BindRuntimeActors(
		ASkyguardMissionMapAssemblyDirector* InMapAssembly,
		ASkyguardYak52Aircraft* Aircraft,
		ASkyguardGunner* InGunner,
		ASkyguardRunwayBreakerBoss* InRunwayBreaker);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission06|Waves")
	bool StartNextWave();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission06|Waves")
	bool NotifyThreatDestroyed(int32 Amount = 1);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission06|Payload")
	bool StartPayloadWindow(
		ESkyguardAirfieldTarget Target,
		float WindowSeconds);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission06|Payload")
	bool AdvancePayloadWindow(float DeltaSeconds);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission06|Payload")
	bool TryJamActivePayload();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission06|Targets")
	bool NotifyAirfieldTargetDamage(
		ESkyguardAirfieldTarget Target,
		int32 Damage);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission06|Integration")
	void SynchronizeRuntimeState();
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission06|Integration")
	bool IsCorePlayableReady() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission06|Integration")
	const FSkyguardMission06IntegrationReadiness& GetReadiness() const
	{
		return Readiness;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission06|Integration")
	USkyguardObjectiveRuntime* GetObjectiveRuntime() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission06|Waves")
	ESkyguardMission06WaveState GetWaveState() const { return WaveState; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission06|Waves")
	int32 GetRemainingThreatsInWave() const { return RemainingThreatsInWave; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission06|Payload")
	const FSkyguardPayloadWindowRuntime& GetPayloadWindow() const
	{
		return PayloadWindow;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission06|Targets")
	FSkyguardAirfieldTargetRuntime GetTargetRuntime(
		ESkyguardAirfieldTarget Target) const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission06|Targets")
	int32 GetSurvivingTargetCount() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission06|Integration")
	static FName GetMissionId() { return TEXT("M06_AirfieldDefense"); }
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission06|Integration")
	static bool ValidateMissionContract(
		const USkyguardMissionDefinition* Mission,
		TArray<FText>& OutErrors);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission06")
	TObjectPtr<USceneComponent> Root;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission06")
	TObjectPtr<USkyguardMissionBriefingComponent> Briefing;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission06")
	TObjectPtr<USkyguardAudioDirectorComponent> AudioDirector;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission06")
	TObjectPtr<USkyguardRadioChatterComponent> RadioChatter;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission06")
	TSoftObjectPtr<USkyguardCampaignDefinition> CampaignDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission06")
	TSoftObjectPtr<USkyguardMissionDefinition> MissionDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission06")
	bool bAutoInitialize = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission06")
	bool bAllowBoundedActorSpawning = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission06")
	bool bAutoLaunchAfterBriefing = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission06")
	FVector YakSpawnLocation = FVector(0.f, 18000.f, 6600.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission06")
	FRotator YakSpawnRotation = FRotator(0.f, -18.f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission06")
	FVector RunwayBreakerSpawnLocation = FVector(78000.f, 22000.f, 6000.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission06")
	FRotator RunwayBreakerSpawnRotation = FRotator(0.f, 180.f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission06", meta=(ClampMin="1"))
	int32 MaximumTargetIntegrity = 100;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission06", meta=(ClampMin="1"))
	int32 PayloadImpactDamage = 100;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission06")
	FSkyguardMission06IntegrationReadiness Readiness;

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
	TObjectPtr<ASkyguardRunwayBreakerBoss> RunwayBreaker;
	UPROPERTY(Transient)
	TArray<FSkyguardAirfieldTargetRuntime> ProtectedTargets;
	UPROPERTY(Transient)
	FSkyguardPayloadWindowRuntime PayloadWindow;

	ESkyguardMission06WaveState WaveState =
		ESkyguardMission06WaveState::Briefing;
	int32 CurrentWaveIndex = -1;
	int32 RemainingThreatsInWave = 0;
	int32 ObservedBossWeakPointsDestroyed = 0;
	int32 ObservedPayloadRacksDestroyed = 0;
	bool bInitialized = false;
	bool bSortieLaunched = false;
	bool bMissionCompleted = false;

	bool NotifyObjectiveProgress(FName ObjectiveId, int32 Amount = 1);
	int32 CalculateWaveThreatCount(int32 WaveIndex) const;
	int32 CountDestroyedPayloadRacks() const;
	bool IsPayloadJammedForTarget(ESkyguardAirfieldTarget Target) const;
	FSkyguardAirfieldTargetRuntime* FindTarget(
		ESkyguardAirfieldTarget Target);
	const FSkyguardAirfieldTargetRuntime* FindTarget(
		ESkyguardAirfieldTarget Target) const;
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
