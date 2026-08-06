#pragma once

#include "CoreMinimal.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardTempestBoss.generated.h"

class USkyguardBossWeakPointComponent;
class UStaticMeshComponent;

/** Mission 5 severe-weather boss governed by the Tempest definition. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardTempestBoss : public ASkyguardBossDroneBase
{
	GENERATED_BODY()

public:
	ASkyguardTempestBoss();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Boss")
	void SetLightningExposed(bool bExposed);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Boss")
	bool ApplyCorrectiveBankGust(float Turbulence);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Boss")
	bool AdvanceStabilizedIglaLock(float DeltaSeconds, float Turbulence);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission05|Boss")
	bool ArmBreakRifleFinish();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission05|Boss")
	bool IsLightningExposed() const { return bLightningExposed; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission05|Boss")
	float GetLockStabilitySeconds() const { return LockStabilitySeconds; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission05|Boss")
	bool IsBreakRifleFinishArmed() const
	{
		return bBreakRifleFinishArmed;
	}

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Skyguard|Mission05|Boss", meta=(ClampMin="0.1"))
	float RequiredLockStabilitySeconds = 2.5f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission05|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> PortDischargeBoom;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission05|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> StarboardDischargeBoom;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission05|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> ControlServo;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission05|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> EngineIntake;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisPortPanel;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisStarboardPanel;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisIntakePanel;

protected:
	virtual void HandleWeakPointDestroyed(
		USkyguardBossWeakPointComponent* WeakPoint,
		ESkyguardBossWeapon Weapon) override;

private:
	bool bLightningExposed = false;
	bool bCorrectiveBankExposed = false;
	bool bBreakRifleFinishArmed = false;
	float LockStabilitySeconds = 0.f;
};
