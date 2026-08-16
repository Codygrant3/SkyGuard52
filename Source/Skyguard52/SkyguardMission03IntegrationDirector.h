#pragma once

class ASkyguardDrone;

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardBossTypes.h"
#include "SkyguardDaySortieBeatKit.h"
#include "SkyguardMission03IntegrationDirector.generated.h"

class ASkyguardGunner;
class ASkyguardMissionMapAssemblyDirector;
class ASkyguardRoadHunterBoss;
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
enum class ESkyguardMission03WaveState : uint8
{
	Briefing,
	AwaitingWave,
	WaveActive,
	BossEngaged,
	Completed,
	Failed
};

UENUM(BlueprintType)
enum class ESkyguardConvoyRouteState : uint8
{
	Holding,
	Advancing,
	TunnelReached,
	Destroyed
};

USTRUCT(BlueprintType)
struct FSkyguardMission03IntegrationReadiness
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
	bool bRoadHunterReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bObjectivesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bWavesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bConvoyRouteReady = false;
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
	int32 RadioLineCount = 0;
};

/** Mission 3 moving-convoy playable-integration boundary. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardMission03IntegrationDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardMission03IntegrationDirector();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission03|Integration")
	bool InitializePlayableMission();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission03|Integration")
	bool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission03|Integration")
	void BindRuntimeActors(
		ASkyguardMissionMapAssemblyDirector* InMapAssembly,
		ASkyguardYak52Aircraft* Aircraft,
		ASkyguardGunner* InGunner,
		ASkyguardRoadHunterBoss* InRoadHunter);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission03|Waves")
	bool StartNextWave();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission03|Waves")
	bool NotifyThreatDestroyed(int32 Amount = 1);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission03|Convoy")
	bool AdvanceConvoyByDistance(float DistanceCentimeters);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission03|Convoy")
	bool NotifyConvoyDamage(int32 Damage);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission03|Objectives")
	bool NotifyProtectedAssetFailed();

	void HandleDroneCityImpact(ASkyguardDrone* Drone);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission03|Integration")
	void SynchronizeRuntimeState();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission03|Integration")
	bool IsCorePlayableReady() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission03|Integration")
	const FSkyguardMission03IntegrationReadiness& GetReadiness() const
	{
		return Readiness;
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission03|Integration")
	USkyguardObjectiveRuntime* GetObjectiveRuntime() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission03|Waves")
	ESkyguardMission03WaveState GetWaveState() const { return WaveState; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission03|Waves")
	int32 GetCurrentWaveIndex() const { return CurrentWaveIndex; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission03|Waves")
	int32 GetRemainingThreatsInWave() const { return RemainingThreatsInWave; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission03|Convoy")
	ESkyguardConvoyRouteState GetConvoyRouteState() const
	{
		return ConvoyRouteState;
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission03|Convoy")
	float GetConvoyRouteAlpha() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission03|Convoy")
	FVector GetConvoyWorldLocation() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission03|Convoy")
	int32 GetConvoyIntegrity() const { return ConvoyIntegrity; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission03|Integration")
	static FName GetMissionId() { return TEXT("M03_ConvoyEscort"); }

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission03|Integration")
	static bool ValidateMissionContract(
		const USkyguardMissionDefinition* Mission,
		TArray<FText>& OutErrors);

	const FSkyguardDaySortieBeatKit& GetDayBeatKit() const;
	ESkyguardDaySortieBeatKind GetDayBeatKind() const;
	int32 GetDayBeatIndex() const { return DayBeatIndex; }
	void TickDayBeatKit(float DeltaSeconds);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission03")
	TObjectPtr<USceneComponent> Root;
	/**
	 * Runtime attachment point for the protected convoy visuals. The director
	 * moves this anchor along the governed map spline; authored vehicle actors
	 * can be attached without duplicating route logic.
	 */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission03|Convoy")
	TObjectPtr<USceneComponent> ConvoyRuntimeAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission03")
	TObjectPtr<USkyguardMissionBriefingComponent> Briefing;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission03")
	TObjectPtr<USkyguardAudioDirectorComponent> AudioDirector;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission03")
	TObjectPtr<USkyguardRadioChatterComponent> RadioChatter;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission03")
	TObjectPtr<USkyguardSortiePresentationComponent> SortiePresentation;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission03")
	TSoftObjectPtr<USkyguardCampaignDefinition> CampaignDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission03")
	TSoftObjectPtr<USkyguardMissionDefinition> MissionDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission03")
	bool bAutoInitialize = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission03")
	bool bAllowBoundedActorSpawning = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission03")
	bool bAutoLaunchAfterBriefing = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission03|Campaign")
	FString CampaignSaveSlotName = TEXT("Skyguard52Campaign");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission03|Campaign",
		meta=(ClampMin="0"))
	int32 CampaignSaveUserIndex = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission03")
	FVector YakSpawnLocation = FVector(0.f, -5000.f, 7000.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission03")
	FRotator YakSpawnRotation = FRotator(0.f, 27.5f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission03")
	FVector RoadHunterSpawnLocation = FVector(70000.f, 45000.f, 6100.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission03")
	FRotator RoadHunterSpawnRotation = FRotator(0.f, 210.f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission03", meta=(ClampMin="1"))
	int32 MaximumConvoyIntegrity = 100;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission03")
	FSkyguardMission03IntegrationReadiness Readiness;

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
	TObjectPtr<ASkyguardRoadHunterBoss> RoadHunter;

	ESkyguardMission03WaveState WaveState =
		ESkyguardMission03WaveState::Briefing;
	ESkyguardConvoyRouteState ConvoyRouteState =
		ESkyguardConvoyRouteState::Holding;
	int32 CurrentWaveIndex = -1;
	int32 RemainingThreatsInWave = 0;
	int32 ConvoyIntegrity = 100;
	float ConvoyDistanceCentimeters = 0.f;
	int32 ObservedBossWeakPointsDestroyed = 0;
	int32 DayBeatIndex = 0;
	float DayBeatElapsed = 0.f;
	bool bCameraObjectiveRecorded = false;
	bool bInitialized = false;
	bool bSortieLaunched = false;
	bool bMissionCompleted = false;

	bool NotifyObjectiveProgress(FName ObjectiveId, int32 Amount = 1);
	int32 CalculateWaveThreatCount(int32 WaveIndex) const;
	float GetConvoyRouteLength() const;
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
