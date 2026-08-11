#include "SkyguardCampaignSaveGame.h"

bool USkyguardCampaignSaveGame::MigrateCampaignSave(USkyguardCampaignSaveGame& SaveGame)
{
	if (SaveGame.SaveVersion < MinSupportedSaveVersion ||
		SaveGame.SaveVersion > CurrentSaveVersion)
	{
		return false;
	}

	// Walk forward one version at a time so future bumps can append steps.
	if (SaveGame.SaveVersion == 1)
	{
		// v1 and v2 share FSkyguardMissionSaveRecord layout. Older binary slots
		// already receive UPROPERTY defaults for any fields added at v2; clamp
		// legacy values so ApplySaveGame sees a coherent current-version payload.
		for (TPair<FName, FSkyguardMissionSaveRecord>& Pair : SaveGame.MissionRecords)
		{
			FSkyguardMissionSaveRecord& Record = Pair.Value;
			Record.BestScore = FMath::Max(0, Record.BestScore);
			Record.BestMedalTier = FMath::Clamp(Record.BestMedalTier, 0, 3);
			Record.BestCompletionTimeSeconds =
				FMath::IsFinite(Record.BestCompletionTimeSeconds)
					? FMath::Max(0.f, Record.BestCompletionTimeSeconds)
					: 0.f;
			if (!Record.bCompleted)
			{
				Record.BestScore = 0;
				Record.BestMedalTier = 0;
				Record.BestCompletionTimeSeconds = 0.f;
			}
		}
		SaveGame.SaveVersion = 2;
	}

	return SaveGame.SaveVersion == CurrentSaveVersion;
}