#if WITH_DEV_AUTOMATION_TESTS

#include "SkyguardCampaignRoster.h"
#include "SkyguardDrone.h"
#include "SkyguardGunner.h"
#include "SkyguardGunshipSortieDirector.h"
#include "SkyguardGunshipTypes.h"
#include "SkyguardPatrolShipBoss.h"
#include "SkyguardProtectAsset.h"
#include "SkyguardRadarNode.h"
#include "SkyguardThreatTypes.h"
#include "Components/PrimitiveComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
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
	FSkyguardSortieInboundIntervalsStretchForFifteenMinutesTest,
	"Skyguard52.Campaign.InboundIntervalsStretchForFifteenMinutes",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSortieInboundIntervalsStretchForFifteenMinutesTest::RunTest(
	const FString& Parameters)
{
	const float Live =
		ASkyguardGunshipSortieDirector::IncomingIntervalSeconds(true);
	const float Down =
		ASkyguardGunshipSortieDirector::IncomingIntervalSeconds(false);
	TestEqual(
		TEXT("radar-live uses the named live interval"),
		Live,
		static_cast<double>(
			ASkyguardGunshipSortieDirector::IncomingRadarLiveIntervalSeconds));
	TestEqual(
		TEXT("radar-down uses the named down interval"),
		Down,
		static_cast<double>(
			ASkyguardGunshipSortieDirector::IncomingRadarDownIntervalSeconds));
	TestTrue(TEXT("radar-live interval is faster than radar-down"), Live < Down);
	TestTrue(
		TEXT("radar-live is stretched past the old 14s SAM clock"),
		Live > 14.0);
	TestTrue(
		TEXT("radar-down is stretched past the old 28s gap"),
		Down > 28.0);
	TestTrue(
		TEXT("approach still refuses inbound tick-fire"),
		!ASkyguardGunshipSortieDirector::BeatAllowsInbound(
			ESkyguardSortieBeat::Approach));
	TestTrue(
		TEXT("radar-net uses the live cadence once the net is up"),
		ASkyguardGunshipSortieDirector::UsesRadarLiveInboundCadence(
			ESkyguardSortieBeat::RadarNet));
	TestTrue(
		TEXT("contact stays on the earned-gap cadence"),
		!ASkyguardGunshipSortieDirector::UsesRadarLiveInboundCadence(
			ESkyguardSortieBeat::InitialContact));
	TestTrue(
		TEXT("climax still has a source if the launcher is live"),
		ASkyguardGunshipSortieDirector::HasInboundSource(
			ESkyguardSortieBeat::Climax, false, true));
	TestTrue(
		TEXT("climax still has a source if shore ADA is live"),
		ASkyguardGunshipSortieDirector::HasInboundSource(
			ESkyguardSortieBeat::Climax, true, false));
	TestFalse(
		TEXT("climax inbound dies when launcher and shore net are both dead"),
		ASkyguardGunshipSortieDirector::HasInboundSource(
			ESkyguardSortieBeat::Climax, false, false));
	TestTrue(
		TEXT("contact inbound does not need the ship launcher"),
		ASkyguardGunshipSortieDirector::HasInboundSource(
			ESkyguardSortieBeat::InitialContact, false, false));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardSortieBeatWaveCountsEscalateTest,
	"Skyguard52.Campaign.BeatWaveCountsEscalate",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSortieBeatWaveCountsEscalateTest::RunTest(const FString& Parameters)
{
	const int32 Contact = ASkyguardGunshipSortieDirector::BeatWaveCount(
		ESkyguardSortieBeat::InitialContact);
	const int32 Shore = ASkyguardGunshipSortieDirector::BeatWaveCount(
		ESkyguardSortieBeat::ShoreAssault);
	const int32 Radar = ASkyguardGunshipSortieDirector::BeatWaveCount(
		ESkyguardSortieBeat::RadarNet);
	const int32 Choice = ASkyguardGunshipSortieDirector::BeatWaveCount(
		ESkyguardSortieBeat::Choice);
	const int32 Extract = ASkyguardGunshipSortieDirector::BeatWaveCount(
		ESkyguardSortieBeat::Extraction);
	TestEqual(
		TEXT("approach has no beat pack"),
		ASkyguardGunshipSortieDirector::BeatWaveCount(ESkyguardSortieBeat::Approach),
		0);
	TestEqual(
		TEXT("climax pack stays on ClimaxKind, not a numbered wave"),
		ASkyguardGunshipSortieDirector::BeatWaveCount(ESkyguardSortieBeat::Climax),
		0);
	TestTrue(TEXT("contact wave count is lighter than shore"), Contact < Shore);
	TestTrue(TEXT("contact wave count is lighter than radar"), Contact < Radar);
	TestTrue(TEXT("choice is denser than contact"), Choice > Contact);
	TestTrue(TEXT("extract is a spike over contact"), Extract > Contact);
	TestTrue(TEXT("extract is not another identical 4-pack"), Extract != 4);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardSortieApproachHasNoInboundTest,
	"Skyguard52.Campaign.ApproachHasNoInbound",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSortieApproachHasNoInboundTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardApproachInboundWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	ASkyguardGunner* Gunner = World->SpawnActor<ASkyguardGunner>();
	TestNotNull(TEXT("director"), Director);
	TestNotNull(TEXT("gunner"), Gunner);
	if (!Director || !Gunner)
	{
		World->DestroyWorld(false);
		return false;
	}

	Director->bAutoStart = false;
	Director->StartMissionIndex(1);
	TestEqual(
		TEXT("harbor starts on approach"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Approach);

	const float ApproachHold =
		ASkyguardGunshipSortieDirector::IncomingFirstDelaySeconds + 18.f;
	Director->Tick(ApproachHold);
	TestEqual(
		TEXT("still on approach after the first-delay window"),
		Director->GetBeat(),
		ESkyguardSortieBeat::Approach);
	TestFalse(TEXT("approach does not tick-fire inbound"), Gunner->IsMissileInbound());

	Director->EnterBeat(ESkyguardSortieBeat::InitialContact);
	Director->Tick(0.1f);
	TestEqual(
		TEXT("contact is the first inbound beat"),
		Director->GetBeat(),
		ESkyguardSortieBeat::InitialContact);
	TestTrue(
		TEXT("inbound can come once approach is over"),
		Gunner->IsMissileInbound());

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardSortieExtractUsesExtractKindTest,
	"Skyguard52.Campaign.ExtractUsesExtractKind",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSortieExtractUsesExtractKindTest::RunTest(const FString& Parameters)
{
	const FSkyguardCampaignMissionSpec& Harbor = SkyguardCampaignRoster::Get(1);
	TestEqual(
		TEXT("Harbor Breaker extract kind stays rotor"),
		Harbor.ExtractKind,
		ESkyguardThreatKind::RotorScout);
	TestEqual(
		TEXT("Harbor Breaker climax stays the patrol ship"),
		Harbor.Climax,
		ESkyguardClimaxKind::PatrolShip);
	TestEqual(
		TEXT("extract wave uses roster ExtractKind, not a new climax"),
		ASkyguardGunshipSortieDirector::BeatWaveKind(
			1, ESkyguardSortieBeat::Extraction),
		Harbor.ExtractKind);

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardExtractKindWorld"));
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
	Director->EnterBeat(ESkyguardSortieBeat::Extraction);

	int32 Rotors = 0;
	int32 Ships = 0;
	for (TActorIterator<ASkyguardDrone> It(World); It; ++It)
	{
		const ASkyguardDrone* Threat = *It;
		if (Threat && !Threat->IsDestroyed() &&
			Threat->GetThreatKind() == ESkyguardThreatKind::RotorScout)
		{
			++Rotors;
		}
	}
	for (TActorIterator<ASkyguardPatrolShipBoss> It(World); It; ++It)
	{
		if (IsValid(*It))
		{
			++Ships;
		}
	}

	TestEqual(
		TEXT("extract spawns the named rotor spike"),
		Rotors,
		ASkyguardGunshipSortieDirector::ExtractWaveCount);
	TestEqual(TEXT("extract is not a second patrol-ship climax"), Ships, 0);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardSortieBeatWaveSkipsRoadConvoyTest,
	"Skyguard52.Campaign.BeatWaveSkipsRoadConvoy",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardSortieBeatWaveSkipsRoadConvoyTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardBeatWaveConvoyWorld"));
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
		TEXT("mission start owns the road column"),
		Director->CountLiveRoadConvoy(),
		ASkyguardGunshipSortieDirector::CoastalConvoyCount);

	Director->EnterBeat(ESkyguardSortieBeat::ShoreAssault);
	TestEqual(
		TEXT("shore wave does not add road-convoy hulls"),
		Director->CountLiveRoadConvoy(),
		ASkyguardGunshipSortieDirector::CoastalConvoyCount);

	int32 LooseArmor = 0;
	for (TActorIterator<ASkyguardDrone> It(World); It; ++It)
	{
		const ASkyguardDrone* Threat = *It;
		if (Threat && !Threat->IsDestroyed() &&
			Threat->GetThreatKind() == ESkyguardThreatKind::GroundArmor &&
			!Threat->IsFollowingRoad())
		{
			++LooseArmor;
		}
	}
	TestEqual(
		TEXT("shore armor is a beat pack, not the highway column"),
		LooseArmor,
		ASkyguardGunshipSortieDirector::ShoreWaveCount);

	World->DestroyWorld(false);
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
	if (UPrimitiveComponent* Hull = Cast<UPrimitiveComponent>(
			Ship->GetDefaultSubobjectByName(TEXT("Hull"))))
	{
		Ship->ApplyHit(Hull, 500.f);
	}
	TestEqual(
		TEXT("hull splash is not a system kill"),
		Ship->GetDestroyedSystemCount(),
		0);
	TestTrue(TEXT("radar still coordinates after hull spam"), Ship->CanCoordinateAda());
	TestFalse(TEXT("hull spam does not defeat the ship"), Ship->IsDefeated());
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
	TestEqual(
		TEXT("five vehicles roll out"),
		Spawned,
		ASkyguardGunshipSortieDirector::CoastalConvoyCount);
	TestEqual(
		TEXT("live convoy matches spawn"),
		Director->CountLiveRoadConvoy(),
		ASkyguardGunshipSortieDirector::CoastalConvoyCount);

	World->DestroyWorld(false);
	return true;
}

namespace SkyguardCoastalConvoyTest
{
	static float DistanceToPolylineXY(
		const FVector& Point,
		const TArray<FVector>& Path,
		const bool bLoop)
	{
		if (Path.Num() < 2)
		{
			return 1.e12f;
		}

		float Best = TNumericLimits<float>::Max();
		const int32 SegmentCount = bLoop ? Path.Num() : (Path.Num() - 1);
		for (int32 Index = 0; Index < SegmentCount; ++Index)
		{
			const FVector2D Start(Path[Index].X, Path[Index].Y);
			const FVector2D End(
				Path[(Index + 1) % Path.Num()].X,
				Path[(Index + 1) % Path.Num()].Y);
			const FVector2D Delta = End - Start;
			const float LengthSq = Delta.SizeSquared();
			const FVector2D Query(Point.X, Point.Y);
			float Alpha = 0.f;
			if (LengthSq > KINDA_SMALL_NUMBER)
			{
				Alpha = FMath::Clamp(
					FVector2D::DotProduct(Query - Start, Delta) / LengthSq,
					0.f,
					1.f);
			}
			Best = FMath::Min(Best, FVector2D::Distance(Query, Start + Delta * Alpha));
		}
		return Best;
	}

	static void CollectLiveRoadConvoy(
		UWorld* World,
		TArray<ASkyguardDrone*>& OutConvoy)
	{
		OutConvoy.Reset();
		if (!World)
		{
			return;
		}
		for (TActorIterator<ASkyguardDrone> It(World); It; ++It)
		{
			ASkyguardDrone* Threat = *It;
			if (Threat && !Threat->IsDestroyed() && Threat->IsFollowingRoad())
			{
				OutConvoy.Add(Threat);
			}
		}
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCoastalConvoyHighwayLoopsTest,
	"Skyguard52.Campaign.CoastalConvoyHighwayLoops",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCoastalConvoyHighwayLoopsTest::RunTest(const FString& Parameters)
{
	const TArray<FVector> Path =
		ASkyguardGunshipSortieDirector::GetCoastalHighwayPath();
	TestTrue(TEXT("authored highway has at least eight points"), Path.Num() >= 8);

	// Same HarborHover → city corridor. Do not invent a new map.
	for (int32 Index = 0; Index < Path.Num(); ++Index)
	{
		const FVector& Point = Path[Index];
		TestTrue(
			FString::Printf(TEXT("point %d stays on the coastal X strip"), Index),
			Point.X >= -2400.f && Point.X <= 2300.f);
		TestTrue(
			FString::Printf(TEXT("point %d stays on the coastal Y strip"), Index),
			Point.Y >= -6600.f && Point.Y <= 3500.f);
		TestEqual(
			FString::Printf(TEXT("point %d authored Z is road height"), Index),
			Point.Z,
			92.0);
	}

	for (int32 Index = 0; Index < Path.Num(); ++Index)
	{
		const FVector& From = Path[Index];
		const FVector& To = Path[(Index + 1) % Path.Num()];
		const float SegmentCm = (To - From).Size2D();
		TestTrue(
			FString::Printf(TEXT("segment %d is a highway stride, not a 6m kink"), Index),
			SegmentCm >= 1000.f);
	}

	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardConvoyLoopWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardDrone* Tail = World->SpawnActor<ASkyguardDrone>(
		Path.Last(),
		FRotator::ZeroRotator);
	TestNotNull(TEXT("tail vehicle"), Tail);
	if (!Tail)
	{
		World->DestroyWorld(false);
		return false;
	}

	Tail->ConfigureRoadConvoy(Path, Path.Num() - 1, TEXT("Vehicle.Truck"));
	TestTrue(TEXT("tail is a road follower"), Tail->IsFollowingRoad());
	for (int32 Step = 0; Step < 10; ++Step)
	{
		Tail->Tick(0.25f);
	}

	const float AwayFromLast = (Tail->GetActorLocation() - Path.Last()).Size2D();
	TestTrue(
		TEXT("bLoopRoad wraps the last waypoint toward the harbor end"),
		AwayFromLast > 140.f);

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCoastalConvoyIsShorelineArmorTest,
	"Skyguard52.Campaign.CoastalConvoyIsShorelineArmor",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCoastalConvoyIsShorelineArmorTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardConvoyArmorWorld"));
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
	Director->SpawnCoastalConvoy();

	TArray<ASkyguardDrone*> Convoy;
	SkyguardCoastalConvoyTest::CollectLiveRoadConvoy(World, Convoy);
	TestEqual(
		TEXT("five live road-followers"),
		Convoy.Num(),
		ASkyguardGunshipSortieDirector::CoastalConvoyCount);

	for (const ASkyguardDrone* Threat : Convoy)
	{
		TestTrue(TEXT("column stays road-bound"), Threat->IsFollowingRoad());
		TestTrue(TEXT("column is missile-lock eligible"), Threat->IsMissileLockEligible());
		TestEqual(
			TEXT("column is shoreline GroundArmor, not a Shahed"),
			Threat->GetThreatKind(),
			ESkyguardThreatKind::GroundArmor);
	}

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCoastalConvoyCrawlsBelowFastBoatTest,
	"Skyguard52.Campaign.CoastalConvoyCrawlsBelowFastBoat",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCoastalConvoyCrawlsBelowFastBoatTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardConvoyPaceWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardDrone* Boat = World->SpawnActor<ASkyguardDrone>(
		FVector(0.f, 0.f, 40.f),
		FRotator::ZeroRotator);
	ASkyguardDrone* Truck = World->SpawnActor<ASkyguardDrone>(
		FVector(100.f, 0.f, 92.f),
		FRotator::ZeroRotator);
	TestNotNull(TEXT("boat"), Boat);
	TestNotNull(TEXT("truck"), Truck);
	if (!Boat || !Truck)
	{
		World->DestroyWorld(false);
		return false;
	}

	Boat->ConfigureThreat(ESkyguardThreatKind::FastBoat);
	const TArray<FVector> Path = {
		FVector(100.f, 0.f, 92.f),
		FVector(100.f, 2000.f, 92.f)
	};
	Truck->ConfigureRoadConvoy(Path, 0, TEXT("Vehicle.Truck"));

	TestEqual(
		TEXT("named ground-column pace"),
		Truck->CruiseSpeed,
		ASkyguardDrone::RoadConvoyCruiseSpeed);
	TestTrue(
		TEXT("convoy cruise sits in the 250-400 ground band"),
		Truck->CruiseSpeed >= 250.f && Truck->CruiseSpeed <= 400.f);
	TestTrue(
		TEXT("convoy crawls slower than a FastBoat"),
		Truck->CruiseSpeed < Boat->CruiseSpeed);
	TestTrue(
		TEXT("FastBoat default stays a sea sprint"),
		Boat->CruiseSpeed >= 650.f);

	ASkyguardGunshipSortieDirector* Director =
		World->SpawnActor<ASkyguardGunshipSortieDirector>();
	TestNotNull(TEXT("director"), Director);
	if (!Director)
	{
		World->DestroyWorld(false);
		return false;
	}
	Director->bAutoStart = false;
	Director->SpawnCoastalConvoy();

	TArray<ASkyguardDrone*> Convoy;
	SkyguardCoastalConvoyTest::CollectLiveRoadConvoy(World, Convoy);
	TestTrue(TEXT("spawned column exists"), Convoy.Num() >= 5);
	for (const ASkyguardDrone* Threat : Convoy)
	{
		if (Threat == Truck)
		{
			continue;
		}
		TestEqual(
			TEXT("spawned column uses the named convoy speed"),
			Threat->CruiseSpeed,
			ASkyguardDrone::RoadConvoyCruiseSpeed);
	}

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCoastalConvoyNeedsAWeaponDecisionTest,
	"Skyguard52.Campaign.CoastalConvoyNeedsAWeaponDecision",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCoastalConvoyNeedsAWeaponDecisionTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardConvoyHealthWorld"));
	TestNotNull(TEXT("world"), World);
	if (!World)
	{
		return false;
	}

	ASkyguardDrone* Truck = World->SpawnActor<ASkyguardDrone>(
		FVector::ZeroVector, FRotator::ZeroRotator);
	ASkyguardDrone* Bus = World->SpawnActor<ASkyguardDrone>(
		FVector(200.f, 0.f, 0.f), FRotator::ZeroRotator);
	ASkyguardDrone* Car = World->SpawnActor<ASkyguardDrone>(
		FVector(400.f, 0.f, 0.f), FRotator::ZeroRotator);
	ASkyguardDrone* Fast = World->SpawnActor<ASkyguardDrone>(
		FVector(600.f, 0.f, 0.f), FRotator::ZeroRotator);
	TestNotNull(TEXT("truck"), Truck);
	TestNotNull(TEXT("bus"), Bus);
	TestNotNull(TEXT("car"), Car);
	TestNotNull(TEXT("fast attacker"), Fast);
	if (!Truck || !Bus || !Car || !Fast)
	{
		World->DestroyWorld(false);
		return false;
	}

	const TArray<FVector> Path = {
		FVector::ZeroVector,
		FVector(0.f, 1200.f, 0.f)
	};
	Truck->ConfigureRoadConvoy(Path, 0, TEXT("Vehicle.Truck"));
	Bus->ConfigureRoadConvoy(Path, 0, TEXT("Vehicle.Bus"));
	Car->ConfigureRoadConvoy(Path, 0, TEXT("Vehicle.Car"));
	Fast->ConfigureThreat(ESkyguardThreatKind::FastAttacker);

	TestEqual(
		TEXT("truck uses named convoy hull"),
		Truck->MaxHealth,
		ASkyguardDrone::RoadConvoyTruckHealth);
	TestEqual(
		TEXT("bus matches truck hull"),
		Bus->MaxHealth,
		ASkyguardDrone::RoadConvoyTruckHealth);
	TestEqual(
		TEXT("car is the softer convoy slot"),
		Car->MaxHealth,
		ASkyguardDrone::RoadConvoyCarHealth);
	TestTrue(TEXT("truck/bus tougher than car"), Truck->MaxHealth > Car->MaxHealth);
	TestTrue(TEXT("bus tougher than car"), Bus->MaxHealth > Car->MaxHealth);
	TestTrue(
		TEXT("car is still armor, not a 34-hp drone"),
		Car->MaxHealth > Fast->MaxHealth);
	TestEqual(TEXT("FastAttacker stays 34"), Fast->MaxHealth, 34.f);

	// Cannon pecks (52). A short burst must not wreck a truck; a Hellfire-class
	// hit (280) must. Do not retune gunner stations here.
	Truck->ApplyBallisticHit(52.f, Truck->GetActorLocation(), FVector::ForwardVector);
	Truck->ApplyBallisticHit(52.f, Truck->GetActorLocation(), FVector::ForwardVector);
	Truck->ApplyBallisticHit(52.f, Truck->GetActorLocation(), FVector::ForwardVector);
	TestFalse(TEXT("short cannon burst pecks the truck"), Truck->IsDestroyed());
	Truck->ApplyBallisticHit(280.f, Truck->GetActorLocation(), FVector::ForwardVector);
	TestTrue(TEXT("missile-class hit finishes the truck"), Truck->IsDestroyed());

	World->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FSkyguardCoastalConvoyStaysOnHighwayTest,
	"Skyguard52.Campaign.CoastalConvoyStaysOnHighway",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FSkyguardCoastalConvoyStaysOnHighwayTest::RunTest(const FString& Parameters)
{
	UWorld* World = UWorld::CreateWorld(
		EWorldType::Game, false, TEXT("SkyguardConvoyFollowWorld"));
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
	Director->SpawnCoastalConvoy();

	const TArray<FVector> Path =
		ASkyguardGunshipSortieDirector::GetCoastalHighwayPath();
	TArray<ASkyguardDrone*> Convoy;
	SkyguardCoastalConvoyTest::CollectLiveRoadConvoy(World, Convoy);
	TestEqual(
		TEXT("five live road-followers after spawn"),
		Convoy.Num(),
		ASkyguardGunshipSortieDirector::CoastalConvoyCount);

	for (int32 Step = 0; Step < 8; ++Step)
	{
		for (ASkyguardDrone* Threat : Convoy)
		{
			Threat->Tick(0.25f);
		}
	}

	constexpr float MaxOffRoadCm = 220.f;
	for (const ASkyguardDrone* Threat : Convoy)
	{
		const float OffRoad = SkyguardCoastalConvoyTest::DistanceToPolylineXY(
			Threat->GetActorLocation(),
			Path,
			true);
		TestTrue(
			TEXT("after TickRoadFollow the hull stays on the yellow-road polyline"),
			OffRoad <= MaxOffRoadCm);
		TestTrue(TEXT("still a road follower"), Threat->IsFollowingRoad());
	}

	World->DestroyWorld(false);
	return true;
}

#endif
