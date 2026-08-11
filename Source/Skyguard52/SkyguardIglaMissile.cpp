#include "SkyguardIglaMissile.h"

#include "SkyguardAudioDirectorComponent.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardCombatVFX.h"
#include "SkyguardDrone.h"
#include "SkyguardGunner.h"
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

bool ASkyguardIglaMissile::ShouldDamageLockedTargetOnImpact(
	const FVector& ImpactPoint,
	const AActor* HitActor) const
{
	AActor* LockedTarget = TargetActor.Get();
	if (!LockedTarget)
	{
		return false;
	}
	if (HitActor && HitActor == LockedTarget)
	{
		return true;
	}
	return FVector::DistSquared(ImpactPoint, LockedTarget->GetActorLocation()) <=
		FMath::Square(ProximityFuseCentimeters);
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
			Detonate(Target->GetActorLocation(), Target);
			return;
		}
	}

	FHitResult Hit;
	const FVector NextLocation = GetActorLocation() + Velocity * DeltaSeconds;
	SetActorLocation(NextLocation, true, &Hit, ETeleportType::None);
	SetActorRotation(Velocity.Rotation());
	if (bArmed && Hit.bBlockingHit && Hit.GetActor() != GetOwner())
	{
		AActor* HitActor = Hit.GetActor();
		AActor* LockedTarget = TargetActor.Get();
		const bool bHitIsCombatant =
			HitActor &&
			(HitActor->IsA(ASkyguardBossDroneBase::StaticClass()) ||
				HitActor->IsA(ASkyguardDrone::StaticClass()));
		const bool bShouldDamageLock =
			ShouldDamageLockedTargetOnImpact(Hit.ImpactPoint, HitActor);

		// Terrain/world clips only damage the lock if the impact is within
		// proximity of that target. Direct combatant hits always apply.
		Detonate(
			Hit.ImpactPoint,
			bHitIsCombatant ? HitActor : (bShouldDamageLock ? LockedTarget : nullptr));
	}
}

void ASkyguardIglaMissile::Detonate(
	const FVector& ImpactPoint,
	AActor* DamageTarget)
{
	if (bDetonated)
	{
		return;
	}
	bDetonated = true;

	AActor* Target = DamageTarget ? DamageTarget : nullptr;
	const FVector Direction =
		Velocity.GetSafeNormal(SMALL_NUMBER, FVector::ForwardVector);
	bool bAppliedDamage = false;
	if (ASkyguardBossDroneBase* Boss = Cast<ASkyguardBossDroneBase>(Target))
	{
		bAppliedDamage = Boss->ApplyIglaStrike(Damage, ImpactPoint, Direction);
	}
	else if (ASkyguardDrone* Drone = Cast<ASkyguardDrone>(Target))
	{
		Drone->ApplyBallisticHit(Damage, ImpactPoint, Direction);
		bAppliedDamage = true;
	}
	if (bAppliedDamage)
	{
		if (ASkyguardGunner* Gunner = Cast<ASkyguardGunner>(GetOwner()))
		{
			Gunner->RecordIglaHit();
		}
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
