#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission06IntegrationDirector.h"

#include "SkyguardMissionDefinition.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardMission06IntegrationTests.cpp.
// Public director API only: nullptr map/Yak/Gunner/RunwayBreaker, no actor
// spawn, no rifle/Igla hits, no day-beat kit edits.

namespace SkyguardMission06IntegrationDirectorTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M06_AirfieldDefense.DA_Mission_M06_AirfieldDefense");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission06DirectorTestWorld"));
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

	USkyguardMissionDefinition* MakeIsolatedAirfieldDefinition()
	{
		USkyguardMissionDefinition* Mission =
			NewObject<USkyguardMissionDefinition>();
		Mission->MissionId =
			ASkyguardMission06IntegrationDirector::GetMissionId();
		Mission->DisplayName = FText::FromString(TEXT("Airfield Defense"));
		for (int32 Index = 0; Index < 4; ++Index)
		{
			FSkyguardRoutePoint Point;
			Point.PointId =
				FName(*FString::Printf(TEXT("M06_Isolated_P%d"), Index));
			Point.WorldLocation = FVector(Index * 14000.f, 0.f, 6000.f);
			Mission->Route.Points.Add(Point);
		}

		FSkyguardObjectiveDefinition Protect;
		Protect.ObjectiveId = TEXT("ProtectAirfieldAssets");
		Protect.RequiredProgress = 1;
		FSkyguardObjectiveDefinition Jam;
		Jam.ObjectiveId = TEXT("JamPayloadRacks");
		Jam.RequiredProgress = 2;
		FSkyguardObjectiveDefinition Defeat;
		Defeat.ObjectiveId = TEXT("DefeatRunwayBreaker");
		Defeat.RequiredProgress = 4;
		Mission->Objectives = {Protect, Jam, Defeat};

		Mission->Boss.BossId = TEXT("RunwayBreaker");
		Mission->Boss.DefeatObjectiveId = TEXT("DefeatRunwayBreaker");
		Mission->Boss.MaximumBreakupPieces = 3;
		const FName WeakPointIds[] = {
			TEXT("RunwayRack"),
			TEXT("HangarRack"),
			TEXT("HeatManifold"),
			TEXT("PortEngine")};
		const FName RequiredWeapons[] = {
			TEXT("Rifle"), TEXT("Rifle"),
			TEXT("Rifle"), TEXT("Igla")};
		const FName Exposes[] = {
			TEXT("HeatManifold"), TEXT("HeatManifold"),
			TEXT("PortEngine"), NAME_None};
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
				FName(*FString::Printf(TEXT("M06_Isolated_Wave_%d"), Index + 1));
			FSkyguardEnemyFormationDefinition Formation;
			Formation.FormationId = FName(
				*FString::Printf(TEXT("M06_Isolated_Form_%d"), Index + 1));
			Formation.UnitCount = Index + 2;
			Wave.Formations.Add(Formation);
			Mission->Waves.Add(Wave);
		}
		Mission->Weather.ProfileId = TEXT("AirfieldHaze");
		Mission->Presentation.Briefing =
			FText::FromString(TEXT("Isolated Mission 6 airfield contract."));
		Mission->Presentation.RadioChatter = {
			FText::FromString(TEXT("Isolated radio 1")),
			FText::FromString(TEXT("Isolated radio 2")),
			FText::FromString(TEXT("Isolated radio 3"))};
		return Mission;
	}

	ASkyguardMission06IntegrationDirector* SpawnBoundDirector(UWorld* World)
	{
		ASkyguardMission06IntegrationDirector* Director =
			World->SpawnActor<ASkyguardMission06IntegrationDirector>();
		if (!Director)
		{
			return nullptr;
		}
		Director->bAutoInitialize = false;
		Director->bAllowBoundedActorSpawning = false;
		Director->BindRuntimeActors(nullptr, nullptr, nullptr, nullptr);
		return Director;
	}

	void AssertPayloadWindowAsImplemented(
		FAutomationTestBase& Test,
		const ASkyguardMission06IntegrationDirector* Director,
		const bool bExpectedActive,
		const ESkyguardAirfieldTarget ExpectedTarget,
		const float ExpectedRemainingSeconds,
		const bool bExpectedJammed)
	{
		const FSkyguardPayloadWindowRuntime& Window =
			Director->GetPayloadWindow();
		if (bExpectedActive)
		{
			Test.TestTrue(
				TEXT("Payload window Active matches implementation"),
				Window.bActive);
		}
		else
		{
			Test.TestFalse(
				TEXT("Payload window Active matches implementation"),
				Window.bActive);
		}
		Test.TestEqual(
			TEXT("Payload window Target matches implementation"),
			Window.Target,
			ExpectedTarget);
		Test.TestEqual(
			TEXT("Payload window RemainingSeconds matches implementation"),
			Window.RemainingSeconds,
			ExpectedRemainingSeconds);
		if (bExpectedJammed)
		{
			Test.TestTrue(
				TEXT("Payload window bJammed matches implementation"),
				Window.bJammed);
		}
		else
		{
			Test.TestFalse(
				TEXT("Payload window bJammed matches implementation"),
				Window.bJammed);
		}
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission06DirectorMissionIdNullContractAndPayloadFailClosedTest,
	"Skyguard52.Mission06.Director.MissionIdNullContractAndPayloadFailClosed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission06DirectorMissionIdNullContractAndPayloadFailClosedTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission06IntegrationDirectorTests;

	TestEqual(
		TEXT("GetMissionId is M06_AirfieldDefense"),
		ASkyguardMission06IntegrationDirector::GetMissionId(),
		FName(TEXT("M06_AirfieldDefense")));

	TArray<FText> NullContractErrors;
	TestFalse(
		TEXT("ValidateMissionContract rejects a null definition"),
		ASkyguardMission06IntegrationDirector::ValidateMissionContract(
			nullptr, NullContractErrors));
	TestTrue(
		TEXT("Null contract reports at least one error"),
		NullContractErrors.Num() > 0);

	FWorldScope Scope;
	ASkyguardMission06IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(
		TEXT("Director spawns without Yak, Gunner, or RunwayBreaker"),
		Director);
	if (!Director)
	{
		return false;
	}

	TestFalse(
		TEXT("StartPayloadWindow is fail-closed before configure"),
		Director->StartPayloadWindow(ESkyguardAirfieldTarget::Runway, 4.f));
	TestFalse(
		TEXT("AdvancePayloadWindow is fail-closed while inactive"),
		Director->AdvancePayloadWindow(1.f));
	TestFalse(
		TEXT("TryJamActivePayload is fail-closed while inactive"),
		Director->TryJamActivePayload());
	AssertPayloadWindowAsImplemented(
		*this,
		Director,
		false,
		ESkyguardAirfieldTarget::Runway,
		0.f,
		false);
	TestEqual(
		TEXT("Unconfigured surviving target count is zero"),
		Director->GetSurvivingTargetCount(),
		0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission06DirectorPayloadWindowAndAirfieldTargetTest,
	"Skyguard52.Mission06.Director.PayloadWindowAndAirfieldTargetPublicApi",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission06DirectorPayloadWindowAndAirfieldTargetTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission06IntegrationDirectorTests;

	USkyguardMissionDefinition* Mission = TryLoadMission();
	if (Mission)
	{
		TArray<FText> Errors;
		TestTrue(
			TEXT("Loaded Mission 6 contract validates"),
			ASkyguardMission06IntegrationDirector::ValidateMissionContract(
				Mission, Errors));
		TestEqual(TEXT("Loaded contract emits no errors"), Errors.Num(), 0);
	}
	else
	{
		AddWarning(TEXT(
			"Mission 6 DataAsset unavailable; using an isolated in-memory "
			"contract so public-API payload and airfield-target tests still run."));
		Mission = MakeIsolatedAirfieldDefinition();
		TArray<FText> IsolatedErrors;
		if (!ASkyguardMission06IntegrationDirector::ValidateMissionContract(
				Mission, IsolatedErrors))
		{
			AddError(TEXT("Isolated Mission 6 contract must validate."));
			return false;
		}
	}

	FWorldScope Scope;
	ASkyguardMission06IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(
		TEXT("Director binds nullptr map/Yak/Gunner/RunwayBreaker"),
		Director);
	if (!Director)
	{
		return false;
	}

	TestTrue(
		TEXT("Director configures from the isolated or loaded mission"),
		Director->ConfigureMissionDefinition(Mission));
	TestEqual(
		TEXT("Three airfield targets start intact"),
		Director->GetSurvivingTargetCount(),
		3);
	TestFalse(
		TEXT("StartPayloadWindow is fail-closed before a wave is active"),
		Director->StartPayloadWindow(ESkyguardAirfieldTarget::Runway, 5.f));
	AssertPayloadWindowAsImplemented(
		*this,
		Director,
		false,
		ESkyguardAirfieldTarget::Runway,
		0.f,
		false);

	TestTrue(TEXT("First wave starts"), Director->StartNextWave());
	TestEqual(
		TEXT("Wave state is WaveActive"),
		Director->GetWaveState(),
		ESkyguardMission06WaveState::WaveActive);
	TestFalse(
		TEXT("StartPayloadWindow rejects a non-positive window"),
		Director->StartPayloadWindow(ESkyguardAirfieldTarget::Runway, 0.f));

	TestTrue(
		TEXT("Hangar payload window starts"),
		Director->StartPayloadWindow(ESkyguardAirfieldTarget::Hangars, 5.f));
	AssertPayloadWindowAsImplemented(
		*this,
		Director,
		true,
		ESkyguardAirfieldTarget::Hangars,
		5.f,
		false);
	TestFalse(
		TEXT("Second payload window is rejected while one is active"),
		Director->StartPayloadWindow(ESkyguardAirfieldTarget::Runway, 2.f));
	TestFalse(
		TEXT("TryJamActivePayload is fail-closed without RunwayBreaker"),
		Director->TryJamActivePayload());
	AssertPayloadWindowAsImplemented(
		*this,
		Director,
		true,
		ESkyguardAirfieldTarget::Hangars,
		5.f,
		false);

	TestFalse(
		TEXT("AdvancePayloadWindow rejects a non-positive delta"),
		Director->AdvancePayloadWindow(0.f));
	TestTrue(
		TEXT("Payload timer advances without jamming"),
		Director->AdvancePayloadWindow(2.f));
	AssertPayloadWindowAsImplemented(
		*this,
		Director,
		true,
		ESkyguardAirfieldTarget::Hangars,
		3.f,
		false);

	TestTrue(
		TEXT("Runway accepts bounded damage"),
		Director->NotifyAirfieldTargetDamage(
			ESkyguardAirfieldTarget::Runway, 15));
	const FSkyguardAirfieldTargetRuntime RunwayAfterHit =
		Director->GetTargetRuntime(ESkyguardAirfieldTarget::Runway);
	TestEqual(
		TEXT("Runway integrity drops by the applied damage"),
		RunwayAfterHit.Integrity,
		Director->MaximumTargetIntegrity - 15);
	TestFalse(TEXT("Damaged runway is not destroyed"), RunwayAfterHit.bDestroyed);

	TestTrue(
		TEXT("Hangars accept bounded damage"),
		Director->NotifyAirfieldTargetDamage(
			ESkyguardAirfieldTarget::Hangars, 20));
	const FSkyguardAirfieldTargetRuntime HangarsAfterHit =
		Director->GetTargetRuntime(ESkyguardAirfieldTarget::Hangars);
	TestEqual(
		TEXT("Hangar integrity drops by the applied damage"),
		HangarsAfterHit.Integrity,
		Director->MaximumTargetIntegrity - 20);
	TestFalse(TEXT("Damaged hangars are not destroyed"), HangarsAfterHit.bDestroyed);

	TestTrue(
		TEXT("Parked aircraft accept bounded damage"),
		Director->NotifyAirfieldTargetDamage(
			ESkyguardAirfieldTarget::ParkedAircraft, 25));
	const FSkyguardAirfieldTargetRuntime ParkedAfterHit =
		Director->GetTargetRuntime(ESkyguardAirfieldTarget::ParkedAircraft);
	TestEqual(
		TEXT("Parked-aircraft integrity drops by the applied damage"),
		ParkedAfterHit.Integrity,
		Director->MaximumTargetIntegrity - 25);
	TestFalse(
		TEXT("Damaged parked aircraft are not destroyed"),
		ParkedAfterHit.bDestroyed);
	TestEqual(
		TEXT("All three targets still survive after partial damage"),
		Director->GetSurvivingTargetCount(),
		3);

	TestTrue(
		TEXT("Wiping parked aircraft is accepted"),
		Director->NotifyAirfieldTargetDamage(
			ESkyguardAirfieldTarget::ParkedAircraft,
			Director->MaximumTargetIntegrity));
	const FSkyguardAirfieldTargetRuntime WipedParked =
		Director->GetTargetRuntime(ESkyguardAirfieldTarget::ParkedAircraft);
	TestEqual(
		TEXT("Wiped parked-aircraft integrity is zero"),
		WipedParked.Integrity,
		0);
	TestTrue(
		TEXT("Wiped parked aircraft are marked destroyed"),
		WipedParked.bDestroyed);
	TestEqual(
		TEXT("Surviving target count drops after one wipe"),
		Director->GetSurvivingTargetCount(),
		2);

	TestTrue(
		TEXT("Remaining hangar window expires without a jam"),
		Director->AdvancePayloadWindow(3.f));
	AssertPayloadWindowAsImplemented(
		*this,
		Director,
		false,
		ESkyguardAirfieldTarget::Hangars,
		0.f,
		false);
	TestTrue(
		TEXT("Expired hangar payload destroys hangars"),
		Director->GetTargetRuntime(ESkyguardAirfieldTarget::Hangars).bDestroyed);
	TestEqual(
		TEXT("Two wipes leave one surviving target"),
		Director->GetSurvivingTargetCount(),
		1);
	return true;
}

#endif
