#include "SkyguardGunner.h"
#include "SkyguardGunFireCameraShake.h"
#include "SkyguardGameUserSettings.h"
#include "SkyguardAudioDirectorComponent.h"
#include "SkyguardRuntimeMeshCatalog.h"
#include "SkyguardSortieHudHostComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/Font.h"
#include "Components/InputComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/StaticMesh.h"
#include "DrawDebugHelpers.h"
#include "SkyguardDrone.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardCombatVFX.h"
#include "SkyguardIglaMissile.h"
#include "SkyguardInputCombatPerformanceCapture.h"
#include "SkyguardPauseHostComponent.h"
#include "SkyguardYak52Aircraft.h"
#include "SkyguardApacheAircraft.h"
#include "SkyguardPlayerAircraft.h"
#include "SkyguardArcadeLookComponent.h"
#include "SkyguardCpgHud.h"
#include "SkyguardCpgSightHud.h"
#include "SkyguardGuidedLockRules.h"
#include "Blueprint/UserWidget.h"
#include "SkyguardPatrolShipBoss.h"
#include "SkyguardPilotVoice.h"
#include "SkyguardThreatTypes.h"
#include "SkyguardRadarNode.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "CollisionQueryParams.h"
#include "CollisionShape.h"
#include "Engine/OverlapResult.h"
#include "Components/SceneComponent.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "GameFramework/PlayerController.h"

namespace SkyguardGunnerMeshBind
{
	bool IsSameMeshPath(const UStaticMesh* Mesh, const TCHAR* SoftPath)
	{
		return Mesh && Mesh->GetPathName() == SoftPath;
	}

