#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission10IntegrationDirector.h"

#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardGunner.h"
#include "SkyguardLastFlightBoss.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardYak52Aircraft.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardMission10IntegrationTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M10_EvacuationFinale.DA_Mission_M10_EvacuationFinale");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission10IntegrationTestWorld"));
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
			ASkyguardMission10IntegrationDirector::GetMissionId();
		Assembly->AssemblyRevision = TEXT("CampaignMapAssembly_v1");
		Assembly->SkylineStyle =
			ESkyguardMissionSkylineStyle::HarborIndustrial;
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
				FVector(55000.f + Index * 10000.f, 28000.f, 100.f);
			Assembly->ObjectiveAnchors.Add(Anchor);
		}
		const FName Roles[] = {
			FName(TEXT("EvacuationTerminalProxy")),
			FName(TEXT("EvacuationShipProxy")),
			FName(TEXT("CivilianConvoyProxy"))};
		for (int32 Index = 0; Index < 3; ++Index)
		{
			FSkyguardMissionLandmarkAnchor Landmark;
			Landmark.LandmarkId =
				FName(*FString::Printf(TEXT("M10_TestLandmark_%d"), Index));
			Landmark.Role = Roles[Index];
			Landmark.WorldLocation =
				FVector(47000.f + Index * 9000.f, 5000.f, 0.f);
			Landmark.bMissionExclusive = true;
			Assembly->LandmarkAnchors.Add(Landmark);
		}
		Assembly->RebuildRouteSpline();
	}

	bool ClearPhaseWaves(ASkyguardMission10IntegrationDirector* Director)
	{
		const int32 ExpectedCounts[] = {3, 4, 5};
		const ESkyguardMission10RoutePhase ExpectedPhases[] = {
			ESkyguardMission10RoutePhase::FerryTerminal,
			ESkyguardMission10RoutePhase::EvacuationShip,
			ESkyguardMission10RoutePhase::BossEngaged};
		for (int32 Index = 0; Index < 3; ++Index)
		{
			if (!Director->StartPhaseWave() ||
				Director->GetRemainingThreatsInWave() !=
					ExpectedCounts[Index] ||
				!Director->NotifyThreatDestroyed(ExpectedCounts[Index]) ||
				Director->GetRoutePhase() != ExpectedPhases[Index])
			{
				return false;
			}
		}
		return true;
	}

	bool Rifle(
		ASkyguardLastFlightBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint, ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}

	bool DefeatAndDivertLastFlight(ASkyguardLastFlightBoss* Boss)
	{
		Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
		if (!Boss->OpenGuidanceArrayExposure() ||
			!Rifle(Boss, Boss->PortGuidanceArray))
		{
			return false;
		}
		Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
		if (!Boss->OpenGuidanceArrayExposure() ||
			!Rifle(Boss, Boss->StarboardGuidanceArray) ||
			!Boss->BeginTerminalStrikeCycle() ||
			!Rifle(Boss, Boss->PortStrikeBayMechanism) ||
			!Rifle(Boss, Boss->StarboardStrikeBayMechanism) ||
			!Rifle(Boss, Boss->PortCoolingSystem) ||
			!Rifle(Boss, Boss->StarboardCoolingSystem))
		{
			return false;
		}
		Boss->SetCivilianSeparationMeters(800.f);
		Boss->IssuePilotCommand(ESkyguardPilotCommand::Extend);
		if (!Boss->OpenFirstIglaWindow() ||
			!Boss->ApplyIglaStrike(
				Boss->PortEngine->MaxIntegrity,
				FVector::ZeroVector,
				FVector::ForwardVector) ||
			!Boss->IssueClimbCommand() ||
			!Rifle(Boss, Boss->Jammer))
		{
			return false;
		}
		Boss->IssuePilotCommand(ESkyguardPilotCommand::Extend);
		if (!Boss->OpenFinalIglaWindow() ||
			!Boss->ApplyIglaStrike(
				Boss->StarboardEngine->MaxIntegrity,
				FVector::ZeroVector,
				FVector::ForwardVector))
		{
			return false;
		}
		Boss->IssuePilotCommand(ESkyguardPilotCommand::Pursuit);
		if (!Boss->ArmCommandCoreRiflePath() ||
			!Rifle(Boss, Boss->CommandCore))
		{
			return false;
		}
		Boss->IssuePilotCommand(ESkyguardPilotCommand::Break);
		return Boss->DivertWreckFromCivilians();
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission10ContractPhasesTest,
	"Skyguard52.Mission10.Integration.GovernedFinaleContractAndPhases",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission10ContractPhasesTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission10IntegrationTests;
	USkyguardMissionDefinition* Mission = LoadMission();
	TestNotNull(TEXT("Governed Mission 10 DataAsset loads"), Mission);
	if (!Mission)
	{
		return false;
	}
	TArray<FText> Errors;
	TestTrue(
		TEXT("Mission 10 contract validates"),
		ASkyguardMission10IntegrationDirector::ValidateMissionContract(
			Mission, Errors));
	TestEqual(TEXT("Contract emits no errors"), Errors.Num(), 0);

	FWorldScope Scope;
	ASkyguardMissionMapAssemblyDirector* Assembly =
		Scope.Get()->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardLastFlightBoss* Boss =
		Scope.Get()->SpawnActor<ASkyguardLastFlightBoss>();
	ASkyguardMission10IntegrationDirector* Director =
		Scope.Get()->SpawnActor<ASkyguardMission10IntegrationDirector>();
	ConfigureAssembly(Assembly, Mission);
	Director->bAutoInitialize = false;
	TestTrue(TEXT("Definition configures"), Director->ConfigureMissionDefinition(Mission));
	Director->BindRuntimeActors(Assembly, nullptr, nullptr, Boss);
	TestTrue(TEXT("Three phase-tied waves clear"), ClearPhaseWaves(Director));
	TestEqual(TEXT("Three protected groups survive"), Director->GetSurvivingProtectedGroupCount(), 3);
	TestEqual(
		TEXT("Three wave lanes record"),
		Director->GetObjectiveRuntime()
			->GetProgress(TEXT("ClearEvacuationLanes")).CurrentProgress,
		3);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission10PlayableFinaleTest,
	"Skyguard52.Mission10.Integration.PlayableEvacuationWavesBossAndSuccess",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission10PlayableFinaleTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission10IntegrationTests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardMissionMapAssemblyDirector* Assembly =
		World->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardYak52Aircraft* Aircraft =
		World->SpawnActor<ASkyguardYak52Aircraft>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	ASkyguardLastFlightBoss* Boss =
		World->SpawnActor<ASkyguardLastFlightBoss>();
	ASkyguardMission10IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission10IntegrationDirector>();
	if (!Mission || !Assembly || !Aircraft || !Gunner || !Boss || !Director)
	{
		AddError(TEXT("Mission 10 setup failed."));
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
	TestTrue(TEXT("Mission 10 systems compose"), Director->InitializePlayableMission());
	TestTrue(TEXT("Core playable readiness is green"), Director->IsCorePlayableReady());
	TestTrue(TEXT("Highway, terminal and ship waves clear"), ClearPhaseWaves(Director));
	TestTrue(TEXT("Safe civilian corridor validates"), Director->ValidateWeaponRelease(800.f, false));
	TestTrue(TEXT("Last Flight is defeated and diverted"), DefeatAndDivertLastFlight(Boss));
	Director->SynchronizeRuntimeState();

	USkyguardObjectiveRuntime* Objectives = Director->GetObjectiveRuntime();
	TestNotNull(TEXT("Objective runtime remains available"), Objectives);
	if (!Objectives)
	{
		return false;
	}
	TestEqual(
		TEXT("Four lane stages complete"),
		Objectives->GetProgress(TEXT("ClearEvacuationLanes")).CurrentProgress,
		4);
	TestEqual(
		TEXT("Four boss milestones complete"),
		Objectives->GetProgress(TEXT("DefeatLastFlight")).CurrentProgress,
		4);
	TestEqual(
		TEXT("Evacuation hub protection completes"),
		Objectives->GetProgress(TEXT("ProtectEvacuationHub")).CurrentProgress,
		1);
	TestEqual(
		TEXT("Finale completes"),
		Director->GetRoutePhase(),
		ESkyguardMission10RoutePhase::Completed);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission10SafetyFailureTest,
	"Skyguard52.Mission10.Integration.FriendlyCorridorAndDeterministicFailure",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission10SafetyFailureTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission10IntegrationTests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardLastFlightBoss* Boss =
		World->SpawnActor<ASkyguardLastFlightBoss>();
	ASkyguardMission10IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission10IntegrationDirector>();
	if (!Mission || !Boss || !Director)
	{
		AddError(TEXT("Mission 10 failure setup failed."));
		return false;
	}
	Director->bAutoInitialize = false;
	TestTrue(TEXT("Failure runtime configures"), Director->ConfigureMissionDefinition(Mission));
	Director->BindRuntimeActors(nullptr, nullptr, nullptr, Boss);
	TestFalse(
		TEXT("Civilian corridor blocks release"),
		Director->ValidateWeaponRelease(900.f, true));
	TestFalse(
		TEXT("Unsafe distance blocks release"),
		Director->ValidateWeaponRelease(250.f, false));
	TestEqual(TEXT("Two rejected releases record"), Director->GetRejectedWeaponReleases(), 2);
	TestTrue(
		TEXT("Catastrophic ferry-terminal damage applies"),
		Director->NotifyProtectedGroupDamage(
			ESkyguardMission10ProtectedGroup::FerryTerminal,
			Director->MaximumProtectedIntegrity));
	TestEqual(
		TEXT("Protected loss deterministically fails finale"),
		Director->GetRoutePhase(),
		ESkyguardMission10RoutePhase::Failed);
	TestTrue(
		TEXT("Protection objective records terminal failure"),
		Director->GetObjectiveRuntime()->HasTerminalFailure());
	TestFalse(
		TEXT("Failed finale cannot begin another wave"),
		Director->StartPhaseWave());
	return true;
}

#endif
