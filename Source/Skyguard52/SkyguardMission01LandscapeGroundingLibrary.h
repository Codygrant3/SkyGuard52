#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "SkyguardMission01LandscapeGroundingLibrary.generated.h"

class ALandscapeProxy;

/** One immutable, read-only world-space height query against a Landscape. */
USTRUCT(BlueprintType)
struct FSkyguardLandscapeHeightSample
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bValid = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FVector QueryLocation = FVector::ZeroVector;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float HeightCentimeters = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FString HeightfieldSource;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FString Error;
};

/**
 * Complete footprint evidence for a governed placement query.
 *
 * The authoring contract permits exactly five samples for small props/trees,
 * nine for buildings, and thirteen for road or shoreline modules. Every
 * requested XY location must be unique and supported for the result to pass.
 */
USTRUCT(BlueprintType)
struct FSkyguardLandscapeFootprintSampleResult
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bSuccess = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 RequiredSampleCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 ValidSampleCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float SupportedFraction = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float MinimumHeightCentimeters = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float MaximumHeightCentimeters = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float MeanHeightCentimeters = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float HeightDeltaCentimeters = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	TArray<FSkyguardLandscapeHeightSample> Samples;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	FString Error;
};

/**
 * Read-only Mission 1 Landscape grounding bridge for Unreal Python and
 * Blueprint authoring. It never moves actors, modifies Landscape state, saves
 * packages, or falls back to hard-coded Z constants.
 */
UCLASS()
class SKYGUARD52_API USkyguardMission01LandscapeGroundingLibrary final
	: public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Samples one world-space location using UE 5.8's editor heightfield. */
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Environment|Grounding")
	static FSkyguardLandscapeHeightSample SampleLandscapeHeight(
		ALandscapeProxy* Landscape,
		const FVector& WorldLocation);

	/**
	 * Samples exactly 5, 9, or 13 unique footprint locations. Success requires
	 * 100 percent support and finite heights for the entire footprint.
	 */
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission01|Environment|Grounding")
	static FSkyguardLandscapeFootprintSampleResult SampleLandscapeFootprint(
		ALandscapeProxy* Landscape,
		const TArray<FVector>& WorldLocations);
};
