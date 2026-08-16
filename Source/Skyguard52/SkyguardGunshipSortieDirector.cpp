#include "SkyguardGunshipSortieDirector.h"

#include "SkyguardApacheAircraft.h"
#include "SkyguardArcadeLookComponent.h"
#include "SkyguardCampaignRoster.h"
#include "SkyguardDrone.h"
#include "SkyguardGunner.h"
#include "SkyguardPatrolShipBoss.h"
#include "SkyguardPilotVoice.h"
#include "SkyguardPlayerAircraft.h"
#include "SkyguardProtectAsset.h"
#include "SkyguardRadarNode.h"
#include "CollisionQueryParams.h"
#include "Engine/Engine.h"
#include "Engine/HitResult.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "WorldCollision.h"
#include "GameFramework/Actor.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"

ASkyguardGunshipSortieDirector::ASkyguardGunshipSortieDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	Tags.AddUnique(TEXT("Skyguard.GunshipSortie"));
}

void ASkyguardGunshipSortieDirector::BeginPlay()
{
	Super::BeginPlay();
	ASkyguardDrone::OnAnyCityImpacted.AddUObject(
		this, &ASkyguardGunshipSortieDirector::HandleDroneImpact);
	if (bAutoStart)
	{
		StartMissionIndex(StartingMissionIndex);
	}
}

void ASkyguardGunshipSortieDirector::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	ASkyguardDrone::OnAnyCityImpacted.RemoveAll(this);
	Super::EndPlay(EndPlayReason);
}

void ASkyguardGunshipSortieDirector::StartMissionIndex(const int32 Index)
{
	MissionIndex = FMath::Clamp(
		Index, 0, SkyguardCampaignRoster::NumMissions() - 1);
	Elapsed = 0.f;
	IncomingCooldown = IncomingFirstDelaySeconds;
	IncomingWindow = 0.f;
	bInbound = false;
	PostSortieSeconds = 0.f;
	bClimaxSpawned = false;
	bExtractSpawned = false;
	bChoiceRadarFirst = false;
	bAwaitingContinue = false;
	ThreatsKilled = 0;
	LastCargoFraction = 1.f;
	Beat = ESkyguardSortieBeat::Approach;
	if (PatrolShip)
	{
		PatrolShip->Destroy();
		PatrolShip = nullptr;
	}
	EnsureSetPieces();
	DestroyRoadConvoy();
	NextRoadConvoySlot = 0;
	SpawnCoastalConvoy();
	if (Cargo)
	{
		Cargo->ResetIntegrity();
	}
	if (Radar)
	{
		Radar->ResetNode();
	}
	const FSkyguardCampaignMissionSpec& Spec =
		SkyguardCampaignRoster::Get(MissionIndex);
	USkyguardArcadeLookComponent::ApplyWorldMoodForWeather(this, Spec.Weather);
	if (Spec.bNightIdentity)
	{
		SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::GoThermal);
	}
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(
			84720,
			6.f,
			FColor::White,
			FString::Printf(
				TEXT("%s — %s"),
				Spec.Title,
				Spec.Brief));
	}
	SkyguardPilotVoice::ConfirmCommand(this, ESkyguardPilotCommand::Hold);
}

void ASkyguardGunshipSortieDirector::StartNextMission()
{
	if (MissionIndex + 1 >= SkyguardCampaignRoster::NumMissions())
	{
		return;
	}
	StartMissionIndex(MissionIndex + 1);
}

FName ASkyguardGunshipSortieDirector::GetMissionId() const
{
	return SkyguardCampaignRoster::IdAt(MissionIndex);
}

FString ASkyguardGunshipSortieDirector::GetMissionTitle() const
{
	return SkyguardCampaignRoster::Get(MissionIndex).Title;
}

int32 ASkyguardGunshipSortieDirector::BeatWaveCount(const ESkyguardSortieBeat InBeat)
{
	switch (InBeat)
	{
	case ESkyguardSortieBeat::InitialContact:
		return ContactWaveCount;
	case ESkyguardSortieBeat::ShoreAssault:
		return ShoreWaveCount;
	case ESkyguardSortieBeat::RadarNet:
		return RadarNetWaveCount;
	case ESkyguardSortieBeat::Choice:
		return ChoiceWaveCount;
	case ESkyguardSortieBeat::Extraction:
		return ExtractWaveCount;
	case ESkyguardSortieBeat::Approach:
	case ESkyguardSortieBeat::Climax:
	case ESkyguardSortieBeat::Succeeded:
	case ESkyguardSortieBeat::Failed:
		return 0;
	default:
		return 0;
	}
}

