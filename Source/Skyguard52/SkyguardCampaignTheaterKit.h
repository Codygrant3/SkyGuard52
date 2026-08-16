#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardCampaignTheaterKit.generated.h"

class UHierarchicalInstancedStaticMeshComponent;
class UMaterialInterface;
class UMeshComponent;
class UPointLightComponent;
class USceneComponent;
class UStaticMesh;
class UStaticMeshComponent;

/**
 * Restyle-in-place identity for one playable coastal map.
 * Keyed by roster WeatherIdentity — not a second weather system.
 */
USTRUCT(BlueprintType)
struct FSkyguardTheaterKitSpec
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FName WeatherIdentity;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FName KitId;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FName LandmarkSet;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FName BuildingKit;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FLinearColor BuildingTint = FLinearColor::White;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FName LampTreatment;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FLinearColor LampColor = FLinearColor::White;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	float LampIntensity = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FName RoadTreatment;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FLinearColor RoadTint = FLinearColor::White;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FName NamedLandmark;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FLinearColor LandmarkTint = FLinearColor::White;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FName SilhouetteKit;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FLinearColor SilhouetteTint = FLinearColor::White;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	int32 LandmarkMeshIndex = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FVector LandmarkScale = FVector(4.f, 4.f, 12.f);
};

namespace SkyguardCampaignTheaterKit
{
	int32 NumKits();
	const FSkyguardTheaterKitSpec& GetByIndex(int32 Index);
	const FSkyguardTheaterKitSpec& Resolve(FName WeatherIdentity);
	FString Fingerprint(const FSkyguardTheaterKitSpec& Spec);
	bool AreKitsPairwiseDistinct();
}

/**
 * One kit actor restyles the shared playable map per mission.
 * Roads, lamps, buildings, landmarks, and silhouette blocks change
 * in place. No unique umap. No imported art.
 */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardCampaignTheaterKit : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardCampaignTheaterKit();
	virtual void BeginPlay() override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Theater",
		meta=(WorldContext="WorldContextObject"))
	static void ApplyTheaterKitToWorld(
		UObject* WorldContextObject,
		FName WeatherIdentity);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Theater")
	void ApplyTheaterKit(FName WeatherIdentity);

	UFUNCTION(BlueprintPure, Category="Skyguard|Theater")
	FName GetAppliedWeatherIdentity() const { return AppliedSpec.WeatherIdentity; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Theater")
	FName GetAppliedKitId() const { return AppliedSpec.KitId; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Theater")
	FName GetNamedLandmark() const { return AppliedSpec.NamedLandmark; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Theater")
	FLinearColor GetBuildingTint() const { return AppliedSpec.BuildingTint; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Theater")
	const FSkyguardTheaterKitSpec& GetAppliedSpec() const { return AppliedSpec; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Theater")
	int32 GetRoadInstanceCount() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Theater")
	int32 GetBuildingInstanceCount() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Theater")
	int32 GetLampInstanceCount() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Theater")
	int32 GetSilhouetteInstanceCount() const;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	TObjectPtr<UHierarchicalInstancedStaticMeshComponent> RoadInstances;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	TObjectPtr<UHierarchicalInstancedStaticMeshComponent> BuildingInstances;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	TObjectPtr<UHierarchicalInstancedStaticMeshComponent> LampInstances;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	TObjectPtr<UHierarchicalInstancedStaticMeshComponent> SilhouetteInstances;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	TObjectPtr<UStaticMeshComponent> NamedLandmarkMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Theater")
	FSkyguardTheaterKitSpec AppliedSpec;

private:
	void RebuildDressing();
	void RestyleTaggedWorldActors() const;
	void ApplyTint(UMeshComponent* Component, const FLinearColor& Tint) const;
	void EnsureLamps();
	UStaticMesh* MeshForLandmark(int32 MeshIndex) const;
	static int32 CountInstances(const UHierarchicalInstancedStaticMeshComponent* Component);

	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> CubeMesh;

	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> CylinderMesh;

	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> ConeMesh;

	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> SphereMesh;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInterface> ShapeMaterial;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UPointLightComponent>> Lamps;
};
