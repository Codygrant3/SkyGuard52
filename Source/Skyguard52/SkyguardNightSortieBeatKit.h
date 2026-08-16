#pragma once

#include "CoreMinimal.h"
#include "SkyguardThreatTypes.h"

/**
 * Phase 3 night beat kinds. M04 is a radar-net hunt. M07 is hold-the-wreck
 * / search island. These are sortie identities, not weather labels.
 */
enum class ESkyguardNightSortieBeatKind : uint8
{
	DarkIngress,
	ThermalHunt,
	RadarVanHunt,
	RooftopHeat,
	RadarNetCollapse,
	IslandIngress,
	SearchIsland,
	HoldTheWreck,
	RescuePressure,
	RescueLift,
	MixedSwarm,
	Extraction
};

struct FSkyguardNightSortieBeat
{
	ESkyguardNightSortieBeatKind Kind = ESkyguardNightSortieBeatKind::DarkIngress;
	const TCHAR* Call = TEXT("");
	ESkyguardThreatKind Threat = ESkyguardThreatKind::FastAttacker;
};

struct FSkyguardNightSortieBeatKit
{
	FName MissionId;
	FName WeatherIdentity;
	bool bKeepThermal = true;
	FSkyguardNightSortieBeat Beats[7];
};

namespace SkyguardNightSortieBeatKit
{
	const FSkyguardNightSortieBeatKit& NightEyes();
	const FSkyguardNightSortieBeatKit& DownedBird();
	const FSkyguardNightSortieBeatKit& ForMission(FName MissionId);
	bool SequencesDiffer(
		const FSkyguardNightSortieBeatKit& Left,
		const FSkyguardNightSortieBeatKit& Right);
	int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);
	ESkyguardNightSortieBeatKind KindAt(
		const FSkyguardNightSortieBeatKit& Kit,
		int32 Index);
}
