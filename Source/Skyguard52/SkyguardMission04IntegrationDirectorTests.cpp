#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission04IntegrationDirector.h"

#include "SkyguardMissionDefinition.h"
#include "SkyguardObjectiveRuntime.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardMission04IntegrationTests.cpp.
// Public director API only: nullptr map/Yak/Gunner/BlackKite, no actor spawn,
// no rifle/Igla hits, no night-beat kit edits.

namespace SkyguardMission04IntegrationDirectorTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M04_NightBlackout.DA_Mission_M04_NightBlackout");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission04DirectorTestWorld"));
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

	USkyguardMissionDefinition* MakeIsolatedNightBlackoutDefinition()
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>();
		Mission->MissionId =
			ASkyguardMission04IntegrationDirector::GetMissionId();
		Mission->DisplayName = FText::FromString(TEXT("Night Blackout"));
		for (int32 Index = 0; Index < 4; ++Index)
		{
			FSkyguardRoutePoint Point;
			Point.PointId =
				FName(*FString::Printf(TEXT("M04_Isolated_P%d"), Index));
			Point.WorldLocation = FVector(Index * 12000.f, 0.f, 5800.f);
			Mission->Route.Points.Add(Point);
		}

		FSkyguardObjectiveDefinition Protect;
		Protect.ObjectiveId = TEXT("ProtectSubstation");
		Protect.RequiredProgress = 1;
		Protect.Type = ESkyguardMissionObjectiveType::ProtectAsset;
		Protect.bFailureEndsMission = true;
		FSkyguardObjectiveDefinition Searchlight;
		Searchlight.ObjectiveId = TEXT("HoldSearchlightTrack");
		Searchlight.RequiredProgress = 3;
		FSkyguardObjectiveDefinition Defeat;
		Defeat.ObjectiveId = TEXT("DefeatBlackKite");
		Defeat.RequiredProgress = 4;
		Defeat.Type = ESkyguardMissionObjectiveType::BossPhase;
		Mission->Objectives = {Protect, Searchlight, Defeat};

		Mission->Boss.BossId = TEXT("BlackKite");
		Mission->Boss.DefeatObjectiveId = TEXT("DefeatBlackKite");
		Mission->Boss.MaximumBreakupPieces = 3;
		const FName WeakPointIds[] = {
			TEXT("PortNavigationVane"),
			TEXT("StarboardNavigationVane"),
			TEXT("Jammer"),
			TEXT("PowerBus")};
		const FName RequiredWeapons[] = {
			TEXT("Rifle"), TEXT("Rifle"),
			TEXT("Rifle"), TEXT("Igla")};
		const FName Exposes[] = {
			TEXT("Jammer"), TEXT("Jammer"),
			TEXT("PowerBus"), NAME_None};
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
				FName(*FString::Printf(TEXT("M04_Isolated_Wave_%d"), Index + 1));
			FSkyguardEnemyFormationDefinition Formation;
			Formation.FormationId =
				FName(*FString::Printf(TEXT("M04_Isolated_Form_%d"), Index + 1));
			Formation.UnitCount = Index + 2;
			Wave.Formations.Add(Formation);
			Mission->Waves.Add(Wave);
		}
		Mission->Weather.ProfileId = TEXT("BlackoutNight");
		Mission->Presentation.Briefing =
			FText::FromString(TEXT("Isolated Mission 4 night-blackout contract."));
		Mission->Presentation.RadioChatter = {
			FText::FromString(TEXT("Isolated radio 1")),
			FText::FromString(TEXT("Isolated radio 2")),
			FText::FromString(TEXT("Isolated radio 3"))};
		return Mission;
	}

	ASkyguardMission04IntegrationDirector* SpawnBoundDirector(UWorld* World)
	{
		ASkyguardMission04IntegrationDirector* Director =
			World->SpawnActor<ASkyguardMission04IntegrationDirector>();
		if (!Director)
		{
			return nullptr;
		}
		Director->bAutoInitialize = false;
		Director->bAllowBoundedActorSpawning = false;
		Director->BindRuntimeActors(nullptr, nullptr, nullptr, nullptr);
		return Director;
	}

	void AssertSearchlightRuntimeAsImplemented(
		FAutomationTestBase& Test,
		const ASkyguardMission04IntegrationDirector* Director,
		const bool bExpectedActive,
		const bool bExpectedBossTracked,
		const float ExpectedRemainingSeconds,
		const float ExpectedHeldSeconds,
		const int32 ExpectedCompletedPasses)
	{
		const FSkyguardSearchlightTrackRuntime& Searchlight =
			Director->GetSearchlightRuntime();
		if (bExpectedActive)
		{
			Test.TestTrue(
				TEXT("Searchlight Active matches implementation"),
				Searchlight.bActive);
		}
		else
		{
			Test.TestFalse(
				TEXT("Searchlight Active matches implementation"),
				Searchlight.bActive);
		}
		if (bExpectedBossTracked)
		{
			Test.TestTrue(
				TEXT("Searchlight BossTracked matches implementation"),
				Searchlight.bBossTracked);
		}
		else
		{
			Test.TestFalse(
				TEXT("Searchlight BossTracked matches implementation"),
				Searchlight.bBossTracked);
		}
		Test.TestEqual(
			TEXT("Searchlight RemainingSeconds matches implementation"),
			Searchlight.RemainingSeconds,
			ExpectedRemainingSeconds);
		Test.TestEqual(
			TEXT("Searchlight HeldSeconds matches implementation"),
			Searchlight.HeldSeconds,
			ExpectedHeldSeconds);
		Test.TestEqual(
			TEXT("Searchlight CompletedPasses matches implementation"),
			Searchlight.CompletedPasses,
			ExpectedCompletedPasses);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission04DirectorMissionIdNullContractAndSearchlightTest,
	"Skyguard52.Mission04.Director.MissionIdNullContractAndSearchlight",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission04DirectorMissionIdNullContractAndSearchlightTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission04IntegrationDirectorTests;

	TestEqual(
		TEXT("GetMissionId is M04_NightBlackout"),
		ASkyguardMission04IntegrationDirector::GetMissionId(),
		FName(TEXT("M04_NightBlackout")));

	TArray<FText> NullContractErrors;
	TestFalse(
		TEXT("ValidateMissionContract rejects a null definition"),
		ASkyguardMission04IntegrationDirector::ValidateMissionContract(
			nullptr, NullContractErrors));
	TestTrue(
		TEXT("Null contract reports at least one error"),
		NullContractErrors.Num() > 0);

	FWorldScope Scope;
	ASkyguardMission04IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(TEXT("Director spawns without Yak, Gunner, or BlackKite"), Director);
	if (!Director)
	{
		return false;
	}

	AssertSearchlightRuntimeAsImplemented(*this, Director, false, false, 0.f, 0.f, 0);

	// StartSearchlightWindow requires BlackKite, WindowSeconds > 0, an inactive
	// window, and WaveActive/BossEngaged. Isolated nullptr bind stays Briefing.
	TestFalse(
		TEXT("StartSearchlightWindow is fail-closed without BlackKite"),
		Director->StartSearchlightWindow(5.f));
	AssertSearchlightRuntimeAsImplemented(*this, Director, false, false, 0.f, 0.f, 0);

	TestFalse(
		TEXT("AdvanceSearchlightTrack is fail-closed while the window is inactive"),
		Director->AdvanceSearchlightTrack(1.f, true));
	AssertSearchlightRuntimeAsImplemented(*this, Director, false, false, 0.f, 0.f, 0);

	// Completing RequiredTrackSeconds increments CompletedPasses only after an
	// active window holds the boss. That window cannot open without BlackKite.
	TestFalse(
		TEXT("RequiredTrackSeconds cannot complete a pass without an active window"),
		Director->AdvanceSearchlightTrack(Director->RequiredTrackSeconds, true));
	AssertSearchlightRuntimeAsImplemented(*this, Director, false, false, 0.f, 0.f, 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission04DirectorContractSearchlightAndSubstationTest,
	"Skyguard52.Mission04.Director.ContractSearchlightAndSubstationIntegrity",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission04DirectorContractSearchlightAndSubstationTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission04IntegrationDirectorTests;

	USkyguardMissionDefinition* Mission = TryLoadMission();
	if (Mission)
	{
		TArray<FText> Errors;
		TestTrue(
			TEXT("Loaded Mission 4 contract validates"),
			ASkyguardMission04IntegrationDirector::ValidateMissionContract(
				Mission, Errors));
		TestEqual(TEXT("Loaded contract emits no errors"), Errors.Num(), 0);
	}
	else
	{
		AddWarning(TEXT(
			"Mission 4 DataAsset unavailable; using an isolated in-memory "
			"contract so public-API searchlight and substation tests still run."));
		Mission = MakeIsolatedNightBlackoutDefinition();
		TArray<FText> IsolatedErrors;
		if (!ASkyguardMission04IntegrationDirector::ValidateMissionContract(
				Mission, IsolatedErrors))
		{
			AddError(TEXT("Isolated Mission 4 contract must validate."));
			return false;
		}
	}

	FWorldScope Scope;
	ASkyguardMission04IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(TEXT("Director binds nullptr map/Yak/Gunner/BlackKite"), Director);
	if (!Director)
	{
		return false;
	}

	TestTrue(
		TEXT("Director configures from the isolated or loaded mission"),
		Director->ConfigureMissionDefinition(Mission));
	TestEqual(
		TEXT("ConfigureMissionDefinition resets substation integrity"),
		Director->GetSubstationIntegrity(),
		Director->MaximumSubstationIntegrity);
	AssertSearchlightRuntimeAsImplemented(*this, Director, false, false, 0.f, 0.f, 0);

	TestFalse(
		TEXT("StartSearchlightWindow stays fail-closed without BlackKite after configure"),
		Director->StartSearchlightWindow(5.f));
	TestFalse(
		TEXT("AdvanceSearchlightTrack stays fail-closed after a rejected window"),
		Director->AdvanceSearchlightTrack(Director->RequiredTrackSeconds, true));
	AssertSearchlightRuntimeAsImplemented(*this, Director, false, false, 0.f, 0.f, 0);

	const int32 PartialDamage = 25;
	TestTrue(
		TEXT("Substation accepts bounded damage"),
		Director->NotifySubstationDamage(PartialDamage));
	TestEqual(
		TEXT("Substation integrity drops by the applied damage"),
		Director->GetSubstationIntegrity(),
		Director->MaximumSubstationIntegrity - PartialDamage);
	TestEqual(
		TEXT("Partial substation damage does not fail the mission"),
		Director->GetWaveState(),
		ESkyguardMission04WaveState::AwaitingWave);

	TestTrue(
		TEXT("Wiping MaximumSubstationIntegrity is accepted"),
		Director->NotifySubstationDamage(Director->MaximumSubstationIntegrity));
	TestEqual(TEXT("Wiped substation integrity is zero"), Director->GetSubstationIntegrity(), 0);
	TestEqual(
		TEXT("Wiping the substation fails the mission"),
		Director->GetWaveState(),
		ESkyguardMission04WaveState::Failed);

	USkyguardObjectiveRuntime* Objectives = Director->GetObjectiveRuntime();
	TestNotNull(TEXT("Local objective runtime exists after configure"), Objectives);
	if (Objectives)
	{
		TestTrue(
			TEXT("Protection objective records terminal failure"),
			Objectives->HasTerminalFailure());
	}

	TestFalse(
		TEXT("Further substation damage is rejected after wipe"),
		Director->NotifySubstationDamage(1));
	TestEqual(
		TEXT("Wiped integrity stays zero"),
		Director->GetSubstationIntegrity(),
		0);
	return true;
}

#endif
