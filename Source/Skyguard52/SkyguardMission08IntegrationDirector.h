#pragma once

class ASkyguardDrone;

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardBossTypes.h"
#include "SkyguardStormRainBeatKit.h"
#include "SkyguardMission08IntegrationDirector.generated.h"

class ASkyguardGunner;
class ASkyguardLifelineHunterBoss;
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
enum class ESkyguardMission08WaveState : uint8
{
	Briefing,
	AwaitingWave,
	WaveActive,
	BossEngaged,
	Completed,
	Failed
};

UENUM(BlueprintType)
enum class ESkyguardMission08ProtectedTarget : uint8
{
	RescueHelicopter,
	SurvivorsAndRafts,
	RescueVessel
};

USTRUCT(BlueprintType)
struct FSkyguardMission08ProtectedTargetRuntime
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardMission08ProtectedTarget Target =
		ESkyguardMission08ProtectedTarget::RescueHelicopter;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 Integrity = 100;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bDestroyed = false;
};

USTRUCT(BlueprintType)
struct FSkyguardHoistWindowRuntime
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bActive = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float RemainingSeconds = 0.f;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float CoveredSeconds = 0.f;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 CompletedWindows = 0;
};

USTRUCT(BlueprintType)
struct FSkyguardMission08IntegrationReadiness
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
	bool bLifelineHunterReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bObjectivesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bWavesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bRescueAnimationReady = false;
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

