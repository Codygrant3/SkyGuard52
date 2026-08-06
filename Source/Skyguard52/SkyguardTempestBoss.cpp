#include "SkyguardTempestBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	void ConfigureTempestPoint(
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

ASkyguardTempestBoss::ASkyguardTempestBoss()
{
	MaxDefeatDebrisPieces = 3;
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderAsset(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (CubeAsset.Succeeded())
	{
		BodyMesh->SetStaticMesh(CubeAsset.Object);
		BodyMesh->SetRelativeScale3D(FVector(4.4f, 3.5f, 0.65f));
	}

	PortDischargeBoom =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("PortDischargeBoom"));
	PortDischargeBoom->SetupAttachment(BodyMesh);
	ConfigureTempestPoint(
		PortDischargeBoom, TEXT("PortDischargeBoom"),
		FVector(45.f, -155.f, 12.f), FVector(0.2f, 0.2f, 0.9f),
		90.f, true, false, false);

	StarboardDischargeBoom =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("StarboardDischargeBoom"));
	StarboardDischargeBoom->SetupAttachment(BodyMesh);
	ConfigureTempestPoint(
		StarboardDischargeBoom, TEXT("StarboardDischargeBoom"),
		FVector(45.f, 155.f, 12.f), FVector(0.2f, 0.2f, 0.9f),
		90.f, true, false, false);

	ControlServo =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("ControlServo"));
	ControlServo->SetupAttachment(BodyMesh);
	ConfigureTempestPoint(
		ControlServo, TEXT("ControlServo"),
		FVector(-30.f, 0.f, 48.f), FVector(0.45f, 0.7f, 0.22f),
		125.f, true, false, false);

	EngineIntake =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("EngineIntake"));
	EngineIntake->SetupAttachment(BodyMesh);
	ConfigureTempestPoint(
		EngineIntake, TEXT("EngineIntake"),
		FVector(-175.f, 0.f, 8.f), FVector(0.52f, 0.52f, 0.65f),
		250.f, false, true, false);

	if (CylinderAsset.Succeeded())
	{
		PortDischargeBoom->SetStaticMesh(CylinderAsset.Object);
		StarboardDischargeBoom->SetStaticMesh(CylinderAsset.Object);
		EngineIntake->SetStaticMesh(CylinderAsset.Object);
	}
	if (CubeAsset.Succeeded())
	{
		ControlServo->SetStaticMesh(CubeAsset.Object);
	}

	DebrisPortPanel = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisPortPanel"));
	DebrisPortPanel->SetupAttachment(BodyMesh);
	DebrisPortPanel->SetRelativeLocation(FVector(0.f, -125.f, 25.f));
	DebrisStarboardPanel = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisStarboardPanel"));
	DebrisStarboardPanel->SetupAttachment(BodyMesh);
	DebrisStarboardPanel->SetRelativeLocation(FVector(0.f, 125.f, 25.f));
	DebrisIntakePanel = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisIntakePanel"));
	DebrisIntakePanel->SetupAttachment(BodyMesh);
	DebrisIntakePanel->SetRelativeLocation(FVector(-165.f, 0.f, 8.f));
	if (CubeAsset.Succeeded())
	{
		DebrisPortPanel->SetStaticMesh(CubeAsset.Object);
		DebrisPortPanel->SetRelativeScale3D(FVector(1.25f, 0.65f, 0.12f));
		DebrisStarboardPanel->SetStaticMesh(CubeAsset.Object);
		DebrisStarboardPanel->SetRelativeScale3D(FVector(1.25f, 0.65f, 0.12f));
		DebrisIntakePanel->SetStaticMesh(CubeAsset.Object);
		DebrisIntakePanel->SetRelativeScale3D(FVector(0.55f, 0.65f, 0.18f));
	}
	RegisterDefeatDebris(DebrisPortPanel);
	RegisterDefeatDebris(DebrisStarboardPanel);
	RegisterDefeatDebris(DebrisIntakePanel);

	Tags.AddUnique(TEXT("Skyguard.Mission05.Tempest"));
	Tags.AddUnique(TEXT("Skyguard.StormBoss"));
	Tags.AddUnique(TEXT("Skyguard.ProxyArt.Runtime"));
}

void ASkyguardTempestBoss::SetLightningExposed(const bool bExposed)
{
	bLightningExposed = bExposed;
	if (!PortDischargeBoom->bDestroyed)
	{
		PortDischargeBoom->SetExposed(bExposed);
	}
	if (!StarboardDischargeBoom->bDestroyed)
	{
		StarboardDischargeBoom->SetExposed(bExposed);
	}
}

bool ASkyguardTempestBoss::ApplyCorrectiveBankGust(
	const float Turbulence)
{
	if (Turbulence < 0.7f ||
		!PortDischargeBoom->bDestroyed ||
		!StarboardDischargeBoom->bDestroyed ||
		ControlServo->bDestroyed)
	{
		return false;
	}
	bCorrectiveBankExposed = true;
	ControlServo->SetExposed(true);
	return true;
}

bool ASkyguardTempestBoss::AdvanceStabilizedIglaLock(
	const float DeltaSeconds,
	const float Turbulence)
{
	if (DeltaSeconds <= 0.f ||
		Phase != ESkyguardBossPhase::LockWindow ||
		!ControlServo->bDestroyed ||
		EngineIntake->bDestroyed ||
		CurrentPilotCommand != ESkyguardPilotCommand::Extend)
	{
		LockStabilitySeconds = 0.f;
		return false;
	}
	const float StabilityRate =
		FMath::Clamp(1.f - FMath::Clamp(Turbulence, 0.f, 1.f) * 0.65f,
			0.25f, 1.f);
	LockStabilitySeconds += DeltaSeconds * StabilityRate;
	if (LockStabilitySeconds >= RequiredLockStabilitySeconds)
	{
		bIglaLockEnabled = true;
		return true;
	}
	return false;
}

bool ASkyguardTempestBoss::ArmBreakRifleFinish()
{
	if (Phase != ESkyguardBossPhase::LockWindow ||
		!ControlServo->bDestroyed ||
		EngineIntake->bDestroyed ||
		CurrentPilotCommand != ESkyguardPilotCommand::Break)
	{
		return false;
	}
	bBreakRifleFinishArmed = true;
	bIglaLockEnabled = false;
	EngineIntake->bAcceptsRifle = true;
	SetBossPhase(ESkyguardBossPhase::Critical);
	return true;
}

void ASkyguardTempestBoss::HandleWeakPointDestroyed(
	USkyguardBossWeakPointComponent* WeakPoint,
	const ESkyguardBossWeapon Weapon)
{
	if (WeakPoint == PortDischargeBoom ||
		WeakPoint == StarboardDischargeBoom)
	{
		if (PortDischargeBoom->bDestroyed &&
			StarboardDischargeBoom->bDestroyed)
		{
			SetBossPhase(ESkyguardBossPhase::Disarm);
		}
		return;
	}
	if (WeakPoint == ControlServo &&
		bCorrectiveBankExposed &&
		PortDischargeBoom->bDestroyed &&
		StarboardDischargeBoom->bDestroyed)
	{
		EngineIntake->SetExposed(true);
		bIglaLockEnabled = false;
		LockStabilitySeconds = 0.f;
		SetBossPhase(ESkyguardBossPhase::LockWindow);
		return;
	}
	if (WeakPoint == EngineIntake &&
		(Weapon == ESkyguardBossWeapon::Igla ||
			bBreakRifleFinishArmed))
	{
		SetBossPhase(ESkyguardBossPhase::Defeated);
	}
}
