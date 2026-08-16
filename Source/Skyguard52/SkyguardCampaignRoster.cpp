#include "SkyguardCampaignRoster.h"

namespace
{
	FSkyguardCampaignMissionSpec Make(
		const TCHAR* Id,
		const TCHAR* Title,
		const TCHAR* Brief,
		const TCHAR* Success,
		const TCHAR* Failure,
		const ESkyguardMissionWeather Weather,
		const TCHAR* WeatherIdentity,
		const TCHAR* WeatherLabel,
		const float TimeOfDayHours,
		const float B0, const float B1, const float B2, const float B3,
		const float B4, const float B5, const float B6,
		const ESkyguardThreatKind Contact,
		const ESkyguardThreatKind Shore,
		const ESkyguardThreatKind Support,
		const ESkyguardThreatKind Extract,
		const ESkyguardClimaxKind Climax,
		const bool bNight,
		const bool bStormRockets)
	{
		FSkyguardCampaignMissionSpec Spec;
		Spec.MissionId = Id;
		Spec.Title = Title;
		Spec.Brief = Brief;
		Spec.Success = Success;
		Spec.Failure = Failure;
		Spec.Weather = Weather;
		Spec.WeatherIdentity = WeatherIdentity;
		Spec.WeatherLabel = WeatherLabel;
		Spec.TimeOfDayHours = TimeOfDayHours;
		Spec.BeatSeconds[0] = B0;
		Spec.BeatSeconds[1] = B1;
		Spec.BeatSeconds[2] = B2;
		Spec.BeatSeconds[3] = B3;
		Spec.BeatSeconds[4] = B4;
		Spec.BeatSeconds[5] = B5;
		Spec.BeatSeconds[6] = B6;
		Spec.ContactKind = Contact;
		Spec.ShoreKind = Shore;
		Spec.SupportKind = Support;
		Spec.ExtractKind = Extract;
		Spec.Climax = Climax;
		Spec.bNightIdentity = bNight;
		Spec.bStormRocketContract = bStormRockets;
		return Spec;
	}

