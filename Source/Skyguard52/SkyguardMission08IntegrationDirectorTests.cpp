#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission08IntegrationDirector.h"

#include "SkyguardMissionDefinition.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardMission08IntegrationTests.cpp.
// Public director API only: nullptr Yak/Gunner/LifelineHunter, no live weapon hits.

namespace SkyguardMission08IntegrationDirectorTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M08_RescueCover.DA_Mission_M08_RescueCover");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission08DirectorTestWorld"));
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
		Mission->MissionId = TEXT("M08_RescueCover");
		Mission->DisplayName = FText::FromString(TEXT("Rescue Cover"));
		Mission->CampaignOrder = 8;
		Mission->Route.RouteId = TEXT("M08_RescueOrbit");
		for (int32 Index = 0; Index < 4; ++Index)
		{
			FSkyguardRoutePoint Point;
			Point.PointId = FName(*FString::Printf(TEXT("M08_P%d"), Index));
			Point.WorldLocation = FVector(
				30000.f + Index * 8000.f, 12000.f, 5200.f);
			Mission->Route.Points.Add(Point);
		}

		FSkyguardObjectiveDefinition Protect;
		Protect.ObjectiveId = TEXT("ProtectRescueFlight");
		Protect.DisplayName = FText::FromString(TEXT("Protect rescue flight"));
		Protect.Type = ESkyguardMissionObjectiveType::ProtectAsset;
		Protect.RequiredProgress = 1;
		Protect.bFailureEndsMission = true;
		FSkyguardObjectiveDefinition Hoists;
		Hoists.ObjectiveId = TEXT("CompleteHoistWindows");
		Hoists.DisplayName = FText::FromString(TEXT("Complete hoist windows"));
		Hoists.Type = ESkyguardMissionObjectiveType::Rescue;
		Hoists.RequiredProgress = 3;
		FSkyguardObjectiveDefinition Defeat;
		Defeat.ObjectiveId = TEXT("DefeatLifelineHunter");
		Defeat.DisplayName = FText::FromString(TEXT("Defeat Lifeline Hunter"));
		Defeat.Type = ESkyguardMissionObjectiveType::BossPhase;
		Defeat.RequiredProgress = 4;
		Mission->Objectives = {Protect, Hoists, Defeat};

		const int32 WaveCounts[] = {2, 3, 4};
		for (int32 WaveIndex = 0; WaveIndex < 3; ++WaveIndex)
		{
			FSkyguardEnemyWaveDefinition Wave;
			Wave.WaveId = FName(*FString::Printf(TEXT("M08_W%d"), WaveIndex));
			FSkyguardEnemyFormationDefinition Formation;
			Formation.FormationId =
				FName(*FString::Printf(TEXT("M08_F%d"), WaveIndex));
			Formation.UnitCount = WaveCounts[WaveIndex];
			Wave.Formations.Add(Formation);
			Mission->Waves.Add(Wave);
		}

		Mission->Boss.BossId = TEXT("LifelineHunter");
		Mission->Boss.DefeatObjectiveId = TEXT("DefeatLifelineHunter");
		Mission->Boss.MaximumBreakupPieces = 3;
		const FName WeakPointIds[] = {
			TEXT("OpticalTracker"),
			TEXT("WeaponServo"),
			TEXT("CountermeasurePod"),
			TEXT("Engine")};
		// Contract RequiredWeapon names only. No live rifle/Igla copy or hits.
		const FName RequiredWeapons[] = {
			TEXT("Rifle"), TEXT("Rifle"), TEXT("Rifle"), TEXT("Igla")};
		const FName Exposes[] = {
			TEXT("WeaponServo"),
			TEXT("CountermeasurePod"),
			TEXT("Engine"),
			NAME_None};
		for (int32 Index = 0; Index < 4; ++Index)
		{
			FSkyguardBossWeakPointDefinition Point;
			Point.WeakPointId = WeakPointIds[Index];
			Point.RequiredWeapon = RequiredWeapons[Index];
			Point.ExposesWeakPointId = Exposes[Index];
			Mission->Boss.WeakPoints.Add(Point);
		}

		Mission->Weather.ProfileId = TEXT("RescueSunset");
		Mission->Presentation.Briefing =
			FText::FromString(TEXT("Cover the hoist."));
		Mission->Presentation.RadioChatter = {
			FText::FromString(TEXT("Rescue is inbound.")),
			FText::FromString(TEXT("Hold the corridor.")),
			FText::FromString(TEXT("Hoist window now."))};
		return Mission;
	}

	ASkyguardMission08IntegrationDirector* SpawnBoundDirector(UWorld* World)
	{
		ASkyguardMission08IntegrationDirector* Director =
			World->SpawnActor<ASkyguardMission08IntegrationDirector>();
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
	FSkyguardMission08DirectorMissionIdAndNullRuntimeTest,
	"Skyguard52.Mission08.Director.MissionIdHoistClosedAndFriendlyExclusion",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission08DirectorMissionIdAndNullRuntimeTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission08IntegrationDirectorTests;

	TestEqual(
		TEXT("GetMissionId is M08_RescueCover"),
		ASkyguardMission08IntegrationDirector::GetMissionId(),
		FName(TEXT("M08_RescueCover")));

	TArray<FText> NullContractErrors;
	TestFalse(
		TEXT("ValidateMissionContract rejects a null definition"),
		ASkyguardMission08IntegrationDirector::ValidateMissionContract(
			nullptr, NullContractErrors));
	TestTrue(
		TEXT("Null contract reports at least one error"),
		NullContractErrors.Num() > 0);

	FWorldScope Scope;
	ASkyguardMission08IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(
		TEXT("Director spawns without Yak, Gunner, or LifelineHunter"),
		Director);
	if (!Director)
	{
		return false;
	}

	TestEqual(
		TEXT("Unconfigured wave stays Briefing"),
		Director->GetWaveState(),
		ESkyguardMission08WaveState::Briefing);
	TestFalse(
		TEXT("StartHoistWindow is fail-closed before WaveActive"),
		Director->StartHoistWindow(6.f));
	TestFalse(
		TEXT("AdvanceHoistWindow is fail-closed while inactive"),
		Director->AdvanceHoistWindow(1.f, true));
	const FSkyguardHoistWindowRuntime ClosedHoist = Director->GetHoistRuntime();
	TestFalse(TEXT("Closed hoist is inactive"), ClosedHoist.bActive);
	TestEqual(
		TEXT("Closed hoist remaining seconds stay zero"),
		ClosedHoist.RemainingSeconds,
		0.f);
	TestEqual(
		TEXT("Closed hoist covered seconds stay zero"),
		ClosedHoist.CoveredSeconds,
		0.f);
	TestEqual(
		TEXT("Closed hoist completed windows stay zero"),
		ClosedHoist.CompletedWindows,
		0);

	TestFalse(
		TEXT("Friendly corridor intersection rejects release"),
		Director->ValidateWeaponRelease(900.f, true));
	TestFalse(
		TEXT("Below-minimum separation rejects release"),
		Director->ValidateWeaponRelease(200.f, false));
	TestTrue(
		TEXT("Far non-corridor shot allows release"),
		Director->ValidateWeaponRelease(700.f, false));
	TestEqual(
		TEXT("Two rejected releases record"),
		Director->GetRejectedWeaponReleases(),
		2);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission08DirectorHoistAndProtectedTargetsTest,
	"Skyguard52.Mission08.Director.HoistWindowAndProtectedTargetWipe",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission08DirectorHoistAndProtectedTargetsTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission08IntegrationDirectorTests;

	USkyguardMissionDefinition* Mission = TryLoadMission();
	if (Mission)
	{
		TArray<FText> LoadedErrors;
		TestTrue(
			TEXT("Loaded Mission 8 contract validates"),
			ASkyguardMission08IntegrationDirector::ValidateMissionContract(
				Mission, LoadedErrors));
		TestEqual(
			TEXT("Loaded contract emits no errors"),
			LoadedErrors.Num(),
			0);
	}
	else
	{
		AddWarning(TEXT(
			"Mission 8 DataAsset unavailable; using an in-memory "
			"contract-valid definition for hoist and protected-target "
			"public API coverage."));
		Mission = MakeContractValidMission();
	}
	if (!Mission)
	{
		AddError(TEXT("Mission 8 definition was not available."));
		return false;
	}

	FWorldScope Scope;
	ASkyguardMission08IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(
		TEXT("Director binds nullptr Yak/Gunner/LifelineHunter"),
		Director);
	if (!Director)
	{
		return false;
	}

	TestTrue(
		TEXT("Director configures from Mission 8 definition"),
		Director->ConfigureMissionDefinition(Mission));
	TestEqual(
		TEXT("Configured wave waits for the first start"),
		Director->GetWaveState(),
		ESkyguardMission08WaveState::AwaitingWave);
	TestFalse(
		TEXT("Hoist stays closed while AwaitingWave"),
		Director->StartHoistWindow(6.f));
	TestTrue(
		TEXT("First governed wave becomes WaveActive"),
		Director->StartNextWave());
	TestEqual(
		TEXT("Active wave is WaveActive"),
		Director->GetWaveState(),
		ESkyguardMission08WaveState::WaveActive);

	TestTrue(
		TEXT("Hoist window starts while WaveActive"),
		Director->StartHoistWindow(6.f));
	FSkyguardHoistWindowRuntime Hoist = Director->GetHoistRuntime();
	TestTrue(TEXT("Started hoist is active"), Hoist.bActive);
	TestEqual(TEXT("Started hoist remaining is 6s"), Hoist.RemainingSeconds, 6.f);
	TestEqual(TEXT("Started hoist covered is 0s"), Hoist.CoveredSeconds, 0.f);
	TestEqual(TEXT("Started hoist completed windows are 0"), Hoist.CompletedWindows, 0);

	TestTrue(
		TEXT("Partial covered advance keeps the window open"),
		Director->AdvanceHoistWindow(2.f, true));
	Hoist = Director->GetHoistRuntime();
	TestTrue(TEXT("Partially covered hoist stays active"), Hoist.bActive);
	TestEqual(TEXT("Partial advance remaining is 4s"), Hoist.RemainingSeconds, 4.f);
	TestEqual(TEXT("Partial advance covered is 2s"), Hoist.CoveredSeconds, 2.f);
	TestEqual(
		TEXT("Partial advance does not complete a window"),
		Hoist.CompletedWindows,
		0);

	TestTrue(
		TEXT("Reaching RequiredCoveredSeconds completes the window"),
		Director->AdvanceHoistWindow(2.f, true));
	Hoist = Director->GetHoistRuntime();
	TestFalse(TEXT("Completed hoist is inactive"), Hoist.bActive);
	TestEqual(
		TEXT("Completed hoist remaining is 2s after the last tick"),
		Hoist.RemainingSeconds,
		2.f);
	TestEqual(
		TEXT("Completed hoist covered meets RequiredCoveredSeconds"),
		Hoist.CoveredSeconds,
		Director->RequiredCoveredSeconds);
	TestEqual(
		TEXT("Completing RequiredCoveredSeconds increments CompletedWindows"),
		Hoist.CompletedWindows,
		1);
	TestFalse(
		TEXT("AdvanceHoistWindow is fail-closed after completion"),
		Director->AdvanceHoistWindow(1.f, true));

	TestEqual(
		TEXT("Three protected targets survive before damage"),
		Director->GetSurvivingTargetCount(),
		3);
	TestTrue(
		TEXT("RescueHelicopter takes non-fatal damage"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission08ProtectedTarget::RescueHelicopter, 15));
	TestTrue(
		TEXT("SurvivorsAndRafts take non-fatal damage"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission08ProtectedTarget::SurvivorsAndRafts, 15));
	TestTrue(
		TEXT("RescueVessel takes non-fatal damage"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission08ProtectedTarget::RescueVessel, 15));
	TestEqual(
		TEXT("All three friendly groups still survive"),
		Director->GetSurvivingTargetCount(),
		3);

	TestTrue(
		TEXT("Wiping RescueVessel destroys that group"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission08ProtectedTarget::RescueVessel,
			Director->MaximumProtectedTargetIntegrity));
	const FSkyguardMission08ProtectedTargetRuntime Vessel =
		Director->GetProtectedTarget(
			ESkyguardMission08ProtectedTarget::RescueVessel);
	TestEqual(TEXT("Wiped vessel integrity is zero"), Vessel.Integrity, 0);
	TestTrue(TEXT("Wiped vessel is marked destroyed"), Vessel.bDestroyed);
	TestEqual(
		TEXT("Surviving target count drops after one wipe"),
		Director->GetSurvivingTargetCount(),
		2);
	return true;
}

#endif
