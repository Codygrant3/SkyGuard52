#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCombatVFX.h"
#include "SkyguardCombatVFXPoolSubsystem.h"

#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Misc/AutomationTest.h"

namespace SkyguardCombatVFXTests
{
	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game,
				false,
				TEXT("SkyguardCombatVFXPoolTestWorld"));
			check(World);
			FWorldContext& Context =
				GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
		}

		~FWorldScope()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(false);
			}
		}

		UWorld* Get() const { return World; }

	private:
		UWorld* World = nullptr;
	};

	int32 CountActors(UWorld* World)
	{
		int32 Count = 0;
		for (TActorIterator<AActor> Iterator(World); Iterator; ++Iterator)
		{
			++Count;
		}
		return Count;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCombatVFXFixedPoolTest,
	"Skyguard52.Combat.VFX.FixedPool.NoCombatPathAllocationOrActorSpawns",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCombatVFXFixedPoolTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCombatVFXTests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	USkyguardCombatVFXPoolSubsystem* Pool =
		World->GetSubsystem<USkyguardCombatVFXPoolSubsystem>();
	TestNotNull(TEXT("Combat VFX pool subsystem exists in a game world"), Pool);
	if (!Pool)
	{
		return false;
	}

	TestTrue(TEXT("Assets and fixed pool are prepared before combat"), Pool->IsPrewarmed());
	TestEqual(
		TEXT("The pool has exactly the governed fixed capacity"),
		Pool->GetAllocatedCount(),
		USkyguardCombatVFXPoolSubsystem::PoolCapacity);
	TestEqual(TEXT("Fresh pool starts with no active effects"), Pool->GetActiveCount(), 0);

	const int32 ActorsBefore = CountActors(World);
	const int32 AllocatedBefore = Pool->GetAllocatedCount();
	const int32 ActivationsBefore = Pool->GetActivationCount();
	const FVector Origin(100.f, 200.f, 300.f);

	USkyguardCombatVFX::SpawnMuzzleFlash(World, Origin, FVector::ForwardVector);
	USkyguardCombatVFX::SpawnGunSmoke(World, Origin, FVector::ForwardVector);
	USkyguardCombatVFX::SpawnHitSparks(World, Origin, FVector::UpVector);
	USkyguardCombatVFX::SpawnIglaLaunch(World, Origin, FVector::ForwardVector);
	USkyguardCombatVFX::SpawnMissileTrail(
		World, Origin, Origin + FVector(1200.f, 0.f, 0.f));
	USkyguardCombatVFX::SpawnTracer(
		World, Origin, Origin + FVector(2000.f, 0.f, 0.f));
	for (int32 Index = 0; Index < 8; ++Index)
	{
		USkyguardCombatVFX::SpawnExplosion(
			World,
			Origin + FVector(static_cast<float>(Index) * 100.f, 0.f, 0.f),
			1.f);
	}

	TestEqual(
		TEXT("Combat emissions do not grow the component pool"),
		Pool->GetAllocatedCount(),
		AllocatedBefore);
	TestEqual(
		TEXT("Combat emissions do not spawn transient actors"),
		CountActors(World),
		ActorsBefore);
	TestTrue(
		TEXT("All governed effects exercised the prepared pool"),
		Pool->GetActivationCount() > ActivationsBefore);
	TestTrue(
		TEXT("Exhaustion recycles the earliest slot without allocation"),
		Pool->GetRecycleCount() > 0);
	TestTrue(
		TEXT("Active effects never exceed the fixed capacity"),
		Pool->GetActiveCount() <=
			USkyguardCombatVFXPoolSubsystem::PoolCapacity);
	return true;
}

#endif
