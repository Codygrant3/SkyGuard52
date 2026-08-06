#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "SkyguardCampaignSaveGame.generated.h"

USTRUCT(BlueprintType)
struct FSkyguardMissionSaveRecord
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	bool bCompleted = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 BestScore = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, meta = (ClampMin = "0", ClampMax = "3"))
	int32 BestMedalTier = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float BestCompletionTimeSeconds = 0.f;
};

UCLASS(BlueprintType)
class SKYGUARD52_API USkyguardCampaignSaveGame : public USaveGame
{
	GENERATED_BODY()

public:
	static constexpr int32 CurrentSaveVersion = 2;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 SaveVersion = CurrentSaveVersion;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FName CampaignId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TMap<FName, FSkyguardMissionSaveRecord> MissionRecords;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FDateTime SavedAtUtc;
};
