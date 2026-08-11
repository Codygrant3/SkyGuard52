#pragma once

#include "CoreMinimal.h"

class ASkyguardGunner;
class USkyguardCampaignSubsystem;
class USkyguardSortiePresentationComponent;

/**
 * Shared campaign load/finalize/fail helpers for mission integration directors.
 * Used by M01-M10 to keep sortie combat-stat and save wiring consistent.
 */
namespace SkyguardMissionDirectorCampaignHelpers
{
	/** Call after ConfigureCampaign succeeds to restore prior completions. */
	void LoadCampaignProgressAfterConfigure(
		USkyguardCampaignSubsystem* Campaign,
		const FString& SlotName,
		int32 UserIndex);

	/**
	 * FillResultCombatStats + FinalizeActiveMission + optional RefreshDebrief.
	 * Returns FinalizeActiveMission result (false if Campaign is null).
	 */
	bool FillAndFinalize(
		USkyguardCampaignSubsystem* Campaign,
		const ASkyguardGunner* Gunner,
		const UObject* WorldContextObject,
		USkyguardSortiePresentationComponent* SortiePresentation,
		const FString& SlotName,
		int32 UserIndex);

	/**
	 * FillResultCombatStats + FailActiveMission + optional RefreshDebrief.
	 * Returns FailActiveMission result (false if Campaign is null).
	 */
	bool FillAndFail(
		USkyguardCampaignSubsystem* Campaign,
		const ASkyguardGunner* Gunner,
		const UObject* WorldContextObject,
		USkyguardSortiePresentationComponent* SortiePresentation,
		const FString& SlotName,
		int32 UserIndex);
}
