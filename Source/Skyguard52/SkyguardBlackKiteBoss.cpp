#include "SkyguardBlackKiteBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	void ConfigureBlackKitePoint(
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

ASkyguardBlackKiteBoss::ASkyguardBlackKiteBoss()
{
	MaxDefeatDebrisPieces = 3;
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (CubeAsset.Succeeded())
	{
		BodyMesh->SetStaticMesh(CubeAsset.Object);
		BodyMesh->SetRelativeScale3D(FVector(3.8f, 3.0f, 0.35f));
	}

	PortNavigationVane =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("PortNavigationVane"));
	PortNavigationVane->SetupAttachment(BodyMesh);
	ConfigureBlackKitePoint(
		PortNavigationVane, TEXT("PortNavigationVane"),
		FVector(-90.f, -120.f, 25.f), FVector(0.55f, 0.15f, 0.45f),
		75.f, true, false, false);

	StarboardNavigationVane =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("StarboardNavigationVane"));
	StarboardNavigationVane->SetupAttachment(BodyMesh);
	ConfigureBlackKitePoint(
		StarboardNavigationVane, TEXT("StarboardNavigationVane"),
		FVector(-90.f, 120.f, 25.f), FVector(0.55f, 0.15f, 0.45f),
		75.f, true, false, false);

	Jammer = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("Jammer"));
	Jammer->SetupAttachment(BodyMesh);
	ConfigureBlackKitePoint(
		Jammer, TEXT("Jammer"), FVector(25.f, 0.f, -35.f),
		FVector(0.55f, 0.55f, 0.25f), 125.f,
		true, false, false);

	PowerBus = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("PowerBus"));
	PowerBus->SetupAttachment(BodyMesh);
	ConfigureBlackKitePoint(
		PowerBus, TEXT("PowerBus"), FVector(-135.f, 0.f, 15.f),
		FVector(0.38f, 0.8f, 0.2f), 225.f,
		false, true, false);

	if (CubeAsset.Succeeded())
	{
		PortNavigationVane->SetStaticMesh(CubeAsset.Object);
		StarboardNavigationVane->SetStaticMesh(CubeAsset.Object);
		Jammer->SetStaticMesh(CubeAsset.Object);
		PowerBus->SetStaticMesh(CubeAsset.Object);
	}

	DebrisPortVane = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisPortVane"));
	DebrisPortVane->SetupAttachment(BodyMesh);
	DebrisPortVane->SetRelativeLocation(FVector(-90.f, -120.f, 25.f));
	DebrisStarboardVane = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisStarboardVane"));
	DebrisStarboardVane->SetupAttachment(BodyMesh);
	DebrisStarboardVane->SetRelativeLocation(FVector(-90.f, 120.f, 25.f));
	DebrisJammer = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisJammer"));
	DebrisJammer->SetupAttachment(BodyMesh);
	DebrisJammer->SetRelativeLocation(FVector(25.f, 0.f, -35.f));
	if (CubeAsset.Succeeded())
	{
		DebrisPortVane->SetStaticMesh(CubeAsset.Object);
		DebrisPortVane->SetRelativeScale3D(FVector(0.5f, 0.14f, 0.42f));
		DebrisStarboardVane->SetStaticMesh(CubeAsset.Object);
		DebrisStarboardVane->SetRelativeScale3D(FVector(0.5f, 0.14f, 0.42f));
		DebrisJammer->SetStaticMesh(CubeAsset.Object);
		DebrisJammer->SetRelativeScale3D(FVector(0.5f, 0.5f, 0.22f));
	}
	RegisterDefeatDebris(DebrisPortVane);
	RegisterDefeatDebris(DebrisStarboardVane);
	RegisterDefeatDebris(DebrisJammer);

	Tags.AddUnique(TEXT("Skyguard.Mission04.BlackKite"));
	Tags.AddUnique(TEXT("Skyguard.LowObservable"));
	Tags.AddUnique(TEXT("Skyguard.Jammer"));
	Tags.AddUnique(TEXT("Skyguard.ProxyArt.Runtime"));
}

void ASkyguardBlackKiteBoss::SetSearchlightTracked(const bool bTracked)
{
	bSearchlightTracked = bTracked;
	if (!PortNavigationVane->bDestroyed)
	{
		PortNavigationVane->SetExposed(bTracked);
	}
	if (!StarboardNavigationVane->bDestroyed)
	{
		StarboardNavigationVane->SetExposed(bTracked);
	}
}

bool ASkyguardBlackKiteBoss::ArmEmergencyRifleFinish()
{
	const bool bOrbit =
		CurrentPilotCommand == ESkyguardPilotCommand::OrbitLeft ||
		CurrentPilotCommand == ESkyguardPilotCommand::OrbitRight;
	if (Phase != ESkyguardBossPhase::LockWindow ||
		!Jammer->bDestroyed ||
		PowerBus->bDestroyed ||
		!bOrbit)
	{
		return false;
	}
	bEmergencyRifleFinishArmed = true;
	bIglaLockEnabled = false;
	PowerBus->bAcceptsRifle = true;
	SetBossPhase(ESkyguardBossPhase::Critical);
	return true;
}

void ASkyguardBlackKiteBoss::HandleWeakPointDestroyed(
	USkyguardBossWeakPointComponent* WeakPoint,
	const ESkyguardBossWeapon Weapon)
{
	if (WeakPoint == PortNavigationVane ||
		WeakPoint == StarboardNavigationVane)
	{
		if (PortNavigationVane->bDestroyed &&
			StarboardNavigationVane->bDestroyed)
		{
			Jammer->SetExposed(true);
			SetBossPhase(ESkyguardBossPhase::Disarm);
		}
		return;
	}
	if (WeakPoint == Jammer &&
		PortNavigationVane->bDestroyed &&
		StarboardNavigationVane->bDestroyed)
	{
		PowerBus->SetExposed(true);
		bIglaLockEnabled = true;
		SetBossPhase(ESkyguardBossPhase::LockWindow);
		return;
	}
	if (WeakPoint == PowerBus &&
		(Weapon == ESkyguardBossWeapon::Igla ||
			bEmergencyRifleFinishArmed))
	{
		SetBossPhase(ESkyguardBossPhase::Defeated);
	}
}
