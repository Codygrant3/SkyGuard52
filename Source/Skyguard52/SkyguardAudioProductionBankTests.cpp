#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardAudioAcceptanceHarness.h"
#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardAudioProductionBank.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardAudioProductionBankContractTest,
	"Skyguard52.Audio.ProductionBank.ExplicitMissingSourceContract",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardAudioProductionBankContractTest::RunTest(const FString& Parameters)
{
	USkyguardAudioProductionBank* Bank = NewObject<USkyguardAudioProductionBank>();
	Bank->InitializeRequiredEntries();
	const FSkyguardProductionAudioAudit Audit = Bank->EvaluateReadiness();
	TestEqual(TEXT("Every production category has one explicit entry"),
		Bank->Entries.Num(), USkyguardAudioProductionBank::GetRequiredCategories().Num());
	TestTrue(TEXT("Missing content remains an explicit, structurally valid contract"),
		Audit.bCategoryContractComplete);
	TestEqual(TEXT("Every absent recording reports MISSING_SOURCE"),
		Audit.ExplicitMissingSourceCount, Audit.RequiredCategoryCount);
	TestEqual(TEXT("No unavailable source is misrepresented as production-bound"),
		Audit.BoundProductionSourceCount, 0);
	TestFalse(TEXT("Explicit missing sources cannot pass production readiness"),
		Audit.bProductionReady);
	TestEqual(TEXT("All seven routing assets remain visibly missing"),
		Audit.MissingRoutingAssets.Num(), 7);

	Bank->Routing.CockpitExteriorAttenuation = 0.61f;
	Bank->Routing.CockpitLowPassHz = 6400.f;
	USkyguardAudioDirectorComponent* Director =
		NewObject<USkyguardAudioDirectorComponent>();
	Director->ApplyProductionBank(Bank);
	TestEqual(TEXT("Production bank applies cockpit attenuation to listener state"),
		Director->CockpitExteriorAttenuation, 0.61f);
	TestEqual(TEXT("Production bank applies cockpit filtering to listener state"),
		Director->CockpitLowPassHz, 6400.f);
	TestEqual(TEXT("Director exposes the same explicit missing-source audit"),
		Director->GetProductionBankAudit().ExplicitMissingSourceCount,
		Audit.RequiredCategoryCount);
	TestEqual(TEXT("Applying the bank resolves all five continuous loop routes"),
		Director->GetResolvedProductionLoopRouteCount(), 5);
	TestFalse(TEXT("Unsourced loop routes cannot claim complete routing"),
		Director->AreResolvedProductionLoopRoutesComplete());

	FSkyguardProductionAudioEntry& Candidate = Bank->Entries[0];
	Candidate.SourceStatus =
		ESkyguardAudioSourceStatus::PROJECT_OWNED_RECORDING;
	Candidate.Sound = TSoftObjectPtr<USoundBase>(
		FSoftObjectPath(TEXT("/Game/Skyguard/Audio/Production/Test/SW_Test.SW_Test")));
	Candidate.ProvenanceId = TEXT("test_provenance");
	Candidate.SourceSha256 = FString::ChrN(64, TEXT('a'));
	const FSkyguardProductionAudioAudit UnroutedAudit =
		Bank->EvaluateReadiness();
	TestEqual(TEXT("A sourced entry without attenuation is reported"),
		UnroutedAudit.MissingAttenuationBindings.Num(), 1);
	TestEqual(TEXT("A sourced entry without concurrency is reported"),
		UnroutedAudit.MissingConcurrencyBindings.Num(), 1);
	TestEqual(TEXT("A sourced entry without output submix is reported"),
		UnroutedAudit.MissingOutputSubmixBindings.Num(), 1);
	TestFalse(TEXT("A sourced but unrouted bank remains fail closed"),
		UnroutedAudit.bProductionReady);

	Bank->Entries.RemoveAt(0);
	const FSkyguardProductionAudioAudit MissingEntryAudit = Bank->EvaluateReadiness();
	TestFalse(TEXT("Deleting a required category breaks contract coverage"),
		MissingEntryAudit.bCategoryContractComplete);
	TestEqual(TEXT("Deleted category is named in the audit"),
		MissingEntryAudit.MissingCategoryEntries.Num(), 1);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardAudioAcceptanceHarnessTest,
	"Skyguard52.Audio.Acceptance.RefusesUnprovenAudibleClaims",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardAudioAcceptanceHarnessTest::RunTest(const FString& Parameters)
{
	USkyguardAudioAcceptanceHarness* Harness = NewObject<USkyguardAudioAcceptanceHarness>();
	const FString ValidHash = FString::ChrN(64, TEXT('a'));

	Harness->BeginEvidenceRun(ValidHash, ValidHash, true, false, true, true);
	for (int32 Index = 0; Index < 600; ++Index)
	{
		Harness->RecordMeasuredSample(24, 0, 0.8f, -2.f);
	}
	TestFalse(TEXT("A run without an observed audible device cannot pass"),
		Harness->CompleteEvidenceRun());

	Harness->BeginEvidenceRun(ValidHash, ValidHash, true, true, true, false);
	for (int32 Index = 0; Index < 600; ++Index)
	{
		Harness->RecordMeasuredSample(24, 0, 0.8f, -2.f);
	}
	TestFalse(TEXT("A run with missing production sources cannot pass"),
		Harness->CompleteEvidenceRun());

	Harness->BeginEvidenceRun(ValidHash, ValidHash, true, true, true, true);
	for (int32 Index = 0; Index < 600; ++Index)
	{
		Harness->RecordMeasuredSample(24, Index == 500 ? 1 : 0, 0.8f, -2.f);
	}
	TestFalse(TEXT("Any measured underrun rejects the run"),
		Harness->CompleteEvidenceRun());
	return true;
}

#endif
