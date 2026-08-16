#pragma once

class ASkyguardDrone;

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardBossTypes.h"
#include "SkyguardNightSortieBeatKit.h"
#include "SkyguardMission04IntegrationDirector.generated.h"

class ASkyguardBlackKiteBoss;
class ASkyguardGunner;
class ASkyguardMissionMapAssemblyDirector;
class ASkyguardYak52Aircraft;
class USceneComponent;
class USpotLightComponent;
class USkyguardAudioDirectorComponent;
class USkyguardCampaignDefinition;
class USkyguardCampaignSubsystem;
class USkyguardMissionBriefingComponent;
class USkyguardMissionDefinition;
class USkyguardObjectiveRuntime;
class USkyguardRadioChatterComponent;
class USkyguardSortiePresentationComponent;

UENUM(BlueprintType)
enum class ESkyguardMission04WaveState : uint8
{
	Briefing,
	AwaitingWave,
	WaveActive,
	BossEngaged,
	Completed,
	Failed
};

USTRUCT(BlueprintType)
struct FSkyguardSearchlightTrackRuntime
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bActive = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bBossTracked = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float RemainingSeconds = 0.f;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float HeldSeconds = 0.f;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 CompletedPasses = 0;
};

USTRUCT(BlueprintType)
struct FSkyguardMission04IntegrationReadiness
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
	bool bBlackKiteReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bObjectivesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bWavesReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bSearchlightsReady = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bSubstationReady = false;
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
};

/** Mission 4 blackout/searchlight playable-integration boundary. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardMission04IntegrationDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardMission04IntegrationDirector();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission04|Integration")
	bool InitializePlayableMission();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission04|Integration")
	bool ConfigureMissionDefinition(USkyguardMissionDefinition* Mission);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission04|Integration")
	void BindRuntimeActors(
		ASkyguardMissionMapAssemblyDirector* InMapAssembly,
		ASkyguardYak52Aircraft* Aircraft,
		ASkyguardGunner* InGunner,
		ASkyguardBlackKiteBoss* InBlackKite);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission04|Waves")
	bool StartNextWave();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission04|Waves")
	bool NotifyThreatDestroyed(int32 Amount = 1);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission04|Searchlight")
	bool StartSearchlightWindow(float WindowSeconds);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission04|Searchlight")
	bool AdvanceSearchlightTrack(float DeltaSeconds, bool bBossInTrack);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission04|Substation")
	bool NotifySubstationDamage(int32 Damage);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission04|Objectives")
	bool NotifyProtectedAssetFailed();

	void HandleDroneCityImpact(ASkyguardDrone* Drone);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission04|Integration")
	void SynchronizeRuntimeState();
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission04|Integration")
	bool IsCorePlayableReady() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission04|Integration")
	const FSkyguardMission04IntegrationReadiness& GetReadiness() const
	{
		return Readiness;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission04|Integration")
	USkyguardObjectiveRuntime* GetObjectiveRuntime() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission04|Waves")
	ESkyguardMission04WaveState GetWaveState() const { return WaveState; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission04|Waves")
	int32 GetRemainingThreatsInWave() const { return RemainingThreatsInWave; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission04|Searchlight")
	const FSkyguardSearchlightTrackRuntime& GetSearchlightRuntime() const
	{
		return SearchlightRuntime;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission04|Substation")
	int32 GetSubstationIntegrity() const { return SubstationIntegrity; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission04|Integration")
	static FName GetMissionId() { return TEXT("M04_NightBlackout"); }
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission04|Integration")
	static bool ValidateMissionContract(
		const USkyguardMissionDefinition* Mission,
		TArray<FText>& OutErrors);

	const FSkyguardNightSortieBeatKit& GetNightBeatKit() const;
	ESkyguardNightSortieBeatKind GetNightBeatKind() const;
	int32 GetNightBeatIndex() const { return NightBeatIndex; }
	void TickNightBeatKit(float DeltaSeconds);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission04")
	TObjectPtr<USceneComponent> Root;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission04")
	TObjectPtr<USpotLightComponent> SearchlightPort;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission04")
	TObjectPtr<USpotLightComponent> SearchlightStarboard;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission04")
	TObjectPtr<USkyguardMissionBriefingComponent> Briefing;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission04")
	TObjectPtr<USkyguardAudioDirectorComponent> AudioDirector;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission04")
	TObjectPtr<USkyguardRadioChatterComponent> RadioChatter;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission04")
	TObjectPtr<USkyguardSortiePresentationComponent> SortiePresentation;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04")
	TSoftObjectPtr<USkyguardCampaignDefinition> CampaignDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04")
	TSoftObjectPtr<USkyguardMissionDefinition> MissionDefinition;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04")
	bool bAutoInitialize = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04")
	bool bAllowBoundedActorSpawning = true;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04")
	bool bAutoLaunchAfterBriefing = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04|Campaign")
	FString CampaignSaveSlotName = TEXT("Skyguard52Campaign");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04|Campaign",
		meta=(ClampMin="0"))
	int32 CampaignSaveUserIndex = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04")
	FVector YakSpawnLocation = FVector(0.f, 12000.f, 5800.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04")
	FRotator YakSpawnRotation = FRotator(0.f, -12.f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04")
	FVector BlackKiteSpawnLocation = FVector(69000.f, -11000.f, 5200.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04")
	FRotator BlackKiteSpawnRotation = FRotator(0.f, 170.f, 0.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04", meta=(ClampMin="0.1"))
	float RequiredTrackSeconds = 3.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04", meta=(ClampMin="1"))
	int32 MaximumSubstationIntegrity = 100;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission04", meta=(ClampMin="1"))
	int32 MissedTrackDamage = 35;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission04")
	FSkyguardMission04IntegrationReadiness Readiness;

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
	TObjectPtr<ASkyguardBlackKiteBoss> BlackKite;
	UPROPERTY(Transient)
	FSkyguardSearchlightTrackRuntime SearchlightRuntime;

	ESkyguardMission04WaveState WaveState =
		ESkyguardMission04WaveState::Briefing;
	int32 CurrentWaveIndex = -1;
	int32 RemainingThreatsInWave = 0;
	int32 SubstationIntegrity = 100;
	int32 ObservedBossWeakPointsDestroyed = 0;
	int32 NightBeatIndex = 0;
	float NightBeatElapsed = 0.f;
	bool bInitialized = false;
	bool bSortieLaunched = false;
	bool bMissionCompleted = false;
	void ApplyNightThermalContract();

	bool NotifyObjectiveProgress(FName ObjectiveId, int32 Amount = 1);
	int32 CalculateWaveThreatCount(int32 WaveIndex) const;
	void ResolveOrSpawnActors();
	void ConfigurePresentation();
	void UpdateReadiness();
	void TryLaunchSortie();
	void CompleteMissionIfReady();
	void SetSearchlightPresentation(bool bEnabled);

	UFUNCTION()
	void HandleBossPhaseChanged(
		ESkyguardBossPhase PreviousPhase,
		ESkyguardBossPhase NewPhase);
	void HandlePilotCommand(ESkyguardPilotCommand Command);
};
