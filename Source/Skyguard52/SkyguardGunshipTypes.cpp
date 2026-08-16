#include "SkyguardGunshipTypes.h"

FSkyguardLoadoutSpec SkyguardResolveLoadout(const ESkyguardLoadout Loadout)
{
	FSkyguardLoadoutSpec Spec;
	Spec.Loadout = Loadout;
	switch (Loadout)
	{
	case ESkyguardLoadout::AntiArmor:
		Spec.StartingStation = ESkyguardGunshipWeapon::GuidedMissile;
		Spec.CannonMagazineSize = 24;
		Spec.CannonReserve = 220;
		Spec.RocketMagazineSize = 8;
		Spec.RocketReserve = 10;
		Spec.GuidedMagazineSize = 4;
		Spec.GuidedReserve = 10;
		Spec.FlareCount = 8;
		Spec.HullIntegrity = 120.f;
		Spec.PlaystyleLine = TEXT("Hellfire station, extra guided missiles");
		break;
	case ESkyguardLoadout::RocketHeavy:
		Spec.StartingStation = ESkyguardGunshipWeapon::Rockets;
		Spec.CannonMagazineSize = 24;
		Spec.CannonReserve = 200;
		Spec.RocketMagazineSize = 20;
		Spec.RocketReserve = 36;
		Spec.GuidedMagazineSize = 1;
		Spec.GuidedReserve = 3;
		Spec.FlareCount = 5;
		Spec.HullIntegrity = 140.f;
		Spec.PlaystyleLine = TEXT("Hydra station, extra rockets");
		break;
	case ESkyguardLoadout::Intercept:
		Spec.StartingStation = ESkyguardGunshipWeapon::Cannon;
		Spec.CannonMagazineSize = 40;
		Spec.CannonReserve = 400;
		Spec.RocketMagazineSize = 8;
		Spec.RocketReserve = 12;
		Spec.GuidedMagazineSize = 1;
		Spec.GuidedReserve = 4;
		Spec.FlareCount = 10;
		Spec.HullIntegrity = 170.f;
		Spec.PlaystyleLine = TEXT("30 mm station, extra cannon and flares");
		break;
	case ESkyguardLoadout::Balanced:
	default:
		Spec.StartingStation = ESkyguardGunshipWeapon::Cannon;
		Spec.CannonMagazineSize = SkyguardApacheCpgFeel::CannonMagazineSize;
		Spec.CannonReserve = SkyguardApacheCpgFeel::CannonReserve;
		Spec.RocketMagazineSize = SkyguardApacheCpgFeel::RocketMagazineSize;
		Spec.RocketReserve = SkyguardApacheCpgFeel::RocketReserve;
		Spec.GuidedMagazineSize = SkyguardApacheCpgFeel::GuidedMagazineSize;
		Spec.GuidedReserve = SkyguardApacheCpgFeel::GuidedReserve;
		Spec.FlareCount = 6;
		Spec.HullIntegrity = 140.f;
		Spec.PlaystyleLine = TEXT("30 mm station, mixed cannon, rockets, missiles");
		break;
	}
	return Spec;
}

ESkyguardLoadout SkyguardLoadoutFromSlot(const int32 Slot)
{
	switch (Slot)
	{
	case 1:
		return ESkyguardLoadout::AntiArmor;
	case 2:
		return ESkyguardLoadout::RocketHeavy;
	case 3:
		return ESkyguardLoadout::Intercept;
	case 4:
	default:
		return ESkyguardLoadout::Balanced;
	}
}

int32 SkyguardLoadoutSlot(const ESkyguardLoadout Loadout)
{
	switch (Loadout)
	{
	case ESkyguardLoadout::AntiArmor:
		return 1;
	case ESkyguardLoadout::RocketHeavy:
		return 2;
	case ESkyguardLoadout::Intercept:
		return 3;
	case ESkyguardLoadout::Balanced:
	default:
		return 4;
	}
}

const TCHAR* SkyguardLoadoutDisplayName(const ESkyguardLoadout Loadout)
{
	switch (Loadout)
	{
	case ESkyguardLoadout::AntiArmor:
		return TEXT("Anti-Armor");
	case ESkyguardLoadout::RocketHeavy:
		return TEXT("Rocket Heavy");
	case ESkyguardLoadout::Intercept:
		return TEXT("Intercept");
	case ESkyguardLoadout::Balanced:
	default:
		return TEXT("Balanced");
	}
}
