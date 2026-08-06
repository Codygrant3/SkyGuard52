#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardMission01EnvironmentDirector.generated.h"

class UBoxComponent;
class UHierarchicalInstancedStaticMeshComponent;
class UMaterialInterface;
class UPCGComponent;
class UPCGGraphInterface;
class USceneComponent;
class UExponentialHeightFogComponent;
class ALandscapeProxy;

USTRUCT(BlueprintType)
struct FSkyguardMission01EnvironmentReadiness
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 OceanTileCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 BeachTileCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 LandTileCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bAuthoredLandscapeSurfaceExposed = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bContinuousCoastline = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bRouteExclusionValid = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 LandscapeComponentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bProductionLandscapeBound = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bAuthoredPCGGraphBound = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bPCGBoundsTagged = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bAuthoredPCGStructureReady = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bLicensedVegetationApproved = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bPCGGenerationAuthorized = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bReadyForAuthoredPCGGeneration = false;
};

/**
 * Stable Mission 1 coastline composition.
 *
 * This intentionally uses engine static-mesh/HISM primitives and ordinary
 * materials. It has no dependency on the UE 5.8 experimental Landmass,
 * Volumetrics or Water plugin chain that destabilized the prior candidate.
 * Its inclusion and exclusion volumes are an explicit handoff boundary for
 * an authored PCG graph.
 */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardMission01EnvironmentDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardMission01EnvironmentDirector();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void OnConstruction(const FTransform& Transform) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Environment")
	void RebuildProductionLayout();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Environment")
	bool IsPointAllowedForPCG(const FVector& WorldPoint) const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Environment")
	bool IsRouteExclusionSafe() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Environment")
	bool HasContinuousCoastline() const;

	/**
	 * Candidate-only validation switch. This removes the legacy inland HISM
	 * slabs so the real imported Landscape is the only inland ground surface.
	 * It does not alter OceanTiles, BeachTiles, PCG state, or the v5 default.
	 */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Environment|Landscape")
	void SetUseAuthoredLandscapeSurfaceForValidation(bool bEnable);

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Environment|Landscape")
	bool IsAuthoredLandscapeSurfaceExposed() const
	{
		return bUseAuthoredLandscapeSurface && Readiness.LandTileCount == 0;
	}

	/**
	 * Refresh the serialized Landscape/PCG handoff. This never generates content.
	 * Generation remains fail-closed until a valid imported Landscape and the
	 * governed authored graph are both assigned.
	 */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission01|Environment|PCG")
	void RefreshAuthoredEnvironmentBindings();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Environment|PCG")
	bool IsAuthoredEnvironmentReady() const
	{
		return Readiness.bAuthoredPCGStructureReady;
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Environment|PCG")
	bool IsPCGGenerationAuthorized() const
	{
		return Readiness.bReadyForAuthoredPCGGeneration;
	}

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Environment")
	const FSkyguardMission01EnvironmentReadiness& GetReadiness() const { return Readiness; }

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01|Environment")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01|Environment")
	TObjectPtr<UHierarchicalInstancedStaticMeshComponent> OceanTiles;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01|Environment")
	TObjectPtr<UHierarchicalInstancedStaticMeshComponent> BeachTiles;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01|Environment")
	TObjectPtr<UHierarchicalInstancedStaticMeshComponent> LandTiles;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01|Environment|PCG")
	TObjectPtr<UBoxComponent> RouteExclusion;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01|Environment|PCG")
	TObjectPtr<UBoxComponent> LandScatterBounds;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01|Environment|PCG")
	TObjectPtr<UPCGComponent> InlandVegetationPCG;

	/**
	 * The imported production Landscape for Mission 1. It must carry
	 * Skyguard.Environment.Mission01.Landscape and contain registered Landscape
	 * components before the PCG component can activate.
	 */
	UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Landscape")
	TObjectPtr<ALandscapeProxy> ProductionLandscape;

	/**
	 * Governed graph path:
	 * /Game/Skyguard/Environment/Mission01/PCG/PCG_M01_InlandVegetation
	 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|PCG")
	TSoftObjectPtr<UPCGGraphInterface> AuthoredPCGGraph;

	/** Must remain false until immutable license/provenance evidence is accepted. */
	UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|PCG")
	bool bLicensedVegetationLibraryApproved = false;

	/** Explicit production authorization; never implied by a valid graph. */
	UPROPERTY(EditInstanceOnly, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|PCG")
	bool bAllowAuthoredPCGGeneration = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Layout", meta=(ClampMin="10000.0"))
	float RouteLengthCm = 45000.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Layout", meta=(ClampMin="1000.0"))
	float DistrictLengthCm = 7500.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Layout", meta=(ClampMin="100.0"))
	float RouteCorridorHalfWidthCm = 2800.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Layout", meta=(ClampMin="100.0"))
	float ShorelineLandOffsetCm = 5200.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Layout", meta=(ClampMin="100.0"))
	float BeachWidthCm = 1800.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Layout", meta=(ClampMin="1000.0"))
	float InlandExtentCm = 18000.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Layout", meta=(ClampMin="1000.0"))
	float SeawardExtentCm = 20000.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Materials")
	TObjectPtr<UMaterialInterface> OceanMaterial;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Materials")
	TObjectPtr<UMaterialInterface> BeachMaterial;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Materials")
	TObjectPtr<UMaterialInterface> LandMaterial;

	/**
	 * False preserves the accepted v5 layout. Only immutable Landscape visible
	 * review candidates may set this true.
	 */
	UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category="Skyguard|Mission01|Environment|Landscape")
	bool bUseAuthoredLandscapeSurface = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission01|Environment")
	FSkyguardMission01EnvironmentReadiness Readiness;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Visibility")
	bool bEnableCoastalHazeTransition = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Visibility", meta=(ClampMin="5.0"))
	float CoastalHazeDelaySeconds = 30.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Visibility", meta=(ClampMin="1.0"))
	float CoastalHazeFadeSeconds = 8.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Visibility", meta=(ClampMin="1.0"))
	float CoastalHazeHoldSeconds = 12.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Mission01|Environment|Visibility", meta=(ClampMin="0.001", ClampMax="0.1"))
	float CoastalHazeDensityIncrease = 0.018f;

private:
	void ConfigureInstanceComponent(UHierarchicalInstancedStaticMeshComponent* Component) const;
	void AddDistrictInstances(int32 DistrictCount);

	TWeakObjectPtr<UExponentialHeightFogComponent> RuntimeFogComponent;
	float RuntimeBaseFogDensity = 0.f;
	float RuntimeVisibilityElapsedSeconds = 0.f;
	bool bVisibilityTransitionRecorded = false;
};
