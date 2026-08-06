#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission09IntegrationDirector.h"

#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardCampaignDefinition.h"
#include "SkyguardCampaignSaveGame.h"
#include "SkyguardCampaignSubsystem.h"
#include "SkyguardGunner.h"
#include "SkyguardIronRainBoss.h"
#include "SkyguardMissionDefinition.h"
#include "SkyguardMissionMapAssemblyDirector.h"
#include "SkyguardObjectiveRuntime.h"
#include "SkyguardYak52Aircraft.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

namespace SkyguardMission09Tests
{
	static const TCHAR* MissionPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M09_SaturationAttack.DA_Mission_M09_SaturationAttack");
	static const TCHAR* CampaignPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Campaign_Skyguard52.DA_Campaign_Skyguard52");

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false, TEXT("SkyguardMission09TestWorld"));
			check(World);
			FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
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
		return LoadObject<USkyguardMissionDefinition>(nullptr, MissionPath);
	}

	void ConfigureAssembly(
		ASkyguardMissionMapAssemblyDirector* Assembly,
		USkyguardMissionDefinition* Mission)
	{
		Assembly->MissionDefinition = Mission;
		Assembly->MissionId = ASkyguardMission09IntegrationDirector::GetMissionId();
		Assembly->AssemblyRevision = TEXT("CampaignMapAssembly_v1");
		Assembly->SkylineStyle = ESkyguardMissionSkylineStyle::BlackoutUrban;
		Assembly->WeatherProfileId = Mission->Weather.ProfileId;
		for (const FSkyguardRoutePoint& Point : Mission->Route.Points)
		{
			Assembly->RoutePoints.Add(Point.WorldLocation);
		}
		for (int32 Index = 0; Index < Mission->Objectives.Num(); ++Index)
		{
			FSkyguardMissionObjectiveAnchor Anchor;
			Anchor.ObjectiveId = Mission->Objectives[Index].ObjectiveId;
			Anchor.WorldLocation = FVector(40000.f + Index * 12000.f, 30000.f, 200.f);
			Assembly->ObjectiveAnchors.Add(Anchor);
		}
		const FName Roles[] = {
			TEXT("DenseMetroSkylineProxy"),
			TEXT("PowerInfrastructureProxy"),
			TEXT("BridgeInfrastructureProxy"),
			TEXT("SwarmRelayProxy")};
		for (int32 Index = 0; Index < 4; ++Index)
		{
			FSkyguardMissionLandmarkAnchor Anchor;
			Anchor.LandmarkId = FName(*FString::Printf(TEXT("M09_Test_%d"), Index));
			Anchor.Role = Roles[Index];
			Anchor.WorldLocation = FVector(25000.f + Index * 14000.f, 33000.f, 0.f);
			Anchor.bMissionExclusive = Index > 0;
			Assembly->LandmarkAnchors.Add(Anchor);
		}
		Assembly->RebuildRouteSpline();
	}

	bool Rifle(ASkyguardIronRainBoss* Boss, USkyguardBossWeakPointComponent* Point)
	{
		return Boss->ApplyWeaponHit(
			Point, ESkyguardBossWeapon::Rifle, Point->MaxIntegrity,
			Boss->GetActorLocation(), FVector::ForwardVector);
	}

	bool DisarmAndExposeEngines(ASkyguardIronRainBoss* Boss)
	{
		return Rifle(Boss, Boss->DispenserPort) &&
			Rifle(Boss, Boss->DispenserCenter) &&
			Rifle(Boss, Boss->DispenserStarboard) &&
			Rifle(Boss, Boss->CommandAntennaPort) &&
			Rifle(Boss, Boss->CommandAntennaStarboard) &&
			Rifle(Boss, Boss->DecoyController) &&
			Boss->IssueClimbCommand() &&
			Boss->IssueCrossCommand() &&
			Boss->OpenUpperEngineExposure();
	}

	bool ClearWaves(ASkyguardMission09IntegrationDirector* Director)
	{
		const int32 Counts[] = {8, 12, 16};
		for (const int32 Count : Counts)
		{
			if (!Director->StartNextWave() ||
				Director->GetRemainingThreatsInWave() != Count ||
				!Director->NotifyThreatDestroyed(Count))
			{
				return false;
			}
		}
		return Director->GetWaveState() == ESkyguardMission09WaveState::BossEngaged;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission09ContractPoolTest,
	"Skyguard52.Mission09.Integration.GovernedContractEscalationAndPoolBounds",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission09ContractPoolTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardMission09Tests;
	USkyguardMissionDefinition* Mission = LoadMission();
	TestNotNull(TEXT("Mission 9 DataAsset loads"), Mission);
	if (!Mission) return false;
	TArray<FText> Errors;
	TestTrue(TEXT("Governed contract validates"),
		ASkyguardMission09IntegrationDirector::ValidateMissionContract(Mission, Errors));
	FWorldScope Scope;
	ASkyguardMission09IntegrationDirector* Director =
		Scope.Get()->SpawnActor<ASkyguardMission09IntegrationDirector>();
	Director->bAutoInitialize = false;
	TestTrue(TEXT("Mission configures"), Director->ConfigureMissionDefinition(Mission));
	TestTrue(TEXT("Three escalating waves clear"), ClearWaves(Director));
	TestEqual(TEXT("Peak active remains bounded"), Director->GetPoolRuntime().PeakActive, 16);
	TestEqual(TEXT("All 36 logical threats recycle"), Director->GetPoolRuntime().Recycled, 36);
	TestTrue(TEXT("Pool returns to full capacity"),
		Director->GetPoolRuntime().Available == Director->PoolBudget.PoolCapacity);
	TestTrue(TEXT("Active count returns to zero"), Director->GetPoolRuntime().Active == 0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission09IglaBossTest,
	"Skyguard52.Mission09.IronRain.DispensersClimbCrossAndSecondIgla",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission09IglaBossTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardMission09Tests;
	FWorldScope Scope;
	ASkyguardIronRainBoss* Boss = Scope.Get()->SpawnActor<ASkyguardIronRainBoss>();
	Scope.Get()->BeginPlay();
	TestTrue(TEXT("Three dispenser releases are bounded and pool-facing"),
		Boss->OpenDispenserBay(0) && Boss->ReleasePooledEscort(0) &&
		Boss->OpenDispenserBay(1) && Boss->ReleasePooledEscort(1) &&
		Boss->OpenDispenserBay(2) && Boss->ReleasePooledEscort(2));
	TestTrue(TEXT("Disarm and climb/cross exposes upper engines"), DisarmAndExposeEngines(Boss));
	TestEqual(TEXT("Cross maneuver is recorded"), Boss->GetManeuver(), ESkyguardIronRainManeuver::Cross);
	TestEqual(TEXT("All eleven authored weak points are registered for weapon routing"),
		Boss->WeakPoints.Num(), 11);
	TestTrue(TEXT("Climb/cross opens the Igla lock window"), Boss->IsIglaLockEligible());
	TestTrue(TEXT("All upper engine pods are exposed and accept Igla"),
		Boss->EnginePodPort->bExposed &&
		Boss->EnginePodCenter->bExposed &&
		Boss->EnginePodStarboard->bExposed &&
		Boss->EnginePodPort->AcceptsWeapon(ESkyguardBossWeapon::Igla) &&
		Boss->EnginePodCenter->AcceptsWeapon(ESkyguardBossWeapon::Igla) &&
		Boss->EnginePodStarboard->AcceptsWeapon(ESkyguardBossWeapon::Igla));
	TestTrue(TEXT("First Igla destroys one upper engine"),
		Boss->ApplyIglaStrike(250.f, FVector::ZeroVector, FVector::ForwardVector));
	TestEqual(TEXT("Exactly one upper engine is destroyed"), Boss->GetDestroyedEngineCount(), 1);
	TestTrue(TEXT("Second Igla finishes remaining engine pods"), Boss->ApplySecondIglaFinish(250.f));
	TestEqual(TEXT("Iron Rain is defeated"), Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);
	TestEqual(TEXT("Breakup is pre-authored and bounded"), Boss->GetDefeatDebrisPieceCount(), 3);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission09RifleBossTest,
	"Skyguard52.Mission09.IronRain.DifficultRifleFuelControlFinish",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission09RifleBossTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardMission09Tests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	ASkyguardYak52Aircraft* Yak = World->SpawnActor<ASkyguardYak52Aircraft>();
	ASkyguardIronRainBoss* Boss = World->SpawnActor<ASkyguardIronRainBoss>();
	ASkyguardMission09IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission09IntegrationDirector>();
	Director->bAutoInitialize = false;
	Director->BindRuntimeActors(nullptr, Yak, nullptr, Boss);
	World->BeginPlay();
	TestTrue(TEXT("Upper engine route opens"), DisarmAndExposeEngines(Boss));
	TestEqual(TEXT("Weapon routing registry remains complete"), Boss->WeakPoints.Num(), 11);
	TestTrue(TEXT("Upper-engine Igla lock is eligible before first strike"),
		Boss->IsIglaLockEligible());
	TestEqual(TEXT("Cross propagates to pilot as right crossing command"),
		Yak->GetPilotCommand(), ESkyguardPilotCommand::OrbitRight);
	TestTrue(TEXT("First engine accepts Igla"),
		Boss->ApplyIglaStrike(250.f, FVector::ZeroVector, FVector::ForwardVector));
	Boss->IssuePilotCommand(ESkyguardPilotCommand::Break);
	TestTrue(TEXT("Break arms difficult fuel-control rifle finish"),
		Boss->ArmFuelControlRifleFinish());
	TestTrue(TEXT("Port fuel control accepts rifle"), Rifle(Boss, Boss->FuelControlPort));
	TestTrue(TEXT("Starboard fuel control accepts rifle"), Rifle(Boss, Boss->FuelControlStarboard));
	TestEqual(TEXT("Rifle route deterministically defeats Iron Rain"),
		Boss->GetBossPhase(), ESkyguardBossPhase::Defeated);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission09OutcomeTest,
	"Skyguard52.Mission09.Integration.DeterministicSuccessAndInfrastructureFailure",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission09OutcomeTest::RunTest(const FString& Parameters)
{
	using namespace SkyguardMission09Tests;
	FWorldScope Scope;
	UWorld* World = Scope.Get();
	USkyguardMissionDefinition* Mission = LoadMission();
	ASkyguardMissionMapAssemblyDirector* Assembly =
		World->SpawnActor<ASkyguardMissionMapAssemblyDirector>();
	ASkyguardYak52Aircraft* Yak = World->SpawnActor<ASkyguardYak52Aircraft>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	ASkyguardIronRainBoss* Boss = World->SpawnActor<ASkyguardIronRainBoss>();
	ASkyguardMission09IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission09IntegrationDirector>();
	if (!Mission || !Assembly || !Yak || !Gunner || !Boss || !Director) return false;
	ConfigureAssembly(Assembly, Mission);
	Director->bAutoInitialize = false;
	Director->bAllowBoundedActorSpawning = false;
	World->BeginPlay();
	TestTrue(TEXT("Playable systems compose"), Director->InitializePlayableMission());
	TestTrue(TEXT("Readiness is green"), Director->IsCorePlayableReady());
	TestTrue(TEXT("Saturation waves clear"), ClearWaves(Director));
	TestTrue(TEXT("One infrastructure loss is survivable"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission09ProtectedTarget::MetropolitanSkyline, 100));
	TestTrue(TEXT("Boss route opens"), DisarmAndExposeEngines(Boss));
	TestTrue(TEXT("First Igla lands"),
		Boss->ApplyIglaStrike(250.f, FVector::ZeroVector, FVector::ForwardVector));
	TestTrue(TEXT("Second Igla finishes"), Boss->ApplySecondIglaFinish(250.f));
	Director->SynchronizeRuntimeState();
	TestEqual(TEXT("Two surviving nodes produce deterministic success"),
		Director->GetWaveState(), ESkyguardMission09WaveState::Completed);

	ASkyguardMission09IntegrationDirector* Failure =
		World->SpawnActor<ASkyguardMission09IntegrationDirector>();
	Failure->bAutoInitialize = false;
	TestTrue(TEXT("Failure state configures"), Failure->ConfigureMissionDefinition(Mission));
	TestTrue(TEXT("Power station destruction applies"),
		Failure->NotifyProtectedTargetDamage(
			ESkyguardMission09ProtectedTarget::CoastalPowerStation, 100));
	TestTrue(TEXT("Bridge destruction applies"),
		Failure->NotifyProtectedTargetDamage(
			ESkyguardMission09ProtectedTarget::MajorBridge, 100));
	TestEqual(TEXT("Fewer than two protected nodes deterministically fails"),
		Failure->GetWaveState(), ESkyguardMission09WaveState::Failed);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission09CampaignProgressionTest,
	"Skyguard52.Mission09.Campaign.CompletionRecordsAndUnlocksFinale",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission09CampaignProgressionTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission09Tests;
	USkyguardCampaignDefinition* Campaign =
		LoadObject<USkyguardCampaignDefinition>(nullptr, CampaignPath);
	USkyguardMissionDefinition* Mission = LoadMission();
	TestNotNull(TEXT("Campaign V1 loads"), Campaign);
	TestNotNull(TEXT("Mission 9 loads"), Mission);
	if (!Campaign || !Mission)
	{
		return false;
	}

	UGameInstance* GameInstance =
		NewObject<UGameInstance>(GetTransientPackage());
	USkyguardCampaignSubsystem* Runtime =
		NewObject<USkyguardCampaignSubsystem>(GameInstance);
	TestTrue(TEXT("Campaign V1 configures"), Runtime->ConfigureCampaign(Campaign));

	USkyguardCampaignSaveGame* PriorProgress =
		NewObject<USkyguardCampaignSaveGame>(GetTransientPackage());
	PriorProgress->CampaignId = Campaign->CampaignId;
	for (int32 MissionIndex = 0; MissionIndex < 8; ++MissionIndex)
	{
		USkyguardMissionDefinition* PriorMission =
			Campaign->Missions.IsValidIndex(MissionIndex)
				? Campaign->Missions[MissionIndex].Get()
				: nullptr;
		if (!PriorMission)
		{
			AddError(TEXT("Campaign V1 is missing a prerequisite mission."));
			return false;
		}
		FSkyguardMissionSaveRecord Record;
		Record.bCompleted = true;
		Record.BestMedalTier = 3;
		PriorProgress->MissionRecords.Add(PriorMission->MissionId, Record);
	}
	TestTrue(TEXT("Completed Missions 1-8 restore"),
		Runtime->ApplySaveGame(PriorProgress));
	TestTrue(TEXT("Mission 9 starts from restored campaign progress"),
		Runtime->StartMission(ASkyguardMission09IntegrationDirector::GetMissionId()));
	TestFalse(TEXT("Mission 10 remains locked before Mission 9 completion"),
		Runtime->IsMissionUnlocked(TEXT("M10_EvacuationFinale")));

	FWorldScope Scope;
	UWorld* World = Scope.Get();
	ASkyguardIronRainBoss* Boss =
		World->SpawnActor<ASkyguardIronRainBoss>();
	ASkyguardMission09IntegrationDirector* Director =
		World->SpawnActor<ASkyguardMission09IntegrationDirector>();
	Director->bAutoInitialize = false;
	TestTrue(TEXT("Mission 9 director configures"),
		Director->ConfigureMissionDefinition(Mission));
	TestTrue(TEXT("Director binds the active campaign runtime"),
		Director->BindCampaignRuntime(Runtime));
	Director->BindRuntimeActors(nullptr, nullptr, nullptr, Boss);
	World->BeginPlay();

	TestTrue(TEXT("Saturation waves clear"), ClearWaves(Director));
	TestTrue(TEXT("Boss route opens"), DisarmAndExposeEngines(Boss));
	TestTrue(TEXT("First Igla lands"),
		Boss->ApplyIglaStrike(
			250.f, FVector::ZeroVector, FVector::ForwardVector));
	TestTrue(TEXT("Second Igla finishes"),
		Boss->ApplySecondIglaFinish(250.f));
	Director->SynchronizeRuntimeState();

	const FSkyguardMissionSaveRecord* Mission09Record =
		Runtime->GetMissionRecords().Find(
			ASkyguardMission09IntegrationDirector::GetMissionId());
	TestTrue(TEXT("Mission 9 reaches completed state"),
		Director->GetWaveState() == ESkyguardMission09WaveState::Completed);
	TestTrue(TEXT("Campaign records Mission 9 completion"),
		Mission09Record && Mission09Record->bCompleted);
	TestTrue(TEXT("Mission 10 unlocks after Mission 9 completion"),
		Runtime->IsMissionUnlocked(TEXT("M10_EvacuationFinale")));
	return true;
}

#endif
