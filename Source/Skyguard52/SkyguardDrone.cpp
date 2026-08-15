#include "SkyguardDrone.h"

FSkyguardDroneCityImpactNative ASkyguardDrone::OnAnyCityImpacted;
#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardCombatVFX.h"
#include "SkyguardInputCombatPerformanceCapture.h"
#include "SkyguardRuntimeMeshCatalog.h"
#include "SkyguardApacheAircraft.h"
#include "SkyguardPlayerAircraft.h"
#include "SkyguardYak52Aircraft.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"

ASkyguardDrone::ASkyguardDrone()
{
	PrimaryActorTick.bCanEverTick = true;
	Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
	SetRootComponent(Body);
	Body->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	Body->SetCollisionResponseToAllChannels(ECR_Block);
	Body->SetSimulatePhysics(false);
	Body->SetNotifyRigidBodyCollision(true);

	Wing = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Wing"));
	Wing->SetupAttachment(Body);
	Wing->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Wing->SetRelativeScale3D(FVector(1.f, 1.f, 1.f));

	Exhaust = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Exhaust"));
	Exhaust->SetupAttachment(Body);
	Exhaust->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Exhaust->SetRelativeLocation(FVector(-80.f, 0.f, 0.f));
	Exhaust->SetRelativeScale3D(FVector(0.25f, 0.25f, 0.25f));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cone(TEXT("/Engine/BasicShapes/Cone.Cone"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> WebWing(
		TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-wing.drone-wing"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> WebFins(
		TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-fins.drone-fins"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> WebMotor(
		TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-motor.drone-motor"));

	// Prefer Hero shahed_proxy; WebGame body only if Preferred + ProxyFallback fail.
	if (UStaticMesh* ResolvedBody =
		USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(TEXT("Drone.Body")))
	{
		Body->SetStaticMesh(ResolvedBody);
		const bool bWebGameBody =
			ResolvedBody->GetPathName() ==
			TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-body.drone-body");
		if (bWebGameBody)
		{
			Body->SetRelativeScale3D(FVector(0.9f, 0.9f, 0.9f));
			Body->SetRelativeRotation(FRotator(0.f, 0.f, 0.f));
		}
		else
		{
			Body->SetRelativeScale3D(FVector(18.f, 18.f, 18.f));
		}
	}
	else if (Cone.Succeeded())
	{
		Body->SetStaticMesh(Cone.Object);
		Body->SetRelativeScale3D(FVector(1.2f, 1.2f, 3.2f));
		Body->SetRelativeRotation(FRotator(0.f, -90.f, 0.f));
	}

	if (WebWing.Succeeded())
	{
		Wing->SetStaticMesh(WebWing.Object);
		Wing->SetRelativeScale3D(FVector(0.9f, 0.9f, 0.9f));
	}
	else if (Cube.Succeeded())
	{
		Wing->SetStaticMesh(Cube.Object);
		Wing->SetRelativeScale3D(FVector(2.8f, 0.15f, 0.08f));
	}

	if (WebMotor.Succeeded())
	{
		Exhaust->SetStaticMesh(WebMotor.Object);
		Exhaust->SetRelativeScale3D(FVector(0.9f, 0.9f, 0.9f));
		Exhaust->SetRelativeLocation(FVector(-60.f, 0.f, 0.f));
	}
	else if (WebFins.Succeeded())
	{
		Exhaust->SetStaticMesh(WebFins.Object);
		Exhaust->SetRelativeScale3D(FVector(0.9f, 0.9f, 0.9f));
	}
	else if (Sphere.Succeeded())
	{
		Exhaust->SetStaticMesh(Sphere.Object);
	}
}

void ASkyguardDrone::BeginPlay()
{
	Super::BeginPlay();
	ApplyThreatPresentation();
}

void ASkyguardDrone::ConfigureVariant(const bool bInHeavy)
{
	ConfigureThreat(
		bInHeavy
			? ESkyguardThreatKind::HeavyAttacker
			: ESkyguardThreatKind::FastAttacker);
}

void ASkyguardDrone::ConfigureThreat(const ESkyguardThreatKind Kind)
{
	ThreatKind = Kind;
	bHeavy = Kind != ESkyguardThreatKind::FastAttacker;
	ApplyThreatPresentation();
}

void ASkyguardDrone::ConfigureRoadConvoy(
	const TArray<FVector>& Path,
	const int32 StartWaypointIndex,
	const FName VehicleSlot)
{
	RoadWaypoints = Path;
	bFollowRoad = RoadWaypoints.Num() >= 2;
	bLoopRoad = true;
	RoadWaypointIndex = 0;
	if (bFollowRoad)
	{
		RoadWaypointIndex = FMath::Clamp(
			StartWaypointIndex, 0, RoadWaypoints.Num() - 1);
	}
	if (!VehicleSlot.IsNone())
	{
		GroundVehicleSlot = VehicleSlot;
	}
	// Follow-state first so GroundArmor presentation applies convoy pace,
	// not the 620 cm/s off-road armor default.
	ConfigureThreat(ESkyguardThreatKind::GroundArmor);
	Tags.AddUnique(TEXT("Skyguard.Threat.RoadConvoy"));
	if (bFollowRoad)
	{
		SetActorLocation(RoadWaypoints[RoadWaypointIndex], false);
		const int32 NextIndex =
			(RoadWaypointIndex + 1) % RoadWaypoints.Num();
		const FVector Ahead =
			(RoadWaypoints[NextIndex] - RoadWaypoints[RoadWaypointIndex])
				.GetSafeNormal2D();
		if (!Ahead.IsNearlyZero())
		{
			SetActorRotation(Ahead.Rotation());
		}
	}
}

bool ASkyguardDrone::IsMissileLockEligible() const
{
	return ThreatKind != ESkyguardThreatKind::FastAttacker ||
		bHeavy ||
		MaxHealth >= 80.f;
}

void ASkyguardDrone::ApplyVariantVisualsAndHealth()
{
	Health = MaxHealth = bHeavy ? 100.f : 34.f;
	if (!Body)
	{
		return;
	}
	if (bHeavy)
	{
		if (UStaticMesh* Heavy =
			USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(TEXT("Drone.HeavyBody")))
		{
			Body->SetStaticMesh(Heavy);
			Body->SetRelativeScale3D(FVector(20.f, 20.f, 20.f));
		}
	}
	else if (UStaticMesh* LightBody =
		USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(TEXT("Drone.Body")))
	{
		Body->SetStaticMesh(LightBody);
		const bool bWebGameBody =
			LightBody->GetPathName() ==
			TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-body.drone-body");
		Body->SetRelativeScale3D(
			bWebGameBody ? FVector(0.9f, 0.9f, 0.9f) : FVector(18.f, 18.f, 18.f));
	}
}

void ASkyguardDrone::ApplyThreatPresentation()
{
	ApplyVariantVisualsAndHealth();
	switch (ThreatKind)
	{
	case ESkyguardThreatKind::RotorScout:
		Health = MaxHealth = 140.f;
		if (Body)
		{
			Body->SetRelativeScale3D(FVector(2.4f, 1.1f, 0.7f));
		}
		if (Wing)
		{
			Wing->SetRelativeScale3D(FVector(4.2f, 4.2f, 0.08f));
			Wing->SetRelativeLocation(FVector(0.f, 0.f, 40.f));
		}
		CruiseSpeed = CruiseSpeed > 0.f ? CruiseSpeed : 720.f;
		break;
	case ESkyguardThreatKind::GroundArmor:
		Health = MaxHealth = 220.f;
		CruiseSpeed = CruiseSpeed > 0.f ? FMath::Min(CruiseSpeed, 720.f) : 620.f;
		TargetCityLocation.Z = FMath::Min(TargetCityLocation.Z, 92.f);
		if (bFollowRoad || !GroundVehicleSlot.IsNone())
		{
			ApplyGroundVehiclePresentation();
			ApplyRoadConvoyPace();
		}
		else
		{
			if (Body)
			{
				Body->SetRelativeScale3D(FVector(2.8f, 1.6f, 0.7f));
				Body->SetRelativeRotation(FRotator::ZeroRotator);
			}
			if (Wing)
			{
				Wing->SetVisibility(false);
			}
			if (Exhaust)
			{
				Exhaust->SetRelativeLocation(FVector(40.f, 0.f, 18.f));
				Exhaust->SetRelativeScale3D(FVector(0.35f, 0.35f, 0.55f));
			}
		}
		break;
	case ESkyguardThreatKind::FastBoat:
		Health = MaxHealth = 90.f;
		if (Body)
		{
			Body->SetRelativeScale3D(FVector(3.6f, 0.9f, 0.35f));
			Body->SetRelativeRotation(FRotator::ZeroRotator);
		}
		if (Wing)
		{
			Wing->SetVisibility(false);
		}
		CruiseSpeed = CruiseSpeed > 0.f ? FMath::Min(CruiseSpeed, 780.f) : 650.f;
		TargetCityLocation.Z = FMath::Min(TargetCityLocation.Z, 50.f);
		break;
	case ESkyguardThreatKind::HeavyAttacker:
		Health = MaxHealth = 100.f;
		break;
	case ESkyguardThreatKind::FastAttacker:
	default:
		Health = MaxHealth = 34.f;
		break;
	}
}

void ASkyguardDrone::LifeSpanExpired()
{
	if (bDead && !bReachedCity)
	{
		USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
			this, TEXT("drone_breakup_cleanup"));
	}
	Super::LifeSpanExpired();
}

void ASkyguardDrone::ApplyGroundVehiclePresentation()
{
	if (Wing)
	{
		Wing->SetVisibility(false);
	}
	if (Exhaust)
	{
		Exhaust->SetVisibility(false);
	}
	if (!Body)
	{
		return;
	}

	FName Slot = GroundVehicleSlot;
	if (Slot.IsNone())
	{
		Slot = TEXT("Vehicle.Truck");
	}
	UStaticMesh* VehicleMesh =
		USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(Slot);
	float TargetLengthCm = 520.f;
	if (Slot == TEXT("Vehicle.Car"))
	{
		TargetLengthCm = 400.f;
	}
	else if (Slot == TEXT("Vehicle.Bus"))
	{
		TargetLengthCm = 680.f;
	}

	if (VehicleMesh)
	{
		Body->SetStaticMesh(VehicleMesh);
		const FBoxSphereBounds Bounds = VehicleMesh->GetBounds();
		const float Longest =
			FMath::Max3(Bounds.BoxExtent.X, Bounds.BoxExtent.Y, Bounds.BoxExtent.Z) *
			2.f;
		const float Scale = Longest > 1.f ? (TargetLengthCm / Longest) : 1.f;
		Body->SetRelativeScale3D(FVector(Scale));
		const bool bLongerOnY = Bounds.BoxExtent.Y > Bounds.BoxExtent.X + 1.f;
		Body->SetRelativeRotation(
			bLongerOnY ? FRotator(0.f, -90.f, 0.f) : FRotator::ZeroRotator);
		Body->SetRelativeLocation(FVector::ZeroVector);
	}
	else
	{
		Body->SetRelativeScale3D(FVector(2.8f, 1.6f, 0.7f));
		Body->SetRelativeRotation(FRotator::ZeroRotator);
	}
}

void ASkyguardDrone::ApplyRoadConvoyPace()
{
	// Named ground-column pace. Do not reuse the 620 GroundArmor default —
	// that reads as a sprint from the CPG seat.
	CruiseSpeed = RoadConvoyCruiseSpeed;
	if (GroundVehicleSlot == TEXT("Vehicle.Car"))
	{
		Health = MaxHealth = RoadConvoyCarHealth;
	}
	else
	{
		Health = MaxHealth = RoadConvoyTruckHealth;
	}
}

void ASkyguardDrone::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (bDead)
	{
		return;
	}
	if (IsFollowingRoad())
	{
		TickRoadFollow(DeltaSeconds);
		return;
	}
	TickCruiseToCity(DeltaSeconds);
}

void ASkyguardDrone::TickCruiseToCity(const float DeltaSeconds)
{
	const FVector Loc = GetActorLocation();
	const FVector ToTarget = (TargetCityLocation - Loc).GetSafeNormal();
	const FVector NewLoc = Loc + ToTarget * CruiseSpeed * DeltaSeconds;
	FHitResult Hit;
	SetActorLocation(NewLoc, true, &Hit);
	if (Hit.bBlockingHit)
	{
		if (FSkyguardPlayerAircraft::IsPlayerPlatform(Hit.GetActor()))
		{
			ImpactPlatform(Hit.GetActor());
			return;
		}
	}
	const FRotator Face = ToTarget.Rotation();
	SetActorRotation(FMath::RInterpTo(GetActorRotation(), Face, DeltaSeconds, 2.5f));
	Spin += DeltaSeconds * 40.f;
	if (Wing)
	{
		Wing->SetRelativeRotation(FRotator(0.f, Spin, 0.f));
	}
	if (FVector::DistSquared(GetActorLocation(), TargetCityLocation) < FMath::Square(180.f))
	{
		ImpactCity(ToTarget);
	}
}

void ASkyguardDrone::TickRoadFollow(const float DeltaSeconds)
{
	if (RoadWaypoints.Num() < 2)
	{
		return;
	}

	FVector Loc = GetActorLocation();
	int32 Safety = 0;
	while (Safety++ < RoadWaypoints.Num())
	{
		const FVector Goal = RoadWaypoints[RoadWaypointIndex];
		const FVector ToGoal = Goal - Loc;
		if (ToGoal.Size2D() > 140.f)
		{
			const FVector Dir = ToGoal.GetSafeNormal();
			const FVector Step = Dir * CruiseSpeed * DeltaSeconds;
			if (Step.SizeSquared() >= ToGoal.SizeSquared())
			{
				Loc = Goal;
			}
			else
			{
				Loc = Loc + Step;
			}
			SetActorLocation(Loc, false);
			const FRotator Face = FVector(Dir.X, Dir.Y, 0.f).Rotation();
			SetActorRotation(
				FMath::RInterpTo(GetActorRotation(), Face, DeltaSeconds, 4.5f));
			return;
		}

		if (bLoopRoad)
		{
			RoadWaypointIndex = (RoadWaypointIndex + 1) % RoadWaypoints.Num();
		}
		else if (RoadWaypointIndex + 1 < RoadWaypoints.Num())
		{
			++RoadWaypointIndex;
		}
		else
		{
			return;
		}
	}
}

void ASkyguardDrone::ApplyBallisticHit(float Damage, FVector HitLocation, FVector HitDirection)
{
	if (bDead) return;
	Health -= Damage;
	AddActorWorldOffset(HitDirection * 30.f + FVector(0,0,10.f), true);
	USkyguardCombatVFX::SpawnHitSparks(GetWorld(), HitLocation, HitDirection);
	if (Health <= 0.f)
	{
		Die(HitDirection);
	}
}

void ASkyguardDrone::SpawnDebris(const FVector& HitDir)
{
	// Lightweight debris only — avoid expensive runtime mesh generation freezes.
	if (Wing)
	{
		Wing->DetachFromComponent(FDetachmentTransformRules::KeepWorldTransform);
		Wing->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
		Wing->SetSimulatePhysics(true);
		Wing->SetPhysicsLinearVelocity(HitDir * 800.f + FVector(FMath::FRandRange(-200.f, 200.f), FMath::FRandRange(-200.f, 200.f), 300.f));
		Wing->SetPhysicsAngularVelocityInDegrees(FVector(400.f, -300.f, 250.f));
	}
	if (Exhaust)
	{
		Exhaust->DetachFromComponent(FDetachmentTransformRules::KeepWorldTransform);
		Exhaust->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
		Exhaust->SetSimulatePhysics(true);
		Exhaust->SetPhysicsLinearVelocity(HitDir * -400.f + FVector(0,0,200.f));
	}
}


void ASkyguardDrone::ImpactCity(const FVector& ImpactDirection)
{
	if (bDead)
	{
		return;
	}
	bDead = true;
	bReachedCity = true;

	// City strike is a protect failure, not a player kill — no breakup debris/telemetry.
	if (Body)
	{
		Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Body->SetVisibility(false, true);
	}
	if (Wing)
	{
		Wing->SetVisibility(false, true);
	}
	if (Exhaust)
	{
		Exhaust->SetVisibility(false, true);
	}

	USkyguardCombatVFX::SpawnExplosion(
		GetWorld(),
		TargetCityLocation,
		bHeavy ? 2.0f : 1.35f);
	USkyguardAudioDirectorComponent::TriggerWorldEvent(
		this,
		bHeavy
			? ESkyguardAudioEvent::ExplosionHeavy
			: ESkyguardAudioEvent::ExplosionSmall,
		TargetCityLocation);
	USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
		this, TEXT("drone_city_impact"));

	OnCityImpacted.Broadcast(this);
	OnAnyCityImpacted.Broadcast(this);
	SetLifeSpan(0.35f);
}

