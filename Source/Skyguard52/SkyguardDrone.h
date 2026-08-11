#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardDrone.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(
	FSkyguardDroneCityImpactSignature,
	ASkyguardDrone*,
	Drone);

DECLARE_MULTICAST_DELEGATE_OneParam(
	FSkyguardDroneCityImpactNative,
	ASkyguardDrone*);

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

	UFUNCTION(BlueprintPure, Category="Skyguard")
	bool HasReachedCity() const { return bReachedCity; }

	UFUNCTION(BlueprintPure, Category="Skyguard")
	bool IsDestroyed() const { return bDead; }

	/** Apply heavy/light variant after spawn (safe before or after BeginPlay). */
	UFUNCTION(BlueprintCallable, Category="Skyguard")
	void ConfigureVariant(bool bInHeavy);

	/** Per-actor protect-fail signal when this drone impacts the city. */
	UPROPERTY(BlueprintAssignable, Category="Skyguard")
	FSkyguardDroneCityImpactSignature OnCityImpacted;

	/** Native fan-out for mission directors without per-actor binds. */
	static FSkyguardDroneCityImpactNative OnAnyCityImpacted;

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
	bool bReachedCity = false;
	float Spin = 0.f;
	void Die(const FVector& HitDir);
	void ImpactCity(const FVector& ImpactDirection);
	void SpawnDebris(const FVector& HitDir);
	void ApplyVariantVisualsAndHealth();
};