ESkyguardThreatKind ASkyguardGunshipSortieDirector::BeatWaveKind(
	const int32 InMissionIndex,
	const ESkyguardSortieBeat InBeat)
{
	const FSkyguardCampaignMissionSpec& Spec =
		SkyguardCampaignRoster::Get(InMissionIndex);
	switch (InBeat)
	{
	case ESkyguardSortieBeat::InitialContact:
		return Spec.ContactKind;
	case ESkyguardSortieBeat::ShoreAssault:
		return Spec.ShoreKind;
	case ESkyguardSortieBeat::RadarNet:
		return Spec.SupportKind;
	case ESkyguardSortieBeat::Choice:
		return Spec.ContactKind;
	case ESkyguardSortieBeat::Extraction:
		return Spec.ExtractKind;
	case ESkyguardSortieBeat::Approach:
	case ESkyguardSortieBeat::Climax:
	case ESkyguardSortieBeat::Succeeded:
	case ESkyguardSortieBeat::Failed:
		return Spec.ContactKind;
	default:
		return Spec.ContactKind;
	}
}

float ASkyguardGunshipSortieDirector::IncomingIntervalSeconds(const bool bRadarLive)
{
	return bRadarLive
		? IncomingRadarLiveIntervalSeconds
		: IncomingRadarDownIntervalSeconds;
}

bool ASkyguardGunshipSortieDirector::BeatAllowsInbound(const ESkyguardSortieBeat InBeat)
{
	switch (InBeat)
	{
	case ESkyguardSortieBeat::Approach:
	case ESkyguardSortieBeat::Succeeded:
	case ESkyguardSortieBeat::Failed:
		return false;
	case ESkyguardSortieBeat::InitialContact:
	case ESkyguardSortieBeat::ShoreAssault:
	case ESkyguardSortieBeat::RadarNet:
	case ESkyguardSortieBeat::Choice:
	case ESkyguardSortieBeat::Climax:
	case ESkyguardSortieBeat::Extraction:
		return true;
	default:
		return false;
	}
}

bool ASkyguardGunshipSortieDirector::UsesRadarLiveInboundCadence(
	const ESkyguardSortieBeat InBeat)
{
	switch (InBeat)
	{
	case ESkyguardSortieBeat::RadarNet:
	case ESkyguardSortieBeat::Choice:
	case ESkyguardSortieBeat::Climax:
	case ESkyguardSortieBeat::Extraction:
		return true;
	case ESkyguardSortieBeat::Approach:
	case ESkyguardSortieBeat::InitialContact:
	case ESkyguardSortieBeat::ShoreAssault:
	case ESkyguardSortieBeat::Succeeded:
	case ESkyguardSortieBeat::Failed:
		return false;
	default:
		return false;
	}
}

bool ASkyguardGunshipSortieDirector::HasInboundSource(
	const ESkyguardSortieBeat InBeat,
	const bool bShoreAda,
	const bool bShipCanLaunch)
{
	if (!BeatAllowsInbound(InBeat))
	{
		return false;
	}
	const bool bClimaxShip =
		InBeat == ESkyguardSortieBeat::Climax ||
		InBeat == ESkyguardSortieBeat::Extraction;
	// Approach is already refused. Before the hull is in play, the shore
	// net can still fire. Once the ship is up, inbound dies if the
	// launcher is dead and the shore net is gone.
	return !bClimaxShip || bShoreAda || bShipCanLaunch;
}

void ASkyguardGunshipSortieDirector::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (IsSortieOver())
	{
		HandleDebriefInput();
		return;
	}
	Elapsed += DeltaSeconds;
	AdvanceBeats();
	TickIncoming(DeltaSeconds);
	TickShipSystems(DeltaSeconds);

	if (Cargo)
	{
		const float CargoNow = Cargo->GetIntegrityFraction();
		if (CargoNow < LastCargoFraction - 0.08f)
		{
			SkyguardPilotVoice::CallEvent(
				this,
				CargoNow < 0.35f
					? ESkyguardPilotLine::CargoCritical
					: ESkyguardPilotLine::CargoHit);
			LastCargoFraction = CargoNow;
		}
		if (Cargo->IsDestroyed())
		{
			ResolveFail(TEXT("The cargo hull is gone."));
			return;
		}
	}
	if (ASkyguardApacheAircraft* Apache = FindApache())
	{
		if (Apache->GetDamageFraction() >= 1.f)
		{
			ResolveFail(TEXT("We're hit. Autorotating — that's a wrap."));
			return;
		}
	}
	if (Beat == ESkyguardSortieBeat::Extraction &&
		Elapsed >= SkyguardCampaignRoster::Get(MissionIndex).BeatSeconds[6])
	{
		ResolveWin();
	}
}

