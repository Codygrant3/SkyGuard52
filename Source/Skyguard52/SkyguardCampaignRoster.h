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
	// Harbor Breaker proof clock: 2/4/6/8/10/13/15 min = 120/240/360/480/600/780/900 s.
	float BeatSeconds[7] = {120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f};
	ESkyguardThreatKind ContactKind = ESkyguardThreatKind::FastAttacker;
	ESkyguardThreatKind ShoreKind = ESkyguardThreatKind::GroundArmor;
	ESkyguardThreatKind SupportKind = ESkyguardThreatKind::HeavyAttacker;
	ESkyguardThreatKind ExtractKind = ESkyguardThreatKind::RotorScout;
	ESkyguardClimaxKind Climax = ESkyguardClimaxKind::PatrolShip;
	bool bNightIdentity = false;
};

namespace SkyguardCampaignRoster
{
	int32 NumMissions();
	const FSkyguardCampaignMissionSpec& Get(int32 Index);
	int32 IndexOf(FName MissionId);
	FName IdAt(int32 Index);
	const TCHAR* LoadoutLabel(ESkyguardLoadout Loadout);
}
