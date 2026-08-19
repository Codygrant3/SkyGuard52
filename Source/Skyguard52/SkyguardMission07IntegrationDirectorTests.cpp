#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardMission07IntegrationDirector.h"

#include "SkyguardMissionDefinition.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

// Neighbor of SkyguardMission07IntegrationTests.cpp.
// Public director API only: nullptr map/Yak/Gunner/RadarGhost, no actor spawn,
// no rifle/Igla hits, no night-beat kit edits.

namespace SkyguardMission07IntegrationDirectorTests
{
	static const TCHAR* MissionAssetPath =
		TEXT("/Game/Skyguard/Data/Campaign_v1/DA_Mission_M07_SearchIntercept.DA_Mission_M07_SearchIntercept");

	// Track IDs written by ConfigureMissionDefinition. Do not invent others.
	static const FName ConfiguredTrackA(TEXT("FalseTrack_A"));
	static const FName ConfiguredTrackB(TEXT("FalseTrack_B"));
	static const FName ConfiguredTrackC(TEXT("FalseTrack_C"));

	class FWorldScope
	{
	public:
		FWorldScope()
		{
			World = UWorld::CreateWorld(
				EWorldType::Game, false,
				TEXT("SkyguardMission07DirectorTestWorld"));
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

	USkyguardMissionDefinition* TryLoadMission()
	{
		return LoadObject<USkyguardMissionDefinition>(
			nullptr, MissionAssetPath);
	}

	ASkyguardMission07IntegrationDirector* SpawnBoundDirector(UWorld* World)
	{
		ASkyguardMission07IntegrationDirector* Director =
			World->SpawnActor<ASkyguardMission07IntegrationDirector>();
		if (!Director)
		{
			return nullptr;
		}
		Director->bAutoInitialize = false;
		Director->bAllowBoundedActorSpawning = false;
		Director->BindRuntimeActors(nullptr, nullptr, nullptr, nullptr);
		return Director;
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission07DirectorMissionIdNullContractAndFailClosedSearchTest,
	"Skyguard52.Mission07.Director.MissionIdNullContractAndFailClosedSearch",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission07DirectorMissionIdNullContractAndFailClosedSearchTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission07IntegrationDirectorTests;

	TestEqual(
		TEXT("GetMissionId is M07_SearchIntercept"),
		ASkyguardMission07IntegrationDirector::GetMissionId(),
		FName(TEXT("M07_SearchIntercept")));

	TArray<FText> NullContractErrors;
	TestFalse(
		TEXT("ValidateMissionContract rejects a null definition"),
		ASkyguardMission07IntegrationDirector::ValidateMissionContract(
			nullptr, NullContractErrors));
	TestTrue(
		TEXT("Null contract reports at least one error"),
		NullContractErrors.Num() > 0);

	FWorldScope Scope;
	ASkyguardMission07IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(
		TEXT("Director spawns without map, Yak, Gunner, or RadarGhost"),
		Director);
	if (!Director)
	{
		return false;
	}

	TestEqual(
		TEXT("Unconfigured wave stays Briefing"),
		Director->GetWaveState(),
		ESkyguardMission07WaveState::Briefing);
	TestEqual(
		TEXT("Unconfigured search stays SectorA"),
		Director->GetSearchSector(),
		ESkyguardSearchSector::SectorA);
	TestEqual(
		TEXT("Unconfigured classified-false count stays zero"),
		Director->GetClassifiedFalseTrackCount(),
		0);
	TestFalse(
		TEXT("Unconfigured hostile contact is not confirmed"),
		Director->IsHostileContactConfirmed());
	TestFalse(
		TEXT("ClassifyFalseTrack is fail-closed before configure"),
		Director->ClassifyFalseTrack(ConfiguredTrackA));
	TestFalse(
		TEXT("ConfirmRadarGhostIdentification is fail-closed before configure"),
		Director->ConfirmRadarGhostIdentification(true, true, true));
	TestEqual(
		TEXT("Failed classify does not increment classified-false count"),
		Director->GetClassifiedFalseTrackCount(),
		0);
	TestEqual(
		TEXT("Failed confirm leaves search in SectorA"),
		Director->GetSearchSector(),
		ESkyguardSearchSector::SectorA);
	TestFalse(
		TEXT("Failed confirm does not mark hostile contact"),
		Director->IsHostileContactConfirmed());

	TestFalse(
		TEXT("Unconfigured NavigationStation damage is fail-closed"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission07ProtectedTarget::NavigationStation, 20));
	TestFalse(
		TEXT("Unconfigured FishingFleet damage is fail-closed"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission07ProtectedTarget::FishingFleet, 20));
	TestEqual(
		TEXT("Unconfigured surviving target count stays zero"),
		Director->GetSurvivingTargetCount(),
		0);

	TestFalse(
		TEXT("AdvanceReinforcementTimer is fail-closed without RadarGhost"),
		Director->AdvanceReinforcementTimer(1.f));
	TestEqual(
		TEXT("Reinforcement remaining stays at the authored deadline"),
		Director->GetReinforcementTimeRemaining(),
		Director->ReinforcementDeadlineSeconds);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardMission07DirectorConfiguredSearchIdentifyAndProtectTest,
	"Skyguard52.Mission07.Director.ConfiguredSearchIdentifyAndProtect",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardMission07DirectorConfiguredSearchIdentifyAndProtectTest::RunTest(
	const FString& Parameters)
{
	using namespace SkyguardMission07IntegrationDirectorTests;

	USkyguardMissionDefinition* Mission = TryLoadMission();
	if (!Mission)
	{
		AddWarning(TEXT(
			"Mission 7 DataAsset unavailable; skipped ConfigureMissionDefinition "
			"search/identify and protected-target tests. Public-API fail-closed "
			"coverage remains in MissionIdNullContractAndFailClosedSearch."));
		return true;
	}

	TArray<FText> Errors;
	TestTrue(
		TEXT("Loaded Mission 7 contract validates"),
		ASkyguardMission07IntegrationDirector::ValidateMissionContract(
			Mission, Errors));
	TestEqual(TEXT("Loaded contract emits no errors"), Errors.Num(), 0);

	FWorldScope Scope;
	ASkyguardMission07IntegrationDirector* Director =
		SpawnBoundDirector(Scope.Get());
	TestNotNull(
		TEXT("Director binds nullptr map/Yak/Gunner/RadarGhost"),
		Director);
	if (!Director)
	{
		return false;
	}

	TestTrue(
		TEXT("Director configures from loaded Mission 7"),
		Director->ConfigureMissionDefinition(Mission));
	TestEqual(
		TEXT("Configured wave enters Searching"),
		Director->GetWaveState(),
		ESkyguardMission07WaveState::Searching);
	TestEqual(
		TEXT("Configured search starts in SectorA"),
		Director->GetSearchSector(),
		ESkyguardSearchSector::SectorA);
	TestEqual(
		TEXT("Configured classified-false count starts at zero"),
		Director->GetClassifiedFalseTrackCount(),
		0);
	TestFalse(
		TEXT("Configured hostile contact starts unconfirmed"),
		Director->IsHostileContactConfirmed());

	TestFalse(
		TEXT("SectorB FalseTrack_C is rejected while search is SectorA"),
		Director->ClassifyFalseTrack(ConfiguredTrackC));
	TestTrue(
		TEXT("SectorA FalseTrack_A classifies"),
		Director->ClassifyFalseTrack(ConfiguredTrackA));
	TestEqual(
		TEXT("One classified-false track after FalseTrack_A"),
		Director->GetClassifiedFalseTrackCount(),
		1);
	TestEqual(
		TEXT("Search stays SectorA after the first SectorA track"),
		Director->GetSearchSector(),
		ESkyguardSearchSector::SectorA);
	TestTrue(
		TEXT("SectorA FalseTrack_B classifies"),
		Director->ClassifyFalseTrack(ConfiguredTrackB));
	TestEqual(
		TEXT("Two classified-false tracks after FalseTrack_B"),
		Director->GetClassifiedFalseTrackCount(),
		2);
	TestEqual(
		TEXT("Search advances to SectorB after two SectorA tracks"),
		Director->GetSearchSector(),
		ESkyguardSearchSector::SectorB);
	TestTrue(
		TEXT("SectorB FalseTrack_C classifies after the sector advance"),
		Director->ClassifyFalseTrack(ConfiguredTrackC));
	TestEqual(
		TEXT("Three classified-false tracks after FalseTrack_C"),
		Director->GetClassifiedFalseTrackCount(),
		3);
	TestEqual(
		TEXT("Search stays SectorB until identification confirms"),
		Director->GetSearchSector(),
		ESkyguardSearchSector::SectorB);

	TestFalse(
		TEXT("Identification rejects incomplete cues"),
		Director->ConfirmRadarGhostIdentification(true, false, true));
	TestFalse(
		TEXT("Identification is fail-closed without a bound RadarGhost"),
		Director->ConfirmRadarGhostIdentification(true, true, true));
	TestFalse(
		TEXT("Hostile contact stays unconfirmed without RadarGhost"),
		Director->IsHostileContactConfirmed());
	TestEqual(
		TEXT("Failed identification does not enter Intercept"),
		Director->GetSearchSector(),
		ESkyguardSearchSector::SectorB);
	TestEqual(
		TEXT("Failed identification leaves classified-false count at three"),
		Director->GetClassifiedFalseTrackCount(),
		3);

	TestEqual(
		TEXT("Both protected targets start intact"),
		Director->GetSurvivingTargetCount(),
		2);
	TestTrue(
		TEXT("NavigationStation accepts bounded damage"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission07ProtectedTarget::NavigationStation, 25));
	const FSkyguardMission07ProtectedTargetRuntime StationAfterHit =
		Director->GetProtectedTarget(
			ESkyguardMission07ProtectedTarget::NavigationStation);
	TestEqual(
		TEXT("NavigationStation integrity drops by the applied damage"),
		StationAfterHit.Integrity,
		Director->MaximumProtectedTargetIntegrity - 25);
	TestFalse(
		TEXT("Damaged NavigationStation is not destroyed"),
		StationAfterHit.bDestroyed);
	TestTrue(
		TEXT("FishingFleet accepts bounded damage"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission07ProtectedTarget::FishingFleet, 40));
	const FSkyguardMission07ProtectedTargetRuntime FleetAfterHit =
		Director->GetProtectedTarget(
			ESkyguardMission07ProtectedTarget::FishingFleet);
	TestEqual(
		TEXT("FishingFleet integrity drops by the applied damage"),
		FleetAfterHit.Integrity,
		Director->MaximumProtectedTargetIntegrity - 40);
	TestFalse(TEXT("Damaged FishingFleet is not destroyed"), FleetAfterHit.bDestroyed);
	TestEqual(
		TEXT("Both targets still survive after partial damage"),
		Director->GetSurvivingTargetCount(),
		2);

	TestTrue(
		TEXT("Wiping NavigationStation is accepted"),
		Director->NotifyProtectedTargetDamage(
			ESkyguardMission07ProtectedTarget::NavigationStation,
			Director->MaximumProtectedTargetIntegrity));
	const FSkyguardMission07ProtectedTargetRuntime WipedStation =
		Director->GetProtectedTarget(
			ESkyguardMission07ProtectedTarget::NavigationStation);
	TestEqual(TEXT("Wiped NavigationStation integrity is zero"), WipedStation.Integrity, 0);
	TestTrue(TEXT("Wiped NavigationStation is marked destroyed"), WipedStation.bDestroyed);
	TestEqual(
		TEXT("Surviving target count drops after one wipe"),
		Director->GetSurvivingTargetCount(),
		1);

	TestFalse(
		TEXT("AdvanceReinforcementTimer stays fail-closed without RadarGhost"),
		Director->AdvanceReinforcementTimer(
			Director->ReinforcementDeadlineSeconds));
	TestEqual(
		TEXT("Reinforcement remaining is unchanged without RadarGhost"),
		Director->GetReinforcementTimeRemaining(),
		Director->ReinforcementDeadlineSeconds);
	return true;
}

#endif
