#include "SkyguardCpgHud.h"

#include "SkyguardGuidedLockRules.h"

const TCHAR* SkyguardCpgWeaponLabel(const ESkyguardGunshipWeapon Weapon)
{
	switch (Weapon)
	{
	case ESkyguardGunshipWeapon::Cannon:
		return TEXT("30MM");
	case ESkyguardGunshipWeapon::Rockets:
		return TEXT("RKT");
	case ESkyguardGunshipWeapon::GuidedMissile:
		return TEXT("MSL");
	}
	checkNoEntry();
	return TEXT("30MM");
}

const TCHAR* SkyguardCpgThreatLabel(const ESkyguardThreatKind Kind)
{
	switch (Kind)
	{
	case ESkyguardThreatKind::HeavyAttacker:
		return TEXT("HVY");
	case ESkyguardThreatKind::RotorScout:
		return TEXT("RTR");
	case ESkyguardThreatKind::GroundArmor:
		return TEXT("ARM");
	case ESkyguardThreatKind::FastBoat:
		return TEXT("BOAT");
	case ESkyguardThreatKind::FastAttacker:
		return TEXT("FAST");
	}
	checkNoEntry();
	return TEXT("FAST");
}

const TCHAR* SkyguardCpgLockPhaseLabel(const ESkyguardGuidedLockPhase Phase)
{
	return FSkyguardGuidedLockRules::PhaseLabel(Phase);
}

const TCHAR* SkyguardCpgSightLabel(const ESkyguardCpgSightMode Sight)
{
	return FSkyguardGuidedLockRules::SightLabel(Sight);
}

bool SkyguardCpgHudHasLegacyLiveWording(const FString& Text)
{
	return Text.Contains(TEXT("Igla"), ESearchCase::IgnoreCase) ||
		Text.Contains(TEXT("Yak"), ESearchCase::IgnoreCase) ||
		Text.Contains(TEXT("rifle"), ESearchCase::IgnoreCase);
}

const TCHAR* SkyguardCpgShipSystemLabel(const ESkyguardPatrolShipSystem System)
{
	switch (System)
	{
	case ESkyguardPatrolShipSystem::Radar:
		return TEXT("RADAR");
	case ESkyguardPatrolShipSystem::Cannon:
		return TEXT("GUN");
	case ESkyguardPatrolShipSystem::Launcher:
		return TEXT("LNCH");
	case ESkyguardPatrolShipSystem::Engines:
		return TEXT("ENG");
	case ESkyguardPatrolShipSystem::DroneDeck:
		return TEXT("DECK");
	default:
		return TEXT("SHIP");
	}
}
