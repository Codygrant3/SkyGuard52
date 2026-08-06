#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission07IntegrationDirector.h"

#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardGunner.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardRadarGhostBoss.h"
#include "SkyguardYak52Aircraft.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardMission07IntegrationTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M07_SearchIntercept.DA_Mission_M07_SearchIntercept");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission07IntegrationTestWorld"));
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
			ASkyguardMission07IntegrationDirector::GetMissionId();
		Assembly->AssemblyRevision = TEXT("CampaignMapAssembly_v1");
		Assembly->SkylineStyle =
			ESkyguardMissionSkylineStyle::IslandSearch;
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
				FVector(34000.f + Index * 16000.f, -5000.f, 100.f);
			Assembly->ObjectiveAnchors.Add(Anchor);
		}
		const FName Roles[] = {
			FName(TEXT("RadarObjective")),
			FName(TEXT("NavigationReference")),
			FName(TEXT("IdentificationTraffic"))};
		for (int32 Index = 0; Index < 3; ++Index)
		{
			FSkyguardMissionLandmarkAnchor Landmark;
			Landmark.LandmarkId =
				FName(*FString::Printf(TEXT("M07_TestLandmark_%d"), Index));
			Landmark.Role = Roles[Index];
			Landmark.WorldLocation =
				FVector(17000.f + Index * 18000.f, 23000.f, 0.f);
			Landmark.bMissionExclusive = true;
			Assembly->LandmarkAnchors.Add(Landmark);
		}
		Assembly->RebuildRouteSpline();
	}

	bool Identify(ASkyguardMission07IntegrationDirector* Director)
	{
		return Director->ClassifyFalseTrack(FName(TEXT("FalseTrack_A"))) &&
			Director->ClassifyFalseTrack(FName(TEXT("FalseTrack_B"))) &&
			Director->GetSearchSector() ==
				ESkyguardSearchSector::SectorB &&
			Director->ClassifyFalseTrack(FName(TEXT("FalseTrack_C"))) &&
			Director->ConfirmRadarGhostIdentification(true, true, true);
	}

	bool ClearWaves(ASkyguardMission07IntegrationDirector* Director)
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
			ESkyguardMission07WaveState::BossEngaged;
	}

	bool Rifle(
		ASkyguardRadarGhostBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint, ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission07ContractSearchTest,
	"Skyguard52.Mission07.Integration.GovernedContractSearchWavesAndProtection",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission07ContractSearchTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission07IntegrationTests;
	USkyguardMissionDefinition* Mission = LoadMission();
	TestNotNull(TEXT("Governed Mission 7 DataAsset loads"), Mission);
	if (!Mission)
	{
		return false;
	}
	TArray<FText> Errors;
	TestTrue(
		TEXT("Mission 7 contract validates"),
		ASkyguardMission07IntegrationDirector::ValidateMissionContract(
			Mission, Errors));
	TestEqual(TEXT("Contract emits no errors"), Errors.Num(), 0);

	FWorldScope Scope;
	ASkyguardMissionMapAssemblyDirector* Assembly =
		Scope.Get()->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardRadarGhostBoss* Boss =
		Scope.Get()->SpawnActor<ASkyguardRadarGhostBoss>();
	ASkyguardMission07IntegrationDirector* Director =
		Scope.Get()->SpawnActor<ASkyguardMission07IntegrationDirector>();
	ConfigureAssembly(Assembly, Mission);
	Director->bAutoInitialize = false;
	TestTrue(TEXT("Definition configures"), Director->ConfigureMissionDefinition(Mission));
	Director->BindRuntimeActors(Assembly, nullptr, nullptr, Boss);
	TestFalse(TEXT("Engagement cannot start before identification"), Director->StartNextWave());
	TestTrue(TEXT("Two-sector identification completes"), Identify(Director));
	TestEqual(TEXT("Three false tracks classified"), Director->GetClassifiedFalseTrackCount(), 3);
	TestTrue(TEXT("Hostile contact is confirmed"), Director->IsHostileContactConfirmed());
	TestTrue(TEXT("Three governed waves clear"), ClearWaves(Director));
	TestTrue(
		TEXT("Bounded fishing-fleet damage applies"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission07ProtectedTarget::FishingFleet, 20));
	TestEqual(TEXT("Both protected targets survive"), Director->GetSurvivingTargetCount(), 2);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission07PlayableCompositionTest,
	"Skyguard52.Mission07.Integration.PlayableIdentificationBilateralAndIgla",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission07PlayableCompositionTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission07IntegrationTests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardMissionMapAssemblyDirector* Assembly =
		World->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardYak52Aircraft* Aircraft =
		World->SpawnActor<ASkyguardYak52Aircraft>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	ASkyguardRadarGhostBoss* Boss =
		World->SpawnActor<ASkyguardRadarGhostBoss>();
	ASkyguardMission07IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission07IntegrationDirector>();
	if (!Mission || !Assembly || !Aircraft || !Gunner || !Boss || !Director)
	{
		AddError(TEXT("Mission 7 setup failed."));
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
	TestTrue(TEXT("Mission 7 systems compose"), Director->InitializePlayableMission());
	TestTrue(TEXT("Core playable readiness is green"), Director->IsCorePlayableReady());
	TestTrue(TEXT("Identification gate completes"), Identify(Director));
	TestTrue(TEXT("All waves clear"), ClearWaves(Director));

	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestEqual(TEXT("Left orbit reaches Yak"), Aircraft->GetPilotCommand(), ESkyguardPilotCommand::OrbitLeft);
	TestTrue(TEXT("Left orbit exposes modulator"), Boss->OpenOrbitExposure());
	TestTrue(TEXT("Rifle destroys modulator"), Rifle(Boss, Boss->SignatureModulator));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	TestEqual(TEXT("Right orbit reaches Yak"), Aircraft->GetPilotCommand(), ESkyguardPilotCommand::OrbitRight);
	TestTrue(TEXT("Right orbit exposes receiver"), Boss->OpenOrbitExposure());
	TestTrue(TEXT("Rifle destroys receiver"), Rifle(Boss, Boss->RadarReceiver));
	TestTrue(TEXT("Rifle opens cooling door"), Rifle(Boss, Boss->CoolingDoor));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Pursuit);
	TestTrue(TEXT("Rear aspect opens Igla"), Boss->OpenRearAspectIglaWindow());
	TestTrue(
		TEXT("Igla destroys engine"),
		Boss->ApplyIglaStrike(
			Boss->Engine->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector));
	Director->SynchronizeRuntimeState();

	USkyguardObjectiveRuntime* Objectives = Director->GetObjectiveRuntime();
	TestNotNull(TEXT("Objective runtime remains available"), Objectives);
	if (!Objectives)
	{
		return false;
	}
	TestEqual(
		TEXT("Classification objective completes"),
		Objectives->GetProgress(TEXT("ClassifyFalseTracks")).CurrentProgress,
		3);
	TestEqual(
		TEXT("Four points complete boss objective"),
		Objectives->GetProgress(TEXT("DefeatRadarGhost")).CurrentProgress, 4);
	TestEqual(
		TEXT("Protection objective completes"),
		Objectives->GetProgress(TEXT("ProtectRadarChain")).CurrentProgress, 1);
	TestEqual(
		TEXT("Mission completes"),
		Director->GetWaveState(),
		ESkyguardMission07WaveState::Completed);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission07FallbackFailureTest,
	"Skyguard52.Mission07.Integration.BreakRifleFallbackAndReinforcementFailure",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission07FallbackFailureTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission07IntegrationTests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardRadarGhostBoss* Boss =
		World->SpawnActor<ASkyguardRadarGhostBoss>();
	ASkyguardMission07IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission07IntegrationDirector>();
	if (!Mission || !Boss || !Director)
	{
		AddError(TEXT("Mission 7 fallback setup failed."));
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
	Boss->SetContactIdentified(true);
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestTrue(TEXT("Left orbit exposes modulator"), Boss->OpenOrbitExposure());
	TestTrue(TEXT("Rifle destroys modulator"), Rifle(Boss, Boss->SignatureModulator));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	TestTrue(TEXT("Right orbit exposes receiver"), Boss->OpenOrbitExposure());
	TestTrue(TEXT("Rifle destroys receiver"), Rifle(Boss, Boss->RadarReceiver));
	TestTrue(TEXT("Rifle destroys cooling door"), Rifle(Boss, Boss->CoolingDoor));
	TestFalse(TEXT("Fallback rejects without Break"), Boss->ArmBreakRifleFinish());
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Break);
	TestTrue(TEXT("Break arms rifle fallback"), Boss->ArmBreakRifleFinish());
	TestFalse(TEXT("Fallback closes Igla lock"), Boss->IsIglaLockEligible());
	TestTrue(TEXT("Rifle destroys engine"), Rifle(Boss, Boss->Engine));
	TestEqual(TEXT("Fallback defeats Radar Ghost"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);

	ASkyguardMission07IntegrationDirector* FailureDirector =
		World->SpawnActor<ASkyguardMission07IntegrationDirector>();
	ASkyguardRadarGhostBoss* FailureBoss =
		World->SpawnActor<ASkyguardRadarGhostBoss>();
	FailureDirector->bAutoInitialize = false;
	TestTrue(TEXT("Failure runtime configures"), FailureDirector->ConfigureMissionDefinition(Mission));
	FailureDirector->BindRuntimeActors(nullptr, nullptr, nullptr, FailureBoss);
	TestTrue(TEXT("Failure search identifies contact"), Identify(FailureDirector));
	TestTrue(TEXT("Failure waves clear"), ClearWaves(FailureDirector));
	TestTrue(
		TEXT("Reinforcement timer advances to deadline"),
		FailureDirector->AdvanceReinforcementTimer(
			FailureDirector->ReinforcementDeadlineSeconds));
	TestEqual(
		TEXT("Reinforcement transmission fails mission"),
		FailureDirector->GetWaveState(),
		ESkyguardMission07WaveState::Failed);
	TestTrue(
		TEXT("Protection objective records terminal failure"),
		FailureDirector->GetObjectiveRuntime()->HasTerminalFailure());
	return true;
}

#endif
