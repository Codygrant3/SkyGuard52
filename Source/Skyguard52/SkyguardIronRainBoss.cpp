#include "SkyguardIronRainBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	void ConfigureIronRainPoint(
		USkyguardBossWeakPointComponent* Point,
		const FName Id,
		const FVector& Location,
		const FVector& Scale,
		const float Integrity,
		const bool bRifle,
		const bool bIgla,
		const bool bExposed)
	{
		Point->WeakPointId = Id;
		Point->SetRelativeLocation(Location);
		Point->SetRelativeScale3D(Scale);
		Point->MaxIntegrity = Integrity;
		Point->Integrity = Integrity;
		Point->bAcceptsRifle = bRifle;
		Point->bAcceptsIgla = bIgla;
		Point->SetExposed(bExposed);
	}
}

ASkyguardIronRainBoss::ASkyguardIronRainBoss()
{
	MaxDefeatDebrisPieces = 3;
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderAsset(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (CubeAsset.Succeeded())
	{
		BodyMesh->SetStaticMesh(CubeAsset.Object);
		BodyMesh->SetRelativeScale3D(FVector(7.2f, 5.0f, 0.65f));
	}

#define CREATE_POINT(Member, Id, Location, Scale, Integrity, Rifle, Igla, Exposed) \
	Member = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(TEXT(#Member)); \
	Member->SetupAttachment(BodyMesh); \
	ConfigureIronRainPoint(Member, TEXT(Id), Location, Scale, Integrity, Rifle, Igla, Exposed)

	CREATE_POINT(DispenserPort, "DispenserPort", FVector(90.f, -250.f, -35.f),
		FVector(0.8f, 0.65f, 0.22f), 110.f, true, false, true);
	CREATE_POINT(DispenserCenter, "DispenserCenter", FVector(70.f, 0.f, -42.f),
		FVector(0.8f, 0.65f, 0.22f), 110.f, true, false, true);
	CREATE_POINT(DispenserStarboard, "DispenserStarboard", FVector(90.f, 250.f, -35.f),
		FVector(0.8f, 0.65f, 0.22f), 110.f, true, false, true);
	CREATE_POINT(CommandAntennaPort, "CommandAntennaPort", FVector(40.f, -120.f, 70.f),
		FVector(0.12f, 0.12f, 0.9f), 90.f, true, false, false);
	CREATE_POINT(CommandAntennaStarboard, "CommandAntennaStarboard", FVector(40.f, 120.f, 70.f),
		FVector(0.12f, 0.12f, 0.9f), 90.f, true, false, false);
	CREATE_POINT(DecoyController, "DecoyController", FVector(-20.f, 0.f, 65.f),
		FVector(0.5f, 0.7f, 0.22f), 125.f, true, false, false);
	CREATE_POINT(EnginePodPort, "EnginePodPort", FVector(-220.f, -210.f, 55.f),
		FVector(0.5f, 0.5f, 0.9f), 250.f, false, true, false);
	CREATE_POINT(EnginePodCenter, "EnginePodCenter", FVector(-250.f, 0.f, 60.f),
		FVector(0.5f, 0.5f, 0.9f), 250.f, false, true, false);
	CREATE_POINT(EnginePodStarboard, "EnginePodStarboard", FVector(-220.f, 210.f, 55.f),
		FVector(0.5f, 0.5f, 0.9f), 250.f, false, true, false);
	CREATE_POINT(FuelControlPort, "FuelControlPort", FVector(-170.f, -95.f, 78.f),
		FVector(0.2f, 0.2f, 0.2f), 160.f, true, false, false);
	CREATE_POINT(FuelControlStarboard, "FuelControlStarboard", FVector(-170.f, 95.f, 78.f),
		FVector(0.2f, 0.2f, 0.2f), 160.f, true, false, false);
#undef CREATE_POINT

	Dispensers = {DispenserPort, DispenserCenter, DispenserStarboard};
	Antennae = {CommandAntennaPort, CommandAntennaStarboard};
	Engines = {EnginePodPort, EnginePodCenter, EnginePodStarboard};
	RefreshAuthoredWeakPointRegistry();
	BayReleaseCounts.Init(0, 3);
	for (USkyguardBossWeakPointComponent* Point : Dispensers)
	{
		if (CubeAsset.Succeeded()) Point->SetStaticMesh(CubeAsset.Object);
	}
	for (USkyguardBossWeakPointComponent* Point : Antennae)
	{
		if (CylinderAsset.Succeeded()) Point->SetStaticMesh(CylinderAsset.Object);
	}
	if (CubeAsset.Succeeded())
	{
		DecoyController->SetStaticMesh(CubeAsset.Object);
		FuelControlPort->SetStaticMesh(CubeAsset.Object);
		FuelControlStarboard->SetStaticMesh(CubeAsset.Object);
	}
	for (USkyguardBossWeakPointComponent* Point : Engines)
	{
		if (CylinderAsset.Succeeded()) Point->SetStaticMesh(CylinderAsset.Object);
	}

	DebrisPortWing = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DebrisPortWing"));
	DebrisCenterRack = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DebrisCenterRack"));
	DebrisStarboardWing = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DebrisStarboardWing"));
	for (UStaticMeshComponent* Debris : {DebrisPortWing, DebrisCenterRack, DebrisStarboardWing})
	{
		Debris->SetupAttachment(BodyMesh);
		if (CubeAsset.Succeeded()) Debris->SetStaticMesh(CubeAsset.Object);
		RegisterDefeatDebris(Debris);
	}
	DebrisPortWing->SetRelativeLocation(FVector(0.f, -260.f, 0.f));
	DebrisCenterRack->SetRelativeLocation(FVector(30.f, 0.f, -35.f));
	DebrisStarboardWing->SetRelativeLocation(FVector(0.f, 260.f, 0.f));

	Tags.AddUnique(TEXT("Skyguard.Mission09.IronRain"));
	Tags.AddUnique(TEXT("Skyguard.PoolBounded"));
	Tags.AddUnique(TEXT("Skyguard.ProxyArt.Runtime"));
}

void ASkyguardIronRainBoss::BeginPlay()
{
	Super::BeginPlay();
	// Keep a deterministic authored order after the base component discovery.
	RefreshAuthoredWeakPointRegistry();
}

void ASkyguardIronRainBoss::RefreshAuthoredWeakPointRegistry()
{
	WeakPoints = {
		DispenserPort,
		DispenserCenter,
		DispenserStarboard,
		CommandAntennaPort,
		CommandAntennaStarboard,
		DecoyController,
		EnginePodPort,
		EnginePodCenter,
		EnginePodStarboard,
		FuelControlPort,
		FuelControlStarboard,
	};
}

bool ASkyguardIronRainBoss::OpenDispenserBay(const int32 BayIndex)
{
	if (!Dispensers.IsValidIndex(BayIndex) || Dispensers[BayIndex]->bDestroyed ||
		BayReleaseCounts[BayIndex] >= MaxReleasesPerBay)
	{
		return false;
	}
	Dispensers[BayIndex]->SetExposed(true);
	return true;
}

bool ASkyguardIronRainBoss::ReleasePooledEscort(const int32 BayIndex)
{
	if (!Dispensers.IsValidIndex(BayIndex) || Dispensers[BayIndex]->bDestroyed ||
		!Dispensers[BayIndex]->bExposed ||
		BayReleaseCounts[BayIndex] >= MaxReleasesPerBay)
	{
		return false;
	}
	++BayReleaseCounts[BayIndex];
	++ReleasedEscortCount;
	return true;
}

bool ASkyguardIronRainBoss::IssueClimbCommand()
{
	if (!DecoyController->bDestroyed || Maneuver != ESkyguardIronRainManeuver::None)
	{
		return false;
	}
	Maneuver = ESkyguardIronRainManeuver::Climb;
	IssuePilotCommand(ESkyguardPilotCommand::Extend);
	return true;
}

bool ASkyguardIronRainBoss::IssueCrossCommand()
{
	if (Maneuver != ESkyguardIronRainManeuver::Climb)
	{
		return false;
	}
	Maneuver = ESkyguardIronRainManeuver::Cross;
	IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	return true;
}

bool ASkyguardIronRainBoss::OpenUpperEngineExposure()
{
	if (!DecoyController->bDestroyed ||
		Maneuver != ESkyguardIronRainManeuver::Cross)
	{
		return false;
	}
	// ApplyIglaStrike resolves its target through the base registry. Populate
	// it here as well as BeginPlay so command sequencing is safe in editor
	// simulations and deterministic automation worlds that have not dispatched
	// actor BeginPlay yet.
	RefreshAuthoredWeakPointRegistry();
	for (USkyguardBossWeakPointComponent* Engine : Engines)
	{
		if (!Engine->bDestroyed) Engine->SetExposed(true);
	}
	bIglaLockEnabled = true;
	SetBossPhase(ESkyguardBossPhase::LockWindow);
	return true;
}

bool ASkyguardIronRainBoss::ApplySecondIglaFinish(const float Damage)
{
	if (GetDestroyedEngineCount() != 1 || !IsIglaLockEligible() || Damage <= 0.f)
	{
		return false;
	}
	bool bApplied = false;
	for (USkyguardBossWeakPointComponent* Engine : Engines)
	{
		if (!Engine->bDestroyed)
		{
			bApplied |= ApplyWeaponHit(
				Engine, ESkyguardBossWeapon::Igla, Damage,
				GetActorLocation(), -GetActorForwardVector());
		}
	}
	return bApplied && Phase == ESkyguardBossPhase::Defeated;
}

bool ASkyguardIronRainBoss::ArmFuelControlRifleFinish()
{
	if (GetDestroyedEngineCount() != 1 ||
		Maneuver != ESkyguardIronRainManeuver::Cross ||
		CurrentPilotCommand != ESkyguardPilotCommand::Break)
	{
		return false;
	}
	bFuelControlFinishArmed = true;
	bIglaLockEnabled = false;
	FuelControlPort->SetExposed(true);
	FuelControlStarboard->SetExposed(true);
	return true;
}

int32 ASkyguardIronRainBoss::GetDestroyedDispenserCount() const
{
	int32 Count = 0;
	for (const USkyguardBossWeakPointComponent* Point : Dispensers)
	{
		if (Point && Point->bDestroyed) ++Count;
	}
	return Count;
}

int32 ASkyguardIronRainBoss::GetDestroyedAntennaCount() const
{
	int32 Count = 0;
	for (const USkyguardBossWeakPointComponent* Point : Antennae)
	{
		if (Point && Point->bDestroyed) ++Count;
	}
	return Count;
}

int32 ASkyguardIronRainBoss::GetDestroyedEngineCount() const
{
	int32 Count = 0;
	for (const USkyguardBossWeakPointComponent* Point : Engines)
	{
		if (Point && Point->bDestroyed) ++Count;
	}
	return Count;
}

bool ASkyguardIronRainBoss::AreAllDestroyed(
	const TArray<TObjectPtr<USkyguardBossWeakPointComponent>>& Points) const
{
	if (Points.IsEmpty()) return false;
	for (const USkyguardBossWeakPointComponent* Point : Points)
	{
		if (!Point || !Point->bDestroyed) return false;
	}
	return true;
}

void ASkyguardIronRainBoss::HandleWeakPointDestroyed(
	USkyguardBossWeakPointComponent* WeakPoint,
	const ESkyguardBossWeapon Weapon)
{
	if (Dispensers.Contains(WeakPoint))
	{
		if (AreAllDestroyed(Dispensers))
		{
			for (USkyguardBossWeakPointComponent* Antenna : Antennae)
			{
				Antenna->SetExposed(true);
			}
			SetBossPhase(ESkyguardBossPhase::Disarm);
		}
		return;
	}
	if (Antennae.Contains(WeakPoint))
	{
		if (AreAllDestroyed(Antennae))
		{
			DecoyController->SetExposed(true);
		}
		return;
	}
	if (WeakPoint == DecoyController)
	{
		bIglaLockEnabled = false;
		SetBossPhase(ESkyguardBossPhase::Disarm);
		return;
	}
	if (Engines.Contains(WeakPoint) && Weapon == ESkyguardBossWeapon::Igla)
	{
		if (AreAllDestroyed(Engines))
		{
			SetBossPhase(ESkyguardBossPhase::Defeated);
		}
		else
		{
			SetBossPhase(ESkyguardBossPhase::Critical);
			bIglaLockEnabled = true;
		}
		return;
	}
	if (bFuelControlFinishArmed &&
		(WeakPoint == FuelControlPort || WeakPoint == FuelControlStarboard) &&
		FuelControlPort->bDestroyed && FuelControlStarboard->bDestroyed)
	{
		SetBossPhase(ESkyguardBossPhase::Defeated);
	}
}
