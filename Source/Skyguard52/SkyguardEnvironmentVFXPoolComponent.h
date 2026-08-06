#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SkyguardEnvironmentVFXPoolComponent.generated.h"

class UNiagaraComponent;
class UNiagaraSystem;

UENUM(BlueprintType)
enum class ESkyguardEnvironmentVFXType : uint8
{
	Smoke,
	Fire,
	Sparks,
	Explosion
};

UCLASS(ClassGroup=(Skyguard), meta=(BlueprintSpawnableComponent))
class SKYGUARD52_API USkyguardEnvironmentVFXPoolComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	USkyguardEnvironmentVFXPoolComponent();
	virtual void BeginPlay() override;

	UFUNCTION(BlueprintCallable, Category="Skyguard|Environment|VFX")
	bool ActivatePooledEffect(
		ESkyguardEnvironmentVFXType Type,
		const FTransform& WorldTransform);

	UFUNCTION(BlueprintCallable, Category="Skyguard|Environment|VFX")
	void DeactivateAllEffects();

	UFUNCTION(BlueprintPure, Category="Skyguard|Environment|VFX")
	int32 GetAllocatedPoolSize() const { return Components.Num(); }

	UFUNCTION(BlueprintPure, Category="Skyguard|Environment|VFX")
	int32 GetActivationCount() const { return ActivationCount; }

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|VFX", meta=(ClampMin="1", ClampMax="32"))
	int32 PoolCapacity = 12;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|VFX")
	TObjectPtr<UNiagaraSystem> SmokeSystem;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|VFX")
	TObjectPtr<UNiagaraSystem> FireSystem;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|VFX")
	TObjectPtr<UNiagaraSystem> SparksSystem;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Environment|VFX")
	TObjectPtr<UNiagaraSystem> ExplosionSystem;

private:
	UPROPERTY(Transient)
	TArray<TObjectPtr<UNiagaraComponent>> Components;

	int32 NextComponentIndex = 0;
	int32 ActivationCount = 0;

	UNiagaraSystem* ResolveSystem(ESkyguardEnvironmentVFXType Type) const;
	void AllocatePool();
};
