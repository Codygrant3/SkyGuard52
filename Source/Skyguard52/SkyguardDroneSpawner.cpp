#include "SkyguardDroneSpawner.h"
#include "SkyguardDrone.h"
#include "SkyguardThreatTypes.h"
#include "Engine/World.h"
#include "EngineUtils.h"

ASkyguardDroneSpawner::ASkyguardDroneSpawner()
{
	PrimaryActorTick.bCanEverTick = true;
}

void ASkyguardDroneSpawner::SetSpawningEnabled(const bool bEnabled)
{
	bSpawningEnabled = bEnabled;
}

void ASkyguardDroneSpawner::BeginPlay()
{
	Super::BeginPlay();
	SpawnTimer = 0.5f;
}

int32 ASkyguardDroneSpawner::CountActiveDrones() const
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return 0;
	}

	int32 ActiveCount = 0;
	for (TActorIterator<ASkyguardDrone> It(World); It; ++It)
	{
		const ASkyguardDrone* Drone = *It;
		if (Drone && !Drone->IsDestroyed())
		{
			++ActiveCount;
		}
	}
	return ActiveCount;
}

void ASkyguardDroneSpawner::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!bSpawningEnabled)
	{
		return;
	}
	SpawnTimer -= DeltaSeconds;
	if (SpawnTimer > 0.f) return;
	SpawnTimer = SpawnInterval;

	if (!GetWorld()) return;
	if (CountActiveDrones() >= MaxActiveDrones)
	{
		return;
	}

	const int32 Lane = FMath::RandRange(0, 5);
	const bool bHeavy =
		HeavyLaneModulo > 0 && Lane % HeavyLaneModulo == 0;
	ESkyguardThreatKind Kind = bHeavy
		? ESkyguardThreatKind::HeavyAttacker
		: ESkyguardThreatKind::FastAttacker;
	if (bMixedThreatRoster)
	{
		switch (Lane % 5)
		{
		case 0:
			Kind = ESkyguardThreatKind::HeavyAttacker;
			break;
		case 1:
			Kind = ESkyguardThreatKind::RotorScout;
			break;
		case 2:
			Kind = ESkyguardThreatKind::GroundArmor;
			break;
		case 3:
			Kind = ESkyguardThreatKind::FastBoat;
			break;
		default:
			Kind = ESkyguardThreatKind::FastAttacker;
			break;
		}
	}
	const float Y = -1800.f + Lane * 700.f + FMath::FRandRange(-80.f, 80.f);
	float Z = 360.f + FMath::FRandRange(0.f, 160.f);
	switch (Kind)
	{
	case ESkyguardThreatKind::RotorScout:
		Z = 620.f + FMath::FRandRange(0.f, 180.f);
		break;
	case ESkyguardThreatKind::GroundArmor:
		Z = 70.f + FMath::FRandRange(0.f, 30.f);
		break;
	case ESkyguardThreatKind::FastBoat:
		Z = 36.f + FMath::FRandRange(0.f, 18.f);
		break;
	default:
		break;
	}
	const FVector Loc = GetActorLocation() + FVector(FMath::FRandRange(-200.f, 400.f), Y - GetActorLocation().Y, Z - GetActorLocation().Z);
	const FRotator Rot(0.f, 180.f, 0.f);
	const FTransform SpawnTransform(Rot, Loc);
	ASkyguardDrone* Drone = GetWorld()->SpawnActorDeferred<ASkyguardDrone>(
		ASkyguardDrone::StaticClass(),
		SpawnTransform,
		nullptr,
		nullptr,
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
	if (!Drone)
	{
		return;
	}
	Drone->ConfigureThreat(Kind);
	const float SafeLightSpeedMin = FMath::Min(LightSpeedMin, LightSpeedMax);
	const float SafeLightSpeedMax = FMath::Max(LightSpeedMin, LightSpeedMax);
	float ChosenSpeed = Kind == ESkyguardThreatKind::FastAttacker
		? FMath::FRandRange(
			FMath::Max(0.f, SafeLightSpeedMin),
			FMath::Max(0.f, SafeLightSpeedMax))
		: FMath::Max(0.f, HeavyCruiseSpeed);
	float TargetZ = 350.f;
	switch (Kind)
	{
	case ESkyguardThreatKind::RotorScout:
		ChosenSpeed = 720.f;
		TargetZ = 620.f;
		break;
	case ESkyguardThreatKind::GroundArmor:
		ChosenSpeed = 280.f;
		TargetZ = 70.f;
		break;
	case ESkyguardThreatKind::FastBoat:
		ChosenSpeed = 650.f;
		TargetZ = 40.f;
		break;
	default:
		break;
	}
	Drone->CruiseSpeed = ChosenSpeed;
	Drone->TargetCityLocation = FVector(
		-1800.f,
		FMath::FRandRange(-400.f, 400.f),
		TargetZ);
	Drone->FinishSpawning(SpawnTransform);
}