	const FSkyguardCampaignMissionSpec GMissions[] = {
		Make(TEXT("M01_CoastalIntercept"), TEXT("First Contact"),
			TEXT("Clear day. First hop. Helmet cannon on the inbound swarm, rockets the trucks. Switch stations - this is not a drone intercept."),
			TEXT("Road is clear. Cannon and rockets both earned their keep."),
			TEXT("We stayed on one station. The column is gone."),
			ESkyguardMissionWeather::Clear,
			TEXT("ClearNoon"), TEXT("Clear day"), 12.f,
			20.f, 50.f, 80.f, 110.f, 140.f, 200.f, 240.f,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardClimaxKind::ArmorColumn, false, false),
		Make(TEXT("M02_HarborShield"), TEXT("Harbor Breaker"),
			TEXT("Harbor overcast. Fifteen-minute proof. 30 mm the boats, Hydra the shoreline armor, Hellfire the radar. Choice: kill the net or save the damaged ship. Strip the patrol ship by system, then helmet-sight extract."),
			TEXT("Harbor holds. Radar dead, ship stripped, cargo underway."),
			TEXT("Wrong station, wrong priority. The cargo is burning."),
			ESkyguardMissionWeather::Overcast,
			TEXT("HarborOvercast"), TEXT("Harbor overcast"), 10.5f,
			120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f,
			ESkyguardThreatKind::FastBoat,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::PatrolShip, false, false),
		Make(TEXT("M03_ConvoyEscort"), TEXT("Broken Highway"),
			TEXT("Dry morning. Ridge tanks will kill the convoy. Save Hellfires for the armor - 30 mm the technicals, Hydra the clusters."),
			TEXT("Convoy is through the pass. Missiles went to tanks."),
			TEXT("We spent Hellfires on the wrong hulls. The highway is a graveyard."),
			ESkyguardMissionWeather::Clear,
			TEXT("DryMorning"), TEXT("Dry morning"), 8.f,
			25.f, 70.f, 120.f, 170.f, 220.f, 320.f, 380.f,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::ArmorColumn, false, false),
		Make(TEXT("M04_NightBlackout"), TEXT("Night Eyes"),
			TEXT("Blackout night. Sensor thermal. Hellfire the radar vans, 30 mm rooftop heat - do not hose dark blocks in helmet-sight."),
			TEXT("The grid is dark and the radars are dead. Thermal found them."),
			TEXT("Thermal was off. We lit the wrong block."),
			ESkyguardMissionWeather::NightClear,
			TEXT("BlackoutNight"), TEXT("Blackout night"), 22.5f,
			25.f, 80.f, 140.f, 200.f, 260.f, 360.f, 420.f,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::RotorScout,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::MixedSwarm, true, false),
		Make(TEXT("M05_StormFront"), TEXT("River Hammer"),
			TEXT("Storm valley. Rockets for the barge clusters, 30 mm the fast boats. Hellfire the rival helo when the lock is clean."),
			TEXT("The river is ours. Rockets broke the clusters."),
			TEXT("We hoarded rockets. The barges broke the line."),
			ESkyguardMissionWeather::Storm,
			TEXT("SevereSquall"), TEXT("Storm valley"), 14.f,
			25.f, 80.f, 140.f, 190.f, 250.f, 350.f, 410.f,
			ESkyguardThreatKind::FastBoat,
			ESkyguardThreatKind::FastBoat,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::RivalHelo, false, true),
		Make(TEXT("M06_AirfieldDefense"), TEXT("Dust Offensive"),
			TEXT("Airfield haze. Hellfire ADA before it pins our armor. Hydra the dug-in line, 30 mm anything on the fence."),
			TEXT("ADA down. The field is taken."),
			TEXT("ADA lived. Our armor never made the fence."),
			ESkyguardMissionWeather::Overcast,
			TEXT("AirfieldHaze"), TEXT("Airfield haze"), 13.5f,
			25.f, 75.f, 130.f, 190.f, 250.f, 360.f, 420.f,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardClimaxKind::ArmorColumn, false, false),
		Make(TEXT("M07_SearchIntercept"), TEXT("Downed Bird"),
			TEXT("Island mist at dusk. Sensor thermal. Hold the wreck. Prioritize what can kill the rescue - cannon the swarm, rockets the armor, missile the rotor that tries to lift first."),
			TEXT("Crew is on the bird. Right threats, right stations."),
			TEXT("Wrong priority. The rescue never lifted."),
			ESkyguardMissionWeather::NightOvercast,
			TEXT("IslandMist"), TEXT("Island mist"), 17.f,
			20.f, 60.f, 110.f, 170.f, 230.f, 330.f, 390.f,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::RotorScout,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::MixedSwarm, true, false),
		Make(TEXT("M08_RescueCover"), TEXT("Iron Rain"),
			TEXT("Artillery rain at sunset. Hellfire the launchers first, Hydra the gun line - do not dump the cannon into the barrage."),
			TEXT("Launchers dead. The rain stopped."),
			TEXT("We hosed guns and left the SAMs. The city is under the barrage."),
			ESkyguardMissionWeather::Rain,
			TEXT("RescueSunset"), TEXT("Artillery rain"), 17.5f,
			20.f, 70.f, 130.f, 190.f, 250.f, 370.f, 430.f,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::MixedSwarm, false, false),
		Make(TEXT("M09_SaturationAttack"), TEXT("Hunter-Killer"),
			TEXT("City dusk. TEL hunt. Sensor-track the convoy. Hellfire the real launcher - 30 mm the decoys. Do not spend the last missile on a dummy."),
			TEXT("The TEL is scrap. The last Hellfire went to the real hull."),
			TEXT("Last Hellfire hit a decoy. The convoy slipped the net."),
			ESkyguardMissionWeather::Clear,
			TEXT("CityDusk"), TEXT("City dusk"), 19.f,
			25.f, 80.f, 140.f, 200.f, 270.f, 380.f, 440.f,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::ArmorColumn, false, false),
		Make(TEXT("M10_EvacuationFinale"), TEXT("Fortress Dawn"),
			TEXT("Fortress dawn. Hellfire the radar, Hydra the bunkers, strip the ship by system. Save a missile for the rival gunship on extract."),
			TEXT("Dawn, and the fortress is quiet. Every station earned its keep."),
			TEXT("Wrong order. We did not come home."),
			ESkyguardMissionWeather::Clear,
			TEXT("EvacuationDawn"), TEXT("Fortress dawn"), 5.5f,
			30.f, 90.f, 150.f, 220.f, 290.f, 400.f, 480.f,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::FastBoat,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::PatrolShip, false, false)
	};
}

int32 SkyguardCampaignRoster::NumMissions()
{
	return UE_ARRAY_COUNT(GMissions);
}

const FSkyguardCampaignMissionSpec& SkyguardCampaignRoster::Get(const int32 Index)
{
	const int32 Safe = FMath::Clamp(Index, 0, NumMissions() - 1);
	return GMissions[Safe];
}

int32 SkyguardCampaignRoster::IndexOf(const FName MissionId)
{
	for (int32 Index = 0; Index < NumMissions(); ++Index)
	{
		if (GMissions[Index].MissionId == MissionId)
		{
			return Index;
		}
	}
	return 0;
}

FName SkyguardCampaignRoster::IdAt(const int32 Index)
{
	return Get(Index).MissionId;
}

const TCHAR* SkyguardCampaignRoster::LoadoutLabel(const ESkyguardLoadout Loadout)
{
	switch (Loadout)
	{
	case ESkyguardLoadout::AntiArmor: return TEXT("Anti-Armor");
	case ESkyguardLoadout::RocketHeavy: return TEXT("Rocket Heavy");
	case ESkyguardLoadout::Intercept: return TEXT("Intercept");
	case ESkyguardLoadout::Balanced:
	default: return TEXT("Balanced");
	}
}

const TCHAR* SkyguardCampaignRoster::WeatherEnumLabel(
	const ESkyguardMissionWeather Weather)
{
	switch (Weather)
	{
	case ESkyguardMissionWeather::Clear: return TEXT("Clear");
	case ESkyguardMissionWeather::Overcast: return TEXT("Overcast");
	case ESkyguardMissionWeather::Rain: return TEXT("Rain");
	case ESkyguardMissionWeather::Storm: return TEXT("Storm");
	case ESkyguardMissionWeather::NightClear: return TEXT("Night clear");
	case ESkyguardMissionWeather::NightOvercast: return TEXT("Night overcast");
	default: return TEXT("Unknown");
	}
}
