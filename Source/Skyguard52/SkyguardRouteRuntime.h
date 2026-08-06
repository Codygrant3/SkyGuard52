#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "SkyguardMissionTypes.h"
#include "SkyguardRouteRuntime.generated.h"

UCLASS(BlueprintType)
class SKYGUARD52_API USkyguardRouteRuntime : public UObject
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Mission|Route")
	bool InitializeRoute(const FSkyguardRouteDefinition& Definition);

	UFUNCTION(BlueprintPure, Category = "Mission|Route")
	FVector SampleLocationByDistance(float DistanceCentimeters) const;

	UFUNCTION(BlueprintPure, Category = "Mission|Route")
	float GetRouteLength() const { return TotalLength; }

private:
	UPROPERTY()
	FSkyguardRouteDefinition Route;

	UPROPERTY()
	TArray<float> CumulativeDistances;

	UPROPERTY()
	float TotalLength = 0.f;
};
