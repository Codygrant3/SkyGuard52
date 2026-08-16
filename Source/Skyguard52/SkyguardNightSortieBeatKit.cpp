#include "SkyguardNightSortieBeatKit.h"

#include "SkyguardCampaignRoster.h"

namespace
{
	FSkyguardNightSortieBeat MakeBeat(
		const ESkyguardNightSortieBeatKind Kind,
		const TCHAR* Call,
		const ESkyguardThreatKind Threat)
	{
		FSkyguardNightSortieBeat Beat;
		Beat.Kind = Kind;
		Beat.Call = Call;
		Beat.Threat = Threat;
		return Beat;
	}

	FSkyguardNightSortieBeatKit NightEyesKit()
	{
		FSkyguardNightSortieBeatKit Kit;
		Kit.MissionId = TEXT("M04_NightBlackout");
		Kit.WeatherIdentity = TEXT("BlackoutNight");
		Kit.bKeepThermal = true;
		Kit.Beats[0] = MakeBeat(
			ESkyguardNightSortieBeatKind::DarkIngress,
			TEXT("Blackout ingress. Sensor thermal."),
			ESkyguardThreatKind::FastAttacker);
		Kit.Beats[1] = MakeBeat(
			ESkyguardNightSortieBeatKind::ThermalHunt,
			TEXT("Hunt the heat. Do not hose dark blocks in helmet-sight."),
			ESkyguardThreatKind::HeavyAttacker);
		Kit.Beats[2] = MakeBeat(
			ESkyguardNightSortieBeatKind::RadarVanHunt,
			TEXT("Hellfire the radar vans."),
			ESkyguardThreatKind::HeavyAttacker);
		Kit.Beats[3] = MakeBeat(
			ESkyguardNightSortieBeatKind::RooftopHeat,
			TEXT("30 mm rooftop heat."),
			ESkyguardThreatKind::FastAttacker);
		Kit.Beats[4] = MakeBeat(
			ESkyguardNightSortieBeatKind::RadarNetCollapse,
			TEXT("The net is coordinating. Kill the radar."),
			ESkyguardThreatKind::RotorScout);
		Kit.Beats[5] = MakeBeat(
			ESkyguardNightSortieBeatKind::MixedSwarm,
			TEXT("Mixed swarm. Prioritize what can kill the airframe."),
			ESkyguardThreatKind::RotorScout);
		Kit.Beats[6] = MakeBeat(
			ESkyguardNightSortieBeatKind::Extraction,
			TEXT("Extract. Thermal stays on."),
			ESkyguardThreatKind::RotorScout);
		return Kit;
	}

	FSkyguardNightSortieBeatKit DownedBirdKit()
	{
		FSkyguardNightSortieBeatKit Kit;
		Kit.MissionId = TEXT("M07_SearchIntercept");
		Kit.WeatherIdentity = TEXT("IslandMist");
		Kit.bKeepThermal = true;
		Kit.Beats[0] = MakeBeat(
			ESkyguardNightSortieBeatKind::IslandIngress,
			TEXT("Island mist. Sensor thermal."),
			ESkyguardThreatKind::FastAttacker);
		Kit.Beats[1] = MakeBeat(
			ESkyguardNightSortieBeatKind::SearchIsland,
			TEXT("Search the island. Find the wreck."),
			ESkyguardThreatKind::FastAttacker);
		Kit.Beats[2] = MakeBeat(
			ESkyguardNightSortieBeatKind::HoldTheWreck,
			TEXT("Hold the wreck. The rescue is the objective."),
			ESkyguardThreatKind::GroundArmor);
		Kit.Beats[3] = MakeBeat(
			ESkyguardNightSortieBeatKind::RescuePressure,
			TEXT("Cannon the swarm that can kill the crew."),
			ESkyguardThreatKind::FastAttacker);
		Kit.Beats[4] = MakeBeat(
			ESkyguardNightSortieBeatKind::RescueLift,
			TEXT("Rockets the armor. Missile the rotor that tries to lift first."),
			ESkyguardThreatKind::RotorScout);
		Kit.Beats[5] = MakeBeat(
			ESkyguardNightSortieBeatKind::MixedSwarm,
			TEXT("Keep the wreck. Right threats, right stations."),
			ESkyguardThreatKind::RotorScout);
		Kit.Beats[6] = MakeBeat(
			ESkyguardNightSortieBeatKind::Extraction,
			TEXT("Crew is on the bird. Extract."),
			ESkyguardThreatKind::RotorScout);
		return Kit;
	}
}

const FSkyguardNightSortieBeatKit& SkyguardNightSortieBeatKit::NightEyes()
{
	static const FSkyguardNightSortieBeatKit Kit = NightEyesKit();
	return Kit;
}

const FSkyguardNightSortieBeatKit& SkyguardNightSortieBeatKit::DownedBird()
{
	static const FSkyguardNightSortieBeatKit Kit = DownedBirdKit();
	return Kit;
}

const FSkyguardNightSortieBeatKit& SkyguardNightSortieBeatKit::ForMission(
	const FName MissionId)
{
	if (MissionId == TEXT("M07_SearchIntercept"))
	{
		return DownedBird();
	}
	return NightEyes();
}

bool SkyguardNightSortieBeatKit::SequencesDiffer(
	const FSkyguardNightSortieBeatKit& Left,
	const FSkyguardNightSortieBeatKit& Right)
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

int32 SkyguardNightSortieBeatKit::BeatIndexForElapsed(
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

ESkyguardNightSortieBeatKind SkyguardNightSortieBeatKit::KindAt(
	const FSkyguardNightSortieBeatKit& Kit,
	const int32 Index)
{
	const int32 Safe = FMath::Clamp(Index, 0, 6);
	return Kit.Beats[Safe].Kind;
}
