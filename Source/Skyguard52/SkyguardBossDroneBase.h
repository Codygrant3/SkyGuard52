#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardBossTypes.h"
#include "SkyguardBossDroneBase.generated.h"

class USceneComponent;
class UStaticMeshComponent;
class USkyguardBossWeakPointComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(
	FSkyguardBossPhaseEvent,
	ESkyguardBossPhase, PreviousPhase,
	ESkyguardBossPhase, NewPhase);

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(
	FSkyguardPilotCommandEvent,
	ESkyguardPilotCommand, Command);

DECLARE_MULTICAST_DELEGATE_OneParam(
	FSkyguardPilotCommandNativeEvent,
	ESkyguardPilotCommand);

UCLASS(Abstract, Blueprintable)
class SKYGUARD52_API ASkyguardBossDroneBase : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardBossDroneBase();
	virtual void BeginPlay() override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Boss")
	bool ApplyWeaponHit(
		UPrimitiveComponent* HitComponent,
		ESkyguardBossWeapon Weapon,
		float Damage,
		FVector HitLocation,
		FVector HitDirection);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Boss")
	bool ApplyIglaStrike(float Damage, FVector HitLocation, FVector HitDirection);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Boss")
	void IssuePilotCommand(ESkyguardPilotCommand Command);

	UFUNCTION(BlueprintPure, Category="Skyguard|Boss")
	bool IsIglaLockEligible() const { return bIglaLockEnabled && Phase != ESkyguardBossPhase::Defeated; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Boss")
	ESkyguardBossPhase GetBossPhase() const { return Phase; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Boss")
	const FSkyguardBossTelemetry& GetTelemetry() const { return Telemetry; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Boss|Destruction")
	int32 GetDefeatDebrisPieceCount() const { return DefeatDebrisComponents.Num(); }

	UFUNCTION(BlueprintPure, Category="Skyguard|Boss|Destruction")
	int32 GetMaxDefeatDebrisPieces() const { return MaxDefeatDebrisPieces; }

	void NotifyWeakPointDestroyed(
		USkyguardBossWeakPointComponent* WeakPoint,
		ESkyguardBossWeapon Weapon);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss")
	TObjectPtr<UStaticMeshComponent> BodyMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss")
	TArray<TObjectPtr<USkyguardBossWeakPointComponent>> WeakPoints;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss")
	ESkyguardBossPhase Phase = ESkyguardBossPhase::Approach;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss")
	ESkyguardPilotCommand CurrentPilotCommand = ESkyguardPilotCommand::Pursuit;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss")
	FSkyguardBossTelemetry Telemetry;

	UPROPERTY(BlueprintAssignable, Category="Skyguard|Boss")
	FSkyguardBossPhaseEvent OnBossPhaseChanged;

	UPROPERTY(BlueprintAssignable, Category="Skyguard|Boss")
	FSkyguardPilotCommandEvent OnPilotCommand;

	/**
	 * Native gameplay route paired with the reflected presentation event.
	 *
	 * Mission-owned C++ orchestration binds here so pilot-control propagation
	 * does not depend on reflected dynamic-delegate dispatch. Blueprint
	 * consumers continue to receive OnPilotCommand above.
	 */
	FSkyguardPilotCommandNativeEvent OnPilotCommandNative;

protected:
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Skyguard|Boss")
	bool bIglaLockEnabled = false;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Skyguard|Boss|Destruction", meta=(ClampMin="0", ClampMax="8"))
	int32 MaxDefeatDebrisPieces = 3;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Skyguard|Boss|Destruction", meta=(ClampMin="1.0", ClampMax="20.0"))
	float DefeatDebrisLifetimeSeconds = 6.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Destruction")
	TArray<TObjectPtr<UStaticMeshComponent>> DefeatDebrisComponents;

	void RegisterDefeatDebris(UStaticMeshComponent* DebrisComponent);
	void CleanupDefeatDebris();
	void SetBossPhase(ESkyguardBossPhase NewPhase);
	virtual void HandleWeakPointDestroyed(
		USkyguardBossWeakPointComponent* WeakPoint,
		ESkyguardBossWeapon Weapon);
	virtual void HandleDefeated();

private:
	FTimerHandle DefeatDebrisCleanupTimer;
};
