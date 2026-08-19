#pragma once

class ASkyguardDrone;

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardBossTypes.h"
#include "SkyguardStormRainBeatKit.h"
#include "SkyguardMission05IntegrationDirector.generated.h"

class ASkyguardGunner;
class ASkyguardMissionMapAssemblyDirector;
class ASkyguardTempestBoss;
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
enum class ESkyguardMission05WaveState : uint8
{
	Briefing,
	AwaitingWave,
	WaveActive,
	BossEngaged,
	Completed,
	Failed
};

UENUM(BlueprintType)
enum class ESkyguardMission05ProtectedTarget : uint8
{
	OffshorePlatform,
	DistressedTrawler
};

USTRUCT(BlueprintType)
struct FSkyguardMission05ProtectedTargetRuntime
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardMission05ProtectedTarget Target =
		ESkyguardMission05ProtectedTarget::OffshorePlatform;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 Integrity = 100;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bDestroyed = false;
};

USTRUCT(BlueprintType)
struct FSkyguardStormRuntime
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float Turbulence = 0.f;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bLightningActive = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float LightningRemainingSeconds = 0.f;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 LightningFlashCount = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bMaintainingAim = false;
};

USTRUCT(BlueprintType)
struct FSkyguardMission05IntegrationReadiness
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
	bool bTempestReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bObjectivesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bWavesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bStormRuntimeReady = false;
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
	int32 ProtectedTargetCount = 0;
};

/** Mission 5 severe-squall playable-integration boundary. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardMission05IntegrationDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardMission05IntegrationDirector();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Integration")
	bool InitializePlayableMission();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Integration")
	bool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Integration")
	void BindRuntimeActors(
		ASkyguardMissionMapAssemblyDirector* InMapAssembly,
		ASkyguardYak52Aircraft* Aircraft,
		ASkyguardGunner* InGunner,
		ASkyguardTempestBoss* InTempest);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Waves")
	bool StartNextWave();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Waves")
	bool NotifyThreatDestroyed(int32 Amount = 1);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Storm")
	bool TriggerLightningWindow(float DurationSeconds);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Storm")
	bool AdvanceLightningWindow(float DeltaSeconds);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Storm")
	bool AdvanceTurbulence(
		float DeltaSeconds,
		float Turbulence,
		bool bMaintainingAim);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Protection")
	bool NotifyProtectedTargetDamage(
		ESkyguardMission05ProtectedTarget Target,
		int32 Damage);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Objectives")
	bool NotifyProtectedAssetFailed();

	void HandleDroneCityImpact(ASkyguardDrone* Drone);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Integration")
	void SynchronizeRuntimeState();
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission05|Integration")
	bool IsCorePlayableReady() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission05|Integration")
	const FSkyguardMission05IntegrationReadiness& GetReadiness() const
	{
		return Readiness;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission05|Integration")
	USkyguardObjectiveRuntime* GetObjectiveRuntime() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission05|Waves")
	ESkyguardMission05WaveState GetWaveState() const { return WaveState; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission05|Waves")
	int32 GetRemainingThreatsInWave() const { return RemainingThreatsInWave; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission05|Storm")
	const FSkyguardStormRuntime& GetStormRuntime() const
	{
		return StormRuntime;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission05|Protection")
	FSkyguardMission05ProtectedTargetRuntime GetProtectedTarget(
		ESkyguardMission05ProtectedTarget Target) const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission05|Protection")
	int32 GetSurvivingTargetCount() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission05|Integration")
	static FName GetMissionId() { return TEXT("M05_StormFront"); }
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Integration")
	static bool ValidateMissionContract(
		const USkyguardMissionDefinition* Mission,
		TArray<FText>& OutErrors);

	static const FSkyguardStormRainBeatKit& GetStormRainBeatKit();
	bool ApplyStormRainPlayContract(ASkyguardGunner* InGunner) const;
	ESkyguardStormRainBeatKind GetStormRainBeatKind() const;
	void TickStormRainBeatKit(float ElapsedSeconds);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission05")
	TObjectPtr<USceneComponent> Root;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission05")
	TObjectPtr<USkyguardMissionBriefingComponent> Briefing;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission05")
	TObjectPtr<USkyguardAudioDirectorComponent> AudioDirector;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission05")
	TObjectPtr<USkyguardRadioChatterComponent> RadioChatter;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission05")
	TObjectPtr<USkyguardSortiePresentationComponent> SortiePresentation;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission05")
	TSoftObjectPtr<USkyguardCampaignDefinition> CampaignDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission05")
	TSoftObjectPtr<USkyguardMissionDefinition> MissionDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission05")
	bool bAutoInitialize = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission05")
	bool bAllowBoundedActorSpawning = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission05")
	bool bAutoLaunchAfterBriefing = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission05|Campaign")
	FString CampaignSaveSlotName = TEXT("Skyguard52Campaign");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission05|Campaign",
		meta=(ClampMin="0"))
	int32 CampaignSaveUserIndex = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission05")
	FVector YakSpawnLocation = FVector(0.f, -32000.f, 8300.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission05")
	FRotator YakSpawnRotation = FRotator(0.f, 22.f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission05")
	FVector TempestSpawnLocation = FVector(70000.f, 24000.f, 7600.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission05")
	FRotator TempestSpawnRotation = FRotator(0.f, 195.f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission05", meta=(ClampMin="1"))
	int32 MaximumProtectedTargetIntegrity = 100;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission05")
	FSkyguardMission05IntegrationReadiness Readiness;

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
	TObjectPtr<ASkyguardTempestBoss> Tempest;
	UPROPERTY(Transient)
	TArray<FSkyguardMission05ProtectedTargetRuntime> ProtectedTargets;
	UPROPERTY(Transient)
	FSkyguardStormRuntime StormRuntime;

	ESkyguardMission05WaveState WaveState =
		ESkyguardMission05WaveState::Briefing;
	int32 CurrentWaveIndex = -1;
	int32 RemainingThreatsInWave = 0;
	int32 ObservedBossWeakPointsDestroyed = 0;
	int32 ObservedDischargeBoomsDestroyed = 0;
	int32 StormRainBeatIndex = 0;
	float StormRainBeatElapsed = 0.f;
	bool bInitialized = false;
	bool bSortieLaunched = false;
	bool bMissionCompleted = false;

	bool NotifyObjectiveProgress(FName ObjectiveId, int32 Amount = 1);
	int32 CalculateWaveThreatCount(int32 WaveIndex) const;
	int32 CountDestroyedDischargeBooms() const;
	FSkyguardMission05ProtectedTargetRuntime* FindProtectedTarget(
		ESkyguardMission05ProtectedTarget Target);
	const FSkyguardMission05ProtectedTargetRuntime* FindProtectedTarget(
		ESkyguardMission05ProtectedTarget Target) const;
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
