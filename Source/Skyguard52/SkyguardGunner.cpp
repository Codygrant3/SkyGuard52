#include "SkyguardGunner.h"
#include "SkyguardGameUserSettings.h"
#include "SkyguardAudioDirectorComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/InputComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/StaticMesh.h"
#include "DrawDebugHelpers.h"
#include "SkyguardDrone.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardCombatVFX.h"
#include "SkyguardIglaMissile.h"
#include "SkyguardInputCombatPerformanceCapture.h"
#include "SkyguardYak52Aircraft.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "CollisionQueryParams.h"
#include "Components/SceneComponent.h"
#include "Materials/MaterialInterface.h"

ASkyguardGunner::ASkyguardGunner()
{
	PrimaryActorTick.bCanEverTick = true;
	bUseControllerRotationYaw = false;
	bUseControllerRotationPitch = false;
	bUseControllerRotationRoll = false;

	if (UCharacterMovementComponent* Move = GetCharacterMovement())
	{
		Move->DefaultLandMovementMode = MOVE_None;
		Move->GravityScale = 0.f;
		Move->SetMovementMode(MOVE_None);
		Move->bOrientRotationToMovement = false;
	}

	Boom = CreateDefaultSubobject<USpringArmComponent>(TEXT("Boom"));
	Boom->SetupAttachment(RootComponent);
	Boom->TargetArmLength = 0.f;
	Boom->bDoCollisionTest = false;
	Boom->bUsePawnControlRotation = false;
	Boom->SetRelativeLocation(FVector(18.f, 0.f, 68.f));

	GunnerCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("GunnerCamera"));
	GunnerCamera->SetupAttachment(Boom);
	GunnerCamera->SetFieldOfView(HipFov);

	RifleMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RifleMesh"));
	RifleMesh->SetupAttachment(GunnerCamera);
	RifleMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	RifleMesh->SetRelativeLocation(FVector(35.f, 14.f, -12.f));
	RifleMesh->SetRelativeRotation(FRotator(0.f, 0.f, 0.f));
	RifleMesh->SetRelativeScale3D(FVector(0.08f, 0.08f, 1.15f));

	RifleReceiver = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RifleReceiver"));
	RifleReceiver->SetupAttachment(RifleMesh);
	RifleReceiver->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	RifleReceiver->SetRelativeLocation(FVector(0.f, 0.f, -18.f));
	RifleReceiver->SetRelativeScale3D(FVector(1.8f, 3.2f, 0.18f));

	FrontSight = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("FrontSight"));
	FrontSight->SetupAttachment(RifleMesh);
	FrontSight->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	FrontSight->SetRelativeLocation(FVector(0.f, 0.f, 42.f));
	FrontSight->SetRelativeScale3D(FVector(0.35f, 0.12f, 0.08f));

	RearSight = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RearSight"));
	RearSight->SetupAttachment(RifleMesh);
	RearSight->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	RearSight->SetRelativeLocation(FVector(0.f, 0.f, -8.f));
	RearSight->SetRelativeScale3D(FVector(0.55f, 0.2f, 0.1f));

	HandMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("HandMesh"));
	HandMesh->SetupAttachment(RifleMesh);
	HandMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	HandMesh->SetRelativeLocation(FVector(2.f, -2.f, -10.f));
	HandMesh->SetRelativeScale3D(FVector(1.5f, 1.1f, 0.22f));

	ForearmMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ForearmMesh"));
	ForearmMesh->SetupAttachment(HandMesh);
	ForearmMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	ForearmMesh->SetRelativeLocation(FVector(-8.f, -18.f, -6.f));
	ForearmMesh->SetRelativeRotation(FRotator(70.f, 12.f, 0.f));
	ForearmMesh->SetRelativeScale3D(FVector(0.9f, 0.9f, 2.2f));

	IglaTube = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("IglaTube"));
	IglaTube->SetupAttachment(GunnerCamera);
	IglaTube->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	IglaTube->SetRelativeLocation(FVector(28.f, -22.f, -8.f));
	IglaTube->SetRelativeRotation(FRotator(0.f, 0.f, 90.f));
	IglaTube->SetRelativeScale3D(FVector(0.12f, 0.12f, 1.4f));
	IglaTube->SetVisibility(false);

	IglaMuzzle = CreateDefaultSubobject<USceneComponent>(TEXT("IglaMuzzle"));
	IglaMuzzle->SetupAttachment(GunnerCamera);
	IglaMuzzle->SetRelativeLocation(FVector(105.f, -22.f, -8.f));
	IglaMuzzle->SetRelativeRotation(FRotator::ZeroRotator);
	IglaMissileClass = ASkyguardIglaMissile::StaticClass();

	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cyl(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> WebRifle(TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-fde.rifle-fde"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> WebGlove(TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-glove.rifle-glove"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> WebSleeve(TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-sleeve.rifle-sleeve"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> WebIgla(TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-interceptor/StaticMeshes/compact-launcher-tube.compact-launcher-tube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> HeroRifle(TEXT("/Game/Skyguard/Meshes/Hero/rifle_ads_proxy.rifle_ads_proxy"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> HeroIgla(TEXT("/Game/Skyguard/Meshes/Hero/igla_proxy.igla_proxy"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> HeroRifleAlt(TEXT("/Game/Skyguard/Meshes/Hero/rifle_irons_proxy.rifle_irons_proxy"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> HeroHand(TEXT("/Game/Skyguard/Meshes/Hero/glove_hand_proxy.glove_hand_proxy"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> HeroArm(TEXT("/Game/Skyguard/Meshes/Hero/glove_arm_proxy.glove_arm_proxy"));

	if (WebRifle.Succeeded())
	{
		RifleMesh->SetStaticMesh(WebRifle.Object);
		RifleMesh->SetRelativeScale3D(FVector(0.55f, 0.55f, 0.55f));
		RifleMesh->SetRelativeLocation(FVector(28.f, 10.f, -10.f));
		RifleMesh->SetRelativeRotation(FRotator(0.f, 90.f, 0.f));
	}
	else if (HeroRifle.Succeeded())
	{
		RifleMesh->SetStaticMesh(HeroRifle.Object);
		RifleMesh->SetRelativeScale3D(FVector(30.f, 30.f, 30.f));
	}
	else if (HeroRifleAlt.Succeeded())
	{
		RifleMesh->SetStaticMesh(HeroRifleAlt.Object);
		RifleMesh->SetRelativeScale3D(FVector(28.f, 28.f, 28.f));
	}
	else if (Cyl.Succeeded())
	{
		RifleMesh->SetStaticMesh(Cyl.Object);
	}

	if (WebGlove.Succeeded())
	{
		HandMesh->SetStaticMesh(WebGlove.Object);
		HandMesh->SetRelativeScale3D(FVector(1.f, 1.f, 1.f));
		HandMesh->SetRelativeLocation(FVector(4.f, -6.f, -8.f));
	}
	else if (HeroHand.Succeeded())
	{
		HandMesh->SetStaticMesh(HeroHand.Object);
		HandMesh->SetRelativeScale3D(FVector(12.f, 12.f, 12.f));
	}
	else if (Sphere.Succeeded())
	{
		HandMesh->SetStaticMesh(Sphere.Object);
	}

	if (WebSleeve.Succeeded())
	{
		ForearmMesh->SetStaticMesh(WebSleeve.Object);
		ForearmMesh->SetRelativeScale3D(FVector(1.f, 1.f, 1.f));
		ForearmMesh->SetRelativeLocation(FVector(-6.f, -14.f, -4.f));
		ForearmMesh->SetRelativeRotation(FRotator(40.f, 8.f, 0.f));
	}
	else if (HeroArm.Succeeded())
	{
		ForearmMesh->SetStaticMesh(HeroArm.Object);
		ForearmMesh->SetRelativeScale3D(FVector(10.f, 10.f, 10.f));
	}
	else if (Cyl.Succeeded())
	{
		ForearmMesh->SetStaticMesh(Cyl.Object);
	}

	if (WebIgla.Succeeded())
	{
		IglaTube->SetStaticMesh(WebIgla.Object);
		IglaTube->SetRelativeScale3D(FVector(0.45f, 0.45f, 0.45f));
		IglaTube->SetRelativeRotation(FRotator(0.f, 0.f, 90.f));
	}
	else if (HeroIgla.Succeeded())
	{
		IglaTube->SetStaticMesh(HeroIgla.Object);
		IglaTube->SetRelativeScale3D(FVector(18.f, 18.f, 18.f));
	}
	else if (Cyl.Succeeded())
	{
		IglaTube->SetStaticMesh(Cyl.Object);
	}

	if (Cube.Succeeded())
	{
		// Keep tiny iron-sight markers for ADS reference when using low-detail rifle fallbacks
		RifleReceiver->SetStaticMesh(Cube.Object);
		FrontSight->SetStaticMesh(Cube.Object);
		RearSight->SetStaticMesh(Cube.Object);
		// Hide cube parts when web rifle is present (more realistic silhouette)
		if (WebRifle.Succeeded())
		{
			RifleReceiver->SetVisibility(false);
			FrontSight->SetVisibility(false);
			RearSight->SetVisibility(false);
		}
	}
}

void ASkyguardGunner::BeginPlay()
{
	Super::BeginPlay();
	BindUserSettings();
	for (TActorIterator<ASkyguardYak52Aircraft> It(GetWorld()); It; ++It)
	{
		ASkyguardYak52Aircraft* Aircraft = *It;
		if (Aircraft && Aircraft->GetRearGunnerMount())
		{
			AttachToComponent(
				Aircraft->GetRearGunnerMount(),
				FAttachmentTransformRules::SnapToTargetNotIncludingScale);
			SetActorRelativeLocation(FVector::ZeroVector);
			SetActorRelativeRotation(FRotator::ZeroRotator);
			break;
		}
	}
	ApplyLocalPlayerControlState();
}

void ASkyguardGunner::PossessedBy(AController* NewController)
{
	Super::PossessedBy(NewController);
	ApplyLocalPlayerControlState();
}

void ASkyguardGunner::PawnClientRestart()
{
	Super::PawnClientRestart();
	ApplyLocalPlayerControlState();
}

void ASkyguardGunner::ApplyLocalPlayerControlState()
{
	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (PC->IsLocalController())
		{
			PC->bShowMouseCursor = false;
			PC->SetInputMode(FInputModeGameOnly());
			PC->SetViewTarget(this);
		}
	}
}

void ASkyguardGunner::BindUserSettings()
{
	if (bUserSettingsBound)
	{
		return;
	}
	USkyguardGameUserSettings::OnSettingsApplied.AddUObject(
		this, &ASkyguardGunner::HandleUserSettingsApplied);
	bUserSettingsBound = true;
	if (const USkyguardGameUserSettings* Settings =
		USkyguardGameUserSettings::GetSkyguardGameUserSettings())
	{
		ApplyUserSettings(*Settings);
	}
}

void ASkyguardGunner::UnbindUserSettings()
{
	if (!bUserSettingsBound)
	{
		return;
	}
	USkyguardGameUserSettings::OnSettingsApplied.RemoveAll(this);
	bUserSettingsBound = false;
}

void ASkyguardGunner::HandleUserSettingsApplied(
	const USkyguardGameUserSettings& Settings)
{
	ApplyUserSettings(Settings);
}

void ASkyguardGunner::ApplyUserSettings(const USkyguardGameUserSettings& Settings)
{
	AppliedLookSensitivity = FMath::Clamp(
		Settings.GetMouseSensitivity() * SettingsSensitivityToLookScale,
		0.05f,
		8.f);
	bInvertVerticalLookApplied = Settings.GetInvertVerticalLook();
	AppliedCameraShakeScale = Settings.GetCameraShakeScale();
}

void ASkyguardGunner::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	UnbindUserSettings();
	Super::EndPlay(EndPlayReason);
}


