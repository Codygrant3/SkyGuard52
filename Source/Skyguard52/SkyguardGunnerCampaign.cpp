#include "SkyguardGunner.h"

#include "SkyguardApacheAircraft.h"
#include "SkyguardCombatVFX.h"

void ASkyguardGunner::InputToggleThermal()
{
	ToggleThermal();
}

void ASkyguardGunner::InputPopFlares()
{
	PopFlares();
}

void ASkyguardGunner::ApplyLoadout(const ESkyguardLoadout Loadout)
{
	ActiveLoadout = Loadout;
	switch (Loadout)
	{
	case ESkyguardLoadout::AntiArmor:
		CannonMagazineSize = 24;
		CannonMagazine = 24;
		CannonReserve = 220;
		RocketMagazineSize = 8;
		RocketAmmo = 8;
		RocketReserve = 10;
		GuidedMagazineSize = 4;
		GuidedAmmo = 4;
		GuidedReserve = 10;
		FlareCount = 8;
		break;
	case ESkyguardLoadout::RocketHeavy:
		CannonMagazineSize = 24;
		CannonMagazine = 24;
		CannonReserve = 200;
		RocketMagazineSize = 20;
		RocketAmmo = 20;
		RocketReserve = 36;
		GuidedMagazineSize = 1;
		GuidedAmmo = 1;
		GuidedReserve = 3;
		FlareCount = 5;
		break;
	case ESkyguardLoadout::Intercept:
		CannonMagazineSize = 40;
		CannonMagazine = 40;
		CannonReserve = 400;
		RocketMagazineSize = 8;
		RocketAmmo = 8;
		RocketReserve = 12;
		GuidedMagazineSize = 1;
		GuidedAmmo = 1;
		GuidedReserve = 4;
		FlareCount = 10;
		break;
	case ESkyguardLoadout::Balanced:
	default:
		CannonMagazineSize = SkyguardApacheCpgFeel::CannonMagazineSize;
		CannonMagazine = SkyguardApacheCpgFeel::CannonMagazineSize;
		CannonReserve = SkyguardApacheCpgFeel::CannonReserve;
		RocketMagazineSize = SkyguardApacheCpgFeel::RocketMagazineSize;
		RocketAmmo = SkyguardApacheCpgFeel::RocketMagazineSize;
		RocketReserve = SkyguardApacheCpgFeel::RocketReserve;
		GuidedMagazineSize = SkyguardApacheCpgFeel::GuidedMagazineSize;
		GuidedAmmo = SkyguardApacheCpgFeel::GuidedMagazineSize;
		GuidedReserve = SkyguardApacheCpgFeel::GuidedReserve;
		FlareCount = 6;
		break;
	}

	if (ASkyguardApacheAircraft* Apache = FindAttachedApache())
	{
		const float Hull =
			Loadout == ESkyguardLoadout::Intercept ? 170.f :
			Loadout == ESkyguardLoadout::AntiArmor ? 120.f : 140.f;
		Apache->MaxIntegrity = Hull;
		Apache->CurrentIntegrity = Hull;
	}
}

void ASkyguardGunner::ToggleThermal()
{
	bThermalEnabled = !bThermalEnabled;
}

void ASkyguardGunner::PopFlares()
{
	if (FlareCount <= 0)
	{
		return;
	}
	--FlareCount;
	if (bMissileInbound)
	{
		bFlarePoppedThisInbound = true;
	}
	if (ASkyguardApacheAircraft* Apache = FindAttachedApache())
	{
		USkyguardCombatVFX::SpawnGunSmoke(
			GetWorld(),
			Apache->GetActorLocation() + Apache->GetActorRightVector() * 80.f,
			-Apache->GetActorForwardVector());
		USkyguardCombatVFX::SpawnGunSmoke(
			GetWorld(),
			Apache->GetActorLocation() - Apache->GetActorRightVector() * 80.f,
			-Apache->GetActorForwardVector());
	}
}

void ASkyguardGunner::NotifyMissileInbound()
{
	bMissileInbound = true;
	bFlarePoppedThisInbound = false;
}

bool ASkyguardGunner::TryDefeatInboundWithFlares()
{
	if (!bMissileInbound || !bFlarePoppedThisInbound)
	{
		return false;
	}
	bMissileInbound = false;
	bFlarePoppedThisInbound = false;
	return true;
}
