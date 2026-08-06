#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardAudioProceduralBankComponent.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardAudioProceduralBankTest,
	"Skyguard52.Audio.ProceduralAudition.DeterministicBoundedSignals",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardAudioProceduralBankTest::RunTest(const FString& Parameters)
{
	USkyguardAudioProceduralBankComponent* First =
		NewObject<USkyguardAudioProceduralBankComponent>();
	USkyguardAudioProceduralBankComponent* Second =
		NewObject<USkyguardAudioProceduralBankComponent>();
	First->BuildDevelopmentCues();
	Second->BuildDevelopmentCues();

	TestTrue(TEXT("Development audition is enabled outside Shipping"), First->IsAuditionAllowed());
	TestEqual(TEXT("Six lawful procedural audition signals are generated"), First->GetCueCount(), 6);
	TestTrue(TEXT("Generated PCM remains inside its hard memory budget"),
		First->GetTotalGeneratedBytes() > 0
		&& First->GetTotalGeneratedBytes() <= First->GeneratedByteBudget);
	TestEqual(TEXT("Identical bank builds use identical byte counts"),
		First->GetTotalGeneratedBytes(), Second->GetTotalGeneratedBytes());
	UE_LOG(
		LogTemp,
		Display,
		TEXT("[SkyguardPhase5] Procedural audition cues=%d bytes=%d budget=%d"),
		First->GetCueCount(),
		First->GetTotalGeneratedBytes(),
		First->GeneratedByteBudget);

	for (int32 Index = 0; Index < 6; ++Index)
	{
		const ESkyguardProceduralAuditionCue Cue =
			static_cast<ESkyguardProceduralAuditionCue>(Index);
		TestNotNull(TEXT("Every procedural category has an audition signal"), First->GetCue(Cue));
		TestTrue(TEXT("Every audition signal has a non-zero deterministic checksum"),
			First->GetCueChecksum(Cue) != 0);
		TestEqual(TEXT("Checksums remain deterministic across builds"),
			First->GetCueChecksum(Cue), Second->GetCueChecksum(Cue));
	}

	First->bEnableDevelopmentAudition = false;
	First->BuildDevelopmentCues();
	TestEqual(TEXT("Disabling audition clears generated signals"), First->GetCueCount(), 0);
	TestFalse(TEXT("Disabled bank cannot play a signal"),
		First->AuditionCue(ESkyguardProceduralAuditionCue::RifleImpulse));
	return true;
}

#endif