/** Mission 8 rescue-orbit, hoist and friendly-exclusion boundary. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardMission08IntegrationDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardMission08IntegrationDirector();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Integration")
	bool InitializePlayableMission();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Integration")
	bool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Integration")
	void BindRuntimeActors(
		ASkyguardMissionMapAssemblyDirector* InMapAssembly,
		ASkyguardYak52Aircraft* Aircraft,
		ASkyguardGunner* InGunner,
		ASkyguardLifelineHunterBoss* InLifelineHunter);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Waves")
	bool StartNextWave();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Waves")
	bool NotifyThreatDestroyed(int32 Amount = 1);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Hoist")
	bool StartHoistWindow(float WindowSeconds);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Hoist")
	bool AdvanceHoistWindow(float DeltaSeconds, bool bCoverMaintained);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Safety")
	bool ValidateWeaponRelease(
		float FriendlySeparationMeters,
		bool bShotIntersectsFriendlyCorridor);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Protection")
	bool NotifyProtectedTargetDamage(
		ESkyguardMission08ProtectedTarget Target,
		int32 Damage);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Objectives")
	bool NotifyProtectedAssetFailed();

	void HandleDroneCityImpact(ASkyguardDrone* Drone);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Integration")
	void SynchronizeRuntimeState();
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission08|Integration")
	bool IsCorePlayableReady() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission08|Integration")
	const FSkyguardMission08IntegrationReadiness& GetReadiness() const
	{
		return Readiness;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission08|Integration")
	USkyguardObjectiveRuntime* GetObjectiveRuntime() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission08|Waves")
	ESkyguardMission08WaveState GetWaveState() const { return WaveState; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission08|Waves")
	int32 GetRemainingThreatsInWave() const { return RemainingThreatsInWave; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission08|Hoist")
	const FSkyguardHoistWindowRuntime& GetHoistRuntime() const
	{
		return HoistRuntime;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission08|Safety")
	int32 GetRejectedWeaponReleases() const
	{
		return RejectedWeaponReleases;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission08|Protection")
	FSkyguardMission08ProtectedTargetRuntime GetProtectedTarget(
		ESkyguardMission08ProtectedTarget Target) const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission08|Protection")
	int32 GetSurvivingTargetCount() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission08|Integration")
	static FName GetMissionId() { return TEXT("M08_RescueCover"); }
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Integration")
	static bool ValidateMissionContract(
		const USkyguardMissionDefinition* Mission,
		TArray<FText>& OutErrors);

	static const FSkyguardStormRainBeatKit& GetStormRainBeatKit();
	bool ApplyStormRainPlayContract(ASkyguardGunner* InGunner) const;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08")
	TObjectPtr<USceneComponent> Root;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08|Rescue")
	TObjectPtr<USceneComponent> RescueHelicopterAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08|Rescue")
	TObjectPtr<USceneComponent> HoistCableAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08|Rescue")
	TObjectPtr<USceneComponent> SurvivorsAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08|Rescue")
	TObjectPtr<USceneComponent> RaftsAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08|Rescue")
	TObjectPtr<USceneComponent> RescueVesselAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08")
	TObjectPtr<USkyguardMissionBriefingComponent> Briefing;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08")
	TObjectPtr<USkyguardAudioDirectorComponent> AudioDirector;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08")
	TObjectPtr<USkyguardRadioChatterComponent> RadioChatter;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08")
	TObjectPtr<USkyguardSortiePresentationComponent> SortiePresentation;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08")
	TSoftObjectPtr<USkyguardCampaignDefinition> CampaignDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08")
	TSoftObjectPtr<USkyguardMissionDefinition> MissionDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08")
	bool bAutoInitialize = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08")
	bool bAllowBoundedActorSpawning = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08")
	bool bAutoLaunchAfterBriefing = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08|Campaign")
	FString CampaignSaveSlotName = TEXT("Skyguard52Campaign");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08|Campaign",
		meta=(ClampMin="0"))
	int32 CampaignSaveUserIndex = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08")
	FVector YakSpawnLocation = FVector(0.f, 9000.f, 6200.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08")
	FRotator YakSpawnRotation = FRotator(0.f, 24.f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08")
	FVector LifelineHunterSpawnLocation = FVector(57000.f, -9000.f, 5400.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08")
	FRotator LifelineHunterSpawnRotation = FRotator(0.f, 160.f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08|Hoist", meta=(ClampMin="0.1"))
	float RequiredCoveredSeconds = 4.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08|Safety", meta=(ClampMin="1.0"))
	float MinimumWeaponSeparationMeters = 450.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission08", meta=(ClampMin="1"))
	int32 MaximumProtectedTargetIntegrity = 100;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08")
	FSkyguardMission08IntegrationReadiness Readiness;

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
	TObjectPtr<ASkyguardLifelineHunterBoss> LifelineHunter;
	UPROPERTY(Transient)
	TArray<FSkyguardMission08ProtectedTargetRuntime> ProtectedTargets;
	UPROPERTY(Transient)
	FSkyguardHoistWindowRuntime HoistRuntime;

	ESkyguardMission08WaveState WaveState =
		ESkyguardMission08WaveState::Briefing;
	int32 CurrentWaveIndex = -1;
	int32 RemainingThreatsInWave = 0;
	int32 ObservedBossWeakPointsDestroyed = 0;
	int32 RejectedWeaponReleases = 0;
	float RescueAnimationSeconds = 0.f;
	bool bInitialized = false;
	bool bSortieLaunched = false;
	bool bMissionCompleted = false;

	bool NotifyObjectiveProgress(FName ObjectiveId, int32 Amount = 1);
	int32 CalculateWaveThreatCount(int32 WaveIndex) const;
	FSkyguardMission08ProtectedTargetRuntime* FindProtectedTarget(
		ESkyguardMission08ProtectedTarget Target);
	const FSkyguardMission08ProtectedTargetRuntime* FindProtectedTarget(
		ESkyguardMission08ProtectedTarget Target) const;
	void ResolveOrSpawnActors();
	void ConfigurePresentation();
	void UpdateReadiness();
	void UpdateRescueAnimation(float DeltaSeconds);
	void TryLaunchSortie();
	void CompleteMissionIfReady();

	UFUNCTION()
	void HandleBossPhaseChanged(
		ESkyguardBossPhase PreviousPhase,
		ESkyguardBossPhase NewPhase);
	void HandlePilotCommand(ESkyguardPilotCommand Command);
};
