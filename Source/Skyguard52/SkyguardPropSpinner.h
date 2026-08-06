#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardPropSpinner.generated.h"

class UStaticMeshComponent;

/** High-RPM propeller disc/blade spinner for Yak-52 nose. */
UCLASS()
class SKYGUARD52_API ASkyguardPropSpinner : public AActor
{
	GENERATED_BODY()
public:
	ASkyguardPropSpinner();
	virtual void Tick(float DeltaSeconds) override;
	virtual void BeginPlay() override;

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	TObjectPtr<UStaticMeshComponent> Hub;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	TObjectPtr<UStaticMeshComponent> BladeA;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	TObjectPtr<UStaticMeshComponent> BladeB;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	TObjectPtr<UStaticMeshComponent> BlurDisc;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard")
	float SpinRPM = 2200.f;

	float Angle = 0.f;
};
