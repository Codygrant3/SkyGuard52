#pragma once

#include "CoreMinimal.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardBreakwaterBoss.generated.h"

class USkyguardBossWeakPointComponent;
class UStaticMeshComponent;

/**
 * Mission 2's deterministic armored-drone encounter.
 *
 * Port latch -> starboard latch -> decoy pods exposes the Igla engine window.
 * A successful missile then exposes the elevator linkage for a rifle finish.
 * If no missile is available, an orbit command may expose the same linkage as
 * a harder emergency rifle-only route.
 */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardBreakwaterBoss : public ASkyguardBossDroneBase
{
	GENERATED_BODY()

public:
	ASkyguardBreakwaterBoss();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission02|Boss")
	bool ArmEmergencyRifleFinish();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission02|Boss")
	bool IsEmergencyRifleFinishArmed() const
	{
		return bEmergencyRifleFinishArmed;
	}

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission02|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> PortLatch;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission02|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> StarboardLatch;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission02|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> DecoyPods;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission02|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> Engine;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission02|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> ElevatorLinkage;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisPortPanel;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisEngine;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisStarboardPanel;

protected:
	virtual void HandleWeakPointDestroyed(
		USkyguardBossWeakPointComponent* WeakPoint,
		ESkyguardBossWeapon Weapon) override;

private:
	bool bEmergencyRifleFinishArmed = false;
};
