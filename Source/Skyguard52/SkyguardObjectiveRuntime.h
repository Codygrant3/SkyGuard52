#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "SkyguardMissionTypes.h"
#include "SkyguardObjectiveRuntime.generated.h"

UCLASS(BlueprintType)
class SKYGUARD52_API USkyguardObjectiveRuntime : public UObject
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Mission|Objectives")
	void InitializeObjectives(const TArray<FSkyguardObjectiveDefinition>& Definitions);

	UFUNCTION(BlueprintCallable, Category = "Mission|Objectives")
	bool AddProgress(FName ObjectiveId, int32 Amount = 1);

	UFUNCTION(BlueprintCallable, Category = "Mission|Objectives")
	bool FailObjective(FName ObjectiveId);

	UFUNCTION(BlueprintPure, Category = "Mission|Objectives")
	bool AreRequiredObjectivesComplete() const;

	UFUNCTION(BlueprintPure, Category = "Mission|Objectives")
	bool HasTerminalFailure() const;

	UFUNCTION(BlueprintPure, Category = "Mission|Objectives")
	FSkyguardObjectiveProgress GetProgress(FName ObjectiveId) const;

	UFUNCTION(BlueprintPure, Category = "Mission|Objectives")
	TArray<FName> GetCompletedObjectiveIds() const;

private:
	UPROPERTY()
	TArray<FSkyguardObjectiveDefinition> AuthoredDefinitions;

	UPROPERTY()
	TMap<FName, FSkyguardObjectiveProgress> RuntimeProgress;
};
