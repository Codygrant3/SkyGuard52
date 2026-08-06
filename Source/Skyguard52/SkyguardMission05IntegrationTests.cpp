#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission05IntegrationDirector.h"

#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardGunner.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardTempestBoss.h"
#include "SkyguardYak52Aircraft.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardMission05IntegrationTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M05_StormFront.DA_Mission_M05_StormFront");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission05IntegrationTestWorld"));
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
			ASkyguardMission05IntegrationDirector::GetMissionId();
		Assembly->AssemblyRevision = TEXT("CampaignMapAssembly_v1");
		Assembly->SkylineStyle =
			ESkyguardMissionSkylineStyle::OffshoreStorm;
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
				FVector(42000.f + Index * 14000.f, -12000.f, 0.f);
			Assembly->ObjectiveAnchors.Add(Anchor);
		}
	const FName Roles[] = {
			FName(TEXT("RescuePressure")),
			FName(TEXT("IndustrialOffshore")),
			FName(TEXT("NaturalFlightGate"))};
		for (int32 Index = 0; Index < 3; ++Index)
		{
			FSkyguardMissionLandmarkAnchor Landmark;
			Landmark.LandmarkId =
				FName(*FString::Printf(TEXT("M05_TestLandmark_%d"), Index));
			Landmark.Role = Roles[Index];
			Landmark.WorldLocation =
				FVector(18000.f + Index * 22000.f, 16000.f, 0.f);
			Landmark.bMissionExclusive = true;
			Assembly->LandmarkAnchors.Add(Landmark);
		}
		Assembly->RebuildRouteSpline();
	}

	bool Rifle(
		ASkyguardTempestBoss* Boss,
		USkyguardBossWeakPointComponent* WeakPoint)
	{
		return Boss->ApplyWeaponHit(
			WeakPoint, ESkyguardBossWeapon::Rifle,
			WeakPoint->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}

	bool ClearWaves(ASkyguardMission05IntegrationDirector* Director)
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
			ESkyguardMission05WaveState::BossEngaged;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission05ContractStormTest,
	"Skyguard52.Mission05.Integration.GovernedContractWavesStormAndProtection",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission05ContractStormTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission05IntegrationTests;
	USkyguardMissionDefinition* Mission = LoadMission();
	TestNotNull(TEXT("Governed Mission 5 DataAsset loads"), Mission);
	if (!Mission)
	{
		return false;
	}
	TArray<FText> Errors;
	TestTrue(
		TEXT("Mission 5 contract validates"),
		ASkyguardMission05IntegrationDirector::ValidateMissionContract(
			Mission, Errors));
	TestEqual(TEXT("Contract emits no errors"), Errors.Num(), 0);

	FWorldScope Scope;
	ASkyguardMissionMapAssemblyDirector* Assembly =
		Scope.Get()->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardTempestBoss* Boss =
		Scope.Get()->SpawnActor<ASkyguardTempestBoss>();
	ASkyguardMission05IntegrationDirector* Director =
		Scope.Get()->SpawnActor<ASkyguardMission05IntegrationDirector>();
	ConfigureAssembly(Assembly, Mission);
	Director->bAutoInitialize = false;
	TestTrue(TEXT("Definition configures"), Director->ConfigureMissionDefinition(Mission));
	Director->BindRuntimeActors(Assembly, nullptr, nullptr, Boss);
	TestTrue(TEXT("Three governed waves clear"), ClearWaves(Director));
	TestTrue(TEXT("Lightning window opens"), Director->TriggerLightningWindow(2.f));
	TestTrue(TEXT("Lightning window advances"), Director->AdvanceLightningWindow(2.f));
	TestFalse(TEXT("Lightning closes deterministically"), Director->GetStormRuntime().bLightningActive);
	TestEqual(TEXT("One lightning flash recorded"), Director->GetStormRuntime().LightningFlashCount, 1);
	TestTrue(
		TEXT("Bounded platform damage applies"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission05ProtectedTarget::OffshorePlatform, 25));
	TestEqual(TEXT("Both protected targets survive"), Director->GetSurvivingTargetCount(), 2);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission05PlayableCompositionTest,
	"Skyguard52.Mission05.Integration.PlayableCompositionLightningTurbulenceAndIgla",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission05PlayableCompositionTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission05IntegrationTests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardMissionMapAssemblyDirector* Assembly =
		World->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardYak52Aircraft* Aircraft =
		World->SpawnActor<ASkyguardYak52Aircraft>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	ASkyguardTempestBoss* Boss =
		World->SpawnActor<ASkyguardTempestBoss>();
	ASkyguardMission05IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission05IntegrationDirector>();
	if (!Mission || !Assembly || !Aircraft || !Gunner || !Boss || !Director)
	{
		AddError(TEXT("Mission 5 setup failed."));
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
	TestTrue(TEXT("Mission 5 systems compose"), Director->InitializePlayableMission());
	TestTrue(TEXT("Core playable readiness is green"), Director->IsCorePlayableReady());
	TestTrue(TEXT("All waves clear"), ClearWaves(Director));
	TestTrue(TEXT("Lightning exposes Tempest"), Director->TriggerLightningWindow(5.f));
	TestTrue(TEXT("Rifle destroys port boom"), Rifle(Boss, Boss->PortDischargeBoom));
	TestTrue(TEXT("Rifle destroys starboard boom"), Rifle(Boss, Boss->StarboardDischargeBoom));
	TestTrue(
		TEXT("Strong gust exposes corrective-bank servo"),
		Director->AdvanceTurbulence(1.f, 0.9f, false));
	TestTrue(TEXT("Rifle jams control servo"), Rifle(Boss, Boss->ControlServo));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Extend);
	TestEqual(TEXT("Extend command reaches Yak"), Aircraft->GetPilotCommand(), ESkyguardPilotCommand::Extend);
	TestTrue(
		TEXT("Player stabilizes Igla lock through storm"),
		Director->AdvanceTurbulence(8.f, 0.85f, true));
	TestTrue(TEXT("Igla lock becomes eligible"), Boss->IsIglaLockEligible());
	TestTrue(
		TEXT("Igla destroys exposed intake"),
		Boss->ApplyIglaStrike(
			Boss->EngineIntake->MaxIntegrity,
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
		TEXT("Both discharge booms complete objective"),
		Objectives->GetProgress(TEXT("DisableDischargeBooms")).CurrentProgress,
		2);
	TestEqual(
		TEXT("Four weak points complete boss objective"),
		Objectives->GetProgress(TEXT("DefeatTempest")).CurrentProgress, 4);
	TestEqual(TEXT("Both protected targets survive"), Director->GetSurvivingTargetCount(), 2);
	TestEqual(
		TEXT("Protection objective completes"),
		Objectives->GetProgress(TEXT("ProtectOffshoreCrew")).CurrentProgress,
		1);
	TestEqual(
		TEXT("Mission completes"),
		Director->GetWaveState(),
		ESkyguardMission05WaveState::Completed);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission05FallbackFailureTest,
	"Skyguard52.Mission05.Integration.BreakRifleFallbackAndProtectedTargetFailure",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission05FallbackFailureTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission05IntegrationTests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardTempestBoss* Boss =
		World->SpawnActor<ASkyguardTempestBoss>();
	ASkyguardMission05IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission05IntegrationDirector>();
	if (!Mission || !Boss || !Director)
	{
		AddError(TEXT("Mission 5 fallback setup failed."));
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
	Boss->SetLightningExposed(true);
	TestTrue(TEXT("Rifle destroys port boom"), Rifle(Boss, Boss->PortDischargeBoom));
	TestTrue(TEXT("Rifle destroys starboard boom"), Rifle(Boss, Boss->StarboardDischargeBoom));
	TestTrue(TEXT("Strong gust exposes servo"), Boss->ApplyCorrectiveBankGust(0.9f));
	TestTrue(TEXT("Rifle destroys servo"), Rifle(Boss, Boss->ControlServo));
	TestFalse(TEXT("Fallback rejects without Break"), Boss->ArmBreakRifleFinish());
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Break);
	TestTrue(TEXT("Break arms rifle fallback"), Boss->ArmBreakRifleFinish());
	TestFalse(TEXT("Fallback closes Igla lock"), Boss->IsIglaLockEligible());
	TestTrue(TEXT("Rifle destroys intake"), Rifle(Boss, Boss->EngineIntake));
	TestEqual(TEXT("Rifle fallback defeats Tempest"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);

	ASkyguardMission05IntegrationDirector* FailureDirector =
		World->SpawnActor<ASkyguardMission05IntegrationDirector>();
	FailureDirector->bAutoInitialize = false;
	TestTrue(TEXT("Failure runtime configures"), FailureDirector->ConfigureMissionDefinition(Mission));
	TestTrue(
		TEXT("Catastrophic trawler damage is accepted"),
		FailureDirector->NotifyProtectedTargetDamage(
			ESkyguardMission05ProtectedTarget::DistressedTrawler,
			FailureDirector->MaximumProtectedTargetIntegrity));
	TestEqual(TEXT("One protected target remains"), FailureDirector->GetSurvivingTargetCount(), 1);
	TestEqual(
		TEXT("Trawler loss fails mission"),
		FailureDirector->GetWaveState(),
		ESkyguardMission05WaveState::Failed);
	TestTrue(
		TEXT("Protected objective records terminal failure"),
		FailureDirector->GetObjectiveRuntime()->HasTerminalFailure());
	return true;
}

#endif
