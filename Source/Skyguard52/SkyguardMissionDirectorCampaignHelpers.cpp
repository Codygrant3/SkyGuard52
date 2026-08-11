#include "SkyguardMissionDirectorCampaignHelpers.h"

#include "SkyguardCampaignSubsystem.h"
#include "SkyguardMissionTypes.h"
#include "SkyguardSortiePresentationComponent.h"

void SkyguardMissionDirectorCampaignHelpers::LoadCampaignProgressAfterConfigure(
	USkyguardCampaignSubsystem* Campaign,
	const FString& SlotName,
	const int32 UserIndex)
{
	if (!Campaign)
	{
		return;
	}
	// Missing/invalid slots are non-fatal for a fresh campaign start, but log so
	// corrupt or rejected saves are visible instead of silently ignored.
	if (!Campaign->LoadCampaignFromSlot(SlotName, UserIndex))
	{
		UE_LOG(
			LogTemp,
			Warning,
			TEXT("Skyguard campaign load skipped or failed for slot '%s' (user %d)."),
			*SlotName,
			UserIndex);
	}
}

bool SkyguardMissionDirectorCampaignHelpers::FillAndFinalize(
	USkyguardCampaignSubsystem* Campaign,
	const ASkyguardGunner* Gunner,
	const UObject* WorldContextObject,
	USkyguardSortiePresentationComponent* SortiePresentation,
	const FString& SlotName,
	const int32 UserIndex)
{
	if (!Campaign)
	{
		return false;
	}

	FSkyguardMissionResult Result;
	Campaign->FillResultCombatStats(Result, Gunner, WorldContextObject);
	const bool bCompleted =
		Campaign->FinalizeActiveMission(Result, SlotName, UserIndex);
	if (SortiePresentation)
	{
		SortiePresentation->RefreshDebrief();
	}
	return bCompleted;
}

bool SkyguardMissionDirectorCampaignHelpers::FillAndFail(
	USkyguardCampaignSubsystem* Campaign,
	const ASkyguardGunner* Gunner,
	const UObject* WorldContextObject,
	USkyguardSortiePresentationComponent* SortiePresentation,
	const FString& SlotName,
	const int32 UserIndex)
{
	if (!Campaign)
	{
		return false;
	}

	FSkyguardMissionResult Result;
	Campaign->FillResultCombatStats(Result, Gunner, WorldContextObject);
	const bool bFailed =
		Campaign->FailActiveMission(Result, SlotName, UserIndex);
	if (SortiePresentation)
	{
		SortiePresentation->RefreshDebrief();
	}
	return bFailed;
}
