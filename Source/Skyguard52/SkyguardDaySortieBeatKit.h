#pragma once

#include "CoreMinimal.h"
#include "SkyguardThreatTypes.h"

/**
 * Phase 3 day / dusk beat kinds. M03 is ridge highway escort. M06 is
 * airfield ADA suppress. M09 is metro TEL hunt. These are sortie
 * identities, not weather labels.
 */
enum class ESkyguardDaySortieBeatKind : uint8
{
	RidgeIngress,
	TechnicalScreen,
	ClusterRidge,
	TankAmbush,
	ConvoyPressure,
	ArmorColumn,
	HazeIngress,
	FenceSweep,
	DugInLine,
	AdaAcquire,
	AdaSuppress,
	ArmorPush,
	DuskIngress,
	SensorTrack,
	DecoyScreen,
	TelAcquire,
	TelStrike,
	ConvoyBreak,
	Extraction
};

struct FSkyguardDaySortieBeat
{
	ESkyguardDaySortieBeatKind Kind = ESkyguardDaySortieBeatKind::RidgeIngress;
	const TCHAR* Call = TEXT("");
	ESkyguardThreatKind Threat = ESkyguardThreatKind::GroundArmor;
};

struct FSkyguardDaySortieBeatKit
{
	FName MissionId;
	FName WeatherIdentity;
	FSkyguardDaySortieBeat Beats[7];
};

namespace SkyguardDaySortieBeatKit
{
	const FSkyguardDaySortieBeatKit& BrokenHighway();
	const FSkyguardDaySortieBeatKit& DustOffensive();
	const FSkyguardDaySortieBeatKit& HunterKiller();
	const FSkyguardDaySortieBeatKit& ForMission(FName MissionId);
	bool SequencesDiffer(
		const FSkyguardDaySortieBeatKit& Left,
		const FSkyguardDaySortieBeatKit& Right);
	int32 BeatIndexForElapsed(FName MissionId, float ElapsedSeconds);
	ESkyguardDaySortieBeatKind KindAt(
		const FSkyguardDaySortieBeatKit& Kit,
		int32 Index);
}
