#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission02IntegrationDirector.h"

#include "SkyguardBreakwaterBoss.h"
#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardGunner.h"
#include "SkyguardMissionBriefingComponent.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardYak52Aircraft.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardMission02IntegrationTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M02_HarborShield.DA_Mission_M02_HarborShield");

	class FScopedWorld
	{
	public:
		FScopedWorld()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game,
				false,
				TEXT("SkyguardMission02IntegrationTestWorld"));
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
			ASkyguardMission02IntegrationDirector::GetMissionId();
		Assembly->AssemblyRevision = TEXT("CampaignMapAssembly_v1");
		Assembly->SkylineStyle =
			ESkyguardMissionSkylineStyle::HarborIndustrial;
		Assembly->WeatherProfileId = Mission->Weather.ProfileId;
		Assembly->RoutePoints.Reset();
		for (const FSkyguardRoutePoint& Point : Mission->Route.Points)
		{
			Assembly->RoutePoints.Add(Point.WorldLocation);
		}
		Assembly->ObjectiveAnchors.Reset();
		for (int32 Index = 0; Index < Mission->Objectives.Num(); ++Index)
		{
			FSkyguardMissionObjectiveAnchor Anchor;
			Anchor.ObjectiveId = Mission->Objectives[Index].ObjectiveId;
			Anchor.WorldLocation =
				FVector(70000.f + Index * 4000.f, 43000.f, 100.f);
			Assembly->ObjectiveAnchors.Add(Anchor);
		}
		Assembly->LandmarkAnchors.Reset();
		for (int32 Index = 0; Index < 3; ++Index)
		{
			FSkyguardMissionLandmarkAnchor Landmark;
			Landmark.LandmarkId =
				FName(*FString::Printf(TEXT("M02_TestLandmark_%d"), Index));
			Landmark.Role =
				FName(*FString::Printf(TEXT("M02_TestRole_%d"), Index));
			Landmark.WorldLocation =
				FVector(20000.f + Index * 25000.f, 70000.f, 0.f);
			Landmark.bMissionExclusive = Index < 2;
			Assembly->LandmarkAnchors.Add(Landmark);
		}
		Assembly->RebuildRouteSpline();
	}

	bool Rifle(
		ASkyguardBreakwaterBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint,
			ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector);
	}

	bool ClearAllWaves(ASkyguardMission02IntegrationDirector* Director)
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
		return
			Director->GetWaveState() ==
			ESkyguardMission02WaveState::BossEngaged;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission02ContractAndWavesTest,
	"Skyguard52.Mission02.Integration.GovernedContractAndWaveProgression",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission02ContractAndWavesTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission02IntegrationTests;

	USkyguardMissionDefinition* Mission = LoadMission();
	TestNotNull(TEXT("Governed Mission 2 DataAsset loads"), Mission);
	if (!Mission)
	{
		return false;
	}

	TArray<FText> Errors;
	TestTrue(
		TEXT("Mission 2 satisfies the playable contract"),
		ASkyguardMission02IntegrationDirector::ValidateMissionContract(
			Mission, Errors));
	TestEqual(TEXT("Contract emits no errors"), Errors.Num(), 0);

	FScopedWorld TestWorld;
	ASkyguardMission02IntegrationDirector* Director =
		TestWorld.Get()->SpawnActor<ASkyguardMission02IntegrationDirector>();
	TestNotNull(TEXT("Mission 2 director spawns"), Director);
	if (!Director)
	{
		return false;
	}
	Director->bAutoInitialize = false;
	TestTrue(
		TEXT("Governed definition configures deterministic wave runtime"),
		Director->ConfigureMissionDefinition(Mission));
	TestEqual(
		TEXT("Wave runtime begins awaiting first wave"),
		Director->GetWaveState(),
		ESkyguardMission02WaveState::AwaitingWave);
	TestTrue(
		TEXT("Three governed formations progress 2, 3, 4 threats"),
		ClearAllWaves(Director));
	TestEqual(TEXT("Final wave index is two"), Director->GetCurrentWaveIndex(), 2);
	TestEqual(TEXT("Final wave has no remaining threats"), Director->GetRemainingThreatsInWave(), 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission02PlayableIglaTest,
	"Skyguard52.Mission02.Integration.PlayableCompositionIglaAndObjectives",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission02PlayableIglaTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission02IntegrationTests;

	FScopedWorld TestWorld;
	UWorld* World = TestWorld.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardMissionMapAssemblyDirector* Assembly =
		World->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardYak52Aircraft* Aircraft =
		World->SpawnActor<ASkyguardYak52Aircraft>();
	ASkyguardGunner* Gunner =
		World->SpawnActor<ASkyguardGunner>();
	ASkyguardBreakwaterBoss* Boss =
		World->SpawnActor<ASkyguardBreakwaterBoss>();
	ASkyguardMission02IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission02IntegrationDirector>();
	TestNotNull(TEXT("Mission definition loads"), Mission);
	TestNotNull(TEXT("Map assembly spawns"), Assembly);
	TestNotNull(TEXT("Yak runtime spawns"), Aircraft);
	TestNotNull(TEXT("Rear gunner spawns"), Gunner);
	TestNotNull(TEXT("Breakwater runtime spawns"), Boss);
	TestNotNull(TEXT("Mission 2 integration director spawns"), Director);
	if (!Mission || !Assembly || !Aircraft || !Gunner || !Boss || !Director)
	{
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
	TestTrue(
		TEXT("Mission 2 composes accepted map and native runtimes"),
		Director->InitializePlayableMission());

	const FSkyguardMission02IntegrationReadiness& Ready =
		Director->GetReadiness();
	TestTrue(TEXT("Proxy map assembly validates"), Ready.bMapAssemblyReady);
	TestTrue(TEXT("Yak runtime validates"), Ready.bYakRuntimeReady);
	TestTrue(TEXT("Gunner is mounted"), Ready.bGunnerReady);
	TestTrue(TEXT("Breakwater runtime validates"), Ready.bBreakwaterReady);
	TestTrue(TEXT("Objectives validate"), Ready.bObjectivesReady);
	TestTrue(TEXT("Three waves validate"), Ready.bWavesReady);
	TestEqual(TEXT("Three objectives are governed"), Ready.ObjectiveCount, 3);
	TestEqual(TEXT("Three waves are governed"), Ready.WaveCount, 3);
	TestEqual(TEXT("Three radio lines are governed"), Ready.RadioLineCount, 3);
	TestTrue(TEXT("Core playable readiness is green"), Director->IsCorePlayableReady());
	TestTrue(TEXT("All waves clear into boss engagement"), ClearAllWaves(Director));

	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestEqual(
		TEXT("Boss pilot command reaches Yak runtime"),
		Aircraft->GetPilotCommand(),
		ESkyguardPilotCommand::OrbitLeft);

	TestTrue(TEXT("Rifle destroys port latch"), Rifle(Boss, Boss->PortLatch));
	TestTrue(TEXT("Rifle destroys starboard latch"), Rifle(Boss, Boss->StarboardLatch));
	TestTrue(TEXT("Rifle destroys decoys"), Rifle(Boss, Boss->DecoyPods));
	TestTrue(
		TEXT("Igla destroys exposed engine"),
		Boss->ApplyIglaStrike(
			Boss->Engine->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector));
	TestTrue(TEXT("Rifle finishes elevator linkage"), Rifle(Boss, Boss->ElevatorLinkage));
	Director->SynchronizeRuntimeState();

	USkyguardObjectiveRuntime* Objectives = Director->GetObjectiveRuntime();
	TestNotNull(TEXT("Objective runtime remains available"), Objectives);
	if (!Objectives)
	{
		return false;
	}
	TestEqual(
		TEXT("Four governed boss interactions complete defeat objective"),
		Objectives->GetProgress(TEXT("DefeatBreakwater")).CurrentProgress,
		4);
	TestEqual(
		TEXT("Two latches complete armor objective"),
		Objectives->GetProgress(TEXT("StripArmorPanels")).CurrentProgress,
		2);
	TestEqual(
		TEXT("Surviving terminal completes protection objective"),
		Objectives->GetProgress(TEXT("ProtectFuelTerminal")).CurrentProgress,
		1);
	TestTrue(TEXT("All required objectives complete"), Objectives->AreRequiredObjectivesComplete());
	TestEqual(
		TEXT("Completed mission reaches terminal wave state"),
		Director->GetWaveState(),
		ESkyguardMission02WaveState::Completed);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission02RifleOnlyFailureTest,
	"Skyguard52.Mission02.Integration.EmergencyRifleOnlyAndTerminalFailure",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission02RifleOnlyFailureTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission02IntegrationTests;

	FScopedWorld TestWorld;
	UWorld* World = TestWorld.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardBreakwaterBoss* Boss =
		World->SpawnActor<ASkyguardBreakwaterBoss>();
	ASkyguardMission02IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission02IntegrationDirector>();
	TestNotNull(TEXT("Mission definition loads"), Mission);
	TestNotNull(TEXT("Emergency-route Breakwater spawns"), Boss);
	TestNotNull(TEXT("Emergency-route director spawns"), Director);
	if (!Mission || !Boss || !Director)
	{
		return false;
	}
	Director->bAutoInitialize = false;
	Director->bAllowBoundedActorSpawning = false;
	TestTrue(TEXT("Mission definition configures"), Director->ConfigureMissionDefinition(Mission));
	Director->BindRuntimeActors(nullptr, nullptr, nullptr, Boss);
	World->BeginPlay();
	TestTrue(TEXT("All waves clear before boss resolution"), ClearAllWaves(Director));

	TestTrue(TEXT("Port latch accepts rifle"), Rifle(Boss, Boss->PortLatch));
	TestTrue(TEXT("Starboard latch accepts rifle"), Rifle(Boss, Boss->StarboardLatch));
	TestTrue(TEXT("Decoys accept rifle"), Rifle(Boss, Boss->DecoyPods));
	TestFalse(
		TEXT("Emergency finish requires an orbit command"),
		Boss->ArmEmergencyRifleFinish());
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	TestTrue(
		TEXT("Orbit exposes emergency rifle-only linkage"),
		Boss->ArmEmergencyRifleFinish());
	TestFalse(TEXT("Emergency route closes Igla lock"), Boss->IsIglaLockEligible());
	TestTrue(TEXT("Rifle severs emergency linkage"), Rifle(Boss, Boss->ElevatorLinkage));
	Director->SynchronizeRuntimeState();
	TestEqual(TEXT("Rifle-only route defeats Breakwater"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);
	TestEqual(
		TEXT("Rifle-only substitute still completes governed boss progress"),
		Director->GetObjectiveRuntime()
			->GetProgress(TEXT("DefeatBreakwater")).CurrentProgress,
		4);

	ASkyguardMission02IntegrationDirector* FailureDirector =
		World->SpawnActor<ASkyguardMission02IntegrationDirector>();
	FailureDirector->bAutoInitialize = false;
	TestTrue(
		TEXT("Failure director configures governed mission"),
		FailureDirector->ConfigureMissionDefinition(Mission));
	TestTrue(
		TEXT("Catastrophic terminal damage is accepted"),
		FailureDirector->NotifyFuelTerminalDamage(
			FailureDirector->MaximumFuelTerminalIntegrity));
	TestEqual(TEXT("Fuel terminal reaches zero integrity"), FailureDirector->GetFuelTerminalIntegrity(), 0);
	TestEqual(
		TEXT("Terminal loss enters failed wave state"),
		FailureDirector->GetWaveState(),
		ESkyguardMission02WaveState::Failed);
	TestTrue(
		TEXT("Protected objective records terminal failure"),
		FailureDirector->GetObjectiveRuntime()->HasTerminalFailure());
	return true;
}

#endif
