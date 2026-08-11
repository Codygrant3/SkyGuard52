#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "SkyguardMissionTypes.h"
#include "SkyguardGunner.generated.h"

class UCameraComponent;
class USpringArmComponent;
class UStaticMeshComponent;
class UInputComponent;
class USceneComponent;
class UCameraShakeBase;
class USkyguardGameUserSettings;

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
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	/** Applied look sensitivity after mapping from GameUserSettings. */
	UFUNCTION(BlueprintPure, Category="Skyguard|Settings")
	float GetAppliedLookSensitivity() const { return AppliedLookSensitivity; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Settings")
	float GetAppliedCameraShakeScale() const { return AppliedCameraShakeScale; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Settings")
	bool IsVerticalLookInverted() const { return bInvertVerticalLookApplied; }

	/** Clears per-sortie combat counters used for mission result scoring. */
	UFUNCTION(BlueprintCallable, Category="Skyguard|Combat|Sortie")
	void ResetSortieCombatStats();

	/** Copies sortie shots/hits/aircraft-damage into a mission result. */
	void FillSortieCombatStats(FSkyguardMissionResult& OutResult) const;

	UFUNCTION(BlueprintPure, Category="Skyguard|Combat|Sortie")
	int32 GetSortieShotsFired() const { return SortieShotsFired; }

	UFUNCTION(BlueprintPure, Category="Skyguard|Combat|Sortie")
	int32 GetSortieHits() const { return SortieHits; }

	/**
	 * Fraction of aircraft integrity lost this sortie.
	 * ASkyguardYak52Aircraft has no health/damage API yet, so this stays 0
	 * until aircraft damage exists (do not invent a damage system here).
	 */
	UFUNCTION(BlueprintPure, Category="Skyguard|Combat|Sortie")
	float GetSortieAircraftDamageFraction() const { return SortieAircraftDamageFraction; }

	void RecordRifleShot();
	void RecordRifleHit();
	void RecordIglaShot();
	void RecordIglaHit();

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

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat|Feedback")
	TSubclassOf<UCameraShakeBase> FireCameraShakeClass;

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

	/** Full seeker rescan interval; current lock stays sticky between scans. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Combat")
	float IglaAcquireIntervalSeconds = 0.12f;

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
	void PlayAppliedCameraShake(float IntensityScale = 1.f);
	bool IsRifleDirectionOutsidePilotSafetyArc() const;
	void UpdateADSVisuals(float DeltaSeconds);
	void UpdateIglaLock(float DeltaSeconds);
	void FireIgla();
	AActor* AcquireIglaTarget() const;
	bool IsIglaLockCandidateValid(const AActor* Candidate) const;
	bool ScoreIglaLockCandidate(
		const AActor* Candidate,
		const FVector& Origin,
		const FVector& Forward,
		float MinimumDot,
		float& OutScore) const;

	bool bFireHeldFromPlayerInput = false;
	bool bIglaLaunchRequestedFromPlayerInput = false;
	bool bIglaLockPreviouslyAcquired = false;
	float IglaAcquireCooldownRemaining = 0.f;
	bool bAimInputRecorded = false;
	void ApplyLocalPlayerControlState();
	void ApplyUserSettings(const USkyguardGameUserSettings& Settings);
	void HandleUserSettingsApplied(const USkyguardGameUserSettings& Settings);
	void BindUserSettings();
	void UnbindUserSettings();

	/** Maps GameUserSettings mouse sensitivity (default 0.07) onto gunner look scale (baseline 1.1). */
	static constexpr float SettingsSensitivityToLookScale = 1.1f / 0.07f;
	float AppliedLookSensitivity = 1.1f;
	float AppliedCameraShakeScale = 1.f;
	bool bInvertVerticalLookApplied = false;
	bool bUserSettingsBound = false;

	int32 SortieShotsFired = 0;
	int32 SortieHits = 0;
	/** Remains 0 until Yak/aircraft damage plumbing exists. */
	float SortieAircraftDamageFraction = 0.f;
};
