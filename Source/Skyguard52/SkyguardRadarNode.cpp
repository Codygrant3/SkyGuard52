#include "SkyguardRadarNode.h"

#include "SkyguardCombatVFX.h"
#include "SkyguardRuntimeMeshCatalog.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/SoftObjectPath.h"

namespace SkyguardRadarNodePrivate
{
	const TCHAR* VanSlotId = TEXT("Radar.Van");
	const TCHAR* DishSlotId = TEXT("Radar.Dish");
	const TCHAR* EngineVanPath = TEXT("/Engine/BasicShapes/Cube.Cube");
	const TCHAR* EngineDishPath = TEXT("/Engine/BasicShapes/Cylinder.Cylinder");

	const FSkyguardMeshBindSlot* FindCodeSlot(const FName SlotId)
	{
		for (const FSkyguardMeshBindSlot& Slot :
			USkyguardRuntimeMeshCatalog::GetCodeDefaultSlots())
		{
			if (Slot.SlotId == SlotId)
			{
				return &Slot;
			}
		}
		return nullptr;
	}

	UStaticMesh* ResolvePresentationMesh(
		const FName SlotId,
		const TCHAR* EnginePrimitivePath)
	{
		FSkyguardMeshBindSlot BindSlot;
		BindSlot.SlotId = SlotId;
		// Preferred stays empty so this bind never accepts authored art.
		if (const FSkyguardMeshBindSlot* CatalogSlot = FindCodeSlot(SlotId))
		{
			BindSlot.ProxyFallback = CatalogSlot->ProxyFallback;
		}
		if (BindSlot.ProxyFallback.IsNull() && EnginePrimitivePath &&
			EnginePrimitivePath[0] != TEXT('\0'))
		{
			BindSlot.ProxyFallback = TSoftObjectPtr<UStaticMesh>(
				FSoftObjectPath(EnginePrimitivePath));
		}
		return USkyguardRuntimeMeshCatalog::ResolveSlot(BindSlot);
	}

	void BindMeshIfPresent(UStaticMeshComponent* Component, UStaticMesh* Mesh)
	{
		if (!Component || !Mesh)
		{
			return;
		}
		Component->SetStaticMesh(Mesh);
	}
}

ASkyguardRadarNode::ASkyguardRadarNode()
{
	PrimaryActorTick.bCanEverTick = true;
	Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
	SetRootComponent(Body);
	Body->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	Body->SetCollisionResponseToAllChannels(ECR_Block);
	Body->SetRelativeScale3D(FVector(2.4f, 1.6f, 1.1f));

	Dish = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Dish"));
	Dish->SetupAttachment(Body);
	Dish->SetRelativeLocation(FVector(0.f, 0.f, 90.f));
	Dish->SetRelativeScale3D(FVector(1.8f, 1.8f, 0.12f));

	Tags.AddUnique(TEXT("Skyguard.RadarNode"));
	Health = MaxHealth;
}

void ASkyguardRadarNode::BeginPlay()
{
	Super::BeginPlay();
	BindPresentation();
}

void ASkyguardRadarNode::Tick(const float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!bPresentationEnabled || bDead || !Dish)
	{
		return;
	}
	Dish->AddLocalRotation(
		FRotator(0.f, DishSpinDegreesPerSecond * DeltaSeconds, 0.f));
}

void ASkyguardRadarNode::BindPresentation()
{
	using namespace SkyguardRadarNodePrivate;

	BindMeshIfPresent(
		Body, ResolvePresentationMesh(FName(VanSlotId), EngineVanPath));
	BindMeshIfPresent(
		Dish, ResolvePresentationMesh(FName(DishSlotId), EngineDishPath));
	ApplyPresentationVisibility();
}

void ASkyguardRadarNode::SetPresentationEnabled(const bool bEnabled)
{
	bPresentationEnabled = bEnabled;
	ApplyPresentationVisibility();
}

void ASkyguardRadarNode::ApplyPresentationVisibility()
{
	if (Body)
	{
		Body->SetVisibility(bPresentationEnabled);
		Body->SetHiddenInGame(!bPresentationEnabled);
	}
	if (Dish)
	{
		const bool bShowDish = bPresentationEnabled && !bDead;
		Dish->SetVisibility(bShowDish);
		Dish->SetHiddenInGame(!bShowDish);
	}
}

void ASkyguardRadarNode::ApplyDamage(const float Amount)
{
	if (bDead || Amount <= 0.f)
	{
		return;
	}
	Health -= Amount;
	if (Health <= 0.f)
	{
		bDead = true;
		USkyguardCombatVFX::SpawnExplosion(GetWorld(), GetActorLocation(), 1.4f);
		ApplyPresentationVisibility();
		SetActorEnableCollision(false);
	}
}

void ASkyguardRadarNode::ResetNode()
{
	bDead = false;
	Health = MaxHealth;
	SetActorEnableCollision(true);
	if (Body)
	{
		Body->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	}
	ApplyPresentationVisibility();
}
