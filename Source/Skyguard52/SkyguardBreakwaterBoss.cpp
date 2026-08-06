#include "SkyguardBreakwaterBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	void ConfigureBreakwaterWeakPoint(
		USkyguardBossWeakPointComponent* Component,
		const FName Id,
		const FVector& Location,
		const FVector& Scale,
		const float Integrity,
		const bool bAcceptsRifle,
		const bool bAcceptsIgla,
		const bool bExposed)
	{
		Component->WeakPointId = Id;
		Component->SetRelativeLocation(Location);
		Component->SetRelativeScale3D(Scale);
		Component->MaxIntegrity = Integrity;
		Component->Integrity = Integrity;
		Component->bAcceptsRifle = bAcceptsRifle;
		Component->bAcceptsIgla = bAcceptsIgla;
		Component->SetExposed(bExposed);
	}
}

ASkyguardBreakwaterBoss::ASkyguardBreakwaterBoss()
{
	PrimaryActorTick.bCanEverTick = false;
	MaxDefeatDebrisPieces = 3;

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderAsset(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));

	if (CubeAsset.Succeeded())
	{
		BodyMesh->SetStaticMesh(CubeAsset.Object);
		BodyMesh->SetRelativeScale3D(FVector(3.8f, 2.6f, 0.45f));
	}

	PortLatch = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("PortLatch"));
	PortLatch->SetupAttachment(BodyMesh);
	ConfigureBreakwaterWeakPoint(
		PortLatch, TEXT("PortLatch"), FVector(0.f, -78.f, 18.f),
		FVector(0.18f), 100.f, true, false, true);

	StarboardLatch = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("StarboardLatch"));
	StarboardLatch->SetupAttachment(BodyMesh);
	ConfigureBreakwaterWeakPoint(
		StarboardLatch, TEXT("StarboardLatch"), FVector(0.f, 78.f, 18.f),
		FVector(0.18f), 100.f, true, false, false);

	DecoyPods = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("DecoyPods"));
	DecoyPods->SetupAttachment(BodyMesh);
	ConfigureBreakwaterWeakPoint(
		DecoyPods, TEXT("DecoyPods"), FVector(-45.f, 0.f, -25.f),
		FVector(0.3f, 0.55f, 0.2f), 100.f, true, false, false);

	Engine = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("Engine"));
	Engine->SetupAttachment(BodyMesh);
	ConfigureBreakwaterWeakPoint(
		Engine, TEXT("Engine"), FVector(-155.f, 0.f, 5.f),
		FVector(0.42f, 0.42f, 0.65f), 250.f, false, true, false);

	ElevatorLinkage = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("ElevatorLinkage"));
	ElevatorLinkage->SetupAttachment(BodyMesh);
	ConfigureBreakwaterWeakPoint(
		ElevatorLinkage, TEXT("ElevatorLinkage"), FVector(-205.f, 0.f, 24.f),
		FVector(0.25f, 0.8f, 0.18f), 160.f, true, false, false);

	if (CylinderAsset.Succeeded())
	{
		PortLatch->SetStaticMesh(CylinderAsset.Object);
		StarboardLatch->SetStaticMesh(CylinderAsset.Object);
		Engine->SetStaticMesh(CylinderAsset.Object);
	}
	if (CubeAsset.Succeeded())
	{
		DecoyPods->SetStaticMesh(CubeAsset.Object);
		ElevatorLinkage->SetStaticMesh(CubeAsset.Object);
	}

	DebrisPortPanel = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisPortPanel"));
	DebrisPortPanel->SetupAttachment(BodyMesh);
	DebrisPortPanel->SetRelativeLocation(FVector(0.f, -95.f, 0.f));
	if (CubeAsset.Succeeded())
	{
		DebrisPortPanel->SetStaticMesh(CubeAsset.Object);
		DebrisPortPanel->SetRelativeScale3D(FVector(1.5f, 0.15f, 0.25f));
	}
	RegisterDefeatDebris(DebrisPortPanel);

	DebrisEngine = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisEngine"));
	DebrisEngine->SetupAttachment(BodyMesh);
	DebrisEngine->SetRelativeLocation(FVector(-150.f, 0.f, 0.f));
	if (CylinderAsset.Succeeded())
	{
		DebrisEngine->SetStaticMesh(CylinderAsset.Object);
		DebrisEngine->SetRelativeScale3D(FVector(0.4f, 0.4f, 0.65f));
	}
	RegisterDefeatDebris(DebrisEngine);

	DebrisStarboardPanel = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisStarboardPanel"));
	DebrisStarboardPanel->SetupAttachment(BodyMesh);
	DebrisStarboardPanel->SetRelativeLocation(FVector(0.f, 95.f, 0.f));
	if (CubeAsset.Succeeded())
	{
		DebrisStarboardPanel->SetStaticMesh(CubeAsset.Object);
		DebrisStarboardPanel->SetRelativeScale3D(FVector(1.5f, 0.15f, 0.25f));
	}
	RegisterDefeatDebris(DebrisStarboardPanel);

	Tags.AddUnique(TEXT("Skyguard.Mission02.Breakwater"));
	Tags.AddUnique(TEXT("Skyguard.ProxyArt.Runtime"));
}

bool ASkyguardBreakwaterBoss::ArmEmergencyRifleFinish()
{
	const bool bOrbitCommand =
		CurrentPilotCommand == ESkyguardPilotCommand::OrbitLeft ||
		CurrentPilotCommand == ESkyguardPilotCommand::OrbitRight;
	if (Phase != ESkyguardBossPhase::LockWindow ||
		!DecoyPods->bDestroyed ||
		Engine->bDestroyed ||
		!bOrbitCommand)
	{
		return false;
	}

	bEmergencyRifleFinishArmed = true;
	bIglaLockEnabled = false;
	ElevatorLinkage->SetExposed(true);
	SetBossPhase(ESkyguardBossPhase::Critical);
	return true;
}

void ASkyguardBreakwaterBoss::HandleWeakPointDestroyed(
	USkyguardBossWeakPointComponent* WeakPoint,
	ESkyguardBossWeapon Weapon)
{
	if (WeakPoint == PortLatch)
	{
		StarboardLatch->SetExposed(true);
		SetBossPhase(ESkyguardBossPhase::Disarm);
		return;
	}

	if (WeakPoint == StarboardLatch && PortLatch->bDestroyed)
	{
		DecoyPods->SetExposed(true);
		return;
	}

	if (WeakPoint == DecoyPods &&
		PortLatch->bDestroyed &&
		StarboardLatch->bDestroyed)
	{
		Engine->SetExposed(true);
		bIglaLockEnabled = true;
		SetBossPhase(ESkyguardBossPhase::LockWindow);
		return;
	}

	if (WeakPoint == Engine && Weapon == ESkyguardBossWeapon::Igla)
	{
		bIglaLockEnabled = false;
		ElevatorLinkage->SetExposed(true);
		SetBossPhase(ESkyguardBossPhase::Critical);
		return;
	}

	if (WeakPoint == ElevatorLinkage &&
		(Engine->bDestroyed || bEmergencyRifleFinishArmed))
	{
		SetBossPhase(ESkyguardBossPhase::Defeated);
	}
}
