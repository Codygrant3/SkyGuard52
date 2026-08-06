#include "SkyguardLastFlightBoss.h"

#include "SkyguardBossWeakPointComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	void ConfigureFinaleWeakPoint(
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

ASkyguardLastFlightBoss::ASkyguardLastFlightBoss()
{
	MaxDefeatDebrisPieces = 6;
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderAsset(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	UStaticMesh* Cube = CubeAsset.Succeeded() ? CubeAsset.Object : nullptr;
	UStaticMesh* Cylinder =
		CylinderAsset.Succeeded() ? CylinderAsset.Object : nullptr;
	if (Cube)
	{
		BodyMesh->SetStaticMesh(Cube);
		BodyMesh->SetRelativeScale3D(FVector(6.2f, 4.4f, 0.7f));
	}

	PortGuidanceArray =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("PortGuidanceArray"));
	PortGuidanceArray->SetupAttachment(BodyMesh);
	ConfigureFinaleWeakPoint(
		PortGuidanceArray, TEXT("PortGuidanceArray"),
		FVector(210.f, -250.f, 40.f), FVector(0.35f, 0.55f, 0.3f),
		85.f, true, false);
	StarboardGuidanceArray =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("StarboardGuidanceArray"));
	StarboardGuidanceArray->SetupAttachment(BodyMesh);
	ConfigureFinaleWeakPoint(
		StarboardGuidanceArray, TEXT("StarboardGuidanceArray"),
		FVector(210.f, 250.f, 40.f), FVector(0.35f, 0.55f, 0.3f),
		85.f, true, false);
	PortStrikeBayMechanism =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("PortStrikeBayMechanism"));
	PortStrikeBayMechanism->SetupAttachment(BodyMesh);
	ConfigureFinaleWeakPoint(
		PortStrikeBayMechanism, TEXT("PortStrikeBayMechanism"),
		FVector(50.f, -225.f, -45.f), FVector(0.65f, 0.4f, 0.22f),
		110.f, true, false);
	StarboardStrikeBayMechanism =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("StarboardStrikeBayMechanism"));
	StarboardStrikeBayMechanism->SetupAttachment(BodyMesh);
	ConfigureFinaleWeakPoint(
		StarboardStrikeBayMechanism, TEXT("StarboardStrikeBayMechanism"),
		FVector(50.f, 225.f, -45.f), FVector(0.65f, 0.4f, 0.22f),
		110.f, true, false);
	PortCoolingSystem =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("PortCoolingSystem"));
	PortCoolingSystem->SetupAttachment(BodyMesh);
	ConfigureFinaleWeakPoint(
		PortCoolingSystem, TEXT("PortCoolingSystem"),
		FVector(-80.f, -160.f, 45.f), FVector(0.48f, 0.36f, 0.3f),
		120.f, true, false);
	StarboardCoolingSystem =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("StarboardCoolingSystem"));
	StarboardCoolingSystem->SetupAttachment(BodyMesh);
	ConfigureFinaleWeakPoint(
		StarboardCoolingSystem, TEXT("StarboardCoolingSystem"),
		FVector(-80.f, 160.f, 45.f), FVector(0.48f, 0.36f, 0.3f),
		120.f, true, false);
	Jammer = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("Jammer"));
	Jammer->SetupAttachment(BodyMesh);
	ConfigureFinaleWeakPoint(
		Jammer, TEXT("Jammer"), FVector(-20.f, 0.f, 95.f),
		FVector(0.52f, 0.52f, 0.25f), 135.f, true, false);
	PortEngine = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("PortEngine"));
	PortEngine->SetupAttachment(BodyMesh);
	ConfigureFinaleWeakPoint(
		PortEngine, TEXT("PortEngine"), FVector(-260.f, -145.f, 0.f),
		FVector(0.5f, 0.5f, 0.8f), 260.f, false, true);
	StarboardEngine =
		CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
			TEXT("StarboardEngine"));
	StarboardEngine->SetupAttachment(BodyMesh);
	ConfigureFinaleWeakPoint(
		StarboardEngine, TEXT("StarboardEngine"),
		FVector(-260.f, 145.f, 0.f), FVector(0.5f, 0.5f, 0.8f),
		260.f, false, true);
	CommandCore = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(
		TEXT("CommandCore"));
	CommandCore->SetupAttachment(BodyMesh);
	ConfigureFinaleWeakPoint(
		CommandCore, TEXT("CommandCore"), FVector(-40.f, 0.f, 5.f),
		FVector(0.55f, 0.55f, 0.55f), 180.f, false, false);

	for (USkyguardBossWeakPointComponent* Point : {
		PortGuidanceArray, StarboardGuidanceArray,
		PortStrikeBayMechanism, StarboardStrikeBayMechanism,
		PortCoolingSystem, StarboardCoolingSystem, Jammer, CommandCore})
	{
		if (Point && Cube)
		{
			Point->SetStaticMesh(Cube);
		}
	}
	for (USkyguardBossWeakPointComponent* Engine :
		{PortEngine, StarboardEngine})
	{
		if (Engine && Cylinder)
		{
			Engine->SetStaticMesh(Cylinder);
		}
	}

	DebrisArmorPort = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisArmorPort"));
	DebrisArmorPort->SetupAttachment(BodyMesh);
	DebrisArmorPort->SetRelativeLocation(FVector(30.f, -235.f, 30.f));
	DebrisArmorPort->SetRelativeScale3D(FVector(1.2f, 0.28f, 0.16f));
	DebrisArmorStarboard = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisArmorStarboard"));
	DebrisArmorStarboard->SetupAttachment(BodyMesh);
	DebrisArmorStarboard->SetRelativeLocation(FVector(30.f, 235.f, 30.f));
	DebrisArmorStarboard->SetRelativeScale3D(
		FVector(1.2f, 0.28f, 0.16f));
	DebrisStrikeBayPort = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisStrikeBayPort"));
	DebrisStrikeBayPort->SetupAttachment(BodyMesh);
	DebrisStrikeBayPort->SetRelativeLocation(FVector(50.f, -225.f, -45.f));
	DebrisStrikeBayPort->SetRelativeScale3D(
		FVector(0.65f, 0.4f, 0.22f));
	DebrisStrikeBayStarboard =
		CreateDefaultSubobject<UStaticMeshComponent>(
			TEXT("DebrisStrikeBayStarboard"));
	DebrisStrikeBayStarboard->SetupAttachment(BodyMesh);
	DebrisStrikeBayStarboard->SetRelativeLocation(
		FVector(50.f, 225.f, -45.f));
	DebrisStrikeBayStarboard->SetRelativeScale3D(
		FVector(0.65f, 0.4f, 0.22f));
	DebrisEnginePort = CreateDefaultSubobject<UStaticMeshComponent>(
		TEXT("DebrisEnginePort"));
	DebrisEnginePort->SetupAttachment(BodyMesh);
	DebrisEnginePort->SetRelativeLocation(FVector(-260.f, -145.f, 0.f));
	DebrisEnginePort->SetRelativeScale3D(FVector(0.5f, 0.5f, 0.8f));
	DebrisEngineStarboard =
		CreateDefaultSubobject<UStaticMeshComponent>(
			TEXT("DebrisEngineStarboard"));
	DebrisEngineStarboard->SetupAttachment(BodyMesh);
	DebrisEngineStarboard->SetRelativeLocation(
		FVector(-260.f, 145.f, 0.f));
	DebrisEngineStarboard->SetRelativeScale3D(
		FVector(0.5f, 0.5f, 0.8f));
	for (UStaticMeshComponent* Debris : {
		DebrisArmorPort, DebrisArmorStarboard,
		DebrisStrikeBayPort, DebrisStrikeBayStarboard})
	{
		if (Debris && Cube)
		{
			Debris->SetStaticMesh(Cube);
		}
	}
	for (UStaticMeshComponent* Debris :
		{DebrisEnginePort, DebrisEngineStarboard})
	{
		if (Debris && Cylinder)
		{
			Debris->SetStaticMesh(Cylinder);
		}
	}
	for (UStaticMeshComponent* Debris : {
		DebrisArmorPort, DebrisArmorStarboard,
		DebrisStrikeBayPort, DebrisStrikeBayStarboard,
		DebrisEnginePort, DebrisEngineStarboard})
	{
		RegisterDefeatDebris(Debris);
	}

	Tags.AddUnique(TEXT("Skyguard.Mission10.LastFlight"));
	Tags.AddUnique(TEXT("Skyguard.EvacuationThreat"));
	Tags.AddUnique(TEXT("Skyguard.ProxyArt.Runtime"));
}

