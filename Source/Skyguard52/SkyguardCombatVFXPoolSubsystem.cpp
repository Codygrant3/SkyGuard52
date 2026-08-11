#include "SkyguardCombatVFXPoolSubsystem.h"

#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Materials/Material.h"
#include "Materials/MaterialInterface.h"
#include "UObject/UObjectGlobals.h"

bool USkyguardCombatVFXPoolSubsystem::DoesSupportWorldType(
	const EWorldType::Type WorldType) const
{
	return WorldType == EWorldType::Game ||
		WorldType == EWorldType::PIE ||
		WorldType == EWorldType::GamePreview;
}

void USkyguardCombatVFXPoolSubsystem::Initialize(
	FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
	PrewarmAssets();
	AllocatePool();
}

void USkyguardCombatVFXPoolSubsystem::PrewarmAssets()
{
	SphereMesh = LoadObject<UStaticMesh>(
		nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	ConeMesh = LoadObject<UStaticMesh>(
		nullptr, TEXT("/Engine/BasicShapes/Cone.Cone"));
	CylinderMesh = LoadObject<UStaticMesh>(
		nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));

	HotMaterial = LoadObject<UMaterialInterface>(
		nullptr,
		TEXT("/Game/Skyguard/Materials/Generated/MI_MuzzleFlash_Hot.MI_MuzzleFlash_Hot"));
	if (!HotMaterial)
	{
		HotMaterial = LoadObject<UMaterialInterface>(
			nullptr, TEXT("/Game/Skyguard/Materials/M_ExhaustGlow.M_ExhaustGlow"));
	}

	SmokeMaterial = LoadObject<UMaterialInterface>(
		nullptr,
		TEXT("/Game/Skyguard/Materials/M_Tex_L8_plaster2.M_Tex_L8_plaster2"));
	if (!SmokeMaterial)
	{
		SmokeMaterial = LoadObject<UMaterialInterface>(
			nullptr, TEXT("/Game/Skyguard/Materials/M_CityConcrete.M_CityConcrete"));
	}
	if (!HotMaterial)
	{
		HotMaterial = UMaterial::GetDefaultMaterial(MD_Surface);
	}
	if (!SmokeMaterial)
	{
		SmokeMaterial = UMaterial::GetDefaultMaterial(MD_Surface);
	}

	ExplosionMaterial = LoadObject<UMaterialInterface>(
		nullptr,
		TEXT("/Game/Skyguard/Materials/Generated/MI_ExplosionCore.MI_ExplosionCore"));
	if (!ExplosionMaterial)
	{
		ExplosionMaterial = HotMaterial;
	}

	FlakMaterial = LoadObject<UMaterialInterface>(
		nullptr,
		TEXT("/Game/Skyguard/Materials/Generated/MI_FlakFlash.MI_FlakFlash"));
	if (!FlakMaterial)
	{
		FlakMaterial = ExplosionMaterial;
	}

	TrailMaterial = LoadObject<UMaterialInterface>(
		nullptr,
		TEXT("/Game/Skyguard/Materials/Generated/MI_DroneTrail.MI_DroneTrail"));
	if (!TrailMaterial)
	{
		TrailMaterial = HotMaterial;
	}

	bAssetsPrewarmed = SphereMesh && ConeMesh && CylinderMesh &&
		HotMaterial && SmokeMaterial && ExplosionMaterial &&
		FlakMaterial && TrailMaterial;
}

void USkyguardCombatVFXPoolSubsystem::AllocatePool()
{
	if (Components.Num() > 0 || !GetWorld())
	{
		return;
	}

	Components.Reserve(PoolCapacity);
	ExpiryTimes.Reserve(PoolCapacity);
	ActiveSlots.Reserve(PoolCapacity);
	for (int32 Index = 0; Index < PoolCapacity; ++Index)
	{
		UStaticMeshComponent* Component = NewObject<UStaticMeshComponent>(
			this,
			*FString::Printf(TEXT("CombatVFXPool_%03d"), Index),
			RF_Transient);
		if (!Component)
		{
			continue;
		}

		Component->SetMobility(EComponentMobility::Movable);
		Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Component->SetGenerateOverlapEvents(false);
		Component->SetCanEverAffectNavigation(false);
		Component->SetCastShadow(false);
		Component->SetVisibility(false, true);
		Component->SetHiddenInGame(true, true);
		Component->RegisterComponentWithWorld(GetWorld());
		Components.Add(Component);
		ExpiryTimes.Add(0.0);
		ActiveSlots.Add(0);
	}
}

