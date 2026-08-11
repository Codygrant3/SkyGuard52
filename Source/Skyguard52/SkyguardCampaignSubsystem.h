#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "SkyguardCampaignSaveGame.h"
#include "SkyguardMissionTypes.h"
#include "SkyguardCampaignSubsystem.generated.h"

class ASkyguardGunner;
class USkyguardCampaignDefinition;
class USkyguardCampaignSaveGame;
class USkyguardMissionDefinition;
class USkyguardObjectiveRuntime;
class USkyguardRouteRuntime;

UCLASS(BlueprintType)
class SKYGUARD52_API USkyguardCampaignSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Campaign")
	bool ConfigureCampaign(USkyguardCampaignDefinition* InCampaign);

	UFUNCTION(BlueprintPure, Category = "Campaign")
	bool CanStartMission(FName MissionId) const;

	UFUNCTION(BlueprintCallable, Category = "Campaign")
	bool StartMission(FName MissionId);

	UFUNCTION(BlueprintCallable, Category = "Campaign")
	bool AddObjectiveProgress(FName ObjectiveId, int32 Amount = 1);

	UFUNCTION(BlueprintCallable, Category = "Campaign")
	bool FailObjective(FName ObjectiveId);

	UFUNCTION(BlueprintCallable, Category = "Campaign")
	bool CompleteSurviveObjectiveIfIntact(FName ObjectiveId);

	UFUNCTION(BlueprintCallable, Category = "Campaign")
	bool CompleteActiveMission(FSkyguardMissionResult& InOutResult);

	/**
	 * Completes and scores the active mission, builds the player-facing
	 * debrief, then attempts to persist progression. A completed sortie remains
	 * complete if disk persistence fails; inspect LastDebrief.bProgressSaved
	 * and offer RetrySaveLastDebrief before allowing mission travel.
	 */
	UFUNCTION(BlueprintCallable, Category = "Campaign|Sortie")
	bool FinalizeActiveMission(
		FSkyguardMissionResult& InOutResult,
		const FString& SlotName = TEXT("Skyguard52Campaign"),
		int32 UserIndex = 0);

	/**
	 * Ends the active mission as a failure. Builds FailureDebrief presentation,
	 * clears the active mission, and does not persist progression unlocks.
	 * Combat fields on InOutResult should already be filled by the caller
	 * (see FillResultCombatStats).
	 */
	UFUNCTION(BlueprintCallable, Category = "Campaign|Sortie")
	bool FailActiveMission(
		FSkyguardMissionResult& InOutResult,
		const FString& SlotName = TEXT("Skyguard52Campaign"),
		int32 UserIndex = 0);

	/** Copies gunner sortie combat counters and elapsed mission time into Result. */
	UFUNCTION(BlueprintCallable, Category = "Campaign|Sortie",
		meta = (WorldContext = "WorldContextObject"))
	void FillResultCombatStats(
		FSkyguardMissionResult& InOutResult,
		const ASkyguardGunner* Gunner,
		const UObject* WorldContextObject) const;

	UFUNCTION(BlueprintPure, Category = "Campaign|Sortie",
		meta = (WorldContext = "WorldContextObject"))
	float GetActiveMissionElapsedSeconds(
		const UObject* WorldContextObject) const;

	UFUNCTION(BlueprintCallable, Category = "Campaign|Sortie")
	bool RetrySaveLastDebrief(
		const FString& SlotName = TEXT("Skyguard52Campaign"),
		int32 UserIndex = 0);

	UFUNCTION(BlueprintCallable, Category = "Campaign|Sortie")
	bool AcknowledgeDebrief();

	UFUNCTION(BlueprintPure, Category = "Campaign|Sortie")
	const FSkyguardMissionDebrief& GetLastDebrief() const
	{
		return LastDebrief;
	}

	UFUNCTION(BlueprintPure, Category = "Campaign|Sortie")
	bool CanTravelToNextMission() const;

	UFUNCTION(BlueprintPure, Category = "Campaign|Sortie")
	FString GetNextMissionMapPackageName() const;

	UFUNCTION(BlueprintCallable, Category = "Campaign|Sortie",
		meta = (WorldContext = "WorldContextObject"))
	bool TravelToNextMission(UObject* WorldContextObject);

	UFUNCTION(BlueprintCallable, Category = "Campaign")
	bool ApplySaveGame(const USkyguardCampaignSaveGame* SaveGame);

	UFUNCTION(BlueprintCallable, Category = "Campaign")
	USkyguardCampaignSaveGame* BuildSaveGame() const;

	UFUNCTION(BlueprintCallable, Category = "Campaign|Persistence")
	bool SaveCampaignToSlot(
		const FString& SlotName = TEXT("Skyguard52Campaign"),
		int32 UserIndex = 0) const;

	UFUNCTION(BlueprintCallable, Category = "Campaign|Persistence")
	bool LoadCampaignFromSlot(
		const FString& SlotName = TEXT("Skyguard52Campaign"),
		int32 UserIndex = 0);

	UFUNCTION(BlueprintCallable, Category = "Campaign|Persistence")
	bool DeleteCampaignSlot(
		const FString& SlotName = TEXT("Skyguard52Campaign"),
		int32 UserIndex = 0) const;

	UFUNCTION(BlueprintPure, Category = "Campaign|Persistence")
	static bool IsValidCampaignSlotName(const FString& SlotName);

	UFUNCTION(BlueprintPure, Category = "Campaign")
	bool IsMissionUnlocked(FName MissionId) const;

	UFUNCTION(BlueprintPure, Category = "Campaign")
	int32 GetEarnedCampaignMedals() const;

	UFUNCTION(BlueprintPure, Category = "Campaign")
	USkyguardMissionDefinition* GetActiveMission() const { return ActiveMission; }

	UFUNCTION(BlueprintPure, Category = "Campaign")
	USkyguardObjectiveRuntime* GetObjectiveRuntime() const { return ObjectiveRuntime; }

	UFUNCTION(BlueprintPure, Category = "Campaign")
	USkyguardRouteRuntime* GetRouteRuntime() const { return RouteRuntime; }

	const TMap<FName, FSkyguardMissionSaveRecord>& GetMissionRecords() const
	{
		return MissionRecords;
	}

	static int32 CalculateMissionScore(
		const USkyguardMissionDefinition& Mission,
		const FSkyguardMissionResult& Result);

	static int32 CalculateMedalTier(
		const FSkyguardMissionScoreRules& Rules,
		int32 Score);

private:
	UPROPERTY(Transient)
	TObjectPtr<USkyguardCampaignDefinition> Campaign;

	UPROPERTY(Transient)
	TObjectPtr<USkyguardMissionDefinition> ActiveMission;

	UPROPERTY(Transient)
	TObjectPtr<USkyguardObjectiveRuntime> ObjectiveRuntime;

	UPROPERTY(Transient)
	TObjectPtr<USkyguardRouteRuntime> RouteRuntime;

	UPROPERTY()
	TMap<FName, FSkyguardMissionSaveRecord> MissionRecords;

	UPROPERTY(Transient)
	FSkyguardMissionDebrief LastDebrief;

	void BuildSuccessDebrief(
		const USkyguardMissionDefinition& CompletedMission,
		const FSkyguardMissionResult& Result,
		const FSkyguardMissionSaveRecord* PreviousRecord);

	void BuildFailureDebrief(
		const USkyguardMissionDefinition& FailedMission,
		const FSkyguardMissionResult& Result);

	void ClearActiveMissionRuntime();

	/** World time seconds when StartMission last succeeded; < 0 when inactive. */
	float MissionStartWorldTimeSeconds = -1.f;
};
