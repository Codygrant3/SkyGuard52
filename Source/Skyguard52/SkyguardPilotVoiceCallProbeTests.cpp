#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCpgDebrief.h"
#include "SkyguardPilotVoice.h"

#include "Misc/AutomationTest.h"

// Isolated public-API lock for ResetCallProbe / CallEvent probe state.
// Does not re-test ConfirmLineForCommand or LineDurationForEvent.
// No world, Gunner, Yak, Igla, or rifle spawn.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPilotVoiceCallProbeTest,
	"Skyguard52.Audio.Pilot.CallProbe",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPilotVoiceCallProbeTest::RunTest(const FString& Parameters)
{
	SkyguardPilotVoice::ResetCallProbe();
	TestEqual(
		TEXT("reset last line is RadarLit"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::RadarLit);
	TestTrue(
		TEXT("reset last text is empty"),
		SkyguardPilotVoice::GetLastCalledText().IsEmpty());
	TestEqual(
		TEXT("reset count is 0"),
		SkyguardPilotVoice::GetCalledEventCount(),
		0);

	SkyguardPilotVoice::CallEvent(nullptr, ESkyguardPilotLine::Inbound);
	TestEqual(
		TEXT("nullptr Inbound last line is Inbound"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::Inbound);
	TestEqual(
		TEXT("nullptr Inbound last text"),
		SkyguardPilotVoice::GetLastCalledText(),
		FString(TEXT("Missile inbound — flares!")));
	TestEqual(
		TEXT("nullptr Inbound count is 1"),
		SkyguardPilotVoice::GetCalledEventCount(),
		1);
	TestFalse(
		TEXT("Inbound copy bans Igla/Yak/rifle"),
		SkyguardCpgCopyHasBannedTerm(SkyguardPilotVoice::GetLastCalledText()));

	const int32 CountAfterInbound = SkyguardPilotVoice::GetCalledEventCount();
	const FString TextAfterInbound = SkyguardPilotVoice::GetLastCalledText();
	// 255 is an out-of-range ESkyguardPilotLine (uint8) that hits default:
	// and returns empty LineTextForEvent.
	SkyguardPilotVoice::CallEvent(
		nullptr,
		static_cast<ESkyguardPilotLine>(255));
	TestEqual(
		TEXT("out-of-range 255 does not increment count"),
		SkyguardPilotVoice::GetCalledEventCount(),
		CountAfterInbound);
	TestEqual(
		TEXT("out-of-range 255 leaves last line Inbound"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::Inbound);
	TestEqual(
		TEXT("out-of-range 255 leaves last text unchanged"),
		SkyguardPilotVoice::GetLastCalledText(),
		TextAfterInbound);

	SkyguardPilotVoice::ResetCallProbe();
	TestEqual(
		TEXT("second reset last line is RadarLit"),
		SkyguardPilotVoice::GetLastCalledLine(),
		ESkyguardPilotLine::RadarLit);
	TestTrue(
		TEXT("second reset last text is empty"),
		SkyguardPilotVoice::GetLastCalledText().IsEmpty());
	TestEqual(
		TEXT("second reset count is 0"),
		SkyguardPilotVoice::GetCalledEventCount(),
		0);

	return true;
}

#endif