int32 USkyguardCombatVFXPoolSubsystem::AcquireSlot()
{
	if (Components.Num() == 0)
	{
		return INDEX_NONE;
	}

	for (int32 Offset = 0; Offset < Components.Num(); ++Offset)
	{
		const int32 Candidate = (NextSlot + Offset) % Components.Num();
		if (ActiveSlots.IsValidIndex(Candidate) && ActiveSlots[Candidate] == 0)
		{
			NextSlot = (Candidate + 1) % Components.Num();
			return Candidate;
		}
	}

	int32 EarliestSlot = 0;
	double EarliestExpiry = ExpiryTimes[0];
	for (int32 Index = 1; Index < ExpiryTimes.Num(); ++Index)
	{
		if (ExpiryTimes[Index] < EarliestExpiry)
		{
			EarliestExpiry = ExpiryTimes[Index];
			EarliestSlot = Index;
		}
	}
	ReleaseSlot(EarliestSlot);
	NextSlot = (EarliestSlot + 1) % Components.Num();
	++RecycleCount;
	return EarliestSlot;
}

void USkyguardCombatVFXPoolSubsystem::ReleaseSlot(const int32 SlotIndex)
{
	if (!Components.IsValidIndex(SlotIndex))
	{
		return;
	}
	if (UStaticMeshComponent* Component = Components[SlotIndex])
	{
		Component->SetVisibility(false, true);
		Component->SetHiddenInGame(true, true);
	}
	ActiveSlots[SlotIndex] = 0;
	ExpiryTimes[SlotIndex] = 0.0;
}

bool USkyguardCombatVFXPoolSubsystem::EmitMesh(
	UStaticMesh* Mesh,
	const FVector& Location,
	const FVector& Scale,
	const FRotator& Rotation,
	UMaterialInterface* Material,
	const float LifetimeSeconds)
{
	if (!Mesh || !GetWorld() || LifetimeSeconds <= 0.f ||
		Scale.GetMin() <= KINDA_SMALL_NUMBER)
	{
		return false;
	}

	const int32 SlotIndex = AcquireSlot();
	if (!Components.IsValidIndex(SlotIndex))
	{
		return false;
	}

	UStaticMeshComponent* Component = Components[SlotIndex];
	if (!Component)
	{
		return false;
	}

	Component->SetVisibility(false, true);
	Component->SetHiddenInGame(true, true);
	Component->SetStaticMesh(Mesh);
	Component->SetMaterial(0, Material);
	Component->SetWorldTransform(
		FTransform(Rotation, Location, Scale),
		false,
		nullptr,
		ETeleportType::TeleportPhysics);
	Component->SetHiddenInGame(false, true);
	Component->SetVisibility(true, true);

	ActiveSlots[SlotIndex] = 1;
	ExpiryTimes[SlotIndex] =
		static_cast<double>(GetWorld()->GetTimeSeconds()) +
		FMath::Max(0.05f, LifetimeSeconds);
	++ActivationCount;
	return true;
}

void USkyguardCombatVFXPoolSubsystem::Tick(const float DeltaTime)
{
	Super::Tick(DeltaTime);
	if (!GetWorld())
	{
		return;
	}

	const double Now = static_cast<double>(GetWorld()->GetTimeSeconds());
	for (int32 Index = 0; Index < ActiveSlots.Num(); ++Index)
	{
		if (ActiveSlots[Index] != 0 && ExpiryTimes[Index] <= Now)
		{
			ReleaseSlot(Index);
		}
	}
}

int32 USkyguardCombatVFXPoolSubsystem::GetActiveCount() const
{
	int32 Count = 0;
	for (const uint8 Active : ActiveSlots)
	{
		Count += Active != 0 ? 1 : 0;
	}
	return Count;
}

TStatId USkyguardCombatVFXPoolSubsystem::GetStatId() const
{
	RETURN_QUICK_DECLARE_CYCLE_STAT(
		USkyguardCombatVFXPoolSubsystem,
		STATGROUP_Tickables);
}

void USkyguardCombatVFXPoolSubsystem::Deinitialize()
{
	for (UStaticMeshComponent* Component : Components)
	{
		if (Component)
		{
			Component->DestroyComponent();
		}
	}
	Components.Reset();
	ExpiryTimes.Reset();
	ActiveSlots.Reset();
	SphereMesh = nullptr;
	ConeMesh = nullptr;
	CylinderMesh = nullptr;
	HotMaterial = nullptr;
	SmokeMaterial = nullptr;
	ExplosionMaterial = nullptr;
	FlakMaterial = nullptr;
	TrailMaterial = nullptr;
	bAssetsPrewarmed = false;
	Super::Deinitialize();
}
