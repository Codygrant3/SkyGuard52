#pragma once

#include "CoreMinimal.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardRoadHunterBoss.generated.h"

class USkyguardBossWeakPointComponent;
class UStaticMeshComponent;

/** Mission 3 crossing-attack boss with bilateral actuator exposure. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardRoadHunterBoss : public ASkyguardBossDroneBase
{
	GENERATED_BODY()

public:
	ASkyguardRoadHunterBoss();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission03|Boss")
	bool ArmEmergencyRifleFinish();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission03|Boss")
	bool IsEmergencyRifleFinishArmed() const
	{
		return bEmergencyRifleFinishArmed;
	}

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission03|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> TargetingCamera;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission03|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> LeftActuator;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission03|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> RightActuator;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission03|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> Engine;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisLeftWing;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisEngine;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisRightWing;

protected:
	virtual void HandleWeakPointDestroyed(
		USkyguardBossWeakPointComponent* WeakPoint,
		ESkyguardBossWeapon Weapon) override;

private:
	bool bEmergencyRifleFinishArmed = false;
};
