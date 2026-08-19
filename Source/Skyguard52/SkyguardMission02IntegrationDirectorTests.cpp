#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission02IntegrationDirector.h"

#include "SkyguardMissionDefinition.h"
#include "SkyguardObjectiveRuntime.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardMission02IntegrationTests.cpp.
// Public director API only: nullptr map/Yak/Gunner/Breakwater, no actor spawn,
// no live weapon-hit or Igla-strike calls.

namespace SkyguardMission02IntegrationDirectorTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M02_HarborShield.DA_Mission_M02_HarborShield");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission02DirectorTestWorld"));
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

	USkyguardMissionDefinition* MakeIsolatedHarborShieldDefinition()
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>();
		Mission->MissionId =
			ASkyguardMission02IntegrationDirector::GetMissionId();
		Mission->DisplayName = FText::FromString(TEXT("Harbor Shield"));
		for (int32 Index = 0; Index < 4; ++Index)
		{
			FSkyguardRoutePoint Point;
			Point.PointId =
				FName(*FString::Printf(TEXT("M02_Isolated_P%d"), Index));
			Point.WorldLocation = FVector(Index * 12000.f, 0.f, 5200.f);
			Mission->Route.Points.Add(Point);
		}

		FSkyguardObjectiveDefinition Protect;
		Protect.ObjectiveId = TEXT("ProtectFuelTerminal");
		Protect.Type = ESkyguardMissionObjectiveType::ProtectAsset;
		Protect.RequiredProgress = 1;
		Protect.bFailureEndsMission = true;
		FSkyguardObjectiveDefinition Strip;
		Strip.ObjectiveId = TEXT("StripArmorPanels");
		Strip.RequiredProgress = 2;
		FSkyguardObjectiveDefinition Defeat;
		Defeat.ObjectiveId = TEXT("DefeatBreakwater");
		Defeat.RequiredProgress = 4;
		Mission->Objectives = {Protect, Strip, Defeat};

		Mission->Boss.BossId = TEXT("Breakwater");
		Mission->Boss.DefeatObjectiveId = TEXT("DefeatBreakwater");
		Mission->Boss.MaximumBreakupPieces = 3;
		const FName WeakPointIds[] = {
			TEXT("PortLatch"),
			TEXT("StarboardLatch"),
			TEXT("DecoyPods"),
			TEXT("Engine")};
		const FName RequiredWeapons[] = {
			TEXT("Rifle"), TEXT("Rifle"),
			TEXT("Rifle"), TEXT("Igla")};
		const FName Exposes[] = {
			TEXT("StarboardLatch"), TEXT("DecoyPods"),
			TEXT("Engine"), NAME_None};
		for (int32 Index = 0; Index < 4; ++Index)
		{
			FSkyguardBossWeakPointDefinition Point;
			Point.WeakPointId = WeakPointIds[Index];
			Point.RequiredWeapon = RequiredWeapons[Index];
			Point.ExposesWeakPointId = Exposes[Index];
			Mission->Boss.WeakPoints.Add(Point);
		}

		for (int32 Index = 0; Index < 3; ++Index)
		{
			FSkyguardEnemyWaveDefinition Wave;
			Wave.WaveId =
				FName(*FString::Printf(TEXT("M02_Isolated_Wave_%d"), Index + 1));
			Mission->Waves.Add(Wave);
		}
		Mission->Weather.ProfileId = TEXT("HarborOvercast");
		Mission->Presentation.Briefing =
			FText::FromString(TEXT("Isolated Mission 2 harbor contract."));
		Mission->Presentation.RadioChatter = {
			FText::FromString(TEXT("Isolated radio 1")),
			FText::FromString(TEXT("Isolated radio 2")),
			FText::FromString(TEXT("Isolated radio 3"))};
		return Mission;
	}

	ASkyguardMission02IntegrationDirector* SpawnBoundDirector(UWorld* World)
	{
		ASkyguardMission02IntegrationDirector* Director =
			World->SpawnActor<ASkyguardMission02IntegrationDirector>();
		if (!Director)
		{
			return nullptr;
		}
		Director->bAutoInitialize = false;
		Director->bAllowBoundedActorSpawning = false;
		Director->BindRuntimeActors(nullptr, nullptr, nullptr, nullptr);
		return Director;
	}

	bool ExerciseFuelTerminalIntegrityAndWipeFail(
		FAutomationTestBase& Test,
		ASkyguardMission02IntegrationDirector* Director)
	{
		const int32 StartingIntegrity = Director->GetFuelTerminalIntegrity();
		Test.TestEqual(
			TEXT("Configured fuel integrity matches MaximumFuelTerminalIntegrity"),
			StartingIntegrity,
			Director->MaximumFuelTerminalIntegrity);
		if (!Test.TestTrue(
			TEXT("Partial fuel-terminal damage applies"),
			Director->NotifyFuelTerminalDamage(11)))
		{
			return false;
		}
		Test.TestEqual(
			TEXT("Partial fuel-terminal damage reduces integrity"),
			Director->GetFuelTerminalIntegrity(),
			StartingIntegrity - 11);
		if (!Test.TestTrue(
			TEXT("MaximumFuelTerminalIntegrity wipe is accepted"),
			Director->NotifyFuelTerminalDamage(
				Director->MaximumFuelTerminalIntegrity)))
		{
			return false;
		}
		Test.TestEqual(
			TEXT("Wiped fuel terminal integrity is zero"),
			Director->GetFuelTerminalIntegrity(),
			0);
		Test.TestEqual(
			TEXT("Wiping the fuel terminal fails the mission"),
			Director->GetWaveState(),
			ESkyguardMission02WaveState::Failed);
		USkyguardObjectiveRuntime* Objectives = Director->GetObjectiveRuntime();
		Test.TestNotNull(
			TEXT("Local objective runtime exists after configure"),
			Objectives);
		if (Objectives)
		{
			Test.TestTrue(
				TEXT("ProtectFuelTerminal records terminal failure"),
				Objectives->HasTerminalFailure());
		}
		Test.TestFalse(
			TEXT("Failed mission rejects StartNextWave"),
			Director->StartNextWave());
		return true;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission02DirectorMissionIdAndNullRuntimeTest,
	"Skyguard52.Mission02.Director.MissionIdAndNullRuntimeBind",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission02DirectorMissionIdAndNullRuntimeTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission02IntegrationDirectorTests;

	TestEqual(
		TEXT("GetMissionId is M02_HarborShield"),
		ASkyguardMission02IntegrationDirector::GetMissionId(),
		FName(TEXT("M02_HarborShield")));

	TArray<FText> NullContractErrors;
	TestFalse(
		TEXT("ValidateMissionContract rejects a null definition"),
		ASkyguardMission02IntegrationDirector::ValidateMissionContract(
			nullptr, NullContractErrors));
	TestTrue(
		TEXT("Null contract reports at least one error"),
		NullContractErrors.Num() > 0);

	FWorldScope Scope;
	ASkyguardMission02IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(
		TEXT("Director spawns without Yak, Gunner, or Breakwater"),
		Director);
	if (!Director)
	{
		return false;
	}

	TestNull(
		TEXT("BindRuntimeActors(nullptr) does not attach a Breakwater"),
		Director->GetBreakwater());
	TestEqual(
		TEXT("Unconfigured wave state stays Briefing"),
		Director->GetWaveState(),
		ESkyguardMission02WaveState::Briefing);
	TestFalse(
		TEXT("StartNextWave is fail-closed before configure"),
		Director->StartNextWave());
	TestEqual(
		TEXT("Failed StartNextWave leaves Briefing"),
		Director->GetWaveState(),
		ESkyguardMission02WaveState::Briefing);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission02DirectorContractWavesAndFuelFailTest,
	"Skyguard52.Mission02.Director.ContractWavesAndFuelTerminalFail",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission02DirectorContractWavesAndFuelFailTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission02IntegrationDirectorTests;

	USkyguardMissionDefinition* Mission = TryLoadMission();
	const bool bLoadedCampaignAsset = Mission != nullptr;
	if (bLoadedCampaignAsset)
	{
		TArray<FText> Errors;
		TestTrue(
			TEXT("Loaded Mission 2 contract validates"),
			ASkyguardMission02IntegrationDirector::ValidateMissionContract(
				Mission, Errors));
		TestEqual(TEXT("Loaded contract emits no errors"), Errors.Num(), 0);
	}
	else
	{
		AddWarning(TEXT(
			"Mission 2 DataAsset unavailable; skipped governed wave "
			"tests and used an isolated in-memory contract so "
			"fuel-terminal public-API tests still run. Null-runtime "
			"tests still passed."));
		Mission = MakeIsolatedHarborShieldDefinition();
		TArray<FText> IsolatedErrors;
		if (!ASkyguardMission02IntegrationDirector::ValidateMissionContract(
				Mission, IsolatedErrors))
		{
			AddError(TEXT("Isolated Mission 2 contract must validate."));
			return false;
		}
	}

	FWorldScope Scope;
	UWorld* World = Scope.Get();
	ASkyguardMission02IntegrationDirector* WaveDirector =
		SpawnBoundDirector(World);
	ASkyguardMission02IntegrationDirector* FuelDirector =
		SpawnBoundDirector(World);
	TestNotNull(TEXT("Wave director binds nullptr runtime actors"), WaveDirector);
	TestNotNull(TEXT("Fuel director binds nullptr runtime actors"), FuelDirector);
	if (!WaveDirector || !FuelDirector)
	{
		return false;
	}

	if (bLoadedCampaignAsset)
	{
		TestTrue(
			TEXT("Wave director configures from loaded Mission 2"),
			WaveDirector->ConfigureMissionDefinition(Mission));
		TestEqual(
			TEXT("ConfigureMissionDefinition awaits the first wave"),
			WaveDirector->GetWaveState(),
			ESkyguardMission02WaveState::AwaitingWave);
		TestTrue(
			TEXT("StartNextWave opens the first governed wave"),
			WaveDirector->StartNextWave());
		TestEqual(
			TEXT("StartNextWave promotes AwaitingWave to WaveActive"),
			WaveDirector->GetWaveState(),
			ESkyguardMission02WaveState::WaveActive);
		const int32 RemainingAfterStart =
			WaveDirector->GetRemainingThreatsInWave();
		TestTrue(
			TEXT("First wave reports at least one remaining threat"),
			RemainingAfterStart > 0);
		TestTrue(
			TEXT("NotifyThreatDestroyed accepts one kill"),
			WaveDirector->NotifyThreatDestroyed(1));
		TestEqual(
			TEXT("NotifyThreatDestroyed decrements remaining threats"),
			WaveDirector->GetRemainingThreatsInWave(),
			RemainingAfterStart - 1);
		TestNull(
			TEXT("StartNextWave does not spawn a Breakwater"),
			WaveDirector->GetBreakwater());
	}

	TestTrue(
		TEXT("Fuel director configures from the isolated or loaded mission"),
		FuelDirector->ConfigureMissionDefinition(Mission));
	TestNull(
		TEXT("Configure does not spawn a Breakwater"),
		FuelDirector->GetBreakwater());
	return ExerciseFuelTerminalIntegrityAndWipeFail(*this, FuelDirector);
}

#endif
