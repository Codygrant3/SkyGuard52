#pragma once

#include "CoreMinimal.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardRadarGhostBoss.generated.h"

class USkyguardBossWeakPointComponent;
class UStaticMeshComponent;

/** Mission 7 electronic-warfare boss governed by the RadarGhost definition. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardRadarGhostBoss : public ASkyguardBossDroneBase
{
	GENERATED_BODY()

public:
	ASkyguardRadarGhostBoss();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Boss")
	void SetContactIdentified(bool bIdentified);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Boss")
	bool OpenOrbitExposure();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Boss")
	bool OpenRearAspectIglaWindow();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission07|Boss")
	bool ArmBreakRifleFinish();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Boss")
	bool IsContactIdentified() const { return bContactIdentified; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission07|Boss")
	bool IsBreakRifleFinishArmed() const
	{
		return bBreakRifleFinishArmed;
	}

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission07|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> SignatureModulator;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission07|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> RadarReceiver;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission07|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> CoolingDoor;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission07|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> Engine;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisPortEWPanel;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisStarboardEWPanel;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisCoolingDoor;

protected:
	virtual void HandleWeakPointDestroyed(
		USkyguardBossWeakPointComponent* WeakPoint,
		ESkyguardBossWeapon Weapon) override;

private:
	bool bContactIdentified = false;
	bool bBreakRifleFinishArmed = false;
};
