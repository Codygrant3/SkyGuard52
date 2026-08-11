#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "SkyguardCombatVFXPoolSubsystem.generated.h"

class UMaterialInterface;
class UStaticMesh;
class UStaticMeshComponent;

/**
 * Fixed, world-lifetime pool for the transitional combat mesh effects.
 *
 * Assets and components are prepared when the game world is initialized. The
 * firing, impact and breakup paths only recycle existing components; they do
 * not synchronously load packages, spawn actors or grow the pool.
 */
UCLASS()
class SKYGUARD52_API USkyguardCombatVFXPoolSubsystem : public UTickableWorldSubsystem
{
	GENERATED_BODY()

public:
	static constexpr int32 PoolCapacity = 192;

	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;
	virtual void Tick(float DeltaTime) override;
	virtual TStatId GetStatId() const override;

	bool EmitMesh(
		UStaticMesh* Mesh,
		const FVector& Location,
		const FVector& Scale,
		const FRotator& Rotation,
		UMaterialInterface* Material,
		float LifetimeSeconds);

	UStaticMesh* GetSphereMesh() const { return SphereMesh; }
	UStaticMesh* GetConeMesh() const { return ConeMesh; }
	UStaticMesh* GetCylinderMesh() const { return CylinderMesh; }
	UMaterialInterface* GetHotMaterial() const { return HotMaterial; }
	UMaterialInterface* GetSmokeMaterial() const { return SmokeMaterial; }
	UMaterialInterface* GetExplosionMaterial() const { return ExplosionMaterial; }
	UMaterialInterface* GetFlakMaterial() const { return FlakMaterial; }
	UMaterialInterface* GetTrailMaterial() const { return TrailMaterial; }

	int32 GetAllocatedCount() const { return Components.Num(); }
	int32 GetActiveCount() const;
	int32 GetActivationCount() const { return ActivationCount; }
	int32 GetRecycleCount() const { return RecycleCount; }
	bool IsPrewarmed() const { return bAssetsPrewarmed && Components.Num() == PoolCapacity; }

protected:
	virtual bool DoesSupportWorldType(EWorldType::Type WorldType) const override;

private:
	void PrewarmAssets();
	void AllocatePool();
	int32 AcquireSlot();
	void ReleaseSlot(int32 SlotIndex);

	UPROPERTY(Transient)
	TArray<TObjectPtr<UStaticMeshComponent>> Components;

	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> SphereMesh;

	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> ConeMesh;

	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> CylinderMesh;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInterface> HotMaterial;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInterface> SmokeMaterial;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInterface> ExplosionMaterial;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInterface> FlakMaterial;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInterface> TrailMaterial;

	TArray<double> ExpiryTimes;
	TArray<uint8> ActiveSlots;
	int32 NextSlot = 0;
	int32 ActivationCount = 0;
	int32 RecycleCount = 0;
	bool bAssetsPrewarmed = false;
};
