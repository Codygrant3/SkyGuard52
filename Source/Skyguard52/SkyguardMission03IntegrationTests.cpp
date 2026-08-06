#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission03IntegrationDirector.h"

#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardGunner.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardRoadHunterBoss.h"
#include "SkyguardYak52Aircraft.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardMission03IntegrationTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M03_ConvoyEscort.DA_Mission_M03_ConvoyEscort");

	class FScopedWorld
	{
	public:
		FScopedWorld()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission03IntegrationTestWorld"));
			check(World);
			FWorldContext& Context =
				GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
		}
		~FScopedWorld()
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
			ASkyguardMission03IntegrationDirector::GetMissionId();
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
			Anchor.ObjectiveId = Mission->Objectives[Index].ObjectiveId;
			Anchor.WorldLocation =
				FVector(46000.f + Index * 12000.f, 50000.f, 100.f);
			Assembly->ObjectiveAnchors.Add(Anchor);
		}
		for (int32 Index = 0; Index < 3; ++Index)
		{
			FSkyguardMissionLandmarkAnchor Landmark;
			Landmark.LandmarkId =
				FName(*FString::Printf(TEXT("M03_TestLandmark_%d"), Index));
			Landmark.Role =
				FName(*FString::Printf(TEXT("M03_TestRole_%d"), Index));
			Landmark.WorldLocation =
				FVector(18000.f + Index * 30000.f, 78000.f, 0.f);
			Landmark.bMissionExclusive = Index < 2;
			Assembly->LandmarkAnchors.Add(Landmark);
		}
		Assembly->RebuildRouteSpline();
	}

	bool Rifle(
		ASkyguardRoadHunterBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint, ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}

	bool ClearAllWaves(ASkyguardMission03IntegrationDirector* Director)
	{
		const int32 ExpectedCounts[] = {2, 3, 4};
		for (const int32 Expected : ExpectedCounts)
		{
			if (!Director->StartNextWave() ||
				Director->GetRemainingThreatsInWave() != Expected ||
				!Director->NotifyThreatDestroyed(Expected))
			{
				return false;
			}
		}
		return Director->GetWaveState() ==
			ESkyguardMission03WaveState::BossEngaged;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission03ContractRouteWaveTest,
	"Skyguard52.Mission03.Integration.GovernedContractRouteAndWaves",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission03ContractRouteWaveTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission03IntegrationTests;
	USkyguardMissionDefinition* Mission = LoadMission();
	TestNotNull(TEXT("Governed Mission 3 DataAsset loads"), Mission);
	if (!Mission)
	{
		return false;
	}
	TArray<FText> Errors;
	TestTrue(
		TEXT("Mission 3 contract validates"),
		ASkyguardMission03IntegrationDirector::ValidateMissionContract(
			Mission, Errors));
	TestEqual(TEXT("Mission contract emits no errors"), Errors.Num(), 0);

	FScopedWorld TestWorld;
	ASkyguardMissionMapAssemblyDirector* Assembly =
		TestWorld.Get()->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardMission03IntegrationDirector* Director =
		TestWorld.Get()->SpawnActor<ASkyguardMission03IntegrationDirector>();
	ConfigureAssembly(Assembly, Mission);
	Director->bAutoInitialize = false;
	TestTrue(TEXT("Definition configures"), Director->ConfigureMissionDefinition(Mission));
	Director->BindRuntimeActors(Assembly, nullptr, nullptr, nullptr);
	TestTrue(TEXT("Three waves progress 2, 3, 4 threats"), ClearAllWaves(Director));
	TestEqual(
		TEXT("Convoy begins advancing with first wave"),
		Director->GetConvoyRouteState(),
		ESkyguardConvoyRouteState::Advancing);
	TestTrue(
		TEXT("Convoy advances deterministically to tunnel"),
		Director->AdvanceConvoyByDistance(1000000.f));
	TestEqual(
		TEXT("Convoy records tunnel arrival"),
		Director->GetConvoyRouteState(),
		ESkyguardConvoyRouteState::TunnelReached);
	TestEqual(TEXT("Convoy route alpha clamps to one"), Director->GetConvoyRouteAlpha(), 1.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission03PlayableIglaTest,
	"Skyguard52.Mission03.Integration.PlayableCompositionIglaAndObjectives",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission03PlayableIglaTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission03IntegrationTests;
	FScopedWorld TestWorld;
	UWorld* World = TestWorld.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardMissionMapAssemblyDirector* Assembly =
		World->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardYak52Aircraft* Aircraft =
		World->SpawnActor<ASkyguardYak52Aircraft>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	ASkyguardRoadHunterBoss* Boss =
		World->SpawnActor<ASkyguardRoadHunterBoss>();
	ASkyguardMission03IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission03IntegrationDirector>();
	if (!Mission || !Assembly || !Aircraft || !Gunner || !Boss || !Director)
	{
		AddError(TEXT("Required Mission 3 test object failed to spawn."));
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
	TestTrue(TEXT("Mission 3 playable systems compose"), Director->InitializePlayableMission());
	const FSkyguardMission03IntegrationReadiness& Ready = Director->GetReadiness();
	TestTrue(TEXT("Map assembly validates"), Ready.bMapAssemblyReady);
	TestTrue(TEXT("Convoy spline validates"), Ready.bConvoyRouteReady);
	TestTrue(TEXT("Road Hunter validates"), Ready.bRoadHunterReady);
	TestTrue(TEXT("Core playable readiness is green"), Director->IsCorePlayableReady());
	TestTrue(TEXT("Three waves clear"), ClearAllWaves(Director));
	TestTrue(TEXT("Convoy reaches tunnel"), Director->AdvanceConvoyByDistance(1000000.f));

	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestEqual(
		TEXT("Pilot command reaches Yak"),
		Aircraft->GetPilotCommand(),
		ESkyguardPilotCommand::OrbitLeft);
	TestTrue(TEXT("Rifle blinds camera"), Rifle(Boss, Boss->TargetingCamera));
	TestTrue(TEXT("Rifle destroys left actuator"), Rifle(Boss, Boss->LeftActuator));
	TestTrue(TEXT("Rifle destroys right actuator"), Rifle(Boss, Boss->RightActuator));
	TestTrue(
		TEXT("Igla destroys exposed engine"),
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
		TEXT("Camera objective completes once"),
		Objectives->GetProgress(TEXT("BlindTargetingCamera")).CurrentProgress,
		1);
	TestEqual(
		TEXT("Four boss points complete Road Hunter objective"),
		Objectives->GetProgress(TEXT("DefeatRoadHunter")).CurrentProgress,
		4);
	TestEqual(
		TEXT("Tunnel arrival with surviving convoy completes protection"),
		Objectives->GetProgress(TEXT("ProtectConvoyCore")).CurrentProgress,
		1);
	TestTrue(TEXT("Required objectives complete"), Objectives->AreRequiredObjectivesComplete());
	TestEqual(
		TEXT("Mission reaches completed state"),
		Director->GetWaveState(),
		ESkyguardMission03WaveState::Completed);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission03RifleFallbackFailureTest,
	"Skyguard52.Mission03.Integration.OrbitRifleFallbackAndConvoyFailure",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission03RifleFallbackFailureTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission03IntegrationTests;
	FScopedWorld TestWorld;
	UWorld* World = TestWorld.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardRoadHunterBoss* Boss =
		World->SpawnActor<ASkyguardRoadHunterBoss>();
	ASkyguardMission03IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission03IntegrationDirector>();
	if (!Mission || !Boss || !Director)
	{
		AddError(TEXT("Emergency route test setup failed."));
		return false;
	}
	Director->bAutoInitialize = false;
	TestTrue(TEXT("Mission definition configures"), Director->ConfigureMissionDefinition(Mission));
	Director->BindRuntimeActors(nullptr, nullptr, nullptr, Boss);
	World->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}
	TestTrue(TEXT("Rifle blinds camera"), Rifle(Boss, Boss->TargetingCamera));
	TestTrue(TEXT("Rifle destroys left actuator"), Rifle(Boss, Boss->LeftActuator));
	TestTrue(TEXT("Rifle destroys right actuator"), Rifle(Boss, Boss->RightActuator));
	TestFalse(TEXT("Fallback rejects without orbit"), Boss->ArmEmergencyRifleFinish());
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	TestTrue(TEXT("Orbit arms rifle fallback"), Boss->ArmEmergencyRifleFinish());
	TestFalse(TEXT("Fallback closes Igla lock"), Boss->IsIglaLockEligible());
	TestTrue(TEXT("Rifle destroys fallback engine"), Rifle(Boss, Boss->Engine));
	TestEqual(TEXT("Fallback defeats Road Hunter"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);
	TestEqual(TEXT("Fallback still destroys four governed points"), Boss->GetTelemetry().WeakPointsDestroyed, 4);

	ASkyguardMission03IntegrationDirector* FailureDirector =
		World->SpawnActor<ASkyguardMission03IntegrationDirector>();
	FailureDirector->bAutoInitialize = false;
	TestTrue(TEXT("Failure runtime configures"), FailureDirector->ConfigureMissionDefinition(Mission));
	TestTrue(
		TEXT("Catastrophic convoy damage is accepted"),
		FailureDirector->NotifyConvoyDamage(
			FailureDirector->MaximumConvoyIntegrity));
	TestEqual(TEXT("Convoy integrity reaches zero"), FailureDirector->GetConvoyIntegrity(), 0);
	TestEqual(
		TEXT("Convoy route records destruction"),
		FailureDirector->GetConvoyRouteState(),
		ESkyguardConvoyRouteState::Destroyed);
	TestEqual(
		TEXT("Convoy loss fails mission"),
		FailureDirector->GetWaveState(),
		ESkyguardMission03WaveState::Failed);
	TestTrue(
		TEXT("Protected objective records terminal failure"),
		FailureDirector->GetObjectiveRuntime()->HasTerminalFailure());
	return true;
}

#endif
