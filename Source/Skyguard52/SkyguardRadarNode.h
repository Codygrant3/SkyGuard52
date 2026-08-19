#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardRadarNode.generated.h"

class UStaticMeshComponent;

/** Kill this to slow enemy air defenses. */
UCLASS()
class SKYGUARD52_API ASkyguardRadarNode : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardRadarNode();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void ApplyDamage(float Amount);

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool IsDestroyed() const { return bDead; }

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void ResetNode();

	/**
	 * Bind van/dish meshes from catalog ProxyFallback or engine primitives.
	 * Preferred stays empty. Not invoked from the CDO constructor.
	 */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void BindPresentation();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void SetPresentationEnabled(bool bEnabled);

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool IsPresentationEnabled() const { return bPresentationEnabled; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	UStaticMeshComponent* GetBody() const { return Body; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	UStaticMeshComponent* GetDish() const { return Dish; }

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Campaign")
	float MaxHealth = 160.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Campaign")
	float Health = 160.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Campaign")
	float DishSpinDegreesPerSecond = 45.f;

protected:
	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> Body;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> Dish;

	bool bDead = false;
	bool bPresentationEnabled = true;

	void ApplyPresentationVisibility();
};
