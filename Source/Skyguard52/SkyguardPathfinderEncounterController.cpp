#include "SkyguardPathfinderEncounterController.h"
#include "SkyguardPathfinderBoss.h"

USkyguardPathfinderEncounterController::USkyguardPathfinderEncounterController()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PrePhysics;
}

void USkyguardPathfinderEncounterController::BeginPlay()
{
	Super::BeginPlay();
	Pathfinder = Cast<ASkyguardPathfinderBoss>(GetOwner());
	if (ASkyguardPathfinderBoss* Boss = Pathfinder.Get())
	{
		ResetEncounterState(Boss->GetActorTransform());
		ObservedPhase = Boss->GetBossPhase();
	}
}

void USkyguardPathfinderEncounterController::TickComponent(
	const float DeltaTime,
	const ELevelTick TickType,
	FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (bAutoAdvance)
	{
		AdvanceEncounter(DeltaTime);
	}
}

void USkyguardPathfinderEncounterController::ResetEncounterState(const FTransform& NewRouteOrigin)
{
	RouteOrigin = NewRouteOrigin;
	RouteProgressCm = 0.f;
	PhaseElapsedSeconds = 0.f;
	TelegraphCycleSeconds = 0.f;
	TelegraphsTriggered = 0;
	CriticalTurnSign = 1.f;
	SetTelegraphActive(false);

	if (ASkyguardPathfinderBoss* Boss = Pathfinder.Get())
	{
		ObservedPhase = Boss->GetBossPhase();
		Boss->SetActorTransform(NewRouteOrigin, false, nullptr, ETeleportType::TeleportPhysics);
	}
}

void USkyguardPathfinderEncounterController::AdvanceEncounter(const float DeltaSeconds)
{
	ASkyguardPathfinderBoss* Boss = Pathfinder.Get();
	if (!Boss || DeltaSeconds <= 0.f)
	{
		return;
	}

	ObservePhaseChange();
	if (ObservedPhase == ESkyguardBossPhase::Defeated)
	{
		SetTelegraphActive(false);
		return;
	}

	const float StepSize = FMath::Clamp(MaxSimulationStepSeconds, 0.01f, 0.25f);
	const float MaxAdvance = StepSize * FMath::Clamp(MaxSimulationSubsteps, 1, 16);
	float Remaining = FMath::Min(DeltaSeconds, MaxAdvance);
	while (Remaining > UE_KINDA_SMALL_NUMBER)
	{
		const float Step = FMath::Min(StepSize, Remaining);
		AdvanceFixedStep(Step);
		Remaining -= Step;
	}
}

void USkyguardPathfinderEncounterController::ObservePhaseChange()
{
	const ASkyguardPathfinderBoss* Boss = Pathfinder.Get();
	if (!Boss || Boss->GetBossPhase() == ObservedPhase)
	{
		return;
	}

	ObservedPhase = Boss->GetBossPhase();
	PhaseElapsedSeconds = 0.f;
	TelegraphCycleSeconds = 0.f;
	SetTelegraphActive(false);

	if (ObservedPhase == ESkyguardBossPhase::Critical)
	{
		CriticalTurnSign =
			Boss->CurrentPilotCommand == ESkyguardPilotCommand::OrbitLeft ? -1.f :
			Boss->CurrentPilotCommand == ESkyguardPilotCommand::OrbitRight ? 1.f :
			1.f;
	}
}