void ASkyguardGunner::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
	PlayerInputComponent->BindAxis(TEXT("Turn"), this, &ASkyguardGunner::InputLookX);
	PlayerInputComponent->BindAxis(TEXT("LookUp"), this, &ASkyguardGunner::InputLookY);
	PlayerInputComponent->BindAction(TEXT("ADS"), IE_Pressed, this, &ASkyguardGunner::InputADSPressed);
	PlayerInputComponent->BindAction(TEXT("ADS"), IE_Released, this, &ASkyguardGunner::InputADSReleased);
	PlayerInputComponent->BindAction(TEXT("Fire"), IE_Pressed, this, &ASkyguardGunner::InputFirePressed);
	PlayerInputComponent->BindAction(TEXT("Fire"), IE_Released, this, &ASkyguardGunner::InputFireReleased);
	PlayerInputComponent->BindAction(TEXT("SwitchWeapon"), IE_Pressed, this, &ASkyguardGunner::InputSwitchWeaponPressed);
	PlayerInputComponent->BindAction(TEXT("LaunchIgla"), IE_Pressed, this, &ASkyguardGunner::InputLaunchIglaPressed);
	// Look is bound only through Turn/LookUp. DefaultInput maps MouseX/MouseY into
	// those axes; binding MouseX/MouseY again double-applies look.
}

