#pragma once

#include "CoreMinimal.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardBlackKiteBoss.generated.h"

class USkyguardBossWeakPointComponent;
class UStaticMeshComponent;

/** Mission 4 low-observable jammer boss governed by the BlackKite definition. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardBlackKiteBoss : public ASkyguardBossDroneBase
{
	GENERATED_BODY()

public:
	ASkyguardBlackKiteBoss();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission04|Boss")
	void SetSearchlightTracked(bool bTracked);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission04|Boss")
	bool ArmEmergencyRifleFinish();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission04|Boss")
	bool IsSearchlightTracked() const { return bSearchlightTracked; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission04|Boss")
	bool IsEmergencyRifleFinishArmed() const
	{
		return bEmergencyRifleFinishArmed;
	}

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission04|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> PortNavigationVane;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission04|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> StarboardNavigationVane;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission04|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> Jammer;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission04|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> PowerBus;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisPortVane;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisStarboardVane;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisJammer;

protected:
	virtual void HandleWeakPointDestroyed(
		USkyguardBossWeakPointComponent* WeakPoint,
		ESkyguardBossWeapon Weapon) override;

private:
	bool bSearchlightTracked = false;
	bool bEmergencyRifleFinishArmed = false;
};
