#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "SkyguardGameMode.generated.h"

UCLASS()
class SKYGUARD52_API ASkyguardGameMode : public AGameModeBase
{
	GENERATED_BODY()
public:
	ASkyguardGameMode();

protected:
	virtual void BeginPlay() override;
	virtual APawn* SpawnDefaultPawnAtTransform_Implementation(
		AController* NewPlayer,
		const FTransform& SpawnTransform) override;

private:
	void CompleteStartupSmoke();
	bool WriteStartupSmokeReceipt(const TCHAR* State) const;
	void RunPackagedRuntimeValidation();

	FTimerHandle StartupSmokeTimer;
	FTimerHandle RuntimeValidationTimer;
	FString StartupSmokeReceiptPath;
	FString StartupSmokeMapName;
	FString RuntimeValidationArtifactPath;
	int32 RuntimeValidationPhase = 0;
};
