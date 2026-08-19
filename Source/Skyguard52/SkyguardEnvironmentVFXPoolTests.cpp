#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardEnvironmentVFXPoolComponent.h"

#include "Components/SceneComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#include "Misc/AutomationTest.h"
#include "NiagaraSystem.h"

namespace SkyguardEnvironmentVFXPoolTests
{
	class FScopedPoolWorld
	{
	public:
		FScopedPoolWorld()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game,
				false,
				TEXT("SkyguardEnvironmentVFXPoolTestWorld"));
			check(World);
			FWorldContext& Context =
				GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
		}

		~FScopedPoolWorld()
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

	struct FPooledVFXHost
	{
		AActor* Actor = nullptr;
		USkyguardEnvironmentVFXPoolComponent* Pool = nullptr;
	};

	static const ESkyguardEnvironmentVFXType AllEffectTypes[] = {
		ESkyguardEnvironmentVFXType::Smoke,
		ESkyguardEnvironmentVFXType::Fire,
		ESkyguardEnvironmentVFXType::Sparks,
		ESkyguardEnvironmentVFXType::Explosion};

	FPooledVFXHost AttachPoolToTestActor(UWorld* World, const int32 Capacity)
	{
		FPooledVFXHost Host;
		Host.Actor = World->SpawnActor<AActor>();
		if (!Host.Actor)
		{
			return Host;
		}

		USceneComponent* Root =
			NewObject<USceneComponent>(Host.Actor, TEXT("Root"));
		Host.Actor->SetRootComponent(Root);
		Root->RegisterComponent();

		Host.Pool = NewObject<USkyguardEnvironmentVFXPoolComponent>(
			Host.Actor,
			TEXT("EnvironmentVFXPool"));
		if (!Host.Pool)
		{
			return Host;
		}

		Host.Pool->PoolCapacity = Capacity;
		Host.Actor->AddInstanceComponent(Host.Pool);
		Host.Pool->RegisterComponent();
		return Host;
	}

	void EnsureSystemsWithoutImportingAssets(
		USkyguardEnvironmentVFXPoolComponent* Pool)
	{
		auto EnsureSlot = [Pool](
			TObjectPtr<UNiagaraSystem>& Slot,
			const TCHAR* Name)
		{
			if (!Slot)
			{
				Slot = NewObject<UNiagaraSystem>(Pool, Name);
			}
		};

		EnsureSlot(Pool->SmokeSystem, TEXT("TransientSmokeSystem"));
		EnsureSlot(Pool->FireSystem, TEXT("TransientFireSystem"));
		EnsureSlot(Pool->SparksSystem, TEXT("TransientSparksSystem"));
		EnsureSlot(Pool->ExplosionSystem, TEXT("TransientExplosionSystem"));
	}

	void ClearAllSystems(USkyguardEnvironmentVFXPoolComponent* Pool)
	{
		Pool->SmokeSystem = nullptr;
		Pool->FireSystem = nullptr;
		Pool->SparksSystem = nullptr;
		Pool->ExplosionSystem = nullptr;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardEnvironmentVFXPoolCapacityRecycleTest,
	"Skyguard52.Environment.VFXPool.RespectsCapacityAndRecycles",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardEnvironmentVFXPoolCapacityRecycleTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardEnvironmentVFXPoolTests;

	FScopedPoolWorld TestWorld;
	const int32 Capacity = 4;
	const FPooledVFXHost Host =
		AttachPoolToTestActor(TestWorld.Get(), Capacity);
	TestNotNull(TEXT("Test actor spawns"), Host.Actor);
	TestNotNull(TEXT("Environment VFX pool attaches to the test actor"), Host.Pool);
	if (!Host.Actor || !Host.Pool)
	{
		return false;
	}

	TestEqual(
		TEXT("Attached pool uses the requested small capacity"),
		Host.Pool->PoolCapacity,
		Capacity);
	TestEqual(
		TEXT("Fresh pool has allocated nothing"),
		Host.Pool->GetAllocatedPoolSize(),
		0);
	TestEqual(
		TEXT("Fresh pool has no activations"),
		Host.Pool->GetActivationCount(),
		0);

	Host.Pool->DeactivateAllEffects();
	TestEqual(
		TEXT("DeactivateAllEffects is safe before any allocation"),
		Host.Pool->GetAllocatedPoolSize(),
		0);

	EnsureSystemsWithoutImportingAssets(Host.Pool);

	const int32 OverflowRequests = Capacity * 3;
	int32 Accepted = 0;
	for (int32 Index = 0; Index < OverflowRequests; ++Index)
	{
		const ESkyguardEnvironmentVFXType Type =
			AllEffectTypes[Index % UE_ARRAY_COUNT(AllEffectTypes)];
		const bool bAccepted = Host.Pool->ActivatePooledEffect(
			Type,
			FTransform(FVector(Index * 25.f, 0.f, 80.f)));
		Accepted += bAccepted ? 1 : 0;
		TestTrue(
			*FString::Printf(
				TEXT("Pool size stays at or under capacity after request %d"),
				Index + 1),
			Host.Pool->GetAllocatedPoolSize() <= Capacity);
	}

	TestEqual(
		TEXT("Smoke/Fire/Sparks/Explosion activations are accepted"),
		Accepted,
		OverflowRequests);
	TestEqual(
		TEXT("Allocated pool size equals the small capacity"),
		Host.Pool->GetAllocatedPoolSize(),
		Capacity);
	TestEqual(
		TEXT("Activation count advances for every accepted recycle"),
		Host.Pool->GetActivationCount(),
		OverflowRequests);

	const int32 SizeAfterFirstWave = Host.Pool->GetAllocatedPoolSize();
	const int32 CountAfterFirstWave = Host.Pool->GetActivationCount();
	for (int32 Index = 0; Index < Capacity * 2; ++Index)
	{
		TestTrue(
			TEXT("Further Smoke/Fire/Sparks/Explosion calls recycle in place"),
			Host.Pool->ActivatePooledEffect(
				AllEffectTypes[Index % UE_ARRAY_COUNT(AllEffectTypes)],
				FTransform(FVector(0.f, Index * 15.f, 40.f))));
	}

	TestEqual(
		TEXT("A second overflow wave does not grow the allocated pool"),
		Host.Pool->GetAllocatedPoolSize(),
		SizeAfterFirstWave);
	TestEqual(
		TEXT("Activation count keeps advancing after the pool is full"),
		Host.Pool->GetActivationCount(),
		CountAfterFirstWave + Capacity * 2);

	Host.Pool->DeactivateAllEffects();
	TestEqual(
		TEXT("DeactivateAllEffects does not shrink the allocated pool"),
		Host.Pool->GetAllocatedPoolSize(),
		Capacity);
	TestEqual(
		TEXT("DeactivateAllEffects does not rewind activation telemetry"),
		Host.Pool->GetActivationCount(),
		CountAfterFirstWave + Capacity * 2);

	Host.Pool->DeactivateAllEffects();
	TestEqual(
		TEXT("A second DeactivateAllEffects call stays safe"),
		Host.Pool->GetAllocatedPoolSize(),
		Capacity);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardEnvironmentVFXPoolMissingNiagaraNullSafeTest,
	"Skyguard52.Environment.VFXPool.MissingNiagaraSystemsAreNullSafe",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardEnvironmentVFXPoolMissingNiagaraNullSafeTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardEnvironmentVFXPoolTests;

	FScopedPoolWorld TestWorld;
	const int32 Capacity = 4;
	const FPooledVFXHost Host =
		AttachPoolToTestActor(TestWorld.Get(), Capacity);
	TestNotNull(TEXT("Null-safe test actor spawns"), Host.Actor);
	TestNotNull(TEXT("Null-safe environment VFX pool attaches"), Host.Pool);
	if (!Host.Actor || !Host.Pool)
	{
		return false;
	}

	ClearAllSystems(Host.Pool);
	Host.Pool->DeactivateAllEffects();

	int32 Rejected = 0;
	const int32 NullRequests = Capacity * 3;
	for (int32 Index = 0; Index < NullRequests; ++Index)
	{
		const ESkyguardEnvironmentVFXType Type =
			AllEffectTypes[Index % UE_ARRAY_COUNT(AllEffectTypes)];
		const bool bAccepted = Host.Pool->ActivatePooledEffect(
			Type,
			FTransform(FVector(Index * 10.f, 20.f, 30.f)));
		Rejected += bAccepted ? 0 : 1;
		TestTrue(
			*FString::Printf(
				TEXT("Missing Niagara does not grow the pool past capacity after request %d"),
				Index + 1),
			Host.Pool->GetAllocatedPoolSize() <= Capacity);
	}

	TestEqual(
		TEXT("Missing Smoke/Fire/Sparks/Explosion systems are rejected"),
		Rejected,
		NullRequests);
	TestEqual(
		TEXT("Null-safe activations still preallocate up to capacity"),
		Host.Pool->GetAllocatedPoolSize(),
		Capacity);
	TestEqual(
		TEXT("Rejected missing-system calls do not advance activation count"),
		Host.Pool->GetActivationCount(),
		0);

	Host.Pool->DeactivateAllEffects();
	TestEqual(
		TEXT("DeactivateAllEffects is safe with missing Niagara systems"),
		Host.Pool->GetActivationCount(),
		0);
	TestTrue(
		TEXT("DeactivateAllEffects leaves the allocated pool at capacity"),
		Host.Pool->GetAllocatedPoolSize() <= Capacity);

	TestFalse(
		TEXT("A later missing-system Smoke call stays null-safe"),
		Host.Pool->ActivatePooledEffect(
			ESkyguardEnvironmentVFXType::Smoke,
			FTransform::Identity));
	TestFalse(
		TEXT("A later missing-system Fire call stays null-safe"),
		Host.Pool->ActivatePooledEffect(
			ESkyguardEnvironmentVFXType::Fire,
			FTransform::Identity));
	TestFalse(
		TEXT("A later missing-system Sparks call stays null-safe"),
		Host.Pool->ActivatePooledEffect(
			ESkyguardEnvironmentVFXType::Sparks,
			FTransform::Identity));
	TestFalse(
		TEXT("A later missing-system Explosion call stays null-safe"),
		Host.Pool->ActivatePooledEffect(
			ESkyguardEnvironmentVFXType::Explosion,
			FTransform::Identity));
	TestEqual(
		TEXT("Follow-up missing-system calls still do not advance activation count"),
		Host.Pool->GetActivationCount(),
		0);
	return true;
}

#endif
