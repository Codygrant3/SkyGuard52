#include "SkyguardRadarGhostBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	void ConfigureRadarGhostPoint(
		USkyguardBossWeakPointComponent* Component,
		const FName Id,
		const FVector& Location,
		const FVector& Scale,
		const float Integrity,
		const bool bRifle,
		const bool bIgla)
	{
		Component->WeakPointId = Id;
		Component->SetRelativeLocation(Location);
		Component->SetRelativeScale3D(Scale);
		Component->MaxIntegrity = Integrity;
		Component->Integrity = Integrity;
		Component->bAcceptsRifle = bRifle;
		Component->bAcceptsIgla = bIgla;
		Component->SetExposed(false);
	}
}

ASkyguardRadarGhostBoss::ASkyguardRadarGhostBoss()
{
	MaxDefeatDebrisPieces = 3;
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderAsset(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (CubeAsset.Succeeded())
	{
		BodyMesh->SetStaticMesh(CubeAsset.Object);
		BodyMesh->SetRelativeScale3D(FVector(3.9f, 3.1f, 0.42f));
	}

	SignatureModulator =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("SignatureModulator"));
	SignatureModulator->SetupAttachment(BodyMesh);
	ConfigureRadarGhostPoint(
		SignatureModulator, TEXT("SignatureModulator"),
		FVector(20.f, -110.f, -28.f), FVector(0.55f, 0.32f, 0.24f),
		100.f, true, false);

	RadarReceiver =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("RadarReceiver"));
	RadarReceiver->SetupAttachment(BodyMesh);
	ConfigureRadarGhostPoint(
		RadarReceiver, TEXT("RadarReceiver"),
		FVector(20.f, 110.f, -28.f), FVector(0.55f, 0.32f, 0.24f),
		100.f, true, false);

	CoolingDoor =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("CoolingDoor"));
	CoolingDoor->SetupAttachment(BodyMesh);
	ConfigureRadarGhostPoint(
		CoolingDoor, TEXT("CoolingDoor"),
		FVector(-60.f, 0.f, 38.f), FVector(0.5f, 0.7f, 0.16f),
		125.f, true, false);

	Engine = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("Engine"));
	Engine->SetupAttachment(BodyMesh);
	ConfigureRadarGhostPoint(
		Engine, TEXT("Engine"), FVector(-165.f, 0.f, 5.f),
		FVector(0.5f, 0.5f, 0.7f), 250.f, false, true);

	if (CubeAsset.Succeeded())
	{
		SignatureModulator->SetStaticMesh(CubeAsset.Object);
		RadarReceiver->SetStaticMesh(CubeAsset.Object);
		CoolingDoor->SetStaticMesh(CubeAsset.Object);
	}
	if (CylinderAsset.Succeeded())
	{
		Engine->SetStaticMesh(CylinderAsset.Object);
	}

	DebrisPortEWPanel = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisPortEWPanel"));
	DebrisPortEWPanel->SetupAttachment(BodyMesh);
	DebrisPortEWPanel->SetRelativeLocation(FVector(20.f, -110.f, -28.f));
	DebrisStarboardEWPanel = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisStarboardEWPanel"));
	DebrisStarboardEWPanel->SetupAttachment(BodyMesh);
	DebrisStarboardEWPanel->SetRelativeLocation(FVector(20.f, 110.f, -28.f));
	DebrisCoolingDoor = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisCoolingDoor"));
	DebrisCoolingDoor->SetupAttachment(BodyMesh);
	DebrisCoolingDoor->SetRelativeLocation(FVector(-60.f, 0.f, 38.f));
	if (CubeAsset.Succeeded())
	{
		DebrisPortEWPanel->SetStaticMesh(CubeAsset.Object);
		DebrisPortEWPanel->SetRelativeScale3D(FVector(0.5f, 0.3f, 0.2f));
		DebrisStarboardEWPanel->SetStaticMesh(CubeAsset.Object);
		DebrisStarboardEWPanel->SetRelativeScale3D(FVector(0.5f, 0.3f, 0.2f));
		DebrisCoolingDoor->SetStaticMesh(CubeAsset.Object);
		DebrisCoolingDoor->SetRelativeScale3D(FVector(0.48f, 0.65f, 0.14f));
	}
	RegisterDefeatDebris(DebrisPortEWPanel);
	RegisterDefeatDebris(DebrisStarboardEWPanel);
	RegisterDefeatDebris(DebrisCoolingDoor);

	Tags.AddUnique(TEXT("Skyguard.Mission07.RadarGhost"));
	Tags.AddUnique(TEXT("Skyguard.ElectronicWarfare"));
	Tags.AddUnique(TEXT("Skyguard.ProxyArt.Runtime"));
}

void ASkyguardRadarGhostBoss::SetContactIdentified(
	const bool bIdentified)
{
	bContactIdentified = bIdentified;
	if (!bIdentified)
	{
		SignatureModulator->SetExposed(false);
		RadarReceiver->SetExposed(false);
	}
}

bool ASkyguardRadarGhostBoss::OpenOrbitExposure()
{
	if (!bContactIdentified)
	{
		return false;
	}
	if (!SignatureModulator->bDestroyed &&
		CurrentPilotCommand == ESkyguardPilotCommand::OrbitLeft)
	{
		SignatureModulator->SetExposed(true);
		return true;
	}
	if (SignatureModulator->bDestroyed &&
		!RadarReceiver->bDestroyed &&
		CurrentPilotCommand == ESkyguardPilotCommand::OrbitRight)
	{
		RadarReceiver->SetExposed(true);
		return true;
	}
	return false;
}

bool ASkyguardRadarGhostBoss::OpenRearAspectIglaWindow()
{
	if (Phase != ESkyguardBossPhase::LockWindow ||
		!CoolingDoor->bDestroyed || Engine->bDestroyed ||
		(CurrentPilotCommand != ESkyguardPilotCommand::Pursuit &&
			CurrentPilotCommand != ESkyguardPilotCommand::Extend))
	{
		return false;
	}
	bIglaLockEnabled = true;
	return true;
}

bool ASkyguardRadarGhostBoss::ArmBreakRifleFinish()
{
	if (Phase != ESkyguardBossPhase::LockWindow ||
		!CoolingDoor->bDestroyed || Engine->bDestroyed ||
		CurrentPilotCommand != ESkyguardPilotCommand::Break)
	{
		return false;
	}
	bBreakRifleFinishArmed = true;
	bIglaLockEnabled = false;
	Engine->bAcceptsRifle = true;
	SetBossPhase(ESkyguardBossPhase::Critical);
	return true;
}

void ASkyguardRadarGhostBoss::HandleWeakPointDestroyed(
	USkyguardBossWeakPointComponent* WeakPoint,
	const ESkyguardBossWeapon Weapon)
{
	if (WeakPoint == SignatureModulator)
	{
		SetBossPhase(ESkyguardBossPhase::Disarm);
		return;
	}
	if (WeakPoint == RadarReceiver &&
		SignatureModulator->bDestroyed)
	{
		CoolingDoor->SetExposed(true);
		SetBossPhase(ESkyguardBossPhase::Disarm);
		return;
	}
	if (WeakPoint == CoolingDoor &&
		RadarReceiver->bDestroyed)
	{
		Engine->SetExposed(true);
		bIglaLockEnabled = false;
		SetBossPhase(ESkyguardBossPhase::LockWindow);
		return;
	}
	if (WeakPoint == Engine &&
		(Weapon == ESkyguardBossWeapon::Igla ||
			bBreakRifleFinishArmed))
	{
		SetBossPhase(ESkyguardBossPhase::Defeated);
	}
}
