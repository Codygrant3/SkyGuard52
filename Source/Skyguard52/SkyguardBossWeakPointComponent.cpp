#include "SkyguardBossWeakPointComponent.h"
#include "SkyguardBossDroneBase.h"

USkyguardBossWeakPointComponent::USkyguardBossWeakPointComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
	SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	SetCollisionResponseToAllChannels(ECR_Ignore);
	SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
	SetGenerateOverlapEvents(false);
}

void USkyguardBossWeakPointComponent::BeginPlay()
{
	Super::BeginPlay();
	Integrity = MaxIntegrity;
}

bool USkyguardBossWeakPointComponent::AcceptsWeapon(const ESkyguardBossWeapon Weapon) const
{
	return Weapon == ESkyguardBossWeapon::Rifle ? bAcceptsRifle : bAcceptsIgla;
}

void USkyguardBossWeakPointComponent::SetExposed(const bool bNewExposed)
{
	bExposed = bNewExposed;
	SetCollisionResponseToChannel(ECC_Visibility, bExposed ? ECR_Block : ECR_Ignore);
}

bool USkyguardBossWeakPointComponent::ApplyWeaponDamage(
	const ESkyguardBossWeapon Weapon,
	const float Damage)
{
	if (bDestroyed || !bExposed || !AcceptsWeapon(Weapon) || Damage <= 0.f)
	{
		return false;
	}

	Integrity = FMath::Max(0.f, Integrity - Damage);
	OnWeakPointDamaged.Broadcast(WeakPointId, Weapon, Integrity);
	if (Integrity <= 0.f)
	{
		bDestroyed = true;
		SetCollisionResponseToChannel(ECC_Visibility, ECR_Ignore);
		OnWeakPointDestroyed.Broadcast(WeakPointId, Weapon, Integrity);
		if (ASkyguardBossDroneBase* Boss = Cast<ASkyguardBossDroneBase>(GetOwner()))
		{
			Boss->NotifyWeakPointDestroyed(this, Weapon);
		}
	}
	return true;
}