void ASkyguardGunshipSortieDirector::AdvanceBeats()
{
	const FSkyguardCampaignMissionSpec& Spec =
		SkyguardCampaignRoster::Get(MissionIndex);
	if (Beat == ESkyguardSortieBeat::Approach && Elapsed >= Spec.BeatSeconds[0])
	{
		EnterBeat(ESkyguardSortieBeat::InitialContact);
	}
	else if (Beat == ESkyguardSortieBeat::InitialContact &&
		Elapsed >= Spec.BeatSeconds[1])
	{
		EnterBeat(ESkyguardSortieBeat::ShoreAssault);
	}
	else if (Beat == ESkyguardSortieBeat::ShoreAssault &&
		Elapsed >= Spec.BeatSeconds[2])
	{
		EnterBeat(ESkyguardSortieBeat::RadarNet);
	}
	else if (Beat == ESkyguardSortieBeat::RadarNet &&
		Elapsed >= Spec.BeatSeconds[3])
	{
		EnterBeat(ESkyguardSortieBeat::Choice);
	}
	else if (Beat == ESkyguardSortieBeat::Choice &&
		Elapsed >= Spec.BeatSeconds[4])
	{
		EnterBeat(ESkyguardSortieBeat::Climax);
	}
	else if (Beat == ESkyguardSortieBeat::Climax &&
		Elapsed >= Spec.BeatSeconds[5])
	{
		EnterBeat(ESkyguardSortieBeat::Extraction);
	}
}

void ASkyguardGunshipSortieDirector::EnterBeat(const ESkyguardSortieBeat NewBeat)
{
	Beat = NewBeat;
	SpawnBeatWave();
	switch (NewBeat)
	{
	case ESkyguardSortieBeat::RadarNet:
		IncomingCooldown = FMath::Min(IncomingCooldown, IncomingRadarLitDelaySeconds);
		SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::RadarLit);
		break;
	case ESkyguardSortieBeat::Choice:
		bChoiceRadarFirst = Radar && !Radar->IsDestroyed();
		SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::Choice);
		break;
	case ESkyguardSortieBeat::Climax:
		break;
	case ESkyguardSortieBeat::Extraction:
		SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::Extract);
		break;
	default:
		break;
	}
}

void ASkyguardGunshipSortieDirector::EnsureSetPieces()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	ASkyguardApacheAircraft* Apache = FindApache();
	const FVector ApacheLoc = Apache
		? Apache->GetActorLocation()
		: FVector(2500.f, -8000.f, 2200.f);
	const FVector Forward = Apache
		? Apache->GetActorForwardVector()
		: FVector(-1.f, 0.f, 0.f);
	const FVector Right = Apache
		? Apache->GetActorRightVector()
		: FVector(0.f, 1.f, 0.f);
	const FVector Harbor = ApacheLoc + Forward * 3800.f + Right * -600.f;

	if (!Cargo)
	{
		FVector CargoLoc = Harbor;
		CargoLoc.Z = 90.f;
		Cargo = World->SpawnActor<ASkyguardProtectAsset>(
			CargoLoc, Forward.Rotation());
	}
	if (!Radar)
	{
		FVector RadarLoc = Harbor + Right * 1600.f + Forward * 400.f;
		RadarLoc.Z = 110.f;
		Radar = World->SpawnActor<ASkyguardRadarNode>(
			RadarLoc, Forward.Rotation());
	}
}

