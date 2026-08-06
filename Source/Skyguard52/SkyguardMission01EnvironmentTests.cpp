#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission01EnvironmentDirector.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "HAL/PlatformTime.h"
#include "Misc/AutomationTest.h"
#include "PCGComponent.h"

namespace
{
	class FScopedMission01EnvironmentWorld
	{
	public:
		FScopedMission01EnvironmentWorld()
		{
			World = UWorld::CreateWorld(EWorldType::Game, false, TEXT("SkyguardMission01EnvironmentTestWorld"));
			check(World);
			FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
		}
		~FScopedMission01EnvironmentWorld()
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
	FSkyguardMission01EnvironmentStructureTest,
	"Skyguard52.Environment.Mission01Production.StructureAndRouteExclusion",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission01EnvironmentStructureTest::RunTest(const FString& Parameters)
{
	FScopedMission01EnvironmentWorld World;
	ASkyguardMission01EnvironmentDirector* Director =
		World.Get()->SpawnActor<ASkyguardMission01EnvironmentDirector>();
	TestNotNull(TEXT("Production environment director spawns"), Director);
	if (!Director)
	{
		return false;
	}
	Director->RebuildProductionLayout();
	const FSkyguardMission01EnvironmentReadiness& State = Director->GetReadiness();
	TestEqual(TEXT("Six ocean districts cover the route"), State.OceanTileCount, 6);
	TestEqual(TEXT("Six beach districts cover the route"), State.BeachTileCount, 6);
	TestEqual(TEXT("Six land districts cover the route"), State.LandTileCount, 6);
	TestTrue(TEXT("Coastline districts have no gaps"), State.bContinuousCoastline);
	TestTrue(TEXT("Route exclusion spans the authored flight corridor"), State.bRouteExclusionValid);
	TestFalse(TEXT("Flight corridor cannot receive PCG scatter"),
		Director->IsPointAllowedForPCG(FVector(20000.f, 0.f, 0.f)));
	TestFalse(TEXT("Beach remains outside vegetation scatter"),
		Director->IsPointAllowedForPCG(FVector(20000.f, 6000.f, 0.f)));
	TestTrue(TEXT("Inland terrain accepts PCG scatter"),
		Director->IsPointAllowedForPCG(FVector(20000.f, 12000.f, 0.f)));
	TestFalse(TEXT("Scatter cannot escape the mission route"),
		Director->IsPointAllowedForPCG(FVector(50000.f, 12000.f, 0.f)));
	Director->SetUseAuthoredLandscapeSurfaceForValidation(true);
	TestEqual(TEXT("Landscape validation removes legacy inland slabs"),
		Director->GetReadiness().LandTileCount, 0);
	TestTrue(TEXT("Landscape validation reports its inland surface exposed"),
		Director->GetReadiness().bAuthoredLandscapeSurfaceExposed);
	TestTrue(TEXT("Ocean and beach continuity survives slab removal"),
		Director->HasContinuousCoastline());
	Director->SetUseAuthoredLandscapeSurfaceForValidation(false);
	TestEqual(TEXT("Default production layout restores six inland districts"),
		Director->GetReadiness().LandTileCount, 6);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission01EnvironmentPerformanceTest,
	"Skyguard52.Environment.Mission01Production.BoundedScatterQueryCost",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission01EnvironmentPerformanceTest::RunTest(const FString& Parameters)
{
	FScopedMission01EnvironmentWorld World;
	ASkyguardMission01EnvironmentDirector* Director =
		World.Get()->SpawnActor<ASkyguardMission01EnvironmentDirector>();
	if (!Director)
	{
		AddError(TEXT("Production environment director did not spawn"));
		return false;
	}
	const double Start = FPlatformTime::Seconds();
	int32 Accepted = 0;
	for (int32 Index = 0; Index < 100000; ++Index)
	{
		const float X = static_cast<float>(Index % 50000);
		const float Y = static_cast<float>((Index * 37) % 24000) - 4000.f;
		Accepted += Director->IsPointAllowedForPCG(FVector(X, Y, 0.f)) ? 1 : 0;
	}
	const double ElapsedMs = (FPlatformTime::Seconds() - Start) * 1000.0;
	UE_LOG(LogTemp, Display, TEXT("[SkyguardPhase4] 100000 PCG exclusion queries: %.3f ms; accepted=%d"), ElapsedMs, Accepted);
	TestTrue(TEXT("Scatter query produces a non-empty, bounded inland set"), Accepted > 0 && Accepted < 100000);
	TestTrue(TEXT("One hundred thousand exclusion queries remain under broad CPU guard"), ElapsedMs < 100.0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission01AuthoredEnvironmentFailClosedTest,
	"Skyguard52.Environment.Mission01Production.AuthoredPCGFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission01AuthoredEnvironmentFailClosedTest::RunTest(
	const FString& Parameters)
{
	FScopedMission01EnvironmentWorld World;
	ASkyguardMission01EnvironmentDirector* Director =
		World.Get()->SpawnActor<ASkyguardMission01EnvironmentDirector>();
	TestNotNull(TEXT("Production environment director spawns"), Director);
	if (!Director)
	{
		return false;
	}

	Director->RebuildProductionLayout();
	Director->RefreshAuthoredEnvironmentBindings();
	const FSkyguardMission01EnvironmentReadiness& State =
		Director->GetReadiness();

	TestNotNull(TEXT("Director owns a real PCG component"),
		Director->InlandVegetationPCG.Get());
	TestTrue(TEXT("Authored inclusion and exclusion bounds are tagged"),
		State.bPCGBoundsTagged);
	TestFalse(TEXT("No imported Landscape is never production-ready"),
		State.bProductionLandscapeBound);
	// The governed graph is now a serialized project asset and is expected to
	// resolve even in this transient test world. The absent world Landscape,
	// empty licensed mesh selector, and explicit authorization lock must still
	// keep generation and structural readiness fail-closed.
	TestTrue(TEXT("Serialized governed graph resolves in the project"),
		State.bAuthoredPCGGraphBound);
	TestFalse(TEXT("Missing authoring inputs keep generation fail-closed"),
		State.bReadyForAuthoredPCGGeneration);
	TestFalse(TEXT("Missing authoring inputs are not structurally ready"),
		State.bAuthoredPCGStructureReady);
	TestFalse(TEXT("Licensed vegetation is not implicitly approved"),
		State.bLicensedVegetationApproved);
	TestFalse(TEXT("Generation requires explicit authorization"),
		State.bPCGGenerationAuthorized);
	TestFalse(TEXT("Fail-closed PCG component remains inactive"),
		Director->InlandVegetationPCG
		&& Director->InlandVegetationPCG->bActivated);
	return true;
}

#endif