void ASkyguardGunner::InputLookX(const float V)
{
	LookX(V);
	if (!bAimInputRecorded && !FMath::IsNearlyZero(V))
	{
		bAimInputRecorded = true;
		USkyguardInputCombatPerformanceCapture::RecordPlayerEvent(
			this, TEXT("aim_input"));
	}
}

void ASkyguardGunner::InputLookY(const float V)
{
	LookY(V);
	if (!bAimInputRecorded && !FMath::IsNearlyZero(V))
	{
		bAimInputRecorded = true;
		USkyguardInputCombatPerformanceCapture::RecordPlayerEvent(
			this, TEXT("aim_input"));
	}
}

void ASkyguardGunner::InputADSPressed()
{
	ADSPressed();
	USkyguardInputCombatPerformanceCapture::RecordPlayerEvent(
		this, TEXT("ads_started"));
}

void ASkyguardGunner::InputADSReleased()
{
	ADSReleased();
	USkyguardInputCombatPerformanceCapture::RecordPlayerEvent(
		this, TEXT("ads_ended"));
}

void ASkyguardGunner::InputFirePressed()
{
	FirePressed();
	bFireHeldFromPlayerInput = true;
	if (bADS)
	{
		USkyguardInputCombatPerformanceCapture::RecordPlayerEvent(
			this, TEXT("ads_left_fire_overlap"));
	}
}

