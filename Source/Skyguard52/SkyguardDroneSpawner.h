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

	UFUNCTION(BlueprintCallable, Category="Skyguard|Spawning")
	void SetSpawningEnabled(bool bEnabled);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Spawning")
	bool bSpawningEnabled = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard")
	float SpawnInterval = 1.85f;

	/** Refuse new spawns while this many live drones remain in the world. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard", meta=(ClampMin="1"))
	int32 MaxActiveDrones = 12;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Spawning")
	int32 HeavyLaneModulo = 4;

	/** When true, lanes mix aerial, rotor, boat, and armor threats. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Spawning")
	bool bMixedThreatRoster = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Spawning")
	float LightSpeedMin = 1300.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Spawning")
	float LightSpeedMax = 1750.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Spawning")
	float HeavyCruiseSpeed = 1150.f;

protected:
	float SpawnTimer = 0.f;

	int32 CountActiveDrones() const;
};
