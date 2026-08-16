#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardStormRainBeatKit.h"

#include "SkyguardCampaignRoster.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardMission05IntegrationDirector.h"
#include "SkyguardMission08IntegrationDirector.h"
#include "SkyguardMissionTypes.h"
#include "Misc/AutomationTest.h"

namespace SkyguardStormRainBeatKitTests
{
	bool CopyContainsBannedTerm(const TCHAR* Text)
	{
		const FString Lower = FString(Text).ToLower();
		return Lower.Contains(TEXT("igla")) ||
			Lower.Contains(TEXT("yak")) ||
			Lower.Contains(TEXT("rifle"));
	}

	bool KitCopyIsClean(const FSkyguardStormRainBeatKit& Kit)
	{
		if (CopyContainsBannedTerm(Kit.Title) ||
			CopyContainsBannedTerm(Kit.WeatherLabel))
		{
			return false;
		}
		for (int32 Index = 0; Index < FSkyguardStormRainBeatKit::BeatCount; ++Index)
		{
			if (CopyContainsBannedTerm(Kit.Calls[Index]))
			{
				return false;
			}
		}
		return true;
	}

	bool SequencesEqual(
		const FSkyguardStormRainBeatKit& Left,
		const FSkyguardStormRainBeatKit& Right)
	{
		for (int32 Index = 0; Index < FSkyguardStormRainBeatKit::BeatCount; ++Index)
		{
			if (Left.Kinds[Index] != Right.Kinds[Index])
			{
				return false;
			}
		}
		return true;
	}

	bool StartsHydraOrRocketHeavy(const ASkyguardGunner* Gunner)
	{
		return Gunner &&
			(Gunner->GetSelectedGunshipWeapon() ==
				ESkyguardGunshipWeapon::Rockets ||
				Gunner->GetActiveLoadout() == ESkyguardLoadout::RocketHeavy);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardStormRainBeatSequencesDifferTest,
	"Skyguard52.Campaign.StormRain.M05SequenceDiffersFromM08",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardStormRainBeatSequencesDifferTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardStormRainBeatKitTests;
	const FSkyguardStormRainBeatKit& River =
		SkyguardStormRainBeatKits::RiverHammer();
	const FSkyguardStormRainBeatKit& Rain =
		SkyguardStormRainBeatKits::IronRain();

	TestEqual(TEXT("M05 id"), River.MissionId, FName(TEXT("M05_StormFront")));
	TestEqual(TEXT("M08 id"), Rain.MissionId, FName(TEXT("M08_RescueCover")));
	TestEqual(TEXT("M05 title"), FString(River.Title), FString(TEXT("River Hammer")));
	TestEqual(TEXT("M08 title"), FString(Rain.Title), FString(TEXT("Iron Rain")));
	TestEqual(
		TEXT("M05 weather identity"),
		River.WeatherIdentity,
		FName(TEXT("SevereSquall")));
	TestEqual(
		TEXT("M08 weather identity"),
		Rain.WeatherIdentity,
		FName(TEXT("RescueSunset")));
	TestEqual(TEXT("M05 is Storm"), River.Weather, ESkyguardMissionWeather::Storm);
	TestEqual(TEXT("M08 is Rain"), Rain.Weather, ESkyguardMissionWeather::Rain);

	TestEqual(
		TEXT("M05 beat 1 is waterway boats"),
		River.Kinds[1],
		ESkyguardStormRainBeatKind::WaterwayBoats);
	TestEqual(
		TEXT("M05 climax is Tempest"),
		River.Kinds[5],
		ESkyguardStormRainBeatKind::Tempest);
	TestEqual(
		TEXT("M08 beat 2 is kill the battery"),
		Rain.Kinds[2],
		ESkyguardStormRainBeatKind::KillBattery);
	TestEqual(
		TEXT("M08 climax is Iron Rain"),
		Rain.Kinds[5],
		ESkyguardStormRainBeatKind::IronRain);

	TestFalse(
		TEXT("M05 sequence is not M08 sequence"),
		SequencesEqual(River, Rain));
	TestTrue(
		TEXT("directors expose the same kits"),
		!SequencesEqual(
			ASkyguardMission05IntegrationDirector::GetStormRainBeatKit(),
			ASkyguardMission08IntegrationDirector::GetStormRainBeatKit()));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardStormRainKeepsHydraContractTest,
	"Skyguard52.Campaign.StormRain.KeepsHydraOrRocketHeavy",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardStormRainKeepsHydraContractTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardStormRainBeatKitTests;
	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}

