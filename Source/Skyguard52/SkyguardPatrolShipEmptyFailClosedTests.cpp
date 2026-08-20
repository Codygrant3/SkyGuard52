#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardPatrolShipBoss.h"

#include "Misc/AutomationTest.h"

// Neighbor of SkyguardPatrolShipBossTests.cpp,
// SkyguardPatrolShipNearestSystemTests.cpp, and
// SkyguardPatrolShipPresentationTests.cpp.
// Remaining empty NewObject public getters only, before
// ApplyHit / ApplyHitToSystem / BindPresentation / ConsumeDeckLaunch.
// Existing SkyguardPatrolShipBossTests.cpp covers world-spawn
// system kills and defeat. SkyguardPatrolShipNearestSystemTests.cpp
// covers FindNearestLiveSystem after hits.
// SkyguardPatrolShipPresentationTests.cpp covers BindPresentation
// and MakeHullBindSlot.
// This file is undamaged empty / CDO defaults.
// NewObject only. No CreateWorld / SpawnActor.
// No Gunner / Yak / Igla / rifle live copy.
// Does not call ApplyHit, ApplyHitToSystem, BindPresentation,
// ConsumeDeckLaunch, Tick, or BeginPlay.

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPatrolShipEmptyFailClosedTest,
	"Skyguard52.PatrolShip.EmptyFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPatrolShipEmptyFailClosedTest::RunTest(const FString& Parameters)
{
	ASkyguardPatrolShipBoss* Ship =
		NewObject<ASkyguardPatrolShipBoss>(GetTransientPackage());
	TestNotNull(TEXT("NewObject empty patrol ship constructs"), Ship);
	if (!Ship)
	{
		return false;
	}

	TestTrue(
		TEXT("Constructor enables PrimaryActorTick"),
		Ship->PrimaryActorTick.bCanEverTick);

	TestNotNull(TEXT("NewObject GetHull is non-null"), Ship->GetHull());

	TestFalse(TEXT("NewObject IsDefeated is false"), Ship->IsDefeated());
	TestFalse(TEXT("NewObject IsRadarDead is false"), Ship->IsRadarDead());
	TestFalse(
		TEXT("NewObject AreEnginesDead is false"),
		Ship->AreEnginesDead());

	TestFalse(
		TEXT("NewObject IsSystemDead(Radar) is false"),
		Ship->IsSystemDead(ESkyguardPatrolShipSystem::Radar));
	TestFalse(
		TEXT("NewObject IsSystemDead(Cannon) is false"),
		Ship->IsSystemDead(ESkyguardPatrolShipSystem::Cannon));
	TestFalse(
		TEXT("NewObject IsSystemDead(Launcher) is false"),
		Ship->IsSystemDead(ESkyguardPatrolShipSystem::Launcher));
	TestFalse(
		TEXT("NewObject IsSystemDead(Engines) is false"),
		Ship->IsSystemDead(ESkyguardPatrolShipSystem::Engines));
	TestFalse(
		TEXT("NewObject IsSystemDead(DroneDeck) is false"),
		Ship->IsSystemDead(ESkyguardPatrolShipSystem::DroneDeck));

	TestTrue(
		TEXT("NewObject CanCoordinateAda is true"),
		Ship->CanCoordinateAda());
	TestTrue(
		TEXT("NewObject CanLaunchInbound is true"),
		Ship->CanLaunchInbound());
	TestTrue(
		TEXT("NewObject CanFireCannon is true"),
		Ship->CanFireCannon());
	TestTrue(
		TEXT("NewObject CanLaunchDrones is true"),
		Ship->CanLaunchDrones());

	TestEqual(
		TEXT("NewObject GetDestroyedSystemCount is 0"),
		Ship->GetDestroyedSystemCount(),
		0);
	TestEqual(
		TEXT("NewObject GetLastDestroyedSystem is NAME_None"),
		Ship->GetLastDestroyedSystem(),
		NAME_None);
	TestEqual(
		TEXT("NewObject GetPriorityLiveSystem is Radar"),
		Ship->GetPriorityLiveSystem(),
		ESkyguardPatrolShipSystem::Radar);

	TestEqual(
		TEXT("UnderwayCruiseSpeed is 180"),
		ASkyguardPatrolShipBoss::UnderwayCruiseSpeed,
		180.f);
	TestEqual(
		TEXT("NewObject GetUnderwaySpeed is UnderwayCruiseSpeed"),
		Ship->GetUnderwaySpeed(),
		ASkyguardPatrolShipBoss::UnderwayCruiseSpeed);
	TestEqual(
		TEXT("NewObject GetUnderwaySpeed is 180"),
		Ship->GetUnderwaySpeed(),
		180.f);

	TestEqual(
		TEXT("CannonThreatDamage is 10"),
		ASkyguardPatrolShipBoss::CannonThreatDamage,
		10.f);
	TestEqual(
		TEXT("NewObject GetCannonThreatDamage is CannonThreatDamage"),
		Ship->GetCannonThreatDamage(),
		ASkyguardPatrolShipBoss::CannonThreatDamage);
	TestEqual(
		TEXT("NewObject GetCannonThreatDamage is 10"),
		Ship->GetCannonThreatDamage(),
		10.f);

	return true;
}

#endif