void USkyguardPathfinderEncounterController::AdvanceFixedStep(const float StepSeconds)
{
	ASkyguardPathfinderBoss* Boss = Pathfinder.Get();
	if (!Boss)
	{
		return;
	}

	PhaseElapsedSeconds += StepSeconds;
	RouteProgressCm = FMath::Clamp(
		RouteProgressCm + GetPhaseSpeed() * GetEffectiveSpeedMultiplier() * StepSeconds,
		0.f,
		FMath::Max(100.f, RouteLengthCm));

	const FVector Forward = RouteOrigin.GetRotation().GetForwardVector();
	const FVector Right = RouteOrigin.GetRotation().GetRightVector();
	const FVector Up = RouteOrigin.GetRotation().GetUpVector();
	const FVector OriginLocation = RouteOrigin.GetLocation();

	float LateralOffset = 0.f;
	float HeightOffset = 0.f;
	float LateralSlope = 0.f;
	if (ObservedPhase == ESkyguardBossPhase::Approach ||
		ObservedPhase == ESkyguardBossPhase::Disarm)
	{
		const float Wave = FMath::Max(100.f, IngressSwayWavelengthCm);
		const float Angle = RouteProgressCm / Wave * 2.f * PI;
		LateralOffset = FMath::Sin(Angle) * IngressSwayAmplitudeCm;
		LateralSlope = FMath::Cos(Angle) * IngressSwayAmplitudeCm * 2.f * PI / Wave;
	}
	else if (ObservedPhase == ESkyguardBossPhase::LockWindow)
	{
		const float ClimbAlpha = FMath::Clamp(
			PhaseElapsedSeconds / FMath::Max(0.1f, LockWindowClimbSeconds),
			0.f,
			1.f);
		HeightOffset = FMath::InterpEaseInOut(0.f, LockWindowClimbCm, ClimbAlpha, 2.f);
		LateralOffset =
			FMath::Sin(PhaseElapsedSeconds * 5.2f) * IngressSwayAmplitudeCm * (1.f - ClimbAlpha) * 0.45f;
	}
	else if (ObservedPhase == ESkyguardBossPhase::Critical)
	{
		const float TurnAlpha = FMath::Clamp(
			PhaseElapsedSeconds / FMath::Max(1.f, CriticalTurnSeconds),
			0.f,
			1.f);
		const float TurnAngle = TurnAlpha * PI;
		LateralOffset =
			CriticalTurnSign * CriticalTurnRadiusCm * (1.f - FMath::Cos(TurnAngle));
		LateralSlope =
			CriticalTurnSign * CriticalTurnRadiusCm * FMath::Sin(TurnAngle) *
			(PI / FMath::Max(1.f, CriticalTurnSeconds)) /
			FMath::Max(100.f, GetPhaseSpeed());
		HeightOffset = LockWindowClimbCm * FMath::Lerp(1.f, 0.55f, TurnAlpha);
	}

	LateralOffset += GetCommandLateralOffset();
	HeightOffset += GetCommandHeightOffset();
	LateralOffset = FMath::Clamp(LateralOffset, -MaxLateralOffsetCm, MaxLateralOffsetCm);
	HeightOffset = FMath::Clamp(HeightOffset, MinHeightFromOriginCm, MaxHeightFromOriginCm);

	const FVector DesiredLocation =
		OriginLocation +
		Forward * RouteProgressCm +
		Right * LateralOffset +
		Up * HeightOffset;
	const FVector DesiredDirection = (Forward + Right * LateralSlope).GetSafeNormal();
	const FRotator DesiredRotation = DesiredDirection.Rotation();
	Boss->SetActorLocationAndRotation(
		DesiredLocation,
		DesiredRotation,
		false,
		nullptr,
		ETeleportType::TeleportPhysics);

	UpdateTelegraph(StepSeconds);
}

float USkyguardPathfinderEncounterController::GetPhaseSpeed() const
{
	switch (ObservedPhase)
	{
	case ESkyguardBossPhase::LockWindow:
		return LockWindowSpeedCmPerSecond;
	case ESkyguardBossPhase::Critical:
		return CriticalSpeedCmPerSecond;
	case ESkyguardBossPhase::Defeated:
		return 0.f;
	default:
		return ApproachSpeedCmPerSecond;
	}
}

float USkyguardPathfinderEncounterController::GetEffectiveSpeedMultiplier() const
{
	const ASkyguardPathfinderBoss* Boss = Pathfinder.Get();
	if (!Boss)
	{
		return 1.f;
	}

	switch (Boss->CurrentPilotCommand)
	{
	case ESkyguardPilotCommand::Pursuit:
		return 0.78f;
	case ESkyguardPilotCommand::Break:
		return 1.08f;
	case ESkyguardPilotCommand::OrbitLeft:
	case ESkyguardPilotCommand::OrbitRight:
		return 0.9f;
	case ESkyguardPilotCommand::Extend:
		return 1.18f;
	default:
		return 1.f;
	}
}