void ASkyguardGunshipSortieDirector::SpawnBeatWave()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	ASkyguardApacheAircraft* Apache = FindApache();
	const FVector Origin = Apache ? Apache->GetActorLocation() : GetActorLocation();
	const FVector Forward = Apache
		? Apache->GetActorForwardVector()
		: FVector(-1.f, 0.f, 0.f);
	const FVector Right = Apache
		? Apache->GetActorRightVector()
		: FVector(0.f, 1.f, 0.f);
	const FVector Ahead = Origin + Forward * 2800.f;

	const FSkyguardCampaignMissionSpec& Spec =
		SkyguardCampaignRoster::Get(MissionIndex);
	int32 Count = BeatWaveCount(Beat);
	if (Beat == ESkyguardSortieBeat::Extraction && bExtractSpawned)
	{
		Count = 0;
	}
	for (int32 Index = 0; Index < Count; ++Index)
	{
		const FVector Loc = Ahead
			+ Forward * FMath::FRandRange(-400.f, 600.f)
			+ Right * (-1600.f + Index * 800.f)
			+ FVector(0.f, 0.f, FMath::FRandRange(-200.f, 200.f));
		SpawnThreat(BeatWaveKind(MissionIndex, Beat), Loc);
	}

	if (Beat == ESkyguardSortieBeat::Climax && !bClimaxSpawned)
	{
		bClimaxSpawned = true;
		switch (Spec.Climax)
		{
		case ESkyguardClimaxKind::RivalHelo:
			SpawnThreat(ESkyguardThreatKind::RotorScout, Ahead + FVector(0.f, 400.f, 280.f));
			SpawnThreat(ESkyguardThreatKind::RotorScout, Ahead + FVector(200.f, -500.f, 240.f));
			SpawnThreat(ESkyguardThreatKind::RotorScout, Ahead + FVector(-200.f, 0.f, 320.f));
			break;
		case ESkyguardClimaxKind::ArmorColumn:
			for (int32 Index = 0; Index < 5; ++Index)
			{
				SpawnThreat(
					ESkyguardThreatKind::GroundArmor,
					Ahead + FVector(-200.f + Index * 180.f, -800.f + Index * 220.f, -500.f));
			}
			break;
		case ESkyguardClimaxKind::MixedSwarm:
			SpawnThreat(ESkyguardThreatKind::HeavyAttacker, Ahead);
			SpawnThreat(ESkyguardThreatKind::RotorScout, Ahead + FVector(0.f, 600.f, 200.f));
			SpawnThreat(ESkyguardThreatKind::GroundArmor, Ahead + FVector(400.f, -400.f, -400.f));
			break;
		case ESkyguardClimaxKind::PatrolShip:
		default:
			PatrolShip = World->SpawnActor<ASkyguardPatrolShipBoss>(
				Ahead + FVector(1400.f, 0.f, -900.f),
				FRotator(0.f, 180.f, 0.f));
			break;
		}
	}
	if (Beat == ESkyguardSortieBeat::Extraction)
	{
		bExtractSpawned = true;
	}
}

TArray<FVector> ASkyguardGunshipSortieDirector::GetCoastalHighwayPath()
{
	// World-space coastal strip between HarborHover (2500, -8000) and the city
	// (-1800, 0). Vehicles travel north along the yellow road in the CPG view.
	// North apex sits at (-1000, 3200) so the old 632 cm hairpin becomes a
	// ~12 m / ~16 m turn. XY stays in the HarborHover → city corridor.
	return {
		FVector(2100.f, -6400.f, 92.f),
		FVector(1400.f, -5000.f, 92.f),
		FVector(600.f, -3600.f, 92.f),
		FVector(-200.f, -2200.f, 92.f),
		FVector(-900.f, -900.f, 92.f),
		FVector(-1600.f, 200.f, 92.f),
		FVector(-2000.f, 1500.f, 92.f),
		FVector(-2200.f, 2800.f, 92.f),
		FVector(-1000.f, 3200.f, 92.f),
		FVector(-800.f, 1600.f, 92.f),
		FVector(-200.f, 200.f, 92.f),
		FVector(600.f, -1200.f, 92.f),
		FVector(1400.f, -2800.f, 92.f),
		FVector(2000.f, -4600.f, 92.f)
	};
}

float ASkyguardGunshipSortieDirector::SnapRoadHeight(
	const UWorld* World,
	const FVector& Horizontal)
{
	if (!World)
	{
		return Horizontal.Z;
	}
	FHitResult Hit;
	const FVector Start(Horizontal.X, Horizontal.Y, 6000.f);
	const FVector End(Horizontal.X, Horizontal.Y, -800.f);
	FCollisionQueryParams Params(SCENE_QUERY_STAT(SkyguardConvoyGround), true);
	if (World->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params) &&
		Hit.bBlockingHit)
	{
		return Hit.ImpactPoint.Z + 46.f;
	}
	return Horizontal.Z;
}

