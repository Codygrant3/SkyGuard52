#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardAudioDirectorComponent.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardAudioDirectorTests.cpp.
// Remaining SetListenerPerspective public API only. NewObject, no
// world spawn, no Gunner / Yak / Igla / rifle, no RifleShot / Igla
// events, no invented ListenerPerspective getter. Existing
// SkyguardAudioDirectorTests.cpp already covers SetEngineState
// blends, ApplyHearingSuppression duration, and TriggerEvent
// cooldown/voice budget.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardAudioDirectorListenerPerspectiveFailClosedTest,
	"Skyguard52.Audio.Director.ListenerPerspectiveFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardAudioDirectorListenerPerspectiveFailClosedTest::RunTest(
	const FString& Parameters)
{
	USkyguardAudioDirectorComponent* Director =
		NewObject<USkyguardAudioDirectorComponent>();
	TestNotNull(TEXT("NewObject audio director constructs"), Director);
	if (!Director)
	{
		return false;
	}

	TestNull(
		TEXT("NewObject director has no production bank"),
		Director->ProductionBank.Get());
	TestEqual(
		TEXT("NewObject CockpitExteriorAttenuation is 0.72"),
		Director->CockpitExteriorAttenuation,
		0.72f);
	TestEqual(
		TEXT("NewObject CockpitLowPassHz is 7200"),
		Director->CockpitLowPassHz,
		7200.f);
	TestEqual(TEXT("NewObject GetIdleBlend is 1"), Director->GetIdleBlend(), 1.f);
	TestEqual(TEXT("NewObject GetCruiseBlend is 0"), Director->GetCruiseBlend(), 0.f);
	TestEqual(TEXT("NewObject GetPowerBlend is 0"), Director->GetPowerBlend(), 0.f);
	TestEqual(TEXT("NewObject GetWindBlend is 0"), Director->GetWindBlend(), 0.f);
	TestEqual(
		TEXT("NewObject GetSuppressionAmount is 0"),
		Director->GetSuppressionAmount(),
		0.f);

	const FSkyguardAudioTelemetry Empty = Director->GetTelemetry();
	TestEqual(TEXT("NewObject RequestedEvents is 0"), Empty.RequestedEvents, 0);
	TestEqual(TEXT("NewObject PlayedEvents is 0"), Empty.PlayedEvents, 0);
	TestEqual(TEXT("NewObject RejectedByCooldown is 0"), Empty.RejectedByCooldown, 0);
	TestEqual(
		TEXT("NewObject RejectedByConcurrency is 0"),
		Empty.RejectedByConcurrency,
		0);
	TestEqual(
		TEXT("NewObject RejectedMissingAsset is 0"),
		Empty.RejectedMissingAsset,
		0);
	TestEqual(TEXT("NewObject PriorityEvictions is 0"), Empty.PriorityEvictions, 0);
	TestEqual(TEXT("NewObject PeakActiveVoices is 0"), Empty.PeakActiveVoices, 0);
	TestEqual(TEXT("NewObject GetActiveVoiceCount is 0"), Director->GetActiveVoiceCount(), 0);
	TestEqual(
		TEXT("NewObject GetResolvedProductionLoopRouteCount is 0"),
		Director->GetResolvedProductionLoopRouteCount(),
		0);
	TestFalse(
		TEXT("NewObject AreResolvedProductionLoopRoutesComplete is false"),
		Director->AreResolvedProductionLoopRoutesComplete());

	Director->SetListenerPerspective(ESkyguardListenerPerspective::RearCockpit);
	Director->SetListenerPerspective(ESkyguardListenerPerspective::Exterior);

	TestNull(
		TEXT("SetListenerPerspective leaves ProductionBank null"),
		Director->ProductionBank.Get());
	TestEqual(
		TEXT("SetListenerPerspective leaves CockpitExteriorAttenuation 0.72"),
		Director->CockpitExteriorAttenuation,
		0.72f);
	TestEqual(
		TEXT("SetListenerPerspective leaves CockpitLowPassHz 7200"),
		Director->CockpitLowPassHz,
		7200.f);
	TestEqual(
		TEXT("SetListenerPerspective leaves GetIdleBlend 1"),
		Director->GetIdleBlend(),
		1.f);
	TestEqual(
		TEXT("SetListenerPerspective leaves GetCruiseBlend 0"),
		Director->GetCruiseBlend(),
		0.f);
	TestEqual(
		TEXT("SetListenerPerspective leaves GetPowerBlend 0"),
		Director->GetPowerBlend(),
		0.f);
	TestEqual(
		TEXT("SetListenerPerspective leaves GetWindBlend 0"),
		Director->GetWindBlend(),
		0.f);
	TestEqual(
		TEXT("SetListenerPerspective leaves GetSuppressionAmount 0"),
		Director->GetSuppressionAmount(),
		0.f);

	const FSkyguardAudioTelemetry AfterPerspective = Director->GetTelemetry();
	TestEqual(
		TEXT("SetListenerPerspective leaves RequestedEvents 0"),
		AfterPerspective.RequestedEvents,
		0);
	TestEqual(
		TEXT("SetListenerPerspective leaves PlayedEvents 0"),
		AfterPerspective.PlayedEvents,
		0);
	TestEqual(
		TEXT("SetListenerPerspective leaves RejectedByCooldown 0"),
		AfterPerspective.RejectedByCooldown,
		0);
	TestEqual(
		TEXT("SetListenerPerspective leaves RejectedByConcurrency 0"),
		AfterPerspective.RejectedByConcurrency,
		0);
	TestEqual(
		TEXT("SetListenerPerspective leaves RejectedMissingAsset 0"),
		AfterPerspective.RejectedMissingAsset,
		0);
	TestEqual(
		TEXT("SetListenerPerspective leaves PriorityEvictions 0"),
		AfterPerspective.PriorityEvictions,
		0);
	TestEqual(
		TEXT("SetListenerPerspective leaves PeakActiveVoices 0"),
		AfterPerspective.PeakActiveVoices,
		0);
	TestEqual(
		TEXT("SetListenerPerspective leaves GetActiveVoiceCount 0"),
		Director->GetActiveVoiceCount(),
		0);
	TestEqual(
		TEXT("SetListenerPerspective leaves GetResolvedProductionLoopRouteCount 0"),
		Director->GetResolvedProductionLoopRouteCount(),
		0);
	TestFalse(
		TEXT("SetListenerPerspective leaves loop routes incomplete"),
		Director->AreResolvedProductionLoopRoutesComplete());

	return true;
}

#endif
