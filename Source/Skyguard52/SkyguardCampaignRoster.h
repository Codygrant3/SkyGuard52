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
	float BeatSeconds[7] = {30.f, 90.f, 150.f, 210.f, 270.f, 390.f, 450.f};
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
