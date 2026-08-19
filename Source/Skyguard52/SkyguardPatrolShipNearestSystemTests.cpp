#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardGunshipTypes.h"
#include "SkyguardPatrolShipBoss.h"
#include "Components/PrimitiveComponent.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardPatrolShipNearestSystemTests
{
	const ESkyguardPatrolShipSystem kPriorityOrder[] = {
		ESkyguardPatrolShipSystem::Radar,
		ESkyguardPatrolShipSystem::Cannon,
		ESkyguardPatrolShipSystem::Launcher,
		ESkyguardPatrolShipSystem::Engines,
		ESkyguardPatrolShipSystem::DroneDeck
	};

	ASkyguardPatrolShipBoss* SpawnShipWithParts(UWorld* World)
	{
		ASkyguardPatrolShipBoss* Ship = World->SpawnActor<ASkyguardPatrolShipBoss>(
			FVector::ZeroVector,
			FRotator::ZeroRotator);
		if (Ship && !Ship->HasActorBegunPlay())
		{
			Ship->DispatchBeginPlay();
		}
		return Ship;
	}

	bool ComponentIsLiveSystem(
		const ASkyguardPatrolShipBoss* Ship,
		const UPrimitiveComponent* Part)
	{
		if (!Ship || !Part)
		{
			return false;
		}
		for (const ESkyguardPatrolShipSystem System : kPriorityOrder)
		{
			if (Ship->IsSystemDead(System))
			{
				continue;
			}
			if (Ship->GetSystemComponent(System) == Part)
			{
				return true;
			}
		}
		return false;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPatrolShipPriorityAfterTwoKillsTest,
	"Skyguard52.Campaign.PatrolShipPriorityAfterTwoKills",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPatrolShipPriorityAfterTwoKillsTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardPatrolShipNearestSystemTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardShipPriorityWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardPatrolShipBoss* Ship = SpawnShipWithParts(World);
	TestNotNull(TEXT("ship"), Ship);
	if (!Ship)
	{
		World->DestroyWorld(false);
		return false;
	}

	TestTrue(
		TEXT("priority order starts at Radar"),
		Ship->GetPriorityLiveSystem() == ESkyguardPatrolShipSystem::Radar);

	Ship->ApplyHitToSystem(ESkyguardPatrolShipSystem::Radar, 500.f);
	TestTrue(
		TEXT("after Radar, priority is Cannon"),
		Ship->GetPriorityLiveSystem() == ESkyguardPatrolShipSystem::Cannon);

	Ship->ApplyHitToSystem(ESkyguardPatrolShipSystem::Cannon, 500.f);
	TestTrue(
		TEXT("after Radar then Cannon, priority is Launcher"),
		Ship->GetPriorityLiveSystem() == ESkyguardPatrolShipSystem::Launcher);
	TestEqual(TEXT("two systems destroyed"), Ship->GetDestroyedSystemCount(), 2);
	TestFalse(TEXT("two kills do not defeat the ship (needs 4)"), Ship->IsDefeated());

	Ship->ApplyHitToSystem(ESkyguardPatrolShipSystem::Launcher, 500.f);
	TestTrue(
		TEXT("after Launcher, priority is Engines"),
		Ship->GetPriorityLiveSystem() == ESkyguardPatrolShipSystem::Engines);

	Ship->ApplyHitToSystem(ESkyguardPatrolShipSystem::Engines, 500.f);
	TestTrue(
		TEXT("after Engines, priority is DroneDeck"),
		Ship->GetPriorityLiveSystem() == ESkyguardPatrolShipSystem::DroneDeck);
	TestEqual(TEXT("four systems destroyed"), Ship->GetDestroyedSystemCount(), 4);
	TestTrue(TEXT("four systems defeat the ship"), Ship->IsDefeated());

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPatrolShipFindNearestLiveSystemTest,
	"Skyguard52.Campaign.PatrolShipFindNearestLiveSystem",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPatrolShipFindNearestLiveSystemTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardPatrolShipNearestSystemTests;

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardShipNearestWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardPatrolShipBoss* Ship = SpawnShipWithParts(World);
	TestNotNull(TEXT("ship"), Ship);
	if (!Ship)
	{
		World->DestroyWorld(false);
		return false;
	}

	UPrimitiveComponent* Radar = Ship->GetSystemComponent(
		ESkyguardPatrolShipSystem::Radar);
	UPrimitiveComponent* Cannon = Ship->GetSystemComponent(
		ESkyguardPatrolShipSystem::Cannon);
	UPrimitiveComponent* Launcher = Ship->GetSystemComponent(
		ESkyguardPatrolShipSystem::Launcher);
	UPrimitiveComponent* Engines = Ship->GetSystemComponent(
		ESkyguardPatrolShipSystem::Engines);
	UPrimitiveComponent* DroneDeck = Ship->GetSystemComponent(
		ESkyguardPatrolShipSystem::DroneDeck);
	TestNotNull(TEXT("radar part"), Radar);
	TestNotNull(TEXT("cannon part"), Cannon);
	TestNotNull(TEXT("launcher part"), Launcher);
	TestNotNull(TEXT("engines part"), Engines);
	TestNotNull(TEXT("drone deck part"), DroneDeck);
	if (!Radar || !Cannon || !Launcher || !Engines || !DroneDeck)
	{
		World->DestroyWorld(false);
		return false;
	}

	UPrimitiveComponent* NearestCannon = Ship->FindNearestLiveSystem(
		Cannon->GetComponentLocation());
	TestTrue(
		TEXT("nearest to live Cannon is the cannon primitive"),
		NearestCannon == Cannon);

	const FVector DeadRadarQuery = Radar->GetComponentLocation();
	Ship->ApplyHitToSystem(ESkyguardPatrolShipSystem::Radar, 500.f);
	UPrimitiveComponent* AfterRadar = Ship->FindNearestLiveSystem(DeadRadarQuery);
	TestNotNull(TEXT("nearest after Radar kill still finds a live system"), AfterRadar);
	TestTrue(
		TEXT("nearest to a dead Radar does not return the radar part"),
		AfterRadar != Radar);
	TestTrue(
		TEXT("nearest after Radar kill is a remaining live system"),
		ComponentIsLiveSystem(Ship, AfterRadar));

	const FVector DeadCannonQuery = Cannon->GetComponentLocation();
	Ship->ApplyHitToSystem(ESkyguardPatrolShipSystem::Cannon, 500.f);
	TestEqual(TEXT("two systems destroyed"), Ship->GetDestroyedSystemCount(), 2);
	TestFalse(TEXT("two kills do not defeat the ship"), Ship->IsDefeated());
	UPrimitiveComponent* AfterTwoKills =
		Ship->FindNearestLiveSystem(DeadCannonQuery);
	TestNotNull(
		TEXT("nearest to the dead Cannon after two kills is not null"),
		AfterTwoKills);
	TestTrue(
		TEXT("nearest to the dead Cannon is not the dead cannon part"),
		AfterTwoKills != Cannon);
	TestTrue(
		TEXT("nearest to the dead Cannon is not the dead radar part"),
		AfterTwoKills != Radar);
	TestTrue(
		TEXT("nearest to the dead Cannon is a remaining live system"),
		ComponentIsLiveSystem(Ship, AfterTwoKills));

	Ship->ApplyHitToSystem(ESkyguardPatrolShipSystem::Launcher, 500.f);
	Ship->ApplyHitToSystem(ESkyguardPatrolShipSystem::Engines, 500.f);
	TestEqual(TEXT("four systems destroyed"), Ship->GetDestroyedSystemCount(), 4);
	TestTrue(TEXT("four systems defeat the ship"), Ship->IsDefeated());
	TestFalse(TEXT("DroneDeck is still live after four kills"), Ship->IsSystemDead(
		ESkyguardPatrolShipSystem::DroneDeck));

	UPrimitiveComponent* AfterFourKills =
		Ship->FindNearestLiveSystem(DeadCannonQuery);
	TestTrue(
		TEXT("four-plus nearest is the remaining live DroneDeck, not nullptr"),
		AfterFourKills == DroneDeck);

	Ship->ApplyHitToSystem(ESkyguardPatrolShipSystem::DroneDeck, 500.f);
	TestFalse(
		TEXT("defeated ship rejects a fifth system kill"),
		Ship->IsSystemDead(ESkyguardPatrolShipSystem::DroneDeck));
	UPrimitiveComponent* AfterRejectedFifth =
		Ship->FindNearestLiveSystem(DeadCannonQuery);
	TestTrue(
		TEXT("all-dead is unreachable; nearest stays the remaining live part"),
		AfterRejectedFifth == DroneDeck);

	World->DestroyWorld(false);
	return true;
}

#endif
