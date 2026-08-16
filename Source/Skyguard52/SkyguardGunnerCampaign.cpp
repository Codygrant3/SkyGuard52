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
	const FSkyguardLoadoutSpec Spec = SkyguardResolveLoadout(Loadout);
	ActiveLoadout = Spec.Loadout;
	CannonMagazineSize = Spec.CannonMagazineSize;
	CannonMagazine = Spec.CannonMagazineSize;
	CannonReserve = Spec.CannonReserve;
	RocketMagazineSize = Spec.RocketMagazineSize;
	RocketAmmo = Spec.RocketMagazineSize;
	RocketReserve = Spec.RocketReserve;
	GuidedMagazineSize = Spec.GuidedMagazineSize;
	GuidedAmmo = Spec.GuidedMagazineSize;
	GuidedReserve = Spec.GuidedReserve;
	FlareCount = Spec.FlareCount;
	SelectGunshipWeapon(Spec.StartingStation);

	if (ASkyguardApacheAircraft* Apache = FindAttachedApache())
	{
		Apache->MaxIntegrity = Spec.HullIntegrity;
		Apache->CurrentIntegrity = Spec.HullIntegrity;
	}
}

void ASkyguardGunner::ToggleThermal()
{
	bThermalEnabled = !bThermalEnabled;
}

void ASkyguardGunner::SetThermalEnabled(const bool bEnabled)
{
	bThermalEnabled = bEnabled;
}

void ASkyguardGunner::ApplyWeatherPlayContracts(
	const bool bNightIdentity,
	const bool bStormRocketContract)
{
	if (bNightIdentity)
	{
		bThermalEnabled = true;
		bADS = true;
		bWasTargetingSensor = true;
	}
	else
	{
		bThermalEnabled = false;
	}

	if (bStormRocketContract)
	{
		ApplyLoadout(ESkyguardLoadout::RocketHeavy);
		SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
	}
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
