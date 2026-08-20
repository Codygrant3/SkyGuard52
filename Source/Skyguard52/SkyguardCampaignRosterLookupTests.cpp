#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCampaignRoster.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardMissionTypes.h"

#include "Misc/AutomationTest.h"

namespace SkyguardCampaignRosterLookupTests
{
	bool CopyContainsBannedTerm(const TCHAR* Text)
	{
		if (!Text)
		{
			return false;
		}
		const FString Lower = FString(Text).ToLower();
		return Lower.Contains(TEXT("igla")) ||
			Lower.Contains(TEXT("yak")) ||
			Lower.Contains(TEXT("rifle"));
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignRosterLookupCountAndIndexTest,
	"Skyguard52.Campaign.Roster.LookupCountAndIndex",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignRosterLookupCountAndIndexTest::RunTest(
	const FString& Parameters)
{
	TestEqual(
		TEXT("NumMissions is the ten-mission roster"),
		SkyguardCampaignRoster::NumMissions(),
		10);

	TestEqual(
		TEXT("IndexOf(M01_CoastalIntercept) is 0"),
		SkyguardCampaignRoster::IndexOf(TEXT("M01_CoastalIntercept")),
		0);
	TestEqual(
		TEXT("IndexOf(M02_HarborShield) is 1"),
		SkyguardCampaignRoster::IndexOf(TEXT("M02_HarborShield")),
		1);
	TestEqual(
		TEXT("IndexOf(M10_EvacuationFinale) is 9"),
		SkyguardCampaignRoster::IndexOf(TEXT("M10_EvacuationFinale")),
		9);

	TestEqual(
		TEXT("IndexOf(NAME_None) returns 0, not INDEX_NONE"),
		SkyguardCampaignRoster::IndexOf(NAME_None),
		0);
	TestEqual(
		TEXT("IndexOf of an unknown id returns 0, not INDEX_NONE"),
		SkyguardCampaignRoster::IndexOf(TEXT("UnknownRosterMission")),
		0);

	TestEqual(
		TEXT("IdAt(0) is M01_CoastalIntercept"),
		SkyguardCampaignRoster::IdAt(0),
		FName(TEXT("M01_CoastalIntercept")));
	TestEqual(
		TEXT("IdAt(1) is M02_HarborShield"),
		SkyguardCampaignRoster::IdAt(1),
		FName(TEXT("M02_HarborShield")));
	TestEqual(
		TEXT("IdAt(9) is M10_EvacuationFinale"),
		SkyguardCampaignRoster::IdAt(9),
		FName(TEXT("M10_EvacuationFinale")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignRosterLookupClampTest,
	"Skyguard52.Campaign.Roster.LookupClamp",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignRosterLookupClampTest::RunTest(const FString& Parameters)
{
	const FSkyguardCampaignMissionSpec& ClampedLow =
		SkyguardCampaignRoster::Get(-1);
	const FSkyguardCampaignMissionSpec& ClampedHigh =
		SkyguardCampaignRoster::Get(99);
	const FSkyguardCampaignMissionSpec& First =
		SkyguardCampaignRoster::Get(0);
	const FSkyguardCampaignMissionSpec& Last =
		SkyguardCampaignRoster::Get(9);

	TestFalse(TEXT("Get(-1) yields a valid mission id"), ClampedLow.MissionId.IsNone());
	TestFalse(TEXT("Get(99) yields a valid mission id"), ClampedHigh.MissionId.IsNone());
	TestEqual(
		TEXT("Get(-1) clamps to the first roster mission"),
		ClampedLow.MissionId,
		First.MissionId);
	TestEqual(
		TEXT("Get(99) clamps to the last roster mission"),
		ClampedHigh.MissionId,
		Last.MissionId);
	TestEqual(
		TEXT("Get(-1) is M01_CoastalIntercept"),
		ClampedLow.MissionId,
		FName(TEXT("M01_CoastalIntercept")));
	TestEqual(
		TEXT("Get(99) is M10_EvacuationFinale"),
		ClampedHigh.MissionId,
		FName(TEXT("M10_EvacuationFinale")));

	TestEqual(
		TEXT("IdAt(-1) follows Get(-1)"),
		SkyguardCampaignRoster::IdAt(-1),
		ClampedLow.MissionId);
	TestEqual(
		TEXT("IdAt(99) follows Get(99)"),
		SkyguardCampaignRoster::IdAt(99),
		ClampedHigh.MissionId);
	TestEqual(
		TEXT("IdAt(-1) matches IdAt(0)"),
		SkyguardCampaignRoster::IdAt(-1),
		SkyguardCampaignRoster::IdAt(0));
	TestEqual(
		TEXT("IdAt(99) matches IdAt(9)"),
		SkyguardCampaignRoster::IdAt(99),
		SkyguardCampaignRoster::IdAt(9));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignRosterLookupLabelTest,
	"Skyguard52.Campaign.Roster.LookupLabels",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignRosterLookupLabelTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCampaignRosterLookupTests;

	const TCHAR* AntiArmor =
		SkyguardCampaignRoster::LoadoutLabel(ESkyguardLoadout::AntiArmor);
	const TCHAR* RocketHeavy =
		SkyguardCampaignRoster::LoadoutLabel(ESkyguardLoadout::RocketHeavy);
	const TCHAR* Intercept =
		SkyguardCampaignRoster::LoadoutLabel(ESkyguardLoadout::Intercept);
	const TCHAR* Balanced =
		SkyguardCampaignRoster::LoadoutLabel(ESkyguardLoadout::Balanced);

	TestEqual(
		TEXT("AntiArmor label is Anti-Armor"),
		FString(AntiArmor),
		FString(TEXT("Anti-Armor")));
	TestEqual(
		TEXT("RocketHeavy label is Rocket Heavy"),
		FString(RocketHeavy),
		FString(TEXT("Rocket Heavy")));
	TestEqual(
		TEXT("Intercept label is Intercept"),
		FString(Intercept),
		FString(TEXT("Intercept")));
	TestEqual(
		TEXT("Balanced label is Balanced"),
		FString(Balanced),
		FString(TEXT("Balanced")));

	const TCHAR* Clear =
		SkyguardCampaignRoster::WeatherEnumLabel(ESkyguardMissionWeather::Clear);
	const TCHAR* Overcast =
		SkyguardCampaignRoster::WeatherEnumLabel(ESkyguardMissionWeather::Overcast);
	const TCHAR* Rain =
		SkyguardCampaignRoster::WeatherEnumLabel(ESkyguardMissionWeather::Rain);
	const TCHAR* Storm =
		SkyguardCampaignRoster::WeatherEnumLabel(ESkyguardMissionWeather::Storm);
	const TCHAR* NightClear =
		SkyguardCampaignRoster::WeatherEnumLabel(ESkyguardMissionWeather::NightClear);
	const TCHAR* NightOvercast =
		SkyguardCampaignRoster::WeatherEnumLabel(
			ESkyguardMissionWeather::NightOvercast);

	TestEqual(
		TEXT("Clear weather label"),
		FString(Clear),
		FString(TEXT("Clear")));
	TestEqual(
		TEXT("Overcast weather label"),
		FString(Overcast),
		FString(TEXT("Overcast")));
	TestEqual(
		TEXT("Rain weather label"),
		FString(Rain),
		FString(TEXT("Rain")));
	TestEqual(
		TEXT("Storm weather label"),
		FString(Storm),
		FString(TEXT("Storm")));
	TestEqual(
		TEXT("NightClear weather label uses a space"),
		FString(NightClear),
		FString(TEXT("Night clear")));
	TestEqual(
		TEXT("NightOvercast weather label uses a space"),
		FString(NightOvercast),
		FString(TEXT("Night overcast")));

	const TCHAR* LabelCopy[] = {
		AntiArmor,
		RocketHeavy,
		Intercept,
		Balanced,
		Clear,
		Overcast,
		Rain,
		Storm,
		NightClear,
		NightOvercast
	};
	for (const TCHAR* Label : LabelCopy)
	{
		TestFalse(
			*FString::Printf(
				TEXT("label '%s' bans Igla/Yak/rifle"),
				Label ? Label : TEXT("")),
			CopyContainsBannedTerm(Label));
	}
	return true;
}

#endif
