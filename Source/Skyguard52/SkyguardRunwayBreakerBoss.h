#pragma once

#include "CoreMinimal.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardRunwayBreakerBoss.generated.h"

class USkyguardBossWeakPointComponent;
class UStaticMeshComponent;

/** Mission 6 payload-carrier boss, governed by the RunwayBreaker definition. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardRunwayBreakerBoss : public ASkyguardBossDroneBase
{
	GENERATED_BODY()

public:
	ASkyguardRunwayBreakerBoss();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission06|Boss")
	bool ArmEmergencyRifleFinish();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission06|Boss")
	bool IsEmergencyRifleFinishArmed() const
	{
		return bEmergencyRifleFinishArmed;
	}

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission06|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> RunwayRack;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission06|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> HangarRack;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission06|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> HeatManifold;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission06|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> PortEngine;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisPortWing;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisPayloadBay;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisEngine;

protected:
	virtual void HandleWeakPointDestroyed(
		USkyguardBossWeakPointComponent* WeakPoint,
		ESkyguardBossWeapon Weapon) override;

private:
	bool bEmergencyRifleFinishArmed = false;
};
