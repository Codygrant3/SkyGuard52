#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission01IntegrationDirector.h"

#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardGunner.h"
#include "SkyguardMission01EnvironmentDirector.h"
#include "SkyguardMissionBriefingComponent.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardPathfinderBoss.h"
#include "SkyguardSortiePresentationComponent.h"
#include "SkyguardYak52Aircraft.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardMission01IntegrationTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M01_CoastalIntercept.DA_Mission_M01_CoastalIntercept");

	class FScopedWorld
	{
	public:
		FScopedWorld()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game,
				false,
				TEXT("SkyguardMission01IntegrationAutomationWorld"));
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
			nullptr,
			MissionAssetPath);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission01BriefingContractTest,
	"Skyguard52.Mission01Integration.BriefingGateAndGovernedContract",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission01BriefingContractTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission01IntegrationTests;

	USkyguardMissionDefinition* Mission = LoadMission();
	TestNotNull(TEXT("Governed Mission 1 DataAsset loads"), Mission);
	if (!Mission)
	{
		return false;
	}

	TArray<FText> Errors;
	TestTrue(
		TEXT("Governed Mission 1 satisfies the playable integration contract"),
		ASkyguardMission01IntegrationDirector::ValidateMissionContract(
			Mission,
			Errors));
	TestEqual(TEXT("Mission contract emits no errors"), Errors.Num(), 0);

	USkyguardMissionBriefingComponent* Briefing =
		NewObject<USkyguardMissionBriefingComponent>(GetTransientPackage());
	TestTrue(
		TEXT("Briefing configures from governed presentation data"),
		Briefing->ConfigureFromMission(Mission));
	TestEqual(
		TEXT("All three authored radio lines reach the briefing"),
		Briefing->GetRadioChatter().Num(),
		3);
	TestFalse(
		TEXT("Briefing cannot launch before assets and reading time are ready"),
		Briefing->CanLaunch());

	Briefing->SetAssetsReady(true);
	Briefing->AdvanceBriefing(
		FMath::Max(0.f, Briefing->GetMinimumWarmupSeconds() - 0.1f));
	TestFalse(
		TEXT("Asset readiness does not bypass minimum briefing time"),
		Briefing->CanLaunch());
	Briefing->AdvanceBriefing(0.2f);
	TestTrue(
		TEXT("Briefing becomes ready after assets and minimum time"),
		Briefing->CanLaunch());
	TestTrue(
		TEXT("Ready briefing acknowledges and launches exactly once"),
		Briefing->AcknowledgeAndLaunch());
	TestEqual(
		TEXT("Briefing records launched state"),
		Briefing->GetBriefingState(),
		ESkyguardMissionBriefingState::Launched);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission01PlayableRuntimeTest,
	"Skyguard52.Mission01Integration.PlayableRuntimeCompositionAndProgression",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission01PlayableRuntimeTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission01IntegrationTests;

	FScopedWorld TestWorld;
	UWorld* World = TestWorld.Get();
	ASkyguardMission01EnvironmentDirector* Environment =
		World->SpawnActor<ASkyguardMission01EnvironmentDirector>();
	ASkyguardYak52Aircraft* Aircraft =
		World->SpawnActor<ASkyguardYak52Aircraft>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	ASkyguardPathfinderBoss* Boss =
		World->SpawnActor<ASkyguardPathfinderBoss>();
	ASkyguardMission01IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission01IntegrationDirector>();

	TestNotNull(TEXT("Environment director spawns"), Environment);
	TestNotNull(TEXT("Yak runtime spawns"), Aircraft);
	TestNotNull(TEXT("Rear gunner spawns"), Gunner);
	TestNotNull(TEXT("Pathfinder runtime spawns"), Boss);
	TestNotNull(TEXT("Mission integration director spawns"), Director);
	if (!Environment || !Aircraft || !Gunner || !Boss || !Director)
	{
		return false;
	}

	Director->bAutoInitialize = false;
	Director->bAllowBoundedActorSpawning = false;
	World->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}

	TestTrue(
		TEXT("Mission director composes the accepted systems"),
		Director->InitializePlayableMission());
	const FSkyguardMission01IntegrationReadiness& Ready =
		Director->GetReadiness();
	TestTrue(TEXT("Accepted coastline is ready"), Ready.bEnvironmentReady);
	TestTrue(TEXT("Validated Yak runtime is ready"), Ready.bYakRuntimeReady);
	TestTrue(TEXT("Rear gunner is mounted"), Ready.bGunnerReady);
	TestTrue(TEXT("Pathfinder gameplay runtime is ready"), Ready.bPathfinderReady);
	TestTrue(TEXT("Governed objective runtime is ready"), Ready.bObjectivesReady);
	TestTrue(TEXT("Briefing component is configured"), Ready.bBriefingReady);
	TestTrue(TEXT("Audio and radio components are present"), Ready.bAudioReady);
	TestTrue(TEXT("Dense sortie presentation model is configured"),
		Ready.bSortiePresentationReady);
	TestEqual(TEXT("Exactly three objectives are governed"), Ready.ObjectiveCount, 3);
	TestEqual(TEXT("Exactly three radio lines are governed"), Ready.RadioLineCount, 3);
	TestTrue(TEXT("Core playable contract is green"), Director->IsCorePlayableReady());
	TestTrue(
		TEXT("Gunner is attached to the aircraft"),
		Gunner->GetAttachParentActor() == Aircraft);

	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestEqual(
		TEXT("Pathfinder pilot commands reach the Yak runtime"),
		Aircraft->GetPilotCommand(),
		ESkyguardPilotCommand::OrbitLeft);

	const FVector HitLocation(100.f, 0.f, 0.f);
	const FVector HitDirection(1.f, 0.f, 0.f);
	TestTrue(
		TEXT("Rifle destroys Pathfinder command antenna"),
		Boss->ApplyWeaponHit(
			Boss->CommandAntenna,
			ESkyguardBossWeapon::Rifle,
			Boss->CommandAntenna->MaxIntegrity,
			HitLocation,
			HitDirection));
	Director->SynchronizeRuntimeState();
	TestTrue(
		TEXT("Rifle destroys Pathfinder nose camera"),
		Boss->ApplyWeaponHit(
			Boss->NoseCamera,
			ESkyguardBossWeapon::Rifle,
			Boss->NoseCamera->MaxIntegrity,
			HitLocation,
			HitDirection));
	Director->SynchronizeRuntimeState();
	TestTrue(
		TEXT("Igla destroys exposed Pathfinder engine"),
		Boss->ApplyIglaStrike(
			Boss->Engine->MaxIntegrity,
			HitLocation,
			HitDirection));
	Director->SynchronizeRuntimeState();
	TestTrue(
		TEXT("Rifle destroys exposed Pathfinder control linkage"),
		Boss->ApplyWeaponHit(
			Boss->ControlLinkage,
			ESkyguardBossWeapon::Rifle,
			Boss->ControlLinkage->MaxIntegrity,
			HitLocation,
			HitDirection));
	Director->SynchronizeRuntimeState();

	USkyguardObjectiveRuntime* Objectives = Director->GetObjectiveRuntime();
	TestNotNull(TEXT("Objective runtime remains available after boss defeat"), Objectives);
	if (!Objectives)
	{
		return false;
	}
	TestEqual(
		TEXT("All four boss weak points advance the boss objective"),
		Objectives->GetProgress(TEXT("DefeatPathfinder")).CurrentProgress,
		4);
	TestEqual(
		TEXT("Two rifle disarm points complete the optional network objective"),
		Objectives->GetProgress(TEXT("DisableCommandNetwork")).CurrentProgress,
		2);
	TestEqual(
		TEXT("Surviving radar completes the protect objective at victory"),
		Objectives->GetProgress(TEXT("ProtectCoastalRadar")).CurrentProgress,
		1);
	TestTrue(
		TEXT("Required Mission 1 objectives are complete"),
		Objectives->AreRequiredObjectivesComplete());
	TestFalse(
		TEXT("Mission 1 does not record a terminal protection failure"),
		Objectives->HasTerminalFailure());
	return true;
}

#endif
