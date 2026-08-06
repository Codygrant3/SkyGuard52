#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "SkyguardCampaignDefinition.generated.h"

class USkyguardMissionDefinition;

UCLASS(BlueprintType)
class SKYGUARD52_API USkyguardCampaignDefinition : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Campaign")
	FName CampaignId = TEXT("Skyguard52MainCampaign");

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Campaign")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Campaign")
	TArray<TObjectPtr<USkyguardMissionDefinition>> Missions;

	virtual FPrimaryAssetId GetPrimaryAssetId() const override;

	UFUNCTION(BlueprintCallable, Category = "Campaign")
	bool ValidateDefinition(TArray<FText>& OutErrors) const;

	UFUNCTION(BlueprintPure, Category = "Campaign")
	USkyguardMissionDefinition* FindMission(FName MissionId) const;
};
