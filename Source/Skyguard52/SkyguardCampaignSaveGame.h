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
	/** Oldest on-disk save layout this build can migrate forward. */
	static constexpr int32 MinSupportedSaveVersion = 1;

	static constexpr int32 CurrentSaveVersion = 2;

	/**
	 * Migrates SaveGame in-place from any supported older version to CurrentSaveVersion.
	 * Returns false for unknown (too old) or future versions.
	 * v1 -> v2: same mission-record layout; UE already defaulted any newly added
	 * UPROPERTY fields on load. This step validates/clamps legacy values and bumps
	 * SaveVersion so subsequent slot writes persist the current version.
	 */
	static bool MigrateCampaignSave(USkyguardCampaignSaveGame& SaveGame);

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 SaveVersion = CurrentSaveVersion;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FName CampaignId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	TMap<FName, FSkyguardMissionSaveRecord> MissionRecords;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FDateTime SavedAtUtc;
};
