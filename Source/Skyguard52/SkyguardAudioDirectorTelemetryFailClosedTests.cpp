#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardAudioDirectorComponent.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardAudioDirectorTests.cpp.
// Remaining empty-telemetry / ExplosionHeavy play / cooldown public
// API only. NewObject, no world spawn, no Gunner / Yak / Igla / rifle,
// no RifleShot / Igla events. Existing SkyguardAudioDirectorTests.cpp
// already covers SetEngineState blends, ApplyHearingSuppression
// duration, and GlobalVoiceLimit eviction.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardAudioDirectorTelemetryFailClosedTest,
	"Skyguard52.Audio.Director.TelemetryFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardAudioDirectorTelemetryFailClosedTest::RunTest(const FString& Parameters)
{
	USkyguardAudioDirectorComponent* Director =
		NewObject<USkyguardAudioDirectorComponent>();
	TestNotNull(TEXT("NewObject audio director constructs"), Director);
	if (!Director)
	{
		return false;
	}

	const FSkyguardAudioTelemetry Empty = Director->GetTelemetry();
	TestEqual(TEXT("NewObject RequestedEvents is 0"), Empty.RequestedEvents, 0);
	TestEqual(TEXT("NewObject PlayedEvents is 0"), Empty.PlayedEvents, 0);
	TestEqual(TEXT("NewObject RejectedByCooldown is 0"), Empty.RejectedByCooldown, 0);
	TestEqual(TEXT("NewObject RejectedByConcurrency is 0"), Empty.RejectedByConcurrency, 0);
	TestEqual(TEXT("NewObject RejectedMissingAsset is 0"), Empty.RejectedMissingAsset, 0);
	TestEqual(TEXT("NewObject PriorityEvictions is 0"), Empty.PriorityEvictions, 0);
	TestEqual(TEXT("NewObject PeakActiveVoices is 0"), Empty.PeakActiveVoices, 0);
	TestEqual(TEXT("NewObject GetActiveVoiceCount is 0"), Director->GetActiveVoiceCount(), 0);

	TestTrue(
		TEXT("TriggerEvent(ExplosionHeavy) is admitted"),
		Director->TriggerEvent(ESkyguardAudioEvent::ExplosionHeavy, FVector::ZeroVector));

	const FSkyguardAudioTelemetry AfterPlay = Director->GetTelemetry();
	TestEqual(TEXT("Played ExplosionHeavy RequestedEvents is 1"), AfterPlay.RequestedEvents, 1);
	TestEqual(TEXT("Played ExplosionHeavy PlayedEvents is 1"), AfterPlay.PlayedEvents, 1);
	TestEqual(TEXT("Played ExplosionHeavy PeakActiveVoices is 1"), AfterPlay.PeakActiveVoices, 1);
	TestEqual(TEXT("Played ExplosionHeavy GetActiveVoiceCount is 1"), Director->GetActiveVoiceCount(), 1);
	TestEqual(
		TEXT("Played ExplosionHeavy does not increment RejectedByCooldown"),
		AfterPlay.RejectedByCooldown,
		0);
	TestEqual(
		TEXT("Played ExplosionHeavy does not increment RejectedByConcurrency"),
		AfterPlay.RejectedByConcurrency,
		0);
	TestEqual(
		TEXT("Played ExplosionHeavy does not increment RejectedMissingAsset"),
		AfterPlay.RejectedMissingAsset,
		0);
	TestEqual(
		TEXT("Played ExplosionHeavy does not increment PriorityEvictions"),
		AfterPlay.PriorityEvictions,
		0);

	TestFalse(
		TEXT("Immediate second ExplosionHeavy is rejected by cooldown"),
		Director->TriggerEvent(ESkyguardAudioEvent::ExplosionHeavy, FVector::ZeroVector));

	const FSkyguardAudioTelemetry AfterCooldown = Director->GetTelemetry();
	TestEqual(
		TEXT("Cooldown reject RequestedEvents is 2"),
		AfterCooldown.RequestedEvents,
		2);
	TestEqual(
		TEXT("Cooldown reject PlayedEvents stays 1"),
		AfterCooldown.PlayedEvents,
		1);
	TestEqual(
		TEXT("Cooldown reject RejectedByCooldown is 1"),
		AfterCooldown.RejectedByCooldown,
		1);
	TestEqual(
		TEXT("Cooldown reject PeakActiveVoices stays 1"),
		AfterCooldown.PeakActiveVoices,
		1);
	TestEqual(
		TEXT("Cooldown reject GetActiveVoiceCount stays 1"),
		Director->GetActiveVoiceCount(),
		1);
	TestEqual(
		TEXT("Cooldown reject does not increment RejectedByConcurrency"),
		AfterCooldown.RejectedByConcurrency,
		0);
	TestEqual(
		TEXT("Cooldown reject does not increment RejectedMissingAsset"),
		AfterCooldown.RejectedMissingAsset,
		0);
	TestEqual(
		TEXT("Cooldown reject does not increment PriorityEvictions"),
		AfterCooldown.PriorityEvictions,
		0);

	return true;
}

#endif
