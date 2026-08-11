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

	World->DestroyWorld(false);
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
