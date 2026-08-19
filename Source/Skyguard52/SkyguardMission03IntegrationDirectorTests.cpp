#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission03IntegrationDirector.h"

#include "SkyguardMissionDefinition.h"
#include "SkyguardObjectiveRuntime.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardMission03IntegrationTests.cpp.
// Isolated convoy-route public API: nullptr runtime actors, no Yak/Gunner/
// RoadHunter spawn, no rifle/Igla hits, no day-beat kit edits.

namespace SkyguardMission03IntegrationDirectorTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M03_ConvoyEscort.DA_Mission_M03_ConvoyEscort");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission03DirectorTestWorld"));
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

	USkyguardMissionDefinition* TryLoadMission()
	{
		return LoadObject<USkyguardMissionDefinition>(
			nullptr, MissionAssetPath);
	}

	ASkyguardMission03IntegrationDirector* SpawnBoundDirector(UWorld* World)
	{
		ASkyguardMission03IntegrationDirector* Director =
			World->SpawnActor<ASkyguardMission03IntegrationDirector>();
		if (!Director)
		{
			return nullptr;
		}
		Director->bAutoInitialize = false;
		Director->bAllowBoundedActorSpawning = false;
		Director->BindRuntimeActors(nullptr, nullptr, nullptr, nullptr);
		return Director;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission03DirectorMissionIdAndNullRuntimeTest,
	"Skyguard52.Mission03.Director.MissionIdAndNullRuntimeConvoyRoute",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission03DirectorMissionIdAndNullRuntimeTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission03IntegrationDirectorTests;

	TestEqual(
		TEXT("GetMissionId is M03_ConvoyEscort"),
		ASkyguardMission03IntegrationDirector::GetMissionId(),
		FName(TEXT("M03_ConvoyEscort")));

	TArray<FText> NullContractErrors;
	TestFalse(
		TEXT("ValidateMissionContract rejects a null definition"),
		ASkyguardMission03IntegrationDirector::ValidateMissionContract(
			nullptr, NullContractErrors));
	TestTrue(
		TEXT("Null contract reports at least one error"),
		NullContractErrors.Num() > 0);

	FWorldScope Scope;
	ASkyguardMission03IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(TEXT("Director spawns without Yak, Gunner, or RoadHunter"), Director);
	if (!Director)
	{
		return false;
	}

	TestEqual(
		TEXT("Unconfigured convoy route stays Holding"),
		Director->GetConvoyRouteState(),
		ESkyguardConvoyRouteState::Holding);
	TestEqual(
		TEXT("Unconfigured convoy route alpha is zero"),
		Director->GetConvoyRouteAlpha(),
		0.f);
	TestTrue(
		TEXT("Unconfigured convoy world location is origin"),
		Director->GetConvoyWorldLocation().Equals(FVector::ZeroVector));
	TestFalse(
		TEXT("AdvanceConvoyByDistance is fail-closed before configure"),
		Director->AdvanceConvoyByDistance(1000000.f));
	TestEqual(
		TEXT("Failed advance leaves the convoy Holding"),
		Director->GetConvoyRouteState(),
		ESkyguardConvoyRouteState::Holding);
	TestEqual(
		TEXT("Failed advance leaves route alpha at zero"),
		Director->GetConvoyRouteAlpha(),
		0.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission03DirectorConfiguredConvoyRouteAndDamageTest,
	"Skyguard52.Mission03.Director.ConfiguredConvoyRouteAndDamage",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission03DirectorConfiguredConvoyRouteAndDamageTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission03IntegrationDirectorTests;

	USkyguardMissionDefinition* Mission = TryLoadMission();
	if (!Mission)
	{
		AddWarning(TEXT(
			"Mission 3 DataAsset unavailable; skipped configure, "
			"convoy-route, and convoy-damage tests. Null-runtime tests still passed."));
		return true;
	}

	TArray<FText> Errors;
	TestTrue(
		TEXT("Loaded Mission 3 contract validates"),
		ASkyguardMission03IntegrationDirector::ValidateMissionContract(
			Mission, Errors));
	TestEqual(TEXT("Loaded contract emits no errors"), Errors.Num(), 0);

	FWorldScope Scope;
	UWorld* World = Scope.Get();
	ASkyguardMission03IntegrationDirector* RouteDirector =
		SpawnBoundDirector(World);
	ASkyguardMission03IntegrationDirector* DamageDirector =
		SpawnBoundDirector(World);
	TestNotNull(TEXT("Route director binds nullptr runtime actors"), RouteDirector);
	TestNotNull(TEXT("Damage director binds nullptr runtime actors"), DamageDirector);
	if (!RouteDirector || !DamageDirector)
	{
		return false;
	}

	TestTrue(
		TEXT("Route director configures from loaded mission"),
		RouteDirector->ConfigureMissionDefinition(Mission));
	TestEqual(
		TEXT("ConfigureMissionDefinition resets the convoy to Holding"),
		RouteDirector->GetConvoyRouteState(),
		ESkyguardConvoyRouteState::Holding);
	TestEqual(
		TEXT("Configured convoy alpha starts at zero"),
		RouteDirector->GetConvoyRouteAlpha(),
		0.f);
	TestTrue(
		TEXT("Configured convoy location stays origin without a bound spline"),
		RouteDirector->GetConvoyWorldLocation().Equals(FVector::ZeroVector));
	// AdvanceConvoyByDistance requires ConvoyRouteState==Advancing and a bound
	// FlightRouteSpline (GetConvoyRouteLength). BindRuntimeActors(nullptr,...)
	// leaves route length 0, so the public API stays fail-closed. TunnelReached
	// is therefore unreachable on this isolated nullptr-runtime path.
	TestFalse(
		TEXT("AdvanceConvoyByDistance stays fail-closed while Holding"),
		RouteDirector->AdvanceConvoyByDistance(1000000.f));
	TestEqual(
		TEXT("Holding advance leaves route alpha at zero"),
		RouteDirector->GetConvoyRouteAlpha(),
		0.f);
	TestTrue(
		TEXT("First wave starts after configure"),
		RouteDirector->StartNextWave());
	TestEqual(
		TEXT("StartNextWave promotes a Holding convoy to Advancing"),
		RouteDirector->GetConvoyRouteState(),
		ESkyguardConvoyRouteState::Advancing);
	TestFalse(
		TEXT("AdvanceConvoyByDistance stays fail-closed without a bound spline"),
		RouteDirector->AdvanceConvoyByDistance(1000000.f));
	TestEqual(
		TEXT("Spline-less advance leaves the convoy Advancing"),
		RouteDirector->GetConvoyRouteState(),
		ESkyguardConvoyRouteState::Advancing);
	TestEqual(
		TEXT("Spline-less advance leaves route alpha at zero"),
		RouteDirector->GetConvoyRouteAlpha(),
		0.f);
	TestTrue(
		TEXT("Spline-less advance leaves world location at origin"),
		RouteDirector->GetConvoyWorldLocation().Equals(FVector::ZeroVector));

	TestTrue(
		TEXT("Damage director configures from loaded mission"),
		DamageDirector->ConfigureMissionDefinition(Mission));
	const int32 StartingIntegrity = DamageDirector->GetConvoyIntegrity();
	TestEqual(
		TEXT("Configured convoy integrity matches MaximumConvoyIntegrity"),
		StartingIntegrity,
		DamageDirector->MaximumConvoyIntegrity);
	TestTrue(
		TEXT("Partial convoy damage applies"),
		DamageDirector->NotifyConvoyDamage(11));
	TestEqual(
		TEXT("Partial convoy damage reduces integrity"),
		DamageDirector->GetConvoyIntegrity(),
		StartingIntegrity - 11);
	TestEqual(
		TEXT("Partial damage leaves the convoy Holding"),
		DamageDirector->GetConvoyRouteState(),
		ESkyguardConvoyRouteState::Holding);
	TestTrue(
		TEXT("MaximumConvoyIntegrity damage is accepted"),
		DamageDirector->NotifyConvoyDamage(
			DamageDirector->MaximumConvoyIntegrity));
	TestEqual(
		TEXT("Destroyed convoy integrity is zero"),
		DamageDirector->GetConvoyIntegrity(),
		0);
	TestEqual(
		TEXT("Convoy route records destruction"),
		DamageDirector->GetConvoyRouteState(),
		ESkyguardConvoyRouteState::Destroyed);
	TestEqual(
		TEXT("Convoy loss fails the mission"),
		DamageDirector->GetWaveState(),
		ESkyguardMission03WaveState::Failed);
	USkyguardObjectiveRuntime* Objectives =
		DamageDirector->GetObjectiveRuntime();
	TestNotNull(TEXT("Local objective runtime exists after configure"), Objectives);
	if (Objectives)
	{
		TestTrue(
			TEXT("Protection objective records terminal failure"),
			Objectives->HasTerminalFailure());
	}
	TestFalse(
		TEXT("Destroyed convoy rejects further advance"),
		DamageDirector->AdvanceConvoyByDistance(1000.f));
	return true;
}

#endif
