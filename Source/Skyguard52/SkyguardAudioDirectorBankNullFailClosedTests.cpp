#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardAudioDirectorComponent.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardAudioDirectorTests.cpp.
// Remaining ApplyProductionBank(nullptr) / empty-audit public API only.
// NewObject, no world spawn, no Gunner / Yak / Igla / rifle, no
// InitializeRequiredEntries, no real bank apply. Existing
// SkyguardAudioProductionBankTests.cpp already covers applying a
// bank and EvaluateReadiness.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardAudioDirectorBankNullFailClosedTest,
	"Skyguard52.Audio.Director.BankNullFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardAudioDirectorBankNullFailClosedTest::RunTest(const FString& Parameters)
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

	const FSkyguardProductionAudioAudit DefaultAudit =
		Director->GetProductionBankAudit();
	TestEqual(
		TEXT("NewObject GetProductionBankAudit RequiredCategoryCount is 0"),
		DefaultAudit.RequiredCategoryCount,
		0);
	TestEqual(
		TEXT("NewObject GetProductionBankAudit ExplicitMissingSourceCount is 0"),
		DefaultAudit.ExplicitMissingSourceCount,
		0);
	TestFalse(
		TEXT("NewObject GetProductionBankAudit bProductionReady is false"),
		DefaultAudit.bProductionReady);
	TestFalse(
		TEXT("NewObject GetProductionBankAudit bCategoryContractComplete is false"),
		DefaultAudit.bCategoryContractComplete);
	TestEqual(
		TEXT("NewObject GetProductionBankAudit MissingRoutingAssets is empty"),
		DefaultAudit.MissingRoutingAssets.Num(),
		0);
	TestEqual(
		TEXT("NewObject GetResolvedProductionLoopRouteCount is 0"),
		Director->GetResolvedProductionLoopRouteCount(),
		0);
	TestFalse(
		TEXT("NewObject AreResolvedProductionLoopRoutesComplete is false"),
		Director->AreResolvedProductionLoopRoutesComplete());

	Director->ApplyProductionBank(nullptr);

	TestNull(
		TEXT("ApplyProductionBank(nullptr) leaves ProductionBank null"),
		Director->ProductionBank.Get());

	const FSkyguardProductionAudioAudit NullBankAudit =
		Director->GetProductionBankAudit();
	TestEqual(
		TEXT("ApplyProductionBank(nullptr) keeps RequiredCategoryCount 0"),
		NullBankAudit.RequiredCategoryCount,
		0);
	TestEqual(
		TEXT("ApplyProductionBank(nullptr) keeps ExplicitMissingSourceCount 0"),
		NullBankAudit.ExplicitMissingSourceCount,
		0);
	TestFalse(
		TEXT("ApplyProductionBank(nullptr) keeps bProductionReady false"),
		NullBankAudit.bProductionReady);
	TestFalse(
		TEXT("ApplyProductionBank(nullptr) keeps bCategoryContractComplete false"),
		NullBankAudit.bCategoryContractComplete);
	TestEqual(
		TEXT("ApplyProductionBank(nullptr) keeps MissingRoutingAssets empty"),
		NullBankAudit.MissingRoutingAssets.Num(),
		0);
	TestEqual(
		TEXT("ApplyProductionBank(nullptr) does not rebuild loop routes"),
		Director->GetResolvedProductionLoopRouteCount(),
		0);
	TestFalse(
		TEXT("ApplyProductionBank(nullptr) leaves loop routes incomplete"),
		Director->AreResolvedProductionLoopRoutesComplete());

	return true;
}

#endif
