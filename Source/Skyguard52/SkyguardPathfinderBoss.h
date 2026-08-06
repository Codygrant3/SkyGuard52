#pragma once

#include "CoreMinimal.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardPathfinderBoss.generated.h"

class USkyguardBossWeakPointComponent;
class USkyguardPathfinderEncounterController;
class UStaticMeshComponent;

UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardPathfinderBoss : public ASkyguardBossDroneBase
{
	GENERATED_BODY()

public:
	ASkyguardPathfinderBoss();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> CommandAntenna;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> NoseCamera;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> Engine;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> ControlLinkage;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisNose;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisCenter;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisTail;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisSpine;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Encounter")
	TObjectPtr<USkyguardPathfinderEncounterController> EncounterController;

protected:
	virtual void HandleWeakPointDestroyed(
		USkyguardBossWeakPointComponent* WeakPoint,
		ESkyguardBossWeapon Weapon) override;
};