TArray<FVector> ASkyguardGunshipSortieDirector::BuildGroundedCoastalHighwayPath() const
{
	TArray<FVector> Path = GetCoastalHighwayPath();
	UWorld* World = GetWorld();
	for (FVector& Point : Path)
	{
		Point.Z = SnapRoadHeight(World, Point);
	}
	return Path;
}

FName ASkyguardGunshipSortieDirector::ConvoyVehicleSlotForIndex(const int32 Index)
{
	switch (FMath::Abs(Index) % 5)
	{
	case 1:
		return TEXT("Vehicle.Car");
	case 3:
		return TEXT("Vehicle.Bus");
	default:
		return TEXT("Vehicle.Truck");
	}
}

void ASkyguardGunshipSortieDirector::DestroyRoadConvoy()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	TArray<ASkyguardDrone*> Convoy;
	for (TActorIterator<ASkyguardDrone> It(World); It; ++It)
	{
		ASkyguardDrone* Threat = *It;
		if (Threat && Threat->IsFollowingRoad())
		{
			Convoy.Add(Threat);
		}
	}
	for (ASkyguardDrone* Threat : Convoy)
	{
		Threat->Destroy();
	}
}

int32 ASkyguardGunshipSortieDirector::CountLiveRoadConvoy() const
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return 0;
	}
	int32 Count = 0;
	for (TActorIterator<ASkyguardDrone> It(World); It; ++It)
	{
		const ASkyguardDrone* Threat = *It;
		if (Threat && !Threat->IsDestroyed() && Threat->IsFollowingRoad())
		{
			++Count;
		}
	}
	return Count;
}

void ASkyguardGunshipSortieDirector::BindThreatToCoastalRoad(ASkyguardDrone* Threat)
{
	if (!Threat)
	{
		return;
	}
	const TArray<FVector> Path = BuildGroundedCoastalHighwayPath();
	if (Path.Num() < 2)
	{
		return;
	}
	const int32 StartIndex = NextRoadConvoySlot++ % Path.Num();
	Threat->ConfigureRoadConvoy(
		Path,
		StartIndex,
		ConvoyVehicleSlotForIndex(StartIndex));
}

int32 ASkyguardGunshipSortieDirector::SpawnCoastalConvoy()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return 0;
	}
	const TArray<FVector> Path = BuildGroundedCoastalHighwayPath();
	if (Path.Num() < 2)
	{
		return 0;
	}

	int32 Spawned = 0;
	for (int32 Index = 0; Index < CoastalConvoyCount; ++Index)
	{
		// Every other authored point: a readable northbound column on the
		// yellow road, not five hulls stacked on the first five waypoints.
		const int32 Waypoint = (Index * 2) % Path.Num();
		const FTransform Transform(
			FRotator::ZeroRotator,
			Path[Waypoint]);
		ASkyguardDrone* Threat = World->SpawnActorDeferred<ASkyguardDrone>(
			ASkyguardDrone::StaticClass(),
			Transform,
			nullptr,
			nullptr,
			ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
		if (!Threat)
		{
			continue;
		}
		Threat->ConfigureThreat(ESkyguardThreatKind::GroundArmor);
		if (Cargo)
		{
			Threat->TargetCityLocation = Cargo->GetActorLocation();
		}
		Threat->FinishSpawning(Transform);
		Threat->ConfigureRoadConvoy(
			Path,
			Waypoint,
			ConvoyVehicleSlotForIndex(Index));
		++NextRoadConvoySlot;
		++Spawned;
	}
	return Spawned;
}

void ASkyguardGunshipSortieDirector::SpawnThreat(
	const ESkyguardThreatKind Kind,
	const FVector& Location)
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	FTransform Transform(FRotator(0.f, 180.f, 0.f), Location);
	ASkyguardDrone* Threat = World->SpawnActorDeferred<ASkyguardDrone>(
		ASkyguardDrone::StaticClass(),
		Transform,
		nullptr,
		nullptr,
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
	if (!Threat)
	{
		return;
	}
	Threat->ConfigureThreat(Kind);
	if (Cargo)
	{
		Threat->TargetCityLocation = Cargo->GetActorLocation();
	}
	Threat->FinishSpawning(Transform);
}

