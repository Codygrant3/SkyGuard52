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
		const float B0, const float B1, const float B2, const float B3,
		const float B4, const float B5, const float B6,
		const ESkyguardThreatKind Contact,
		const ESkyguardThreatKind Shore,
		const ESkyguardThreatKind Support,
		const ESkyguardThreatKind Extract,
		const ESkyguardClimaxKind Climax,
		const bool bNight)
	{
		FSkyguardCampaignMissionSpec Spec;
		Spec.MissionId = Id;
		Spec.Title = Title;
		Spec.Brief = Brief;
		Spec.Success = Success;
		Spec.Failure = Failure;
		Spec.Weather = Weather;
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
		return Spec;
	}

	const FSkyguardCampaignMissionSpec GMissions[] = {
		Make(TEXT("M01_CoastalIntercept"), TEXT("First Contact"),
			TEXT("Tutorial run. Cannon the drones, rockets the trucks. Keep the roadblock alive."),
			TEXT("Road is clear. Not bad for a first run."),
			TEXT("The column is gone."),
			ESkyguardMissionWeather::Clear,
			20.f, 50.f, 80.f, 110.f, 140.f, 200.f, 240.f,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardClimaxKind::ArmorColumn, false),
		Make(TEXT("M02_HarborShield"), TEXT("Harbor Breaker"),
			TEXT("Protect the cargo. Boats, shoreline armor, radar, then strip the patrol ship."),
			TEXT("Harbor holds. The ships are underway."),
			TEXT("The cargo is burning. Harbor is lost."),
			ESkyguardMissionWeather::Overcast,
			30.f, 90.f, 150.f, 210.f, 270.f, 390.f, 450.f,
			ESkyguardThreatKind::FastBoat,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::PatrolShip, false),
		Make(TEXT("M03_ConvoyEscort"), TEXT("Broken Highway"),
			TEXT("Ridge armor will kill the convoy. Missiles on the tanks."),
			TEXT("Convoy is through the pass."),
			TEXT("The highway is a graveyard."),
			ESkyguardMissionWeather::Clear,
			25.f, 70.f, 120.f, 170.f, 220.f, 320.f, 380.f,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::ArmorColumn, false),
		Make(TEXT("M04_NightBlackout"), TEXT("Night Eyes"),
			TEXT("Blackout city. Thermal. Radar vans and rooftop heat. Don't hose the dark blocks."),
			TEXT("The grid is dark and the radars are dead."),
			TEXT("We lit up the wrong block."),
			ESkyguardMissionWeather::NightClear,
			25.f, 80.f, 140.f, 200.f, 260.f, 360.f, 420.f,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::RotorScout,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::MixedSwarm, true),
		Make(TEXT("M05_StormFront"), TEXT("River Hammer"),
			TEXT("Storm valley. Barges and a rival helo. Rockets for clusters."),
			TEXT("The river is ours."),
			TEXT("The barges broke the line."),
			ESkyguardMissionWeather::Storm,
			25.f, 80.f, 140.f, 190.f, 250.f, 350.f, 410.f,
			ESkyguardThreatKind::FastBoat,
			ESkyguardThreatKind::FastBoat,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::RivalHelo, false),
		Make(TEXT("M06_AirfieldDefense"), TEXT("Dust Offensive"),
			TEXT("Sand. Support the armor. Kill ADA before it pins the advance."),
			TEXT("The field is taken."),
			TEXT("Our armor never made the fence."),
			ESkyguardMissionWeather::Overcast,
			25.f, 75.f, 130.f, 190.f, 250.f, 360.f, 420.f,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardClimaxKind::ArmorColumn, false),
		Make(TEXT("M07_SearchIntercept"), TEXT("Downed Bird"),
			TEXT("Hold the wreck. Everything converges. Keep the rescue alive."),
			TEXT("Crew is on the bird."),
			TEXT("The rescue never lifted."),
			ESkyguardMissionWeather::Overcast,
			20.f, 60.f, 110.f, 170.f, 230.f, 330.f, 390.f,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::RotorScout,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::MixedSwarm, false),
		Make(TEXT("M08_RescueCover"), TEXT("Iron Rain"),
			TEXT("Artillery and SAMs at once. Kill the shooters, then the launchers."),
			TEXT("The rain stopped."),
			TEXT("The city is under the barrage."),
			ESkyguardMissionWeather::Rain,
			20.f, 70.f, 130.f, 190.f, 250.f, 370.f, 430.f,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::MixedSwarm, false),
		Make(TEXT("M09_SaturationAttack"), TEXT("Hunter-Killer"),
			TEXT("Missile convoy with decoys. Do not spend the last Hellfire on a dummy."),
			TEXT("The TEL is scrap."),
			TEXT("The convoy slipped the net."),
			ESkyguardMissionWeather::Clear,
			25.f, 80.f, 140.f, 200.f, 270.f, 380.f, 440.f,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::FastAttacker,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::ArmorColumn, false),
		Make(TEXT("M10_EvacuationFinale"), TEXT("Fortress Dawn"),
			TEXT("Radar, ship, bunkers, then a rival gunship on extract."),
			TEXT("Dawn, and the fortress is quiet."),
			TEXT("We did not come home."),
			ESkyguardMissionWeather::Clear,
			30.f, 90.f, 150.f, 220.f, 290.f, 400.f, 480.f,
			ESkyguardThreatKind::HeavyAttacker,
			ESkyguardThreatKind::GroundArmor,
			ESkyguardThreatKind::FastBoat,
			ESkyguardThreatKind::RotorScout,
			ESkyguardClimaxKind::PatrolShip, false)
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
