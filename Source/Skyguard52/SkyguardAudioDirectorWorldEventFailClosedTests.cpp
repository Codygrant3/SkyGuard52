#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardAudioDirectorComponent.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardAudioDirectorTests.cpp.
// Remaining TriggerWorldEvent / unregistered-director fail-closed
// public API only. NewObject, no world spawn, no Gunner / Yak / Igla /
// rifle, no ApplyWeaponHit. Existing SkyguardAudioDirectorTests.cpp
// already covers SetEngineState blends, ApplyHearingSuppression
// duration, and TriggerEvent cooldown/voice budget.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardAudioDirectorWorldEventFailClosedTest,
	"Skyguard52.Audio.Director.WorldEventFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardAudioDirectorWorldEventFailClosedTest::RunTest(const FString& Parameters)
{
	TestFalse(
		TEXT("TriggerWorldEvent(nullptr) is fail-closed"),
		USkyguardAudioDirectorComponent::TriggerWorldEvent(
			nullptr,
			ESkyguardAudioEvent::ExplosionHeavy,
			FVector::ZeroVector));

	USkyguardAudioDirectorComponent* Unregistered =
		NewObject<USkyguardAudioDirectorComponent>();
	TestNotNull(TEXT("NewObject audio director constructs"), Unregistered);
	if (!Unregistered)
	{
		return false;
	}

	TestNull(
		TEXT("NewObject director has no UWorld"),
		Unregistered->GetWorld());
	TestFalse(
		TEXT("TriggerWorldEvent on an unregistered NewObject director is fail-closed"),
		USkyguardAudioDirectorComponent::TriggerWorldEvent(
			Unregistered,
			ESkyguardAudioEvent::ExplosionHeavy,
			FVector::ZeroVector));

	return true;
}

#endif
