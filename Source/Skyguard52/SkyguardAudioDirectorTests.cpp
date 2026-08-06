#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardAudioDirectorComponent.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardAudioDirectorStateTest,
	"Skyguard52.Audio.Director.DeterministicStateAndBudgets",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardAudioDirectorStateTest::RunTest(const FString& Parameters)
{
	USkyguardAudioDirectorComponent* Director = NewObject<USkyguardAudioDirectorComponent>();
	TestNotNull(TEXT("Audio director can exist without a world or final assets"), Director);

	Director->SetEngineState(0.f, 0.f, 0.f, 1.f);
	TestEqual(TEXT("Stopped engine has full idle blend"), Director->GetIdleBlend(), 1.f);
	TestEqual(TEXT("Stopped engine has no power blend"), Director->GetPowerBlend(), 0.f);

	Director->SetEngineState(1.f, 1.f, 260.f, 1.f);
	TestEqual(TEXT("Full engine state has full power blend"), Director->GetPowerBlend(), 1.f);
	TestEqual(TEXT("Open cockpit at reference speed has full wind blend"), Director->GetWindBlend(), 1.f);

	Director->ApplyHearingSuppression(0.8f, 1.f);
	TestEqual(TEXT("Hearing suppression applies deterministically"), Director->GetSuppressionAmount(), 0.8f);
	Director->AdvanceAudioState(0.5f);
	TestEqual(TEXT("Suppression remains inside its authored duration"), Director->GetSuppressionAmount(), 0.8f);
	Director->AdvanceAudioState(0.51f);
	TestEqual(TEXT("Suppression clears after its duration"), Director->GetSuppressionAmount(), 0.f);

	TestTrue(TEXT("First rifle event is admitted"),
		Director->TriggerEvent(ESkyguardAudioEvent::RifleShot, FVector::ZeroVector));
	TestFalse(TEXT("Immediate duplicate rifle event is rejected by cooldown"),
		Director->TriggerEvent(ESkyguardAudioEvent::RifleShot, FVector::ZeroVector));
	TestEqual(TEXT("Cooldown rejection is captured in telemetry"), Director->GetTelemetry().RejectedByCooldown, 1);
	Director->AdvanceAudioState(2.f);

	Director->GlobalVoiceLimit = 2;
	for (FSkyguardAudioEventDefinition& Definition : Director->EventDefinitions)
	{
		Definition.CooldownSeconds = 0.f;
		Definition.MaxConcurrent = 8;
	}
	TestTrue(TEXT("First low-priority drone voice is accepted with no asset configured"),
		Director->TriggerEvent(ESkyguardAudioEvent::DroneMotor, FVector::ZeroVector));
	TestTrue(TEXT("Second low-priority drone voice is accepted"),
		Director->TriggerEvent(ESkyguardAudioEvent::DroneMotor, FVector::ZeroVector));
	TestTrue(TEXT("Critical heavy explosion evicts a lower-priority voice"),
		Director->TriggerEvent(ESkyguardAudioEvent::ExplosionHeavy, FVector::ZeroVector));
	TestEqual(TEXT("Voice count remains bounded"), Director->GetActiveVoiceCount(), 2);
	TestEqual(TEXT("One priority eviction is recorded"), Director->GetTelemetry().PriorityEvictions, 1);

	Director->AdvanceAudioState(10.f);
	TestEqual(TEXT("Expired estimated voices are removed"), Director->GetActiveVoiceCount(), 0);
	TestEqual(TEXT("Peak voice telemetry preserves the hard limit"), Director->GetTelemetry().PeakActiveVoices, 2);

	return true;
}

#endif