void ASkyguardGunner::InputFireReleased()
{
	bFireHeldFromPlayerInput = false;
	FireReleased();
}

void ASkyguardGunner::InputSwitchWeaponPressed()
{
	SwitchWeaponPressed();
	USkyguardInputCombatPerformanceCapture::RecordPlayerEvent(
		this, TEXT("weapon_switch"));
}

void ASkyguardGunner::InputLaunchIglaPressed()
{
	bIglaLaunchRequestedFromPlayerInput = true;
	LaunchIglaPressed();
	bIglaLaunchRequestedFromPlayerInput = false;
}

void ASkyguardGunner::LookX(float V)
{
	if (FMath::IsNearlyZero(V)) return;
	const float Sens = bADS ? AppliedLookSensitivity * 0.55f : AppliedLookSensitivity;
	Yaw = FMath::Clamp(Yaw + V * Sens * 1.8f, -LookYawLimit, LookYawLimit);
}

void ASkyguardGunner::LookY(float V)
{
	if (FMath::IsNearlyZero(V)) return;
	const float Axis = bInvertVerticalLookApplied ? -V : V;
	const float Sens = bADS ? AppliedLookSensitivity * 0.55f : AppliedLookSensitivity;
	Pitch = FMath::Clamp(Pitch + Axis * Sens * 1.5f, LookPitchMin, LookPitchMax);
}

void ASkyguardGunner::ADSPressed() { bADS = true; }
void ASkyguardGunner::ADSReleased() { bADS = false; }
void ASkyguardGunner::FirePressed() { bFireHeld = true; }
void ASkyguardGunner::FireReleased() { bFireHeld = false; }

