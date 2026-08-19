#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission10IntegrationDirector.h"

#include "SkyguardMissionDefinition.h"
#include "SkyguardObjectiveRuntime.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardMission10IntegrationTests.cpp.
// Public director API only: nullptr Yak/Gunner, no Yak spawn, no rifle/Igla hits.

namespace SkyguardMission10IntegrationDirectorTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M10_EvacuationFinale.DA_Mission_M10_EvacuationFinale");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission10DirectorTestWorld"));
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

	ASkyguardMission10IntegrationDirector* SpawnBoundDirector(UWorld* World)
	{
		ASkyguardMission10IntegrationDirector* Director =
			World->SpawnActor<ASkyguardMission10IntegrationDirector>();
		if (!Director)
		{
			return nullptr;
		}
		Director->bAutoInitialize = false;
		Director->bAllowBoundedActorSpawning = false;
		Director->BindRuntimeActors(nullptr, nullptr, nullptr, nullptr);
		return Director;
	}

	bool AdvancePhaseWaves(ASkyguardMission10IntegrationDirector* Director)
	{
		const int32 ExpectedCounts[] = {3, 4, 5};
		const ESkyguardMission10RoutePhase ExpectedPhases[] = {
			ESkyguardMission10RoutePhase::FerryTerminal,
			ESkyguardMission10RoutePhase::EvacuationShip,
			ESkyguardMission10RoutePhase::BossEngaged};
		for (int32 Index = 0; Index < 3; ++Index)
		{
			if (!Director->StartPhaseWave() ||
				Director->GetRemainingThreatsInWave() != ExpectedCounts[Index])
			{
				return false;
			}
			if (!Director->NotifyThreatDestroyed(1) ||
				Director->GetRemainingThreatsInWave() !=
					ExpectedCounts[Index] - 1)
			{
				return false;
			}
			if (!Director->NotifyThreatDestroyed(ExpectedCounts[Index] - 1) ||
				Director->GetRemainingThreatsInWave() != 0 ||
				Director->GetRoutePhase() != ExpectedPhases[Index])
			{
				return false;
			}
		}
		return true;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission10DirectorMissionIdAndNullRuntimeTest,
	"Skyguard52.Mission10.Director.MissionIdAndNullRuntimeWeaponRelease",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission10DirectorMissionIdAndNullRuntimeTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission10IntegrationDirectorTests;

	TestEqual(
		TEXT("GetMissionId is M10_EvacuationFinale"),
		ASkyguardMission10IntegrationDirector::GetMissionId(),
		FName(TEXT("M10_EvacuationFinale")));

	TArray<FText> NullContractErrors;
	TestFalse(
		TEXT("ValidateMissionContract rejects a null definition"),
		ASkyguardMission10IntegrationDirector::ValidateMissionContract(
			nullptr, NullContractErrors));
	TestTrue(
		TEXT("Null contract reports at least one error"),
		NullContractErrors.Num() > 0);

	FWorldScope Scope;
	ASkyguardMission10IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(TEXT("Director spawns without Yak or Gunner"), Director);
	if (!Director)
	{
		return false;
	}

	TestEqual(
		TEXT("Unconfigured route stays Briefing"),
		Director->GetRoutePhase(),
		ESkyguardMission10RoutePhase::Briefing);
	TestFalse(
		TEXT("StartPhaseWave is fail-closed before configure"),
		Director->StartPhaseWave());
	TestTrue(
		TEXT("Safe civilian corridor allows release"),
		Director->ValidateWeaponRelease(800.f, false));
	TestFalse(
		TEXT("Civilian corridor intersection rejects release"),
		Director->ValidateWeaponRelease(900.f, true));
	TestFalse(
		TEXT("Below-minimum separation rejects release"),
		Director->ValidateWeaponRelease(250.f, false));
	TestEqual(
		TEXT("Two rejected releases record"),
		Director->GetRejectedWeaponReleases(),
		2);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission10DirectorContractWavesAndProtectFailTest,
	"Skyguard52.Mission10.Director.ContractWavesAndProtectedGroupFail",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission10DirectorContractWavesAndProtectFailTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission10IntegrationDirectorTests;

	USkyguardMissionDefinition* Mission = TryLoadMission();
	if (!Mission)
	{
		AddWarning(TEXT(
			"Mission 10 DataAsset unavailable; skipped contract, "
			"wave, and protected-group tests."));
		return true;
	}

	TArray<FText> Errors;
	TestTrue(
		TEXT("Loaded Mission 10 contract validates"),
		ASkyguardMission10IntegrationDirector::ValidateMissionContract(
			Mission, Errors));
	TestEqual(TEXT("Loaded contract emits no errors"), Errors.Num(), 0);

	FWorldScope Scope;
	UWorld* World = Scope.Get();
	ASkyguardMission10IntegrationDirector* WaveDirector =
		SpawnBoundDirector(World);
	ASkyguardMission10IntegrationDirector* FailDirector =
		SpawnBoundDirector(World);
	TestNotNull(TEXT("Wave director binds nullptr Yak/Gunner"), WaveDirector);
	TestNotNull(TEXT("Fail director binds nullptr Yak/Gunner"), FailDirector);
	if (!WaveDirector || !FailDirector)
	{
		return false;
	}

	TestTrue(
		TEXT("Wave director configures from loaded mission"),
		WaveDirector->ConfigureMissionDefinition(Mission));
	TestEqual(
		TEXT("Configured route starts on Highway"),
		WaveDirector->GetRoutePhase(),
		ESkyguardMission10RoutePhase::Highway);
	TestTrue(
		TEXT("Highway, ferry, and ship waves advance in order"),
		AdvancePhaseWaves(WaveDirector));
	TestEqual(
		TEXT("Third wave hands off to BossEngaged"),
		WaveDirector->GetRoutePhase(),
		ESkyguardMission10RoutePhase::BossEngaged);

	TestTrue(
		TEXT("Fail director configures from loaded mission"),
		FailDirector->ConfigureMissionDefinition(Mission));
	TestTrue(
		TEXT("Catastrophic convoy damage applies"),
		FailDirector->NotifyProtectedGroupDamage(
			ESkyguardMission10ProtectedGroup::Convoy,
			FailDirector->MaximumProtectedIntegrity));
	TestEqual(
		TEXT("Protected loss fails the finale"),
		FailDirector->GetRoutePhase(),
		ESkyguardMission10RoutePhase::Failed);
	const FSkyguardMission10ProtectedRuntime Convoy =
		FailDirector->GetProtectedGroup(
			ESkyguardMission10ProtectedGroup::Convoy);
	TestEqual(TEXT("Destroyed convoy integrity is zero"), Convoy.Integrity, 0);
	TestTrue(TEXT("Destroyed convoy is marked destroyed"), Convoy.bDestroyed);
	TestEqual(
		TEXT("Two protected groups remain"),
		FailDirector->GetSurvivingProtectedGroupCount(),
		2);
	USkyguardObjectiveRuntime* Objectives =
		FailDirector->GetObjectiveRuntime();
	TestNotNull(TEXT("Local objective runtime exists"), Objectives);
	if (Objectives)
	{
		TestTrue(
			TEXT("Protection objective records terminal failure"),
			Objectives->HasTerminalFailure());
	}
	TestFalse(
		TEXT("Failed finale cannot begin another wave"),
		FailDirector->StartPhaseWave());
	return true;
}

#endif