	const FSkyguardStormRainBeatKit& River =
		SkyguardStormRainBeatKits::RiverHammer();
	const FSkyguardStormRainBeatKit& Rain =
		SkyguardStormRainBeatKits::IronRain();
	TestTrue(TEXT("M05 keeps Hydra for clusters"), River.bHydraForClusters);
	TestTrue(TEXT("M08 rain keeps Hydra for clusters"), Rain.bHydraForClusters);
	TestTrue(
		TEXT("Storm weather keeps Hydra"),
		SkyguardStormRainBeatKits::KeepsHydraForClusters(
			ESkyguardMissionWeather::Storm));
	TestTrue(
		TEXT("Rain weather keeps Hydra"),
		SkyguardStormRainBeatKits::KeepsHydraForClusters(
			ESkyguardMissionWeather::Rain));
	TestFalse(
		TEXT("Clear weather is not a storm/rain Hydra identity"),
		SkyguardStormRainBeatKits::KeepsHydraForClusters(
			ESkyguardMissionWeather::Clear));

	TestTrue(
		TEXT("M05 applies Hydra contract"),
		SkyguardStormRainBeatKits::ApplyHydraForClusters(Gunner, River));
	TestTrue(TEXT("M05 starts Hydra or Rocket Heavy"), StartsHydraOrRocketHeavy(Gunner));
	TestEqual(
		TEXT("M05 selects Hydra rockets"),
		Gunner->GetSelectedGunshipWeapon(),
		ESkyguardGunshipWeapon::Rockets);
	TestEqual(
		TEXT("M05 starts Rocket Heavy"),
		Gunner->GetActiveLoadout(),
		ESkyguardLoadout::RocketHeavy);
	TestTrue(TEXT("M05 brings a real rocket magazine"), Gunner->GetRocketAmmo() >= 14);

	Gunner->ApplyLoadout(ESkyguardLoadout::Balanced);
	TestTrue(
		TEXT("M08 applies Hydra contract"),
		SkyguardStormRainBeatKits::ApplyHydraForClusters(Gunner, Rain));
	TestTrue(TEXT("M08 starts Hydra or Rocket Heavy"), StartsHydraOrRocketHeavy(Gunner));
	TestEqual(
		TEXT("M08 selects Hydra rockets"),
		Gunner->GetSelectedGunshipWeapon(),
		ESkyguardGunshipWeapon::Rockets);
	TestEqual(
		TEXT("M08 starts Rocket Heavy"),
		Gunner->GetActiveLoadout(),
		ESkyguardLoadout::RocketHeavy);

	ASkyguardMission05IntegrationDirector* M05 =
		NewObject<ASkyguardMission05IntegrationDirector>();
	ASkyguardMission08IntegrationDirector* M08 =
		NewObject<ASkyguardMission08IntegrationDirector>();
	TestNotNull(TEXT("M05 director"), M05);
	TestNotNull(TEXT("M08 director"), M08);
	if (!M05 || !M08)
	{
		return false;
	}
	Gunner->ApplyLoadout(ESkyguardLoadout::Balanced);
	TestTrue(TEXT("M05 director applies contract"), M05->ApplyStormRainPlayContract(Gunner));
	TestTrue(TEXT("M05 director starts Hydra"), StartsHydraOrRocketHeavy(Gunner));
	Gunner->ApplyLoadout(ESkyguardLoadout::Balanced);
	TestTrue(TEXT("M08 director applies contract"), M08->ApplyStormRainPlayContract(Gunner));
	TestTrue(TEXT("M08 director starts Hydra"), StartsHydraOrRocketHeavy(Gunner));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardStormRainBannedCopyAndHarborClockTest,
	"Skyguard52.Campaign.StormRain.BannedTermsAndHarborClockUntouched",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardStormRainBannedCopyAndHarborClockTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardStormRainBeatKitTests;
	const FSkyguardStormRainBeatKit& River =
		SkyguardStormRainBeatKits::RiverHammer();
	const FSkyguardStormRainBeatKit& Rain =
		SkyguardStormRainBeatKits::IronRain();
	TestTrue(TEXT("M05 copy bans Igla/Yak/rifle"), KitCopyIsClean(River));
	TestTrue(TEXT("M08 copy bans Igla/Yak/rifle"), KitCopyIsClean(Rain));

	const FSkyguardCampaignMissionSpec& Harbor = SkyguardCampaignRoster::Get(1);
	TestEqual(TEXT("harbor id"), Harbor.MissionId, FName(TEXT("M02_HarborShield")));
	const float ExpectedBeats[7] = {120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f};
	for (int32 Index = 0; Index < 7; ++Index)
	{
		TestTrue(
			*FString::Printf(TEXT("Harbor BeatSeconds[%d] untouched"), Index),
			FMath::IsNearlyEqual(Harbor.BeatSeconds[Index], ExpectedBeats[Index], 2.f));
	}
	return true;
}

#endif
