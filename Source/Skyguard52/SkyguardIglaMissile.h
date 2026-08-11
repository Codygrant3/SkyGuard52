#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardIglaMissile.generated.h"

class USphereComponent;
class UStaticMeshComponent;

UCLASS()
class SKYGUARD52_API ASkyguardIglaMissile : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardIglaMissile();

	virtual void Tick(float DeltaSeconds) override;

	void InitializeMissile(AActor* InTarget, float InDamage, const FVector& InitialDirection);

	UFUNCTION(BlueprintPure, Category="Skyguard|Igla")
	AActor* GetTargetActor() const { return TargetActor.Get(); }

	UFUNCTION(BlueprintPure, Category="Skyguard|Igla")
	bool IsArmed() const { return bArmed; }

	/**
	 * Returns whether a blocking impact should damage the locked target.
	 * Direct hits on the lock or nearby proximity impacts qualify; distant
	 * world/terrain clips do not.
	 */
	UFUNCTION(BlueprintPure, Category="Skyguard|Igla")
	bool ShouldDamageLockedTargetOnImpact(
		const FVector& ImpactPoint,
		const AActor* HitActor) const;

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Igla")
	TObjectPtr<USphereComponent> Collision;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Igla")
	TObjectPtr<UStaticMeshComponent> MissileMesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Igla")
	float Speed = 7200.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Igla")
	float TurnRateDegreesPerSecond = 95.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Igla")
	float ProximityFuseCentimeters = 180.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Igla")
	float ArmDelaySeconds = 0.12f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Igla")
	float MaximumFlightSeconds = 8.f;

private:
	/**
	 * Detonates at ImpactPoint. Damage is applied only to DamageTarget when it
	 * is a boss/drone; null skips damage (terrain self-destruct / miss).
	 */
	void Detonate(const FVector& ImpactPoint, AActor* DamageTarget);

	TWeakObjectPtr<AActor> TargetActor;
	FVector Velocity = FVector::ForwardVector;
	float Damage = 160.f;
	float FlightSeconds = 0.f;
	bool bArmed = false;
	bool bDetonated = false;
};
