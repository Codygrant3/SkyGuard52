#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission04IntegrationDirector.h"

#include "SkyguardBlackKiteBoss.h"
#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardGunner.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardYak52Aircraft.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardMission04IntegrationTests
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
				TEXT("SkyguardMission04IntegrationTestWorld"));
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
			ASkyguardMission04IntegrationDirector::GetMissionId();
		Assembly->AssemblyRevision = TEXT("CampaignMapAssembly_v1");
		Assembly->SkylineStyle =
			ESkyguardMissionSkylineStyle::BlackoutUrban;
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
				FVector(32000.f + Index * 9000.f, 26000.f, 100.f);
			Assembly->ObjectiveAnchors.Add(Anchor);
		}
		for (int32 Index = 0; Index < 3; ++Index)
		{
			const FName Roles[] = {
				TEXT("SearchlightBatteryPort"),
				TEXT("SearchlightBatteryStarboard"),
				TEXT("DarkUrbanSkyline")
			};
			FSkyguardMissionLandmarkAnchor Landmark;
			Landmark.LandmarkId =
				FName(*FString::Printf(TEXT("M04_TestLandmark_%d"), Index));
			Landmark.Role = Roles[Index];
			Landmark.WorldLocation =
				FVector(18000.f + Index * 26000.f, 30000.f, 0.f);
			Landmark.bMissionExclusive = Index < 2;
			Assembly->LandmarkAnchors.Add(Landmark);
		}
		Assembly->RebuildRouteSpline();
	}

	bool Rifle(
		ASkyguardBlackKiteBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint, ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}

	bool ClearWaves(ASkyguardMission04IntegrationDirector* Director)
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
			ESkyguardMission04WaveState::BossEngaged;
	}

	bool CompleteSearchlightPass(
		ASkyguardMission04IntegrationDirector* Director)
	{
		return Director->StartSearchlightWindow(5.f) &&
			Director->AdvanceSearchlightTrack(3.f, true);
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission04ContractSearchlightTest,
	"Skyguard52.Mission04.Integration.GovernedContractWavesAndSearchlight",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission04ContractSearchlightTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission04IntegrationTests;
	USkyguardMissionDefinition* Mission = LoadMission();
	TestNotNull(TEXT("Governed Mission 4 DataAsset loads"), Mission);
	if (!Mission)
	{
		return false;
	}
	TArray<FText> Errors;
	TestTrue(
		TEXT("Mission 4 contract validates"),
		ASkyguardMission04IntegrationDirector::ValidateMissionContract(
			Mission, Errors));
	TestEqual(TEXT("Contract emits no errors"), Errors.Num(), 0);

	FWorldScope Scope;
	ASkyguardMissionMapAssemblyDirector* Assembly =
		Scope.Get()->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardBlackKiteBoss* Boss =
		Scope.Get()->SpawnActor<ASkyguardBlackKiteBoss>();
	ASkyguardMission04IntegrationDirector* Director =
		Scope.Get()->SpawnActor<ASkyguardMission04IntegrationDirector>();
	ConfigureAssembly(Assembly, Mission);
	Director->bAutoInitialize = false;
	TestTrue(TEXT("Definition configures"), Director->ConfigureMissionDefinition(Mission));
	Director->BindRuntimeActors(Assembly, nullptr, nullptr, Boss);
	TestTrue(TEXT("Three governed waves clear"), ClearWaves(Director));
	for (int32 Index = 0; Index < 3; ++Index)
	{
		TestTrue(TEXT("Searchlight track completes"), CompleteSearchlightPass(Director));
	}
	TestEqual(
		TEXT("Three searchlight passes recorded"),
		Director->GetSearchlightRuntime().CompletedPasses, 3);
	TestEqual(
		TEXT("Exclusive objective reaches three"),
		Director->GetObjectiveRuntime()
			->GetProgress(TEXT("HoldSearchlightTrack")).CurrentProgress,
		3);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission04PlayableCompositionTest,
	"Skyguard52.Mission04.Integration.PlayableCompositionSearchlightJammerAndIgla",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission04PlayableCompositionTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission04IntegrationTests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardMissionMapAssemblyDirector* Assembly =
		World->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardYak52Aircraft* Aircraft =
		World->SpawnActor<ASkyguardYak52Aircraft>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	ASkyguardBlackKiteBoss* Boss =
		World->SpawnActor<ASkyguardBlackKiteBoss>();
	ASkyguardMission04IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission04IntegrationDirector>();
	if (!Mission || !Assembly || !Aircraft || !Gunner || !Boss || !Director)
	{
		AddError(TEXT("Mission 4 setup failed."));
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
	TestTrue(TEXT("Mission 4 systems compose"), Director->InitializePlayableMission());
	const FSkyguardMission04IntegrationReadiness& Ready = Director->GetReadiness();
	TestTrue(TEXT("Mission definition validates"), Ready.bMissionDefinitionValid);
	TestTrue(TEXT("Campaign definition validates"), Ready.bCampaignDefinitionValid);
	TestTrue(TEXT("Map assembly validates"), Ready.bMapAssemblyReady);
	TestTrue(TEXT("Yak runtime validates"), Ready.bYakRuntimeReady);
	TestTrue(TEXT("Gunner is mounted"), Ready.bGunnerReady);
	TestTrue(TEXT("Black Kite validates"), Ready.bBlackKiteReady);
	TestTrue(TEXT("Objectives validate"), Ready.bObjectivesReady);
	TestTrue(TEXT("Three waves validate"), Ready.bWavesReady);
	TestTrue(TEXT("Searchlights validate"), Ready.bSearchlightsReady);
	TestTrue(TEXT("Substation validates"), Ready.bSubstationReady);
	TestTrue(TEXT("Briefing validates"), Ready.bBriefingReady);
	TestTrue(TEXT("Audio routing validates"), Ready.bAudioReady);
	TestTrue(TEXT("Core playable readiness is green"), Director->IsCorePlayableReady());
	TestTrue(TEXT("All waves clear"), ClearWaves(Director));
	for (int32 Index = 0; Index < 3; ++Index)
	{
		TestTrue(TEXT("Required searchlight pass completes"), CompleteSearchlightPass(Director));
	}
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestEqual(TEXT("Pilot command reaches Yak"), Aircraft->GetPilotCommand(), ESkyguardPilotCommand::OrbitLeft);
	TestTrue(TEXT("Searchlight reveals port vane"), Rifle(Boss, Boss->PortNavigationVane));
	TestTrue(TEXT("Searchlight reveals starboard vane"), Rifle(Boss, Boss->StarboardNavigationVane));
	TestTrue(TEXT("Rifle destroys exposed jammer"), Rifle(Boss, Boss->Jammer));
	TestTrue(
		TEXT("Igla destroys exposed power bus"),
		Boss->ApplyIglaStrike(
			Boss->PowerBus->MaxIntegrity,
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
		TEXT("Four points complete boss objective"),
		Objectives->GetProgress(TEXT("DefeatBlackKite")).CurrentProgress, 4);
	TestEqual(
		TEXT("Substation survives"),
		Director->GetSubstationIntegrity(),
		Director->MaximumSubstationIntegrity);
	TestEqual(
		TEXT("Protection objective completes"),
		Objectives->GetProgress(TEXT("ProtectSubstation")).CurrentProgress, 1);
	TestEqual(
		TEXT("Mission completes"),
		Director->GetWaveState(),
		ESkyguardMission04WaveState::Completed);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission04FallbackFailureTest,
	"Skyguard52.Mission04.Integration.OrbitRifleFallbackAndSubstationFailure",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission04FallbackFailureTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission04IntegrationTests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardBlackKiteBoss* Boss =
		World->SpawnActor<ASkyguardBlackKiteBoss>();
	ASkyguardMission04IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission04IntegrationDirector>();
	if (!Mission || !Boss || !Director)
	{
		AddError(TEXT("Mission 4 fallback setup failed."));
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
	Boss->SetSearchlightTracked(true);
	TestTrue(TEXT("Rifle destroys port vane"), Rifle(Boss, Boss->PortNavigationVane));
	TestTrue(TEXT("Rifle destroys starboard vane"), Rifle(Boss, Boss->StarboardNavigationVane));
	TestTrue(TEXT("Rifle destroys jammer"), Rifle(Boss, Boss->Jammer));
	TestFalse(TEXT("Fallback rejects without orbit"), Boss->ArmEmergencyRifleFinish());
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	TestTrue(TEXT("Orbit arms rifle fallback"), Boss->ArmEmergencyRifleFinish());
	TestFalse(TEXT("Fallback closes Igla lock"), Boss->IsIglaLockEligible());
	TestTrue(TEXT("Rifle destroys power bus"), Rifle(Boss, Boss->PowerBus));
	TestEqual(TEXT("Fallback defeats Black Kite"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);

	ASkyguardMission04IntegrationDirector* FailureDirector =
		World->SpawnActor<ASkyguardMission04IntegrationDirector>();
	FailureDirector->bAutoInitialize = false;
	TestTrue(TEXT("Failure runtime configures"), FailureDirector->ConfigureMissionDefinition(Mission));
	TestTrue(
		TEXT("Catastrophic substation damage is accepted"),
		FailureDirector->NotifySubstationDamage(
			FailureDirector->MaximumSubstationIntegrity));
	TestEqual(TEXT("Substation reaches zero"), FailureDirector->GetSubstationIntegrity(), 0);
	TestEqual(
		TEXT("Substation loss fails mission"),
		FailureDirector->GetWaveState(),
		ESkyguardMission04WaveState::Failed);
	TestTrue(
		TEXT("Protection objective records terminal failure"),
		FailureDirector->GetObjectiveRuntime()->HasTerminalFailure());
	return true;
}

#endif
