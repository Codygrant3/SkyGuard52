#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCampaignRoster.h"
#include "Misc/AutomationTest.h"

namespace SkyguardCampaignRosterTests
{
	bool CopyContainsBannedTerm(const TCHAR* Text)
	{
		const FString Lower = FString(Text).ToLower();
		return Lower.Contains(TEXT("igla")) ||
			Lower.Contains(TEXT("yak")) ||
			Lower.Contains(TEXT("rifle"));
	}

	bool MentionsCannon(const FString& Text)
	{
		return Text.Contains(TEXT("cannon"), ESearchCase::IgnoreCase) ||
			Text.Contains(TEXT("30 mm"), ESearchCase::IgnoreCase) ||
			Text.Contains(TEXT("30mm"), ESearchCase::IgnoreCase);
	}

	bool MentionsRocketsOrMissiles(const FString& Text)
	{
		return Text.Contains(TEXT("rocket"), ESearchCase::IgnoreCase) ||
			Text.Contains(TEXT("hydra"), ESearchCase::IgnoreCase) ||
			Text.Contains(TEXT("missile"), ESearchCase::IgnoreCase) ||
			Text.Contains(TEXT("hellfire"), ESearchCase::IgnoreCase);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignRosterIdentityTest,
	"Skyguard52.Campaign.RosterIdentity",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignRosterIdentityTest::RunTest(const FString& Parameters)
{
	TestEqual(TEXT("ten campaign sorties"), SkyguardCampaignRoster::NumMissions(), 10);
	TestEqual(
		TEXT("M01 id stable"),
		SkyguardCampaignRoster::IdAt(0),
		FName(TEXT("M01_CoastalIntercept")));
	TestEqual(
		TEXT("M02 id stable"),
		SkyguardCampaignRoster::IdAt(1),
		FName(TEXT("M02_HarborShield")));
	TestEqual(
		TEXT("M02 title stays Harbor Breaker"),
		FString(SkyguardCampaignRoster::Get(1).Title),
		FString(TEXT("Harbor Breaker")));
	TestEqual(
		TEXT("finale id stable"),
		SkyguardCampaignRoster::IdAt(9),
		FName(TEXT("M10_EvacuationFinale")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardHarborBreakerProofClockTest,
	"Skyguard52.Campaign.HarborBreakerProofClock",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardHarborBreakerProofClockTest::RunTest(const FString& Parameters)
{
	const FSkyguardCampaignMissionSpec& Spec = SkyguardCampaignRoster::Get(1);
	TestEqual(TEXT("harbor id"), Spec.MissionId, FName(TEXT("M02_HarborShield")));
	TestEqual(TEXT("harbor title"), FString(Spec.Title), FString(TEXT("Harbor Breaker")));

	// Pivot proof table, cumulative seconds: 2 / 4 / 6 / 8 / 10 / 13 / 15 min.
	const float ExpectedBeats[7] = {120.f, 240.f, 360.f, 480.f, 600.f, 780.f, 900.f};
	const TCHAR* BeatNames[7] = {
		TEXT("approach ends 2 min"),
		TEXT("boats end 4 min"),
		TEXT("shore armor ends 6 min"),
		TEXT("radar ends 8 min"),
		TEXT("choice ends 10 min"),
		TEXT("patrol-ship climax ends 13 min"),
		TEXT("extract ends 15 min")
	};
	for (int32 Index = 0; Index < 7; ++Index)
	{
		TestTrue(
			BeatNames[Index],
			FMath::IsNearlyEqual(Spec.BeatSeconds[Index], ExpectedBeats[Index], 2.f));
	}

	TestEqual(TEXT("contact boats"), Spec.ContactKind, ESkyguardThreatKind::FastBoat);
	TestEqual(TEXT("shore armor"), Spec.ShoreKind, ESkyguardThreatKind::GroundArmor);
	TestEqual(TEXT("patrol-ship climax"), Spec.Climax, ESkyguardClimaxKind::PatrolShip);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignRosterCpgCopyTest,
	"Skyguard52.Campaign.RosterCpgCopy",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignRosterCpgCopyTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCampaignRosterTests;

	for (int32 Index = 0; Index < SkyguardCampaignRoster::NumMissions(); ++Index)
	{
		const FSkyguardCampaignMissionSpec& Spec = SkyguardCampaignRoster::Get(Index);
		const FString Label = Spec.MissionId.ToString();
		TestFalse(
			*FString::Printf(TEXT("%s brief bans Igla/Yak/rifle"), *Label),
			CopyContainsBannedTerm(Spec.Brief));
		TestFalse(
			*FString::Printf(TEXT("%s success bans Igla/Yak/rifle"), *Label),
			CopyContainsBannedTerm(Spec.Success));
		TestFalse(
			*FString::Printf(TEXT("%s failure bans Igla/Yak/rifle"), *Label),
			CopyContainsBannedTerm(Spec.Failure));
		TestFalse(
			*FString::Printf(TEXT("%s is not a shoot-down-the-drones mission"), *Label),
			FString(Spec.Brief).Contains(
				TEXT("shoot down the drones"),
				ESearchCase::IgnoreCase));
	}

	const FString M01 = SkyguardCampaignRoster::Get(0).Brief;
	TestTrue(TEXT("M01 teaches cannon"), MentionsCannon(M01));
	TestTrue(
		TEXT("M01 teaches rockets or missiles"),
		MentionsRocketsOrMissiles(M01));
	TestFalse(TEXT("M01 is not Igla"), CopyContainsBannedTerm(M01));

	const FString Night = SkyguardCampaignRoster::Get(3).Brief;
	TestTrue(
		TEXT("night brief keeps thermal"),
		Night.Contains(TEXT("thermal"), ESearchCase::IgnoreCase));

	const FString Storm = SkyguardCampaignRoster::Get(4).Brief;
	TestTrue(
		TEXT("storm brief keeps rockets for clusters"),
		Storm.Contains(TEXT("rocket"), ESearchCase::IgnoreCase) &&
			Storm.Contains(TEXT("cluster"), ESearchCase::IgnoreCase));
	return true;
}

#endif
