#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "SkyguardMissionTypes.h"
#include "SkyguardMissionDefinition.generated.h"

UCLASS(BlueprintType)
class SKYGUARD52_API USkyguardMissionDefinition : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Identity")
	FName MissionId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Identity")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Identity", meta = (ClampMin = "1"))
	int32 CampaignOrder = 1;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "World")
	TSoftObjectPtr<UWorld> MissionMap;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Flight")
	FSkyguardRouteDefinition Route;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Objectives")
	TArray<FSkyguardObjectiveDefinition> Objectives;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combat")
	TArray<FSkyguardEnemyWaveDefinition> Waves;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combat")
	FSkyguardBossDefinition Boss;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Environment")
	FSkyguardWeatherProfile Weather;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Presentation")
	FSkyguardMissionPresentation Presentation;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Scoring")
	FSkyguardMissionScoreRules ScoreRules;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Progression")
	TArray<FName> PrerequisiteMissionIds;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Progression", meta = (ClampMin = "0"))
	int32 RequiredCampaignMedals = 0;

	virtual FPrimaryAssetId GetPrimaryAssetId() const override;

	UFUNCTION(BlueprintCallable, Category = "Mission")
	bool ValidateDefinition(TArray<FText>& OutErrors) const;

	const FSkyguardObjectiveDefinition* FindObjective(FName ObjectiveId) const;
};
