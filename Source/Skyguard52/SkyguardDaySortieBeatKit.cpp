#include "SkyguardDaySortieBeatKit.h"

#include "SkyguardCampaignRoster.h"

namespace
{
	FSkyguardDaySortieBeat MakeBeat(
		const ESkyguardDaySortieBeatKind Kind,
		const TCHAR* Call,
		const ESkyguardThreatKind Threat)
	{
		FSkyguardDaySortieBeat Beat;
		Beat.Kind = Kind;
		Beat.Call = Call;
		Beat.Threat = Threat;
		return Beat;
	}

	FSkyguardDaySortieBeatKit BrokenHighwayKit()
	{
		FSkyguardDaySortieBeatKit Kit;
		Kit.MissionId = TEXT("M03_ConvoyEscort");
		Kit.WeatherIdentity = TEXT("DryMorning");
		Kit.Beats[0] = MakeBeat(
			ESkyguardDaySortieBeatKind::RidgeIngress,
			TEXT("Dry morning. Ridge highway. Helmet the road."),
			ESkyguardThreatKind::GroundArmor);
		Kit.Beats[1] = MakeBeat(
			ESkyguardDaySortieBeatKind::TechnicalScreen,
			TEXT("30 mm the technicals. Hold Hellfires for the tanks."),
			ESkyguardThreatKind::FastAttacker);
		Kit.Beats[2] = MakeBeat(
			ESkyguardDaySortieBeatKind::ClusterRidge,
			TEXT("Hydra the clusters on the ridge."),
			ESkyguardThreatKind::GroundArmor);
		Kit.Beats[3] = MakeBeat(
			ESkyguardDaySortieBeatKind::TankAmbush,
			TEXT("Ridge tanks. Save Hellfires for the armor."),
			ESkyguardThreatKind::GroundArmor);
		Kit.Beats[4] = MakeBeat(
			ESkyguardDaySortieBeatKind::ConvoyPressure,
			TEXT("The convoy is under fire. Kill what can stop the column."),
			ESkyguardThreatKind::HeavyAttacker);
		Kit.Beats[5] = MakeBeat(
			ESkyguardDaySortieBeatKind::ArmorColumn,
			TEXT("Armor column. Missile the tanks that can close the pass."),
			ESkyguardThreatKind::GroundArmor);
		Kit.Beats[6] = MakeBeat(
			ESkyguardDaySortieBeatKind::Extraction,
			TEXT("Convoy is through the pass. Extract."),
			ESkyguardThreatKind::RotorScout);
		return Kit;
	}

	FSkyguardDaySortieBeatKit DustOffensiveKit()
	{
		FSkyguardDaySortieBeatKit Kit;
		Kit.MissionId = TEXT("M06_AirfieldDefense");
		Kit.WeatherIdentity = TEXT("AirfieldHaze");
		Kit.Beats[0] = MakeBeat(
			ESkyguardDaySortieBeatKind::HazeIngress,
			TEXT("Airfield haze. Ingress the fence."),
			ESkyguardThreatKind::FastAttacker);
		Kit.Beats[1] = MakeBeat(
			ESkyguardDaySortieBeatKind::FenceSweep,
			TEXT("30 mm anything on the fence."),
			ESkyguardThreatKind::FastAttacker);
		Kit.Beats[2] = MakeBeat(
			ESkyguardDaySortieBeatKind::DugInLine,
			TEXT("Hydra the dug-in line."),
			ESkyguardThreatKind::GroundArmor);
		Kit.Beats[3] = MakeBeat(
			ESkyguardDaySortieBeatKind::AdaAcquire,
			TEXT("ADA is lighting up. Sensor the emitters."),
			ESkyguardThreatKind::HeavyAttacker);
		Kit.Beats[4] = MakeBeat(
			ESkyguardDaySortieBeatKind::AdaSuppress,
			TEXT("Hellfire ADA before it pins our armor."),
			ESkyguardThreatKind::HeavyAttacker);
		Kit.Beats[5] = MakeBeat(
			ESkyguardDaySortieBeatKind::ArmorPush,
			TEXT("Armor push. Keep the field open."),
			ESkyguardThreatKind::GroundArmor);
		Kit.Beats[6] = MakeBeat(
			ESkyguardDaySortieBeatKind::Extraction,
			TEXT("ADA down. The field is taken. Extract."),
			ESkyguardThreatKind::FastAttacker);
		return Kit;
	}

