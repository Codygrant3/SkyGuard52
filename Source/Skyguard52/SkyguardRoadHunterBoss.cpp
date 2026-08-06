#include "SkyguardRoadHunterBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	void ConfigureRoadHunterWeakPoint(
		USkyguardBossWeakPointComponent* Component,
		const FName Id,
		const FVector& Location,
		const FVector& Scale,
		const float Integrity,
		const bool bRifle,
		const bool bIgla,
		const bool bExposed)
	{
		Component->WeakPointId = Id;
		Component->SetRelativeLocation(Location);
		Component->SetRelativeScale3D(Scale);
		Component->MaxIntegrity = Integrity;
		Component->Integrity = Integrity;
		Component->bAcceptsRifle = bRifle;
		Component->bAcceptsIgla = bIgla;
		Component->SetExposed(bExposed);
	}
}

ASkyguardRoadHunterBoss::ASkyguardRoadHunterBoss()
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
		BodyMesh->SetRelativeScale3D(FVector(3.2f, 2.8f, 0.32f));
	}

	TargetingCamera =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("TargetingCamera"));
	TargetingCamera->SetupAttachment(BodyMesh);
	ConfigureRoadHunterWeakPoint(
		TargetingCamera, TEXT("TargetingCamera"),
		FVector(145.f, 0.f, -18.f), FVector(0.22f),
		100.f, true, false, true);

	LeftActuator =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("LeftActuator"));
	LeftActuator->SetupAttachment(BodyMesh);
	ConfigureRoadHunterWeakPoint(
		LeftActuator, TEXT("LeftActuator"),
		FVector(-20.f, -112.f, 8.f), FVector(0.18f, 0.4f, 0.18f),
		100.f, true, false, false);

	RightActuator =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("RightActuator"));
	RightActuator->SetupAttachment(BodyMesh);
	ConfigureRoadHunterWeakPoint(
		RightActuator, TEXT("RightActuator"),
		FVector(-20.f, 112.f, 8.f), FVector(0.18f, 0.4f, 0.18f),
		100.f, true, false, false);

	Engine = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("Engine"));
	Engine->SetupAttachment(BodyMesh);
	ConfigureRoadHunterWeakPoint(
		Engine, TEXT("Engine"),
		FVector(-145.f, 0.f, 5.f), FVector(0.42f, 0.42f, 0.65f),
		250.f, false, true, false);

	if (CylinderAsset.Succeeded())
	{
		TargetingCamera->SetStaticMesh(CylinderAsset.Object);
		Engine->SetStaticMesh(CylinderAsset.Object);
	}
	if (CubeAsset.Succeeded())
	{
		LeftActuator->SetStaticMesh(CubeAsset.Object);
		RightActuator->SetStaticMesh(CubeAsset.Object);
	}

	DebrisLeftWing = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisLeftWing"));
	DebrisLeftWing->SetupAttachment(BodyMesh);
	DebrisLeftWing->SetRelativeLocation(FVector(0.f, -105.f, 0.f));
	if (CubeAsset.Succeeded())
	{
		DebrisLeftWing->SetStaticMesh(CubeAsset.Object);
		DebrisLeftWing->SetRelativeScale3D(FVector(1.35f, 0.65f, 0.12f));
	}
	RegisterDefeatDebris(DebrisLeftWing);

	DebrisEngine = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisEngine"));
	DebrisEngine->SetupAttachment(BodyMesh);
	DebrisEngine->SetRelativeLocation(FVector(-145.f, 0.f, 0.f));
	if (CylinderAsset.Succeeded())
	{
		DebrisEngine->SetStaticMesh(CylinderAsset.Object);
		DebrisEngine->SetRelativeScale3D(FVector(0.4f, 0.4f, 0.6f));
	}
	RegisterDefeatDebris(DebrisEngine);

	DebrisRightWing = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisRightWing"));
	DebrisRightWing->SetupAttachment(BodyMesh);
	DebrisRightWing->SetRelativeLocation(FVector(0.f, 105.f, 0.f));
	if (CubeAsset.Succeeded())
	{
		DebrisRightWing->SetStaticMesh(CubeAsset.Object);
		DebrisRightWing->SetRelativeScale3D(FVector(1.35f, 0.65f, 0.12f));
	}
	RegisterDefeatDebris(DebrisRightWing);

	Tags.AddUnique(TEXT("Skyguard.Mission03.RoadHunter"));
	Tags.AddUnique(TEXT("Skyguard.ProxyArt.Runtime"));
}

bool ASkyguardRoadHunterBoss::ArmEmergencyRifleFinish()
{
	const bool bOrbitCommand =
		CurrentPilotCommand == ESkyguardPilotCommand::OrbitLeft ||
		CurrentPilotCommand == ESkyguardPilotCommand::OrbitRight;
	if (Phase != ESkyguardBossPhase::LockWindow ||
		!LeftActuator->bDestroyed ||
		!RightActuator->bDestroyed ||
		Engine->bDestroyed ||
		!bOrbitCommand)
	{
		return false;
	}

	bEmergencyRifleFinishArmed = true;
	bIglaLockEnabled = false;
	Engine->bAcceptsRifle = true;
	SetBossPhase(ESkyguardBossPhase::Critical);
	return true;
}

void ASkyguardRoadHunterBoss::HandleWeakPointDestroyed(
	USkyguardBossWeakPointComponent* WeakPoint,
	ESkyguardBossWeapon Weapon)
{
	if (WeakPoint == TargetingCamera)
	{
		LeftActuator->SetExposed(true);
		RightActuator->SetExposed(true);
		SetBossPhase(ESkyguardBossPhase::Disarm);
		return;
	}

	if ((WeakPoint == LeftActuator || WeakPoint == RightActuator) &&
		LeftActuator->bDestroyed &&
		RightActuator->bDestroyed)
	{
		Engine->SetExposed(true);
		bIglaLockEnabled = true;
		SetBossPhase(ESkyguardBossPhase::LockWindow);
		return;
	}

	if (WeakPoint == Engine &&
		(Weapon == ESkyguardBossWeapon::Igla ||
			bEmergencyRifleFinishArmed))
	{
		SetBossPhase(ESkyguardBossPhase::Defeated);
	}
}
