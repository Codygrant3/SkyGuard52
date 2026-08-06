#include "SkyguardPathfinderBoss.h"
#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardPathfinderEncounterController.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	void ConfigureWeakPoint(
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
		Component->bExposed = bExposed;
		Component->SetCollisionResponseToChannel(ECC_Visibility, bExposed ? ECR_Block : ECR_Ignore);
	}
}

ASkyguardPathfinderBoss::ASkyguardPathfinderBoss()
{
	PrimaryActorTick.bCanEverTick = false;
	MaxDefeatDebrisPieces = 4;

	static ConstructorHelpers::FObjectFinder<UStaticMesh> BodyAsset(
		TEXT("/Game/Skyguard/Meshes/Mission01/Wave1Coast/wave1_coastal_pathfinder/StaticMeshes/SM_Boss_Pathfinder_Body.SM_Boss_Pathfinder_Body"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> AntennaAsset(
		TEXT("/Game/Skyguard/Meshes/Mission01/Wave1Coast/wave1_coastal_pathfinder/StaticMeshes/SM_Boss_Pathfinder_CommandAntenna.SM_Boss_Pathfinder_CommandAntenna"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CameraAsset(
		TEXT("/Game/Skyguard/Meshes/Mission01/Wave1Coast/wave1_coastal_pathfinder/StaticMeshes/SM_Boss_Pathfinder_NoseCamera.SM_Boss_Pathfinder_NoseCamera"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> EngineAsset(
		TEXT("/Game/Skyguard/Meshes/Mission01/Wave1Coast/wave1_coastal_pathfinder/StaticMeshes/SM_Boss_Pathfinder_Engine.SM_Boss_Pathfinder_Engine"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> LinkageAsset(
		TEXT("/Game/Skyguard/Meshes/Mission01/Wave1Coast/wave1_coastal_pathfinder/StaticMeshes/SM_Boss_Pathfinder_ControlLinkage.SM_Boss_Pathfinder_ControlLinkage"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> DebrisNoseAsset(
		TEXT("/Game/Skyguard/Meshes/Mission01/Wave1Coast/wave1_coastal_pathfinder/StaticMeshes/SM_Boss_Pathfinder_BreakChunk_L.SM_Boss_Pathfinder_BreakChunk_L"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> DebrisCenterAsset(
		TEXT("/Game/Skyguard/Meshes/Mission01/Wave1Coast/wave1_coastal_pathfinder/StaticMeshes/SM_Boss_Pathfinder_BreakChunk_Engine.SM_Boss_Pathfinder_BreakChunk_Engine"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> DebrisTailAsset(
		TEXT("/Game/Skyguard/Meshes/Mission01/Wave1Coast/wave1_coastal_pathfinder/StaticMeshes/SM_Boss_Pathfinder_BreakChunk_R.SM_Boss_Pathfinder_BreakChunk_R"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> DebrisSpineAsset(
		TEXT("/Game/Skyguard/Meshes/Mission01/Wave1Refinement/m01_wave1_aaa_refinement/StaticMeshes/SM_Boss_Pathfinder_BreakChunk_Spine_AAA.SM_Boss_Pathfinder_BreakChunk_Spine_AAA"));

	if (BodyAsset.Succeeded())
	{
		BodyMesh->SetStaticMesh(BodyAsset.Object);
	}

	CommandAntenna = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(TEXT("CommandAntenna"));
	CommandAntenna->SetupAttachment(BodyMesh);
	ConfigureWeakPoint(CommandAntenna, TEXT("CommandAntenna"), FVector(20.f, 0.f, 65.f), FVector(1.f), 68.f, true, false, true);
	if (AntennaAsset.Succeeded()) CommandAntenna->SetStaticMesh(AntennaAsset.Object);

	NoseCamera = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(TEXT("NoseCamera"));
	NoseCamera->SetupAttachment(BodyMesh);
	ConfigureWeakPoint(NoseCamera, TEXT("NoseCamera"), FVector(155.f, 0.f, -5.f), FVector(1.f), 68.f, true, false, true);
	if (CameraAsset.Succeeded()) NoseCamera->SetStaticMesh(CameraAsset.Object);

	Engine = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(TEXT("Engine"));
	Engine->SetupAttachment(BodyMesh);
	ConfigureWeakPoint(Engine, TEXT("Engine"), FVector(-145.f, 0.f, 5.f), FVector(1.f), 150.f, false, true, false);
	if (EngineAsset.Succeeded()) Engine->SetStaticMesh(EngineAsset.Object);

	ControlLinkage = CreateDefaultSubobject<USkyguardBossWeakPointComponent>(TEXT("ControlLinkage"));
	ControlLinkage->SetupAttachment(BodyMesh);
	ConfigureWeakPoint(ControlLinkage, TEXT("ControlLinkage"), FVector(-45.f, 0.f, 20.f), FVector(1.f), 60.f, true, false, false);
	if (LinkageAsset.Succeeded()) ControlLinkage->SetStaticMesh(LinkageAsset.Object);

	DebrisNose = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DebrisNose"));
	DebrisNose->SetupAttachment(BodyMesh);
	DebrisNose->SetRelativeLocation(FVector(95.f, 0.f, 0.f));
	if (DebrisNoseAsset.Succeeded()) DebrisNose->SetStaticMesh(DebrisNoseAsset.Object);
	RegisterDefeatDebris(DebrisNose);

	DebrisCenter = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DebrisCenter"));
	DebrisCenter->SetupAttachment(BodyMesh);
	DebrisCenter->SetRelativeLocation(FVector(0.f, 0.f, 0.f));
	if (DebrisCenterAsset.Succeeded()) DebrisCenter->SetStaticMesh(DebrisCenterAsset.Object);
	RegisterDefeatDebris(DebrisCenter);

	DebrisTail = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DebrisTail"));
	DebrisTail->SetupAttachment(BodyMesh);
	DebrisTail->SetRelativeLocation(FVector(-95.f, 0.f, 0.f));
	if (DebrisTailAsset.Succeeded()) DebrisTail->SetStaticMesh(DebrisTailAsset.Object);
	RegisterDefeatDebris(DebrisTail);

	DebrisSpine = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DebrisSpine"));
	DebrisSpine->SetupAttachment(BodyMesh);
	DebrisSpine->SetRelativeLocation(FVector(-20.f, 0.f, 22.f));
	if (DebrisSpineAsset.Succeeded()) DebrisSpine->SetStaticMesh(DebrisSpineAsset.Object);
	RegisterDefeatDebris(DebrisSpine);

	EncounterController =
		CreateDefaultSubobject<USkyguardPathfinderEncounterController>(TEXT("EncounterController"));
}

void ASkyguardPathfinderBoss::HandleWeakPointDestroyed(
	USkyguardBossWeakPointComponent* WeakPoint,
	ESkyguardBossWeapon Weapon)
{
	if ((WeakPoint == CommandAntenna || WeakPoint == NoseCamera) &&
		CommandAntenna->bDestroyed && NoseCamera->bDestroyed)
	{
		Engine->SetExposed(true);
		bIglaLockEnabled = true;
		SetBossPhase(ESkyguardBossPhase::LockWindow);
		return;
	}

	if (WeakPoint == Engine)
	{
		bIglaLockEnabled = false;
		ControlLinkage->SetExposed(true);
		SetBossPhase(ESkyguardBossPhase::Critical);
		return;
	}

	if (WeakPoint == ControlLinkage && Engine->bDestroyed)
	{
		SetBossPhase(ESkyguardBossPhase::Defeated);
	}
}
