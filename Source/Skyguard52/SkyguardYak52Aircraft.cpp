#include "SkyguardYak52Aircraft.h"

#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"

namespace
{
	const TCHAR* L88Root =
		TEXT("/Game/Skyguard/Meshes/L88/yak52_l88_silhouette_blockout/StaticMeshes/");
}

ASkyguardYak52Aircraft::ASkyguardYak52Aircraft()
{
	PrimaryActorTick.bCanEverTick = true;

	AircraftRoot = CreateDefaultSubobject<USceneComponent>(TEXT("AircraftRoot"));
	SetRootComponent(AircraftRoot);

	auto CreateVisual = [this](const TCHAR* Name)
	{
		UStaticMeshComponent* Component = CreateDefaultSubobject<UStaticMeshComponent>(Name);
		Component->SetupAttachment(AircraftRoot);
		Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Component->SetGenerateOverlapEvents(false);
		Component->SetCanEverAffectNavigation(false);
		return Component;
	};

	Airframe = CreateVisual(TEXT("Airframe"));
	Wings = CreateVisual(TEXT("Wings"));
	EngineCowling = CreateVisual(TEXT("EngineCowling"));
	HorizontalTail = CreateVisual(TEXT("HorizontalTail"));
	VerticalTail = CreateVisual(TEXT("VerticalTail"));
	CockpitTub = CreateVisual(TEXT("CockpitTub"));
	RearPanel = CreateVisual(TEXT("RearPanel"));
	FrontCanopyGlass = CreateVisual(TEXT("FrontCanopyGlass"));
	RearCanopyGlass = CreateVisual(TEXT("RearCanopyGlass"));
	PropellerHub = CreateVisual(TEXT("PropellerHub"));
	PropellerBlade = CreateVisual(TEXT("PropellerBlade"));

	ConfigureVisual(Airframe, TEXT("GEO_Airframe.GEO_Airframe"));
	ConfigureVisual(Wings, TEXT("GEO_Wings.GEO_Wings"));
	ConfigureVisual(EngineCowling, TEXT("GEO_EngineCowling.GEO_EngineCowling"));
	ConfigureVisual(HorizontalTail, TEXT("GEO_HorizontalTail.GEO_HorizontalTail"));
	ConfigureVisual(VerticalTail, TEXT("GEO_VerticalTail.GEO_VerticalTail"));
	ConfigureVisual(CockpitTub, TEXT("GEO_CockpitTub.GEO_CockpitTub"));
	ConfigureVisual(RearPanel, TEXT("GEO_RearPanel.GEO_RearPanel"));
	ConfigureVisual(FrontCanopyGlass, TEXT("GEO_FrontCanopyGlass.GEO_FrontCanopyGlass"));
	ConfigureVisual(
		RearCanopyGlass,
		TEXT("GEO_RearCanopyGlass_Stowed.GEO_RearCanopyGlass_Stowed"));
	ConfigureVisual(PropellerHub, TEXT("GEO_PropHub.GEO_PropHub"));
	ConfigureVisual(PropellerBlade, TEXT("GEO_PropBlade_A.GEO_PropBlade_A"));

	RearGunnerMount = CreateDefaultSubobject<USceneComponent>(TEXT("SO_RearGunnerSeat"));
	RearGunnerMount->SetupAttachment(AircraftRoot);
	RearGunnerMount->SetRelativeLocation(FVector(-65.f, -64.f, 72.f));

	RearEyeMount = CreateDefaultSubobject<USceneComponent>(TEXT("SO_RearEye"));
	RearEyeMount->SetupAttachment(AircraftRoot);
	RearEyeMount->SetRelativeLocation(FVector(-65.f, -64.f, 102.f));

	RearWeaponMount = CreateDefaultSubobject<USceneComponent>(TEXT("SO_RearWeaponMount"));
	RearWeaponMount->SetupAttachment(AircraftRoot);
	RearWeaponMount->SetRelativeLocation(FVector(-32.f, -64.f, 60.f));

	PilotProtection = CreateDefaultSubobject<UBoxComponent>(TEXT("PilotProtection"));
	PilotProtection->SetupAttachment(AircraftRoot);
	PilotProtection->SetRelativeLocation(FVector(55.f, 0.f, 92.f));
	PilotProtection->SetBoxExtent(FVector(58.f, 45.f, 62.f));
	PilotProtection->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	PilotProtection->SetCollisionResponseToAllChannels(ECR_Ignore);
	PilotProtection->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);

	CockpitProtection = CreateDefaultSubobject<UBoxComponent>(TEXT("CockpitProtection"));
	CockpitProtection->SetupAttachment(AircraftRoot);
	CockpitProtection->SetRelativeLocation(FVector(8.f, 0.f, 82.f));
	CockpitProtection->SetBoxExtent(FVector(8.f, 58.f, 56.f));
	CockpitProtection->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	CockpitProtection->SetCollisionResponseToAllChannels(ECR_Ignore);
	CockpitProtection->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);

	CurrentPropellerRPM = FMath::Lerp(MinimumFlightRPM, MaximumFlightRPM, EnginePower);
}