void ASkyguardGunner::SwitchWeaponPressed()
{
	bIglaMode = !bIglaMode;
	if (IglaTube) IglaTube->SetVisibility(bIglaMode);
	if (RifleMesh) RifleMesh->SetVisibility(!bIglaMode);
	if (RifleReceiver) RifleReceiver->SetVisibility(false);
	if (FrontSight) FrontSight->SetVisibility(false);
	if (RearSight) RearSight->SetVisibility(false);
	if (HandMesh) HandMesh->SetVisibility(!bIglaMode);
	if (ForearmMesh) ForearmMesh->SetVisibility(!bIglaMode);
	IglaLockProgress = 0.f;
	IglaTarget = nullptr;
}

void ASkyguardGunner::LaunchIglaPressed()
{
	if (!bIglaMode) return;
	if (IglaLockProgress >= 1.f && IglaTarget.IsValid())
	{
		FireIgla();
	}
}

void ASkyguardGunner::UpdateADSVisuals(float DeltaSeconds)
{
	if (!GunnerCamera || !RifleMesh) return;
	const float TargetFov = bADS ? ADSFov : HipFov;
	GunnerCamera->SetFieldOfView(FMath::FInterpTo(GunnerCamera->FieldOfView, TargetFov, DeltaSeconds, 12.f));

	// Iron-sights style ADS: pull weapon to centerline, slightly down from camera
	const FVector HipLoc(28.f, 10.f, -10.f);
	const FVector AdsLoc(18.f, 0.f, -3.0f);
	const FVector TargetLoc = bADS ? AdsLoc : HipLoc;
	RifleMesh->SetRelativeLocation(FMath::VInterpTo(RifleMesh->GetRelativeLocation(), TargetLoc, DeltaSeconds, 14.f));

	const FRotator HipRot(0.f, 90.f, 0.f);
	const FRotator AdsRot(-1.5f, 90.f, 0.f);
	const FRotator TargetRot = bADS ? AdsRot : HipRot;
	RifleMesh->SetRelativeRotation(FMath::RInterpTo(RifleMesh->GetRelativeRotation(), TargetRot, DeltaSeconds, 14.f));
}

void ASkyguardGunner::UpdateIglaLock(float DeltaSeconds)
{
	const bool bWasAcquired = IglaLockProgress >= 1.f && IglaTarget.IsValid();
	if (!bIglaMode || !GunnerCamera)
	{
		IglaLockProgress = 0.f;
		IglaTarget = nullptr;
		bIglaLockPreviouslyAcquired = false;
		return;
	}
	AActor* Candidate = AcquireIglaTarget();
	if (Candidate)
	{
		if (IglaTarget.Get() != Candidate)
		{
			IglaTarget = Candidate;
			IglaLockProgress = 0.f;
			USkyguardAudioDirectorComponent::TriggerWorldEvent(
				this,
				ESkyguardAudioEvent::IglaSeekerSearch,
				Candidate->GetActorLocation());
		}
		IglaLockProgress = FMath::Clamp(
			IglaLockProgress + DeltaSeconds / FMath::Max(IglaLockSeconds, 0.1f),
			0.f,
			1.f);
	}
	else
	{
		IglaTarget = nullptr;
		IglaLockProgress = FMath::Max(0.f, IglaLockProgress - DeltaSeconds * 1.5f);
	}
	const bool bIsAcquired = IglaLockProgress >= 1.f && IglaTarget.IsValid();
	if (bIsAcquired && !bWasAcquired && !bIglaLockPreviouslyAcquired)
	{
		USkyguardAudioDirectorComponent::TriggerWorldEvent(
			this,
			ESkyguardAudioEvent::IglaLock,
			IglaTarget->GetActorLocation());
		USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
			this, TEXT("igla_lock_acquired"));
	}
	bIglaLockPreviouslyAcquired = bIsAcquired;
}


