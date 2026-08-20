#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardAudioAcceptanceHarness.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardAudioProductionBankTests.cpp.
// Remaining CompleteEvidenceRun fail-closed paths only. Does not re-test
// no audible device, missing production bank, or any underrun.
// NewObject only. No world, Gunner, Yak, Igla, or rifle.

namespace SkyguardAudioAcceptanceHarnessFailClosedTests
{
	FString ValidHash()
	{
		return FString::ChrN(64, TEXT('a'));
	}

	FString NonHexHash()
	{
		return FString::ChrN(64, TEXT('g'));
	}

	void RecordGoodSamples(
		USkyguardAudioAcceptanceHarness* Harness,
		const int32 Count)
	{
		for (int32 Index = 0; Index < Count; ++Index)
		{
			Harness->RecordMeasuredSample(24, 0, 0.8f, -2.f);
		}
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardAudioAcceptanceHarnessFailClosedTest,
	"Skyguard52.Audio.Acceptance.FailClosedRemainingPaths",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardAudioAcceptanceHarnessFailClosedTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardAudioAcceptanceHarnessFailClosedTests;

	USkyguardAudioAcceptanceHarness* Harness =
		NewObject<USkyguardAudioAcceptanceHarness>(GetTransientPackage());
	TestNotNull(TEXT("NewObject harness constructs"), Harness);
	if (!Harness)
	{
		return false;
	}

	TestFalse(
		TEXT("NewObject default GetReceipt().bAccepted is false"),
		Harness->GetReceipt().bAccepted);
	TestEqual(
		TEXT("NewObject default GetReceipt().SampleCount is 0"),
		Harness->GetReceipt().SampleCount,
		0);
	TestEqual(
		TEXT("Default MinimumMeasuredSamples is 600"),
		Harness->MinimumMeasuredSamples,
		600);
	TestEqual(
		TEXT("Default MaximumAllowedVoices is 48"),
		Harness->MaximumAllowedVoices,
		48);
	TestEqual(
		TEXT("Default MaximumAudioThreadMs is 2"),
		Harness->MaximumAudioThreadMs,
		2.f);
	TestEqual(
		TEXT("Default MaximumTruePeakDbTP is -1"),
		Harness->MaximumTruePeakDbTP,
		-1.f);

	Harness->RecordMeasuredSample(24, 0, 0.8f, -2.f);
	TestEqual(
		TEXT("RecordMeasuredSample before BeginEvidenceRun is ignored"),
		Harness->GetReceipt().SampleCount,
		0);
	TestFalse(
		TEXT("GetReceipt().bAccepted stays false before BeginEvidenceRun"),
		Harness->GetReceipt().bAccepted);

	const FString Hash = ValidHash();
	const FString BadHex = NonHexHash();

	Harness->BeginEvidenceRun(TEXT("short"), Hash, true, true, true, true);
	RecordGoodSamples(Harness, 600);
	TestFalse(
		TEXT("Short BuildSha256 refuses CompleteEvidenceRun"),
		Harness->CompleteEvidenceRun());
	TestFalse(
		TEXT("Short BuildSha256 leaves bAccepted false"),
		Harness->GetReceipt().bAccepted);

	Harness->BeginEvidenceRun(Hash, TEXT("short"), true, true, true, true);
	RecordGoodSamples(Harness, 600);
	TestFalse(
		TEXT("Short EvidenceSha256 refuses CompleteEvidenceRun"),
		Harness->CompleteEvidenceRun());
	TestFalse(
		TEXT("Short EvidenceSha256 leaves bAccepted false"),
		Harness->GetReceipt().bAccepted);

	Harness->BeginEvidenceRun(BadHex, Hash, true, true, true, true);
	RecordGoodSamples(Harness, 600);
	TestFalse(
		TEXT("Non-hex BuildSha256 refuses CompleteEvidenceRun"),
		Harness->CompleteEvidenceRun());
	TestFalse(
		TEXT("Non-hex BuildSha256 leaves bAccepted false"),
		Harness->GetReceipt().bAccepted);

	Harness->BeginEvidenceRun(Hash, BadHex, true, true, true, true);
	RecordGoodSamples(Harness, 600);
	TestFalse(
		TEXT("Non-hex EvidenceSha256 refuses CompleteEvidenceRun"),
		Harness->CompleteEvidenceRun());
	TestFalse(
		TEXT("Non-hex EvidenceSha256 leaves bAccepted false"),
		Harness->GetReceipt().bAccepted);

	Harness->BeginEvidenceRun(Hash, Hash, true, true, true, true);
	RecordGoodSamples(Harness, 599);
	TestEqual(
		TEXT("Fewer than MinimumMeasuredSamples records 599 samples"),
		Harness->GetReceipt().SampleCount,
		599);
	TestFalse(
		TEXT("Fewer than MinimumMeasuredSamples refuses CompleteEvidenceRun"),
		Harness->CompleteEvidenceRun());
	TestFalse(
		TEXT("Fewer than MinimumMeasuredSamples leaves bAccepted false"),
		Harness->GetReceipt().bAccepted);

	Harness->BeginEvidenceRun(Hash, Hash, true, true, true, true);
	for (int32 Index = 0; Index < 600; ++Index)
	{
		Harness->RecordMeasuredSample(Index == 0 ? 49 : 24, 0, 0.8f, -2.f);
	}
	TestFalse(
		TEXT("PeakActiveVoices above MaximumAllowedVoices refuses CompleteEvidenceRun"),
		Harness->CompleteEvidenceRun());
	TestFalse(
		TEXT("PeakActiveVoices above cap leaves bAccepted false"),
		Harness->GetReceipt().bAccepted);

	Harness->BeginEvidenceRun(Hash, Hash, true, true, true, true);
	for (int32 Index = 0; Index < 600; ++Index)
	{
		Harness->RecordMeasuredSample(24, 0, Index == 0 ? 2.5f : 0.8f, -2.f);
	}
	TestFalse(
		TEXT("MaximumAudioThreadMs above the harness cap refuses CompleteEvidenceRun"),
		Harness->CompleteEvidenceRun());
	TestFalse(
		TEXT("Audio thread ms above cap leaves bAccepted false"),
		Harness->GetReceipt().bAccepted);

	Harness->BeginEvidenceRun(Hash, Hash, true, true, true, true);
	for (int32 Index = 0; Index < 600; ++Index)
	{
		Harness->RecordMeasuredSample(24, 0, 0.8f, Index == 0 ? 0.f : -2.f);
	}
	TestFalse(
		TEXT("MaximumTruePeakDbTP above the harness cap refuses CompleteEvidenceRun"),
		Harness->CompleteEvidenceRun());
	TestFalse(
		TEXT("True peak above cap leaves bAccepted false"),
		Harness->GetReceipt().bAccepted);

	Harness->BeginEvidenceRun(Hash, Hash, false, true, true, true);
	RecordGoodSamples(Harness, 600);
	TestFalse(
		TEXT("bPackagedDevelopmentBuild false refuses CompleteEvidenceRun"),
		Harness->CompleteEvidenceRun());
	TestFalse(
		TEXT("Unpacked build leaves bAccepted false"),
		Harness->GetReceipt().bAccepted);

	Harness->BeginEvidenceRun(Hash, Hash, true, true, false, true);
	RecordGoodSamples(Harness, 600);
	TestFalse(
		TEXT("bCalibratedMetering false refuses CompleteEvidenceRun"),
		Harness->CompleteEvidenceRun());
	TestFalse(
		TEXT("Uncalibrated metering leaves bAccepted false"),
		Harness->GetReceipt().bAccepted);

	return true;
}

#endif
