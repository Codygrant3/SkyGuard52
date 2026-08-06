#include "SkyguardDrone.h"
#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardCombatVFX.h"
#include "SkyguardInputCombatPerformanceCapture.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"

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
	static ConstructorHelpers::FObjectFinder<UStaticMesh> WebBody(TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-body.drone-body"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> WebWing(TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-wing.drone-wing"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> WebFins(TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-fins.drone-fins"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> WebMotor(TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-drone/StaticMeshes/drone-motor.drone-motor"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> HeroShahed(TEXT("/Game/Skyguard/Meshes/Hero/shahed_proxy.shahed_proxy"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> HeroHeavy(TEXT("/Game/Skyguard/Meshes/Hero/shahed_heavy_proxy.shahed_heavy_proxy"));

	if (WebBody.Succeeded())
	{
		Body->SetStaticMesh(WebBody.Object);
		Body->SetRelativeScale3D(FVector(0.9f, 0.9f, 0.9f));
		Body->SetRelativeRotation(FRotator(0.f, 0.f, 0.f));
	}
	else if (HeroShahed.Succeeded())
	{
		Body->SetStaticMesh(HeroShahed.Object);
		Body->SetRelativeScale3D(FVector(18.f, 18.f, 18.f));
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

	// Heavy variant visual swap is applied in BeginPlay based on bHeavy
	if (HeroHeavy.Succeeded())
	{
		// cache via transient load path in BeginPlay instead
	}
}

void ASkyguardDrone::BeginPlay()
{
	Super::BeginPlay();
	Health = MaxHealth = bHeavy ? 100.f : 34.f;
	if (bHeavy)
	{
		if (UStaticMesh* Heavy = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Skyguard/Meshes/Hero/shahed_heavy_proxy.shahed_heavy_proxy")))
		{
			Body->SetStaticMesh(Heavy);
			Body->SetRelativeScale3D(FVector(20.f, 20.f, 20.f));
		}
	}
}

void ASkyguardDrone::LifeSpanExpired()
{
	if (bDead)
	{
		USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
			this, TEXT("drone_breakup_cleanup"));
	}
	Super::LifeSpanExpired();
}

void ASkyguardDrone::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (bDead) return;
	const FVector Loc = GetActorLocation();
	const FVector ToTarget = (TargetCityLocation - Loc).GetSafeNormal();
	const FVector NewLoc = Loc + ToTarget * CruiseSpeed * DeltaSeconds;
	SetActorLocation(NewLoc, true);
	const FRotator Face = ToTarget.Rotation();
	SetActorRotation(FMath::RInterpTo(GetActorRotation(), Face, DeltaSeconds, 2.5f));
	Spin += DeltaSeconds * 40.f;
	if (Wing) Wing->SetRelativeRotation(FRotator(0.f, Spin, 0.f));
	if (FVector::DistSquared(NewLoc, TargetCityLocation) < FMath::Square(180.f))
	{
		Die(ToTarget);
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

void ASkyguardDrone::Die(const FVector& HitDir)
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
}

