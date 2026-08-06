#include "SkyguardLifelineHunterBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	void ConfigureLifelinePoint(
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

ASkyguardLifelineHunterBoss::ASkyguardLifelineHunterBoss()
{
	MaxDefeatDebrisPieces = 3;
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderAsset(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (CubeAsset.Succeeded())
	{
		BodyMesh->SetStaticMesh(CubeAsset.Object);
		BodyMesh->SetRelativeScale3D(FVector(4.0f, 3.0f, 0.45f));
	}

	OpticalTracker =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("OpticalTracker"));
	OpticalTracker->SetupAttachment(BodyMesh);
	ConfigureLifelinePoint(
		OpticalTracker, TEXT("OpticalTracker"),
		FVector(150.f, -70.f, 5.f), FVector(0.32f, 0.32f, 0.42f),
		90.f, true, false);

	WeaponServo =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("WeaponServo"));
	WeaponServo->SetupAttachment(BodyMesh);
	ConfigureLifelinePoint(
		WeaponServo, TEXT("WeaponServo"),
		FVector(75.f, 85.f, -25.f), FVector(0.42f, 0.35f, 0.28f),
		110.f, true, false);

	CountermeasurePod =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("CountermeasurePod"));
	CountermeasurePod->SetupAttachment(BodyMesh);
	ConfigureLifelinePoint(
		CountermeasurePod, TEXT("CountermeasurePod"),
		FVector(-35.f, 0.f, 38.f), FVector(0.55f, 0.7f, 0.2f),
		125.f, true, false);

	Engine = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("Engine"));
	Engine->SetupAttachment(BodyMesh);
	ConfigureLifelinePoint(
		Engine, TEXT("Engine"), FVector(-165.f, 0.f, 5.f),
		FVector(0.5f, 0.5f, 0.7f), 250.f, false, true);

	if (CubeAsset.Succeeded())
	{
		OpticalTracker->SetStaticMesh(CubeAsset.Object);
		WeaponServo->SetStaticMesh(CubeAsset.Object);
		CountermeasurePod->SetStaticMesh(CubeAsset.Object);
	}
	if (CylinderAsset.Succeeded())
	{
		Engine->SetStaticMesh(CylinderAsset.Object);
	}

	DebrisPrimarySensor = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisPrimarySensor"));
	DebrisPrimarySensor->SetupAttachment(BodyMesh);
	DebrisPrimarySensor->SetRelativeLocation(FVector(150.f, -70.f, 5.f));
	DebrisSecondarySensor = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisSecondarySensor"));
	DebrisSecondarySensor->SetupAttachment(BodyMesh);
	DebrisSecondarySensor->SetRelativeLocation(FVector(75.f, 85.f, -25.f));
	DebrisControlSurface = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisControlSurface"));
	DebrisControlSurface->SetupAttachment(BodyMesh);
	DebrisControlSurface->SetRelativeLocation(FVector(-35.f, 0.f, 38.f));
	if (CubeAsset.Succeeded())
	{
		DebrisPrimarySensor->SetStaticMesh(CubeAsset.Object);
		DebrisPrimarySensor->SetRelativeScale3D(FVector(0.3f));
		DebrisSecondarySensor->SetStaticMesh(CubeAsset.Object);
		DebrisSecondarySensor->SetRelativeScale3D(FVector(0.38f, 0.3f, 0.25f));
		DebrisControlSurface->SetStaticMesh(CubeAsset.Object);
		DebrisControlSurface->SetRelativeScale3D(FVector(0.5f, 0.65f, 0.18f));
	}
	RegisterDefeatDebris(DebrisPrimarySensor);
	RegisterDefeatDebris(DebrisSecondarySensor);
	RegisterDefeatDebris(DebrisControlSurface);

	Tags.AddUnique(TEXT("Skyguard.Mission08.LifelineHunter"));
	Tags.AddUnique(TEXT("Skyguard.RescueThreat"));
	Tags.AddUnique(TEXT("Skyguard.ProxyArt.Runtime"));
}

bool ASkyguardLifelineHunterBoss::OpenSensorExposure()
{
	if (!OpticalTracker->bDestroyed &&
		CurrentPilotCommand == ESkyguardPilotCommand::OrbitLeft)
	{
		OpticalTracker->SetExposed(true);
		return true;
	}
	if (OpticalTracker->bDestroyed &&
		!WeaponServo->bDestroyed &&
		CurrentPilotCommand == ESkyguardPilotCommand::OrbitRight)
	{
		WeaponServo->SetExposed(true);
		return true;
	}
	return false;
}

void ASkyguardLifelineHunterBoss::SetFriendlySeparationMeters(
	const float SeparationMeters)
{
	FriendlySeparationMeters = FMath::Max(0.f, SeparationMeters);
	if (FriendlySeparationMeters < MinimumWeaponSeparationMeters)
	{
		bIglaLockEnabled = false;
	}
}

bool ASkyguardLifelineHunterBoss::OpenSafeIglaWindow()
{
	if (Phase != ESkyguardBossPhase::LockWindow ||
		!CountermeasurePod->bDestroyed || Engine->bDestroyed ||
		FriendlySeparationMeters < MinimumWeaponSeparationMeters ||
		CurrentPilotCommand != ESkyguardPilotCommand::Extend)
	{
		return false;
	}
	bIglaLockEnabled = true;
	return true;
}

bool ASkyguardLifelineHunterBoss::ArmSafeRifleEngineFallback()
{
	if (Phase != ESkyguardBossPhase::LockWindow ||
		!CountermeasurePod->bDestroyed || Engine->bDestroyed ||
		FriendlySeparationMeters < MinimumWeaponSeparationMeters ||
		CurrentPilotCommand != ESkyguardPilotCommand::Break)
	{
		return false;
	}
	bSafeRifleFallbackArmed = true;
	bIglaLockEnabled = false;
	Engine->bAcceptsRifle = true;
	return true;
}

bool ASkyguardLifelineHunterBoss::RedirectDisabledDrone()
{
	if (!bDisabledDescent || bCrashRedirected ||
		FriendlySeparationMeters < MinimumWeaponSeparationMeters ||
		CurrentPilotCommand != ESkyguardPilotCommand::Break)
	{
		return false;
	}
	bCrashRedirected = true;
	SetBossPhase(ESkyguardBossPhase::Defeated);
	return true;
}

void ASkyguardLifelineHunterBoss::HandleWeakPointDestroyed(
	USkyguardBossWeakPointComponent* WeakPoint,
	const ESkyguardBossWeapon Weapon)
{
	if (WeakPoint == OpticalTracker)
	{
		SetBossPhase(ESkyguardBossPhase::Disarm);
		return;
	}
	if (WeakPoint == WeaponServo && OpticalTracker->bDestroyed)
	{
		CountermeasurePod->SetExposed(true);
		SetBossPhase(ESkyguardBossPhase::Disarm);
		return;
	}
	if (WeakPoint == CountermeasurePod && WeaponServo->bDestroyed)
	{
		Engine->SetExposed(true);
		bIglaLockEnabled = false;
		SetBossPhase(ESkyguardBossPhase::LockWindow);
		return;
	}
	if (WeakPoint == Engine &&
		(Weapon == ESkyguardBossWeapon::Igla ||
			bSafeRifleFallbackArmed))
	{
		bDisabledDescent = true;
		bIglaLockEnabled = false;
		SetBossPhase(ESkyguardBossPhase::Critical);
	}
}
