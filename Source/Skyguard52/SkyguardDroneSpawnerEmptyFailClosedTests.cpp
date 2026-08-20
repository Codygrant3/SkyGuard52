#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardDroneSpawner.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardDroneSpawnerTests.cpp.
// Remaining empty-spawner NewObject public CDO defaults only.
// Existing SkyguardDroneSpawnerTests.cpp already covers
// CreateWorld / SpawnActor / Tick / SetSpawningEnabled and the
// MaxActiveDrones cap.
// NewObject only. No world, no Gunner / Yak / Igla / rifle.
// Does not call SetSpawningEnabled, Tick, BeginPlay, or
// CountActiveDrones. Does not spawn drones.
// Does not invent INDEX_NONE.
// Does not assert Harbor IncomingRadarLiveIntervalSeconds /
// IncomingRadarDownIntervalSeconds.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardDroneSpawnerEmptyFailClosedTest,
	"Skyguard52.DroneSpawner.EmptyFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardDroneSpawnerEmptyFailClosedTest::RunTest(const FString& Parameters)
{
	ASkyguardDroneSpawner* Spawner =
		NewObject<ASkyguardDroneSpawner>(GetTransientPackage());
	TestNotNull(TEXT("NewObject empty drone spawner constructs"), Spawner);
	if (!Spawner)
	{
		return false;
	}

	TestTrue(
		TEXT("Constructor enables PrimaryActorTick"),
		Spawner->PrimaryActorTick.bCanEverTick);

	TestTrue(
		TEXT("NewObject bSpawningEnabled is true"),
		Spawner->bSpawningEnabled);
	TestEqual(
		TEXT("NewObject SpawnInterval is 1.85"),
		Spawner->SpawnInterval,
		1.85f);
	TestEqual(
		TEXT("NewObject MaxActiveDrones is 12"),
		Spawner->MaxActiveDrones,
		12);
	TestEqual(
		TEXT("NewObject HeavyLaneModulo is 4"),
		Spawner->HeavyLaneModulo,
		4);
	TestTrue(
		TEXT("NewObject bMixedThreatRoster is true"),
		Spawner->bMixedThreatRoster);
	TestEqual(
		TEXT("NewObject LightSpeedMin is 1300"),
		Spawner->LightSpeedMin,
		1300.f);
	TestEqual(
		TEXT("NewObject LightSpeedMax is 1750"),
		Spawner->LightSpeedMax,
		1750.f);
	TestEqual(
		TEXT("NewObject HeavyCruiseSpeed is 1150"),
		Spawner->HeavyCruiseSpeed,
		1150.f);

	return true;
}

#endif
