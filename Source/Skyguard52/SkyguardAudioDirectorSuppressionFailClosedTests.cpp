#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardAudioDirectorComponent.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardAudioDirectorTests.cpp.
// Remaining ApplyHearingSuppression clamp / AdvanceAudioState
// fail-closed public API only. NewObject, no world spawn, no
// Gunner / Yak / Igla / rifle, no RifleShot / Igla events. Existing
// SkyguardAudioDirectorTests.cpp already covers SetEngineState blends,
// ApplyHearingSuppression(0.8, 1) duration, and TriggerEvent
// cooldown/voice budget.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardAudioDirectorSuppressionFailClosedTest,
	"Skyguard52.Audio.Director.SuppressionFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardAudioDirectorSuppressionFailClosedTest::RunTest(const FString& Parameters)
{
	USkyguardAudioDirectorComponent* Defaults =
		NewObject<USkyguardAudioDirectorComponent>();
	TestNotNull(TEXT("NewObject audio director constructs"), Defaults);
	if (!Defaults)
	{
		return false;
	}

	TestEqual(
		TEXT("NewObject GetSuppressionAmount is 0"),
		Defaults->GetSuppressionAmount(),
		0.f);
	TestEqual(
		TEXT("NewObject GetActiveVoiceCount is 0"),
		Defaults->GetActiveVoiceCount(),
		0);

	USkyguardAudioDirectorComponent* Overstrength =
		NewObject<USkyguardAudioDirectorComponent>();
	TestNotNull(TEXT("Overstrength NewObject audio director constructs"), Overstrength);
	if (!Overstrength)
	{
		return false;
	}

	Overstrength->ApplyHearingSuppression(5.f, 1.f);
	TestEqual(
		TEXT("ApplyHearingSuppression(5, 1) clamps amount to 1"),
		Overstrength->GetSuppressionAmount(),
		1.f);

	Overstrength->AdvanceAudioState(-1.f);
	TestEqual(
		TEXT("AdvanceAudioState(-1) is a no-op (SafeDelta 0)"),
		Overstrength->GetSuppressionAmount(),
		1.f);
	TestEqual(
		TEXT("AdvanceAudioState(-1) does not spawn voices"),
		Overstrength->GetActiveVoiceCount(),
		0);

	USkyguardAudioDirectorComponent* NegativeStrength =
		NewObject<USkyguardAudioDirectorComponent>();
	TestNotNull(
		TEXT("Negative-strength NewObject audio director constructs"),
		NegativeStrength);
	if (!NegativeStrength)
	{
		return false;
	}

	NegativeStrength->ApplyHearingSuppression(-1.f, 1.f);
	TestEqual(
		TEXT("ApplyHearingSuppression(-1, 1) clamps amount to 0"),
		NegativeStrength->GetSuppressionAmount(),
		0.f);

	USkyguardAudioDirectorComponent* NegativeDuration =
		NewObject<USkyguardAudioDirectorComponent>();
	TestNotNull(
		TEXT("Negative-duration NewObject audio director constructs"),
		NegativeDuration);
	if (!NegativeDuration)
	{
		return false;
	}

	NegativeDuration->ApplyHearingSuppression(0.4f, -10.f);
	TestEqual(
		TEXT("ApplyHearingSuppression(0.4, -10) applies amount 0.4"),
		NegativeDuration->GetSuppressionAmount(),
		0.4f);

	NegativeDuration->AdvanceAudioState(0.5f);
	TestEqual(
		TEXT("AdvanceAudioState(0.5) does not clear amount when remaining was never > 0"),
		NegativeDuration->GetSuppressionAmount(),
		0.4f);

	return true;
}

#endif
