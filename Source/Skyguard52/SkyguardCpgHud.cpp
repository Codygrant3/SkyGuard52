#include "SkyguardCpgHud.h"

const TCHAR* SkyguardCpgWeaponLabel(const ESkyguardGunshipWeapon Weapon)
{
	switch (Weapon)
	{
	case ESkyguardGunshipWeapon::Rockets:
		return TEXT("HYDRA");
	case ESkyguardGunshipWeapon::GuidedMissile:
		return TEXT("HLF");
	case ESkyguardGunshipWeapon::Cannon:
	default:
		return TEXT("M230");
	}
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
	default:
		return TEXT("FAST");
	}
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
