#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission06IntegrationDirector.h"

#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardGunner.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardRunwayBreakerBoss.h"
#include "SkyguardYak52Aircraft.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardMission06IntegrationTests
{
	static const TCHAR* MissionPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M06_AirfieldDefense.DA_Mission_M06_AirfieldDefense");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false, TEXT("SkyguardMission06TestWorld"));
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

	USkyguardMissionDefinition* Mission()
	{
		return LoadObject<USkyguardMissionDefinition>(nullptr, MissionPath);
	}

	void ConfigureAssembly(
		ASkyguardMissionMapAssemblyDirector* Assembly,
		USkyguardMissionDefinition* Definition)
	{
		Assembly->MissionDefinition = Definition;
		Assembly->MissionId =
			ASkyguardMission06IntegrationDirector::GetMissionId();
		Assembly->AssemblyRevision = TEXT("CampaignMapAssembly_v1");
		Assembly->SkylineStyle =
			ESkyguardMissionSkylineStyle::AirfieldMilitary;
		Assembly->WeatherProfileId = Definition->Weather.ProfileId;
		for (const FSkyguardRoutePoint& Point : Definition->Route.Points)
		{
			Assembly->RoutePoints.Add(Point.WorldLocation);
		}
		for (int32 Index = 0; Index < Definition->Objectives.Num(); ++Index)
		{
			FSkyguardMissionObjectiveAnchor Anchor;
			Anchor.ObjectiveId = Definition->Objectives[Index].ObjectiveId;
			Anchor.WorldLocation =
				FVector(57000.f + Index * 8000.f, 60000.f, 100.f);
			Assembly->ObjectiveAnchors.Add(Anchor);
		}
		for (int32 Index = 0; Index < 3; ++Index)
		{
			FSkyguardMissionLandmarkAnchor Landmark;
			Landmark.LandmarkId =
				FName(*FString::Printf(TEXT("M06_Landmark_%d"), Index));
			Landmark.Role =
				FName(*FString::Printf(TEXT("M06_Role_%d"), Index));
			Landmark.WorldLocation =
				FVector(18000.f + Index * 30000.f, 85000.f, 0.f);
			Landmark.bMissionExclusive = Index < 2;
			Assembly->LandmarkAnchors.Add(Landmark);
		}
		Assembly->RebuildRouteSpline();
	}

	bool Rifle(
		ASkyguardRunwayBreakerBoss* Boss,
		USkyguardBossWeakPointComponent* Point)
	{
		return Boss->ApplyWeaponHit(
			Point, ESkyguardBossWeapon::Rifle,
			Point->MaxIntegrity, FVector::ZeroVector,
			FVector::ForwardVector);
	}

	bool ClearWaves(ASkyguardMission06IntegrationDirector* Director)
	{
		for (const int32 Count : {2, 3, 4})
		{
			if (!Director->StartNextWave() ||
				Director->GetRemainingThreatsInWave() != Count ||
				!Director->NotifyThreatDestroyed(Count))
			{
				return false;
			}
		}
		return Director->GetWaveState() ==
			ESkyguardMission06WaveState::BossEngaged;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission06ContractPayloadTest,
	"Skyguard52.Mission06.Integration.GovernedContractWavesAndPayloadTiming",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission06ContractPayloadTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardMission06IntegrationTests;
	USkyguardMissionDefinition* Definition = Mission();
	TestNotNull(TEXT("Mission 6 DataAsset loads"), Definition);
	if (!Definition)
	{
		return false;
	}
	TArray<FText> Errors;
	TestTrue(
		TEXT("Mission 6 contract validates"),
		ASkyguardMission06IntegrationDirector::ValidateMissionContract(
			Definition, Errors));
	TestEqual(TEXT("Contract emits no errors"), Errors.Num(), 0);

	FWorldScope Scope;
	ASkyguardMission06IntegrationDirector* Director =
		Scope.Get()->SpawnActor<ASkyguardMission06IntegrationDirector>();
	Director->bAutoInitialize = false;
	TestTrue(TEXT("Definition configures"), Director->ConfigureMissionDefinition(Definition));
	TestTrue(TEXT("First wave starts"), Director->StartNextWave());
	TestTrue(
		TEXT("Runway payload window starts"),
		Director->StartPayloadWindow(ESkyguardAirfieldTarget::Runway, 2.f));
	TestTrue(TEXT("Payload timer advances"), Director->AdvancePayloadWindow(2.f));
	TestTrue(
		TEXT("Expired payload destroys runway"),
		Director->GetTargetRuntime(
			ESkyguardAirfieldTarget::Runway).bDestroyed);
	TestEqual(TEXT("Two targets still survive"), Director->GetSurvivingTargetCount(), 2);
	TestTrue(
		TEXT("Hangar damage is accepted"),
		Director->NotifyAirfieldTargetDamage(
			ESkyguardAirfieldTarget::Hangars, 100));
	TestEqual(TEXT("Only one target survives"), Director->GetSurvivingTargetCount(), 1);
	TestEqual(
		TEXT("Losing two targets fails mission"),
		Director->GetWaveState(),
		ESkyguardMission06WaveState::Failed);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission06PlayableIglaTest,
	"Skyguard52.Mission06.Integration.PlayableCompositionPayloadDefenseAndIgla",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission06PlayableIglaTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardMission06IntegrationTests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	USkyguardMissionDefinition* Definition = Mission();
	ASkyguardMissionMapAssemblyDirector* Assembly =
		World->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardYak52Aircraft* Aircraft =
		World->SpawnActor<ASkyguardYak52Aircraft>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	ASkyguardRunwayBreakerBoss* Boss =
		World->SpawnActor<ASkyguardRunwayBreakerBoss>();
	ASkyguardMission06IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission06IntegrationDirector>();
	if (!Definition || !Assembly || !Aircraft || !Gunner || !Boss || !Director)
	{
		AddError(TEXT("Mission 6 setup failed."));
		return false;
	}
	ConfigureAssembly(Assembly, Definition);
	Director->bAutoInitialize = false;
	Director->bAllowBoundedActorSpawning = false;
	World->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}
	TestTrue(TEXT("Mission 6 systems compose"), Director->InitializePlayableMission());
	TestTrue(TEXT("Core playable readiness is green"), Director->IsCorePlayableReady());
	TestTrue(TEXT("All waves clear"), ClearWaves(Director));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	TestEqual(TEXT("Pilot command reaches Yak"), Aircraft->GetPilotCommand(), ESkyguardPilotCommand::OrbitLeft);

	TestTrue(
		TEXT("Runway payload window starts"),
		Director->StartPayloadWindow(ESkyguardAirfieldTarget::Runway, 5.f));
	TestTrue(TEXT("Rifle jams runway rack"), Rifle(Boss, Boss->RunwayRack));
	Director->SynchronizeRuntimeState();
	TestFalse(TEXT("Destroyed rack cancels payload window"), Director->GetPayloadWindow().bActive);
	TestTrue(TEXT("Rifle jams hangar rack"), Rifle(Boss, Boss->HangarRack));
	TestTrue(TEXT("Rifle exposes engine manifold"), Rifle(Boss, Boss->HeatManifold));
	TestTrue(
		TEXT("Igla destroys port engine"),
		Boss->ApplyIglaStrike(
			Boss->PortEngine->MaxIntegrity,
			FVector::ZeroVector,
			FVector::ForwardVector));
	Director->SynchronizeRuntimeState();

	USkyguardObjectiveRuntime* Objectives = Director->GetObjectiveRuntime();
	TestEqual(TEXT("Both racks complete jam objective"), Objectives->GetProgress(TEXT("JamPayloadRacks")).CurrentProgress, 2);
	TestEqual(TEXT("Four weak points complete boss objective"), Objectives->GetProgress(TEXT("DefeatRunwayBreaker")).CurrentProgress, 4);
	TestEqual(TEXT("All three assets survive"), Director->GetSurvivingTargetCount(), 3);
	TestEqual(TEXT("Protection objective completes"), Objectives->GetProgress(TEXT("ProtectAirfieldAssets")).CurrentProgress, 1);
	TestEqual(TEXT("Mission completes"), Director->GetWaveState(), ESkyguardMission06WaveState::Completed);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission06RifleFallbackTest,
	"Skyguard52.Mission06.Integration.OrbitRifleFallback",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission06RifleFallbackTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardMission06IntegrationTests;
	FWorldScope Scope;
	ASkyguardRunwayBreakerBoss* Boss =
		Scope.Get()->SpawnActor<ASkyguardRunwayBreakerBoss>();
	TestNotNull(TEXT("Payload carrier spawns"), Boss);
	if (!Boss)
	{
		return false;
	}
	Scope.Get()->BeginPlay();
	if (!Boss->HasActorBegunPlay())
	{
		Boss->DispatchBeginPlay();
	}
	TestTrue(TEXT("Rifle destroys runway rack"), Rifle(Boss, Boss->RunwayRack));
	TestTrue(TEXT("Rifle destroys hangar rack"), Rifle(Boss, Boss->HangarRack));
	TestTrue(TEXT("Rifle destroys manifold"), Rifle(Boss, Boss->HeatManifold));
	TestFalse(TEXT("Fallback requires orbit"), Boss->ArmEmergencyRifleFinish());
	Boss->IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	TestTrue(TEXT("Orbit arms fallback"), Boss->ArmEmergencyRifleFinish());
	TestFalse(TEXT("Fallback closes Igla lock"), Boss->IsIglaLockEligible());
	TestTrue(TEXT("Rifle destroys exposed engine"), Rifle(Boss, Boss->PortEngine));
	TestEqual(TEXT("Rifle fallback defeats carrier"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);
	TestEqual(TEXT("Four weak points destroyed"), Boss->GetTelemetry().WeakPointsDestroyed, 4);
	return true;
}

#endif