float USkyguardPathfinderEncounterController::GetCommandLateralOffset() const
{
	const ASkyguardPathfinderBoss* Boss = Pathfinder.Get();
	if (!Boss)
	{
		return 0.f;
	}

	switch (Boss->CurrentPilotCommand)
	{
	case ESkyguardPilotCommand::OrbitLeft:
		return -CommandLateralBiasCm;
	case ESkyguardPilotCommand::OrbitRight:
		return CommandLateralBiasCm;
	case ESkyguardPilotCommand::Break:
		return FMath::Sin(PhaseElapsedSeconds * 3.6f) * CommandLateralBiasCm * 0.8f;
	default:
		return 0.f;
	}
}

float USkyguardPathfinderEncounterController::GetCommandHeightOffset() const
{
	const ASkyguardPathfinderBoss* Boss = Pathfinder.Get();
	return Boss && Boss->CurrentPilotCommand == ESkyguardPilotCommand::Break
		? BreakClimbCm
		: 0.f;
}

float USkyguardPathfinderEncounterController::GetAttackInterval() const
{
	switch (ObservedPhase)
	{
	case ESkyguardBossPhase::LockWindow:
		return LockWindowAttackIntervalSeconds;
	case ESkyguardBossPhase::Critical:
		return CriticalAttackIntervalSeconds;
	default:
		return ApproachAttackIntervalSeconds;
	}
}

void USkyguardPathfinderEncounterController::UpdateTelegraph(const float StepSeconds)
{
	if (MaxTelegraphsPerEncounter <= 0 ||
		TelegraphsTriggered >= MaxTelegraphsPerEncounter)
	{
		SetTelegraphActive(false);
		return;
	}

	const float Interval = FMath::Max(AttackTelegraphLeadSeconds + 0.05f, GetAttackInterval());
	TelegraphCycleSeconds += StepSeconds;
	const bool bShouldTelegraph =
		TelegraphCycleSeconds >= Interval - AttackTelegraphLeadSeconds &&
		TelegraphCycleSeconds < Interval;
	SetTelegraphActive(bShouldTelegraph);

	if (TelegraphCycleSeconds >= Interval)
	{
		++TelegraphsTriggered;
		OnAttackCommitted.Broadcast(TelegraphsTriggered, ObservedPhase);
		TelegraphCycleSeconds = FMath::Fmod(TelegraphCycleSeconds, Interval);
		SetTelegraphActive(false);
	}
}

void USkyguardPathfinderEncounterController::SetTelegraphActive(const bool bNewActive)
{
	if (bAttackTelegraphActive == bNewActive)
	{
		return;
	}
	bAttackTelegraphActive = bNewActive;
	OnAttackTelegraphChanged.Broadcast(bAttackTelegraphActive);
}

bool USkyguardPathfinderEncounterController::IsRouteStateSafe() const
{
	const ASkyguardPathfinderBoss* Boss = Pathfinder.Get();
	if (!Boss ||
		!FMath::IsFinite(RouteProgressCm) ||
		RouteProgressCm < 0.f ||
		RouteProgressCm > FMath::Max(100.f, RouteLengthCm) + KINDA_SMALL_NUMBER)
	{
		return false;
	}

	const FTransform InverseOrigin = RouteOrigin.Inverse();
	const FVector LocalLocation = InverseOrigin.TransformPosition(Boss->GetActorLocation());
	return
		LocalLocation.ContainsNaN() == false &&
		FMath::Abs(LocalLocation.Y) <= MaxLateralOffsetCm + 1.f &&
		LocalLocation.Z >= MinHeightFromOriginCm - 1.f &&
		LocalLocation.Z <= MaxHeightFromOriginCm + 1.f;
}
