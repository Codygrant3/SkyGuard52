#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SkyguardYakR3DonorEvaluationRig.generated.h"

class UBoxComponent;
class USceneComponent;
class UStaticMeshComponent;

/**
 * Quarantined evaluation-only assembly for the ten R3 Yak donor meshes.
 *
 * This actor never replaces ASkyguardYak52Aircraft and is not referenced by a
 * runtime map. It provides a deterministic Unreal-side compatibility contract
 * for pivot, material, collision, camera and weapon-clearance review.
 */
UCLASS(NotBlueprintable, Transient)
class SKYGUARD52_API ASkyguardYakR3DonorEvaluationRig : public AActor
{
	GENERATED_BODY()

public:
	ASkyguardYakR3DonorEvaluationRig();

	const TArray<UStaticMeshComponent*>& GetDonorComponents() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Yak|R3 Evaluation")
	bool AreAllDonorsLoaded() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Yak|R3 Evaluation")
	bool DoDonorsPreserveRequiredClearances() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Yak|R3 Evaluation")
	FVector GetRearGunnerEyeLocation() const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Yak|R3 Evaluation")
	FVector GetRearGunnerSightTarget() const;

protected:
	UPROPERTY(VisibleAnywhere, Category="Skyguard|Yak|R3 Evaluation")
	TObjectPtr<USceneComponent> EvaluationRoot;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Yak|R3 Evaluation")
	TArray<TObjectPtr<UStaticMeshComponent>> DonorComponents;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Yak|R3 Evaluation")
	TObjectPtr<USceneComponent> RearGunnerEye;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Yak|R3 Evaluation")
	TObjectPtr<USceneComponent> RearGunnerSightTarget;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Yak|R3 Evaluation")
	TObjectPtr<UBoxComponent> CameraClearance;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Yak|R3 Evaluation")
	TObjectPtr<UBoxComponent> PilotSafety;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Yak|R3 Evaluation")
	TObjectPtr<UBoxComponent> RifleMuzzleClearance;

	UPROPERTY(VisibleAnywhere, Category="Skyguard|Yak|R3 Evaluation")
	TObjectPtr<UBoxComponent> IglaBackblastClearance;

private:
	mutable TArray<UStaticMeshComponent*> DonorComponentView;
};
