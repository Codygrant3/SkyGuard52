#include "SkyguardEnvironmentVFXPoolComponent.h"
#include "NiagaraComponent.h"
#include "NiagaraSystem.h"
#include "UObject/ConstructorHelpers.h"

USkyguardEnvironmentVFXPoolComponent::USkyguardEnvironmentVFXPoolComponent()
{
	PrimaryComponentTick.bCanEverTick = false;

	static ConstructorHelpers::FObjectFinder<UNiagaraSystem> SmokeAsset(
		TEXT("/Game/Skyguard/VFX/NS_GunSmoke.NS_GunSmoke"));
	static ConstructorHelpers::FObjectFinder<UNiagaraSystem> FireAsset(
		TEXT("/Game/Skyguard/VFX/NS_CityFire.NS_CityFire"));
	static ConstructorHelpers::FObjectFinder<UNiagaraSystem> SparksAsset(
		TEXT("/Game/Skyguard/VFX/NS_HitSparks.NS_HitSparks"));
	static ConstructorHelpers::FObjectFinder<UNiagaraSystem> ExplosionAsset(
		TEXT("/Game/Skyguard/VFX/NS_DroneExplosion.NS_DroneExplosion"));

	if (SmokeAsset.Succeeded()) SmokeSystem = SmokeAsset.Object;
	if (FireAsset.Succeeded()) FireSystem = FireAsset.Object;
	if (SparksAsset.Succeeded()) SparksSystem = SparksAsset.Object;
	if (ExplosionAsset.Succeeded()) ExplosionSystem = ExplosionAsset.Object;
}

void USkyguardEnvironmentVFXPoolComponent::BeginPlay()
{
	Super::BeginPlay();
	AllocatePool();
}

void USkyguardEnvironmentVFXPoolComponent::AllocatePool()
{
	if (Components.Num() > 0 || !GetOwner())
	{
		return;
	}

	const int32 BoundedCapacity = FMath::Clamp(PoolCapacity, 1, 32);
	Components.Reserve(BoundedCapacity);
	for (int32 Index = 0; Index < BoundedCapacity; ++Index)
	{
		UNiagaraComponent* Component = NewObject<UNiagaraComponent>(
			GetOwner(),
			*FString::Printf(TEXT("EnvironmentVFXPool_%02d"), Index));
		if (!Component)
		{
			continue;
		}
		Component->SetupAttachment(GetOwner()->GetRootComponent());
		Component->SetAutoActivate(false);
		Component->SetAutoDestroy(false);
		Component->RegisterComponent();
		Component->DeactivateImmediate();
		Components.Add(Component);
	}
}

UNiagaraSystem* USkyguardEnvironmentVFXPoolComponent::ResolveSystem(
	const ESkyguardEnvironmentVFXType Type) const
{
	switch (Type)
	{
	case ESkyguardEnvironmentVFXType::Smoke:
		return SmokeSystem;
	case ESkyguardEnvironmentVFXType::Fire:
		return FireSystem;
	case ESkyguardEnvironmentVFXType::Sparks:
		return SparksSystem;
	case ESkyguardEnvironmentVFXType::Explosion:
		return ExplosionSystem;
	default:
		return nullptr;
	}
}

bool USkyguardEnvironmentVFXPoolComponent::ActivatePooledEffect(
	const ESkyguardEnvironmentVFXType Type,
	const FTransform& WorldTransform)
{
	AllocatePool();
	UNiagaraSystem* System = ResolveSystem(Type);
	if (!System || Components.Num() == 0)
	{
		return false;
	}

	UNiagaraComponent* Component =
		Components[NextComponentIndex % Components.Num()];
	NextComponentIndex = (NextComponentIndex + 1) % Components.Num();
	if (!Component)
	{
		return false;
	}

	Component->DeactivateImmediate();
	Component->SetAsset(System);
	Component->SetWorldTransform(WorldTransform);
	Component->Activate(true);
	++ActivationCount;
	return true;
}

void USkyguardEnvironmentVFXPoolComponent::DeactivateAllEffects()
{
	for (UNiagaraComponent* Component : Components)
	{
		if (Component)
		{
			Component->DeactivateImmediate();
		}
	}
}
