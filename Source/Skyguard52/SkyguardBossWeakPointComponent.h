#pragma once

#include "CoreMinimal.h"
#include "Components/StaticMeshComponent.h"
#include "SkyguardBossTypes.h"
#include "SkyguardBossWeakPointComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(
	FSkyguardWeakPointStateEvent,
	FName, WeakPointId,
	ESkyguardBossWeapon, Weapon,
	float, RemainingIntegrity);

UCLASS(ClassGroup=(Skyguard), meta=(BlueprintSpawnableComponent))
class SKYGUARD52_API USkyguardBossWeakPointComponent : public UStaticMeshComponent
{
	GENERATED_BODY()

public:
	USkyguardBossWeakPointComponent();
	virtual void BeginPlay() override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Boss")
	bool ApplyWeaponDamage(ESkyguardBossWeapon Weapon, float Damage);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Boss")
	void SetExposed(bool bNewExposed);

	UFUNCTION(BlueprintPure, Category="Skyguard|Boss")
	bool AcceptsWeapon(ESkyguardBossWeapon Weapon) const;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss")
	FName WeakPointId = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss", meta=(ClampMin="1.0"))
	float MaxIntegrity = 100.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss")
	float Integrity = 100.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss")
	bool bExposed = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss")
	bool bAcceptsRifle = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss")
	bool bAcceptsIgla = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss")
	bool bDestroyed = false;

	UPROPERTY(BlueprintAssignable, Category="Skyguard|Boss")
	FSkyguardWeakPointStateEvent OnWeakPointDamaged;

	UPROPERTY(BlueprintAssignable, Category="Skyguard|Boss")
	FSkyguardWeakPointStateEvent OnWeakPointDestroyed;
};
