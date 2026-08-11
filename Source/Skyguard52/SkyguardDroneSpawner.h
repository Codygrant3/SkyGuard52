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

	/** Refuse new spawns while this many live drones remain in the world. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard", meta=(ClampMin="1"))
	int32 MaxActiveDrones = 24;

protected:
	float SpawnTimer = 0.f;

	int32 CountActiveDrones() const;
};
