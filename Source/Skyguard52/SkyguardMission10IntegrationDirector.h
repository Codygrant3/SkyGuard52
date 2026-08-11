#pragma once

class ASkyguardDrone;

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardBossTypes.h"
#include "SkyguardMission10IntegrationDirector.generated.h"

class ASkyguardGunner;
class ASkyguardLastFlightBoss;
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
enum class ESkyguardMission10RoutePhase : uint8
{
	Briefing,
	Highway,
	FerryTerminal,
	EvacuationShip,
	BossEngaged,
	Completed,
	Failed
};

UENUM(BlueprintType)
enum class ESkyguardMission10ProtectedGroup : uint8
{
	Convoy,
	FerryTerminal,
	EvacuationShip
};

USTRUCT(BlueprintType)
struct FSkyguardMission10ProtectedRuntime
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	ESkyguardMission10ProtectedGroup Group =
		ESkyguardMission10ProtectedGroup::Convoy;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 Integrity = 100;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bDestroyed = false;
};

USTRUCT(BlueprintType)
struct FSkyguardMission10IntegrationReadiness
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
	bool bLastFlightReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bObjectivesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bPhaseWavesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bEvacuationPresentationReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bProtectedGroupsReady = false;
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
	int32 ProtectedGroupCount = 0;
};

/** Three-stage evacuation-finale mission boundary. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardMission10IntegrationDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardMission10IntegrationDirector();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Integration")
	bool InitializePlayableMission();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Integration")
	bool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Integration")
	void BindRuntimeActors(
		ASkyguardMissionMapAssemblyDirector* InMapAssembly,
		ASkyguardYak52Aircraft* Aircraft,
		ASkyguardGunner* InGunner,
		ASkyguardLastFlightBoss* InLastFlight);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Waves")
	bool StartPhaseWave();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Waves")
	bool NotifyThreatDestroyed(int32 Amount = 1);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Safety")
	bool ValidateWeaponRelease(
		float CivilianSeparationMeters,
		bool bShotIntersectsCivilianCorridor);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Protection")
	bool NotifyProtectedGroupDamage(
		ESkyguardMission10ProtectedGroup Group,
		int32 Damage);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Objectives")
	bool NotifyProtectedAssetFailed();

	void HandleDroneCityImpact(ASkyguardDrone* Drone);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Integration")
	void SynchronizeRuntimeState();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Integration")
	bool IsCorePlayableReady() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Integration")
	const FSkyguardMission10IntegrationReadiness& GetReadiness() const
	{
		return Readiness;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Integration")
	USkyguardObjectiveRuntime* GetObjectiveRuntime() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Waves")
	ESkyguardMission10RoutePhase GetRoutePhase() const
	{
		return RoutePhase;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Waves")
	int32 GetRemainingThreatsInWave() const
	{
		return RemainingThreatsInWave;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Safety")
	int32 GetRejectedWeaponReleases() const
	{
		return RejectedWeaponReleases;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Protection")
	FSkyguardMission10ProtectedRuntime GetProtectedGroup(
		ESkyguardMission10ProtectedGroup Group) const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Protection")
	int32 GetSurvivingProtectedGroupCount() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Integration")
	static FName GetMissionId() { return TEXT("M10_EvacuationFinale"); }
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Integration")
	static bool ValidateMissionContract(
		const USkyguardMissionDefinition* Mission,
		TArray<FText>& OutErrors);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10")
	TObjectPtr<USceneComponent> Root;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Evacuation")
	TObjectPtr<USceneComponent> HighwayConvoyAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Evacuation")
	TObjectPtr<USceneComponent> BusAAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Evacuation")
	TObjectPtr<USceneComponent> BusBAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Evacuation")
	TObjectPtr<USceneComponent> AmbulanceAAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Evacuation")
	TObjectPtr<USceneComponent> AmbulanceBAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Evacuation")
	TObjectPtr<USceneComponent> FerryTerminalAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Evacuation")
	TObjectPtr<USceneComponent> EvacuationShipAnchor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10")
	TObjectPtr<USkyguardMissionBriefingComponent> Briefing;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10")
	TObjectPtr<USkyguardAudioDirectorComponent> AudioDirector;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10")
	TObjectPtr<USkyguardRadioChatterComponent> RadioChatter;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10")
	TObjectPtr<USkyguardSortiePresentationComponent> SortiePresentation;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission10")
	TSoftObjectPtr<USkyguardCampaignDefinition> CampaignDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission10")
	TSoftObjectPtr<USkyguardMissionDefinition> MissionDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission10")
	bool bAutoInitialize = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission10")
	bool bAllowBoundedActorSpawning = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission10")
	bool bAutoLaunchAfterBriefing = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission10|Campaign")
	FString CampaignSaveSlotName = TEXT("Skyguard52Campaign");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission10|Campaign",
		meta=(ClampMin="0"))
	int32 CampaignSaveUserIndex = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission10")
	FVector YakSpawnLocation = FVector(0.f, 30000.f, 9200.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission10")
	FRotator YakSpawnRotation = FRotator(0.f, -24.f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission10")
	FVector LastFlightSpawnLocation = FVector(81000.f, -13000.f, 7800.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission10")
	FRotator LastFlightSpawnRotation = FRotator(0.f, 195.f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission10|Safety", meta=(ClampMin="1.0"))
	float MinimumWeaponSeparationMeters = 550.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission10", meta=(ClampMin="1"))
	int32 MaximumProtectedIntegrity = 100;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10")
	FSkyguardMission10IntegrationReadiness Readiness;

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
	TObjectPtr<ASkyguardLastFlightBoss> LastFlight;
	UPROPERTY(Transient)
	TArray<FSkyguardMission10ProtectedRuntime> ProtectedGroups;

	ESkyguardMission10RoutePhase RoutePhase =
		ESkyguardMission10RoutePhase::Briefing;
	int32 CurrentWaveIndex = -1;
	int32 RemainingThreatsInWave = 0;
	int32 ObservedBossMilestones = 0;
	int32 RejectedWeaponReleases = 0;
	float EvacuationAnimationSeconds = 0.f;
	bool bInitialized = false;
	bool bSortieLaunched = false;
	bool bMissionCompleted = false;

	bool NotifyObjectiveProgress(FName ObjectiveId, int32 Amount = 1);
	int32 CalculateWaveThreatCount(int32 WaveIndex) const;
	FSkyguardMission10ProtectedRuntime* FindProtectedGroup(
		ESkyguardMission10ProtectedGroup Group);
	const FSkyguardMission10ProtectedRuntime* FindProtectedGroup(
		ESkyguardMission10ProtectedGroup Group) const;
	void ResolveOrSpawnActors();
	void ConfigurePresentation();
	void UpdateReadiness();
	void UpdateEvacuationAnimation(float DeltaSeconds);
	void TryLaunchSortie();
	void CompleteMissionIfReady();

	UFUNCTION()
	void HandleBossPhaseChanged(
		ESkyguardBossPhase PreviousPhase,
		ESkyguardBossPhase NewPhase);
	void HandlePilotCommand(ESkyguardPilotCommand Command);
};
