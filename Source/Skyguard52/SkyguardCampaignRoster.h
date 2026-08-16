#pragma once

#include "CoreMinimal.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardMissionTypes.h"
#include "SkyguardThreatTypes.h"

struct FSkyguardCampaignMissionSpec
{
	FName MissionId;
	const TCHAR* Title = TEXT("");
	const TCHAR* Brief = TEXT("");
	const TCHAR* Success = TEXT("");
	const TCHAR* Failure = TEXT("");
	ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Clear;
	/** Stable Play identity. Distinct across the ten-mission roster. */
	FName WeatherIdentity;
	/** Readable day / dusk / night / storm line for brief and on-screen mood. */
	const TCHAR* WeatherLabel = TEXT("");
	float TimeOfDayHours = 12.f;
	// Harbor Breaker proof clock: 2/4/6/8/10/13/15 min = 120/240/360/480/600/780/900 s.
	float BeatSeconds[7] = {120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f};
	ESkyguardThreatKind ContactKind = ESkyguardThreatKind::FastAttacker;
	ESkyguardThreatKind ShoreKind = ESkyguardThreatKind::GroundArmor;
	ESkyguardThreatKind SupportKind = ESkyguardThreatKind::HeavyAttacker;
	ESkyguardThreatKind ExtractKind = ESkyguardThreatKind::RotorScout;
	ESkyguardClimaxKind Climax = ESkyguardClimaxKind::PatrolShip;
	/** Night missions force sensor thermal — sight identity, not a reskin. */
	bool bNightIdentity = false;
	/** Storm missions start on Hydra for barge/armor clusters. No new station. */
	bool bStormRocketContract = false;
};

namespace SkyguardCampaignRoster
{
	int32 NumMissions();
	const FSkyguardCampaignMissionSpec& Get(int32 Index);
	int32 IndexOf(FName MissionId);
	FName IdAt(int32 Index);
	const TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);
	const TCHAR* WeatherEnumLabel(ESkyguardMissionWeather Weather);
}
