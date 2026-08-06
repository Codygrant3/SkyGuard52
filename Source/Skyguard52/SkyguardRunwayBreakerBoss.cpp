#include "SkyguardRunwayBreakerBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	void ConfigureRunwayBreakerPoint(
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

ASkyguardRunwayBreakerBoss::ASkyguardRunwayBreakerBoss()
{
	MaxDefeatDebrisPieces = 3;
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderAsset(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (CubeAsset.Succeeded())
	{
		BodyMesh->SetStaticMesh(CubeAsset.Object);
		BodyMesh->SetRelativeScale3D(FVector(4.2f, 3.2f, 0.55f));
	}

	RunwayRack = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("RunwayRack"));
	RunwayRack->SetupAttachment(BodyMesh);
	ConfigureRunwayBreakerPoint(
		RunwayRack, TEXT("RunwayRack"), FVector(35.f, -95.f, -32.f),
		FVector(0.55f, 0.32f, 0.25f), 100.f, true, false, true);

	HangarRack = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("HangarRack"));
	HangarRack->SetupAttachment(BodyMesh);
	ConfigureRunwayBreakerPoint(
		HangarRack, TEXT("HangarRack"), FVector(35.f, 95.f, -32.f),
		FVector(0.55f, 0.32f, 0.25f), 100.f, true, false, true);

	HeatManifold = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("HeatManifold"));
	HeatManifold->SetupAttachment(BodyMesh);
	ConfigureRunwayBreakerPoint(
		HeatManifold, TEXT("HeatManifold"), FVector(-35.f, 0.f, 35.f),
		FVector(0.4f, 0.65f, 0.18f), 100.f, true, false, false);

	PortEngine = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("PortEngine"));
	PortEngine->SetupAttachment(BodyMesh);
	ConfigureRunwayBreakerPoint(
		PortEngine, TEXT("PortEngine"), FVector(-165.f, -65.f, 5.f),
		FVector(0.45f, 0.45f, 0.7f), 250.f, false, true, false);

	if (CubeAsset.Succeeded())
	{
		RunwayRack->SetStaticMesh(CubeAsset.Object);
		HangarRack->SetStaticMesh(CubeAsset.Object);
		HeatManifold->SetStaticMesh(CubeAsset.Object);
	}
	if (CylinderAsset.Succeeded())
	{
		PortEngine->SetStaticMesh(CylinderAsset.Object);
	}

	DebrisPortWing = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisPortWing"));
	DebrisPortWing->SetupAttachment(BodyMesh);
	DebrisPortWing->SetRelativeLocation(FVector(0.f, -125.f, 0.f));
	if (CubeAsset.Succeeded())
	{
		DebrisPortWing->SetStaticMesh(CubeAsset.Object);
		DebrisPortWing->SetRelativeScale3D(FVector(1.6f, 0.8f, 0.15f));
	}
	RegisterDefeatDebris(DebrisPortWing);

	DebrisPayloadBay = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisPayloadBay"));
	DebrisPayloadBay->SetupAttachment(BodyMesh);
	DebrisPayloadBay->SetRelativeLocation(FVector(35.f, 0.f, -25.f));
	if (CubeAsset.Succeeded())
	{
		DebrisPayloadBay->SetStaticMesh(CubeAsset.Object);
		DebrisPayloadBay->SetRelativeScale3D(FVector(0.75f, 0.8f, 0.22f));
	}
	RegisterDefeatDebris(DebrisPayloadBay);

	DebrisEngine = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisEngine"));
	DebrisEngine->SetupAttachment(BodyMesh);
	DebrisEngine->SetRelativeLocation(FVector(-165.f, -65.f, 0.f));
	if (CylinderAsset.Succeeded())
	{
		DebrisEngine->SetStaticMesh(CylinderAsset.Object);
		DebrisEngine->SetRelativeScale3D(FVector(0.42f, 0.42f, 0.62f));
	}
	RegisterDefeatDebris(DebrisEngine);

	Tags.AddUnique(TEXT("Skyguard.Mission06.RunwayBreaker"));
	Tags.AddUnique(TEXT("Skyguard.PayloadCarrier"));
	Tags.AddUnique(TEXT("Skyguard.ProxyArt.Runtime"));
}

bool ASkyguardRunwayBreakerBoss::ArmEmergencyRifleFinish()
{
	const bool bOrbit =
		CurrentPilotCommand == ESkyguardPilotCommand::OrbitLeft ||
		CurrentPilotCommand == ESkyguardPilotCommand::OrbitRight;
	if (Phase != ESkyguardBossPhase::LockWindow ||
		!HeatManifold->bDestroyed ||
		PortEngine->bDestroyed ||
		!bOrbit)
	{
		return false;
	}
	bEmergencyRifleFinishArmed = true;
	bIglaLockEnabled = false;
	PortEngine->bAcceptsRifle = true;
	SetBossPhase(ESkyguardBossPhase::Critical);
	return true;
}

void ASkyguardRunwayBreakerBoss::HandleWeakPointDestroyed(
	USkyguardBossWeakPointComponent* WeakPoint,
	ESkyguardBossWeapon Weapon)
{
	if (WeakPoint == RunwayRack || WeakPoint == HangarRack)
	{
		SetBossPhase(ESkyguardBossPhase::Disarm);
		if (RunwayRack->bDestroyed && HangarRack->bDestroyed)
		{
			HeatManifold->SetExposed(true);
		}
		return;
	}
	if (WeakPoint == HeatManifold &&
		RunwayRack->bDestroyed &&
		HangarRack->bDestroyed)
	{
		PortEngine->SetExposed(true);
		bIglaLockEnabled = true;
		SetBossPhase(ESkyguardBossPhase::LockWindow);
		return;
	}
	if (WeakPoint == PortEngine &&
		(Weapon == ESkyguardBossWeapon::Igla ||
			bEmergencyRifleFinishArmed))
	{
		SetBossPhase(ESkyguardBossPhase::Defeated);
	}
}
