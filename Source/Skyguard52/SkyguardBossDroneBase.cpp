#include "SkyguardBossDroneBase.h"
#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardCombatVFX.h"
#include "SkyguardInputCombatPerformanceCapture.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "TimerManager.h"

ASkyguardBossDroneBase::ASkyguardBossDroneBase()
{
	PrimaryActorTick.bCanEverTick = false;
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("BossRoot"));
	SetRootComponent(Root);

	BodyMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BodyMesh"));
	BodyMesh->SetupAttachment(Root);
	BodyMesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	BodyMesh->SetCollisionResponseToAllChannels(ECR_Block);
}

void ASkyguardBossDroneBase::BeginPlay()
{
	Super::BeginPlay();
	WeakPoints.Reset();
	GetComponents<USkyguardBossWeakPointComponent>(WeakPoints);
	for (USkyguardBossWeakPointComponent* WeakPoint : WeakPoints)
	{
		if (WeakPoint)
		{
			WeakPoint->Integrity = WeakPoint->MaxIntegrity;
		}
	}
}

bool ASkyguardBossDroneBase::ApplyWeaponHit(
	UPrimitiveComponent* HitComponent,
	const ESkyguardBossWeapon Weapon,
	const float Damage,
	const FVector HitLocation,
	const FVector HitDirection)
{
	if (Phase == ESkyguardBossPhase::Defeated || Damage <= 0.f)
	{
		return false;
	}

	USkyguardBossWeakPointComponent* WeakPoint =
		Cast<USkyguardBossWeakPointComponent>(HitComponent);
	if (!WeakPoint)
	{
		return false;
	}

	const bool bApplied = WeakPoint->ApplyWeaponDamage(Weapon, Damage);
	if (bApplied)
	{
		if (Weapon == ESkyguardBossWeapon::Rifle)
		{
			++Telemetry.RifleHits;
		}
		else
		{
			++Telemetry.IglaHits;
		}
		USkyguardCombatVFX::SpawnHitSparks(GetWorld(), HitLocation, -HitDirection);
	}
	return bApplied;
}

bool ASkyguardBossDroneBase::ApplyIglaStrike(
	const float Damage,
	const FVector HitLocation,
	const FVector HitDirection)
{
	if (!IsIglaLockEligible())
	{
		return false;
	}

	for (USkyguardBossWeakPointComponent* WeakPoint : WeakPoints)
	{
		if (WeakPoint && !WeakPoint->bDestroyed && WeakPoint->bExposed &&
			WeakPoint->AcceptsWeapon(ESkyguardBossWeapon::Igla))
		{
			return ApplyWeaponHit(
				WeakPoint,
				ESkyguardBossWeapon::Igla,
				Damage,
				HitLocation,
				HitDirection);
		}
	}
	return false;
}

void ASkyguardBossDroneBase::IssuePilotCommand(const ESkyguardPilotCommand Command)
{
	CurrentPilotCommand = Command;
	++Telemetry.PilotCommandsIssued;
	OnPilotCommandNative.Broadcast(Command);
	OnPilotCommand.Broadcast(Command);
}

void ASkyguardBossDroneBase::RegisterDefeatDebris(UStaticMeshComponent* DebrisComponent)
{
	if (!DebrisComponent || DefeatDebrisComponents.Num() >= MaxDefeatDebrisPieces)
	{
		return;
	}

	DebrisComponent->SetMobility(EComponentMobility::Movable);
	DebrisComponent->SetVisibility(false, true);
	DebrisComponent->SetHiddenInGame(true);
	DebrisComponent->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	DebrisComponent->SetSimulatePhysics(false);
	DefeatDebrisComponents.Add(DebrisComponent);
}

void ASkyguardBossDroneBase::CleanupDefeatDebris()
{
	for (UStaticMeshComponent* Debris : DefeatDebrisComponents)
	{
		if (!Debris)
		{
			continue;
		}
		Debris->SetSimulatePhysics(false);
		Debris->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Debris->SetVisibility(false, true);
		Debris->SetHiddenInGame(true);
	}
	USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
		this, TEXT("boss_destruction_cleanup"));
}

void ASkyguardBossDroneBase::NotifyWeakPointDestroyed(
	USkyguardBossWeakPointComponent* WeakPoint,
	const ESkyguardBossWeapon Weapon)
{
	if (!WeakPoint || Phase == ESkyguardBossPhase::Defeated)
	{
		return;
	}
	++Telemetry.WeakPointsDestroyed;
	HandleWeakPointDestroyed(WeakPoint, Weapon);
}

void ASkyguardBossDroneBase::SetBossPhase(const ESkyguardBossPhase NewPhase)
{
	if (Phase == NewPhase)
	{
		return;
	}
	const ESkyguardBossPhase Previous = Phase;
	Phase = NewPhase;
	OnBossPhaseChanged.Broadcast(Previous, NewPhase);
	if (Phase == ESkyguardBossPhase::Defeated)
	{
		HandleDefeated();
	}
}

void ASkyguardBossDroneBase::HandleWeakPointDestroyed(
	USkyguardBossWeakPointComponent* WeakPoint,
	ESkyguardBossWeapon Weapon)
{
	USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
		this, TEXT("boss_weak_point_destroyed"));
}

void ASkyguardBossDroneBase::HandleDefeated()
{
	bIglaLockEnabled = false;

	BodyMesh->SetHiddenInGame(true);
	BodyMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	for (USkyguardBossWeakPointComponent* WeakPoint : WeakPoints)
	{
		if (WeakPoint)
		{
			WeakPoint->SetHiddenInGame(true);
			WeakPoint->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		}
	}

	const int32 DebrisCount = FMath::Min(DefeatDebrisComponents.Num(), MaxDefeatDebrisPieces);
	for (int32 Index = 0; Index < DebrisCount; ++Index)
	{
		UStaticMeshComponent* Debris = DefeatDebrisComponents[Index];
		if (!Debris)
		{
			continue;
		}

		Debris->DetachFromComponent(FDetachmentTransformRules::KeepWorldTransform);
		Debris->SetVisibility(true, true);
		Debris->SetHiddenInGame(false);
		if (Debris->GetStaticMesh())
		{
			Debris->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
			Debris->SetSimulatePhysics(true);
			const FVector Direction =
				(GetActorForwardVector() * -0.35f +
				 GetActorRightVector() * (Index - 1) * 0.45f +
				 FVector::UpVector * (0.55f + Index * 0.1f)).GetSafeNormal();
			Debris->AddImpulse(Direction * (10500.f + Index * 1800.f), NAME_None, true);
		}
	}
	if (DebrisCount > 0)
	{
		USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
			this, TEXT("drone_breakup"));
	}
	USkyguardCombatVFX::SpawnExplosion(GetWorld(), GetActorLocation(), 1.8f);
	USkyguardInputCombatPerformanceCapture::RecordGameplayEvent(
		this, TEXT("boss_destroyed"));
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().SetTimer(
			DefeatDebrisCleanupTimer,
			this,
			&ASkyguardBossDroneBase::CleanupDefeatDebris,
			FMath::Clamp(DefeatDebrisLifetimeSeconds, 1.f, 20.f),
			false);
	}
}