bool ASkyguardLastFlightBoss::OpenGuidanceArrayExposure()
{
	if (FinaleStage != ESkyguardLastFlightStage::Highway)
	{
		return false;
	}
	if (CurrentPilotCommand == ESkyguardPilotCommand::OrbitLeft &&
		!PortGuidanceArray->bDestroyed)
	{
		PortGuidanceArray->SetExposed(true);
		return true;
	}
	if (CurrentPilotCommand == ESkyguardPilotCommand::OrbitRight &&
		!StarboardGuidanceArray->bDestroyed)
	{
		StarboardGuidanceArray->SetExposed(true);
		return true;
	}
	return false;
}

bool ASkyguardLastFlightBoss::BeginTerminalStrikeCycle()
{
	if (FinaleStage != ESkyguardLastFlightStage::Terminal ||
		!PortGuidanceArray->bDestroyed ||
		!StarboardGuidanceArray->bDestroyed)
	{
		return false;
	}
	bTerminalStrikeCycleOpen = true;
	PortStrikeBayMechanism->SetExposed(true);
	StarboardStrikeBayMechanism->SetExposed(true);
	return true;
}

bool ASkyguardLastFlightBoss::OpenFirstIglaWindow()
{
	if (FinaleStage != ESkyguardLastFlightStage::Terminal ||
		!PortCoolingSystem->bDestroyed ||
		!StarboardCoolingSystem->bDestroyed ||
		!HasSafeCivilianSeparation() ||
		CurrentPilotCommand != ESkyguardPilotCommand::Extend)
	{
		return false;
	}
	PortEngine->SetExposed(true);
	bIglaLockEnabled = true;
	return true;
}