void ASkyguardGunshipSortieDirector::HandleDroneImpact(ASkyguardDrone* Drone)
{
	if (!Drone || !Cargo || Cargo->IsDestroyed())
	{
		return;
	}
	Cargo->ApplyDamage(Drone->IsHeavyTarget() ? 16.f : 9.f);
}

void ASkyguardGunshipSortieDirector::TickIncoming(const float DeltaSeconds)
{
	ASkyguardGunner* Gunner = FindGunner();
	if (!Gunner)
	{
		return;
	}
	const bool bShoreAda = Radar && !Radar->IsDestroyed();
	const bool bShipAda = PatrolShip && PatrolShip->CanCoordinateAda();
	const bool bShipCanLaunch = PatrolShip && PatrolShip->CanLaunchInbound();
	const bool bCoordinatorLive = bShoreAda || bShipAda;
	const bool bRadarLive =
		bCoordinatorLive && UsesRadarLiveInboundCadence(Beat);
	IncomingCooldown -= DeltaSeconds;
	const float Interval = IncomingIntervalSeconds(bRadarLive);
	if (IncomingCooldown <= 0.f &&
		HasInboundSource(Beat, bShoreAda, bShipCanLaunch) &&
		!IsSortieOver())
	{
		IncomingCooldown = Interval;
		bInbound = true;
		IncomingWindow = IncomingWindowSeconds;
		Gunner->NotifyMissileInbound();
		SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::Inbound);
	}
	if (bInbound)
	{
		IncomingWindow -= DeltaSeconds;
		if (Gunner->TryDefeatInboundWithFlares())
		{
			bInbound = false;
			SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::FlaresGood);
		}
		else if (IncomingWindow <= 0.f)
		{
			bInbound = false;
			if (ASkyguardApacheAircraft* Apache = FindApache())
			{
				Apache->ApplyDamage(
					bRadarLive
						? IncomingRadarLiveHitDamage
						: IncomingRadarDownHitDamage);
			}
		}
	}
}

void ASkyguardGunshipSortieDirector::TickShipSystems(const float DeltaSeconds)
{
	if (!PatrolShip ||
		(Beat != ESkyguardSortieBeat::Climax &&
			Beat != ESkyguardSortieBeat::Extraction))
	{
		return;
	}
	if (!PatrolShip->ConsumeDeckLaunch(DeltaSeconds))
	{
		return;
	}
	const FVector Deck = PatrolShip->GetActorLocation() + FVector(0.f, 0.f, 280.f);
	SpawnThreat(ESkyguardThreatKind::RotorScout, Deck);
}

void ASkyguardGunshipSortieDirector::ResolveWin()
{
	Beat = ESkyguardSortieBeat::Succeeded;
	bAwaitingContinue = true;
	ScoreSortie(true);
	SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::Win);
	SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::LoadoutPrompt);
	ShowDebrief();
}

void ASkyguardGunshipSortieDirector::ResolveFail(const TCHAR* Reason)
{
	Beat = ESkyguardSortieBeat::Failed;
	bAwaitingContinue = true;
	ScoreSortie(false);
	SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::Fail);
	SkyguardPilotVoice::CallEvent(this, ESkyguardPilotLine::LoadoutPrompt);
	ShowDebrief();
	if (GEngine && Reason)
	{
		GEngine->AddOnScreenDebugMessage(84723, 6.f, FColor::Red, Reason);
	}
}

void ASkyguardGunshipSortieDirector::ScoreSortie(const bool bWon)
{
	const float CargoFrac = Cargo ? Cargo->GetIntegrityFraction() : 0.f;
	const int32 RadarBonus = (Radar && Radar->IsDestroyed()) ? 1500 : 0;
	const int32 ShipBonus = PatrolShip ? PatrolShip->GetDestroyedSystemCount() * 400 : 0;
	const ASkyguardGunner* Gunner = FindGunner();
	const int32 Hits = Gunner ? Gunner->GetSortieHits() : 0;
	const float Damage = Gunner ? Gunner->GetSortieAircraftDamageFraction() : 0.f;
	LastScore = (bWon ? 4000 : 500)
		+ FMath::RoundToInt(CargoFrac * 3000.f)
		+ RadarBonus
		+ ShipBonus
		+ Hits * 12
		- FMath::RoundToInt(Damage * 2000.f);
	LastScore = FMath::Max(0, LastScore);
	LastMedal = LastScore >= 11000 ? 3 : (LastScore >= 8000 ? 2 : (LastScore >= 5000 ? 1 : 0));
}

