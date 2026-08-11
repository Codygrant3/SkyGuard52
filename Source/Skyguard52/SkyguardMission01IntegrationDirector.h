#pragma once

class ASkyguardDrone;

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardBossTypes.h"
#include "SkyguardMission01IntegrationDirector.generated.h"

class ASkyguardGunner;
class ASkyguardMission01EnvironmentDirector;
class ASkyguardPathfinderBoss;
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

USTRUCT(BlueprintType)
struct FSkyguardMission01IntegrationReadiness
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bMissionDefinitionValid = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bCampaignDefinitionValid = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bEnvironmentReady = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bYakRuntimeReady = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bGunnerReady = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bPathfinderReady = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bObjectivesReady = false;

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
	int32 RadioLineCount = 0;
};

/**
 * Mission 1 playable orchestration boundary.
 *
 * The director composes already-accepted systems. It does not replace their
 * art, flight, combat, boss, audio, campaign, or environment implementation.
 * It is safe to place once in a level: initialization is idempotent and actor
 * discovery always precedes bounded native-class spawning.
 */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardMission01IntegrationDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardMission01IntegrationDirector();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Integration")
	bool InitializePlayableMission();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Integration")
	bool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Integration")
	void BindRuntimeActors(
		ASkyguardYak52Aircraft* Aircraft,
		ASkyguardGunner* InGunner,
		ASkyguardPathfinderBoss* InPathfinder);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Integration")
	bool NotifyObjectiveProgress(FName ObjectiveId, int32 Amount = 1);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Integration")
	bool NotifyProtectedAssetFailed();

	void HandleDroneCityImpact(ASkyguardDrone* Drone);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Integration")
	void SynchronizeRuntimeState();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Integration")
	bool IsCorePlayableReady() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Integration")
	const FSkyguardMission01IntegrationReadiness& GetReadiness() const
	{
		return Readiness;
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Integration")
	USkyguardObjectiveRuntime* GetObjectiveRuntime() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Integration")
	ASkyguardYak52Aircraft* GetAircraft() const { return YakAircraft; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Integration")
	ASkyguardGunner* GetGunner() const { return Gunner; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Integration")
	ASkyguardPathfinderBoss* GetPathfinder() const { return Pathfinder; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Integration")
	static FName GetMissionId() { return TEXT("M01_CoastalIntercept"); }

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Integration")
	static bool ValidateMissionContract(
		const USkyguardMissionDefinition* Mission,
		TArray<FText>& OutErrors);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01")
	TObjectPtr<USkyguardMissionBriefingComponent> Briefing;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01")
	TObjectPtr<USkyguardAudioDirectorComponent> AudioDirector;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01")
	TObjectPtr<USkyguardRadioChatterComponent> RadioChatter;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01")
	TObjectPtr<USkyguardSortiePresentationComponent> SortiePresentation;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01")
	TSoftObjectPtr<USkyguardCampaignDefinition> CampaignDefinition;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01")
	TSoftObjectPtr<USkyguardMissionDefinition> MissionDefinition;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01")
	bool bAutoInitialize = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01")
	bool bAllowBoundedActorSpawning = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01")
	bool bAutoLaunchAfterBriefing = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Campaign")
	FString CampaignSaveSlotName = TEXT("Skyguard52Campaign");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Campaign",
		meta=(ClampMin="0"))
	int32 CampaignSaveUserIndex = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01")
	FVector YakSpawnLocation = FVector(0.f, -18000.f, 6500.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01")
	FRotator YakSpawnRotation = FRotator(0.f, 5.4f, 0.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01")
	FVector PathfinderSpawnLocation = FVector(56000.f, -7800.f, 6100.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01")
	FRotator PathfinderSpawnRotation = FRotator(0.f, 180.f, 0.f);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01")
	FSkyguardMission01IntegrationReadiness Readiness;

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
	TObjectPtr<ASkyguardMission01EnvironmentDirector> Environment;

	UPROPERTY(Transient)
	TObjectPtr<ASkyguardYak52Aircraft> YakAircraft;

	UPROPERTY(Transient)
	TObjectPtr<ASkyguardGunner> Gunner;

	UPROPERTY(Transient)
	TObjectPtr<ASkyguardPathfinderBoss> Pathfinder;

	int32 ObservedWeakPointsDestroyed = 0;
	bool bInitialized = false;
	bool bSortieLaunched = false;
	bool bMissionCompleted = false;

	void ResolveOrSpawnActors();
	void ConfigurePresentation();
	void UpdateReadiness();
	void TryLaunchSortie();
	void CompleteMissionIfReady();

	UFUNCTION()
	void HandleBossPhaseChanged(
		ESkyguardBossPhase PreviousPhase,
		ESkyguardBossPhase NewPhase);

	UFUNCTION()
	void HandlePilotCommand(ESkyguardPilotCommand Command);
};
