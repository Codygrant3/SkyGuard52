#pragma once

#include "CoreMinimal.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardLifelineHunterBoss.generated.h"

class USkyguardBossWeakPointComponent;
class UStaticMeshComponent;

/** Mission 8 rescue-zone boss with explicit friendly-separation safety. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardLifelineHunterBoss
	: public ASkyguardBossDroneBase
{
	GENERATED_BODY()

public:
	ASkyguardLifelineHunterBoss();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Boss")
	bool OpenSensorExposure();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Boss")
	void SetFriendlySeparationMeters(float SeparationMeters);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Boss")
	bool OpenSafeIglaWindow();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Boss")
	bool ArmSafeRifleEngineFallback();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission08|Boss")
	bool RedirectDisabledDrone();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission08|Boss")
	bool IsDisabledDescent() const { return bDisabledDescent; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission08|Boss")
	bool IsCrashRedirected() const { return bCrashRedirected; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission08|Boss")
	float GetFriendlySeparationMeters() const
	{
		return FriendlySeparationMeters;
	}

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Skyguard|Mission08|Safety", meta=(ClampMin="1.0"))
	float MinimumWeaponSeparationMeters = 450.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> OpticalTracker;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> WeaponServo;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> CountermeasurePod;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission08|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> Engine;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisPrimarySensor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisSecondarySensor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisControlSurface;

protected:
	virtual void HandleWeakPointDestroyed(
		USkyguardBossWeakPointComponent* WeakPoint,
		ESkyguardBossWeapon Weapon) override;

private:
	float FriendlySeparationMeters = 0.f;
	bool bSafeRifleFallbackArmed = false;
	bool bDisabledDescent = false;
	bool bCrashRedirected = false;
};
