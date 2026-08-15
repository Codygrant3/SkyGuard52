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
