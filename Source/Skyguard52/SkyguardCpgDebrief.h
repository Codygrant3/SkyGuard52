#pragma once

#include "CoreMinimal.h"
#include "SkyguardGunshipTypes.h"

class ASkyguardGunner;
class ASkyguardGunshipSortieDirector;
class ASkyguardPatrolShipBoss;

/** Presentation-safe CPG debrief. No Yak / Igla / rifle wording. */
struct FSkyguardCpgDebriefSnapshot
{
	bool bValid = false;
	bool bWon = false;
	FString MissionTitle;
	FString OutcomeNarrative;
	int32 Score = 0;
	int32 Medal = 0;
	int32 ShotsFired = 0;
	int32 Hits = 0;
	int32 CargoPercent = 100;
	bool bRadarDead = false;
	TArray<ESkyguardPatrolShipSystem> DestroyedSystems;
	ESkyguardLoadout SelectedLoadout = ESkyguardLoadout::Balanced;
	int32 CannonReady = 0;
	int32 RocketReady = 0;
	int32 GuidedReady = 0;
};

FSkyguardCpgDebriefSnapshot SkyguardCaptureCpgDebrief(
	const ASkyguardGunshipSortieDirector* Director,
	const ASkyguardGunner* Gunner,
	const ASkyguardPatrolShipBoss* Ship);

FString SkyguardBuildCpgDebriefCopy(const FSkyguardCpgDebriefSnapshot& Snap);

inline bool SkyguardCpgCopyHasBannedTerm(const FString& Text)
{
	const FString Lower = Text.ToLower();
	return Lower.Contains(TEXT("igla")) ||
		Lower.Contains(TEXT("yak")) ||
		Lower.Contains(TEXT("rifle"));
}
