#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardAudioProceduralBankComponent.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardAudioProceduralBankTests.cpp.
// Remaining empty-Waves NewObject fail-closed public API only.
// Does not call BuildDevelopmentCues. Existing
// SkyguardAudioProceduralBankTests.cpp already covers
// BuildDevelopmentCues (six cues, checksums, disable-then-rebuild).
// NewObject only. No world spawn, no Gunner / Yak / Igla / rifle.
// Live cues under test: ExplosionHeavy and RadioBeep only
// (not RifleImpulse / IglaLockTone / IglaLaunchImpulse).

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardAudioProceduralBankEmptyFailClosedTest,
	"Skyguard52.Audio.ProceduralAudition.EmptyWavesFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardAudioProceduralBankEmptyFailClosedTest::RunTest(const FString& Parameters)
{
	USkyguardAudioProceduralBankComponent* Bank =
		NewObject<USkyguardAudioProceduralBankComponent>();
	TestNotNull(TEXT("NewObject procedural bank constructs"), Bank);
	if (!Bank)
	{
		return false;
	}

	TestFalse(
		TEXT("Constructor disables component tick"),
		Bank->PrimaryComponentTick.bCanEverTick);
	TestEqual(TEXT("NewObject SampleRate is 48000"), Bank->SampleRate, 48000);
	TestEqual(
		TEXT("NewObject GeneratedByteBudget is 1048576"),
		Bank->GeneratedByteBudget,
		1048576);
	TestTrue(
		TEXT("NewObject bEnableDevelopmentAudition is true"),
		Bank->bEnableDevelopmentAudition);

	TestEqual(
		TEXT("Empty Waves GetCueCount is 0 before BuildDevelopmentCues"),
		Bank->GetCueCount(),
		0);
	TestEqual(
		TEXT("Empty Waves GetTotalGeneratedBytes is 0 before BuildDevelopmentCues"),
		Bank->GetTotalGeneratedBytes(),
		0);
	TestNull(
		TEXT("GetCue(ExplosionHeavy) is nullptr on empty Waves"),
		Bank->GetCue(ESkyguardProceduralAuditionCue::ExplosionHeavy));
	TestNull(
		TEXT("GetCue(RadioBeep) is nullptr on empty Waves"),
		Bank->GetCue(ESkyguardProceduralAuditionCue::RadioBeep));
	TestEqual(
		TEXT("GetCueChecksum(ExplosionHeavy) is 0 on empty Waves"),
		Bank->GetCueChecksum(ESkyguardProceduralAuditionCue::ExplosionHeavy),
		0u);
	TestEqual(
		TEXT("GetCueChecksum(RadioBeep) is 0 on empty Waves"),
		Bank->GetCueChecksum(ESkyguardProceduralAuditionCue::RadioBeep),
		0u);
	TestFalse(
		TEXT("AuditionCue(ExplosionHeavy) is false on empty Waves (invalid index / null)"),
		Bank->AuditionCue(ESkyguardProceduralAuditionCue::ExplosionHeavy));
	TestFalse(
		TEXT("AuditionCue(RadioBeep) is false on empty Waves (invalid index / null)"),
		Bank->AuditionCue(ESkyguardProceduralAuditionCue::RadioBeep));
	TestTrue(
		TEXT("IsAuditionAllowed is true outside Shipping when bEnableDevelopmentAudition is true"),
		Bank->IsAuditionAllowed());

	Bank->bEnableDevelopmentAudition = false;
	TestFalse(
		TEXT("IsAuditionAllowed is false when bEnableDevelopmentAudition is false"),
		Bank->IsAuditionAllowed());
	TestFalse(
		TEXT("AuditionCue(ExplosionHeavy) is false when audition is disabled (cues do not exist)"),
		Bank->AuditionCue(ESkyguardProceduralAuditionCue::ExplosionHeavy));

	return true;
}

#endif