	FSkyguardDaySortieBeatKit HunterKillerKit()
	{
		FSkyguardDaySortieBeatKit Kit;
		Kit.MissionId = TEXT("M09_SaturationAttack");
		Kit.WeatherIdentity = TEXT("CityDusk");
		Kit.Beats[0] = MakeBeat(
			ESkyguardDaySortieBeatKind::DuskIngress,
			TEXT("City dusk. Metro TEL hunt."),
			ESkyguardThreatKind::GroundArmor);
		Kit.Beats[1] = MakeBeat(
			ESkyguardDaySortieBeatKind::SensorTrack,
			TEXT("Sensor-track the convoy. Do not hose the first hull."),
			ESkyguardThreatKind::GroundArmor);
		Kit.Beats[2] = MakeBeat(
			ESkyguardDaySortieBeatKind::DecoyScreen,
			TEXT("30 mm the decoys. Hold the last Hellfire."),
			ESkyguardThreatKind::FastAttacker);
		Kit.Beats[3] = MakeBeat(
			ESkyguardDaySortieBeatKind::TelAcquire,
			TEXT("Real launcher in the net. Confirm before you spend."),
			ESkyguardThreatKind::GroundArmor);
		Kit.Beats[4] = MakeBeat(
			ESkyguardDaySortieBeatKind::TelStrike,
			TEXT("Hellfire the real launcher. Not the dummy."),
			ESkyguardThreatKind::GroundArmor);
		Kit.Beats[5] = MakeBeat(
			ESkyguardDaySortieBeatKind::ConvoyBreak,
			TEXT("The convoy is breaking. Keep the TEL in the sensor."),
			ESkyguardThreatKind::FastAttacker);
		Kit.Beats[6] = MakeBeat(
			ESkyguardDaySortieBeatKind::Extraction,
			TEXT("The TEL is scrap. Extract."),
			ESkyguardThreatKind::RotorScout);
		return Kit;
	}
}

const FSkyguardDaySortieBeatKit& SkyguardDaySortieBeatKit::BrokenHighway()
{
	static const FSkyguardDaySortieBeatKit Kit = BrokenHighwayKit();
	return Kit;
}

const FSkyguardDaySortieBeatKit& SkyguardDaySortieBeatKit::DustOffensive()
{
	static const FSkyguardDaySortieBeatKit Kit = DustOffensiveKit();
	return Kit;
}

const FSkyguardDaySortieBeatKit& SkyguardDaySortieBeatKit::HunterKiller()
{
	static const FSkyguardDaySortieBeatKit Kit = HunterKillerKit();
	return Kit;
}

const FSkyguardDaySortieBeatKit& SkyguardDaySortieBeatKit::ForMission(
	const FName MissionId)
{
	if (MissionId == TEXT("M06_AirfieldDefense"))
	{
		return DustOffensive();
	}
	if (MissionId == TEXT("M09_SaturationAttack"))
	{
		return HunterKiller();
	}
	return BrokenHighway();
}

bool SkyguardDaySortieBeatKit::SequencesDiffer(
	const FSkyguardDaySortieBeatKit& Left,
	const FSkyguardDaySortieBeatKit& Right)
{
	for (int32 Index = 0; Index < 7; ++Index)
	{
		if (Left.Beats[Index].Kind != Right.Beats[Index].Kind)
		{
			return true;
		}
	}
	return false;
}

int32 SkyguardDaySortieBeatKit::BeatIndexForElapsed(
	const FName MissionId,
	const float ElapsedSeconds)
{
	const FSkyguardCampaignMissionSpec& Spec =
		SkyguardCampaignRoster::Get(SkyguardCampaignRoster::IndexOf(MissionId));
	int32 Index = 0;
	for (int32 Beat = 0; Beat < 6; ++Beat)
	{
		if (ElapsedSeconds >= Spec.BeatSeconds[Beat])
		{
			Index = Beat + 1;
		}
	}
	return Index;
}

ESkyguardDaySortieBeatKind SkyguardDaySortieBeatKit::KindAt(
	const FSkyguardDaySortieBeatKit& Kit,
	const int32 Index)
{
	const int32 Safe = FMath::Clamp(Index, 0, 6);
	return Kit.Beats[Safe].Kind;
}
