#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardPilotVoice.h"

#include "Misc/AutomationTest.h"

// Isolated public-API lock for SkyguardPilotVoice::LineDurationForEvent.
// Harbor beat/event call tests already cover LineTextForEvent / CallEvent /
// MakeRadioLine enqueue. This file does not spawn a world, Gunner, Yak,
// Igla, or rifle, and does not call CallEvent or ApplyWeaponHit.

namespace SkyguardPilotVoiceDurationTests
{
	struct FExpectedLineDuration
	{
		ESkyguardPilotLine Line;
		float Seconds;
		const TCHAR* Label;
	};

	const FExpectedLineDuration ExpectedDurations[] = {
		{ESkyguardPilotLine::RadarLit, 3.2f, TEXT("RadarLit")},
		{ESkyguardPilotLine::CargoCritical, 3.2f, TEXT("CargoCritical")},
		{ESkyguardPilotLine::Choice, 3.2f, TEXT("Choice")},
		{ESkyguardPilotLine::GoThermal, 3.2f, TEXT("GoThermal")},
		{ESkyguardPilotLine::Win, 3.0f, TEXT("Win")},
		{ESkyguardPilotLine::Fail, 3.0f, TEXT("Fail")},
		{ESkyguardPilotLine::CargoHit, 2.8f, TEXT("CargoHit")},
		{ESkyguardPilotLine::ShipRadarDown, 2.8f, TEXT("ShipRadarDown")},
		{ESkyguardPilotLine::ShipEnginesDown, 2.8f, TEXT("ShipEnginesDown")},
		{ESkyguardPilotLine::ShipLauncherDown, 2.8f, TEXT("ShipLauncherDown")},
		{ESkyguardPilotLine::ShipDeckDown, 2.8f, TEXT("ShipDeckDown")},
		{ESkyguardPilotLine::ShipDead, 2.8f, TEXT("ShipDead")},
		{ESkyguardPilotLine::Extract, 2.8f, TEXT("Extract")},
		{ESkyguardPilotLine::Inbound, 2.6f, TEXT("Inbound")},
		{ESkyguardPilotLine::ShipCannonDown, 2.6f, TEXT("ShipCannonDown")},
		{ESkyguardPilotLine::FlaresGood, 2.0f, TEXT("FlaresGood")},
		{ESkyguardPilotLine::LoadoutPrompt, 4.0f, TEXT("LoadoutPrompt")},
	};

	bool CopyHasBannedTerm(const FString& Text)
	{
		const FString Lower = Text.ToLower();
		return Lower.Contains(TEXT("igla")) ||
			Lower.Contains(TEXT("yak")) ||
			Lower.Contains(TEXT("rifle"));
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPilotVoiceLineDurationForEventMatchesSwitchTest,
	"Skyguard52.Audio.Pilot.LineDurationForEventMatchesSwitch",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPilotVoiceLineDurationForEventMatchesSwitchTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardPilotVoiceDurationTests;

	for (const FExpectedLineDuration& Entry : ExpectedDurations)
	{
		TestEqual(
			*FString::Printf(TEXT("%s LineDurationForEvent"), Entry.Label),
			SkyguardPilotVoice::LineDurationForEvent(Entry.Line),
			Entry.Seconds);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPilotVoiceMakeRadioLineDurationMatchesEventTest,
	"Skyguard52.Audio.Pilot.MakeRadioLineDurationMatchesLineDurationForEvent",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPilotVoiceMakeRadioLineDurationMatchesEventTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardPilotVoiceDurationTests;

	for (const FExpectedLineDuration& Entry : ExpectedDurations)
	{
		const FSkyguardRadioLine RadioLine =
			SkyguardPilotVoice::MakeRadioLine(Entry.Line);
		TestEqual(
			*FString::Printf(
				TEXT("%s MakeRadioLine duration equals LineDurationForEvent"),
				Entry.Label),
			RadioLine.EstimatedDurationSeconds,
			SkyguardPilotVoice::LineDurationForEvent(Entry.Line));
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPilotVoiceLineTextForEventStaysCleanTest,
	"Skyguard52.Audio.Pilot.LineTextForEventNonEmptyAndBansIglaYakRifle",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPilotVoiceLineTextForEventStaysCleanTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardPilotVoiceDurationTests;

	for (const FExpectedLineDuration& Entry : ExpectedDurations)
	{
		const FString Text = SkyguardPilotVoice::LineTextForEvent(Entry.Line);
		TestFalse(
			*FString::Printf(TEXT("%s LineTextForEvent stays non-empty"), Entry.Label),
			Text.IsEmpty());
		TestFalse(
			*FString::Printf(TEXT("%s LineTextForEvent bans Igla/Yak/rifle"), Entry.Label),
			CopyHasBannedTerm(Text));
	}
	return true;
}

#endif
