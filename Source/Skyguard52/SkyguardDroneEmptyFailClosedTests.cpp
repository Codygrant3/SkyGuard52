#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardDrone.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardDroneMeshBindTests.cpp and
// SkyguardDroneAircraftDamageTests.cpp.
// Remaining empty NewObject public getters and UPROPERTY defaults only.
// Existing SkyguardDroneMeshBindTests.cpp covers MakeHullBindSlot /
// Preferred-empty catalog policy. SkyguardDroneAircraftDamageTests.cpp
// covers world-spawn Yak ram wiring.
// This file is undamaged empty / CDO defaults.
// NewObject only. No CreateWorld / SpawnActor.
// No Gunner / Yak / Igla / rifle live copy.
// Does not call ApplyBallisticHit, ImpactAircraft, ImpactPlatform,
// ConfigureThreat, ConfigureRoadConvoy, ConfigureVariant, BindHull,
// Tick, or BeginPlay.
// ImpactAircraft is historical Yak ram — not live player fantasy.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardDroneEmptyFailClosedTest,
	"Skyguard52.Drone.EmptyFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardDroneEmptyFailClosedTest::RunTest(const FString& Parameters)
{
	ASkyguardDrone* Drone =
		NewObject<ASkyguardDrone>(GetTransientPackage());
	TestNotNull(TEXT("NewObject empty drone constructs"), Drone);
	if (!Drone)
	{
		return false;
	}

	TestTrue(
		TEXT("Constructor enables PrimaryActorTick"),
		Drone->PrimaryActorTick.bCanEverTick);

	TestNotNull(TEXT("NewObject GetHull is non-null"), Drone->GetHull());

	TestEqual(
		TEXT("NewObject GetThreatKind is FastAttacker"),
		Drone->GetThreatKind(),
		ESkyguardThreatKind::FastAttacker);
	TestFalse(TEXT("NewObject IsHeavyTarget is false"), Drone->IsHeavyTarget());
	TestFalse(TEXT("NewObject bHeavy is false"), Drone->bHeavy);

	TestFalse(TEXT("NewObject IsDestroyed is false"), Drone->IsDestroyed());
	TestFalse(TEXT("NewObject HasReachedCity is false"), Drone->HasReachedCity());
	TestFalse(
		TEXT("NewObject IsFollowingRoad is false"),
		Drone->IsFollowingRoad());
	TestEqual(
		TEXT("NewObject GetRoadWaypointIndex is 0"),
		Drone->GetRoadWaypointIndex(),
		0);

	TestEqual(TEXT("NewObject Health is 34"), Drone->Health, 34.f);
	TestEqual(TEXT("NewObject MaxHealth is 34"), Drone->MaxHealth, 34.f);
	TestEqual(TEXT("NewObject CruiseSpeed is 1600"), Drone->CruiseSpeed, 1600.f);
	TestTrue(
		TEXT("NewObject TargetCityLocation is (-1800, 0, 350)"),
		Drone->TargetCityLocation.Equals(FVector(-1800.f, 0.f, 350.f)));

	// origin/main: FastAttacker && !bHeavy && MaxHealth < 80 is ineligible.
	TestFalse(
		TEXT("NewObject IsMissileLockEligible is false"),
		Drone->IsMissileLockEligible());

	TestEqual(
		TEXT("RoadConvoyCruiseSpeed is 320"),
		ASkyguardDrone::RoadConvoyCruiseSpeed,
		320.f);
	TestEqual(
		TEXT("RoadConvoyTruckHealth is 220"),
		ASkyguardDrone::RoadConvoyTruckHealth,
		220.f);
	TestEqual(
		TEXT("RoadConvoyCarHealth is 160"),
		ASkyguardDrone::RoadConvoyCarHealth,
		160.f);

	const FSkyguardMeshBindSlot HullSlot = ASkyguardDrone::MakeHullBindSlot();
	TestEqual(
		TEXT("MakeHullBindSlot SlotId is Drone.Hull"),
		HullSlot.SlotId,
		FName(TEXT("Drone.Hull")));
	TestTrue(
		TEXT("MakeHullBindSlot Preferred is empty"),
		HullSlot.Preferred.IsNull());

	return true;
}

#endif
