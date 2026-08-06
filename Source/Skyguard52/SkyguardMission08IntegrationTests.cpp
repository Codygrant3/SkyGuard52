#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission08IntegrationDirector.h"

#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardGunner.h"
#include "SkyguardLifelineHunterBoss.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardYak52Aircraft.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardMission08IntegrationTests
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
				TEXT("SkyguardMission08IntegrationTestWorld"));
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

	USkyguardMissionDefinition* LoadMission()
	{
		return LoadObject<USkyguardMissionDefinition>(
			nullptr, MissionAssetPath);
	}

	void ConfigureAssembly(
		ASkyguardMissionMapAssemblyDirector* Assembly,
		USkyguardMissionDefinition* Mission)
	{
		Assembly->MissionDefinition = Mission;
		Assembly->MissionId =
			ASkyguardMission08IntegrationDirector::GetMissionId();
		Assembly->AssemblyRevision = TEXT("CampaignMapAssembly_v1");
		Assembly->SkylineStyle =
			ESkyguardMissionSkylineStyle::CoastalHighway;
		Assembly->WeatherProfileId = Mission->Weather.ProfileId;
		for (const FSkyguardRoutePoint& Point : Mission->Route.Points)
		{
			Assembly->RoutePoints.Add(Point.WorldLocation);
		}
		for (int32 Index = 0; Index < Mission->Objectives.Num(); ++Index)
		{
			FSkyguardMissionObjectiveAnchor Anchor;
			Anchor.ObjectiveId =
				Mission->Objectives[Index].ObjectiveId;
			Anchor.WorldLocation =
				FVector(39000.f + Index * 9000.f, 18000.f, 100.f);
			Assembly->ObjectiveAnchors.Add(Anchor);
		}
		const FName Roles[] = {
			FName(TEXT("AnimatedRescueFlightProxy")),
			FName(TEXT("HoistObjectiveProxy")),
			FName(TEXT("MaritimeRescueProxy"))};
		for (int32 Index = 0; Index < 3; ++Index)
		{
			FSkyguardMissionLandmarkAnchor Landmark;
			Landmark.LandmarkId =
				FName(*FString::Printf(TEXT("M08_TestLandmark_%d"), Index));
			Landmark.Role = Roles[Index];
			Landmark.WorldLocation =
				FVector(28000.f + Index * 7000.f, 3000.f, 0.f);
			Landmark.bMissionExclusive = true;
			Assembly->LandmarkAnchors.Add(Landmark);
		}
		Assembly->RebuildRouteSpline();
	}

	bool ClearWaves(ASkyguardMission08IntegrationDirector* Director)
	{
		const int32 ExpectedCounts[] = {2, 3, 4};
		for (const int32 Count : ExpectedCounts)
		{
			if (!Director->StartNextWave() ||
				Director->GetRemainingThreatsInWave() != Count ||
				!Director->NotifyThreatDestroyed(Count))
			{
				return false;
			}
		}
		return Director->GetWaveState() ==
			ESkyguardMission08WaveState::BossEngaged;
	}

	bool CompleteHoists(ASkyguardMission08IntegrationDirector* Director)
	{
		for (int32 Index = 0; Index < 3; ++Index)
		{
			if (!Director->StartHoistWindow(6.f) ||
				!Director->AdvanceHoistWindow(4.f, true))
			{
				return false;
			}
		}
		return Director->GetHoistRuntime().CompletedWindows == 3;
	}

	bool Rifle(
		ASkyguardLifelineHunterBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint, ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission08ContractHoistTest,
	"Skyguard52.Mission08.Integration.GovernedContractWavesHoistsAndFriendlies",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission08ContractHoistTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission08IntegrationTests;
	USkyguardMissionDefinition* Mission = LoadMission();
	TestNotNull(TEXT("Governed Mission 8 DataAsset loads"), Mission);
	if (!Mission)
	{
		return false;
	}
	TArray<FText> Errors;
	TestTrue(
		TEXT("Mission 8 contract validates"),
		ASkyguardMission08IntegrationDirector::ValidateMissionContract(
			Mission, Errors));
	TestEqual(TEXT("Contract emits no errors"), Errors.Num(), 0);

	FWorldScope Scope;
	ASkyguardMissionMapAssemblyDirector* Assembly =
		Scope.Get()->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardLifelineHunterBoss* Boss =
		Scope.Get()->SpawnActor<ASkyguardLifelineHunterBoss>();
	ASkyguardMission08IntegrationDirector* Director =
		Scope.Get()->SpawnActor<ASkyguardMission08IntegrationDirector>();
	ConfigureAssembly(Assembly, Mission);
	Director->bAutoInitialize = false;
	TestTrue(TEXT("Definition configures"), Director->ConfigureMissionDefinition(Mission));
	Director->BindRuntimeActors(Assembly, nullptr, nullptr, Boss);
	TestTrue(TEXT("Three governed waves clear"), ClearWaves(Director));
	TestTrue(TEXT("Three hoist windows complete"), CompleteHoists(Director));
	TestFalse(
		TEXT("Friendly corridor rejects weapon release"),
		Director->ValidateWeaponRelease(900.f, true));
	TestFalse(
		TEXT("Insufficient separation rejects release"),
		Director->ValidateWeaponRelease(200.f, false));
	TestEqual(TEXT("Two unsafe releases recorded"), Director->GetRejectedWeaponReleases(), 2);
	TestTrue(TEXT("Safe separated release is accepted"), Director->ValidateWeaponRelease(700.f, false));
	TestEqual(TEXT("All three friendly groups survive"), Director->GetSurvivingTargetCount(), 3);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission08PlayableCompositionTest,
	"Skyguard52.Mission08.Integration.PlayableHoistSensorIglaAndSafeRedirect",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission08PlayableCompositionTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission08IntegrationTests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardMissionMapAssemblyDirector* Assembly =
		World->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardYak52Aircraft* Aircraft =
		World->SpawnActor<ASkyguardYak52Aircraft>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	ASkyguardLifelineHunterBoss* Boss =
		World->SpawnActor<ASkyguardLifelineHunterBoss>();
	ASkyguardMission08IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission08IntegrationDirector>();
	if (!Mission || !Assembly || !Aircraft || !Gunner || !Boss || !Director)
	{
		AddError(TEXT("Mission 8 setup failed."));
		return false;
	}
	ConfigureAssembly(Assembly, Mission);
	Director->bAutoInitialize = false;
	Director->bAllowBoundedActorSpawning = false;
	World->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}
	TestTrue(TEXT("Mission 8 systems compose"), Director->InitializePlayableMission());
	TestTrue(TEXT("Core playable readiness is green"), Director->IsCorePlayableReady());
	TestTrue(TEXT("All waves clear"), ClearWaves(Director));
	TestTrue(TEXT("All hoists complete"), CompleteHoists(Director));

	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestEqual(TEXT("Left orbit reaches Yak"), Aircraft->GetPilotCommand(), ESkyguardPilotCommand::OrbitLeft);
	TestTrue(TEXT("Left orbit exposes primary sensor"), Boss->OpenSensorExposure());
	TestTrue(TEXT("Rifle destroys optical tracker"), Rifle(Boss, Boss->OpticalTracker));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	TestTrue(TEXT("Right orbit exposes secondary sensor"), Boss->OpenSensorExposure());
	TestTrue(TEXT("Rifle destroys weapon servo"), Rifle(Boss, Boss->WeaponServo));
	TestTrue(TEXT("Rifle destroys countermeasure pod"), Rifle(Boss, Boss->CountermeasurePod));
	TestTrue(TEXT("Safe weapon release validates"), Director->ValidateWeaponRelease(700.f, false));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Extend);
	TestTrue(TEXT("Safe separation opens Igla"), Boss->OpenSafeIglaWindow());
	TestTrue(
		TEXT("Igla disables engine"),
		Boss->ApplyIglaStrike(
			Boss->Engine->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector));
	TestEqual(TEXT("Disabled drone remains critical"), Boss->GetBossPhase(), ESkyguardBossPhase::Critical);
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Break);
	TestTrue(TEXT("Break redirects wreckage"), Boss->RedirectDisabledDrone());
	Director->SynchronizeRuntimeState();

	USkyguardObjectiveRuntime* Objectives = Director->GetObjectiveRuntime();
	TestNotNull(TEXT("Objective runtime remains available"), Objectives);
	if (!Objectives)
	{
		return false;
	}
	TestEqual(
		TEXT("Three hoists complete objective"),
		Objectives->GetProgress(TEXT("CompleteHoistWindows")).CurrentProgress,
		3);
	TestEqual(
		TEXT("Four points complete boss objective"),
		Objectives->GetProgress(TEXT("DefeatLifelineHunter")).CurrentProgress,
		4);
	TestEqual(
		TEXT("Protection objective completes"),
		Objectives->GetProgress(TEXT("ProtectRescueFlight")).CurrentProgress,
		1);
	TestEqual(
		TEXT("Mission completes"),
		Director->GetWaveState(),
		ESkyguardMission08WaveState::Completed);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission08FallbackFailureTest,
	"Skyguard52.Mission08.Integration.RifleFallbackRedirectAndFriendlyFailure",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission08FallbackFailureTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission08IntegrationTests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardLifelineHunterBoss* Boss =
		World->SpawnActor<ASkyguardLifelineHunterBoss>();
	ASkyguardMission08IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission08IntegrationDirector>();
	if (!Mission || !Boss || !Director)
	{
		AddError(TEXT("Mission 8 fallback setup failed."));
		return false;
	}
	Director->bAutoInitialize = false;
	TestTrue(TEXT("Definition configures"), Director->ConfigureMissionDefinition(Mission));
	Director->BindRuntimeActors(nullptr, nullptr, nullptr, Boss);
	World->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestTrue(TEXT("Left orbit exposes tracker"), Boss->OpenSensorExposure());
	TestTrue(TEXT("Rifle destroys tracker"), Rifle(Boss, Boss->OpticalTracker));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	TestTrue(TEXT("Right orbit exposes servo"), Boss->OpenSensorExposure());
	TestTrue(TEXT("Rifle destroys servo"), Rifle(Boss, Boss->WeaponServo));
	TestTrue(TEXT("Rifle destroys countermeasure pod"), Rifle(Boss, Boss->CountermeasurePod));
	Boss->SetFriendlySeparationMeters(700.f);
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Break);
	TestTrue(TEXT("Break arms rifle engine fallback"), Boss->ArmSafeRifleEngineFallback());
	TestTrue(TEXT("Rifle disables engine"), Rifle(Boss, Boss->Engine));
	TestTrue(TEXT("Break redirects rifle-disabled drone"), Boss->RedirectDisabledDrone());
	TestEqual(TEXT("Fallback reaches safe defeat"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);

	ASkyguardMission08IntegrationDirector* FailureDirector =
		World->SpawnActor<ASkyguardMission08IntegrationDirector>();
	FailureDirector->bAutoInitialize = false;
	TestTrue(TEXT("Failure runtime configures"), FailureDirector->ConfigureMissionDefinition(Mission));
	TestTrue(
		TEXT("Catastrophic survivor damage applies"),
		FailureDirector->NotifyProtectedTargetDamage(
			ESkyguardMission08ProtectedTarget::SurvivorsAndRafts,
			FailureDirector->MaximumProtectedTargetIntegrity));
	TestEqual(
		TEXT("Friendly loss fails mission"),
		FailureDirector->GetWaveState(),
		ESkyguardMission08WaveState::Failed);
	TestTrue(
		TEXT("Protection objective records terminal failure"),
		FailureDirector->GetObjectiveRuntime()->HasTerminalFailure());
	return true;
}

#endif
