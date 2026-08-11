#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCoastalEnvironmentDirector.h"
#include "SkyguardEnvironmentVFXPoolComponent.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "HAL/PlatformTime.h"
#include "Misc/AutomationTest.h"

namespace SkyguardCoastalEnvironmentDirectorTests
{
	class FScopedEnvironmentWorld
	{
	public:
		FScopedEnvironmentWorld()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game,
				false,
				TEXT("SkyguardCoastalEnvironmentAutomationWorld"));
			check(World);
			FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
		}

		~FScopedEnvironmentWorld()
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
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCoastalEnvironmentDirectorTest,
	"Skyguard52.Environment.Mission01.CoastalDirectorStructureAndBudget",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCoastalEnvironmentDirectorTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardCoastalEnvironmentDirectorTests;

	FScopedEnvironmentWorld TestWorld;
	ASkyguardCoastalEnvironmentDirector* Director =
		TestWorld.Get()->SpawnActor<ASkyguardCoastalEnvironmentDirector>();
	TestNotNull(TEXT("Coastal environment director spawns"), Director);
	if (!Director)
	{
		return false;
	}

	static const FName ExpectedCapabilityTags[] = {
		TEXT("Skyguard.Environment.Water"),
		TEXT("Skyguard.Environment.Landmass"),
		TEXT("Skyguard.Environment.PCG"),
		TEXT("Skyguard.Environment.Atmosphere"),
		TEXT("Skyguard.Environment.Cloud"),
		TEXT("Skyguard.Environment.Fog"),
		TEXT("Skyguard.Environment.Wind")
	};
	for (const FName Tag : ExpectedCapabilityTags)
	{
		AActor* CapabilityActor = TestWorld.Get()->SpawnActor<AActor>();
		TestNotNull(FString::Printf(TEXT("Capability actor %s spawns"), *Tag.ToString()), CapabilityActor);
		if (CapabilityActor)
		{
			CapabilityActor->Tags.Add(Tag);
		}
	}

	TestWorld.Get()->BeginPlay();
	if (!Director->HasActorBegunPlay())
	{
		Director->DispatchBeginPlay();
	}
	Director->RefreshCapabilityBindings();

	TestEqual(TEXT("All seven environment capability tags bind"), Director->GetReadiness().BoundCapabilityCount, 7);
	TestEqual(TEXT("VFX pool preallocates its fixed capacity"), Director->VFXPool->GetAllocatedPoolSize(), Director->VFXPool->PoolCapacity);
	TestTrue(TEXT("Vegetation is excluded from the flight corridor"), Director->IsVegetationOutsideRouteCorridor());

	Director->ApplyQuality(ESkyguardEnvironmentQuality::Low);
	const int32 LowTrees = Director->TreeInstances->GetInstanceCount();
	const int32 LowShrubs = Director->ShrubInstances->GetInstanceCount();
	TestTrue(TEXT("Low quality keeps a nonzero tree layer"), LowTrees > 0);
	TestTrue(TEXT("Low quality keeps a nonzero shrub layer"), LowShrubs > 0);

	Director->ApplyQuality(ESkyguardEnvironmentQuality::Epic);
	const int32 EpicTrees = Director->TreeInstances->GetInstanceCount();
	const int32 EpicShrubs = Director->ShrubInstances->GetInstanceCount();
	TestTrue(TEXT("Epic quality raises the tree budget"), EpicTrees > LowTrees);
	TestTrue(TEXT("Epic quality raises the shrub budget"), EpicShrubs > LowShrubs);
	TestTrue(TEXT("Tree count stays inside the hard cap"), EpicTrees <= 1024);
	TestTrue(TEXT("Shrub count stays inside the hard cap"), EpicShrubs <= 2048);
	TestTrue(TEXT("Epic vegetation remains route safe"), Director->IsVegetationOutsideRouteCorridor());

	FTransform FirstTreeBefore;
	FTransform FirstTreeAfter;
	const bool bHadTreeBefore =
		Director->TreeInstances->GetInstanceTransform(0, FirstTreeBefore, false);
	const double RebuildStart = FPlatformTime::Seconds();
	Director->RebuildDeterministicVegetation();
	const double RebuildMilliseconds =
		(FPlatformTime::Seconds() - RebuildStart) * 1000.0;
	const bool bHadTreeAfter =
		Director->TreeInstances->GetInstanceTransform(0, FirstTreeAfter, false);
	TestTrue(TEXT("Deterministic vegetation produces a first tree"), bHadTreeBefore && bHadTreeAfter);
	TestTrue(TEXT("Same seed reproduces the same first tree"), FirstTreeBefore.Equals(FirstTreeAfter, 0.01f));
	AddInfo(FString::Printf(
		TEXT("Epic deterministic vegetation rebuild: %.3f ms for %d instances"),
		RebuildMilliseconds,
		Director->TreeInstances->GetInstanceCount() +
			Director->ShrubInstances->GetInstanceCount()));

	const int32 PoolSizeBefore = Director->VFXPool->GetAllocatedPoolSize();
	const double VFXStart = FPlatformTime::Seconds();
	bool bAllEffectsAccepted = true;
	for (int32 Index = 0; Index < 100; ++Index)
	{
		const ESkyguardEnvironmentVFXType Type =
			static_cast<ESkyguardEnvironmentVFXType>(Index % 4);
		bAllEffectsAccepted &=
			Director->VFXPool->ActivatePooledEffect(
				Type,
				FTransform(FVector(Index * 10.f, 0.f, 100.f)));
	}
	const double VFXMilliseconds =
		(FPlatformTime::Seconds() - VFXStart) * 1000.0;
	TestTrue(TEXT("All four configured Niagara effect types activate"), bAllEffectsAccepted);
	TestEqual(TEXT("One hundred activations do not grow the pool"), Director->VFXPool->GetAllocatedPoolSize(), PoolSizeBefore);
	TestEqual(TEXT("Activation telemetry records all requests"), Director->VFXPool->GetActivationCount(), 100);
	AddInfo(FString::Printf(
		TEXT("One hundred pooled Niagara activations: %.3f ms, fixed pool %d"),
		VFXMilliseconds,
		PoolSizeBefore));

	return true;
}

#endif