AActor* ASkyguardGunner::AcquireIglaTarget() const
{
	if (!GetWorld() || !GunnerCamera)
	{
		return nullptr;
	}

	const FVector Origin = GunnerCamera->GetComponentLocation();
	const FVector Forward = GunnerCamera->GetForwardVector();
	const float MinimumDot = FMath::Cos(FMath::DegreesToRadians(IglaMaximumLockAngleDegrees));
	AActor* BestTarget = nullptr;
	float BestScore = TNumericLimits<float>::Max();

	for (TActorIterator<ASkyguardBossDroneBase> It(GetWorld()); It; ++It)
	{
		ASkyguardBossDroneBase* Boss = *It;
		if (!Boss || !Boss->IsIglaLockEligible())
		{
			continue;
		}
		const FVector Offset = Boss->GetActorLocation() - Origin;
		const float Distance = Offset.Size();
		if (Distance < IglaMinimumRange || Distance > IglaMaximumRange)
		{
			continue;
		}
		const float Dot = FVector::DotProduct(Forward, Offset / Distance);
		if (Dot < MinimumDot)
		{
			continue;
		}
		FHitResult Occlusion;
		FCollisionQueryParams Query(SCENE_QUERY_STAT(SkyguardIglaOcclusion), true, this);
		const bool bBlocked = GetWorld()->LineTraceSingleByChannel(
			Occlusion,
			Origin,
			Boss->GetActorLocation(),
			ECC_Visibility,
			Query);
		if (bBlocked && Occlusion.GetActor() != Boss)
		{
			continue;
		}
		const float Score = (1.f - Dot) * IglaMaximumRange + Distance * 0.05f;
		if (Score < BestScore)
		{
			BestScore = Score;
			BestTarget = Boss;
		}
	}

	for (TActorIterator<ASkyguardDrone> It(GetWorld()); It; ++It)
	{
		ASkyguardDrone* Drone = *It;
		if (!Drone || !(Drone->IsHeavyTarget() || Drone->MaxHealth >= 80.f))
		{
			continue;
		}
		const FVector Offset = Drone->GetActorLocation() - Origin;
		const float Distance = Offset.Size();
		if (Distance < IglaMinimumRange || Distance > IglaMaximumRange)
		{
			continue;
		}
		const float Dot = FVector::DotProduct(Forward, Offset / Distance);
		if (Dot < MinimumDot)
		{
			continue;
		}
		FHitResult Occlusion;
		FCollisionQueryParams Query(SCENE_QUERY_STAT(SkyguardIglaOcclusion), true, this);
		const bool bBlocked = GetWorld()->LineTraceSingleByChannel(
			Occlusion,
			Origin,
			Drone->GetActorLocation(),
			ECC_Visibility,
			Query);
		if (bBlocked && Occlusion.GetActor() != Drone)
		{
			continue;
		}
		const float Score = (1.f - Dot) * IglaMaximumRange + Distance * 0.05f;
		if (Score < BestScore)
		{
			BestScore = Score;
			BestTarget = Drone;
		}
	}

	return BestTarget;
}

void ASkyguardGunner::FireIgla()
{
	if (!IglaTarget.IsValid() || !GunnerCamera) return;
	AActor* Target = IglaTarget.Get();
	const FVector TargetLocation = Target->GetActorLocation();
	const FVector Dir = (TargetLocation - GunnerCamera->GetComponentLocation()).GetSafeNormal();
	const FVector Muzzle = IglaMuzzle
		? IglaMuzzle->GetComponentLocation()
		: GunnerCamera->GetComponentLocation() + GunnerCamera->GetForwardVector() * 60.f;
	bool bMissileSpawned = false;
	if (IglaMissileClass)
	{
		FActorSpawnParameters SpawnParameters;
		SpawnParameters.Owner = this;
		SpawnParameters.Instigator = this;
		if (ASkyguardIglaMissile* Missile = GetWorld()->SpawnActor<ASkyguardIglaMissile>(
			IglaMissileClass,
			Muzzle,
			Dir.Rotation(),
			SpawnParameters))
		{
			Missile->InitializeMissile(Target, IglaDamage, Dir);
			bMissileSpawned = true;
		}
		USkyguardCombatVFX::SpawnIglaLaunch(GetWorld(), Muzzle, Dir);
	}
	if (bMissileSpawned &&
		(bIglaLaunchRequestedFromPlayerInput || bFireHeldFromPlayerInput))
	{
		USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
			this, TEXT("igla_launch"));
	}
	if (bMissileSpawned)
	{
		USkyguardAudioDirectorComponent::TriggerWorldEvent(
			this,
			ESkyguardAudioEvent::IglaLaunch,
			Muzzle);
	}
	IglaLockProgress = 0.f;
	IglaTarget = nullptr;
	bIglaLockPreviouslyAcquired = false;
}

