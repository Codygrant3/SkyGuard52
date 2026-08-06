#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "SkyguardGunner.generated.h"

class UCameraComponent;
class USpringArmComponent;
class UStaticMeshComponent;
class UInputComponent;
class USceneComponent;

UCLASS()
class SKYGUARD52_API ASkyguardGunner : public ACharacter
{
	GENERATED_BODY()
	friend class ASkyguardGameMode;
public:
	ASkyguardGunner();
	virtual void Tick(float DeltaSeconds) override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
	virtual void BeginPlay() override;
	virtual void PossessedBy(AController* NewController) override;
	virtual void PawnClientRestart() override;

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<USpringArmComponent> Boom;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UCameraComponent> GunnerCamera;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> RifleMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> RifleReceiver;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> FrontSight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> RearSight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> HandMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> ForearmMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<UStaticMeshComponent> IglaTube;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Skyguard")
	TObjectPtr<USceneComponent> IglaMuzzle;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float LookYawLimit = 95.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float LookPitchMin = -35.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float LookPitchMax = 55.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float MouseSensitivity = 1.1f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float ADSFov = 42.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float HipFov = 85.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float FireRate = 9.5f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float TraceRange = 25000.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float BaseDamage = 34.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float RecoilPitch = 0.55f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat|Safety")
	float MinimumSafeSideFireYaw = 28.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float IglaLockSeconds = 1.15f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float IglaDamage = 160.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float IglaMaximumLockAngleDegrees = 7.5f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float IglaMinimumRange = 350.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float IglaMaximumRange = 18000.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	TSubclassOf<AActor> IglaMissileClass;

	bool bADS = false;
	bool bFireHeld = false;
	bool bIglaMode = false;
	float FireCooldown = 0.f;
	float Yaw = 0.f;
	float Pitch = 0.f;
	float Recoil = 0.f;
	float IglaLockProgress = 0.f;
	TWeakObjectPtr<AActor> IglaTarget;

	void LookX(float V);
	void LookY(float V);
	void InputLookX(float V);
	void InputLookY(float V);
	void InputADSPressed();
	void InputADSReleased();
	void InputFirePressed();
	void InputFireReleased();
	void InputSwitchWeaponPressed();
	void InputLaunchIglaPressed();
	void ADSPressed();
	void ADSReleased();
	void FirePressed();
	void FireReleased();
	void SwitchWeaponPressed();
	void LaunchIglaPressed();
	void FireShot();
	bool IsRifleDirectionOutsidePilotSafetyArc() const;
	void UpdateADSVisuals(float DeltaSeconds);
	void UpdateIglaLock(float DeltaSeconds);
	void FireIgla();
	AActor* AcquireIglaTarget() const;

	bool bFireHeldFromPlayerInput = false;
	bool bIglaLaunchRequestedFromPlayerInput = false;
	bool bIglaLockPreviouslyAcquired = false;
	bool bAimInputRecorded = false;
	void ApplyLocalPlayerControlState();
};
