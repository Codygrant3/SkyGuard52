#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SkyguardBossTypes.h"
#include "SkyguardPathfinderEncounterController.generated.h"

class ASkyguardPathfinderBoss;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(
	FSkyguardPathfinderTelegraphEvent,
	bool, bTelegraphActive);

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(
	FSkyguardPathfinderAttackEvent,
	int32, AttackIndex,
	ESkyguardBossPhase, Phase);

UCLASS(ClassGroup=(Skyguard), meta=(BlueprintSpawnableComponent))
class SKYGUARD52_API USkyguardPathfinderEncounterController : public UActorComponent
{
	GENERATED_BODY()

public:
	USkyguardPathfinderEncounterController();
	virtual void BeginPlay() override;
	virtual void TickComponent(
		float DeltaTime,
		ELevelTick TickType,
		FActorComponentTickFunction* ThisTickFunction) override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Boss|Encounter")
	void AdvanceEncounter(float DeltaSeconds);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Boss|Encounter")
	void ResetEncounterState(const FTransform& NewRouteOrigin);

	UFUNCTION(BlueprintPure, Category="Skyguard|Boss|Encounter")
	bool IsRouteStateSafe() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Boss|Encounter")
	float GetRouteProgress() const { return RouteProgressCm; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Boss|Encounter")
	float GetEffectiveSpeedMultiplier() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Boss|Encounter")
	bool IsAttackTelegraphActive() const { return bAttackTelegraphActive; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Boss|Encounter")
	int32 GetTelegraphsTriggered() const { return TelegraphsTriggered; }

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter")
	bool bAutoAdvance = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Route", meta=(ClampMin="100.0"))
	float RouteLengthCm = 45000.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Route", meta=(ClampMin="100.0"))
	float ApproachSpeedCmPerSecond = 1250.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Route", meta=(ClampMin="100.0"))
	float LockWindowSpeedCmPerSecond = 850.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Route", meta=(ClampMin="100.0"))
	float CriticalSpeedCmPerSecond = 700.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Route", meta=(ClampMin="0.0"))
	float IngressSwayAmplitudeCm = 320.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Route", meta=(ClampMin="100.0"))
	float IngressSwayWavelengthCm = 9000.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Route", meta=(ClampMin="0.0"))
	float LockWindowClimbCm = 650.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Route", meta=(ClampMin="0.1"))
	float LockWindowClimbSeconds = 2.4f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Route", meta=(ClampMin="100.0"))
	float CriticalTurnRadiusCm = 1500.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Route", meta=(ClampMin="1.0"))
	float CriticalTurnSeconds = 5.5f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Safety", meta=(ClampMin="100.0"))
	float MaxLateralOffsetCm = 3600.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Safety")
	float MinHeightFromOriginCm = -80.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Safety")
	float MaxHeightFromOriginCm = 1200.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Safety", meta=(ClampMin="0.01", ClampMax="0.25"))
	float MaxSimulationStepSeconds = 0.05f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Safety", meta=(ClampMin="1", ClampMax="16"))
	int32 MaxSimulationSubsteps = 8;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Commands", meta=(ClampMin="0.0"))
	float CommandLateralBiasCm = 850.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Commands", meta=(ClampMin="0.0"))
	float BreakClimbCm = 260.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Telegraph", meta=(ClampMin="0.2"))
	float ApproachAttackIntervalSeconds = 6.5f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Telegraph", meta=(ClampMin="0.2"))
	float LockWindowAttackIntervalSeconds = 8.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Telegraph", meta=(ClampMin="0.2"))
	float CriticalAttackIntervalSeconds = 4.8f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Telegraph", meta=(ClampMin="0.05"))
	float AttackTelegraphLeadSeconds = 1.2f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Boss|Encounter|Telegraph", meta=(ClampMin="0", ClampMax="32"))
	int32 MaxTelegraphsPerEncounter = 16;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard|Boss|Encounter")
	ESkyguardBossPhase ObservedPhase = ESkyguardBossPhase::Approach;

	UPROPERTY(BlueprintAssignable, Category="Skyguard|Boss|Encounter")
	FSkyguardPathfinderTelegraphEvent OnAttackTelegraphChanged;

	// The controller never spawns projectiles. A mission-owned, pooled attack
	// presentation may consume this bounded event.
	UPROPERTY(BlueprintAssignable, Category="Skyguard|Boss|Encounter")
	FSkyguardPathfinderAttackEvent OnAttackCommitted;

private:
	TWeakObjectPtr<ASkyguardPathfinderBoss> Pathfinder;
	FTransform RouteOrigin;
	float RouteProgressCm = 0.f;
	float PhaseElapsedSeconds = 0.f;
	float TelegraphCycleSeconds = 0.f;
	int32 TelegraphsTriggered = 0;
	bool bAttackTelegraphActive = false;
	float CriticalTurnSign = 1.f;

	void AdvanceFixedStep(float StepSeconds);
	void ObservePhaseChange();
	void UpdateTelegraph(float StepSeconds);
	float GetPhaseSpeed() const;
	float GetCommandLateralOffset() const;
	float GetCommandHeightOffset() const;
	float GetAttackInterval() const;
	void SetTelegraphActive(bool bNewActive);
};
