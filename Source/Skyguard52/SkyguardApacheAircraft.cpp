#include "SkyguardApacheAircraft.h"
#include "SkyguardPilotVoice.h"
#include "SkyguardRuntimeMeshCatalog.h"

#include "Components/BoxComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/InputSettings.h"
#include "GameFramework/PlayerController.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

ASkyguardApacheAircraft::ASkyguardApacheAircraft()
{
	PrimaryActorTick.bCanEverTick = true;

	AircraftRoot = CreateDefaultSubobject<USceneComponent>(TEXT("AircraftRoot"));
	SetRootComponent(AircraftRoot);

	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(
		TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cylinder(
		TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(
		TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> ShapeMat(
		TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));

	UStaticMesh* CubeMesh = Cube.Succeeded() ? Cube.Object : nullptr;
	UStaticMesh* CylinderMesh = Cylinder.Succeeded() ? Cylinder.Object : nullptr;
	UStaticMesh* SphereMesh = Sphere.Succeeded() ? Sphere.Object : nullptr;
	if (ShapeMat.Succeeded())
	{
		ShapeMaterial = ShapeMat.Object;
	}

	const FLinearColor Green(0.07f, 0.09f, 0.06f);
	const FLinearColor DarkGreen(0.05f, 0.06f, 0.045f);
	const FLinearColor CanopyTint(0.14f, 0.16f, 0.20f);
	const FLinearColor RotorTint(0.06f, 0.06f, 0.06f);
	const FLinearColor Metal(0.12f, 0.12f, 0.11f);
	const FLinearColor Store(0.14f, 0.14f, 0.13f);

	SilhouetteMesh = CreateVisual(TEXT("SilhouetteMesh"), AircraftRoot);
	SilhouetteMesh->SetCastShadow(true);
	SilhouetteMesh->SetVisibility(false);

	// Entirely behind the CPG. A cube 50cm ahead reads as a gold wall.
	Fuselage = CreateVisual(TEXT("Fuselage"), AircraftRoot);
	BindPrimitive(
		Fuselage, CubeMesh,
		FVector(-280.f, 0.f, 70.f), FRotator::ZeroRotator,
		FVector(4.2f, 1.05f, 0.9f), Green);

	Nose = CreateVisual(TEXT("Nose"), AircraftRoot);
	BindPrimitive(
		Nose, CubeMesh,
		FVector(360.f, 0.f, 18.f), FRotator::ZeroRotator,
		FVector(1.4f, 0.5f, 0.28f), DarkGreen);

	Canopy = CreateVisual(TEXT("Canopy"), AircraftRoot);
	BindPrimitive(
		Canopy, CubeMesh,
		FVector(168.f, 0.f, 22.f), FRotator::ZeroRotator,
		FVector(1.6f, 0.9f, 0.12f), CanopyTint);
	Canopy->SetVisibility(false);

	TailBoom = CreateVisual(TEXT("TailBoom"), AircraftRoot);
	BindPrimitive(
		TailBoom, CubeMesh,
		FVector(-420.f, 0.f, 92.f), FRotator::ZeroRotator,
		FVector(5.6f, 0.32f, 0.32f), Green);

	VerticalTail = CreateVisual(TEXT("VerticalTail"), AircraftRoot);
	BindPrimitive(
		VerticalTail, CubeMesh,
		FVector(-690.f, 0.f, 168.f), FRotator::ZeroRotator,
		FVector(0.55f, 0.16f, 1.7f), DarkGreen);

	StubWingLeft = CreateVisual(TEXT("StubWingLeft"), AircraftRoot);
	BindPrimitive(
		StubWingLeft, CubeMesh,
		FVector(40.f, -168.f, 70.f), FRotator::ZeroRotator,
		FVector(0.9f, 2.6f, 0.12f), DarkGreen);

	StubWingRight = CreateVisual(TEXT("StubWingRight"), AircraftRoot);
	BindPrimitive(
		StubWingRight, CubeMesh,
		FVector(40.f, 168.f, 70.f), FRotator::ZeroRotator,
		FVector(0.9f, 2.6f, 0.12f), DarkGreen);

	RotorMast = CreateVisual(TEXT("RotorMast"), AircraftRoot);
	BindPrimitive(
		RotorMast, CylinderMesh,
		FVector(30.f, 0.f, 198.f), FRotator::ZeroRotator,
		FVector(0.22f, 0.22f, 1.15f), Metal);

	MainRotor = CreateVisual(TEXT("MainRotor"), AircraftRoot);
	BindPrimitive(
		MainRotor, CubeMesh,
		FVector(30.f, 0.f, 258.f), FRotator::ZeroRotator,
		FVector(14.5f, 0.22f, 0.06f), RotorTint);

	MainRotorCross = CreateVisual(TEXT("MainRotorCross"), AircraftRoot);
	BindPrimitive(
		MainRotorCross, CubeMesh,
		FVector(30.f, 0.f, 258.f), FRotator(0.f, 90.f, 0.f),
		FVector(14.5f, 0.22f, 0.06f), RotorTint);

	TailRotor = CreateVisual(TEXT("TailRotor"), AircraftRoot);
	BindPrimitive(
		TailRotor, CylinderMesh,
		FVector(-700.f, 42.f, 178.f), FRotator(0.f, 0.f, 90.f),
		FVector(1.5f, 1.5f, 0.05f), RotorTint);

	ChinTurret = CreateDefaultSubobject<USceneComponent>(TEXT("ChinTurret"));
	ChinTurret->SetupAttachment(AircraftRoot);
	ChinTurret->SetRelativeLocation(FVector(270.f, 0.f, -48.f));

	ChinHousing = CreateVisual(TEXT("ChinHousing"), ChinTurret);
	BindPrimitive(
		ChinHousing, CubeMesh,
		FVector::ZeroVector, FRotator::ZeroRotator,
		FVector(0.42f, 0.28f, 0.38f), Metal);

	ChinBarrel = CreateVisual(TEXT("ChinBarrel"), ChinTurret);
	BindPrimitive(
		ChinBarrel, CylinderMesh,
		FVector(72.f, 0.f, -8.f), FRotator(8.f, 0.f, 90.f),
		FVector(0.10f, 0.10f, 1.25f), Metal);

	// Public side-profile: TADS under the nose, M230 hanging below.
	SensorTurret = CreateDefaultSubobject<USceneComponent>(TEXT("SO_GunnerSensorTurret"));
	SensorTurret->SetupAttachment(AircraftRoot);
	SensorTurret->SetRelativeLocation(FVector(236.f, 0.f, 28.f));

	SensorBall = CreateVisual(TEXT("SensorBall"), SensorTurret);
	BindPrimitive(
		SensorBall, SphereMesh,
		FVector::ZeroVector, FRotator::ZeroRotator,
		FVector(0.42f, 0.46f, 0.40f), Metal);

	NightVisionTurret = CreateVisual(TEXT("NightVisionTurret"), SensorTurret);
	BindPrimitive(
		NightVisionTurret, CylinderMesh,
		FVector(32.f, 0.f, 0.f), FRotator(0.f, 0.f, 90.f),
		FVector(0.16f, 0.16f, 0.38f), Metal);

	PilotCanopy = CreateVisual(TEXT("PilotCanopy"), AircraftRoot);
	BindPrimitive(
		PilotCanopy, CubeMesh,
		FVector(48.f, 0.f, 128.f), FRotator::ZeroRotator,
		FVector(1.1f, 0.85f, 0.55f), CanopyTint);

	EngineLeft = CreateVisual(TEXT("EngineLeft"), AircraftRoot);
	BindPrimitive(
		EngineLeft, CylinderMesh,
		FVector(-90.f, -82.f, 108.f), FRotator(0.f, 0.f, 90.f),
		FVector(0.42f, 0.42f, 1.55f), DarkGreen);

	EngineRight = CreateVisual(TEXT("EngineRight"), AircraftRoot);
	BindPrimitive(
		EngineRight, CylinderMesh,
		FVector(-90.f, 82.f, 108.f), FRotator(0.f, 0.f, 90.f),
		FVector(0.42f, 0.42f, 1.55f), DarkGreen);

	RadarDome = CreateVisual(TEXT("RadarDome"), AircraftRoot);
	BindPrimitive(
		RadarDome, SphereMesh,
		FVector(30.f, 0.f, 292.f), FRotator::ZeroRotator,
		FVector(0.42f, 0.42f, 0.32f), Metal);

	HorizontalTail = CreateVisual(TEXT("HorizontalTail"), AircraftRoot);
	BindPrimitive(
		HorizontalTail, CubeMesh,
		FVector(-690.f, 0.f, 118.f), FRotator::ZeroRotator,
		FVector(0.45f, 2.4f, 0.10f), DarkGreen);

	GearNose = CreateVisual(TEXT("GearNose"), AircraftRoot);
	BindPrimitive(
		GearNose, CylinderMesh,
		FVector(200.f, 0.f, -40.f), FRotator(18.f, 0.f, 0.f),
		FVector(0.16f, 0.16f, 0.70f), Metal);

	GearLeft = CreateVisual(TEXT("GearLeft"), AircraftRoot);
	BindPrimitive(
		GearLeft, CylinderMesh,
		FVector(-20.f, -70.f, -22.f), FRotator::ZeroRotator,
		FVector(0.14f, 0.14f, 0.55f), Metal);

	GearRight = CreateVisual(TEXT("GearRight"), AircraftRoot);
	BindPrimitive(
		GearRight, CylinderMesh,
		FVector(-20.f, 70.f, -22.f), FRotator::ZeroRotator,
		FVector(0.14f, 0.14f, 0.55f), Metal);

	PylonLeft = CreateVisual(TEXT("PylonLeft"), AircraftRoot);
	BindPrimitive(
		PylonLeft, CubeMesh,
		FVector(40.f, -168.f, 42.f), FRotator::ZeroRotator,
		FVector(0.18f, 0.10f, 0.55f), DarkGreen);

	PylonRight = CreateVisual(TEXT("PylonRight"), AircraftRoot);
	BindPrimitive(
		PylonRight, CubeMesh,
		FVector(40.f, 168.f, 42.f), FRotator::ZeroRotator,
		FVector(0.18f, 0.10f, 0.55f), DarkGreen);

	HydraLeft = CreateVisual(TEXT("HydraLeft"), AircraftRoot);
	BindPrimitive(
		HydraLeft, CylinderMesh,
		FVector(40.f, -200.f, 28.f), FRotator(0.f, 0.f, 90.f),
		FVector(0.28f, 0.28f, 1.15f), Store);

	HydraRight = CreateVisual(TEXT("HydraRight"), AircraftRoot);
	BindPrimitive(
		HydraRight, CylinderMesh,
		FVector(40.f, 200.f, 28.f), FRotator(0.f, 0.f, 90.f),
		FVector(0.28f, 0.28f, 1.15f), Store);

	HellfireLeft = CreateVisual(TEXT("HellfireLeft"), AircraftRoot);
	BindPrimitive(
		HellfireLeft, CubeMesh,
		FVector(36.f, -128.f, 32.f), FRotator::ZeroRotator,
		FVector(1.05f, 0.22f, 0.16f), Store);

	HellfireRight = CreateVisual(TEXT("HellfireRight"), AircraftRoot);
	BindPrimitive(
		HellfireRight, CubeMesh,
		FVector(36.f, 128.f, 32.f), FRotator::ZeroRotator,
		FVector(1.05f, 0.22f, 0.16f), Store);

	GunnerMount = CreateDefaultSubobject<USceneComponent>(TEXT("SO_FrontGunnerSeat"));
	GunnerMount->SetupAttachment(AircraftRoot);
	GunnerMount->SetRelativeLocation(FVector(168.f, 0.f, 118.f));

	PilotMount = CreateDefaultSubobject<USceneComponent>(TEXT("SO_RearPilotSeat"));
	PilotMount->SetupAttachment(AircraftRoot);
	PilotMount->SetRelativeLocation(FVector(48.f, 0.f, 118.f));

	EyeMount = CreateDefaultSubobject<USceneComponent>(TEXT("SO_FrontEye"));
	EyeMount->SetupAttachment(AircraftRoot);
	EyeMount->SetRelativeLocation(FVector(176.f, 0.f, 146.f));

	WeaponMount = CreateDefaultSubobject<USceneComponent>(TEXT("SO_ChinWeapon"));
	WeaponMount->SetupAttachment(ChinTurret);
	WeaponMount->SetRelativeLocation(FVector(110.f, 0.f, 0.f));

	HullCollider = CreateDefaultSubobject<UBoxComponent>(TEXT("HullCollider"));
	HullCollider->SetupAttachment(AircraftRoot);
	HullCollider->SetRelativeLocation(FVector(0.f, 0.f, 90.f));
	HullCollider->SetBoxExtent(FVector(420.f, 180.f, 110.f));
	HullCollider->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	HullCollider->SetCollisionObjectType(ECC_WorldStatic);
	HullCollider->SetCollisionResponseToAllChannels(ECR_Ignore);
	HullCollider->SetCollisionResponseToChannel(ECC_WorldDynamic, ECR_Block);
	HullCollider->SetGenerateOverlapEvents(false);
	HullCollider->SetCanEverAffectNavigation(false);

	CurrentIntegrity = MaxIntegrity;
	CurrentRotorRPM = FMath::Lerp(210.f, 310.f, RotorPower);
}

void ASkyguardApacheAircraft::BeginPlay()
{
	Super::BeginPlay();
	CurrentIntegrity = MaxIntegrity;
	HoverBaseLocation = GetActorLocation();
	OrbitCenter = HoverBaseLocation + GetActorForwardVector() * OrbitRadius;
	const FVector ToSelf = HoverBaseLocation - OrbitCenter;
	OrbitAngleDegrees = FMath::RadiansToDegrees(FMath::Atan2(ToSelf.Y, ToSelf.X));
	FaceTargetLocation = OrbitCenter;
	AirYawDegrees = GetActorRotation().Yaw;
	AirPitchDegrees = GetActorRotation().Pitch;
	AirRollDegrees = GetActorRotation().Roll;
	ApplyPendingTints();
	BindSilhouetteMesh();
	OpenCockpitView();
}

void ASkyguardApacheAircraft::OpenCockpitView()
{
	// Keep the CPG looking at the world, not the inside of a hull cube.
	if (Canopy)
	{
		Canopy->SetCastShadow(false);
	}
}

void ASkyguardApacheAircraft::ApplyPendingTints()
{
	for (const TPair<TObjectPtr<UStaticMeshComponent>, FLinearColor>& Pair : PendingTint)
	{
		Tint(Pair.Key, Pair.Value);
	}
}

void ASkyguardApacheAircraft::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	const float TargetRPM = FMath::Lerp(210.f, 310.f, RotorPower);
	CurrentRotorRPM = FMath::FInterpTo(CurrentRotorRPM, TargetRPM, DeltaSeconds, 6.f);
	if (MainRotor)
	{
		MainRotor->AddLocalRotation(
			FRotator(0.f, CurrentRotorRPM * 6.f * DeltaSeconds, 0.f));
	}
	if (MainRotorCross)
	{
		MainRotorCross->AddLocalRotation(
			FRotator(0.f, CurrentRotorRPM * 6.f * DeltaSeconds, 0.f));
	}
	if (TailRotor)
	{
		TailRotor->AddLocalRotation(
			FRotator(0.f, CurrentRotorRPM * 11.f * DeltaSeconds, 0.f));
	}

	HoverSeconds += DeltaSeconds;
	PollPilotCommandInput();
	UpdatePilotMotion(DeltaSeconds);
	const float Bob = FMath::Sin(HoverSeconds * 1.35f) * HoverBobCentimeters;
	SetActorLocation(HoverBaseLocation + FVector(0.f, 0.f, Bob));
}

void ASkyguardApacheAircraft::SetDirectFlightInput(
	const float Collective,
	const float Yaw,
	const float CyclicPitch,
	const float CyclicRoll)
{
	CollectiveInput = FMath::Clamp(Collective, -1.f, 1.f);
	YawInput = FMath::Clamp(Yaw, -1.f, 1.f);
	CyclicPitchInput = FMath::Clamp(CyclicPitch, -1.f, 1.f);
	CyclicRollInput = FMath::Clamp(CyclicRoll, -1.f, 1.f);
	// Keep W/S/A/D when pressed. Idle stick leaves engagement geometry to the pilot.
	bHasDirectFlight =
		!FMath::IsNearlyZero(CollectiveInput, 0.02f) ||
		!FMath::IsNearlyZero(YawInput, 0.02f) ||
		!FMath::IsNearlyZero(CyclicPitchInput, 0.02f) ||
		!FMath::IsNearlyZero(CyclicRollInput, 0.02f);
}

void ASkyguardApacheAircraft::UpdateDirectFlight(const float DeltaSeconds)
{
	AirYawDegrees += YawInput * 78.f * DeltaSeconds;
	const float TargetPitch = -CyclicPitchInput * 16.f;
	const float TargetRoll = CyclicRollInput * 22.f;
	AirPitchDegrees = FMath::FInterpTo(AirPitchDegrees, TargetPitch, DeltaSeconds, 5.f);
	AirRollDegrees = FMath::FInterpTo(AirRollDegrees, TargetRoll, DeltaSeconds, 5.f);

	if (CollectiveInput > 0.f)
	{
		ForwardSpeed += CollectiveInput * 2200.f * DeltaSeconds;
		HoverBaseLocation.Z += CollectiveInput * 900.f * DeltaSeconds;
	}
	else if (CollectiveInput < 0.f)
	{
		ForwardSpeed += CollectiveInput * 2600.f * DeltaSeconds;
		HoverBaseLocation.Z += CollectiveInput * 820.f * DeltaSeconds;
	}
	else
	{
		ForwardSpeed = FMath::FInterpTo(ForwardSpeed, 700.f, DeltaSeconds, 0.35f);
	}
	ForwardSpeed = FMath::Clamp(ForwardSpeed, 0.f, 3800.f);
	HoverBaseLocation.Z = FMath::Clamp(HoverBaseLocation.Z, 280.f, 14000.f);

	const FRotator Attitude(AirPitchDegrees, AirYawDegrees, AirRollDegrees);
	SetActorRotation(FMath::RInterpTo(GetActorRotation(), Attitude, DeltaSeconds, 6.f));

	const FVector NoseForward = Attitude.Vector();
	FVector Travel = NoseForward;
	Travel.Z *= 0.25f;
	HoverBaseLocation += Travel * ForwardSpeed * DeltaSeconds;
	HoverBaseLocation += GetActorRightVector() * (AirRollDegrees / 22.f) * ForwardSpeed * 0.35f * DeltaSeconds;
	RotorPower = FMath::Clamp(0.62f + ForwardSpeed / 5000.f + FMath::Max(0.f, CollectiveInput) * 0.2f, 0.45f, 1.f);
}

void ASkyguardApacheAircraft::UpdatePilotMotion(const float DeltaSeconds)
{
	if (bHasDirectFlight)
	{
		UpdateDirectFlight(DeltaSeconds);
		bHasDirectFlight = false;
		return;
	}

	const float Horizontal = 1700.f * DeltaSeconds;
	const float Vertical = 720.f * DeltaSeconds;
	FVector Forward = GetActorForwardVector();
	Forward.Z = 0.f;
	if (!Forward.Normalize())
	{
		Forward = FVector::ForwardVector;
	}
	FVector DesiredFacing = Forward;

	switch (CurrentPilotCommand)
	{
	case ESkyguardPilotCommand::OrbitLeft:
		OrbitAngleDegrees -= 16.f * DeltaSeconds;
		HoverBaseLocation = OrbitCenter +
			FRotator(0.f, OrbitAngleDegrees, 0.f).RotateVector(
				FVector(OrbitRadius, 0.f, 0.f));
		HoverBaseLocation.Z = FMath::Max(HoverBaseLocation.Z, 420.f);
		DesiredFacing = (OrbitCenter - HoverBaseLocation).GetSafeNormal();
		break;
	case ESkyguardPilotCommand::OrbitRight:
		OrbitAngleDegrees += 16.f * DeltaSeconds;
		HoverBaseLocation = OrbitCenter +
			FRotator(0.f, OrbitAngleDegrees, 0.f).RotateVector(
				FVector(OrbitRadius, 0.f, 0.f));
		HoverBaseLocation.Z = FMath::Max(HoverBaseLocation.Z, 420.f);
		DesiredFacing = (OrbitCenter - HoverBaseLocation).GetSafeNormal();
		break;
	case ESkyguardPilotCommand::AttackRun:
		HoverBaseLocation += Forward * Horizontal * 1.25f;
		DesiredFacing = Forward;
		break;
	case ESkyguardPilotCommand::Break:
		HoverBaseLocation -= Forward * Horizontal;
		HoverBaseLocation.Z += Vertical * 0.65f;
		break;
	case ESkyguardPilotCommand::Extend:
		HoverBaseLocation -= Forward * Horizontal * 0.7f;
		OrbitRadius = FMath::Min(OrbitRadius + Horizontal, 6000.f);
		break;
	case ESkyguardPilotCommand::Hold:
		break;
	case ESkyguardPilotCommand::Climb:
		HoverBaseLocation.Z += Vertical;
		break;
	case ESkyguardPilotCommand::Descend:
		HoverBaseLocation.Z = FMath::Max(280.f, HoverBaseLocation.Z - Vertical);
		break;
	case ESkyguardPilotCommand::FaceTarget:
	{
		const FVector ToFace = FaceTargetLocation - HoverBaseLocation;
		if (!ToFace.IsNearlyZero())
		{
			DesiredFacing = ToFace.GetSafeNormal();
		}
		break;
	}
	case ESkyguardPilotCommand::Pursuit:
	default:
		HoverBaseLocation += Forward * Horizontal * 0.22f;
		break;
	}

	FRotator TargetRotation = DesiredFacing.Rotation() + GetCommandAttitude();
	TargetRotation.Pitch = FMath::Clamp(TargetRotation.Pitch, -18.f, 12.f);
	SetActorRotation(FMath::RInterpTo(
		GetActorRotation(), TargetRotation, DeltaSeconds, 1.8f));
}

UStaticMeshComponent* ASkyguardApacheAircraft::CreateVisual(
	const TCHAR* Name,
	USceneComponent* Parent)
{
	UStaticMeshComponent* Component =
		CreateDefaultSubobject<UStaticMeshComponent>(Name);
	Component->SetupAttachment(Parent);
	Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Component->SetGenerateOverlapEvents(false);
	Component->SetCanEverAffectNavigation(false);
	Component->SetCastShadow(true);
	return Component;
}

void ASkyguardApacheAircraft::BindPrimitive(
	UStaticMeshComponent* Component,
	UStaticMesh* Mesh,
	const FVector& Location,
	const FRotator& Rotation,
	const FVector& Scale,
	const FLinearColor& Color)
{
	if (!Component)
	{
		return;
	}
	if (Mesh)
	{
		Component->SetStaticMesh(Mesh);
	}
	if (ShapeMaterial)
	{
		Component->SetMaterial(0, ShapeMaterial);
	}
	Component->SetRelativeLocation(Location);
	Component->SetRelativeRotation(Rotation);
	Component->SetRelativeScale3D(Scale);
	PendingTint.Add(Component, Color);
}

void ASkyguardApacheAircraft::Tint(
	UStaticMeshComponent* Component,
	const FLinearColor& Color) const
{
	if (!Component)
	{
		return;
	}
	UMaterialInterface* Base = ShapeMaterial
		? ShapeMaterial.Get()
		: Component->GetMaterial(0);
	if (!Base)
	{
		return;
	}
	UMaterialInstanceDynamic* Mid = UMaterialInstanceDynamic::Create(Base, Component);
	if (!Mid)
	{
		return;
	}
	Component->SetMaterial(0, Mid);
	const FLinearColor Lit(Color.R, Color.G, Color.B, 1.f);
	Mid->SetVectorParameterValue(TEXT("Color"), Lit);
	Mid->SetVectorParameterValue(TEXT("BaseColor"), Lit);
}

FVector ASkyguardApacheAircraft::GetChinMuzzleLocation() const
{
	if (WeaponMount)
	{
		return WeaponMount->GetComponentLocation();
	}
	if (ChinTurret)
	{
		return ChinTurret->GetComponentLocation() + GetActorForwardVector() * 110.f;
	}
	return GetActorLocation();
}

void ASkyguardApacheAircraft::AimChinTurret(const FRotator& WorldAim)
{
	if (!ChinTurret)
	{
		return;
	}
	const FRotator Local = (WorldAim - GetActorRotation()).GetNormalized();
	ChinTurret->SetRelativeRotation(FRotator(
		FMath::Clamp(Local.Pitch, -70.f, 12.f),
		FMath::Clamp(Local.Yaw, -110.f, 110.f),
		0.f));
}

void ASkyguardApacheAircraft::SetRotorPower(const float NormalizedPower)
{
	RotorPower = FMath::Clamp(NormalizedPower, 0.f, 1.f);
}

void ASkyguardApacheAircraft::IssuePilotCommand(const ESkyguardPilotCommand Command)
{
	const bool bChanged = Command != CurrentPilotCommand;
	CurrentPilotCommand = Command;
	if (Command == ESkyguardPilotCommand::OrbitLeft ||
		Command == ESkyguardPilotCommand::OrbitRight)
	{
		const FVector ToSelf = HoverBaseLocation - OrbitCenter;
		if (ToSelf.SizeSquared2D() > 10000.f)
		{
			OrbitRadius = FMath::Clamp(ToSelf.Size2D(), 900.f, 6000.f);
			OrbitAngleDegrees =
				FMath::RadiansToDegrees(FMath::Atan2(ToSelf.Y, ToSelf.X));
		}
	}
	if (bChanged)
	{
		SkyguardPilotVoice::ConfirmCommand(this, Command);
		++PilotConfirmationsIssued;
	}
}

void ASkyguardApacheAircraft::SetOrbitFocus(const FVector& WorldLocation)
{
	OrbitCenter = WorldLocation;
	const FVector ToSelf = HoverBaseLocation - OrbitCenter;
	OrbitRadius = FMath::Clamp(ToSelf.Size2D(), 900.f, 6000.f);
	OrbitAngleDegrees = FMath::RadiansToDegrees(FMath::Atan2(ToSelf.Y, ToSelf.X));
}

void ASkyguardApacheAircraft::FaceWorldLocation(const FVector& WorldLocation)
{
	FaceTargetLocation = WorldLocation;
	IssuePilotCommand(ESkyguardPilotCommand::FaceTarget);
}

bool ASkyguardApacheAircraft::IsActionJustPressed(const FName ActionName) const
{
	const UWorld* World = GetWorld();
	if (!World)
	{
		return false;
	}
	const APlayerController* PC = World->GetFirstPlayerController();
	const UInputSettings* Settings = GetDefault<UInputSettings>();
	if (!PC || !Settings)
	{
		return false;
	}
	TArray<FInputActionKeyMapping> Mappings;
	Settings->GetActionMappingByName(ActionName, Mappings);
	for (const FInputActionKeyMapping& Mapping : Mappings)
	{
		if (PC->WasInputKeyJustPressed(Mapping.Key))
		{
			return true;
		}
	}
	return false;
}

void ASkyguardApacheAircraft::PollPilotCommandInput()
{
	if (IsActionJustPressed(TEXT("PilotOrbitLeft")))
	{
		IssuePilotCommand(ESkyguardPilotCommand::OrbitLeft);
	}
	else if (IsActionJustPressed(TEXT("PilotOrbitRight")))
	{
		IssuePilotCommand(ESkyguardPilotCommand::OrbitRight);
	}
	else if (IsActionJustPressed(TEXT("PilotHold")))
	{
		IssuePilotCommand(ESkyguardPilotCommand::Hold);
	}
	else if (IsActionJustPressed(TEXT("PilotBreak")))
	{
		IssuePilotCommand(ESkyguardPilotCommand::Break);
	}
	else if (IsActionJustPressed(TEXT("PilotAttackRun")))
	{
		IssuePilotCommand(ESkyguardPilotCommand::AttackRun);
	}
}

void ASkyguardApacheAircraft::SetSensorView(const bool bInSensor)
{
	bSensorView = bInSensor;
}

void ASkyguardApacheAircraft::BindSilhouetteMesh()
{
	if (!SilhouetteMesh)
	{
		return;
	}
	if (!SilhouetteMesh->GetStaticMesh())
	{
		if (UStaticMesh* Mesh =
			USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(TEXT("Apache.Airframe")))
		{
			SilhouetteMesh->SetStaticMesh(Mesh);
		}
	}
	if (!SilhouetteMesh->GetStaticMesh())
	{
		return;
	}
	SilhouetteMesh->SetRelativeLocation(FVector::ZeroVector);
	SilhouetteMesh->SetRelativeRotation(FRotator::ZeroRotator);
	SilhouetteMesh->SetRelativeScale3D(FVector(1.f));
	SilhouetteMesh->SetVisibility(true);
	SilhouetteMesh->SetHiddenInGame(false);
	SetProxyKitHidden(true);
}

void ASkyguardApacheAircraft::SetProxyKitHidden(const bool bHideKit)
{
	auto Hide = [bHideKit](UStaticMeshComponent* Part)
	{
		if (Part)
		{
			Part->SetVisibility(!bHideKit);
			Part->SetHiddenInGame(bHideKit);
		}
	};
	Hide(Fuselage);
	Hide(Nose);
	Hide(Canopy);
	Hide(TailBoom);
	Hide(VerticalTail);
	Hide(StubWingLeft);
	Hide(StubWingRight);
	Hide(RotorMast);
	Hide(MainRotor);
	Hide(MainRotorCross);
	Hide(TailRotor);
	Hide(ChinHousing);
	Hide(ChinBarrel);
	Hide(SensorBall);
	Hide(NightVisionTurret);
	Hide(PilotCanopy);
	Hide(EngineLeft);
	Hide(EngineRight);
	Hide(RadarDome);
	Hide(HorizontalTail);
	Hide(GearNose);
	Hide(GearLeft);
	Hide(GearRight);
	Hide(PylonLeft);
	Hide(PylonRight);
	Hide(HydraLeft);
	Hide(HydraRight);
	Hide(HellfireLeft);
	Hide(HellfireRight);
}

void ASkyguardApacheAircraft::SetFirstPersonInterior(const bool bInterior)
{
	if (SilhouetteMesh && SilhouetteMesh->GetStaticMesh())
	{
		SetProxyKitHidden(true);
		SilhouetteMesh->SetHiddenInGame(false);
		SilhouetteMesh->SetVisibility(true);
		return;
	}
	auto HideNearField = [bInterior](UStaticMeshComponent* Part)
	{
		if (Part)
		{
			Part->SetHiddenInGame(bInterior);
		}
	};
	HideNearField(Fuselage);
	HideNearField(Nose);
	HideNearField(PilotCanopy);
	if (Canopy)
	{
		Canopy->SetHiddenInGame(true);
	}
}

void ASkyguardApacheAircraft::ApplyDamage(const float Amount)
{
	if (Amount <= 0.f)
	{
		return;
	}
	CurrentIntegrity = FMath::Max(0.f, CurrentIntegrity - Amount);
}

float ASkyguardApacheAircraft::GetDamageFraction() const
{
	if (MaxIntegrity <= KINDA_SMALL_NUMBER)
	{
		return 1.f;
	}
	return FMath::Clamp(1.f - (CurrentIntegrity / MaxIntegrity), 0.f, 1.f);
}

FRotator ASkyguardApacheAircraft::GetCommandAttitude() const
{
	switch (CurrentPilotCommand)
	{
	case ESkyguardPilotCommand::OrbitLeft:
		return FRotator(-3.f, -10.f, -14.f);
	case ESkyguardPilotCommand::OrbitRight:
		return FRotator(-3.f, 10.f, 14.f);
	case ESkyguardPilotCommand::Break:
		return FRotator(8.f, 0.f, 18.f);
	case ESkyguardPilotCommand::Extend:
		return FRotator(-8.f, 0.f, 0.f);
	case ESkyguardPilotCommand::Hold:
		return FRotator(-1.f, 0.f, 0.f);
	case ESkyguardPilotCommand::Climb:
		return FRotator(10.f, 0.f, 0.f);
	case ESkyguardPilotCommand::Descend:
		return FRotator(-12.f, 0.f, 0.f);
	case ESkyguardPilotCommand::AttackRun:
		return FRotator(-6.f, 0.f, 0.f);
	case ESkyguardPilotCommand::FaceTarget:
		return FRotator(-2.f, 0.f, 0.f);
	case ESkyguardPilotCommand::Pursuit:
	default:
		return FRotator(-2.f, 0.f, 0.f);
	}
}
