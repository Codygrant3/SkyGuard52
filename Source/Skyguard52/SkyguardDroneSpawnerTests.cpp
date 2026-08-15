#include "Misc/AutomationTest.h"

#include "SkyguardDrone.h"
#include "SkyguardDroneSpawner.h"
#include "Engine/World.h"
#include "EngineUtils.h"

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardDroneSpawnerActiveCapTest,
	"Skyguard52.Combat.Spawner.RespectsMaxActiveDrones",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardDroneSpawnerActiveCapTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardSpawnerCapWorld"));
	TestNotNull(TEXT("Automation world is created"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardDroneSpawner* Spawner = World->SpawnActor<ASkyguardDroneSpawner>(
		ASkyguardDroneSpawner::StaticClass(),
		FVector::ZeroVector,
		FRotator::ZeroRotator);
	TestNotNull(TEXT("Spawner spawns"), Spawner);
	if (!Spawner)
	{
		World->DestroyWorld(false);
		return false;
	}
	TestTrue(TEXT("Spawning is enabled by default"), Spawner->bSpawningEnabled);
	TestEqual(TEXT("Default spawn interval is tuned"), Spawner->SpawnInterval, 1.85f);
	TestEqual(TEXT("Default active cap is tuned"), Spawner->MaxActiveDrones, 12);
	TestEqual(TEXT("Default heavy lane modulo is tuned"), Spawner->HeavyLaneModulo, 4);
	TestEqual(TEXT("Default light minimum speed is tuned"), Spawner->LightSpeedMin, 1300.f);
	TestEqual(TEXT("Default light maximum speed is tuned"), Spawner->LightSpeedMax, 1750.f);
	TestEqual(TEXT("Default heavy speed is tuned"), Spawner->HeavyCruiseSpeed, 1150.f);

	Spawner->DispatchBeginPlay();
	Spawner->MaxActiveDrones = 2;
	Spawner->SpawnInterval = 0.01f;

	for (int32 Index = 0; Index < 20; ++Index)
	{
		Spawner->Tick(1.f);
	}

	int32 AliveCount = 0;
	for (TActorIterator<ASkyguardDrone> It(World); It; ++It)
	{
		if (IsValid(*It) && !It->IsActorBeingDestroyed())
		{
			++AliveCount;
		}
	}

	TestTrue(
		TEXT("Spawner never exceeds MaxActiveDrones"),
		AliveCount <= Spawner->MaxActiveDrones);

	Spawner->SetSpawningEnabled(false);
	const int32 AliveBeforeDisabledTick = AliveCount;
	for (int32 Index = 0; Index < 5; ++Index)
	{
		Spawner->Tick(10.f);
	}
	AliveCount = 0;
	for (TActorIterator<ASkyguardDrone> It(World); It; ++It)
	{
		if (IsValid(*It) && !It->IsActorBeingDestroyed())
		{
			++AliveCount;
		}
	}
	TestEqual(
		TEXT("Disabled spawning does not add drones"),
		AliveCount,
		AliveBeforeDisabledTick);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardGroundArmorFollowsRoadAndDiesToBallisticsTest,
	"Skyguard52.Combat.GroundArmor.FollowsRoadAndDiesToBallistics",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardGroundArmorFollowsRoadAndDiesToBallisticsTest::RunTest(
	const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game,
		false,
		TEXT("SkyguardConvoyDriveWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardDrone* Truck = World->SpawnActor<ASkyguardDrone>(
		FVector(0.f, 0.f, 90.f),
		FRotator::ZeroRotator);
	TestNotNull(TEXT("truck"), Truck);
	if (!Truck)
	{
		World->DestroyWorld(false);
		return false;
	}

	const TArray<FVector> Path = {
		FVector(0.f, 0.f, 90.f),
		FVector(2000.f, 0.f, 90.f),
		FVector(2000.f, 2000.f, 90.f)
	};
	Truck->ConfigureRoadConvoy(Path, 0, TEXT("Vehicle.Truck"));
	TestTrue(TEXT("truck is road-bound"), Truck->IsFollowingRoad());
	TestTrue(TEXT("truck is missile food"), Truck->IsMissileLockEligible());
	TestEqual(TEXT("starts on first waypoint"), Truck->GetRoadWaypointIndex(), 0);

	for (int32 Step = 0; Step < 40; ++Step)
	{
		Truck->Tick(0.25f);
	}
	TestTrue(
		TEXT("truck advanced along the road"),
		Truck->GetActorLocation().X > 400.f);
	TestFalse(TEXT("truck is still alive"), Truck->IsDestroyed());

	Truck->ApplyBallisticHit(80.f, Truck->GetActorLocation(), FVector::ForwardVector);
	TestFalse(TEXT("one rocket does not wreck armor"), Truck->IsDestroyed());
	Truck->ApplyBallisticHit(160.f, Truck->GetActorLocation(), FVector::ForwardVector);
	TestTrue(TEXT("hellfire-class hit finishes the wreck"), Truck->IsDestroyed());

	World->DestroyWorld(false);
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