void ASkyguardDrone::ImpactAircraft(ASkyguardYak52Aircraft* Aircraft)
{
	ImpactPlatform(Aircraft);
}

void ASkyguardDrone::ImpactPlatform(AActor* Platform)
{
	if (bDead || !IsValid(Platform))
	{
		return;
	}
	const float Damage = bHeavy ? HeavyAircraftCollisionDamage : AircraftCollisionDamage;
	FSkyguardPlayerAircraft::ApplyHullDamage(Platform, Damage);
	const FVector Away =
		(GetActorLocation() - Platform->GetActorLocation()).GetSafeNormal();
	Die(Away.IsNearlyZero() ? GetActorForwardVector() : Away, Platform);
}

void ASkyguardDrone::DamageNearbyAircraft(
	const float Amount,
	const float RadiusCm,
	const AActor* ExcludeAircraft)
{
	if (Amount <= 0.f || RadiusCm <= 0.f)
	{
		return;
	}
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	const float RadiusSq = FMath::Square(RadiusCm);
	const FVector Origin = GetActorLocation();

	auto DamageIfNear = [&](AActor* Platform)
	{
		if (!IsValid(Platform) || Platform == ExcludeAircraft)
		{
			return;
		}
		if (FVector::DistSquared(Origin, Platform->GetActorLocation()) <= RadiusSq)
		{
			FSkyguardPlayerAircraft::ApplyHullDamage(Platform, Amount);
		}
	};

	for (TActorIterator<ASkyguardApacheAircraft> It(World); It; ++It)
	{
		DamageIfNear(*It);
	}
	for (TActorIterator<ASkyguardYak52Aircraft> It(World); It; ++It)
	{
		DamageIfNear(*It);
	}
}

void ASkyguardDrone::Die(
	const FVector& HitDir,
	AActor* AlreadyDamagedAircraft)
{
	if (bDead) return;
	bDead = true;
	SpawnDebris(HitDir);
	Body->SetSimulatePhysics(true);
	Body->SetPhysicsLinearVelocity(HitDir * 1200.f + FVector(0,0,400.f));
	Body->SetPhysicsAngularVelocityInDegrees(FVector(300.f, 500.f, 200.f));
	SetLifeSpan(3.5f);
	USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
		this, TEXT("drone_breakup"));

	USkyguardCombatVFX::SpawnExplosion(GetWorld(), GetActorLocation(), bHeavy ? 1.6f : 1.0f);
	USkyguardAudioDirectorComponent::TriggerWorldEvent(
		this,
		bHeavy
			? ESkyguardAudioEvent::ExplosionHeavy
			: ESkyguardAudioEvent::ExplosionSmall,
		GetActorLocation());

	// Shoot-down / breakup near the Yak can nick the airframe.
	const float Splash = bHeavy ? HeavyAircraftExplosionDamage : AircraftExplosionDamage;
	DamageNearbyAircraft(Splash, AircraftExplosionRadiusCm, AlreadyDamagedAircraft);
}

