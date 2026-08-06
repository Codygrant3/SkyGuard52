#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardDrone.generated.h"

UCLASS()
class SKYGUARD52_API ASkyguardDrone : public AActor
{
	GENERATED_BODY()
public:
	ASkyguardDrone();
	virtual void Tick(float DeltaSeconds) override;
	virtual void BeginPlay() override;
	virtual void LifeSpanExpired() override;

	UFUNCTION(BlueprintCallable, Category="Skyguard")
	void ApplyBallisticHit(float Damage, FVector HitLocation, FVector HitDirection);

	UFUNCTION(BlueprintCallable, Category="Skyguard")
	bool IsHeavyTarget() const { return bHeavy; }

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	TObjectPtr<UStaticMeshComponent> Body;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	TObjectPtr<UStaticMeshComponent> Wing;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	TObjectPtr<UStaticMeshComponent> Exhaust;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard")
	float MaxHealth = 34.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard")
	float Health = 34.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard")
	float CruiseSpeed = 1600.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard")
	FVector TargetCityLocation = FVector(-1800.f, 0.f, 350.f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard")
	bool bHeavy = false;

protected:
	bool bDead = false;
	float Spin = 0.f;
	void Die(const FVector& HitDir);
	void SpawnDebris(const FVector& HitDir);
};
