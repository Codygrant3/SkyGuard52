#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCampaignRoster.h"
#include "SkyguardDrone.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardPatrolShipBoss.h"
#include "SkyguardProtectAsset.h"
#include "SkyguardRadarNode.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCampaignRosterHasTenMissionsTest,
	"Skyguard52.Campaign.RosterHasTenMissions",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCampaignRosterHasTenMissionsTest::RunTest(const FString& Parameters)
{
	TestEqual(TEXT("ten campaign sorties"), SkyguardCampaignRoster::NumMissions(), 10);
	TestEqual(
		TEXT("first identity"),
		SkyguardCampaignRoster::IdAt(0),
		FName(TEXT("M01_CoastalIntercept")));
	TestEqual(
		TEXT("harbor breaker identity"),
		SkyguardCampaignRoster::IdAt(1),
		FName(TEXT("M02_HarborShield")));
	TestEqual(
		TEXT("finale identity"),
		SkyguardCampaignRoster::IdAt(9),
		FName(TEXT("M10_EvacuationFinale")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardSortieDirectorAdvancesBeatsTest,
	"Skyguard52.Campaign.SortieAdvancesBeats",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSortieDirectorAdvancesBeatsTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardSortieWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	TestNotNull(TEXT("director"), Director);
	if (!Director)
	{
		World->DestroyWorld(false);
		return false;
	}
	Director->bAutoStart = false;
	Director->StartMissionIndex(1);
	TestEqual(
		TEXT("starts on approach"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Approach);
	TestEqual(
		TEXT("harbor title"),
		Director->GetMissionTitle(),
		FString(TEXT("Harbor Breaker")));

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardFlaresDefeatInboundTest,
	"Skyguard52.Campaign.FlaresDefeatInbound",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardFlaresDefeatInboundTest::RunTest(const FString& Parameters)
{
	ASkyguardGunner* Gunner = NewObject<ASkyguardGunner>();
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Gunner)
	{
		return false;
	}
	TestEqual(TEXT("six flares"), Gunner->GetFlareCount(), 6);
	Gunner->NotifyMissileInbound();
	TestFalse(TEXT("no flare yet"), Gunner->TryDefeatInboundWithFlares());
	Gunner->PopFlares();
	TestTrue(TEXT("flare kills the inbound"), Gunner->TryDefeatInboundWithFlares());
	TestEqual(TEXT("one flare spent"), Gunner->GetFlareCount(), 5);
	Gunner->ApplyLoadout(ESkyguardLoadout::AntiArmor);
	TestEqual(
		TEXT("anti-armor loadout"),
		Gunner->GetActiveLoadout(),
		ESkyguardLoadout::AntiArmor);
	TestTrue(TEXT("anti-armor brings more missiles"), Gunner->GetGuidedAmmo() >= 4);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardPatrolShipStripsBySystemTest,
	"Skyguard52.Campaign.PatrolShipStripsBySystem",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardPatrolShipStripsBySystemTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardShipWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}
	ASkyguardPatrolShipBoss* Ship = World->SpawnActor<ASkyguardPatrolShipBoss>();
	TestNotNull(TEXT("ship"), Ship);
	if (!Ship)
	{
		World->DestroyWorld(false);
		return false;
	}
	TestFalse(TEXT("starts alive"), Ship->IsDefeated());
	for (int32 Index = 0; Index < 40; ++Index)
	{
		Ship->ApplyHit(nullptr, 80.f);
	}
	TestTrue(TEXT("enough hits defeat the ship"), Ship->GetDestroyedSystemCount() >= 1);
	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCoastalConvoySpawnsOnRoadTest,
	"Skyguard52.Campaign.CoastalConvoySpawnsOnRoad",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCoastalConvoySpawnsOnRoadTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardConvoyWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	const TArray<FVector> Path =
		ASkyguardGunshipSortieDirector::GetCoastalHighwayPath();
	TestTrue(TEXT("coastal highway has a loop"), Path.Num() >= 8);

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	TestNotNull(TEXT("director"), Director);
	if (!Director)
	{
		World->DestroyWorld(false);
		return false;
	}
	Director->bAutoStart = false;
	const int32 Spawned = Director->SpawnCoastalConvoy();
	TestEqual(TEXT("five vehicles roll out"), Spawned, 5);
	TestEqual(
		TEXT("live convoy matches spawn"),
		Director->CountLiveRoadConvoy(),
		5);

	World->DestroyWorld(false);
	return true;
}

#endif
