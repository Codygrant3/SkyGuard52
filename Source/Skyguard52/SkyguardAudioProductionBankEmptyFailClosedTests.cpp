#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardAudioProductionBank.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardAudioProductionBankTests.cpp.
// Remaining empty-Entries NewObject fail-closed public API only.
// Does not call InitializeRequiredEntries / EnsureDefaultEntries.
// Existing SkyguardAudioProductionBankTests.cpp already covers
// InitializeRequiredEntries + EvaluateReadiness on a filled
// MISSING_SOURCE bank. NewObject only. No world spawn, no Gunner /
// Yak / Igla / rifle. FindEntry uses EngineIdle and ExplosionHeavyBody
// only (not RifleMuzzle / IglaLock / IglaLaunch).
// HasBoundObject and HasValidSha256 are private on origin/main;
// this file does not invent a public call.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardAudioProductionBankEmptyFailClosedTest,
	"Skyguard52.Audio.ProductionBank.EmptyEntriesFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardAudioProductionBankEmptyFailClosedTest::RunTest(const FString& Parameters)
{
	USkyguardAudioProductionBank* Bank = NewObject<USkyguardAudioProductionBank>();
	TestNotNull(TEXT("NewObject production bank constructs"), Bank);
	if (!Bank)
	{
		return false;
	}

	TestEqual(TEXT("NewObject Entries is empty"), Bank->Entries.Num(), 0);
	TestTrue(TEXT("NewObject MasterSubmix is null"), Bank->Routing.MasterSubmix.IsNull());
	TestTrue(TEXT("NewObject CockpitSubmix is null"), Bank->Routing.CockpitSubmix.IsNull());
	TestTrue(TEXT("NewObject ExteriorSubmix is null"), Bank->Routing.ExteriorSubmix.IsNull());
	TestTrue(TEXT("NewObject WeaponsSubmix is null"), Bank->Routing.WeaponsSubmix.IsNull());
	TestTrue(TEXT("NewObject ExplosionsSubmix is null"), Bank->Routing.ExplosionsSubmix.IsNull());
	TestTrue(TEXT("NewObject RadioSubmix is null"), Bank->Routing.RadioSubmix.IsNull());
	TestTrue(TEXT("NewObject CockpitSoundMix is null"), Bank->Routing.CockpitSoundMix.IsNull());
	TestEqual(
		TEXT("NewObject CockpitExteriorAttenuation is 0.72"),
		Bank->Routing.CockpitExteriorAttenuation,
		0.72f);
	TestEqual(
		TEXT("NewObject CockpitLowPassHz is 7200"),
		Bank->Routing.CockpitLowPassHz,
		7200.f);

	const TArray<ESkyguardProductionAudioCategory>& Required =
		USkyguardAudioProductionBank::GetRequiredCategories();
	const FSkyguardProductionAudioAudit Audit = Bank->EvaluateReadiness();

	TestEqual(
		TEXT("Empty bank RequiredCategoryCount matches GetRequiredCategories().Num()"),
		Audit.RequiredCategoryCount,
		Required.Num());
	TestEqual(
		TEXT("Empty bank lists every required category as missing (DuplicateCount != 1)"),
		Audit.MissingCategoryEntries.Num(),
		Required.Num());

	const UEnum* CategoryEnum = StaticEnum<ESkyguardProductionAudioCategory>();
	TestNotNull(TEXT("ESkyguardProductionAudioCategory reflection is available"), CategoryEnum);
	if (CategoryEnum)
	{
		for (const ESkyguardProductionAudioCategory Category : Required)
		{
			const FName Expected(
				*CategoryEnum->GetNameStringByValue(static_cast<int64>(Category)));
			TestTrue(
				*FString::Printf(
					TEXT("MissingCategoryEntries contains %s (DuplicateCount != 1)"),
					*Expected.ToString()),
				Audit.MissingCategoryEntries.Contains(Expected));
		}
	}

	TestEqual(
		TEXT("Empty Entries ExplicitMissingSourceCount is 0"),
		Audit.ExplicitMissingSourceCount,
		0);
	TestEqual(
		TEXT("Empty Entries BoundProductionSourceCount is 0"),
		Audit.BoundProductionSourceCount,
		0);
	TestFalse(
		TEXT("Empty Entries bCategoryContractComplete is false"),
		Audit.bCategoryContractComplete);
	TestFalse(
		TEXT("Empty Entries bProductionReady is false"),
		Audit.bProductionReady);
	TestEqual(
		TEXT("Empty routing reports all seven missing assets"),
		Audit.MissingRoutingAssets.Num(),
		7);
	TestTrue(
		TEXT("MissingRoutingAssets names MasterSubmix"),
		Audit.MissingRoutingAssets.Contains(FName(TEXT("MasterSubmix"))));
	TestTrue(
		TEXT("MissingRoutingAssets names CockpitSubmix"),
		Audit.MissingRoutingAssets.Contains(FName(TEXT("CockpitSubmix"))));
	TestTrue(
		TEXT("MissingRoutingAssets names ExteriorSubmix"),
		Audit.MissingRoutingAssets.Contains(FName(TEXT("ExteriorSubmix"))));
	TestTrue(
		TEXT("MissingRoutingAssets names WeaponsSubmix"),
		Audit.MissingRoutingAssets.Contains(FName(TEXT("WeaponsSubmix"))));
	TestTrue(
		TEXT("MissingRoutingAssets names ExplosionsSubmix"),
		Audit.MissingRoutingAssets.Contains(FName(TEXT("ExplosionsSubmix"))));
	TestTrue(
		TEXT("MissingRoutingAssets names RadioSubmix"),
		Audit.MissingRoutingAssets.Contains(FName(TEXT("RadioSubmix"))));
	TestTrue(
		TEXT("MissingRoutingAssets names CockpitSoundMix"),
		Audit.MissingRoutingAssets.Contains(FName(TEXT("CockpitSoundMix"))));

	TestEqual(
		TEXT("GetUnboundRequiredCategories covers every required category"),
		Bank->GetUnboundRequiredCategories().Num(),
		Required.Num());
	TestNull(
		TEXT("FindEntry(EngineIdle) is nullptr on empty Entries"),
		Bank->FindEntry(ESkyguardProductionAudioCategory::EngineIdle));
	TestNull(
		TEXT("FindEntry(ExplosionHeavyBody) is nullptr on empty Entries"),
		Bank->FindEntry(ESkyguardProductionAudioCategory::ExplosionHeavyBody));
	TestFalse(
		TEXT("ConfigureRoutingTopology returns false when MasterSubmix cannot load"),
		Bank->ConfigureRoutingTopology());

	return true;
}

#endif
