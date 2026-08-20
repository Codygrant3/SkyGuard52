#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCoastalEnvironmentDirector.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardCoastalEnvironmentDirectorTests.cpp.
// Remaining empty-director NewObject public defaults only, before
// RebuildDeterministicVegetation / RefreshCapabilityBindings /
// ApplyQuality / ApplyMissionWeather. Existing
// SkyguardCoastalEnvironmentDirectorTests.cpp already covers
// ApplyQuality Low vs Epic in a world.
// NewObject only. No world, no Gunner / Yak / Igla / rifle.
// Does not call RebuildDeterministicVegetation, RefreshCapabilityBindings,
// ApplyQuality, or ApplyMissionWeather.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCoastalEnvironmentDirectorEmptyFailClosedTest,
	"Skyguard52.Environment.CoastalDirector.EmptyFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCoastalEnvironmentDirectorEmptyFailClosedTest::RunTest(
	const FString& Parameters)
{
	ASkyguardCoastalEnvironmentDirector* Director =
		NewObject<ASkyguardCoastalEnvironmentDirector>(GetTransientPackage());
	TestNotNull(TEXT("NewObject empty coastal environment director constructs"), Director);
	if (!Director)
	{
		return false;
	}

	TestFalse(
		TEXT("Constructor disables PrimaryActorTick"),
		Director->PrimaryActorTick.bCanEverTick);

	TestEqual(
		TEXT("NewObject Quality is High"),
		Director->Quality,
		ESkyguardEnvironmentQuality::High);
	TestEqual(
		TEXT("NewObject PlacementSeed is 5201"),
		Director->PlacementSeed,
		5201);
	TestEqual(
		TEXT("NewObject EpicTreeBudget is 240"),
		Director->EpicTreeBudget,
		240);
	TestEqual(
		TEXT("NewObject EpicShrubBudget is 480"),
		Director->EpicShrubBudget,
		480);

	TestEqual(
		TEXT("NewObject RouteLengthCm is 45000"),
		Director->RouteLengthCm,
		45000.f);
	TestEqual(
		TEXT("NewObject RouteCorridorHalfWidthCm is 2800"),
		Director->RouteCorridorHalfWidthCm,
		2800.f);

	TestEqual(
		TEXT("NewObject WindStrength is 0.35"),
		Director->WindStrength,
		0.35f);
	TestEqual(
		TEXT("NewObject WindSpeed is 0.5"),
		Director->WindSpeed,
		0.5f);

	TestEqual(
		TEXT("NewObject GetAppliedWeather is Clear"),
		Director->GetAppliedWeather(),
		ESkyguardMissionWeather::Clear);

	const FSkyguardEnvironmentReadiness& Readiness = Director->GetReadiness();
	TestEqual(
		TEXT("NewObject GetReadiness BoundCapabilityCount is 0"),
		Readiness.BoundCapabilityCount,
		0);
	TestEqual(
		TEXT("NewObject GetReadiness TreeInstanceCount is 0"),
		Readiness.TreeInstanceCount,
		0);
	TestEqual(
		TEXT("NewObject GetReadiness ShrubInstanceCount is 0"),
		Readiness.ShrubInstanceCount,
		0);
	TestEqual(
		TEXT("NewObject GetReadiness VFXPoolSize is 0"),
		Readiness.VFXPoolSize,
		0);

	return true;
}

#endif