	bool IsWebGameRifle(const UStaticMesh* Mesh)
	{
		return IsSameMeshPath(
			Mesh,
			TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-fde.rifle-fde"));
	}

	bool IsWebGameGlove(const UStaticMesh* Mesh)
	{
		return IsSameMeshPath(
			Mesh,
			TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-glove.rifle-glove"));
	}

	bool IsWebGameSleeve(const UStaticMesh* Mesh)
	{
		return IsSameMeshPath(
			Mesh,
			TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-rifle/StaticMeshes/rifle-sleeve.rifle-sleeve"));
	}

	bool IsWebGameIgla(const UStaticMesh* Mesh)
	{
		return IsSameMeshPath(
			Mesh,
			TEXT("/Game/Skyguard/Meshes/WebGame/skyguard-interceptor/StaticMeshes/compact-launcher-tube.compact-launcher-tube"));
	}
}

ASkyguardGunner::ASkyguardGunner()
{
	PrimaryActorTick.bCanEverTick = true;
	FireCameraShakeClass = USkyguardGunFireCameraShake::StaticClass();
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
	Boom->SetRelativeLocation(FVector(22.f, 0.f, 72.f));
	Boom->SetRelativeRotation(FRotator(-2.f, 0.f, 0.f));

	GunnerCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("GunnerCamera"));
	GunnerCamera->SetupAttachment(Boom);
	GunnerCamera->SetFieldOfView(HipFov);

	CpgStation = CreateDefaultSubobject<USceneComponent>(TEXT("CpgStation"));
	CpgStation->SetupAttachment(RootComponent);
	CpgStation->SetRelativeLocation(FVector(22.f, 0.f, 72.f));
	CpgStation->SetRelativeRotation(FRotator(-2.f, 0.f, 0.f));

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

	CpgCockpit = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgCockpit"));
	CpgCockpit->SetupAttachment(GunnerCamera);
	CpgCockpit->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	CpgCockpit->SetCastShadow(false);
	CpgCockpit->SetRelativeLocation(FVector::ZeroVector);
	CpgCockpit->SetRelativeRotation(FRotator::ZeroRotator);
	CpgCockpit->SetRelativeScale3D(FVector(1.f));
	CpgCockpit->SetVisibility(false);

	CpgSeatBack = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgSeatBack"));
	CpgSeatPan = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgSeatPan"));
	CpgKneeLeft = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgKneeLeft"));
	CpgKneeRight = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgKneeRight"));
	CpgCanopyBow = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgCanopyBow"));
	CpgDash = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgDash"));
	CpgTedac = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgTedac"));
	CpgMpdLeft = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgMpdLeft"));
	CpgMpdRight = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgMpdRight"));
	CpgEufd = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgEufd"));
	CpgTedacBezel = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgTedacBezel"));
	CpgReticleH = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgReticleH"));
	CpgReticleV = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgReticleV"));
	CpgGripLeft = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgGripLeft"));
	CpgGripRight = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgGripRight"));
	CpgConsoleRight = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgConsoleRight"));
	CpgRailLeft = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgRailLeft"));
	CpgRailRight = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CpgRailRight"));
	CpgTedacText = CreateDefaultSubobject<UTextRenderComponent>(TEXT("CpgTedacText"));
	CpgMpdLeftText = CreateDefaultSubobject<UTextRenderComponent>(TEXT("CpgMpdLeftText"));
	CpgMpdRightText = CreateDefaultSubobject<UTextRenderComponent>(TEXT("CpgMpdRightText"));
	CpgEufdText = CreateDefaultSubobject<UTextRenderComponent>(TEXT("CpgEufdText"));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Cyl(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	static ConstructorHelpers::FObjectFinder<UMaterialInterface> ShapeMat(
		TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	static ConstructorHelpers::FObjectFinder<UFont> HudFont(
		TEXT("/Engine/EngineFonts/RobotoDistanceField.RobotoDistanceField"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> HeroRifleAlt(
		TEXT("/Game/Skyguard/Meshes/Hero/rifle_irons_proxy.rifle_irons_proxy"));

	UStaticMesh* CubeMesh = Cube.Succeeded() ? Cube.Object : nullptr;
	UStaticMesh* CylMesh = Cyl.Succeeded() ? Cyl.Object.Get() : CubeMesh;
	UStaticMesh* SphereMesh = Sphere.Succeeded() ? Sphere.Object.Get() : CubeMesh;
	UMaterialInterface* VisorMat = ShapeMat.Succeeded() ? ShapeMat.Object : nullptr;
	UFont* Font = HudFont.Succeeded() ? HudFont.Object : nullptr;
	const FLinearColor Bezel(0.02f, 0.02f, 0.025f);
	const FLinearColor TedacFace(0.10f, 0.16f, 0.11f);
	const FLinearColor MpdFace(0.04f, 0.38f, 0.10f);
	const FLinearColor Optic(0.08f, 0.14f, 0.22f);
	const FLinearColor Reticle(0.20f, 0.95f, 0.30f);
	const FLinearColor Grip(0.04f, 0.04f, 0.04f);
	const FLinearColor Suit(0.16f, 0.20f, 0.10f);
	// Runway FP: TEDAC between the knees, world through the greenhouse above.
	BindCpgVisorPart(
		CpgSeatBack, FVector(-22.f, 0.f, -10.f), FVector(0.08f, 0.42f, 0.58f),
		Bezel, CubeMesh, VisorMat);
	BindCpgVisorPart(
		CpgSeatPan, FVector(-8.f, 0.f, -44.f), FVector(0.36f, 0.40f, 0.07f),
		Bezel, CubeMesh, VisorMat);
	BindCpgVisorPart(
		CpgKneeLeft, FVector(16.f, -13.f, -50.f), FVector(0.14f, 0.10f, 0.08f),
		Suit, CubeMesh, VisorMat);
	BindCpgVisorPart(
		CpgKneeRight, FVector(16.f, 13.f, -50.f), FVector(0.14f, 0.10f, 0.08f),
		Suit, CubeMesh, VisorMat);
	BindCpgVisorPart(
		CpgDash, FVector(52.f, 0.f, -37.f), FVector(0.05f, 0.50f, 0.03f),
		Bezel, CubeMesh, VisorMat);
	BindCpgVisorPart(
		CpgTedacBezel, FVector(50.f, 0.f, -30.f), FVector(0.04f, 0.15f, 0.15f),
		Bezel, CubeMesh, VisorMat);
	BindCpgVisorPart(
		CpgTedac, FVector(47.8f, 0.f, -30.f), FVector(0.01f, 0.12f, 0.12f),
		TedacFace, CubeMesh, VisorMat);
	BindCpgVisorPart(
		CpgCockpit, FVector(27.f, 0.f, -12.f), FVector(0.05f, 0.05f, 0.05f),
		Optic, SphereMesh, VisorMat);
	BindCpgVisorPart(
		CpgReticleV, FVector(47.6f, 0.f, -27.f), FVector(0.004f, 0.004f, 0.05f),
		Reticle, CubeMesh, VisorMat);
	BindCpgVisorPart(
		CpgReticleH, FVector(47.6f, 0.f, -33.f), FVector(0.004f, 0.028f, 0.024f),
		Reticle, CubeMesh, VisorMat);
	BindCpgVisorPart(
		CpgEufd, FVector(52.f, 0.f, -38.f), FVector(0.04f, 0.05f, 0.07f),
		Bezel, CubeMesh, VisorMat);
	BindCpgVisorPart(
		CpgGripLeft, FVector(50.f, -10.f, -31.f), FVector(0.08f, 0.035f, 0.06f),
		Grip, CubeMesh, VisorMat, FRotator(8.f, 12.f, 0.f));
	BindCpgVisorPart(
		CpgGripRight, FVector(50.f, 10.f, -31.f), FVector(0.08f, 0.035f, 0.06f),
		Grip, CubeMesh, VisorMat, FRotator(8.f, -12.f, 0.f));
	BindCpgVisorPart(
		CpgConsoleRight, FVector(42.f, -7.f, -48.f), FVector(0.022f, 0.022f, 0.12f),
		Grip, CylMesh, VisorMat, FRotator(58.f, 6.f, 0.f));
	BindCpgVisorPart(
		CpgMpdLeft, FVector(50.f, -20.f, -30.f), FVector(0.02f, 0.09f, 0.08f),
		MpdFace, CubeMesh, VisorMat);
	BindCpgVisorPart(
		CpgMpdRight, FVector(50.f, 20.f, -30.f), FVector(0.02f, 0.09f, 0.08f),
		MpdFace, CubeMesh, VisorMat);
	BindCpgVisorPart(
		CpgCanopyBow, FVector(18.f, 0.f, 20.f), FVector(0.10f, 0.82f, 0.045f),
		Bezel, CubeMesh, VisorMat);
	BindCpgVisorPart(
		CpgRailLeft, FVector(22.f, -23.f, 4.f), FVector(0.18f, 0.07f, 0.72f),
		Bezel, CubeMesh, VisorMat, FRotator(0.f, 0.f, -16.f));
	BindCpgVisorPart(
		CpgRailRight, FVector(22.f, 23.f, 4.f), FVector(0.18f, 0.07f, 0.72f),
		Bezel, CubeMesh, VisorMat, FRotator(0.f, 0.f, 16.f));
	BindCpgHudText(
		CpgTedacText, CpgStation, FVector(47.5f, 0.f, -30.f),
		FLinearColor(0.35f, 1.f, 0.35f), 1.1f, Font);
	BindCpgHudText(
		CpgMpdLeftText, CpgStation, FVector(48.8f, -20.f, -30.f),
		FLinearColor(0.15f, 0.95f, 0.25f), 1.2f, Font);
	BindCpgHudText(
		CpgMpdRightText, CpgStation, FVector(48.8f, 20.f, -30.f),
		FLinearColor(0.15f, 0.95f, 0.25f), 1.2f, Font);
	BindCpgHudText(
		CpgEufdText, GunnerCamera, FVector(50.f, 0.f, 18.f),
		FLinearColor(0.45f, 1.f, 0.45f), 1.6f, Font);
	if (UStaticMesh* CockpitMesh =
		USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(TEXT("Gunner.Cockpit")))
	{
		CpgCockpit->SetStaticMesh(CockpitMesh);
	}
	SetCpgVisorVisible(false);

	// Catalog order: Preferred (accepted/staged) → Hero ProxyFallback → WebGame last-resort.
	UStaticMesh* ResolvedRifle =
		USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(TEXT("Gunner.Rifle"));
	if (ResolvedRifle)
	{
		RifleMesh->SetStaticMesh(ResolvedRifle);
		if (SkyguardGunnerMeshBind::IsWebGameRifle(ResolvedRifle))
		{
			RifleMesh->SetRelativeScale3D(FVector(0.55f, 0.55f, 0.55f));
			RifleMesh->SetRelativeLocation(FVector(28.f, 10.f, -10.f));
			RifleMesh->SetRelativeRotation(FRotator(0.f, 90.f, 0.f));
		}
		else
		{
			RifleMesh->SetRelativeScale3D(FVector(30.f, 30.f, 30.f));
		}
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

	if (UStaticMesh* ResolvedHand =
		USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(TEXT("Gunner.Hand")))
	{
		HandMesh->SetStaticMesh(ResolvedHand);
		if (SkyguardGunnerMeshBind::IsWebGameGlove(ResolvedHand))
		{
			HandMesh->SetRelativeScale3D(FVector(1.f, 1.f, 1.f));
			HandMesh->SetRelativeLocation(FVector(4.f, -6.f, -8.f));
		}
		else
		{
			HandMesh->SetRelativeScale3D(FVector(12.f, 12.f, 12.f));
		}
	}
	else if (Sphere.Succeeded())
	{
		HandMesh->SetStaticMesh(Sphere.Object);
	}

	if (UStaticMesh* ResolvedForearm =
		USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(TEXT("Gunner.Forearm")))
	{
		ForearmMesh->SetStaticMesh(ResolvedForearm);
		if (SkyguardGunnerMeshBind::IsWebGameSleeve(ResolvedForearm))
		{
			ForearmMesh->SetRelativeScale3D(FVector(1.f, 1.f, 1.f));
			ForearmMesh->SetRelativeLocation(FVector(-6.f, -14.f, -4.f));
			ForearmMesh->SetRelativeRotation(FRotator(40.f, 8.f, 0.f));
		}
		else
		{
			ForearmMesh->SetRelativeScale3D(FVector(10.f, 10.f, 10.f));
		}
	}
	else if (Cyl.Succeeded())
	{
		ForearmMesh->SetStaticMesh(Cyl.Object);
	}

	if (UStaticMesh* ResolvedIgla =
		USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(TEXT("Gunner.Igla")))
	{
		IglaTube->SetStaticMesh(ResolvedIgla);
		if (SkyguardGunnerMeshBind::IsWebGameIgla(ResolvedIgla))
		{
			IglaTube->SetRelativeScale3D(FVector(0.45f, 0.45f, 0.45f));
			IglaTube->SetRelativeRotation(FRotator(0.f, 0.f, 90.f));
		}
		else
		{
			IglaTube->SetRelativeScale3D(FVector(18.f, 18.f, 18.f));
		}
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
		// Hide cube parts when a full rifle mesh is bound (Hero or WebGame last-resort)
		if (ResolvedRifle)
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
	AttachToLivePlatform();
	const APlayerController* PC = Cast<APlayerController>(GetController());
	const bool bControllerHasHost = PC &&
		PC->FindComponentByClass<USkyguardSortieHudHostComponent>() != nullptr;
	if (!bControllerHasHost &&
		!FindComponentByClass<USkyguardSortieHudHostComponent>())
	{
		if (USkyguardSortieHudHostComponent* HudHost =
			NewObject<USkyguardSortieHudHostComponent>(
				this,
				TEXT("SortieHudHost")))
		{
			HudHost->RegisterComponent();
			AddInstanceComponent(HudHost);
		}
	}
	if (!FindComponentByClass<USkyguardArcadeLookComponent>())
	{
		if (USkyguardArcadeLookComponent* ArcadeLook =
			NewObject<USkyguardArcadeLookComponent>(
				this,
				TEXT("ArcadeLook")))
		{
			ArcadeLook->RegisterComponent();
			AddInstanceComponent(ArcadeLook);
			ArcadeLook->ApplyToCamera(GunnerCamera);
		}
	}
	ApplyApacheGunnerPresentation();
	ApplyLocalPlayerControlState();
}

void ASkyguardGunner::AttachToLivePlatform()
{
	FSkyguardPlayerAircraft::AttachGunner(
		this,
		FSkyguardPlayerAircraft::FindYak(GetWorld()));
}

void ASkyguardGunner::ApplyApacheGunnerPresentation()
{
	ASkyguardApacheAircraft* Apache = FindAttachedApache();
	if (!Apache)
	{
		Apache = FSkyguardPlayerAircraft::FindApache(GetWorld());
	}
	if (!Apache)
	{
		bApacheGunnerMode = false;
		return;
	}

	bApacheGunnerMode = true;
	Pitch = -2.f;
	if (USkeletalMeshComponent* Body = GetMesh())
	{
		Body->SetHiddenInGame(true);
		Body->SetVisibility(false);
	}
	LookYawLimit = 120.f;
	LookPitchMin = -58.f;
	LookPitchMax = 22.f;
	FireRate = SkyguardApacheCpgFeel::CannonFireRate;
	BaseDamage = SkyguardApacheCpgFeel::CannonDamage;
	RecoilPitch = SkyguardApacheCpgFeel::CannonRecoilPitch;
	TraceRange = SkyguardApacheCpgFeel::CannonTraceRange;
	MinimumSafeSideFireYaw = 0.f;
	IglaLockSeconds = SkyguardApacheCpgFeel::GuidedLockSeconds;
	IglaDamage = SkyguardApacheCpgFeel::GuidedDamage;
	IglaMaximumLockAngleDegrees = SkyguardApacheCpgFeel::GuidedLockConeDegrees;
	IglaMinimumRange = SkyguardApacheCpgFeel::GuidedMinRange;
	IglaMaximumRange = SkyguardApacheCpgFeel::GuidedMaxRange;
	RocketSalvoSeconds = SkyguardApacheCpgFeel::RocketSalvoSeconds;
	RocketDamage = SkyguardApacheCpgFeel::RocketDamage;
	RocketsPerSalvo = SkyguardApacheCpgFeel::RocketsPerSalvo;
	RocketSpreadDegrees = SkyguardApacheCpgFeel::RocketSpreadDegrees;
	ADSFov = 46.f;
	HipFov = 82.f;

	if (RifleMesh)
	{
		RifleMesh->SetVisibility(false);
	}
	if (RifleReceiver)
	{
		RifleReceiver->SetVisibility(false);
	}
	if (HandMesh)
	{
		HandMesh->SetVisibility(false);
	}
	if (ForearmMesh)
	{
		ForearmMesh->SetVisibility(false);
	}
	if (FrontSight)
	{
		FrontSight->SetVisibility(false);
	}
	if (RearSight)
	{
		RearSight->SetVisibility(false);
	}
	if (IglaTube)
	{
		IglaTube->SetVisibility(false);
	}
	if (CpgCockpit && !CpgCockpit->GetStaticMesh())
	{
		if (UStaticMesh* CockpitMesh =
			USkyguardRuntimeMeshCatalog::ResolveDefaultSlot(TEXT("Gunner.Cockpit")))
		{
			CpgCockpit->SetStaticMesh(CockpitMesh);
		}
	}
	SetCpgVisorVisible(true);
	SetCpgSightHudVisible(true);
	UpdateCpgHud();
	Apache->SetFirstPersonInterior(true);
	SelectedGunshipWeapon = ESkyguardGunshipWeapon::Cannon;
	bIglaMode = false;
}

void ASkyguardGunner::BindCpgVisorPart(
	UStaticMeshComponent* Part,
	const FVector& Location,
	const FVector& Scale,
	const FLinearColor& Color,
	UStaticMesh* ShapeMesh,
	UMaterialInterface* ShapeMat,
	const FRotator Rotation)
{
	if (!Part)
	{
		return;
	}
	Part->SetupAttachment(CpgStation ? CpgStation : GunnerCamera);
	Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Part->SetCastShadow(false);
	Part->SetRelativeLocation(Location);
	Part->SetRelativeRotation(Rotation);
	Part->SetRelativeScale3D(Scale);
	Part->SetVisibility(false);
	if (ShapeMesh)
	{
		Part->SetStaticMesh(ShapeMesh);
	}
	if (ShapeMat)
	{
		UMaterialInstanceDynamic* Mid = UMaterialInstanceDynamic::Create(ShapeMat, Part);
		if (Mid)
		{
			const FLinearColor Lit(Color.R, Color.G, Color.B, 1.f);
			Mid->SetVectorParameterValue(TEXT("Color"), Lit);
			Mid->SetVectorParameterValue(TEXT("BaseColor"), Lit);
			Part->SetMaterial(0, Mid);
		}
	}
}

void ASkyguardGunner::BindCpgHudText(
	UTextRenderComponent* Text,
	USceneComponent* Parent,
	const FVector& Location,
	const FLinearColor& Color,
	const float WorldSize,
	UFont* Font)
{
	if (!Text)
	{
		return;
	}
	Text->SetupAttachment(Parent ? Parent : GunnerCamera);
	Text->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Text->SetCastShadow(false);
	Text->SetRelativeLocation(Location);
	Text->SetRelativeRotation(FRotator(0.f, 180.f, 0.f));
	Text->SetHorizontalAlignment(EHTA_Center);
	Text->SetVerticalAlignment(EVRTA_TextCenter);
	Text->SetWorldSize(WorldSize);
	Text->SetTextRenderColor(Color.ToFColor(true));
	if (Font)
	{
		Text->SetFont(Font);
	}
	Text->SetText(FText::GetEmpty());
	Text->SetVisibility(false);
}

void ASkyguardGunner::SetCpgSightHudVisible(const bool bVisible)
{
	if (!bVisible)
	{
		if (CpgSightHud)
		{
			CpgSightHud->RemoveFromParent();
		}
		return;
	}
	if (!CpgSightHud)
	{
		APlayerController* PC = Cast<APlayerController>(GetController());
		if (!PC && GetWorld())
		{
			PC = GetWorld()->GetFirstPlayerController();
		}
		if (!PC)
		{
			return;
		}
		CpgSightHud = CreateWidget<USkyguardCpgSightHud>(
			PC,
			USkyguardCpgSightHud::StaticClass());
		if (CpgSightHud)
		{
			CpgSightHud->BindGunner(this);
		}
	}
	if (CpgSightHud && !CpgSightHud->IsInViewport())
	{
		CpgSightHud->AddToViewport(40);
	}
}

void ASkyguardGunner::SetCpgVisorVisible(const bool bVisible)
{
	// Imported cabin/visor meshes stay off the lens. Screens carry the HUD.
	if (CpgCockpit)
	{
		CpgCockpit->SetVisibility(false);
	}
	if (CpgKneeLeft) CpgKneeLeft->SetVisibility(bVisible);
	if (CpgKneeRight) CpgKneeRight->SetVisibility(bVisible);
	if (CpgCanopyBow) CpgCanopyBow->SetVisibility(false);
	if (CpgSeatBack) CpgSeatBack->SetVisibility(false);
	if (CpgSeatPan) CpgSeatPan->SetVisibility(false);
	if (CpgDash)
	{
		CpgDash->SetVisibility(bVisible);
	}
	if (CpgTedac) CpgTedac->SetVisibility(bVisible);
	if (CpgTedacBezel) CpgTedacBezel->SetVisibility(bVisible);
	if (CpgReticleH) CpgReticleH->SetVisibility(bVisible);
	if (CpgReticleV) CpgReticleV->SetVisibility(bVisible);
	if (CpgGripLeft) CpgGripLeft->SetVisibility(bVisible);
	if (CpgGripRight) CpgGripRight->SetVisibility(bVisible);
	if (CpgConsoleRight) CpgConsoleRight->SetVisibility(bVisible);
	if (CpgRailLeft) CpgRailLeft->SetVisibility(false);
	if (CpgRailRight) CpgRailRight->SetVisibility(false);
	if (CpgMpdLeft) CpgMpdLeft->SetVisibility(bVisible);
	if (CpgMpdRight) CpgMpdRight->SetVisibility(bVisible);
	if (CpgEufd) CpgEufd->SetVisibility(bVisible);
	if (CpgTedacText) CpgTedacText->SetVisibility(bVisible);
	if (CpgMpdLeftText) CpgMpdLeftText->SetVisibility(bVisible);
	if (CpgMpdRightText) CpgMpdRightText->SetVisibility(bVisible);
	if (CpgEufdText) CpgEufdText->SetVisibility(bVisible);
}

ASkyguardApacheAircraft* ASkyguardGunner::FindAttachedApache() const
{
	if (ASkyguardApacheAircraft* Parent =
		Cast<ASkyguardApacheAircraft>(GetAttachParentActor()))
	{
		return Parent;
	}
	return Cast<ASkyguardApacheAircraft>(GetOwner());
}

FSkyguardCpgHudSnapshot ASkyguardGunner::BuildCpgHudSnapshot() const
{
	FSkyguardCpgHudSnapshot Snap;
	const TCHAR* Weapon = SkyguardCpgWeaponLabel(SelectedGunshipWeapon);
	const int32 Ready = GetSelectedReadyAmmo();
	const int32 Mag = GetSelectedMagazineSize();
	Snap.LockPhase = GetGuidedLockPhase();
	Snap.SightMode = GetCpgSightMode();
	Snap.LockProgress = IglaLockProgress;
	Snap.SightLine = SkyguardCpgSightLabel(Snap.SightMode);
	if (bReloading)
	{
		Snap.StationStatus = TEXT("RELOAD");
	}
	else if (Ready <= 0)
	{
		Snap.StationStatus = TEXT("EMPTY");
	}
	else if (SelectedGunshipWeapon == ESkyguardGunshipWeapon::GuidedMissile)
	{
		Snap.StationStatus = SkyguardCpgLockPhaseLabel(Snap.LockPhase);
	}
	else
	{
		Snap.StationStatus = TEXT("RDY");
	}
	Snap.WeaponLine = FString::Printf(
		TEXT("%s\n%d / %d\n%s"), Weapon, Ready, Mag, *Snap.StationStatus);

	float RangeCm = -1.f;
	if (GunnerCamera && GetWorld())
	{
		FHitResult Hit;
		const FVector Start = GunnerCamera->GetComponentLocation();
		const FVector End = Start + GunnerCamera->GetForwardVector() * TraceRange;
		FCollisionQueryParams Params(SCENE_QUERY_STAT(SkyguardCpgRange), true, this);
		if (GetWorld()->LineTraceSingleByChannel(
				Hit, Start, End, ECC_Visibility, Params))
		{
			RangeCm = Hit.Distance;
		}
	}
	if (RangeCm < 0.f)
	{
		Snap.RangeMeters = -1.f;
		Snap.RangeLine = TEXT("RNG  ----\nNO CNT");
	}
	else
	{
		Snap.RangeMeters = RangeCm * 0.01f;
		Snap.RangeLine = FString::Printf(TEXT("RNG  %.0f M"), Snap.RangeMeters);
	}
	if (SelectedGunshipWeapon == ESkyguardGunshipWeapon::GuidedMissile)
	{
		Snap.LockLine = SkyguardCpgLockPhaseLabel(Snap.LockPhase);
		if (Snap.LockPhase != ESkyguardGuidedLockPhase::Search)
		{
			Snap.LockLine += FString::Printf(
				TEXT("  %d"),
				FMath::RoundToInt(IglaLockProgress * 100.f));
		}
		Snap.RangeLine += FString::Printf(TEXT("\n%s"), *Snap.LockLine);
	}
	else
	{
		Snap.LockLine = TEXT("----");
		Snap.RangeLine += TEXT("\nLCK  --");
	}

	int32 Threats = 0;
	FString NearestKind;
	FString ShipTape;
	float NearestSq = TNumericLimits<float>::Max();
	if (UWorld* World = GetWorld())
	{
		const FVector Origin = GunnerCamera
			? GunnerCamera->GetComponentLocation()
			: GetActorLocation();
		const FVector Forward = GunnerCamera
			? GunnerCamera->GetForwardVector()
			: GetActorForwardVector();
		for (TActorIterator<ASkyguardDrone> It(World); It; ++It)
		{
			const ASkyguardDrone* Threat = *It;
			if (!IsValid(Threat) || Threat->IsDestroyed())
			{
				continue;
			}
			const FVector Offset = Threat->GetActorLocation() - Origin;
			const float DistSq = Offset.SizeSquared();
			if (DistSq > FMath::Square(24000.f) || DistSq < 1.f)
			{
				continue;
			}
			if (FVector::DotProduct(Forward, Offset.GetSafeNormal()) < 0.15f)
			{
				continue;
			}
			++Threats;
			if (DistSq < NearestSq)
			{
				NearestSq = DistSq;
				NearestKind = SkyguardCpgThreatLabel(Threat->GetThreatKind());
			}
		}
		for (TActorIterator<ASkyguardPatrolShipBoss> It(World); It; ++It)
		{
			const ASkyguardPatrolShipBoss* Ship = *It;
			if (!IsValid(Ship) || Ship->IsDefeated())
			{
				continue;
			}
			const FVector Offset = Ship->GetActorLocation() - Origin;
			const float DistSq = Offset.SizeSquared();
			if (DistSq > FMath::Square(28000.f) || DistSq < 1.f)
			{
				continue;
			}
			if (FVector::DotProduct(Forward, Offset.GetSafeNormal()) < 0.05f)
			{
				continue;
			}
			++Threats;
			ShipTape = Ship->GetHudSystemLine();
			if (DistSq < NearestSq)
			{
				NearestSq = DistSq;
				NearestKind = SkyguardCpgShipSystemLabel(Ship->GetPriorityLiveSystem());
			}
		}
	}
	float Heading = GetActorRotation().Yaw;
	if (const ASkyguardApacheAircraft* Apache = FindAttachedApache())
	{
		Heading = Apache->GetActorRotation().Yaw;
	}
	Snap.HeadingDegrees = FMath::Fmod(Heading + 360.f, 360.f);
	Snap.ThreatCount = Threats;
	Snap.FlareCount = FlareCount;
	Snap.bMissileInbound = bMissileInbound;
	const FString FlareTape = SkyguardCpgFlareTape(FlareCount);
	if (bMissileInbound)
	{
		Snap.ThreatLine = FString::Printf(
			TEXT("%s\n%s"),
			SkyguardCpgInboundLabel(),
			*FlareTape);
	}
	else if (Threats <= 0)
	{
		Snap.ThreatLine = FString::Printf(TEXT("CLR\n%s"), *FlareTape);
	}
	else if (!ShipTape.IsEmpty())
	{
		Snap.ThreatLine = FString::Printf(
			TEXT("%d THRT\n%s\n%s\n%s"),
			Threats,
			*NearestKind,
			*ShipTape,
			*FlareTape);
	}
	else
	{
		Snap.ThreatLine = FString::Printf(
			TEXT("%d THRT\n%s\n%s"),
			Threats,
			*NearestKind,
			*FlareTape);
	}

	const FString RangeShort = Snap.RangeMeters < 0.f
		? FString(TEXT("----"))
		: FString::Printf(TEXT("%.0fM"), Snap.RangeMeters);
	const FString ThreatShort = bMissileInbound
		? FString(SkyguardCpgInboundLabel())
		: (Threats > 0
			? FString::Printf(TEXT("%d %s"), Threats, *NearestKind)
			: FString(TEXT("CLR")));
	Snap.EufdLine = FString::Printf(
		TEXT("%s  %s  %s  %s  %s  %s"),
		Weapon,
		*Snap.StationStatus,
		*Snap.SightLine,
		*RangeShort,
		*ThreatShort,
		*FlareTape);
	return Snap;
}

void ASkyguardGunner::CollectCpgContactMarks(
	TArray<FSkyguardCpgContactMark>& OutMarks) const
{
	OutMarks.Reset();
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	const FVector Origin = GunnerCamera
		? GunnerCamera->GetComponentLocation()
		: GetActorLocation();
	const FVector Forward = GunnerCamera
		? GunnerCamera->GetForwardVector()
		: GetActorForwardVector();
	AActor* Locked = IglaTarget.Get();

	auto AddMark = [&](AActor* Actor, const FString& Label)
	{
		if (!IsValid(Actor))
		{
			return;
		}
		const FVector Offset = Actor->GetActorLocation() - Origin;
		const float DistSq = Offset.SizeSquared();
		const float MaxRangeCm = bThermalEnabled ? 34000.f : 28000.f;
		if (DistSq < 1.f || DistSq > FMath::Square(MaxRangeCm))
		{
			return;
		}
		const float MinDot = bThermalEnabled ? -0.02f : 0.08f;
		if (FVector::DotProduct(Forward, Offset.GetSafeNormal()) < MinDot)
		{
			return;
		}
		FSkyguardCpgContactMark Mark;
		Mark.WorldLocation = Actor->GetActorLocation();
		Mark.Label = bThermalEnabled
			? FString::Printf(TEXT("HEAT %s"), *Label)
			: Label;
		const ESkyguardGuidedLockPhase Phase = GetGuidedLockPhase();
		Mark.bLocked =
			Actor == Locked && Phase == ESkyguardGuidedLockPhase::Lock;
		Mark.bSeeking =
			Actor == Locked &&
			(Phase == ESkyguardGuidedLockPhase::Detect ||
				Phase == ESkyguardGuidedLockPhase::Track);
		Mark.LockAlpha = Actor == Locked ? IglaLockProgress : 0.f;
		OutMarks.Add(Mark);
	};

	for (TActorIterator<ASkyguardDrone> It(World); It; ++It)
	{
		ASkyguardDrone* Threat = *It;
		if (!IsValid(Threat) || Threat->IsDestroyed())
		{
			continue;
		}
		AddMark(Threat, SkyguardCpgThreatLabel(Threat->GetThreatKind()));
	}
	for (TActorIterator<ASkyguardPatrolShipBoss> It(World); It; ++It)
	{
		ASkyguardPatrolShipBoss* Ship = *It;
		if (!IsValid(Ship) || Ship->IsDefeated())
		{
			continue;
		}
		AddMark(Ship, SkyguardCpgShipSystemLabel(Ship->GetPriorityLiveSystem()));
	}
}

void ASkyguardGunner::UpdateCpgHud()
{
	const FSkyguardCpgHudSnapshot Snap = BuildCpgHudSnapshot();
	const TCHAR* Weapon = SkyguardCpgWeaponLabel(SelectedGunshipWeapon);
	if (CpgTedacText)
	{
		float Heading = GetActorRotation().Yaw;
		if (const ASkyguardApacheAircraft* Apache = FindAttachedApache())
		{
			Heading = Apache->GetActorRotation().Yaw;
		}
		Heading = FMath::Fmod(Heading + 360.f, 360.f);
		const int32 Center = FMath::RoundToInt(Heading);
		const int32 Left = (Center + 357) % 360;
		const int32 Right = (Center + 3) % 360;
		const FString Range = Snap.RangeMeters < 0.f
			? FString(TEXT("----"))
			: FString::Printf(TEXT("%.0f"), Snap.RangeMeters);
		CpgTedacText->SetText(FText::FromString(FString::Printf(
			TEXT("%03d  %03d  %03d\nRNG %s  %s  %s"),
			Left,
			Center,
			Right,
			*Range,
			Weapon,
			*Snap.StationStatus)));
	}
	if (CpgMpdLeftText)
	{
		CpgMpdLeftText->SetText(FText::FromString(Snap.WeaponLine));
	}
	if (CpgMpdRightText)
	{
		CpgMpdRightText->SetText(FText::FromString(Snap.ThreatLine));
		CpgMpdRightText->SetTextRenderColor(
			Snap.bMissileInbound
				? FColor(255, 72, 48)
				: FColor(80, 230, 70));
	}
	if (CpgEufdText)
	{
		const FString FlareTape = SkyguardCpgFlareTape(Snap.FlareCount);
		if (Snap.bMissileInbound)
		{
			CpgEufdText->SetText(FText::FromString(FString::Printf(
				TEXT("%03.0f  %s  %s"),
				Snap.HeadingDegrees,
				SkyguardCpgInboundLabel(),
				*FlareTape)));
			CpgEufdText->SetTextRenderColor(FColor(255, 72, 48));
		}
		else
		{
			CpgEufdText->SetText(FText::FromString(FString::Printf(
				TEXT("%03.0f  %s"),
				Snap.HeadingDegrees,
				*FlareTape)));
			CpgEufdText->SetTextRenderColor(FColor(115, 255, 115));
		}
	}
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
	SetCpgSightHudVisible(false);
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
	PlayerInputComponent->BindAction(TEXT("SelectWeapon1"), IE_Pressed, this, &ASkyguardGunner::InputSelectWeapon1);
	PlayerInputComponent->BindAction(TEXT("SelectWeapon2"), IE_Pressed, this, &ASkyguardGunner::InputSelectWeapon2);
	PlayerInputComponent->BindAction(TEXT("SelectWeapon3"), IE_Pressed, this, &ASkyguardGunner::InputSelectWeapon3);
	PlayerInputComponent->BindAction(TEXT("LaunchIgla"), IE_Pressed, this, &ASkyguardGunner::InputLaunchIglaPressed);
	PlayerInputComponent->BindAction(TEXT("Reload"), IE_Pressed, this, &ASkyguardGunner::InputReloadPressed);
	PlayerInputComponent->BindAction(TEXT("ToggleThermal"), IE_Pressed, this, &ASkyguardGunner::InputToggleThermal);
	PlayerInputComponent->BindAction(TEXT("PopFlares"), IE_Pressed, this, &ASkyguardGunner::InputPopFlares);
	PlayerInputComponent->BindAxis(TEXT("PilotCollective"), this, &ASkyguardGunner::InputPilotCollective);
	PlayerInputComponent->BindAxis(TEXT("PilotYaw"), this, &ASkyguardGunner::InputPilotYaw);
	PlayerInputComponent->BindAxis(TEXT("PilotCyclicPitch"), this, &ASkyguardGunner::InputPilotCyclicPitch);
	PlayerInputComponent->BindAxis(TEXT("PilotCyclicRoll"), this, &ASkyguardGunner::InputPilotCyclicRoll);
	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (USkyguardPauseHostComponent* PauseHost =
			PC->FindComponentByClass<USkyguardPauseHostComponent>())
		{
			PauseHost->BindPauseInput(PlayerInputComponent);
		}
	}
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

void ASkyguardGunner::InputSelectWeapon1()
{
	SelectGunshipWeapon(ESkyguardGunshipWeapon::Cannon);
}

void ASkyguardGunner::InputSelectWeapon2()
{
	SelectGunshipWeapon(ESkyguardGunshipWeapon::Rockets);
}

void ASkyguardGunner::InputSelectWeapon3()
{
	SelectGunshipWeapon(ESkyguardGunshipWeapon::GuidedMissile);
}

void ASkyguardGunner::SelectGunshipWeapon(const ESkyguardGunshipWeapon Weapon)
{
	const ESkyguardGunshipWeapon Previous = SelectedGunshipWeapon;
	SelectedGunshipWeapon = Weapon;
	if (bApacheGunnerMode &&
		Previous == ESkyguardGunshipWeapon::GuidedMissile &&
		Weapon != ESkyguardGunshipWeapon::GuidedMissile)
	{
		ResetGuidedLock();
	}
	if (bApacheGunnerMode)
	{
		bIglaMode = Weapon == ESkyguardGunshipWeapon::GuidedMissile;
		if (IglaTube)
		{
			IglaTube->SetVisibility(false);
		}
		if (RifleMesh) RifleMesh->SetVisibility(false);
		if (HandMesh) HandMesh->SetVisibility(false);
		if (ForearmMesh) ForearmMesh->SetVisibility(false);
		if (FrontSight) FrontSight->SetVisibility(false);
		if (RearSight) RearSight->SetVisibility(false);
		if (RifleReceiver) RifleReceiver->SetVisibility(false);
		USkyguardInputCombatPerformanceCapture::RecordPlayerEvent(
			this, TEXT("weapon_switch"));
		return;
	}

	bIglaMode = Weapon != ESkyguardGunshipWeapon::Cannon;
	if (IglaTube) IglaTube->SetVisibility(bIglaMode);
	if (RifleMesh) RifleMesh->SetVisibility(!bIglaMode);
	if (HandMesh) HandMesh->SetVisibility(!bIglaMode);
	if (ForearmMesh) ForearmMesh->SetVisibility(!bIglaMode);
	if (FrontSight) FrontSight->SetVisibility(false);
	if (RearSight) RearSight->SetVisibility(false);
	if (RifleReceiver) RifleReceiver->SetVisibility(false);
	USkyguardInputCombatPerformanceCapture::RecordPlayerEvent(
		this, TEXT("weapon_switch"));
}

void ASkyguardGunner::InputLaunchIglaPressed()
{
	bIglaLaunchRequestedFromPlayerInput = true;
	LaunchIglaPressed();
	bIglaLaunchRequestedFromPlayerInput = false;
}

void ASkyguardGunner::InputReloadPressed()
{
	ReloadSelectedWeapon();
}

int32 ASkyguardGunner::GetSelectedReadyAmmo() const
{
	switch (SelectedGunshipWeapon)
	{
	case ESkyguardGunshipWeapon::Rockets:
		return RocketAmmo;
	case ESkyguardGunshipWeapon::GuidedMissile:
		return GuidedAmmo;
	case ESkyguardGunshipWeapon::Cannon:
	default:
		return CannonMagazine;
	}
}

int32 ASkyguardGunner::GetSelectedMagazineSize() const
{
	switch (SelectedGunshipWeapon)
	{
	case ESkyguardGunshipWeapon::Rockets:
		return RocketMagazineSize;
	case ESkyguardGunshipWeapon::GuidedMissile:
		return GuidedMagazineSize;
	case ESkyguardGunshipWeapon::Cannon:
	default:
		return CannonMagazineSize;
	}
}

void ASkyguardGunner::ReloadSelectedWeapon()
{
	if (bReloading)
	{
		return;
	}
	if (GetSelectedReadyAmmo() >= GetSelectedMagazineSize())
	{
		return;
	}

	int32 Reserve = 0;
	const TCHAR* Station = TEXT("guns");
	switch (SelectedGunshipWeapon)
	{
	case ESkyguardGunshipWeapon::Rockets:
		Reserve = RocketReserve;
		Station = TEXT("rockets");
		break;
	case ESkyguardGunshipWeapon::GuidedMissile:
		Reserve = GuidedReserve;
		Station = TEXT("missiles");
		break;
	case ESkyguardGunshipWeapon::Cannon:
	default:
		Reserve = CannonReserve;
		Station = TEXT("the cannon");
		break;
	}
	if (Reserve <= 0)
	{
		return;
	}

	bReloading = true;
	bFireHeld = false;
	switch (SelectedGunshipWeapon)
	{
	case ESkyguardGunshipWeapon::Rockets:
		ReloadRemaining = SkyguardApacheCpgFeel::RocketReloadSeconds;
		break;
	case ESkyguardGunshipWeapon::GuidedMissile:
		ReloadRemaining = SkyguardApacheCpgFeel::GuidedReloadSeconds;
		break;
	case ESkyguardGunshipWeapon::Cannon:
	default:
		ReloadRemaining = SkyguardApacheCpgFeel::CannonReloadSeconds;
		break;
	}
	SkyguardPilotVoice::CallReload(this, Station);
}

void ASkyguardGunner::AdvanceReload(const float DeltaSeconds)
{
	if (!bReloading)
	{
		return;
	}
	ReloadRemaining -= DeltaSeconds;
	if (ReloadRemaining <= 0.f)
	{
		FinishReload();
	}
}

void ASkyguardGunner::FinishReload()
{
	bReloading = false;
	ReloadRemaining = 0.f;
	auto Fill = [](int32& Mag, const int32 MagSize, int32& Reserve)
	{
		const int32 Need = FMath::Max(0, MagSize - Mag);
		const int32 Taken = FMath::Min(Need, Reserve);
		Mag += Taken;
		Reserve -= Taken;
	};
	switch (SelectedGunshipWeapon)
	{
	case ESkyguardGunshipWeapon::Rockets:
		Fill(RocketAmmo, RocketMagazineSize, RocketReserve);
		break;
	case ESkyguardGunshipWeapon::GuidedMissile:
		Fill(GuidedAmmo, GuidedMagazineSize, GuidedReserve);
		break;
	case ESkyguardGunshipWeapon::Cannon:
	default:
		Fill(CannonMagazine, CannonMagazineSize, CannonReserve);
		break;
	}
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
	if (bApacheGunnerMode)
	{
		const uint8 Next =
			(static_cast<uint8>(SelectedGunshipWeapon) + 1) % 3;
		SelectGunshipWeapon(static_cast<ESkyguardGunshipWeapon>(Next));
		return;
	}

	bIglaMode = !bIglaMode;
	if (IglaTube) IglaTube->SetVisibility(bIglaMode);
	if (RifleMesh) RifleMesh->SetVisibility(!bIglaMode);
	if (HandMesh) HandMesh->SetVisibility(!bIglaMode);
	if (ForearmMesh) ForearmMesh->SetVisibility(!bIglaMode);
	if (FrontSight) FrontSight->SetVisibility(false);
	if (RearSight) RearSight->SetVisibility(false);
	if (RifleReceiver) RifleReceiver->SetVisibility(false);
	ResetGuidedLock();
}

void ASkyguardGunner::LaunchIglaPressed()
{
	if (CanFireGuidedMissile())
	{
		FireGuidedMissile();
	}
}

void ASkyguardGunner::InputPilotCollective(const float Value)
{
	PilotCollectiveAxis = Value;
}

void ASkyguardGunner::InputPilotYaw(const float Value)
{
	PilotYawAxis = Value;
}

void ASkyguardGunner::InputPilotCyclicPitch(const float Value)
{
	PilotCyclicPitchAxis = Value;
}

void ASkyguardGunner::InputPilotCyclicRoll(const float Value)
{
	PilotCyclicRollAxis = Value;
}

void ASkyguardGunner::ApplyDirectFlightInput()
{
	if (!bApacheGunnerMode)
	{
		return;
	}
	if (ASkyguardApacheAircraft* Apache = FindAttachedApache())
	{
		Apache->SetDirectFlightInput(
			PilotCollectiveAxis,
			PilotYawAxis,
			PilotCyclicPitchAxis,
			PilotCyclicRollAxis);
	}
}

void ASkyguardGunner::UpdateSensorAwareness(const float DeltaSeconds)
{
	SensorWarningCooldown = FMath::Max(0.f, SensorWarningCooldown - DeltaSeconds);
	const bool bSensor = bApacheGunnerMode && bADS && GunnerCamera;
	if (!bSensor)
	{
		SensorTunnelSeconds = 0.f;
		return;
	}

	bool bOffAxisDanger = false;
	const FVector Origin = GunnerCamera->GetComponentLocation();
	const FVector Forward = GunnerCamera->GetForwardVector();
	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<ASkyguardDrone> It(World); It; ++It)
		{
			const ASkyguardDrone* Threat = *It;
			if (!IsValid(Threat) || Threat->IsDestroyed())
			{
				continue;
			}
			const FVector Offset = Threat->GetActorLocation() - Origin;
			const float DistSq = Offset.SizeSquared();
			if (DistSq > FMath::Square(9000.f) || DistSq < 1.f)
			{
				continue;
			}
			const float Dot = FVector::DotProduct(Forward, Offset.GetSafeNormal());
			if (Dot < 0.45f &&
				(Threat->IsMissileLockEligible() ||
				 Threat->GetThreatKind() == ESkyguardThreatKind::RotorScout))
			{
				bOffAxisDanger = true;
				break;
			}
		}
	}

	if (bOffAxisDanger)
	{
		SensorTunnelSeconds += DeltaSeconds;
		if (SensorTunnelSeconds > 2.4f && SensorWarningCooldown <= 0.f)
		{
			SkyguardPilotVoice::WarnOffAxis(this);
			SensorWarningCooldown = 8.f;
			SensorTunnelSeconds = 0.f;
		}
	}
	else
	{
		SensorTunnelSeconds = FMath::Max(0.f, SensorTunnelSeconds - DeltaSeconds * 0.7f);
	}
}

void ASkyguardGunner::UpdateADSVisuals(float DeltaSeconds)
{
	if (!GunnerCamera) return;
	const float TargetFov = bADS ? ADSFov : HipFov;
	GunnerCamera->SetFieldOfView(FMath::FInterpTo(GunnerCamera->FieldOfView, TargetFov, DeltaSeconds, 12.f));
	if (bApacheGunnerMode)
	{
		if (USkyguardArcadeLookComponent* Look =
			FindComponentByClass<USkyguardArcadeLookComponent>())
		{
			if (bADS)
			{
				if (bThermalEnabled)
				{
					Look->ApplyThermalSensor(GunnerCamera);
				}
				else
				{
					Look->ApplyTargetingSensor(GunnerCamera);
				}
			}
			else if (bWasTargetingSensor)
			{
				Look->ApplyHelmetSight(GunnerCamera);
			}
		}
		if (ASkyguardApacheAircraft* Apache = FindAttachedApache())
		{
			Apache->SetSensorView(bADS);
		}
		SetCpgVisorVisible(!bADS);
		SetCpgSightHudVisible(true);
		bWasTargetingSensor = bADS;
		return;
	}
	if (!RifleMesh)
	{
		return;
	}

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

ESkyguardGuidedLockPhase ASkyguardGunner::GetGuidedLockPhase() const
{
	return FSkyguardGuidedLockRules::PhaseFromProgress(
		IglaLockProgress,
		IglaTarget.IsValid());
}

ESkyguardCpgSightMode ASkyguardGunner::GetCpgSightMode() const
{
	return (bApacheGunnerMode && bADS)
		? ESkyguardCpgSightMode::TargetingSensor
		: ESkyguardCpgSightMode::Helmet;
}

bool ASkyguardGunner::CanFireGuidedMissile() const
{
	if (!IglaTarget.IsValid())
	{
		return false;
	}
	if (!FSkyguardGuidedLockRules::CanFire(GetGuidedLockPhase()))
	{
		return false;
	}
	if (bApacheGunnerMode && GuidedAmmo <= 0)
	{
		return false;
	}
	return true;
}

bool ASkyguardGunner::IsGuidedSeekerLive() const
{
	if (bApacheGunnerMode)
	{
		return SelectedGunshipWeapon == ESkyguardGunshipWeapon::GuidedMissile;
	}
	return bIglaMode;
}

void ASkyguardGunner::ResetGuidedLock()
{
	IglaLockProgress = 0.f;
	IglaTarget = nullptr;
	bIglaLockPreviouslyAcquired = false;
	IglaAcquireCooldownRemaining = 0.f;
}

float ASkyguardGunner::GetActiveLockSeconds() const
{
	if (bApacheGunnerMode)
	{
		return FSkyguardGuidedLockRules::LockSeconds(GetCpgSightMode());
	}
	return IglaLockSeconds;
}

float ASkyguardGunner::GetActiveLockAngleDegrees() const
{
	if (bApacheGunnerMode)
	{
		return FSkyguardGuidedLockRules::AcquireDegrees(GetCpgSightMode());
	}
	return IglaMaximumLockAngleDegrees;
}

void ASkyguardGunner::UpdateIglaLock(float DeltaSeconds)
{
	const bool bWasAcquired = IglaLockProgress >= 1.f && IglaTarget.IsValid();
	if (!IsGuidedSeekerLive() || !GunnerCamera)
	{
		ResetGuidedLock();
		return;
	}

	// Keep the active seeker target sticky between throttled world queries.
	AActor* Candidate = nullptr;
	if (IglaTarget.IsValid() && IsIglaLockCandidateValid(IglaTarget.Get()))
	{
		Candidate = IglaTarget.Get();
	}

	IglaAcquireCooldownRemaining -= DeltaSeconds;
	const bool bShouldScan =
		IglaAcquireCooldownRemaining <= 0.f || Candidate == nullptr;
	if (bShouldScan)
	{
		IglaAcquireCooldownRemaining = FMath::Max(0.05f, IglaAcquireIntervalSeconds);
		if (AActor* Acquired = AcquireIglaTarget())
		{
			Candidate = Acquired;
		}
	}

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
			IglaLockProgress + DeltaSeconds / FMath::Max(GetActiveLockSeconds(), 0.1f),
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
		if (bApacheGunnerMode)
		{
			SkyguardPilotVoice::CallLock(this);
		}
	}
	bIglaLockPreviouslyAcquired = bIsAcquired;
}

bool ASkyguardGunner::ScoreIglaLockCandidate(
	const AActor* Candidate,
	const FVector& Origin,
	const FVector& Forward,
	const float MinimumDot,
	float& OutScore) const
{
	if (!Candidate || !GetWorld())
	{
		return false;
	}

	const FVector CandidateLocation = Candidate->GetActorLocation();
	const FVector Offset = CandidateLocation - Origin;
	const float Distance = Offset.Size();
	if (Distance < IglaMinimumRange || Distance > IglaMaximumRange)
	{
		return false;
	}

	const float Dot = FVector::DotProduct(Forward, Offset / Distance);
	if (Dot < MinimumDot)
	{
		return false;
	}

	FHitResult Occlusion;
	FCollisionQueryParams Query(SCENE_QUERY_STAT(SkyguardIglaOcclusion), true, this);
	const bool bBlocked = GetWorld()->LineTraceSingleByChannel(
		Occlusion,
		Origin,
		CandidateLocation,
		ECC_Visibility,
		Query);
	if (bBlocked && Occlusion.GetActor() != Candidate)
	{
		return false;
	}

	OutScore = (1.f - Dot) * IglaMaximumRange + Distance * 0.05f;
	return true;
}

bool ASkyguardGunner::IsIglaLockCandidateValid(const AActor* Candidate) const
{
	if (!Candidate || !GetWorld() || !GunnerCamera)
	{
		return false;
	}

	if (const ASkyguardBossDroneBase* Boss = Cast<ASkyguardBossDroneBase>(Candidate))
	{
		if (!Boss->IsIglaLockEligible())
		{
			return false;
		}
	}
	else if (const ASkyguardDrone* Drone = Cast<ASkyguardDrone>(Candidate))
	{
		if (!Drone->IsMissileLockEligible())
		{
			return false;
		}
	}
	else if (const ASkyguardPatrolShipBoss* Ship =
		Cast<ASkyguardPatrolShipBoss>(Candidate))
	{
		if (Ship->IsDefeated())
		{
			return false;
		}
	}
	else if (const ASkyguardRadarNode* Radar = Cast<ASkyguardRadarNode>(Candidate))
	{
		if (Radar->IsDestroyed())
		{
			return false;
		}
	}
	else
	{
		return false;
	}

	const FVector Origin = GunnerCamera->GetComponentLocation();
	const FVector Forward = GunnerCamera->GetForwardVector();
	const float MinimumDot =
		FMath::Cos(FMath::DegreesToRadians(GetActiveLockAngleDegrees()));
	float UnusedScore = 0.f;
	return ScoreIglaLockCandidate(
		Candidate,
		Origin,
		Forward,
		MinimumDot,
		UnusedScore);
}

AActor* ASkyguardGunner::AcquireIglaTarget() const
{
	if (!GetWorld() || !GunnerCamera)
	{
		return nullptr;
	}

	const FVector Origin = GunnerCamera->GetComponentLocation();
	const FVector Forward = GunnerCamera->GetForwardVector();
	const float MinimumDot =
		FMath::Cos(FMath::DegreesToRadians(GetActiveLockAngleDegrees()));
	AActor* BestTarget = nullptr;
	float BestScore = TNumericLimits<float>::Max();

	// Spatial query in seeker range instead of two full-world actor iterators.
	FCollisionObjectQueryParams ObjectQuery;
	ObjectQuery.AddObjectTypesToQuery(ECC_WorldDynamic);
	ObjectQuery.AddObjectTypesToQuery(ECC_WorldStatic);
	ObjectQuery.AddObjectTypesToQuery(ECC_Pawn);
	ObjectQuery.AddObjectTypesToQuery(ECC_PhysicsBody);

	FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(SkyguardIglaAcquire), false, this);
	TArray<FOverlapResult> Overlaps;
	GetWorld()->OverlapMultiByObjectType(
		Overlaps,
		Origin,
		FQuat::Identity,
		ObjectQuery,
		FCollisionShape::MakeSphere(IglaMaximumRange),
		QueryParams);

	for (const FOverlapResult& Overlap : Overlaps)
	{
		AActor* Actor = Overlap.GetActor();
		if (!Actor)
		{
			continue;
		}

		AActor* Candidate = nullptr;
		if (ASkyguardBossDroneBase* Boss = Cast<ASkyguardBossDroneBase>(Actor))
		{
			if (!Boss->IsIglaLockEligible())
			{
				continue;
			}
			Candidate = Boss;
		}
		else if (ASkyguardDrone* Drone = Cast<ASkyguardDrone>(Actor))
		{
			if (!Drone->IsMissileLockEligible())
			{
				continue;
			}
			Candidate = Drone;
		}
		else if (ASkyguardPatrolShipBoss* Ship = Cast<ASkyguardPatrolShipBoss>(Actor))
		{
			if (Ship->IsDefeated())
			{
				continue;
			}
			Candidate = Ship;
		}
		else if (ASkyguardRadarNode* RadarNode = Cast<ASkyguardRadarNode>(Actor))
		{
			if (RadarNode->IsDestroyed())
			{
				continue;
			}
			Candidate = RadarNode;
		}
		else
		{
			continue;
		}

		float Score = 0.f;
		if (!ScoreIglaLockCandidate(Candidate, Origin, Forward, MinimumDot, Score))
		{
			continue;
		}
		if (Score < BestScore)
		{
			BestScore = Score;
			BestTarget = Candidate;
		}
	}

	return BestTarget;
}
void ASkyguardGunner::ResetSortieCombatStats()
{
	SortieShotsFired = 0;
	SortieHits = 0;
	// Fallback cache only; Fill/Get prefer the owning Yak's GetDamageFraction().
	SortieAircraftDamageFraction = 0.f;
}

float ASkyguardGunner::GetSortieAircraftDamageFraction() const
{
	if (const AActor* Platform = GetAttachParentActor())
	{
		if (FSkyguardPlayerAircraft::IsPlayerPlatform(Platform))
		{
			return FSkyguardPlayerAircraft::GetHullDamageFraction(Platform);
		}
	}
	if (const AActor* OwnerPlatform = GetOwner())
	{
		if (FSkyguardPlayerAircraft::IsPlayerPlatform(OwnerPlatform))
		{
			return FSkyguardPlayerAircraft::GetHullDamageFraction(OwnerPlatform);
		}
	}
	return SortieAircraftDamageFraction;
}

void ASkyguardGunner::FillSortieCombatStats(FSkyguardMissionResult& OutResult) const
{
	OutResult.ShotsFired = SortieShotsFired;
	OutResult.Hits = SortieHits;
	OutResult.AircraftDamageFraction = GetSortieAircraftDamageFraction();
}

void ASkyguardGunner::RecordRifleShot()
{
	++SortieShotsFired;
}

void ASkyguardGunner::RecordRifleHit()
{
	++SortieHits;
}

void ASkyguardGunner::RecordIglaShot()
{
	++SortieShotsFired;
}

void ASkyguardGunner::RecordIglaHit()
{
	++SortieHits;
}

void ASkyguardGunner::FireIgla()
{
	FireGuidedMissile();
}

void ASkyguardGunner::FireGuidedMissile()
{
	if (!CanFireGuidedMissile() || !GunnerCamera || !GetWorld())
	{
		return;
	}
	AActor* Target = IglaTarget.Get();
	const FVector TargetLocation = Target->GetActorLocation();
	const FVector Dir = (TargetLocation - GunnerCamera->GetComponentLocation()).GetSafeNormal();
	FVector Muzzle = IglaMuzzle
		? IglaMuzzle->GetComponentLocation()
		: GunnerCamera->GetComponentLocation() + GunnerCamera->GetForwardVector() * 60.f;
	if (ASkyguardApacheAircraft* Apache = FindAttachedApache())
	{
		const FVector Pylon = Apache->GetActorLocation() +
			Apache->GetActorRightVector() * 180.f +
			Apache->GetActorUpVector() * -20.f +
			Apache->GetActorForwardVector() * 40.f;
		Muzzle = Pylon;
	}
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
	if (bMissileSpawned)
	{
		if (bApacheGunnerMode)
		{
			GuidedAmmo = FMath::Max(0, GuidedAmmo - 1);
		}
		PlayAppliedCameraShake(1.35f);
		RecordIglaShot();
		if (bIglaLaunchRequestedFromPlayerInput || bFireHeldFromPlayerInput)
		{
			USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
				this, TEXT("igla_launch"));
		}
		USkyguardAudioDirectorComponent::TriggerWorldEvent(
			this,
			ESkyguardAudioEvent::IglaLaunch,
			Muzzle);
	}
	ResetGuidedLock();
}


void ASkyguardGunner::PlayAppliedCameraShake(const float IntensityScale)
{
	const float Scale = AppliedCameraShakeScale * IntensityScale;
	if (Scale <= KINDA_SMALL_NUMBER || !FireCameraShakeClass)
	{
		return;
	}

	APlayerController* PC = Cast<APlayerController>(GetController());
	if (!PC)
	{
		PC = Cast<APlayerController>(GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr);
	}
	if (!PC)
	{
		return;
	}

	PC->ClientStartCameraShake(FireCameraShakeClass, Scale);
}

void ASkyguardGunner::FireShot()
{
	if (!GunnerCamera || bReloading) return;
	if (bApacheGunnerMode)
	{
		switch (SelectedGunshipWeapon)
		{
		case ESkyguardGunshipWeapon::Rockets:
			FireRockets();
			return;
		case ESkyguardGunshipWeapon::GuidedMissile:
			FireGuidedMissile();
			return;
		case ESkyguardGunshipWeapon::Cannon:
			FireCannon();
			return;
		}
		checkNoEntry();
		FireCannon();
		return;
	}
	if (bIglaMode)
	{
		FireGuidedMissile();
		return;
	}
	FireCannon();
}

void ASkyguardGunner::FireCannon()
{
	if (!GunnerCamera || bReloading)
	{
		return;
	}
	if (bApacheGunnerMode)
	{
		if (CannonMagazine <= 0)
		{
			return;
		}
	}
	if (!GetWorld())
	{
		return;
	}
	if (bApacheGunnerMode)
	{
		--CannonMagazine;
	}
	// Yak rear seat keeps the pilot/canopy as a no-fire sector. Apache CPG
	// fires the chin gun forward, so the safety arc is skipped.
	if (!bApacheGunnerMode && !IsRifleDirectionOutsidePilotSafetyArc())
	{
		return;
	}
	RecordRifleShot();
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
	FVector Muzzle = Start;
	if (ASkyguardApacheAircraft* Apache = FindAttachedApache())
	{
		Muzzle = Apache->GetChinMuzzleLocation();
	}
	else if (RifleMesh)
	{
		Muzzle = RifleMesh->GetComponentLocation() +
			RifleMesh->GetForwardVector() * 55.f +
			RifleMesh->GetUpVector() * 8.f;
	}
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
			RecordRifleHit();
		}
		else if (ASkyguardDrone* Drone = Cast<ASkyguardDrone>(Hit.GetActor()))
		{
			Drone->ApplyBallisticHit(BaseDamage, Hit.ImpactPoint, Dir);
			RecordRifleHit();
		}
		else if (ASkyguardRadarNode* Radar = Cast<ASkyguardRadarNode>(Hit.GetActor()))
		{
			Radar->ApplyDamage(BaseDamage);
			RecordRifleHit();
		}
		else if (ASkyguardPatrolShipBoss* Ship = Cast<ASkyguardPatrolShipBoss>(Hit.GetActor()))
		{
			Ship->ApplyHit(Hit.GetComponent(), BaseDamage);
			RecordRifleHit();
		}
		USkyguardCombatVFX::SpawnHitSparks(GetWorld(), Hit.ImpactPoint, Hit.ImpactNormal);
	}
	Recoil = RecoilPitch;
	Pitch = FMath::Clamp(Pitch + RecoilPitch * 0.35f, LookPitchMin, LookPitchMax);
	PlayAppliedCameraShake(1.f);
}

void ASkyguardGunner::FireRockets()
{
	if (!GunnerCamera || !GetWorld() || bReloading || RocketAmmo <= 0 || RocketCooldown > 0.f)
	{
		return;
	}

	const FVector Origin = GunnerCamera->GetComponentLocation();
	const FVector Aim = GunnerCamera->GetForwardVector();
	FVector Muzzle = Origin + Aim * 80.f;
	if (ASkyguardApacheAircraft* Apache = FindAttachedApache())
	{
		Muzzle = Apache->GetActorLocation() +
			Apache->GetActorRightVector() * (RocketAmmo % 2 == 0 ? 170.f : -170.f) +
			Apache->GetActorUpVector() * -30.f +
			Apache->GetActorForwardVector() * 20.f;
	}

	const int32 Count = FMath::Max(1, RocketsPerSalvo);
	const float SpreadRad = FMath::DegreesToRadians(RocketSpreadDegrees);
	bool bAnyHit = false;
	for (int32 Index = 0; Index < Count && RocketAmmo > 0; ++Index)
	{
		const FVector Dir = FMath::VRandCone(Aim, SpreadRad);
		const FVector End = Origin + Dir * TraceRange;
		FHitResult Hit;
		FCollisionQueryParams Params(SCENE_QUERY_STAT(SkyguardRocket), true, this);
		const bool bHit = GetWorld()->LineTraceSingleByChannel(
			Hit, Origin, End, ECC_Visibility, Params);
		const FVector Impact = bHit ? Hit.ImpactPoint : End;
		USkyguardCombatVFX::SpawnMissileTrail(GetWorld(), Muzzle, Impact);
		if (bHit)
		{
			USkyguardCombatVFX::SpawnExplosion(GetWorld(), Impact, 0.85f);
			TArray<FOverlapResult> Overlaps;
			FCollisionObjectQueryParams ObjectQuery;
			ObjectQuery.AddObjectTypesToQuery(ECC_WorldDynamic);
			ObjectQuery.AddObjectTypesToQuery(ECC_WorldStatic);
			ObjectQuery.AddObjectTypesToQuery(ECC_Pawn);
			GetWorld()->OverlapMultiByObjectType(
				Overlaps,
				Impact,
				FQuat::Identity,
				ObjectQuery,
				FCollisionShape::MakeSphere(SkyguardApacheCpgFeel::RocketSplashRadius),
				Params);
			for (const FOverlapResult& Overlap : Overlaps)
			{
				AActor* Actor = Overlap.GetActor();
				if (ASkyguardDrone* Drone = Cast<ASkyguardDrone>(Actor))
				{
					Drone->ApplyBallisticHit(RocketDamage, Impact, Dir);
					bAnyHit = true;
				}
				else if (ASkyguardBossDroneBase* Boss = Cast<ASkyguardBossDroneBase>(Actor))
				{
					Boss->ApplyWeaponHit(
						Overlap.GetComponent(),
						ESkyguardBossWeapon::Rifle,
						RocketDamage,
						Impact,
						Dir);
					bAnyHit = true;
				}
				else if (ASkyguardRadarNode* Radar = Cast<ASkyguardRadarNode>(Actor))
				{
					Radar->ApplyDamage(RocketDamage);
					bAnyHit = true;
				}
				else if (ASkyguardPatrolShipBoss* Ship = Cast<ASkyguardPatrolShipBoss>(Actor))
				{
					Ship->ApplyHit(Overlap.GetComponent(), RocketDamage);
					bAnyHit = true;
				}
			}
		}
		--RocketAmmo;
		RecordRifleShot();
	}

	RocketCooldown = RocketSalvoSeconds;
	FireCooldown = RocketSalvoSeconds;
	PlayAppliedCameraShake(1.6f);
	USkyguardAudioDirectorComponent::TriggerWorldEvent(
		this,
		ESkyguardAudioEvent::IglaLaunch,
		Muzzle);
	if (bAnyHit)
	{
		RecordRifleHit();
	}
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
	if (ASkyguardApacheAircraft* Apache = FindAttachedApache())
	{
		if (GunnerCamera)
		{
			Apache->AimChinTurret(GunnerCamera->GetComponentRotation());
		}
		ApplyDirectFlightInput();
	}
	if (bApacheGunnerMode)
	{
		UpdateCpgHud();
	}
	Recoil = FMath::FInterpTo(Recoil, 0.f, DeltaSeconds, 10.f);
	UpdateADSVisuals(DeltaSeconds);
	UpdateIglaLock(DeltaSeconds);
	UpdateSensorAwareness(DeltaSeconds);
	AdvanceReload(DeltaSeconds);
	FireCooldown = FMath::Max(0.f, FireCooldown - DeltaSeconds);
	RocketCooldown = FMath::Max(0.f, RocketCooldown - DeltaSeconds);
	if (bFireHeld && FireCooldown <= 0.f)
	{
		FireShot();
		const float CannonInterval = 1.f / FMath::Max(FireRate, 0.1f);
		if (FireCooldown <= 0.f)
		{
			FireCooldown = CannonInterval;
		}
	}
}