bool ASkyguardLastFlightBoss::IssueClimbCommand()
{
	if (FinaleStage != ESkyguardLastFlightStage::EvacuationShip ||
		!PortEngine->bDestroyed)
	{
		return false;
	}
	bClimbCommandIssued = true;
	Jammer->SetExposed(true);
	return true;
}

bool ASkyguardLastFlightBoss::OpenFinalIglaWindow()
{
	if (FinaleStage != ESkyguardLastFlightStage::EvacuationShip ||
		!bClimbCommandIssued || !Jammer->bDestroyed ||
		!HasSafeCivilianSeparation() ||
		CurrentPilotCommand != ESkyguardPilotCommand::Extend)
	{
		return false;
	}
	StarboardEngine->SetExposed(true);
	bIglaLockEnabled = true;
	return true;
}

bool ASkyguardLastFlightBoss::ArmCommandCoreRiflePath()
{
	if (FinaleStage != ESkyguardLastFlightStage::EvacuationShip ||
		!StarboardEngine->bDestroyed ||
		CurrentPilotCommand != ESkyguardPilotCommand::Pursuit)
	{
		return false;
	}
	bCommandCoreRifleArmed = true;
	CommandCore->bAcceptsRifle = true;
	CommandCore->SetExposed(true);
	return true;
}

bool ASkyguardLastFlightBoss::DivertWreckFromCivilians()
{
	if (FinaleStage != ESkyguardLastFlightStage::DisabledDescent ||
		bWreckDiverted || !HasSafeCivilianSeparation() ||
		CurrentPilotCommand != ESkyguardPilotCommand::Break)
	{
		return false;
	}
	bWreckDiverted = true;
	FinaleStage = ESkyguardLastFlightStage::Defeated;
	SetBossPhase(ESkyguardBossPhase::Defeated);
	return true;
}

void ASkyguardLastFlightBoss::SetCivilianSeparationMeters(
	const float SeparationMeters)
{
	CivilianSeparationMeters = FMath::Max(0.f, SeparationMeters);
	if (!HasSafeCivilianSeparation())
	{
		bIglaLockEnabled = false;
	}
}

bool ASkyguardLastFlightBoss::HasSafeCivilianSeparation() const
{
	return CivilianSeparationMeters >= MinimumCivilianSeparationMeters;
}

void ASkyguardLastFlightBoss::AdvanceObjectiveMilestone()
{
	ObjectiveMilestonesReached =
		FMath::Clamp(ObjectiveMilestonesReached + 1, 0, 4);
}

void ASkyguardLastFlightBoss::HandleWeakPointDestroyed(
	USkyguardBossWeakPointComponent* WeakPoint,
	const ESkyguardBossWeapon Weapon)
{
	if ((WeakPoint == PortGuidanceArray ||
			WeakPoint == StarboardGuidanceArray) &&
		PortGuidanceArray->bDestroyed &&
		StarboardGuidanceArray->bDestroyed)
	{
		FinaleStage = ESkyguardLastFlightStage::Terminal;
		SetBossPhase(ESkyguardBossPhase::Disarm);
		AdvanceObjectiveMilestone();
		return;
	}
	if (WeakPoint == PortStrikeBayMechanism &&
		bTerminalStrikeCycleOpen)
	{
		PortCoolingSystem->SetExposed(true);
		return;
	}
	if (WeakPoint == StarboardStrikeBayMechanism &&
		bTerminalStrikeCycleOpen)
	{
		StarboardCoolingSystem->SetExposed(true);
		return;
	}
	if ((WeakPoint == PortCoolingSystem ||
			WeakPoint == StarboardCoolingSystem) &&
		PortCoolingSystem->bDestroyed &&
		StarboardCoolingSystem->bDestroyed)
	{
		SetBossPhase(ESkyguardBossPhase::LockWindow);
		return;
	}
	if (WeakPoint == PortEngine &&
		Weapon == ESkyguardBossWeapon::Igla)
	{
		bIglaLockEnabled = false;
		FinaleStage = ESkyguardLastFlightStage::EvacuationShip;
		SetBossPhase(ESkyguardBossPhase::Critical);
		AdvanceObjectiveMilestone();
		return;
	}
	if (WeakPoint == Jammer && bClimbCommandIssued)
	{
		SetBossPhase(ESkyguardBossPhase::LockWindow);
		return;
	}
	if (WeakPoint == StarboardEngine &&
		Weapon == ESkyguardBossWeapon::Igla)
	{
		bIglaLockEnabled = false;
		SetBossPhase(ESkyguardBossPhase::Critical);
		AdvanceObjectiveMilestone();
		return;
	}
	if (WeakPoint == CommandCore && bCommandCoreRifleArmed)
	{
		FinaleStage = ESkyguardLastFlightStage::DisabledDescent;
		SetBossPhase(ESkyguardBossPhase::Critical);
		AdvanceObjectiveMilestone();
	}
}