void ASkyguardGunner::FireShot()
{
	if (!GunnerCamera) return;
	if (bIglaMode)
	{
		if (IglaLockProgress >= 1.f && IglaTarget.IsValid())
		{
			FireIgla();
		}
		return;
	}
	// The rear cockpit is open, but the forward canopy and pilot remain a hard
	// no-fire sector. The rifle can engage only once the gunner has moved the
	// weapon clear of the aircraft centerline.
	if (!IsRifleDirectionOutsidePilotSafetyArc())
	{
		return;
	}
	if (bFireHeldFromPlayerInput)
	{
		USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
			this, TEXT("rifle_shot"));
	}
	const FVector Start = GunnerCamera->GetComponentLocation();
	const FVector Dir = GunnerCamera->GetForwardVector();
	const FVector End = Start + Dir * TraceRange;

	FHitResult Hit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(SkyguardRifle), true, this);
	const bool bHit = GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params);
	const FVector Muzzle = RifleMesh
		? (RifleMesh->GetComponentLocation() + RifleMesh->GetForwardVector() * 55.f + RifleMesh->GetUpVector() * 8.f)
		: Start;
	USkyguardAudioDirectorComponent::TriggerWorldEvent(
		this,
		ESkyguardAudioEvent::RifleShot,
		Muzzle);
	USkyguardAudioDirectorComponent::TriggerWorldEvent(
		this,
		ESkyguardAudioEvent::RifleMechanical,
		Muzzle);

	USkyguardCombatVFX::SpawnMuzzleFlash(GetWorld(), Muzzle, Dir);
	USkyguardCombatVFX::SpawnTracer(GetWorld(), Muzzle, bHit ? Hit.ImpactPoint : End);
	USkyguardCombatVFX::SpawnGunSmoke(GetWorld(), Muzzle - Dir * 8.f, Dir);

	if (bHit)
	{
		if (ASkyguardBossDroneBase* Boss = Cast<ASkyguardBossDroneBase>(Hit.GetActor()))
		{
			Boss->ApplyWeaponHit(
				Hit.GetComponent(),
				ESkyguardBossWeapon::Rifle,
				BaseDamage,
				Hit.ImpactPoint,
				Dir);
		}
		else if (ASkyguardDrone* Drone = Cast<ASkyguardDrone>(Hit.GetActor()))
		{
			Drone->ApplyBallisticHit(BaseDamage, Hit.ImpactPoint, Dir);
		}
		USkyguardCombatVFX::SpawnHitSparks(GetWorld(), Hit.ImpactPoint, Hit.ImpactNormal);
	}
	Recoil = RecoilPitch;
	Pitch = FMath::Clamp(Pitch + RecoilPitch * 0.35f, LookPitchMin, LookPitchMax);
}

bool ASkyguardGunner::IsRifleDirectionOutsidePilotSafetyArc() const
{
	return FMath::Abs(Yaw) >= MinimumSafeSideFireYaw;
}

void ASkyguardGunner::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (Boom)
	{
		Boom->SetRelativeRotation(FRotator(Pitch + Recoil, Yaw, 0.f));
	}
	Recoil = FMath::FInterpTo(Recoil, 0.f, DeltaSeconds, 10.f);
	UpdateADSVisuals(DeltaSeconds);
	UpdateIglaLock(DeltaSeconds);
	FireCooldown = FMath::Max(0.f, FireCooldown - DeltaSeconds);
	if (bFireHeld && FireCooldown <= 0.f)
	{
		FireShot();
		FireCooldown = 1.f / FMath::Max(FireRate, 0.1f);
	}
}