void ASkyguardGunshipSortieDirector::ShowDebrief() const
{
	if (!GEngine)
	{
		return;
	}
	const FSkyguardCampaignMissionSpec& Spec =
		SkyguardCampaignRoster::Get(MissionIndex);
	const TCHAR* Medal =
		LastMedal >= 3 ? TEXT("Gold") :
		LastMedal == 2 ? TEXT("Silver") :
		LastMedal == 1 ? TEXT("Bronze") : TEXT("None");
	const float CargoFrac = Cargo ? Cargo->GetIntegrityFraction() : 0.f;
	const int32 Systems = PatrolShip ? PatrolShip->GetDestroyedSystemCount() : 0;
	const FString ShipTape = PatrolShip
		? PatrolShip->GetHudSystemLine()
		: FString(TEXT("RADAR GUN LNCH ENG DECK"));
	GEngine->AddOnScreenDebugMessage(
		84730,
		30.f,
		FColor::White,
		FString::Printf(
			TEXT("%s — %s\nScore %d   Medal: %s\nCargo %d%%   Radar %s\nShip %d/5  %s\nLoadout: 1 Anti-Armor  2 Rockets  3 Intercept  4 Balanced\n%s   Current: %s"),
			Spec.Title,
			Beat == ESkyguardSortieBeat::Succeeded ? Spec.Success : Spec.Failure,
			LastScore,
			Medal,
			FMath::RoundToInt(CargoFrac * 100.f),
			(Radar && Radar->IsDestroyed()) ? TEXT("dead") : TEXT("alive"),
			Systems,
			*ShipTape,
			Beat == ESkyguardSortieBeat::Succeeded
				? TEXT("N / Enter  next sortie")
				: TEXT("N / Enter  retry"),
			SkyguardCampaignRoster::LoadoutLabel(PendingLoadout)));
}

void ASkyguardGunshipSortieDirector::SetPendingLoadout(const ESkyguardLoadout Loadout)
{
	PendingLoadout = Loadout;
	ShowDebrief();
}

void ASkyguardGunshipSortieDirector::ApplyPendingLoadout()
{
	if (ASkyguardGunner* Gunner = FindGunner())
	{
		Gunner->ApplyLoadout(PendingLoadout);
	}
}

void ASkyguardGunshipSortieDirector::ConfirmContinue()
{
	if (!bAwaitingContinue)
	{
		return;
	}
	bAwaitingContinue = false;
	ApplyPendingLoadout();
	if (Beat == ESkyguardSortieBeat::Succeeded)
	{
		if (MissionIndex + 1 < SkyguardCampaignRoster::NumMissions())
		{
			StartNextMission();
		}
		return;
	}
	StartMissionIndex(MissionIndex);
}

void ASkyguardGunshipSortieDirector::HandleDebriefInput()
{
	APlayerController* PC = GetWorld()
		? GetWorld()->GetFirstPlayerController()
		: nullptr;
	if (!PC)
	{
		return;
	}
	if (PC->WasInputKeyJustPressed(EKeys::One))
	{
		SetPendingLoadout(ESkyguardLoadout::AntiArmor);
	}
	else if (PC->WasInputKeyJustPressed(EKeys::Two))
	{
		SetPendingLoadout(ESkyguardLoadout::RocketHeavy);
	}
	else if (PC->WasInputKeyJustPressed(EKeys::Three))
	{
		SetPendingLoadout(ESkyguardLoadout::Intercept);
	}
	else if (PC->WasInputKeyJustPressed(EKeys::Four))
	{
		SetPendingLoadout(ESkyguardLoadout::Balanced);
	}
	else if (PC->WasInputKeyJustPressed(EKeys::N) ||
		PC->WasInputKeyJustPressed(EKeys::Enter))
	{
		ConfirmContinue();
	}
}

ASkyguardApacheAircraft* ASkyguardGunshipSortieDirector::FindApache() const
{
	return FSkyguardPlayerAircraft::FindApache(GetWorld());
}

ASkyguardGunner* ASkyguardGunshipSortieDirector::FindGunner() const
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return nullptr;
	}
	for (TActorIterator<ASkyguardGunner> It(World); It; ++It)
	{
		if (IsValid(*It))
		{
			return *It;
		}
	}
	return nullptr;
}
