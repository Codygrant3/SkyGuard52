#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission09IntegrationDirector.h"

#include "SkyguardMissionDefinition.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardMission09IntegrationTests.cpp.
// Public director API only: nullptr map/Yak/Gunner/IronRain, no actor
// spawn, no rifle/Igla hits, no day-beat kit edits.

namespace SkyguardMission09IntegrationDirectorTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M09_SaturationAttack.DA_Mission_M09_SaturationAttack");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission09DirectorTestWorld"));
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

	USkyguardMissionDefinition* MakeContractValidMission()
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>(GetTransientPackage());
		Mission->MissionId =
			ASkyguardMission09IntegrationDirector::GetMissionId();
		Mission->DisplayName = FText::FromString(TEXT("Saturation Attack"));
		Mission->CampaignOrder = 9;
		Mission->Route.RouteId = TEXT("M09_SaturationOrbit");
		for (int32 Index = 0; Index < 4; ++Index)
		{
			FSkyguardRoutePoint Point;
			Point.PointId = FName(*FString::Printf(TEXT("M09_P%d"), Index));
			Point.WorldLocation = FVector(
				40000.f + Index * 10000.f, 24000.f, 6200.f);
			Mission->Route.Points.Add(Point);
		}

		FSkyguardObjectiveDefinition Protect;
		Protect.ObjectiveId = TEXT("ProtectCityInfrastructure");
		Protect.DisplayName = FText::FromString(TEXT("Protect city infrastructure"));
		Protect.Type = ESkyguardMissionObjectiveType::ProtectAsset;
		Protect.RequiredProgress = 1;
		Protect.bFailureEndsMission = true;
		FSkyguardObjectiveDefinition Relays;
		Relays.ObjectiveId = TEXT("BreakSwarmRelays");
		Relays.DisplayName = FText::FromString(TEXT("Break swarm relays"));
		Relays.Type = ESkyguardMissionObjectiveType::DestroyTargets;
		Relays.RequiredProgress = 3;
		FSkyguardObjectiveDefinition Defeat;
		Defeat.ObjectiveId = TEXT("DefeatIronRain");
		Defeat.DisplayName = FText::FromString(TEXT("Defeat Iron Rain"));
		Defeat.Type = ESkyguardMissionObjectiveType::BossPhase;
		Defeat.RequiredProgress = 4;
		Mission->Objectives = {Protect, Relays, Defeat};

		const int32 WaveCounts[] = {8, 12, 16};
		for (int32 WaveIndex = 0; WaveIndex < 3; ++WaveIndex)
		{
			FSkyguardEnemyWaveDefinition Wave;
			Wave.WaveId = FName(*FString::Printf(TEXT("M09_W%d"), WaveIndex));
			FSkyguardEnemyFormationDefinition Formation;
			Formation.FormationId =
				FName(*FString::Printf(TEXT("M09_F%d"), WaveIndex));
			Formation.UnitCount = WaveCounts[WaveIndex];
			Wave.Formations.Add(Formation);
			Mission->Waves.Add(Wave);
		}

		Mission->Boss.BossId = TEXT("IronRain");
		Mission->Boss.DefeatObjectiveId = TEXT("DefeatIronRain");
		Mission->Boss.MaximumBreakupPieces = 3;
		Mission->Weather.ProfileId = TEXT("CityDusk");
		Mission->Presentation.Briefing =
			FText::FromString(TEXT("Hold the skyline."));
		Mission->Presentation.RadioChatter = {
			FText::FromString(TEXT("Saturation inbound.")),
			FText::FromString(TEXT("Protect the grid.")),
			FText::FromString(TEXT("Iron Rain is on the board."))};
		return Mission;
	}

	ASkyguardMission09IntegrationDirector* SpawnBoundDirector(UWorld* World)
	{
		ASkyguardMission09IntegrationDirector* Director =
			World->SpawnActor<ASkyguardMission09IntegrationDirector>();
		if (!Director)
		{
			return nullptr;
		}
		Director->bAutoInitialize = false;
		Director->bAllowBoundedActorSpawning = false;
		Director->BindRuntimeActors(nullptr, nullptr, nullptr, nullptr);
		return Director;
	}

	void AssertPoolRuntimeAsImplemented(
		FAutomationTestBase& Test,
		const ASkyguardMission09IntegrationDirector* Director,
		const int32 ExpectedAvailable,
		const int32 ExpectedActive,
		const int32 ExpectedPeakActive,
		const int32 ExpectedRecycled)
	{
		const FSkyguardMission09PoolRuntime& Pool = Director->GetPoolRuntime();
		Test.TestEqual(
			TEXT("Pool Available matches implementation"),
			Pool.Available,
			ExpectedAvailable);
		Test.TestEqual(
			TEXT("Pool Active matches implementation"),
			Pool.Active,
			ExpectedActive);
		Test.TestEqual(
			TEXT("Pool PeakActive matches implementation"),
			Pool.PeakActive,
			ExpectedPeakActive);
		Test.TestEqual(
			TEXT("Pool Recycled matches implementation"),
			Pool.Recycled,
			ExpectedRecycled);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission09DirectorMissionIdNullContractAndFailClosedWaveTest,
	"Skyguard52.Mission09.Director.MissionIdNullContractAndFailClosedWave",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission09DirectorMissionIdNullContractAndFailClosedWaveTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission09IntegrationDirectorTests;

	TestEqual(
		TEXT("GetMissionId is M09_SaturationAttack"),
		ASkyguardMission09IntegrationDirector::GetMissionId(),
		FName(TEXT("M09_SaturationAttack")));

	TArray<FText> NullContractErrors;
	TestFalse(
		TEXT("ValidateMissionContract rejects a null definition"),
		ASkyguardMission09IntegrationDirector::ValidateMissionContract(
			nullptr, NullContractErrors));
	TestTrue(
		TEXT("Null contract reports at least one error"),
		NullContractErrors.Num() > 0);

	FWorldScope Scope;
	ASkyguardMission09IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(
		TEXT("Director spawns without Yak, Gunner, or IronRain"),
		Director);
	if (!Director)
	{
		return false;
	}

	TestEqual(
		TEXT("Unconfigured wave stays Briefing"),
		Director->GetWaveState(),
		ESkyguardMission09WaveState::Briefing);
	TestFalse(
		TEXT("StartNextWave is fail-closed before configure"),
		Director->StartNextWave());
	TestEqual(
		TEXT("Failed StartNextWave leaves the wave in Briefing"),
		Director->GetWaveState(),
		ESkyguardMission09WaveState::Briefing);
	TestFalse(
		TEXT("NotifyThreatDestroyed is fail-closed before a wave is active"),
		Director->NotifyThreatDestroyed(1));
	AssertPoolRuntimeAsImplemented(
		*this,
		Director,
		48,
		0,
		0,
		0);

	TestFalse(
		TEXT("Unconfigured MetropolitanSkyline damage is fail-closed"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission09ProtectedTarget::MetropolitanSkyline, 20));
	TestFalse(
		TEXT("Unconfigured CoastalPowerStation damage is fail-closed"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission09ProtectedTarget::CoastalPowerStation, 20));
	TestFalse(
		TEXT("Unconfigured MajorBridge damage is fail-closed"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission09ProtectedTarget::MajorBridge, 20));
	TestEqual(
		TEXT("Unconfigured surviving target count stays zero"),
		Director->GetSurvivingTargetCount(),
		0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission09DirectorConfiguredWavesPoolAndProtectTest,
	"Skyguard52.Mission09.Director.ConfiguredWavesPoolAndProtect",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission09DirectorConfiguredWavesPoolAndProtectTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission09IntegrationDirectorTests;

	USkyguardMissionDefinition* Mission = TryLoadMission();
	if (Mission)
	{
		TArray<FText> LoadedErrors;
		TestTrue(
			TEXT("Loaded Mission 9 contract validates"),
			ASkyguardMission09IntegrationDirector::ValidateMissionContract(
				Mission, LoadedErrors));
		TestEqual(
			TEXT("Loaded contract emits no errors"),
			LoadedErrors.Num(),
			0);
	}
	else
	{
		AddWarning(TEXT(
			"Mission 9 DataAsset unavailable; using an in-memory "
			"contract-valid definition so public-API wave, pool, and "
			"protected-target tests still run."));
		Mission = MakeContractValidMission();
		TArray<FText> IsolatedErrors;
		if (!ASkyguardMission09IntegrationDirector::ValidateMissionContract(
				Mission, IsolatedErrors))
		{
			AddError(TEXT("Isolated Mission 9 contract must validate."));
			return false;
		}
	}
	if (!Mission)
	{
		AddError(TEXT("Mission 9 definition was not available."));
		return false;
	}

	FWorldScope Scope;
	ASkyguardMission09IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(
		TEXT("Director binds nullptr map/Yak/Gunner/IronRain"),
		Director);
	if (!Director)
	{
		return false;
	}

	TestTrue(
		TEXT("Director configures from the isolated or loaded mission"),
		Director->ConfigureMissionDefinition(Mission));
	TestEqual(
		TEXT("Configured wave waits for the first start"),
		Director->GetWaveState(),
		ESkyguardMission09WaveState::AwaitingWave);
	AssertPoolRuntimeAsImplemented(
		*this,
		Director,
		Director->PoolBudget.PoolCapacity,
		0,
		0,
		0);
	TestEqual(
		TEXT("Three protected targets start intact"),
		Director->GetSurvivingTargetCount(),
		3);

	if (Mission->Waves.Num() > 0)
	{
		TestTrue(TEXT("First wave starts"), Director->StartNextWave());
		TestEqual(
			TEXT("Wave state is WaveActive"),
			Director->GetWaveState(),
			ESkyguardMission09WaveState::WaveActive);
		const int32 RemainingAfterStart = Director->GetRemainingThreatsInWave();
		TestTrue(
			TEXT("Started wave has remaining threats"),
			RemainingAfterStart > 0);
		AssertPoolRuntimeAsImplemented(
			*this,
			Director,
			Director->PoolBudget.PoolCapacity - RemainingAfterStart,
			RemainingAfterStart,
			RemainingAfterStart,
			0);

		const int32 Destroyed = FMath::Min(3, RemainingAfterStart);
		TestTrue(
			TEXT("NotifyThreatDestroyed applies while WaveActive"),
			Director->NotifyThreatDestroyed(Destroyed));
		TestEqual(
			TEXT("Remaining threats drop by the destroyed count"),
			Director->GetRemainingThreatsInWave(),
			RemainingAfterStart - Destroyed);
		AssertPoolRuntimeAsImplemented(
			*this,
			Director,
			Director->PoolBudget.PoolCapacity - (RemainingAfterStart - Destroyed),
			RemainingAfterStart - Destroyed,
			RemainingAfterStart,
			Destroyed);
	}

	TestTrue(
		TEXT("MetropolitanSkyline accepts bounded damage"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission09ProtectedTarget::MetropolitanSkyline, 15));
	const FSkyguardMission09ProtectedTargetRuntime SkylineAfterHit =
		Director->GetProtectedTarget(
			ESkyguardMission09ProtectedTarget::MetropolitanSkyline);
	TestEqual(
		TEXT("MetropolitanSkyline integrity drops by the applied damage"),
		SkylineAfterHit.Integrity,
		Director->MaximumProtectedTargetIntegrity - 15);
	TestFalse(
		TEXT("Damaged MetropolitanSkyline is not destroyed"),
		SkylineAfterHit.bDestroyed);

	TestTrue(
		TEXT("CoastalPowerStation accepts bounded damage"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission09ProtectedTarget::CoastalPowerStation, 20));
	const FSkyguardMission09ProtectedTargetRuntime StationAfterHit =
		Director->GetProtectedTarget(
			ESkyguardMission09ProtectedTarget::CoastalPowerStation);
	TestEqual(
		TEXT("CoastalPowerStation integrity drops by the applied damage"),
		StationAfterHit.Integrity,
		Director->MaximumProtectedTargetIntegrity - 20);
	TestFalse(
		TEXT("Damaged CoastalPowerStation is not destroyed"),
		StationAfterHit.bDestroyed);

	TestTrue(
		TEXT("MajorBridge accepts bounded damage"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission09ProtectedTarget::MajorBridge, 25));
	const FSkyguardMission09ProtectedTargetRuntime BridgeAfterHit =
		Director->GetProtectedTarget(
			ESkyguardMission09ProtectedTarget::MajorBridge);
	TestEqual(
		TEXT("MajorBridge integrity drops by the applied damage"),
		BridgeAfterHit.Integrity,
		Director->MaximumProtectedTargetIntegrity - 25);
	TestFalse(TEXT("Damaged MajorBridge is not destroyed"), BridgeAfterHit.bDestroyed);
	TestEqual(
		TEXT("All three targets still survive after partial damage"),
		Director->GetSurvivingTargetCount(),
		3);

	TestTrue(
		TEXT("Wiping MajorBridge is accepted"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission09ProtectedTarget::MajorBridge,
			Director->MaximumProtectedTargetIntegrity));
	const FSkyguardMission09ProtectedTargetRuntime WipedBridge =
		Director->GetProtectedTarget(
			ESkyguardMission09ProtectedTarget::MajorBridge);
	TestEqual(TEXT("Wiped MajorBridge integrity is zero"), WipedBridge.Integrity, 0);
	TestTrue(TEXT("Wiped MajorBridge is marked destroyed"), WipedBridge.bDestroyed);
	TestEqual(
		TEXT("Surviving target count drops after one wipe"),
		Director->GetSurvivingTargetCount(),
		2);
	return true;
}

#endif
