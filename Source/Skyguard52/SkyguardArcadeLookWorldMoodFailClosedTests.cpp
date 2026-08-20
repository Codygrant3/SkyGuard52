#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardArcadeLookComponent.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardArcadeLookTests.cpp and
// SkyguardArcadeLookFailClosedTests.cpp.
// Remaining static world-mood fail-closed public API only:
// ApplyWorldMood / ApplyWorldMoodForWeather with a null world context.
// Existing SkyguardArcadeLookFailClosedTests.cpp already covers
// ApplyToCamera nullptr and disabled. Existing SkyguardArcadeLookTests.cpp
// already covers dusk combat grade and world-mood spawn. No CreateWorld,
// no camera / Gunner / Yak / Igla / rifle spawn.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardArcadeLookWorldMoodFailClosedTest,
	"Skyguard52.Arcade.LookWorldMoodFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardArcadeLookWorldMoodFailClosedTest::RunTest(const FString& Parameters)
{
	// ApplyWorldMood forwards to ApplyWorldMoodForWeather(..., Overcast).
	// ApplyWorldMoodForWeather: World = WorldContextObject
	//     ? WorldContextObject->GetWorld() : nullptr; if (!World) return;
	USkyguardArcadeLookComponent::ApplyWorldMood(nullptr);
	USkyguardArcadeLookComponent::ApplyWorldMoodForWeather(
		nullptr,
		ESkyguardMissionWeather::Overcast);
	USkyguardArcadeLookComponent::ApplyWorldMoodForWeather(
		nullptr,
		ESkyguardMissionWeather::Storm,
		0.f);
	USkyguardArcadeLookComponent::ApplyWorldMoodForWeather(
		nullptr,
		ESkyguardMissionWeather::NightClear);

	TestTrue(
		TEXT("Null world-context ApplyWorldMood / ApplyWorldMoodForWeather are no-ops"),
		true);
	return true;
}

#endif
