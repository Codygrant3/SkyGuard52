#include "SkyguardStormRainBeatKit.h"

#include "SkyguardGunner.h"

namespace
{
	FSkyguardStormRainBeatKit MakeRiverHammer()
	{
		FSkyguardStormRainBeatKit Kit;
		Kit.MissionId = TEXT("M05_StormFront");
		Kit.Title = TEXT("River Hammer");
		Kit.WeatherIdentity = TEXT("SevereSquall");
		Kit.WeatherLabel = TEXT("Storm valley");
		Kit.Weather = ESkyguardMissionWeather::Storm;
		Kit.bHydraForClusters = true;

		const ESkyguardStormRainBeatKind Kinds[7] = {
			ESkyguardStormRainBeatKind::Approach,
			ESkyguardStormRainBeatKind::WaterwayBoats,
			ESkyguardStormRainBeatKind::BargeClusters,
			ESkyguardStormRainBeatKind::LightningWindow,
			ESkyguardStormRainBeatKind::ProtectWaterway,
			ESkyguardStormRainBeatKind::Tempest,
			ESkyguardStormRainBeatKind::Extract};
		const ESkyguardThreatKind Threats[7] = {
			ESkyguardThreatKind::FastBoat,
			ESkyguardThreatKind::FastBoat,
			ESkyguardThreatKind::FastBoat,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::FastBoat,
			ESkyguardThreatKind::RotorScout,
			ESkyguardThreatKind::RotorScout};
		const ESkyguardGunshipWeapon Stations[7] = {
			ESkyguardGunshipWeapon::Rockets,
			ESkyguardGunshipWeapon::Cannon,
			ESkyguardGunshipWeapon::Rockets,
			ESkyguardGunshipWeapon::Cannon,
			ESkyguardGunshipWeapon::Cannon,
			ESkyguardGunshipWeapon::GuidedMissile,
			ESkyguardGunshipWeapon::Cannon};
		const TCHAR* Calls[7] = {
			TEXT("Storm valley inbound. Helmet on the river."),
			TEXT("30 mm the fast boats."),
			TEXT("Hydra the barge clusters."),
			TEXT("Lightning. Hold aim through the squall."),
			TEXT("Keep the platform and the trawler."),
			TEXT("Hellfire the rival helo when the lock is clean."),
			TEXT("River is ours. Helmet-sight home.")};

		for (int32 Index = 0; Index < FSkyguardStormRainBeatKit::BeatCount; ++Index)
		{
			Kit.Kinds[Index] = Kinds[Index];
			Kit.Threats[Index] = Threats[Index];
			Kit.Stations[Index] = Stations[Index];
			Kit.Calls[Index] = Calls[Index];
		}
		return Kit;
	}

	FSkyguardStormRainBeatKit MakeIronRain()
	{
		FSkyguardStormRainBeatKit Kit;
		Kit.MissionId = TEXT("M08_RescueCover");
		Kit.Title = TEXT("Iron Rain");
		Kit.WeatherIdentity = TEXT("RescueSunset");
		Kit.WeatherLabel = TEXT("Artillery rain");
		Kit.Weather = ESkyguardMissionWeather::Rain;
		Kit.bHydraForClusters = true;

		const ESkyguardStormRainBeatKind Kinds[7] = {
			ESkyguardStormRainBeatKind::Approach,
			ESkyguardStormRainBeatKind::GunLine,
			ESkyguardStormRainBeatKind::KillBattery,
			ESkyguardStormRainBeatKind::BarrageCover,
			ESkyguardStormRainBeatKind::RescueCorridor,
			ESkyguardStormRainBeatKind::IronRain,
			ESkyguardStormRainBeatKind::Extract};
		const ESkyguardThreatKind Threats[7] = {
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::RotorScout,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::RotorScout};
		const ESkyguardGunshipWeapon Stations[7] = {
			ESkyguardGunshipWeapon::Rockets,
			ESkyguardGunshipWeapon::Rockets,
			ESkyguardGunshipWeapon::GuidedMissile,
			ESkyguardGunshipWeapon::Rockets,
			ESkyguardGunshipWeapon::Cannon,
			ESkyguardGunshipWeapon::GuidedMissile,
			ESkyguardGunshipWeapon::Cannon};
		const TCHAR* Calls[7] = {
			TEXT("Artillery rain at sunset. Hydra ready."),
			TEXT("Hydra the gun line."),
			TEXT("Hellfire the launchers first."),
			TEXT("Do not dump the cannon into the barrage."),
			TEXT("Keep fire off the rescue corridor."),
			TEXT("Kill the battery. Stop the rain."),
			TEXT("Launchers dead. The rain stopped.")};

		for (int32 Index = 0; Index < FSkyguardStormRainBeatKit::BeatCount; ++Index)
		{
			Kit.Kinds[Index] = Kinds[Index];
			Kit.Threats[Index] = Threats[Index];
			Kit.Stations[Index] = Stations[Index];
			Kit.Calls[Index] = Calls[Index];
		}
		return Kit;
	}
}

const FSkyguardStormRainBeatKit& SkyguardStormRainBeatKits::RiverHammer()
{
	static const FSkyguardStormRainBeatKit Kit = MakeRiverHammer();
	return Kit;
}

const FSkyguardStormRainBeatKit& SkyguardStormRainBeatKits::IronRain()
{
	static const FSkyguardStormRainBeatKit Kit = MakeIronRain();
	return Kit;
}

const FSkyguardStormRainBeatKit& SkyguardStormRainBeatKits::ForMission(
	const FName MissionId)
{
	if (MissionId == TEXT("M08_RescueCover"))
	{
		return IronRain();
	}
	return RiverHammer();
}

bool SkyguardStormRainBeatKits::KeepsHydraForClusters(
	const ESkyguardMissionWeather Weather)
{
	return Weather == ESkyguardMissionWeather::Storm ||
		Weather == ESkyguardMissionWeather::Rain;
}

bool SkyguardStormRainBeatKits::ApplyHydraForClusters(
	ASkyguardGunner* Gunner,
	const FSkyguardStormRainBeatKit& Kit)
{
	if (!Gunner || !Kit.bHydraForClusters ||
		!KeepsHydraForClusters(Kit.Weather))
	{
		return false;
	}
	Gunner->ApplyWeatherPlayContracts(false, true);
	return Gunner->GetSelectedGunshipWeapon() ==
			ESkyguardGunshipWeapon::Rockets &&
		Gunner->GetActiveLoadout() == ESkyguardLoadout::RocketHeavy;
}
