#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "SkyguardRuntimeMeshCatalog.generated.h"

class UStaticMesh;

/**
 * One governed mesh bind slot for runtime actors (Gunner / Drone / Yak).
 *
 * Preferred must only point at accepted or reversibly-staged content
 * (see AGENTS.md: do not import Blender candidates into accepted runtime
 * content until marked accepted). WebGame paths must never be Preferred;
 * they remain last-resort only when Preferred and ProxyFallback both fail.
 */
USTRUCT(BlueprintType)
struct FSkyguardMeshBindSlot
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Skyguard|MeshBind")
	FName SlotId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Skyguard|MeshBind")
	TSoftObjectPtr<UStaticMesh> Preferred;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Skyguard|MeshBind")
	TSoftObjectPtr<UStaticMesh> ProxyFallback;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Skyguard|MeshBind")
	FString Notes;
};

/**
 * Governed mesh resolution layer for reversible proxy rip-out.
 *
 * Content asset (optional): /Game/Skyguard/Data/DA_SkyguardRuntimeMeshCatalog
 * When the DataAsset is absent, ResolveDefaultSlot uses the same C++ defaults.
 */
UCLASS(BlueprintType)
class SKYGUARD52_API USkyguardRuntimeMeshCatalog : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	/** Soft path for the optional Content DataAsset (may be created later in editor). */
	static const TCHAR* DefaultCatalogAssetPath;

	UFUNCTION(BlueprintCallable, Category="Skyguard|MeshBind")
	void EnsureDefaultSlots();

	UFUNCTION(BlueprintPure, Category="Skyguard|MeshBind")
	UStaticMesh* ResolveMesh(FName SlotId) const;

	const FSkyguardMeshBindSlot* FindSlot(FName SlotId) const;

	/** Resolve using an in-memory slot (Preferred → ProxyFallback → WebGame last-resort). */
	static UStaticMesh* ResolveSlot(const FSkyguardMeshBindSlot& Slot);

	/**
	 * Resolve a code-default slot without loading the Content DataAsset.
	 * Safe for constructors via soft-path LoadSynchronous.
	 */
	UFUNCTION(BlueprintPure, Category="Skyguard|MeshBind")
	static UStaticMesh* ResolveDefaultSlot(FName SlotId);

	/** Ordered soft-path fallbacks; first valid existing mesh wins. */
	static UStaticMesh* ResolveOrderedSoftPaths(
		const TArray<FSoftObjectPath>& OrderedPaths,
		FName SlotIdForLastResortLog = NAME_None);

	static const TArray<FSkyguardMeshBindSlot>& GetCodeDefaultSlots();

	static FSoftObjectPath GetWebGameLastResortPath(FName SlotId);

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Skyguard|MeshBind")
	TArray<FSkyguardMeshBindSlot> Slots;

private:
	static void LogWebGameLastResortOnce(FName SlotId);
};
