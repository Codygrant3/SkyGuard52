#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardDrone.generated.h"

class ASkyguardYak52Aircraft;

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

	/** Ram / sweep contact with the player Yak -- applies collision damage then breaks up. */
	UFUNCTION(BlueprintCallable, Category="Skyguard")
	void ImpactAircraft(ASkyguardYak52Aircraft* Aircraft);

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

	/** Integrity subtracted from Yak on direct swept collision (light). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|AircraftDamage", meta=(ClampMin="0.0"))
	float AircraftCollisionDamage = 30.f;

	/** Integrity subtracted from Yak on direct swept collision (heavy). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|AircraftDamage", meta=(ClampMin="0.0"))
	float HeavyAircraftCollisionDamage = 50.f;

	/** Integrity splash when this drone breaks up near the Yak (light). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|AircraftDamage", meta=(ClampMin="0.0"))
	float AircraftExplosionDamage = 12.f;

	/** Integrity splash when this drone breaks up near the Yak (heavy). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|AircraftDamage", meta=(ClampMin="0.0"))
	float HeavyAircraftExplosionDamage = 20.f;

	/** Radius for breakup explosion splash onto nearby Yak airframes. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|AircraftDamage", meta=(ClampMin="0.0"))
	float AircraftExplosionRadiusCm = 600.f;

protected:
	bool bDead = false;
	bool bReachedCity = false;
	float Spin = 0.f;
	void Die(const FVector& HitDir, ASkyguardYak52Aircraft* AlreadyDamagedAircraft = nullptr);
	void ImpactCity(const FVector& ImpactDirection);
	void SpawnDebris(const FVector& HitDir);
	void ApplyVariantVisualsAndHealth();
	void DamageNearbyAircraft(
		float Amount,
		float RadiusCm,
		const ASkyguardYak52Aircraft* ExcludeAircraft = nullptr);
};
