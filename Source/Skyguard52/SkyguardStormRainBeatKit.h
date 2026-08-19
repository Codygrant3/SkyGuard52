#pragma once

#include "CoreMinimal.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardMissionTypes.h"
#include "SkyguardThreatTypes.h"

class ASkyguardGunner;

/**
 * Phase 3 storm/rain beat kinds. These are sortie jobs, not Harbor Breaker
 * Approach/Contact/Shore labels and not a second weather system.
 */
enum class ESkyguardStormRainBeatKind : uint8
{
	Approach,
	WaterwayBoats,
	BargeClusters,
	LightningWindow,
	ProtectWaterway,
	Tempest,
	GunLine,
	KillBattery,
	BarrageCover,
	RescueCorridor,
	IronRain,
	Extract
};

struct FSkyguardStormRainBeatKit
{
	static constexpr int32 BeatCount = 7;

	FName MissionId;
	const TCHAR* Title = TEXT("");
	FName WeatherIdentity;
	const TCHAR* WeatherLabel = TEXT("");
	ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Storm;
	bool bHydraForClusters = true;
	ESkyguardStormRainBeatKind Kinds[BeatCount] = {};
	ESkyguardThreatKind Threats[BeatCount] = {};
	ESkyguardGunshipWeapon Stations[BeatCount] = {};
	const TCHAR* Calls[BeatCount] = {};
};

namespace SkyguardStormRainBeatKits
{
	const FSkyguardStormRainBeatKit& RiverHammer();
	const FSkyguardStormRainBeatKit& IronRain();
	const FSkyguardStormRainBeatKit& ForMission(FName MissionId);

	bool KeepsHydraForClusters(ESkyguardMissionWeather Weather);
	bool ApplyHydraForClusters(
		ASkyguardGunner* Gunner,
		const FSkyguardStormRainBeatKit& Kit);
	int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);
}
