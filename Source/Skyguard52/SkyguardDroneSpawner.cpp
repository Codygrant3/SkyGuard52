#include "SkyguardDroneSpawner.h"
#include "SkyguardDrone.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

ASkyguardDroneSpawner::ASkyguardDroneSpawner()
{
	PrimaryActorTick.bCanEverTick = true;
}

void ASkyguardDroneSpawner::BeginPlay()
{
	Super::BeginPlay();
	SpawnTimer = 0.5f;
}

void ASkyguardDroneSpawner::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	SpawnTimer -= DeltaSeconds;
	if (SpawnTimer > 0.f) return;
	SpawnTimer = SpawnInterval;

	if (!GetWorld()) return;
	const int32 Lane = FMath::RandRange(0, 5);
	const float Y = -1800.f + Lane * 700.f + FMath::FRandRange(-80.f, 80.f);
	const float Z = 360.f + FMath::FRandRange(0.f, 160.f);
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
	const bool bHeavy = (Lane % 3 == 0);
	Drone->bHeavy = bHeavy;
	Drone->CruiseSpeed = bHeavy ? 1200.f : FMath::FRandRange(1400.f, 1900.f);
	Drone->TargetCityLocation = FVector(-1800.f, FMath::FRandRange(-400.f, 400.f), 350.f);
	if (bHeavy)
	{
		Drone->SetActorScale3D(FVector(1.35f, 1.35f, 1.35f));
	}
	Drone->FinishSpawning(SpawnTransform);
}