void ASkyguardYak52Aircraft::BeginPlay()
{
	Super::BeginPlay();
	if (RearCanopyGlass)
	{
		const FVector AuthoredRelative = RearCanopyGlass->GetRelativeLocation();
		// Authored mesh is the open/stowed pose when bRearCanopyOpen starts true.
		// Closed pose is Travel centimeters forward of the open relative location.
		if (bRearCanopyOpen)
		{
			RearCanopyClosedLocation =
				AuthoredRelative + FVector(RearCanopyTravelCentimeters, 0.f, 0.f);
		}
		else
		{
			RearCanopyClosedLocation = AuthoredRelative;
		}
	}
}

void ASkyguardYak52Aircraft::ConfigureVisual(
	UStaticMeshComponent* Component,
	const TCHAR* AssetPath)
{
	if (!Component)
	{
		return;
	}

	const FString FullPath = FString(L88Root) + AssetPath;
	if (UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, *FullPath))
	{
		Component->SetStaticMesh(Mesh);
	}
}

void ASkyguardYak52Aircraft::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	const float TargetRPM = FMath::Lerp(MinimumFlightRPM, MaximumFlightRPM, EnginePower);
	CurrentPropellerRPM = FMath::FInterpTo(CurrentPropellerRPM, TargetRPM, DeltaSeconds, 8.f);
	if (PropellerBlade)
	{
		const float DegreesPerSecond = CurrentPropellerRPM * 6.f;
		PropellerBlade->AddLocalRotation(FRotator(DegreesPerSecond * DeltaSeconds, 0.f, 0.f));
	}

	const FRotator TargetAttitude = GetCommandAttitude();
	const FRotator CurrentAttitude = AircraftRoot->GetRelativeRotation();
	AircraftRoot->SetRelativeRotation(
		FMath::RInterpConstantTo(
			CurrentAttitude,
			TargetAttitude,
			DeltaSeconds,
			PilotResponseDegreesPerSecond));

	const float TargetCanopyAlpha = bRearCanopyOpen ? 1.f : 0.f;
	RearCanopyAlpha = FMath::FInterpTo(RearCanopyAlpha, TargetCanopyAlpha, DeltaSeconds, 4.f);
	if (RearCanopyGlass)
	{
		RearCanopyGlass->SetRelativeLocation(
			RearCanopyClosedLocation + FVector(-RearCanopyTravelCentimeters * RearCanopyAlpha, 0.f, 0.f));
	}
}

void ASkyguardYak52Aircraft::SetEnginePower(const float NormalizedPower)
{
	EnginePower = FMath::Clamp(NormalizedPower, 0.f, 1.f);
}

void ASkyguardYak52Aircraft::IssuePilotCommand(const ESkyguardPilotCommand Command)
{
	CurrentPilotCommand = Command;
}

void ASkyguardYak52Aircraft::SetRearCanopyOpen(const bool bOpen)
{
	bRearCanopyOpen = bOpen;
}

FRotator ASkyguardYak52Aircraft::GetCommandAttitude() const
{
	switch (CurrentPilotCommand)
	{
	case ESkyguardPilotCommand::OrbitLeft:
		return FRotator(-2.f, -8.f, -24.f);
	case ESkyguardPilotCommand::OrbitRight:
		return FRotator(-2.f, 8.f, 24.f);
	case ESkyguardPilotCommand::Break:
		return FRotator(12.f, 0.f, 32.f);
	case ESkyguardPilotCommand::Extend:
		return FRotator(-6.f, 0.f, 0.f);
	case ESkyguardPilotCommand::Pursuit:
	default:
		return FRotator::ZeroRotator;
	}
}
