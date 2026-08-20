#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardAudioDirectorComponent.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardAudioDirectorTests.cpp.
// Remaining SetEngineState clamp public API only.
// NewObject, no world spawn, no Gunner / Yak / Igla / rifle, no
// TriggerEvent RifleShot/Igla. Existing SkyguardAudioDirectorTests.cpp
// already covers SetEngineState(0,0,0,1) idle and
// SetEngineState(1,1,260,1) full power/wind.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardAudioDirectorEngineStateFailClosedTest,
	"Skyguard52.Audio.Director.EngineStateFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardAudioDirectorEngineStateFailClosedTest::RunTest(const FString& Parameters)
{
	USkyguardAudioDirectorComponent* Director =
		NewObject<USkyguardAudioDirectorComponent>();
	TestNotNull(TEXT("NewObject audio director constructs"), Director);
	if (!Director)
	{
		return false;
	}

	Director->SetEngineState(-1.f, -1.f, -50.f, -1.f);
	TestEqual(
		TEXT("Below-range rpm clamps to 0 so IdleBlend is 1"),
		Director->GetIdleBlend(),
		1.f);
	TestEqual(
		TEXT("Below-range rpm/load clamp so PowerBlend is 0"),
		Director->GetPowerBlend(),
		0.f);
	TestEqual(
		TEXT("Negative airspeed Max 0 and canopy clamp 0 so WindBlend is 0"),
		Director->GetWindBlend(),
		0.f);

	Director->SetEngineState(2.f, 2.f, 1000.f, 2.f);
	TestEqual(
		TEXT("Above-range rpm clamps to 1 so IdleBlend is 0"),
		Director->GetIdleBlend(),
		0.f);
	TestEqual(
		TEXT("Above-range rpm/load clamp so PowerBlend is 1"),
		Director->GetPowerBlend(),
		1.f);
	TestEqual(
		TEXT("Airspeed/260 and canopy clamp to 1 so WindBlend is 1"),
		Director->GetWindBlend(),
		1.f);

	return true;
}

#endif
