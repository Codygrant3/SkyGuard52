#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardMissionMapAssemblyDirector.generated.h"

class USceneComponent;
class USkyguardMissionDefinition;
class USplineComponent;

UENUM(BlueprintType)
enum class ESkyguardMissionSkylineStyle : uint8
{
	HarborIndustrial,
	CoastalHighway,
	BlackoutUrban,
	OffshoreStorm,
	AirfieldMilitary,
	IslandSearch
};

USTRUCT(BlueprintType)
struct FSkyguardMissionObjectiveAnchor
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName ObjectiveId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FVector WorldLocation = FVector::ZeroVector;
};

USTRUCT(BlueprintType)
struct FSkyguardMissionLandmarkAnchor
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName LandmarkId;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FName Role;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	FVector WorldLocation = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadOnly)
	bool bMissionExclusive = false;
};

USTRUCT(BlueprintType)
struct FSkyguardMissionMapReadiness
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bDefinitionValid = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bRouteMatchesDefinition = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bRequiredObjectivesAnchored = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bLandmarksDistinct = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	bool bWeatherMatchesDefinition = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 RoutePointCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 ObjectiveAnchorCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 LandmarkCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	int32 MissionExclusiveLandmarkCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	float RouteLengthCentimeters = 0.f;
};

/**
 * Native integrity boundary for authored campaign maps.
 *
 * The director binds a persisted USkyguardMissionDefinition to map-local route,
 * objective and landmark anchors. It deliberately does not generate final art.
 */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardMissionMapAssemblyDirector : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardMissionMapAssemblyDirector();
	virtual void OnConstruction(const FTransform& Transform) override;

	UFUNCTION(BlueprintCallable, Category = "Skyguard|MissionMap")
	void RebuildRouteSpline();

	UFUNCTION(BlueprintCallable, Category = "Skyguard|MissionMap")
	bool ValidateAssembly(TArray<FText>& OutErrors);

	UFUNCTION(BlueprintPure, Category = "Skyguard|MissionMap")
	bool IsPointInsideFlightClearance(const FVector& WorldPoint) const;

	UFUNCTION(BlueprintPure, Category = "Skyguard|MissionMap")
	const FSkyguardMissionMapReadiness& GetReadiness() const { return Readiness; }

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Skyguard|MissionMap")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Skyguard|MissionMap")
	TObjectPtr<USplineComponent> FlightRouteSpline;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skyguard|MissionMap")
	TObjectPtr<USkyguardMissionDefinition> MissionDefinition;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skyguard|MissionMap")
	FName MissionId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skyguard|MissionMap")
	FName AssemblyRevision = TEXT("CampaignMapAssembly_v1");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skyguard|MissionMap")
	ESkyguardMissionSkylineStyle SkylineStyle =
		ESkyguardMissionSkylineStyle::HarborIndustrial;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skyguard|MissionMap")
	FName WeatherProfileId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skyguard|MissionMap")
	TArray<FVector> RoutePoints;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skyguard|MissionMap")
	TArray<FSkyguardMissionObjectiveAnchor> ObjectiveAnchors;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skyguard|MissionMap")
	TArray<FSkyguardMissionLandmarkAnchor> LandmarkAnchors;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skyguard|MissionMap", meta = (ClampMin = "500.0"))
	float FlightClearanceRadiusCentimeters = 3000.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skyguard|MissionMap", meta = (ClampMin = "500.0"))
	float FlightClearanceVerticalCentimeters = 2500.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Skyguard|MissionMap")
	FSkyguardMissionMapReadiness Readiness;

private:
	float CalculateRouteLength() const;
};
