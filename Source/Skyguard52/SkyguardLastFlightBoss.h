#pragma once

#include "CoreMinimal.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardLastFlightBoss.generated.h"

class USkyguardBossWeakPointComponent;
class UStaticMeshComponent;

UENUM(BlueprintType)
enum class ESkyguardLastFlightStage : uint8
{
	Highway,
	Terminal,
	EvacuationShip,
	DisabledDescent,
	Defeated
};

/**
 * Mission 10's campaign-finale command drone.
 *
 * The boss retains the shared rifle/Igla/pilot-command interfaces while its
 * ten physical mechanisms form four deterministic objective milestones.
 */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardLastFlightBoss
	: public ASkyguardBossDroneBase
{
	GENERATED_BODY()

public:
	ASkyguardLastFlightBoss();

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Boss")
	bool OpenGuidanceArrayExposure();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Boss")
	bool BeginTerminalStrikeCycle();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Boss")
	bool OpenFirstIglaWindow();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Boss")
	bool IssueClimbCommand();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Boss")
	bool OpenFinalIglaWindow();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Boss")
	bool ArmCommandCoreRiflePath();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Boss")
	bool DivertWreckFromCivilians();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission10|Safety")
	void SetCivilianSeparationMeters(float SeparationMeters);

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Boss")
	ESkyguardLastFlightStage GetFinaleStage() const { return FinaleStage; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Boss")
	int32 GetObjectiveMilestonesReached() const
	{
		return ObjectiveMilestonesReached;
	}
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Boss")
	bool IsClimbCommandIssued() const { return bClimbCommandIssued; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Boss")
	bool IsWreckDiverted() const { return bWreckDiverted; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission10|Boss")
	float GetCivilianSeparationMeters() const
	{
		return CivilianSeparationMeters;
	}

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Skyguard|Mission10|Safety", meta=(ClampMin="1.0"))
	float MinimumCivilianSeparationMeters = 550.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> PortGuidanceArray;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> StarboardGuidanceArray;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> PortStrikeBayMechanism;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> StarboardStrikeBayMechanism;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> PortCoolingSystem;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> StarboardCoolingSystem;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> Jammer;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> PortEngine;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> StarboardEngine;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission10|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> CommandCore;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisArmorPort;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisArmorStarboard;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisStrikeBayPort;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisStrikeBayStarboard;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisEnginePort;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisEngineStarboard;

protected:
	virtual void HandleWeakPointDestroyed(
		USkyguardBossWeakPointComponent* WeakPoint,
		ESkyguardBossWeapon Weapon) override;

private:
	ESkyguardLastFlightStage FinaleStage =
		ESkyguardLastFlightStage::Highway;
	int32 ObjectiveMilestonesReached = 0;
	float CivilianSeparationMeters = 0.f;
	bool bTerminalStrikeCycleOpen = false;
	bool bClimbCommandIssued = false;
	bool bCommandCoreRifleArmed = false;
	bool bWreckDiverted = false;

	bool HasSafeCivilianSeparation() const;
	void AdvanceObjectiveMilestone();
};
