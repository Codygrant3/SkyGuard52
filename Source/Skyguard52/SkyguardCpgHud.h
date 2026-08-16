#pragma once

#include "CoreMinimal.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardThreatTypes.h"

/** Readable CPG tapes. Names do not imply quality — review does. */
struct FSkyguardCpgHudSnapshot
{
	FString WeaponLine;
	FString RangeLine;
	FString ThreatLine;
	FString EufdLine;
	FString LockLine;
	FString SightLine;
	FString StationStatus;
	ESkyguardGuidedLockPhase LockPhase = ESkyguardGuidedLockPhase::Search;
	ESkyguardCpgSightMode SightMode = ESkyguardCpgSightMode::Helmet;
	float RangeMeters = -1.f;
	int32 ThreatCount = 0;
	float HeadingDegrees = 0.f;
	float LockProgress = 0.f;
	int32 FlareCount = 0;
	bool bMissileInbound = false;
};

struct FSkyguardCpgContactMark
{
	FVector WorldLocation = FVector::ZeroVector;
	FString Label;
	bool bLocked = false;
	bool bSeeking = false;
	float LockAlpha = 0.f;
};

const TCHAR* SkyguardCpgWeaponLabel(ESkyguardGunshipWeapon Weapon);
const TCHAR* SkyguardCpgThreatLabel(ESkyguardThreatKind Kind);
const TCHAR* SkyguardCpgShipSystemLabel(ESkyguardPatrolShipSystem System);
const TCHAR* SkyguardCpgLockPhaseLabel(ESkyguardGuidedLockPhase Phase);
const TCHAR* SkyguardCpgSightLabel(ESkyguardCpgSightMode Sight);
const TCHAR* SkyguardCpgInboundLabel();
FString SkyguardCpgFlareTape(int32 FlareCount);
bool SkyguardCpgHudHasLegacyLiveWording(const FString& Text);
