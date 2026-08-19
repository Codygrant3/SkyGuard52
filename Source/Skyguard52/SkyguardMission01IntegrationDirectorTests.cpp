#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission01IntegrationDirector.h"

#include "SkyguardMissionDefinition.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardMission01IntegrationTests.cpp.
// Public director API only: nullptr Yak/Gunner/Pathfinder, no actor spawn, no Igla hits.

namespace SkyguardMission01IntegrationDirectorTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M01_CoastalIntercept.DA_Mission_M01_CoastalIntercept");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission01DirectorTestWorld"));
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

	ASkyguardMission01IntegrationDirector* SpawnBoundDirector(UWorld* World)
	{
		ASkyguardMission01IntegrationDirector* Director =
			World->SpawnActor<ASkyguardMission01IntegrationDirector>();
		if (!Director)
		{
			return nullptr;
		}
		Director->bAutoInitialize = false;
		Director->bAllowBoundedActorSpawning = false;
		Director->BindRuntimeActors(nullptr, nullptr, nullptr);
		return Director;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission01DirectorMissionIdAndNullRuntimeTest,
	"Skyguard52.Mission01.Director.MissionIdAndNullRuntimeBind",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission01DirectorMissionIdAndNullRuntimeTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission01IntegrationDirectorTests;

	TestEqual(
		TEXT("GetMissionId is M01_CoastalIntercept"),
		ASkyguardMission01IntegrationDirector::GetMissionId(),
		FName(TEXT("M01_CoastalIntercept")));

	TArray<FText> NullContractErrors;
	TestFalse(
		TEXT("ValidateMissionContract rejects a null definition"),
		ASkyguardMission01IntegrationDirector::ValidateMissionContract(
			nullptr, NullContractErrors));
	TestTrue(
		TEXT("Null contract reports at least one error"),
		NullContractErrors.Num() > 0);

	FWorldScope Scope;
	ASkyguardMission01IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(TEXT("Director spawns without Yak, Gunner, or Pathfinder"), Director);
	if (!Director)
	{
		return false;
	}

	TestNull(TEXT("BindRuntimeActors(nullptr) does not attach a Yak"), Director->GetAircraft());
	TestNull(TEXT("BindRuntimeActors(nullptr) does not attach a Gunner"), Director->GetGunner());
	TestNull(TEXT("BindRuntimeActors(nullptr) does not attach a Pathfinder"), Director->GetPathfinder());
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission01DirectorCampaignAssetContractTest,
	"Skyguard52.Mission01.Director.CampaignAssetContractAndConfigure",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission01DirectorCampaignAssetContractTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission01IntegrationDirectorTests;

	USkyguardMissionDefinition* Mission = TryLoadMission();
	if (!Mission)
	{
		AddWarning(TEXT(
			"Mission 01 DataAsset unavailable; skipped contract and "
			"ConfigureMissionDefinition tests."));
		return true;
	}

	TArray<FText> Errors;
	TestTrue(
		TEXT("Loaded Mission 01 contract validates"),
		ASkyguardMission01IntegrationDirector::ValidateMissionContract(
			Mission, Errors));
	TestEqual(TEXT("Loaded contract emits no errors"), Errors.Num(), 0);

	FWorldScope Scope;
	ASkyguardMission01IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(TEXT("Director binds nullptr Yak/Gunner/Pathfinder"), Director);
	if (!Director)
	{
		return false;
	}

	TestTrue(
		TEXT("Director configures from loaded Mission 01"),
		Director->ConfigureMissionDefinition(Mission));
	TestNull(TEXT("Configure does not spawn a Yak"), Director->GetAircraft());
	TestNull(TEXT("Configure does not spawn a Gunner"), Director->GetGunner());
	TestNull(TEXT("Configure does not spawn a Pathfinder"), Director->GetPathfinder());
	return true;
}

#endif
