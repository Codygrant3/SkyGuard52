#include "SkyguardIglaMissile.h"

#include "SkyguardAudioDirectorComponent.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardCombatVFX.h"
#include "SkyguardDrone.h"
#include "SkyguardInputCombatPerformanceCapture.h"

ASkyguardIglaMissile::ASkyguardIglaMissile()
{
	PrimaryActorTick.bCanEverTick = true;

	Collision = CreateDefaultSubobject<USphereComponent>(TEXT("Collision"));
	SetRootComponent(Collision);
	Collision->InitSphereRadius(16.f);
	Collision->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Collision->SetCollisionResponseToAllChannels(ECR_Ignore);
	Collision->SetCollisionResponseToChannel(ECC_WorldStatic, ECR_Block);
	Collision->SetCollisionResponseToChannel(ECC_WorldDynamic, ECR_Block);

	MissileMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MissileMesh"));
	MissileMesh->SetupAttachment(Collision);
	MissileMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	// The former igla_projectile_proxy path never existed as a cooked asset.
	// Keep a deterministic engine-mesh fallback until the governed Blender
	// missile is imported; do not issue a missing-package load every launch.
	if (UStaticMesh* Cylinder = LoadObject<UStaticMesh>(
		nullptr,
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder")))
	{
		MissileMesh->SetStaticMesh(Cylinder);
		MissileMesh->SetRelativeScale3D(FVector(0.04f, 0.04f, 0.7f));
		MissileMesh->SetRelativeRotation(FRotator(0.f, 90.f, 0.f));
	}

	SetLifeSpan(MaximumFlightSeconds + 0.5f);
}

void ASkyguardIglaMissile::InitializeMissile(
	AActor* InTarget,
	const float InDamage,
	const FVector& InitialDirection)
{
	TargetActor = InTarget;
	Damage = FMath::Max(0.f, InDamage);
	Velocity = InitialDirection.GetSafeNormal(SMALL_NUMBER, FVector::ForwardVector) * Speed;
	SetActorRotation(Velocity.Rotation());
}

void ASkyguardIglaMissile::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (bDetonated)
	{
		return;
	}

	FlightSeconds += DeltaSeconds;
	bArmed = FlightSeconds >= ArmDelaySeconds;
	if (FlightSeconds >= MaximumFlightSeconds)
	{
		Destroy();
		return;
	}

	AActor* Target = TargetActor.Get();
	if (Target)
	{
		const FVector DesiredDirection =
			(Target->GetActorLocation() - GetActorLocation()).GetSafeNormal();
		const FVector CurrentDirection =
			Velocity.GetSafeNormal(SMALL_NUMBER, FVector::ForwardVector);
		const FVector NewDirection =
			FMath::VInterpNormalRotationTo(
				CurrentDirection,
				DesiredDirection,
				DeltaSeconds,
				TurnRateDegreesPerSecond);
		Velocity = NewDirection.GetSafeNormal(SMALL_NUMBER, CurrentDirection) * Speed;

		if (bArmed && FVector::DistSquared(GetActorLocation(), Target->GetActorLocation()) <=
			FMath::Square(ProximityFuseCentimeters))
		{
			Detonate(Target->GetActorLocation());
			return;
		}
	}

	FHitResult Hit;
	const FVector NextLocation = GetActorLocation() + Velocity * DeltaSeconds;
	SetActorLocation(NextLocation, true, &Hit, ETeleportType::None);
	SetActorRotation(Velocity.Rotation());
	if (bArmed && Hit.bBlockingHit && Hit.GetActor() != GetOwner())
	{
		Detonate(Hit.ImpactPoint);
	}
}

void ASkyguardIglaMissile::Detonate(const FVector& ImpactPoint)
{
	if (bDetonated)
	{
		return;
	}
	bDetonated = true;

	AActor* Target = TargetActor.Get();
	const FVector Direction =
		Velocity.GetSafeNormal(SMALL_NUMBER, FVector::ForwardVector);
	if (ASkyguardBossDroneBase* Boss = Cast<ASkyguardBossDroneBase>(Target))
	{
		Boss->ApplyIglaStrike(Damage, ImpactPoint, Direction);
	}
	else if (ASkyguardDrone* Drone = Cast<ASkyguardDrone>(Target))
	{
		Drone->ApplyBallisticHit(Damage, ImpactPoint, Direction);
	}

	USkyguardCombatVFX::SpawnExplosion(GetWorld(), ImpactPoint, 1.35f);
	USkyguardAudioDirectorComponent::TriggerWorldEvent(
		this,
		ESkyguardAudioEvent::IglaImpact,
		ImpactPoint);
	USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
		this, TEXT("igla_impact"));
	Destroy();
}
