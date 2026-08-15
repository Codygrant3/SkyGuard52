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

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void ApplyDamage(float Amount);

	UFUNCTION(BlueprintPure, Category="Skyguard|Campaign")
	bool IsDestroyed() const { return bDead; }

	UFUNCTION(BlueprintCallable, Category="Skyguard|Campaign")
	void ResetNode();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Campaign")
	float MaxHealth = 160.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Campaign")
	float Health = 160.f;

protected:
	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> Body;

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> Dish;

	bool bDead = false;
};
