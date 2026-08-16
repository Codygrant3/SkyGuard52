#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardMissionTypes.h"
#include "SkyguardCoastalEnvironmentDirector.generated.h"

class UHierarchicalInstancedStaticMeshComponent;
class USceneComponent;
class USkyguardEnvironmentVFXPoolComponent;
class UWindDirectionalSourceComponent;

UENUM(BlueprintType)
enum class ESkyguardEnvironmentQuality : uint8
{
	Low,
	Medium,
	High,
	Epic
};

USTRUCT(BlueprintType)
struct FSkyguardEnvironmentReadiness
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 BoundCapabilityCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 TreeInstanceCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 ShrubInstanceCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 VFXPoolSize = 0;
};

UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardCoastalEnvironmentDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardCoastalEnvironmentDirector();
	virtual void BeginPlay() override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Environment")
	void RebuildDeterministicVegetation();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Environment")
	void RefreshCapabilityBindings();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Environment")
	void ApplyQuality(ESkyguardEnvironmentQuality NewQuality);

	/** Drive existing wind from campaign weather — not a second weather engine. */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Environment")
	void ApplyMissionWeather(ESkyguardMissionWeather Weather);

	UFUNCTION(BlueprintPure, Category="Skyguard|Environment")
	ESkyguardMissionWeather GetAppliedWeather() const { return AppliedWeather; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Environment")
	bool IsVegetationOutsideRouteCorridor() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Environment")
	const FSkyguardEnvironmentReadiness& GetReadiness() const { return Readiness; }

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Environment")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Environment|Vegetation")
	TObjectPtr<UHierarchicalInstancedStaticMeshComponent> TreeInstances;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Environment|Vegetation")
	TObjectPtr<UHierarchicalInstancedStaticMeshComponent> ShrubInstances;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Environment|Wind")
	TObjectPtr<UWindDirectionalSourceComponent> WindSource;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Environment|VFX")
	TObjectPtr<USkyguardEnvironmentVFXPoolComponent> VFXPool;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|Vegetation")
	ESkyguardEnvironmentQuality Quality = ESkyguardEnvironmentQuality::High;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|Vegetation")
	int32 PlacementSeed = 5201;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|Vegetation", meta=(ClampMin="0", ClampMax="1024"))
	int32 EpicTreeBudget = 240;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|Vegetation", meta=(ClampMin="0", ClampMax="2048"))
	int32 EpicShrubBudget = 480;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|Route", meta=(ClampMin="1000.0"))
	float RouteLengthCm = 45000.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|Route", meta=(ClampMin="100.0"))
	float RouteCorridorHalfWidthCm = 2800.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|Coast", meta=(ClampMin="0.0"))
	float ShorelineLandOffsetCm = 5200.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|Coast", meta=(ClampMin="1000.0"))
	float InlandExtentCm = 16000.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|Performance", meta=(ClampMin="1000"))
	int32 VegetationStartCullDistanceCm = 8000;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|Performance", meta=(ClampMin="2000"))
	int32 VegetationEndCullDistanceCm = 32000;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|Wind", meta=(ClampMin="0.0", ClampMax="1.0"))
	float WindStrength = 0.35f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|Wind", meta=(ClampMin="0.0", ClampMax="1.0"))
	float WindSpeed = 0.5f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Environment")
	FSkyguardEnvironmentReadiness Readiness;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Environment|Weather")
	ESkyguardMissionWeather AppliedWeather = ESkyguardMissionWeather::Clear;

private:
	float GetQualityMultiplier() const;
	void PlaceInstances(
		UHierarchicalInstancedStaticMeshComponent* Component,
		int32 Count,
		FRandomStream& Random,
		float ScaleMin,
		float ScaleMax);
};
