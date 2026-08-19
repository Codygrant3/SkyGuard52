#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardRuntimeMeshCatalog.h"
#include "SkyguardProtectAsset.generated.h"

class UBoxComponent;
class UStaticMeshComponent;

/** Friendly hull the player must keep alive. */
UCLASS()
class SKYGUARD52_API ASkyguardProtectAsset : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardProtectAsset();

	virtual void BeginPlay() override;

	/** Empty Preferred; engine-primitive ProxyFallback. Not a catalog Preferred fill. */
	static FSkyguardMeshBindSlot MakeCargoHullBindSlot();

	/** Resolve ProxyFallback onto Hull. Safe with no authored mesh. Not for the CDO constructor. */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void BindCargoHull();

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	UStaticMeshComponent* GetHull() const { return Hull; }

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void ApplyDamage(float Amount);

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool IsDestroyed() const { return bDead; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	float GetIntegrityFraction() const;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void ResetIntegrity();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Campaign")
	float MaxIntegrity = 100.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Campaign")
	float CurrentIntegrity = 100.f;

protected:
	UPROPERTY(VisibleAnywhere)
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> Hull;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UBoxComponent> Volume;

	bool bDead = false;
};
