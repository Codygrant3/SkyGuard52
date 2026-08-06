#pragma once

#include "CoreMinimal.h"
#include "SkyguardBossDroneBase.h"
#include "SkyguardIronRainBoss.generated.h"

class USkyguardBossWeakPointComponent;
class UStaticMeshComponent;

UENUM(BlueprintType)
enum class ESkyguardIronRainManeuver : uint8
{
	None,
	Climb,
	Cross
};

/** Mission 9 command carrier with bounded dispensers and two deterministic finishes. */
UCLASS(Blueprintable)
class SKYGUARD52_API ASkyguardIronRainBoss : public ASkyguardBossDroneBase
{
	GENERATED_BODY()

public:
	ASkyguardIronRainBoss();
	virtual void BeginPlay() override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Boss")
	bool OpenDispenserBay(int32 BayIndex);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Boss")
	bool ReleasePooledEscort(int32 BayIndex);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Boss")
	bool IssueClimbCommand();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Boss")
	bool IssueCrossCommand();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Boss")
	bool OpenUpperEngineExposure();
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Boss")
	bool ApplySecondIglaFinish(float Damage);
	UFUNCTION(BlueprintCallable, Category="Skyguard|Mission09|Boss")
	bool ArmFuelControlRifleFinish();

	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Boss")
	int32 GetDestroyedDispenserCount() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Boss")
	int32 GetDestroyedAntennaCount() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Boss")
	int32 GetDestroyedEngineCount() const;
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Boss")
	int32 GetReleasedEscortCount() const { return ReleasedEscortCount; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Boss")
	ESkyguardIronRainManeuver GetManeuver() const { return Maneuver; }
	UFUNCTION(BlueprintPure, Category="Skyguard|Mission09|Boss")
	bool IsFuelControlFinishArmed() const { return bFuelControlFinishArmed; }

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Skyguard|Mission09|Performance", meta=(ClampMin="1", ClampMax="24"))
	int32 MaxReleasesPerBay = 6;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> DispenserPort;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> DispenserCenter;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> DispenserStarboard;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> CommandAntennaPort;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> CommandAntennaStarboard;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> DecoyController;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> EnginePodPort;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> EnginePodCenter;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> EnginePodStarboard;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> FuelControlPort;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Mission09|Boss")
	TObjectPtr<USkyguardBossWeakPointComponent> FuelControlStarboard;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisPortWing;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisCenterRack;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TObjectPtr<UStaticMeshComponent> DebrisStarboardWing;

protected:
	virtual void HandleWeakPointDestroyed(
		USkyguardBossWeakPointComponent* WeakPoint,
		ESkyguardBossWeapon Weapon) override;

private:
	TArray<TObjectPtr<USkyguardBossWeakPointComponent>> Dispensers;
	TArray<TObjectPtr<USkyguardBossWeakPointComponent>> Antennae;
	TArray<TObjectPtr<USkyguardBossWeakPointComponent>> Engines;
	TArray<int32> BayReleaseCounts;
	ESkyguardIronRainManeuver Maneuver = ESkyguardIronRainManeuver::None;
	int32 ReleasedEscortCount = 0;
	bool bFuelControlFinishArmed = false;

	void RefreshAuthoredWeakPointRegistry();
	bool AreAllDestroyed(
		const TArray<TObjectPtr<USkyguardBossWeakPointComponent>>& Points) const;
};
