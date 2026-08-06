#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardDroneSpawner.generated.h"

UCLASS()
class SKYGUARD52_API ASkyguardDroneSpawner : public AActor
{
	GENERATED_BODY()
public:
	ASkyguardDroneSpawner();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard")
	float SpawnInterval = 1.35f;

protected:
	float SpawnTimer = 0.f;
};
